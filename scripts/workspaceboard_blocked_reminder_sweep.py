#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_BASE = "http://127.0.0.1:17878"
DEFAULT_STATE_PATH = Path("/Users/werkstatt/ai_workspace/runtime/workspaceboard-blocked-reminders.json")
DEFAULT_LOG_PATH = Path("/Users/werkstatt/ai_workspace/runtime/workspaceboard-blocked-reminders.jsonl")
DEFAULT_SENT_LOG_PATH = Path("/Users/werkstatt/ai_workspace/runtime/workspaceboard-blocked-reminder-sent-log.jsonl")
DEFAULT_SEND_SCRIPT = Path("/Users/werkstatt/ai_workspace/scripts/send_codex_ops_email.py")
DEFAULT_THRESHOLD_HOURS = 24
DEFAULT_COOLDOWN_HOURS = 24
RECIPIENTS = {
    1: ("Robert", "robert@kovaldistillery.com"),
    3: ("Sonat", "sonat@kovaldistillery.com"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send 24-hour reminders for blocked Workspaceboard sessions.")
    parser.add_argument("--api-base", default=API_BASE)
    parser.add_argument("--state-path", default=str(DEFAULT_STATE_PATH))
    parser.add_argument("--log-path", default=str(DEFAULT_LOG_PATH))
    parser.add_argument("--threshold-hours", type=float, default=DEFAULT_THRESHOLD_HOURS)
    parser.add_argument("--cooldown-hours", type=float, default=DEFAULT_COOLDOWN_HOURS)
    parser.add_argument("--send-script", default=str(DEFAULT_SEND_SCRIPT))
    parser.add_argument("--sent-log", default=str(DEFAULT_SENT_LOG_PATH))
    parser.add_argument("--creds-file", default=os.environ.get("WB_BLOCKED_REMINDER_CREDS_FILE", ""))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def parse_time(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw).astimezone(timezone.utc)
    except ValueError:
        return None


def request_json(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: {exc.code} {body}") from exc


def taskflow_closeout_statuses() -> set[str]:
    return {
        "closed",
        "closed_with_proof",
        "completed",
        "complete",
        "reported",
        "filed",
        "handled",
        "no_action_closed",
    }


def nested_work_state(session: dict) -> dict:
    work_state = session.get("work_state")
    return work_state if isinstance(work_state, dict) else {}


def session_taskflow_keys(session: dict) -> set[str]:
    work_state = nested_work_state(session)
    keys = {
        str(session.get("taskflow_key") or "").strip(),
        str(work_state.get("taskflow_key") or "").strip(),
    }
    details = work_state.get("details")
    if isinstance(details, dict):
        keys.add(str(details.get("taskflow_key") or "").strip())
    text = "\n".join(
        str(value or "")
        for value in [
            session.get("title"),
            session.get("taskflow_key"),
            session.get("blocker"),
            session.get("owner_question"),
            work_state.get("title"),
            work_state.get("taskflow_key"),
            work_state.get("blocker_text"),
            work_state.get("owner_question"),
            json.dumps(details, ensure_ascii=True) if isinstance(details, dict) else "",
        ]
    )
    keys.update(match.group(0) for match in re.finditer(r"taskflow-[A-Za-z0-9]+", text))
    return {key for key in keys if key}


def taskflow_report_items(args: argparse.Namespace) -> list[dict]:
    try:
        report = request_json(
            "GET",
            f"{args.api_base.rstrip('/')}/api/task-flow/report?mode=all&limit=500&refresh=1",
        )
    except Exception:
        return []
    items = report.get("items") if isinstance(report.get("items"), list) else []
    return [item for item in items if isinstance(item, dict)]


def taskflow_text_has_message_id(text: str) -> bool:
    return re.search(r"<[^<>\s]+@[^<>\s]+>", text) is not None


def taskflow_closeout_for_session(session: dict, items: list[dict]) -> dict | None:
    session_id = str(session.get("id") or session.get("session_id") or "").strip()
    taskflow_keys = session_taskflow_keys(session)
    if not session_id and not taskflow_keys:
        return None
    closeout_statuses = taskflow_closeout_statuses()
    for item in items:
        dedupe_key = str(item.get("dedupe_key") or "").strip()
        item_session = str(item.get("workspaceboard_session") or item.get("session_id") or "").strip()
        if dedupe_key not in taskflow_keys and (not session_id or item_session != session_id):
            continue
        status = str(item.get("status") or "").strip().lower()
        effective = str(item.get("effective_status") or "").strip().lower()
        completion = str(item.get("completion_or_blocker_email") or "").strip()
        verification = str(item.get("verification_readback") or "").strip()
        proof = completion or verification
        sent_clarification = status in {"clarification_sent", "waiting", "waiting_owner_decision", "waiting_owner_input"} and taskflow_text_has_message_id(completion)
        if status in closeout_statuses or effective in {"closed", "completed"} or sent_clarification:
            return {
                "dedupe_key": dedupe_key,
                "status": status,
                "effective_status": effective,
                "workspaceboard_session": item_session,
                "proof": proof[:240],
                "reason": "task-flow-closeout-proof",
            }
    return None


def load_state(path: Path) -> dict:
    if not path.is_file():
        return {"sent": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("sent", {})
            return data
    except json.JSONDecodeError:
        pass
    return {"sent": {}}


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_log(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def session_blocked_at(session: dict) -> datetime | None:
    work_state = session.get("work_state") if isinstance(session.get("work_state"), dict) else {}
    for key in ("heartbeat_at", "updated_at", "last_activity_at", "created_at"):
        stamp = work_state.get(key) if key == "heartbeat_at" else session.get(key)
        parsed = parse_time(str(stamp or ""))
        if parsed is not None:
            return parsed
    return None


def recipient_for_session(session: dict) -> tuple[int, str, str]:
    text = " ".join(
        str(value or "")
        for value in [
            session.get("workspace_key"),
            session.get("title"),
            (session.get("work_state") or {}).get("escalation_persona", ""),
            (session.get("work_state") or {}).get("owner_question", ""),
        ]
    ).lower()
    if "avignon" in text or "sonat" in text and "robert" not in text:
        user_id = 3
    else:
        user_id = 1
    label, email = RECIPIENTS[user_id]
    return user_id, label, email


def reminder_key(session: dict) -> str:
    work_state = session.get("work_state") if isinstance(session.get("work_state"), dict) else {}
    question = str(work_state.get("owner_question") or session.get("owner_question") or "")
    blocker = str(work_state.get("blocker_text") or session.get("blocker") or "")
    digest = hashlib.sha256(f"{question}\n{blocker}".encode("utf-8")).hexdigest()[:12]
    return f"{session.get('id')}:{digest}"


def build_message(session: dict, blocked_at: datetime, age_hours: float) -> str:
    work_state = session.get("work_state") if isinstance(session.get("work_state"), dict) else {}
    blocker = str(work_state.get("blocker_text") or session.get("blocker") or "").strip()
    question = str(work_state.get("owner_question") or session.get("owner_question") or "").strip()
    title = str(session.get("title") or "Blocked Workspaceboard item").strip()
    workspace = str(session.get("workspace_key") or "").strip()
    session_id = str(session.get("id") or "").strip()
    lines = [
        "This Workspaceboard item has been blocked for more than 24 hours.",
        "",
        f"Item: {title}",
        f"Workspace: {workspace}",
        f"Session: {session_id}",
        f"Blocked since: {blocked_at.astimezone().isoformat(timespec='minutes')}",
        f"Age: {age_hours:.1f} hours",
        "",
        "Needed:",
        question or blocker or "Please provide the missing decision or confirm this blocker should be closed.",
    ]
    if blocker and blocker != question:
        lines.extend(["", "Current blocker:", blocker])
    lines.extend(["", "Reply with the decision or the missing facts, and Codex will continue or close the item with proof."])
    return "\n".join(lines)


def send_email(args: argparse.Namespace, to_addr: str, subject: str, body: str) -> dict:
    if not args.creds_file:
        raise RuntimeError("Email credentials are not configured for live blocked-reminder sends.")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(body)
        body_path = Path(handle.name)
    try:
        command = [
            "/usr/local/bin/python3.13",
            str(args.send_script),
            "--creds-file",
            str(args.creds_file),
            "--to",
            to_addr,
            "--subject",
            subject,
            "--body-file",
            str(body_path),
            "--from-address",
            "codex@kovaldistillery.com",
            "--from-name",
            "Codex Local Agent",
            "--sent-log",
            str(args.sent_log),
        ]
        proc = subprocess.run(command, text=True, capture_output=True, check=False, timeout=60)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip() or "Email send failed.")
        payload = json.loads(proc.stdout.strip() or "{}")
        payload["ok"] = True
        return payload
    finally:
        body_path.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    now = datetime.now(timezone.utc)
    state_path = Path(args.state_path)
    log_path = Path(args.log_path)
    state = load_state(state_path)
    sent_state = state.setdefault("sent", {})
    status = request_json("GET", f"{args.api_base.rstrip('/')}/api/status")
    blocked = status.get("blocked_sessions") if isinstance(status.get("blocked_sessions"), list) else []
    taskflow_items = taskflow_report_items(args) if blocked else []
    results = []
    for session in blocked:
        if not isinstance(session, dict):
            continue
        blocked_at = session_blocked_at(session)
        if blocked_at is None:
            continue
        age_hours = (now - blocked_at).total_seconds() / 3600
        key = reminder_key(session)
        last_sent = parse_time(str(sent_state.get(key, {}).get("sent_at", ""))) if isinstance(sent_state.get(key), dict) else None
        cooldown_hours = ((now - last_sent).total_seconds() / 3600) if last_sent else None
        if age_hours < args.threshold_hours:
            results.append({"session_id": session.get("id"), "action": "skip_young", "age_hours": round(age_hours, 2)})
            continue
        if cooldown_hours is not None and cooldown_hours < args.cooldown_hours:
            results.append({"session_id": session.get("id"), "action": "skip_cooldown", "age_hours": round(age_hours, 2), "cooldown_hours": round(cooldown_hours, 2)})
            continue
        closeout = taskflow_closeout_for_session(session, taskflow_items)
        if isinstance(closeout, dict) and closeout.get("reason") == "task-flow-closeout-proof":
            results.append({
                "session_id": session.get("id"),
                "action": "skip_taskflow_proof",
                "age_hours": round(age_hours, 2),
                "proof": closeout,
            })
            sent_state[key] = {
                "sent_at": now.isoformat(),
                "session_id": session.get("id"),
                "message_id": "",
                "route_signature": f"blocked-24h:{session.get('id')}:{key.split(':')[-1]}",
                "suppressed": True,
                "reason": "task-flow-closeout-proof",
                "proof": closeout,
            }
            append_log(log_path, {
                "logged_at": now.isoformat(),
                "session_id": session.get("id"),
                "workspace_key": session.get("workspace_key"),
                "title": session.get("title"),
                "age_hours": round(age_hours, 2),
                "dry_run": bool(args.dry_run),
                "ok": True,
                "suppressed": True,
                "reason": "task-flow-closeout-proof",
                "proof": closeout,
            })
            continue
        user_id, user_label, to_addr = recipient_for_session(session)
        subject = f"Blocked reminder: {str(session.get('title') or 'Workspaceboard item')[:110]}"
        message = build_message(session, blocked_at, age_hours)
        route_signature = f"blocked-24h:{session.get('id')}:{key.split(':')[-1]}"
        if args.dry_run:
            result = {"ok": True, "dry_run": True, "message_id": ""}
        else:
            result = send_email(args, to_addr, subject, message)
        row = {
            "logged_at": now.isoformat(),
            "session_id": session.get("id"),
            "workspace_key": session.get("workspace_key"),
            "title": session.get("title"),
            "recipient_user_id": user_id,
            "recipient_label": user_label,
            "age_hours": round(age_hours, 2),
            "route_signature": route_signature,
            "message_id": result.get("message_id") or result.get("receipt", {}).get("message_id", ""),
            "dry_run": bool(args.dry_run),
            "ok": bool(result.get("ok")),
        }
        sent_state[key] = {
            "sent_at": now.isoformat(),
            "session_id": session.get("id"),
            "message_id": row["message_id"],
            "route_signature": route_signature,
        }
        append_log(log_path, row)
        results.append({"session_id": session.get("id"), "action": "email", "ok": row["ok"], "message_id": row["message_id"]})
    state["updated_at"] = now.isoformat()
    if not args.dry_run:
        write_state(state_path, state)
    print(json.dumps({"ok": True, "checked": len(blocked), "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
