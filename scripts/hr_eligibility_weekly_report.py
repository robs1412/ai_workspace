#!/usr/local/bin/python3.13
"""Send the weekly OPS HR benefits eligibility report for Codex task 371791."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from email.utils import make_msgid
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
OPS_BOOTSTRAP = Path("/Users/werkstatt/ops/bootstrap.php")
DEFAULT_TASK_ID = 371791
DEFAULT_TO = "sebastian.saller@kovaldistillery.com"
DEFAULT_SEND_SCRIPT = ROOT / "scripts/send_codex_ops_email.py"
DEFAULT_CREDS_FILE = os.environ.get("CODEX_OPS_EMAIL_CREDS_FILE", "")
DEFAULT_SENT_LOG = Path("/Users/admin/.nationaloutreach-launch/state/sent-log.jsonl")
DEFAULT_STATE = ROOT / "tmp/hr-eligibility-weekly-report/latest.json"
DEFAULT_LOG = ROOT / "tmp/hr-eligibility-weekly-report/runs.jsonl"


@dataclass(frozen=True)
class TaskState:
    task_id: int
    subject: str
    status: str
    due_date: str
    date_start: str
    recurringtype: str
    owner_user_id: int
    assigned_user_ids: list[int]


def run_php(code: str) -> str:
    proc = subprocess.run(
        ["php", "-r", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or "PHP command failed.")
    return proc.stdout


def load_task(task_id: int) -> TaskState:
    code = (
        f"require '{OPS_BOOTSTRAP}';"
        "$pdo=get_event_pdo();"
        "$stmt=$pdo->prepare(\"SELECT act.activityid, act.subject, act.status, act.due_date, "
        "act.date_start, act.recurringtype, ent.smownerid "
        "FROM koval_crm.vtiger_activity act "
        "JOIN koval_crm.vtiger_crmentity ent ON ent.crmid=act.activityid "
        "WHERE act.activityid=? AND act.activitytype='Task' LIMIT 1\");"
        f"$stmt->execute([{task_id}]);"
        "$task=$stmt->fetch(PDO::FETCH_ASSOC);"
        "if(!$task){fwrite(STDERR,'Task not found'); exit(1);}"
        "$a=$pdo->prepare('SELECT user_id FROM koval_crm.activity2user WHERE activity_id=? ORDER BY user_id');"
        f"$a->execute([{task_id}]);"
        "$task['assigned_user_ids']=$a->fetchAll(PDO::FETCH_COLUMN);"
        "echo json_encode($task, JSON_UNESCAPED_SLASHES);"
    )
    payload = json.loads(run_php(code))
    return TaskState(
        task_id=int(payload.get("activityid") or task_id),
        subject=str(payload.get("subject") or ""),
        status=str(payload.get("status") or ""),
        due_date=str(payload.get("due_date") or ""),
        date_start=str(payload.get("date_start") or ""),
        recurringtype=str(payload.get("recurringtype") or ""),
        owner_user_id=int(payload.get("smownerid") or 0),
        assigned_user_ids=[int(value) for value in payload.get("assigned_user_ids") or []],
    )


def load_hr_rows(limit: int) -> list[dict[str, Any]]:
    code = (
        f"require '{OPS_BOOTSTRAP}';"
        f"$rows=ops_hr_eligibility_rows({max(1, min(limit, 500))});"
        "echo json_encode($rows, JSON_UNESCAPED_SLASHES);"
    )
    rows = json.loads(run_php(code))
    return rows if isinstance(rows, list) else []


def parse_display_date(value: object) -> date | None:
    text = str(value or "").strip()
    if not text or text == "-":
        return None
    text = text.replace("\u2014", "").strip()
    for fmt in ("%b %d, %Y", "%b %e, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def eligible_items(rows: list[dict[str, Any]], today: date, days_ahead: int) -> list[dict[str, Any]]:
    window_end = today + timedelta(days=days_ahead)
    items: list[dict[str, Any]] = []
    for row in rows:
        benefits: list[str] = []
        health_trigger = parse_display_date(row.get("health_trigger"))
        fsa_trigger = parse_display_date(row.get("fsa_trigger"))
        k401_trigger = parse_display_date(row.get("k401_trigger"))
        if health_trigger and today <= health_trigger <= window_end and not row.get("health_enrolled"):
            benefits.append(f"Health Insurance, eligible {row.get('health_eligibility')}")
        if fsa_trigger and today <= fsa_trigger <= window_end:
            benefits.append(f"FSA/DCA, eligible {row.get('fsa_eligibility')}")
        if k401_trigger and today <= k401_trigger <= window_end and not row.get("k401_enrolled"):
            benefits.append(f"401(k), entry {row.get('k401_entry')}")
        if not benefits:
            continue
        items.append(
            {
                "user_id": int(row.get("user_id") or 0),
                "name": str(row.get("name") or "Unknown"),
                "status": str(row.get("status") or ""),
                "hire_date": str(row.get("hire_date") or ""),
                "benefits": benefits,
            }
        )
    return items


def advance_once(current: date, recurring_type: str) -> date:
    value = recurring_type.lower()
    if "biweek" in value:
        return current + timedelta(days=14)
    if "week" in value:
        return current + timedelta(days=7)
    if "day" in value:
        return current + timedelta(days=1)
    raise ValueError(f"Unsupported recurrence for HR eligibility task: {recurring_type or '[blank]'}")


def next_due_date(task: TaskState, minimum_after: date) -> str:
    raw = task.due_date or task.date_start
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise ValueError(f"Invalid OPS task due date: {raw}")
    current = datetime.strptime(raw, "%Y-%m-%d").date()
    candidate = advance_once(current, task.recurringtype)
    while candidate <= minimum_after:
        candidate = advance_once(candidate, task.recurringtype)
    return candidate.isoformat()


def advance_task(task_id: int, due_date: str, message_id: str) -> None:
    code = (
        f"require '{OPS_BOOTSTRAP}';"
        "$pdo=get_event_pdo();"
        "$stmt=$pdo->prepare(\"UPDATE koval_crm.vtiger_activity AS a "
        "JOIN koval_crm.vtiger_crmentity AS e ON e.crmid=a.activityid "
        "SET a.date_start=?, a.due_date=?, a.status='Not Started', a.sendnotification=1, "
        "e.description=CONCAT(COALESCE(e.description,''), CHAR(10), CHAR(10), ?), "
        "e.modifiedtime=NOW(), e.modifiedby=1332 "
        "WHERE a.activitytype='Task' AND a.activityid=?\");"
        "$stmt->execute(["
        + json.dumps(due_date)
        + ","
        + json.dumps(due_date)
        + ","
        + json.dumps(f"Last Codex HR eligibility report Message-ID: {message_id}")
        + ","
        + str(task_id)
        + "]);"
        "if($stmt->rowCount()<1){fwrite(STDERR,'No OPS task rows updated.'); exit(1);}"
    )
    run_php(code)


def build_body(items: list[dict[str, Any]], today: date, days_ahead: int) -> str:
    header = [
        "Sebastian,",
        "",
        f"Weekly HR benefits eligibility review for {today.isoformat()} through {(today + timedelta(days=days_ahead)).isoformat()}:",
        "",
    ]
    if not items:
        body = ["No new eligibility is due in the next week.", ""]
    else:
        body = ["The following employees are now eligible or due for eligibility review:", ""]
        for item in items:
            body.append(f"- {item['name']} (User #{item['user_id']}, {item['status']}, hire date {item['hire_date']})")
            for benefit in item["benefits"]:
                body.append(f"  - {benefit}")
        body.append("")
    footer = [
        "Source: OPS HR Benefits & Eligibility",
        "https://www.koval-distillery.com/ops/index.php?view=hr_eligibility",
        "",
        "Codex",
    ]
    return "\n".join(header + body + footer) + "\n"


def send_email(args: argparse.Namespace, body: str) -> str:
    if not args.creds_file:
        if args.dry_run:
            return make_msgid(domain="kovaldistillery.com")
        raise RuntimeError("Codex ops email credential path is not configured.")
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
            args.to,
            "--subject",
            args.subject,
            "--body-file",
            str(body_path),
            "--from-address",
            "codex@kovaldistillery.com",
            "--from-name",
            "Codex Local Agent",
            "--sent-log",
            str(args.sent_log),
        ]
        if args.dry_run:
            command.append("--dry-run")
        proc = subprocess.run(command, text=True, capture_output=True, check=False, timeout=45)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip() or "Email send failed.")
        payload = json.loads(proc.stdout.strip() or "{}")
        return str(payload.get("message_id") or ("dry-run" if args.dry_run else ""))
    finally:
        body_path.unlink(missing_ok=True)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", type=int, default=DEFAULT_TASK_ID)
    parser.add_argument("--to", default=DEFAULT_TO)
    parser.add_argument("--subject", default="Weekly HR benefits eligibility report")
    parser.add_argument("--days-ahead", type=int, default=7)
    parser.add_argument("--row-limit", type=int, default=200)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--send-script", type=Path, default=DEFAULT_SEND_SCRIPT)
    parser.add_argument("--creds-file", default=DEFAULT_CREDS_FILE)
    parser.add_argument("--sent-log", type=Path, default=DEFAULT_SENT_LOG)
    parser.add_argument("--force", action="store_true", help="Send even when the OPS task is not due.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    today = date.today()
    task = load_task(args.task_id)
    due_raw = task.due_date or task.date_start
    is_due = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_raw) and datetime.strptime(due_raw, "%Y-%m-%d").date() <= today)
    rows = load_hr_rows(args.row_limit)
    items = eligible_items(rows, today, args.days_ahead)
    body = build_body(items, today, args.days_ahead)
    result: dict[str, Any] = {
        "ok": True,
        "task_id": task.task_id,
        "task_due_date": due_raw,
        "task_due": is_due,
        "forced": args.force,
        "dry_run": args.dry_run,
        "recipient": args.to,
        "eligible_count": len(items),
        "eligible_items": items,
        "sent": False,
        "message_id": "",
        "advanced_to": "",
    }
    if is_due or args.force:
        message_id = send_email(args, body)
        result["sent"] = not args.dry_run
        result["message_id"] = message_id
        if not args.dry_run:
            new_due = next_due_date(task, today)
            advance_task(task.task_id, new_due, message_id)
            result["advanced_to"] = new_due
    else:
        result["skipped_reason"] = "task_not_due"

    args.state.parent.mkdir(parents=True, exist_ok=True)
    args.state.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(args.log, result)
    if args.print_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
