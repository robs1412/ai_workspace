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
import time
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import EmailMessage, Message
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path


ALLOWED_FROM = {
    "codex@kovaldistillery.com",
    "nationaloutreach@kovaldistillery.com",
    "vanessa.sterling@kovaldistillery.com",
}

FROM_DISPLAY_NAMES = {
    "nationaloutreach@kovaldistillery.com": "Vanessa Sterling",
    "vanessa.sterling@kovaldistillery.com": "Vanessa Sterling",
}

SENSITIVE_PATTERNS = re.compile(
    r"\b(password|passcode|2fa|verification code|wire|bank account|routing number|gift card|urgent payment|w-?9|ssn|social security|credential|oauth|token)\b",
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


def classify_message(headers: dict[str, str], body: str) -> dict[str, str]:
    combined = f"{headers.get('subject', '')}\n{headers.get('from', '')}\n{headers.get('to', '')}\n{headers.get('cc', '')}\n{body}"
    if SENSITIVE_PATTERNS.search(combined):
        return {
            "route": "security-guard",
            "suggestion": "Review as sensitive/security-gated before any reply or filing.",
            "send_allowed": "no",
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
    review_log = state_dir / "mail-review.jsonl"
    workspace_review = workspace_root / "mail-review.jsonl"
    body_dir = state_dir / "bodies"
    seen = load_seen(seen_path)
    reviewed = 0
    new_items = 0
    route_counts: dict[str, int] = {}
    conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]), timeout=25)
    try:
        conn.login(creds["user"], creds["password"])
        conn.select(mailbox, readonly=True)
        status, data = conn.search(None, search)
        if status != "OK":
            raise RuntimeError(f"IMAP search failed: {status}")
        ids = data[0].split()[-limit:] if data and data[0] else []
        for imap_id in ids:
            status, msg_data = conn.fetch(imap_id, "(RFC822)")
            if status != "OK":
                continue
            raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
            if not raw:
                continue
            msg = message_from_bytes(raw)
            source_id = normalize_message_id(decode_value(msg.get("Message-ID", ""))) or f"imap-{imap_id.decode('ascii', errors='replace')}"
            if source_id in seen and not review_old:
                continue
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
            row = {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": "nationaloutreach",
                "email": creds["user"],
                "source_message_id": source_id,
                "body_read": True,
                "body_path": str(body_path),
                "body_chars": len(body),
                "mailbox_mutation": False,
                **headers,
                **classification,
            }
            append_jsonl(review_log, row)
            append_jsonl(workspace_review, {k: v for k, v in row.items() if k != "body_path"})
            seen.add(source_id)
            reviewed += 1
            new_items += 1
            route_counts[classification["route"]] = route_counts.get(classification["route"], 0) + 1
    finally:
        try:
            conn.logout()
        except Exception:
            pass
    save_seen(seen_path, seen)
    return {"reviewed": reviewed, "new_items": new_items, "route_counts": route_counts}


def normalize_addresses(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def send_one(creds: dict[str, str], draft_path: Path, sent_dir: Path, failed_dir: Path, default_from: str) -> dict:
    payload = read_json(draft_path, {})
    from_addr = str(payload.get("from") or default_from).strip().lower()
    if from_addr not in ALLOWED_FROM:
        raise ValueError(f"From address is not allowed by National Outreach registry: {from_addr}")
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
    if html_body:
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
    return {
        "draft": str(target),
        "from": from_addr,
        "to_count": len(to_addrs),
        "cc_count": len(cc_addrs),
        "bcc_count": len(bcc_addrs),
        "subject": subject,
        "message_id": msg["Message-ID"],
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
        for failure in failures:
            append_jsonl(state_dir / "send-failures.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **failure})
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
    send_result = send_approved(creds, state_dir, args.from_address) if args.send_approved else {"sent": 0, "failed": 0, "skipped_locked": False}
    summary = {
        "ok": True,
        "worker": "nationaloutreach",
        "mailbox": args.mailbox,
        "body_read": True,
        "reviewed": review["reviewed"],
        "route_counts": review["route_counts"],
        "queued_sends_sent": send_result["sent"],
        "queued_sends_failed": send_result["failed"],
        "queued_sends_skipped_locked": bool(send_result.get("skipped_locked")),
        "mailbox_mutation": False,
    }
    append_jsonl(state_dir / "cycle-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **summary})
    print(json.dumps(summary, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
