#!/usr/local/bin/python3.13
"""Send the weekly Allianz covered-account stop-ship report for OPS task 371818."""

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
SALESREPORT_HELPERS = Path("/Users/werkstatt/salesreport/invoice_compliance_helpers.php")
LOGIN_DATALOGIN = Path("/Users/werkstatt/login/datalogin.php")
DEFAULT_TASK_ID = 371818
DEFAULT_TO = "sebastian.saller@kovaldistillery.com"
DEFAULT_SEND_SCRIPT = ROOT / "scripts/send_codex_ops_email.py"
DEFAULT_CREDS_FILE = os.environ.get("CODEX_OPS_EMAIL_CREDS_FILE", "")
DEFAULT_SENT_LOG = Path("/Users/admin/.nationaloutreach-launch/state/sent-log.jsonl")
DEFAULT_STATE = ROOT / "tmp/allianz-stop-ship-weekly-report/latest.json"
DEFAULT_LOG = ROOT / "tmp/allianz-stop-ship-weekly-report/runs.jsonl"
REPORT_URL = "https://www.koval-distillery.com/salesreport/allianz_trade_compliance_logic.php"


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


def run_php(code: str, timeout: int = 45) -> str:
    proc = subprocess.run(
        ["php", "-r", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
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


def load_stop_ship_rows(days_back: int, limit: int) -> dict[str, Any]:
    php = (
        f"include '{LOGIN_DATALOGIN}';"
        f"require_once '{SALESREPORT_HELPERS}';"
        "if(!isset($db) || !($db instanceof mysqli)){fwrite(STDERR,'Salesreport mysqli connection missing'); exit(1);}"
        "$today=date('Y-m-d');"
        f"$from=date('Y-m-d', strtotime('-{max(1, min(days_back, 730))} days'));"
        f"$limit={max(1, min(limit, 1000))};"
        "$policy=koval_allianz_trade_policy_config();"
        "$raw=koval_invoice_compliance_fetch($db,$from,$today,$limit);"
        "$rows=koval_allianz_trade_source_rows($raw,$policy);"
        "$rows=koval_allianz_trade_enrich_rows($rows,$policy);"
        "$rows=array_values(array_filter($rows, static function(array $row): bool {"
        "return !empty($row['allianz_covered']) && !empty($row['allianz_stop_ship_required']);"
        "}));"
        "$summary=koval_allianz_trade_summarize($rows);"
        "$out=['from'=>$from,'to'=>$today,'raw_count'=>count($raw),'stop_ship_count'=>count($rows),'summary'=>$summary,'rows'=>array_slice($rows,0,100)];"
        "echo json_encode($out, JSON_UNESCAPED_SLASHES);"
    )
    payload = json.loads(run_php(php, timeout=60))
    return payload if isinstance(payload, dict) else {}


def advance_once(current: date, recurring_type: str) -> date:
    value = recurring_type.lower()
    if "biweek" in value:
        return current + timedelta(days=14)
    if "week" in value:
        return current + timedelta(days=7)
    if "day" in value:
        return current + timedelta(days=1)
    raise ValueError(f"Unsupported recurrence for Allianz task: {recurring_type or '[blank]'}")


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
        + json.dumps(f"Last Codex Allianz stop-ship report Message-ID: {message_id}")
        + ","
        + str(task_id)
        + "]);"
        "if($stmt->rowCount()<1){fwrite(STDERR,'No OPS task rows updated.'); exit(1);}"
    )
    run_php(code)


def money(value: object) -> str:
    try:
        return f"${float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def build_body(payload: dict[str, Any]) -> str:
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    lines = [
        "Sebastian,",
        "",
        f"Weekly Allianz covered-account stop-ship review for {payload.get('from', '')} through {payload.get('to', '')}:",
        "",
    ]
    if not rows:
        lines.extend(["No covered accounts are currently in the stop-ship review area.", ""])
    else:
        lines.extend(["Covered accounts currently in stop-ship review:", ""])
        for row in rows:
            account = str(row.get("account_name") or "Unknown account")
            invoice = str(row.get("invoice_no") or row.get("invoice_number") or "")
            status = str(row.get("allianz_status") or "Stop-ship review")
            exposure = money(row.get("portal_total"))
            days = int(row.get("days_overdue") or 0)
            covered = str(row.get("allianz_covered_name") or "")
            limit = money(row.get("allianz_approved_limit"))
            pieces = [f"- {account}"]
            if invoice:
                pieces.append(f"invoice {invoice}")
            pieces.append(f"{exposure}")
            pieces.append(f"{days} days overdue")
            pieces.append(status)
            if covered:
                pieces.append(f"covered as {covered}, limit {limit}")
            lines.append("; ".join(pieces))
        lines.append("")
    lines.extend([
        "Source: Allianz Trade compliance logic",
        REPORT_URL + "?payment_status=unpaid&alert_status=stop_ship&covered_only=1&show_all=0&limit=500",
        "",
        "Codex",
    ])
    return "\n".join(lines) + "\n"


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
    parser.add_argument("--subject", default="Weekly Allianz covered-account stop-ship review")
    parser.add_argument("--days-back", type=int, default=180)
    parser.add_argument("--row-limit", type=int, default=500)
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
    payload = load_stop_ship_rows(args.days_back, args.row_limit)
    body = build_body(payload)
    result: dict[str, Any] = {
        "ok": True,
        "task_id": task.task_id,
        "task_due_date": due_raw,
        "task_due": is_due,
        "forced": args.force,
        "dry_run": args.dry_run,
        "recipient": args.to,
        "from": payload.get("from", ""),
        "to": payload.get("to", ""),
        "raw_count": int(payload.get("raw_count") or 0),
        "stop_ship_count": int(payload.get("stop_ship_count") or 0),
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
