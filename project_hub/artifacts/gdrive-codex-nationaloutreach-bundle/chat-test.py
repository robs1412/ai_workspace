#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


CLIENT_FILE = Path(os.environ["GOOGLE_DRIVE_CLIENT_FILE"])
TOKEN_FILE = Path(os.environ["GOOGLE_CHAT_LOCAL_TOKEN_FILE"])
CHAT_SCOPES = [
    "https://www.googleapis.com/auth/chat.messages.readonly",
    "https://www.googleapis.com/auth/chat.spaces.readonly",
]


def load_client() -> dict:
    payload = json.loads(CLIENT_FILE.read_text(encoding="utf-8"))
    return payload.get("installed") or payload.get("web") or payload


def load_credentials() -> Credentials:
    client = load_client()
    token = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
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


def main() -> int:
    if not TOKEN_FILE.exists():
        print(json.dumps({"ok": False, "error": "chat_token_missing", "token_file_exists": False}))
        return 2
    creds = load_credentials()
    request = urllib.request.Request(
        "https://chat.googleapis.com/v1/spaces?pageSize=10",
        headers={"Authorization": f"Bearer {creds.token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(
            json.dumps(
                {
                    "ok": False,
                    "status": exc.code,
                    "reason": exc.reason,
                    "error_preview": body[:600],
                },
                indent=2,
            )
        )
        return 1

    spaces = payload.get("spaces") or []
    print(
        json.dumps(
            {
                "ok": True,
                "space_count": len(spaces),
                "spaces": [
                    {
                        "name": space.get("name"),
                        "displayName": space.get("displayName", ""),
                        "spaceType": space.get("spaceType", ""),
                    }
                    for space in spaces
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
