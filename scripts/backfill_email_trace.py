#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime, parseaddr
from pathlib import Path
from typing import Any

import email_trace_recorder
import shared_task_flow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill DB email trace rows from existing worker JSONL state.")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--now", default="")
    parser.add_argument("--owner-only", action="store_true", help="Only backfill direct owner / owner-instruction slices.")
    return parser.parse_args()


def parse_time(value: object) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if re_fullmatch_numeric(raw):
        try:
            return datetime.fromtimestamp(float(raw), tz=timezone.utc)
        except Exception:
            return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
        except Exception:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def re_fullmatch_numeric(raw: str) -> bool:
    try:
        float(raw)
        return True
    except Exception:
        return False


def sender_email(value: object) -> str:
    return parseaddr(str(value or ""))[1].strip().lower()


def nationaloutreach_owner_row(row: dict[str, Any]) -> bool:
    sender = sender_email(row.get("from", ""))
    if sender not in {"robert@kovaldistillery.com", "sonat@kovaldistillery.com"}:
        return False
    recipients = {sender_email(item) for item in normalize_addresses(row.get("to", "")) + normalize_addresses(row.get("cc", ""))}
    worker_aliases = {
        "vanessa.sterling@kovaldistillery.com",
        "naomi.stern@kovaldistillery.com",
        "ezra.katz@kovaldistillery.com",
        "codex@kovaldistillery.com",
    }
    route = str(row.get("route") or "")
    return bool(recipients & worker_aliases) or route in {"outreach-coordinator", "naomi-stern", "ezra-katz", "internal-communicator"}


def avignon_owner_action(action: dict[str, Any]) -> bool:
    classification = str(action.get("classification") or "")
    owner = str(action.get("owner") or "")
    sender = sender_email(action.get("from", ""))
    return classification.startswith("direct-owner") or owner in {"sonat", "robert-approver"} or sender in {"robert@kovaldistillery.com", "sonat@kovaldistillery.com"}


def normalize_addresses(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def iter_jsonl(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                yield row


def latest_rows_by_source(
    path: Path,
    *,
    source_key: str = "source_message_id",
    time_candidates: tuple[str, ...] = ("logged_at", "routed_at", "ack_sent_at", "date"),
    cutoff: datetime | None = None,
    predicate=None,
) -> dict[str, tuple[datetime, dict]]:
    latest: dict[str, tuple[datetime, dict]] = {}
    for row in iter_jsonl(path):
        if predicate is not None and not predicate(row):
            continue
        source_id = str(row.get(source_key) or "").strip()
        if not source_id:
            continue
        logged = None
        for key in time_candidates:
            logged = parse_time(row.get(key))
            if logged is not None:
                break
        if logged is None:
            continue
        if cutoff is not None and logged < cutoff:
            continue
        current = latest.get(source_id)
        if current is None or logged >= current[0]:
            latest[source_id] = (logged, row)
    return latest


def nationaloutreach_task_packet(row: dict[str, Any]) -> dict[str, Any]:
    packet = row.get("task_packet")
    if isinstance(packet, dict) and packet:
        return packet
    route = str(row.get("route") or "email-coordinator")
    status = "classified"
    if route in {"security-guard"}:
        status = "blocked"
    return shared_task_flow.build_packet(
        source_ref=str(row.get("source_message_id") or ""),
        intake_channel="email:nationaloutreach",
        requester=str(row.get("from") or ""),
        owner_lane=route,
        responsible_worker_or_persona=route,
        status=status,
        approval_gates=str(row.get("send_allowed") or ""),
        source_links=str(row.get("subject") or ""),
        next_update=str(row.get("suggestion") or ""),
    )


def avignon_task_packet(action: dict[str, Any]) -> dict[str, Any]:
    current_state = str(action.get("current_state") or "")
    decision = str(action.get("decision") or "")
    classification = str(action.get("classification") or "")
    status = "classified"
    if current_state == "routed_pending_completion":
        status = "working"
    elif current_state in {"blocked_report_sent", "captured_route_blocked_report_sent", "blocked_pending_security_guard"} or "blocked" in decision:
        status = "blocked"
    elif current_state in {"completed_report_sent", "no_action_logged"} or action.get("archived"):
        status = "reported"
    elif "decision-email" in decision or classification in {"ambiguous-email-review", "duplicate-ambiguous-email-review"}:
        status = "clarification_sent"
    return shared_task_flow.build_packet(
        source_ref=str(action.get("source_message_id") or ""),
        dedupe_key=str(action.get("dedupe_key") or ""),
        intake_channel="email:avignon",
        requester=str(action.get("from") or ""),
        owner_lane=str(action.get("owner") or "avignon"),
        responsible_worker_or_persona="avignon",
        workspaceboard_session=str(action.get("routed_session_id") or ""),
        ops_portal_or_domain_task=str(action.get("ops_portal_or_domain_task") or action.get("task_id") or ""),
        status=status,
        source_links=str(action.get("subject") or ""),
        approval_gates=classification,
        verification_readback=str(action.get("monitor_state") or decision),
        next_update=str(action.get("completion_target") or decision or ""),
        clarification_email=str(action.get("ack_message_id") or action.get("blocker_message_id") or ""),
        completion_or_blocker_email=str(action.get("completion_message_id") or action.get("blocker_message_id") or ""),
    )


def frank_owner_action(action: dict[str, Any]) -> bool:
    classification = str(action.get("classification") or "")
    sender = sender_email(action.get("from", ""))
    return (
        classification.startswith("primary")
        or classification.startswith("tracked-primary")
        or str(action.get("owner") or "") == "robert"
        or sender == "robert@kovaldistillery.com"
    )


def frank_task_packet(action: dict[str, Any]) -> dict[str, Any]:
    current_state = str(action.get("current_state") or "")
    decision = str(action.get("decision") or "")
    classification = str(action.get("classification") or "")
    status = "classified"
    if current_state in {"completed_report_sent", "blocked_report_sent"}:
        status = "reported"
    elif current_state == "routed_pending_completion":
        status = "working"
    elif current_state in {"blocked_pending_security_guard", "captured_route_blocked_report_sent"} or "blocked" in decision:
        status = "blocked"
    elif action.get("archived_to_handled") or decision.endswith("filed-to-handled") or "filed" in decision:
        status = "filed"
    elif action.get("sent_message_id") or action.get("completion_message_id") or action.get("ack_sent_message_id"):
        status = "reported" if "complete" in decision or "blocked" in decision else "clarification_sent"
    elif "route-still-open" in decision or "still-pending" in decision:
        status = "waiting"
    elif "routed" in decision or action.get("routed_session_id"):
        status = "working"
    elif "drafted" in decision or classification == "receipt":
        status = "working"
    elif "escalate" in decision:
        status = "clarification_needed"
    return shared_task_flow.build_packet(
        source_ref=str(action.get("source_message_id") or ""),
        dedupe_key=str(action.get("dedupe_key") or ""),
        intake_channel="email:frank",
        requester=str(action.get("from") or ""),
        owner_lane=str(action.get("owner") or "frank"),
        responsible_worker_or_persona="frank",
        workspaceboard_session=str(action.get("routed_session_id") or ""),
        ops_portal_or_domain_task=str(action.get("ops_portal_or_domain_task") or action.get("task_id") or action.get("thread_task_id") or ""),
        status=status,
        due_or_trigger=str(action.get("ack_held_until") or ""),
        source_links=str(action.get("subject") or ""),
        approval_gates=classification,
        verification_readback=str(action.get("monitor_state") or decision),
        next_update=str(action.get("completion_target") or decision or ""),
        clarification_email=str(action.get("ack_sent_message_id") or action.get("sent_message_id") or action.get("escalation_message_id") or ""),
        completion_or_blocker_email=str(action.get("completion_message_id") or ""),
    )


def backfill_nationaloutreach(cutoff: datetime, owner_only: bool) -> dict[str, int]:
    state_dir = Path("/Users/admin/.nationaloutreach-launch/state")
    counts = {"reviewed": 0, "archived": 0, "sent": 0}
    for row in iter_jsonl(state_dir / "mail-review.jsonl"):
        logged = parse_time(row.get("logged_at"))
        if not logged or logged < cutoff:
            continue
        if owner_only and not nationaloutreach_owner_row(row):
            continue
        source_id = str(row.get("source_message_id") or "").strip()
        if not source_id:
            continue
        packet = nationaloutreach_task_packet(row)
        message = email_trace_recorder.build_message_record(
            mailbox_lane="nationaloutreach",
            worker="nationaloutreach",
            event="email_reviewed",
            source_message_id=source_id,
            source_ref=source_id,
            subject=row.get("subject", ""),
            from_address=sender_email(row.get("from", "")),
            to_addresses=normalize_addresses(row.get("to", "")),
            cc_addresses=normalize_addresses(row.get("cc", "")),
            header_date=row.get("date", ""),
            email_account=row.get("email", ""),
            direction="inbound",
            body_path=row.get("body_path", ""),
            body_chars=row.get("body_chars", ""),
            body_summary="",
            status=str(packet.get("status") or "classified"),
            first_seen_at=logged.isoformat(),
            event_at=logged.isoformat(),
            task_packet=packet,
            metadata={"route": row.get("route", ""), "review_reason": row.get("review_reason", "")},
        )
        email_trace_recorder.record_event(state_dir, event="email_reviewed", message=message, task_packet=packet, details={"backfill": True})
        counts["reviewed"] += 1
    for row in iter_jsonl(state_dir / "archive-log.jsonl"):
        logged = parse_time(row.get("logged_at"))
        if not logged or logged < cutoff:
            continue
        if owner_only:
            continue
        source_id = str(row.get("source_message_id") or "").strip()
        if not source_id:
            continue
        message = email_trace_recorder.build_message_record(
            mailbox_lane="nationaloutreach",
            worker="nationaloutreach",
            event="email_archived",
            source_message_id=source_id,
            source_ref=source_id,
            subject=row.get("subject", ""),
            direction="inbound",
            status="archived",
            archived_at=logged.isoformat(),
            event_at=logged.isoformat(),
            metadata={"reason": row.get("reason", ""), "action": row.get("action", "")},
        )
        email_trace_recorder.record_event(state_dir, event="email_archived", message=message, details={"backfill": True, "reason": row.get("reason", "")})
        counts["archived"] += 1
    for row in iter_jsonl(state_dir / "sent-log.jsonl"):
        logged = parse_time(row.get("logged_at") or row.get("sent_at"))
        if not logged or logged < cutoff:
            continue
        if owner_only:
            source_ref = str(row.get("source_ref") or "").strip()
            if not source_ref or "mail.gmail.com" not in source_ref and "koval-distillery.com" not in source_ref:
                continue
        packet = row.get("task_packet") if isinstance(row.get("task_packet"), dict) else {}
        message = email_trace_recorder.build_message_record(
            mailbox_lane="nationaloutreach",
            worker="nationaloutreach",
            event="email_sent",
            message_id=row.get("message_id", ""),
            source_ref=row.get("source_ref", ""),
            subject=row.get("subject", ""),
            from_address=row.get("from", ""),
            email_account=row.get("from", ""),
            direction="outbound",
            status="reported",
            event_at=logged.isoformat(),
            task_packet=packet,
            metadata={"to_count": row.get("to_count", 0), "cc_count": row.get("cc_count", 0), "bcc_count": row.get("bcc_count", 0)},
        )
        email_trace_recorder.record_event(state_dir, event="email_sent", message=message, task_packet=packet, details={"backfill": True})
        counts["sent"] += 1
    return counts


def backfill_avignon(cutoff: datetime, owner_only: bool) -> dict[str, int]:
    state_dir = Path("/Users/admin/.avignon-launch/state")
    counts = {"action_logged": 0}
    for row in iter_jsonl(state_dir / "automation-log.jsonl"):
        logged = parse_time(row.get("logged_at"))
        if not logged or logged < cutoff:
            continue
        actions = row.get("message_actions")
        if not isinstance(actions, list):
            continue
        for action in actions:
            if not isinstance(action, dict):
                continue
            if owner_only and not avignon_owner_action(action):
                continue
            source_id = str(action.get("source_message_id") or "").strip()
            if not source_id:
                continue
            packet = avignon_task_packet(action)
            status = str(packet.get("status") or "classified")
            message = email_trace_recorder.build_message_record(
                mailbox_lane="avignon",
                worker="avignon",
                event="email_action_logged",
                source_message_id=source_id,
                source_ref=source_id,
                subject=action.get("subject", ""),
                from_address=sender_email(action.get("from", "")),
                header_date=action.get("date", ""),
                direction="inbound",
                status=status,
                first_seen_at=logged.isoformat(),
                event_at=logged.isoformat(),
                task_packet=packet,
                workspaceboard_session=action.get("routed_session_id", ""),
                ops_portal_or_domain_task=action.get("ops_portal_or_domain_task", "") or action.get("dedupe_key", ""),
                metadata={
                    "classification": action.get("classification", ""),
                    "decision": action.get("decision", ""),
                    "archived": bool(action.get("archived")),
                    "current_state": action.get("current_state", ""),
                },
                body_summary=action.get("classification", ""),
            )
            email_trace_recorder.record_event(state_dir, event="email_action_logged", message=message, task_packet=packet, details={"backfill": True})
            counts["action_logged"] += 1
    return counts


def backfill_frank(cutoff: datetime, owner_only: bool) -> dict[str, int]:
    state_dir = Path("/Users/admin/.frank-launch/state")
    counts = {"action_logged": 0, "sent": 0}
    latest_actions = latest_rows_by_source(
        state_dir / "automation-log.jsonl",
        cutoff=cutoff,
        predicate=(lambda row: frank_owner_action(row)) if owner_only else None,
    )
    for source_id, (logged, action) in latest_actions.items():
        packet = frank_task_packet(action)
        message = email_trace_recorder.build_message_record(
            mailbox_lane="frank",
            worker="frank",
            event="email_action_logged",
            source_message_id=source_id,
            source_ref=source_id,
            subject=action.get("subject", ""),
            from_address=sender_email(action.get("from", "")),
            to_addresses=normalize_addresses(action.get("to", "")),
            cc_addresses=normalize_addresses(action.get("cc", "")),
            header_date=action.get("date", ""),
            email_account="frank.cannoli@kovaldistillery.com",
            direction="inbound",
            status=str(packet.get("status") or "classified"),
            first_seen_at=logged.isoformat(),
            event_at=logged.isoformat(),
            task_packet=packet,
            workspaceboard_session=action.get("routed_session_id", ""),
            ops_portal_or_domain_task=action.get("ops_portal_or_domain_task", "") or action.get("task_id", ""),
            metadata={
                "classification": action.get("classification", ""),
                "decision": action.get("decision", ""),
                "current_state": action.get("current_state", ""),
                "archived_to_handled": bool(action.get("archived_to_handled")),
            },
            body_summary=action.get("summary", "") or action.get("classification", ""),
        )
        email_trace_recorder.record_event(state_dir, event="email_action_logged", message=message, task_packet=packet, details={"backfill": True})
        counts["action_logged"] += 1
    latest_sent = latest_rows_by_source(
        state_dir / "sent-log.jsonl",
        source_key="message_id",
        time_candidates=("date", "logged_at", "sent_at"),
        cutoff=cutoff,
        predicate=(lambda row: frank_owner_action(row)) if owner_only else None,
    )
    for _, (logged, row) in latest_sent.items():
        message = email_trace_recorder.build_message_record(
            mailbox_lane="frank",
            worker="frank",
            event="email_sent",
            message_id=row.get("message_id", ""),
            source_ref=row.get("source_ref", ""),
            subject=row.get("subject", ""),
            from_address=row.get("from", ""),
            to_addresses=normalize_addresses(row.get("to", "")),
            cc_addresses=normalize_addresses(row.get("cc", "")),
            email_account=row.get("from", ""),
            direction="outbound",
            status="reported",
            event_at=logged.isoformat(),
            task_packet={},
            metadata={"task_id": row.get("task_id", ""), "body_intent": row.get("body_intent", ""), "thread_task_id": row.get("thread_task_id", "")},
        )
        email_trace_recorder.record_event(state_dir, event="email_sent", message=message, details={"backfill": True})
        counts["sent"] += 1
    return counts


def main() -> int:
    args = parse_args()
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    if now is None:
        now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=args.days)
    result = {
        "cutoff": cutoff.isoformat(),
        "owner_only": bool(args.owner_only),
        "nationaloutreach": backfill_nationaloutreach(cutoff, bool(args.owner_only)),
        "avignon": backfill_avignon(cutoff, bool(args.owner_only)),
        "frank": backfill_frank(cutoff, bool(args.owner_only)),
    }
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
