#!/usr/bin/env python3
"""Read-only Gmail export CLI.

Exports messages matching an explicit Gmail search query as `.eml` plus JSON
metadata. OAuth token is separate from the Google Docs exporter.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import email
import email.policy
import hashlib
import http.server
import json
import os
import pathlib
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
DEFAULT_CLIENT_SECRET = pathlib.Path(
    os.environ.get(
        "GMAIL_EXPORT_CLIENT_SECRET",
        "~/.config/koval-google-doc-export/client_secret.json",
    )
).expanduser()
DEFAULT_TOKEN = pathlib.Path(
    os.environ.get(
        "GMAIL_EXPORT_TOKEN",
        "~/.config/koval-gmail-export/token.json",
    )
).expanduser()


class CliError(RuntimeError):
    pass


@dataclass(frozen=True)
class GmailMessageRef:
    message_id: str
    thread_id: str | None = None

    @property
    def safe_id(self) -> str:
        return hashlib.sha256(self.message_id.encode("utf-8")).hexdigest()[:16]


def load_json(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CliError(f"Missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CliError(f"Invalid JSON in {path}: {exc}") from exc


def client_info(path: pathlib.Path) -> tuple[str, str, str, str]:
    data = load_json(path)
    config = data.get("installed") or data.get("web")
    if not config:
        raise CliError("OAuth client JSON must contain an 'installed' or 'web' config")
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    auth_uri = config.get("auth_uri", "https://accounts.google.com/o/oauth2/v2/auth")
    token_uri = config.get("token_uri", "https://oauth2.googleapis.com/token")
    if not client_id or not client_secret:
        raise CliError("OAuth client JSON is missing client_id or client_secret")
    return client_id, client_secret, auth_uri, token_uri


def reserve_local_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    code: str | None = None
    error: str | None = None

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        type(self).code = params.get("code", [None])[0]
        type(self).error = params.get("error", [None])[0]
        body = b"Gmail read-only authorization received. You can close this browser tab.\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def http_json(req: urllib.request.Request, timeout: int = 120) -> dict:
    transient_errors = (
        ConnectionResetError,
        TimeoutError,
        socket.timeout,
        ssl.SSLError,
        urllib.error.URLError,
    )
    last_error: BaseException | None = None
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            if exc.code in {429, 500, 502, 503, 504} and attempt < 5:
                last_error = exc
                time.sleep(min(30, 2**attempt))
                continue
            raise CliError(f"HTTP {exc.code}: {details}") from exc
        except transient_errors as exc:
            last_error = exc
            if attempt >= 5:
                break
            time.sleep(min(30, 2**attempt))
    raise CliError(str(last_error))


def http_post_json(url: str, data: dict) -> dict:
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    return http_json(req, timeout=60)


def authorize(args: argparse.Namespace) -> None:
    client_secret = pathlib.Path(args.client_secret).expanduser()
    token_path = pathlib.Path(args.token).expanduser()
    client_id, client_secret_value, auth_uri, token_uri = client_info(client_secret)
    port = int(args.port or reserve_local_port())
    redirect_uri = f"http://localhost:{port}/"

    OAuthCallbackHandler.code = None
    OAuthCallbackHandler.error = None
    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    auth_url = f"{auth_uri}?{query}"
    print("Open this URL in a browser to authorize Gmail read-only export:")
    print(auth_url)
    if not args.no_browser:
        webbrowser.open(auth_url)

    with http.server.HTTPServer(("127.0.0.1", port), OAuthCallbackHandler) as server:
        server.timeout = int(args.timeout)
        print(f"Waiting for OAuth callback on {redirect_uri}")
        server.handle_request()

    if OAuthCallbackHandler.error:
        raise CliError(f"OAuth returned error: {OAuthCallbackHandler.error}")
    if not OAuthCallbackHandler.code:
        raise CliError("No OAuth code received before timeout")

    token = http_post_json(
        token_uri,
        {
            "code": OAuthCallbackHandler.code,
            "client_id": client_id,
            "client_secret": client_secret_value,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    token["created_at"] = int(time.time())
    token["token_uri"] = token_uri
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(json.dumps(token, indent=2, sort_keys=True), encoding="utf-8")
    os.chmod(token_path.parent, 0o700)
    os.chmod(token_path, 0o600)
    print(f"Stored Gmail OAuth token metadata at {token_path}")


def access_token(token_path: pathlib.Path, client_secret_path: pathlib.Path) -> str:
    token = load_json(token_path)
    current = token.get("access_token")
    expires_in = int(token.get("expires_in", 0) or 0)
    created_at = int(token.get("created_at", 0) or 0)
    if current and created_at + expires_in - 120 > int(time.time()):
        return str(current)

    refresh = token.get("refresh_token")
    if not refresh:
        raise CliError("Gmail token expired and has no refresh_token; run authorize again")
    client_id, client_secret_value, _auth_uri, token_uri = client_info(client_secret_path)
    refreshed = http_post_json(
        token_uri,
        {
            "client_id": client_id,
            "client_secret": client_secret_value,
            "refresh_token": refresh,
            "grant_type": "refresh_token",
        },
    )
    token.update(refreshed)
    token["refresh_token"] = refresh
    token["created_at"] = int(time.time())
    token_path.write_text(json.dumps(token, indent=2, sort_keys=True), encoding="utf-8")
    os.chmod(token_path, 0o600)
    return str(token["access_token"])


def gmail_get(path: str, access: str, params: dict | None = None) -> dict:
    query = urllib.parse.urlencode(params or {})
    url = f"https://gmail.googleapis.com/gmail/v1/{path}"
    if query:
        url += f"?{query}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access}"})
    return http_json(req)


def list_messages(access: str, query: str, max_results: int) -> list[GmailMessageRef]:
    refs: list[GmailMessageRef] = []
    page_token = None
    while True:
        params = {"q": query, "maxResults": min(500, max_results - len(refs) if max_results else 500)}
        if page_token:
            params["pageToken"] = page_token
        data = gmail_get("users/me/messages", access, params)
        for item in data.get("messages", []) or []:
            refs.append(GmailMessageRef(str(item["id"]), item.get("threadId")))
            if max_results and len(refs) >= max_results:
                return refs
        page_token = data.get("nextPageToken")
        if not page_token:
            return refs


def get_message_raw(access: str, message_id: str) -> tuple[bytes, dict]:
    data = gmail_get(f"users/me/messages/{urllib.parse.quote(message_id)}", access, {"format": "raw"})
    raw = str(data.get("raw", ""))
    if not raw:
        raise CliError("Gmail message response did not include raw content")
    padded = raw + ("=" * (-len(raw) % 4))
    content = base64.urlsafe_b64decode(padded.encode("ascii"))
    return content, data


def header_value(msg: email.message.EmailMessage, name: str) -> str:
    value = msg.get(name, "")
    return str(value).replace("\n", " ").replace("\r", " ").strip()


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[/:\\\0]+", " - ", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:120] or "message"


def search(args: argparse.Namespace) -> None:
    access = access_token(pathlib.Path(args.token).expanduser(), pathlib.Path(args.client_secret).expanduser())
    refs = list_messages(access, args.query, int(args.limit or 10))
    print(f"Matched {len(refs)} message(s) for query; showing hashed IDs only.")
    for ref in refs:
        print(ref.safe_id)


def export(args: argparse.Namespace) -> None:
    token_path = pathlib.Path(args.token).expanduser()
    client_secret_path = pathlib.Path(args.client_secret).expanduser()
    access = access_token(token_path, client_secret_path)
    refs = list_messages(access, args.query, int(args.limit or 0))
    output = pathlib.Path(args.output).expanduser().resolve()
    if args.dry_run:
        print(f"Would export {len(refs)} message(s) to {output}")
        for ref in refs[:20]:
            print(ref.safe_id)
        return

    output.mkdir(parents=True, exist_ok=True)
    existing_hashes = set()
    for message_path in output.glob("*.eml"):
        match = re.match(r"^\d{5}-([0-9a-f]{16})-", message_path.name)
        if match:
            existing_hashes.add(match.group(1))

    if not existing_hashes:
        for metadata_path in output.glob("*.json"):
            try:
                metadata = load_json(metadata_path)
            except CliError:
                continue
            message_hash = metadata.get("message_hash")
            if message_hash:
                existing_hashes.add(str(message_hash))

    token_lock = threading.Lock()
    output_lock = threading.Lock()

    def current_access_token() -> str:
        with token_lock:
            return access_token(token_path, client_secret_path)

    def export_one(index_and_ref: tuple[int, GmailMessageRef]) -> tuple[str, int, str]:
        idx, ref = index_and_ref
        if ref.safe_id in existing_hashes:
            return "skipped", idx, ref.safe_id
        raw, api_meta = get_message_raw(current_access_token(), ref.message_id)
        parsed = email.message_from_bytes(raw, policy=email.policy.default)
        date = safe_filename(header_value(parsed, "Date") or "no-date")
        subject = safe_filename(header_value(parsed, "Subject") or "no-subject")
        filename = f"{idx:05d}-{ref.safe_id}-{subject}.eml"
        path = output / filename
        path.write_bytes(raw)
        meta = {
            "message_hash": ref.safe_id,
            "thread_hash": hashlib.sha256((ref.thread_id or "").encode("utf-8")).hexdigest()[:16] if ref.thread_id else None,
            "date": date,
            "from": header_value(parsed, "From"),
            "to": header_value(parsed, "To"),
            "cc": header_value(parsed, "Cc"),
            "subject": header_value(parsed, "Subject"),
            "label_ids": api_meta.get("labelIds", []),
            "internal_date": api_meta.get("internalDate"),
            "exported_at": int(time.time()),
            "query": args.query,
        }
        with output_lock:
            if ref.safe_id in existing_hashes:
                return "skipped", idx, ref.safe_id
            path.write_bytes(raw)
            path.with_suffix(".json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
            existing_hashes.add(ref.safe_id)
        return "exported", idx, f"{ref.safe_id} -> {path}"

    exported = 0
    skipped = 0
    workers = max(1, int(args.workers or 1))
    if workers == 1:
        for item in enumerate(refs, start=1):
            status, idx, detail = export_one(item)
            if status == "skipped":
                skipped += 1
                print(f"SKIPPED {idx:05d} {detail} already exported")
            else:
                exported += 1
                print(f"EXPORTED {idx:05d} {detail}")
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(export_one, item) for item in enumerate(refs, start=1)]
            for future in as_completed(futures):
                status, idx, detail = future.result()
                if status == "skipped":
                    skipped += 1
                    print(f"SKIPPED {idx:05d} {detail} already exported")
                else:
                    exported += 1
                    print(f"EXPORTED {idx:05d} {detail}")
    print(f"Exported {exported} message(s) to {output}; skipped {skipped} existing message(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Gmail search and export CLI.")
    parser.add_argument("--client-secret", default=str(DEFAULT_CLIENT_SECRET))
    parser.add_argument("--token", default=str(DEFAULT_TOKEN))
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("authorize", help="Authorize Gmail read-only access")
    auth.add_argument("--port", type=int, default=0)
    auth.add_argument("--timeout", type=int, default=300)
    auth.add_argument("--no-browser", action="store_true")
    auth.set_defaults(func=authorize)

    search_cmd = sub.add_parser("search", help="Search Gmail and print hashed message IDs")
    search_cmd.add_argument("--query", required=True, help="Gmail search query")
    search_cmd.add_argument("--limit", type=int, default=10)
    search_cmd.set_defaults(func=search)

    export_cmd = sub.add_parser("export", help="Export Gmail messages as .eml files")
    export_cmd.add_argument("--query", required=True, help="Gmail search query")
    export_cmd.add_argument("--output", required=True, help="Output directory")
    export_cmd.add_argument("--limit", type=int, default=0, help="0 means no explicit limit")
    export_cmd.add_argument("--dry-run", action="store_true")
    export_cmd.add_argument("--workers", type=int, default=1, help="Concurrent message downloads")
    export_cmd.set_defaults(func=export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
