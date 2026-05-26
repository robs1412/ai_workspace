#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import json
from email.utils import parseaddr
from pathlib import Path

import email_trace_recorder


MAILBOX_LANE = "nationaloutreach"
WORKER = "nationaloutreach"
EMAIL_ACCOUNT = "nationaloutreach@kovaldistillery.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill National Outreach mailbox state into ai_email_messages.")
    parser.add_argument("--state-dir", required=True)
    return parser.parse_args()


def normalize_message_id(value: object) -> str:
    return str(value or "").strip().strip("<>").lower()


def sender_email(value: object) -> str:
    return parseaddr(str(value or ""))[1].strip().lower()


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def iter_jsonl(path: Path):
    try:
        handle = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return
    with handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                yield row


def collect_latest_reviews(path: Path) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for row in iter_jsonl(path):
        source_id = normalize_message_id(row.get("source_message_id"))
        if not source_id:
            continue
        latest[source_id] = row
    return latest


def collect_archive_rows(path: Path) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for row in iter_jsonl(path):
        source_id = normalize_message_id(row.get("source_message_id"))
        if not source_id:
            continue
        latest[source_id] = row
    return latest


def collect_active_records(path: Path) -> dict[str, dict]:
    payload = read_json(path, {"messages": {}})
    messages = payload.get("messages") if isinstance(payload, dict) else {}
    if not isinstance(messages, dict):
        return {}
    active: dict[str, dict] = {}
    for source_id, row in messages.items():
        if not isinstance(row, dict):
            continue
        norm = normalize_message_id(source_id)
        if norm:
            active[norm] = row
    return active


def record_review_event(state_dir: Path, source_id: str, row: dict, active_records: dict[str, dict]) -> None:
    active_record = active_records.get(source_id, {})
    is_active = str(active_record.get("status") or "") == "active_inbox"
    message = email_trace_recorder.build_message_record(
        mailbox_lane=MAILBOX_LANE,
        worker=WORKER,
        event="email_reviewed",
        source_message_id=source_id,
        source_ref=source_id,
        subject=row.get("subject", ""),
        from_address=sender_email(row.get("from", "")),
        to_addresses=row.get("to", ""),
        cc_addresses=row.get("cc", ""),
        header_date=row.get("date", ""),
        email_account=EMAIL_ACCOUNT,
        direction="inbound",
        body_path=row.get("body_path", ""),
        body_chars=row.get("body_chars", ""),
        body_summary="",
        status=str((row.get("task_packet") or {}).get("status") or ("reviewed" if is_active else "classified")),
        first_seen_at=active_record.get("first_seen_at") or row.get("logged_at", ""),
        event_at=row.get("logged_at", ""),
        task_packet=row.get("task_packet") if isinstance(row.get("task_packet"), dict) else {},
        metadata={
            "route": row.get("route", ""),
            "send_allowed": row.get("send_allowed", ""),
            "suggestion": row.get("suggestion", ""),
            "active_inbox": is_active,
            "seen_before": bool(row.get("seen_before")),
            "review_reason": row.get("review_reason", ""),
        },
    )
    email_trace_recorder.record_event(
        state_dir,
        event="email_reviewed",
        message=message,
        task_packet=row.get("task_packet") if isinstance(row.get("task_packet"), dict) else {},
        details={"backfill": True, "route": row.get("route", ""), "review_reason": row.get("review_reason", "")},
    )


def record_archive_event(state_dir: Path, source_id: str, review_row: dict, archive_row: dict) -> None:
    message = email_trace_recorder.build_message_record(
        mailbox_lane=MAILBOX_LANE,
        worker=WORKER,
        event="email_archived",
        source_message_id=source_id,
        source_ref=source_id,
        subject=archive_row.get("subject", "") or review_row.get("subject", ""),
        from_address=sender_email(review_row.get("from", "")),
        to_addresses=review_row.get("to", ""),
        cc_addresses=review_row.get("cc", ""),
        header_date=review_row.get("date", ""),
        email_account=EMAIL_ACCOUNT,
        direction="inbound",
        body_path=review_row.get("body_path", ""),
        body_chars=review_row.get("body_chars", ""),
        body_summary="",
        status="archived",
        first_seen_at=review_row.get("logged_at", ""),
        event_at=archive_row.get("logged_at", ""),
        task_packet=review_row.get("task_packet") if isinstance(review_row.get("task_packet"), dict) else {},
        metadata={
            "route": review_row.get("route", ""),
            "send_allowed": review_row.get("send_allowed", ""),
            "archive_reason": archive_row.get("reason", ""),
            "active_inbox": False,
        },
    )
    email_trace_recorder.record_event(
        state_dir,
        event="email_archived",
        message=message,
        task_packet=review_row.get("task_packet") if isinstance(review_row.get("task_packet"), dict) else {},
        details={"backfill": True, "reason": archive_row.get("reason", ""), "action": archive_row.get("action", "")},
    )


def record_resolved_event(state_dir: Path, source_id: str, review_row: dict, active_record: dict) -> None:
    message = email_trace_recorder.build_message_record(
        mailbox_lane=MAILBOX_LANE,
        worker=WORKER,
        event="email_resolved_not_in_inbox",
        source_message_id=source_id,
        source_ref=source_id,
        subject=review_row.get("subject", "") or active_record.get("subject", ""),
        from_address=sender_email(review_row.get("from", "") or active_record.get("from", "")),
        to_addresses=review_row.get("to", "") or active_record.get("to", ""),
        cc_addresses=review_row.get("cc", "") or active_record.get("cc", ""),
        header_date=review_row.get("date", "") or active_record.get("date", ""),
        email_account=EMAIL_ACCOUNT,
        direction="inbound",
        body_path=review_row.get("body_path", "") or active_record.get("body_path", ""),
        body_chars=review_row.get("body_chars", "") or active_record.get("body_chars", ""),
        body_summary="",
        status="resolved_not_in_inbox",
        first_seen_at=active_record.get("first_seen_at", "") or review_row.get("logged_at", ""),
        event_at=active_record.get("resolved_at", "") or active_record.get("last_seen_at", ""),
        task_packet=review_row.get("task_packet") if isinstance(review_row.get("task_packet"), dict) else {},
        metadata={
            "route": active_record.get("route", "") or review_row.get("route", ""),
            "send_allowed": active_record.get("send_allowed", "") or review_row.get("send_allowed", ""),
            "active_inbox": False,
        },
    )
    email_trace_recorder.record_event(
        state_dir,
        event="email_resolved_not_in_inbox",
        message=message,
        task_packet=review_row.get("task_packet") if isinstance(review_row.get("task_packet"), dict) else {},
        details={"backfill": True, "previous_status": "active_inbox"},
    )


def main() -> int:
    args = parse_args()
    state_dir = Path(args.state_dir).expanduser()
    reviews = collect_latest_reviews(state_dir / "mail-review.jsonl")
    archives = collect_archive_rows(state_dir / "archive-log.jsonl")
    active_records = collect_active_records(state_dir / "active-inbox.json")

    reviewed = archived = resolved = 0
    for source_id, row in reviews.items():
        record_review_event(state_dir, source_id, row, active_records)
        reviewed += 1
    for source_id, row in archives.items():
        review_row = reviews.get(source_id, {})
        record_archive_event(state_dir, source_id, review_row, row)
        archived += 1
    for source_id, active_record in active_records.items():
        if str(active_record.get("status") or "") != "resolved_not_in_inbox":
            continue
        record_resolved_event(state_dir, source_id, reviews.get(source_id, {}), active_record)
        resolved += 1

    print(
        json.dumps(
            {
                "ok": True,
                "mailbox_lane": MAILBOX_LANE,
                "reviewed_backfilled": reviewed,
                "archived_backfilled": archived,
                "resolved_backfilled": resolved,
                "active_inbox_records": len(active_records),
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
