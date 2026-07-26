#!/usr/local/bin/python3.13
"""Replace an existing shared Google Doc by importing local HTML.

This is intentionally narrow for the Family AI Class packet. It finds an
available National Outreach OAuth session without printing credential paths or
token values, uploads HTML to the existing Google Docs file ID, and verifies by
exporting the resulting document.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def form_post(url: str, data: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def api(method: str, url: str, token: str, body: bytes | dict | None = None, content_type: str = "application/json", timeout: int = 120) -> bytes:
    payload = None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        payload = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def client_config(data: dict) -> dict | None:
    config = data.get("installed") or data.get("web") or data
    if isinstance(config, dict) and config.get("client_id") and "client_secret" in config:
        return config
    return None


def nationaloutreach_token() -> tuple[str, str]:
    client_path = os.environ.get("GOOGLE_OAUTH_CLIENT_FILE", "")
    token_path = os.environ.get("GOOGLE_OAUTH_TOKEN_FILE", "")
    if not client_path or not token_path:
        raise RuntimeError(
            "GOOGLE_OAUTH_CLIENT_FILE and GOOGLE_OAUTH_TOKEN_FILE must be configured."
        )

    client_payload = load_json(Path(client_path).expanduser())
    token_payload = load_json(Path(token_path).expanduser())
    config = client_config(client_payload or {})
    if config is None or token_payload is None:
        raise RuntimeError("Configured Google OAuth files are not usable.")

    candidates: list[str] = []
    if token_payload.get("access_token"):
        candidates.append(str(token_payload["access_token"]))
    refresh_token = token_payload.get("refresh_token")
    if refresh_token:
        refreshed = form_post(
            config.get("token_uri", "https://oauth2.googleapis.com/token"),
            {
                "client_id": config["client_id"],
                "client_secret": config.get("client_secret", ""),
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if refreshed.get("access_token"):
            candidates.append(str(refreshed["access_token"]))

    seen: set[str] = set()
    for token in candidates:
        if not token or token in seen:
            continue
        seen.add(token)
        try:
            raw = api("GET", "https://www.googleapis.com/drive/v3/about?fields=user(emailAddress)", token)
            email = (json.loads(raw.decode("utf-8")).get("user") or {}).get("emailAddress") or ""
        except Exception:
            continue
        if email.lower().startswith("nationaloutreach@"):
            return token, email

    raise RuntimeError("No usable nationaloutreach OAuth session was found.")


def upload_html(token: str, doc_id: str, title: str, html_path: Path) -> dict:
    boundary = f"==============={uuid.uuid4().hex}=="
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
    }
    html_bytes = html_path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n\r\n"
    ).encode("utf-8") + html_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
    url = (
        f"https://www.googleapis.com/upload/drive/v3/files/{urllib.parse.quote(doc_id)}"
        "?uploadType=multipart&supportsAllDrives=true&fields=id,name,mimeType,webViewLink,modifiedTime"
    )
    raw = api("PATCH", url, token, body, f"multipart/related; boundary={boundary}", timeout=180)
    return json.loads(raw.decode("utf-8"))


def api_json(method: str, url: str, token: str, body: dict | None = None, timeout: int = 120) -> dict:
    raw = api(method, url, token, body, "application/json", timeout)
    return json.loads(raw.decode("utf-8")) if raw else {}


def insert_native_toc(token: str, doc_id: str) -> None:
    doc = api_json(
        "GET",
        f"https://docs.googleapis.com/v1/documents/{urllib.parse.quote(doc_id)}?fields=body/content/endIndex",
        token,
    )
    content = doc.get("body", {}).get("content", [])
    insert_index = 1
    if content:
        insert_index = int(content[0].get("endIndex", 1))
    requests = [
        {"insertText": {"location": {"index": insert_index}, "text": "\n"}},
        {"insertTableOfContents": {"location": {"index": insert_index + 1}}},
        {"insertText": {"location": {"index": insert_index + 2}, "text": "\n"}},
    ]
    api_json(
        "POST",
        f"https://docs.googleapis.com/v1/documents/{urllib.parse.quote(doc_id)}:batchUpdate",
        token,
        {"requests": requests},
        timeout=120,
    )


def export_text(token: str, doc_id: str) -> str:
    url = (
        f"https://www.googleapis.com/drive/v3/files/{urllib.parse.quote(doc_id)}/export?"
        + urllib.parse.urlencode({"mimeType": "text/plain"})
    )
    return api("GET", url, token, timeout=180).decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload HTML into an existing shared Google Doc.")
    parser.add_argument("--doc-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--must-contain", action="append", default=[])
    parser.add_argument("--insert-native-toc", action="store_true")
    args = parser.parse_args()

    token, email = nationaloutreach_token()
    result = upload_html(token, args.doc_id, args.title, Path(args.html))
    if args.insert_native_toc:
        insert_native_toc(token, args.doc_id)
    exported = export_text(token, args.doc_id)
    missing = [needle for needle in args.must_contain if needle not in exported]
    print(
        json.dumps(
            {
                "ok": not missing,
                "account": email,
                "title": result.get("name"),
                "mimeType": result.get("mimeType"),
                "webViewLink": result.get("webViewLink"),
                "modifiedTime": result.get("modifiedTime"),
                "exported_chars": len(exported),
                "missing": missing,
            },
            sort_keys=True,
        )
    )
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
