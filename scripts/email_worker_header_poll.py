#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import contextlib
import html
import imaplib
import json
import os
import re
import shutil
import socket
import smtplib
import ssl
import sys
import time
from email import message_from_bytes
from email.message import EmailMessage
from email.header import decode_header, make_header
from email.message import Message
from email.utils import formataddr, formatdate, make_msgid, parseaddr
from pathlib import Path

try:
    import mailbox_imap_helpers
except ImportError:  # pragma: no cover - shared mailbox proof helpers are optional.
    mailbox_imap_helpers = None

try:
    import email_trace_recorder
except ImportError:  # pragma: no cover - DB email trace is optional fail-open plumbing.
    email_trace_recorder = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Email worker polling cycle.")
    parser.add_argument("--worker", required=True, help="Worker slug, for example asher or venetia.")
    parser.add_argument("--creds-file", required=True, help="Private credential file.")
    parser.add_argument("--workspace-root", required=True, help="Worker workspace root.")
    parser.add_argument("--state-dir", required=True, help="Machine-local state directory.")
    parser.add_argument("--limit", type=int, default=200, help="Maximum INBOX messages to inspect.")
    parser.add_argument("--mail-server", default="", help="Optional IMAP server override. Defaults to credential Mail server or imap.gmail.com.")
    parser.add_argument("--manager", default="avignon", help="Manager label to record in header-only logs.")
    parser.add_argument("--read-bodies", action="store_true", help="Fetch and persist message bodies for new messages.")
    parser.add_argument("--send-approved", action="store_true", help="Send approved outbox drafts after polling.")
    return parser.parse_args()


OWNER_QUESTION_PATTERNS = re.compile(
    r"(?is)\b("
    r"can you|could you|would you|should i|should we|what should|what do you want|which one|who should|how should|"
    r"please confirm|need your guidance|need your decision|not sure|can't answer|cannot answer|missing fact|owner question"
    r")\b"
)

OWNER_QUESTION_TARGETS: dict[str, tuple[str, str, str]] = {
    "asher": ("sonat@kovaldistillery.com", "Sonat", "Asher Wilde"),
    "venetia": ("sonat@kovaldistillery.com", "Sonat", "Venetia Tempest-Dunn"),
}

DEFAULT_BCC_BY_WORKER: dict[str, list[str]] = {
    "asher": ["sonat@kovaldistillery.com"],
    "venetia": ["sonat@kovaldistillery.com"],
}


def decode_value(value: str) -> str:
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def load_credentials(path: Path, mail_server: str = "") -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    user = values.get("user", "")
    password = values.get("app password") or values.get("app pw") or values.get("app-pw") or values.get("app_pw") or values.get("password") or ""
    server = mail_server or values.get("mail server", "") or "imap.gmail.com"
    if not user or not password:
        raise ValueError("Credential file must contain User and App pw entries.")
    return {
        "user": user,
        "password": password,
        "server": server,
        "imap_port": values.get("imap ssl port", "993") or "993",
        "smtp_server": values.get("smtp server", "") or server,
        "smtp_port": values.get("smtp ssl port", "465") or "465",
    }


def normalize_message_id(value: str) -> str:
    return str(value or "").strip().strip("<>").lower()


def html_to_text(value: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value or "")
    text = re.sub(r"(?i)<(br|/p|/div|/li|/h[1-6])\b[^>]*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def message_text(msg: Message) -> str:
    plain_parts: list[str] = []
    html_parts: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = (part.get("Content-Disposition") or "").lower()
            if "attachment" in content_disposition:
                continue
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if content_type == "text/plain":
                plain_parts.append(text)
            elif content_type == "text/html":
                html_parts.append(html_to_text(text))
    else:
        payload = msg.get_payload(decode=True)
        if payload is not None:
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html_parts.append(html_to_text(text))
            else:
                plain_parts.append(text)
    text = "\n\n".join(part.strip() for part in plain_parts if part.strip())
    if not text:
        text = "\n\n".join(part.strip() for part in html_parts if part.strip())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def safe_body_name(source_id: str) -> str:
    safe = re.sub(r"[^a-z0-9._-]+", "-", source_id.lower()).strip("-")
    return (safe[:120] or "message") + ".txt"


def store_body(body_dir: Path, source_id: str, body: str) -> Path:
    body_dir.mkdir(parents=True, exist_ok=True)
    if ".private" in body_dir.parts or str(body_dir).startswith("/Users/admin/."):
        body_dir.parent.mkdir(parents=True, exist_ok=True)
    path = body_dir / safe_body_name(source_id)
    path.write_text(body, encoding="utf-8", errors="replace")
    if ".private" in path.parts or str(path).startswith("/Users/admin/."):
        path.chmod(0o600)
    return path


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return set()
    return {str(item) for item in data.get("seen_message_ids", []) if item}


def load_seen_db_first(worker: str, path: Path) -> set[str]:
    seen: set[str] = set()
    if mailbox_imap_helpers is not None:
        seen.update(mailbox_imap_helpers.collect_seen_source_ids_from_db(str(worker or "").strip().lower(), 20000))
    if seen:
        return seen
    return load_seen(path)


def record_header_worker_email_trace(
    state_dir: Path,
    worker: str,
    creds: dict[str, str],
    row: dict,
    *,
    event: str,
    direction: str = "inbound",
    message_id: str = "",
) -> None:
    if email_trace_recorder is None:
        return
    source_id = normalize_message_id(row.get("source_message_id") or row.get("source_ref") or row.get("message_id") or "")
    try:
        message = email_trace_recorder.build_message_record(
            mailbox_lane=str(worker or "").strip().lower(),
            worker=str(worker or "").strip().lower(),
            event=event,
            message_id=message_id or row.get("message_id", ""),
            source_message_id=source_id,
            source_ref=row.get("source_ref", "") or source_id,
            subject=row.get("subject", ""),
            from_address=parseaddr(str(row.get("from", "")))[1].strip().lower(),
            to_addresses=row.get("to", ""),
            cc_addresses=row.get("cc", ""),
            header_date=row.get("date", ""),
            email_account=creds.get("user", ""),
            direction=direction,
            body_path=row.get("body_path", ""),
            body_chars=row.get("body_chars", ""),
            body_summary=row.get("classification", ""),
            status=row.get("classification", "") or ("reported" if direction == "outbound" else "classified"),
            first_seen_at=row.get("logged_at", ""),
            event_at=row.get("logged_at", ""),
            metadata={
                "classification": row.get("classification", ""),
                "manager": row.get("manager", ""),
                "body_read": bool(row.get("body_read")),
                "mailbox_mutation": bool(row.get("mailbox_mutation")),
                "event": row.get("event", ""),
            },
        )
        email_trace_recorder.record_event(
            state_dir,
            event=event,
            message=message,
            details={"classification": row.get("classification", ""), "manager": row.get("manager", ""), "backfill": bool(row.get("backfill"))},
        )
    except Exception:
        pass


def save_seen(path: Path, seen: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if ".private" in path.parts:
        path.parent.chmod(0o700)
    payload = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "seen_message_ids": sorted(seen)[-5000:],
    }
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    if ".private" in path.parts:
        path.chmod(0o600)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if ".private" in path.parts:
        path.parent.chmod(0o700)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    if ".private" in path.parts or str(path).startswith("/Users/admin/."):
        path.chmod(0o600)


def normalize_recipients(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        raw_values = re.split(r"[,;\n]+", value)
    elif isinstance(value, list):
        raw_values = []
        for item in value:
            raw_values.extend(re.split(r"[,;\n]+", str(item)))
    else:
        raw_values = [str(value)]
    recipients: list[str] = []
    for raw in raw_values:
        name, addr = parseaddr(str(raw).strip())
        if not addr or "@" not in addr:
            continue
        recipients.append(formataddr((name, addr)) if name else addr)
    return recipients


def recipient_email(value: str) -> str:
    return parseaddr(str(value or ""))[1].strip().lower()


def add_default_bcc(worker: str, to_addrs: list[str], cc_addrs: list[str], bcc_addrs: list[str]) -> list[str]:
    present = {recipient_email(addr) for addr in [*to_addrs, *cc_addrs, *bcc_addrs]}
    result = list(bcc_addrs)
    for addr in DEFAULT_BCC_BY_WORKER.get(str(worker or "").strip().lower(), []):
        normalized = recipient_email(addr)
        if normalized and normalized not in present:
            result.append(addr)
            present.add(normalized)
    return result


def safe_outbox_name(path: Path) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", path.name).strip("-") or "approved.json"


def normalize_source_ref(value: str) -> str:
    return normalize_message_id(value)


def jsonl_has_source_ref(path: Path, source_id: str) -> bool:
    if not path.exists():
        return False
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if normalize_source_ref(row.get("source_ref") or row.get("source_message_id") or "") == normalize_source_ref(source_id):
                return True
    except Exception:
        return False
    return False


def owner_question_target(worker: str) -> tuple[str, str, str]:
    return OWNER_QUESTION_TARGETS.get(str(worker or "").strip().lower(), ("", "", ""))


def owner_question_subject(subject: str) -> str:
    subject = str(subject or "").strip()
    if not subject:
        return "Re: owner question"
    if subject.lower().startswith("re:"):
        return f"{subject} [owner question]"
    return f"Re: owner question: {subject}"


def owner_question_probe_text(body: str) -> str:
    lines: list[str] = []
    for raw_line in str(body or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            continue
        if re.match(r"^(on .+wrote:|from:|sent:|to:|cc:|subject:)", line, flags=re.I):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def should_queue_owner_question(subject: str, body: str) -> bool:
    combined = "\n".join(part for part in [str(subject or "").strip(), owner_question_probe_text(body)] if part).strip()
    if not combined:
        return False
    if not OWNER_QUESTION_PATTERNS.search(combined):
        return False
    return "?" in combined or "owner question" in combined.lower()


def owner_question_body(headers: dict[str, str], body: str, owner_name: str, worker_label: str) -> str:
    original = owner_question_probe_text(body) or str(body or "").strip()
    greeting = f"Hi {owner_name}," if owner_name else "Hi,"
    return "\n".join(
        [
            greeting,
            "",
            "This is an owner question. The message below needs your decision before any reply, filing, or other mailbox action.",
            "",
            "Original message for review:",
            f"From: {headers.get('from', '')}",
            f"To: {headers.get('to', '')}",
            f"Cc: {headers.get('cc', '')}",
            f"Date: {headers.get('date', '')}",
            f"Subject: {headers.get('subject', '')}",
            "",
            original,
            "",
            "Please answer the owner question with the next action.",
            "",
            "Best,",
            "",
            worker_label,
        ]
    ).strip()


def quoted_original_message_block(headers: dict[str, str], body: str) -> str:
    original = owner_question_probe_text(body) or str(body or "").strip()
    lines = [
        "Original message:",
        f"From: {headers.get('from', '')}",
        f"To: {headers.get('to', '')}",
        f"Cc: {headers.get('cc', '')}",
        f"Date: {headers.get('date', '')}",
        f"Subject: {headers.get('subject', '')}",
        "",
        original,
    ]
    return "\n".join(f"> {line}" if line else ">" for line in lines).strip()


def owner_question_draft_exists(state_dir: Path, source_id: str) -> bool:
    outbox = state_dir / "outbox"
    if outbox.exists():
        for draft_path in outbox.glob("*.approved.json"):
            try:
                payload = json.loads(draft_path.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            if normalize_source_ref(payload.get("source_ref") or payload.get("source_message_id") or "") == normalize_source_ref(source_id):
                return True
    if mailbox_imap_helpers:
        sent_entries = mailbox_imap_helpers.collect_sent_entries(state_dir)
        return mailbox_imap_helpers.sent_entries_have_source_ref(sent_entries, source_id)
    return jsonl_has_source_ref(state_dir / "sent-log.jsonl", source_id)


def queue_owner_question_draft(
    creds: dict[str, str],
    state_dir: Path,
    worker: str,
    headers: dict[str, str],
    body: str,
    source_id: str,
) -> bool:
    owner_email, owner_name, worker_label = owner_question_target(worker)
    if not owner_email or not worker_label:
        return False
    if owner_question_draft_exists(state_dir, source_id):
        return False
    outbox = state_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    outbox.chmod(0o700)
    payload = {
        "source_ref": source_id,
        "intake_channel": f"email:{worker}",
        "requester": headers.get("from", ""),
        "owner_lane": worker,
        "responsible_worker_or_persona": creds["user"],
        "status": "draft",
        "due_or_trigger": "",
        "scheduled_action": "",
        "calendar_event": "",
        "source_links": headers.get("subject", ""),
        "approval_gates": "owner question, filing, deletes, and external replies remain gated until the human owner answers",
        "verification_readback": "owner_question_draft_queued",
        "next_update": "Human owner must answer one owner question before any reply or filing.",
        "requested_deliverable": "Human owner answer",
        "human_owner_or_recipient": owner_name or owner_email,
        "output_channel": "email",
        "proof_required": "sent Message-ID plus original source email attached or quoted",
        "owner_question_required": "required",
        "owner_question": "true",
        "from": creds["user"],
        "from_name": worker_label,
        "to": [owner_email],
        "subject": owner_question_subject(headers.get("subject", "")),
        "body": owner_question_body(headers, body, owner_name, worker_label),
        "reply_chain_required": True,
        "original_from": headers.get("from", ""),
        "original_to": headers.get("to", ""),
        "original_cc": headers.get("cc", ""),
        "original_date": headers.get("date", ""),
        "original_subject": headers.get("subject", ""),
        "original_body": owner_question_probe_text(body) or str(body or "").strip(),
        "in_reply_to": headers.get("message_id", ""),
        "references": headers.get("references", "") or headers.get("message_id", ""),
    }
    draft_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", f"owner-question-{source_id}").strip("-") + ".approved.json"
    draft_path = outbox / draft_name
    draft_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    draft_path.chmod(0o600)
    append_jsonl(
        state_dir / "owner-question-log.jsonl",
        {
            "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "worker": worker,
            "source_message_id": source_id,
            "subject": headers.get("subject", ""),
            "owner_question": "true",
            "draft": str(draft_path),
            "recipient": owner_email,
            "event": "email_owner_question_queued",
        },
    )
    return True


def parse_imap_folder_name(raw_folder) -> str:
    text = raw_folder.decode("utf-8", errors="replace") if isinstance(raw_folder, bytes) else str(raw_folder)
    match = re.search(r'(?:"([^"]+)"| ([^ ]+))$', text)
    return (match.group(1) or match.group(2)) if match else ""


def sent_folder_candidates(conn: imaplib.IMAP4_SSL) -> list[str]:
    discovered: list[str] = []
    try:
        status, folders = conn.list()
    except Exception:
        status, folders = "NO", []
    if status == "OK":
        for raw_folder in folders or []:
            text = raw_folder.decode("utf-8", errors="replace") if isinstance(raw_folder, bytes) else str(raw_folder)
            folder = parse_imap_folder_name(raw_folder)
            if not folder:
                continue
            if "\\Sent" in text or "sent" in folder.lower():
                discovered.append(folder)
    candidates = [*discovered, "INBOX.Sent", "Sent", "Sent Mail", "[Gmail]/Sent Mail"]
    ordered: list[str] = []
    seen: set[str] = set()
    for folder in candidates:
        key = folder.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(folder)
    return ordered


def append_message_to_sent_folder(creds: dict[str, str], msg: EmailMessage) -> str:
    raw_message = msg.as_bytes()
    last_error = ""
    conn = imaplib.IMAP4_SSL(creds["server"], int(creds["imap_port"]), timeout=30)
    try:
        conn.login(creds["user"], creds["password"])
        for folder in sent_folder_candidates(conn):
            try:
                status, _ = conn.append(folder, "\\Seen", imaplib.Time2Internaldate(time.time()), raw_message)
                if status == "OK":
                    return folder
            except Exception as exc:
                last_error = f"{folder}: {exc}"
    finally:
        with contextlib.suppress(Exception):
            conn.logout()
    raise RuntimeError(f"sent folder append failed for {msg.get('Message-ID', '')}: {last_error or 'no sent folder accepted APPEND'}")


def send_approved_outbox(creds: dict[str, str], state_dir: Path, worker: str) -> dict:
    outbox_dir = state_dir / "outbox"
    sent_dir = state_dir / "sent"
    failed_dir = state_dir / "failed"
    log_path = state_dir / "sent-log.jsonl"
    lock_dir = state_dir / "send-approved.lock"
    summary = {"queued_sends_seen": 0, "queued_sends_sent": 0, "queued_sends_failed": 0, "queued_sends_skipped_locked": 0}
    if not outbox_dir.exists():
        return summary
    try:
        lock_dir.mkdir(parents=True)
    except FileExistsError:
        summary["queued_sends_skipped_locked"] = 1
        return summary
    try:
        drafts = sorted(outbox_dir.glob("*.approved.json"))
        summary["queued_sends_seen"] = len(drafts)
        if not drafts:
            return summary
        sent_dir.mkdir(parents=True, exist_ok=True)
        failed_dir.mkdir(parents=True, exist_ok=True)
        for path in drafts:
            started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            message_id = ""
            smtp_sent = False
            try:
                payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
                to_addrs = normalize_recipients(payload.get("to"))
                cc_addrs = normalize_recipients(payload.get("cc"))
                bcc_addrs = normalize_recipients(payload.get("bcc"))
                bcc_addrs = add_default_bcc(worker, to_addrs, cc_addrs, bcc_addrs)
                subject = str(payload.get("subject") or "").strip()
                body = str(payload.get("body") or payload.get("text") or "").strip()
                if not to_addrs or not subject or not body:
                    raise ValueError("approved draft requires to, subject, and body")
                from_name = str(payload.get("from_name") or worker.title()).strip()
                from_addr = creds["user"]
                msg = EmailMessage()
                msg["From"] = formataddr((from_name, from_addr))
                msg["To"] = ", ".join(to_addrs)
                if cc_addrs:
                    msg["Cc"] = ", ".join(cc_addrs)
                msg["Subject"] = subject
                msg["Date"] = formatdate(localtime=True)
                message_id = str(payload.get("message_id") or make_msgid(domain=from_addr.split("@", 1)[-1]))
                msg["Message-ID"] = message_id
                if payload.get("in_reply_to"):
                    msg["In-Reply-To"] = str(payload.get("in_reply_to"))
                if payload.get("references"):
                    msg["References"] = str(payload.get("references"))
                reply_chain_required = payload.get("reply_chain_required")
                if isinstance(reply_chain_required, str):
                    reply_chain_required = reply_chain_required.strip().lower() in {"1", "true", "yes", "on"}
                else:
                    reply_chain_required = bool(reply_chain_required)
                if reply_chain_required and "Original message:" not in body:
                    original_headers = {
                        "from": payload.get("original_from", ""),
                        "to": payload.get("original_to", ""),
                        "cc": payload.get("original_cc", ""),
                        "date": payload.get("original_date", ""),
                        "subject": payload.get("original_subject", ""),
                    }
                    original_body = str(payload.get("original_body") or "").strip()
                    if original_body or any(str(v or "").strip() for v in original_headers.values()):
                        body = f"{body}\n\n{quoted_original_message_block(original_headers, original_body)}".strip()
                msg.set_content(body)
                with smtplib.SMTP_SSL(creds["smtp_server"], int(creds["smtp_port"]), context=ssl.create_default_context(), timeout=30) as smtp:
                    smtp.login(creds["user"], creds["password"])
                    smtp.send_message(msg, from_addr=from_addr, to_addrs=[*to_addrs, *cc_addrs, *bcc_addrs])
                smtp_sent = True
                sent_folder = append_message_to_sent_folder(creds, msg)
                row = {
                    "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "worker": worker,
                    "event": "approved_email_sent",
                    "draft": path.name,
                    "source_ref": str(payload.get("source_ref") or payload.get("source_message_id") or ""),
                    "to": to_addrs,
                    "cc": cc_addrs,
                    "bcc_count": len(bcc_addrs),
                    "subject": subject,
                    "message_id": message_id,
                    "started_at": started_at,
                    "sent_folder_appended": True,
                    "sent_folder": sent_folder,
                }
                append_jsonl(log_path, row)
                record_header_worker_email_trace(state_dir, worker, creds, row, event="email_action_logged")
                archive_payload = dict(payload)
                archive_payload.update({"sent_at": row["logged_at"], "message_id": message_id, "send_status": "sent", "sent_folder_appended": True, "sent_folder": sent_folder})
                archive_path = sent_dir / f"{safe_outbox_name(path)}.sent-{int(time.time())}.json"
                archive_path.write_text(json.dumps(archive_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
                archive_path.chmod(0o600)
                path.unlink()
                summary["queued_sends_sent"] += 1
            except Exception as exc:
                failed_payload = {
                    "failed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "worker": worker,
                    "draft": path.name,
                    "error_type": exc.__class__.__name__,
                    "error": re.sub(r"(?i)(password|app pw|secret|token)\S*", "[REDACTED]", str(exc)),
                    "message_id": message_id,
                    "smtp_sent": smtp_sent,
                }
                append_jsonl(log_path, {"event": "approved_email_failed", **failed_payload})
                failed_path = failed_dir / f"{safe_outbox_name(path)}.failed-{int(time.time())}.json"
                try:
                    shutil.move(str(path), str(failed_path))
                except Exception:
                    failed_path.write_text(json.dumps(failed_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
                    failed_path.chmod(0o600)
                summary["queued_sends_failed"] += 1
        return summary
    finally:
        try:
            lock_dir.rmdir()
        except OSError:
            pass


def fetch_headers(creds: dict[str, str], limit: int, read_bodies: bool) -> list[dict]:
    conn = imaplib.IMAP4_SSL(creds["server"], int(creds["imap_port"]), timeout=25)
    conn.login(creds["user"], creds["password"])
    conn.select("INBOX", readonly=True)
    status, data = conn.search(None, "ALL")
    if status != "OK":
        conn.logout()
        raise RuntimeError(f"IMAP search failed: {status}")
    ids = data[0].split()[-limit:] if data and data[0] else []
    messages: list[dict] = []
    for imap_id in ids:
        fetch_spec = "(BODY.PEEK[])" if read_bodies else "(BODY.PEEK[HEADER])"
        status, msg_data = conn.fetch(imap_id, fetch_spec)
        if status != "OK":
            continue
        raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
        if not raw:
            continue
        msg = message_from_bytes(raw)
        row = {
            "imap_id": imap_id.decode("ascii", errors="replace"),
            "message_id": decode_value(msg.get("Message-ID", "")),
            "date": decode_value(msg.get("Date", "")),
            "from": decode_value(msg.get("From", "")),
            "to": decode_value(msg.get("To", "")),
            "cc": decode_value(msg.get("Cc", "")),
            "subject": decode_value(msg.get("Subject", "")),
            "in_reply_to": decode_value(msg.get("In-Reply-To", "")),
            "references": decode_value(msg.get("References", "")),
        }
        if read_bodies:
            row["body"] = message_text(msg)
        messages.append(row)
    conn.logout()
    return messages


def main() -> int:
    args = parse_args()
    state_dir = Path(args.state_dir).expanduser()
    workspace_root = Path(args.workspace_root).expanduser()
    creds_path = Path(args.creds_file).expanduser()
    seen_path = state_dir / "seen-headers.json"
    log_path = state_dir / "header-poll-log.jsonl"
    worker_log_path = workspace_root / "header-poll-log.jsonl"
    body_dir = state_dir / "bodies"
    start = time.time()
    try:
        creds = load_credentials(creds_path, args.mail_server)
        seen = load_seen_db_first(args.worker, seen_path)
        headers = fetch_headers(creds, args.limit, args.read_bodies)
        new_rows = []
        for item in headers:
            source_id = normalize_message_id(item.get("message_id", ""))
            if not source_id:
                source_id = f"imap-{item.get('imap_id', '')}"
            if source_id in seen:
                continue
            seen.add(source_id)
            row = {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": args.worker,
                "email": creds["user"],
                "source_message_id": source_id,
                "classification": "new-header-only-unprocessed",
                "manager": args.manager,
                "body_read": bool(args.read_bodies),
                "mailbox_mutation": False,
                **item,
            }
            if args.read_bodies:
                body = str(item.get("body") or "").strip()
                body_path = store_body(body_dir, source_id, body)
                row["body_chars"] = len(body)
                row["body_path"] = str(body_path)
                if should_queue_owner_question(item.get("subject", ""), body):
                    if queue_owner_question_draft(creds, state_dir, args.worker, item, body, source_id):
                        owner_email, owner_name, worker_label = owner_question_target(args.worker)
                        row["classification"] = "new-body-owner-question-queued"
                        row["owner_question"] = "true"
                        row["owner_question_required"] = "required"
                        row["owner_question_recipient"] = owner_email
                        row["owner_question_owner"] = owner_name
                        row["owner_question_sender"] = worker_label
            new_rows.append(row)
            append_jsonl(log_path, row)
            append_jsonl(worker_log_path, row)
            record_header_worker_email_trace(state_dir, args.worker, creds, row, event="email_action_logged")
        save_seen(seen_path, seen)
        send_result = send_approved_outbox(creds, state_dir, args.worker) if args.send_approved else {"queued_sends_seen": 0, "queued_sends_sent": 0, "queued_sends_failed": 0, "queued_sends_skipped_locked": 0}
        append_jsonl(
            log_path,
            {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": args.worker,
                "event": "cycle_complete",
                "headers_seen": len(headers),
                "new_headers": len(new_rows),
                "queued_sends_seen": send_result["queued_sends_seen"],
                "queued_sends_sent": send_result["queued_sends_sent"],
                "queued_sends_failed": send_result["queued_sends_failed"],
                "queued_sends_skipped_locked": send_result["queued_sends_skipped_locked"],
                "duration_seconds": round(time.time() - start, 3),
                "host": socket.gethostname(),
            },
        )
        print(json.dumps({
            "ok": True,
            "worker": args.worker,
            "headers_seen": len(headers),
            "new_headers": len(new_rows),
            "queued_sends_seen": send_result["queued_sends_seen"],
            "queued_sends_sent": send_result["queued_sends_sent"],
            "queued_sends_failed": send_result["queued_sends_failed"],
            "queued_sends_skipped_locked": send_result["queued_sends_skipped_locked"],
        }))
        return 0
    except Exception as exc:
        append_jsonl(
            log_path,
            {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": args.worker,
                "event": "cycle_failed",
                "error_type": exc.__class__.__name__,
                "error": re.sub(r"(?i)(password|app pw|secret|token)\S*", "[REDACTED]", str(exc)),
            },
        )
        print(f"poll failed for {args.worker}: {exc.__class__.__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
