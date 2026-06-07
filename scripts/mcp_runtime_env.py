#!/usr/local/bin/python3.13
"""Load MCP runtime secrets without printing secret values.

Preferred source is an approved Infisical export command. The fallback is an
owner-only local dotenv file under .private for bridge validation runs.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import shlex
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_ENV = ROOT / ".private" / "mcp-runtime" / "mcp.env"
DEFAULT_REFRESH_ENV = ROOT / ".private" / "mcp-runtime" / "refresh.env"
REQUIRED_KEYS = ("KOVAL_TOKEN", "SCREENBOX_API_KEY")
MIN_TOKEN_TTL_SECONDS = 300


def parse_dotenv(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        try:
            values[key] = shlex.split(f"v={value}", posix=True)[0].split("=", 1)[1]
        except (IndexError, ValueError):
            values[key] = value.strip("\"'")
    return values


def local_file_mode(path: Path) -> str:
    try:
        return oct(stat.S_IMODE(path.stat().st_mode))
    except OSError:
        return ""


def read_local_env(path: Path) -> tuple[dict[str, str], dict[str, object]]:
    meta = {
        "source": "local",
        "exists": path.exists(),
        "mode": local_file_mode(path),
    }
    if not path.exists():
        return {}, meta
    return parse_dotenv(path.read_text(encoding="utf-8")), meta


def infisical_command_from_env() -> list[str] | None:
    explicit = os.environ.get("INFISICAL_EXPORT_COMMAND", "").strip()
    if explicit:
        return ["/bin/sh", "-c", explicit]
    project = os.environ.get("INFISICAL_PROJECT_ID", "").strip()
    environment = os.environ.get("INFISICAL_ENV", "").strip()
    secret_path = os.environ.get("INFISICAL_PATH", "").strip()
    if not project or not environment or not secret_path:
        return None
    return [
        "infisical",
        "export",
        "--format=dotenv",
        f"--projectId={project}",
        f"--env={environment}",
        f"--path={secret_path}",
    ]


def read_infisical_env() -> tuple[dict[str, str], dict[str, object]]:
    command = infisical_command_from_env()
    meta = {
        "source": "infisical",
        "configured": bool(command),
        "available": False,
        "loaded": False,
    }
    if not command:
        return {}, meta
    if command[0] == "infisical" and not shutil_which("infisical"):
        meta["error"] = "infisical CLI is not on PATH"
        return {}, meta
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    except Exception as exc:  # noqa: BLE001 - keep status non-secret and concise.
        meta["error"] = str(exc)
        return {}, meta
    meta["available"] = True
    meta["loaded"] = True
    return parse_dotenv(result.stdout), meta


def shutil_which(command: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / command
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def merged_env(local_path: Path) -> tuple[dict[str, str], list[dict[str, object]]]:
    sources: list[dict[str, object]] = []
    values: dict[str, str] = {}
    infisical_values, infisical_meta = read_infisical_env()
    sources.append(infisical_meta)
    values.update(infisical_values)
    local_values, local_meta = read_local_env(local_path)
    sources.append(local_meta)
    for key, value in local_values.items():
        values.setdefault(key, value)
    return values, sources


def decode_jwt_payload(value: str) -> dict[str, object] | None:
    parts = value.split(".")
    if len(parts) < 2:
        return None
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode((payload + padding).encode("ascii"))
        parsed = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def jwt_status(value: str) -> dict[str, object]:
    shaped = bool(re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.", value or ""))
    status: dict[str, object] = {"jwt_shaped": shaped}
    if not shaped:
        return status

    payload = decode_jwt_payload(value)
    if payload is None:
        status["parseable"] = False
        return status

    status["parseable"] = True
    exp = payload.get("exp")
    if not isinstance(exp, int):
        status["has_exp"] = False
        return status

    now = int(dt.datetime.now(dt.UTC).timestamp())
    seconds_until_exp = exp - now
    status.update(
        {
            "has_exp": True,
            "exp_iso": dt.datetime.fromtimestamp(exp, dt.UTC).isoformat(),
            "seconds_until_exp": seconds_until_exp,
            "expired": seconds_until_exp <= 0,
            "usable": seconds_until_exp > MIN_TOKEN_TTL_SECONDS,
            "minimum_ttl_seconds": MIN_TOKEN_TTL_SECONDS,
        }
    )
    return status


def safe_status(values: dict[str, str], sources: list[dict[str, object]]) -> dict[str, object]:
    keys: dict[str, dict[str, object]] = {}
    for key in REQUIRED_KEYS:
        key_status: dict[str, object] = {"present": bool(values.get(key))}
        if key == "KOVAL_TOKEN":
            key_status.update(jwt_status(values.get(key, "")))
        keys[key] = key_status

    token = keys.get("KOVAL_TOKEN", {})
    token_usable = not values.get("KOVAL_TOKEN") or bool(token.get("usable"))
    return {
        "ok": all(values.get(key) for key in REQUIRED_KEYS) and token_usable,
        "sources": sources,
        "keys": keys,
    }


def init_local(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Owner-only local fallback for MCP bridge validation.\n"
            "# Do not commit, print, email, or paste these values.\n"
            "KOVAL_TOKEN=\n"
            "SCREENBOX_API_KEY=\n",
            encoding="utf-8",
        )
    path.chmod(0o600)


def runtime_blockers(values: dict[str, str]) -> list[str]:
    blockers = [f"{key} is missing" for key in REQUIRED_KEYS if not values.get(key)]
    if not values.get("KOVAL_TOKEN"):
        return blockers

    token = jwt_status(values["KOVAL_TOKEN"])
    if not token.get("jwt_shaped"):
        blockers.append("KOVAL_TOKEN is not JWT-shaped")
    elif token.get("parseable") is False:
        blockers.append("KOVAL_TOKEN JWT payload is not parseable")
    elif token.get("has_exp") is False:
        blockers.append("KOVAL_TOKEN JWT has no exp claim")
    elif token.get("usable") is False:
        exp_iso = token.get("exp_iso", "unknown")
        blockers.append(f"KOVAL_TOKEN is expired or under minimum TTL; exp={exp_iso}")
    return blockers


def token_needs_refresh(values: dict[str, str]) -> bool:
    if not values.get("KOVAL_TOKEN"):
        return False
    token = jwt_status(values["KOVAL_TOKEN"])
    return bool(token.get("jwt_shaped") and token.get("usable") is False)


def auto_refresh_token(local_path: Path) -> dict[str, object]:
    if not DEFAULT_REFRESH_ENV.exists():
        return {"attempted": False, "reason": "refresh config absent"}
    command = [
        sys.executable,
        str(ROOT / "scripts" / "mcp_runtime_token_refresh.py"),
        "--config",
        str(DEFAULT_REFRESH_ENV),
        "--local-env",
        str(local_path),
    ]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=45)
    except Exception as exc:  # noqa: BLE001 - metadata-only status.
        return {"attempted": True, "ok": False, "error": str(exc)}
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {"ok": False, "error": "refresh helper returned non-json output"}
    payload["attempted"] = True
    payload["returncode"] = result.returncode
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Load MCP runtime env from Infisical or local fallback.")
    parser.add_argument("--local-env", default=str(DEFAULT_LOCAL_ENV))
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Print non-secret key/source status.")
    subparsers.add_parser("init-local", help="Create a chmod 600 local fallback template.")
    exec_parser = subparsers.add_parser("exec", help="Run a command with loaded MCP env.")
    exec_parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    local_path = Path(args.local_env).expanduser()
    if args.command == "init-local":
        init_local(local_path)
        print(json.dumps({"ok": True, "mode": local_file_mode(local_path)}, indent=2))
        return 0

    values, sources = merged_env(local_path)
    if args.command == "status":
        status = safe_status(values, sources)
        print(json.dumps(status, indent=2))
        return 0 if status["ok"] else 2

    argv = list(args.argv)
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        raise SystemExit("exec requires a command after --")
    refresh_result: dict[str, object] | None = None
    if token_needs_refresh(values):
        refresh_result = auto_refresh_token(local_path)
        if refresh_result.get("ok"):
            values, sources = merged_env(local_path)

    blockers = runtime_blockers(values)
    if blockers:
        print(
            json.dumps(
                {
                    "ok": False,
                    "blockers": blockers,
                    "refresh": refresh_result,
                    "status": safe_status(values, sources),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 2
    child_env = os.environ.copy()
    child_env.update({key: values[key] for key in REQUIRED_KEYS})
    os.execvpe(argv[0], argv, child_env)
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
