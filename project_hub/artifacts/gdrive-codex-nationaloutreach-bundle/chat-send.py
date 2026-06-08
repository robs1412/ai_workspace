#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


BUNDLE_DIR = Path(__file__).resolve().parent
DEFAULT_ALLOWLIST = BUNDLE_DIR / "chat-readback-allowlist.json"
CLIENT_FILE = Path(os.environ["GOOGLE_DRIVE_CLIENT_FILE"])
TOKEN_FILE = Path(os.environ["GOOGLE_CHAT_LOCAL_TOKEN_FILE"])
CHAT_SCOPES = [
    "https://www.googleapis.com/auth/chat.messages.create",
    "https://www.googleapis.com/auth/chat.messages.readonly",
    "https://www.googleapis.com/auth/chat.spaces.readonly",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send to approved National Outreach Google Chat targets.")
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST))
    parser.add_argument("--target", required=True, help="Allowed email, label, named space, or space id.")
    parser.add_argument("--message", help="Message text to send.")
    parser.add_argument("--message-file", help="UTF-8 file containing message text to send.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve and validate target without sending.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_client() -> dict:
    payload = load_json(CLIENT_FILE)
    return payload.get("installed") or payload.get("web") or payload


def credentials() -> Credentials:
    client = load_client()
    token = load_json(TOKEN_FILE)
    creds = Credentials(
        token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_uri=client["token_uri"],
        client_id=client["client_id"],
        client_secret=client["client_secret"],
        scopes=CHAT_SCOPES,
    )
    try:
        creds.refresh(Request())
    except RefreshError as exc:
        details = str(exc)
        if "invalid_scope" in details:
            raise RuntimeError("reauthorize_chat_with_send_scope") from exc
        raise
    return creds


def allowed_targets(allowlist: dict) -> dict[str, dict]:
    targets: dict[str, dict] = {}
    for email, item in (allowlist.get("direct_messages") or {}).items():
        label = item.get("label") or email
        record = {
            "kind": "direct_message",
            "key": email,
            "label": label,
            "space": item["space"],
        }
        targets[email.lower()] = record
        targets[label.lower()] = record
        targets[item["space"].lower()] = record
    for label, item in (allowlist.get("spaces") or {}).items():
        record = {
            "kind": "space",
            "key": label,
            "label": label,
            "space": item["space"],
        }
        targets[label.lower()] = record
        targets[item["space"].lower()] = record
    return targets


def message_text(args: argparse.Namespace) -> str:
    if bool(args.message) == bool(args.message_file):
        raise ValueError("Provide exactly one of --message or --message-file.")
    text = args.message if args.message is not None else Path(args.message_file).read_text(encoding="utf-8")
    text = text.strip()
    if not text:
        raise ValueError("Message text is empty.")
    if len(text) > 4000:
        raise ValueError("Message text is too long for this helper limit.")
    return text


def post_message(creds: Credentials, target: dict, text: str) -> dict:
    url = "https://chat.googleapis.com/v1/" + target["space"] + "/messages"
    body = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return {"ok": True, "status": response.status, "message": summarize_message(payload)}
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "error": error_body}


def summarize_message(message: dict) -> dict:
    sender = message.get("sender") or {}
    return {
        "name": message.get("name", ""),
        "createTime": message.get("createTime", ""),
        "senderType": sender.get("type", ""),
        "senderName": sender.get("name", ""),
        "thread": (message.get("thread") or {}).get("name", ""),
    }


def render(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2))
        return
    if not result.get("ok"):
        print(f"send_failed status={result.get('status')} error={result.get('error', '')}")
        return
    target = result["target"]
    if result.get("dry_run"):
        print(f"dry_run ok target={target['label']} space={target['space']}")
        return
    message = result["message"]
    print(f"sent target={target['label']} name={message['name']} createTime={message['createTime']}")


def main() -> int:
    args = parse_args()
    try:
        allowlist = load_json(Path(args.allowlist))
        targets = allowed_targets(allowlist)
        key = args.target.strip().lower()
        target = targets.get(key)
        if target is None:
            result = {"ok": False, "error": "target_not_allowed", "target": args.target}
            render(result, args.json)
            return 2
        text = message_text(args)
        if args.dry_run:
            render({"ok": True, "dry_run": True, "target": target, "message_length": len(text)}, args.json)
            return 0
        result = post_message(credentials(), target, text)
        result["target"] = target
        render(result, args.json)
        return 0 if result.get("ok") else 1
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
        render(result, args.json)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
