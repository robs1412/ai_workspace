#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path


RECORDER = Path("/Users/werkstatt/ai_workspace/scripts/task_flow_mysql_recorder.php")
MCP_ENV = Path("/Users/werkstatt/ai_workspace/scripts/mcp_runtime_env.py")
PAPERS_MCP_URL = "https://papers.koval.lan/mcp"


def run_recorder(*args: str) -> dict:
    result = subprocess.run(["php", str(RECORDER), *args], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise RuntimeError(f"recorder returned non-ok payload for {' '.join(args)}")
    return payload


def mcp_env() -> dict[str, str]:
    probe = subprocess.run([str(MCP_ENV), "status"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    if probe.returncode != 0:
        raise RuntimeError("MCP env is not available for Papers projection.")
    values = os.environ.copy()
    # Re-execing through mcp_runtime_env keeps secret loading out of stdout; this script is also used through that wrapper.
    if not values.get("KOVAL_TOKEN"):
        raise RuntimeError("KOVAL_TOKEN is not present in this process; run through mcp_runtime_env.py exec.")
    return values


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


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return clean[:80] or "task-flow-record"


def markdown_for_item(item: dict) -> str:
    title = f"Task Flow Projection - {item.get('owner_lane') or item.get('dedupe_key')}"
    rows = [
        ("Dedupe key", item.get("dedupe_key", "")),
        ("Source reference", item.get("source_ref", "")),
        ("Intake channel", item.get("intake_channel", "")),
        ("Owner lane", item.get("owner_lane", "")),
        ("Responsible worker/persona", item.get("responsible_worker_or_persona", "")),
        ("Workspaceboard session", item.get("workspaceboard_session", "")),
        ("OPS/Portal/domain task", item.get("ops_portal_or_domain_task", "")),
        ("Status", item.get("status", "")),
        ("Due or trigger", item.get("due_or_trigger", "")),
        ("Scheduled action", item.get("scheduled_action", "")),
        ("Calendar event", item.get("calendar_event", "")),
        ("Completion/blocker email", item.get("completion_or_blocker_email", "")),
        ("Verification readback", item.get("verification_readback", "")),
        ("Next update", item.get("next_update", "")),
    ]
    table = "\n".join(f"| {label} | {str(value or '').replace('|', '/')} |" for label, value in rows)
    return (
        f"# {title}\n\n"
        f"Projected: {datetime.now().isoformat(timespec='seconds')}\n\n"
        "This non-secret projection was generated from the shared email-worker task-flow tables. "
        "It intentionally excludes credentials, token values, private mailbox bodies, private SOP text, payment details, and unauthorized access instructions.\n\n"
        "| Field | Value |\n| --- | --- |\n"
        f"{table}\n"
    )


def project_item(item: dict, session_id: str) -> tuple[dict, str]:
    dedupe = str(item.get("dedupe_key") or "")
    path = f"teams/ai-team/task-flow/{datetime.now().date().isoformat()}-{slug(dedupe)}.md"
    content = markdown_for_item(item)
    result, session_id = mcp_call(
        "tools/call",
        {
            "name": "papers_create",
            "arguments": {
                "path": path,
                "content": content,
                "title": f"Task Flow Projection - {dedupe}",
                "summary": "Non-secret email-worker task-flow projection.",
                "tags": ["task-flow", "email-workers", "codex"],
                "created_by": "codex-task-flow",
            },
        },
        3,
        session_id,
    )
    projection_ref = result.get("guid") or result.get("path") or path
    run_recorder("projected", dedupe, str(projection_ref))
    return {"dedupe_key": dedupe, "path": path, "papers_result": result, "projection_ref": projection_ref}, session_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Project non-secret task-flow records to Papers.")
    parser.add_argument("--dedupe-key", default="")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    mcp_env()
    report = run_recorder("report", str(args.limit))
    items = report.get("items") if isinstance(report.get("items"), list) else []
    if args.dedupe_key:
        items = [item for item in items if item.get("dedupe_key") == args.dedupe_key]
    else:
        items = [
            item for item in items
            if (item.get("papers_projection_missing") or item.get("papers_projection") == "papers_pending")
            and item.get("severity") in {"closed", "papers_pending"}
        ]
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "projectable": items}, ensure_ascii=True))
        return 0
    if not items:
        print(json.dumps({"ok": True, "projected": 0, "items": []}, ensure_ascii=True))
        return 0
    _, session_id = mcp_call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "codex-task-flow", "version": "1"}}, 1)
    projected = []
    for item in items:
        result, session_id = project_item(item, session_id or "")
        projected.append(result)
    print(json.dumps({"ok": True, "projected": len(projected), "items": projected}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
