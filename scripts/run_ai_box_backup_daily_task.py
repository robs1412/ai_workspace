#!/usr/local/bin/python3.13

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

OPS_BOOTSTRAP = "/Users/werkstatt/ops/bootstrap.php"
BACKUP_SCRIPT = "/Users/werkstatt/ai_workspace/scripts/ai_box_backup.sh"
DEFAULT_TASK_ID = 369899
BACKUP_ROOT = Path("/Users/werkstatt/ai_box_backups")
STALE_SUCCESS_WARNING_DAYS = int(os.environ.get("AI_BOX_BACKUP_STALE_WARNING_DAYS", "2"))
WARNING_EMAIL_SCRIPT = Path("/Users/werkstatt/ai_workspace/scripts/send_codex_ops_email.py")
WARNING_EMAIL_TO = os.environ.get("AI_BOX_BACKUP_WARNING_TO", "robert@kovaldistillery.com")
WARNING_EMAIL_CREDS = os.environ.get(
    "AI_BOX_BACKUP_WARNING_CREDS_FILE",
    "/Users/werkstatt/ai_workspace/.private/mailboxes/nationaloutreach/credential.txt",
)
WARNING_EMAIL_SENT_LOG = os.environ.get(
    "AI_BOX_BACKUP_WARNING_SENT_LOG",
    "/Users/admin/.nationaloutreach-launch/state/sent-log.jsonl",
)
WARNING_EMAIL_DRY_RUN = os.environ.get("AI_BOX_BACKUP_WARNING_DRY_RUN", "0") == "1"


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


def parse_backup_created(value: str) -> datetime | None:
    value = value.strip()
    if re.fullmatch(r"\d{8}-\d{6}", value):
        return datetime.strptime(value, "%Y%m%d-%H%M%S")
    return None


def manifest_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def latest_successful_backup() -> dict[str, object]:
    latest: dict[str, object] = {"path": "", "created": "", "age_days": None}
    if not BACKUP_ROOT.is_dir():
        return latest
    newest_created: datetime | None = None
    newest_path: Path | None = None
    for manifest in BACKUP_ROOT.glob("*/MANIFEST.txt"):
        values = manifest_values(manifest)
        if values.get("remote_push_status") != "success":
            continue
        created = parse_backup_created(values.get("created", "")) or parse_backup_created(manifest.parent.name)
        if created is None:
            continue
        if newest_created is None or created > newest_created:
            newest_created = created
            newest_path = manifest.parent
    if newest_created is None or newest_path is None:
        return latest
    age = datetime.now() - newest_created
    return {
        "path": str(newest_path),
        "created": newest_created.strftime("%Y%m%d-%H%M%S"),
        "age_days": age.total_seconds() / 86400,
    }


def send_stale_success_warning(reason: str, latest_success: dict[str, object], backup_meta: dict[str, str], stdout_text: str, stderr_text: str) -> dict[str, str]:
    if not WARNING_EMAIL_SCRIPT.is_file():
        return {"status": "script_missing", "message_id": ""}
    body = (
        "Hi Robert,\n\n"
        "The AI box backup lane needs attention.\n\n"
        f"Reason: {reason}\n"
        f"Latest successful .205 push: {latest_success.get('path') or '[none found]'}\n"
        f"Latest successful timestamp: {latest_success.get('created') or '[none found]'}\n"
        f"Latest successful age days: {latest_success.get('age_days')}\n"
        f"Current run local backup: {backup_meta.get('backup', '')}\n"
        f"Current run remote_push_status: {backup_meta.get('remote_push_status', '')}\n"
        f"Current run warning_email_status: {backup_meta.get('warning_email_status', '')}\n\n"
        "This warning is sent because the latest successful remote backup is older than the configured stale threshold.\n\n"
        "Codex\n"
    )
    if stderr_text.strip():
        body += "\nNon-secret stderr summary:\n" + stderr_text.strip()[:1200] + "\n"
    elif stdout_text.strip():
        body += "\nNon-secret stdout summary:\n" + stdout_text.strip()[:1200] + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(body)
        body_path = handle.name
    cmd = [
        sys.executable,
        str(WARNING_EMAIL_SCRIPT),
        "--creds-file",
        WARNING_EMAIL_CREDS,
        "--to",
        WARNING_EMAIL_TO,
        "--subject",
        "AI box backup stale warning",
        "--body-file",
        body_path,
        "--from-address",
        "codex@kovaldistillery.com",
        "--from-name",
        "Codex Local Agent",
        "--sent-log",
        WARNING_EMAIL_SENT_LOG,
    ]
    if WARNING_EMAIL_DRY_RUN:
        cmd.append("--dry-run")
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            return {"status": "failed", "message_id": "", "error": (proc.stderr or proc.stdout).strip()[:500]}
        payload = json.loads(proc.stdout.strip() or "{}")
        return {
            "status": "dry_run" if WARNING_EMAIL_DRY_RUN else "sent",
            "message_id": str(payload.get("message_id", "")),
        }
    finally:
        Path(body_path).unlink(missing_ok=True)


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
        "$stmt=$pdo->prepare(\"UPDATE koval_crm.vtiger_activity AS a "
        "JOIN koval_crm.vtiger_crmentity AS e ON e.crmid=a.activityid "
        "SET a.date_start=?, a.due_date=?, a.status='Not Started', a.sendnotification=0, e.modifiedtime=NOW(), e.modifiedby=1332 "
        "WHERE a.activitytype='Task' AND a.activityid=?\");"
        "$stmt->execute(['" + new_due_date + "','" + new_due_date + "'," + str(task_id) + "]);"
        "if ($stmt->rowCount() < 1) { fwrite(STDERR, 'No OPS task rows updated.'); exit(1); }"
    )
    proc = subprocess.run(["php", "-r", query], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to advance OPS task.")


def main() -> int:
    task_id = DEFAULT_TASK_ID
    latest_success_before = latest_successful_backup()
    returncode, backup_meta, stdout_text, stderr_text = run_backup()
    latest_success_after = latest_successful_backup()
    result: dict[str, object] = {
        "task_id": task_id,
        "backup_exit_code": returncode,
        "backup": backup_meta.get("backup", ""),
        "remote_push_status": backup_meta.get("remote_push_status", ""),
        "warning_email_status": backup_meta.get("warning_email_status", ""),
        "warning_email_message_id": backup_meta.get("warning_email_message_id", ""),
        "latest_success_before": latest_success_before,
        "latest_success_after": latest_success_after,
    }
    stale_age = latest_success_after.get("age_days")
    stale = isinstance(stale_age, (int, float)) and stale_age > STALE_SUCCESS_WARNING_DAYS

    if returncode != 0:
        if stale:
            result["stale_success_warning"] = send_stale_success_warning(
                "backup wrapper failed",
                latest_success_after,
                backup_meta,
                stdout_text,
                stderr_text,
            )
        result["task_advanced"] = False
        result["stdout"] = stdout_text.strip()
        result["stderr"] = stderr_text.strip()
        print(json.dumps(result, ensure_ascii=True))
        return returncode

    if backup_meta.get("remote_push_status") != "success" and stale:
        if backup_meta.get("warning_email_status") in {"sent", "dry_run"}:
            result["stale_success_warning"] = {
                "status": "covered_by_remote_push_warning",
                "message_id": backup_meta.get("warning_email_message_id", ""),
            }
        else:
            result["stale_success_warning"] = send_stale_success_warning(
                "remote push failed and latest successful remote backup is stale",
                latest_success_after,
                backup_meta,
                stdout_text,
                stderr_text,
            )

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
