#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from email import message_from_bytes
from email.header import decode_header, make_header
from pathlib import Path

import imaplib

from frank_autodraft import build_receipt_draft, load_recipient_map, parse_receipt_message, write_draft_file
from frank_inbox_monitor import load_credentials, load_sent_log, normalize_message_id
from frank_paths import (
    bid_recipients_file,
    frank_automation_log,
    frank_creds_file,
    frank_drafts_dir,
    frank_sent_log,
    frank_cycle_lock_dir,
    machine_label,
)
from send_frank_email import PROFILES as SEND_PROFILES
from send_frank_email import append_sent_log, build_message, send_message

ROBERT_EMAIL = "robert@kovaldistillery.com"
DMYTRO_EMAIL = "dmytro.klymentiev@kovaldistillery.com"
CLAUDE_EMAIL = "claude@koval-distillery.com"
CLAUDE_WORKSPACE_THREAD_TASK = "frank-2026-claude-ai-workspace-setup-review"
BOARD_API = os.environ.get("WORKSPACEBOARD_API", "http://127.0.0.1:17878").rstrip("/")
DIRECT_PRIMARY_PENDING_STATES = {"routed_pending_completion"}
DIRECT_PRIMARY_DONE_STATES = {"completed_report_sent", "blocked_report_sent"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one scheduled Frank inbox automation cycle."
    )
    parser.add_argument("--limit", type=int, default=100, help="Number of unseen inbox messages to inspect.")
    parser.add_argument(
        "--mode",
        choices=["draft-only", "send-clear"],
        default="draft-only",
        help="Whether clear receipt follow-ups are drafted only or also sent to Robert.",
    )
    parser.add_argument(
        "--notify",
        default="robert@kovaldistillery.com",
        help="Escalation recipient for unclear items.",
    )
    parser.add_argument(
        "--primary-email",
        default="robert@kovaldistillery.com",
        help="Primary human this assistant supports. Replies from this address to assistant review messages are handled locally.",
    )
    parser.add_argument(
        "--assistant-name",
        default="Frank",
        help="Short assistant name used in generated review subjects, e.g. Frank or Avignon.",
    )
    parser.add_argument(
        "--from-name",
        default="Frank Cannoli",
        help="Display name used when sending scheduled review messages.",
    )
    parser.add_argument(
        "--auto-task-id",
        default="frank-auto-escalation",
        help="Task id to record for generated scheduled review messages.",
    )
    parser.add_argument("--creds-file", default=str(frank_creds_file()))
    parser.add_argument("--sent-log", default=str(frank_sent_log()))
    parser.add_argument("--recipients-file", default=str(bid_recipients_file()))
    parser.add_argument("--drafts-dir", default=str(frank_drafts_dir()))
    parser.add_argument("--automation-log", default=str(frank_automation_log()))
    parser.add_argument("--cycle-lock-dir", default=str(frank_cycle_lock_dir()))
    parser.add_argument("--dry-run", action="store_true", help="Do not send any mail; print planned actions.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def decode_value(value: str) -> str:
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def load_automation_log(path: Path) -> dict[str, list[dict]]:
    records: dict[str, list[dict]] = {}
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            source_message_id = normalize_message_id(row.get("source_message_id", ""))
            if not source_message_id:
                continue
            records.setdefault(source_message_id, []).append(row)
    return records


def append_automation_log(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def latest_automation_action(records: dict[str, list[dict]], source_message_id: str) -> dict:
    items = records.get(normalize_message_id(source_message_id), [])
    return items[-1] if items else {}


def is_direct_primary_action(action: dict) -> bool:
    return bool(
        str(action.get("current_state") or "") in DIRECT_PRIMARY_PENDING_STATES | DIRECT_PRIMARY_DONE_STATES
        or str(action.get("dedupe_key") or "").startswith("frank-direct-primary-")
        or str(action.get("decision") or "").startswith("routed-primary")
    )


def fetch_unseen_messages(user: str, app_pw: str, limit: int) -> list[dict]:
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(user, app_pw)
    conn.select("INBOX", readonly=True)
    status, data = conn.search(None, "ALL")
    if status != "OK":
        conn.logout()
        raise RuntimeError(f"IMAP search failed: {status}")

    ids = data[0].split()[-limit:]
    messages = []
    for msg_id in ids:
        status, msg_data = conn.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue
        raw = b""
        for part in msg_data:
            if isinstance(part, tuple):
                raw += part[1]
        if not raw:
            continue

        msg = message_from_bytes(raw)
        body_parts = []
        html_parts = []
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            payload = part.get_payload(decode=True)
            if payload and "attachment" not in disposition.lower():
                if content_type == "text/plain":
                    body_parts.append(
                        payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    )
                elif content_type == "text/html":
                    html_parts.append(
                        payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    )

        body = "\n".join(body_parts).strip()
        if not body and html_parts:
            body = html_to_text("\n".join(html_parts))

        messages.append(
            {
                "imap_id": msg_id.decode(),
                "date": decode_value(msg.get("Date", "")),
                "from": decode_value(msg.get("From", "")),
                "to": decode_value(msg.get("To", "")),
                "cc": decode_value(msg.get("Cc", "")),
                "subject": decode_value(msg.get("Subject", "")),
                "message_id": decode_value(msg.get("Message-ID", "")),
                "in_reply_to": decode_value(msg.get("In-Reply-To", "")),
                "references": decode_value(msg.get("References", "")),
                "body": body,
            }
        )
    conn.logout()
    return messages


def ensure_mailbox(conn: imaplib.IMAP4_SSL, mailbox: str) -> None:
    status, data = conn.list(pattern=f'"{mailbox}"')
    if status == "OK" and data and data[0]:
        return
    conn.create(mailbox)


def archive_email(user: str, app_pw: str, message_id: str, mailbox: str) -> bool:
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(user, app_pw)
    conn.select("INBOX")
    status, data = conn.search(None, "HEADER", "Message-ID", f'"{message_id}"')
    if status != "OK" or not data or not data[0].strip():
        conn.logout()
        return False

    ensure_mailbox(conn, mailbox)
    archived = False
    for msg_id in data[0].split():
        label_status, _ = conn.store(msg_id, "+X-GM-LABELS", mailbox)
        if label_status == "OK":
            conn.store(msg_id, "+FLAGS", "\\Deleted")
            archived = True
    if archived:
        conn.expunge()
    conn.logout()
    return archived


def find_tracked_reply(message: dict, sent_log: dict[str, dict]) -> dict | None:
    in_reply_to = normalize_message_id(message.get("in_reply_to", ""))
    if in_reply_to and in_reply_to in sent_log:
        return sent_log[in_reply_to]

    for ref in message.get("references", "").split():
        normalized = normalize_message_id(ref)
        if normalized in sent_log:
            return sent_log[normalized]
    return None


def sender_email_from_header(value: str) -> str:
    match = re.search(r"<([^>]+)>", value or "")
    if match:
        return match.group(1).strip().lower()
    return (value or "").strip().lower()


def html_to_text(value: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value or "")
    text = re.sub(r"(?i)<(br|/p|/div|/li|/h[1-6])\b[^>]*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def summarize_body(message: dict, limit: int = 220) -> str:
    body = " ".join((message.get("body") or "").split())
    body = redact_sensitive_text(body)
    if len(body) <= limit:
        return body
    return body[: limit - 3].rstrip() + "..."


def action_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return slug[:48] or "direct-robert-work"


def direct_primary_dedupe_key(message: dict) -> str:
    source_id = normalize_message_id(str(message.get("message_id") or message.get("source_message_id") or ""))
    if source_id:
        compact = re.sub(r"[^a-zA-Z0-9]+", "-", source_id.strip("<>")).strip("-")
        return f"frank-direct-primary-{compact[:90]}"
    return f"frank-direct-primary-{action_slug(message.get('subject', ''))}"


def direct_primary_thread_task_id(action: dict) -> str:
    task_id = str(action.get("task_id") or "").strip()
    if task_id and task_id != "frank-primary-intake-ack":
        return task_id
    original_subject = normalize_subject_for_compare(str(action.get("original_subject") or action.get("subject") or ""))
    original_to = ",".join(normalize_email_list(str(action.get("original_to") or ROBERT_EMAIL)))
    if task_id:
        return f"{task_id}|{original_subject}|{original_to}"
    return f"{original_subject}|{original_to or ROBERT_EMAIL}"


def direct_primary_thread_key(action: dict) -> str:
    return "|".join([
        direct_primary_thread_task_id(action),
        normalize_subject_for_compare(str(action.get("subject") or action.get("original_subject") or "")),
        str(action.get("classification") or "").strip().lower(),
    ])


def direct_primary_session_title(message: dict) -> str:
    subject = re.sub(r"\s+", " ", str(message.get("subject") or "direct Robert work")).strip()
    return f"Frank direct Robert: {subject}"[:96]


def redact_sensitive_text(value: str) -> str:
    text = value or ""
    patterns = [
        (r"(?i)\b(password|passcode|app password|app pw|login code|2fa code|token|api key|secret)\s*[:=]\s*\S+", r"\1: [REDACTED]"),
        (r"(?i)\b(password|passcode|app password|app pw|login code|2fa code|token|api key|secret)\s+is\s+\S+", r"\1 is [REDACTED]"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def looks_like_acknowledgement(body: str) -> bool:
    lowered = body.lower()
    patterns = [
        "thank you",
        "thanks",
        "we are set",
        "we're set",
        "ok, i got it",
        "no need",
        "just for us to keep as a record",
        "keep as a record",
        "for our records",
        "for the record",
        "can all be archived",
        "can be archived",
        "archive them",
        "keep you updated",
        "i will keep you updated",
    ]
    return any(pattern in lowered for pattern in patterns)


def looks_like_primary_instruction(body: str) -> bool:
    lowered = body.lower()
    patterns = [
        "please ",
        "add ",
        "create ",
        "update ",
        "check ",
        "change ",
        "fix ",
        "send ",
        "schedule ",
        "queue ",
        "task",
        "don't ",
        "do not ",
        "should ",
        "approve",
        "deny",
    ]
    return any(pattern in lowered for pattern in patterns)


def looks_like_approval_gated_tracked_reply(message: dict) -> bool:
    text = f"{message.get('subject', '')} {message.get('body', '')}".lower()
    patterns = [
        "password",
        "passcode",
        "login code",
        "2fa",
        "credential",
        "api key",
        "secret",
        "wire",
        "payment",
        "invoice",
        "legal",
        "contract",
        "delete",
        "disable",
        "production",
        "deploy",
        "external send",
    ]
    return any(pattern in text for pattern in patterns)


def subject_starts_with_reply_to(subject: str, expected: str) -> bool:
    normalized = normalize_subject_for_compare(subject)
    expected = normalize_subject_for_compare(expected)
    return normalized.startswith(expected)


def is_assistant_review_reply(subject: str, tracked: dict | None, assistant_name: str) -> bool:
    expected_subject = f"{assistant_name} inbox review"
    if subject_starts_with_reply_to(subject, expected_subject):
        return True
    if not tracked:
        return False
    task_id = (tracked.get("task_id") or "").strip().lower()
    original_subject = tracked.get("subject", "")
    return task_id.endswith("auto-escalation") or subject_starts_with_reply_to(
        original_subject, expected_subject
    )


def tracked_reply_metadata(message: dict, tracked: dict) -> dict:
    return {
        "task_id": tracked.get("task_id", ""),
        "original_subject": tracked.get("subject", ""),
        "original_to": tracked.get("to", ""),
        "summary": summarize_body(message),
    }


def email_list_contains(value: str, email: str) -> bool:
    return email.lower() in (value or "").lower()


def is_copied_only(message: dict, assistant_email: str) -> bool:
    return email_list_contains(message.get("cc", ""), assistant_email) and not email_list_contains(
        message.get("to", ""), assistant_email
    )


def explicitly_requests_assistant_action(message: dict, assistant_name: str, assistant_email: str) -> bool:
    subject = message.get("subject", "")
    body = message.get("body", "")
    local_part = assistant_email.split("@", 1)[0]
    assistant_tokens = {
        assistant_name.strip().lower(),
        local_part.strip().lower(),
        local_part.split(".", 1)[0].strip().lower(),
    }
    text = re.sub(r"\s+", " ", f"{subject} {body}".lower())
    action_verbs = r"(please|can you|could you|would you|need you to|route|handle|file|archive|create|update|check|fix|send|draft|reply|ask|tell|schedule|log|record|escalate)"
    for token in assistant_tokens:
        if token and re.search(rf"\b{re.escape(token)}\b[^.?!]{{0,120}}\b{action_verbs}\b", text):
            return True
        if token and re.search(rf"\b{action_verbs}\b[^.?!]{{0,120}}\b{re.escape(token)}\b", text):
            return True
    return False


def is_claude_workspace_thread(tracked: dict) -> bool:
    task_id = (tracked.get("task_id") or "").strip().lower()
    original_subject = (tracked.get("subject") or "").lower()
    original_to = tracked.get("to") or ""
    return (
        task_id == CLAUDE_WORKSPACE_THREAD_TASK
        or (
            "thoughts on our ai workspace setup" in original_subject
            and email_list_contains(original_to, CLAUDE_EMAIL)
        )
    )


def is_papers_access_followup(message: dict, tracked: dict, sender_email: str) -> bool:
    if sender_email != CLAUDE_EMAIL or not is_claude_workspace_thread(tracked):
        return False
    body = (message.get("body") or "").lower()
    return "papers.koval.lan" in body and ("codex" in body or "frank" in body)


def classify_message(
    message: dict,
    sent_log: dict[str, dict],
    primary_email: str,
    assistant_email: str,
    assistant_name: str,
) -> tuple[str, dict]:
    subject = message.get("subject", "")
    sender = message.get("from", "")
    sender_email = sender_email_from_header(sender)
    body = message.get("body", "")
    tracked = find_tracked_reply(message, sent_log)
    primary_email = primary_email.strip().lower()
    assistant_email = assistant_email.strip().lower()

    if "Receipt from" in subject:
        return "receipt", {}
    if sender_email == assistant_email:
        return "assistant-self-mail", {"summary": summarize_body(message)}
    if sender_email == primary_email and "test:" in subject.lower():
        return "primary-test", {"summary": summarize_body(message)}
    if tracked:
        metadata = tracked_reply_metadata(message, tracked)
        if sender_email == primary_email and is_assistant_review_reply(subject, tracked, assistant_name):
            return "assistant-review-reply", metadata
        if sender_email == primary_email and is_claude_workspace_thread(tracked):
            metadata["handled_reason"] = "Robert instruction on Claude workspace thread; log locally instead of review-pinging Robert."
            return "tracked-primary-thread-instruction", metadata
        if sender_email == primary_email and looks_like_primary_instruction(body):
            metadata["handled_reason"] = "Primary recipient gave Frank an instruction or correction; log for local routing instead of review-pinging the sender."
            return "tracked-primary-instruction", metadata
        if is_papers_access_followup(message, tracked, sender_email):
            metadata["reply_to"] = CLAUDE_EMAIL
            metadata["cc"] = f"{ROBERT_EMAIL}, {DMYTRO_EMAIL}"
            metadata["handled_reason"] = "Claude asked for Frank/Codex Papers access confirmation on the approved workspace thread."
            return "tracked-claude-papers-access-followup", metadata
        if looks_like_approval_gated_tracked_reply(message):
            return "tracked-reply-approval-gate", metadata
        classification = "tracked-reply-info" if sender_email == primary_email and looks_like_acknowledgement(body) else "tracked-reply"
        return classification, metadata
    if sender_email == primary_email and subject_starts_with_reply_to(subject, f"{assistant_name} inbox review"):
        return "assistant-review-reply", {"summary": summarize_body(message)}
    if sender_email == primary_email and subject.lower().startswith("fwd:"):
        return "primary-forward", {
            "summary": summarize_body(message),
            "handled_reason": "Primary recipient forwarded a task/request to Frank; route locally instead of sending an inbox-review email back to the sender.",
        }
    if is_copied_only(message, assistant_email) and not explicitly_requests_assistant_action(
        message, assistant_name, assistant_email
    ):
        return "cc-fyi-no-action", {
            "summary": "Frank was copied on this message and no explicit Frank action request was detected.",
            "handled_reason": "Copied/FYI message without a Frank action request; log and file without decision email, including credential/auth status copies already visible to the primary recipient.",
        }
    if "portal digest" in subject.lower() or "digest" in subject.lower():
        return "digest", {"summary": summarize_body(message)}
    if re.search(r"(invoice|payment update|wire|gift card|password|login code)", subject, re.IGNORECASE):
        return "suspicious", {"summary": summarize_body(message)}
    if re.search(r"(noreply|no-reply|notifications?)", sender, re.IGNORECASE):
        return "notification", {"summary": summarize_body(message)}
    if sender_email == primary_email:
        return "primary-input", {
            "summary": summarize_body(message),
            "handled_reason": "Primary recipient sent Frank an instruction/request; route locally instead of sending an inbox-review email back to the sender.",
        }
    return "unclear", {"summary": summarize_body(message)}


def compose_escalation_body(item: dict, assistant_name: str, notify: str) -> str:
    recipient_name = sender_email_from_header(notify).split("@", 1)[0].split(".", 1)[0].title()
    context = item.get("summary") or "Frank found one message that is not safe to auto-handle from metadata alone."
    lines = [
        f"Hi {recipient_name},",
        "",
        f"{assistant_name}'s scheduled inbox check found one message that needs a concrete decision.",
        "",
        f"Subject: {item['subject']}",
        f"From/date: {item['from']} / {item['date']}",
        f"Context: {context}",
        "Proposed safe next action: Keep the source email in the mailbox and route it to the right worker or owner before any reply, filing, or external action.",
        "Approval boundary: No external send, credential handling, production change, or destructive mailbox action without the matching approved rule or explicit approval.",
        f"Needed: Decide how {assistant_name} should handle this single message.",
        "Next: Reply with the owner/action, or tell Frank to hold it for manual review.",
        f"Decision: Should {assistant_name} route/handle this message under standing rules, or hold it for your review?",
        "",
        "This is one item only. Other attention-needed messages will surface separately if still unhandled.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def send_plain_email(
    sender_email: str,
    app_pw: str,
    sent_log_path: Path,
    to_addr: str,
    subject: str,
    body: str,
    task_id: str,
    dry_run: bool,
    from_name: str,
    cc_addr: str = "",
    log_fields: dict | None = None,
) -> str:
    subject = re.sub(r"[\r\n]+", " ", str(subject or "")).strip()
    to_addrs = [addr.strip() for addr in to_addr.split(",") if addr.strip()]
    cc_addrs = [addr.strip() for addr in cc_addr.split(",") if addr.strip()]
    msg = build_message(sender_email, from_name, to_addrs, cc_addrs, [], subject, body)
    if not dry_run:
        send_message(sender_email, app_pw, msg)
        sent_row = {
            "task_id": task_id,
            "to": to_addr,
            "subject": subject,
            "message_id": msg["Message-ID"],
            "date": msg["Date"],
            "from": msg["From"],
            "cc": cc_addr,
        }
        if log_fields:
            sent_row.update(log_fields)
        append_sent_log(sent_log_path, sent_row)
    return str(msg["Message-ID"])


def normalize_subject_for_compare(subject: str) -> str:
    normalized = re.sub(r"\s+", " ", (subject or "").strip().lower())
    while normalized.startswith("re:"):
        normalized = normalized[3:].strip()
    return normalized


def normalize_email_list(value: str) -> tuple[str, ...]:
    return tuple(sorted(addr.strip().lower() for addr in (value or "").split(",") if addr.strip()))


def sent_log_has_row(
    sent_log: dict[str, dict],
    *,
    to_addr: str,
    subject: str,
    thread_task_id: str = "",
    body_intent: str = "",
    cc_addr: str = "",
    fallback_task_ids: tuple[str, ...] = (),
) -> bool:
    normalized_to = normalize_email_list(to_addr)
    normalized_cc = normalize_email_list(cc_addr)
    normalized_subject = normalize_subject_for_compare(subject)
    for row in sent_log.values():
        row_to = normalize_email_list(str(row.get("to") or ""))
        row_cc = normalize_email_list(str(row.get("cc") or ""))
        row_subject = normalize_subject_for_compare(str(row.get("subject") or ""))
        row_thread_task_id = str(row.get("thread_task_id") or row.get("task_id") or "")
        row_body_intent = str(row.get("body_intent") or "")
        row_task_id = str(row.get("task_id") or "")
        if row_to != normalized_to or row_subject != normalized_subject:
            continue
        if normalized_cc and row_cc != normalized_cc:
            continue
        if body_intent:
            if row_body_intent == body_intent and (not thread_task_id or row_thread_task_id == thread_task_id):
                return True
            if row_body_intent:
                continue
        if thread_task_id and row_thread_task_id == thread_task_id:
            return True
        if fallback_task_ids and row_task_id in fallback_task_ids:
            return True
    return False


def claude_papers_access_reply_already_sent(sent_log: dict[str, dict], subject: str) -> bool:
    for row in sent_log.values():
        task_id = str(row.get("task_id") or "")
        to_addr = str(row.get("to") or "")
        row_subject = str(row.get("subject") or "")
        if (
            task_id == CLAUDE_WORKSPACE_THREAD_TASK
            and email_list_contains(to_addr, CLAUDE_EMAIL)
            and normalize_subject_for_compare(row_subject) == normalize_subject_for_compare(subject)
        ):
            return True
    return sent_log_has_row(
        sent_log,
        to_addr=CLAUDE_EMAIL,
        cc_addr=f"{ROBERT_EMAIL}, {DMYTRO_EMAIL}",
        subject=subject,
        thread_task_id=CLAUDE_WORKSPACE_THREAD_TASK,
        body_intent="claude-papers-access-fixed-reply",
    )


def remember_sent_row(
    sent_log: dict[str, dict],
    *,
    message_id: str,
    task_id: str,
    to_addr: str,
    subject: str,
    cc_addr: str = "",
    extra: dict | None = None,
) -> None:
    if not message_id:
        return
    row = {
        "task_id": task_id,
        "to": to_addr,
        "subject": subject,
        "message_id": message_id,
        "cc": cc_addr,
    }
    if extra:
        row.update(extra)
    sent_log[normalize_message_id(message_id)] = row


def compose_claude_papers_access_reply() -> str:
    signature = SEND_PROFILES["frank"]["signature"]
    return (
        "Hi Claude,\n\n"
        "Robert asked that any response on this thread keep him and Dmytro copied.\n\n"
        "On Papers access: I do not currently have a confirmed MI/Papers login from the "
        "Frank/Codex runtime. I can work from the document once the Codex/Frank user has "
        "access, or from an accessible export/excerpt if that is faster.\n\n"
        "Please create the IT follow-up for the Codex/Frank access path, or send the "
        "document content in a form Codex can read safely.\n\n"
        f"{signature}"
    )


def compose_task_manager_route_message(action: dict, assistant_name: str) -> str:
    subject = str(action.get("subject") or "(no subject)").strip()
    sender = str(action.get("from") or "(unknown sender)").strip()
    date = str(action.get("date") or "(unknown date)").strip()
    source_id = normalize_message_id(str(action.get("source_message_id") or ""))
    summary = str(action.get("summary") or "No summary available.").strip()
    classification = str(action.get("classification") or "primary-input").strip()
    return "\n".join([
        f"{assistant_name} direct-email intake route.",
        "",
        f"Source Message-ID: {source_id}",
        f"Classification: {classification}",
        f"Subject: {subject}",
        f"From/date: {sender} / {date}",
        f"Context: {summary}",
        "",
        "Needed: Create or reuse a visible board-managed worker session in the correct workspace and handle this as a concrete Robert request.",
        "Next: If the request is safe and clear, route it to the owning workspace with a full task brief and monitor it to completion. If blocked, report the concrete blocker.",
        "Approval boundary: Do not expose secrets, change credentials/auth, send external-sensitive mail, mutate production, deploy, or perform destructive actions unless that specific action is separately approved.",
        "Completion: Record TODO/HANDOFF/project state and have Frank send Robert the required task-specific completion report when the routed work is complete.",
    ]).rstrip() + "\n"


def post_json(path: str, payload: dict, timeout: int = 8) -> dict:
    request = urllib.request.Request(
        f"{BOARD_API}{path}",
        data=json.dumps(payload, ensure_ascii=True).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
        parsed = json.loads(raw) if raw else {}
        if response.status >= 400 or not parsed.get("ok"):
            raise RuntimeError(str(parsed.get("message") or raw[:200] or "Workspaceboard API call failed"))
        return parsed


def get_json(path: str, timeout: int = 8) -> dict:
    with urllib.request.urlopen(f"{BOARD_API}{path}", timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}


def wait_for_session_prompt(session_id: str, timeout_seconds: float = 18.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    query = urllib.parse.urlencode({"session_id": session_id})
    while time.monotonic() < deadline:
        try:
            payload = get_json(f"/api/session-history?{query}", timeout=5)
        except Exception:
            time.sleep(0.5)
            continue
        history = str(payload.get("history") or "")
        if "OpenAI Codex" in history and ("\n›" in history or "\ngpt-" in history):
            return True
        time.sleep(0.5)
    return False


def build_direct_primary_prompt(action: dict, route: dict) -> str:
    return "\n".join([
        "Frank direct-owner intake task.",
        "",
        f"Source Message-ID: {normalize_message_id(str(action.get('source_message_id') or ''))}",
        f"Dedupe key: {route['dedupe_key']}",
        "Owner/source: Robert",
        f"Subject: {action.get('subject', '')}",
        f"From/date: {action.get('from', '')} / {action.get('date', '')}",
        f"Redacted context summary: {action.get('summary') or 'No summary available.'}",
        "",
        "Goal: handle this as Frank, Robert's chief-of-staff mailbox worker. Start with the point, be concise, and convert the request into a concrete next action.",
        "Required mechanics: create or reuse the correct visible worker route for substantive work, verify it started, monitor it to completion or a real blocker, update Frank TODO/HANDOFF/decision state, and report back before the source item is filed to Handled.",
        "Completion report target: robert@kovaldistillery.com.",
        "Report shape: what was done, what changed, what was not done, remaining decisions or approval gates, and relevant session/task IDs.",
        "Approval boundary: do not expose credentials or private mailbox bodies in chat; no OAuth/token/auth work; no external-sensitive replies; no CRM/Portal/OPS mutation unless the target is clear and the normal workspace route owns it; do not guess at pricing, account commitments, or unclear duplicate/target handling.",
    ]).rstrip() + "\n"


def create_visible_direct_primary_route(action: dict) -> dict:
    route = {
        "dedupe_key": str(action.get("dedupe_key") or ""),
        "workspace": "frank",
        "session_id": "",
        "session_title": str(action.get("session_title") or direct_primary_session_title(action)),
        "prompt_delivery": {},
    }
    created = post_json(
        "/api/session/create",
        {"workspace": route["workspace"], "mode": "codex", "title": route["session_title"]},
    )
    session = created.get("session") if isinstance(created.get("session"), dict) else {}
    route["session_id"] = str(session.get("id") or "")
    route["session_title"] = str(session.get("title") or session.get("display_name") or route["session_title"])
    if not route["session_id"] or not route["session_title"]:
        raise RuntimeError("Workspaceboard did not return a visible session id/title.")
    wait_for_session_prompt(route["session_id"])
    delivered = post_json(
        "/api/session-message",
        {"session_id": route["session_id"], "message": build_direct_primary_prompt(action, route), "wait_ms": 5000},
        timeout=10,
    )
    route["prompt_delivery"] = delivered.get("prompt_delivery") if isinstance(delivered.get("prompt_delivery"), dict) else {}
    return route


def find_existing_direct_primary_route(automation_log: dict[str, list[dict]], action: dict) -> dict | None:
    expected_key = direct_primary_thread_key(action)
    matches: list[dict] = []
    for rows in automation_log.values():
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_thread_key = str(row.get("thread_key") or "")
            if not row_thread_key and str(row.get("routed_session_id") or ""):
                row_thread_key = direct_primary_thread_key(row)
            if row_thread_key != expected_key:
                continue
            if str(row.get("routed_session_id") or ""):
                matches.append(row)
    return matches[-1] if matches else None


def direct_primary_ack_already_sent(
    sent_log: dict[str, dict],
    action: dict,
    assistant_name: str,
    notify: str,
) -> bool:
    return sent_log_has_row(
        sent_log,
        to_addr=notify,
        subject=f"{assistant_name} captured: {str(action.get('subject') or '')[:80]}",
        thread_task_id=direct_primary_thread_task_id(action),
        body_intent="direct-primary-route-ack",
        fallback_task_ids=("frank-primary-intake-ack", f"{action.get('dedupe_key', '')}-ack"),
    )


def route_to_task_manager(action: dict, assistant_name: str) -> tuple[bool, str]:
    payload = {
        "message": compose_task_manager_route_message(action, assistant_name),
        "wait_ms": 700,
    }
    request = urllib.request.Request(
        "http://127.0.0.1:17878/api/task-manager/message",
        data=json.dumps(payload, ensure_ascii=True).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw else {}
            if response.status == 200 and parsed.get("ok"):
                session = parsed.get("session") if isinstance(parsed.get("session"), dict) else {}
                session_id = str(session.get("id") or "")
                return True, session_id
            return False, str(parsed.get("message") or raw[:200] or "Task Manager route failed.")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return False, str(exc)


def compose_primary_ack(action: dict, assistant_name: str, route_ok: bool, route_detail: str, route_title: str = "") -> str:
    subject = str(action.get("subject") or "(no subject)").strip()
    summary = str(action.get("summary") or "I received your message.").strip()
    assistant_key = "avignon" if assistant_name.lower().startswith("avignon") else "frank"
    recipient_name = "Sonat" if assistant_key == "avignon" else "Robert"
    signature = SEND_PROFILES[assistant_key]["signature"]
    lines = [
        f"Hi {recipient_name},",
        "",
        f"I received your message about {subject}. I recorded the source context as: {summary}",
        "",
    ]
    if route_ok:
        route_text = f"visible work session {route_detail} / {route_title}" if route_detail and route_title else (f"Task Manager session {route_detail}" if route_detail else "Task Manager")
        lines.extend([
            f"I routed it into {route_text}. Current status: captured and routed; it is not complete yet.",
            "Next: I will follow the worker to completion or a real blocker, then send the closeout before the source message is filed to Handled.",
        ])
    else:
        lines.extend([
            f"I could not route it to Task Manager automatically. Current status: captured but blocked before worker routing; blocker: {route_detail}",
        ])
    lines.extend([
        "",
        signature,
    ])
    return "\n".join(lines).rstrip() + "\n"


def board_session_status(session_id: str) -> dict | None:
    payload = get_json("/api/status")
    for session in payload.get("managed_sessions", []) or []:
        if isinstance(session, dict) and session.get("id") == session_id:
            return session
    return None


def compose_direct_primary_closeout(action: dict, session: dict, blocked: bool) -> str:
    subject = str(action.get("subject") or "direct Robert request")
    session_id = str(action.get("routed_session_id") or "")
    session_title = str(action.get("routed_session_title") or session.get("title") or session.get("display_name") or "")
    state = str(session.get("status_label") or session.get("status") or "unknown")
    lines = [
        "Hi Robert,",
        "",
        f"Closeout: {subject}.",
        "",
        f"- Visible session: {session_id} / {session_title}",
        f"- Current worker state: {state}",
    ]
    if blocked:
        lines.extend([
            "- What was done: the request was captured and routed to a visible Frank worker.",
            "- What changed: durable Frank routing state now links the source message to the worker session.",
            "- What was not done: I did not make credential/auth, external-sensitive, production, destructive, or unclear data changes.",
            "- Remaining decision: the worker is blocked or needs follow-up before the source message can be filed as complete.",
        ])
    else:
        lines.extend([
            "- What was done: the routed worker reached a non-running completion state.",
            "- What changed: durable Frank routing state links the source message, dedupe key, and worker session.",
            "- What was not done: no extra external reply, credential/auth work, or unapproved production mutation was performed by the mailbox runtime.",
            "- Remaining decision: none recorded by the mailbox runtime. If the worker left a separate decision, it should be in the visible session output/TODO state.",
        ])
    return "\n".join(lines).rstrip() + "\n"


def monitor_direct_primary_action(action: dict, sender_email: str, app_pw: str, sent_log_path: Path, dry_run: bool, from_name: str) -> dict:
    state = str(action.get("current_state") or "")
    if state in DIRECT_PRIMARY_DONE_STATES:
        return {"monitor_state": state, "current_state": state, "archivable_now": True}
    if state not in DIRECT_PRIMARY_PENDING_STATES:
        return {"monitor_state": "not-pending", "archivable_now": False}
    try:
        session = board_session_status(str(action.get("routed_session_id") or ""))
    except Exception as exc:
        return {"monitor_state": "session-status-unavailable", "current_state": state, "archivable_now": False, "status_blocker": redact_sensitive_text(str(exc))[:240]}
    if not session:
        return {"monitor_state": "session-not-found", "current_state": state, "archivable_now": False}
    session_state = str(session.get("status") or "").lower()
    if session_state not in {"finished", "blocked"}:
        return {"monitor_state": "still-pending", "current_state": state, "session_status": session_state, "archivable_now": False}
    blocked = session_state == "blocked"
    closeout_state = "blocked_report_sent" if blocked else "completed_report_sent"
    message_id = send_plain_email(
        sender_email,
        app_pw,
        sent_log_path,
        ROBERT_EMAIL,
        f"Frank {'blocker' if blocked else 'complete'}: {str(action.get('subject') or '')[:80]}",
        compose_direct_primary_closeout(action, session, blocked),
        f"{action.get('dedupe_key', 'frank-direct-primary')}-{closeout_state}",
        dry_run,
        from_name,
    )
    return {
        "monitor_state": closeout_state,
        "current_state": closeout_state,
        "session_status": session_state,
        "completion_message_id": message_id,
        "archivable_now": True,
    }


def route_direct_primary_message(
    action: dict,
    automation_log: dict[str, list[dict]],
    sent_log: dict[str, dict],
    sender_email: str,
    app_pw: str,
    sent_log_path: Path,
    notify: str,
    assistant_name: str,
    dry_run: bool,
    from_name: str,
) -> None:
    action["dedupe_key"] = direct_primary_dedupe_key(action)
    action["thread_key"] = direct_primary_thread_key(action)
    action["thread_task_id"] = direct_primary_thread_task_id(action)
    existing_route = find_existing_direct_primary_route(automation_log, action)
    if existing_route:
        route = {
            "workspace": str(existing_route.get("routed_workspace") or "frank"),
            "session_id": str(existing_route.get("routed_session_id") or ""),
            "session_title": str(existing_route.get("routed_session_title") or ""),
            "prompt_delivery": existing_route.get("prompt_delivery") if isinstance(existing_route.get("prompt_delivery"), dict) else {},
        }
    else:
        route = create_visible_direct_primary_route(action)
    route_ok = bool(route["session_id"])
    route_detail = route["session_id"]
    route_title = route["session_title"]
    action.update({
        "routed_workspace": route["workspace"],
        "routed_session_id": route["session_id"],
        "routed_session_title": route["session_title"],
        "prompt_delivery": route["prompt_delivery"],
        "current_state": "routed_pending_completion",
        "owner": "robert",
        "completion_target": "visible-worker-completion-or-blocker",
        "report_target": ROBERT_EMAIL,
    })
    if direct_primary_ack_already_sent(sent_log, action, assistant_name, notify):
        action["decision"] = "routed-primary-ack-already-sent-no-resend" if route_ok else "primary-route-blocked-ack-already-sent-no-resend"
        action["no_send"] = True
        return
    log_fields = {
        "body_intent": "direct-primary-route-ack",
        "thread_key": action["thread_key"],
        "thread_task_id": action["thread_task_id"],
    }
    action["sent_message_id"] = send_plain_email(
        sender_email,
        app_pw,
        sent_log_path,
        notify,
        f"{assistant_name} captured: {str(action.get('subject') or '')[:80]}",
        compose_primary_ack(action, assistant_name, route_ok, route_detail, route_title),
        f"{action['dedupe_key']}-ack",
        dry_run,
        from_name,
        log_fields=log_fields,
    )
    remember_sent_row(
        sent_log,
        message_id=str(action.get("sent_message_id") or ""),
        task_id=f"{action['dedupe_key']}-ack",
        to_addr=notify,
        subject=f"{assistant_name} captured: {str(action.get('subject') or '')[:80]}",
        extra=log_fields,
    )
    action["decision"] = "routed-primary-instruction-ack-sent" if route_ok else "primary-instruction-route-blocked-ack-sent"


@contextmanager
def cycle_lock(lock_dir: Path):
    lock_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkdir(lock_dir)
    except FileExistsError as exc:
        raise RuntimeError(f"Frank automation lock already exists at {lock_dir}") from exc
    try:
        yield
    finally:
        try:
            os.rmdir(lock_dir)
        except OSError:
            pass


def main() -> int:
    args = parse_args()
    try:
        if args.notify.strip().lower() != args.primary_email.strip().lower():
            raise ValueError("Scheduled automation only notifies its configured primary recipient by default.")
        with cycle_lock(Path(args.cycle_lock_dir)):
            sender_email, app_pw = load_credentials(Path(args.creds_file))
            sent_log = load_sent_log(Path(args.sent_log))
            automation_log = load_automation_log(Path(args.automation_log))
            recipients = None
            messages = fetch_unseen_messages(sender_email, app_pw, args.limit)

            actions: list[dict] = []
            escalations: list[dict] = []
            for message in messages:
                source_message_id = normalize_message_id(message.get("message_id", ""))
                if not source_message_id:
                    continue
                if source_message_id in automation_log:
                    previous = latest_automation_action(automation_log, source_message_id)
                    previous_direct_primary = is_direct_primary_action(previous)
                    monitor_result = {}
                    archived = False
                    if previous_direct_primary:
                        monitor_result = monitor_direct_primary_action(
                            previous,
                            sender_email,
                            app_pw,
                            Path(args.sent_log),
                            args.dry_run,
                            args.from_name,
                        )
                        if monitor_result.get("archivable_now") and not args.dry_run:
                            archived = archive_email(sender_email, app_pw, source_message_id, "Handled")
                    else:
                        if not args.dry_run:
                            archived = archive_email(sender_email, app_pw, source_message_id, "Handled")
                    if previous_direct_primary and not monitor_result.get("archivable_now"):
                        decision = "direct-primary-route-still-open-not-filed"
                        classification = "previously-logged-direct-primary-pending"
                    elif previous_direct_primary and monitor_result.get("archivable_now"):
                        decision = "direct-primary-report-sent-filed-to-handled" if archived else "direct-primary-report-sent-archive-not-found"
                        classification = "previously-logged-direct-primary-closed"
                    else:
                        decision = "filed-previously-logged-to-handled"
                        classification = "previously-logged-inbox-residue"
                    action = {
                        "source_message_id": source_message_id,
                        "classification": classification,
                        "subject": message.get("subject", ""),
                        "from": message.get("from", ""),
                        "date": message.get("date", ""),
                        "decision": decision,
                        "archived_to_handled": bool(archived),
                        "machine": machine_label(),
                    }
                    for key in (
                        "dedupe_key",
                        "owner",
                        "completion_target",
                        "report_target",
                        "current_state",
                        "routed_workspace",
                        "routed_session_id",
                        "routed_session_title",
                        "prompt_delivery",
                        "sent_message_id",
                    ):
                        if key in previous:
                            action[key] = previous[key]
                    action.update(monitor_result)
                    if not args.dry_run:
                        append_automation_log(Path(args.automation_log), action)
                    actions.append(action)
                    continue

                classification, metadata = classify_message(
                    message,
                    sent_log,
                    args.primary_email,
                    sender_email,
                    args.assistant_name,
                )
                action = {
                    "source_message_id": source_message_id,
                    "classification": classification,
                    "subject": message.get("subject", ""),
                    "from": message.get("from", ""),
                    "date": message.get("date", ""),
                }
                action.update(metadata)

                if classification == "receipt":
                    if recipients is None:
                        recipients = load_recipient_map(Path(args.recipients_file))
                    parsed = parse_receipt_message(message)
                    draft = build_receipt_draft(message, parsed, recipients.get(parsed["card_last4"]), args.notify)
                    draft_path = write_draft_file(Path(args.drafts_dir), draft)
                    action["draft_file"] = str(draft_path)
                    if args.mode == "send-clear":
                        action["sent_message_id"] = send_plain_email(
                            sender_email,
                            app_pw,
                            Path(args.sent_log),
                            args.notify,
                            draft["subject"],
                            draft["body"],
                            "frank-auto-receipt",
                            args.dry_run,
                            args.from_name,
                        )
                        action["decision"] = "sent-clear"
                    else:
                        action["decision"] = "drafted-clear"
                elif classification == "assistant-review-reply":
                    action["decision"] = "logged-local-follow-up"
                elif classification == "tracked-primary-thread-instruction":
                    route_direct_primary_message(
                        action,
                        automation_log,
                        sent_log,
                        sender_email,
                        app_pw,
                        Path(args.sent_log),
                        args.notify,
                        args.assistant_name,
                        args.dry_run,
                        args.from_name,
                    )
                elif classification == "tracked-primary-instruction":
                    route_direct_primary_message(
                        action,
                        automation_log,
                        sent_log,
                        sender_email,
                        app_pw,
                        Path(args.sent_log),
                        args.notify,
                        args.assistant_name,
                        args.dry_run,
                        args.from_name,
                    )
                elif classification == "tracked-claude-papers-access-followup":
                    claude_subject = f"Re: {message.get('subject', '').removeprefix('Re:').strip()}"
                    if claude_papers_access_reply_already_sent(sent_log, claude_subject):
                        action["decision"] = "duplicate-claude-papers-access-reply-suppressed-no-send"
                        action["no_send"] = True
                        if not args.dry_run:
                            action["archived_to_handled"] = archive_email(
                                sender_email,
                                app_pw,
                                source_message_id,
                                "Handled",
                            )
                    else:
                        action["sent_message_id"] = send_plain_email(
                            sender_email,
                            app_pw,
                            Path(args.sent_log),
                            action["reply_to"],
                            claude_subject,
                            compose_claude_papers_access_reply(),
                            CLAUDE_WORKSPACE_THREAD_TASK,
                            args.dry_run,
                            args.from_name,
                            action["cc"],
                            log_fields={"body_intent": "claude-papers-access-fixed-reply", "thread_task_id": CLAUDE_WORKSPACE_THREAD_TASK},
                        )
                        remember_sent_row(
                            sent_log,
                            message_id=str(action.get("sent_message_id") or ""),
                            task_id=CLAUDE_WORKSPACE_THREAD_TASK,
                            to_addr=action["reply_to"],
                            subject=claude_subject,
                            cc_addr=action["cc"],
                            extra={"body_intent": "claude-papers-access-fixed-reply", "thread_task_id": CLAUDE_WORKSPACE_THREAD_TASK},
                        )
                        action["decision"] = "sent-internal-answer-with-robert-dmytro-cc"
                elif classification in {
                    "primary-test",
                    "tracked-reply-approval-gate",
                    "tracked-reply-info",
                    "tracked-reply",
                    "assistant-self-mail",
                    "notification",
                    "cc-fyi-no-action",
                    "primary-forward",
                    "primary-input",
                }:
                    if classification in {"primary-forward", "primary-input"}:
                        route_direct_primary_message(
                            action,
                            automation_log,
                            sent_log,
                            sender_email,
                            app_pw,
                            Path(args.sent_log),
                            args.notify,
                            args.assistant_name,
                            args.dry_run,
                            args.from_name,
                        )
                        if action.get("decision") == "routed-primary-instruction-ack-sent":
                            action["decision"] = "routed-primary-input-ack-sent"
                        elif action.get("decision") == "primary-instruction-route-blocked-ack-sent":
                            action["decision"] = "primary-input-route-blocked-ack-sent"
                    else:
                        action["decision"] = "logged-local-routing-no-email" if classification == "tracked-reply-approval-gate" else "logged-no-action"
                    if action["decision"] == "logged-no-action" and not args.dry_run:
                        action["archived_to_handled"] = archive_email(
                            sender_email,
                            app_pw,
                            source_message_id,
                            "Handled",
                        )
                else:
                    action["decision"] = "escalate"
                    escalations.append(action)

                action["machine"] = machine_label()
                actions.append(action)
                if not args.dry_run and action.get("decision") != "escalate":
                    append_automation_log(Path(args.automation_log), action)

            if escalations:
                escalation = escalations[0]
                subject = f"{args.assistant_name} decision needed: {escalation['subject'][:80]}"
                body = compose_escalation_body(escalation, args.assistant_name, args.notify)
                escalation_message_id = send_plain_email(
                    sender_email,
                    app_pw,
                    Path(args.sent_log),
                    args.notify,
                    subject,
                    body,
                    args.auto_task_id,
                    args.dry_run,
                    args.from_name,
                )
                escalation["escalation_message_id"] = escalation_message_id
                if not args.dry_run:
                    append_automation_log(Path(args.automation_log), escalation)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(actions, ensure_ascii=True, indent=2))
    else:
        if not actions:
            print("No new unseen messages required action.")
        for action in actions:
            print(json.dumps(action, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
