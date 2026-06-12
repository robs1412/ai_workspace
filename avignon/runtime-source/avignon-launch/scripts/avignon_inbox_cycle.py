#!/usr/local/bin/python3.13

from __future__ import annotations

import imaplib
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from assistant_decision_email import send_decision_email
from frank_auto_runner import classify_message
from frank_inbox_monitor import load_credentials, load_sent_log, normalize_message_id
from frank_paths import machine_label
from frank_portal_receipt import archive_email

FRANK_SCRIPT_DIR = Path("/Users/admin/.frank-launch/runtime/scripts")
if FRANK_SCRIPT_DIR.exists() and str(FRANK_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(FRANK_SCRIPT_DIR))
TASK_FLOW_SCRIPT_DIR = Path("/Users/werkstatt/ai_workspace/scripts")
if TASK_FLOW_SCRIPT_DIR.exists() and str(TASK_FLOW_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(TASK_FLOW_SCRIPT_DIR))

from frank_google_calendar import calendar_request, ensure_valid_token, load_client_config

try:
    import shared_task_flow
except ImportError:  # pragma: no cover - task-flow recorder is optional fail-open audit plumbing.
    shared_task_flow = None

try:
    import email_trace_recorder
except ImportError:  # pragma: no cover - email trace recorder is optional fail-open audit plumbing.
    email_trace_recorder = None

try:
    import mailbox_imap_helpers
except ImportError:  # pragma: no cover - shared mailbox helper is optional fail-open plumbing.
    mailbox_imap_helpers = None

CANONICAL_AI_ROOT = Path("/Users/werkstatt/ai_workspace")


def resolve_existing_path(*candidates) -> Path:
    first_valid = None
    for candidate in candidates:
        if not candidate:
            continue
        if first_valid is None:
            first_valid = candidate
        if candidate.exists():
            return candidate
    if first_valid is None:
        raise ValueError("At least one candidate path is required.")
    return first_valid


AI_ROOT = resolve_existing_path(
    Path(os.environ.get("AI_WORKSPACE_ROOT", "")).expanduser() if os.environ.get("AI_WORKSPACE_ROOT") else None,
    CANONICAL_AI_ROOT,
    SCRIPT_DIR.parent,
)
AVIGNON_ROOT = resolve_existing_path(
    Path(os.environ.get("AVIGNON_WORKSPACE_ROOT", "")).expanduser() if os.environ.get("AVIGNON_WORKSPACE_ROOT") else None,
    AI_ROOT / "avignon",
    SCRIPT_DIR.parent,
)
CREDS = resolve_existing_path(
    Path(os.environ.get("AVIGNON_CREDS_FILE", "")).expanduser() if os.environ.get("AVIGNON_CREDS_FILE") else None,
    CANONICAL_AI_ROOT / ".private" / "passwords" / "avignon-secret.txt",
    AI_ROOT / ".private" / "passwords" / "avignon-secret.txt",
    AVIGNON_ROOT / ".private" / "passwords" / "avignon-secret.txt",
)
SENT_LOG = Path(os.environ.get("AVIGNON_SENT_LOG", AVIGNON_ROOT / "sent-log.jsonl")).expanduser()
AUTO_LOG = Path(os.environ.get("AVIGNON_AUTOMATION_LOG", AVIGNON_ROOT / "automation-log.jsonl")).expanduser()
DECISIONS = Path(
    os.environ.get("AVIGNON_DECISIONS_FILE", AVIGNON_ROOT / "EMAIL_DERIVED_DECISIONS.md")
).expanduser()
SEND_DECISION_EMAILS = os.environ.get("AVIGNON_SEND_DECISION_EMAILS", "").strip().lower() in {
    "1",
    "true",
    "yes",
}
CENTRAL = ZoneInfo("America/Chicago")
GOOGLE_CAL_CLIENT = Path("/Users/admin/.frank-launch/private/frank-calendar-desktop-client.json")
GOOGLE_CAL_TOKEN = Path("/Users/admin/.frank-launch/private/frank-google-calendar-token.json")
ROBERT_EMAIL = "robert@kovaldistillery.com"
SONAT_EMAIL = "sonat@kovaldistillery.com"
BOARD_API = os.environ.get("WORKSPACEBOARD_API", "http://127.0.0.1:17878").rstrip("/")
IMAP_TIMEOUT_SECONDS = int(os.environ.get("AVIGNON_IMAP_TIMEOUT_SECONDS", "45"))
INBOX_SCAN_LIMIT = int(os.environ.get("AVIGNON_INBOX_SCAN_LIMIT", "100"))
DIRECT_OWNER_PENDING_STATES = {
    "routed_pending_completion",
    "blocked_pending_security_guard",
}
DIRECT_OWNER_DONE_STATES = {
    "completed_report_sent",
    "blocked_report_sent",
    "captured_route_blocked_report_sent",
    "no_action_logged",
}
DIRECT_OWNER_ACTIONS: dict[str, dict] = {}


def task_flow_status_from_action(action: dict) -> str:
    current_state = str(action.get("current_state") or "")
    decision = str(action.get("decision") or "")
    classification = str(action.get("classification") or "")
    if current_state in {"completed_report_sent", "blocked_report_sent", "captured_route_blocked_report_sent"}:
        return "reported" if "report_sent" in current_state else "blocked"
    if current_state == "routed_pending_completion":
        return "working"
    if current_state == "blocked_pending_security_guard":
        return "blocked"
    if current_state == "no_action_logged":
        return "filed" if action.get("archived") or action.get("archivable_now") else "completed"
    if action.get("archived") or "filed" in decision:
        return "filed"
    if action.get("completion_message_id") or action.get("blocker_message_id"):
        return "reported"
    if action.get("ack_message_id"):
        return "clarification_sent"
    if "route-still-open" in decision or "still-pending" in decision:
        return "waiting"
    if "routed" in decision or action.get("routed_session_id"):
        return "working"
    if "calendar-directive" in decision:
        return "completed" if "created" in decision or "existing" in decision else "clarification_needed"
    if "decision-email" in decision or classification in {"ambiguous-email-review", "duplicate-ambiguous-email-review"}:
        return "clarification_sent"
    if "blocked" in decision:
        return "blocked"
    return "classified"


def task_flow_packet_from_action(action: dict) -> dict:
    if not shared_task_flow:
        return {}
    source_ref = str(action.get("source_message_id") or "")
    report_target = action.get("report_target") if isinstance(action.get("report_target"), dict) else {}
    routed_session_id = action.get("routed_session_id") or ""
    dedupe_key = action.get("dedupe_key") or ""
    reported_state = action.get("monitor_state") or action.get("current_state") or ""
    reported_message_id = action.get("completion_message_id") or action.get("blocker_message_id")
    if not reported_message_id and reported_state in {"blocked_report_sent", "completed_report_sent", "captured_route_blocked_report_sent"}:
        reported_message_id = action.get("ack_message_id") or ""
    verification_readback = action.get("monitor_state") or action.get("decision") or ""
    if reported_message_id and "closeout_proof_marker" not in str(verification_readback):
        verification_readback = f"closeout_proof_marker: {verification_readback or reported_state}"
    return shared_task_flow.build_packet(
        source_ref=source_ref,
        dedupe_key=dedupe_key,
        intake_channel="email:avignon",
        requester=action.get("from") or "",
        owner_lane=action.get("owner") or "avignon",
        responsible_worker_or_persona="avignon",
        workspaceboard_session=routed_session_id,
        ops_portal_or_domain_task=action.get("ops_portal_or_domain_task") or action.get("task_id") or action.get("thread_task_id") or (f"workspaceboard:{routed_session_id}" if routed_session_id else "") or (f"email-report:{dedupe_key}" if reported_message_id and dedupe_key else "") or (",".join(action.get("decision_items") or []) if isinstance(action.get("decision_items"), list) else ""),
        status=task_flow_status_from_action(action),
        due_or_trigger="",
        scheduled_action="",
        calendar_event=action.get("calendar_event_id") or "",
        clarification_email=action.get("ack_message_id") or action.get("blocker_message_id") or "",
        completion_or_blocker_email=reported_message_id or "",
        source_links=action.get("subject") or "",
        approval_gates=action.get("classification") or "",
        verification_readback=verification_readback,
        papers_projection="",
        next_update=action.get("completion_target") or report_target.get("to") or action.get("decision") or "",
    )


def record_task_flow_event(action: dict, event: str = "avignon_action") -> None:
    if not shared_task_flow:
        return
    packet = task_flow_packet_from_action(action)
    if not packet:
        return
    action["task_packet"] = packet
    try:
        shared_task_flow.append_event(AUTO_LOG.parent / "task-flow-events.jsonl", packet, event, action=action)
    except Exception as exc:
        action["task_flow_record_error"] = exc.__class__.__name__


def task_flow_allows_archive(action: dict) -> bool:
    if not shared_task_flow:
        return True
    candidate = {**action, "archived": True}
    packet = task_flow_packet_from_action(candidate)
    allowed, missing = shared_task_flow.closeout_allowed(packet)
    if not allowed:
        action["task_flow_archive_blocked"] = True
        action["task_flow_missing_fields"] = missing
    return allowed


def decode_value(value: str) -> str:
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def sender_email(value: str) -> str:
    match = re.search(r"<([^>]+)>", value or "")
    return (match.group(1) if match else (value or "")).strip().lower()


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
    action_verbs = r"(please|can you|could you|would you|need you to|route|handle|file|archive|create|update|check|fix|send|share|provide|confirm|pull|draft|reply|ask|tell|schedule|log|record|escalate|follow up|follow-up)"
    for token in assistant_tokens:
        if token and re.search(rf"\b{re.escape(token)}\b[^.?!]{{0,120}}\b{action_verbs}\b", text):
            return True
        if token and re.search(rf"\b{action_verbs}\b[^.?!]{{0,120}}\b{re.escape(token)}\b", text):
            return True
        if token and re.search(rf"(?:^|[;:,\-\(\)\s]){re.escape(token)}(?:[;:,\-\)\s]|$)[^.?!]{{0,160}}\b(send|share|provide|confirm|check|pull|draft|reply|follow up|follow-up|schedule|look up)\b", text):
            return True
        if token and re.search(rf"\b(send|share|provide|confirm|check|pull|draft|reply|follow up|follow-up|schedule|look up)\b[^.?!]{{0,160}}(?:^|[;:,\-\(\)\s]){re.escape(token)}(?:[;:,\-\)\s]|$)", text):
            return True
    return False


def is_reply_or_forward_subject(subject: str) -> bool:
    return bool(re.match(r"^\s*((re|fw|fwd)\s*:)+", subject or "", re.IGNORECASE))


def normalized_subject(value: str) -> str:
    subject = re.sub(r"\s+", " ", (value or "").strip())
    while re.match(r"(?i)^(re|fw|fwd):\s*", subject):
        subject = re.sub(r"(?i)^(re|fw|fwd):\s*", "", subject, count=1).strip()
    return subject


def subject_slug(value: str) -> str:
    normalized = normalized_subject(value).lower()
    normalized = re.sub(r"^avignon rose decision needed:\s*", "", normalized)
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")[:60] or "message"


def is_decision_email_reply(message: dict) -> bool:
    subject = normalized_subject(message.get("subject", "")).lower()
    if subject.startswith("avignon rose decision needed:"):
        return True
    reply_tokens = " ".join(
        [
            message.get("subject", ""),
            message.get("in_reply_to", ""),
            message.get("references", ""),
        ]
    ).lower()
    return "avignon-email-review-" in reply_tokens and "decision needed" in reply_tokens


def html_to_text(value: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value or "")
    text = re.sub(r"(?i)<(br|/p|/div|/li|/h[1-6])\b[^>]*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def load_automation_ids() -> set[str]:
    ids: set[str] = set()
    if not AUTO_LOG.exists():
        return ids
    for line in AUTO_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        source_id = row.get("source_message_id")
        if source_id:
            ids.add(normalize_message_id(str(source_id)))
        for action in row.get("message_actions", []) or []:
            source_id = action.get("source_message_id")
            if source_id:
                ids.add(normalize_message_id(str(source_id)))
    return ids


def load_seen_ids_db_first() -> set[str]:
    ids: set[str] = set()
    if mailbox_imap_helpers is not None:
        ids.update(mailbox_imap_helpers.collect_seen_source_ids_from_db("avignon", 20000))
    ids.update(load_automation_ids())
    return ids


def load_automation_actions() -> dict[str, list[dict]]:
    actions: dict[str, list[dict]] = {}
    if not AUTO_LOG.exists():
        return actions
    for line in AUTO_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        candidates: list[dict] = []
        if row.get("source_message_id"):
            candidates.append(row)
        for action in row.get("message_actions", []) or []:
            if isinstance(action, dict) and action.get("source_message_id"):
                enriched = dict(action)
                enriched.setdefault("logged_at", row.get("logged_at"))
                candidates.append(enriched)
        for action in candidates:
            source_id = normalize_message_id(str(action.get("source_message_id") or ""))
            if source_id:
                actions.setdefault(source_id, []).append(action)
    return actions


def latest_action_for_source(records: dict[str, list[dict]], source_id: str) -> dict | None:
    items = records.get(normalize_message_id(source_id), [])
    return items[-1] if items else None


def open_imap(user: str, app_pw: str) -> imaplib.IMAP4_SSL:
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=IMAP_TIMEOUT_SECONDS)
    conn.login(user, app_pw)
    return conn


def fetch_inbox_count(user: str, app_pw: str) -> int:
    conn = open_imap(user, app_pw)
    try:
        status, data = conn.select("INBOX", readonly=True)
        if status != "OK":
            return 0
        return int(data[0]) if data and data[0] else 0
    finally:
        conn.logout()


def fetch_inbox(user: str, app_pw: str, seen_ids: set[str] | None = None, limit: int = INBOX_SCAN_LIMIT) -> list[dict]:
    conn = open_imap(user, app_pw)
    try:
        conn.select("INBOX", readonly=True)
        status, data = conn.search(None, "ALL")
        seen_ids = seen_ids or set()
        ids = data[0].split() if status == "OK" and data else []
        if limit > 0:
            ids = ids[-limit:]
        messages: list[dict] = []
        for imap_id in ids:
            status, header_data = conn.fetch(imap_id, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID DATE FROM TO CC SUBJECT IN-REPLY-TO REFERENCES)])")
            if status != "OK":
                continue
            header_raw = b"".join(part[1] for part in header_data if isinstance(part, tuple))
            if not header_raw:
                continue
            header_msg = message_from_bytes(header_raw)
            header_record = {
                "imap_id": imap_id.decode(),
                "date": decode_value(header_msg.get("Date", "")),
                "from": decode_value(header_msg.get("From", "")),
                "to": decode_value(header_msg.get("To", "")),
                "cc": decode_value(header_msg.get("Cc", "")),
                "subject": decode_value(header_msg.get("Subject", "")),
                "message_id": decode_value(header_msg.get("Message-ID", "")),
                "in_reply_to": decode_value(header_msg.get("In-Reply-To", "")),
                "references": decode_value(header_msg.get("References", "")),
                "body": "",
                "attachments": [],
                "body_fetched": False,
            }
            source_id = normalize_message_id(header_record["message_id"])
            if source_id and source_id in seen_ids:
                messages.append(header_record)
                continue

            status, msg_data = conn.fetch(imap_id, "(BODY.PEEK[])")
            if status != "OK":
                continue
            raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
            msg = message_from_bytes(raw)
            body_parts: list[str] = []
            html_parts: list[str] = []
            attachments: list[dict] = []
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", "")).lower()
                filename = decode_value(part.get_filename(""))
                payload = part.get_payload(decode=True) or b""
                if payload and "attachment" not in disposition:
                    if content_type == "text/plain":
                        body_parts.append(
                            payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                        )
                    elif content_type == "text/html":
                        html_parts.append(
                            payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                        )
                if filename or "attachment" in disposition:
                    attachments.append(
                        {
                            "filename": filename or "[unnamed]",
                            "content_type": content_type,
                            "bytes": len(payload),
                        }
                    )
            body = "\n".join(body_parts).strip()
            if not body and html_parts:
                body = html_to_text("\n".join(html_parts))
            header_record.update(
                {
                    "date": decode_value(msg.get("Date", header_record["date"])),
                    "from": decode_value(msg.get("From", header_record["from"])),
                    "to": decode_value(msg.get("To", header_record["to"])),
                    "cc": decode_value(msg.get("Cc", header_record["cc"])),
                    "subject": decode_value(msg.get("Subject", header_record["subject"])),
                    "message_id": decode_value(msg.get("Message-ID", header_record["message_id"])),
                    "in_reply_to": decode_value(msg.get("In-Reply-To", header_record["in_reply_to"])),
                    "references": decode_value(msg.get("References", header_record["references"])),
                    "body": body,
                    "attachments": attachments,
                    "body_fetched": True,
                }
            )
            messages.append(header_record)
        return messages
    finally:
        conn.logout()


def fetch_message_by_message_id(user: str, app_pw: str, source_message_id: str) -> dict | None:
    normalized = normalize_message_id(source_message_id)
    if not normalized:
        return None
    conn = open_imap(user, app_pw)
    try:
        for mailbox in ("INBOX", '"[Gmail]/All Mail"'):
            status, _ = conn.select(mailbox, readonly=True)
            if status != "OK":
                continue
            status, data = conn.search(None, "HEADER", "MESSAGE-ID", source_message_id)
            ids = data[0].split() if status == "OK" and data and data[0] else []
            for imap_id in ids:
                status, msg_data = conn.fetch(imap_id, "(BODY.PEEK[])")
                if status != "OK":
                    continue
                raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
                if not raw:
                    continue
                msg = message_from_bytes(raw)
                body_parts: list[str] = []
                html_parts: list[str] = []
                attachments: list[dict] = []
                for part in msg.walk():
                    content_type = part.get_content_type()
                    disposition = str(part.get("Content-Disposition", "")).lower()
                    filename = decode_value(part.get_filename(""))
                    payload = part.get_payload(decode=True) or b""
                    if payload and "attachment" not in disposition:
                        if content_type == "text/plain":
                            body_parts.append(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
                        elif content_type == "text/html":
                            html_parts.append(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
                    if filename or "attachment" in disposition:
                        attachments.append(
                            {
                                "filename": filename or "[unnamed]",
                                "content_type": content_type,
                                "bytes": len(payload),
                            }
                        )
                body = "\n".join(body_parts).strip()
                if not body and html_parts:
                    body = html_to_text("\n".join(html_parts))
                message = {
                    "imap_id": imap_id.decode(),
                    "date": decode_value(msg.get("Date", "")),
                    "from": decode_value(msg.get("From", "")),
                    "to": decode_value(msg.get("To", "")),
                    "cc": decode_value(msg.get("Cc", "")),
                    "subject": decode_value(msg.get("Subject", "")),
                    "message_id": decode_value(msg.get("Message-ID", "")),
                    "in_reply_to": decode_value(msg.get("In-Reply-To", "")),
                    "references": decode_value(msg.get("References", "")),
                    "body": body,
                    "attachments": attachments,
                    "body_fetched": True,
                    "mailbox": mailbox,
                }
                if normalize_message_id(str(message.get("message_id") or "")) == normalized:
                    return message
    finally:
        conn.logout()
    return None


def decision_item_exists(item_id: str) -> bool:
    if not DECISIONS.exists():
        return False
    return item_id in DECISIONS.read_text(encoding="utf-8")


def decision_thread_exists(slug: str, sent_log: dict[str, dict]) -> bool:
    if DECISIONS.exists() and slug in DECISIONS.read_text(encoding="utf-8").lower():
        return True
    for row in sent_log.values():
        task_id = (row.get("task_id") or "").lower()
        subject = (row.get("subject") or "").lower()
        if slug and (slug in task_id or slug in subject):
            return True
    return False


def append_decision_item(item_id: str, needed: str, next_step: str, decision: str) -> None:
    if DECISIONS.exists():
        text = DECISIONS.read_text(encoding="utf-8")
    else:
        text = "# Email-Derived Decisions - avignon\n\n## Open\n\n"
    entry = (
        f"- `{item_id}`\n"
        f"  - Needed: {needed}\n"
        f"  - Next: {next_step}\n"
        f"  - Decision: {decision}\n"
    )
    if "## Open" in text:
        text = text.replace("## Open\n\n", "## Open\n\n" + entry, 1)
    else:
        text += "\n## Open\n\n" + entry
    DECISIONS.write_text(text, encoding="utf-8")


def record_decision_item(item_id: str, needed: str, next_step: str, decision: str) -> str:
    if decision_item_exists(item_id):
        return ""
    message_id = ""
    if SEND_DECISION_EMAILS:
        message_id = send_decision_email("avignon", item_id, needed, next_step, decision)
    append_decision_item(item_id, needed, next_step, decision)
    return message_id


def append_log(row: dict) -> None:
    AUTO_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUTO_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    if email_trace_recorder is None:
        return
    logged_at = str(row.get("logged_at") or datetime.now(timezone.utc).isoformat())
    actions = row.get("message_actions") if isinstance(row.get("message_actions"), list) else []
    for action in actions:
        if not isinstance(action, dict):
            continue
        source_id = normalize_message_id(str(action.get("source_message_id") or ""))
        if not source_id:
            continue
        task_packet = task_flow_packet_from_action(action) if shared_task_flow else {}
        status = task_flow_status_from_action(action)
        details = {
            "classification": action.get("classification", ""),
            "decision": action.get("decision", ""),
            "archived": bool(action.get("archived")),
            "current_state": action.get("current_state", ""),
        }
        message = email_trace_recorder.build_message_record(
            mailbox_lane="avignon",
            worker="avignon",
            event="email_action_logged",
            source_message_id=source_id,
            source_ref=source_id,
            subject=action.get("subject", ""),
            from_address=action.get("from", ""),
            header_date=action.get("date", ""),
            direction="inbound",
            status=status,
            first_seen_at=logged_at,
            event_at=logged_at,
            task_packet=task_packet,
            workspaceboard_session=action.get("routed_session_id", ""),
            metadata=details,
            ops_portal_or_domain_task=action.get("dedupe_key", ""),
            body_summary=action.get("classification", ""),
        )
        email_trace_recorder.record_event(
            AUTO_LOG.parent,
            event="email_action_logged",
            message=message,
            task_packet=task_packet,
            details=details,
        )


def redact_sensitive_text(value: str) -> str:
    text = value or ""
    patterns = [
        (r"(?i)\b(password|passcode|app password|app pw|login code|2fa code|token|api key|secret)\s*[:=]\s*\S+", r"\1: [REDACTED]"),
        (r"(?i)\b(password|passcode|app password|app pw|login code|2fa code|token|api key|secret)\s+is\s+\S+", r"\1 is [REDACTED]"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def safe_summary(message: dict, limit: int = 320) -> str:
    text = " ".join(str(message.get("body") or "").split())
    text = redact_sensitive_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def action_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalized_subject(value).lower()).strip("-")
    return slug[:48] or "direct-owner-work"


def direct_owner_dedupe_key(message: dict, owner: str) -> str:
    source_id = normalize_message_id(str(message.get("message_id") or ""))
    if source_id:
        compact = re.sub(r"[^a-zA-Z0-9]+", "-", source_id.strip("<>")).strip("-")
        return f"avignon-direct-owner-{owner}-{compact[:80]}"
    return f"avignon-direct-owner-{owner}-{action_slug(message.get('subject', ''))}"


def direct_owner_task_title(message: dict, owner: str) -> str:
    owner_label = "Sonat" if owner == "sonat" else "Robert"
    subject = normalized_subject(message.get("subject", "")) or "direct owner work"
    title = f"Avignon direct {owner_label}: {subject}"
    return title[:96]


def direct_owner_reply_subject(subject: str) -> str:
    subject_text = " ".join(str(subject or "").split()).strip()
    if not subject_text:
        return "Re: direct request"
    if re.match(r"(?i)^(re|fw|fwd):", subject_text):
        return subject_text
    return f"Re: {subject_text}"


def source_thread_headers(message: dict) -> tuple[str, str]:
    source_message_id = normalize_message_id(str(message.get("message_id") or ""))
    in_reply_to = str(message.get("message_id") or source_message_id or "").strip()
    references = str(message.get("references") or "").strip()
    if source_message_id and source_message_id not in references:
        references = f"{references} {source_message_id}".strip()
    return in_reply_to, references


def direct_owner_report_target(owner: str) -> dict:
    if owner == "robert-approver":
        return {"to": ROBERT_EMAIL, "cc": ""}
    return {"to": SONAT_EMAIL, "cc": ""}


def looks_like_action_request_direct(message: dict) -> bool:
    body = re.sub(r"\s+", " ", str(message.get("body", "") or "").strip()).lower()
    text = f"{message.get('subject', '')} {body}".lower()
    action_patterns = [
        r"\badd\s+(someone|person|contact|account|customer|lead|prospect)\b",
        r"\b(create|add|update|enter|record|link|route|handle|process|complete|review|send|schedule|invite|follow up|follow-up)\b",
        r"\b(crm|portal|ops|account|contact|activity|sample request|samples|calendar|task|quote|pricing|dedupe)\b",
        r"\bplease\s+(add|create|update|enter|record|route|handle|process|send|schedule|invite|follow up)\b",
        r"\bcan you\s+(add|create|update|enter|record|route|handle|process|send|schedule|invite|follow up)\b",
    ]
    return any(re.search(pattern, text) for pattern in action_patterns)


def looks_like_no_action_direct(message: dict) -> bool:
    body = re.sub(r"\s+", " ", str(message.get("body", "") or "").strip()).lower()
    text = f"{message.get('subject', '')} {body}".lower()
    if re.fullmatch(r"(ok|okay|thanks|thank you|ok thanks|okay thanks|ok thank you|got it|sounds good)[.! ]*", body):
        return True
    if looks_like_action_request_direct(message):
        return False
    patterns = [
        "for your records",
        "for our records",
        "keep as a record",
        "no action",
        "no need",
        "no action needed",
        "nothing needed",
        "can be archived",
        "can all be archived",
        "archive this",
    ]
    if any(pattern in text for pattern in patterns):
        return True
    return bool(re.fullmatch(r"(fyi|for your records|for our records)[.! ]*", body))


def looks_like_sensitive_or_suspicious(message: dict) -> bool:
    text = f"{message.get('subject', '')} {message.get('body', '')}".lower()
    hard_stop_patterns = [
        r"\b(password|passcode|login code|2fa|credential|api key|secret)\b",
        r"\b(wire|payment|bank)\b",
        r"\b(legal review|legal issue|legal matter|legal approval|legal compliance|compliance matter)\b",
        r"\b(delete all|bulk delete)\b",
        r"\b(production|deploy|oauth|token)\b",
    ]
    if any(re.search(pattern, text) for pattern in hard_stop_patterns):
        return True

    # Trusted direct-owner CRM/market work often mentions agreements or contracts as
    # business context. Gate only when the request asks Avignon to do legal work.
    legal_context = re.search(r"\b(contract|agreement|msa|nda)\b", text)
    legal_action = re.search(
        r"\b(review|approve|sign|negotiate|redline|draft|execute|amend|terminate)\b",
        text,
    )
    return bool(legal_context and legal_action)


def looks_like_robert_avignon_instruction(message: dict) -> bool:
    if sender_email(message.get("from", "")) != ROBERT_EMAIL:
        return False
    if is_copied_only(message, "avignon.rose@kovaldistillery.com") and not explicitly_requests_assistant_action(
        message,
        "Avignon",
        "avignon.rose@kovaldistillery.com",
    ):
        return False
    text = f"{message.get('subject', '')} {message.get('body', '')}".lower()
    if not re.search(r"\b(avignon|sonat|crm|portal|handled mail|completion report|acknowledge|route)\b", text):
        return False
    return bool(
        re.search(
            r"\b(approve|approved|please|need|should|route|handle|fix|check|send|record|follow|complete|acknowledge)\b",
            text,
        )
    )


def direct_owner_kind(message: dict, classification: str) -> str:
    from_email = sender_email(message.get("from", ""))
    if from_email == SONAT_EMAIL and classification in {
        "primary-input",
        "primary-forward",
        "tracked-primary-instruction",
        "tracked-primary-thread-instruction",
    }:
        return "sonat"
    if looks_like_robert_avignon_instruction(message):
        return "robert-approver"
    return ""


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


def build_direct_owner_prompt(message: dict, owner: str, route: dict) -> str:
    source_id = normalize_message_id(str(message.get("message_id") or ""))
    report_target = direct_owner_report_target(owner)
    owner_label = "Sonat" if owner == "sonat" else "Robert as Avignon workflow owner/approver"
    cc_line = f"Copy Robert: {report_target['cc']}" if report_target["cc"] else "Copy Robert only if the task context or approval path requires it."
    return "\n".join(
        [
            "Avignon direct-owner intake task.",
            "",
            f"Source Message-ID: {source_id}",
            f"Dedupe key: {route['dedupe_key']}",
            f"Owner/source: {owner_label}",
            f"Subject: {message.get('subject', '')}",
            f"From/date: {message.get('from', '')} / {message.get('date', '')}",
            f"Redacted context summary: {safe_summary(message) or '(no body summary available)'}",
            "",
            "Goal: handle this as Avignon, Sonat's Strategic Market Architect and trusted consigliere. Start with the point, be concise, and convert the request into a concrete next action.",
            "Acknowledgement rule: if this is a quick-answer item and the answer is available in the same pass, send the answer directly and do not send a separate captured/routed receipt. Use a captured/routed acknowledgement only when the work will take a moment, is otherwise invisible, or is not immediately answerable.",
            "Required mechanics: create or reuse the correct visible worker route for substantive work, verify it started, monitor it to completion or a real blocker, update Avignon TODO/HANDOFF/decision state, and report back before the source item is filed to Handled.",
            f"Completion report target: {report_target['to']}. {cc_line}",
            "Report shape: what was done, what changed, what was not done, remaining decisions or approval gates, and relevant session/task IDs.",
            "Approval boundary: do not expose credentials or private mailbox bodies in chat; no OAuth/token/auth work; no external replies; no CRM/Portal/OPS mutation unless the target is clear and the normal workspace route owns it; do not guess at pricing, account commitments, or unclear CRM duplicate/target handling.",
        ]
    ).rstrip() + "\n"


def create_visible_direct_owner_route(message: dict, owner: str) -> dict:
    route = {
        "dedupe_key": direct_owner_dedupe_key(message, owner),
        "workspace": "avignon",
        "session_id": "",
        "session_title": direct_owner_task_title(message, owner),
        "prompt_delivery": {},
        "reused_existing": False,
    }
    existing = find_open_direct_owner_session(route["session_title"])
    if existing:
        route["session_id"] = str(existing.get("id") or "")
        route["session_title"] = str(existing.get("title") or existing.get("display_name") or route["session_title"])
        route["reused_existing"] = True
        return route
    try:
        created = post_json(
            "/api/session/create",
            {"workspace": route["workspace"], "mode": "codex", "title": route["session_title"]},
        )
        session = created.get("session") if isinstance(created.get("session"), dict) else {}
        route["session_id"] = str(session.get("id") or "")
        route["session_title"] = str(session.get("title") or session.get("display_name") or route["session_title"])
    except Exception as exc:
        blocker = redact_sensitive_text(str(exc))
        if "409" in blocker or "conflict" in blocker.casefold():
            existing = find_open_direct_owner_session(route["session_title"])
            if existing:
                route["session_id"] = str(existing.get("id") or "")
                route["session_title"] = str(existing.get("title") or existing.get("display_name") or route["session_title"])
                route["reused_existing"] = True
                return route
        raise
    if not route["session_id"] or not route["session_title"]:
        raise RuntimeError("Workspaceboard did not return a visible session id/title.")
    if route["reused_existing"]:
        return route
    wait_for_session_prompt(route["session_id"])
    prompt = build_direct_owner_prompt(message, owner, route)
    delivered = post_json(
        "/api/session-message",
        {"session_id": route["session_id"], "message": prompt, "wait_ms": 5000},
        timeout=10,
    )
    route["prompt_delivery"] = delivered.get("prompt_delivery") if isinstance(delivered.get("prompt_delivery"), dict) else {}
    return route


def write_direct_owner_body_file(kind: str, dedupe_key: str, body: str) -> Path:
    drafts_dir = Path(os.environ.get("AVIGNON_DRAFTS_DIR", "/Users/admin/.avignon-launch/state/drafts")).expanduser()
    drafts_dir.mkdir(parents=True, exist_ok=True)
    safe_key = re.sub(r"[^a-zA-Z0-9_-]+", "-", dedupe_key).strip("-")[:96]
    path = drafts_dir / f"{kind}-{safe_key}.txt"
    path.write_text(body.rstrip() + "\n", encoding="utf-8")
    return path


def send_avignon_owner_email(
    subject: str,
    body: str,
    task_id: str,
    to_addr: str,
    cc_addr: str = "",
    in_reply_to: str = "",
    references: str = "",
    html_body: str = "",
) -> str:
    body_path = write_direct_owner_body_file("direct-owner", task_id, body)
    html_body_path = None
    if html_body:
        html_body_path = write_direct_owner_body_file("direct-owner-html", task_id, html_body)
    recipients = {to_addr.strip().lower()}
    if cc_addr:
        recipients.add(cc_addr.strip().lower())
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "send_frank_email.py"),
        "--assistant",
        "avignon",
        "--to",
        to_addr,
        "--subject",
        subject,
        "--body-file",
        str(body_path),
        "--task-id",
        task_id,
    ]
    if html_body_path is not None:
        cmd.extend(["--html-body-file", str(html_body_path)])
    if cc_addr:
        cmd.extend(["--cc", cc_addr])
    if in_reply_to:
        cmd.extend(["--in-reply-to", in_reply_to])
    if references:
        cmd.extend(["--references", references])
    if any(addr and addr != SONAT_EMAIL for addr in recipients):
        cmd.append("--allow-non-primary")
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "AVIGNON_CREDS_FILE": str(CREDS),
            "AVIGNON_SENT_LOG": str(SENT_LOG),
            "AI_WORKSPACE_ROOT": str(AI_ROOT),
        },
        timeout=45,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Avignon direct-owner email send failed")
    match = re.search(r"Message-ID:\s*(\S+)", result.stdout)
    if match:
        return match.group(1)
    if SENT_LOG.exists():
        for line in reversed(SENT_LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-120:]):
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("task_id") == task_id and row.get("message_id"):
                return str(row.get("message_id"))
    return ""


def compose_direct_owner_ack(message: dict, owner: str, route: dict) -> str:
    subject = normalized_subject(message.get("subject", "")) or "your request"
    greeting = "Hi Robert," if owner == "robert-approver" else "Hi Sonat,"
    owner_line = "I am treating this as a Robert-supervised Avignon workflow item and will report back to Robert." if owner == "robert-approver" else ""
    if owner != "robert-approver":
        return "\n".join(
            [
                greeting,
                "",
                f"Captured: {subject}.",
                "",
                f"I routed it into visible work and will come back with either the finished result or the one concrete thing I need from you.",
                "",
                "Best,",
            ]
        ).rstrip() + "\n"
    lines = [
        greeting,
        "",
        f"Captured: {subject}.",
        "",
        f"I routed it into visible work session {route['session_id']} / {route['session_title']}. Current status: captured and routed; not complete yet.",
        "Next: I will follow the worker to completion or a real blocker, then send the closeout before the source message is filed to Handled.",
    ]
    if owner_line:
        lines.extend(["", owner_line])
    return "\n".join(lines).rstrip() + "\n"


def handle_direct_owner_message(message: dict, owner: str) -> dict:
    source_id = normalize_message_id(str(message.get("message_id") or ""))
    dedupe_key = direct_owner_dedupe_key(message, owner)
    report_target = direct_owner_report_target(owner)
    base = {
        "source_message_id": source_id,
        "dedupe_key": dedupe_key,
        "owner": owner,
        "completion_target": "visible-worker-completion-or-blocker",
        "report_target": report_target,
    }
    if looks_like_no_action_direct(message):
        return {
            **base,
            "classification": "direct-owner-no-action",
            "decision": "logged-no-action",
            "current_state": "no_action_logged",
            "archivable_now": True,
        }
    if looks_like_sensitive_or_suspicious(message):
        return {
            **base,
            "classification": "direct-owner-security-gated",
            "decision": "security-guard-route-required-before-handling",
            "current_state": "blocked_pending_security_guard",
            "archivable_now": False,
        }
    if reply_to_prior_direct_owner_email(load_avignon_sent_logs(), message, owner):
        return {
            **base,
            "classification": "direct-owner-reply-to-prior-report",
            "decision": "direct-owner-prior-report-reply-filed-no-resend",
            "current_state": "completed_report_sent",
            "archivable_now": True,
        }
    try:
        route = create_visible_direct_owner_route(message, owner)
        in_reply_to, references = source_thread_headers(message)
        ack_body = compose_direct_owner_ack(message, owner, route)
        ack_message_id = send_avignon_owner_email(
            direct_owner_reply_subject(str(message.get("subject") or "")),
            ack_body,
            f"{dedupe_key}-ack",
            report_target["to"],
            report_target["cc"],
            in_reply_to=in_reply_to,
            references=references,
        )
    except Exception as exc:
        blocker = redact_sensitive_text(str(exc))
        if "409" in blocker or "conflict" in blocker.casefold():
            existing_open = find_open_direct_owner_session(direct_owner_task_title(message, owner))
            if existing_open:
                return {
                    **base,
                    "classification": "direct-owner-route-reused-open-session",
                    "decision": "direct-owner-existing-open-route-reused",
                    "current_state": "routed_pending_completion",
                    "routed_workspace": str(existing_open.get("workspace_key") or "avignon"),
                    "routed_session_id": str(existing_open.get("id") or ""),
                    "routed_session_title": str(existing_open.get("title") or ""),
                    "route_blocker": blocker,
                    "archivable_now": False,
                }
            prior_session = find_closed_direct_owner_session(
                str(message.get("subject", "")),
                owner,
            )
            if prior_session:
                prior_work_state = prior_session.get("work_state") or {}
                return {
                    **base,
                    "classification": "direct-owner-route-duplicate-closed",
                    "decision": "direct-owner-duplicate-already-closed-no-resend",
                    "current_state": "completed_report_sent",
                    "routed_workspace": str(prior_session.get("workspace_key") or "avignon"),
                    "routed_session_id": str(prior_session.get("id") or ""),
                    "routed_session_title": str(prior_session.get("title") or ""),
                    "closeout_proof_marker": str(prior_work_state.get("proof_marker") or ""),
                    "route_blocker": blocker,
                    "archivable_now": True,
                }
        if direct_owner_closeout_already_sent(load_sent_log(SENT_LOG), base):
            return {
                **base,
                "classification": "direct-owner-route-blocked-already-reported",
                "decision": "direct-owner-route-blocked-already-reported-no-resend",
                "current_state": "blocked_report_sent",
                "route_blocker": blocker,
                "archivable_now": True,
            }
        blocker_lower = blocker.casefold()
        if (
            "timed out" in blocker_lower
            or "timeout" in blocker_lower
            or "409" in blocker_lower
            or "conflict" in blocker_lower
        ):
            return {
                **base,
                "classification": "direct-owner-route-local-retry",
                "decision": "direct-owner-route-blocked-local-no-email",
                "current_state": "captured_route_blocked_local_retry",
                "route_blocker": blocker,
                "archivable_now": False,
            }
        greeting = "Hi Robert," if owner == "robert-approver" else "Hi Sonat,"
        blocker_body = "\n".join(
            [
                greeting,
                "",
                f"Captured but blocked: {normalized_subject(message.get('subject', '')) or 'direct request'}.",
                "",
                "What was done: I recognized this as direct Avignon work and recorded the source/dedupe state.",
                f"What changed: the item is blocked before visible worker routing; blocker: {blocker}",
                "What was not done: I did not file the source message to Handled, make CRM/Portal/OPS changes, send external replies, or guess at account/pricing/duplicate handling.",
                "Next: Task Manager or Security Guard should restore/approve the visible route path, then Avignon can route and follow through.",
            ]
        )
        in_reply_to, references = source_thread_headers(message)
        blocker_message_id = send_avignon_owner_email(
            direct_owner_reply_subject(str(message.get("subject") or "")),
            blocker_body,
            f"{dedupe_key}-route-blocked",
            report_target["to"],
            report_target["cc"],
            in_reply_to=in_reply_to,
            references=references,
        )
        return {
            **base,
            "classification": "direct-owner-route-blocked",
            "decision": "direct-owner-route-blocked-report-sent",
            "current_state": "captured_route_blocked_report_sent",
            "route_blocker": blocker,
            "blocker_message_id": blocker_message_id,
            "archivable_now": False,
        }
    return {
        **base,
        "classification": "direct-owner-work-request",
        "decision": "routed-direct-owner-ack-sent",
        "current_state": "routed_pending_completion",
        "routed_workspace": route["workspace"],
        "routed_session_id": route["session_id"],
        "routed_session_title": route["session_title"],
        "prompt_delivery": route["prompt_delivery"],
        "ack_message_id": ack_message_id,
        "archivable_now": False,
    }


def board_session_status(session_id: str) -> dict | None:
    if not session_id:
        return None
    payload = get_json("/api/status")
    for session in payload.get("managed_sessions", []) or []:
        if isinstance(session, dict) and session.get("id") == session_id:
            return session
    return None


def find_open_direct_owner_session(expected_title: str) -> dict | None:
    expected = str(expected_title or "").strip().casefold()
    if not expected:
        return None
    payload = get_json("/api/status")
    for session in payload.get("managed_sessions", []) or []:
        if not isinstance(session, dict):
            continue
        title = str(session.get("title") or "").strip().casefold()
        if title != expected:
            continue
        status = str(session.get("status") or "").strip().lower()
        if status in {"finished", "blocked", "closed"}:
            continue
        return session
    return None


def find_closed_direct_owner_session(subject: str, owner: str) -> dict | None:
    subject_text = normalized_subject(subject).strip()
    if not subject_text:
        return None
    owner_label = "Robert" if owner == "robert-approver" else "Sonat"
    expected_title = f"Avignon direct {owner_label}: {subject_text}".casefold()
    payload = get_json("/api/status")
    for session in payload.get("closed_sessions", []) or []:
        if not isinstance(session, dict):
            continue
        title = str(session.get("title") or "").strip().casefold()
        if title != expected_title:
            continue
        work_state = session.get("work_state") or {}
        if (
            str(work_state.get("state") or "") == "closed_with_proof"
            or str(work_state.get("proof_marker") or "")
            or session.get("closed_at")
        ):
            return session
    return None


def board_session_summary(session_id: str) -> dict | None:
    if not session_id:
        return None
    query = urllib.parse.urlencode({"session_id": session_id})
    try:
        payload = get_json(f"/api/session-summary?{query}")
    except Exception:
        payload = None
    if isinstance(payload, dict) and payload:
        return payload
    session = board_session_status(session_id)
    if not isinstance(session, dict):
        return None
    work_state = session.get("work_state") if isinstance(session.get("work_state"), dict) else {}
    summary_parts = [
        str(session.get("blocker") or work_state.get("blocker_text") or "").strip(),
        str(session.get("owner_question") or work_state.get("owner_question") or "").strip(),
    ]
    summary = " ".join(part for part in summary_parts if part).strip()
    if not summary:
        return None
    return {"summary": summary}


def session_blocker_text(session: dict, session_summary: dict | None = None) -> str:
    summary_text = str((session_summary or {}).get("summary") or "").strip()
    if summary_text:
        return summary_text
    work_state = session.get("work_state") if isinstance(session.get("work_state"), dict) else {}
    return str(session.get("blocker") or work_state.get("blocker_text") or "").strip()


def session_owner_question_text(session: dict) -> str:
    work_state = session.get("work_state") if isinstance(session.get("work_state"), dict) else {}
    return str(session.get("owner_question") or work_state.get("owner_question") or "").strip()


def clarification_request_text(subject: str, summary_text: str) -> str:
    cleaned_subject = " ".join(str(subject or "").split()).strip()
    cleaned_summary = " ".join(str(summary_text or "").split()).strip()
    patterns = [
        r"(?:what i need from you|remaining blocker|remaining decision|next approval\/action needed|clarification needed)\s*:\s*(.+)",
        r"(please reply with .+?[.?!])",
        r"(confirm whether .+?[.?!])",
        r"(provide .+?[.?!])",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned_summary, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    if cleaned_summary == "":
        return (
            f'I only have the subject "{cleaned_subject or "this request"}" preserved in the current route, '
            "not the original request details. Please reply with the exact action you want handled."
        )
    generic_subjects = {"project", "update", "status", "backup", "external", "avignon", "2 items", "new role"}
    if cleaned_subject.lower() in generic_subjects or len(cleaned_subject.split()) <= 2:
        return f'Please reply with the exact project/task name, the workflow to automate or improve, the desired outcome, and the next action for "{cleaned_subject or "this request"}".'
    return f'Please reply with the missing workflow/target details or exact next step for "{cleaned_subject or "this request"}".'


def session_summary_has_active_context(summary_text: str) -> bool:
    cleaned = " ".join(str(summary_text or "").split()).lower()
    if not cleaned:
        return False
    signals = (
        "task #",
        "queued",
        "in progress",
        "awaiting review",
        "already tracking",
        "existing task",
        "access packet",
        "will send",
        "specialists will",
        "planner task",
    )
    return any(signal in cleaned for signal in signals)


def compose_owner_style_status(subject: str, session_id: str, session_title: str, state: str, summary_text: str, owner: str) -> str:
    normalized = normalized_subject(subject) or subject or "this request"
    greeting = "Hi Robert," if owner == "robert-approver" else "Hi Sonat,"
    if owner != "robert-approver":
        return "\n".join(
            [
                greeting,
                "",
                f"I am still working on {normalized}.",
                "",
                "No reply is needed from you unless the scope has changed. I will come back with the next useful update when it is finished or when there is one clear blocker.",
                "",
                "Best,",
            ]
        ).rstrip() + "\n"
    status_line = f"I am continuing {normalized} through the existing work lane {session_id} / {session_title}."
    if session_summary_has_active_context(summary_text):
        next_line = "No reply is needed from you unless the scope changed; I will send the next concrete update when the active task advances or reaches a real blocker."
    else:
        next_line = "I will send the next concrete update when the active task advances or reaches a real blocker."
    return "\n".join(
        [
            greeting,
            "",
            status_line,
            f"Current worker state: {state}.",
            next_line,
        ]
    ).rstrip() + "\n"


def closeout_text_to_html(body: str) -> str:
    paragraphs = []
    for block in str(body or "").rstrip().split("\n\n"):
        lines = [html.escape(line) for line in block.splitlines()]
        if not lines:
            continue
        paragraphs.append("<p>" + "<br>\n".join(lines) + "</p>")
    return "\n".join(paragraphs)


def compose_direct_owner_closeout(action: dict, session: dict, blocked: bool, session_summary: dict | None = None) -> str:
    subject = str(action.get("subject") or "direct-owner request")
    state = str(session.get("status_label") or session.get("status") or "unknown")
    session_id = str(action.get("routed_session_id") or "")
    session_title = str(action.get("routed_session_title") or session.get("title") or session.get("display_name") or "")
    greeting = "Hi Robert," if str(action.get("owner") or "") == "robert-approver" else "Hi Sonat,"
    summary_text = session_blocker_text(session, session_summary)
    owner_question_text = session_owner_question_text(session)
    if str(action.get("owner") or "") != "robert-approver":
        if blocked and session_summary_has_active_context(summary_text):
            return compose_owner_style_status(subject, session_id, session_title, state, summary_text, str(action.get("owner") or "sonat"))
        blocker_text = summary_text or "I do not yet have one preserved blocker line in mailbox state."
        lines = [
            greeting,
            "",
            (
                f"I need one more piece before I can finish {normalized_subject(subject) or subject}."
                if blocked
                else f"{normalized_subject(subject) or subject} is complete."
            ),
            "",
        ]
        if blocked:
            lines.extend(
                [
                    f"Current blocker: {blocker_text}",
                    "",
                    clarification_request_text(subject, summary_text),
                ]
            )
        else:
            lines.extend(
                [
                    "I have closed the follow-through on my side.",
                    "No external reply, credential/auth work, or unapproved CRM/Portal/OPS change was made by the mailbox monitor.",
                ]
            )
        lines.extend(["", "Best,"])
        return "\n".join(lines).rstrip() + "\n"
    lines = [
        greeting,
        "",
        (
            f"Clarification needed: {normalized_subject(subject) or subject}."
            if blocked
            else f"Closeout: {normalized_subject(subject) or subject}."
        ),
        "",
        f"- Visible session: {session_id} / {session_title}",
        f"- Current worker state: {state}",
    ]
    if blocked and session_summary_has_active_context(summary_text):
        return compose_owner_style_status(subject, session_id, session_title, state, summary_text, str(action.get("owner") or "sonat"))
    if blocked:
        clarification = owner_question_text or clarification_request_text(subject, summary_text)
        lines.extend(
            [
                f"I already have this linked to visible session {session_id} / {session_title}.",
                f"Blocker: {summary_text or 'I do not yet have the concrete blocker text preserved in mailbox state.'}",
                clarification,
            ]
        )
    else:
        lines.extend(
            [
                f"I closed the mailbox follow-through against visible session {session_id} / {session_title}.",
                "No extra external reply, credential/auth work, or unapproved CRM/Portal/OPS mutation was performed by the mailbox runtime.",
                "No further owner decision is recorded in mailbox state.",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def compose_direct_owner_closeout_html(action: dict, session: dict, blocked: bool, session_summary: dict | None = None) -> str:
    body = compose_direct_owner_closeout(action, session, blocked, session_summary)
    return (
        "<html><body style=\"font-family:Arial,sans-serif;font-size:14px;line-height:1.5;color:#111;\">"
        + closeout_text_to_html(body)
        + "</body></html>"
    )


def monitor_direct_owner_action(action: dict, user: str | None = None, app_pw: str | None = None) -> dict:
    state = str(action.get("current_state") or "")
    reported_closeout = direct_owner_closeout_report(load_avignon_sent_logs(), action)
    reported_state = str(reported_closeout.get("state") or "")
    reported_message_id = str(reported_closeout.get("message_id") or "")
    if state in DIRECT_OWNER_DONE_STATES:
        return {"monitor_state": state, "current_state": state, "archivable_now": True}
    if reported_state or state in {"blocked_report_sent", "completed_report_sent"} or action.get("blocker_message_id") or action.get("completion_message_id"):
        report_is_blocked = reported_state == "blocked_report_sent" or action.get("blocker_message_id")
        return {
            "monitor_state": "already-reported",
            "current_state": reported_state or state or ("blocked_report_sent" if action.get("blocker_message_id") else "completed_report_sent"),
            "session_status": "blocked" if report_is_blocked else "finished",
            "blocker_message_id": reported_message_id if report_is_blocked else "",
            "completion_message_id": reported_message_id if not report_is_blocked else "",
            "archivable_now": True,
        }
    if state not in DIRECT_OWNER_PENDING_STATES:
        return {"monitor_state": "not-pending"}
    try:
        session = board_session_status(str(action.get("routed_session_id") or ""))
    except Exception as exc:
        return {
            "monitor_state": "session-status-unavailable",
            "current_state": "routed_pending_completion",
            "archivable_now": False,
            "status_blocker": redact_sensitive_text(str(exc))[:240],
        }
    if not session:
        reroute_message = {
            "message_id": str(action.get("source_message_id") or ""),
            "subject": str(action.get("subject") or ""),
            "from": str(action.get("from") or ""),
            "date": str(action.get("date") or ""),
            "body": "",
        }
        if user and app_pw and str(action.get("source_message_id") or ""):
            fetched = fetch_message_by_message_id(user, app_pw, str(action.get("source_message_id") or ""))
            if isinstance(fetched, dict):
                reroute_message.update({
                    "subject": str(fetched.get("subject") or reroute_message["subject"]),
                    "from": str(fetched.get("from") or reroute_message["from"]),
                    "date": str(fetched.get("date") or reroute_message["date"]),
                    "body": str(fetched.get("body") or ""),
                })
        try:
            repaired_route = create_visible_direct_owner_route(reroute_message, str(action.get("owner") or "sonat"))
        except Exception as exc:
            return {
                "monitor_state": "route-missing-local-retry",
                "current_state": state,
                "session_status": "route-missing",
                "archivable_now": False,
                "status_blocker": redact_sensitive_text(str(exc))[:240],
            }
        return {
            "monitor_state": "route-recreated",
            "current_state": state,
            "session_status": "working",
            "archivable_now": False,
            "routed_workspace": repaired_route.get("workspace") or "avignon",
            "routed_session_id": repaired_route.get("session_id") or "",
            "routed_session_title": repaired_route.get("session_title") or "",
            "prompt_delivery": repaired_route.get("prompt_delivery") if isinstance(repaired_route.get("prompt_delivery"), dict) else {},
            "routed_at": time.time(),
        }
    session_state = str(session.get("status") or "").lower()
    if session_state not in {"finished", "blocked"}:
        return {"monitor_state": "still-pending", "current_state": state, "session_status": session_state}
    blocked = session_state == "blocked"
    session_summary = board_session_summary(str(action.get("routed_session_id") or ""))
    summary_text = str((session_summary or {}).get("summary") or "").strip()
    if blocked and not summary_text and user and app_pw:
        fetched = fetch_message_by_message_id(user, app_pw, str(action.get("source_message_id") or ""))
        fetched_body = str((fetched or {}).get("body") or "").strip()
        if fetched_body:
            session_summary = {**(session_summary or {}), "summary": fetched_body}
    target = direct_owner_report_target(str(action.get("owner") or "sonat"))
    closeout_state = "blocked_report_sent" if blocked else "completed_report_sent"
    task_id = f"{action.get('dedupe_key', 'avignon-direct-owner')}-{closeout_state}"
    message_id = send_avignon_owner_email(
        direct_owner_reply_subject(str(action.get("subject") or "")),
        compose_direct_owner_closeout(action, session, blocked, session_summary),
        task_id,
        str(target.get("to") or SONAT_EMAIL),
        str(target.get("cc") or ""),
        in_reply_to=str(action.get("source_message_id") or ""),
        references=str(action.get("source_message_id") or ""),
        html_body=compose_direct_owner_closeout_html(action, session, blocked, session_summary),
    )
    return {
        "monitor_state": closeout_state,
        "current_state": closeout_state,
        "session_status": session_state,
        "completion_message_id": message_id,
        "archivable_now": True,
    }


def direct_owner_closeout_already_sent(sent_log: dict[str, dict], action: dict) -> bool:
    dedupe_key = str(action.get("dedupe_key") or "").strip()
    if not dedupe_key:
        return False
    prefixes = (
        f"{dedupe_key}-blocked_report_sent",
        f"{dedupe_key}-completed_report_sent",
        f"{dedupe_key}-captured_route_blocked_report_sent",
    )
    for row in sent_log.values():
        task_id = str(row.get("task_id") or "")
        if any(task_id.startswith(prefix) for prefix in prefixes):
            return True
    return False


def load_avignon_sent_logs() -> dict[str, dict]:
    sent_log = load_sent_log(SENT_LOG)
    runtime_sent_log = Path("/Users/admin/.avignon-launch/state/sent-log.jsonl")
    if runtime_sent_log != SENT_LOG and runtime_sent_log.exists():
        sent_log.update(load_sent_log(runtime_sent_log))
    return sent_log


def reply_to_prior_direct_owner_email(sent_log: dict[str, dict], message: dict, owner: str) -> bool:
    refs_raw = " ".join(
        [
            str(message.get("in_reply_to") or ""),
            str(message.get("references") or ""),
        ]
    )
    referenced_ids = {
        normalize_message_id(match)
        for match in re.findall(r"<[^>]+>", refs_raw)
        if normalize_message_id(match)
    }
    if not referenced_ids:
        return False
    owner_prefix = f"avignon-direct-owner-{owner}-"
    for row in sent_log.values():
        if normalize_message_id(str(row.get("message_id") or "")) not in referenced_ids:
            continue
        task_id = str(row.get("task_id") or "")
        sender_path = str(row.get("sender_path") or "")
        if task_id.startswith(owner_prefix) and "avignon:" in sender_path:
            return True
    return False


def direct_owner_closeout_state(sent_log: dict[str, dict], action: dict) -> str:
    return str(direct_owner_closeout_report(sent_log, action).get("state") or "")


def direct_owner_closeout_report(sent_log: dict[str, dict], action: dict) -> dict:
    dedupe_key = str(action.get("dedupe_key") or "").strip()
    if not dedupe_key:
        return {}
    source_ref = normalize_message_id(str(action.get("source_message_id") or ""))
    blocked_suffixes = (
        "blocked_report_sent",
        "captured_route_blocked_report_sent",
        "external-send-blocker",
        "blocker_report_sent",
    )
    completed_suffixes = (
        "completed_report_sent",
        "correction_report_sent",
        "draft-ready",
    )
    prefix = f"{dedupe_key}-"
    for row in sent_log.values():
        task_id = str(row.get("task_id") or "")
        if not task_id.startswith(prefix):
            continue
        suffix = task_id[len(prefix):]
        message_id = str(row.get("message_id") or "")
        if suffix in blocked_suffixes:
            return {"state": "blocked_report_sent", "message_id": message_id}
        if suffix in completed_suffixes:
            return {"state": "completed_report_sent", "message_id": message_id}
    if source_ref:
        for row in sent_log.values():
            refs = " ".join([
                str(row.get("in_reply_to") or ""),
                str(row.get("references") or ""),
            ])
            referenced_ids = {
                normalize_message_id(match)
                for match in re.findall(r"<[^>]+>", refs)
                if normalize_message_id(match)
            }
            if source_ref not in referenced_ids:
                continue
            task_id = str(row.get("task_id") or "").lower()
            message_id = str(row.get("message_id") or "")
            if any(token in task_id for token in ("blocker", "blocked", "external-send-blocker")):
                return {"state": "blocked_report_sent", "message_id": message_id}
            if any(token in task_id for token in ("completed", "correction", "draft-ready")):
                return {"state": "completed_report_sent", "message_id": message_id}
    return {}


def is_direct_owner_action(action: dict) -> bool:
    classification = str(action.get("classification") or "")
    decision = str(action.get("decision") or "")
    current_state = str(action.get("current_state") or "")
    return bool(
        classification.startswith("direct-owner")
        or classification.startswith("previously-logged-direct-owner")
        or decision.startswith("direct-owner")
        or decision.startswith("routed-direct-owner")
        or current_state in DIRECT_OWNER_PENDING_STATES
        or current_state in DIRECT_OWNER_DONE_STATES
        or str(action.get("dedupe_key") or "").startswith("avignon-direct-owner-")
    )


def should_archive_after_route(classification: str, decision: str) -> bool:
    if classification in {
        "assistant-decision-email-reply",
        "calendar-directive",
        "tracked-primary-thread-instruction",
        "notification",
        "assistant-self-mail",
        "tracked-reply-info",
    }:
        return True
    return decision in {
        "logged-no-action",
        "logged-local-follow-up-no-new-decision-email",
        "logged-local-follow-up-no-primary-review",
    }


def message_datetime(message: dict) -> datetime:
    try:
        parsed = parsedate_to_datetime(message.get("date", ""))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=CENTRAL)
        return parsed.astimezone(CENTRAL)
    except Exception:
        return datetime.now(CENTRAL)


def next_weekday(base: datetime, weekday: int) -> datetime:
    days = (weekday - base.weekday()) % 7
    if days == 0:
        days = 7
    return base + timedelta(days=days)


def calendar_directive_start(message: dict) -> datetime | None:
    body = str(message.get("body") or "")
    lowered = f"{message.get('subject', '')} {body}".lower()
    base = message_datetime(message)
    weekday_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    target = None
    for name, idx in weekday_map.items():
        if re.search(rf"\b{name}\b", lowered):
            target = next_weekday(base, idx)
            break
    if target is None:
        return None
    hour = 10 if "morning" in lowered else 10
    return target.replace(hour=hour, minute=0, second=0, microsecond=0)


def is_sonat_robert_calendar_directive(message: dict, assistant_email: str) -> bool:
    if sender_email(message.get("from", "")) != "sonat@kovaldistillery.com":
        return False
    if is_copied_only(message, assistant_email):
        return False
    text = f"{message.get('subject', '')} {message.get('body', '')}".lower()
    if re.search(r"\b(did not ask|do not|don't|refrain|stop|please refrain|unless i tell you otherwise)\b", text):
        return False
    if "robert" not in text:
        return False
    if not re.search(r"\b(meeting|calendar|invite|schedule|create|set up|add)\b", text):
        return False
    direct_avignon_request = re.search(
        r"\bavignon\b[^.?!]{0,120}\b(please|can you|could you|would you|need you to)\b[^.?!]{0,120}\b(schedule|create|invite|set up|add)\b[^.?!]{0,120}\b(meeting|calendar|invite)\b[^.?!]{0,120}\brobert\b",
        text,
    ) or re.search(
        r"\b(please|can you|could you|would you|need you to)\b[^.?!]{0,120}\bavignon\b[^.?!]{0,120}\b(schedule|create|invite|set up|add)\b[^.?!]{0,120}\b(meeting|calendar|invite)\b[^.?!]{0,120}\brobert\b",
        text,
    )
    if explicitly_requests_assistant_action(message, "Avignon", assistant_email) and direct_avignon_request:
        return True
    if is_reply_or_forward_subject(str(message.get("subject") or "")):
        return False
    return bool(direct_avignon_request)


def find_existing_calendar_event(calendar_id: str, source_message_id: str, start_at: datetime) -> dict | None:
    client_config = load_client_config(GOOGLE_CAL_CLIENT)
    token_payload = ensure_valid_token(client_config, GOOGLE_CAL_TOKEN)
    day_start = start_at.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    payload = calendar_request(
        token_payload,
        "GET",
        f"/calendars/{urllib.parse.quote(calendar_id, safe='')}/events",
        query={
            "timeMin": day_start.isoformat(),
            "timeMax": day_end.isoformat(),
            "singleEvents": "true",
            "orderBy": "startTime",
            "q": "Meeting with Robert",
            "maxResults": "20",
        },
    )
    for event in payload.get("items", []):
        description = str(event.get("description") or "")
        attendees = [str(item.get("email") or "").lower() for item in event.get("attendees", [])]
        if source_message_id and source_message_id in description:
            return event
        if "robert@kovaldistillery.com" in attendees and (event.get("summary") or "").lower() == "meeting with robert":
            return event
    return None


def calendar_confirmation_task_id(start_at: datetime) -> str:
    return f"avignon-sonat-meeting-with-robert-{start_at.strftime('%Y-%m-%d-%H%M')}"


def calendar_confirmation_already_sent(sent_log: dict[str, dict], start_at: datetime) -> bool:
    task_id = calendar_confirmation_task_id(start_at)
    for row in sent_log.values():
        if (row.get("task_id") or "") == task_id:
            return True
    return False


def send_calendar_confirmation(start_at: datetime, event: dict, source_message_id: str) -> str:
    drafts_dir = Path(os.environ.get("AVIGNON_DRAFTS_DIR", "/Users/admin/.avignon-launch/state/drafts")).expanduser()
    drafts_dir.mkdir(parents=True, exist_ok=True)
    body_path = drafts_dir / f"sonat-meeting-with-robert-confirmation-{start_at.strftime('%Y-%m-%d')}.txt"
    body = "\n".join(
        [
            "Hi Sonat,",
            "",
            "Done. I created the meeting with Robert.",
            "",
            "- Calendar: sonat@kovaldistillery.com",
            f"- Time: {start_at.strftime('%A, %B %-d, %Y, %-I:%M')} - {(start_at + timedelta(minutes=30)).strftime('%-I:%M %p')} Central",
            "- Title: Meeting with Robert",
            "- Invitee: robert@kovaldistillery.com",
            f"- Calendar link: {event.get('htmlLink', '')}",
            "",
            "Robert was invited through Google Calendar.",
        ]
    ).rstrip() + "\n"
    body_path.write_text(body, encoding="utf-8")
    task_id = calendar_confirmation_task_id(start_at)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "send_frank_email.py"),
            "--assistant",
            "avignon",
            "--to",
            "sonat@kovaldistillery.com",
            "--subject",
            "Meeting with Robert scheduled",
            "--body-file",
            str(body_path),
            "--task-id",
            task_id,
        ],
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "AVIGNON_CREDS_FILE": str(CREDS),
            "AVIGNON_SENT_LOG": str(SENT_LOG),
            "AI_WORKSPACE_ROOT": str(AI_ROOT),
        },
        timeout=45,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Avignon confirmation send failed")
    return task_id


def handle_sonat_robert_calendar_directive(message: dict, sent_log: dict[str, dict]) -> str:
    calendar_id = "sonat@kovaldistillery.com"
    source_message_id = str(message.get("message_id") or "")
    start_at = calendar_directive_start(message)
    if start_at is None:
        return "calendar-directive-needs-specific-date"
    existing = find_existing_calendar_event(calendar_id, source_message_id, start_at)
    if existing:
        if calendar_confirmation_already_sent(sent_log, start_at):
            return "calendar-directive-existing-event-no-new-email"
        send_calendar_confirmation(start_at, existing, source_message_id)
        return "calendar-directive-existing-event-confirmation-sent"

    client_config = load_client_config(GOOGLE_CAL_CLIENT)
    token_payload = ensure_valid_token(client_config, GOOGLE_CAL_TOKEN)
    end_at = start_at + timedelta(minutes=30)
    event = calendar_request(
        token_payload,
        "POST",
        f"/calendars/{urllib.parse.quote(calendar_id, safe='')}/events",
        query={"sendUpdates": "all"},
        body={
            "summary": "Meeting with Robert",
            "description": f"Created by Avignon from Sonat email directive. Source Message-ID: {source_message_id}",
            "start": {"dateTime": start_at.isoformat(), "timeZone": "America/Chicago"},
            "end": {"dateTime": end_at.isoformat(), "timeZone": "America/Chicago"},
            "attendees": [{"email": "robert@kovaldistillery.com"}],
        },
    )
    if calendar_confirmation_already_sent(sent_log, start_at):
        return "calendar-directive-event-created-no-new-email"
    send_calendar_confirmation(start_at, event, source_message_id)
    return "calendar-directive-event-created-confirmation-sent"


def route_message(message: dict, sent_log: dict, assistant_email: str) -> tuple[str, str, list[str]]:
    from_email = sender_email(message.get("from", ""))
    subject = message.get("subject", "")
    lowered = f"{subject} {from_email}".lower()
    decision_items: list[str] = []

    if is_copied_only(message, assistant_email) and not explicitly_requests_assistant_action(
        message,
        "Avignon",
        assistant_email,
    ):
        body = " ".join(str(message.get("body") or "").split()).lower()
        if re.fullmatch(r"(ok|okay|thanks|thank you|ok thanks|okay thanks|ok thank you|got it|sounds good|done)[.! ]*", body):
            return "tracked-reply-info", "logged-no-action", decision_items
        return "cc-fyi-no-action", "logged-no-action", decision_items

    if is_sonat_robert_calendar_directive(message, assistant_email):
        decision = handle_sonat_robert_calendar_directive(message, sent_log)
        return "calendar-directive", decision, decision_items

    if is_decision_email_reply(message):
        return "assistant-decision-email-reply", "logged-local-follow-up-no-new-decision-email", decision_items

    if (
        "google" in from_email
        or "accounts.google.com" in from_email
        or "device-management" in from_email
        or re.search(r"security alert|work account access|account access", lowered)
    ):
        item_id = "avignon-google-account-security-notifications-2026-04-12"
        message_id = record_decision_item(
            item_id,
            "Avignon received Google account/security or device-management notifications.",
            "Robert or the approved Google Workspace/admin path should verify whether the notifications are expected.",
            "Confirm expected/handled, or treat as security follow-up.",
        )
        decision_items.append(item_id)
        decision = "sent-decision-email-to-sonat" if message_id else "recorded-decision-item-no-email"
        return "security-account-notification", decision, decision_items

    if (
        from_email == "sonat@kovaldistillery.com"
        and message.get("attachments")
        and re.search(r"crm|account|contact|add to crm|create an account", lowered)
    ):
        item_id = "avignon-crm-lj-hospitality-jamie-gilmore-2026-04-12"
        message_id = record_decision_item(
            item_id,
            "Sonat asked Avignon to create or update CRM account/contact data from an email with an attachment.",
            "Use an approved CRM/Portal path to inspect the attachment and prepare exact fields before any write.",
            "Confirm whether Avignon should proceed under the low-risk internal rule, or hold for explicit CRM data-entry approval.",
        )
        decision_items.append(item_id)
        decision = "sent-decision-email-to-sonat" if message_id else "recorded-decision-item-no-email"
        return "crm-write-from-attachment", decision, decision_items

    classification, _ = classify_message(
        message,
        sent_log,
        SONAT_EMAIL,
        assistant_email,
        "Avignon",
    )
    owner = direct_owner_kind(message, classification)
    if owner:
        direct_action = handle_direct_owner_message(message, owner)
        DIRECT_OWNER_ACTIONS[normalize_message_id(str(message.get("message_id") or ""))] = direct_action
        decision_item = direct_action["dedupe_key"]
        decision_items.append(decision_item)
        return direct_action["classification"], direct_action["decision"], decision_items
    if classification == "tracked-primary-thread-instruction":
        return classification, "logged-local-follow-up-no-primary-review", decision_items

    if classification in {"notification", "assistant-self-mail", "tracked-reply-info", "primary-test", "tracked-reply"}:
        return classification, "logged-no-action", decision_items

    slug = subject_slug(subject)
    item_id = f"avignon-email-review-{slug}"
    if decision_thread_exists(slug, sent_log):
        decision_items.append(item_id)
        return "duplicate-ambiguous-email-review", "existing-decision-thread-no-new-email", decision_items
    message_id = record_decision_item(
        item_id,
        f"Avignon received an email that was not clearly safe to auto-handle. Subject: {subject}",
        "Review the message in the approved mailbox/workspace context and decide whether to route, reply, or hold.",
        "Confirm the owner/action for this email-derived item.",
    )
    decision_items.append(item_id)
    decision = "sent-decision-email-to-sonat" if message_id else "recorded-decision-item-no-email"
    return "ambiguous-email-review", decision, decision_items


def main() -> int:
    user, app_pw = load_credentials(CREDS)
    sent_log = load_sent_log(SENT_LOG)
    seen = load_seen_ids_db_first()
    automation_actions = load_automation_actions()
    messages = fetch_inbox(user, app_pw, seen)
    actions: list[dict] = []
    decision_items: list[str] = []
    archived_count = 0

    for message in messages:
        source_id = normalize_message_id(message.get("message_id", ""))
        if source_id in seen:
            previous = latest_action_for_source(automation_actions, source_id) or {}
            inferred_owner = direct_owner_kind(message, str(previous.get("classification") or ""))
            previous_direct_owner = is_direct_owner_action(previous) or bool(inferred_owner)
            if is_direct_owner_action(previous):
                monitor_result = monitor_direct_owner_action(previous, user, app_pw)
                if monitor_result.get("archivable_now"):
                    archive_candidate = {
                        **previous,
                        **monitor_result,
                        "source_message_id": source_id,
                        "subject": message.get("subject", ""),
                        "from": message.get("from", ""),
                    }
                    if task_flow_allows_archive(archive_candidate):
                        archived = archive_email(user, app_pw, source_id, "Handled")
                    else:
                        archived = False
                        monitor_result.update({
                            "archivable_now": False,
                            "task_flow_archive_blocked": True,
                            "task_flow_missing_fields": archive_candidate.get("task_flow_missing_fields", []),
                        })
                else:
                    archived = False
            elif previous_direct_owner:
                monitor_result = {
                    "monitor_state": "direct-owner-preventive-hold",
                    "current_state": "routed_pending_completion",
                    "archivable_now": False,
                    "status_blocker": "Previously logged Sonat/Robert instruction lacks direct-owner closeout proof; keep visible until completion or blocker report.",
                }
                archived = False
            else:
                monitor_result = {}
                archived = archive_email(user, app_pw, source_id, "Handled")
            archived_count += int(bool(archived))
            if (
                previous_direct_owner
                and not monitor_result.get("archivable_now")
                and not archived
            ):
                decision = "direct-owner-route-still-open-not-filed"
                classification = "previously-logged-direct-owner-pending"
            elif monitor_result.get("archivable_now"):
                decision = "direct-owner-report-sent-filed-to-handled" if archived else "direct-owner-report-sent-archive-not-found"
                classification = "previously-logged-direct-owner-closed"
            else:
                decision = "filed-previously-logged-to-handled" if archived else "previously-logged-not-archived"
                classification = "previously-logged-inbox-residue"
            action = {
                "source_message_id": source_id,
                "classification": classification,
                "subject": message.get("subject", ""),
                "from": message.get("from", ""),
                "date": message.get("date", ""),
                "decision": decision,
                "archived": bool(archived),
                **{
                    key: previous[key]
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
                        "ack_message_id",
                        "route_blocker",
                        "blocker_message_id",
                    )
                    if key in previous
                },
                **monitor_result,
            }
            record_task_flow_event(action, "avignon_previous_message_reconciled")
            actions.append(action)
            continue

        classification, decision, new_items = route_message(message, sent_log, user)
        decision_items.extend(new_items)
        archived = False
        if should_archive_after_route(classification, decision):
            archived = archive_email(user, app_pw, source_id, "Handled")
        archived_count += int(bool(archived))
        action = {
            "source_message_id": source_id,
            "classification": classification,
            "subject": message.get("subject", ""),
            "from": message.get("from", ""),
            "date": message.get("date", ""),
            "decision": decision,
            "archived": bool(archived),
            "decision_items": new_items,
        }
        if classification.startswith("direct-owner"):
            direct_action = DIRECT_OWNER_ACTIONS.get(source_id, {})
            if direct_action:
                action.update(direct_action)
                action["archived"] = bool(archived)
                action["decision_items"] = new_items
            else:
                owner = "robert-approver" if looks_like_robert_avignon_instruction(message) else "sonat"
                action.update(
                    {
                        "dedupe_key": direct_owner_dedupe_key(message, owner),
                        "owner": owner,
                        "routed_workspace": "avignon" if decision == "routed-direct-owner-ack-sent" else "",
                        "current_state": "routed_pending_completion" if decision == "routed-direct-owner-ack-sent" else "",
                        "completion_target": "visible-worker-completion-or-blocker",
                        "report_target": direct_owner_report_target(owner),
                    }
                )
        record_task_flow_event(action, "avignon_message_action")
        actions.append(action)

    row = {
        "classification": "monitor-cycle",
        "mailbox": "avignon",
        "inbox_count_start": len(messages),
        "handled_archived_count": archived_count,
        "message_actions": actions,
        "decision_items": sorted(set(decision_items)),
        "machine": machine_label(),
        "logged_by": "Codex RobertMBP-2.local",
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    append_log(row)
    final_count = fetch_inbox_count(user, app_pw)
    print(
        json.dumps(
            {
                "checked_at": row["logged_at"],
                "inbox_count_start": len(messages),
                "inbox_count_end": final_count,
                "handled_archived_count": archived_count,
                "decision_items": sorted(set(decision_items)),
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
