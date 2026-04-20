#!/usr/bin/env python3
"""Build a dry-run Frank completion-confirmation draft with duplicate checks.

This helper intentionally does not send email, connect to mailboxes, move mail,
or read credential files. It writes only local preview artifacts unless
--preview-only is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_TO = "robert@kovaldistillery.com"
DEFAULT_FROM_NAME = "Frank Cannoli"
DEFAULT_SIGNATURE_NOTE = (
    "[Signature rendered by the approved send helper. The HTML signature uses linked text for X.]"
)


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_message_id(value: str) -> str:
    cleaned = (value or "").strip()
    if cleaned.startswith("<") and cleaned.endswith(">"):
        cleaned = cleaned[1:-1]
    return cleaned.strip().lower()


def slugify(value: str, limit: int = 72) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    slug = re.sub(r"-{2,}", "-", slug)
    return (slug or "completion-confirmation")[:limit]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def parse_extra_log_paths(values: list[str]) -> list[Path]:
    return [Path(value).expanduser() for value in values if value.strip()]


def default_sent_logs(root: Path) -> list[Path]:
    return [
        root / "sent-log.jsonl",
        Path("/Users/admin/.frank-launch/state/sent-log.jsonl"),
    ]


def build_confirmation_key(task_id: str, source_message_id: str, tracked_task_id: str) -> str:
    parts = [
        task_id.strip(),
        normalize_message_id(source_message_id),
        tracked_task_id.strip(),
    ]
    raw = "|".join(parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"frank-completion:{slugify(task_id, 48)}:{digest}"


def duplicate_matches(
    *,
    confirmation_key: str,
    confirmation_task_id: str,
    source_message_id: str,
    tracked_task_id: str,
    draft_path: Path,
    sent_logs: list[Path],
    draft_log: Path,
) -> list[str]:
    matches: list[str] = []
    normalized_source = normalize_message_id(source_message_id)

    for path in sent_logs:
        for row in read_jsonl(path):
            row_source = normalize_message_id(str(row.get("source_message_id", "")))

            if str(row.get("confirmation_key", "")) == confirmation_key:
                matches.append(f"{path}: confirmation_key")
            elif str(row.get("task_id", "")) == confirmation_task_id:
                matches.append(f"{path}: task_id={confirmation_task_id}")
            elif normalized_source and row_source == normalized_source:
                matches.append(f"{path}: source Message-ID")

    for row in read_jsonl(draft_log):
        if str(row.get("confirmation_key", "")) == confirmation_key:
            matches.append(f"{draft_log}: confirmation_key")
        elif str(row.get("task_id", "")) == confirmation_task_id:
            matches.append(f"{draft_log}: task_id={confirmation_task_id}")
        elif tracked_task_id and str(row.get("tracked_task_id", "")) == tracked_task_id:
            matches.append(f"{draft_log}: tracked_task_id={tracked_task_id}")
        elif normalized_source and normalize_message_id(str(row.get("source_message_id", ""))) == normalized_source:
            matches.append(f"{draft_log}: source Message-ID")
        elif str(row.get("draft_path", "")) == str(draft_path):
            matches.append(f"{draft_log}: draft_path")

    if draft_path.exists():
        matches.append(f"{draft_path}: draft file exists")

    return sorted(set(matches))


def build_subject(task_id: str, subject: str | None) -> str:
    if subject:
        return subject.strip()
    return f"Frank completion confirmation: {task_id}"


def build_body(args: argparse.Namespace, subject: str, confirmation_key: str) -> str:
    owner = args.owner.strip() or "Robert"
    lines = [
        f"To: {args.to}",
        f"From: {DEFAULT_FROM_NAME}",
        f"Subject: {subject}",
        "",
        f"{owner},",
        "",
        f"{args.done.strip()} This task is complete.",
        "",
        "I recorded the task id, source reference, worker/session details, and duplicate key below so this confirmation can be traced later without resurfacing the same work as a new request.",
        "",
        "ID block:",
    ]
    if args.source_message_id:
        lines.append(f"- Source Message-ID: {args.source_message_id.strip()}")
    lines.extend(
        [
            f"- Dedupe key: {args.dedupe_key.strip() or confirmation_key}",
            f"- Local task ID: {args.task_id}",
            f"- Board/Codex session ID: {args.board_session.strip() or args.worker.strip() or 'not available'}",
            f"- Claude/bridge task ID: {args.claude_task_id.strip() or 'not available'}",
            f"- OPS/Portal task ID: {args.ops_task_id.strip() or 'none created'}",
            f"- Outbound Message-ID: {args.outbound_message_id.strip() or 'not sent yet'}",
            f"- Current status: {args.status.strip() or 'completed'}",
        ]
    )
    if args.tracked_task_id:
        lines.append(f"- Tracked outbound task_id: {args.tracked_task_id.strip()}")
    lines.extend(
        [
            f"- Completion confirmation key: {confirmation_key}",
            "",
            "[DRY RUN ONLY - not sent]",
            "",
            DEFAULT_SIGNATURE_NOTE,
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a dry-run Frank completion-confirmation draft with duplicate protection."
    )
    parser.add_argument("--task-id", required=True, help="Stable OPS/Portal/local Frank task id.")
    parser.add_argument(
        "--source-message-id",
        default="",
        help="Source email Message-ID that started the task, if available.",
    )
    parser.add_argument(
        "--tracked-task-id",
        default="",
        help="Tracked outbound task_id related to the task, if available.",
    )
    parser.add_argument(
        "--done",
        required=True,
        help="One concise sentence describing what was completed.",
    )
    parser.add_argument("--to", default=DEFAULT_TO, help="Preview recipient. Default: Robert.")
    parser.add_argument("--owner", default="Robert", help="Human owner name used in the draft.")
    parser.add_argument("--subject", default="", help="Optional preview subject.")
    parser.add_argument("--worker", default="", help="Optional worker/session reference.")
    parser.add_argument("--board-session", default="", help="Visible board/Codex session id.")
    parser.add_argument("--dedupe-key", default="", help="Stable local dedupe key.")
    parser.add_argument("--claude-task-id", default="", help="Claude task/ref id, if supplied by Claude or bridge logs.")
    parser.add_argument("--ops-task-id", default="", help="OPS/Portal task id when one was created.")
    parser.add_argument("--outbound-message-id", default="", help="Outbound report Message-ID, if already known.")
    parser.add_argument("--status", default="completed", help="Current task status for the ID block.")
    parser.add_argument(
        "--drafts-dir",
        default=str(workspace_root() / "drafts"),
        help="Directory for dry-run draft previews.",
    )
    parser.add_argument(
        "--draft-log",
        default=str(workspace_root() / "completion-confirmation-log.jsonl"),
        help="Dry-run JSONL log path.",
    )
    parser.add_argument(
        "--sent-log",
        action="append",
        default=[],
        help="Additional sent-log JSONL path to include in duplicate checks. Repeatable.",
    )
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Print preview JSON and draft body without writing draft/log files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON summary. Without this, prints a short text summary.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.source_message_id and not args.tracked_task_id:
        print(
            "Error: provide --source-message-id or --tracked-task-id for traceability.",
            file=sys.stderr,
        )
        return 2

    root = workspace_root()
    drafts_dir = Path(args.drafts_dir).expanduser()
    draft_log = Path(args.draft_log).expanduser()
    sent_logs = default_sent_logs(root) + parse_extra_log_paths(args.sent_log)

    confirmation_key = build_confirmation_key(
        args.task_id, args.source_message_id, args.tracked_task_id
    )
    confirmation_task_id = f"{args.task_id}:completion-confirmation"
    draft_path = drafts_dir / f"completion-confirmation-{slugify(confirmation_key)}.txt"
    subject = build_subject(args.task_id, args.subject)

    matches = duplicate_matches(
        confirmation_key=confirmation_key,
        confirmation_task_id=confirmation_task_id,
        source_message_id=args.source_message_id,
        tracked_task_id=args.tracked_task_id,
        draft_path=draft_path,
        sent_logs=sent_logs,
        draft_log=draft_log,
    )

    body = build_body(args, subject, confirmation_key)
    status = "duplicate" if matches else "drafted"
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    row = {
        "ts": now,
        "mode": "dry-run",
        "status": status,
        "confirmation_key": confirmation_key,
        "task_id": confirmation_task_id,
        "base_task_id": args.task_id,
        "source_message_id": args.source_message_id,
        "tracked_task_id": args.tracked_task_id,
        "to": args.to,
        "subject": subject,
        "draft_path": str(draft_path),
        "duplicate_matches": matches,
        "sent": False,
        "mailbox_mutated": False,
    }

    if matches:
        if args.json:
            print(json.dumps(row, ensure_ascii=True, indent=2, sort_keys=True))
        else:
            print("duplicate-skip")
            print(f"confirmation_key: {confirmation_key}")
            for match in matches:
                print(f"- {match}")
        return 3

    if args.preview_only:
        row["status"] = "preview-only"
    else:
        drafts_dir.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(body, encoding="utf-8")
        append_jsonl(draft_log, row)

    if args.json:
        print(json.dumps(row, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(row["status"])
        print(f"confirmation_key: {confirmation_key}")
        print(f"draft_path: {draft_path}")
        if args.preview_only:
            print("")
            print(body)

    return 0


if __name__ == "__main__":
    sys.exit(main())
