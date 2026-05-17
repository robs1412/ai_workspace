#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import shared_task_flow


DEFAULT_RECORDER = Path("/Users/werkstatt/ai_workspace/scripts/task_flow_mysql_recorder.php")
DEFAULT_STATE = Path("/Users/admin/.task-flow-launch/state")
DEFAULT_SEND_HELPER = Path("/Users/admin/.frank-launch/runtime/scripts/send_frank_email.py")
DEFAULT_WATCHDOG = Path("/Users/werkstatt/ai_workspace/scripts/automation_health_watchdog.py")
DEFAULT_WORKSPACEBOARD_URL = "http://127.0.0.1:17878"
DEFAULT_PHP_CANDIDATES = (
    "/usr/local/bin/php",
    "/usr/local/opt/php@8.1/bin/php",
    "/opt/homebrew/bin/php",
    "/usr/bin/php",
)
DMYTRO_EMAIL = "dmytro.klymentiev@kovaldistillery.com"
ROBERT_EMAIL = "robert@kovaldistillery.com"


def resolve_php() -> str:
    configured = os.environ.get("PHP_BIN", "").strip()
    if configured:
        return configured
    found = shutil.which("php")
    if found:
        return found
    for candidate in DEFAULT_PHP_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    return "php"


def load_due(recorder: Path, limit: int) -> dict:
    result = subprocess.run(
        [resolve_php(), str(recorder), "due", str(limit)],
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


def existing_handoff_keys(path: Path) -> set[str]:
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
        key = str(row.get("handoff_key") or "").strip()
        if key:
            keys.add(key)
    return keys


def workspace_for_due_item(item: dict) -> str:
    text = " ".join([
        str(item.get("owner_lane") or ""),
        str(item.get("responsible_worker_or_persona") or ""),
        str(item.get("ops_portal_or_domain_task") or ""),
        str(item.get("scheduled_action") or ""),
        str(item.get("next_update") or ""),
    ]).lower()
    if any(token in text for token in ["portal", "crm", "sample request", "barrel"]):
        return "portal"
    if any(token in text for token in ["phplist", "lists", "mailgun", "campaign"]):
        return "lists"
    if any(token in text for token in ["salesreport", "sales report"]):
        return "salesreport"
    if any(token in text for token in ["bid", "qbo", "quickbooks", "finance", "naomi"]):
        return "bid"
    if any(token in text for token in ["ops task", "ops ", "shift", "calendar"]):
        return "ops"
    return "ai"


def post_json(url: str, payload: dict, timeout: int = 20) -> dict:
    data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Workspaceboard API returned HTTP {error.code}: {body[:500]}") from error
    parsed = json.loads(body)
    if not isinstance(parsed, dict) or parsed.get("ok") is not True:
        raise RuntimeError(f"Workspaceboard API did not return ok=true: {body[:500]}")
    return parsed


def build_worker_handoff_message(items: list[dict]) -> str:
    lines = [
        "Task Flow due-worker handoff.",
        "",
        "Process the due Task Flow item(s) below without waiting for Robert unless a real auth/security/human approval blocker remains.",
        "For each item: verify source state first, do the required worker action, update Task Flow with completed proof, blocked exact blocker, or waiting with next check, and return a concise proof/blocker readback.",
        "Do not expose secrets or raw mailbox bodies. Do not send external mail unless the underlying item already authorizes that send path.",
        "",
    ]
    for index, item in enumerate(items, 1):
        lines.extend([
            f"{index}. key: {item.get('dedupe_key') or ''}",
            f"   owner: {item.get('owner_lane') or ''}",
            f"   worker/persona: {item.get('responsible_worker_or_persona') or ''}",
            f"   due: {item.get('due_or_trigger') or ''}",
            f"   task/domain: {item.get('ops_portal_or_domain_task') or ''}",
            f"   scheduled action: {item.get('scheduled_action') or ''}",
            f"   next update: {item.get('next_update') or ''}",
            "",
        ])
    return "\n".join(lines).rstrip()


def record_routed_packet(recorder: Path, item: dict, session_id: str, due_or_trigger: str) -> dict:
    packet = shared_task_flow.build_packet(
        source_ref=item.get("source_ref") or item.get("dedupe_key") or "",
        dedupe_key=item.get("dedupe_key") or "",
        intake_channel="task-flow-due",
        requester="task-flow-reminder",
        owner_lane=item.get("owner_lane") or "",
        responsible_worker_or_persona=item.get("responsible_worker_or_persona") or "",
        workspaceboard_session=session_id,
        ops_portal_or_domain_task=item.get("ops_portal_or_domain_task") or "",
        status="routed",
        due_or_trigger=due_or_trigger,
        scheduled_action=item.get("scheduled_action") or "",
        calendar_event=item.get("calendar_event") or "",
        verification_readback=f"task_flow_due_runner_routed_visible_worker:{session_id}",
        next_update=f"Visible worker {session_id} must return owner-visible proof, one exact blocker, or a future next check.",
    )
    result = subprocess.run(
        [resolve_php(), str(recorder), "record"],
        input=json.dumps({"event": "task_flow_due_worker_routed", "packet": packet}, ensure_ascii=True),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )
    return json.loads(result.stdout)


def route_due_items_to_worker(recorder: Path, state_dir: Path, items: list[dict], dry_run: bool = False) -> dict:
    route_candidates = [item for item in items if isinstance(item, dict) and item.get("dedupe_key")]
    if not route_candidates:
        return {"ok": True, "routed": False, "reason": "no_due_items", "items": []}

    handoff_log = state_dir / "task-flow-worker-handoffs.jsonl"
    seen_handoffs = existing_handoff_keys(handoff_log)
    pending = [item for item in route_candidates if reminder_key(item) not in seen_handoffs]
    if not pending:
        return {"ok": True, "routed": False, "reason": "all_due_items_already_handed_off", "items": []}

    grouped: dict[str, list[dict]] = {}
    for item in pending:
        grouped.setdefault(workspace_for_due_item(item), []).append(item)

    api_base = os.environ.get("WORKSPACEBOARD_URL", DEFAULT_WORKSPACEBOARD_URL).rstrip("/")
    routed: list[dict] = []
    for workspace, group in grouped.items():
        title = f"Task Flow due worker {time.strftime('%Y-%m-%d %H:%M')} {workspace}"
        message = build_worker_handoff_message(group)
        if dry_run:
            routed.append({"workspace": workspace, "dry_run": True, "items": [item.get("dedupe_key") for item in group]})
            continue
        created = post_json(f"{api_base}/api/session/create", {
            "workspace": workspace,
            "mode": "codex",
            "title": title,
        })
        session = created.get("session") if isinstance(created.get("session"), dict) else {}
        session_id = str(session.get("id") or "").strip()
        if not session_id:
            raise RuntimeError("Workspaceboard session create succeeded without a session id.")
        delivery = post_json(f"{api_base}/api/session-message", {
            "session_id": session_id,
            "message": message,
            "wait_ms": 1000,
        }, timeout=30)
        next_check_epoch = int(time.time()) + 1800
        next_check = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(next_check_epoch))
        recorded_packets = []
        for item in group:
            recorded_packets.append(record_routed_packet(recorder, item, session_id, next_check))
            row = {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "event": "worker_handoff_routed",
                "handoff_key": reminder_key(item),
                "dedupe_key": item.get("dedupe_key") or "",
                "workspace": workspace,
                "session_id": session_id,
            }
            handoff_log.parent.mkdir(parents=True, exist_ok=True)
            with handoff_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            handoff_log.chmod(0o600)
            seen_handoffs.add(reminder_key(item))
        routed.append({
            "workspace": workspace,
            "session_id": session_id,
            "items": [item.get("dedupe_key") for item in group],
            "prompt_delivery": delivery.get("prompt_delivery", {}),
            "recorded_packets": recorded_packets,
        })
    return {"ok": True, "routed": bool(routed), "items": routed}


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


def item_truthy(item: dict, *keys: str) -> bool:
    for key in keys:
        value = str(item.get(key) or "").strip().lower()
        if value in {"1", "true", "yes", "y", "owner-visible", "owner_visible", "email"}:
            return True
    return False


def should_send_owner_due_email(item: dict) -> bool:
    if not isinstance(item, dict):
        return False
    if item_truthy(item, "notify_robert", "owner_visible_reminder", "send_owner_reminder"):
        return True
    output = str(item.get("output_channel") or item.get("completion_output_channel") or "").strip().lower()
    if output in {"email", "owner-email", "owner_visible_email"} and item_truthy(item, "email_due_notice"):
        return True
    text = " ".join([
        str(item.get("owner_lane") or ""),
        str(item.get("responsible_worker_or_persona") or ""),
        str(item.get("scheduled_action") or ""),
        str(item.get("next_update") or ""),
    ]).lower()
    if "robert" not in text:
        return False
    if any(marker in text for marker in [
        "task manager",
        "code/git manager",
        "security guard",
        "workspaceboard reliability",
        "pseudo-flow",
        "review-ready without proof",
        "visible worker",
    ]):
        return False
    return any(marker in text for marker in ["decision", "approve", "approval", "owner question", "exact blocker"])


def notify_robert(send_helper: Path, state_dir: Path, items: list[dict]) -> dict:
    owner_visible_items = [item for item in items if should_send_owner_due_email(item)]
    if not owner_visible_items:
        reason = "no_owner_visible_due_items" if items else "no_new_items"
        return {"sent": False, "reason": reason, "suppressed": len(items)}
    if not items:
        return {"sent": False, "reason": "no_new_items"}
    body_path = state_dir / f"task-flow-reminder-{int(time.time())}.txt"
    write_notification_body(body_path, owner_visible_items)
    subject = "Task Flow Reminder: due item" if len(owner_visible_items) == 1 else f"Task Flow Reminder: {len(owner_visible_items)} due items"
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
        "suppressed": len(items) - len(owner_visible_items),
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


def run_automation_watchdog(script: Path, dry_run: bool = False) -> dict:
    if not script.exists():
        return {"ok": False, "reason": "watchdog_script_missing", "path": str(script)}
    args = ["python3", str(script)]
    if dry_run:
        args.append("--dry-run")
    try:
        result = subprocess.run(
            args,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=150,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": "watchdog_timeout", "path": str(script)}
    payload = {}
    if result.stdout.strip():
        try:
            parsed = json.loads(result.stdout)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = {}
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "path": str(script),
        "summary": {
            "ok": payload.get("ok"),
            "failures": payload.get("failures", []),
            "morning_digest": payload.get("morning_digest", {}),
        },
        "stderr": result.stderr.strip()[-800:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check due task-flow reminders and record wake events.")
    parser.add_argument("--recorder", default=str(DEFAULT_RECORDER))
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE))
    parser.add_argument("--send-helper", default=str(DEFAULT_SEND_HELPER))
    parser.add_argument("--watchdog", default=str(DEFAULT_WATCHDOG))
    parser.add_argument("--run-watchdog", action="store_true", default=True)
    parser.add_argument("--no-watchdog", action="store_false", dest="run_watchdog")
    parser.add_argument("--notify-robert", action="store_true")
    parser.add_argument("--route-worker", action="store_true", default=True)
    parser.add_argument("--no-route-worker", action="store_false", dest="route_worker")
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
    reminder_items: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = reminder_key(item)
        if key in seen:
            skipped_existing += 1
            reminder_items.append(item)
            continue
        packet = packet_from_due_item(item)
        reminder_items.append(item)
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

    worker_handoff = {"ok": True, "routed": False, "reason": "route_worker_disabled", "items": []}
    if args.route_worker:
        worker_handoff = route_due_items_to_worker(recorder, state_dir, reminder_items, dry_run=args.dry_run)

    notification = {"sent": False, "reason": "not_requested"}
    if args.notify_robert and not args.dry_run:
        notification = notify_robert(Path(args.send_helper), state_dir, new_items)

    watchdog = {"ok": True, "skipped": True, "reason": "disabled"}
    if args.run_watchdog:
        watchdog = run_automation_watchdog(Path(args.watchdog), dry_run=args.dry_run)

    summary = {
        "ok": True,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "due_count": len(items),
        "recorded": recorded,
        "skipped_existing": skipped_existing,
        "actions": action_results,
        "worker_handoff": worker_handoff,
        "watchdog": watchdog,
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
