#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


STATES = {
    "captured",
    "classified",
    "routed",
    "task_created",
    "scheduled",
    "clarification_needed",
    "clarification_sent",
    "working",
    "waiting",
    "blocked",
    "completed",
    "reported",
    "filed",
    "papers_pending",
    "projected",
}

CLOSEOUT_STATES = {"filed", "papers_pending", "projected"}
HARD_CLOSEOUT_STATES = {"completed", "reported", "filed"}
TASK_LINK_STATES = {"task_created", "scheduled", "working", "waiting", "completed", "reported", "filed"}
REMINDER_STATES = {"scheduled", "waiting"}
NO_ACTION_READBACKS = {
    "logged-no-action",
    "filed-previously-logged-to-handled",
    "duplicate",
    "already-routed",
    "already-handled",
    "no-action",
    "no_action_logged",
}

PACKET_FIELDS = (
    "source_ref",
    "dedupe_key",
    "intake_channel",
    "requester",
    "owner_lane",
    "responsible_worker_or_persona",
    "workspaceboard_session",
    "ops_portal_or_domain_task",
    "status",
    "due_or_trigger",
    "scheduled_action",
    "calendar_event",
    "clarification_email",
    "completion_or_blocker_email",
    "source_links",
    "approval_gates",
    "verification_readback",
    "papers_projection",
    "next_update",
)


def dedupe_key(source_ref: str, intake_channel: str = "") -> str:
    base = f"{intake_channel}:{source_ref}".strip(":")
    digest = hashlib.sha256(base.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"taskflow-{digest}"


def validate_status(status: str) -> str:
    normalized = str(status or "").strip()
    if normalized not in STATES:
        raise ValueError(f"Invalid task-flow status: {normalized}")
    return normalized


def build_packet(**values: Any) -> dict[str, Any]:
    packet = {field: values.get(field, "") for field in PACKET_FIELDS}
    packet["status"] = validate_status(str(packet.get("status") or "captured"))
    if not packet["source_ref"]:
        packet["source_ref"] = values.get("source_message_id") or values.get("id") or ""
    if not packet["dedupe_key"]:
        packet["dedupe_key"] = dedupe_key(str(packet["source_ref"]), str(packet["intake_channel"]))
    return packet


def can_file(packet: dict[str, Any], *, no_action: bool = False, duplicate: bool = False, already_routed: bool = False) -> bool:
    if no_action or duplicate or already_routed or is_no_action_closed(packet):
        return True
    status = str(packet.get("status") or "")
    if status in CLOSEOUT_STATES:
        return True
    if status == "reported" and packet.get("completion_or_blocker_email"):
        return True
    return False


def is_no_action_closed(packet: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(packet.get(field) or "")
        for field in ("verification_readback", "next_update", "approval_gates")
    ).lower()
    return any(marker in haystack for marker in NO_ACTION_READBACKS)


def missing_fields(packet: dict[str, Any]) -> list[str]:
    status = str(packet.get("status") or "")
    missing: list[str] = []
    for field in ("source_ref", "intake_channel", "owner_lane", "responsible_worker_or_persona"):
        if not str(packet.get(field) or "").strip():
            missing.append(field)
    if status in TASK_LINK_STATES and not str(packet.get("ops_portal_or_domain_task") or "").strip():
        missing.append("ops_portal_or_domain_task")
    if status in REMINDER_STATES and not any(str(packet.get(field) or "").strip() for field in ("due_or_trigger", "scheduled_action", "calendar_event")):
        missing.append("due_or_trigger_or_scheduled_action")
    if status in {"clarification_sent", "blocked"} and not is_no_action_closed(packet) and not any(str(packet.get(field) or "").strip() for field in ("clarification_email", "completion_or_blocker_email")):
        missing.append("clarification_or_blocker_email")
    if status in HARD_CLOSEOUT_STATES and not str(packet.get("verification_readback") or "").strip():
        missing.append("verification_readback")
    if status in {"reported", "filed"} and not str(packet.get("completion_or_blocker_email") or "").strip():
        missing.append("completion_or_blocker_email")
    return sorted(set(missing))


def projection_missing(packet: dict[str, Any]) -> bool:
    return str(packet.get("status") or "") in HARD_CLOSEOUT_STATES and not str(packet.get("papers_projection") or "").strip()


def closeout_allowed(packet: dict[str, Any], *, no_action: bool = False, duplicate: bool = False, already_routed: bool = False) -> tuple[bool, list[str]]:
    if no_action or duplicate or already_routed or is_no_action_closed(packet):
        return True, []
    missing = missing_fields(packet)
    return not (str(packet.get("status") or "") in HARD_CLOSEOUT_STATES and missing), missing


def guard_packet(packet: dict[str, Any], event: str = "") -> tuple[dict[str, Any], dict[str, Any]]:
    normalized = build_packet(**packet)
    missing = missing_fields(normalized)
    info = {
        "closeout_allowed": not (normalized["status"] in HARD_CLOSEOUT_STATES and missing),
        "missing_fields": missing,
        "papers_projection_missing": projection_missing(normalized),
        "requested_status": normalized["status"],
    }
    if not info["closeout_allowed"]:
        normalized = {
            **normalized,
            "status": "blocked",
            "verification_readback": normalized.get("verification_readback") or f"task_flow_closeout_guard_missing:{','.join(missing)}",
            "next_update": normalized.get("next_update") or "Complete required task-flow closeout fields before filing/reporting complete.",
        }
        info["guard_event"] = f"{event}_closeout_guard_blocked" if event else "closeout_guard_blocked"
    elif info["papers_projection_missing"]:
        normalized = {
            **normalized,
            "papers_projection": normalized.get("papers_projection") or "papers_pending",
        }
        info["guard_event"] = f"{event}_papers_pending" if event else "papers_pending"
    return normalized, info


def append_event(path: Path, packet: dict[str, Any], event: str, **values: Any) -> None:
    packet, guard = guard_packet(packet, event)
    if guard.get("guard_event"):
        values = {**values, "task_flow_guard": guard}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "event": event,
                    "packet": packet,
                    **values,
                },
                ensure_ascii=True,
            )
            + "\n"
    )
    path.chmod(0o600)
    if os.environ.get("TASK_FLOW_DISABLE_MYSQL") != "1":
        record_event_mysql(path.parent, packet, event, **values)


def record_event_mysql(state_dir: Path, packet: dict[str, Any], event: str, **values: Any) -> None:
    recorder = Path(os.environ.get("TASK_FLOW_MYSQL_RECORDER", "/Users/werkstatt/ai_workspace/scripts/task_flow_mysql_recorder.php"))
    if not recorder.exists():
        record_mysql_failure(state_dir, "recorder_missing", {"recorder": str(recorder), "event": event})
        return
    normalized = build_packet(**packet)
    payload = {"event": event, "packet": normalized, **values}
    try:
        subprocess.run(
            ["php", str(recorder), "record"],
            input=json.dumps(payload, ensure_ascii=True),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=True,
        )
    except Exception as exc:
        record_mysql_failure(
            state_dir,
            "record_failed",
            {"event": event, "dedupe_key": normalized.get("dedupe_key", ""), "error_type": exc.__class__.__name__},
        )
        if os.environ.get("TASK_FLOW_MYSQL_REQUIRED") == "1":
            raise


def record_mysql_failure(state_dir: Path, reason: str, values: dict[str, Any]) -> None:
    path = state_dir / "task-flow-mysql-failures.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "reason": reason, **values}, ensure_ascii=True) + "\n")
    path.chmod(0o600)


def packet_from_scheduled_action(row: dict[str, Any]) -> dict[str, Any]:
    source_ref = str(row.get("source_ref") or row.get("id") or "")
    task_id = row.get("ops_task_id") or row.get("task_id") or row.get("portal_task_id") or ""
    calendar_parts = [str(row.get("calendar_id") or ""), str(row.get("calendar_event_id") or "")]
    calendar_event = " ".join(part for part in calendar_parts if part)
    return build_packet(
        source_ref=source_ref,
        dedupe_key=row.get("dedupe_key") or "",
        intake_channel=row.get("intake_channel") or "scheduled-action:nationaloutreach",
        requester=row.get("requester") or "",
        owner_lane=row.get("owner_lane") or row.get("persona") or "nationaloutreach",
        responsible_worker_or_persona=row.get("persona") or row.get("from_name") or "nationaloutreach",
        workspaceboard_session=row.get("workspaceboard_session") or "",
        ops_portal_or_domain_task=str(task_id),
        status="scheduled",
        due_or_trigger=row.get("due_at") or "",
        scheduled_action=row.get("id") or "",
        calendar_event=calendar_event,
        clarification_email=row.get("clarification_email") or "",
        completion_or_blocker_email=row.get("completion_or_blocker_email") or "",
        source_links=row.get("source_links") or "",
        approval_gates=row.get("approval_gates") or "",
        verification_readback=row.get("verification_readback") or "",
        papers_projection=row.get("papers_projection") or "",
        next_update=row.get("next_update") or "",
    )
