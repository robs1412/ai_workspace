#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import shared_task_flow


DEFAULT_RECORDER = Path("/Users/werkstatt/ai_workspace/scripts/task_flow_mysql_recorder.php")
DEFAULT_STATE = Path("/Users/admin/.task-flow-launch/state")
DEFAULT_SEND_HELPER = Path("/Users/admin/.frank-launch/runtime/scripts/send_frank_email.py")
DMYTRO_EMAIL = "dmytro.klymentiev@kovaldistillery.com"
ROBERT_EMAIL = "robert@kovaldistillery.com"


def load_due(recorder: Path, limit: int) -> dict:
    result = subprocess.run(
        ["php", str(recorder), "due", str(limit)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise RuntimeError("task-flow due report did not return ok=true")
    return payload


def packet_from_due_item(item: dict) -> dict:
    return shared_task_flow.build_packet(
        source_ref=item.get("source_ref") or item.get("dedupe_key") or "",
        dedupe_key=item.get("dedupe_key") or "",
        intake_channel="task-flow-due",
        requester="task-flow-reminder",
        owner_lane=item.get("owner_lane") or "",
        responsible_worker_or_persona=item.get("responsible_worker_or_persona") or "",
        workspaceboard_session=item.get("workspaceboard_session") or "",
        ops_portal_or_domain_task=item.get("ops_portal_or_domain_task") or "",
        status="waiting",
        due_or_trigger=item.get("due_or_trigger") or "",
        scheduled_action=item.get("scheduled_action") or "",
        calendar_event=item.get("calendar_event") or "",
        verification_readback="task_flow_due_runner_detected_due_item",
        next_update=item.get("next_update") or "Wake the responsible worker/persona and check dependency before sending.",
    )


def reminder_key(item: dict) -> str:
    return "|".join([
        str(item.get("dedupe_key") or ""),
        str(item.get("due_or_trigger") or ""),
        str(item.get("scheduled_action") or ""),
    ])


def existing_reminder_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        due_item = row.get("due_item") if isinstance(row.get("due_item"), dict) else {}
        key = reminder_key(due_item)
        if key.strip("|"):
            keys.add(key)
    return keys


def write_notification_body(path: Path, items: list[dict]) -> None:
    lines = [
        "Hi Robert,",
        "",
        "The following task-flow reminder item is due:",
        "",
    ]
    if len(items) != 1:
        lines[2] = "The following task-flow reminder items are due:"
    for index, item in enumerate(items, 1):
        lines.extend([
            f"{index}. {item.get('owner_lane') or 'unassigned'} / {item.get('responsible_worker_or_persona') or 'unassigned'}",
            f"   Due: {item.get('due_or_trigger') or ''}",
            f"   Task: {item.get('ops_portal_or_domain_task') or item.get('dedupe_key') or ''}",
            f"   Next: {item.get('next_update') or ''}",
            "",
        ])
    lines.extend([
        "Best,",
        "",
        "Frank",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    path.chmod(0o600)


def notify_robert(send_helper: Path, state_dir: Path, items: list[dict]) -> dict:
    if not items:
        return {"sent": False, "reason": "no_new_items"}
    body_path = state_dir / f"task-flow-reminder-{int(time.time())}.txt"
    write_notification_body(body_path, items)
    subject = "Task Flow Reminder: due item" if len(items) == 1 else f"Task Flow Reminder: {len(items)} due items"
    task_id = f"task-flow-reminder-{time.strftime('%Y-%m-%d-%H%M%S')}"
    result = subprocess.run(
        [
            "python3",
            str(send_helper),
            "--assistant",
            "frank",
            "--to",
            "robert@kovaldistillery.com",
            "--subject",
            subject,
            "--body-file",
            str(body_path),
            "--task-id",
            task_id,
            "--no-signature",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    return {
        "sent": result.returncode == 0,
        "task_id": task_id,
        "body_path": str(body_path),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def write_dmytro_gcp_admin_reminder(path: Path) -> None:
    lines = [
        "Hi Dmytro,",
        "",
        "Quick reminder on the KOVAL Agents Drive / Google Sheets blocker.",
        "",
        "We still need the actual Google Cloud Console admin or project owner for project koval-agents, project number 872255708765, or someone with that access to enable sheets.googleapis.com and docs.googleapis.com.",
        "",
        "Claude's last readback said the prior Frank-owner conclusion was only inferred from OAuth context and that real IAM readback was not available from the current server credentials.",
        "",
        "Please either point us to the correct admin/account owner or enable the two APIs if you have access. Please do not send credentials, tokens, private keys, callback URLs, service account keys, or raw secret values by email.",
        "",
        "Best,",
        "",
        "Frank",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    path.chmod(0o600)


def execute_due_action(send_helper: Path, state_dir: Path, item: dict) -> dict:
    action = str(item.get("scheduled_action") or "")
    if action != "frank-send-dmytro-koval-agents-gcp-admin-reminder-2026-05-01-1000":
        return {"executed": False, "reason": "no_matching_action"}

    body_path = state_dir / "dmytro-koval-agents-gcp-admin-reminder-2026-05-01-1000.txt"
    write_dmytro_gcp_admin_reminder(body_path)
    task_id = "frank-dmytro-koval-agents-gcp-admin-reminder-2026-05-01-1000"
    result = subprocess.run(
        [
            "python3",
            str(send_helper),
            "--assistant",
            "frank",
            "--to",
            DMYTRO_EMAIL,
            "--cc",
            ROBERT_EMAIL,
            "--subject",
            "Reminder: KOVAL Agents Drive API admin",
            "--body-file",
            str(body_path),
            "--task-id",
            task_id,
            "--no-signature",
            "--allow-non-primary",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    return {
        "executed": True,
        "sent": result.returncode == 0,
        "task_id": task_id,
        "body_path": str(body_path),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def packet_from_executed_action(item: dict, result: dict) -> dict:
    status = "reported" if result.get("sent") else "blocked"
    return shared_task_flow.build_packet(
        source_ref=item.get("source_ref") or item.get("dedupe_key") or "",
        dedupe_key=item.get("dedupe_key") or "",
        intake_channel="task-flow-action",
        requester="task-flow-reminder",
        owner_lane=item.get("owner_lane") or "",
        responsible_worker_or_persona=item.get("responsible_worker_or_persona") or "",
        workspaceboard_session=item.get("workspaceboard_session") or "",
        ops_portal_or_domain_task=item.get("ops_portal_or_domain_task") or "",
        status=status,
        due_or_trigger=item.get("due_or_trigger") or "",
        scheduled_action=item.get("scheduled_action") or "",
        calendar_event=item.get("calendar_event") or "",
        completion_or_blocker_email=result.get("task_id") or "",
        verification_readback="scheduled_action_sent" if result.get("sent") else "scheduled_action_send_failed",
        next_update="Dmytro reminder sent; waiting for Google Cloud project-admin answer." if result.get("sent") else "Scheduled Dmytro reminder failed; inspect task-flow due runner logs.",
    )


def write_runner_state(path: Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check due task-flow reminders and record wake events.")
    parser.add_argument("--recorder", default=str(DEFAULT_RECORDER))
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE))
    parser.add_argument("--send-helper", default=str(DEFAULT_SEND_HELPER))
    parser.add_argument("--notify-robert", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    recorder = Path(args.recorder)
    state_dir = Path(args.state_dir)
    due = load_due(recorder, args.limit)
    items = due.get("items") if isinstance(due.get("items"), list) else []
    state_dir.mkdir(parents=True, exist_ok=True)
    state_dir.chmod(0o700)
    reminder_log = state_dir / "task-flow-reminders.jsonl"
    seen = existing_reminder_keys(reminder_log)

    recorded = 0
    skipped_existing = 0
    new_items: list[dict] = []
    action_results: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = reminder_key(item)
        if key in seen:
            skipped_existing += 1
            continue
        packet = packet_from_due_item(item)
        if not args.dry_run:
            shared_task_flow.append_event(
                reminder_log,
                packet,
                "reminder_due",
                due_item=item,
            )
            action_result = execute_due_action(Path(args.send_helper), state_dir, item)
            if action_result.get("executed"):
                action_packet = packet_from_executed_action(item, action_result)
                shared_task_flow.append_event(
                    reminder_log,
                    action_packet,
                    "scheduled_action_executed" if action_result.get("sent") else "scheduled_action_failed",
                    due_item=item,
                    action_result=action_result,
                )
                action_results.append(action_result)
            seen.add(key)
            recorded += 1
            new_items.append(item)

    notification = {"sent": False, "reason": "not_requested"}
    if args.notify_robert and not args.dry_run:
        notification = notify_robert(Path(args.send_helper), state_dir, new_items)

    summary = {
        "ok": True,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "due_count": len(items),
        "recorded": recorded,
        "skipped_existing": skipped_existing,
        "actions": action_results,
        "notification": notification,
        "dry_run": bool(args.dry_run),
        "items": items,
    }
    if not args.dry_run:
        write_runner_state(state_dir / "task-flow-due-runner-last.json", summary)
    print(json.dumps(summary, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
