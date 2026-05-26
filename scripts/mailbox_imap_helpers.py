#!/usr/local/bin/python3.13

from __future__ import annotations

import contextlib
import json
import imaplib
import subprocess
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, parseaddr
from email import message_from_bytes
from pathlib import Path
from typing import Optional


EMAIL_TRACE_RECORDER = Path(__file__).resolve().parent / "email_trace_mysql_recorder.php"
STATE_DIR_LANE_MAP = {
    ".nationaloutreach-launch": "nationaloutreach",
    ".avignon-launch": "avignon",
    ".frank-launch": "frank",
    ".asher-launch": "asher",
    ".venetia-launch": "venetia",
}


def normalize_message_id(value: str) -> str:
    return str(value or "").strip().strip("<>").lower()


def decode_value(value: str) -> str:
    return str(value or "")


def parse_header_timestamp(value: str) -> Optional[float]:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def sender_email(value: str) -> str:
    return parseaddr(str(value or ""))[1].strip().lower()


def safe_text(value: object, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


def read_jsonl_tail(path: Path, max_lines: int = 5000) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
    except (FileNotFoundError, OSError):
        return []
    rows: list[dict] = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def mailbox_lane_from_state_dir(state_dir: Path) -> str:
    raw = str(state_dir or "")
    for marker, lane in STATE_DIR_LANE_MAP.items():
        if marker in raw:
            return lane
    return ""


def email_trace_query(command: str, *args: str) -> list[dict]:
    if not EMAIL_TRACE_RECORDER.exists():
        return []
    try:
        result = subprocess.run(
            ["php", str(EMAIL_TRACE_RECORDER), command, *[str(arg) for arg in args]],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    try:
        payload = json.loads(result.stdout.strip() or "[]")
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def normalize_reply_subject(subject: object) -> str:
    return " ".join(str(subject or "").split()).strip().lower()


def is_generic_acknowledgement_body(body: object) -> bool:
    normalized = "\n".join(str(body or "").strip().splitlines()).strip().lower()
    return normalized == "\n".join(
        [
            "hi,",
            "",
            "thanks, i have this and will handle the routine outreach follow-up from here.",
            "",
            "best,",
            "",
            "vanessa",
        ]
    )


def email_addresses_from_text(text: str) -> set[str]:
    import re

    return {addr.lower() for _, addr in re.findall(r'(?:"?([^"<]*)"?\s)?<?([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})>?', str(text), re.IGNORECASE)}


def row_time(row: dict) -> datetime | None:
    for key in ("sent_at", "logged_at", "received_at", "date", "at"):
        raw = str(row.get(key) or "").strip()
        if not raw:
            continue
        try:
            parsed = parsedate_to_datetime(raw)
        except Exception:
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except Exception:
                try:
                    parsed = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S%z")
                except Exception:
                    continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    return None


def collect_sent_entries_from_state_dirs(state_dirs: list[Path]) -> list[dict]:
    sent_entries: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for state_dir in state_dirs:
        if not state_dir:
            continue
        lane = mailbox_lane_from_state_dir(Path(state_dir))
        db_rows = email_trace_query("sent-entries", lane, "6000") if lane else []
        rows = db_rows or read_jsonl_tail(Path(state_dir) / "sent-log.jsonl", 6000)
        for row in rows:
            sent_at = row_time(row)
            subject_key = normalize_reply_subject(row.get("subject"))
            if not sent_at or not subject_key:
                continue
            message_id_norm = normalize_message_id(row.get("message_id"))
            source_ref_norm = normalize_message_id(row.get("source_ref"))
            signature = (message_id_norm, subject_key, sent_at.isoformat())
            if signature in seen:
                continue
            seen.add(signature)
            sent_payload: dict = {}
            draft_path_raw = str(row.get("draft") or "").strip()
            if draft_path_raw and not db_rows:
                draft_path = Path(draft_path_raw)
                try:
                    loaded = json.loads(draft_path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        sent_payload = loaded
                except (OSError, json.JSONDecodeError):
                    sent_payload = {}
            task_packet = sent_payload.get("task_packet") if isinstance(sent_payload.get("task_packet"), dict) else {}
            generic_ack = bool(sent_payload.get("generic_acknowledgement")) or is_generic_acknowledgement_body(sent_payload.get("body"))
            sent_entries.append({
                "sent_at": sent_at,
                "subject_key": subject_key,
                "subject": safe_text(row.get("subject"), 180),
                "message_id": safe_text(row.get("message_id"), 180),
                "message_id_norm": message_id_norm,
                "source_ref": safe_text(row.get("source_ref"), 180),
                "source_ref_norm": source_ref_norm,
                "from": safe_text(row.get("from"), 180),
                "recipients": " ".join(
                    str(value or "")
                    for value in (
                        row.get("to"),
                        row.get("to_addresses"),
                        row.get("cc"),
                        row.get("cc_addresses"),
                        row.get("bcc"),
                        row.get("bcc_addresses"),
                        sent_payload.get("to"),
                        sent_payload.get("cc"),
                        sent_payload.get("bcc"),
                    )
                ).strip(),
                "thread_refs": set(),
                "generic_acknowledgement": generic_ack,
                "task_packet_status": safe_text(task_packet.get("status"), 80),
            })
    return sent_entries


def collect_sent_entries(state_dir: Path) -> list[dict]:
    return collect_sent_entries_from_state_dirs([state_dir])


def collect_owner_replies_from_db(mailbox_lane: str, owners: list[str], limit: int = 6000) -> list[dict]:
    owner_csv = ",".join(sorted({sender_email(owner) for owner in owners if sender_email(owner)}))
    if not mailbox_lane or not owner_csv:
        return []
    replies: list[dict] = []
    for row in email_trace_query("owner-replies", mailbox_lane, owner_csv, str(limit)):
        received_at = row_time(row)
        subject_key = normalize_reply_subject(row.get("subject"))
        source_id = normalize_message_id(
            row.get("source_message_id") or row.get("source_ref") or row.get("message_id_norm")
        )
        owner_email = sender_email(row.get("from"))
        if not source_id or not subject_key or not received_at or not owner_email:
            continue
        replies.append({
            "mailbox": mailbox_lane,
            "source_message_id": source_id,
            "subject": safe_text(row.get("subject"), 180),
            "subject_key": subject_key,
            "from": safe_text(row.get("from"), 180),
            "owner_email": owner_email,
            "received_at": received_at,
            "route": safe_text(row.get("current_status") or row.get("latest_event"), 80),
            "session_id": safe_text(row.get("workspaceboard_session"), 80),
            "task_id": safe_text(row.get("ops_portal_or_domain_task"), 120),
            "thread_refs": sorted(
                {
                    normalize_message_id(row.get("message_id_norm")),
                    normalize_message_id(row.get("source_ref")),
                    normalize_message_id(row.get("source_message_id")),
                }
                - {""}
            ),
        })
    return replies


def collect_active_inbox_from_db(mailbox_lane: str, limit: int = 6000) -> list[dict]:
    if not mailbox_lane:
        return []
    rows = email_trace_query("active-inbox", mailbox_lane, str(limit))
    return [row for row in rows if isinstance(row, dict)]


def collect_seen_source_ids_from_db(mailbox_lane: str, limit: int = 20000) -> set[str]:
    if not mailbox_lane:
        return set()
    seen: set[str] = set()
    for row in email_trace_query("seen-source-ids", mailbox_lane, str(limit)):
        if not isinstance(row, dict):
            continue
        source_id = normalize_message_id(
            row.get("source_message_id") or row.get("source_ref") or row.get("message_id_norm")
        )
        if source_id:
            seen.add(source_id)
    return seen


def sent_entries_have_source_ref(sent_entries: list[dict], source_ref: str) -> bool:
    source_ref_norm = normalize_message_id(source_ref)
    if not source_ref_norm:
        return False
    for sent in sent_entries:
        if source_ref_norm == normalize_message_id(sent.get("source_ref")):
            return True
        if source_ref_norm == normalize_message_id(sent.get("message_id")):
            return True
        if source_ref_norm and source_ref_norm in str(sent.get("message_id", "")).lower():
            return True
    return False


def owner_reply_has_later_send(reply: dict, sent_entries: list[dict]) -> bool:
    reply_at = reply.get("received_at")
    subject_key = reply.get("subject_key", "")
    owner_email = reply.get("owner_email", "")
    source_id = normalize_message_id(reply.get("source_message_id", ""))
    reply_refs = set(reply.get("thread_refs") or [])
    for sent in sent_entries:
        if not isinstance(reply_at, datetime):
            continue
        if sent["sent_at"] < reply_at:
            continue
        if sent.get("generic_acknowledgement"):
            continue
        if source_id and source_id == sent.get("source_ref_norm"):
            return True
        if source_id and source_id == sent.get("message_id_norm"):
            return True
        if reply_refs and sent.get("message_id_norm") in reply_refs:
            return True
        if reply_refs and sent.get("source_ref_norm") in reply_refs:
            return True
        recipients = email_addresses_from_text(sent.get("recipients", ""))
        sent_subject = sent.get("subject_key", "")
        if (
            owner_email
            and owner_email in recipients
            and subject_key
            and sent_subject
            and (subject_key in sent_subject or sent_subject in subject_key)
        ):
            return True
        if source_id and source_id in str(sent.get("message_id", "")).lower():
            return True
    return False


def mailbox_has_matching_reply(creds: dict[str, str], check: dict) -> bool:
    from_contains = str(check.get("from_contains") or "").lower().strip()
    subject_contains = str(check.get("subject_contains") or "").lower().strip()
    after_ts = parse_header_timestamp(str(check.get("after") or ""))
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
            try:
                typ, msgdata = conn.uid("FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)])")
            except imaplib.IMAP4.abort:
                return False
            if typ != "OK":
                continue
            raw = b""
            for part in msgdata or []:
                if isinstance(part, tuple):
                    raw += part[1]
            msg = message_from_bytes(raw)
            sender = decode_value(msg.get("From", "")).lower()
            subject = decode_value(msg.get("Subject", ""))
            if from_contains and from_contains not in sender:
                continue
            if subject_contains and subject_contains not in subject:
                continue
            if after_ts is not None:
                msg_ts = parse_header_timestamp(decode_value(msg.get("Date", "")))
                if msg_ts is None or msg_ts <= after_ts:
                    continue
            return True
        return False
    except imaplib.IMAP4.abort:
        return False
    finally:
        with contextlib.suppress(Exception):
            conn.logout()


def mailbox_has_matching_reply_from_aliases(
    creds: dict[str, str],
    from_contains_list: list[str],
    subject_contains: str,
    after_header_date: str,
) -> bool:
    filtered_aliases = [token.strip().lower() for token in from_contains_list if str(token or "").strip()]
    if not filtered_aliases or not str(subject_contains or "").strip():
        return False
    after_ts = parse_header_timestamp(after_header_date)
    conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]))
    try:
        conn.login(creds["user"], creds["password"])
        conn.select('"[Gmail]/All Mail"', readonly=True)
        typ, data = conn.uid("SEARCH", None, "ALL")
        if typ != "OK":
            return False
        for uid in reversed((data[0].split() if data and data[0] else [])[-500:]):
            try:
                typ, msgdata = conn.uid("FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)])")
            except imaplib.IMAP4.abort:
                return False
            if typ != "OK":
                continue
            raw = b""
            for part in msgdata or []:
                if isinstance(part, tuple):
                    raw += part[1]
            msg = message_from_bytes(raw)
            sender = decode_value(msg.get("From", "")).lower()
            if not any(token in sender for token in filtered_aliases):
                continue
            subject = decode_value(msg.get("Subject", ""))
            if subject_contains.lower() not in subject.lower():
                continue
            if after_ts is not None:
                msg_ts = parse_header_timestamp(decode_value(msg.get("Date", "")))
                if msg_ts is None or msg_ts <= after_ts:
                    continue
            return True
        return False
    except imaplib.IMAP4.abort:
        return False
    finally:
        with contextlib.suppress(Exception):
            conn.logout()
