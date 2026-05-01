#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import imaplib
import json
import contextlib
import os
import re
import shutil
import smtplib
import ssl
import subprocess
import time
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import EmailMessage, Message
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Optional

try:
    import shared_task_flow
except ImportError:  # pragma: no cover - installed runtime should keep helper beside this script.
    shared_task_flow = None


ALLOWED_FROM = {
    "codex@kovaldistillery.com",
    "nationaloutreach@kovaldistillery.com",
    "vanessa.sterling@kovaldistillery.com",
    "naomi.stern@kovaldistillery.com",
    "ezra.katz@kovaldistillery.com",
}

VERIFIED_SEND_AS_ALIASES = {
    "vanessa.sterling@kovaldistillery.com",
    "naomi.stern@kovaldistillery.com",
    "ezra.katz@kovaldistillery.com",
}

FROM_DISPLAY_NAMES = {
    "nationaloutreach@kovaldistillery.com": "Vanessa Sterling",
    "vanessa.sterling@kovaldistillery.com": "Vanessa Sterling",
    "naomi.stern@kovaldistillery.com": "Naomi Stern",
    "ezra.katz@kovaldistillery.com": "Ezra Katz",
}

SOCIAL_LINKS = {
    "X": "http://www.x.com/kovaldistillery",
    "Instagram": "http://www.instagram.com/kovaldistillery",
    "Facebook": "http://www.facebook.com/kovaldistillery",
}

SOCIAL_SIGNATURE_RE = re.compile(r"^\s*X\s*\|\s*Instagram\s*\|\s*Facebook\s*$", re.IGNORECASE | re.MULTILINE)
SOCIAL_SIGNATURE_TEXT_RE = re.compile(r"X\s*\|\s*Instagram\s*\|\s*Facebook", re.IGNORECASE)

SENSITIVE_PATTERNS = re.compile(
    r"\b(password|passcode|2fa|verification code|wire|bank account|routing number|gift card|urgent payment|w-?9|ssn|social security|credential|oauth|token)\b",
    re.IGNORECASE,
)

NAOMI_PATTERNS = re.compile(
    r"\b(naomi stern|finance operations|financial operations|cash flow|cashflow|accounts payable|accounts receivable|payables|receivables|invoice|invoices|bill payment|collections|month-end|month end|close readiness|reconciliation|budget|forecast|cash controls)\b",
    re.IGNORECASE,
)

EZRA_PATTERNS = re.compile(
    r"\b(ezra katz|special projects|legal affairs|legal|lawyer|attorney|counsel|regulatory|permit|license|licence|ttb|tax and trade|label approval|cola|trademark|contract|liability|lawsuit|subpoena|cease and desist|privileged|policy question|document follow-up|approval tracking)\b",
    re.IGNORECASE,
)

OUTREACH_PATTERNS = re.compile(
    r"\b(tasting|demo|sampling|outreach|event|venue|account visit|binny'?s|mariano'?s|whole foods|availability|available|shift|calendar|schedule)\b",
    re.IGNORECASE,
)

MARKETING_PATTERNS = re.compile(
    r"\b(campaign|newsletter|press|media|magazine|distributor email|forge|mailchimp|phplist|promo|promotion)\b",
    re.IGNORECASE,
)

INTERNAL_PATTERNS = re.compile(
    r"\b(team|staff|internal|employee|availability|schedule|shift|reminder)\b",
    re.IGNORECASE,
)

ACTIVE_INBOX_LOG_INTERVAL_SECONDS = 15 * 60


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="National Outreach full-body mailbox cycle with approved queued sends.")
    parser.add_argument("--creds-file", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--mailbox", default="INBOX")
    parser.add_argument("--search", default="ALL")
    parser.add_argument("--send-approved", action="store_true", help="Send queued *.approved.json files from outbox.")
    parser.add_argument("--review-old", action="store_true", help="Include already seen messages in review output.")
    parser.add_argument("--from-address", default="vanessa.sterling@kovaldistillery.com")
    return parser.parse_args()


def decode_value(value: str) -> str:
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def load_credentials(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    user = values.get("user", "")
    password = values.get("app password") or values.get("app pw") or values.get("app-pw") or values.get("app_pw") or values.get("password") or ""
    if not user or not password:
        raise ValueError("Credential file must contain User and App password entries.")
    return {
        "user": user,
        "password": password,
        "imap_server": values.get("mail server", "") or values.get("imap server", "") or "imap.gmail.com",
        "imap_port": values.get("imap ssl port", "993") or "993",
        "smtp_server": values.get("smtp server", "") or "smtp.gmail.com",
        "smtp_port": values.get("smtp ssl port", "465") or "465",
    }


def normalize_message_id(value: str) -> str:
    return str(value or "").strip().strip("<>").lower()


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    path.chmod(0o600)


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return default


def parse_due_at(value: str) -> Optional[float]:
    raw = str(value or "").strip()
    if not raw:
        return None
    normalized = raw.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def mailbox_has_matching_reply(creds: dict[str, str], check: dict) -> bool:
    from_contains = str(check.get("from_contains") or "").lower().strip()
    subject_contains = str(check.get("subject_contains") or "").lower().strip()
    after_ts = parse_due_at(str(check.get("after") or ""))
    if not from_contains and not subject_contains:
        return False
    conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]))
    try:
        conn.login(creds["user"], creds["password"])
        conn.select('"[Gmail]/All Mail"', readonly=True)
        typ, data = conn.uid("SEARCH", None, "ALL")
        if typ != "OK":
            return False
        for uid in reversed((data[0].split() if data and data[0] else [])[-500:]):
            typ, msgdata = conn.uid("FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)])")
            if typ != "OK":
                continue
            raw = b""
            for part in msgdata or []:
                if isinstance(part, tuple):
                    raw += part[1]
            msg = message_from_bytes(raw)
            sender = decode_value(msg.get("From", "")).lower()
            subject = decode_value(msg.get("Subject", "")).lower()
            if from_contains and from_contains not in sender:
                continue
            if subject_contains and subject_contains not in subject:
                continue
            if after_ts is not None:
                try:
                    msg_ts = message_from_bytes(raw).get("Date")
                    parsed = datetime.fromtimestamp(0, tz=timezone.utc)
                    if msg_ts:
                        from email.utils import parsedate_to_datetime

                        parsed = parsedate_to_datetime(msg_ts)
                        if parsed.tzinfo is None:
                            parsed = parsed.replace(tzinfo=timezone.utc)
                    if parsed.timestamp() <= after_ts:
                        continue
                except Exception:
                    continue
            return True
        return False
    finally:
        with contextlib.suppress(Exception):
            conn.logout()


def process_scheduled_actions(creds: dict[str, str], state_dir: Path, now_ts: Optional[float] = None) -> dict:
    schedule_path = state_dir / "scheduled-actions.jsonl"
    if not schedule_path.exists():
        return {"due": 0, "queued": 0, "skipped_resolved": 0, "failed": 0}
    now = time.time() if now_ts is None else now_ts
    lock_dir = state_dir / "scheduled-actions.lock"
    try:
        lock_dir.mkdir()
        lock_acquired = True
    except FileExistsError:
        return {"due": 0, "queued": 0, "skipped_resolved": 0, "failed": 0, "skipped_locked": True}
    rows = []
    due = queued = skipped_resolved = failed = 0
    outbox = state_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    outbox.chmod(0o700)
    try:
        for line in schedule_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                failed += 1
                continue
            status = str(row.get("status") or "pending")
            due_ts = parse_due_at(str(row.get("due_at") or ""))
            if status != "pending" or due_ts is None or due_ts > now:
                rows.append(row)
                continue
            due += 1
            task_packet = shared_task_flow.packet_from_scheduled_action(row) if shared_task_flow else {}
            if shared_task_flow:
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", task_packet, "scheduled_action_due")
            checks = row.get("resolution_checks") if isinstance(row.get("resolution_checks"), list) else []
            if any(mailbox_has_matching_reply(creds, c) for c in checks if isinstance(c, dict)):
                row["status"] = "resolved_no_send"
                row["resolved_at"] = datetime.now(timezone.utc).isoformat()
                rows.append(row)
                append_jsonl(state_dir / "scheduled-actions-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "action_id": row.get("id"), "status": "resolved_no_send"})
                if shared_task_flow:
                    resolved_packet = {**task_packet, "status": "completed", "verification_readback": "resolution_check_matched"}
                    shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", resolved_packet, "scheduled_action_resolved_no_send")
                skipped_resolved += 1
                continue
            payload = row.get("email")
            if str(row.get("kind") or "") == "mitch_weekly_report_draft":
                report_start = str(row.get("report_start") or str(row.get("due_at") or "")[:10])
                try:
                    proc = subprocess.run(
                        [
                            "php",
                            "/Users/werkstatt/ai_workspace/nationaloutreach/scripts/build_mitch_weekly_report.php",
                            "--start",
                            report_start,
                        ],
                        check=True,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    payload = json.loads(proc.stdout)
                except Exception as exc:
                    row["status"] = "failed"
                    row["error"] = f"report_generation_failed: {exc}"
                    rows.append(row)
                    append_jsonl(state_dir / "scheduled-actions-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "action_id": row.get("id"), "status": "failed", "error": row["error"]})
                    if shared_task_flow:
                        failed_packet = {**task_packet, "status": "blocked", "verification_readback": row["error"]}
                        shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", failed_packet, "scheduled_action_failed", error=row["error"])
                    failed += 1
                    continue
            if not isinstance(payload, dict):
                row["status"] = "failed"
                row["error"] = "missing_email_payload"
                rows.append(row)
                if shared_task_flow:
                    failed_packet = {**task_packet, "status": "blocked", "verification_readback": row["error"]}
                    shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", failed_packet, "scheduled_action_failed", error=row["error"])
                failed += 1
                continue
            draft_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(row.get("id") or f"scheduled-{int(now)}")).strip("-") + ".approved.json"
            draft_path = outbox / draft_name
            draft_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
            draft_path.chmod(0o600)
            row["status"] = "queued"
            row["queued_at"] = datetime.now(timezone.utc).isoformat()
            row["queued_draft"] = str(draft_path)
            rows.append(row)
            append_jsonl(state_dir / "scheduled-actions-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "action_id": row.get("id"), "status": "queued", "draft": str(draft_path)})
            if shared_task_flow:
                queued_packet = {**task_packet, "status": "working", "scheduled_action": row.get("id") or "", "next_update": "queued approved draft for send cycle"}
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", queued_packet, "scheduled_action_queued", draft=str(draft_path))
            queued += 1
        tmp = schedule_path.with_suffix(".jsonl.tmp")
        tmp.write_text("\n".join(json.dumps(r, ensure_ascii=True) for r in rows) + ("\n" if rows else ""), encoding="utf-8")
        tmp.chmod(0o600)
        shutil.move(str(tmp), str(schedule_path))
        schedule_path.chmod(0o600)
        return {"due": due, "queued": queued, "skipped_resolved": skipped_resolved, "failed": failed, "skipped_locked": False}
    finally:
        if lock_acquired:
            with contextlib.suppress(OSError):
                lock_dir.rmdir()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


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


def routing_body(body: str) -> str:
    active = re.split(r"(?im)^\s*On .+ wrote:\s*$", body, maxsplit=1)[0]
    active = re.split(r"(?i)\bConfidentiality Notice:", active, maxsplit=1)[0]
    return active.strip()


def classify_message(headers: dict[str, str], body: str) -> dict[str, str]:
    combined = f"{headers.get('subject', '')}\n{headers.get('from', '')}\n{headers.get('to', '')}\n{headers.get('cc', '')}\n{routing_body(body)}"
    if SENSITIVE_PATTERNS.search(combined):
        return {
            "route": "security-guard",
            "suggestion": "Review as sensitive/security-gated before any reply or filing.",
            "send_allowed": "no",
        }
    if NAOMI_PATTERNS.search(combined):
        return {
            "route": "naomi-stern",
            "suggestion": "Route to Naomi Stern for finance-operations triage: cash/control/cadence status, missing sources, and owner decisions. Do not move money or change finance records.",
            "send_allowed": "approval-required",
        }
    if EZRA_PATTERNS.search(combined):
        return {
            "route": "ezra-katz",
            "suggestion": "Route to Ezra Katz for special-project/legal-affairs coordination and a counsel-ready business brief. Keep the tone practical; do not send external legal/regulatory replies or approve regulated action.",
            "send_allowed": "approval-required",
        }
    if MARKETING_PATTERNS.search(combined):
        return {
            "route": "marketing-manager",
            "suggestion": "Review for Marketing Manager or Communications Manager; use Forge/campaign route if this is audience/bulk work.",
            "send_allowed": "approval-required",
        }
    if OUTREACH_PATTERNS.search(combined):
        return {
            "route": "outreach-coordinator",
            "suggestion": "Review for Outreach Coordinator; likely needs OPS Outreach/calendar/team availability follow-up.",
            "send_allowed": "routine-if-clear",
        }
    if INTERNAL_PATTERNS.search(combined):
        return {
            "route": "internal-communicator",
            "suggestion": "Review for Internal Communicator; likely team update/reminder/availability workflow.",
            "send_allowed": "routine-if-clear",
        }
    return {
        "route": "email-coordinator",
        "suggestion": "Review ownership; no strong automatic route detected.",
        "send_allowed": "approval-required",
    }


def load_seen(path: Path) -> set[str]:
    data = read_json(path, {"seen_message_ids": []})
    return {str(item) for item in data.get("seen_message_ids", []) if item}


def save_seen(path: Path, seen: set[str]) -> None:
    write_json(
        path,
        {
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "seen_message_ids": sorted(seen)[-20000:],
        },
    )


def is_inbox_mailbox(mailbox: str) -> bool:
    normalized = str(mailbox or "").strip().strip('"').lower()
    return normalized == "inbox"


def load_active_inbox(path: Path) -> dict[str, dict]:
    data = read_json(path, {"messages": {}})
    messages = data.get("messages") if isinstance(data, dict) else {}
    if not isinstance(messages, dict):
        return {}
    return {str(key): value for key, value in messages.items() if isinstance(value, dict)}


def save_active_inbox(path: Path, messages: dict[str, dict]) -> None:
    def sort_key(item: tuple[str, dict]) -> str:
        value = item[1]
        return str(value.get("last_seen_at") or value.get("resolved_at") or "")

    trimmed = dict(sorted(messages.items(), key=sort_key)[-5000:])
    write_json(
        path,
        {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": trimmed,
        },
    )


def should_log_active_inbox(record: dict, now_ts: float) -> bool:
    try:
        last_logged = float(record.get("last_active_log_epoch") or 0)
    except (TypeError, ValueError):
        last_logged = 0
    return last_logged <= 0 or now_ts - last_logged >= ACTIVE_INBOX_LOG_INTERVAL_SECONDS


def store_body(body_dir: Path, source_id: str, body: str) -> Path:
    safe = re.sub(r"[^a-z0-9._-]+", "-", source_id.lower()).strip("-")[:120] or "message"
    path = body_dir / f"{safe}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(body, encoding="utf-8", errors="replace")
    path.chmod(0o600)
    return path


def fetch_messages(creds: dict[str, str], state_dir: Path, workspace_root: Path, limit: int, mailbox: str, search: str, review_old: bool) -> dict:
    seen_path = state_dir / "seen-full-body.json"
    active_inbox_path = state_dir / "active-inbox.json"
    review_log = state_dir / "mail-review.jsonl"
    workspace_review = workspace_root / "mail-review.jsonl"
    body_dir = state_dir / "bodies"
    seen = load_seen(seen_path)
    inbox_selected = is_inbox_mailbox(mailbox)
    active_records = load_active_inbox(active_inbox_path) if inbox_selected else {}
    reviewed = 0
    new_items = 0
    mailbox_total = 0
    seen_inbox_active_count = 0
    active_inbox_logged = 0
    skipped_seen_non_inbox = 0
    route_counts: dict[str, int] = {}
    active_route_counts: dict[str, int] = {}
    current_inbox_source_ids: set[str] = set()
    active_inbox_subjects: list[dict[str, str]] = []
    now_ts = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]), timeout=25)
    try:
        conn.login(creds["user"], creds["password"])
        conn.select(mailbox, readonly=True)
        status, data = conn.search(None, search)
        if status != "OK":
            raise RuntimeError(f"IMAP search failed: {status}")
        all_ids = data[0].split() if data and data[0] else []
        mailbox_total = len(all_ids)
        ids = all_ids[-limit:] if limit > 0 else []
        for imap_id in ids:
            status, header_data = conn.fetch(imap_id, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID DATE FROM TO CC SUBJECT IN-REPLY-TO REFERENCES)])")
            if status != "OK":
                continue
            header_raw = b"".join(part[1] for part in header_data if isinstance(part, tuple))
            if not header_raw:
                continue
            header_msg = message_from_bytes(header_raw)
            source_id = normalize_message_id(decode_value(header_msg.get("Message-ID", ""))) or f"imap-{imap_id.decode('ascii', errors='replace')}"
            already_seen = source_id in seen
            if inbox_selected:
                current_inbox_source_ids.add(source_id)
            if already_seen and not review_old and not inbox_selected:
                skipped_seen_non_inbox += 1
                continue
            if already_seen and not review_old and inbox_selected:
                seen_inbox_active_count += 1
            status, msg_data = conn.fetch(imap_id, "(BODY.PEEK[])")
            if status != "OK":
                continue
            raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
            if not raw:
                continue
            msg = message_from_bytes(raw)
            body = message_text(msg)
            headers = {
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
            classification = classify_message(headers, body)
            body_path = store_body(body_dir, source_id, body)
            if inbox_selected:
                active_route_counts[classification["route"]] = active_route_counts.get(classification["route"], 0) + 1
                if len(active_inbox_subjects) < 20:
                    active_inbox_subjects.append(
                        {
                            "source_message_id": source_id,
                            "from": headers.get("from", ""),
                            "subject": headers.get("subject", ""),
                            "route": classification["route"],
                            "seen_before": str(already_seen).lower(),
                        }
                    )
            task_packet = {}
            if shared_task_flow:
                task_packet = shared_task_flow.build_packet(
                    source_ref=source_id,
                    intake_channel="email:nationaloutreach",
                    requester=headers.get("from", ""),
                    owner_lane=classification["route"],
                    responsible_worker_or_persona=classification["route"],
                    status="classified",
                    approval_gates=classification["send_allowed"],
                    source_links=headers.get("subject", ""),
                    next_update=classification["suggestion"],
                )
            row = {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": "nationaloutreach",
                "email": creds["user"],
                "source_message_id": source_id,
                "task_packet": task_packet,
                "body_read": True,
                "body_path": str(body_path),
                "body_chars": len(body),
                "mailbox_mutation": False,
                "active_inbox": inbox_selected,
                "seen_before": already_seen,
                "review_reason": "review_old" if review_old and already_seen else ("active_inbox_still_open" if inbox_selected and already_seen else "new_message"),
                **headers,
                **classification,
            }
            active_record = active_records.get(source_id, {}) if inbox_selected else {}
            should_append_review = not already_seen or review_old or not inbox_selected or should_log_active_inbox(active_record, now_ts)
            if should_append_review:
                append_jsonl(review_log, row)
                append_jsonl(workspace_review, {k: v for k, v in row.items() if k != "body_path"})
                reviewed += 1
                route_counts[classification["route"]] = route_counts.get(classification["route"], 0) + 1
                if inbox_selected and already_seen:
                    active_inbox_logged += 1
            if shared_task_flow and should_append_review:
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", task_packet, "email_classified")
            if inbox_selected:
                active_records[source_id] = {
                    **active_record,
                    "status": "active_inbox",
                    "first_seen_at": active_record.get("first_seen_at") or now_iso,
                    "last_seen_at": now_iso,
                    "last_active_log_epoch": now_ts if should_append_review else active_record.get("last_active_log_epoch"),
                    "message_id": headers.get("message_id", ""),
                    "date": headers.get("date", ""),
                    "from": headers.get("from", ""),
                    "to": headers.get("to", ""),
                    "cc": headers.get("cc", ""),
                    "subject": headers.get("subject", ""),
                    "route": classification["route"],
                    "send_allowed": classification["send_allowed"],
                    "suggestion": classification["suggestion"],
                    "body_path": str(body_path),
                    "body_chars": len(body),
                    "seen_before": already_seen,
                }
            seen.add(source_id)
            if not already_seen:
                new_items += 1
    finally:
        try:
            conn.logout()
        except Exception:
            pass
    if inbox_selected:
        for source_id, record in list(active_records.items()):
            if record.get("status") == "active_inbox" and source_id not in current_inbox_source_ids:
                active_records[source_id] = {
                    **record,
                    "status": "resolved_not_in_inbox",
                    "resolved_at": now_iso,
                }
        save_active_inbox(active_inbox_path, active_records)
    save_seen(seen_path, seen)
    return {
        "reviewed": reviewed,
        "new_items": new_items,
        "route_counts": route_counts,
        "mailbox_total": mailbox_total,
        "active_inbox_count": len(current_inbox_source_ids) if inbox_selected else 0,
        "seen_inbox_active_count": seen_inbox_active_count,
        "active_inbox_logged": active_inbox_logged,
        "active_route_counts": active_route_counts,
        "active_inbox_subjects": active_inbox_subjects,
        "skipped_seen_non_inbox": skipped_seen_non_inbox,
    }


def normalize_addresses(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def body_to_html_with_signature_links(body: str) -> str:
    lines = body.splitlines()
    rendered: list[str] = []
    in_paragraph: list[str] = []

    def flush_paragraph() -> None:
        if not in_paragraph:
            return
        rendered.append("<p>" + "<br>".join(html.escape(line) for line in in_paragraph) + "</p>")
        in_paragraph.clear()

    for line in lines:
        if not line.strip():
            flush_paragraph()
            continue
        if SOCIAL_SIGNATURE_RE.match(line):
            flush_paragraph()
            rendered.append("<p>" + social_links_html() + "</p>")
            continue
        in_paragraph.append(line)
    flush_paragraph()
    return "<!doctype html><html><body>" + "".join(rendered) + "</body></html>"


def social_links_html() -> str:
    return " | ".join(
        f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'
        for label, url in SOCIAL_LINKS.items()
    )


def ensure_signature_links_in_html(html_body: str) -> str:
    return SOCIAL_SIGNATURE_TEXT_RE.sub(social_links_html(), html_body)


def send_one(creds: dict[str, str], draft_path: Path, sent_dir: Path, failed_dir: Path, default_from: str) -> dict:
    payload = read_json(draft_path, {})
    from_addr = str(payload.get("from") or default_from).strip().lower()
    if from_addr not in ALLOWED_FROM:
        raise ValueError(f"From address is not allowed by National Outreach registry: {from_addr}")
    auth_user = str(creds.get("user") or "").strip().lower()
    allow_visible_sender = os.environ.get("NATIONALOUTREACH_ALLOW_VISIBLE_SENDER_HEADER") == "1"
    if from_addr != auth_user and from_addr not in VERIFIED_SEND_AS_ALIASES and not allow_visible_sender:
        raise ValueError(
            "Direct persona sends require matching mailbox authentication; "
            "the shared National Outreach mailbox route can expose a visible Sender header."
        )
    to_addrs = normalize_addresses(payload.get("to"))
    cc_addrs = normalize_addresses(payload.get("cc"))
    bcc_addrs = normalize_addresses(payload.get("bcc"))
    subject = str(payload.get("subject") or "").strip()
    body = str(payload.get("body") or "").strip()
    html_body = str(payload.get("html_body") or "").strip()
    if not to_addrs or not subject or not body:
        raise ValueError("Approved send draft requires to, subject, and body.")
    msg = EmailMessage()
    from_name = str(payload.get("from_name") or FROM_DISPLAY_NAMES.get(from_addr, "")).strip()
    msg["From"] = formataddr((from_name, from_addr)) if from_name else from_addr
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=from_addr.split("@", 1)[1])
    msg.set_content(body)
    if not html_body and SOCIAL_SIGNATURE_RE.search(body):
        html_body = body_to_html_with_signature_links(body)
    if html_body:
        html_body = ensure_signature_links_in_html(html_body)
        msg.add_alternative(html_body, subtype="html")
    recipients = to_addrs + cc_addrs + bcc_addrs
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(creds["smtp_server"], int(creds["smtp_port"]), timeout=25, context=context) as conn:
        conn.login(creds["user"], creds["password"])
        conn.send_message(msg, from_addr=from_addr, to_addrs=recipients)
    sent_dir.mkdir(parents=True, exist_ok=True)
    sent_dir.chmod(0o700)
    target = sent_dir / draft_path.name.replace(".approved.json", f".sent-{int(time.time())}.json")
    shutil.move(str(draft_path), str(target))
    target.chmod(0o600)
    task_packet = payload.get("task_packet") if isinstance(payload.get("task_packet"), dict) else {}
    if not task_packet and shared_task_flow:
        task_packet = shared_task_flow.build_packet(
            source_ref=str(payload.get("source_ref") or draft_path.name),
            intake_channel="approved-send:nationaloutreach",
            requester=str(payload.get("requester") or ""),
            owner_lane=str(payload.get("owner_lane") or from_addr),
            responsible_worker_or_persona=from_addr,
            status="reported",
            completion_or_blocker_email=msg["Message-ID"],
            next_update="sent",
        )
    elif task_packet:
        task_packet = {**task_packet, "status": "reported", "completion_or_blocker_email": msg["Message-ID"]}
    return {
        "draft": str(target),
        "from": from_addr,
        "to_count": len(to_addrs),
        "cc_count": len(cc_addrs),
        "bcc_count": len(bcc_addrs),
        "subject": subject,
        "message_id": msg["Message-ID"],
        "task_packet": task_packet,
    }


def send_approved(creds: dict[str, str], state_dir: Path, default_from: str) -> dict:
    lock_dir = state_dir / "send-approved.lock"
    try:
        lock_dir.mkdir()
        lock_acquired = True
    except FileExistsError:
        return {"sent": 0, "failed": 0, "skipped_locked": True}
    outbox = state_dir / "outbox"
    sent_dir = state_dir / "sent"
    failed_dir = state_dir / "failed"
    try:
        outbox.mkdir(parents=True, exist_ok=True)
        outbox.chmod(0o700)
        sent = []
        failures = []
        for draft_path in sorted(outbox.glob("*.approved.json")):
            if not draft_path.exists():
                continue
            try:
                result = send_one(creds, draft_path, sent_dir, failed_dir, default_from)
                sent.append(result)
            except Exception as exc:
                failed_dir.mkdir(parents=True, exist_ok=True)
                failed_dir.chmod(0o700)
                if draft_path.exists():
                    target = failed_dir / draft_path.name.replace(".approved.json", f".failed-{int(time.time())}.json")
                    shutil.move(str(draft_path), str(target))
                    target.chmod(0o600)
                    failure_draft = str(target)
                else:
                    failure_draft = str(draft_path)
                failures.append({"draft": failure_draft, "error_type": exc.__class__.__name__})
        for result in sent:
            append_jsonl(state_dir / "sent-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **result})
            if shared_task_flow and isinstance(result.get("task_packet"), dict):
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", result["task_packet"], "email_sent", message_id=result.get("message_id"))
        for failure in failures:
            append_jsonl(state_dir / "send-failures.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **failure})
            if shared_task_flow:
                packet = shared_task_flow.build_packet(
                    source_ref=str(failure.get("draft") or ""),
                    intake_channel="approved-send:nationaloutreach",
                    responsible_worker_or_persona="nationaloutreach",
                    status="blocked",
                    verification_readback="email_send_blocked",
                    next_update="review failed draft and resend only after blocker is fixed",
                )
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", packet, "email_send_blocked", error_type=failure.get("error_type"))
        return {"sent": len(sent), "failed": len(failures), "skipped_locked": False}
    finally:
        if lock_acquired:
            with contextlib.suppress(OSError):
                lock_dir.rmdir()


def main() -> int:
    args = parse_args()
    state_dir = Path(args.state_dir).expanduser()
    workspace_root = Path(args.workspace_root).expanduser()
    state_dir.mkdir(parents=True, exist_ok=True)
    state_dir.chmod(0o700)
    creds = load_credentials(Path(args.creds_file).expanduser())
    review = fetch_messages(creds, state_dir, workspace_root, args.limit, args.mailbox, args.search, args.review_old)
    scheduled_result = process_scheduled_actions(creds, state_dir) if args.send_approved else {"due": 0, "queued": 0, "skipped_resolved": 0, "failed": 0, "skipped_locked": False}
    send_result = send_approved(creds, state_dir, args.from_address) if args.send_approved else {"sent": 0, "failed": 0, "skipped_locked": False}
    summary = {
        "ok": True,
        "worker": "nationaloutreach",
        "mailbox": args.mailbox,
        "body_read": True,
        "reviewed": review["reviewed"],
        "new_items": review["new_items"],
        "mailbox_total": review["mailbox_total"],
        "active_inbox_count": review["active_inbox_count"],
        "seen_inbox_active_count": review["seen_inbox_active_count"],
        "active_inbox_logged": review["active_inbox_logged"],
        "route_counts": review["route_counts"],
        "active_route_counts": review["active_route_counts"],
        "active_inbox_subjects": review["active_inbox_subjects"],
        "skipped_seen_non_inbox": review["skipped_seen_non_inbox"],
        "queued_sends_sent": send_result["sent"],
        "queued_sends_failed": send_result["failed"],
        "queued_sends_skipped_locked": bool(send_result.get("skipped_locked")),
        "scheduled_actions_due": scheduled_result["due"],
        "scheduled_actions_queued": scheduled_result["queued"],
        "scheduled_actions_skipped_resolved": scheduled_result["skipped_resolved"],
        "scheduled_actions_failed": scheduled_result["failed"],
        "scheduled_actions_skipped_locked": bool(scheduled_result.get("skipped_locked")),
        "mailbox_mutation": False,
    }
    append_jsonl(state_dir / "cycle-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **summary})
    print(json.dumps(summary, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
