#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


BUNDLE_DIR = Path(__file__).resolve().parent
AI_ROOT = Path("/Users/werkstatt/ai_workspace")
DEFAULT_ALLOWLIST = BUNDLE_DIR / "chat-readback-allowlist.json"
DEFAULT_EVENTS = AI_ROOT / "nationaloutreach/runtime/google-chat-watch-events.jsonl"
DEFAULT_STATE = AI_ROOT / "nationaloutreach/runtime/google-chat-task-router-state.json"
DEFAULT_LOG = AI_ROOT / "nationaloutreach/runtime/google-chat-task-router-log.jsonl"
DEFAULT_API_BASE = "http://127.0.0.1:17878"
DEFAULT_IGNORE_SENDERS = {"users/115726766459954580176"}

_CHAT_SEND_SPEC = importlib.util.spec_from_file_location("chat_send_helper", BUNDLE_DIR / "chat-send.py")
if _CHAT_SEND_SPEC is None or _CHAT_SEND_SPEC.loader is None:
    raise RuntimeError("chat-send.py helper could not be loaded")
_CHAT_SEND = importlib.util.module_from_spec(_CHAT_SEND_SPEC)
_CHAT_SEND_SPEC.loader.exec_module(_CHAT_SEND)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route approved Google Chat tasks through AI Manager and Task Manager.")
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST))
    parser.add_argument("--events", default=str(DEFAULT_EVENTS))
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--log", default=str(DEFAULT_LOG))
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--seed-existing", action="store_true")
    parser.add_argument("--route-all", action="store_true", help="Route every non-ignored inbound event, including short acknowledgements.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"processed_message_names": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("name"):
            rows.append(row)
    return rows


def post_json(url: str, payload: dict, timeout: int = 60) -> dict:
    data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"message": body}
        parsed["ok"] = False
        parsed["status"] = exc.code
        return parsed


def build_target_map(allowlist_path: Path) -> dict[str, dict]:
    records = {}
    allowlist = _CHAT_SEND.load_json(allowlist_path)
    for record in {item["space"]: item for item in _CHAT_SEND.allowed_targets(allowlist).values()}.values():
        records[record["space"]] = record
    return records


def actionably_tasklike(text: str) -> bool:
    clean = " ".join(text.lower().split())
    if len(clean) < 12:
        return False
    if clean in {"ok thanks", "thanks", "thank you", "got it", "received", "test", "testing"}:
        return False
    discussion_prefixes = (
        "are there ",
        "is there ",
        "what ",
        "why ",
        "how ",
        "should ",
        "do we ",
        "can we ",
        "could we ",
        "would it ",
        "your take",
        "thoughts",
    )
    explicit_start_markers = (
        "please start",
        "start a worker",
        "start the worker",
        "start work",
        "route this",
        "route it",
        "create a task",
        "open a worker",
        "approve",
    )
    if clean.endswith("?") and clean.startswith(discussion_prefixes) and not any(marker in clean for marker in explicit_start_markers):
        return False
    broad_discovery_markers = (
        "are there ",
        "is there ",
        "do we have ",
        "should we ",
        "may need ",
        "might need ",
        "need a worker",
        "tasks we should",
        "things we should",
        "anything ",
        "which ",
        "what ",
        "look at that may",
        "look at that might",
    )
    if any(marker in clean for marker in broad_discovery_markers):
        return False
    work_markers = [
        "please",
        "start",
        "check",
        "look",
        "fix",
        "add",
        "route",
        "create",
        "send",
        "reply",
        "work on",
        "do ",
        "setup",
        "set up",
        "investigate",
        "review",
        "implement",
        "update",
        "change",
        "make ",
        "build",
    ]
    if any(marker in clean for marker in work_markers):
        return True
    if clean.startswith("can you ") and any(marker in clean for marker in ["start", "check", "fix", "add", "create", "send", "reply", "route", "work on", "set up", "setup"]):
        return True
    return False


def approval_intent(text: str) -> str:
    clean = " ".join(text.lower().split())
    approve = {
        "approve",
        "approved",
        "yes",
        "yes approve",
        "start",
        "start it",
        "go",
        "go ahead",
        "do it",
        "route it",
        "approved start",
    }
    decline = {"decline", "no", "hold", "cancel", "do not start", "don't start", "skip"}
    if clean in approve:
        return "approve"
    if clean in decline:
        return "decline"
    return ""


def ai_manager_input_message(event: dict) -> str:
    return "\n".join(
        [
            "Google Chat task intake for AI Manager.",
            f"Chat target: {event.get('target_label', '')} ({event.get('space', '')})",
            f"Chat message id: {event.get('name', '')}",
            f"Chat create time: {event.get('createTime', '')}",
            f"Chat sender: {event.get('senderName', '')}",
            "",
            "Verbatim Chat message:",
            str(event.get("text") or "").strip(),
        ]
    )


def task_flow_record(event: str, packet: dict) -> dict:
    script = AI_ROOT / "scripts/task_flow_mysql_recorder.php"
    if not script.exists():
        return {"ok": False, "message": "task_flow_recorder_missing"}
    payload = json.dumps({"event": event, "packet": packet}, ensure_ascii=True)
    result = subprocess.run(
        ["php", str(script), "record"],
        input=payload,
        text=True,
        capture_output=True,
        timeout=12,
        check=False,
    )
    if result.returncode != 0:
        return {"ok": False, "message": (result.stderr or result.stdout).strip()[:500]}
    try:
        return json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "message": "task_flow_recorder_non_json"}


def pending_dedupe_key(event: dict) -> str:
    safe = "".join(ch if ch.isalnum() else "-" for ch in str(event.get("name") or "chat-message")).strip("-").lower()
    return f"chat-task-approval-{safe[-80:]}"


def record_pending_task(event: dict, daily_payload: dict) -> dict:
    dedupe_key = pending_dedupe_key(event)
    packet = {
        "dedupe_key": dedupe_key,
        "source_ref": f"google-chat:{event.get('space', '')}:{event.get('name', '')}",
        "intake_channel": "google-chat:approved-allowlist",
        "requester": "Robert",
        "owner_lane": "task-manager",
        "responsible_worker_or_persona": "AI Manager -> Task Manager",
        "ops_portal_or_domain_task": dedupe_key,
        "status": "waiting",
        "due_or_trigger": "Awaiting Robert Chat approval before worker start",
        "scheduled_action": "Google Chat task pending approval",
        "requested_deliverable": str(event.get("text") or "").strip()[:1000],
        "source_links": f"Google Chat message {event.get('name', '')}; AI Manager input #{daily_payload.get('input_id') or 'unknown'}",
        "approval_gates": "Do not create or focus a worker session until Robert replies with explicit approval in the same Chat target.",
        "verification_readback": "Captured from Google Chat; no worker started pending approval.",
        "papers_projection": "not_applicable_internal_chat_task_intake",
        "next_update": "Reply Approve to start a Task Manager route, or Decline/Hold to keep it parked.",
    }
    result = task_flow_record("google_chat_task_captured_pending_approval", packet)
    return {"dedupe_key": dedupe_key, "record": result}


def task_manager_message(event: dict, daily_payload: dict) -> str:
    feedback = daily_payload.get("feedback_push") if isinstance(daily_payload.get("feedback_push"), dict) else {}
    finish = feedback.get("finish_contract") if isinstance(feedback.get("finish_contract"), dict) else {}
    capacity = feedback.get("session_capacity") if isinstance(feedback.get("session_capacity"), dict) else {}
    return "\n".join(
        [
            "AI_MANAGER_PHONE_INPUT",
            "Signed-in AI Manager owner: Robert (workspaceboard user_id unknown).",
            "Treat this as Robert communicating with Robert's AI Manager through approved Google Chat.",
            "Use Task Flow as source of truth for routed/scheduled work.",
            "Hard boundary: AI Manager must not implement substantive code, OPS, Portal, mailbox, finance, deploy, or data-mutation work in the manager lane. For substantive work, hand off to Task Manager and have Task Manager create or focus a visible worker session in the correct workspace.",
            "Return route proof only: worker/session id plus expected proof, first next-check, or one route blocker.",
            "",
            "Google Chat source:",
            f"- target: {event.get('target_label', '')}",
            f"- space: {event.get('space', '')}",
            f"- message id: {event.get('name', '')}",
            f"- create time: {event.get('createTime', '')}",
            "",
            "Verbatim Chat message:",
            str(event.get("text") or "").strip(),
            "",
            "FEEDBACK_PUSH_CONTRACT",
            f"Classification: {feedback.get('kind') or 'create_new_focused_item'}.",
            f"Related Task Flow/domain item: {feedback.get('related_taskflow_key') or 'none matched; create one focused item if substantive'}.",
            f"Responsible worker/persona: {feedback.get('responsible_worker_or_persona') or 'Task Manager -> correct focused worker/persona'}.",
            f"Owner lane: {feedback.get('owner_lane') or 'task-manager'}.",
            f"Route mode: {feedback.get('route_mode') or 'route_or_focus_one_worker_when_safe'}.",
            f"Session capacity: {int(capacity.get('active_sessions') or 0)}/{int(capacity.get('threshold') or 0)} active supervised sessions; throttle exceeded: {'yes' if capacity.get('exceeded') else 'no'}.",
            f"Requested deliverable: {finish.get('requested_deliverable') or 'apply feedback or create focused Task Flow/domain item'}.",
            "Output channel: Google Chat receipt to Robert plus Task Flow/Workspaceboard proof.",
            f"Proof required: {finish.get('proof_required') or 'Task Flow key/domain task/session id plus completion proof, blocker, or owner question'}.",
            f"Due/next update: {finish.get('due_or_next_update') or 'immediate capture proof, then worker finish contract'}.",
            f"Escalation path: {finish.get('escalation_path') or 'Task Manager capture repair before asking Robert'}.",
        ]
    )


def receipt_text(event: dict, daily_payload: dict, task_payload: dict) -> str:
    receipt = task_payload.get("route_receipt") if isinstance(task_payload.get("route_receipt"), dict) else {}
    if not task_payload.get("ok"):
        return (
            "I captured this in AI Manager, but Task Manager routing blocked before a worker receipt.\n"
            f"AI Manager input: #{daily_payload.get('input_id') or 'unknown'}\n"
            f"Blocker: {task_payload.get('message') or 'unknown route failure'}"
        )
    route_state = receipt.get("route_state") or "accepted-no-worker"
    session_id = receipt.get("worker_session_id") or (task_payload.get("target_session") or {}).get("id") or ""
    task_flow = receipt.get("task_flow") if isinstance(receipt.get("task_flow"), dict) else {}
    packet_id = task_flow.get("packet_id") or receipt.get("packet_id") or ""
    first_check = receipt.get("first_next_check_at") or ""
    blocker_check = receipt.get("blocker_check_at") or ""
    if route_state == "blocked-exact":
        return (
            "Captured, but routing is blocked.\n"
            f"AI Manager input: #{daily_payload.get('input_id') or 'unknown'}\n"
            f"Task Flow: {packet_id or 'pending'}\n"
            f"Blocker: {receipt.get('blocker_text') or 'Task Manager returned a route blocker.'}"
        )
    if session_id:
        return (
            "Accepted and handed to Task Manager.\n"
            f"Worker session: {session_id}\n"
            f"Task Flow: {packet_id or 'recorded'}\n"
            f"First check: {first_check or 'about 2 minutes'}\n"
            f"ETA: initial readback in about 2 minutes; blocker/completion checkpoint by {blocker_check or 'about 5 minutes'}."
        )
    return (
        "Accepted by AI Manager and handed to Task Manager.\n"
        f"AI Manager input: #{daily_payload.get('input_id') or 'unknown'}\n"
        f"Task Flow: {packet_id or 'pending'}\n"
        "Worker session: pending\n"
        f"ETA: first route check {first_check or 'about 2 minutes'}."
    )


def approval_request_text(event: dict, daily_payload: dict, pending_packet: dict) -> str:
    return (
        "Captured, pending approval before starting a worker.\n"
        f"AI Manager input: #{daily_payload.get('input_id') or 'unknown'}\n"
        f"Task Flow: {pending_packet.get('dedupe_key') or 'recorded'}\n"
        "Reply Approve to start the Task Manager handoff, or Hold/Decline to leave it parked.\n"
        "No worker session has been started yet."
    )


def status_or_discovery_question(text: str) -> bool:
    clean = " ".join(text.lower().split())
    markers = (
        "how are we doing",
        "are there",
        "is there",
        "do we have",
        "what's the status",
        "what is the status",
        "status",
        "overdue",
        "ops tasks",
        "/ops",
        "task flow",
        "workspaceboard",
        "what should",
        "should we",
    )
    return any(marker in clean for marker in markers)


def followup_status_question(text: str) -> bool:
    clean = " ".join(text.lower().split())
    markers = (
        "did this complete",
        "did it complete",
        "is this done",
        "is it done",
        "what happened",
        "any update",
        "status on this",
        "how did it go",
        "complete?",
        "done?",
    )
    return any(marker in clean for marker in markers)


def discussion_text(event: dict) -> str:
    text = str(event.get("text") or "")
    if status_or_discovery_question(text):
        return (
            "Let me look. I should be able to get back to you in about 1-2 minutes.\n"
            "No worker is being started for this lookup."
        )
    return (
        "I saw this. I can discuss it here without starting a worker.\n"
        "If this turns into work that needs repo/OPS/Portal/mailbox action, I will ask for approval before starting a Task Manager worker."
    )


def task_flow_report(api_base: str) -> dict:
    return post_json(
        f"{api_base.rstrip('/')}/api/task-flow/report?limit=300",
        {},
        timeout=30,
    )


def task_flow_report_get(api_base: str) -> dict:
    url = f"{api_base.rstrip('/')}/api/task-flow/report?limit=300"
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def status_lookup_reply(args: argparse.Namespace, event: dict) -> str:
    text = str(event.get("text") or "").lower()
    try:
        report = task_flow_report_get(args.api_base)
    except Exception as exc:
        return f"I looked, but the Task Flow status lookup failed: {exc}. No worker was started."
    items = report.get("items") if isinstance(report.get("items"), list) else []
    if "/ops" in text or "ops" in text:
        matches = [
            item for item in items
            if "ops" in " ".join(str(item.get(key) or "").lower() for key in [
                "owner_lane",
                "responsible_worker_or_persona",
                "ops_portal_or_domain_task",
                "scheduled_action",
                "source_links",
            ])
        ]
        if not matches:
            return "I looked at Task Flow and do not see visible OPS-related open items needing a worker right now. No worker was started."
        blocked = [item for item in matches if str(item.get("effective_status") or item.get("status") or "").lower() == "blocked"]
        working = [item for item in matches if str(item.get("effective_status") or item.get("status") or "").lower() == "working"]
        waiting = [item for item in matches if str(item.get("effective_status") or item.get("status") or "").lower() == "waiting"]
        first = matches[0]
        label = str(first.get("scheduled_action") or first.get("ops_portal_or_domain_task") or first.get("dedupe_key") or "OPS item").strip()
        session = str(first.get("workspaceboard_session") or "").strip()
        blocker = str(first.get("next_update") or first.get("verification_readback") or "").strip()
        lines = [
            f"I looked at Task Flow: {len(matches)} OPS-related visible item(s).",
            f"Status mix: {len(blocked)} blocked, {len(working)} working, {len(waiting)} waiting.",
            f"Top item: {label[:180]}",
        ]
        if session:
            lines.append(f"Session: {session}.")
        if blocker:
            lines.append(f"Current note: {blocker[:260]}")
        lines.append("No worker was started.")
        return "\n".join(lines)
    visible = int((report.get("totals") or {}).get("visible_packets") or len(items))
    open_count = int((report.get("totals") or {}).get("open_items_shown") or len(items))
    closeout = int((report.get("totals") or {}).get("closeout_issues_shown") or 0)
    return f"I looked at Task Flow: {open_count} open visible item(s), {closeout} closeout issue(s), {visible} visible packet(s) in the current report. No worker was started."


def session_status_reply(args: argparse.Namespace, session_id: str, taskflow_key: str = "") -> str:
    try:
        url = f"{args.api_base.rstrip('/')}/api/session-history?session_id={urllib.parse.quote(session_id)}"
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return f"I tried to check worker session {session_id}, but the readback failed: {exc}."
    session = payload.get("session") if isinstance(payload.get("session"), dict) else {}
    current = payload.get("current_work_state") if isinstance(payload.get("current_work_state"), dict) else {}
    state = str(current.get("work_state") or session.get("status") or "").strip()
    proof = str(current.get("proof_marker") or current.get("summary") or "").strip()
    history = str(payload.get("history") or payload.get("transcript") or "").strip()
    lower = "\n".join([state, proof, history[-4000:]]).lower()
    completed = any(marker in lower for marker in ["closed_with_proof", "completed", "sent the", "proof marker"])
    if completed:
        lines = [f"Yes. Worker session {session_id} is complete/closed with proof."]
    else:
        lines = [f"Not complete yet. Worker session {session_id} is currently {state or 'unknown'}."]
    if taskflow_key:
        lines.append(f"Task Flow: {taskflow_key}.")
    if proof:
        lines.append(f"Proof: {proof[:320]}")
    elif history:
        tail = " ".join(history.splitlines()[-8:]).strip()
        if tail:
            lines.append(f"Latest readback: {tail[:320]}")
    return "\n".join(lines)


def declined_text(pending: dict) -> str:
    packet = pending.get("pending_packet") or {}
    return (
        "Held. I will not start a worker for that Chat task.\n"
        f"Task Flow: {packet.get('dedupe_key') or 'pending approval record'}"
    )


def route_event(args: argparse.Namespace, event: dict, target_map: dict[str, dict]) -> dict:
    daily_payload = post_json(
        f"{args.api_base.rstrip('/')}/api/ai-manager/daily-input",
        {
            "message": ai_manager_input_message(event),
            "user_label": "Robert",
        },
    )
    if not daily_payload.get("ok"):
        raise RuntimeError(f"AI Manager daily-input capture failed: {daily_payload.get('message') or daily_payload}")
    feedback = daily_payload.get("feedback_push") if isinstance(daily_payload.get("feedback_push"), dict) else None
    task_payload = post_json(
        f"{args.api_base.rstrip('/')}/api/task-manager/message",
        {
            "message": task_manager_message(event, daily_payload),
            "feedback_push": feedback,
            "ai_manager_input_uuid": daily_payload.get("input_uuid") or "",
            "ai_manager_input_id": daily_payload.get("input_id") or None,
            "source_path": f"google-chat:{event.get('space', '')}:{event.get('name', '')}",
            "user_label": "Robert",
            "wait_ms": 1000,
        },
        timeout=90,
    )
    target = target_map.get(str(event.get("space") or ""))
    if target:
        chat_result = _CHAT_SEND.post_message(_CHAT_SEND.credentials(), target, receipt_text(event, daily_payload, task_payload))
    else:
        chat_result = {"ok": False, "error": "reply_target_not_allowed"}
    return {
        "event_name": event.get("name", ""),
        "event_create_time": event.get("createTime", ""),
        "target_label": event.get("target_label", ""),
        "ai_manager_input": {
            "ok": daily_payload.get("ok"),
            "input_id": daily_payload.get("input_id"),
            "input_uuid": daily_payload.get("input_uuid"),
        },
        "task_manager": {
            "ok": task_payload.get("ok"),
            "route_receipt": task_payload.get("route_receipt"),
            "message": task_payload.get("message", ""),
        },
        "chat_reply": chat_result,
    }


def capture_pending_event(args: argparse.Namespace, event: dict, target_map: dict[str, dict]) -> dict:
    daily_payload = post_json(
        f"{args.api_base.rstrip('/')}/api/ai-manager/daily-input",
        {
            "message": ai_manager_input_message(event),
            "user_label": "Robert",
        },
    )
    if not daily_payload.get("ok"):
        raise RuntimeError(f"AI Manager daily-input capture failed: {daily_payload.get('message') or daily_payload}")
    pending_packet = record_pending_task(event, daily_payload)
    target = target_map.get(str(event.get("space") or ""))
    chat_result = _CHAT_SEND.post_message(_CHAT_SEND.credentials(), target, approval_request_text(event, daily_payload, pending_packet)) if target else {"ok": False, "error": "reply_target_not_allowed"}
    return {
        "event_name": event.get("name", ""),
        "event_create_time": event.get("createTime", ""),
        "target_label": event.get("target_label", ""),
        "pending": True,
        "pending_packet": pending_packet,
        "ai_manager_input": {
            "ok": daily_payload.get("ok"),
            "input_id": daily_payload.get("input_id"),
            "input_uuid": daily_payload.get("input_uuid"),
        },
        "daily_payload": daily_payload,
        "source_event": event,
        "chat_reply": chat_result,
    }


def process_once(args: argparse.Namespace) -> dict:
    state_path = Path(args.state)
    state = load_state(state_path)
    processed = set(state.get("processed_message_names") or [])
    events = read_events(Path(args.events))
    target_map = build_target_map(Path(args.allowlist))
    routed = []
    skipped = 0
    pending_by_space = state.setdefault("pending_by_space", {})
    routed_by_space = state.setdefault("routed_by_space", {})
    for event in events:
        name = str(event.get("name") or "").strip()
        if not name or name in processed:
            continue
        processed.add(name)
        sender = str(event.get("senderName") or "").strip()
        text = str(event.get("text") or "").strip()
        if args.seed_existing:
            skipped += 1
            continue
        if sender in DEFAULT_IGNORE_SENDERS or not text:
            skipped += 1
            continue
        intent = approval_intent(text)
        space = str(event.get("space") or "")
        if followup_status_question(text) and space in routed_by_space:
            latest_route = routed_by_space.get(space) or {}
            session_id = str(latest_route.get("worker_session_id") or "").strip()
            taskflow_key = str(latest_route.get("taskflow_key") or latest_route.get("packet_id") or "").strip()
            target = target_map.get(space)
            chat_result = _CHAT_SEND.post_message(_CHAT_SEND.credentials(), target, session_status_reply(args, session_id, taskflow_key)) if target and session_id else {"ok": False, "error": "no_recent_worker_session"}
            result = {
                "event_name": name,
                "followup_status": True,
                "worker_session_id": session_id,
                "taskflow_key": taskflow_key,
                "chat_reply": chat_result,
            }
            append_jsonl(Path(args.log), result)
            routed.append(result)
            continue
        if intent and space in pending_by_space:
            pending = pending_by_space.pop(space)
            if intent == "decline":
                target = target_map.get(space)
                chat_result = _CHAT_SEND.post_message(_CHAT_SEND.credentials(), target, declined_text(pending)) if target else {"ok": False, "error": "reply_target_not_allowed"}
                result = {
                    "event_name": name,
                    "approval": "decline",
                    "pending_event_name": pending.get("event_name", ""),
                    "chat_reply": chat_result,
                }
            else:
                source_event = pending.get("source_event") if isinstance(pending.get("source_event"), dict) else event
                daily_payload = pending.get("daily_payload") if isinstance(pending.get("daily_payload"), dict) else {}
                if not daily_payload.get("ok"):
                    daily_payload = post_json(
                        f"{args.api_base.rstrip('/')}/api/ai-manager/daily-input",
                        {"message": ai_manager_input_message(source_event), "user_label": "Robert"},
                    )
                task_payload = post_json(
                    f"{args.api_base.rstrip('/')}/api/task-manager/message",
                    {
                        "message": task_manager_message(source_event, daily_payload),
                        "feedback_push": daily_payload.get("feedback_push") if isinstance(daily_payload.get("feedback_push"), dict) else None,
                        "ai_manager_input_uuid": daily_payload.get("input_uuid") or "",
                        "ai_manager_input_id": daily_payload.get("input_id") or None,
                        "source_path": f"google-chat:{source_event.get('space', '')}:{source_event.get('name', '')}",
                        "user_label": "Robert",
                        "wait_ms": 1000,
                    },
                    timeout=90,
                )
                target = target_map.get(space)
                chat_result = _CHAT_SEND.post_message(_CHAT_SEND.credentials(), target, receipt_text(source_event, daily_payload, task_payload)) if target else {"ok": False, "error": "reply_target_not_allowed"}
                result = {
                    "event_name": name,
                    "approval": "approve",
                    "pending_event_name": pending.get("event_name", ""),
                    "task_manager": {
                        "ok": task_payload.get("ok"),
                        "route_receipt": task_payload.get("route_receipt"),
                        "message": task_payload.get("message", ""),
                    },
                    "chat_reply": chat_result,
                }
                receipt = task_payload.get("route_receipt") if isinstance(task_payload.get("route_receipt"), dict) else {}
                task_flow = receipt.get("task_flow") if isinstance(receipt.get("task_flow"), dict) else {}
                routed_by_space[space] = {
                    "worker_session_id": receipt.get("worker_session_id") or "",
                    "taskflow_key": task_flow.get("packet_id") or receipt.get("packet_id") or "",
                    "packet_id": receipt.get("packet_id") or "",
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "source_event_name": source_event.get("name", ""),
                }
            append_jsonl(Path(args.log), result)
            routed.append(result)
            continue
        if not args.route_all and not actionably_tasklike(text):
            if status_or_discovery_question(text) or text.endswith("?"):
                target = target_map.get(space)
                chat_result = _CHAT_SEND.post_message(_CHAT_SEND.credentials(), target, discussion_text(event)) if target else {"ok": False, "error": "reply_target_not_allowed"}
                followup_result = None
                if target and status_or_discovery_question(text):
                    followup_result = _CHAT_SEND.post_message(_CHAT_SEND.credentials(), target, status_lookup_reply(args, event))
                append_jsonl(Path(args.log), {
                    "event_name": name,
                    "discussion_only": True,
                    "chat_reply": chat_result,
                    "followup_reply": followup_result,
                })
            skipped += 1
            continue
        try:
            result = capture_pending_event(args, event, target_map)
            pending_by_space[space] = result
        except Exception as exc:
            result = {"event_name": name, "ok": False, "error": str(exc)}
        append_jsonl(Path(args.log), result)
        routed.append(result)
    state["processed_message_names"] = list(dict.fromkeys(list(processed)))[-1000:]
    state["last_checked_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    state["router"] = "google-chat-ai-manager-task-manager"
    write_json(state_path, state)
    return {"ok": True, "routed_count": len(routed), "skipped_count": skipped, "routed": routed}


def main() -> int:
    args = parse_args()
    while True:
        result = process_once(args)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, sort_keys=True))
        if args.once:
            return 0
        time.sleep(max(1, args.poll_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
