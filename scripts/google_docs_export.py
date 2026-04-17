#!/usr/bin/env python3
"""Export local Google Drive pointer files to readable local files.

This tool reads `.gdoc`, `.gsheet`, and `.gslides` files created by Google
Drive for Desktop, extracts their Google Drive file IDs, and uses the Drive API
export endpoint to write normal local files.

Secrets are never printed. OAuth client JSON and token JSON stay on disk.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import http.server
import json
import os
import pathlib
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from typing import Iterable


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DEFAULT_CLIENT_SECRET = pathlib.Path(
    os.environ.get(
        "GOOGLE_DOC_EXPORT_CLIENT_SECRET",
        "~/.config/koval-google-doc-export/client_secret.json",
    )
).expanduser()
DEFAULT_TOKEN = pathlib.Path(
    os.environ.get(
        "GOOGLE_DOC_EXPORT_TOKEN",
        "~/.config/koval-google-doc-export/token.json",
    )
).expanduser()

EXPORT_FORMATS = {
    ".gdoc": {
        "txt": ("text/plain", ".txt"),
        "docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".docx",
        ),
        "pdf": ("application/pdf", ".pdf"),
        "html": ("application/zip", ".html.zip"),
    },
    ".gsheet": {
        "csv": ("text/csv", ".csv"),
        "xlsx": (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xlsx",
        ),
        "pdf": ("application/pdf", ".pdf"),
    },
    ".gslides": {
        "txt": ("text/plain", ".txt"),
        "pptx": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".pptx",
        ),
        "pdf": ("application/pdf", ".pdf"),
    },
}

DEFAULT_FORMAT = {
    ".gdoc": "txt",
    ".gsheet": "csv",
    ".gslides": "txt",
}


class CliError(RuntimeError):
    pass


@dataclass(frozen=True)
class PointerFile:
    path: pathlib.Path
    root: pathlib.Path
    suffix: str
    file_id: str
    name: str

    @property
    def rel_parent(self) -> pathlib.Path:
        return self.path.parent.relative_to(self.root)


def load_json(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CliError(f"Missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CliError(f"Invalid JSON in {path}: {exc}") from exc


def parse_pointer(path: pathlib.Path, root: pathlib.Path) -> PointerFile | None:
    suffix = path.suffix.lower()
    if suffix not in EXPORT_FORMATS:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    file_id = data.get("doc_id") or data.get("resource_id")
    if not file_id:
        return None
    return PointerFile(
        path=path,
        root=root,
        suffix=suffix,
        file_id=str(file_id),
        name=path.stem,
    )


def iter_pointers(root: pathlib.Path) -> Iterable[PointerFile]:
    root = root.resolve()
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in EXPORT_FORMATS:
            pointer = parse_pointer(path, root)
            if pointer:
                yield pointer


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[/:\\\0]+", " - ", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "untitled"


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
        body = b"Authorization received. You can close this browser tab.\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def http_post_json(url: str, data: dict) -> dict:
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise CliError(f"OAuth token request failed: HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise CliError(f"OAuth token request failed: {exc}") from exc


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
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    auth_url = f"{auth_uri}?{query}"
    print("Open this URL in a browser to authorize Google Drive read-only export:")
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
    os.chmod(token_path, 0o600)
    print(f"Stored OAuth token metadata at {token_path}")


def load_token(token_path: pathlib.Path, client_secret_path: pathlib.Path) -> str:
    token = load_json(token_path)
    access_token = token.get("access_token")
    expires_in = int(token.get("expires_in", 0) or 0)
    created_at = int(token.get("created_at", 0) or 0)
    if access_token and created_at + expires_in - 120 > int(time.time()):
        return str(access_token)

    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise CliError("Token expired and has no refresh_token; run authorize again")

    client_id, client_secret_value, _auth_uri, token_uri = client_info(client_secret_path)
    refreshed = http_post_json(
        token_uri,
        {
            "client_id": client_id,
            "client_secret": client_secret_value,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    token.update(refreshed)
    token["refresh_token"] = refresh_token
    token["created_at"] = int(time.time())
    token_path.write_text(json.dumps(token, indent=2, sort_keys=True), encoding="utf-8")
    os.chmod(token_path, 0o600)
    return str(token["access_token"])


def drive_export(file_id: str, mime_type: str, access_token: str) -> bytes:
    file_label = hashlib.sha256(file_id.encode("utf-8")).hexdigest()[:12]
    query = urllib.parse.urlencode({"mimeType": mime_type})
    encoded_id = urllib.parse.quote(file_id)
    url = f"https://www.googleapis.com/drive/v3/files/{encoded_id}/export?{query}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise CliError(f"Export failed for file hash {file_label}: HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise CliError(f"Export failed for file hash {file_label}: {exc}") from exc


def choose_format(pointer: PointerFile, args: argparse.Namespace) -> tuple[str, str, str]:
    override = {
        ".gdoc": args.gdoc_format,
        ".gsheet": args.gsheet_format,
        ".gslides": args.gslides_format,
    }[pointer.suffix]
    fmt = override or DEFAULT_FORMAT[pointer.suffix]
    options = EXPORT_FORMATS[pointer.suffix]
    if fmt not in options:
        valid = ", ".join(sorted(options))
        raise CliError(f"Invalid format {fmt!r} for {pointer.suffix}; valid: {valid}")
    mime_type, extension = options[fmt]
    return fmt, mime_type, extension


def output_path(pointer: PointerFile, output_root: pathlib.Path, extension: str) -> pathlib.Path:
    rel_parent = pointer.rel_parent
    filename = safe_filename(pointer.name) + extension
    return output_root / rel_parent / filename


def export_tree(args: argparse.Namespace) -> None:
    root = pathlib.Path(args.root).expanduser().resolve()
    output_root = pathlib.Path(args.output).expanduser().resolve() if args.output else root / "_google_doc_exports"
    if args.limit:
        pointers = []
        for pointer in iter_pointers(root):
            pointers.append(pointer)
            if len(pointers) >= int(args.limit):
                break
    else:
        pointers = sorted(iter_pointers(root), key=lambda item: str(item.path).lower())

    if args.command == "scan":
        for pointer in pointers:
            fmt, _mime_type, extension = choose_format(pointer, args)
            out = output_path(pointer, output_root, extension)
            print(f"{pointer.suffix[1:]:7} {fmt:5} {pointer.path.relative_to(root)} -> {out.relative_to(output_root)}")
        print(f"Found {len(pointers)} Google pointer file(s)")
        return

    if args.dry_run:
        for pointer in pointers:
            _fmt, _mime_type, extension = choose_format(pointer, args)
            out = output_path(pointer, output_root, extension)
            print(f"DRY-RUN {pointer.path.relative_to(root)} -> {out}")
        print(f"Would export {len(pointers)} file(s)")
        return

    client_secret = pathlib.Path(args.client_secret).expanduser()
    token_path = pathlib.Path(args.token).expanduser()
    access_token = load_token(token_path, client_secret)
    output_root.mkdir(parents=True, exist_ok=True)

    exported = 0
    skipped = 0
    for pointer in pointers:
        fmt, mime_type, extension = choose_format(pointer, args)
        out = output_path(pointer, output_root, extension)
        if out.exists() and not args.force:
            skipped += 1
            print(f"SKIP exists: {out}")
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        content = drive_export(pointer.file_id, mime_type, access_token)
        out.write_bytes(content)
        sidecar = out.with_suffix(out.suffix + ".source.json")
        sidecar.write_text(
            json.dumps(
                {
                    "source_pointer": str(pointer.path),
                    "doc_id_hash": hashlib.sha256(pointer.file_id.encode("utf-8")).hexdigest(),
                    "export_format": fmt,
                    "mime_type": mime_type,
                    "exported_at": int(time.time()),
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        exported += 1
        print(f"EXPORTED {pointer.path.relative_to(root)} -> {out}")

    print(f"Exported {exported}; skipped {skipped}; total pointers {len(pointers)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export Google Drive .gdoc/.gsheet/.gslides pointers to local files."
    )
    parser.add_argument(
        "--client-secret",
        default=str(DEFAULT_CLIENT_SECRET),
        help=f"OAuth desktop client JSON path. Default: {DEFAULT_CLIENT_SECRET}",
    )
    parser.add_argument(
        "--token",
        default=str(DEFAULT_TOKEN),
        help=f"OAuth token JSON path. Default: {DEFAULT_TOKEN}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("authorize", help="Authorize Google Drive read-only access")
    auth.add_argument("--port", type=int, default=0, help="Local callback port")
    auth.add_argument("--timeout", type=int, default=300, help="Callback wait seconds")
    auth.add_argument("--no-browser", action="store_true", help="Print URL only")
    auth.set_defaults(func=authorize)

    for name in ("scan", "export"):
        cmd = sub.add_parser(name, help=f"{name} Google pointer files")
        cmd.add_argument("root", help="Folder to scan")
        cmd.add_argument("--output", help="Export output root. Default: ROOT/_google_doc_exports")
        cmd.add_argument("--gdoc-format", choices=sorted(EXPORT_FORMATS[".gdoc"]), default=None)
        cmd.add_argument("--gsheet-format", choices=sorted(EXPORT_FORMATS[".gsheet"]), default=None)
        cmd.add_argument("--gslides-format", choices=sorted(EXPORT_FORMATS[".gslides"]), default=None)
        cmd.add_argument("--limit", type=int, default=0, help="Process only the first N pointers")
        cmd.add_argument("--dry-run", action="store_true", help="Show planned exports only")
        cmd.add_argument("--force", action="store_true", help="Overwrite existing exports")
        cmd.set_defaults(func=export_tree)

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
