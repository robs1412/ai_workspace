#!/usr/bin/env python3
"""Non-secret Workspaceboard health check for AI Health Manager."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_STATUS_URL = "http://127.0.0.1:17878/api/status"
DEFAULT_LOG_DIR = Path("/Users/werkstatt/ai_workspace/tmp/ai-health-manager")
DEFAULT_STALE_MINUTES = 240
DEFAULT_MAX_NON_STANDING_OPEN = 12
DEFAULT_MAX_ROBERT_BLOCKERS = 6
NUDGE_COOLDOWN_SECONDS = 24 * 60 * 60
BOARD_REPAIR_COOLDOWN_SECONDS = 10 * 60
WORKSPACEBOARD_PROCESS_MARKER = "/Users/admin/.workspaceboard-launch/runtime/app/server/index.js"

STANDING_PATTERNS = {
    "Task Manager": ("task manager",),
    "Summary Worker": ("summary worker",),
    "Decision Driver": ("decision driver",),
    "Security Guard": ("security guard",),
    "Frank": ("frank email worker",),
    "Avignon": ("avignon email worker",),
    "AI Health Manager": ("ai health manager",),
}


class HealthCheckError(Exception):
    pass


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
        return None


def minutes_since(value: object, now: datetime) -> float | None:
    parsed = parse_time(value)
    if parsed is None:
        return None
    return max(0.0, (now - parsed).total_seconds() / 60.0)


def fetch_json(url: str, timeout: float) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
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


def classify_sessions(status: dict, stale_minutes: int) -> dict:
    now = utc_now()
    sessions = [item for item in status.get("managed_sessions", []) if isinstance(item, dict)]
    standing: dict[str, list[dict]] = {role: [] for role in STANDING_PATTERNS}
    standing["Email Worker"] = []
    unhealthy: list[dict] = []
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
    for role in ("Task Manager", "Summary Worker", "Decision Driver", "Security Guard", "Frank", "Avignon"):
        if not standing.get(role):
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

    return {
        "standing_count": standing_count,
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


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# AI Health Manager Check",
        "",
        f"- checked_at: `{report['checked_at']}`",
        f"- status_url: `{report['status_url']}`",
        f"- board: `{report['board'].get('host', '')}` / version `{report['board'].get('board_version', '')}`",
        f"- cadence: `{report['cadence_seconds']}s`",
        f"- mode: `{'dry-run/no-mutation' if report['dry_run'] else 'active'}`",
        f"- board_remediation: `{report.get('board_remediation', {}).get('status', 'not-recorded')}`",
        f"- nudge: `{report['nudge']['status']}`",
        "",
        "## Session Counts",
        f"- standing: `{report['management_health']['standing_count']}`",
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
    lines.extend([
        "",
        "## Standing Monitors",
    ])
    for role, sessions in report["classification"]["standing_monitors"].items():
        if not sessions:
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
                    "once internal handling is approved."
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


def build_report(args: argparse.Namespace) -> dict:
    status = fetch_json(args.status_url, args.timeout)
    classification = classify_sessions(status, args.stale_minutes)
    management_health = assess_management_health(
        classification,
        args.max_non_standing_open,
        args.max_robert_blockers,
    )
    workspace_summary = summarize_workspaces(status)
    state_path = Path(args.log_dir) / "state.json"
    state = load_state(state_path)
    nudge = maybe_nudge(args, classification, state)
    state["last_check"] = iso_now()
    state["last_nudge"] = nudge
    atomic_write_json(state_path, state)
    return {
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-url", default=os.environ.get("AI_HEALTH_STATUS_URL", DEFAULT_STATUS_URL))
    parser.add_argument("--message-url", default=os.environ.get("AI_HEALTH_MESSAGE_URL", "http://127.0.0.1:17878/api/session-message"))
    parser.add_argument("--log-dir", default=os.environ.get("AI_HEALTH_LOG_DIR", str(DEFAULT_LOG_DIR)))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--stale-minutes", type=int, default=DEFAULT_STALE_MINUTES)
    parser.add_argument("--max-non-standing-open", type=int, default=DEFAULT_MAX_NON_STANDING_OPEN)
    parser.add_argument("--max-robert-blockers", type=int, default=DEFAULT_MAX_ROBERT_BLOCKERS)
    parser.add_argument("--cadence-seconds", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true", help="report only and do not nudge")
    parser.add_argument("--allow-nudge", action="store_true", help="allow one stale worker nudge when safe")
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
    state_path = log_dir / "state.json"
    remediation = {"status": "not-needed"}
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
                        "unhealthy_sessions": [{"id": "", "title": "Workspaceboard status", "reason": str(second_error)}],
                        "stale_working_sessions": [],
                        "stale_waiting_sessions": [],
                        "review_ready_sessions": [],
                        "active_waiting_sessions": [],
                        "active_working_sessions": [],
                    },
                    "management_health": {
                        "standing_count": 0,
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
                    "nudge": {"status": "not-attempted", "session_id": "", "reason": "status check failed after board repair"},
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
                    "unhealthy_sessions": [{"id": "", "title": "Workspaceboard status", "reason": str(error)}],
                    "stale_working_sessions": [],
                    "stale_waiting_sessions": [],
                    "review_ready_sessions": [],
                    "active_waiting_sessions": [],
                    "active_working_sessions": [],
                },
                "management_health": {
                    "standing_count": 0,
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
                "nudge": {"status": "not-attempted", "session_id": "", "reason": "status check failed"},
                "not_touched": ["mailboxes", "credentials", "production data", "git history"],
            }
            exit_code = 2
    else:
        exit_code = 0

    report["board_remediation"] = remediation

    log_dir.mkdir(parents=True, exist_ok=True)
    append_jsonl(log_dir / "health-checks.jsonl", report)
    atomic_write_json(log_dir / "latest.json", report)
    write_markdown(log_dir / "latest.md", report)
    print(json.dumps({
        "checked_at": report["checked_at"],
        "board_ok": report["board"].get("ok", False),
        "standing": report["management_health"]["standing_count"],
        "active": report["management_health"]["active_working_count"],
        "unhealthy": len(report["classification"]["unhealthy_sessions"]),
        "stale_working": len(report["classification"]["stale_working_sessions"]),
        "stale_waiting": len(report["classification"]["stale_waiting_sessions"]),
        "review_ready": len(report["classification"]["review_ready_sessions"]),
        "active_waiting": len(report["classification"]["active_waiting_sessions"]),
        "non_standing_open": report["management_health"]["non_standing_open_count"],
        "robert_blockers": report["management_health"]["robert_blocker_count"],
        "management_issues": len(report["management_health"]["issues"]),
        "nudge": report["nudge"]["status"],
        "board_remediation": report["board_remediation"]["status"],
        "log": str(log_dir / "latest.md"),
    }, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
