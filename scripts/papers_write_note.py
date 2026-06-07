#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


PAPERS_MCP_URL = "https://papers.koval.lan/mcp"
MCP_ENV = Path("/Users/werkstatt/ai_workspace/scripts/mcp_runtime_env.py")


def mcp_env() -> None:
    probe = subprocess.run([str(MCP_ENV), "status"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    if probe.returncode != 0:
        raise RuntimeError("MCP env is not available for Papers writes.")
    if not os.environ.get("KOVAL_TOKEN"):
        raise RuntimeError("KOVAL_TOKEN is not present in this process; run through mcp_runtime_env.py exec.")


def parse_sse_json(body: str) -> dict:
    stripped = body.strip()
    if stripped.startswith("{"):
        payload = json.loads(stripped)
        if isinstance(payload, dict):
            return payload
    for line in body.splitlines():
        clean = line.strip()
        if clean.startswith("data: "):
            payload = json.loads(clean[6:])
            if isinstance(payload, dict):
                return payload
    raise RuntimeError("MCP response did not contain a JSON data event.")


def mcp_call(method: str, params: dict, request_id: int, session_id: str | None = None) -> tuple[dict, str | None]:
    token = os.environ["KOVAL_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-03-26",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}).encode()
    req = urllib.request.Request(PAPERS_MCP_URL, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        new_session = response.headers.get("Mcp-Session-Id") or session_id
        payload = parse_sse_json(response.read().decode("utf-8", "replace"))
    if "error" in payload:
        raise RuntimeError(json.dumps(payload["error"], ensure_ascii=True))
    return payload.get("result") or {}, new_session


def read_body(input_path: Path | None) -> str:
    if input_path is None:
        return sys.stdin.read()
    return input_path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a non-secret note to Papers.")
    parser.add_argument("--path", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", default="Non-secret durable note.")
    parser.add_argument("--tags", default="")
    parser.add_argument("--created-by", default="codex")
    parser.add_argument("--guid", default="", help="Existing Papers GUID to update instead of creating a new document.")
    parser.add_argument("--updated-by", default="codex")
    parser.add_argument("--input-file", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    body = read_body(Path(args.input_file).expanduser() if args.input_file else None)
    if not body.strip():
        raise RuntimeError("No content supplied for Papers write.")

    mcp_env()
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "path": args.path, "title": args.title, "guid": args.guid}, ensure_ascii=True))
        return 0

    _, session_id = mcp_call(
        "initialize",
        {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "codex-papers-write", "version": "1"}},
        1,
    )
    tags = [tag.strip() for tag in re.split(r"[,\s]+", args.tags) if tag.strip()]
    if args.guid:
        result, _ = mcp_call(
            "tools/call",
            {
                "name": "papers_update",
                "arguments": {
                    "guid": args.guid,
                    "path": args.path,
                    "content": body,
                    "title": args.title,
                    "summary": args.summary,
                    "tags": tags,
                    "updated_by": args.updated_by,
                },
            },
            2,
            session_id,
        )
    else:
        result, _ = mcp_call(
            "tools/call",
            {
                "name": "papers_create",
                "arguments": {
                    "path": args.path,
                    "content": body,
                    "title": args.title,
                    "summary": args.summary,
                    "tags": tags,
                    "created_by": args.created_by,
                },
            },
            2,
            session_id,
        )
    print(json.dumps({"ok": True, "result": result, "path": args.path}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
