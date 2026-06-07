#!/usr/local/bin/python3.13
"""Refresh the local MCP runtime bearer token from an approved packet.

The refresh packet remains in Frank Gmail. This script reads the exact packet
in memory, extracts the machine-identity login payload, validates the new token
against Papers MCP, and updates the owner-only local fallback without printing
secret values.
"""

from __future__ import annotations

import argparse
import email
import email.policy
import html
import json
import os
import re
import stat
import urllib.request
from pathlib import Path

from gmail_export import access_token, get_message_raw, list_messages


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_ENV = ROOT / ".private" / "mcp-runtime" / "mcp.env"
DEFAULT_REFRESH_ENV = ROOT / ".private" / "mcp-runtime" / "refresh.env"
DEFAULT_PACKET_MESSAGE_ID = "56ab638e5cbfdb26c00bc1bd53833cf0.claude@kovaldistillery.com"


def parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def write_dotenv(path: Path, updates: dict[str, str]) -> None:
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    lines: list[str] = []
    for line in existing:
        if "=" not in line or line.lstrip().startswith("#"):
            lines.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in updates:
            lines.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            lines.append(line)
    for key, value in updates.items():
        if key not in seen:
            lines.append(f"{key}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def packet_body(config: dict[str, str]) -> str:
    token_path = Path(config["GMAIL_TOKEN_PATH"]).expanduser()
    client_secret_path = Path(config["GMAIL_CLIENT_SECRET_PATH"]).expanduser()
    packet_message_id = config.get("PACKET_MESSAGE_ID", DEFAULT_PACKET_MESSAGE_ID)
    query = f"rfc822msgid:{packet_message_id}"
    gmail_access = access_token(token_path, client_secret_path)
    refs = list_messages(gmail_access, query, 1)
    if not refs:
        raise RuntimeError("refresh packet not found")
    raw, _meta = get_message_raw(gmail_access, refs[0].message_id)
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    chunks: list[str] = []
    for part in msg.walk():
        if part.get_content_type() in {"text/plain", "text/html"}:
            chunks.append(part.get_content())
    return html.unescape("\n".join(chunks))


def extract_login_payload(body: str) -> dict[str, str]:
    match = re.search(
        r"-d\s+'({\"clientId\"\s*:\s*\"[^\"]+\",\s*\"clientSecret\"\s*:\s*\"[^\"]+\"})'",
        body,
    )
    if not match:
        raise RuntimeError("refresh packet does not contain a machine-identity login payload")
    payload = json.loads(match.group(1))
    if not payload.get("clientId") or not payload.get("clientSecret"):
        raise RuntimeError("machine-identity login payload is incomplete")
    return {"clientId": str(payload["clientId"]), "clientSecret": str(payload["clientSecret"])}


def login(payload: dict[str, str], url: str) -> str:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    token = data.get("accessToken") or data.get("access_token")
    if not token:
        raise RuntimeError("machine-identity login response did not include an access token")
    return str(token)


def validate_papers(token: str, endpoint: str) -> int:
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "codex-refresh", "version": "1"},
            },
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        response.read(120)
        return int(response.status)


def refresh(config_path: Path, local_env: Path) -> dict[str, object]:
    config = parse_dotenv(config_path)
    missing = [key for key in ("GMAIL_TOKEN_PATH", "GMAIL_CLIENT_SECRET_PATH") if not config.get(key)]
    if missing:
        raise RuntimeError(f"refresh config missing: {', '.join(missing)}")
    body = packet_body(config)
    payload = extract_login_payload(body)
    token = login(payload, config.get("INFISICAL_LOGIN_URL", "https://secrets.koval.lan/api/v1/auth/universal-auth/login"))
    status = validate_papers(token, config.get("PAPERS_MCP_ENDPOINT", "https://papers.koval.lan/mcp"))
    if status != 200:
        raise RuntimeError(f"fresh token rejected by Papers MCP: status={status}")
    write_dotenv(local_env, {"KOVAL_TOKEN": token})
    return {
        "ok": True,
        "papers_initialize_status": status,
        "fallback_mode": oct(stat.S_IMODE(local_env.stat().st_mode)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh MCP runtime bearer token without printing secret values.")
    parser.add_argument("--config", default=str(DEFAULT_REFRESH_ENV))
    parser.add_argument("--local-env", default=str(DEFAULT_LOCAL_ENV))
    args = parser.parse_args()
    try:
        result = refresh(Path(args.config).expanduser(), Path(args.local_env).expanduser())
    except Exception as exc:  # noqa: BLE001 - print metadata-only blocker.
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
