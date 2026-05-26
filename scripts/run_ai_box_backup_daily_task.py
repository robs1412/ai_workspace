#!/usr/local/bin/python3.13

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

OPS_BOOTSTRAP = "/Users/werkstatt/ops/bootstrap.php"
BACKUP_SCRIPT = "/Users/werkstatt/ai_workspace/scripts/ai_box_backup.sh"
DEFAULT_TASK_ID = 369899


def parse_key_value_output(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def run_backup() -> tuple[int, dict[str, str], str, str]:
    proc = subprocess.run(
        [BACKUP_SCRIPT],
        text=True,
        capture_output=True,
        check=False,
    )
    combined = "\n".join(part for part in [proc.stdout, proc.stderr] if part).strip()
    parsed = parse_key_value_output(combined)
    return proc.returncode, parsed, proc.stdout, proc.stderr


def load_task(task_id: int) -> dict[str, str]:
    query = (
        "require '" + OPS_BOOTSTRAP + "';"
        "$pdo=get_tracktime_pdo();"
        "$stmt=$pdo->prepare(\"SELECT activityid, subject, status, date_start, due_date, recurringtype "
        "FROM koval_crm.vtiger_activity WHERE activitytype='Task' AND activityid=?\");"
        "$stmt->execute([" + str(task_id) + "]);"
        "$row=$stmt->fetch(PDO::FETCH_ASSOC);"
        "echo json_encode($row, JSON_UNESCAPED_SLASHES);"
    )
    proc = subprocess.run(["php", "-r", query], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to query OPS task.")
    payload = json.loads(proc.stdout.strip() or "null")
    if not isinstance(payload, dict) or not payload:
        raise RuntimeError(f"OPS task {task_id} was not found.")
    return {str(k): "" if v is None else str(v) for k, v in payload.items()}


def advance_once(current: datetime, recurring_type: str) -> datetime:
    low = recurring_type.strip().lower()
    if "daily" in low or "every day" in low:
        return current + timedelta(days=1)
    if "biweek" in low:
        return current + timedelta(days=14)
    if "weekly" in low:
        return current + timedelta(days=7)
    if "monthly" in low:
        month = current.month + 1
        year = current.year
        if month > 12:
            month = 1
            year += 1
        day = min(
            current.day,
            [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1],
        )
        return current.replace(year=year, month=month, day=day)
    if "year" in low or "annual" in low:
        try:
            return current.replace(year=current.year + 1)
        except ValueError:
            return current.replace(year=current.year + 1, day=28)
    raise ValueError(f"Unsupported recurring type for daily task runner: {recurring_type or '[blank]'}")


def compute_next_due(due_date: str, recurring_type: str, minimum_after: date | None = None) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_date):
        raise ValueError(f"Invalid due date: {due_date}")
    current = datetime.strptime(due_date, "%Y-%m-%d")
    new_date = advance_once(current, recurring_type)
    floor = minimum_after or date.today()
    while new_date.date() <= floor:
        new_date = advance_once(new_date, recurring_type)
    return new_date.strftime("%Y-%m-%d")


def advance_task(task_id: int, new_due_date: str) -> None:
    query = (
        "require '" + OPS_BOOTSTRAP + "';"
        "$pdo=get_tracktime_pdo();"
        "$stmt=$pdo->prepare(\"UPDATE koval_crm.vtiger_activity "
        "SET date_start=?, due_date=?, status='Not Started', sendnotification=0 "
        "WHERE activitytype='Task' AND activityid=?\");"
        "$stmt->execute(['" + new_due_date + "','" + new_due_date + "'," + str(task_id) + "]);"
        "if ($stmt->rowCount() < 1) { fwrite(STDERR, 'No OPS task rows updated.'); exit(1); }"
    )
    proc = subprocess.run(["php", "-r", query], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to advance OPS task.")


def main() -> int:
    task_id = DEFAULT_TASK_ID
    returncode, backup_meta, stdout_text, stderr_text = run_backup()
    result: dict[str, object] = {
        "task_id": task_id,
        "backup_exit_code": returncode,
        "backup": backup_meta.get("backup", ""),
        "remote_push_status": backup_meta.get("remote_push_status", ""),
        "warning_email_status": backup_meta.get("warning_email_status", ""),
        "warning_email_message_id": backup_meta.get("warning_email_message_id", ""),
    }

    if returncode != 0:
        result["task_advanced"] = False
        result["stdout"] = stdout_text.strip()
        result["stderr"] = stderr_text.strip()
        print(json.dumps(result, ensure_ascii=True))
        return returncode

    task = load_task(task_id)
    recurring_type = task.get("recurringtype", "")
    due_date = task.get("due_date") or task.get("date_start") or ""
    new_due_date = compute_next_due(due_date, recurring_type, minimum_after=date.today())
    advance_task(task_id, new_due_date)
    refreshed = load_task(task_id)
    result.update(
        {
            "task_advanced": True,
            "old_due_date": due_date,
            "new_due_date": new_due_date,
            "recurringtype": recurring_type,
            "ops_readback_due_date": refreshed.get("due_date", ""),
            "ops_readback_date_start": refreshed.get("date_start", ""),
            "ops_readback_status": refreshed.get("status", ""),
        }
    )
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
