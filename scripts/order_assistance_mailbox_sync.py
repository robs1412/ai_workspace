#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import hashlib
import imaplib
import json
import re
import subprocess
import sys
import time
from email import message_from_bytes
from email.message import Message
from email.utils import parseaddr
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from email_worker_header_poll import (  # noqa: E402
    append_jsonl,
    decode_value,
    load_credentials,
    load_seen,
    message_text,
    normalize_message_id,
    save_seen,
    store_body,
)

DEFAULT_IMPORT_COMMAND = (
    "ssh -o BatchMode=yes ftp.koval-distillery.com "
    "'cd /home/koval/public_html/order && php scripts/order_customer_message_import.php'"
)
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024
MAILBOX_FOLDERS = ("INBOX", "Spam", "Junk", "INBOX.Spam", "INBOX.Junk")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Poll sales@orderkoval.com and import messages into Order customer threads.")
    parser.add_argument("--worker", default="orderassistance")
    parser.add_argument("--creds-file", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--mail-server", default="")
    parser.add_argument("--import-command", default=DEFAULT_IMPORT_COMMAND)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def clean_header(value: str, limit: int = 255) -> str:
    text = re.sub(r"[\r\n]+", " ", str(value or "")).strip()
    return text[:limit]


def safe_path_segment(value: str, fallback: str = "item", limit: int = 120) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value or "").strip()).strip(".-")
    return (safe[:limit] or fallback)


def safe_filename(value: str, fallback: str = "attachment") -> str:
    name = Path(str(value or "").replace("\\", "/")).name.strip()
    return safe_path_segment(name, fallback=fallback, limit=160)


def extract_attachments(msg: Message, attachment_root: Path, source_id: str) -> list[dict]:
    attachments: list[dict] = []
    message_dir = attachment_root / safe_path_segment(source_id, fallback="message")
    for index, part in enumerate(msg.walk() if msg.is_multipart() else [msg], start=1):
        if part.is_multipart():
            continue
        content_disposition = (part.get("Content-Disposition") or "").lower()
        raw_filename = part.get_filename()
        filename = safe_filename(decode_value(raw_filename or ""), fallback=f"attachment-{index}")
        if not raw_filename and "attachment" not in content_disposition:
            continue
        payload = part.get_payload(decode=True) or b""
        byte_size = len(payload)
        content_type = clean_header(part.get_content_type(), 160)
        sha256 = hashlib.sha256(payload).hexdigest() if payload else ""
        row = {
            "filename": filename,
            "content_type": content_type,
            "byte_size": byte_size,
            "sha256": sha256,
            "storage_path": "",
            "storage_status": "stored_private",
        }
        if byte_size > MAX_ATTACHMENT_BYTES:
            row["storage_status"] = "skipped_too_large"
            attachments.append(row)
            continue
        message_dir.mkdir(parents=True, exist_ok=True)
        if str(message_dir).startswith("/Users/admin/.") or ".private" in message_dir.parts:
            message_dir.chmod(0o700)
        target = message_dir / filename
        if target.exists():
            stem = target.stem[:120] or "attachment"
            suffix = target.suffix[:20]
            target = message_dir / f"{stem}-{index}{suffix}"
        target.write_bytes(payload)
        if str(target).startswith("/Users/admin/.") or ".private" in target.parts:
            target.chmod(0o600)
        row["storage_path"] = str(target)
        attachments.append(row)
    return attachments


def fetch_order_messages(creds: dict[str, str], limit: int, attachment_root: Path, seen: set[str]) -> list[dict]:
    conn = imaplib.IMAP4_SSL(creds["server"], int(creds["imap_port"]), timeout=25)
    conn.login(creds["user"], creds["password"])
    try:
        messages: list[dict] = []
        per_folder_limit = max(1, limit)
        for folder in MAILBOX_FOLDERS:
            status, _ = conn.select(folder, readonly=True)
            if status != "OK":
                continue
            status, data = conn.search(None, "ALL")
            if status != "OK":
                continue
            ids = data[0].split()[-per_folder_limit:] if data and data[0] else []
            for imap_id in ids:
                status, msg_data = conn.fetch(imap_id, "(BODY.PEEK[])")
                if status != "OK":
                    continue
                raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
                if not raw:
                    continue
                msg = message_from_bytes(raw)
                message_id = decode_value(msg.get("Message-ID", ""))
                imap_id_text = imap_id.decode("ascii", errors="replace")
                source_id = normalize_message_id(message_id) or f"imap-{safe_path_segment(folder)}-{imap_id_text}"
                is_seen = source_id in seen
                messages.append(
                    {
                        "folder": folder,
                        "imap_id": imap_id_text,
                        "message_id": message_id,
                        "date": decode_value(msg.get("Date", "")),
                        "from": decode_value(msg.get("From", "")),
                        "to": decode_value(msg.get("To", "")),
                        "cc": decode_value(msg.get("Cc", "")),
                        "subject": decode_value(msg.get("Subject", "")),
                        "in_reply_to": decode_value(msg.get("In-Reply-To", "")),
                        "references": decode_value(msg.get("References", "")),
                        "body": "" if is_seen else message_text(msg),
                        "attachments": [] if is_seen else extract_attachments(msg, attachment_root, source_id),
                    }
                )
        return messages
    finally:
        conn.logout()


def import_message(command: str, payload: dict, dry_run: bool) -> dict:
    if dry_run:
        return {"ok": True, "status": "dry_run", "thread_code": "", "message_row_id": 0}
    result = subprocess.run(
        command,
        input=json.dumps(payload, ensure_ascii=True),
        text=True,
        shell=True,
        capture_output=True,
        check=False,
        timeout=45,
    )
    if result.returncode != 0:
        error = re.sub(r"(?i)(password|app pw|secret|token)\S*", "[REDACTED]", (result.stderr or result.stdout or "").strip())
        raise RuntimeError(error or f"import command failed with exit {result.returncode}")
    try:
        parsed = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError("import command returned invalid JSON") from exc
    if not parsed.get("ok"):
        raise RuntimeError(str(parsed))
    return parsed


def main() -> int:
    args = parse_args()
    state_dir = Path(args.state_dir).expanduser()
    workspace_root = Path(args.workspace_root).expanduser()
    creds = load_credentials(Path(args.creds_file).expanduser(), args.mail_server)
    seen_path = state_dir / "seen-headers.json"
    log_path = state_dir / "header-poll-log.jsonl"
    workspace_log_path = workspace_root / "header-poll-log.jsonl"
    body_dir = state_dir / "bodies"
    attachment_dir = state_dir / "attachments"
    started = time.time()

    try:
        seen = load_seen(seen_path)
        headers = fetch_order_messages(creds, args.limit, attachment_dir, seen)
        imported = 0
        duplicates = 0
        failures = 0
        new_rows = 0
        for item in headers:
            source_id = normalize_message_id(item.get("message_id", "")) or f"imap-{item.get('imap_id', '')}"
            if source_id in seen:
                continue
            new_rows += 1
            body = str(item.get("body") or "").strip()
            if body == "":
                body = (
                    "[No readable plain-text body was extracted from this mailbox message. "
                    "Check the original mailbox message for HTML-only, attachment-only, or spam-wrapped content.]"
                )
            body_path = store_body(body_dir, source_id, body)
            from_name, from_email = parseaddr(str(item.get("from") or ""))
            payload = {
                "source": "mailbox_spam" if str(item.get("folder") or "").lower() != "inbox" else "mailbox",
                "from_email": from_email.strip().lower(),
                "from_name": clean_header(from_name, 160),
                "to_email": clean_header(item.get("to", "")),
                "cc_email": clean_header(item.get("cc", "")),
                "subject": clean_header(item.get("subject", "")),
                "body_text": body,
                "message_id": clean_header(item.get("message_id", "")),
                "in_reply_to": clean_header(item.get("in_reply_to", "")),
                "references_header": clean_header(item.get("references", ""), 2000),
                "attachments": item.get("attachments") if isinstance(item.get("attachments"), list) else [],
            }
            row = {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": args.worker,
                "email": creds["user"],
                "event": "mailbox_message_seen",
                "folder": item.get("folder", ""),
                "source_message_id": source_id,
                "message_id": item.get("message_id", ""),
                "subject": item.get("subject", ""),
                "from": item.get("from", ""),
                "to": item.get("to", ""),
                "cc": item.get("cc", ""),
                "date": item.get("date", ""),
                "body_read": True,
                "body_chars": len(body),
                "body_path": str(body_path),
                "attachment_count": len(payload["attachments"]),
                "attachments": payload["attachments"],
                "mailbox_mutation": False,
            }
            try:
                import_result = import_message(args.import_command, payload, args.dry_run)
                row["event"] = "mailbox_message_imported"
                row["import_status"] = import_result.get("status", "")
                row["thread_code"] = import_result.get("thread_code", "")
                row["message_row_id"] = import_result.get("message_row_id", 0)
                row["imported_attachment_count"] = import_result.get("attachment_count", 0)
                row["owner_notified"] = bool(import_result.get("owner_notified"))
                if import_result.get("status") == "duplicate":
                    duplicates += 1
                else:
                    imported += 1
                seen.add(source_id)
            except Exception as exc:
                failures += 1
                row["event"] = "mailbox_message_import_failed"
                row["error_type"] = exc.__class__.__name__
                row["error"] = re.sub(r"(?i)(password|app pw|secret|token)\S*", "[REDACTED]", str(exc))
            append_jsonl(log_path, row)
            append_jsonl(workspace_log_path, row)
        save_seen(seen_path, seen)
        summary = {
            "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "worker": args.worker,
            "event": "cycle_complete",
            "headers_seen": len(headers),
            "new_headers": new_rows,
            "imported": imported,
            "duplicates": duplicates,
            "failures": failures,
            "duration_seconds": round(time.time() - started, 3),
            "dry_run": bool(args.dry_run),
        }
        append_jsonl(log_path, summary)
        print(json.dumps({"ok": failures == 0, **summary}, ensure_ascii=True))
        return 0 if failures == 0 else 1
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
        print(f"order assistance sync failed: {exc.__class__.__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
