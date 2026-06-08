#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


BUNDLE_DIR = Path(__file__).resolve().parent
DEFAULT_ALLOWLIST = BUNDLE_DIR / "chat-readback-allowlist.json"
CLIENT_FILE = Path(os.environ["GOOGLE_DRIVE_CLIENT_FILE"])
TOKEN_FILE = Path(os.environ["GOOGLE_CHAT_LOCAL_TOKEN_FILE"])
CHAT_SCOPES = [
    "https://www.googleapis.com/auth/chat.messages.readonly",
    "https://www.googleapis.com/auth/chat.spaces.readonly",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read only approved National Outreach Google Chat spaces.")
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST))
    parser.add_argument("--target", default="all", help="Allowed email, label, named space, space id, or all.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list-allowed", action="store_true")
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
    creds.refresh(Request())
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


def request_json(creds: Credentials, path: str, params: dict[str, object] | None = None) -> dict:
    url = "https://chat.googleapis.com/v1/" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {creds.token}"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def read_messages(creds: Credentials, target: dict, limit: int) -> dict:
    payload = request_json(
        creds,
        f"{target['space']}/messages",
        {"pageSize": max(1, min(limit, 20)), "orderBy": "createTime desc"},
    )
    messages = []
    for message in payload.get("messages") or []:
        text = (message.get("text") or "").strip()
        sender = message.get("sender") or {}
        messages.append(
            {
                "name": message.get("name", ""),
                "createTime": message.get("createTime", ""),
                "senderType": sender.get("type", ""),
                "senderName": sender.get("name", ""),
                "text": text,
            }
        )
    return {**target, "messages": messages}


def main() -> int:
    args = parse_args()
    allowlist = load_json(Path(args.allowlist))
    targets = allowed_targets(allowlist)
    visible_targets = sorted(
        {record["space"]: record for record in targets.values()}.values(),
        key=lambda item: (item["kind"], item["label"]),
    )
    if args.list_allowed:
        print(json.dumps({"ok": True, "allowed": visible_targets}, indent=2))
        return 0

    key = args.target.strip().lower()
    if key == "all":
        selected = visible_targets
    else:
        selected = [targets[key]] if key in targets else []
    if not selected:
        print(json.dumps({"ok": False, "error": "target_not_allowed", "target": args.target}, indent=2))
        return 2

    creds = credentials()
    result = {"ok": True, "targets": [read_messages(creds, target, args.limit) for target in selected]}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for target in result["targets"]:
            print(f"{target['label']} ({target['space']})")
            for message in target["messages"]:
                print(f"- {message['createTime']} {message['senderType']}: {message['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
