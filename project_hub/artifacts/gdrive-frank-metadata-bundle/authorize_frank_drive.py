#!/usr/bin/env python3
"""
One-time OAuth consent helper for Frank's metadata-only Google Drive slice.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import secrets
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DEFAULT_CLIENT_FILE = Path(
    "/Users/werkstatt/ai_workspace/.private/google-oauth/frank-drive-desktop-client.json"
)
DEFAULT_TOKEN_FILE = Path(
    "/Users/werkstatt/ai_workspace/.private/google-oauth/frank-google-drive-token.json"
)
DEFAULT_SCOPE = "https://www.googleapis.com/auth/drive.metadata.readonly"
DEFAULT_LOGIN_HINT = "frank.cannoli@kovaldistillery.com"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Authorize Frank's metadata-only Google Drive access."
    )
    parser.add_argument(
        "--client-file",
        default=str(DEFAULT_CLIENT_FILE),
        help="OAuth client JSON for the KOVAL Agents Drive desktop client.",
    )
    parser.add_argument(
        "--token-file",
        default=str(DEFAULT_TOKEN_FILE),
        help="Local JSON file for the temporary Frank Drive token payload.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    auth = subparsers.add_parser("authorize", help="Run the one-time OAuth consent flow.")
    auth.add_argument(
        "--scope",
        action="append",
        default=[],
        help="OAuth scope to request. Defaults to drive.metadata.readonly.",
    )
    auth.add_argument(
        "--login-hint",
        default=DEFAULT_LOGIN_HINT,
        help="Google account hint for the consent screen.",
    )
    auth.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Seconds to wait for the OAuth callback.",
    )
    auth.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the URL only; do not try to open the local browser.",
    )

    show = subparsers.add_parser("show-config", help="Print the resolved local config.")
    show.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_client_config(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    config = payload.get("installed") or payload.get("web") or payload
    if not config.get("client_id"):
        raise ValueError(f"OAuth client file missing client_id: {path}")
    return config


def default_scopes(explicit_scopes: list[str]) -> list[str]:
    return explicit_scopes or [DEFAULT_SCOPE]


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_token(path: Path, token_payload: dict) -> None:
    ensure_parent_dir(path)
    normalized = dict(token_payload)
    normalized["created_at"] = int(time.time())
    expires_in = normalized.get("expires_in")
    if expires_in:
        normalized["expires_at"] = int(time.time()) + int(expires_in) - 60
    path.write_text(json.dumps(normalized, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def urlsafe_b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def build_auth_url(
    client_config: dict,
    redirect_uri: str,
    scopes: list[str],
    login_hint: str,
    state: str,
    code_challenge: str,
) -> str:
    params = {
        "client_id": client_config["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "login_hint": login_hint,
    }
    return GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    server_version = "FrankGoogleDrive/1.0"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        self.server.oauth_query = query  # type: ignore[attr-defined]
        body = (
            "<html><body><h1>Frank Google Drive</h1>"
            "<p>Authorization received. You can close this window and return to the terminal.</p>"
            "</body></html>"
        )
        body_bytes = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def log_message(self, format: str, *args) -> None:
        return


def run_local_callback_server() -> tuple[HTTPServer, threading.Thread]:
    server = HTTPServer(("127.0.0.1", 0), OAuthCallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server, thread


def exchange_code_for_tokens(client_config: dict, code: str, redirect_uri: str, code_verifier: str) -> dict:
    payload = {
        "client_id": client_config["client_id"],
        "code": code,
        "code_verifier": code_verifier,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    client_secret = client_config.get("client_secret")
    if client_secret:
        payload["client_secret"] = client_secret
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def open_browser(url: str) -> None:
    try:
        subprocess.run(["open", url], check=False, capture_output=True)
    except Exception:
        pass


def command_show_config(args: argparse.Namespace) -> int:
    payload = {
        "client_file": str(Path(args.client_file).expanduser()),
        "token_file": str(Path(args.token_file).expanduser()),
        "scope": DEFAULT_SCOPE,
        "login_hint": DEFAULT_LOGIN_HINT,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}={value}")
    return 0


def command_authorize(args: argparse.Namespace) -> int:
    client_path = Path(args.client_file).expanduser()
    token_path = Path(args.token_file).expanduser()
    client_config = load_client_config(client_path)
    scopes = default_scopes(args.scope)

    server, thread = run_local_callback_server()
    redirect_uri = f"http://127.0.0.1:{server.server_port}/oauth2callback"
    state = secrets.token_urlsafe(24)
    code_verifier = urlsafe_b64(secrets.token_bytes(64))
    code_challenge = urlsafe_b64(hashlib.sha256(code_verifier.encode("ascii")).digest())
    auth_url = build_auth_url(client_config, redirect_uri, scopes, args.login_hint, state, code_challenge)

    print(f"Client file: {client_path}")
    print(f"Token file: {token_path}")
    print(f"Redirect URI: {redirect_uri}")
    print(f"Scopes: {' '.join(scopes)}")
    print("")
    print(auth_url)
    print("")
    if not args.no_browser:
        open_browser(auth_url)

    thread.join(args.timeout)
    query = getattr(server, "oauth_query", None)
    server.server_close()
    if not query:
        print("Authorization callback was not received before timeout.", file=sys.stderr)
        return 1
    if query.get("state", [""])[0] != state:
        print("OAuth state mismatch.", file=sys.stderr)
        return 1
    if "error" in query:
        print(f"Google returned an OAuth error: {query['error'][0]}", file=sys.stderr)
        return 1
    code = query.get("code", [""])[0]
    if not code:
        print("Authorization code missing from callback.", file=sys.stderr)
        return 1

    token_payload = exchange_code_for_tokens(client_config, code, redirect_uri, code_verifier)
    save_token(token_path, token_payload)
    print("authorized")
    print(token_path)
    return 0


def main() -> int:
    args = parse_args()
    dispatch = {
        "authorize": command_authorize,
        "show-config": command_show_config,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
