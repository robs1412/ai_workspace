#!/usr/local/bin/python3.13
"""Move Ezra's liquor guide to Legal and replace body from HTML source."""

from __future__ import annotations

import html
import json
import re
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DOC_ID = "1QEDGQARePX8kL6R88K6UN9fdl4K7KQf-b0urjUjumxE"
LEGAL_FOLDER_ID = "1P-qGbjguRtlDOm7bNvXJN7yfXy--8DA7"
SOURCE_FILE = Path("project_hub/artifacts/legal-affairs/ezra-liquor-legal-marketing-guide-2026-06-10.md")
HTML_FILE = Path("project_hub/artifacts/legal-affairs/ezra-liquor-legal-marketing-guide-2026-06-10.html")
CLIENT_FILE = Path(".private/google-oauth/frank-drive-desktop-client.json")
TOKEN_FILE = Path(".private/google-oauth/frank-google-drive-token.json")
TOKEN_URI = "https://oauth2.googleapis.com/token"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def access_token() -> str:
    client_payload = load_json(CLIENT_FILE)
    client = client_payload.get("installed") or client_payload.get("web") or client_payload
    token_payload = load_json(TOKEN_FILE)
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
        return json.loads(response.read().decode("utf-8"))["access_token"]


def api_json(method: str, url: str, token: str, payload: dict | None = None, content_type: str = "application/json") -> dict:
    body = None
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google API {method} failed with HTTP {exc.code}: {detail[:500]}") from exc
    return json.loads(raw) if raw else {}


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"(?<!href=\")(https?://[^\s<]+)", r'<a href="\1">\1</a>', escaped)
    return escaped


def markdown_table(lines: list[str]) -> str:
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    out = ["<table>", "<thead><tr>"]
    out.extend(f"<th>{inline_markdown(cell)}</th>" for cell in headers)
    out.extend(["</tr></thead>", "<tbody>"])
    for row in rows:
        out.append("<tr>")
        out.extend(f"<td>{inline_markdown(cell)}</td>" for cell in row)
        out.append("</tr>")
    out.extend(["</tbody>", "</table>"])
    return "\n".join(out)


def render_html(md: str) -> str:
    lines = md.splitlines()
    body: list[str] = []
    i = 0
    in_ul = False
    in_ol = False
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            if in_ul:
                body.append("</ul>")
                in_ul = False
            if in_ol:
                body.append("</ol>")
                in_ol = False
            i += 1
            continue
        if line.startswith("| ") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").replace(" ", "")) <= {"-", ":"}:
            if in_ul:
                body.append("</ul>")
                in_ul = False
            if in_ol:
                body.append("</ol>")
                in_ol = False
            table_lines = [line, lines[i + 1].rstrip()]
            i += 2
            while i < len(lines) and lines[i].startswith("| "):
                table_lines.append(lines[i].rstrip())
                i += 1
            body.append(markdown_table(table_lines))
            continue
        if line.startswith("# "):
            body.append(f"<h1>{inline_markdown(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{inline_markdown(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            body.append(f"<h3>{inline_markdown(line[4:].strip())}</h3>")
        elif re.match(r"^\\d+\\.\\s+", line):
            if in_ul:
                body.append("</ul>")
                in_ul = False
            if not in_ol:
                body.append("<ol>")
                in_ol = True
            body.append(f"<li>{inline_markdown(re.sub(r'^\\d+\\.\\s+', '', line))}</li>")
        elif line.startswith("- "):
            if in_ol:
                body.append("</ol>")
                in_ol = False
            if not in_ul:
                body.append("<ul>")
                in_ul = True
            body.append(f"<li>{inline_markdown(line[2:].strip())}</li>")
        else:
            if in_ul:
                body.append("</ul>")
                in_ul = False
            if in_ol:
                body.append("</ol>")
                in_ol = False
            body.append(f"<p>{inline_markdown(line)}</p>")
        i += 1
    if in_ul:
        body.append("</ul>")
    if in_ol:
        body.append("</ol>")
    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Ezra Katz - Liquor Legal, Distribution, and Marketing Review Guide</title>
  <style>
    body { font-family: Arial, sans-serif; color: #202124; line-height: 1.45; }
    h1 { font-size: 24px; margin: 0 0 12px; }
    h2 { font-size: 17px; margin: 22px 0 8px; color: #174ea6; }
    h3 { font-size: 14px; margin: 16px 0 6px; }
    p { margin: 6px 0; }
    ul, ol { margin-top: 4px; margin-bottom: 10px; }
    li { margin: 3px 0; }
    table { border-collapse: collapse; width: 100%; margin: 10px 0 16px; }
    th, td { border: 1px solid #dadce0; padding: 6px 8px; vertical-align: top; }
    th { background: #f1f3f4; font-weight: 700; }
    code { font-family: Consolas, monospace; background: #f1f3f4; padding: 1px 3px; }
  </style>
</head>
<body>
""" + "\n".join(body) + "\n</body>\n</html>\n"


def multipart_update(token: str, html_text: str) -> dict:
    boundary = "codex-" + uuid.uuid4().hex
    metadata = {"name": "Ezra Katz - Liquor Legal, Distribution, and Marketing Review Guide"}
    parts = [
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(metadata)}\r\n",
        f"--{boundary}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n{html_text}\r\n",
        f"--{boundary}--\r\n",
    ]
    body = "".join(parts).encode("utf-8")
    params = urllib.parse.urlencode({"uploadType": "multipart", "supportsAllDrives": "true", "fields": "id,name,webViewLink,parents,modifiedTime"})
    url = f"https://www.googleapis.com/upload/drive/v3/files/{DOC_ID}?{params}"
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={boundary}",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google upload update failed with HTTP {exc.code}: {detail[:500]}") from exc


def move_to_legal(token: str) -> dict:
    meta = api_json(
        "GET",
        f"https://www.googleapis.com/drive/v3/files/{DOC_ID}?supportsAllDrives=true&fields=id,name,parents,webViewLink,modifiedTime",
        token,
    )
    parents = [p for p in meta.get("parents", []) if p != LEGAL_FOLDER_ID]
    params = urllib.parse.urlencode(
        {
            "addParents": LEGAL_FOLDER_ID,
            "removeParents": ",".join(parents),
            "supportsAllDrives": "true",
            "fields": "id,name,parents,webViewLink,modifiedTime",
        }
    )
    return api_json("PATCH", f"https://www.googleapis.com/drive/v3/files/{DOC_ID}?{params}", token, {})


def main() -> int:
    md = SOURCE_FILE.read_text(encoding="utf-8")
    html_text = render_html(md)
    HTML_FILE.write_text(html_text, encoding="utf-8")
    token = access_token()
    updated = multipart_update(token, html_text)
    moved = move_to_legal(token)
    exported = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{DOC_ID}/export?mimeType=text/html",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(exported, timeout=60) as response:
        export_html = response.read().decode("utf-8", errors="replace")
    result = {
        "ok": LEGAL_FOLDER_ID in moved.get("parents", []) and "<h1" in export_html.lower(),
        "doc_id": DOC_ID,
        "webViewLink": moved.get("webViewLink") or updated.get("webViewLink"),
        "parents": moved.get("parents", []),
        "modifiedTime": moved.get("modifiedTime"),
        "html_working_copy": str(HTML_FILE),
        "export_has_tables": "<table" in export_html.lower(),
        "export_has_links": "https://www.ttb.gov" in export_html,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
