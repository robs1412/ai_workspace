#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import json
from pathlib import Path

import email_trace_recorder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed DB email trace rows from header-worker seen caches.")
    parser.add_argument("--worker", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--email-account", required=True)
    return parser.parse_args()


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def normalize_message_id(value: object) -> str:
    return str(value or "").strip().strip("<>").lower()


def main() -> int:
    args = parse_args()
    worker = str(args.worker or "").strip().lower()
    state_dir = Path(args.state_dir).expanduser()
    seen_payload = read_json(state_dir / "seen-headers.json", {"seen_message_ids": []})
    seen_ids = [normalize_message_id(item) for item in seen_payload.get("seen_message_ids", []) if normalize_message_id(item)]
    count = 0
    for source_id in seen_ids:
        message = email_trace_recorder.build_message_record(
            mailbox_lane=worker,
            worker=worker,
            event="email_action_logged",
            source_message_id=source_id,
            source_ref=source_id,
            subject="",
            email_account=args.email_account,
            direction="inbound",
            status="new-header-only-unprocessed",
            first_seen_at="",
            event_at="",
            metadata={"classification": "new-header-only-unprocessed", "backfill_seen_cache": True},
        )
        email_trace_recorder.record_event(
            state_dir,
            event="email_action_logged",
            message=message,
            details={"backfill_seen_cache": True},
        )
        count += 1
    print(json.dumps({"ok": True, "worker": worker, "seeded": count}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
