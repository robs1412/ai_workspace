#!/usr/bin/env python3
"""Fetch a code-approved file from a workstation transfer gate."""

from __future__ import annotations

import argparse
import getpass
import os
import shlex
import subprocess
import sys
from pathlib import Path


class FetchError(Exception):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="SSH host, for example kovaladmin@192.168.55.35")
    parser.add_argument("grant_id")
    parser.add_argument("--output", "-o", required=True, help="Destination file path on this machine.")
    parser.add_argument("--identity", "-i", default="", help="Optional SSH identity file.")
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--code", default="", help="Approval code. Omit to prompt without echo.")
    return parser


def fetch(args: argparse.Namespace) -> int:
    code = args.code or getpass.getpass("Approval code: ")
    if not code.isdigit() or len(code) != 6:
        raise FetchError("Approval code must be six digits.")

    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(f"{output.suffix}.part")
    ssh_command = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-p", str(args.port),
    ]
    if args.identity:
        ssh_command.extend(["-i", str(Path(args.identity).expanduser())])
    ssh_command.extend([args.host, f"fetch {shlex.quote(args.grant_id)} {shlex.quote(code)}"])

    with tmp.open("wb") as handle:
        result = subprocess.run(ssh_command, stdout=handle, stderr=subprocess.PIPE)
    if result.returncode != 0:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise FetchError(stderr or f"ssh exited with {result.returncode}")
    os.replace(tmp, output)
    print(f"Fetched grant {args.grant_id} to {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return fetch(args)
    except FetchError as error:
        print(f"ai-transfer-fetch: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
