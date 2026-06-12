#!/usr/local/bin/python3.13
"""Create or update Ezra's liquor legal/marketing guide in AI Cloud Google Docs.

This script intentionally uses direct Google API HTTP calls so it does not
depend on google-api-python-client being installed in the shell environment.
It does not print token values or credential paths.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path


DRIVE_ID = "0AP-Yf32mH4IHUk9PVA"
DOC_TITLE = "Ezra Katz - Liquor Legal, Distribution, and Marketing Review Guide"
SOURCE_FILE = Path("project_hub/artifacts/legal-affairs/ezra-liquor-legal-marketing-guide-2026-06-10.md")
CLIENT_FILE = Path(".private/google-oauth/frank-drive-desktop-client.json")
TOKEN_FILE = Path(".private/google-oauth/frank-google-drive-token.json")
TOKEN_URI = "https://oauth2.googleapis.com/token"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_access_token() -> str:
    client_payload = load_json(CLIENT_FILE)
    client = client_payload.get("installed") or client_payload.get("web") or client_payload
    token_payload = load_json(TOKEN_FILE)
    access_token = str(token_payload.get("access_token") or "")
    if access_token:
        # Try the stored token first; refresh only if a simple metadata call fails.
        try:
            api_json(
                "GET",
                "https://www.googleapis.com/drive/v3/about?fields=user",
                access_token,
            )
            return access_token
        except RuntimeError:
            pass

    data = urllib.parse.urlencode(
        {
            "client_id": client["client_id"],
            "client_secret": client.get("client_secret", ""),
            "refresh_token": token_payload["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        client.get("token_uri", TOKEN_URI),
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        refreshed = json.loads(response.read().decode("utf-8"))
    token = str(refreshed.get("access_token") or "")
    if not token:
        raise RuntimeError("Google token refresh did not return an access token.")
    return token


def api_json(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    body = None
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google API {method} failed with HTTP {exc.code}: {detail[:500]}") from exc
    return json.loads(raw) if raw else {}


def quote_query(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_folder(token: str) -> dict:
    wanted = ["Legal Affairs", "AI Workers", "IT"]
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    params = urllib.parse.urlencode(
        {
            "q": query,
            "corpora": "drive",
            "driveId": DRIVE_ID,
            "includeItemsFromAllDrives": "true",
            "supportsAllDrives": "true",
            "fields": "files(id,name,webViewLink)",
            "pageSize": "100",
        }
    )
    result = api_json("GET", f"https://www.googleapis.com/drive/v3/files?{params}", token)
    folders = result.get("files", [])
    by_name = {f["name"]: f for f in folders}
    for name in wanted:
        if name in by_name:
            return by_name[name]
    raise RuntimeError("No suitable AI Cloud folder found.")


def find_doc(token: str, folder_id: str) -> dict | None:
    query = (
        f"name = '{quote_query(DOC_TITLE)}' and "
        "mimeType = 'application/vnd.google-apps.document' and "
        f"'{folder_id}' in parents and trashed = false"
    )
    params = urllib.parse.urlencode(
        {
            "q": query,
            "corpora": "drive",
            "driveId": DRIVE_ID,
            "includeItemsFromAllDrives": "true",
            "supportsAllDrives": "true",
            "fields": "files(id,name,webViewLink,modifiedTime)",
            "pageSize": "10",
        }
    )
    result = api_json("GET", f"https://www.googleapis.com/drive/v3/files?{params}", token)
    files = result.get("files", [])
    return files[0] if files else None


def create_doc(token: str, folder_id: str) -> dict:
    params = urllib.parse.urlencode(
        {
            "supportsAllDrives": "true",
            "fields": "id,name,webViewLink,parents",
        }
    )
    payload = {
        "name": DOC_TITLE,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    return api_json("POST", f"https://www.googleapis.com/drive/v3/files?{params}", token, payload)


def replace_doc_text(token: str, doc_id: str, text: str) -> dict:
    doc = api_json(
        "GET",
        f"https://docs.googleapis.com/v1/documents/{doc_id}?fields=title,body/content/endIndex",
        token,
    )
    content = doc.get("body", {}).get("content", [])
    end_index = content[-1].get("endIndex", 1) if content else 1
    requests = []
    if end_index > 2:
        requests.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index - 1}}})
    requests.append({"insertText": {"location": {"index": 1}, "text": text}})
    api_json(
        "POST",
        f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
        token,
        {"requests": requests},
    )
    return api_json(
        "GET",
        f"https://docs.googleapis.com/v1/documents/{doc_id}?fields=title,body/content/paragraph/elements/textRun/content",
        token,
    )


def main() -> int:
    if not SOURCE_FILE.exists():
        raise RuntimeError(f"Source guide not found: {SOURCE_FILE}")
    text = SOURCE_FILE.read_text(encoding="utf-8")
    token = get_access_token()
    folder = find_folder(token)
    doc = find_doc(token, folder["id"]) or create_doc(token, folder["id"])
    readback = replace_doc_text(token, doc["id"], text)
    meta = api_json(
        "GET",
        f"https://www.googleapis.com/drive/v3/files/{doc['id']}?supportsAllDrives=true&fields=id,name,webViewLink,modifiedTime,parents",
        token,
    )
    body_text = json.dumps(readback)
    result = {
        "ok": DOC_TITLE in body_text and "Forge Approval Process Requirement" in body_text,
        "doc_id": meta.get("id"),
        "title": meta.get("name"),
        "webViewLink": meta.get("webViewLink"),
        "folder": folder.get("name"),
        "modifiedTime": meta.get("modifiedTime"),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
