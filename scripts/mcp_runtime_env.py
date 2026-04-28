#!/usr/bin/env python3
"""Load MCP runtime secrets without printing secret values.

Preferred source is an approved Infisical export command. The fallback is an
owner-only local dotenv file under .private for bridge validation runs.
"""

from __future__ import annotations

import argparse
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
REQUIRED_KEYS = ("KOVAL_TOKEN", "SCREENBOX_API_KEY")


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
        "path": str(path),
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


def safe_status(values: dict[str, str], sources: list[dict[str, object]]) -> dict[str, object]:
    return {
        "ok": all(values.get(key) for key in REQUIRED_KEYS),
        "sources": sources,
        "keys": {
            key: {
                "present": bool(values.get(key)),
                "jwt_shaped": bool(key == "KOVAL_TOKEN" and re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.", values.get(key, ""))),
            }
            for key in REQUIRED_KEYS
        },
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
        print(json.dumps({"ok": True, "path": str(local_path), "mode": local_file_mode(local_path)}, indent=2))
        return 0

    values, sources = merged_env(local_path)
    if args.command == "status":
        print(json.dumps(safe_status(values, sources), indent=2))
        return 0 if all(values.get(key) for key in REQUIRED_KEYS) else 2

    argv = list(args.argv)
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        raise SystemExit("exec requires a command after --")
    missing = [key for key in REQUIRED_KEYS if not values.get(key)]
    if missing:
        print(json.dumps({"ok": False, "missing": missing, "sources": sources}, indent=2), file=sys.stderr)
        return 2
    child_env = os.environ.copy()
    child_env.update({key: values[key] for key in REQUIRED_KEYS})
    os.execvpe(argv[0], argv, child_env)
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
