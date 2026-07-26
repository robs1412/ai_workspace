#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_STATE_DIR = "/Users/admin/.orderassistance-launch/state"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read private Order Assistance mailbox thread state for AI review.")
    parser.add_argument("--state-dir", default=DEFAULT_STATE_DIR)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--body-chars", type=int, default=900)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--show-private-paths", action="store_true")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def normalize_source_id(value: str) -> str:
    return str(value or "").strip().strip("<>").lower()


def safe_path_segment(value: str, fallback: str = "item", limit: int = 120) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value or "").strip()).strip(".-")
    return (safe[:limit] or fallback)


def one_line(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def body_excerpt(path_value: str, limit: int) -> str:
    if limit <= 0 or not path_value:
        return ""
    path = Path(path_value)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def attachment_inventory(state_dir: Path, source_id: str, row_attachments: list, show_paths: bool) -> list[dict]:
    rows: list[dict] = []
    for item in row_attachments:
        if not isinstance(item, dict):
            continue
        row = {
            "filename": item.get("filename", "attachment"),
            "content_type": item.get("content_type", ""),
            "byte_size": int(item.get("byte_size") or 0),
            "storage_status": item.get("storage_status", ""),
        }
        if show_paths and item.get("storage_path"):
            row["private_path"] = item.get("storage_path")
        rows.append(row)
    if rows:
        return rows
    message_dir = state_dir / "attachments" / safe_path_segment(source_id, fallback="message")
    if not message_dir.exists() or not message_dir.is_dir():
        return []
    for path in sorted(message_dir.iterdir()):
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        row = {"filename": path.name, "content_type": "", "byte_size": size, "storage_status": "stored_private"}
        if show_paths:
            row["private_path"] = str(path)
        rows.append(row)
    return rows


def build_messages(state_dir: Path, limit: int, body_chars: int, show_paths: bool) -> list[dict]:
    rows = load_jsonl(state_dir / "header-poll-log.jsonl")
    messages: list[dict] = []
    seen: set[str] = set()
    for row in reversed(rows):
        if row.get("event") not in {"mailbox_message_imported", "mailbox_message_seen", "mailbox_message_import_failed"}:
            continue
        source_id = normalize_source_id(row.get("source_message_id") or row.get("message_id") or "")
        dedupe = source_id or f"{row.get('logged_at', '')}:{row.get('subject', '')}"
        if dedupe in seen:
            continue
        seen.add(dedupe)
        row_attachments = row.get("attachments") if isinstance(row.get("attachments"), list) else []
        attachments = attachment_inventory(state_dir, source_id, row_attachments, show_paths)
        message = {
            "logged_at": row.get("logged_at", ""),
            "event": row.get("event", ""),
            "thread_code": row.get("thread_code", ""),
            "import_status": row.get("import_status", ""),
            "subject": row.get("subject", ""),
            "from": row.get("from", ""),
            "to": row.get("to", ""),
            "cc": row.get("cc", ""),
            "date": row.get("date", ""),
            "source_message_id": source_id,
            "body_excerpt": body_excerpt(str(row.get("body_path", "")), body_chars),
            "attachments": attachments,
            "attachment_count": len(attachments) or int(row.get("attachment_count") or 0),
        }
        if show_paths:
            message["body_path"] = row.get("body_path", "")
        messages.append(message)
        if len(messages) >= limit:
            break
    return messages


def print_text(messages: list[dict]) -> None:
    if not messages:
        print("No Order Assistance mailbox messages have been logged yet.")
        return
    for index, message in enumerate(messages, start=1):
        print(f"{index}. {one_line(message.get('subject', '')) or '(no subject)'}")
        print(f"   from: {one_line(message.get('from', ''))}")
        print(f"   date: {one_line(message.get('date', '')) or one_line(message.get('logged_at', ''))}")
        print(f"   status: {one_line(message.get('event', ''))} {one_line(message.get('import_status', ''))}".rstrip())
        if message.get("thread_code"):
            print(f"   thread: {one_line(message.get('thread_code', ''))}")
        if message.get("attachment_count"):
            print(f"   attachments: {message.get('attachment_count')}")
            for attachment in message.get("attachments", []):
                bits = [
                    str(attachment.get("filename", "attachment")),
                    f"{attachment.get('byte_size', 0)} bytes",
                ]
                if attachment.get("content_type"):
                    bits.append(str(attachment.get("content_type")))
                if attachment.get("storage_status"):
                    bits.append(str(attachment.get("storage_status")))
                print(f"     - {'; '.join(bits)}")
        excerpt = str(message.get("body_excerpt") or "").strip()
        if excerpt:
            print("   body:")
            for line in excerpt.splitlines():
                print(f"     {line}")
        print()


def main() -> int:
    args = parse_args()
    messages = build_messages(
        Path(args.state_dir).expanduser(),
        max(1, args.limit),
        max(0, args.body_chars),
        bool(args.show_private_paths),
    )
    if args.json:
        print(json.dumps({"ok": True, "messages": messages}, ensure_ascii=True, indent=2))
    else:
        print_text(messages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
