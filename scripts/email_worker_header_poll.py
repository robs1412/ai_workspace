#!/usr/bin/env python3

from __future__ import annotations

import argparse
import imaplib
import json
import os
import re
import socket
import sys
import time
from email import message_from_bytes
from email.header import decode_header, make_header
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Header-only email worker polling cycle.")
    parser.add_argument("--worker", required=True, help="Worker slug, for example asher or venetia.")
    parser.add_argument("--creds-file", required=True, help="Private credential file.")
    parser.add_argument("--workspace-root", required=True, help="Worker workspace root.")
    parser.add_argument("--state-dir", required=True, help="Machine-local state directory.")
    parser.add_argument("--limit", type=int, default=200, help="Maximum INBOX messages to inspect.")
    parser.add_argument("--mail-server", default="", help="Optional IMAP server override. Defaults to credential Mail server or imap.gmail.com.")
    parser.add_argument("--manager", default="avignon", help="Manager label to record in header-only logs.")
    return parser.parse_args()


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
    }


def normalize_message_id(value: str) -> str:
    return str(value or "").strip().strip("<>").lower()


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return set()
    return {str(item) for item in data.get("seen_message_ids", []) if item}


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


def fetch_headers(creds: dict[str, str], limit: int) -> list[dict]:
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
        status, msg_data = conn.fetch(imap_id, "(BODY.PEEK[HEADER])")
        if status != "OK":
            continue
        raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
        if not raw:
            continue
        msg = message_from_bytes(raw)
        messages.append(
            {
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
        )
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
    start = time.time()
    try:
        creds = load_credentials(creds_path, args.mail_server)
        seen = load_seen(seen_path)
        headers = fetch_headers(creds, args.limit)
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
                "body_read": False,
                "mailbox_mutation": False,
                **item,
            }
            new_rows.append(row)
            append_jsonl(log_path, row)
            append_jsonl(worker_log_path, row)
        save_seen(seen_path, seen)
        append_jsonl(
            log_path,
            {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": args.worker,
                "event": "cycle_complete",
                "headers_seen": len(headers),
                "new_headers": len(new_rows),
                "duration_seconds": round(time.time() - start, 3),
                "host": socket.gethostname(),
            },
        )
        print(json.dumps({"ok": True, "worker": args.worker, "headers_seen": len(headers), "new_headers": len(new_rows)}))
        return 0
    except Exception as exc:
        append_jsonl(
            log_path,
            {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": args.worker,
                "event": "cycle_failed",
                "error_type": exc.__class__.__name__,
                "error": re.sub(r"(?i)(password|app pw|secret|token)\\S*", "[REDACTED]", str(exc)),
            },
        )
        print(f"poll failed for {args.worker}: {exc.__class__.__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
