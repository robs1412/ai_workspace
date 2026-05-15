#!/usr/bin/env python3
"""Non-secret Workspaceboard health check for AI Health Manager."""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


DEFAULT_STATUS_URL = "http://127.0.0.1:17878/api/status"
DEFAULT_LOG_DIR = Path("/Users/werkstatt/ai_workspace/tmp/ai-health-manager")
DEFAULT_NATIONALOUTREACH_STATE_DIR = Path("/Users/admin/.nationaloutreach-launch/state")
DEFAULT_FRANK_STATE_DIR = Path("/Users/admin/.frank-launch/state")
DEFAULT_AVIGNON_STATE_DIR = Path("/Users/admin/.avignon-launch/state")
DEFAULT_STALE_MINUTES = 8
DEFAULT_SESSION_RESTART_MINUTES = 8
DEFAULT_SESSION_RESTART_COOLDOWN_SECONDS = 6 * 60 * 60
DEFAULT_MAX_NON_STANDING_OPEN = 8
DEFAULT_MAX_ROBERT_BLOCKERS = 6
DEFAULT_INPUT_LOG_DIR = Path("/Users/werkstatt/ai_workspace/daily-inputs")
DEFAULT_INPUT_AUDIT_INTERVAL_SECONDS = 60
DEFAULT_ESCALATION_TIMEOUT_SECONDS = 2 * 60
DEFAULT_ESCALATION_COOLDOWN_SECONDS = 24 * 60 * 60
DEFAULT_ESCALATION_MAX_ACTIONS = 8
DEFAULT_ESCALATION_MAX_EMAILS = 3
DEFAULT_PROOF_REPAIR_BATCH_SIZE = 10
DEFAULT_PROOF_REPAIR_INTERVAL_SECONDS = 60
DEFAULT_WORKSPACEBOARD_SUPERVISOR = Path("/Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_supervisor.php")
DEFAULT_MAILBOX_CANARY_MAX_AGE_MINUTES = 10
DEFAULT_SESSION_SPRAWL_GOVERNOR_INTERVAL_SECONDS = 60
DEFAULT_STANDING_ATTENTION_MINUTES = 60
DEFAULT_WORKER_SUMMARY_ESCALATION_COOLDOWN_SECONDS = 6 * 60 * 60
DEFAULT_WORKER_SUMMARY_ESCALATION_MAX_EMAILS = 4
DEFAULT_OWNER_REPLY_TIMEOUT_SECONDS = 2 * 60
DEFAULT_OWNER_REPLY_COOLDOWN_SECONDS = 5 * 60
DEFAULT_OWNER_REPLY_RECENT_HOURS = 24
DEFAULT_OWNER_REPLY_MAX_ACTIONS = 8
DEFAULT_OWNER_REPLY_ESCALATION_SECONDS = 5 * 60
DEFAULT_OWNER_REPLY_EMAIL_SECONDS = 10 * 60
DEFAULT_OWNER_REPLY_STATE_FILE = "owner-reply-thread-state.json"
DEFAULT_OWNER_REPLY_PUBSUB_PULL_LIMIT = 10
DEFAULT_GMAIL_PUSH_TIMEOUT_SECONDS = 6
DEFAULT_GMAIL_PUSH_SUBSCRIPTION = "projects/gmailconnector-485021/subscriptions/koval-gmail-push-sub"
REQUIRED_MAILBOX_MONITORS = (
    "monitor-frank-inbox",
    "monitor-avignon-inbox",
    "monitor-nationaloutreach-inbox",
    "monitor-asher-inbox",
    "monitor-venetia-inbox",
)
NUDGE_COOLDOWN_SECONDS = 24 * 60 * 60
BOARD_REPAIR_COOLDOWN_SECONDS = 10 * 60
WORKSPACEBOARD_PROCESS_MARKER = "/Users/admin/.workspaceboard-launch/runtime/app/server/index.js"
MAX_BOARD_REQUEST_TIMEOUT_SECONDS = 5.0
INPUT_TRACKING_MARKERS = (
    "task flow keys:",
    "task flow key:",
    "ops task",
    "portal task",
    "domain task",
    "project_hub/",
    "project hub",
    "no-action",
    "no action",
)
FINISH_CONTRACT_STATUSES = {
    "captured",
    "task_created",
    "routed",
    "scheduled",
    "working",
    "waiting",
    "blocked",
    "clarification_sent",
    "completed",
    "handled",
    "reported",
    "filed",
}
FINISH_CONTRACT_FIELDS = (
    "requested_deliverable",
    "responsible_worker_or_persona",
    "human_owner_or_recipient",
    "output_channel",
    "proof_required",
    "due_or_next_update",
    "escalation_path",
)
CLOSED_STATUSES = {"completed", "handled", "reported", "filed"}
PROOF_FIELD_MARKERS = (
    "verification_readback",
    "completion_or_blocker_email",
    "message_id",
    "file_path",
    "artifact_path",
    "task_id",
    "portal_id",
    "ops_id",
    "sheet_range",
    "readback",
    "no_action_reason",
    "closeout_proof_marker",
)
MAILBOX_LOCATION_MARKERS = (
    "mailbox_state",
    "source_mailbox_state",
    "mailbox_folder",
    "source_mailbox_folder",
    "email_folder",
    "source_email_folder",
    "gmail_label",
    "gmail_labels",
    "labels",
)
VAGUE_DECISION_PHRASES = (
    "approval needed",
    "needs approval",
    "need approval",
    "needs decision",
    "decision needed",
    "missing workflow",
    "exact next step",
    "needs input",
    "review needed",
    "please advise",
)
SOURCE_FIRST_SYSTEMS = (
    "Task Flow",
    "Workspaceboard history",
    "Google Drive",
    "OPS",
    "Portal/CRM",
    "Salesreport",
    "BID/finance records",
    "sent logs",
    "mailbox metadata",
    "project-hub/HANDOFF notes",
)
SOURCE_EXHAUSTION_MARKERS = (
    "sources checked",
    "source check",
    "checked task flow",
    "checked workspaceboard",
    "checked google drive",
    "checked ops",
    "checked portal",
    "checked crm",
    "checked salesreport",
    "checked bid",
    "checked sent log",
    "checked mailbox",
    "not available in",
    "not found in",
    "no matching record in",
    "source unavailable",
    "access blocked",
)
REAL_HUMAN_GATE_MARKERS = (
    "auth required",
    "authentication required",
    "credential",
    "2fa",
    "permission denied",
    "access denied",
    "security approval",
    "legal approval",
    "owner approval",
    "external send approval",
    "destructive",
    "bulk delete",
    "payment approval",
    "pricing approval",
)
OWNER_EMAIL_BY_USER_ID = {
    1: "robert@kovaldistillery.com",
    3: "sonat@kovaldistillery.com",
    21: "mark@kovaldistillery.com",
    144: "sebastian@kovaldistillery.com",
    165: "dmytro.klymentiev@kovaldistillery.com",
}
OWNER_USER_ID_BY_EMAIL = {email: user_id for user_id, email in OWNER_EMAIL_BY_USER_ID.items()}
PRIMARY_OWNER_EMAILS = frozenset(OWNER_EMAIL_BY_USER_ID.values())
WORKER_SESSION_BY_MAILBOX = {
    "frank": "monitor-frank-inbox",
    "avignon": "monitor-avignon-inbox",
    "nationaloutreach": "monitor-nationaloutreach-inbox",
}

STANDING_PATTERNS = {
    "Task Manager": ("task manager",),
    "Summary Worker": ("summary worker",),
    "Decision Driver": ("decision driver",),
    "Security Guard": ("security guard",),
    "Code/Git Manager": ("code/git manager", "code and git manager"),
    "Frank": ("frank email worker",),
    "Avignon": ("avignon email worker",),
    "AI Health Manager": ("ai health manager",),
}


def source_first_directive() -> str:
    systems = ", ".join(SOURCE_FIRST_SYSTEMS)
    return (
        "Source-first rule: before asking Robert/Sonat/another owner for information, check the existing sources that fit the item "
        f"({systems}). If the answer is available there, complete the work and record proof. If it is not available, report the exact "
        "source checked and the missing field. Ask a human only for information unavailable from those systems or for a real auth, "
        "security, legal, destructive, external-send, pricing, or approval gate."
    )


def summary_has_source_exhaustion(summary: str) -> bool:
    lowered = " ".join(str(summary or "").lower().split())
    return any(marker in lowered for marker in SOURCE_EXHAUSTION_MARKERS)


def summary_has_real_human_gate(summary: str) -> bool:
    lowered = " ".join(str(summary or "").lower().split())
    return any(marker in lowered for marker in REAL_HUMAN_GATE_MARKERS)


class HealthCheckError(Exception):
    pass


class RunTimeout(Exception):
    pass


def raise_run_timeout(signum: int, frame: object) -> None:
    raise RunTimeout("AI Health Manager run exceeded its process watchdog")


def build_run_timeout_report(args: argparse.Namespace, error: Exception) -> dict:
    reason = safe_text(error, 180)
    return {
        "checked_at": iso_now(),
        "status_url": args.status_url,
        "cadence_seconds": args.cadence_seconds,
        "dry_run": args.dry_run,
        "board": {"ok": False},
        "classification": {
            "standing_monitors": {},
            "standing_attention_sessions": [],
            "unhealthy_sessions": [{"id": "", "title": "AI Health Manager watchdog", "reason": reason}],
            "stale_working_sessions": [],
            "stale_waiting_sessions": [],
            "review_ready_sessions": [],
            "active_waiting_sessions": [],
            "active_working_sessions": [],
        },
        "management_health": {
            "standing_count": 0,
            "standing_attention_count": 0,
            "active_working_count": 0,
            "review_ready_count": 0,
            "stale_working_count": 0,
            "stale_waiting_count": 0,
            "active_waiting_count": 0,
            "non_standing_open_count": 0,
            "robert_blocker_count": 0,
            "issues": [{"type": "run-timeout", "message": reason}],
        },
        "workspace_summary": {"active_workspace_count": 0, "open_item_count": 0, "workspaces": []},
        "canonical_status_line": f"ai health watchdog timeout; last run stopped before exceeding cadence: {reason}",
        "session_sprawl_governor": {"status": "not-run", "action": "none", "changed": 0},
        "standing_attention_minutes": DEFAULT_STANDING_ATTENTION_MINUTES,
        "daily_input_audit": {"status": "not-run", "missing_tracking_count": 0},
        "finish_contract_audit": {"status": "not-run", "missing_finish_contract_count": 0, "missing_proof_count": 0},
        "task_flow_escalation_sweep": {"status": "not-run", "checked": 0, "action": "none"},
        "gmail_push_consumer": {"status": "not-run", "pulled": 0},
        "owner_reply_followup_sweep": {"status": "not-run", "checked": 0, "due": 0, "action": "none"},
        "proof_repair_queue": {"status": "not-run", "queued": 0, "action": "none"},
        "mailbox_canaries": {"status": "not-run", "issue_count": 0, "issues": []},
        "send_path_health": {"status": "not-run", "issue_count": 0, "issues": []},
        "nudge": {"status": "not-attempted", "session_id": "", "reason": "run watchdog timeout"},
        "session_restart": {"status": "not-attempted", "session_id": "", "action": "none", "reason": "run watchdog timeout"},
        "not_touched": ["mailboxes", "credentials", "production data", "git history"],
    }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value: object) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S%z"):
        try:
            return datetime.strptime(text, fmt).astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def parse_email_time(value: object) -> datetime | None:
    parsed = parse_time(value)
    if parsed is not None:
        return parsed
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed_email = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError, AttributeError):
        return None
    if parsed_email.tzinfo is None:
        parsed_email = parsed_email.replace(tzinfo=timezone.utc)
    return parsed_email.astimezone(timezone.utc)


def minutes_since(value: object, now: datetime) -> float | None:
    parsed = parse_time(value)
    if parsed is None:
        return None
    return max(0.0, (now - parsed).total_seconds() / 60.0)


def seconds_since_time(value: datetime | None, now: datetime) -> float | None:
    if value is None:
        return None
    return max(0.0, (now - value).total_seconds())


def fetch_json(url: str, timeout: float) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    request_timeout = min(float(timeout), MAX_BOARD_REQUEST_TIMEOUT_SECONDS)
    try:
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            if response.status != 200:
                raise HealthCheckError(f"status endpoint returned HTTP {response.status}")
            payload = response.read(8 * 1024 * 1024)
    except (TimeoutError, OSError, urllib.error.URLError) as error:
        raise HealthCheckError(f"status endpoint failed: {error}") from error
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as error:
        raise HealthCheckError(f"status endpoint returned invalid JSON: {error}") from error
    if not isinstance(parsed, dict) or not parsed.get("ok"):
        raise HealthCheckError("status endpoint did not report ok=true")
    return parsed


def status_url_port(url: str) -> int | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.port:
        return int(parsed.port)
    if parsed.scheme == "http":
        return 80
    if parsed.scheme == "https":
        return 443
    return None


def listening_pids(port: int) -> list[int]:
    result = subprocess.run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        return []
    pids: list[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line.isdigit():
            continue
        pids.append(int(line))
    return pids


def process_command(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def repair_workspaceboard(args: argparse.Namespace, state: dict, failure_reason: str) -> dict:
    if args.dry_run:
        return {"status": "disabled-dry-run", "reason": failure_reason}
    if not args.allow_board_repair:
        return {"status": "disabled", "reason": "board repair disabled"}

    now_epoch = int(time.time())
    prior = state.get("last_board_repair") if isinstance(state.get("last_board_repair"), dict) else {}
    if now_epoch - int(prior.get("at_epoch") or 0) < BOARD_REPAIR_COOLDOWN_SECONDS:
        return {"status": "cooldown", "reason": failure_reason}

    port = status_url_port(args.status_url)
    if not port:
        return {"status": "skipped", "reason": "status URL has no TCP port"}

    candidates = []
    for pid in listening_pids(port):
        command = process_command(pid)
        if WORKSPACEBOARD_PROCESS_MARKER not in command:
            continue
        candidates.append({"pid": pid, "command": command})

    if len(candidates) != 1:
        return {
            "status": "skipped",
            "reason": f"expected one Workspaceboard listener on port {port}, found {len(candidates)}",
        }

    pid = int(candidates[0]["pid"])
    os.kill(pid, signal.SIGTERM)
    time.sleep(args.board_repair_wait_seconds)

    state["last_board_repair"] = {
        "at": iso_now(),
        "at_epoch": now_epoch,
        "pid": pid,
        "reason": failure_reason,
    }
    return {"status": "sent-term", "pid": pid, "reason": failure_reason}


def safe_text(value: object, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


def session_name(session: dict) -> str:
    return safe_text(session.get("title") or session.get("display_name") or session.get("id"))


def standing_role(session: dict) -> str | None:
    text = f"{session.get('title') or ''} {session.get('display_name') or ''}".lower()
    workspace_key = str(session.get("workspace_key") or "").lower()
    session_type = str(session.get("session_type") or "").lower()
    if session_type == "email_monitor" or (
        workspace_key in {"nationaloutreach", "asher", "venetia"}
        and "inbox" in text
        and "monitor" in text
    ):
        return "Email Worker"
    for role, patterns in STANDING_PATTERNS.items():
        if role == "AI Health Manager" and session.get("workspace_key") != "ai":
            continue
        if any(pattern in text for pattern in patterns):
            return role
    if "email worker" in text and ("inbox" in text or "monitor" in text):
        return "Email Worker"
    return None


def public_session(session: dict) -> dict:
    return {
        "id": safe_text(session.get("id"), 32),
        "title": session_name(session),
        "workspace": safe_text(session.get("workspace_key"), 40),
        "status": safe_text(session.get("status_label") or session.get("status"), 40),
        "runtime": safe_text(session.get("runtime_status"), 40),
        "last_activity_at": safe_text(session.get("last_activity_at"), 40),
    }


def issue_summary(issue: dict) -> str:
    title = safe_text(issue.get("title"), 80)
    reason = safe_text(issue.get("reason"), 180)
    return f"{title}: {reason}" if reason else title


def classify_sessions(status: dict, stale_minutes: int, standing_minutes: int) -> dict:
    now = utc_now()
    sessions = [item for item in status.get("managed_sessions", []) if isinstance(item, dict)]
    standing: dict[str, list[dict]] = {role: [] for role in STANDING_PATTERNS}
    standing["Email Worker"] = []
    unhealthy: list[dict] = []
    standing_attention: list[dict] = []
    stale_working: list[dict] = []
    stale_waiting: list[dict] = []
    review_ready: list[dict] = []
    active_waiting: list[dict] = []
    active_working: list[dict] = []

    for session in sessions:
        role = standing_role(session)
        status_label = str(session.get("status_label") or session.get("status") or "").lower()
        runtime = str(session.get("runtime_status") or "").lower()
        age = minutes_since(session.get("last_activity_at") or session.get("created_at"), now)
        summary = public_session(session)
        if age is not None:
            summary["inactive_minutes"] = round(age, 1)

        if role:
            standing.setdefault(role, []).append(summary)
            if age is not None and age >= standing_minutes:
                standing_attention.append({**summary, "role": role, "reason": f"standing session inactive for {round(age, 1)} minutes"})
            if runtime != "live" or status_label in {"launch-failed", "blocked"}:
                unhealthy.append({**summary, "reason": f"standing monitor is {status_label or runtime}"})
            continue

        if status_label == "review-ready" or str(session.get("status") or "").lower() == "finished":
            review_ready.append(summary)
        elif status_label in {"needs-input", "blocked", "launch-failed"} or str(session.get("status") or "").lower() in {"waiting", "blocked"}:
            if age is not None and age >= stale_minutes:
                stale_waiting.append({**summary, "reason": f"waiting for {round(age, 1)} minutes"})
            else:
                active_waiting.append(summary)
        elif runtime != "live":
            unhealthy.append({**summary, "reason": f"runtime is {runtime or 'unknown'}"})
        elif age is not None and age >= stale_minutes:
            stale_working.append({**summary, "reason": f"no activity for {round(age, 1)} minutes"})
        else:
            active_working.append(summary)

    missing_standing = []
    def standing_role_present(role: str) -> bool:
        if standing.get(role):
            return True
        if role in {"Frank", "Avignon"}:
            target_workspace = role.lower()
            return any(
                str(item.get("workspace") or "").lower() == target_workspace
                for item in standing.get("Email Worker", [])
            )
        return False

    for role in ("Task Manager", "Summary Worker", "Decision Driver", "Security Guard", "Frank", "Avignon"):
        if not standing_role_present(role):
            missing_standing.append(role)
            unhealthy.append({
                "id": "",
                "title": role,
                "workspace": "",
                "status": "missing",
                "runtime": "missing",
                "last_activity_at": "",
                "reason": "standing monitor not visible in board status",
            })

    return {
        "session_count": len(sessions),
        "standing_monitors": standing,
        "standing_attention_sessions": standing_attention,
        "missing_standing_monitors": missing_standing,
        "unhealthy_sessions": unhealthy,
        "stale_working_sessions": stale_working,
        "stale_waiting_sessions": stale_waiting,
        "review_ready_sessions": review_ready,
        "active_waiting_sessions": active_waiting,
        "active_working_sessions": active_working,
    }


def assess_management_health(classification: dict, max_non_standing_open: int, max_robert_blockers: int) -> dict:
    standing_count = sum(len(items) for items in classification.get("standing_monitors", {}).values())
    standing_attention_count = len(classification.get("standing_attention_sessions", []))
    active_working_count = len(classification.get("active_working_sessions", []))
    review_ready_count = len(classification.get("review_ready_sessions", []))
    stale_working_count = len(classification.get("stale_working_sessions", []))
    stale_waiting_count = len(classification.get("stale_waiting_sessions", []))
    active_waiting_count = len(classification.get("active_waiting_sessions", []))
    non_standing_open_count = (
        active_working_count
        + review_ready_count
        + stale_working_count
        + stale_waiting_count
        + active_waiting_count
    )
    robert_blocker_count = active_waiting_count + stale_waiting_count

    issues = []
    if non_standing_open_count > max_non_standing_open:
        issues.append({
            "id": "session-sprawl",
            "severity": "warning",
            "title": "Session sprawl is a management failure",
            "reason": f"non-standing open sessions = {non_standing_open_count} (threshold {max_non_standing_open})",
            "task_manager_action": (
                "Reuse existing correctly-owned sessions when possible, reconcile stale wrappers and "
                "finished-at-prompt workers aggressively, and close routine review-ready parking internally."
            ),
        })
    if robert_blocker_count > max_robert_blockers:
        issues.append({
            "id": "blocker-overflow",
            "severity": "warning",
            "title": "Robert-facing blocker set is too large",
            "reason": f"waiting/blocker sessions = {robert_blocker_count} (threshold {max_robert_blockers})",
            "task_manager_action": (
                "Keep Robert-facing blockers to a small real set, and do not resurface routine cleanup, "
                "review-ready parking, or inbox-zero filing to Robert once internal handling is approved."
            ),
        })
    if standing_attention_count:
        issues.append({
            "id": "standing-session-attention",
            "severity": "warning",
            "title": "Standing sessions need an hourly check",
            "reason": f"standing sessions without recent activity = {standing_attention_count}",
            "task_manager_action": (
                "Check the email workers and monitors on the hourly cadence, verify runtime and last activity, "
                "and restart or nudge only the affected standing session if it stopped reporting."
            ),
        })

    return {
        "standing_count": standing_count,
        "standing_attention_count": standing_attention_count,
        "active_working_count": active_working_count,
        "review_ready_count": review_ready_count,
        "stale_working_count": stale_working_count,
        "stale_waiting_count": stale_waiting_count,
        "active_waiting_count": active_waiting_count,
        "non_standing_open_count": non_standing_open_count,
        "robert_blocker_count": robert_blocker_count,
        "issues": issues,
    }


def summarize_workspaces(status: dict) -> dict:
    workspaces = [item for item in status.get("workspaces", []) if isinstance(item, dict)]
    open_workspaces = []
    for workspace in workspaces:
        todo = workspace.get("todo") if isinstance(workspace.get("todo"), dict) else {}
        open_count = int(todo.get("open_count") or 0)
        running = int(workspace.get("running") or 0)
        total = int(workspace.get("total") or 0)
        if open_count or running or total:
            open_workspaces.append({
                "key": safe_text(workspace.get("key"), 40),
                "label": safe_text(workspace.get("label"), 80),
                "open_count": open_count,
                "waiting_next_step_count": int(todo.get("waiting_next_step_count") or 0),
                "awaiting_input_count": int(todo.get("awaiting_input_count") or 0),
                "waiting_decision_count": int(todo.get("waiting_decision_count") or 0),
                "running_sessions": running,
                "total_sessions": total,
            })
    return {
        "active_workspace_count": len(open_workspaces),
        "open_item_count": sum(item["open_count"] for item in open_workspaces),
        "workspaces": open_workspaces,
    }


def load_state(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
            return loaded if isinstance(loaded, dict) else {}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
            return loaded if isinstance(loaded, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def read_jsonl_tail(path: Path, max_lines: int = 5000) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
    except (FileNotFoundError, OSError):
        return []
    rows: list[dict] = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def run_workspaceboard_supervisor() -> dict:
    if not DEFAULT_WORKSPACEBOARD_SUPERVISOR.is_file():
        return {"status": "missing", "path": str(DEFAULT_WORKSPACEBOARD_SUPERVISOR)}
    try:
        result = subprocess.run(
            ["php", str(DEFAULT_WORKSPACEBOARD_SUPERVISOR), "--record-only", "--no-sync-sessions", "--batch-size", "4"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"status": "failed", "error": safe_text(error, 240)}
    try:
        parsed = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        parsed = {}
    return {
        "status": "checked" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "result": parsed,
        "stderr": safe_text(result.stderr, 240),
    }


def daily_input_files(input_log_dir: Path, now: datetime) -> list[Path]:
    today = now.astimezone().date()
    files = [input_log_dir / f"{today.isoformat()}.md"]
    try:
        yesterday = today.fromordinal(today.toordinal() - 1)
        files.append(input_log_dir / f"{yesterday.isoformat()}.md")
    except ValueError:
        pass
    return files


def parse_daily_input_sections(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    sections: list[dict] = []
    current_heading = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_heading:
                sections.append({
                    "file": str(path),
                    "heading": safe_text(current_heading, 140),
                    "body": "\n".join(current_lines),
                })
            current_heading = line[3:].strip()
            current_lines = []
            continue
        if current_heading:
            current_lines.append(line)
    if current_heading:
        sections.append({
            "file": str(path),
            "heading": safe_text(current_heading, 140),
            "body": "\n".join(current_lines),
        })
    return sections


def section_has_tracking(body: str) -> bool:
    lowered = body.lower()
    return any(marker in lowered for marker in INPUT_TRACKING_MARKERS)


def audit_daily_inputs(args: argparse.Namespace, state: dict) -> dict:
    now_epoch = int(time.time())
    input_state = state.setdefault("daily_input_audit", {})
    prior_epoch = int(input_state.get("last_full_audit_epoch") or 0)
    due = now_epoch - prior_epoch >= args.input_audit_interval_seconds
    input_log_dir = Path(args.input_log_dir)
    files = daily_input_files(input_log_dir, utc_now())
    sections: list[dict] = []
    for path in files:
        sections.extend(parse_daily_input_sections(path))

    missing_tracking = [
        {
            "file": item["file"],
            "heading": item["heading"],
            "reason": "daily input section has no Task Flow/domain/no-action marker",
        }
        for item in sections
        if not section_has_tracking(item["body"])
    ]

    audit = {
        "status": "not-due",
        "due": due,
        "input_log_dir": str(input_log_dir),
        "interval_seconds": args.input_audit_interval_seconds,
        "section_count": len(sections),
        "missing_tracking_count": len(missing_tracking),
        "missing_tracking": missing_tracking[:20],
        "last_full_audit": input_state.get("last_full_audit", ""),
    }

    if due:
        input_state["last_full_audit"] = iso_now()
        input_state["last_full_audit_epoch"] = now_epoch
        audit["status"] = "checked"
    if due and missing_tracking and args.allow_input_audit_nudge:
        task_manager_sessions = []
        try:
            status = fetch_json(args.status_url, args.timeout)
            classification = classify_sessions(status, args.stale_minutes, DEFAULT_STANDING_ATTENTION_MINUTES)
            task_manager_sessions = classification.get("standing_monitors", {}).get("Task Manager", [])
        except HealthCheckError:
            task_manager_sessions = []
        if task_manager_sessions:
            session_id = task_manager_sessions[0].get("id") or ""
            headings = "; ".join(item["heading"] for item in missing_tracking[:5])
            message = (
                "AI Health Manager missed-input audit: daily input sections need capture/follow-through. "
                f"Missing Task Flow/domain/no-action marker: {headings}. "
                "Do not start a broad worker burst; create or update the correct Task Flow/domain records, "
                "queue anything over capacity, and return one concise readback."
            )
            payload = json.dumps({"session_id": session_id, "message": message, "wait_ms": 700}).encode("utf-8")
            request = urllib.request.Request(
                args.message_url,
                data=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=args.timeout) as response:
                    audit["nudge_status"] = "sent" if response.status == 200 else "failed"
            except urllib.error.URLError as error:
                audit["nudge_status"] = "failed"
                audit["nudge_error"] = safe_text(error, 180)
            audit["nudge_session_id"] = session_id
        else:
            audit["nudge_status"] = "no-task-manager"
    elif missing_tracking:
        audit["nudge_status"] = "disabled"
    else:
        audit["nudge_status"] = "not-needed"
    return audit


def run_task_flow_report(command: str, timeout: float) -> dict:
    if not command.strip():
        return {"status": "disabled", "items": []}
    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=Path(__file__).resolve().parents[1],
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"status": "failed", "items": [], "error": safe_text(error, 240)}
    if result.returncode != 0:
        return {
            "status": "failed",
            "items": [],
            "error": safe_text(result.stderr or result.stdout, 240),
        }
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        return {"status": "failed", "items": [], "error": f"invalid Task Flow JSON: {error}"}
    if not isinstance(parsed, dict) or not parsed.get("ok"):
        return {"status": "failed", "items": [], "error": "Task Flow report did not return ok=true"}
    return parsed


def run_task_flow_validate(command: str, timeout: float, packet: dict) -> dict:
    if not command.strip():
        return {"status": "disabled", "ok": False, "error": "Task Flow validate command disabled"}
    try:
        result = subprocess.run(
            shlex.split(command),
            input=json.dumps({"packet": packet}),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=Path(__file__).resolve().parents[1],
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"status": "failed", "ok": False, "error": safe_text(error, 240)}
    if result.returncode != 0:
        return {
            "status": "failed",
            "ok": False,
            "error": safe_text(result.stderr or result.stdout, 240),
        }
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        return {"status": "failed", "ok": False, "error": f"invalid Task Flow validate JSON: {error}"}
    if not isinstance(parsed, dict):
        return {"status": "failed", "ok": False, "error": "Task Flow validate did not return an object"}
    parsed.setdefault("status", "checked")
    return parsed


def mailbox_canary_checks(args: argparse.Namespace, status: dict) -> dict:
    if not args.enable_mailbox_canaries:
        return {"status": "disabled", "required": list(REQUIRED_MAILBOX_MONITORS), "issues": []}
    now = utc_now()
    sessions = [item for item in status.get("managed_sessions", []) if isinstance(item, dict)]
    by_id = {str(item.get("id") or ""): item for item in sessions}
    issues: list[dict] = []
    monitors: list[dict] = []
    for monitor_id in REQUIRED_MAILBOX_MONITORS:
        session = by_id.get(monitor_id)
        if not session:
            issues.append({
                "id": monitor_id,
                "reason": "required mailbox monitor is missing from Workspaceboard status",
            })
            continue
        status_label = str(session.get("status_label") or session.get("status") or "").lower()
        runtime = str(session.get("runtime_status") or "").lower()
        age = minutes_since(session.get("last_activity_at") or session.get("created_at"), now)
        monitor_summary = public_session(session)
        if age is not None:
            monitor_summary["inactive_minutes"] = round(age, 1)
        monitors.append(monitor_summary)
        if str(session.get("session_type") or "") != "email_monitor":
            issues.append({"id": monitor_id, "reason": "required monitor is not typed as email_monitor"})
        if status_label != "monitoring" or runtime != "live":
            issues.append({"id": monitor_id, "reason": f"monitor is {status_label or 'unknown'}/{runtime or 'unknown'}"})
        if age is None:
            issues.append({"id": monitor_id, "reason": "monitor has no readable last activity timestamp"})
        elif age > args.mailbox_canary_max_age_minutes:
            issues.append({
                "id": monitor_id,
                "reason": f"monitor has not reported activity for {round(age, 1)} minutes",
            })

    canary_packet = {
        "dedupe_key": "canary-ai-health-mailbox-proof",
        "source_ref": "canary:mailbox-proof",
        "intake_channel": "canary:ai-health",
        "requester": "AI Health",
        "owner_lane": "ai-health",
        "responsible_worker_or_persona": "ai-health",
        "ops_portal_or_domain_task": "Mailbox monitor canary",
        "status": "completed",
        "completion_or_blocker_email": "canary-message-id",
        "verification_readback": "Canary proof readback",
        "papers_projection": "not_applicable",
        "next_update": "canary complete",
        "requested_deliverable": "Validate mailbox monitor proof path",
        "human_owner_or_recipient": "AI Health",
        "output_channel": "Task Flow validate",
        "proof_required": "closeout proof marker and validation pass",
        "due_or_next_update": "next AI Health run",
        "escalation_path": "AI Health flags canary failure",
    }
    validation = run_task_flow_validate(args.task_flow_validate_cmd, args.timeout, canary_packet)
    if not validation.get("ok") or validation.get("closeout_allowed") is not True:
        issues.append({
            "id": "task-flow-closeout-proof-canary",
            "reason": safe_text(validation.get("error") or validation.get("reason") or validation, 240),
        })
    status_label = "passed" if not issues else "failed"
    return {
        "status": status_label,
        "required": list(REQUIRED_MAILBOX_MONITORS),
        "monitors": monitors,
        "proof_validation": {
            "status": validation.get("status", ""),
            "ok": bool(validation.get("ok")),
            "closeout_allowed": validation.get("closeout_allowed"),
        },
        "issue_count": len(issues),
        "issues": issues,
    }


def send_path_health_check(args: argparse.Namespace) -> dict:
    state_dir = Path(args.nationaloutreach_state_dir).expanduser()
    sent_dir = state_dir / "sent"
    failures_path = state_dir / "send-failures.jsonl"
    issues: list[dict] = []
    checked = 0
    now_epoch = time.time()
    recent_cutoff = now_epoch - (args.send_path_recent_hours * 60 * 60)

    try:
        sent_files = sorted(sent_dir.glob("*.sent-*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    except OSError as error:
        return {
            "status": "failed",
            "state_dir": str(state_dir),
            "checked": 0,
            "issue_count": 1,
            "issues": [{"reason": safe_text(error, 220)}],
        }

    recent_sent_files = [path for path in sent_files if path.stat().st_mtime >= recent_cutoff]
    for path in recent_sent_files[: args.send_path_scan_limit]:
        checked += 1
        payload = load_json(path)
        sent_metadata = payload.get("sent_metadata") if isinstance(payload.get("sent_metadata"), dict) else {}
        packet = payload.get("task_packet") if isinstance(payload.get("task_packet"), dict) else {}
        message_id = safe_text(sent_metadata.get("message_id") or payload.get("message_id"), 180)
        packet_proof = safe_text(packet.get("completion_or_blocker_email"), 180)
        if not message_id:
            issues.append({"file": path.name, "reason": "sent artifact missing Message-ID metadata"})
        if packet and packet.get("status") == "reported" and (not packet_proof or packet_proof.lower().startswith("pending-")):
            issues.append({"file": path.name, "reason": "reported task packet missing completion_or_blocker_email"})
        if len(issues) >= args.send_path_max_issues:
            break

    def failure_has_sent_proof(draft_value: object) -> bool:
        draft_name = Path(str(draft_value or "")).name
        if not draft_name.endswith(".approved.json"):
            return False
        prefix = draft_name.removesuffix(".approved.json")
        for sent_path in sent_dir.glob(f"{prefix}.sent-*.json"):
            payload = load_json(sent_path)
            sent_metadata = payload.get("sent_metadata") if isinstance(payload.get("sent_metadata"), dict) else {}
            packet = payload.get("task_packet") if isinstance(payload.get("task_packet"), dict) else {}
            packet_proof = safe_text(packet.get("completion_or_blocker_email"), 180)
            if sent_metadata.get("message_id") and packet_proof and not packet_proof.lower().startswith("pending-"):
                return True
        return False

    recent_failure_count = 0
    if failures_path.exists():
        try:
            lines = failures_path.read_text(encoding="utf-8", errors="replace").splitlines()[-50:]
        except OSError:
            lines = []
        for line in lines:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(row.get("error_type") or "") in {"NameError", "AttributeError", "KeyError"}:
                if failure_has_sent_proof(row.get("draft")):
                    continue
                recent_failure_count += 1
                issues.append({
                    "file": safe_text(row.get("draft"), 180),
                    "reason": f"send path code error: {safe_text(row.get('error_type'), 60)}",
                })
                if len(issues) >= args.send_path_max_issues:
                    break

    return {
        "status": "passed" if not issues else "failed",
        "state_dir": str(state_dir),
        "checked": checked,
        "recent_hours": args.send_path_recent_hours,
        "recent_code_failure_count": recent_failure_count,
        "issue_count": len(issues),
        "issues": issues,
    }


def packet_dict(item: dict) -> dict:
    raw = item.get("packet_json")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def first_value(item: dict, packet: dict, names: tuple[str, ...]) -> str:
    for name in names:
        value = item.get(name)
        if value in (None, ""):
            value = packet.get(name)
        if isinstance(value, (dict, list)):
            if value:
                return json.dumps(value, sort_keys=True)
            continue
        text = str(value or "").strip()
        if text:
            return text
    return ""


def task_flow_finish_contract_missing(item: dict) -> list[str]:
    packet = packet_dict(item)
    checks = {
        "requested_deliverable": ("requested_deliverable", "deliverable", "expected_output"),
        "responsible_worker_or_persona": (
            "responsible_worker_or_persona",
            "responsible_worker",
            "responsible_persona",
        ),
        "human_owner_or_recipient": (
            "human_owner_or_recipient",
            "human_owner",
            "recipient",
            "completion_report_recipient",
            "requester",
        ),
        "output_channel": ("output_channel", "completion_output_channel", "closeout_channel"),
        "proof_required": ("proof_required", "required_proof", "proof_marker_required"),
        "due_or_next_update": ("due_or_next_update", "due_or_trigger", "next_update", "scheduled_action", "next_update_time"),
        "escalation_path": ("escalation_path", "escalation_if_incomplete", "if_not_complete_on_time"),
    }
    missing = [
        field
        for field, names in checks.items()
        if not first_value(item, packet, names)
        and not task_flow_default_finish_contract_value(item, packet, field)
    ]
    return missing


def task_flow_is_email_derived(item: dict, packet: dict) -> bool:
    haystack = " ".join(
        str(first_value(item, packet, (name,)) or "")
        for name in ("intake_channel", "source_ref", "latest_event")
    ).lower()
    return any(marker in haystack for marker in ("email", "gmail", "nationaloutreach"))


def task_flow_default_finish_contract_value(item: dict, packet: dict, field: str) -> str:
    worker = first_value(item, packet, ("responsible_worker_or_persona", "responsible_worker", "responsible_persona")).lower()
    owner_lane = first_value(item, packet, ("owner_lane",)).lower()
    lane = f"{worker} {owner_lane}"
    email_derived = task_flow_is_email_derived(item, packet)
    if field == "requested_deliverable":
        if first_value(item, packet, ("next_update", "source_links", "ops_portal_or_domain_task")):
            return first_value(item, packet, ("next_update", "source_links", "ops_portal_or_domain_task"))
        return "Complete the requested work or return one exact blocker."
    if field == "human_owner_or_recipient":
        return first_value(item, packet, ("requester", "owner", "human_owner", "recipient")) or "Robert / requesting owner"
    if field == "output_channel":
        return "owner-visible email or Task Flow blocker readback" if email_derived else "Task Flow readback, owner-visible email, or domain artifact"
    if field == "proof_required":
        if "ezra" in lane:
            return "Ezra owner-visible email Message-ID, document/artifact link, or one exact blocker"
        if "vanessa" in lane or "outreach" in lane:
            return "OPS/calendar/event readback, owner-visible email Message-ID, or one exact blocker"
        if "naomi" in lane or "finance" in lane:
            return "Naomi owner-visible email Message-ID, finance readback, or one exact blocker"
        return "owner-visible completion email Message-ID, durable readback, changed file/artifact path, domain ID, or one exact blocker"
    if field == "due_or_next_update":
        return "first check within 2 minutes; result email, owner question, or exact blocker within 5 minutes"
    if field == "escalation_path":
        return "Task Manager repair at 5 minutes; AI Health escalation at 10 minutes; no handled/filed closeout without Message-ID or explicit no-action proof."
    return ""


def task_flow_has_proof(item: dict) -> bool:
    packet = packet_dict(item)
    haystack = " ".join(
        str(item.get(name, "") or first_value(item, packet, (name,)) or "")
        for name in ("verification_readback", "next_update", "approval_gates", "completion_or_blocker_email")
    ).lower()
    if any(marker in haystack for marker in ("no-action", "no_action_logged", "already-handled", "duplicate")):
        return True
    closeout_text = " ".join(
        str(first_value(item, packet, (name,)) or item.get(name, "") or "")
        for name in ("latest_event", "completion_or_blocker_email", "verification_readback")
    ).lower()
    field_proof_present = any(first_value(item, packet, (name,)) for name in PROOF_FIELD_MARKERS)
    if any(marker in closeout_text for marker in (
        "email_filed_to_handled",
        "filed-to-handled-after-durable-route",
        "filed out of inbox to handled",
    )) and not field_proof_present:
        return False
    return field_proof_present


def task_flow_email_still_in_inbox(item: dict) -> bool:
    packet = packet_dict(item)
    for name in MAILBOX_LOCATION_MARKERS:
        text = first_value(item, packet, (name,)).lower()
        if not text:
            continue
        if "inbox" in text and "handled" not in text and "archived" not in text and "filed" not in text:
            return True
    in_inbox = packet.get("in_inbox", item.get("in_inbox"))
    return in_inbox is True


def task_flow_next_check_past_due(item: dict, now: datetime) -> bool:
    if str(item.get("status") or "").strip() != "routed":
        return False
    packet = packet_dict(item)
    for name in ("due_or_trigger", "next_update", "next_update_time", "due_or_next_update"):
        raw = item.get(name)
        if raw in (None, ""):
            raw = packet.get(name)
        parsed = parse_time(raw)
        if parsed is not None and parsed <= now:
            return True
    return False


def task_flow_vague_robert_decision(item: dict) -> bool:
    packet = packet_dict(item)
    decision_text = " ".join(
        first_value(item, packet, (name,))
        for name in (
            "approval_gates",
            "next_update",
            "clarification_email",
            "completion_or_blocker_email",
            "decision",
            "needed",
            "blocker",
        )
    ).strip()
    lowered = decision_text.lower()
    if not any(phrase in lowered for phrase in VAGUE_DECISION_PHRASES):
        return False
    owner_text = " ".join(
        first_value(item, packet, (name,))
        for name in ("human_owner_or_recipient", "recipient", "requester", "owner_lane", "escalation_path")
    ).lower()
    if "robert" not in owner_text and "decision driver" not in owner_text:
        return False
    return "?" not in decision_text and not any(word in lowered for word in ("approve", "decline", "change", "yes", "no"))


def audit_task_flow_finish_contracts(args: argparse.Namespace) -> dict:
    report = run_task_flow_report(args.task_flow_report_cmd, args.timeout)
    if report.get("status") in {"disabled", "failed"}:
        return {
            "status": report.get("status"),
            "task_flow_report_cmd": args.task_flow_report_cmd,
            "items_checked": 0,
            "missing_finish_contract_count": 0,
            "missing_proof_count": 0,
            "email_inbox_after_closeout_count": 0,
            "past_due_routed_count": 0,
            "vague_robert_decision_count": 0,
            "items": [],
            "error": report.get("error", ""),
        }

    items = [item for item in report.get("items", []) if isinstance(item, dict)]
    flagged: list[dict] = []
    missing_proof_count = 0
    email_inbox_after_closeout_count = 0
    past_due_routed_count = 0
    vague_robert_decision_count = 0
    now = utc_now()
    for item in items:
        status = str(item.get("status") or "").strip()
        if status not in FINISH_CONTRACT_STATUSES:
            continue
        finish_missing_fields = [
            field for field in item.get("finish_contract_missing_fields", []) if isinstance(field, str)
        ]
        if "finish_contract_missing_fields" in item:
            missing = finish_missing_fields
        else:
            missing = task_flow_finish_contract_missing(item)
        missing_fields = [field for field in item.get("missing_fields", []) if isinstance(field, str)]
        for field in FINISH_CONTRACT_FIELDS:
            if field in missing_fields and field not in missing:
                missing.append(field)
        closeout_proof_present = item.get("closeout_proof_present")
        if isinstance(closeout_proof_present, bool):
            missing_proof = status in CLOSED_STATUSES and not closeout_proof_present
        else:
            missing_proof = status in CLOSED_STATUSES and not task_flow_has_proof(item)
        if missing_proof:
            missing_proof_count += 1
            if "closeout_proof_marker" not in missing:
                missing.append("closeout_proof_marker")
        closeout_text = " ".join(
            str(item.get(name, "") or first_value(item, packet_dict(item), (name,)) or "")
            for name in ("latest_event", "completion_or_blocker_email", "verification_readback")
        ).lower()
        if any(marker in closeout_text for marker in (
            "email_filed_to_handled",
            "filed-to-handled-after-durable-route",
            "filed out of inbox to handled",
        )) and not task_flow_has_proof(item):
            if "owner_visible_completion_or_blocker_missing_after_handled_filing" not in missing:
                missing.append("owner_visible_completion_or_blocker_missing_after_handled_filing")
        if item.get("email_inbox_after_closeout") is True or (
            status in CLOSED_STATUSES and task_flow_email_still_in_inbox(item)
        ):
            email_inbox_after_closeout_count += 1
            missing.append("source_email_still_in_inbox")
        if item.get("past_due_routed") is True or task_flow_next_check_past_due(item, now):
            past_due_routed_count += 1
            missing.append("past_next_check_still_routed")
        if item.get("vague_robert_decision") is True or task_flow_vague_robert_decision(item):
            vague_robert_decision_count += 1
            missing.append("vague_robert_decision")
        if missing:
            missing = list(dict.fromkeys(missing))
            flagged.append({
                "dedupe_key": safe_text(item.get("dedupe_key"), 120),
                "status": safe_text(status, 40),
                "title": safe_text(item.get("ops_portal_or_domain_task") or item.get("source_links") or item.get("next_update"), 180),
                "owner_lane": safe_text(item.get("owner_lane"), 80),
                "responsible_worker_or_persona": safe_text(item.get("responsible_worker_or_persona"), 80),
                "missing_fields": missing,
                "reason": "Task Flow packet is missing finish-contract fields or closed-state proof",
            })

    return {
        "status": "checked",
        "task_flow_report_cmd": args.task_flow_report_cmd,
        "items_checked": len(items),
        "missing_finish_contract_count": len(flagged),
        "missing_proof_count": missing_proof_count,
        "email_inbox_after_closeout_count": email_inbox_after_closeout_count,
        "past_due_routed_count": past_due_routed_count,
        "vague_robert_decision_count": vague_robert_decision_count,
        "items": flagged[:30],
    }


def task_flow_closeout_marker_text(item: dict) -> str:
    packet = packet_dict(item)
    return " ".join(
        str(item.get(name, "") or first_value(item, packet, (name,)) or "")
        for name in ("latest_event", "completion_or_blocker_email", "verification_readback", "next_update")
    ).lower()


def task_flow_needs_escalation(item: dict) -> bool:
    status = str(item.get("status") or "").strip()
    if status in CLOSED_STATUSES and item.get("closeout_proof_present") is True:
        return False
    missing = [field for field in item.get("missing_fields", []) if isinstance(field, str)]
    if "owner_visible_completion_or_blocker_missing_after_handled_filing" in missing:
        return True
    marker_text = task_flow_closeout_marker_text(item)
    if any(marker in marker_text for marker in (
        "email_filed_to_handled",
        "filed-to-handled-after-durable-route",
        "filed out of inbox to handled",
    )):
        return True
    if status in {"routed", "working", "waiting"} and item.get("closeout_proof_present") is False:
        return "within 2 minutes" in marker_text or "owner-visible" in marker_text
    return False


def owner_for_task_flow_item(item: dict) -> tuple[int, str, str]:
    packet = packet_dict(item)
    text = " ".join(
        first_value(item, packet, (name,))
        for name in ("human_owner_or_recipient", "requester", "completion_report_recipient", "recipient")
    ).lower()
    for email, user_id in OWNER_USER_ID_BY_EMAIL.items():
        if email in text:
            label = "Robert" if user_id == 1 else email.split("@", 1)[0].title()
            return user_id, email, label
    if "sonat" in text:
        return 3, OWNER_EMAIL_BY_USER_ID[3], "Sonat"
    if "mark" in text:
        return 21, OWNER_EMAIL_BY_USER_ID[21], "Mark"
    if "sebastian" in text:
        return 144, OWNER_EMAIL_BY_USER_ID[144], "Sebastian"
    if "dmytro" in text:
        return 165, OWNER_EMAIL_BY_USER_ID[165], "Dmytro"
    return 1, OWNER_EMAIL_BY_USER_ID[1], "Robert"


def email_addresses_from_text(value: object) -> set[str]:
    text = str(value or "").lower()
    return set(re.findall(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", text))


def normalize_message_id(value: object) -> str:
    return str(value or "").strip().strip("<>").lower()


def owner_from_email_text(value: object) -> tuple[int, str, str] | None:
    emails = email_addresses_from_text(value)
    for email in emails:
        if email in OWNER_USER_ID_BY_EMAIL:
            user_id = OWNER_USER_ID_BY_EMAIL[email]
            label = "Robert" if user_id == 1 else email.split("@", 1)[0].split(".", 1)[0].title()
            if user_id == 3:
                label = "Sonat"
            return user_id, email, label
    text = str(value or "").lower()
    if "sonat" in text:
        return 3, OWNER_EMAIL_BY_USER_ID[3], "Sonat"
    if "robert" in text:
        return 1, OWNER_EMAIL_BY_USER_ID[1], "Robert"
    return None


def normalize_reply_subject(subject: object) -> str:
    text = " ".join(str(subject or "").split()).lower()
    changed = True
    while changed:
        changed = False
        for prefix in ("re:", "fw:", "fwd:", "aw:", "antwort:"):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                changed = True
    text = re.sub(r"^(frank|avignon|vanessa|naomi|ezra|codex)\s+(blocker|status|update):\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:180]


def row_time(row: dict) -> datetime | None:
    for name in ("date", "received_at", "logged_at", "created_at", "updated_at"):
        parsed = parse_email_time(row.get(name))
        if parsed is not None:
            return parsed
    return None


def recipient_text(row: dict) -> str:
    values: list[str] = []
    for name in ("to", "to_addresses", "cc", "cc_addresses", "bcc", "bcc_addresses"):
        value = row.get(name)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value or ""))
    return " ".join(values)


def collect_sent_entries(state_dir: Path) -> list[dict]:
    sent_entries: list[dict] = []
    for row in read_jsonl_tail(state_dir / "sent-log.jsonl", 6000):
        sent_at = row_time(row)
        subject_key = normalize_reply_subject(row.get("subject"))
        if not sent_at or not subject_key:
            continue
        sent_entries.append({
            "sent_at": sent_at,
            "subject_key": subject_key,
            "subject": safe_text(row.get("subject"), 180),
            "message_id": safe_text(row.get("message_id"), 180),
            "message_id_norm": normalize_message_id(row.get("message_id")),
            "from": safe_text(row.get("from"), 180),
            "recipients": recipient_text(row),
            "thread_refs": set(),
        })
    return sent_entries


def owner_reply_has_later_send(reply: dict, sent_entries: list[dict]) -> bool:
    reply_at = reply.get("received_at")
    subject_key = reply.get("subject_key", "")
    owner_email = reply.get("owner_email", "")
    source_id = normalize_message_id(reply.get("source_message_id", ""))
    reply_refs = set(reply.get("thread_refs") or [])
    for sent in sent_entries:
        if sent["sent_at"] < reply_at:
            continue
        if source_id and source_id == sent.get("message_id_norm"):
            return True
        if reply_refs and sent.get("message_id_norm") in reply_refs:
            return True
        sent_subject = sent.get("subject_key", "")
        if subject_key and sent_subject and (subject_key in sent_subject or sent_subject in subject_key):
            return True
        recipients = email_addresses_from_text(sent.get("recipients", ""))
        if owner_email and owner_email in recipients and subject_key and sent_subject:
            return True
        if source_id and source_id in str(sent.get("message_id", "")).lower():
            return True
    return False


def thread_refs_from_row(row: dict) -> list[str]:
    refs = set()
    for name in ("message_id", "source_message_id", "in_reply_to", "references"):
        value = row.get(name)
        if isinstance(value, list):
            values = value
        else:
            values = str(value or "").split()
        for item in values:
            normalized = normalize_message_id(item)
            if normalized:
                refs.add(normalized)
    return sorted(refs)


def row_is_acknowledgement_only(row: dict) -> bool:
    packet = packet_dict(row)
    haystack = " ".join(
        str(row.get(name, "") or packet.get(name, "") or "")
        for name in (
            "classification",
            "decision",
            "current_state",
            "send_allowed",
            "verification_readback",
            "approval_gates",
            "output_channel",
            "proof_required",
        )
    ).lower()
    return any(
        marker in haystack
        for marker in (
            "no-action-acknowledgement-only",
            "acknowledgement-only",
            "direct-owner-no-action",
            "tracked-reply-info",
            "logged-no-action",
            "no_action_logged",
        )
    )


def collect_nationaloutreach_owner_replies(state_dir: Path) -> list[dict]:
    replies: dict[str, dict] = {}
    for row in read_jsonl_tail(state_dir / "mail-review.jsonl", 6000):
        if row_is_acknowledgement_only(row):
            continue
        owner = owner_from_email_text(row.get("from"))
        if not owner:
            continue
        received_at = row_time(row)
        subject_key = normalize_reply_subject(row.get("subject"))
        source_id = normalize_message_id(row.get("source_message_id") or row.get("message_id"))
        if not source_id or not subject_key or not received_at:
            continue
        replies[source_id] = {
            "mailbox": "nationaloutreach",
            "source_message_id": source_id,
            "subject": safe_text(row.get("subject"), 180),
            "subject_key": subject_key,
            "from": safe_text(row.get("from"), 180),
            "owner_user_id": owner[0],
            "owner_email": owner[1],
            "owner_label": owner[2],
            "received_at": received_at,
            "route": safe_text(row.get("route"), 80),
            "session_id": "",
            "thread_refs": thread_refs_from_row(row),
        }
    active = load_json(state_dir / "active-inbox.json")
    active_messages = active.get("messages") if isinstance(active.get("messages"), list) else []
    for item in active_messages:
        if not isinstance(item, dict):
            continue
        if row_is_acknowledgement_only(item):
            continue
        owner = owner_from_email_text(item.get("from"))
        if not owner:
            continue
        received_at = row_time(item) or parse_email_time(active.get("updated_at")) or utc_now()
        subject_key = normalize_reply_subject(item.get("subject"))
        source_id = normalize_message_id(item.get("source_message_id") or item.get("message_id"))
        if not source_id or not subject_key:
            continue
        replies.setdefault(source_id, {
            "mailbox": "nationaloutreach",
            "source_message_id": source_id,
            "subject": safe_text(item.get("subject"), 180),
            "subject_key": subject_key,
            "from": safe_text(item.get("from"), 180),
            "owner_user_id": owner[0],
            "owner_email": owner[1],
            "owner_label": owner[2],
            "received_at": received_at,
            "route": safe_text(item.get("route"), 80),
            "session_id": "",
            "thread_refs": thread_refs_from_row(item),
        })
    for row in read_jsonl_tail(state_dir / "cycle-log.jsonl", 300):
        logged_at = row_time(row)
        for item in row.get("active_inbox_subjects", []) if isinstance(row.get("active_inbox_subjects"), list) else []:
            if not isinstance(item, dict):
                continue
            if row_is_acknowledgement_only(item):
                continue
            owner = owner_from_email_text(item.get("from"))
            if not owner:
                continue
            subject_key = normalize_reply_subject(item.get("subject"))
            source_id = normalize_message_id(item.get("source_message_id"))
            if not source_id or not subject_key:
                continue
            replies.setdefault(source_id, {
                "mailbox": "nationaloutreach",
                "source_message_id": source_id,
                "subject": safe_text(item.get("subject"), 180),
                "subject_key": subject_key,
                "from": safe_text(item.get("from"), 180),
                "owner_user_id": owner[0],
                "owner_email": owner[1],
                "owner_label": owner[2],
                "received_at": logged_at or utc_now(),
                "route": safe_text(item.get("route"), 80),
                "session_id": "",
                "thread_refs": thread_refs_from_row(item),
            })
    routes = load_json(state_dir / "worker-routes.json").get("routes")
    if isinstance(routes, dict):
        for reply in replies.values():
            route = routes.get(reply["source_message_id"])
            if isinstance(route, dict):
                reply["session_id"] = safe_text(route.get("session_id"), 80)
    return list(replies.values())


def collect_automation_owner_replies(state_dir: Path, mailbox: str) -> list[dict]:
    replies: dict[str, dict] = {}
    for row in read_jsonl_tail(state_dir / "automation-log.jsonl", 9000):
        if row_is_acknowledgement_only(row):
            continue
        owner = owner_from_email_text(row.get("from"))
        classification = str(row.get("classification") or "").lower()
        decision = str(row.get("decision") or "").lower()
        if not owner and "tracked-primary" not in classification and "direct-primary" not in decision:
            continue
        if owner is None:
            owner = owner_from_email_text(row.get("report_target") or row.get("owner") or "")
        if owner is None:
            continue
        subject_key = normalize_reply_subject(row.get("subject"))
        source_id = normalize_message_id(row.get("source_message_id"))
        received_at = row_time(row)
        if not source_id or not subject_key or not received_at:
            continue
        replies[source_id] = {
            "mailbox": mailbox,
            "source_message_id": source_id,
            "subject": safe_text(row.get("subject"), 180),
            "subject_key": subject_key,
            "from": safe_text(row.get("from"), 180),
            "owner_user_id": owner[0],
            "owner_email": owner[1],
            "owner_label": owner[2],
            "received_at": received_at,
            "route": safe_text(row.get("current_state") or row.get("monitor_state") or row.get("decision"), 80),
            "session_id": safe_text(row.get("routed_session_id"), 80),
            "task_id": safe_text(row.get("task_id"), 120),
            "thread_refs": thread_refs_from_row(row),
        }
    return list(replies.values())


def collect_owner_replies(args: argparse.Namespace) -> list[dict]:
    configs = [
        (Path(args.nationaloutreach_state_dir).expanduser(), "nationaloutreach", collect_nationaloutreach_owner_replies),
        (Path(args.frank_state_dir).expanduser(), "frank", collect_automation_owner_replies),
        (Path(args.avignon_state_dir).expanduser(), "avignon", collect_automation_owner_replies),
    ]
    all_replies: list[dict] = []
    cutoff = utc_now().timestamp() - (args.owner_reply_recent_hours * 60 * 60)
    for state_dir, mailbox, collector in configs:
        try:
            if collector is collect_automation_owner_replies:
                replies = collector(state_dir, mailbox)
            else:
                replies = collector(state_dir)
        except Exception as error:
            all_replies.append({
                "mailbox": mailbox,
                "source_message_id": f"collector-error:{mailbox}",
                "subject": "owner reply collector error",
                "subject_key": "owner reply collector error",
                "from": "",
                "owner_user_id": 1,
                "owner_email": OWNER_EMAIL_BY_USER_ID[1],
                "owner_label": "Robert",
                "received_at": utc_now(),
                "route": "collector-error",
                "session_id": "",
                "collector_error": safe_text(error, 240),
            })
            continue
        sent_entries = collect_sent_entries(state_dir)
        for reply in replies:
            received_at = reply.get("received_at")
            if not isinstance(received_at, datetime) or received_at.timestamp() < cutoff:
                continue
            reply["has_later_send"] = owner_reply_has_later_send(reply, sent_entries)
            all_replies.append(reply)
    return all_replies


def gmail_push_consumer_check(args: argparse.Namespace) -> dict:
    if not args.enable_gmail_push_consumer:
        return {"status": "disabled", "pulled": 0, "subscription": args.gmail_push_subscription}
    gcloud = __import__("shutil").which("gcloud")
    if not gcloud:
        return {
            "status": "blocked",
            "pulled": 0,
            "subscription": args.gmail_push_subscription,
            "blocker": "gcloud is not installed on PATH for the local AI Health runtime",
        }
    command = [
        gcloud,
        "--quiet",
        "pubsub",
        "subscriptions",
        "pull",
        args.gmail_push_subscription,
        "--auto-ack",
        "--limit",
        str(max(1, int(args.gmail_push_pull_limit))),
        "--format=json",
    ]
    env = dict(os.environ)
    env["CLOUDSDK_CORE_DISABLE_PROMPTS"] = "1"
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=min(float(args.timeout), float(args.gmail_push_timeout_seconds)),
            check=False,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "status": "degraded",
            "pulled": 0,
            "subscription": args.gmail_push_subscription,
            "error": safe_text(error, 240),
            "backstop": "60-second mailbox metadata sweep still active",
        }
    if result.returncode != 0:
        return {
            "status": "failed",
            "pulled": 0,
            "subscription": args.gmail_push_subscription,
            "error": safe_text(result.stderr or result.stdout, 240),
        }
    try:
        rows = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        rows = []
    pulled = len(rows) if isinstance(rows, list) else 0
    if pulled:
        append_jsonl(Path(args.log_dir) / "gmail-push-events.jsonl", {
            "at": iso_now(),
            "subscription": args.gmail_push_subscription,
            "pulled": pulled,
            "note": "Gmail push events pulled; owner-reply metadata sweep runs in this same AI Health pass.",
        })
    return {"status": "checked", "pulled": pulled, "subscription": args.gmail_push_subscription}


def task_flow_owner_reply_key(reply: dict) -> str:
    source = normalize_message_id(reply.get("source_message_id"))
    mailbox = str(reply.get("mailbox") or "email")
    import hashlib
    return "taskflow-owner-reply-" + hashlib.sha256(f"{mailbox}:{source}".encode("utf-8")).hexdigest()[:16]


def record_owner_reply_task_flow(args: argparse.Namespace, reply: dict, status: str = "waiting") -> tuple[bool, str]:
    key = task_flow_owner_reply_key(reply)
    packet = {
        "dedupe_key": key,
        "source_ref": reply.get("source_message_id", ""),
        "intake_channel": f"email:{reply.get('mailbox')}",
        "requester": f"{reply.get('owner_label')} <{reply.get('owner_email')}>",
        "owner_lane": reply.get("route") or reply.get("mailbox") or "email-worker",
        "responsible_worker_or_persona": reply.get("mailbox") or "email-worker",
        "workspaceboard_session": reply.get("session_id", ""),
        "ops_portal_or_domain_task": key,
        "status": status,
        "due_or_trigger": "owner_reply_pending_response",
        "scheduled_action": f"Respond to owner reply: {safe_text(reply.get('subject'), 160)}",
        "verification_readback": "owner_reply_pending_response: newest primary-owner reply has no later assistant sent proof yet.",
        "next_update": "AI Health should recheck within 1 minute; worker must send result, domain proof, or one exact blocker/question.",
        "requested_deliverable": "Privately inspect owner reply, complete the requested work if safe, and send a clear owner-visible response.",
        "human_owner_or_recipient": f"{reply.get('owner_label')} <{reply.get('owner_email')}>",
        "output_channel": "email",
        "proof_required": "later sent Message-ID plus domain proof, or one exact owner question/blocker",
        "due_or_next_update": "first worker focus within 2 minutes; result or exact blocker within 5 minutes",
        "escalation_path": "Direct responsible-worker nudge first; Task Manager escalation at 5 minutes; owner-visible exact blocker/question at 10 minutes if still no proof.",
        "papers_projection": "not_applicable",
    }
    if not args.task_flow_record_cmd.strip():
        return False, "Task Flow record command disabled"
    try:
        result = subprocess.run(
            shlex.split(args.task_flow_record_cmd),
            input=json.dumps({"event": "owner_reply_pending_response", "packet": packet}),
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
            cwd=Path(__file__).resolve().parents[1],
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, safe_text(error, 240)
    if result.returncode != 0:
        return False, safe_text(result.stderr or result.stdout, 240)
    return True, key


def direct_worker_session_for_reply(reply: dict) -> str:
    session_id = safe_text(reply.get("session_id"), 80)
    if session_id:
        return session_id
    return ""


def post_owner_reply_exact_blocker_email(args: argparse.Namespace, reply: dict, signature: str) -> tuple[bool, dict | str]:
    return False, (
        "owner email suppressed: newest-owner-reply gaps are internal execution repair items. "
        "Task Manager must push/focus the responsible worker and email the owner only if a real "
        "business, auth, security, or approval question remains."
    )


def reconcile_proof_backed_owner_reply_wrappers(args: argparse.Namespace, replies: list[dict], state: dict) -> dict:
    session_ids = []
    for reply in replies:
        if not reply.get("has_later_send"):
            continue
        session_id = safe_text(reply.get("session_id"), 80)
        if session_id:
            session_ids.append(session_id)
    session_ids = list(dict.fromkeys(session_ids))[: max(1, int(args.owner_reply_max_actions))]
    if not session_ids or not args.enable_owner_reply_wrapper_reconcile:
        return {"status": "disabled" if not args.enable_owner_reply_wrapper_reconcile else "checked", "changed": 0, "session_ids": []}
    ok, detail = post_workspaceboard_json(
        args,
        "/api/session-reconcile-stale",
        {"dry_run": False, "session_ids": session_ids},
    )
    changed = int(detail.get("changed") or 0) if isinstance(detail, dict) else 0
    payload = {
        "at": iso_now(),
        "ok": ok,
        "changed": changed,
        "session_ids": session_ids,
        "detail": detail if isinstance(detail, str) else "",
    }
    append_jsonl(Path(args.log_dir) / "owner-reply-wrapper-reconcile.jsonl", payload)
    return {"status": "checked" if ok else "failed", "changed": changed, "session_ids": session_ids, "error": "" if ok else safe_text(detail, 240)}


def owner_reply_followup_sweep(args: argparse.Namespace, classification: dict, state: dict) -> dict:
    if args.dry_run:
        return {"status": "disabled-dry-run", "checked": 0, "action": "none", "actions": []}
    if not args.enable_owner_reply_followup:
        return {"status": "disabled", "checked": 0, "action": "none", "actions": []}
    now = utc_now()
    now_epoch = int(time.time())
    task_manager_id = task_manager_session_id(classification)
    replies = collect_owner_replies(args)
    wrapper_reconcile = reconcile_proof_backed_owner_reply_wrappers(args, replies, state)
    due_replies = []
    for reply in replies:
        if reply.get("collector_error"):
            due_replies.append(reply)
            continue
        if reply.get("has_later_send"):
            continue
        age = seconds_since_time(reply.get("received_at"), now)
        if age is None or age < args.owner_reply_timeout_seconds:
            continue
        due_replies.append({**reply, "age_seconds": round(age, 1)})
    owner_state = state.setdefault("owner_reply_followups", {})
    thread_state = state.setdefault("owner_reply_thread_state", {})
    actions: list[dict] = []
    for reply in due_replies[: max(1, int(args.owner_reply_max_actions))]:
        signature = f"{reply.get('mailbox')}:{reply.get('source_message_id')}"
        record = owner_state.get(signature) if isinstance(owner_state.get(signature), dict) else {}
        first_seen_epoch = int(record.get("first_seen_epoch") or now_epoch)
        record.setdefault("first_seen_at", iso_now())
        record.setdefault("first_seen_epoch", first_seen_epoch)
        tf_ok, tf_detail = record_owner_reply_task_flow(args, reply)
        thread_state[signature] = {
            "updated_at": iso_now(),
            "mailbox": reply.get("mailbox"),
            "owner_email": reply.get("owner_email"),
            "subject": reply.get("subject"),
            "source_message_id": reply.get("source_message_id"),
            "latest_owner_received_at": reply.get("received_at").isoformat() if isinstance(reply.get("received_at"), datetime) else "",
            "latest_assistant_sent_after_owner": bool(reply.get("has_later_send")),
            "status": "owner_reply_pending_response",
            "task_flow_key": tf_detail if tf_ok else "",
            "task_flow_record_status": "recorded" if tf_ok else "failed",
            "task_flow_record_detail": "" if tf_ok else tf_detail,
        }
        if now_epoch - int(record.get("nudge_at_epoch") or 0) < args.owner_reply_cooldown_seconds:
            actions.append({
                "action": "cooldown",
                "mailbox": reply.get("mailbox"),
                "source_message_id": safe_text(reply.get("source_message_id"), 120),
                "subject": reply.get("subject"),
            })
            continue
        elapsed = now_epoch - first_seen_epoch
        target_session_id = direct_worker_session_for_reply(reply)
        task_flow_note = f"Task Flow: {tf_detail}." if tf_ok else f"Task Flow record failed: {tf_detail}."
        if reply.get("collector_error"):
            message = (
                "AI Health owner-reply follow-up sweep could not read one mailbox state adapter. "
                f"Mailbox: {reply.get('mailbox')}. Error: {reply.get('collector_error')}. "
                "Fix the adapter/runtime state path and rerun the owner reply follow-up sweep."
            )
        else:
            message = "\n".join([
                "AI Health owner-reply follow-up sweep: newest primary-owner reply has no later assistant response proof.",
                f"Mailbox: {reply.get('mailbox')}",
                f"Owner: {reply.get('owner_label')} <{reply.get('owner_email')}>",
                f"Subject: {reply.get('subject')}",
                f"Source Message-ID: {reply.get('source_message_id')}",
                f"Current route/session: {reply.get('route') or 'unknown'} / {reply.get('session_id') or 'not visible'}",
                task_flow_note,
                "",
                "Required action: focus or create the responsible worker now. Privately inspect the owner reply, do the requested domain work if safe, then send the owner a clear response with Message-ID and record Task Flow/domain proof.",
                "Valid return only: sent Message-ID plus domain proof, or one exact blocker/question. Do not close as routed, handled, active, or filed.",
            ])
        if target_session_id:
            ok, detail = post_session_message(args, target_session_id, message)
            action_name = "direct_worker_nudge"
        else:
            ok, detail = False, "no responsible worker session available"
            action_name = "direct_worker_nudge_failed"
        if task_manager_id and (not target_session_id or elapsed >= args.owner_reply_escalation_seconds):
            tm_ok, tm_detail = post_session_message(args, task_manager_id, message)
            detail = f"{detail}; Task Manager escalation: {tm_detail}"
            ok = ok or tm_ok
            if not target_session_id:
                action_name = "task_manager_nudge"
            elif elapsed >= args.owner_reply_escalation_seconds:
                action_name = "direct_worker_and_task_manager_nudge"
        email_detail: dict | str = ""
        email_ok = False
        if elapsed >= args.owner_reply_email_seconds:
            email_ok, email_detail = post_owner_reply_exact_blocker_email(args, reply, f"ai-health-owner-reply:{signature}")
            detail = f"{detail}; owner email escalation: {email_detail if isinstance(email_detail, str) else email_detail.get('message_id', '')}"
        record.update({
            "nudge_at": iso_now(),
            "nudge_at_epoch": now_epoch,
            "mailbox": reply.get("mailbox"),
            "subject": reply.get("subject"),
            "owner_email": reply.get("owner_email"),
            "source_message_id": reply.get("source_message_id"),
            "target_session_id": target_session_id,
            "task_flow_key": tf_detail if tf_ok else "",
            "elapsed_seconds": elapsed,
            "status": "sent" if ok else "failed",
            "detail": detail,
            "owner_email_escalation_status": "sent" if email_ok else ("not-due" if elapsed < args.owner_reply_email_seconds else "failed"),
            "owner_email_escalation_detail": email_detail if isinstance(email_detail, str) else {
                "message_id": email_detail.get("message_id"),
                "recipient": email_detail.get("recipient"),
            },
        })
        owner_state[signature] = record
        action = {
            "at": iso_now(),
            "action": action_name,
            "ok": ok,
            "mailbox": reply.get("mailbox"),
            "owner_email": reply.get("owner_email"),
            "subject": reply.get("subject"),
            "source_message_id": safe_text(reply.get("source_message_id"), 140),
            "session_id": reply.get("session_id", ""),
            "target_session_id": target_session_id,
            "task_flow_key": tf_detail if tf_ok else "",
            "elapsed_seconds": elapsed,
            "owner_email_escalated": email_ok,
            "detail": detail,
        }
        actions.append(action)
        append_jsonl(Path(args.log_dir) / "owner-reply-followups.jsonl", action)
    return {
        "status": "checked",
        "checked": len(replies),
        "due": len(due_replies),
        "action": "+".join(dict.fromkeys(action["action"] for action in actions)) if actions else "none",
        "wrapper_reconcile": wrapper_reconcile,
        "actions": actions[:20],
    }


def task_manager_session_id(classification: dict) -> str:
    sessions = classification.get("standing_monitors", {}).get("Task Manager", [])
    if not sessions:
        return ""
    return str(sessions[0].get("id") or "")


def post_session_message(args: argparse.Namespace, session_id: str, message: str) -> tuple[bool, str]:
    payload = json.dumps({"session_id": session_id, "message": message, "wait_ms": 700}).encode("utf-8")
    request = urllib.request.Request(
        args.message_url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    request_timeout = min(float(args.timeout), MAX_BOARD_REQUEST_TIMEOUT_SECONDS)
    try:
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            return response.status == 200, f"HTTP {response.status}"
    except (TimeoutError, OSError, urllib.error.URLError) as error:
        return False, safe_text(error, 240)


def workspaceboard_endpoint(args: argparse.Namespace, path: str) -> str:
    return urllib.parse.urljoin(args.status_url.rsplit("/", 2)[0] + "/", path.lstrip("/"))


def post_workspaceboard_json(args: argparse.Namespace, path: str, payload: dict) -> tuple[bool, dict | str]:
    request = urllib.request.Request(
        workspaceboard_endpoint(args, path),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    request_timeout = min(float(args.timeout), MAX_BOARD_REQUEST_TIMEOUT_SECONDS)
    try:
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
            return response.status == 200 and bool(parsed.get("ok")), parsed
    except (TimeoutError, OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        return False, safe_text(error, 240)


def fetch_workspaceboard_json(args: argparse.Namespace, path: str) -> tuple[bool, dict | str]:
    request = urllib.request.Request(
        workspaceboard_endpoint(args, path),
        headers={"Accept": "application/json"},
        method="GET",
    )
    request_timeout = min(float(args.timeout), MAX_BOARD_REQUEST_TIMEOUT_SECONDS)
    try:
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
            return response.status == 200 and bool(parsed.get("ok")), parsed
    except (TimeoutError, OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        return False, safe_text(error, 240)


def session_sprawl_governor(args: argparse.Namespace, classification: dict, management_health: dict, state: dict) -> dict:
    if not args.enable_session_sprawl_governor:
        return {"status": "disabled", "action": "none", "changed": 0}
    non_standing_open = int(management_health.get("non_standing_open_count") or 0)
    governor_state = state.setdefault("session_sprawl_governor", {})
    now_epoch = int(time.time())
    if (
        not args.dry_run
        and now_epoch - int(governor_state.get("last_run_epoch") or 0) < args.session_sprawl_governor_interval_seconds
    ):
        return {
            "status": "cooldown",
            "action": "none",
            "changed": 0,
            "non_standing_open": non_standing_open,
            "last_run_at": governor_state.get("last_run_at", ""),
        }
    candidate_ids = []
    for bucket in (
        "review_ready_sessions",
        "stale_waiting_sessions",
        "stale_working_sessions",
        "active_waiting_sessions",
    ):
        for item in classification.get(bucket, []):
            session_id = safe_text(item.get("id"), 80)
            if session_id:
                candidate_ids.append(session_id)
    desired_batch = max(
        1,
        min(
            24,
            max(
                int(args.session_sprawl_governor_batch_size),
                8 if non_standing_open < 24 else non_standing_open // 3,
            ),
        ),
    )
    candidate_ids = list(dict.fromkeys(candidate_ids))[: desired_batch]
    if non_standing_open <= args.max_non_standing_open and not candidate_ids:
        return {
            "status": "checked",
            "action": "none",
            "changed": 0,
            "non_standing_open": non_standing_open,
            "candidate_count": 0,
        }
    ok, detail = post_workspaceboard_json(
        args,
        "/api/session-reconcile-stale",
        {"dry_run": bool(args.dry_run), "session_ids": candidate_ids},
    )
    changed = 0
    actions: list[dict] = []
    if isinstance(detail, dict):
        changed = int(detail.get("changed") or 0)
        actions = [item for item in detail.get("actions", []) if isinstance(item, dict)]
    governor_state["last_run_at"] = iso_now()
    governor_state["last_run_epoch"] = now_epoch
    governor_state["last_status"] = "checked" if ok else "failed"
    governor_state["last_changed"] = changed
    governor_state["last_error"] = "" if ok else safe_text(detail, 240)
    payload = {
        "at": iso_now(),
        "ok": ok,
        "dry_run": bool(args.dry_run),
        "non_standing_open": non_standing_open,
        "candidate_ids": candidate_ids,
        "changed": changed,
        "actions": actions[:20],
        "detail": detail if isinstance(detail, str) else "",
    }
    append_jsonl(Path(args.log_dir) / "session-sprawl-governor.jsonl", payload)
    return {
        "status": "checked" if ok else "failed",
        "action": "reconcile-stale" if ok else "failed",
        "changed": changed,
        "non_standing_open": non_standing_open,
        "candidate_count": len(candidate_ids),
        "candidate_ids": candidate_ids,
        "actions": actions[:20],
        "error": "" if ok else safe_text(detail, 240),
    }


def canonical_status_line(report: dict) -> str:
    board = "board ok" if report.get("board", {}).get("ok") else "board down"
    management = report.get("management_health", {})
    finish = report.get("finish_contract_audit", {})
    canaries = report.get("mailbox_canaries", {})
    sprawl = report.get("session_sprawl_governor", {})
    session_restart = report.get("session_restart", {})
    send_path = report.get("send_path_health", {})
    owner_replies = report.get("owner_reply_followup_sweep", {})
    parts = [
        board,
        f"{management.get('non_standing_open_count', 0)} open work sessions",
        f"{management.get('standing_attention_count', 0)} standing attention",
        f"{finish.get('missing_finish_contract_count', 0)} proof/finish gaps",
        f"{finish.get('past_due_routed_count', 0)} past-due routed",
        f"{owner_replies.get('due', 0)} owner replies needing follow-up",
        f"{canaries.get('issue_count', 0)} mailbox canary issues",
        f"{send_path.get('issue_count', 0)} send-path issues",
        f"sprawl governor {sprawl.get('action', 'none')} changed {sprawl.get('changed', 0)}",
        f"session restart {session_restart.get('status', 'not-recorded')} action {session_restart.get('action', 'none')}",
    ]
    return "; ".join(parts)


def post_owner_escalation_email(args: argparse.Namespace, item: dict, record: dict) -> tuple[bool, dict | str]:
    user_id, recipient, owner_label = owner_for_task_flow_item(item)
    dedupe_key = safe_text(item.get("dedupe_key"), 140)
    worker = safe_text(item.get("responsible_worker_or_persona") or item.get("owner_lane"), 160)
    deliverable = safe_text(item.get("requested_deliverable") or item.get("title") or dedupe_key, 140)
    subject = f"Action needed: {deliverable or 'AI Manager item'}"
    body = "\n".join([
        f"Hi {owner_label},",
        "",
        f"I do not have completion proof for this item yet: {deliverable or dedupe_key}.",
        "",
        "Current status:",
        f"- Responsible worker: {worker or 'unknown'}",
        f"- Task status: {safe_text(item.get('status'), 60) or 'unknown'}",
        f"- First server-side nudge: {record.get('nudge_at', '') or 'not recorded'}",
        "",
        "Response needed:",
        "Please reply only with the missing detail/approval if it is not available from Task Flow, Workspaceboard, Google Drive, OPS, Portal/CRM, Salesreport, BID/finance records, sent logs, mailbox metadata, or project notes. If no owner decision is needed, the worker must return the completed result with proof or one exact blocker.",
        "",
        f"Trace: {dedupe_key}",
    ])
    payload = json.dumps({
        "user_id": user_id,
        "user_label": owner_label,
        "user_email": recipient,
        "subject": subject,
        "message": body,
        "route_signature": f"ai-health-task-flow:{dedupe_key}",
    }).encode("utf-8")
    endpoint = workspaceboard_endpoint(args, "api/ai-manager/escalation-email")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
            return response.status == 200 and bool(parsed.get("ok")), parsed
    except (urllib.error.URLError, json.JSONDecodeError) as error:
        return False, safe_text(error, 240)


def worker_summary_needs_owner_email(summary: str) -> tuple[bool, str]:
    text = " ".join(str(summary or "").split())
    lowered = text.lower()
    if not text:
        return False, ""
    if "exact blocker" in lowered:
        return True, "exact blocker"
    if "no owner-visible completion proof" in lowered:
        return True, "missing owner-visible proof"
    if "proof recorded" in lowered and ("email missing" in lowered or "no email was sent" in lowered):
        return True, "proof recorded but email missing"
    if "no sent message-id" in lowered or "no sent message id" in lowered:
        return True, "missing sent Message-ID"
    if "no new corrected" in lowered and "email" in lowered:
        return True, "corrected email missing"
    return False, ""


def worker_summary_needs_owner_response(summary: str) -> bool:
    text = str(summary or "").strip()
    lowered = " ".join(text.lower().split())
    if not lowered or "?" not in text:
        return False
    explicit_markers = (
        "question:",
        "response needed:",
        "please answer",
        "please confirm",
        "can you confirm",
        "reply approve",
        "reply decline",
        "should i ",
        "should we ",
    )
    if "approve or decline" in lowered or "approve/decline" in lowered:
        return True
    owner_markers = (" robert", " sonat", " owner", " you ", " your ")
    if not any(marker in lowered for marker in explicit_markers):
        return False
    if not any(marker in f" {lowered} " for marker in owner_markers):
        return False
    return summary_has_source_exhaustion(summary) or summary_has_real_human_gate(summary)


def compact_owner_summary(summary: str, limit: int = 1200) -> str:
    text = str(summary or "").replace("\r\n", "\n").strip()
    if not text:
        return ""
    drop_prefixes = (
        "what is true:",
        "what that means:",
        "so the useful answer is:",
        "what should happen next:",
    )
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.lower() in drop_prefixes:
            continue
        if line.lower().startswith(("ran ", "explored ", "working (", "terminal readback loaded")):
            continue
        if len(line) > 220:
            line = line[:217].rstrip() + "..."
        lines.append(line)
    if not lines:
        lines = [" ".join(text.split())]
    compact = "\n".join(lines)
    return compact[:limit].rstrip()


def response_ask_for_worker_summary(reason: str) -> str:
    if "email" in reason.lower() or "message" in reason.lower():
        return "Please reply only if the recipient/thread cannot be determined from Task Flow, sent logs, mailbox metadata, OPS, Portal, Salesreport, Google Drive, or project notes. Otherwise the responsible worker must send the missing owner-visible email and record the Message-ID."
    if "blocker" in reason.lower():
        return "Please reply with the missing detail or approval only if the blocker remains after the worker checks the available source systems. If it does not require you, the responsible worker must fix it and return completion proof."
    return "Please reply with the missing detail/approval only if it is unavailable from existing source systems. If no owner decision is needed, the worker must return completion proof or one exact blocker."


def worker_summary_owner_for_session(session: dict, summary: str) -> tuple[int, str, str]:
    text = " ".join([
        str(session.get("title") or ""),
        str(session.get("display_name") or ""),
        str(session.get("workspace") or ""),
        str(summary or ""),
    ]).lower()
    if "sonat" in text or "avignon" in text:
        return 3, OWNER_EMAIL_BY_USER_ID[3], "Sonat"
    if "mark" in text:
        return 21, OWNER_EMAIL_BY_USER_ID[21], "Mark"
    if "sebastian" in text:
        return 144, OWNER_EMAIL_BY_USER_ID[144], "Sebastian"
    if "dmytro" in text:
        return 165, OWNER_EMAIL_BY_USER_ID[165], "Dmytro"
    return 1, OWNER_EMAIL_BY_USER_ID[1], "Robert"


def post_worker_summary_escalation_email(
    args: argparse.Namespace,
    session: dict,
    summary: str,
    reason: str,
    signature: str,
) -> tuple[bool, dict | str]:
    user_id, recipient, owner_label = worker_summary_owner_for_session(session, summary)
    title = safe_text(session.get("title") or session.get("display_name") or session.get("id"), 120)
    subject_prefix = "Blocker" if "blocker" in reason else "Status"
    readable_summary = compact_owner_summary(summary)
    payload = {
        "user_id": user_id,
        "user_label": owner_label,
        "user_email": recipient,
        "subject": f"{subject_prefix}: {title}",
        "message": "\n".join([
            f"Hi {owner_label},",
            "",
            f"This item needs follow-up: {title}.",
            "",
            f"Why this email was sent: {reason}.",
            "",
            "Current readback:",
            readable_summary or "The worker returned a proof gap, but no readable summary was available.",
            "",
            "Response needed:",
            response_ask_for_worker_summary(reason),
            "",
            "This email was sent automatically because the worker returned a blocker/proof gap instead of owner-visible completion proof.",
        ]),
        "route_signature": signature,
    }
    return post_workspaceboard_json(args, "api/ai-manager/escalation-email", payload)


def worker_summary_escalation_sweep(args: argparse.Namespace, classification: dict, state: dict) -> dict:
    if args.dry_run:
        return {"status": "disabled-dry-run", "checked": 0, "emails_sent": 0, "actions": []}
    if not args.enable_worker_summary_escalation:
        return {"status": "disabled", "checked": 0, "emails_sent": 0, "actions": []}
    now_epoch = int(time.time())
    escalation_state = state.setdefault("worker_summary_escalations", {})
    candidate_sessions = []
    for bucket in ("stale_waiting_sessions", "active_waiting_sessions", "review_ready_sessions"):
        for item in classification.get(bucket, []):
            session_id = safe_text(item.get("id"), 80)
            if session_id:
                candidate_sessions.append(item)
    deduped: dict[str, dict] = {}
    for item in candidate_sessions:
        deduped.setdefault(str(item.get("id") or ""), item)
    actions: list[dict] = []
    checked = 0
    emails_sent = 0
    task_manager_id = task_manager_session_id(classification)
    for session in list(deduped.values())[: max(1, int(args.worker_summary_escalation_scan_limit))]:
        if emails_sent >= args.worker_summary_escalation_max_emails:
            break
        session_id = safe_text(session.get("id"), 80)
        ok, detail = fetch_workspaceboard_json(
            args,
            f"api/session-summary?session_id={urllib.parse.quote(session_id)}",
        )
        checked += 1
        if not ok or not isinstance(detail, dict):
            actions.append({"session_id": session_id, "action": "summary_failed", "ok": False, "detail": safe_text(detail, 180)})
            if "timed out" in safe_text(detail, 180).lower():
                break
            continue
        summary = safe_text(detail.get("summary"), 2800)
        needs_email, reason = worker_summary_needs_owner_email(summary)
        if not needs_email:
            actions.append({"session_id": session_id, "action": "no_owner_email_needed", "ok": True})
            continue
        signature_hash = __import__("hashlib").sha256(summary.encode("utf-8")).hexdigest()[:16]
        signature = f"ai-health-worker-summary:{session_id}:{signature_hash}"
        record = escalation_state.get(signature) if isinstance(escalation_state.get(signature), dict) else {}
        if now_epoch - int(record.get("email_at_epoch") or 0) < args.worker_summary_escalation_cooldown_seconds:
            actions.append({"session_id": session_id, "action": "cooldown", "ok": True, "reason": reason})
            continue
        if not worker_summary_needs_owner_response(summary):
            title = safe_text(session.get("title") or session.get("display_name") or session_id, 140)
            message = (
                "AI Health worker-summary proof repair: this worker returned a blocker/proof gap, but it is not a real owner-response email. "
                f"Session: {session_id}. Title: {title}. Reason: {reason}. "
                "Push/focus the responsible worker and return only completed proof, one exact blocker the worker can fix, or one explicit owner question with answer choices. "
                f"{source_first_directive()} "
                "Do not email Robert for generic internal proof gaps."
            )
            if task_manager_id:
                nudge_ok, nudge_detail = post_session_message(args, task_manager_id, message)
            else:
                nudge_ok, nudge_detail = False, "no Task Manager session available"
            escalation_state[signature] = {
                "nudge_at": iso_now(),
                "nudge_at_epoch": now_epoch,
                "session_id": session_id,
                "title": session.get("title", ""),
                "reason": reason,
                "status": "task-manager-nudged" if nudge_ok else "task-manager-nudge-failed",
                "detail": nudge_detail,
            }
            action = {
                "session_id": session_id,
                "action": "task_manager_nudge",
                "ok": nudge_ok,
                "reason": reason,
                "detail": nudge_detail,
            }
            actions.append(action)
            append_jsonl(Path(args.log_dir) / "worker-summary-escalations.jsonl", {"at": iso_now(), **action})
            continue
        email_ok, email_detail = post_worker_summary_escalation_email(args, session, summary, reason, signature)
        escalation_state[signature] = {
            "email_at": iso_now(),
            "email_at_epoch": now_epoch,
            "session_id": session_id,
            "title": session.get("title", ""),
            "reason": reason,
            "status": "sent" if email_ok else "failed",
            "detail": email_detail if isinstance(email_detail, str) else {
                "recipient": email_detail.get("recipient"),
                "message_id": email_detail.get("message_id"),
                "from": email_detail.get("from"),
            },
        }
        action = {
            "session_id": session_id,
            "action": "email",
            "ok": email_ok,
            "reason": reason,
            "detail": escalation_state[signature]["detail"],
        }
        actions.append(action)
        append_jsonl(Path(args.log_dir) / "worker-summary-escalations.jsonl", {"at": iso_now(), **action})
        if email_ok:
            emails_sent += 1
    return {
        "status": "checked",
        "checked": checked,
        "emails_sent": emails_sent,
        "actions": actions[:20],
    }


def task_flow_escalation_sweep(args: argparse.Namespace, classification: dict, state: dict, report: dict | None = None) -> dict:
    if args.dry_run:
        return {"status": "disabled-dry-run", "checked": 0, "action": "none"}
    if not args.enable_task_flow_escalation:
        return {"status": "disabled", "checked": 0, "action": "none"}
    if report is None:
        report = run_task_flow_report(args.task_flow_report_cmd, args.timeout)
    if report.get("status") in {"disabled", "failed"}:
        return {"status": report.get("status", "failed"), "checked": 0, "action": "none", "error": report.get("error", "")}
    items = [item for item in report.get("items", []) if isinstance(item, dict)]
    candidates = [item for item in items if task_flow_needs_escalation(item)]
    escalation_state = state.setdefault("task_flow_escalations", {})
    now_epoch = int(time.time())
    task_manager_id = task_manager_session_id(classification)
    checked = len(candidates)
    actions: list[dict] = []
    email_count = 0

    def refresh_record(item: dict, dedupe_key: str) -> dict:
        record = escalation_state.get(dedupe_key) if isinstance(escalation_state.get(dedupe_key), dict) else {}
        record.setdefault("first_seen_at", iso_now())
        record.setdefault("first_seen_epoch", now_epoch)
        record["last_seen_at"] = iso_now()
        record["last_status"] = safe_text(item.get("status"), 80)
        record["owner_lane"] = safe_text(item.get("owner_lane"), 120)
        record["responsible_worker_or_persona"] = safe_text(item.get("responsible_worker_or_persona"), 160)
        escalation_state[dedupe_key] = record
        return record

    def append_action(action: str, dedupe_key: str, ok: bool, detail: object) -> None:
        payload = {
            "at": iso_now(),
            "action": action,
            "dedupe_key": dedupe_key,
            "ok": ok,
            "detail": detail,
        }
        actions.append(payload)
        append_jsonl(Path(args.log_dir) / "task-flow-escalations.jsonl", payload)

    keyed_candidates: list[tuple[str, dict, dict]] = []
    for item in candidates:
        dedupe_key = safe_text(item.get("dedupe_key"), 160)
        if not dedupe_key:
            continue
        record = refresh_record(item, dedupe_key)
        keyed_candidates.append((dedupe_key, item, record))

    # First revisit already-nudged rows whose timeout has expired. This prevents
    # a big backlog from starving the owner-visible email/blocker step.
    for dedupe_key, item, record in keyed_candidates:
        if now_epoch - int(record.get("email_at_epoch") or 0) < args.task_flow_escalation_cooldown_seconds:
            continue
        if now_epoch - int(record.get("timeout_escalation_epoch") or 0) < args.task_flow_escalation_cooldown_seconds:
            continue
        if not record.get("nudge_at_epoch"):
            continue
        if now_epoch - int(record.get("nudge_at_epoch") or 0) < args.task_flow_escalation_timeout_seconds:
            continue
        if task_manager_id:
            message = (
                "AI Health escalation timeout: this Task Flow item is still missing owner-visible proof after the first nudge, "
                "but do not email the owner unless there is one explicit human question with answer choices. "
                f"Task Flow key: {dedupe_key}. "
                f"Responsible worker: {record.get('responsible_worker_or_persona') or record.get('owner_lane') or 'unknown'}. "
                f"{source_first_directive()} "
                "Fix internally, produce completion proof, or return one plain owner question with Approve/Decline or exact choices."
            )
            ok, detail = post_session_message(args, task_manager_id, message)
        else:
            ok, detail = False, "no Task Manager session available for timeout escalation"
        record["timeout_escalation_at"] = iso_now()
        record["timeout_escalation_epoch"] = now_epoch
        record["timeout_escalation_status"] = "task-manager-nudged" if ok else "failed"
        record["timeout_escalation_detail"] = detail
        escalation_state[dedupe_key] = record
        append_action("timeout_task_manager_nudge", dedupe_key, ok, detail)
        if len(actions) >= args.task_flow_escalation_max_actions or email_count >= args.task_flow_escalation_max_emails:
            return {
                "status": "checked",
                "checked": checked,
                "action": "+".join(dict.fromkeys(action["action"] for action in actions)),
                "actions": actions,
            }

    for dedupe_key, item, record in keyed_candidates:
        if len(actions) >= args.task_flow_escalation_max_actions:
            break
        if record.get("nudge_at_epoch"):
            continue
        if now_epoch - int(record.get("email_at_epoch") or 0) < args.task_flow_escalation_cooldown_seconds:
            continue
        if not task_manager_id:
            record["last_error"] = "no Task Manager session available for nudge"
            escalation_state[dedupe_key] = record
            continue
        message = (
            "AI Health Manager proof sweep: this Task Flow item was filed/routed but still lacks owner-visible completion proof or one exact blocker. "
            f"Task Flow key: {dedupe_key}. "
            f"Responsible worker: {record.get('responsible_worker_or_persona') or record.get('owner_lane') or 'unknown'}. "
            f"{source_first_directive()} "
            "Push the responsible worker now. Do not return routed/working/handled. Return only completed proof, one exact blocker, or one owner question."
        )
        ok, detail = post_session_message(args, task_manager_id, message)
        record["nudge_at"] = iso_now()
        record["nudge_at_epoch"] = now_epoch
        record["nudge_status"] = "sent" if ok else "failed"
        record["nudge_detail"] = detail
        escalation_state[dedupe_key] = record
        append_action("nudge", dedupe_key, ok, detail)

    if actions:
        return {
            "status": "checked",
            "checked": checked,
            "action": "+".join(dict.fromkeys(action["action"] for action in actions)),
            "actions": actions,
        }
    return {"status": "checked", "checked": checked, "action": "none"}


def proof_repair_queue(args: argparse.Namespace, classification: dict, state: dict, finish_audit: dict) -> dict:
    if args.dry_run:
        return {"status": "disabled-dry-run", "queued": 0, "action": "none"}
    if not args.enable_proof_repair_queue:
        return {"status": "disabled", "queued": 0, "action": "none"}
    items = [item for item in finish_audit.get("items", []) if isinstance(item, dict)]
    if not items:
        return {"status": "checked", "queued": 0, "action": "none"}
    task_manager_id = task_manager_session_id(classification)
    if not task_manager_id:
        return {"status": "blocked", "queued": 0, "action": "none", "reason": "no Task Manager session available"}
    repair_state = state.setdefault("proof_repair_queue", {})
    now_epoch = int(time.time())
    if now_epoch - int(repair_state.get("last_batch_epoch") or 0) < args.proof_repair_interval_seconds:
        return {
            "status": "cooldown",
            "queued": 0,
            "action": "none",
            "next_index": int(repair_state.get("next_index") or 0),
        }
    batch_size = max(1, int(args.proof_repair_batch_size))
    start = int(repair_state.get("next_index") or 0) % len(items)
    ordered = items[start:] + items[:start]
    batch = ordered[:batch_size]
    next_index = (start + len(batch)) % len(items)
    lines = [
        "AI Health proof repair queue batch.",
        "Repair or park each item below. For each one, write the missing finish contract, attach existing proof, reopen/focus the responsible worker, or record one exact blocker. Do not ask Robert unless a real owner decision is required.",
        source_first_directive(),
        "",
    ]
    for index, item in enumerate(batch, 1):
        missing = ", ".join(item.get("missing_fields") or [])
        title = item.get("title") or item.get("reason") or "untitled"
        lines.append(
            f"{index}. {item.get('dedupe_key')} [{item.get('status')}] "
            f"{title} | worker: {item.get('responsible_worker_or_persona') or item.get('owner_lane') or 'unknown'} | missing: {missing}"
        )
    lines.extend([
        "",
        "Return a concise repair readback with item keys and action taken: closed with proof, blocked with exact blocker, waiting with next check, or still needs source recovery.",
    ])
    ok, detail = post_session_message(args, task_manager_id, "\n".join(lines))
    repair_state["last_batch_at"] = iso_now()
    repair_state["last_batch_epoch"] = now_epoch
    repair_state["next_index"] = next_index
    repair_state["last_batch_keys"] = [safe_text(item.get("dedupe_key"), 160) for item in batch]
    repair_state["last_status"] = "sent" if ok else "failed"
    repair_state["last_detail"] = detail
    payload = {
        "at": iso_now(),
        "action": "repair_batch",
        "ok": ok,
        "detail": detail,
        "start_index": start,
        "next_index": next_index,
        "keys": repair_state["last_batch_keys"],
    }
    append_jsonl(Path(args.log_dir) / "proof-repair-queue.jsonl", payload)
    return {
        "status": "checked",
        "queued": len(batch),
        "action": "repair_batch",
        "ok": ok,
        "detail": detail,
        "start_index": start,
        "next_index": next_index,
        "keys": repair_state["last_batch_keys"],
    }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# AI Health Manager Check",
        "",
        f"- checked_at: `{report['checked_at']}`",
        f"- canonical_status: {report.get('canonical_status_line', '')}",
        f"- status_url: `{report['status_url']}`",
        f"- board: `{report['board'].get('host', '')}` / version `{report['board'].get('board_version', '')}`",
        f"- cadence: `{report['cadence_seconds']}s`",
        f"- mode: `{'dry-run/no-mutation' if report['dry_run'] else 'active'}`",
        f"- board_remediation: `{report.get('board_remediation', {}).get('status', 'not-recorded')}`",
        f"- nudge: `{report['nudge']['status']}`",
        f"- session_restart: `{report.get('session_restart', {}).get('status', 'not-recorded')}` / action `{report.get('session_restart', {}).get('action', 'none')}` / inactive_minutes `{report.get('session_restart', {}).get('inactive_minutes', '')}`",
        f"- standing_attention: `{report.get('management_health', {}).get('standing_attention_count', 0)}` / minutes `{report.get('standing_attention_minutes', DEFAULT_STANDING_ATTENTION_MINUTES)}`",
        f"- missed_input_audit: `{report.get('daily_input_audit', {}).get('status', 'not-recorded')}` / missing `{report.get('daily_input_audit', {}).get('missing_tracking_count', 0)}`",
        f"- finish_contract_audit: `{report.get('finish_contract_audit', {}).get('status', 'not-recorded')}` / missing `{report.get('finish_contract_audit', {}).get('missing_finish_contract_count', 0)}` / missing_proof `{report.get('finish_contract_audit', {}).get('missing_proof_count', 0)}`",
        f"- task_flow_escalation_sweep: `{report.get('task_flow_escalation_sweep', {}).get('status', 'not-recorded')}` / action `{report.get('task_flow_escalation_sweep', {}).get('action', 'none')}` / checked `{report.get('task_flow_escalation_sweep', {}).get('checked', 0)}`",
        f"- gmail_push_consumer: `{report.get('gmail_push_consumer', {}).get('status', 'not-recorded')}` / pulled `{report.get('gmail_push_consumer', {}).get('pulled', 0)}`",
        f"- owner_reply_followup_sweep: `{report.get('owner_reply_followup_sweep', {}).get('status', 'not-recorded')}` / due `{report.get('owner_reply_followup_sweep', {}).get('due', 0)}` / action `{report.get('owner_reply_followup_sweep', {}).get('action', 'none')}`",
        f"- worker_summary_escalation_sweep: `{report.get('worker_summary_escalation_sweep', {}).get('status', 'not-recorded')}` / emails `{report.get('worker_summary_escalation_sweep', {}).get('emails_sent', 0)}` / checked `{report.get('worker_summary_escalation_sweep', {}).get('checked', 0)}`",
        f"- proof_repair_queue: `{report.get('proof_repair_queue', {}).get('status', 'not-recorded')}` / action `{report.get('proof_repair_queue', {}).get('action', 'none')}` / queued `{report.get('proof_repair_queue', {}).get('queued', 0)}`",
        f"- mailbox_canaries: `{report.get('mailbox_canaries', {}).get('status', 'not-recorded')}` / issues `{report.get('mailbox_canaries', {}).get('issue_count', 0)}`",
        f"- send_path_health: `{report.get('send_path_health', {}).get('status', 'not-recorded')}` / issues `{report.get('send_path_health', {}).get('issue_count', 0)}`",
        f"- session_sprawl_governor: `{report.get('session_sprawl_governor', {}).get('status', 'not-recorded')}` / action `{report.get('session_sprawl_governor', {}).get('action', 'none')}` / changed `{report.get('session_sprawl_governor', {}).get('changed', 0)}`",
        "",
        "## Session Counts",
        f"- standing: `{report['management_health']['standing_count']}`",
        f"- standing_attention: `{report['management_health'].get('standing_attention_count', 0)}`",
        f"- active: `{report['management_health']['active_working_count']}`",
        f"- review_ready: `{report['management_health']['review_ready_count']}`",
        f"- stale_working: `{report['management_health']['stale_working_count']}`",
        f"- stale_waiting: `{report['management_health']['stale_waiting_count']}`",
        f"- active_waiting: `{report['management_health']['active_waiting_count']}`",
        f"- non_standing_open: `{report['management_health']['non_standing_open_count']}`",
        f"- robert_blockers: `{report['management_health']['robert_blocker_count']}`",
        "",
        "## Management Health",
    ]
    for issue in report["management_health"]["issues"]:
        lines.append(
            f"- `{issue['id']}` {issue['title']}: {issue['reason']}. Task Manager: {issue['task_manager_action']}"
        )
    if not report["management_health"]["issues"]:
        lines.append("- no session-sprawl management issue detected")
    standing_attention = report.get("classification", {}).get("standing_attention_sessions", [])
    lines.extend([
        "",
        "## Standing Session Attention",
        f"- minutes: `{report.get('standing_attention_minutes', DEFAULT_STANDING_ATTENTION_MINUTES)}`",
        f"- sessions: `{len(standing_attention)}`",
    ])
    for item in standing_attention[:20]:
        lines.append(
            f"- `{item.get('id', '')}` {item.get('title', '')} [{item.get('status', '')}/{item.get('runtime', '')}] {item.get('reason', '')}"
        )
    sprawl = report.get("session_sprawl_governor", {})
    lines.extend([
        "",
        "## Session Sprawl Governor",
        f"- status: `{sprawl.get('status', 'not-recorded')}`",
        f"- action: `{sprawl.get('action', 'none')}`",
        f"- changed: `{sprawl.get('changed', 0)}`",
        f"- non_standing_open: `{sprawl.get('non_standing_open', '')}`",
        f"- candidates: `{sprawl.get('candidate_count', '')}`",
    ])
    for session_id in sprawl.get("candidate_ids", [])[:10]:
        lines.append(f"- candidate `{session_id}`")
    for action in sprawl.get("actions", [])[:10]:
        lines.append(
            f"- `{action.get('session_id', '')}` {action.get('action', '')}: {action.get('title', '')} ({action.get('reason', '')})"
        )
    restart = report.get("session_restart", {})
    lines.extend([
        "",
        "## Session Restart",
        f"- status: `{restart.get('status', 'not-recorded')}`",
        f"- action: `{restart.get('action', 'none')}`",
        f"- session_id: `{restart.get('session_id', '')}`",
        f"- inactive_minutes: `{restart.get('inactive_minutes', '')}`",
        f"- reason: `{restart.get('reason', '')}`",
    ])
    if restart.get("detail"):
        lines.append(f"- detail: {restart.get('detail')}")
    send_path = report.get("send_path_health", {})
    lines.extend([
        "",
        "## Send Path Health",
        f"- status: `{send_path.get('status', 'not-recorded')}`",
        f"- checked: `{send_path.get('checked', 0)}`",
        f"- recent_hours: `{send_path.get('recent_hours', '')}`",
        f"- issues: `{send_path.get('issue_count', 0)}`",
    ])
    for issue in send_path.get("issues", [])[:10]:
        lines.append(f"- `{issue.get('file', '')}`: {issue.get('reason', '')}")
    input_audit = report.get("daily_input_audit", {})
    lines.extend([
        "",
        "## Missed Input Audit",
        f"- status: `{input_audit.get('status', 'not-recorded')}`",
        f"- interval_seconds: `{input_audit.get('interval_seconds', '')}`",
        f"- sections_checked: `{input_audit.get('section_count', 0)}`",
        f"- missing_tracking: `{input_audit.get('missing_tracking_count', 0)}`",
        f"- nudge: `{input_audit.get('nudge_status', 'not-recorded')}`",
    ])
    for item in input_audit.get("missing_tracking", [])[:10]:
        lines.append(f"- `{item.get('heading', '')}` in `{item.get('file', '')}`: {item.get('reason', '')}")
    finish_audit = report.get("finish_contract_audit", {})
    lines.extend([
        "",
        "## Finish Contract Audit",
        f"- status: `{finish_audit.get('status', 'not-recorded')}`",
        f"- items_checked: `{finish_audit.get('items_checked', 0)}`",
        f"- missing_finish_contract: `{finish_audit.get('missing_finish_contract_count', 0)}`",
        f"- missing_closed_proof: `{finish_audit.get('missing_proof_count', 0)}`",
        f"- email_inbox_after_closeout: `{finish_audit.get('email_inbox_after_closeout_count', 0)}`",
        f"- past_due_routed: `{finish_audit.get('past_due_routed_count', 0)}`",
        f"- vague_robert_decisions: `{finish_audit.get('vague_robert_decision_count', 0)}`",
    ])
    if finish_audit.get("error"):
        lines.append(f"- error: {finish_audit.get('error')}")
    for item in finish_audit.get("items", [])[:15]:
        fields = ", ".join(item.get("missing_fields", []))
        lines.append(f"- `{item.get('dedupe_key', '')}` [{item.get('status', '')}]: missing {fields}")
    sweep = report.get("task_flow_escalation_sweep", {})
    lines.extend([
        "",
        "## Task Flow Escalation Sweep",
        f"- status: `{sweep.get('status', 'not-recorded')}`",
        f"- action: `{sweep.get('action', 'none')}`",
        f"- checked: `{sweep.get('checked', 0)}`",
        f"- dedupe_key: `{sweep.get('dedupe_key', '')}`",
        f"- ok: `{sweep.get('ok', '')}`",
    ])
    for action in sweep.get("actions", [])[:10]:
        lines.append(f"- `{action.get('action', '')}` `{action.get('dedupe_key', '')}` ok=`{action.get('ok', '')}`")
    gmail_push = report.get("gmail_push_consumer", {})
    lines.extend([
        "",
        "## Gmail Push Consumer",
        f"- status: `{gmail_push.get('status', 'not-recorded')}`",
        f"- pulled: `{gmail_push.get('pulled', 0)}`",
        f"- subscription: `{gmail_push.get('subscription', '')}`",
    ])
    if gmail_push.get("blocker"):
        lines.append(f"- blocker: {gmail_push.get('blocker')}")
    if gmail_push.get("error"):
        lines.append(f"- error: {gmail_push.get('error')}")
    if gmail_push.get("backstop"):
        lines.append(f"- backstop: {gmail_push.get('backstop')}")
    owner_reply_sweep = report.get("owner_reply_followup_sweep", {})
    lines.extend([
        "",
        "## Owner Reply Follow-Up Sweep",
        f"- status: `{owner_reply_sweep.get('status', 'not-recorded')}`",
        f"- checked: `{owner_reply_sweep.get('checked', 0)}`",
        f"- due: `{owner_reply_sweep.get('due', 0)}`",
        f"- action: `{owner_reply_sweep.get('action', 'none')}`",
        f"- wrapper_reconcile: `{owner_reply_sweep.get('wrapper_reconcile', {}).get('status', 'not-recorded')}` / changed `{owner_reply_sweep.get('wrapper_reconcile', {}).get('changed', 0)}`",
    ])
    for action in owner_reply_sweep.get("actions", [])[:10]:
        lines.append(
            f"- `{action.get('mailbox', '')}` {action.get('action', '')} ok=`{action.get('ok', '')}` owner=`{action.get('owner_email', '')}` target=`{action.get('target_session_id', '')}` task_flow=`{action.get('task_flow_key', '')}` subject=`{action.get('subject', '')}`"
        )
    worker_sweep = report.get("worker_summary_escalation_sweep", {})
    lines.extend([
        "",
        "## Worker Summary Escalation Sweep",
        f"- status: `{worker_sweep.get('status', 'not-recorded')}`",
        f"- checked: `{worker_sweep.get('checked', 0)}`",
        f"- emails_sent: `{worker_sweep.get('emails_sent', 0)}`",
    ])
    for action in worker_sweep.get("actions", [])[:10]:
        lines.append(
            f"- `{action.get('session_id', '')}` {action.get('action', '')} ok=`{action.get('ok', '')}` reason=`{action.get('reason', '')}`"
        )
    repair = report.get("proof_repair_queue", {})
    lines.extend([
        "",
        "## Proof Repair Queue",
        f"- status: `{repair.get('status', 'not-recorded')}`",
        f"- action: `{repair.get('action', 'none')}`",
        f"- queued: `{repair.get('queued', 0)}`",
        f"- next_index: `{repair.get('next_index', '')}`",
    ])
    for key in repair.get("keys", [])[:10]:
        lines.append(f"- `{key}`")
    canaries = report.get("mailbox_canaries", {})
    lines.extend([
        "",
        "## Mailbox Canaries",
        f"- status: `{canaries.get('status', 'not-recorded')}`",
        f"- issues: `{canaries.get('issue_count', 0)}`",
        f"- proof_validation: ok=`{canaries.get('proof_validation', {}).get('ok', '')}` closeout_allowed=`{canaries.get('proof_validation', {}).get('closeout_allowed', '')}`",
    ])
    for monitor in canaries.get("monitors", [])[:10]:
        lines.append(
            f"- `{monitor.get('id', '')}` {monitor.get('status', '')}/{monitor.get('runtime', '')} last_activity=`{monitor.get('last_activity_at', '')}`"
        )
    for issue in canaries.get("issues", [])[:10]:
        lines.append(f"- issue `{issue.get('id', '')}`: {issue.get('reason', '')}")
    lines.extend([
        "",
        "## Standing Monitors",
    ])
    for role, sessions in report["classification"]["standing_monitors"].items():
        if not sessions:
            if role in {"Frank", "Avignon"}:
                email_monitor = next(
                    (
                        item for item in report["classification"]["standing_monitors"].get("Email Worker", [])
                        if str(item.get("workspace") or "").lower() == role.lower()
                    ),
                    None,
                )
                if email_monitor:
                    lines.append(
                        f"- {role}: covered by email monitor `{email_monitor.get('id', '')}` {email_monitor.get('status', '')}/{email_monitor.get('runtime', '')}"
                    )
                    continue
            lines.append(f"- {role}: missing")
            continue
        labels = ", ".join(f"{item['id']} {item['status']}/{item['runtime']}" for item in sessions[:4])
        lines.append(f"- {role}: {labels}")
    lines.extend(["", "## Unhealthy Sessions"])
    for item in report["classification"]["unhealthy_sessions"][:20]:
        lines.append(f"- `{item.get('id')}` {item.get('title')} [{item.get('status')}/{item.get('runtime')}]: {item.get('reason', '')}")
    if not report["classification"]["unhealthy_sessions"]:
        lines.append("- none")
    lines.extend(["", "## Stale Working Sessions"])
    for item in report["classification"]["stale_working_sessions"][:20]:
        lines.append(f"- `{item['id']}` {item['title']} [{item['workspace']}]: {item.get('reason', '')}")
    if not report["classification"]["stale_working_sessions"]:
        lines.append("- none")
    lines.extend(["", "## Stale Waiting"])
    for item in report["classification"]["stale_waiting_sessions"][:20]:
        lines.append(f"- `{item['id']}` {item['title']} [{item['workspace']}]: {item.get('reason', '')}")
    if not report["classification"]["stale_waiting_sessions"]:
        lines.append("- none")
    lines.extend(["", "## Review Ready"])
    for item in report["classification"]["review_ready_sessions"][:20]:
        lines.append(f"- `{item['id']}` {item['title']} [{item['workspace']}]")
    if not report["classification"]["review_ready_sessions"]:
        lines.append("- none")
    lines.extend(["", "## Active Waiting"])
    for item in report["classification"]["active_waiting_sessions"][:20]:
        lines.append(f"- `{item['id']}` {item['title']} [{item['workspace']}]: {item['status']}")
    if not report["classification"]["active_waiting_sessions"]:
        lines.append("- none")
    lines.extend(["", "## Not Touched", "- mailbox bodies, mailbox state, credentials, OAuth tokens, private keys, Keychain, production systems, deploys, git history, and standing-monitor closure"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def maybe_nudge(args: argparse.Namespace, classification: dict, state: dict) -> dict:
    if args.dry_run:
        return {"status": "disabled-dry-run", "session_id": "", "reason": "dry-run/no-mutation mode"}
    if not args.allow_nudge:
        return {"status": "disabled", "session_id": "", "reason": "LaunchAgent default is report-only"}
    nudges = state.setdefault("nudges", {})
    now_epoch = int(time.time())
    management_health = assess_management_health(
        classification,
        args.max_non_standing_open,
        args.max_robert_blockers,
    )
    if management_health["issues"]:
        task_manager_sessions = classification.get("standing_monitors", {}).get("Task Manager", [])
        if task_manager_sessions:
            candidate = task_manager_sessions[0]
            session_id = candidate.get("id") or ""
            prior = nudges.get(session_id) if isinstance(nudges.get(session_id), dict) else {}
            if now_epoch - int(prior.get("at_epoch") or 0) >= NUDGE_COOLDOWN_SECONDS:
                issue_list = "; ".join(issue_summary(item) for item in management_health["issues"][:3])
                message = (
                    "AI Health Manager check: session sprawl is a management failure. "
                    f"Issues: {issue_list}. "
                    "Reuse existing correctly-owned sessions when possible, reconcile stale wrappers and "
                    "finished-at-prompt workers aggressively, keep Robert-facing blockers to a small real set, "
                    "and do not resurface routine cleanup, review-ready parking, or inbox-zero filing to Robert "
                    "once internal handling is approved. "
                    f"{source_first_directive()}"
                )
                payload = json.dumps({"session_id": session_id, "message": message, "wait_ms": 700}).encode("utf-8")
                request = urllib.request.Request(
                    args.message_url,
                    data=payload,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(request, timeout=args.timeout) as response:
                        ok = response.status == 200
                except urllib.error.URLError as error:
                    return {"status": "failed", "session_id": session_id, "reason": str(error)}
                if not ok:
                    return {"status": "failed", "session_id": session_id, "reason": "message endpoint did not return 200"}
                nudges[session_id] = {
                    "at": iso_now(),
                    "at_epoch": now_epoch,
                    "reason": issue_list,
                    "title": candidate.get("title", ""),
                }
                return {"status": "sent-management", "session_id": session_id, "reason": issue_list}
    candidates = classification.get("stale_working_sessions", [])
    if not candidates:
        return {"status": "none", "session_id": "", "reason": "no stale working sessions or Task Manager issue"}
    for candidate in candidates:
        session_id = candidate.get("id") or ""
        prior = nudges.get(session_id) if isinstance(nudges.get(session_id), dict) else {}
        if now_epoch - int(prior.get("at_epoch") or 0) < NUDGE_COOLDOWN_SECONDS:
            continue
        message = (
            "AI Health Manager check: this session looks stale from board status. "
            "Continue only if the next step is already in your assigned scope and safe. "
            "If blocked, report the blocker with owner, approval gate, and next safe action. "
            f"{source_first_directive()} "
            "Do not commit, push, deploy, close standing monitors, mutate mailboxes, expose secrets, or change runtime state from this nudge."
        )
        payload = json.dumps({"session_id": session_id, "message": message, "wait_ms": 700}).encode("utf-8")
        request = urllib.request.Request(
            args.message_url,
            data=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                ok = response.status == 200
        except urllib.error.URLError as error:
            return {"status": "failed", "session_id": session_id, "reason": str(error)}
        if not ok:
            return {"status": "failed", "session_id": session_id, "reason": "message endpoint did not return 200"}
        nudges[session_id] = {
            "at": iso_now(),
            "at_epoch": now_epoch,
            "reason": candidate.get("reason", ""),
            "title": candidate.get("title", ""),
        }
        return {"status": "sent", "session_id": session_id, "reason": candidate.get("reason", "")}
    return {"status": "cooldown", "session_id": "", "reason": "all stale candidates were already nudged recently"}


def maybe_restart_sessions(args: argparse.Namespace, classification: dict, state: dict) -> dict:
    if args.dry_run:
        return {"status": "disabled-dry-run", "session_id": "", "reason": "dry-run/no-mutation mode"}
    if not args.allow_nudge:
        return {"status": "disabled", "session_id": "", "reason": "LaunchAgent default is report-only"}
    restarts = state.setdefault("session_restarts", {})
    now_epoch = int(time.time())
    candidates = list(classification.get("stale_working_sessions", [])) + list(classification.get("stale_waiting_sessions", []))
    candidates = sorted(
        candidates,
        key=lambda item: float(item.get("inactive_minutes") or 0),
        reverse=True,
    )
    if not candidates:
        return {"status": "none", "session_id": "", "reason": "no stale working sessions"}
    for candidate in candidates:
        session_id = safe_text(candidate.get("id"), 80)
        if not session_id:
            continue
        inactive_minutes = candidate.get("inactive_minutes")
        if inactive_minutes is None or float(inactive_minutes) < float(args.session_restart_minutes):
            continue
        prior = restarts.get(session_id) if isinstance(restarts.get(session_id), dict) else {}
        if now_epoch - int(prior.get("at_epoch") or 0) < args.session_restart_cooldown_seconds:
            continue
        ok, detail = post_workspaceboard_json(
            args,
            "api/session-reconcile-stale",
            {"dry_run": False, "session_ids": [session_id]},
        )
        if ok:
            restarts[session_id] = {
                "at": iso_now(),
                "at_epoch": now_epoch,
                "reason": safe_text(candidate.get("reason", ""), 180),
                "title": safe_text(candidate.get("title", ""), 120),
                "inactive_minutes": round(float(inactive_minutes), 1),
            }
            return {
                "status": "sent",
                "session_id": session_id,
                "action": "reconcile-stale",
                "reason": safe_text(candidate.get("reason", ""), 180),
                "detail": detail if isinstance(detail, str) else "",
                "inactive_minutes": round(float(inactive_minutes), 1),
            }
        return {
            "status": "failed",
            "session_id": session_id,
            "action": "reconcile-stale",
            "reason": safe_text(candidate.get("reason", ""), 180),
            "detail": detail if isinstance(detail, str) else "",
            "inactive_minutes": round(float(inactive_minutes), 1),
        }
    return {"status": "cooldown", "session_id": "", "reason": "all restart candidates were handled recently"}


def build_report(args: argparse.Namespace) -> dict:
    status = fetch_json(args.status_url, args.timeout)
    classification = classify_sessions(status, args.stale_minutes, args.standing_attention_minutes)
    management_health = assess_management_health(
        classification,
        args.max_non_standing_open,
        args.max_robert_blockers,
    )
    workspace_summary = summarize_workspaces(status)
    state_path = Path(args.log_dir) / "state.json"
    state = load_state(state_path)
    sprawl_governor = session_sprawl_governor(args, classification, management_health, state)
    nudge = maybe_nudge(args, classification, state)
    session_restart = maybe_restart_sessions(args, classification, state)
    daily_input_audit = audit_daily_inputs(args, state)
    finish_contract_audit = audit_task_flow_finish_contracts(args)
    escalation_sweep = task_flow_escalation_sweep(args, classification, state)
    gmail_push = gmail_push_consumer_check(args)
    owner_reply_sweep = owner_reply_followup_sweep(args, classification, state)
    worker_summary_sweep = worker_summary_escalation_sweep(args, classification, state)
    repair_queue = proof_repair_queue(args, classification, state, finish_contract_audit)
    mailbox_canaries = mailbox_canary_checks(args, status)
    send_path_health = send_path_health_check(args)
    state["last_check"] = iso_now()
    state["last_nudge"] = nudge
    state["last_session_restart"] = session_restart
    atomic_write_json(state_path, state)
    report = {
        "checked_at": iso_now(),
        "status_url": args.status_url,
        "cadence_seconds": args.cadence_seconds,
        "dry_run": args.dry_run,
        "board": {
            "ok": bool(status.get("ok")),
            "board_version": safe_text(status.get("board_version"), 40),
            "generated_at": safe_text(status.get("generated_at"), 40),
            "host": safe_text(status.get("host"), 120),
            "tmux_available": bool(status.get("tmux_available")),
        },
        "workspace_summary": workspace_summary,
        "classification": classification,
        "management_health": management_health,
        "session_sprawl_governor": sprawl_governor,
        "session_restart": session_restart,
        "standing_attention_minutes": args.standing_attention_minutes,
        "daily_input_audit": daily_input_audit,
        "finish_contract_audit": finish_contract_audit,
        "task_flow_escalation_sweep": escalation_sweep,
        "gmail_push_consumer": gmail_push,
        "owner_reply_followup_sweep": owner_reply_sweep,
        "worker_summary_escalation_sweep": worker_summary_sweep,
        "proof_repair_queue": repair_queue,
        "mailbox_canaries": mailbox_canaries,
        "send_path_health": send_path_health,
        "nudge": nudge,
        "not_touched": [
            "private mailbox bodies",
            "mailbox state",
            "credentials/tokens/private keys",
            "OAuth/Keychain",
            "production systems",
            "deploy/push/reset/clean",
            "standing-monitor closure",
        ],
    }
    report["canonical_status_line"] = canonical_status_line(report)
    return report


def safe_finish_contract_audit(args: argparse.Namespace) -> dict:
    try:
        return audit_task_flow_finish_contracts(args)
    except Exception as error:
        return {
            "status": "failed",
            "task_flow_report_cmd": args.task_flow_report_cmd,
            "items_checked": 0,
            "missing_finish_contract_count": 0,
            "missing_proof_count": 0,
            "email_inbox_after_closeout_count": 0,
            "past_due_routed_count": 0,
            "vague_robert_decision_count": 0,
            "items": [],
            "error": safe_text(error, 500),
        }


def acquire_run_lock(log_dir: Path) -> Path | None:
    lock_dir = log_dir / "ai-health-check.lock"
    try:
        lock_dir.mkdir(parents=True)
        return lock_dir
    except FileExistsError:
        try:
            age = time.time() - lock_dir.stat().st_mtime
        except OSError:
            return None
        if age < 120:
            return None
        try:
            lock_dir.rmdir()
            lock_dir.mkdir(parents=True)
            return lock_dir
        except OSError:
            return None


def release_run_lock(lock_dir: Path | None) -> None:
    if lock_dir is None:
        return
    try:
        lock_dir.rmdir()
    except OSError:
        pass


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-url", default=os.environ.get("AI_HEALTH_STATUS_URL", DEFAULT_STATUS_URL))
    parser.add_argument("--message-url", default=os.environ.get("AI_HEALTH_MESSAGE_URL", "http://127.0.0.1:17878/api/session-message"))
    parser.add_argument("--log-dir", default=os.environ.get("AI_HEALTH_LOG_DIR", str(DEFAULT_LOG_DIR)))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--max-run-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_MAX_RUN_SECONDS", 110)),
        help="process watchdog; exits before launchd StartInterval jobs can pile up",
    )
    parser.add_argument("--stale-minutes", type=int, default=DEFAULT_STALE_MINUTES)
    parser.add_argument("--session-restart-minutes", type=int, default=DEFAULT_SESSION_RESTART_MINUTES)
    parser.add_argument(
        "--standing-attention-minutes",
        type=int,
        default=int(os.environ.get("AI_HEALTH_STANDING_ATTENTION_MINUTES", DEFAULT_STANDING_ATTENTION_MINUTES)),
    )
    parser.add_argument(
        "--session-restart-cooldown-seconds",
        type=int,
        default=int(os.environ.get(
            "AI_HEALTH_SESSION_RESTART_COOLDOWN_SECONDS",
            DEFAULT_SESSION_RESTART_COOLDOWN_SECONDS,
        )),
    )
    parser.add_argument("--max-non-standing-open", type=int, default=DEFAULT_MAX_NON_STANDING_OPEN)
    parser.add_argument("--max-robert-blockers", type=int, default=DEFAULT_MAX_ROBERT_BLOCKERS)
    parser.add_argument("--input-log-dir", default=os.environ.get("AI_HEALTH_INPUT_LOG_DIR", str(DEFAULT_INPUT_LOG_DIR)))
    parser.add_argument(
        "--nationaloutreach-state-dir",
        default=os.environ.get("AI_HEALTH_NATIONALOUTREACH_STATE_DIR", str(DEFAULT_NATIONALOUTREACH_STATE_DIR)),
        help="National Outreach runtime state directory used for non-secret send-path proof checks",
    )
    parser.add_argument(
        "--frank-state-dir",
        default=os.environ.get("AI_HEALTH_FRANK_STATE_DIR", str(DEFAULT_FRANK_STATE_DIR)),
        help="Frank runtime state directory used for non-secret owner-reply follow-up proof checks",
    )
    parser.add_argument(
        "--avignon-state-dir",
        default=os.environ.get("AI_HEALTH_AVIGNON_STATE_DIR", str(DEFAULT_AVIGNON_STATE_DIR)),
        help="Avignon runtime state directory used for non-secret owner-reply follow-up proof checks",
    )
    parser.add_argument(
        "--send-path-scan-limit",
        type=int,
        default=int(os.environ.get("AI_HEALTH_SEND_PATH_SCAN_LIMIT", 40)),
        help="number of recent sent artifacts to check for Message-ID proof",
    )
    parser.add_argument(
        "--send-path-recent-hours",
        type=int,
        default=int(os.environ.get("AI_HEALTH_SEND_PATH_RECENT_HOURS", 48)),
        help="only treat sent artifacts modified in this recent window as active send-path health issues",
    )
    parser.add_argument(
        "--send-path-max-issues",
        type=int,
        default=int(os.environ.get("AI_HEALTH_SEND_PATH_MAX_ISSUES", 8)),
        help="maximum send-path proof issues to include in the health report",
    )
    parser.add_argument("--input-audit-interval-seconds", type=int, default=DEFAULT_INPUT_AUDIT_INTERVAL_SECONDS)
    parser.add_argument(
        "--task-flow-escalation-timeout-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_TASK_FLOW_ESCALATION_TIMEOUT_SECONDS", DEFAULT_ESCALATION_TIMEOUT_SECONDS)),
    )
    parser.add_argument(
        "--task-flow-escalation-cooldown-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_TASK_FLOW_ESCALATION_COOLDOWN_SECONDS", DEFAULT_ESCALATION_COOLDOWN_SECONDS)),
    )
    parser.add_argument(
        "--task-flow-escalation-max-actions",
        type=int,
        default=int(os.environ.get("AI_HEALTH_TASK_FLOW_ESCALATION_MAX_ACTIONS", DEFAULT_ESCALATION_MAX_ACTIONS)),
    )
    parser.add_argument(
        "--task-flow-escalation-max-emails",
        type=int,
        default=int(os.environ.get("AI_HEALTH_TASK_FLOW_ESCALATION_MAX_EMAILS", DEFAULT_ESCALATION_MAX_EMAILS)),
    )
    parser.add_argument(
        "--task-flow-report-cmd",
        default=os.environ.get(
            "AI_HEALTH_TASK_FLOW_REPORT_CMD",
            "php scripts/task_flow_mysql_recorder.php report 500",
        ),
        help="command used for non-secret Task Flow finish-contract audit; set empty to disable",
    )
    parser.add_argument(
        "--task-flow-validate-cmd",
        default=os.environ.get(
            "AI_HEALTH_TASK_FLOW_VALIDATE_CMD",
            "php scripts/task_flow_mysql_recorder.php validate",
        ),
        help="command used for synthetic Task Flow closeout-proof validation; set empty to disable",
    )
    parser.add_argument(
        "--task-flow-record-cmd",
        default=os.environ.get(
            "AI_HEALTH_TASK_FLOW_RECORD_CMD",
            "php scripts/task_flow_mysql_recorder.php record",
        ),
        help="command used to create/update Task Flow owner-reply pending-response rows; set empty to disable",
    )
    parser.add_argument(
        "--no-input-audit-nudge",
        dest="allow_input_audit_nudge",
        action="store_false",
        default=True,
        help="disable the default Task Manager nudge for untracked daily input sections",
    )
    parser.add_argument("--cadence-seconds", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true", help="report only and do not nudge")
    parser.add_argument("--allow-nudge", action="store_true", help="allow one stale worker nudge when safe")
    parser.add_argument(
        "--disable-task-flow-escalation",
        dest="enable_task_flow_escalation",
        action="store_false",
        default=True,
        help="disable server-side Task Flow proof escalation sweeper",
    )
    parser.add_argument(
        "--disable-owner-reply-followup",
        dest="enable_owner_reply_followup",
        action="store_false",
        default=True,
        help="disable server-side owner-reply follow-up sweeper",
    )
    parser.add_argument(
        "--owner-reply-timeout-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_OWNER_REPLY_TIMEOUT_SECONDS", DEFAULT_OWNER_REPLY_TIMEOUT_SECONDS)),
        help="seconds after a primary-owner reply before AI Health reopens/focuses the responsible worker if no later sent proof exists",
    )
    parser.add_argument(
        "--owner-reply-cooldown-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_OWNER_REPLY_COOLDOWN_SECONDS", DEFAULT_OWNER_REPLY_COOLDOWN_SECONDS)),
        help="cooldown per owner reply before repeating a Task Manager nudge",
    )
    parser.add_argument(
        "--owner-reply-recent-hours",
        type=int,
        default=int(os.environ.get("AI_HEALTH_OWNER_REPLY_RECENT_HOURS", DEFAULT_OWNER_REPLY_RECENT_HOURS)),
        help="recent window for owner-reply follow-up checks",
    )
    parser.add_argument(
        "--owner-reply-max-actions",
        type=int,
        default=int(os.environ.get("AI_HEALTH_OWNER_REPLY_MAX_ACTIONS", DEFAULT_OWNER_REPLY_MAX_ACTIONS)),
        help="maximum owner-reply follow-up nudges per AI Health pass",
    )
    parser.add_argument(
        "--owner-reply-escalation-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_OWNER_REPLY_ESCALATION_SECONDS", DEFAULT_OWNER_REPLY_ESCALATION_SECONDS)),
        help="seconds after first owner-reply detection before also escalating to Task Manager",
    )
    parser.add_argument(
        "--owner-reply-email-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_OWNER_REPLY_EMAIL_SECONDS", DEFAULT_OWNER_REPLY_EMAIL_SECONDS)),
        help="seconds after first owner-reply detection before sending an owner-visible exact blocker alert if no proof exists",
    )
    parser.add_argument(
        "--disable-owner-reply-wrapper-reconcile",
        dest="enable_owner_reply_wrapper_reconcile",
        action="store_false",
        default=True,
        help="disable proof-backed owner-reply wrapper reconciliation through Workspaceboard",
    )
    parser.add_argument(
        "--disable-gmail-push-consumer",
        dest="enable_gmail_push_consumer",
        action="store_false",
        default=True,
        help="disable local Gmail Pub/Sub pull hook before owner-reply reconciliation",
    )
    parser.add_argument(
        "--gmail-push-subscription",
        default=os.environ.get("AI_HEALTH_GMAIL_PUSH_SUBSCRIPTION", DEFAULT_GMAIL_PUSH_SUBSCRIPTION),
        help="Gmail Pub/Sub subscription to pull when gcloud is available locally",
    )
    parser.add_argument(
        "--gmail-push-pull-limit",
        type=int,
        default=int(os.environ.get("AI_HEALTH_GMAIL_PUSH_PULL_LIMIT", 1)),
        help="maximum Gmail Pub/Sub messages to pull per AI Health pass",
    )
    parser.add_argument(
        "--gmail-push-timeout-seconds",
        type=float,
        default=float(os.environ.get("AI_HEALTH_GMAIL_PUSH_TIMEOUT_SECONDS", DEFAULT_GMAIL_PUSH_TIMEOUT_SECONDS)),
        help="short timeout for Gmail Pub/Sub pull so AI Health does not miss its 60-second cadence",
    )
    parser.add_argument(
        "--disable-worker-summary-escalation",
        dest="enable_worker_summary_escalation",
        action="store_false",
        default=True,
        help="disable owner emails generated from worker summaries that contain exact blockers or email-missing proof gaps",
    )
    parser.add_argument(
        "--worker-summary-escalation-cooldown-seconds",
        type=int,
        default=int(os.environ.get(
            "AI_HEALTH_WORKER_SUMMARY_ESCALATION_COOLDOWN_SECONDS",
            DEFAULT_WORKER_SUMMARY_ESCALATION_COOLDOWN_SECONDS,
        )),
    )
    parser.add_argument(
        "--worker-summary-escalation-max-emails",
        type=int,
        default=int(os.environ.get(
            "AI_HEALTH_WORKER_SUMMARY_ESCALATION_MAX_EMAILS",
            DEFAULT_WORKER_SUMMARY_ESCALATION_MAX_EMAILS,
        )),
    )
    parser.add_argument(
        "--worker-summary-escalation-scan-limit",
        type=int,
        default=int(os.environ.get("AI_HEALTH_WORKER_SUMMARY_ESCALATION_SCAN_LIMIT", 12)),
    )
    parser.add_argument(
        "--disable-proof-repair-queue",
        dest="enable_proof_repair_queue",
        action="store_false",
        default=True,
        help="disable rotating Task Flow proof repair batches to Task Manager",
    )
    parser.add_argument(
        "--proof-repair-batch-size",
        type=int,
        default=int(os.environ.get("AI_HEALTH_PROOF_REPAIR_BATCH_SIZE", DEFAULT_PROOF_REPAIR_BATCH_SIZE)),
    )
    parser.add_argument(
        "--proof-repair-interval-seconds",
        type=int,
        default=int(os.environ.get("AI_HEALTH_PROOF_REPAIR_INTERVAL_SECONDS", DEFAULT_PROOF_REPAIR_INTERVAL_SECONDS)),
    )
    parser.add_argument(
        "--disable-mailbox-canaries",
        dest="enable_mailbox_canaries",
        action="store_false",
        default=True,
        help="disable required mailbox monitor and synthetic Task Flow closeout-proof canaries",
    )
    parser.add_argument(
        "--mailbox-canary-max-age-minutes",
        type=int,
        default=int(os.environ.get("AI_HEALTH_MAILBOX_CANARY_MAX_AGE_MINUTES", DEFAULT_MAILBOX_CANARY_MAX_AGE_MINUTES)),
    )
    parser.add_argument(
        "--disable-session-sprawl-governor",
        dest="enable_session_sprawl_governor",
        action="store_false",
        default=os.environ.get("AI_HEALTH_ENABLE_SESSION_SPRAWL_GOVERNOR", "0") == "1",
        help="disable automatic Workspaceboard stale-session reconciliation when open non-standing sessions exceed the threshold",
    )
    parser.add_argument(
        "--session-sprawl-governor-interval-seconds",
        type=int,
        default=int(os.environ.get(
            "AI_HEALTH_SESSION_SPRAWL_GOVERNOR_INTERVAL_SECONDS",
            DEFAULT_SESSION_SPRAWL_GOVERNOR_INTERVAL_SECONDS,
        )),
    )
    parser.add_argument(
        "--session-sprawl-governor-batch-size",
        type=int,
        default=int(os.environ.get("AI_HEALTH_SESSION_SPRAWL_GOVERNOR_BATCH_SIZE", 4)),
    )
    parser.add_argument(
        "--no-board-repair",
        dest="allow_board_repair",
        action="store_false",
        default=True,
        help="disable the default Workspaceboard listener restart when /api/status is hung or unavailable",
    )
    parser.add_argument("--board-repair-wait-seconds", type=float, default=3.0)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    log_dir = Path(args.log_dir)
    lock_dir = acquire_run_lock(log_dir)
    if lock_dir is None:
        print(json.dumps({
            "checked_at": iso_now(),
            "skipped_locked": True,
            "log": str(log_dir / "latest.md"),
        }, sort_keys=True))
        return 0
    state_path = log_dir / "state.json"
    remediation = {"status": "not-needed"}
    previous_alarm_handler = None
    if args.max_run_seconds > 0 and hasattr(signal, "SIGALRM"):
        previous_alarm_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, raise_run_timeout)
        signal.alarm(args.max_run_seconds)
    try:
      try:
        report = build_report(args)
      except HealthCheckError as error:
        state = load_state(state_path)
        remediation = repair_workspaceboard(args, state, str(error))
        atomic_write_json(state_path, state)
        if remediation.get("status") == "sent-term":
            try:
                report = build_report(args)
                exit_code = 0
            except HealthCheckError as second_error:
                report = {
                    "checked_at": iso_now(),
                    "status_url": args.status_url,
                    "cadence_seconds": args.cadence_seconds,
                    "dry_run": args.dry_run,
                    "board": {"ok": False},
                    "classification": {
                        "standing_monitors": {},
                        "standing_attention_sessions": [],
                        "unhealthy_sessions": [{"id": "", "title": "Workspaceboard status", "reason": str(second_error)}],
                        "stale_working_sessions": [],
                        "stale_waiting_sessions": [],
                        "review_ready_sessions": [],
                        "active_waiting_sessions": [],
                        "active_working_sessions": [],
                    },
                    "management_health": {
                        "standing_count": 0,
                        "standing_attention_count": 0,
                        "active_working_count": 0,
                        "review_ready_count": 0,
                        "stale_working_count": 0,
                        "stale_waiting_count": 0,
                        "active_waiting_count": 0,
                        "non_standing_open_count": 0,
                        "robert_blocker_count": 0,
                        "issues": [],
                    },
                    "workspace_summary": {"active_workspace_count": 0, "open_item_count": 0, "workspaces": []},
                    "canonical_status_line": f"board down; status check failed after repair: {safe_text(second_error, 180)}",
                    "session_sprawl_governor": {"status": "not-run", "action": "none", "changed": 0},
                    "standing_attention_minutes": DEFAULT_STANDING_ATTENTION_MINUTES,
                    "daily_input_audit": {"status": "not-run", "missing_tracking_count": 0},
                    "finish_contract_audit": safe_finish_contract_audit(args),
                    "task_flow_escalation_sweep": {"status": "not-run", "checked": 0, "action": "none"},
                    "gmail_push_consumer": {"status": "not-run", "pulled": 0},
                    "owner_reply_followup_sweep": {"status": "not-run", "checked": 0, "due": 0, "action": "none"},
                    "proof_repair_queue": {"status": "not-run", "queued": 0, "action": "none"},
                    "mailbox_canaries": {"status": "not-run", "issue_count": 0, "issues": []},
                    "send_path_health": send_path_health_check(args),
                    "nudge": {"status": "not-attempted", "session_id": "", "reason": "status check failed after board repair"},
                    "session_restart": {"status": "not-attempted", "session_id": "", "action": "none", "reason": "status check failed after board repair"},
                    "not_touched": ["mailboxes", "credentials", "production data", "git history"],
                }
                exit_code = 2
        else:
            report = {
                "checked_at": iso_now(),
                "status_url": args.status_url,
                "cadence_seconds": args.cadence_seconds,
                "dry_run": args.dry_run,
                "board": {"ok": False},
                "classification": {
                    "standing_monitors": {},
                    "standing_attention_sessions": [],
                    "unhealthy_sessions": [{"id": "", "title": "Workspaceboard status", "reason": str(error)}],
                    "stale_working_sessions": [],
                    "stale_waiting_sessions": [],
                    "review_ready_sessions": [],
                    "active_waiting_sessions": [],
                    "active_working_sessions": [],
                },
                "management_health": {
                    "standing_count": 0,
                    "standing_attention_count": 0,
                    "active_working_count": 0,
                    "review_ready_count": 0,
                    "stale_working_count": 0,
                    "stale_waiting_count": 0,
                    "active_waiting_count": 0,
                    "non_standing_open_count": 0,
                    "robert_blocker_count": 0,
                    "issues": [],
                },
                "workspace_summary": {"active_workspace_count": 0, "open_item_count": 0, "workspaces": []},
                "canonical_status_line": f"board down; status check failed: {safe_text(error, 180)}",
                "session_sprawl_governor": {"status": "not-run", "action": "none", "changed": 0},
                "standing_attention_minutes": DEFAULT_STANDING_ATTENTION_MINUTES,
                "daily_input_audit": {"status": "not-run", "missing_tracking_count": 0},
                "finish_contract_audit": safe_finish_contract_audit(args),
                "task_flow_escalation_sweep": {"status": "not-run", "checked": 0, "action": "none"},
                "gmail_push_consumer": {"status": "not-run", "pulled": 0},
                "owner_reply_followup_sweep": {"status": "not-run", "checked": 0, "due": 0, "action": "none"},
                "proof_repair_queue": {"status": "not-run", "queued": 0, "action": "none"},
                "mailbox_canaries": {"status": "not-run", "issue_count": 0, "issues": []},
                "send_path_health": send_path_health_check(args),
                "nudge": {"status": "not-attempted", "session_id": "", "reason": "status check failed"},
                "session_restart": {"status": "not-attempted", "session_id": "", "action": "none", "reason": "status check failed"},
                "not_touched": ["mailboxes", "credentials", "production data", "git history"],
            }
            exit_code = 2
      except RunTimeout as error:
        report = build_run_timeout_report(args, error)
        exit_code = 3
      else:
        exit_code = 0

      report["board_remediation"] = remediation

      log_dir.mkdir(parents=True, exist_ok=True)
      append_jsonl(log_dir / "health-checks.jsonl", report)
      atomic_write_json(log_dir / "latest.json", report)
      report["workspaceboard_supervisor"] = run_workspaceboard_supervisor()
      atomic_write_json(log_dir / "latest.json", report)
      write_markdown(log_dir / "latest.md", report)
      print(json.dumps({
        "checked_at": report["checked_at"],
        "board_ok": report["board"].get("ok", False),
        "standing": report["management_health"]["standing_count"],
        "standing_attention": report["management_health"].get("standing_attention_count", 0),
        "active": report["management_health"]["active_working_count"],
        "unhealthy": len(report["classification"]["unhealthy_sessions"]),
        "stale_working": len(report["classification"]["stale_working_sessions"]),
        "stale_waiting": len(report["classification"]["stale_waiting_sessions"]),
        "review_ready": len(report["classification"]["review_ready_sessions"]),
        "active_waiting": len(report["classification"]["active_waiting_sessions"]),
        "non_standing_open": report["management_health"]["non_standing_open_count"],
        "robert_blockers": report["management_health"]["robert_blocker_count"],
        "management_issues": len(report["management_health"]["issues"]),
        "session_sprawl_governor": report.get("session_sprawl_governor", {}).get("action", "none"),
        "session_sprawl_changed": report.get("session_sprawl_governor", {}).get("changed", 0),
        "session_restart": report.get("session_restart", {}).get("status", "not-recorded"),
        "session_restart_action": report.get("session_restart", {}).get("action", "none"),
        "missed_input_sections": report.get("daily_input_audit", {}).get("missing_tracking_count", 0),
        "missed_input_audit": report.get("daily_input_audit", {}).get("status", "not-recorded"),
        "missing_finish_contracts": report.get("finish_contract_audit", {}).get("missing_finish_contract_count", 0),
        "missing_closeout_proof": report.get("finish_contract_audit", {}).get("missing_proof_count", 0),
        "email_inbox_after_closeout": report.get("finish_contract_audit", {}).get("email_inbox_after_closeout_count", 0),
        "past_due_routed": report.get("finish_contract_audit", {}).get("past_due_routed_count", 0),
        "vague_robert_decisions": report.get("finish_contract_audit", {}).get("vague_robert_decision_count", 0),
        "finish_contract_audit": report.get("finish_contract_audit", {}).get("status", "not-recorded"),
        "task_flow_escalation": report.get("task_flow_escalation_sweep", {}).get("action", "none"),
        "task_flow_escalation_checked": report.get("task_flow_escalation_sweep", {}).get("checked", 0),
        "gmail_push_consumer": report.get("gmail_push_consumer", {}).get("status", "not-recorded"),
        "gmail_push_pulled": report.get("gmail_push_consumer", {}).get("pulled", 0),
        "owner_reply_followup": report.get("owner_reply_followup_sweep", {}).get("action", "none"),
        "owner_reply_followup_due": report.get("owner_reply_followup_sweep", {}).get("due", 0),
        "owner_reply_followup_checked": report.get("owner_reply_followup_sweep", {}).get("checked", 0),
        "owner_reply_wrapper_reconcile_changed": report.get("owner_reply_followup_sweep", {}).get("wrapper_reconcile", {}).get("changed", 0),
        "proof_repair_queue": report.get("proof_repair_queue", {}).get("action", "none"),
        "proof_repair_queued": report.get("proof_repair_queue", {}).get("queued", 0),
        "mailbox_canaries": report.get("mailbox_canaries", {}).get("status", "not-recorded"),
        "mailbox_canary_issues": report.get("mailbox_canaries", {}).get("issue_count", 0),
        "send_path_health": report.get("send_path_health", {}).get("status", "not-recorded"),
        "send_path_issues": report.get("send_path_health", {}).get("issue_count", 0),
        "workspaceboard_supervisor": report.get("workspaceboard_supervisor", {}).get("status", "not-recorded"),
        "nudge": report["nudge"]["status"],
        "session_restart": report.get("session_restart", {}).get("status", "not-recorded"),
        "session_restart_action": report.get("session_restart", {}).get("action", "none"),
        "board_remediation": report["board_remediation"]["status"],
        "canonical_status": report.get("canonical_status_line", ""),
        "log": str(log_dir / "latest.md"),
      }, sort_keys=True))
      return exit_code
    finally:
        if args.max_run_seconds > 0 and hasattr(signal, "SIGALRM"):
            signal.alarm(0)
            if previous_alarm_handler is not None:
                signal.signal(signal.SIGALRM, previous_alarm_handler)
        release_run_lock(lock_dir)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
