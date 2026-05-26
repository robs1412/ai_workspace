#!/usr/local/bin/python3.13

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

RECORDER = Path(os.environ.get("EMAIL_TRACE_MYSQL_RECORDER", "/Users/werkstatt/ai_workspace/scripts/email_trace_mysql_recorder.php"))


def normalize_message_id(value: object) -> str:
    return str(value or "").strip().strip("<>").lower()


def normalize_subject(value: object) -> str:
    return " ".join(str(value or "").split()).strip()


def normalize_addresses(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if "," in text:
        return [item.strip() for item in text.split(",") if item.strip()]
    return [text]


def summarize_body(value: object, limit: int = 280) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


def build_message_record(
    *,
    mailbox_lane: str,
    worker: str,
    event: str,
    message_id: object = "",
    source_message_id: object = "",
    source_ref: object = "",
    subject: object = "",
    from_address: object = "",
    from_name: object = "",
    to_addresses: object = None,
    cc_addresses: object = None,
    bcc_addresses: object = None,
    header_date: object = "",
    email_account: object = "",
    direction: str = "inbound",
    body_path: object = "",
    body_chars: object = "",
    body_summary: object = "",
    status: object = "",
    archived_at: object = "",
    first_seen_at: object = "",
    event_at: object = "",
    task_packet: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    workspaceboard_session: object = "",
    ops_portal_or_domain_task: object = "",
) -> dict[str, Any]:
    task_packet = task_packet or {}
    message_id_norm = normalize_message_id(message_id or source_message_id)
    source_message_id_norm = normalize_message_id(source_message_id or message_id)
    source_ref_value = str(source_ref or source_message_id_norm or message_id_norm).strip()
    normalized_subject = normalize_subject(subject)
    thread_seed = "|".join(
        token
        for token in (
            mailbox_lane,
            normalize_subject(subject).lower(),
            str(from_address or "").strip().lower(),
        )
        if token
    )
    thread_key = hashlib.sha256(thread_seed.encode("utf-8", errors="replace")).hexdigest()[:32] if thread_seed else ""
    message_key_seed = "|".join(
        token
        for token in (
            mailbox_lane,
            message_id_norm,
            source_message_id_norm,
            source_ref_value,
            normalized_subject.lower(),
            str(header_date or "").strip(),
            direction,
        )
        if token
    )
    message_key = "email-" + hashlib.sha256(message_key_seed.encode("utf-8", errors="replace")).hexdigest()[:32]
    return {
        "message_key": message_key,
        "message_id_norm": message_id_norm,
        "source_message_id": source_message_id_norm,
        "source_ref": source_ref_value,
        "thread_key": thread_key,
        "mailbox_lane": mailbox_lane,
        "worker": worker,
        "direction": direction,
        "email_account": str(email_account or "").strip(),
        "subject": normalized_subject,
        "from_address": str(from_address or "").strip(),
        "from_name": str(from_name or "").strip(),
        "to_addresses": normalize_addresses(to_addresses),
        "cc_addresses": normalize_addresses(cc_addresses),
        "bcc_addresses": normalize_addresses(bcc_addresses),
        "header_date": str(header_date or "").strip(),
        "body_path": str(body_path or "").strip(),
        "body_chars": int(body_chars) if str(body_chars or "").strip() else None,
        "body_summary": summarize_body(body_summary),
        "task_flow_dedupe_key": str((task_packet or {}).get("dedupe_key") or "").strip(),
        "workspaceboard_session": str(workspaceboard_session or (task_packet or {}).get("workspaceboard_session") or "").strip(),
        "ops_portal_or_domain_task": str(ops_portal_or_domain_task or (task_packet or {}).get("ops_portal_or_domain_task") or "").strip(),
        "status": str(status or "").strip(),
        "first_seen_at": str(first_seen_at or "").strip(),
        "event_at": str(event_at or "").strip() or time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "archived_at": str(archived_at or "").strip(),
        "metadata": {"event": event, **(metadata or {})},
    }


def record_event(
    state_dir: Path,
    *,
    event: str,
    message: dict[str, Any],
    task_packet: dict[str, Any] | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    logged_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    payload = {
        "event": event,
        "message": message,
        "task_packet": task_packet or {},
        "details": details or {},
    }
    local_log = state_dir / "email-trace-events.jsonl"
    degraded_path = state_dir / "email-trace-db-degraded.json"
    db_failed = False
    db_error_type = ""
    try:
        subprocess.run(
            ["php", str(RECORDER), "record"],
            input=json.dumps(payload, ensure_ascii=True),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=True,
        )
    except Exception as exc:
        db_failed = True
        db_error_type = exc.__class__.__name__
        failure_path = state_dir / "email-trace-mysql-failures.jsonl"
        with failure_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "logged_at": logged_at,
                        "event": event,
                        "message_key": message.get("message_key", ""),
                        "error_type": db_error_type,
                    },
                    ensure_ascii=True,
                )
                + "\n"
            )
        failure_path.chmod(0o600)
        degraded_path.write_text(
            json.dumps(
                {
                    "logged_at": logged_at,
                    "event": event,
                    "message_key": message.get("message_key", ""),
                    "error_type": db_error_type,
                    "db_write_ok": False,
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        degraded_path.chmod(0o600)
    else:
        if degraded_path.exists():
            try:
                degraded_path.unlink()
            except OSError:
                pass
    local_row = {
        "logged_at": logged_at,
        "db_write_ok": not db_failed,
        "db_error_type": db_error_type,
        **payload,
    }
    try:
        with local_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(local_row, ensure_ascii=True) + "\n")
        local_log.chmod(0o600)
    except OSError:
        if db_failed:
            raise
