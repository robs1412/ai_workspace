#!/usr/local/bin/python3.13
"""Create or update a Google Doc in the AI Cloud shared drive.

Uses the approved local OAuth client/token pair. This script does not print
credential values or token paths.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


DRIVE_ID = "0AP-Yf32mH4IHUk9PVA"
CLIENT_FILE = Path(".private/google-oauth/frank-drive-desktop-client.json")
TOKEN_FILE = Path(".private/google-oauth/frank-google-drive-token.json")
TOKEN_URI = "https://oauth2.googleapis.com/token"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def get_access_token() -> str:
    client_payload = load_json(CLIENT_FILE)
    client = client_payload.get("installed") or client_payload.get("web") or client_payload
    token_payload = load_json(TOKEN_FILE)
    access_token = str(token_payload.get("access_token") or "")
    if access_token:
        try:
            api_json("GET", "https://www.googleapis.com/drive/v3/about?fields=user", access_token)
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


def quote_query(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_folder(token: str, folder_name: str) -> dict:
    query = (
        "mimeType = 'application/vnd.google-apps.folder' and "
        f"name = '{quote_query(folder_name)}' and trashed = false"
    )
    params = urllib.parse.urlencode(
        {
            "q": query,
            "corpora": "drive",
            "driveId": DRIVE_ID,
            "includeItemsFromAllDrives": "true",
            "supportsAllDrives": "true",
            "fields": "files(id,name,webViewLink)",
            "pageSize": "10",
        }
    )
    result = api_json("GET", f"https://www.googleapis.com/drive/v3/files?{params}", token)
    files = result.get("files", [])
    if not files:
        raise RuntimeError(f"AI Cloud folder not found: {folder_name}")
    return files[0]


def find_doc(token: str, folder_id: str, title: str) -> dict | None:
    query = (
        f"name = '{quote_query(title)}' and "
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


def create_doc(token: str, folder_id: str, title: str) -> dict:
    params = urllib.parse.urlencode({"supportsAllDrives": "true", "fields": "id,name,webViewLink,parents"})
    payload = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    return api_json("POST", f"https://www.googleapis.com/drive/v3/files?{params}", token, payload)


def markdown_to_readable_text(text: str) -> str:
    text = re.sub(r"^# (.+)$", r"\1\n" + "=" * 72, text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"\n\1\n" + "-" * 48, text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)$", r"\n\1", text, flags=re.MULTILINE)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip() + "\n"


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
    api_json("POST", f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate", token, {"requests": requests})
    return api_json(
        "GET",
        f"https://docs.googleapis.com/v1/documents/{doc_id}?fields=title,body/content/paragraph/elements/textRun/content",
        token,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a local text/Markdown file as an AI Cloud Google Doc.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--folder", default="AI Workers")
    parser.add_argument("--must-contain", action="append", default=[])
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        raise RuntimeError(f"Source file not found: {source}")

    text = markdown_to_readable_text(source.read_text(encoding="utf-8"))
    token = get_access_token()
    folder = find_folder(token, args.folder)
    doc = find_doc(token, folder["id"], args.title) or create_doc(token, folder["id"], args.title)
    readback = replace_doc_text(token, doc["id"], text)
    meta = api_json(
        "GET",
        f"https://www.googleapis.com/drive/v3/files/{doc['id']}?supportsAllDrives=true&fields=id,name,webViewLink,modifiedTime,parents",
        token,
    )
    readback_text = json.dumps(readback)
    missing = [needle for needle in args.must_contain if needle not in readback_text]
    result = {
        "ok": not missing,
        "doc_id": meta.get("id"),
        "title": meta.get("name"),
        "webViewLink": meta.get("webViewLink"),
        "folder": folder.get("name"),
        "modifiedTime": meta.get("modifiedTime"),
        "missing": missing,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
