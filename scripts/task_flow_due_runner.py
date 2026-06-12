#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import shared_task_flow


DEFAULT_RECORDER = Path("/Users/werkstatt/ai_workspace/scripts/task_flow_mysql_recorder.php")
DEFAULT_WORKSPACEBOARD_RECORDER = Path("/Users/werkstatt/workspaceboard/scripts/workspaceboard_db_recorder.php")
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
DAEMON_OWNED_DUE_WORKSPACES = {"nationaloutreach"}
SCHEDULER_RETRY_COOLDOWN_SECONDS = 15 * 60
DEFAULT_TMUX_SOCKET = Path(tempfile.gettempdir()) / f"cdxdash-{os.getuid()}" / "tmux.sock"


class FanoutGuard:
    def __init__(
        self,
        state_dir: Path,
        *,
        max_sessions_per_run: int,
        max_sessions_per_source: int,
        max_live_tmux_sessions: int,
        max_load_1m: float,
        tmux_socket: Path,
    ) -> None:
        self.state_dir = state_dir
        self.max_sessions_per_run = max(0, max_sessions_per_run)
        self.max_sessions_per_source = max(1, max_sessions_per_source)
        self.max_live_tmux_sessions = max(0, max_live_tmux_sessions)
        self.max_load_1m = max(0.0, max_load_1m)
        self.tmux_socket = tmux_socket
        self.created_sessions = 0
        self.created_by_source: dict[str, int] = {}
        self.events: list[dict] = []
        self.overload = self._detect_overload()

    def _detect_overload(self) -> dict:
        load_1m = 0.0
        try:
            load_1m = float(os.getloadavg()[0])
        except (AttributeError, OSError, ValueError):
            pass
        live_tmux = count_tmux_sessions(self.tmux_socket)
        reasons: list[str] = []
        if self.max_load_1m and load_1m >= self.max_load_1m:
            reasons.append(f"load_1m {load_1m:.2f} >= {self.max_load_1m:.2f}")
        if self.max_live_tmux_sessions and live_tmux >= self.max_live_tmux_sessions:
            reasons.append(f"live_tmux_sessions {live_tmux} >= {self.max_live_tmux_sessions}")
        return {
            "active": bool(reasons),
            "load_1m": round(load_1m, 2),
            "live_tmux_sessions": live_tmux,
            "max_load_1m": self.max_load_1m,
            "max_live_tmux_sessions": self.max_live_tmux_sessions,
            "reasons": reasons,
        }

    def source_key(self, items: list[dict]) -> str:
        for item in items:
            for field in ("source_ref", "dedupe_key"):
                value = str(item.get(field) or "").strip()
                if value:
                    return value[:180]
        return "unknown-source"

    def can_create(self, items: list[dict], workspace: str, route_kind: str) -> tuple[bool, str]:
        source_key = self.source_key(items)
        active_sessions = sorted({
            str(item.get("workspaceboard_session") or "").strip()
            for item in items
            if str(item.get("workspaceboard_session") or "").strip()
        })
        if active_sessions:
            return False, f"active_workspaceboard_session_exists:{','.join(active_sessions[:3])}"
        if self.overload["active"]:
            return False, "overload_mode:" + "; ".join(self.overload["reasons"])
        if self.max_sessions_per_run and self.created_sessions >= self.max_sessions_per_run:
            return False, f"max_sessions_per_run_reached:{self.max_sessions_per_run}"
        if self.created_by_source.get(source_key, 0) >= self.max_sessions_per_source:
            return False, f"max_sessions_per_source_reached:{self.max_sessions_per_source}:{source_key}"
        return True, "ok"

    def record_created(self, items: list[dict], workspace: str, route_kind: str, session_id: str) -> None:
        source_key = self.source_key(items)
        self.created_sessions += 1
        self.created_by_source[source_key] = self.created_by_source.get(source_key, 0) + 1
        self.events.append({
            "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "event": "worker_session_created",
            "route_kind": route_kind,
            "workspace": workspace,
            "source_key": source_key,
            "session_id": session_id,
            "items": [item.get("dedupe_key") for item in items],
        })

    def record_blocked(self, items: list[dict], workspace: str, route_kind: str, reason: str) -> None:
        self.events.append({
            "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "event": "worker_session_blocked",
            "route_kind": route_kind,
            "workspace": workspace,
            "source_key": self.source_key(items),
            "reason": reason,
            "items": [item.get("dedupe_key") for item in items],
            "overload": self.overload,
        })

    def flush(self) -> None:
        if not self.events:
            return
        path = self.state_dir / "automation-circuit-breakers.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(event, ensure_ascii=True) + "\n")
        path.chmod(0o600)


def count_tmux_sessions(socket: Path) -> int:
    command = ["tmux"]
    if socket:
        command.extend(["-S", str(socket)])
    command.extend(["list-sessions", "-F", "#{session_name}"])
    try:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    except Exception:
        return 0
    if result.returncode != 0:
        return 0
    return len([line for line in result.stdout.splitlines() if line.strip()])


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


def load_task_flow_report(recorder: Path, limit: int, mode: str = "queue") -> dict:
    result = subprocess.run(
        [resolve_php(), str(recorder), "task-flow-report"],
        input=json.dumps({"limit": limit, "mode": mode}, ensure_ascii=True),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise RuntimeError("task-flow report did not return ok=true")
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


def item_recurrence(item: dict) -> dict:
    return item.get("recurrence") if isinstance(item.get("recurrence"), dict) else {}


def is_owner_reply_daily_item(item: dict) -> bool:
    recurrence = item_recurrence(item)
    return str(item.get("recurrence_rule") or recurrence.get("rule") or "").strip() == "owner_reply_daily_repeat"


def next_owner_reply_daily_due(item: dict) -> str:
    now = datetime.now()
    due_text = str(item.get("due_or_trigger") or "")
    try:
        due = datetime.strptime(due_text[:19], "%Y-%m-%d %H:%M:%S")
        candidate = datetime.combine(now.date(), due.time())
    except ValueError:
        candidate = now
    while candidate <= now:
        candidate += timedelta(days=1)
    return candidate.strftime("%Y-%m-%d %H:%M:%S")


def scheduler_bridge_key(item: dict) -> str:
    return "|".join([
        "scheduler-bridge",
        str(item.get("dedupe_key") or ""),
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


def existing_handoffs(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    handoffs: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        key = str(row.get("handoff_key") or "").strip()
        if key:
            handoffs[key] = row
    return handoffs


def handoff_is_recent(row: dict, cooldown_seconds: int) -> bool:
    logged_at = str(row.get("logged_at") or "").strip()
    if not logged_at:
        return False
    try:
        logged = datetime.strptime(logged_at, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return False
    age_seconds = time.time() - logged.timestamp()
    return age_seconds < cooldown_seconds


def workspace_for_task_flow_item(item: dict) -> str:
    owner_lane = str(item.get("owner_lane") or "").strip().lower()
    responsible = str(item.get("responsible_worker_or_persona") or "").strip().lower()
    if responsible in {
        "workspaceboard", "ai", "ops", "portal", "lists", "salesreport",
        "bid", "forge", "frank", "avignon", "nationaloutreach", "asher", "venetia",
    }:
        return responsible
    scheduled_action = str(item.get("scheduled_action") or "").strip().lower()
    if scheduled_action.startswith("respond to owner reply:") and responsible in {
        "vanessa.sterling@kovaldistillery.com",
        "outreach-coordinator",
        "national outreach",
    }:
        return "nationaloutreach"
    if owner_lane in {
        "workspaceboard", "ai", "ops", "portal", "lists", "salesreport",
        "bid", "forge", "frank", "avignon", "nationaloutreach", "asher", "venetia",
    }:
        return owner_lane
    if owner_lane in {"marketing-manager", "communications-manager", "email-coordinator"}:
        return "forge"
    text = " ".join([
        owner_lane,
        str(item.get("responsible_worker_or_persona") or ""),
        str(item.get("ops_portal_or_domain_task") or ""),
        str(item.get("scheduled_action") or ""),
        str(item.get("next_update") or ""),
        str(item.get("source_ref") or ""),
    ]).lower()
    if any(token in text for token in [
        "workspaceboard", "task manager", "decision driver", "summary worker",
        "security guard", "code/git manager", "code and git manager", "ai manager",
    ]):
        return "workspaceboard"
    if any(token in text for token in ["national outreach", "nationaloutreach", "vanessa", "outreach-coordinator"]):
        return "nationaloutreach"
    if any(token in text for token in ["frank", "robert@kovaldistillery.com"]):
        return "frank"
    if any(token in text for token in ["avignon", "sonat"]):
        return "avignon"
    if any(token in text for token in ["portal", "crm", "sample request", "barrel"]):
        return "portal"
    if any(token in text for token in [
        "forge",
        "communications planner",
        "weekly highlights",
        "social posting",
        "marketing-manager",
        "communications-manager",
        "email coordinator",
        "channel / source system",
        "square direct send",
    ]):
        return "forge"
    if any(token in text for token in ["phplist", "lists", "mailgun", "campaign"]):
        return "lists"
    if any(token in text for token in ["salesreport", "sales report"]):
        return "salesreport"
    if any(token in text for token in ["bid", "qbo", "quickbooks", "finance", "naomi"]):
        return "bid"
    if any(token in text for token in ["ops task", "ops ", "shift", "calendar"]):
        return "ops"
    if any(token in text for token in ["forge", "campaign work"]):
        return "forge"
    return "ai"


def create_worker_route_session(api_base: str, workspace: str, title: str, message: str) -> tuple[str, dict]:
    attachments = create_scheduler_bridge_attachment_group(api_base, workspace, title, message)
    created = post_json(f"{api_base}/api/session/create", {
        "workspace": workspace,
        "mode": "codex",
        "title": title,
        "attachment_group_id": attachments.get("id") or "",
    })
    session = created.get("session") if isinstance(created.get("session"), dict) else {}
    session_id = str(session.get("id") or "").strip()
    if not session_id:
        raise RuntimeError("Workspaceboard session create succeeded without a session id.")
    return session_id, attachments


def deliver_worker_route_message(api_base: str, session_id: str, attachment_group_id: str, message: str) -> dict:
    return post_json(f"{api_base}/api/session-message", {
        "session_id": session_id,
        "message": message,
        "attachment_group_id": attachment_group_id,
        "wait_ms": 250,
    }, timeout=30)


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


def post_multipart(url: str, fields: dict[str, str], files: list[tuple[str, str, bytes, str]], timeout: int = 20) -> dict:
    boundary = f"----WorkspaceboardBoundary{uuid.uuid4().hex}"
    body = bytearray()

    def add_text(value: str) -> None:
        body.extend(value.encode("utf-8"))

    for key, value in fields.items():
        add_text(f"--{boundary}\r\n")
        add_text(f'Content-Disposition: form-data; name="{key}"\r\n\r\n')
        add_text(f"{value}\r\n")
    for field_name, filename, content, content_type in files:
        safe_filename = filename.replace('"', '%22')
        add_text(f"--{boundary}\r\n")
        add_text(f'Content-Disposition: form-data; name="{field_name}"; filename="{safe_filename}"\r\n')
        add_text(f"Content-Type: {content_type}\r\n\r\n")
        body.extend(content)
        add_text("\r\n")
    add_text(f"--{boundary}--\r\n")
    request = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Workspaceboard API returned HTTP {error.code}: {response_body[:500]}") from error
    parsed = json.loads(response_body)
    if not isinstance(parsed, dict) or parsed.get("ok") is not True:
        raise RuntimeError(f"Workspaceboard API did not return ok=true: {response_body[:500]}")
    return parsed


def create_scheduler_bridge_attachment_group(api_base: str, workspace: str, title: str, message: str) -> dict:
    attachment_name = f"scheduler-bridge-{workspace}-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    attachment_body = "\n".join([
        "Task Flow scheduler-bridge handoff packet.",
        "",
        f"Workspace: {workspace}",
        f"Title: {title}",
        "",
        message,
        "",
    ])
    response = post_multipart(
        f"{api_base}/api/attachments",
        {"purpose": "task-flow-scheduler-bridge"},
        [("files", attachment_name, attachment_body.encode("utf-8"), "text/plain; charset=utf-8")],
    )
    attachments = response.get("attachments") if isinstance(response.get("attachments"), dict) else {}
    attachment_id = str(attachments.get("id") or "").strip()
    if not attachment_id:
        raise RuntimeError("Workspaceboard attachment upload succeeded without an attachment id.")
    return attachments


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


def build_scheduler_bridge_message(items: list[dict]) -> str:
    lines = [
        "Task Flow scheduler-bridge handoff.",
        "",
        "These Task Flow rows are actionable and unscheduled: they are waiting/classified, have no live worker session, and do not carry an exact blocker.",
        "Create or continue the real work now. For each item: verify source state first, then either complete the action, record one exact blocker, or write waiting with a concrete next check.",
        "Do not leave the item in generic waiting without a worker, due timestamp, or blocker.",
        "",
    ]
    for index, item in enumerate(items, 1):
        lines.extend([
            f"{index}. key: {item.get('dedupe_key') or ''}",
            f"   owner: {item.get('owner_lane') or ''}",
            f"   worker/persona: {item.get('responsible_worker_or_persona') or ''}",
            f"   source: {item.get('source_ref') or ''}",
            f"   task/domain: {item.get('ops_portal_or_domain_task') or ''}",
            f"   action: {item.get('scheduled_action') or ''}",
            f"   next update: {item.get('next_update') or ''}",
            "",
        ])
    return "\n".join(lines).rstrip()


def record_task_flow_packet(recorder: Path, packet: dict, event: str) -> dict:
    result = subprocess.run(
        [resolve_php(), str(recorder), "record"],
        input=json.dumps({"event": event, "packet": packet}, ensure_ascii=True),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )
    return json.loads(result.stdout)


def record_routed_packet(recorder: Path, item: dict, session_id: str, due_or_trigger: str, *, event: str = "task_flow_due_worker_routed", intake_channel: str = "task-flow-due", verification_readback: str | None = None, next_update: str | None = None) -> dict:
    recurrence = item.get("recurrence") if isinstance(item.get("recurrence"), dict) else {}
    packet = shared_task_flow.build_packet(
        source_ref=item.get("source_ref") or item.get("dedupe_key") or "",
        dedupe_key=item.get("dedupe_key") or "",
        intake_channel=intake_channel,
        requester="task-flow-reminder",
        owner_lane=item.get("owner_lane") or "",
        responsible_worker_or_persona=item.get("responsible_worker_or_persona") or "",
        workspaceboard_session=session_id,
        ops_portal_or_domain_task=item.get("ops_portal_or_domain_task") or "",
        status="working",
        due_or_trigger=due_or_trigger,
        scheduled_action=item.get("scheduled_action") or "",
        calendar_event=item.get("calendar_event") or "",
        verification_readback=verification_readback or f"task_flow_due_runner_started_visible_worker:{session_id}",
        next_update=next_update or f"Visible worker {session_id} must return owner-visible proof, one exact blocker, or a future next check.",
        recurrence_enabled=item.get("recurrence_enabled") or ("true" if recurrence.get("enabled") else ""),
        recurrence_kind=item.get("recurrence_kind") or recurrence.get("kind") or "",
        recurrence_cadence=item.get("recurrence_cadence") or recurrence.get("cadence") or "",
        recurrence_pattern=item.get("recurrence_pattern") or recurrence.get("pattern") or "",
        recurrence_rule=item.get("recurrence_rule") or recurrence.get("rule") or "",
        recurrence_anchor=item.get("recurrence_anchor") or recurrence.get("anchor") or "",
        recurrence_until=item.get("recurrence_until") or recurrence.get("until") or "",
        recurrence_interval=item.get("recurrence_interval") or recurrence.get("interval") or "",
        recurrence_time=item.get("recurrence_time") or recurrence.get("time") or "",
        recurrence_summary=item.get("recurrence_summary") or recurrence.get("summary") or "",
    )
    return record_task_flow_packet(recorder, packet, event)


def record_blocked_packet(recorder: Path, item: dict, blocker_text: str, owner_question: str, *, event: str = "task_flow_scheduler_route_blocked") -> dict:
    packet = shared_task_flow.build_packet(
        source_ref=item.get("source_ref") or item.get("dedupe_key") or "",
        dedupe_key=item.get("dedupe_key") or "",
        intake_channel="task-flow-scheduler-bridge",
        requester="task-flow-reminder",
        owner_lane=item.get("owner_lane") or "",
        responsible_worker_or_persona=item.get("responsible_worker_or_persona") or "",
        workspaceboard_session="",
        ops_portal_or_domain_task=item.get("ops_portal_or_domain_task") or "",
        status="blocked",
        due_or_trigger="",
        scheduled_action=item.get("scheduled_action") or "",
        calendar_event=item.get("calendar_event") or "",
        clarification_email=blocker_text,
        completion_or_blocker_email=blocker_text,
        verification_readback="task_flow_scheduler_bridge_blocked",
        next_update=owner_question,
    )
    return record_task_flow_packet(recorder, packet, event)


def is_daemon_owned_due_item(item: dict) -> bool:
    recurrence = item.get("recurrence") if isinstance(item.get("recurrence"), dict) else {}
    recurrence_rule = str(item.get("recurrence_rule") or recurrence.get("rule") or "").strip()
    scheduled_action = str(item.get("scheduled_action") or "")
    if recurrence_rule == "owner_reply_daily_repeat" or scheduled_action.lower().startswith("respond to owner reply:"):
        return False
    if not str(item.get("scheduled_action") or "").strip():
        return False
    workspace = workspace_for_task_flow_item(item)
    if workspace not in DAEMON_OWNED_DUE_WORKSPACES:
        return False
    text = " ".join([
        str(item.get("owner_lane") or ""),
        str(item.get("responsible_worker_or_persona") or ""),
        str(item.get("scheduled_action") or ""),
        str(item.get("source_ref") or ""),
        str(item.get("next_update") or ""),
    ]).lower()
    return any(token in text for token in [
        "vanessa",
        "nationaloutreach",
        "outreach-coordinator",
        "internal-communicator",
        "day-of cot",
        "cot",
    ])


def record_daemon_owned_packet(recorder: Path, item: dict) -> dict:
    recurrence = item.get("recurrence") if isinstance(item.get("recurrence"), dict) else {}
    packet = shared_task_flow.build_packet(
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
        verification_readback="task_flow_due_runner_skipped_daemon_owned_scheduled_action",
        next_update="Owning automation lane is responsible for this scheduled action; monitor daemon health and escalate only on failure or proof gap.",
        recurrence_enabled=item.get("recurrence_enabled") or ("true" if recurrence.get("enabled") else ""),
        recurrence_kind=item.get("recurrence_kind") or recurrence.get("kind") or "",
        recurrence_cadence=item.get("recurrence_cadence") or recurrence.get("cadence") or "",
        recurrence_pattern=item.get("recurrence_pattern") or recurrence.get("pattern") or "",
        recurrence_rule=item.get("recurrence_rule") or recurrence.get("rule") or "",
        recurrence_anchor=item.get("recurrence_anchor") or recurrence.get("anchor") or "",
        recurrence_until=item.get("recurrence_until") or recurrence.get("until") or "",
        recurrence_interval=item.get("recurrence_interval") or recurrence.get("interval") or "",
        recurrence_time=item.get("recurrence_time") or recurrence.get("time") or "",
        recurrence_summary=item.get("recurrence_summary") or recurrence.get("summary") or "",
    )
    return record_task_flow_packet(recorder, packet, "task_flow_due_runner_daemon_owned_skip")


def record_owner_reply_daily_next_check(recorder: Path, item: dict) -> dict:
    recurrence = item_recurrence(item)
    next_due = next_owner_reply_daily_due(item)
    packet = shared_task_flow.build_packet(
        source_ref=item.get("source_ref") or item.get("dedupe_key") or "",
        dedupe_key=item.get("dedupe_key") or "",
        intake_channel="task-flow-due",
        requester="task-flow-reminder",
        owner_lane=item.get("owner_lane") or "",
        responsible_worker_or_persona=item.get("responsible_worker_or_persona") or "",
        workspaceboard_session=item.get("workspaceboard_session") or "",
        ops_portal_or_domain_task=item.get("ops_portal_or_domain_task") or "",
        status="waiting",
        due_or_trigger=next_due,
        scheduled_action=item.get("scheduled_action") or "",
        calendar_event=item.get("calendar_event") or "",
        verification_readback="owner_reply_daily_repeat: existing handoff preserved; next daily reminder advanced.",
        next_update=f"Daily owner-reply reminder advanced to {next_due}; worker still needs sent proof, domain proof, or one exact blocker/question.",
        recurrence_enabled="true",
        recurrence_kind=item.get("recurrence_kind") or recurrence.get("kind") or "daily",
        recurrence_cadence=item.get("recurrence_cadence") or recurrence.get("cadence") or "daily",
        recurrence_pattern=item.get("recurrence_pattern") or recurrence.get("pattern") or "daily owner reply follow-up",
        recurrence_rule=item.get("recurrence_rule") or recurrence.get("rule") or "owner_reply_daily_repeat",
        recurrence_anchor=next_due,
        recurrence_until=item.get("recurrence_until") or recurrence.get("until") or "",
        recurrence_interval=item.get("recurrence_interval") or recurrence.get("interval") or "1",
        recurrence_time=next_due[11:19],
        recurrence_summary="Daily repeat reminder until assistant sent proof or an exact owner blocker/question is recorded.",
    )
    return record_task_flow_packet(recorder, packet, "task_flow_owner_reply_daily_next_check")


def route_due_items_to_worker(recorder: Path, state_dir: Path, items: list[dict], guard: FanoutGuard, dry_run: bool = False) -> dict:
    route_candidates = [item for item in items if isinstance(item, dict) and item.get("dedupe_key")]
    if not route_candidates:
        return {"ok": True, "routed": False, "reason": "no_due_items", "items": []}

    handoff_log = state_dir / "task-flow-worker-handoffs.jsonl"
    seen_handoffs = existing_handoff_keys(handoff_log)
    skipped_existing = [item for item in route_candidates if reminder_key(item) in seen_handoffs]
    advanced_existing = []
    if not dry_run:
        for item in skipped_existing:
            if is_owner_reply_daily_item(item):
                advanced_existing.append(record_owner_reply_daily_next_check(recorder, item))
    pending = [item for item in route_candidates if reminder_key(item) not in seen_handoffs]
    if not pending:
        return {"ok": True, "routed": False, "reason": "all_due_items_already_handed_off", "items": [], "advanced_existing": advanced_existing}

    daemon_owned: list[dict] = []
    worker_pending: list[dict] = []
    for item in pending:
        if is_daemon_owned_due_item(item):
            daemon_owned.append(item)
        else:
            worker_pending.append(item)

    daemon_owned_results = []
    if daemon_owned:
        handoff_log.parent.mkdir(parents=True, exist_ok=True)
    for item in daemon_owned:
        if dry_run:
            daemon_owned_results.append({"dedupe_key": item.get("dedupe_key"), "dry_run": True, "daemon_owned": True})
        else:
            daemon_owned_results.append(record_daemon_owned_packet(recorder, item))
        row = {
            "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "event": "daemon_owned_due_item_skipped",
            "handoff_key": reminder_key(item),
            "dedupe_key": item.get("dedupe_key") or "",
            "workspace": workspace_for_task_flow_item(item),
            "reason": "owning automation lane executes scheduled action directly",
        }
        with handoff_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
        handoff_log.chmod(0o600)
        seen_handoffs.add(reminder_key(item))

    if not worker_pending:
        return {
            "ok": True,
            "routed": False,
            "reason": "daemon_owned_items_handled_in_runtime",
            "items": [],
            "daemon_owned": daemon_owned_results,
        }

    grouped: dict[str, list[dict]] = {}
    for item in worker_pending:
        grouped.setdefault(workspace_for_task_flow_item(item), []).append(item)

    api_base = os.environ.get("WORKSPACEBOARD_URL", DEFAULT_WORKSPACEBOARD_URL).rstrip("/")
    routed: list[dict] = []
    for workspace, group in grouped.items():
        title = f"Task Flow due worker {time.strftime('%Y-%m-%d %H:%M')} {workspace}"
        message = build_worker_handoff_message(group)
        allowed, reason = guard.can_create(group, workspace, "due-worker")
        if not allowed:
            guard.record_blocked(group, workspace, "due-worker", reason)
            routed.append({
                "workspace": workspace,
                "routed": False,
                "blocked_by_guard": True,
                "reason": reason,
                "items": [item.get("dedupe_key") for item in group],
            })
            continue
        if dry_run:
            routed.append({"workspace": workspace, "dry_run": True, "items": [item.get("dedupe_key") for item in group]})
            continue
        session_id, attachments = create_worker_route_session(api_base, workspace, title, message)
        guard.record_created(group, workspace, "due-worker", session_id)
        delivery = deliver_worker_route_message(api_base, session_id, str(attachments.get("id") or ""), message)
        next_check_epoch = int(time.time()) + 1800
        next_check = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_check_epoch))
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
    return {
        "ok": True,
        "routed": any(bool(item.get("session_id")) for item in routed),
        "items": routed,
        "daemon_owned": daemon_owned_results,
    }


def route_unscheduled_items_to_worker(recorder: Path, board_recorder: Path, state_dir: Path, limit: int, guard: FanoutGuard, dry_run: bool = False) -> dict:
    report = load_task_flow_report(board_recorder, limit, "queue")
    items = report.get("items") if isinstance(report.get("items"), list) else []
    candidates = [item for item in items if isinstance(item, dict) and item.get("scheduler_route_candidate")]
    violations = [item for item in items if isinstance(item, dict) and item.get("scheduler_violation")]
    if not candidates:
        return {
            "ok": True,
            "routed": False,
            "reason": "no_unscheduled_candidates",
            "items": [],
            "candidate_count": 0,
            "violation_count": len(violations),
        }

    handoff_log = state_dir / "task-flow-scheduler-handoffs.jsonl"
    seen_handoffs = existing_handoffs(handoff_log)
    pending = []
    skipped_recent = []
    for item in candidates:
        handoff = seen_handoffs.get(scheduler_bridge_key(item))
        if handoff and handoff_is_recent(handoff, SCHEDULER_RETRY_COOLDOWN_SECONDS):
            skipped_recent.append(item)
            continue
        pending.append(item)
    if not pending:
        return {
            "ok": True,
            "routed": False,
            "reason": "all_unscheduled_candidates_in_retry_cooldown",
            "items": [],
            "candidate_count": len(candidates),
            "violation_count": len(violations),
            "cooldown_seconds": SCHEDULER_RETRY_COOLDOWN_SECONDS,
            "skipped_recent": [item.get("dedupe_key") for item in skipped_recent],
        }

    blocked: list[dict] = []
    grouped: dict[str, list[dict]] = {}
    for item in pending:
        workspace = workspace_for_task_flow_item(item)
        if workspace == "ai" and not any(str(item.get(field) or "").strip() for field in ("owner_lane", "responsible_worker_or_persona", "ops_portal_or_domain_task", "scheduled_action")):
            blocked.append(item)
            continue
        grouped.setdefault(workspace, []).append(item)

    blocked_results = []
    for item in blocked:
        blocker_text = "Scheduler bridge could not determine a target workspace from the Task Flow row."
        owner_question = "Set owner_lane/responsible_worker_or_persona to a concrete workspace route or create the worker manually."
        if dry_run:
            blocked_results.append({"dedupe_key": item.get("dedupe_key"), "dry_run": True, "blocked": True})
            continue
        blocked_results.append(record_blocked_packet(recorder, item, blocker_text, owner_question))

    api_base = os.environ.get("WORKSPACEBOARD_URL", DEFAULT_WORKSPACEBOARD_URL).rstrip("/")
    routed: list[dict] = []
    for workspace, group in grouped.items():
        title = f"Task Flow scheduler bridge {time.strftime('%Y-%m-%d %H:%M')} {workspace}"
        message = build_scheduler_bridge_message(group)
        allowed, reason = guard.can_create(group, workspace, "scheduler-bridge")
        if not allowed:
            guard.record_blocked(group, workspace, "scheduler-bridge", reason)
            routed.append({
                "workspace": workspace,
                "routed": False,
                "blocked_by_guard": True,
                "reason": reason,
                "items": [item.get("dedupe_key") for item in group],
            })
            continue
        if dry_run:
            routed.append({"workspace": workspace, "dry_run": True, "items": [item.get("dedupe_key") for item in group]})
            continue
        try:
            session_id, attachments = create_worker_route_session(api_base, workspace, title, message)
            guard.record_created(group, workspace, "scheduler-bridge", session_id)
        except Exception as exc:
            blocker_text = f"Scheduler bridge could not create a visible worker session: {exc}"
            owner_question = "Inspect Workspaceboard session-create/session-message health and reroute this Task Flow item."
            for item in group:
                blocked_results.append(record_blocked_packet(recorder, item, blocker_text, owner_question))
            continue
        handoff_log.parent.mkdir(parents=True, exist_ok=True)
        for item in group:
            row = {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "event": "scheduler_bridge_worker_handoff_routed",
                "handoff_key": scheduler_bridge_key(item),
                "dedupe_key": item.get("dedupe_key") or "",
                "workspace": workspace,
                "session_id": session_id,
                "attachment_group_id": str(attachments.get("id") or ""),
            }
            with handoff_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            handoff_log.chmod(0o600)
        try:
            delivery = deliver_worker_route_message(api_base, session_id, str(attachments.get("id") or ""), message)
        except Exception as exc:
            blocker_text = f"Scheduler bridge created worker session {session_id} but could not deliver the handoff message: {exc}"
            owner_question = "Inspect Workspaceboard session-message health or open the worker session directly."
            for item in group:
                blocked_results.append(record_blocked_packet(recorder, item, blocker_text, owner_question))
            continue
        next_check_epoch = int(time.time()) + 600
        next_check = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_check_epoch))
        recorded_packets = []
        for item in group:
            recorded_packets.append(record_routed_packet(
                recorder,
                item,
                session_id,
                next_check,
                event="task_flow_scheduler_worker_routed",
                intake_channel="task-flow-scheduler-bridge",
                verification_readback=f"task_flow_scheduler_bridge_started_visible_worker:{session_id}",
                next_update=f"Visible worker {session_id} must return proof, one exact blocker, or a concrete next check by {next_check}.",
            ))
        routed.append({
            "workspace": workspace,
            "session_id": session_id,
            "items": [item.get("dedupe_key") for item in group],
            "prompt_delivery": delivery.get("prompt_delivery", {}),
            "recorded_packets": recorded_packets,
        })

    return {
        "ok": True,
        "routed": any(bool(item.get("session_id")) for item in routed),
        "candidate_count": len(candidates),
        "violation_count": len(violations),
        "items": routed,
        "blocked": blocked_results,
    }


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
    recurrence = item.get("recurrence") if isinstance(item.get("recurrence"), dict) else {}
    recurrence_rule = str(
        recurrence.get("rule")
        or item.get("recurrence_rule")
        or ""
    ).strip().lower()
    scheduled_action = str(item.get("scheduled_action") or "").strip().lower()
    if recurrence_rule == "owner_reply_daily_repeat" or scheduled_action.startswith("respond to owner reply:"):
        # These are worker follow-up timers. They should route to the owning
        # mailbox/workspace, not create a generic Robert reminder digest.
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
            sys.executable,
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


def fetch_ops_tasks_overdue_24h(limit: int = 75) -> list[dict]:
    php_code = r'''
require_once "/Users/werkstatt/ops/bootstrap.php";
$pdo = get_event_pdo();
$sql = "
SELECT
  a.activityid AS task_id,
  COALESCE(a.subject, '') AS subject,
  COALESCE(a.status, '') AS status,
  COALESCE(a.priority, '') AS priority,
  a.due_date,
  COALESCE(a.time_start, '') AS time_start,
  COALESCE(a.time_end, '') AS time_end,
  COALESCE(a.recurringtype, '') AS recurringtype,
  TIMESTAMP(a.due_date, COALESCE(NULLIF(a.time_end, ''), NULLIF(a.time_start, ''), '23:59:59')) AS due_at,
  COALESCE(CONCAT(owner.first_name, ' ', owner.last_name), owner.user_name, '') AS owner_name,
  GROUP_CONCAT(
    DISTINCT COALESCE(NULLIF(CONCAT(TRIM(COALESCE(u.first_name, '')), ' ', TRIM(COALESCE(u.last_name, ''))), ' '), u.user_name, g.groupname, CAST(a2.user_id AS CHAR))
    ORDER BY COALESCE(u.last_name, g.groupname, CAST(a2.user_id AS CHAR)) SEPARATOR ', '
  ) AS assignees
FROM koval_crm.vtiger_activity a
JOIN koval_crm.vtiger_crmentity ce ON ce.crmid = a.activityid AND ce.deleted = 0
LEFT JOIN koval_crm.vtiger_users owner ON owner.id = ce.smownerid
LEFT JOIN koval_crm.activity2user a2 ON a2.activity_id = a.activityid
LEFT JOIN koval_crm.vtiger_users u ON u.id = a2.user_id
LEFT JOIN koval_crm.vtiger_groups g ON g.groupid = a2.user_id
WHERE a.activitytype = 'Task'
  AND a.due_date IS NOT NULL
  AND a.due_date <> ''
  AND a.due_date <> '0000-00-00'
  AND COALESCE(a.sendnotification, 0) = 1
  AND COALESCE(a.status, '') NOT IN ('Completed', 'Cancelled', 'Canceled')
GROUP BY a.activityid, a.subject, a.status, a.priority, a.due_date, a.time_start, a.time_end, a.recurringtype, owner.first_name, owner.last_name, owner.user_name
HAVING due_at <= DATE_SUB(NOW(), INTERVAL 24 HOUR)
   AND due_at > DATE_SUB(NOW(), INTERVAL 48 HOUR)
ORDER BY due_at ASC, a.activityid ASC
LIMIT " . (int)$argv[1];
$rows = $pdo->query($sql)->fetchAll(PDO::FETCH_ASSOC) ?: [];
echo json_encode(["ok" => true, "items" => $rows], JSON_UNESCAPED_SLASHES);
'''
    result = subprocess.run(
        [resolve_php(), "-r", php_code, str(max(1, limit))],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if result.returncode != 0:
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    items = payload.get("items")
    return items if isinstance(items, list) else []


def ops_overdue_alert_key(item: dict) -> str:
    return f"{item.get('task_id') or ''}|{item.get('due_at') or item.get('due_date') or ''}"


def load_ops_overdue_alert_state(path: Path) -> dict:
    if not path.is_file():
        return {"alerted": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"alerted": {}}
    if not isinstance(payload, dict):
        return {"alerted": {}}
    alerted = payload.get("alerted")
    if not isinstance(alerted, dict):
        payload["alerted"] = {}
    return payload


def write_ops_overdue_alert_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def render_ops_overdue_alert_html(path: Path, items: list[dict], new_keys: set[str]) -> None:
    rows = []
    for item in items:
        task_id = html.escape(str(item.get("task_id") or ""))
        subject = html.escape(str(item.get("subject") or "(no subject)"))
        status = html.escape(str(item.get("status") or ""))
        priority = html.escape(str(item.get("priority") or ""))
        due_at = html.escape(str(item.get("due_at") or item.get("due_date") or ""))
        assignees = html.escape(str(item.get("assignees") or item.get("owner_name") or ""))
        recurring = html.escape(str(item.get("recurringtype") or ""))
        is_new = ops_overdue_alert_key(item) in new_keys
        rows.append(
            "<tr>"
            f"<td>{'New' if is_new else ''}</td>"
            f"<td><a href=\"https://www.koval-distillery.com/ops/projects/task.php?id={task_id}\">{task_id}</a></td>"
            f"<td>{subject}</td>"
            f"<td>{status}</td>"
            f"<td>{priority}</td>"
            f"<td>{due_at}</td>"
            f"<td>{assignees}</td>"
            f"<td>{recurring}</td>"
            "</tr>"
        )
    body = f"""<!doctype html>
<html>
<body style="font-family:Arial,sans-serif;color:#111827;">
  <p>Hi Robert,</p>
  <p>The OPS tasks below crossed the 24-hour overdue threshold. Newly alertable rows are marked <strong>New</strong>.</p>
  <table style="border-collapse:collapse;width:100%;font-size:13px;">
    <thead>
      <tr>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Flag</th>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Task</th>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Subject</th>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Status</th>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Priority</th>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Due</th>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Assignee</th>
        <th style="text-align:left;border-bottom:1px solid #d1d5db;padding:6px;">Recurring</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  <p style="color:#6b7280;font-size:12px;">Generated by the Task Flow due runner for notification-enabled OPS tasks in the 24-to-48-hour overdue window.</p>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(0o600)


def notify_robert_ops_overdue(send_helper: Path, state_dir: Path, *, dry_run: bool) -> dict:
    items = fetch_ops_tasks_overdue_24h()
    if not items:
        return {"sent": False, "reason": "no_ops_tasks_overdue_24h", "count": 0}
    state_path = state_dir / "ops-overdue-24h-alert-state.json"
    state = load_ops_overdue_alert_state(state_path)
    alerted = state.get("alerted", {})
    new_keys = {ops_overdue_alert_key(item) for item in items if ops_overdue_alert_key(item) not in alerted}
    if not new_keys:
        return {"sent": False, "reason": "no_new_ops_overdue_24h_tasks", "count": len(items)}
    html_path = state_dir / f"ops-overdue-24h-alert-{int(time.time())}.html"
    render_ops_overdue_alert_html(html_path, items, new_keys)
    subject = f"OPS overdue task alert: {len(new_keys)} new / {len(items)} total 24h+ overdue"
    task_id = f"ops-overdue-24h-alert-{time.strftime('%Y-%m-%d-%H%M%S')}"
    command = [
        sys.executable,
        str(send_helper),
        "--assistant",
        "frank",
        "--to",
        ROBERT_EMAIL,
        "--subject",
        subject,
        "--html-body-file",
        str(html_path),
        "--task-id",
        task_id,
        "--no-signature",
    ]
    if dry_run:
        command.append("--dry-run")
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    sent = result.returncode == 0
    if sent and not dry_run:
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        for item in items:
            key = ops_overdue_alert_key(item)
            if key in new_keys:
                alerted[key] = {
                    "alerted_at": now,
                    "task_id": item.get("task_id"),
                    "due_at": item.get("due_at"),
                    "subject": item.get("subject"),
                }
        state["alerted"] = alerted
        state["last_sent_at"] = now
        state["last_sent_count"] = len(items)
        state["last_new_count"] = len(new_keys)
        write_ops_overdue_alert_state(state_path, state)
    return {
        "sent": sent,
        "dry_run": dry_run,
        "count": len(items),
        "new_count": len(new_keys),
        "task_id": task_id,
        "body_path": str(html_path),
        "stdout": result.stdout.strip()[-2000:],
        "stderr": result.stderr.strip()[-2000:],
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
            sys.executable,
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
    args = [sys.executable, str(script)]
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
    parser.add_argument("--workspaceboard-recorder", default=str(DEFAULT_WORKSPACEBOARD_RECORDER))
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE))
    parser.add_argument("--send-helper", default=str(DEFAULT_SEND_HELPER))
    parser.add_argument("--watchdog", default=str(DEFAULT_WATCHDOG))
    parser.add_argument("--run-watchdog", action="store_true", default=True)
    parser.add_argument("--no-watchdog", action="store_false", dest="run_watchdog")
    parser.add_argument("--notify-robert", action="store_true")
    parser.add_argument("--ops-overdue-alert", action="store_true", default=True)
    parser.add_argument("--no-ops-overdue-alert", action="store_false", dest="ops_overdue_alert")
    parser.add_argument("--route-worker", action="store_true", default=True)
    parser.add_argument("--no-route-worker", action="store_false", dest="route_worker")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--scheduler-limit", type=int, default=500)
    parser.add_argument(
        "--max-new-worker-sessions",
        type=int,
        default=int(os.environ.get("TASK_FLOW_MAX_NEW_WORKER_SESSIONS_PER_RUN", "4")),
        help="Circuit breaker: max new Workspaceboard worker sessions per due-runner cycle.",
    )
    parser.add_argument(
        "--max-new-worker-sessions-per-source",
        type=int,
        default=int(os.environ.get("TASK_FLOW_MAX_NEW_WORKER_SESSIONS_PER_SOURCE", "1")),
        help="Circuit breaker: max new Workspaceboard worker sessions per source_ref/dedupe_key in one cycle.",
    )
    parser.add_argument(
        "--max-live-tmux-sessions",
        type=int,
        default=int(os.environ.get("TASK_FLOW_MAX_LIVE_TMUX_SESSIONS", "25")),
        help="Overload mode: pause worker fan-out when live tmux sessions meet or exceed this count. Set 0 to disable.",
    )
    parser.add_argument(
        "--max-load-1m",
        type=float,
        default=float(os.environ.get("TASK_FLOW_MAX_LOAD_1M", "12.0")),
        help="Overload mode: pause worker fan-out when 1-minute load average meets or exceeds this value. Set 0 to disable.",
    )
    parser.add_argument(
        "--tmux-socket",
        default=os.environ.get("TASK_FLOW_TMUX_SOCKET", str(DEFAULT_TMUX_SOCKET)),
        help="Workspaceboard tmux socket for overload checks.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    recorder = Path(args.recorder)
    board_recorder = Path(args.workspaceboard_recorder)
    state_dir = Path(args.state_dir)
    guard = FanoutGuard(
        state_dir,
        max_sessions_per_run=args.max_new_worker_sessions,
        max_sessions_per_source=args.max_new_worker_sessions_per_source,
        max_live_tmux_sessions=args.max_live_tmux_sessions,
        max_load_1m=args.max_load_1m,
        tmux_socket=Path(args.tmux_socket),
    )
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
    scheduler_bridge = {"ok": True, "routed": False, "reason": "route_worker_disabled", "items": []}
    if args.route_worker:
        worker_handoff = route_due_items_to_worker(recorder, state_dir, reminder_items, guard, dry_run=args.dry_run)
        scheduler_bridge = route_unscheduled_items_to_worker(recorder, board_recorder, state_dir, args.scheduler_limit, guard, dry_run=args.dry_run)
    guard.flush()

    notification = {"sent": False, "reason": "not_requested"}
    if args.notify_robert and not args.dry_run:
        notification = notify_robert(Path(args.send_helper), state_dir, new_items)

    ops_overdue_notification = {"sent": False, "reason": "disabled"}
    if args.notify_robert and args.ops_overdue_alert:
        ops_overdue_notification = notify_robert_ops_overdue(Path(args.send_helper), state_dir, dry_run=args.dry_run)

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
        "scheduler_bridge": scheduler_bridge,
        "fanout_guard": {
            "created_sessions": guard.created_sessions,
            "max_new_worker_sessions": guard.max_sessions_per_run,
            "max_new_worker_sessions_per_source": guard.max_sessions_per_source,
            "overload": guard.overload,
            "events": guard.events,
        },
        "watchdog": watchdog,
        "notification": notification,
        "ops_overdue_notification": ops_overdue_notification,
        "dry_run": bool(args.dry_run),
        "items": items,
    }
    if not args.dry_run:
        write_runner_state(state_dir / "task-flow-due-runner-last.json", summary)
    print(json.dumps(summary, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
