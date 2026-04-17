#!/usr/bin/env python3
"""Short-lived, code-gated file transfer receiver for AI worker hosts."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import secrets
import shlex
import shutil
import stat
import sys
import time
from pathlib import Path


DEFAULT_STATE_DIR = Path.home() / ".ai-transfer-gate"
DEFAULT_TTL_SECONDS = 5 * 60
MAX_TTL_SECONDS = 30 * 60
MAX_FILE_BYTES = 2 * 1024 * 1024 * 1024


class GateError(Exception):
    pass


def now() -> int:
    return int(time.time())


def require_private_dir(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path, 0o700)


def write_private_json(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(tmp, flags, 0o600)
    try:
      with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    except Exception:
      try:
        tmp.unlink()
      except FileNotFoundError:
        pass
      raise
    os.replace(tmp, path)
    os.chmod(path, 0o600)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def hash_code(grant_id: str, nonce: str, code: str) -> str:
    return hashlib.sha256(f"{grant_id}:{nonce}:{code}".encode("utf-8")).hexdigest()


def state_paths(state_dir: Path) -> tuple[Path, Path]:
    return state_dir / "grants", state_dir / "audit.jsonl"


def append_audit(state_dir: Path, event: dict) -> None:
    require_private_dir(state_dir)
    _, audit_path = state_paths(state_dir)
    event = {
        "ts": now(),
        "host": os.uname().nodename,
        "user": getpass.getuser(),
        **event,
    }
    with audit_path.open("a", encoding="utf-8") as handle:
        os.chmod(audit_path, 0o600)
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def real_file(path_text: str) -> Path:
    path = Path(path_text).expanduser().resolve()
    if not path.exists():
        raise GateError(f"File does not exist: {path}")
    if not path.is_file():
        raise GateError(f"Approved path is not a regular file: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise GateError(f"File is too large for this gate: {size} bytes")
    return path


def assert_local_tty(args: argparse.Namespace) -> None:
    if args.non_interactive_test:
        return
    if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_CLIENT"):
        raise GateError("Refusing to create a grant from an SSH session. Run approve locally on this Mac.")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise GateError("Refusing to print an approval code without an interactive local terminal.")


def approve(args: argparse.Namespace) -> int:
    assert_local_tty(args)
    state_dir = Path(args.state_dir).expanduser()
    grants_dir, _ = state_paths(state_dir)
    require_private_dir(state_dir)
    require_private_dir(grants_dir)

    file_path = real_file(args.file)
    ttl = min(max(int(args.ttl), 30), MAX_TTL_SECONDS)
    grant_id = f"{int(time.time())}-{secrets.token_hex(4)}"
    code = f"{secrets.randbelow(1000000):06d}"
    nonce = secrets.token_hex(16)
    expires_at = now() + ttl
    grant_path = grants_dir / f"{grant_id}.json"

    payload = {
        "version": 1,
        "grant_id": grant_id,
        "file_path": str(file_path),
        "basename": file_path.name,
        "size": file_path.stat().st_size,
        "created_at": now(),
        "expires_at": expires_at,
        "ttl_seconds": ttl,
        "code_hash": hash_code(grant_id, nonce, code),
        "nonce": nonce,
        "used_at": None,
        "used_by": "",
    }
    write_private_json(grant_path, payload)
    append_audit(state_dir, {
        "event": "grant_created",
        "grant_id": grant_id,
        "basename": file_path.name,
        "file_path": str(file_path),
        "size": payload["size"],
        "expires_at": expires_at,
    })

    print(f"Grant: {grant_id}")
    print(f"Code: {code}")
    print(f"File: {file_path}")
    print(f"Size: {payload['size']} bytes")
    print(f"Expires in: {ttl} seconds")
    print("Share the grant id and code only for this transfer. The code is not stored in plaintext.")
    return 0


def parse_original_command() -> list[str]:
    original = os.environ.get("SSH_ORIGINAL_COMMAND", "")
    if not original:
        raise GateError("No SSH command supplied. Expected: fetch <grant_id> <code>")
    try:
        return shlex.split(original)
    except ValueError as error:
        raise GateError(f"Invalid SSH command: {error}") from error


def mark_used(grant_path: Path, grant: dict, used_by: str) -> None:
    grant["used_at"] = now()
    grant["used_by"] = used_by
    write_private_json(grant_path, grant)


def serve(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir).expanduser()
    grants_dir, _ = state_paths(state_dir)
    parts = parse_original_command()
    if len(parts) != 3 or parts[0] != "fetch":
        raise GateError("Unsupported command. Expected: fetch <grant_id> <code>")
    grant_id, code = parts[1], parts[2]
    if not grant_id or not code.isdigit() or len(code) != 6:
        raise GateError("Invalid grant id or code format.")

    grant_path = grants_dir / f"{grant_id}.json"
    if not grant_path.exists():
        append_audit(state_dir, {"event": "fetch_denied", "grant_id": grant_id, "reason": "missing"})
        raise GateError("Grant not found.")
    grant = load_json(grant_path)
    if grant.get("used_at"):
        append_audit(state_dir, {"event": "fetch_denied", "grant_id": grant_id, "reason": "used"})
        raise GateError("Grant has already been used.")
    if now() > int(grant.get("expires_at") or 0):
        append_audit(state_dir, {"event": "fetch_denied", "grant_id": grant_id, "reason": "expired"})
        raise GateError("Grant has expired.")
    expected = grant.get("code_hash", "")
    actual = hash_code(grant_id, str(grant.get("nonce", "")), code)
    if not secrets.compare_digest(expected, actual):
        append_audit(state_dir, {"event": "fetch_denied", "grant_id": grant_id, "reason": "bad_code"})
        raise GateError("Invalid approval code.")

    file_path = real_file(str(grant.get("file_path", "")))
    if str(file_path) != str(Path(grant["file_path"]).resolve()):
        raise GateError("Approved file path changed unexpectedly.")

    used_by = os.environ.get("SSH_CONNECTION", "ssh")
    append_audit(state_dir, {
        "event": "fetch_allowed",
        "grant_id": grant_id,
        "basename": grant.get("basename", file_path.name),
        "size": file_path.stat().st_size,
        "used_by": used_by,
    })
    mark_used(grant_path, grant, used_by)

    with file_path.open("rb") as handle:
        shutil.copyfileobj(handle, sys.stdout.buffer)
    return 0


def cleanup(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir).expanduser()
    grants_dir, _ = state_paths(state_dir)
    if not grants_dir.exists():
        return 0
    removed = 0
    cutoff = now()
    for grant_path in grants_dir.glob("*.json"):
        try:
            grant = load_json(grant_path)
        except Exception:
            continue
        if grant.get("used_at") or cutoff > int(grant.get("expires_at") or 0):
            grant_path.unlink()
            removed += 1
    print(f"Removed {removed} consumed or expired grants.")
    return 0


def public_key_text(path: str) -> str:
    key_path = Path(path).expanduser()
    if not key_path.exists():
        raise GateError(f"Public key file does not exist: {key_path}")
    text = key_path.read_text(encoding="utf-8").strip()
    parts = text.split()
    if len(parts) < 2 or not parts[0].startswith("ssh-"):
        raise GateError("Public key file does not look like an OpenSSH public key.")
    return f"{parts[0]} {parts[1]} {parts[2] if len(parts) > 2 else 'ai-transfer-gate'}".strip()


def restricted_authorized_key(public_key: str, gate_path: Path, from_host: str) -> str:
    key_parts = public_key.strip().split()
    key_body = " ".join(key_parts[:2])
    comment = key_parts[2] if len(key_parts) > 2 else "ai-transfer-gate"
    command = f'{shlex.quote(str(gate_path))} serve'
    options = [
        f'from="{from_host}"',
        "restrict",
        "no-agent-forwarding",
        "no-X11-forwarding",
        "no-port-forwarding",
        "no-pty",
        f'command="{command}"',
    ]
    return f"{','.join(options)} {key_body} {comment}"


def install_authorized_key(args: argparse.Namespace) -> int:
    public_key = public_key_text(args.public_key)
    gate_path = Path(args.gate_path).expanduser().resolve()
    if not gate_path.exists():
        raise GateError(f"Gate script does not exist: {gate_path}")
    auth_path = Path(args.authorized_keys).expanduser()
    auth_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not auth_path.exists():
        auth_path.write_text("", encoding="utf-8")
        os.chmod(auth_path, 0o600)
    existing = auth_path.read_text(encoding="utf-8").splitlines()
    key_body = " ".join(public_key.split()[:2])
    replacement = restricted_authorized_key(public_key, gate_path, args.from_host)
    matching = [line for line in existing if key_body in line]
    if matching and not args.replace_existing:
        raise GateError("Matching key already exists. Re-run with --replace-existing after reviewing dry-run output.")
    new_lines = [line for line in existing if key_body not in line]
    new_lines.append(replacement)

    print("Restricted authorized_keys line:")
    print(replacement)
    if not args.apply:
        print("Dry run only. Re-run with --apply --replace-existing to install.")
        if matching:
            print(f"Would replace {len(matching)} existing matching line(s).")
        return 0

    backup = auth_path.with_name(f"{auth_path.name}.bak.{time.strftime('%Y%m%d%H%M%S')}")
    shutil.copy2(auth_path, backup)
    auth_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
    os.chmod(auth_path, 0o600)
    print(f"Installed restricted key. Backup: {backup}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR))
    sub = parser.add_subparsers(dest="command", required=True)

    approve_parser = sub.add_parser("approve", help="Create a local, short-lived transfer grant.")
    approve_parser.add_argument("file")
    approve_parser.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS)
    approve_parser.add_argument("--non-interactive-test", action="store_true")
    approve_parser.set_defaults(func=approve)

    serve_parser = sub.add_parser("serve", help="Forced SSH command entrypoint.")
    serve_parser.set_defaults(func=serve)

    cleanup_parser = sub.add_parser("cleanup", help="Remove expired or consumed grants.")
    cleanup_parser.set_defaults(func=cleanup)

    install_parser = sub.add_parser("install-authorized-key", help="Install a forced-command authorized_keys entry.")
    install_parser.add_argument("--public-key", required=True)
    install_parser.add_argument("--gate-path", required=True)
    install_parser.add_argument("--from-host", default="192.168.55.17")
    install_parser.add_argument("--authorized-keys", default=str(Path.home() / ".ssh" / "authorized_keys"))
    install_parser.add_argument("--replace-existing", action="store_true")
    install_parser.add_argument("--apply", action="store_true")
    install_parser.set_defaults(func=install_authorized_key)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GateError as error:
        print(f"ai-transfer-gate: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
