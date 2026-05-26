#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

AI_WORKSPACE = Path("/Users/werkstatt/ai_workspace")
OPS_CREATE = Path("/Users/werkstatt/ops/scripts/create_codex_task.php")
TASK_FLOW_RECORDER = AI_WORKSPACE / "scripts/task_flow_mysql_recorder.php"
SCRIPT_ROOT = AI_WORKSPACE / "scripts"

if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import shared_task_flow  # type: ignore
from task_flow_due_runner import (  # type: ignore
    DEFAULT_WORKSPACEBOARD_URL,
    create_worker_route_session,
    deliver_worker_route_message,
)


def run_create_task(title: str, notes: str, due: str, creator_id: int, owner_id: int, assignee_ids: str) -> dict:
    cmd = [
        "php",
        str(OPS_CREATE),
        f"--title={title}",
        f"--description={notes}",
        f"--due={due}",
        f"--creator-id={creator_id}",
        f"--owner-id={owner_id}",
        f"--assignee-ids={assignee_ids}",
    ]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("OPS task helper returned non-object JSON.")
    return payload


def record_task_flow(packet: dict, event: str, summary: dict) -> dict:
    payload = {
        "event": event,
        "packet": packet,
        "summary": summary,
    }
    result = subprocess.run(
        ["php", str(TASK_FLOW_RECORDER), "record"],
        input=json.dumps(payload, ensure_ascii=True),
        check=True,
        text=True,
        capture_output=True,
    )
    response = json.loads(result.stdout)
    if not isinstance(response, dict) or response.get("ok") is not True:
        raise RuntimeError("Task Flow recorder did not return ok=true.")
    return response


def build_worker_message(task_id: int, title: str, due: str, workspace: str, notes: str) -> str:
    return "\n".join([
        f"Recorded OPS task {task_id} for workspace `{workspace}`.",
        "",
        f"Subject: {title}",
        f"Due/start date: {due}",
        "",
        "Instructions:",
        notes,
        "",
        "Proof required:",
        "- Keep this task visible in Workspaceboard.",
        "- Preserve the linked OPS task id.",
        "- When work begins, verify source state first and report exact proof or blocker.",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--notes", required=True)
    parser.add_argument("--due", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--requester", default="Robert")
    parser.add_argument("--creator-id", type=int, default=1)
    parser.add_argument("--owner-id", type=int, default=1332)
    parser.add_argument("--assignee-ids", default="1332")
    parser.add_argument("--owner-lane", default="")
    parser.add_argument("--worker", default="Codex")
    parser.add_argument("--api-base", default=DEFAULT_WORKSPACEBOARD_URL)
    args = parser.parse_args()

    task_result = run_create_task(
        title=args.title,
        notes=args.notes,
        due=args.due,
        creator_id=args.creator_id,
        owner_id=args.owner_id,
        assignee_ids=args.assignee_ids,
    )
    task = task_result.get("task") if isinstance(task_result.get("task"), dict) else {}
    task_id = int(task_result.get("task_id") or 0)
    if task_id <= 0:
        raise RuntimeError("OPS task helper did not return a task id.")

    session_title = f"OPS task {task_id}: {args.title}"
    worker_message = build_worker_message(task_id, args.title, args.due, args.workspace, args.notes)
    session_id, attachment_group = create_worker_route_session(
        args.api_base.rstrip("/"),
        args.workspace,
        session_title,
        worker_message,
    )
    deliver_result = deliver_worker_route_message(
        args.api_base.rstrip("/"),
        session_id,
        str(attachment_group.get("id") or ""),
        worker_message,
    )

    owner_lane = args.owner_lane or args.workspace
    packet = shared_task_flow.build_packet(
        source_ref=args.source_ref,
        intake_channel="ops-task-recording",
        requester=args.requester,
        owner_lane=owner_lane,
        responsible_worker_or_persona=args.worker,
        workspaceboard_session=session_id,
        ops_portal_or_domain_task=str(task_id),
        status="working",
        due_or_trigger=args.due,
        verification_readback=(
            f"ops_task_created:{task_id}; "
            f"workspaceboard_session_created:{session_id}; "
            f"worker_message_delivered"
        ),
        next_update="Worker is visible in Workspaceboard and linked to the OPS task.",
        requested_deliverable=args.title,
        proof_required="OPS task id, Workspaceboard session id, and linked Task Flow packet.",
        output_channel="Workspaceboard + OPS",
    )

    record_task_flow(
        packet,
        event="ops_task_recorded_with_workspaceboard_worker",
        summary={
            "title": args.title,
            "notes": args.notes,
            "workspace": args.workspace,
            "task_created": task_result,
            "workspaceboard_delivery": deliver_result,
        },
    )

    print(json.dumps({
        "ok": True,
        "title": args.title,
        "workspace": args.workspace,
        "ops_task": task_result,
        "workspaceboard_session_id": session_id,
        "attachment_group_id": attachment_group.get("id"),
        "task_flow_dedupe_key": packet.get("dedupe_key"),
        "task_flow_packet": packet,
    }, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
