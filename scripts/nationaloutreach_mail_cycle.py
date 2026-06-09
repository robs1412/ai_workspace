#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import html
import imaplib
import json
import contextlib
import mimetypes
import os
import re
import shutil
import smtplib
import ssl
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import EmailMessage, Message
from email.utils import formataddr, formatdate, make_msgid, parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Optional

try:
    import shared_task_flow
except ImportError:  # pragma: no cover - installed runtime should keep helper beside this script.
    shared_task_flow = None

try:
    import mailbox_imap_helpers as mailbox_helpers
except ImportError:  # pragma: no cover - installed runtime should keep helper beside this script.
    mailbox_helpers = None

try:
    import email_trace_recorder
except ImportError:  # pragma: no cover - installed runtime should keep helper beside this script.
    email_trace_recorder = None


SCRIPT_DIR = Path(__file__).resolve().parent
SCHEDULED_ACTIONS_RECORDER = Path("/Users/werkstatt/ai_workspace/scripts/scheduled_actions_mysql_recorder.php")
DEFAULT_MITCH_REPORT_SCRIPT = SCRIPT_DIR / "build_mitch_weekly_report.php"
LEGACY_MITCH_REPORT_SCRIPT = Path("/Users/werkstatt/ai_workspace/nationaloutreach/scripts/build_mitch_weekly_report.php")


ALLOWED_FROM = {
    "codex@kovaldistillery.com",
    "vanessa.sterling@kovaldistillery.com",
    "naomi.stern@kovaldistillery.com",
    "ezra.katz@kovaldistillery.com",
}

FORBIDDEN_FROM = {
    "nationaloutreach@kovaldistillery.com",
    "nationoutreach@kovaldistillery.com",
    "tastingroom@kovaldistillery.com",
}

VERIFIED_SEND_AS_ALIASES = {
    "codex@kovaldistillery.com",
    "vanessa.sterling@kovaldistillery.com",
    "naomi.stern@kovaldistillery.com",
    "ezra.katz@kovaldistillery.com",
}

FROM_DISPLAY_NAMES = {
    "codex@kovaldistillery.com": "Codex Local Agent",
    "vanessa.sterling@kovaldistillery.com": "Vanessa Sterling",
    "naomi.stern@kovaldistillery.com": "Naomi Stern",
    "ezra.katz@kovaldistillery.com": "Ezra Katz",
}

ROBERT_EMAIL = "robert@kovaldistillery.com"
SONAT_EMAIL = "sonat@kovaldistillery.com"

SOCIAL_LINKS = {
    "X": "http://www.x.com/kovaldistillery",
    "Instagram": "http://www.instagram.com/kovaldistillery",
    "Facebook": "http://www.facebook.com/kovaldistillery",
}

SOCIAL_SIGNATURE_RE = re.compile(r"^\s*X\s*\|\s*Instagram\s*\|\s*Facebook\s*$", re.IGNORECASE | re.MULTILINE)
SOCIAL_SIGNATURE_TEXT_RE = re.compile(r"X\s*\|\s*Instagram\s*\|\s*Facebook", re.IGNORECASE)

SENSITIVE_PATTERNS = re.compile(
    r"\b(password|passcode|2fa|verification code|wire|bank account|routing number|gift card|urgent payment|w-?9|ssn|social security|credential|oauth|token)\b",
    re.IGNORECASE,
)

NAOMI_PATTERNS = re.compile(
    r"\b(naomi stern|finance operations|financial operations|cash flow|cashflow|accounts payable|accounts receivable|payables|receivables|invoice|invoices|bill payment|collections|month-end|month end|close readiness|reconciliation|budget|forecast|cash controls)\b",
    re.IGNORECASE,
)

EZRA_PATTERNS = re.compile(
    r"\b(ezra katz|special projects|legal affairs|legal|lawyer|attorney|counsel|regulatory|permit|license|licence|ttb|tax and trade|label approval|cola|trademark|contract|liability|lawsuit|subpoena|cease and desist|privileged|policy question|document follow-up|approval tracking)\b",
    re.IGNORECASE,
)

OUTREACH_PATTERNS = re.compile(
    r"\b(tasting|demo|sampling|outreach|event|venue|account visit|binny'?s|mariano'?s|whole foods|availability|available|shift|calendar|schedule)\b",
    re.IGNORECASE,
)

ORDINARY_RETAIL_TASTING_PATTERNS = re.compile(
    r"\b((binny'?s|mariano'?s|whole foods)[^\n]{0,120}\b(tasting|event|calendar|schedule|shift|availability|account visit|store opening)\b|\b(tasting|event|calendar|schedule|shift|availability|account visit|store opening)\b[^\n]{0,120}(binny'?s|mariano'?s|whole foods))\b",
    re.IGNORECASE,
)

MARKETING_PATTERNS = re.compile(
    r"\b(campaign|newsletter|press|media|magazine|distributor email|forge|mailchimp|phplist|promo|promotion)\b",
    re.IGNORECASE,
)

NEWSLETTER_SENDER_PATTERNS = re.compile(
    r"(@klaviyomail\.com\b|@shared1\.ccsend\.com\b|@mailchimp(?:app)?\.net\b|@campaign-archive\.com\b)",
    re.IGNORECASE,
)

NEWSLETTER_BODY_PATTERNS = re.compile(
    r"\b(unsubscribe|manage preferences|view in browser|email preferences|privacy policy|you received this email)\b",
    re.IGNORECASE,
)

INTERNAL_PATTERNS = re.compile(
    r"\b(team|staff|internal|employee|availability|schedule|shift|reminder)\b",
    re.IGNORECASE,
)

STAFFING_PATTERNS = re.compile(
    r"\b(COT|team member|new team|staffing|open shifts?|shift switch|shift coverage|upcoming shifts?|weekend shift|availability|available|schedule)\b",
    re.IGNORECASE,
)

OWNER_QUESTION_PATTERNS = re.compile(
    r"\b(have you received|did you receive|did you get my email|checking if you received|following up on my email|follow-up on my email|just checking in|please confirm receipt|receipt confirmation)\b",
    re.IGNORECASE,
)

DIRECT_FORWARD_INSTRUCTION_PATTERNS = re.compile(
    r"(?i)(please\s+send\s+this\s+to|send\s+this\s+to|please\s+forward\s+this\s+to|forward\s+this\s+to|please\s+pass\s+this\s+to|pass\s+this\s+to)"
)

DIRECT_OUTREACH_CALENDAR_PATTERNS = re.compile(
    r"(?i)(add[\s\S]{0,80}(outreach calendar|calendar)|assign shift|e-?mail me confirmation of completion|email me confirmation of completion|create[\s\S]{0,80}(outreach calendar|calendar)|put[\s\S]{0,80}(outreach calendar|calendar))"
)

DIRECT_INTERNAL_WORK_PATTERNS = re.compile(
    r"(?i)(\bcodex\b|build out skills|workflow\s+\d|portal sample request|barrel samples|record activities in portal|crm_integration)"
)

AI_TASK_FLOW_PATTERNS = re.compile(
    r"(?i)(task assessment manual|secretary\s*\+\s*pm agent|pm agent|how i assess, review, and create tasks|planner task|specialists \(|email dispatcher|structured acceptance criteria|detailed post in papers|share with you a complete manual)"
)

ROUTE_PERSONAS = {
    "outreach-coordinator": "vanessa.sterling@kovaldistillery.com",
    "internal-communicator": "vanessa.sterling@kovaldistillery.com",
    "naomi-stern": "naomi.stern@kovaldistillery.com",
    "ezra-katz": "ezra.katz@kovaldistillery.com",
    "marketing-manager": "marketing-manager",
    "security-guard": "security-guard",
    "portal-auth": "Codex / Portal login worker",
    "email-coordinator": "email-coordinator",
}

TASK_FLOW_AUTO_ROUTED_ROUTES = {
    "outreach-coordinator",
    "internal-communicator",
    "naomi-stern",
    "ezra-katz",
}

ACTIVE_INBOX_LOG_INTERVAL_SECONDS = 15 * 60
OVERDUE_REPORT_SUBJECT_RE = re.compile(r"^Overdue Reports Summary - ", re.IGNORECASE)
PORTAL_AUTH_CODE_SUBJECT_RE = re.compile(r"^\s*(two-factor authentication code|verification code)\s*$", re.IGNORECASE)


def resolve_mitch_report_script() -> Path:
    configured = str(os.environ.get("NATIONALOUTREACH_BUILD_MITCH_REPORT") or "").strip()
    if configured:
        return Path(configured)
    if DEFAULT_MITCH_REPORT_SCRIPT.is_file():
        return DEFAULT_MITCH_REPORT_SCRIPT
    return LEGACY_MITCH_REPORT_SCRIPT


def shared_sent_log_state_dirs(state_dir: Path) -> list[Path]:
    candidates = [
        state_dir,
        Path("/Users/admin/.frank-launch/state"),
        Path("/Users/admin/.avignon-launch/state"),
    ]
    seen: set[Path] = set()
    result: list[Path] = []
    for candidate in candidates:
        if not candidate:
            continue
        normalized = candidate.resolve() if candidate.exists() else candidate
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(candidate)
    return result


def write_jsonl_rows_atomic(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(r, ensure_ascii=True) for r in rows) + ("\n" if rows else "")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
        path.chmod(0o600)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="National Outreach full-body mailbox cycle with approved queued sends.")
    parser.add_argument("--creds-file", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--mailbox", default="INBOX")
    parser.add_argument("--search", default="ALL")
    parser.add_argument("--send-approved", action="store_true", help="Send queued *.approved.json files from outbox.")
    parser.add_argument("--review-old", action="store_true", help="Include already seen messages in review output.")
    parser.add_argument("--from-address", default="codex@kovaldistillery.com")
    parser.add_argument(
        "--archive-redundant-overdue-reports",
        action="store_true",
        help="Archive older KOVAL Portal overdue report summaries from INBOX, keeping only the newest copy.",
    )
    parser.add_argument(
        "--archive-self-sent-inbox-copies",
        action="store_true",
        help="Archive INBOX copies of messages sent from this mailbox or its approved aliases.",
    )
    parser.add_argument(
        "--archive-replied-inbox",
        action="store_true",
        help="Archive INBOX items that already have a later reply from this mailbox or its approved aliases, excluding direct-owner instructions that still require explicit completion proof.",
    )
    return parser.parse_args()


def decode_value(value: str) -> str:
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def load_credentials(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    user = values.get("user", "")
    password = values.get("app password") or values.get("app pw") or values.get("app-pw") or values.get("app_pw") or values.get("password") or ""
    if not user or not password:
        raise ValueError("Credential file must contain User and App password entries.")
    return {
        "user": user,
        "password": password,
        "imap_server": values.get("mail server", "") or values.get("imap server", "") or "imap.gmail.com",
        "imap_port": values.get("imap ssl port", "993") or "993",
        "smtp_server": values.get("smtp server", "") or "smtp.gmail.com",
        "smtp_port": values.get("smtp ssl port", "465") or "465",
    }


def append_message_to_sent_folder(creds: dict[str, str], msg: EmailMessage) -> str:
    raw_message = msg.as_bytes()
    last_error = ""

    def imap_mailbox_arg(folder: str) -> str:
        value = str(folder or "")
        if value.startswith('"') and value.endswith('"'):
            return value
        if any(ch.isspace() for ch in value) or any(ch in value for ch in ['"', '\\']):
            return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        return value

    conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]), timeout=30)
    try:
        conn.login(creds["user"], creds["password"])
        candidates: list[str] = []
        try:
            status, folders = conn.list()
        except Exception:
            status, folders = "NO", []
        if status == "OK":
            for raw_folder in folders or []:
                text = raw_folder.decode("utf-8", errors="replace") if isinstance(raw_folder, bytes) else str(raw_folder)
                match = re.search(r'(?:"([^"]+)"| ([^ ]+))$', text)
                folder = (match.group(1) or match.group(2)) if match else ""
                if folder and ("\\Sent" in text or "sent" in folder.lower()):
                    candidates.append(folder)
        candidates.extend(["INBOX.Sent", "Sent", "Sent Mail", "[Gmail]/Sent Mail"])
        ordered_candidates: list[str] = []
        seen_candidates: set[str] = set()
        for folder in candidates:
            key = folder.lower()
            if key in seen_candidates:
                continue
            seen_candidates.add(key)
            ordered_candidates.append(folder)
        for folder in ordered_candidates:
            try:
                status, _ = conn.append(imap_mailbox_arg(folder), "\\Seen", imaplib.Time2Internaldate(time.time()), raw_message)
                if status == "OK":
                    return folder
            except Exception as exc:
                last_error = f"{folder}: {exc}"
    finally:
        with contextlib.suppress(Exception):
            conn.logout()
    raise RuntimeError(f"sent folder append failed for {msg.get('Message-ID', '')}: {last_error or 'no sent folder accepted APPEND'}")


def normalize_message_id(value: str) -> str:
    return str(value or "").strip().strip("<>").lower()


def normalize_subject(value: str) -> str:
    return " ".join(str(value or "").split()).strip().lower()


def sender_email(value: str) -> str:
    return parseaddr(str(value or ""))[1].strip().lower()


def sender_name(value: str) -> str:
    return parseaddr(str(value or ""))[0].strip()


def is_internal_koval_sender(value: str) -> bool:
    email_value = sender_email(value)
    return email_value.endswith("@kovaldistillery.com")


def owner_question_target(headers: dict[str, str], classification: dict[str, str]) -> tuple[str, str]:
    source_from = str(headers.get("from", "") or "").strip()
    if classification.get("send_allowed") == "routine-if-clear" and is_internal_koval_sender(source_from):
        email_value = sender_email(source_from)
        if email_value:
            return email_value, sender_name(source_from) or email_value
    return ROBERT_EMAIL, "Robert"


def text_addresses(value: object) -> set[str]:
    if mailbox_helpers is not None:
        return mailbox_helpers.email_addresses_from_text(str(value or ""))
    email_value = sender_email(str(value or ""))
    return {email_value} if email_value else set()


def parse_header_timestamp(value: str) -> Optional[float]:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def read_jsonl_tail(path: Path, max_lines: int = 5000) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
    except (FileNotFoundError, OSError):
        return []
    rows: list[dict] = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    path.chmod(0o600)


def record_email_trace(state_dir: Path, *, event: str, message: dict, task_packet: dict | None = None, details: dict | None = None) -> None:
    if email_trace_recorder is None:
        return
    email_trace_recorder.record_event(
        state_dir,
        event=event,
        message=message,
        task_packet=task_packet or {},
        details=details or {},
    )


def build_email_trace_message(**values) -> dict:
    if email_trace_recorder is None:
        return {}
    return email_trace_recorder.build_message_record(**values)


def is_direct_owner_instruction_record(record: dict) -> bool:
    sender = sender_email(record.get("from") or "")
    if sender not in {ROBERT_EMAIL, "sonat@kovaldistillery.com"}:
        return False
    recipients: set[str] = set()
    for field in ("to", "cc"):
        recipients.update(text_addresses(record.get(field) or ""))
    worker_aliases = {
        "vanessa.sterling@kovaldistillery.com",
        "naomi.stern@kovaldistillery.com",
        "ezra.katz@kovaldistillery.com",
        "codex@kovaldistillery.com",
    }
    return bool(recipients & worker_aliases)


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return default


def parse_due_at(value: str) -> Optional[float]:
    raw = str(value or "").strip()
    if not raw:
        return None
    normalized = raw.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def mailbox_has_matching_reply(creds: dict[str, str], check: dict) -> bool:
    if mailbox_helpers is None:
        return False
    return mailbox_helpers.mailbox_has_matching_reply(creds, check)


def mailbox_has_matching_reply_from_aliases(
    creds: dict[str, str],
    from_contains_list: list[str],
    subject_contains: str,
    after_header_date: str,
) -> bool:
    if mailbox_helpers is None:
        return False
    return mailbox_helpers.mailbox_has_matching_reply_from_aliases(
        creds,
        from_contains_list,
        subject_contains,
        after_header_date,
    )


def scheduled_actions_db_rows(mailbox_lane: str) -> list[dict]:
    if not SCHEDULED_ACTIONS_RECORDER.exists():
        return []
    try:
        result = subprocess.run(
            ["php", str(SCHEDULED_ACTIONS_RECORDER), "rows", mailbox_lane],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    try:
        payload = json.loads(result.stdout.strip() or "[]")
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def scheduled_actions_db_upsert(mailbox_lane: str, rows: list[dict]) -> bool:
    if not SCHEDULED_ACTIONS_RECORDER.exists():
        return False
    try:
        subprocess.run(
            ["php", str(SCHEDULED_ACTIONS_RECORDER), "upsert", mailbox_lane],
            input=json.dumps(rows, ensure_ascii=True),
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def acquire_scheduled_actions_lock(state_dir: Path, now_ts: Optional[float] = None) -> tuple[bool, bool]:
    lock_dir = state_dir / "scheduled-actions.lock"
    try:
        lock_dir.mkdir()
        return True, False
    except FileExistsError:
        pass

    max_age = int(os.environ.get("NATIONALOUTREACH_SCHEDULED_ACTION_LOCK_MAX_AGE_SECONDS", "900") or "900")
    now = time.time() if now_ts is None else now_ts
    try:
        lock_age = now - lock_dir.stat().st_mtime
    except OSError:
        lock_age = 0
    if lock_age < max_age:
        return False, False

    with contextlib.suppress(OSError):
        lock_dir.rmdir()
    try:
        lock_dir.mkdir()
        append_jsonl(
            state_dir / "scheduled-actions-log.jsonl",
            {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "status": "stale_lock_recovered",
                "lock_age_seconds": int(lock_age),
                "max_age_seconds": max_age,
            },
        )
        return True, True
    except FileExistsError:
        return False, False


def scheduled_actions_lock_health(state_dir: Path, skipped_locked: bool, now_ts: Optional[float] = None) -> dict:
    if not skipped_locked:
        return {
            "skip_streak": 0,
            "lock_age_seconds": 0,
            "actionable": False,
        }

    lock_dir = state_dir / "scheduled-actions.lock"
    now = time.time() if now_ts is None else now_ts
    max_age = int(os.environ.get("NATIONALOUTREACH_SCHEDULED_ACTION_LOCK_MAX_AGE_SECONDS", "900") or "900")
    try:
        lock_age = max(0, int(now - lock_dir.stat().st_mtime))
    except OSError:
        lock_age = 0

    streak = 1
    for row in reversed(read_jsonl_tail(state_dir / "cycle-log.jsonl", 25)):
        if row.get("scheduled_actions_skipped_locked"):
            streak += 1
            continue
        break
    actionable = streak >= 3 or lock_age >= max_age
    if actionable:
        append_jsonl(
            state_dir / "scheduled-actions-log.jsonl",
            {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "status": "scheduled_lock_actionable",
                "skip_streak": streak,
                "lock_age_seconds": lock_age,
                "max_age_seconds": max_age,
            },
        )
    return {
        "skip_streak": streak,
        "lock_age_seconds": lock_age,
        "actionable": actionable,
    }


def process_scheduled_actions(creds: dict[str, str], state_dir: Path, now_ts: Optional[float] = None) -> dict:
    schedule_path = state_dir / "scheduled-actions.jsonl"
    rows = scheduled_actions_db_rows("nationaloutreach")
    if not rows and schedule_path.exists():
        rows = read_jsonl_tail(schedule_path, 20000)
    if not rows:
        return {"due": 0, "queued": 0, "skipped_resolved": 0, "failed": 0}
    now = time.time() if now_ts is None else now_ts
    lock_dir = state_dir / "scheduled-actions.lock"
    lock_acquired, stale_lock_recovered = acquire_scheduled_actions_lock(state_dir, now)
    if not lock_acquired:
        return {"due": 0, "queued": 0, "skipped_resolved": 0, "failed": 0, "skipped_locked": True}
    updated_rows = []
    due = queued = skipped_resolved = failed = 0
    outbox = state_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    outbox.chmod(0o700)
    try:
        for row in rows:
            if not isinstance(row, dict):
                failed += 1
                continue
            status = str(row.get("status") or "pending")
            due_ts = parse_due_at(str(row.get("due_at") or ""))
            if status != "pending" or due_ts is None or due_ts > now:
                updated_rows.append(row)
                continue
            due += 1
            task_packet = shared_task_flow.packet_from_scheduled_action(row) if shared_task_flow else {}
            if shared_task_flow:
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", task_packet, "scheduled_action_due")
            checks = row.get("resolution_checks") if isinstance(row.get("resolution_checks"), list) else []
            if any(mailbox_has_matching_reply(creds, c) for c in checks if isinstance(c, dict)):
                row["status"] = "resolved_no_send"
                row["resolved_at"] = datetime.now(timezone.utc).isoformat()
                updated_rows.append(row)
                append_jsonl(state_dir / "scheduled-actions-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "action_id": row.get("id"), "status": "resolved_no_send"})
                if shared_task_flow:
                    resolved_packet = {**task_packet, "status": "completed", "verification_readback": "resolution_check_matched"}
                    shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", resolved_packet, "scheduled_action_resolved_no_send")
                skipped_resolved += 1
                continue
            payload = row.get("email")
            if str(row.get("kind") or "") == "mitch_weekly_report_draft":
                report_start = str(row.get("report_start") or str(row.get("due_at") or "")[:10])
                try:
                    proc = subprocess.run(
                        [
                            "php",
                            str(resolve_mitch_report_script()),
                            "--start",
                            report_start,
                        ],
                        check=True,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    payload = json.loads(proc.stdout)
                except Exception as exc:
                    row["status"] = "failed"
                    row["error"] = f"report_generation_failed: {exc}"
                    updated_rows.append(row)
                    append_jsonl(state_dir / "scheduled-actions-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "action_id": row.get("id"), "status": "failed", "error": row["error"]})
                    if shared_task_flow:
                        failed_packet = {**task_packet, "status": "blocked", "verification_readback": row["error"]}
                        shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", failed_packet, "scheduled_action_failed", error=row["error"])
                    failed += 1
                    continue
            if not isinstance(payload, dict):
                row["status"] = "failed"
                row["error"] = "missing_email_payload"
                updated_rows.append(row)
                if shared_task_flow:
                    failed_packet = {**task_packet, "status": "blocked", "verification_readback": row["error"]}
                    shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", failed_packet, "scheduled_action_failed", error=row["error"])
                failed += 1
                continue
            draft_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(row.get("id") or f"scheduled-{int(now)}")).strip("-") + ".approved.json"
            draft_path = outbox / draft_name
            draft_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
            draft_path.chmod(0o600)
            row["status"] = "queued"
            row["queued_at"] = datetime.now(timezone.utc).isoformat()
            row["queued_draft"] = str(draft_path)
            updated_rows.append(row)
            append_jsonl(state_dir / "scheduled-actions-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "action_id": row.get("id"), "status": "queued", "draft": str(draft_path)})
            if shared_task_flow:
                queued_packet = {**task_packet, "status": "working", "scheduled_action": row.get("id") or "", "next_update": "queued approved draft for send cycle"}
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", queued_packet, "scheduled_action_queued", draft=str(draft_path))
            queued += 1
        write_jsonl_rows_atomic(schedule_path, updated_rows)
        scheduled_actions_db_upsert("nationaloutreach", updated_rows)
        return {"due": due, "queued": queued, "skipped_resolved": skipped_resolved, "failed": failed, "skipped_locked": False, "stale_lock_recovered": stale_lock_recovered}
    finally:
        if lock_acquired:
            with contextlib.suppress(OSError):
                lock_dir.rmdir()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def html_to_text(value: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value or "")
    text = re.sub(r"(?i)<(br|/p|/div|/li|/h[1-6])\b[^>]*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def message_text(msg: Message) -> str:
    plain_parts: list[str] = []
    html_parts: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = (part.get("Content-Disposition") or "").lower()
            if "attachment" in content_disposition:
                continue
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if content_type == "text/plain":
                plain_parts.append(text)
            elif content_type == "text/html":
                html_parts.append(html_to_text(text))
    else:
        payload = msg.get_payload(decode=True)
        if payload is not None:
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html_parts.append(html_to_text(text))
            else:
                plain_parts.append(text)
    text = "\n\n".join(part.strip() for part in plain_parts if part.strip())
    if not text:
        text = "\n\n".join(part.strip() for part in html_parts if part.strip())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def routing_body(body: str) -> str:
    active = re.split(r"(?im)^\s*On .+ wrote:\s*$", body, maxsplit=1)[0]
    active = re.split(r"(?i)\bConfidentiality Notice:", active, maxsplit=1)[0]
    active = re.split(r"(?i)\bThe information transmitted is intended only\b", active, maxsplit=1)[0]
    return active.strip()


def classify_message(headers: dict[str, str], body: str) -> dict[str, str]:
    combined = f"{headers.get('subject', '')}\n{headers.get('from', '')}\n{headers.get('to', '')}\n{headers.get('cc', '')}\n{routing_body(body)}"
    sender = sender_email(headers.get("from", ""))
    if is_portal_auth_code_message(headers, body):
        return {
            "route": "portal-auth",
            "suggestion": "Portal auth-code intake. Use immediately for the active Codex Portal login flow or silent-login path; otherwise file as stale auth residue. Do not escalate this to Robert as a blocker.",
            "send_allowed": "no-owner-escalation",
        }
    if SENSITIVE_PATTERNS.search(combined):
        return {
            "route": "security-guard",
            "suggestion": "Review as sensitive/security-gated before any reply or filing.",
            "send_allowed": "no",
        }
    if sender == ROBERT_EMAIL and DIRECT_INTERNAL_WORK_PATTERNS.search(combined):
        return {
            "route": "email-coordinator",
            "suggestion": "Direct Robert internal work instruction. Do not send the Vanessa routine acknowledgement; route this to the correct internal worker or AI Manager lane instead.",
            "send_allowed": "approval-required",
        }
    if AI_TASK_FLOW_PATTERNS.search(combined):
        return {
            "route": "email-coordinator",
            "suggestion": "Internal AI task-flow or workflow-manual thread. Route to Codex / AI Manager lane for classifier, task-flow, or workflow follow-through; do not send the Vanessa routine acknowledgement.",
            "send_allowed": "approval-required",
        }
    if NAOMI_PATTERNS.search(combined):
        return {
            "route": "naomi-stern",
            "suggestion": "Route to Naomi Stern for finance-operations triage: cash/control/cadence status, missing sources, and owner decisions. Do not move money or change finance records.",
            "send_allowed": "approval-required",
        }
    if sender == ROBERT_EMAIL and DIRECT_FORWARD_INSTRUCTION_PATTERNS.search(combined):
        return {
            "route": "outreach-coordinator",
            "suggestion": "Direct Robert forward/send-to instruction. Do not send the generic Vanessa acknowledgement; send the requested recipient-facing message or route one exact blocker.",
            "send_allowed": "approval-required",
        }
    if ORDINARY_RETAIL_TASTING_PATTERNS.search(combined) and not EZRA_PATTERNS.search(combined):
        return {
            "route": "outreach-coordinator",
            "suggestion": "Route to Vanessa Sterling for ordinary Binny's / Mariano's / Whole Foods tasting coordination through OPS. Keep the tone practical and treat this as scheduling/state work, not legal review.",
            "send_allowed": "routine-if-clear",
        }
    if EZRA_PATTERNS.search(combined):
        return {
            "route": "ezra-katz",
            "suggestion": "Route to Ezra Katz for special-project/legal-affairs coordination and a counsel-ready business brief. Keep the tone practical; do not send external legal/regulatory replies or approve regulated action.",
            "send_allowed": "approval-required",
        }
    if STAFFING_PATTERNS.search(combined):
        return {
            "route": "outreach-coordinator",
            "suggestion": "Route to Vanessa Sterling for COTeam staffing, shift, schedule, or team-member follow-up through Task Manager and OPS where needed.",
            "send_allowed": "routine-if-clear",
        }
    if sender == ROBERT_EMAIL and DIRECT_OUTREACH_CALENDAR_PATTERNS.search(combined):
        return {
            "route": "outreach-coordinator",
            "suggestion": "Direct Robert instruction: create or update the OPS outreach event/calendar entry, assign the requested shift in OPS, copy the requested notes, and send Robert completion proof. Do not send the generic Vanessa routine-follow-up acknowledgement.",
            "send_allowed": "approval-required",
        }
    if MARKETING_PATTERNS.search(combined):
        return {
            "route": "marketing-manager",
            "suggestion": "Review for Marketing Manager or Communications Manager; use Forge/campaign route if this is audience/bulk work.",
            "send_allowed": "approval-required",
        }
    if OUTREACH_PATTERNS.search(combined):
        return {
            "route": "outreach-coordinator",
            "suggestion": "Review for Outreach Coordinator; likely needs OPS Outreach/calendar/team availability follow-up.",
            "send_allowed": "routine-if-clear",
        }
    if INTERNAL_PATTERNS.search(combined):
        return {
            "route": "internal-communicator",
            "suggestion": "Review for Internal Communicator; likely team update/reminder/availability workflow.",
            "send_allowed": "routine-if-clear",
        }
    if OWNER_QUESTION_PATTERNS.search(combined):
        return {
            "route": "outreach-coordinator",
            "suggestion": "Ask Robert one clarification question by email and include the original source email for review.",
            "send_allowed": "routine-if-clear",
        }
    return {
        "route": "email-coordinator",
        "suggestion": "Review ownership; no strong automatic route detected.",
        "send_allowed": "approval-required",
    }


def is_newsletter_no_action_candidate(headers: dict[str, str], body: str, classification: dict[str, str]) -> bool:
    sender = sender_email(headers.get("from", ""))
    subject = clean_subject(headers.get("subject", ""))
    combined = f"{subject}\n{headers.get('from', '')}\n{routing_body(body)}"
    if sender in {ROBERT_EMAIL, SONAT_EMAIL}:
        return False
    if OWNER_QUESTION_PATTERNS.search(combined):
        return False
    if DIRECT_FORWARD_INSTRUCTION_PATTERNS.search(combined):
        return False
    if ORDINARY_RETAIL_TASTING_PATTERNS.search(combined):
        return False
    if STAFFING_PATTERNS.search(combined):
        return False
    newsletter_sender = bool(NEWSLETTER_SENDER_PATTERNS.search(sender))
    newsletter_body = bool(NEWSLETTER_BODY_PATTERNS.search(combined))
    marketing_like = bool(MARKETING_PATTERNS.search(combined))
    no_thread = not clean_subject(headers.get("in_reply_to", "")) and not clean_subject(headers.get("references", ""))
    no_action_subject = bool(re.search(r"\b(our first ever|new release|newsletter|new vintage|release)\b", subject, re.IGNORECASE))
    route = str(classification.get("route") or "")
    return no_thread and (
        (newsletter_sender and (newsletter_body or marketing_like or no_action_subject))
        or (newsletter_body and no_action_subject)
        or (route == "marketing-manager" and newsletter_body)
    )


def task_flow_persona_for_route(route: str) -> str:
    return ROUTE_PERSONAS.get(str(route or ""), str(route or "email-coordinator"))


def task_flow_status_for_classification(classification: dict[str, str]) -> str:
    return "routed" if classification.get("route") in TASK_FLOW_AUTO_ROUTED_ROUTES else "classified"


def task_flow_event_for_status(status: str) -> str:
    return "email_classified"


def task_flow_next_update(classification: dict[str, str]) -> str:
    suggestion = classification.get("suggestion", "")
    persona = task_flow_persona_for_route(classification.get("route", ""))
    if task_flow_status_for_classification(classification) == "classified":
        return f"Classified for {persona}; Task Manager should create or reuse a visible worker route and record completion or blocker. {suggestion}".strip()
    return suggestion


def owner_question_subject(subject: str) -> str:
    subject = re.sub(r"[\r\n]+", " ", str(subject or "")).strip()
    if not subject:
        return "Re: clarification needed"
    if subject.lower().startswith("re:"):
        return subject
    return f"Re: {subject}"


def clean_subject(subject: str) -> str:
    return re.sub(r"[\r\n]+", " ", str(subject or "")).strip()


def is_portal_auth_code_message(headers: dict[str, str], body: str) -> bool:
    sender = sender_email(headers.get("from", ""))
    subject = clean_subject(headers.get("subject", ""))
    recipients = f"{headers.get('to', '')}\n{headers.get('cc', '')}".lower()
    active = routing_body(body)
    return (
        sender == "crm@koval-distillery.com"
        and "codex@kovaldistillery.com" in recipients
        and bool(PORTAL_AUTH_CODE_SUBJECT_RE.search(subject))
        and bool(re.search(r"\b(code|two-factor|verification)\b", active, re.IGNORECASE))
    )


def is_no_action_auth_code_candidate(headers: dict[str, str], body: str, classification: dict[str, str]) -> bool:
    return classification.get("route") == "portal-auth" and is_portal_auth_code_message(headers, body)


def is_generic_acknowledgement_body(body: str) -> bool:
    normalized = "\n".join(str(body or "").strip().splitlines()).strip().lower()
    return normalized == "\n".join(
        [
            "hi,",
            "",
            "thanks, i have this and will handle the routine outreach follow-up from here.",
            "",
            "best,",
            "",
            "vanessa",
        ]
    )


def quoted_original_message_block(headers: dict[str, str], body: str) -> str:
    original = routing_body(body) or str(body or "").strip()
    lines = [
        "Original message:",
        f"From: {headers.get('from', '')}",
        f"To: {headers.get('to', '')}",
        f"Cc: {headers.get('cc', '')}",
        f"Date: {headers.get('date', '')}",
        f"Subject: {headers.get('subject', '')}",
        "",
        original,
    ]
    return "\n".join(f"> {line}" if line else ">" for line in lines).strip()


def owner_question_body(headers: dict[str, str], body: str, owner_name: str) -> str:
    original = routing_body(body)
    return "\n".join(
        [
            f"Hi {owner_name},",
            "",
            "This message looks like a receipt-check or other unclear follow-up. Should Vanessa reply to confirm receipt, or is there a different action you want taken?",
            "",
            "Original message for review:",
            f"From: {headers.get('from', '')}",
            f"To: {headers.get('to', '')}",
            f"Cc: {headers.get('cc', '')}",
            f"Date: {headers.get('date', '')}",
            f"Subject: {headers.get('subject', '')}",
            "",
            original or body.strip(),
            "",
            "Best,",
            "",
            "Vanessa",
            "",
            "Vanessa Sterling",
        ]
    ).strip()


def owner_question_draft_exists(state_dir: Path, source_id: str) -> bool:
    outbox = state_dir / "outbox"
    if outbox.exists():
        for draft_path in outbox.glob("*.approved.json"):
            try:
                payload = read_json(draft_path, {})
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            if normalize_message_id(payload.get("source_ref") or payload.get("source_message_id") or "") == normalize_message_id(source_id):
                return True
    if mailbox_helpers is not None:
        sent_entries = mailbox_helpers.collect_sent_entries_from_state_dirs(shared_sent_log_state_dirs(state_dir))
        if mailbox_helpers.sent_entries_have_source_ref(sent_entries, source_id):
            return True
    return False


def routine_reply_draft_exists(state_dir: Path, source_id: str) -> bool:
    outbox = state_dir / "outbox"
    if outbox.exists():
        for draft_path in outbox.glob("*.approved.json"):
            try:
                payload = read_json(draft_path, {})
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            if normalize_message_id(payload.get("source_ref") or payload.get("source_message_id") or "") == normalize_message_id(source_id):
                return True
    if mailbox_helpers is not None:
        sent_entries = mailbox_helpers.collect_sent_entries_from_state_dirs(shared_sent_log_state_dirs(state_dir))
        if mailbox_helpers.sent_entries_have_source_ref(sent_entries, source_id):
            return True
    return False


def queue_routine_reply_draft(
    creds: dict[str, str],
    state_dir: Path,
    headers: dict[str, str],
    body: str,
    classification: dict[str, str],
    source_id: str,
) -> bool:
    return False


def queue_owner_question_draft(
    creds: dict[str, str],
    state_dir: Path,
    headers: dict[str, str],
    body: str,
    classification: dict[str, str],
    source_id: str,
) -> bool:
    if owner_question_draft_exists(state_dir, source_id):
        return False
    outbox = state_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    outbox.chmod(0o700)
    from_addr = "vanessa.sterling@kovaldistillery.com"
    owner_email, owner_name = owner_question_target(headers, classification)
    payload = {
        "source_ref": source_id,
        "intake_channel": "email:nationaloutreach",
        "requester": headers.get("from", ""),
        "owner_lane": classification.get("route", "outreach-coordinator"),
        "responsible_worker_or_persona": from_addr,
        "status": "draft",
        "due_or_trigger": "",
        "scheduled_action": "",
        "calendar_event": "",
        "source_links": headers.get("subject", ""),
        "approval_gates": "routine-if-clear",
        "verification_readback": f"owner_question_draft_queued_for_{owner_email}",
        "next_update": f"{owner_name} must answer one clarification question before any external reply or filing.",
        "requested_deliverable": f"{owner_name} answer",
        "human_owner_or_recipient": owner_name,
        "output_channel": "email",
        "proof_required": "sent Message-ID plus original source email attached or quoted",
        "owner_question_required": "required",
        "owner_question": "true",
        "from": from_addr,
        "from_name": "Vanessa Sterling",
        "to": [owner_email],
        "subject": owner_question_subject(headers.get("subject", "")),
        "body": owner_question_body(headers, body, owner_name),
        "in_reply_to": headers.get("message_id", ""),
        "references": headers.get("references", "") or headers.get("message_id", ""),
        "task_packet": shared_task_flow.build_packet(
            source_ref=source_id,
            intake_channel="email:nationaloutreach",
            requester=headers.get("from", ""),
            owner_lane=classification.get("route", "outreach-coordinator"),
            responsible_worker_or_persona=from_addr,
            status="classified",
            source_links=headers.get("subject", ""),
            approval_gates="routine-if-clear",
            verification_readback=f"owner_question_draft_queued_for_{owner_email}",
            next_update=f"{owner_name} must answer one clarification question before any external reply or filing.",
            requested_deliverable=f"{owner_name} answer",
            human_owner_or_recipient=owner_name,
            output_channel="email",
            proof_required="sent Message-ID plus original source email attached or quoted",
            owner_question_required="required",
            owner_question="true",
        ),
    }
    draft_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", f"owner-question-{source_id}").strip("-") + ".approved.json"
    draft_path = outbox / draft_name
    write_json(draft_path, payload)
    append_jsonl(
        state_dir / "owner-question-log.jsonl",
        {
            "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "worker": "nationaloutreach",
            "source_message_id": source_id,
            "subject": headers.get("subject", ""),
            "draft": str(draft_path),
            "recipient": owner_email,
        },
    )
    if shared_task_flow:
        packet = payload["task_packet"]
        shared_task_flow.append_event(
            state_dir / "task-flow-events.jsonl",
            packet,
            "email_owner_question_queued",
            recipient=owner_email,
            draft=str(draft_path),
        )
    return True


def load_seen(path: Path) -> set[str]:
    data = read_json(path, {"seen_message_ids": []})
    return {str(item) for item in data.get("seen_message_ids", []) if item}


def save_seen(path: Path, seen: set[str]) -> None:
    write_json(
        path,
        {
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "seen_message_ids": sorted(seen)[-20000:],
        },
    )


def is_inbox_mailbox(mailbox: str) -> bool:
    normalized = str(mailbox or "").strip().strip('"').lower()
    return normalized == "inbox"


def load_active_inbox(path: Path) -> dict[str, dict]:
    data = read_json(path, {"messages": {}})
    messages = data.get("messages") if isinstance(data, dict) else {}
    if not isinstance(messages, dict):
        return {}
    return {str(key): value for key, value in messages.items() if isinstance(value, dict)}


def load_seen_db_first(state_dir: Path, mailbox_lane: str, fallback_path: Path) -> set[str]:
    if mailbox_helpers is not None:
        seen = mailbox_helpers.collect_seen_source_ids_from_db(mailbox_lane, 20000)
        if seen:
            return seen
    return load_seen(fallback_path)


def load_active_inbox_db_first(state_dir: Path, mailbox_lane: str, fallback_path: Path) -> dict[str, dict]:
    if mailbox_helpers is not None:
        rows = mailbox_helpers.collect_active_inbox_from_db(mailbox_lane, 6000)
        if rows:
            records: dict[str, dict] = {}
            for row in rows:
                source_id = normalize_message_id(
                    row.get("source_message_id") or row.get("source_ref") or row.get("message_id")
                )
                if not source_id:
                    continue
                records[source_id] = {
                    "status": str(row.get("status") or "active_inbox"),
                    "first_seen_at": str(row.get("first_seen_at") or ""),
                    "last_seen_at": str(row.get("last_seen_at") or ""),
                    "message_id": str(row.get("message_id") or row.get("source_message_id") or ""),
                    "date": str(row.get("date") or ""),
                    "from": str(row.get("from") or ""),
                    "to": str(row.get("to") or ""),
                    "cc": str(row.get("cc") or ""),
                    "subject": str(row.get("subject") or ""),
                    "route": str(row.get("route") or ""),
                    "send_allowed": str(row.get("send_allowed") or ""),
                    "suggestion": str(row.get("suggestion") or ""),
                    "body_path": str(row.get("body_path") or ""),
                    "body_chars": row.get("body_chars"),
                    "seen_before": bool(row.get("seen_before")),
                }
            if records:
                return records
    return load_active_inbox(fallback_path)


def save_active_inbox(path: Path, messages: dict[str, dict]) -> None:
    def sort_key(item: tuple[str, dict]) -> str:
        value = item[1]
        return str(value.get("last_seen_at") or value.get("resolved_at") or "")

    trimmed = dict(sorted(messages.items(), key=sort_key)[-5000:])
    write_json(
        path,
        {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": trimmed,
        },
    )


def archive_inbox_messages(
    creds: dict[str, str],
    state_dir: Path,
    active_records: dict[str, dict],
    archive_redundant_overdue_reports: bool,
    archive_self_sent_inbox_copies: bool,
    archive_replied_inbox: bool,
) -> dict:
    live_active_records = {
        source_id: record
        for source_id, record in active_records.items()
        if str(record.get("status") or "active_inbox") == "active_inbox"
    }
    if not live_active_records:
        return {"archived": 0, "skipped": 0, "subjects": [], "reasons": {}}

    allowed_aliases = sorted(addr.lower() for addr in ALLOWED_FROM)
    sent_entries = (
        mailbox_helpers.collect_sent_entries_from_state_dirs(shared_sent_log_state_dirs(state_dir))
        if mailbox_helpers is not None
        else []
    )
    targets: dict[str, dict[str, str]] = {}
    overdue_candidates: list[tuple[str, float, str]] = []
    replied_cache: dict[tuple[str, str], bool] = {}

    for source_id, record in live_active_records.items():
        subject = str(record.get("subject") or "")
        if archive_redundant_overdue_reports and OVERDUE_REPORT_SUBJECT_RE.match(subject):
            ts = parse_header_timestamp(str(record.get("date") or "")) or 0
            overdue_candidates.append((source_id, ts, subject))

    if archive_redundant_overdue_reports and len(overdue_candidates) > 1:
        overdue_candidates.sort(key=lambda item: item[1], reverse=True)
        for source_id, _, subject in overdue_candidates[1:]:
            targets[source_id] = {"reason": "redundant_overdue_report", "subject": subject}

    for source_id, record in live_active_records.items():
        if source_id in targets:
            continue
        subject = str(record.get("subject") or "")
        sender = sender_email(record.get("from") or "")
        if archive_self_sent_inbox_copies and sender and sender in allowed_aliases:
            targets[source_id] = {"reason": "self_sent_inbox_copy", "subject": subject}
            continue
        if archive_replied_inbox:
            if is_direct_owner_instruction_record(record):
                continue
            cache_key = (normalize_subject(subject), str(record.get("date") or ""))
            matched = replied_cache.get(cache_key)
            if matched is None:
                if sent_entries:
                    parsed_ts = parse_header_timestamp(str(record.get("date") or "")) or time.time()
                    received_at = datetime.fromtimestamp(parsed_ts, tz=timezone.utc)
                    reply_probe = {
                        "received_at": received_at,
                        "subject_key": normalize_subject(subject),
                        "owner_email": sender,
                        "source_message_id": source_id,
                        "thread_refs": [],
                    }
                    matched = mailbox_helpers.owner_reply_has_later_send(reply_probe, sent_entries)
                else:
                    matched = mailbox_has_matching_reply_from_aliases(
                        creds,
                        allowed_aliases,
                        subject,
                        str(record.get("date") or ""),
                    )
                replied_cache[cache_key] = matched
            if matched:
                targets[source_id] = {"reason": "later_reply_found", "subject": subject}

    archived = 0
    skipped = 0
    subjects: list[dict[str, str]] = []
    reason_counts: dict[str, int] = {}
    archived_redundant_overdue_source_ids: list[str] = []
    if targets:
        conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]), timeout=25)
        try:
            conn.login(creds["user"], creds["password"])
            conn.select("INBOX", readonly=False)
            typ, data = conn.uid("SEARCH", None, "ALL")
            if typ != "OK":
                raise RuntimeError(f"IMAP uid search failed for archive pass: {typ}")
            for uid in data[0].split() if data and data[0] else []:
                typ, header_data = conn.uid("FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID SUBJECT)])")
                if typ != "OK":
                    continue
                raw = b"".join(part[1] for part in header_data if isinstance(part, tuple))
                if not raw:
                    continue
                msg = message_from_bytes(raw)
                source_id = normalize_message_id(decode_value(msg.get("Message-ID", "")))
                target = targets.get(source_id)
                if not target:
                    continue
                move_status = conn.uid("MOVE", uid, '"[Gmail]/All Mail"')
                if move_status[0] != "OK":
                    skipped += 1
                    continue
                archived += 1
                reason = target["reason"]
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
                if reason == "redundant_overdue_report":
                    archived_redundant_overdue_source_ids.append(source_id)
                subjects.append(
                    {
                        "source_message_id": source_id,
                        "subject": target["subject"],
                        "reason": reason,
                    }
                )
                append_jsonl(
                    state_dir / "archive-log.jsonl",
                    {
                        "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "worker": "nationaloutreach",
                        "source_message_id": source_id,
                        "subject": target["subject"],
                        "reason": reason,
                        "mailbox_mutation": True,
                        "action": "archive_move_to_all_mail",
                    },
                )
                record_email_trace(
                    state_dir,
                    event="email_archived",
                    message=build_email_trace_message(
                        mailbox_lane="nationaloutreach",
                        worker="nationaloutreach",
                        event="email_archived",
                        source_message_id=source_id,
                        source_ref=source_id,
                        subject=target["subject"],
                        direction="inbound",
                        status="archived",
                        archived_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        event_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        metadata={
                            "reason": reason,
                            "mailbox_mutation": True,
                            "action": "archive_move_to_all_mail",
                        },
                    ),
                    details={"reason": reason, "mailbox_mutation": True},
                )
        finally:
            with contextlib.suppress(Exception):
                conn.logout()

    if archive_redundant_overdue_reports and overdue_candidates:
        overdue_candidates.sort(key=lambda item: item[1], reverse=True)
        retained_source_id, _, retained_subject = overdue_candidates[0]
        remaining_overdue_count = max(0, len(overdue_candidates) - len(archived_redundant_overdue_source_ids))
        readback_row = {
            "worker": "nationaloutreach",
            "action": "overdue_summary_inbox_readback",
            "mailbox_mutation": bool(archived_redundant_overdue_source_ids),
            "overdue_summary_inbox_count_before_archive": len(overdue_candidates),
            "overdue_summary_inbox_count_after_archive": remaining_overdue_count,
            "newest_retained_source_message_id": retained_source_id,
            "newest_retained_subject": retained_subject,
            "archived_redundant_overdue_count": len(archived_redundant_overdue_source_ids),
            "archived_redundant_overdue_source_ids": archived_redundant_overdue_source_ids,
        }
        readback_state_path = state_dir / "overdue-summary-readback.json"
        previous_readback = read_json(readback_state_path, {})
        if previous_readback != readback_row:
            append_jsonl(
                state_dir / "archive-log.jsonl",
                {
                    "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    **readback_row,
                },
            )
            write_json(readback_state_path, readback_row)

    return {
        "archived": archived,
        "skipped": skipped,
        "subjects": subjects[:20],
        "reasons": reason_counts,
    }


def should_log_active_inbox(record: dict, now_ts: float) -> bool:
    try:
        last_logged = float(record.get("last_active_log_epoch") or 0)
    except (TypeError, ValueError):
        last_logged = 0
    return last_logged <= 0 or now_ts - last_logged >= ACTIVE_INBOX_LOG_INTERVAL_SECONDS


def store_body(body_dir: Path, source_id: str, body: str) -> Path:
    safe = re.sub(r"[^a-z0-9._-]+", "-", source_id.lower()).strip("-")[:120] or "message"
    path = body_dir / f"{safe}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(body, encoding="utf-8", errors="replace")
    path.chmod(0o600)
    return path


def workspace_mailbox_state_dir(workspace_root: Path, mailbox_lane: str) -> Path:
    return workspace_root.expanduser().resolve().parent / ".private" / "mailboxes" / mailbox_lane / "state"


def workspace_relative_state_path(path: Path, workspace_root: Path) -> str:
    try:
        return str(path.relative_to(workspace_root.expanduser().resolve().parent))
    except ValueError:
        return str(path)


def workspace_active_inbox_records(messages: dict[str, dict], workspace_root: Path) -> dict[str, dict]:
    projected: dict[str, dict] = {}
    for source_id, record in messages.items():
        row = dict(record or {})
        body_path = str(row.get("body_path") or "").strip()
        if body_path:
            row["body_path"] = workspace_relative_state_path(Path(body_path), workspace_root)
        projected[source_id] = row
    return projected


def fetch_messages(creds: dict[str, str], state_dir: Path, workspace_root: Path, limit: int, mailbox: str, search: str, review_old: bool) -> dict:
    seen_path = state_dir / "seen-full-body.json"
    active_inbox_path = state_dir / "active-inbox.json"
    review_log = state_dir / "mail-review.jsonl"
    workspace_review = workspace_root / "mail-review.jsonl"
    workspace_state_dir = workspace_mailbox_state_dir(workspace_root, "nationaloutreach")
    workspace_seen_path = workspace_state_dir / "seen-full-body.json"
    workspace_active_inbox_path = workspace_state_dir / "active-inbox.json"
    workspace_state_review = workspace_state_dir / "mail-review.jsonl"
    body_dir = state_dir / "bodies"
    workspace_body_dir = workspace_state_dir / "bodies"
    seen = load_seen_db_first(state_dir, "nationaloutreach", seen_path)
    inbox_selected = is_inbox_mailbox(mailbox)
    active_records = load_active_inbox_db_first(state_dir, "nationaloutreach", active_inbox_path) if inbox_selected else {}
    reviewed = 0
    new_items = 0
    mailbox_total = 0
    seen_inbox_active_count = 0
    active_inbox_logged = 0
    skipped_seen_non_inbox = 0
    route_counts: dict[str, int] = {}
    active_route_counts: dict[str, int] = {}
    current_inbox_source_ids: set[str] = set()
    active_inbox_subjects: list[dict[str, str]] = []
    now_ts = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]), timeout=25)
    try:
        conn.login(creds["user"], creds["password"])
        conn.select(mailbox, readonly=True)
        status, data = conn.search(None, search)
        if status != "OK":
            raise RuntimeError(f"IMAP search failed: {status}")
        all_ids = data[0].split() if data and data[0] else []
        mailbox_total = len(all_ids)
        ids = all_ids[-limit:] if limit > 0 else []
        for imap_id in ids:
            status, header_data = conn.fetch(imap_id, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID DATE FROM TO CC SUBJECT IN-REPLY-TO REFERENCES)])")
            if status != "OK":
                continue
            header_raw = b"".join(part[1] for part in header_data if isinstance(part, tuple))
            if not header_raw:
                continue
            header_msg = message_from_bytes(header_raw)
            source_id = normalize_message_id(decode_value(header_msg.get("Message-ID", ""))) or f"imap-{imap_id.decode('ascii', errors='replace')}"
            already_seen = source_id in seen
            if inbox_selected:
                current_inbox_source_ids.add(source_id)
            if already_seen and not review_old and not inbox_selected:
                skipped_seen_non_inbox += 1
                continue
            if already_seen and not review_old and inbox_selected:
                seen_inbox_active_count += 1
            status, msg_data = conn.fetch(imap_id, "(BODY.PEEK[])")
            if status != "OK":
                continue
            raw = b"".join(part[1] for part in msg_data if isinstance(part, tuple))
            if not raw:
                continue
            msg = message_from_bytes(raw)
            body = message_text(msg)
            headers = {
                "imap_id": imap_id.decode("ascii", errors="replace"),
                "message_id": decode_value(header_msg.get("Message-ID", "")),
                "date": decode_value(header_msg.get("Date", "")),
                "from": decode_value(header_msg.get("From", "")),
                "to": decode_value(header_msg.get("To", "")),
                "cc": decode_value(header_msg.get("Cc", "")),
                "subject": decode_value(header_msg.get("Subject", "")),
                "in_reply_to": decode_value(header_msg.get("In-Reply-To", "")),
                "references": decode_value(header_msg.get("References", "")),
            }
            classification = classify_message(headers, body)
            no_action_newsletter = is_newsletter_no_action_candidate(headers, body, classification)
            no_action_auth_code = is_no_action_auth_code_candidate(headers, body, classification)
            if no_action_newsletter:
                classification = {
                    "route": "marketing-manager",
                    "suggestion": "Newsletter/promotional residue detected from mailbox body plus sender domain. No owner escalation is needed; file as no-action after source-backed logging.",
                    "send_allowed": "no",
                }
            if no_action_auth_code:
                classification = {
                    "route": "portal-auth",
                    "suggestion": "Portal auth-code intake. Use immediately for the active Codex Portal login flow or silent-login path; otherwise file as stale auth residue. Do not escalate this to Robert as a blocker.",
                    "send_allowed": "no-owner-escalation",
                }
            owner_question_needed = bool(
                OWNER_QUESTION_PATTERNS.search(
                    f"{headers.get('subject', '')}\n{headers.get('from', '')}\n{headers.get('to', '')}\n{headers.get('cc', '')}\n{routing_body(body)}"
                )
            ) and sender_email(headers.get("from") or "") != ROBERT_EMAIL
            if owner_question_needed:
                queue_owner_question_draft(creds, state_dir, headers, body, classification, source_id)
            elif classification.get("send_allowed") == "routine-if-clear":
                queue_routine_reply_draft(creds, state_dir, headers, body, classification, source_id)
            body_path = store_body(body_dir, source_id, body)
            workspace_body_path = store_body(workspace_body_dir, source_id, body)
            body_read = bool(body)
            body_chars = len(body or "")
            if inbox_selected and not (no_action_newsletter or no_action_auth_code):
                active_route_counts[classification["route"]] = active_route_counts.get(classification["route"], 0) + 1
                if len(active_inbox_subjects) < 20:
                    active_inbox_subjects.append(
                        {
                            "source_message_id": source_id,
                            "from": headers.get("from", ""),
                            "subject": headers.get("subject", ""),
                            "route": classification["route"],
                            "seen_before": str(already_seen).lower(),
                        }
                    )
            task_packet = {}
            if shared_task_flow:
                task_flow_status = "no_action_closed" if (no_action_newsletter or no_action_auth_code) else task_flow_status_for_classification(classification)
                human_owner = headers.get("from", "") if is_internal_koval_sender(headers.get("from", "")) else ""
                task_packet = shared_task_flow.build_packet(
                    source_ref=source_id,
                    intake_channel="email:nationaloutreach",
                    requester=headers.get("from", ""),
                    owner_lane=classification["route"],
                    responsible_worker_or_persona=task_flow_persona_for_route(classification["route"]),
                    status=task_flow_status,
                    approval_gates=classification["send_allowed"],
                    source_links=headers.get("subject", ""),
                    human_owner_or_recipient=human_owner,
                    next_update=(
                        "Source-backed no-action closeout: Portal auth code is login-flow residue; use it only during the active Codex Portal login flow or silent-login path, otherwise file without owner escalation."
                        if no_action_auth_code
                        else "Source-backed no-action closeout: newsletter/promotional residue already body-read from the mailbox; no owner escalation or follow-up needed."
                        if no_action_newsletter
                        else task_flow_next_update(classification)
                    ),
                    verification_readback=(
                        f"body_read=true; body_chars={body_chars}; portal_auth_code_residue=true; sender={sender_email(headers.get('from', ''))}"
                        if no_action_auth_code
                        else f"body_read=true; body_chars={body_chars}; newsletter_residue_detected=true; sender={sender_email(headers.get('from', ''))}"
                        if no_action_newsletter
                        else ""
                    ),
                )
            row = {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "worker": "nationaloutreach",
                "email": creds["user"],
                "source_message_id": source_id,
                "task_packet": task_packet,
                "body_read": body_read,
                "body_path": str(body_path) if body_path is not None else "",
                "body_chars": body_chars,
                "mailbox_mutation": False,
                "active_inbox": inbox_selected,
                "seen_before": already_seen,
                "review_reason": "review_old" if review_old and already_seen else ("active_inbox_still_open" if inbox_selected and already_seen else "new_message"),
                **headers,
                **classification,
            }
            workspace_row = dict(row)
            workspace_row["body_path"] = workspace_relative_state_path(workspace_body_path, workspace_root)
            active_record = active_records.get(source_id, {}) if inbox_selected else {}
            already_closed_no_action = str(active_record.get("status") or "").strip().lower() == "no_action_closed"
            should_append_review = (
                not already_seen
                or review_old
                or not inbox_selected
                or (not already_closed_no_action and should_log_active_inbox(active_record, now_ts))
            )
            if should_append_review:
                append_jsonl(review_log, row)
                append_jsonl(workspace_review, {k: v for k, v in row.items() if k != "body_path"})
                append_jsonl(workspace_state_review, workspace_row)
                record_email_trace(
                    state_dir,
                    event="email_reviewed",
                    message=build_email_trace_message(
                        mailbox_lane="nationaloutreach",
                        worker="nationaloutreach",
                        event="email_reviewed",
                        source_message_id=source_id,
                        source_ref=source_id,
                        subject=headers.get("subject", ""),
                        from_address=sender_email(headers.get("from", "")),
                        to_addresses=headers.get("to", ""),
                        cc_addresses=headers.get("cc", ""),
                        header_date=headers.get("date", ""),
                        email_account=creds["user"],
                        direction="inbound",
                        body_path=str(body_path) if body_path is not None else "",
                        body_chars=body_chars,
                        body_summary=body,
                        status=str(task_packet.get("status") or "reviewed"),
                        first_seen_at=active_record.get("first_seen_at") or now_iso,
                        event_at=row["logged_at"],
                        task_packet=task_packet,
                        metadata={
                            "route": classification["route"],
                            "send_allowed": classification["send_allowed"],
                            "suggestion": classification["suggestion"],
                            "active_inbox": inbox_selected,
                            "seen_before": already_seen,
                            "review_reason": row["review_reason"],
                        },
                    ),
                    task_packet=task_packet,
                    details={"route": classification["route"], "review_reason": row["review_reason"]},
                )
                reviewed += 1
                route_counts[classification["route"]] = route_counts.get(classification["route"], 0) + 1
                if inbox_selected and already_seen:
                    active_inbox_logged += 1
            if shared_task_flow and should_append_review:
                shared_task_flow.append_event(
                    state_dir / "task-flow-events.jsonl",
                    task_packet,
                    task_flow_event_for_status(task_packet.get("status", "classified")),
                )
            if inbox_selected:
                active_records[source_id] = {
                    **active_record,
                    "status": "no_action_closed" if (no_action_newsletter or no_action_auth_code) else "active_inbox",
                    "first_seen_at": active_record.get("first_seen_at") or now_iso,
                    "last_seen_at": now_iso,
                    "last_active_log_epoch": now_ts if should_append_review else active_record.get("last_active_log_epoch"),
                    "resolved_at": now_iso if (no_action_newsletter or no_action_auth_code) else active_record.get("resolved_at", ""),
                    "message_id": headers.get("message_id", ""),
                    "date": headers.get("date", ""),
                    "from": headers.get("from", ""),
                    "to": headers.get("to", ""),
                    "cc": headers.get("cc", ""),
                    "subject": headers.get("subject", ""),
                    "route": classification["route"],
                    "send_allowed": classification["send_allowed"],
                    "suggestion": classification["suggestion"],
                    "body_path": str(body_path),
                    "body_chars": len(body),
                    "seen_before": already_seen,
                }
            seen.add(source_id)
            if not already_seen:
                new_items += 1
    finally:
        try:
            conn.logout()
        except Exception:
            pass
    if inbox_selected:
        for source_id, record in list(active_records.items()):
            if record.get("status") == "active_inbox" and source_id not in current_inbox_source_ids:
                active_records[source_id] = {
                    **record,
                    "status": "resolved_not_in_inbox",
                    "resolved_at": now_iso,
                }
                record_email_trace(
                    state_dir,
                    event="email_resolved_not_in_inbox",
                    message=build_email_trace_message(
                        mailbox_lane="nationaloutreach",
                        worker="nationaloutreach",
                        event="email_resolved_not_in_inbox",
                        source_message_id=source_id,
                        source_ref=source_id,
                        subject=record.get("subject", ""),
                        from_address=sender_email(record.get("from", "")),
                        to_addresses=record.get("to", ""),
                        cc_addresses=record.get("cc", ""),
                        header_date=record.get("date", ""),
                        email_account=creds["user"],
                        direction="inbound",
                        body_path=record.get("body_path", ""),
                        body_chars=record.get("body_chars", ""),
                        status="resolved_not_in_inbox",
                        first_seen_at=record.get("first_seen_at", ""),
                        event_at=now_iso,
                        metadata={"route": record.get("route", ""), "send_allowed": record.get("send_allowed", "")},
                    ),
                    details={"previous_status": "active_inbox", "route": record.get("route", "")},
                )
        save_active_inbox(active_inbox_path, active_records)
        save_active_inbox(workspace_active_inbox_path, workspace_active_inbox_records(active_records, workspace_root))
    save_seen(seen_path, seen)
    save_seen(workspace_seen_path, seen)
    return {
        "reviewed": reviewed,
        "new_items": new_items,
        "route_counts": route_counts,
        "mailbox_total": mailbox_total,
        "active_inbox_count": len(current_inbox_source_ids) if inbox_selected else 0,
        "seen_inbox_active_count": seen_inbox_active_count,
        "active_inbox_logged": active_inbox_logged,
        "active_route_counts": active_route_counts,
        "active_inbox_subjects": active_inbox_subjects,
        "skipped_seen_non_inbox": skipped_seen_non_inbox,
    }


def normalize_addresses(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def body_to_html_with_signature_links(body: str) -> str:
    lines = body.splitlines()
    rendered: list[str] = []
    in_paragraph: list[str] = []

    def flush_paragraph() -> None:
        if not in_paragraph:
            return
        rendered.append("<p>" + "<br>".join(html.escape(line) for line in in_paragraph) + "</p>")
        in_paragraph.clear()

    for line in lines:
        if not line.strip():
            flush_paragraph()
            continue
        if SOCIAL_SIGNATURE_RE.match(line):
            flush_paragraph()
            rendered.append("<p>" + social_links_html() + "</p>")
            continue
        in_paragraph.append(line)
    flush_paragraph()
    return "<!doctype html><html><body>" + "".join(rendered) + "</body></html>"


def social_links_html() -> str:
    return " | ".join(
        f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'
        for label, url in SOCIAL_LINKS.items()
    )


def ensure_signature_links_in_html(html_body: str) -> str:
    return SOCIAL_SIGNATURE_TEXT_RE.sub(social_links_html(), html_body)


def send_one(creds: dict[str, str], draft_path: Path, sent_dir: Path, failed_dir: Path, default_from: str) -> dict:
    payload = read_json(draft_path, {})
    from_addr = str(payload.get("from") or default_from).strip().lower()
    if from_addr in FORBIDDEN_FROM:
        raise ValueError(f"From address is explicitly forbidden for National Outreach sends: {from_addr}")
    if from_addr not in ALLOWED_FROM:
        raise ValueError(f"From address is not allowed by National Outreach registry: {from_addr}")
    auth_user = str(creds.get("user") or "").strip().lower()
    allow_visible_sender = os.environ.get("NATIONALOUTREACH_ALLOW_VISIBLE_SENDER_HEADER") == "1"
    if from_addr != auth_user and from_addr not in VERIFIED_SEND_AS_ALIASES and not allow_visible_sender:
        raise ValueError(
            "Direct persona sends require matching mailbox authentication; "
            "the shared National Outreach mailbox route can expose a visible Sender header."
        )
    to_addrs = normalize_addresses(payload.get("to"))
    cc_addrs = normalize_addresses(payload.get("cc"))
    bcc_addrs = normalize_addresses(payload.get("bcc"))
    subject = clean_subject(payload.get("subject") or "")
    body = str(payload.get("body") or "").strip()
    html_body = str(payload.get("html_body") or "").strip()
    in_reply_to = clean_subject(payload.get("in_reply_to") or "")
    references = clean_subject(payload.get("references") or "")
    if not to_addrs or not subject or not body:
        raise ValueError("Approved send draft requires to, subject, and body.")
    msg = EmailMessage()
    from_name = str(payload.get("from_name") or FROM_DISPLAY_NAMES.get(from_addr, "")).strip()
    msg["From"] = formataddr((from_name, from_addr)) if from_name else from_addr
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=from_addr.split("@", 1)[1])
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references
    reply_chain_required = payload.get("reply_chain_required")
    if isinstance(reply_chain_required, str):
        reply_chain_required = reply_chain_required.strip().lower() in {"1", "true", "yes", "on"}
    else:
        reply_chain_required = bool(reply_chain_required)
    if reply_chain_required and "Original message:" not in body:
        original_headers = {
            "from": payload.get("original_from", ""),
            "to": payload.get("original_to", ""),
            "cc": payload.get("original_cc", ""),
            "date": payload.get("original_date", ""),
            "subject": payload.get("original_subject", ""),
        }
        original_body = str(payload.get("original_body") or "").strip()
        if original_body or any(str(v or "").strip() for v in original_headers.values()):
            body = f"{body}\n\n{quoted_original_message_block(original_headers, original_body)}".strip()
    msg.set_content(body)
    if not html_body and SOCIAL_SIGNATURE_RE.search(body):
        html_body = body_to_html_with_signature_links(body)
    if html_body:
        html_body = ensure_signature_links_in_html(html_body)
        msg.add_alternative(html_body, subtype="html")
    attachment_specs = payload.get("attachments") or payload.get("attachment_paths") or []
    if isinstance(attachment_specs, (str, Path)):
        attachment_specs = [attachment_specs]
    if not isinstance(attachment_specs, list):
        raise ValueError("attachments must be a list of file paths or attachment objects.")
    attachment_names: list[str] = []
    for spec in attachment_specs:
        if isinstance(spec, dict):
            attachment_path = Path(str(spec.get("path") or "")).expanduser()
            filename = str(spec.get("filename") or attachment_path.name).strip()
            content_type = str(spec.get("content_type") or "").strip()
        else:
            attachment_path = Path(str(spec)).expanduser()
            filename = attachment_path.name
            content_type = ""
        if not attachment_path.is_file():
            raise ValueError(f"Attachment file is missing: {attachment_path}")
        if not filename:
            raise ValueError(f"Attachment filename is empty for: {attachment_path}")
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        maintype, _, subtype = content_type.partition("/")
        if not maintype or not subtype:
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(
            attachment_path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=filename,
        )
        attachment_names.append(filename)
    recipients = to_addrs + cc_addrs + bcc_addrs
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(creds["smtp_server"], int(creds["smtp_port"]), timeout=25, context=context) as conn:
        conn.login(creds["user"], creds["password"])
        conn.send_message(msg, from_addr=from_addr, to_addrs=recipients)
    sent_folder = append_message_to_sent_folder(creds, msg)
    sent_dir.mkdir(parents=True, exist_ok=True)
    sent_dir.chmod(0o700)
    target = sent_dir / draft_path.name.replace(".approved.json", f".sent-{int(time.time())}.json")
    shutil.move(str(draft_path), str(target))
    target.chmod(0o600)
    task_packet = payload.get("task_packet") if isinstance(payload.get("task_packet"), dict) else {}
    owner_question_flag = payload.get("owner_question")
    generic_ack_flag = payload.get("generic_acknowledgement")
    if isinstance(owner_question_flag, str):
        owner_question_flag = owner_question_flag.strip().lower() in {"1", "true", "yes", "on"}
    else:
        owner_question_flag = bool(owner_question_flag)
    if isinstance(generic_ack_flag, str):
        generic_ack_flag = generic_ack_flag.strip().lower() in {"1", "true", "yes", "on"}
    else:
        generic_ack_flag = bool(generic_ack_flag)
    if not task_packet and shared_task_flow:
        task_packet = shared_task_flow.build_packet(
            source_ref=str(payload.get("source_ref") or draft_path.name),
            intake_channel="approved-send:nationaloutreach",
            requester=str(payload.get("requester") or ""),
            owner_lane=str(payload.get("owner_lane") or from_addr),
            responsible_worker_or_persona=from_addr,
            status="reported",
            completion_or_blocker_email=msg["Message-ID"],
            next_update="sent",
        )
    elif task_packet:
        if generic_ack_flag or is_generic_acknowledgement_body(str(payload.get("body") or "")):
            task_packet = {
                **task_packet,
                "status": "waiting",
                "clarification_email": "",
                "completion_or_blocker_email": "",
                "verification_readback": "Generic acknowledgement sent only; substantive follow-up or deliverable proof is still required before filing.",
                "next_update": "Send the actual requested follow-up or record one exact blocker before filing.",
            }
        elif owner_question_flag or str(task_packet.get("status") or "") == "clarification_sent":
            task_packet = {
                **task_packet,
                "status": "clarification_sent",
                "clarification_email": msg["Message-ID"],
                "completion_or_blocker_email": "",
                "next_update": "Robert answered the clarification question.",
            }
        else:
            task_packet = {**task_packet, "status": "reported", "completion_or_blocker_email": msg["Message-ID"]}
    sent_payload = {
        **payload,
        "message_id": msg["Message-ID"],
        "sent_metadata": {
            "message_id": msg["Message-ID"],
            "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "from_addr": from_addr,
            "to_count": len(to_addrs),
            "cc_count": len(cc_addrs),
            "bcc_count": len(bcc_addrs),
            "attachment_count": len(attachment_names),
            "attachment_names": attachment_names,
            "sent_folder_appended": True,
            "sent_folder": sent_folder,
        },
        "task_packet": task_packet,
        "sent_folder_appended": True,
        "sent_folder": sent_folder,
    }
    target.write_text(json.dumps(sent_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    target.chmod(0o600)
    return {
        "draft": str(target),
        "draft_basename": target.name,
        "action_id": draft_path.name.replace(".approved.json", ""),
        "source_ref": str(payload.get("source_ref") or ""),
        "from": from_addr,
        "to_count": len(to_addrs),
        "cc_count": len(cc_addrs),
        "bcc_count": len(bcc_addrs),
        "attachment_count": len(attachment_names),
        "attachment_names": attachment_names,
        "subject": subject,
        "message_id": msg["Message-ID"],
        "sent_folder_appended": True,
        "sent_folder": sent_folder,
        "task_packet": task_packet,
    }


def sent_action_already_logged(state_dir: Path, action_id: str) -> bool:
    if not action_id:
        return False
    sent_dir = state_dir / "sent"
    if sent_dir.exists() and any(sent_dir.glob(f"{action_id}.sent-*.json")):
        return True
    sent_log = state_dir / "sent-log.jsonl"
    if not sent_log.exists():
        return False
    needle = f'"draft_basename":"{action_id}.sent-'
    prefix = f'/{action_id}.sent-'
    try:
        with sent_log.open("r", encoding="utf-8") as handle:
            for line in handle:
                if needle in line or prefix in line:
                    return True
    except OSError:
        return False
    return False


def mark_scheduled_action_sent(
    state_dir: Path,
    mailbox_lane: str,
    action_id: str,
    message_id: str,
    sent_draft: str,
) -> bool:
    if not action_id:
        return False
    schedule_path = state_dir / "scheduled-actions.jsonl"
    rows = scheduled_actions_db_rows(mailbox_lane)
    if not rows and schedule_path.exists():
        rows = read_jsonl_tail(schedule_path, 20000)
    if not rows:
        return False
    changed = False
    sent_at = datetime.now(timezone.utc).isoformat()
    updated_rows = []
    for row in rows:
        if str(row.get("id") or "") == action_id:
            row = {
                **row,
                "status": "completed",
                "sent_at": sent_at,
                "sent_message_id": message_id,
                "sent_draft": sent_draft,
                "resolved_at": sent_at,
            }
            changed = True
        updated_rows.append(row)
    if not changed:
        return False
    write_jsonl_rows_atomic(schedule_path, updated_rows)
    scheduled_actions_db_upsert(mailbox_lane, updated_rows)
    append_jsonl(
        state_dir / "scheduled-actions-log.jsonl",
        {
            "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "action_id": action_id,
            "status": "completed",
            "draft": sent_draft,
            "message_id": message_id,
        },
    )
    return True


def send_approved(creds: dict[str, str], state_dir: Path, default_from: str) -> dict:
    lock_dir = state_dir / "send-approved.lock"
    try:
        lock_dir.mkdir()
        lock_acquired = True
    except FileExistsError:
        return {"sent": 0, "failed": 0, "skipped_locked": True}
    outbox = state_dir / "outbox"
    sent_dir = state_dir / "sent"
    failed_dir = state_dir / "failed"
    try:
        outbox.mkdir(parents=True, exist_ok=True)
        outbox.chmod(0o700)
        sent = []
        failures = []
        for draft_path in sorted(outbox.glob("*.approved.json")):
            if not draft_path.exists():
                continue
            action_id = draft_path.name.replace(".approved.json", "")
            if sent_action_already_logged(state_dir, action_id):
                with contextlib.suppress(OSError):
                    draft_path.unlink()
                append_jsonl(
                    state_dir / "scheduled-actions-log.jsonl",
                    {
                        "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "action_id": action_id,
                        "status": "skipped_duplicate_send",
                        "draft": str(draft_path),
                    },
                )
                mark_scheduled_action_sent(state_dir, "nationaloutreach", action_id, "", "")
                continue
            try:
                result = send_one(creds, draft_path, sent_dir, failed_dir, default_from)
                sent.append(result)
            except Exception as exc:
                failed_dir.mkdir(parents=True, exist_ok=True)
                failed_dir.chmod(0o700)
                if draft_path.exists():
                    target = failed_dir / draft_path.name.replace(".approved.json", f".failed-{int(time.time())}.json")
                    shutil.move(str(draft_path), str(target))
                    target.chmod(0o600)
                    failure_draft = str(target)
                else:
                    failure_draft = str(draft_path)
                failures.append({"draft": failure_draft, "error_type": exc.__class__.__name__})
        for result in sent:
            append_jsonl(state_dir / "sent-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **result})
            mark_scheduled_action_sent(
                state_dir,
                "nationaloutreach",
                str(result.get("action_id") or ""),
                str(result.get("message_id") or ""),
                str(result.get("draft") or ""),
            )
            record_email_trace(
                state_dir,
                event="email_sent",
                message=build_email_trace_message(
                    mailbox_lane="nationaloutreach",
                    worker="nationaloutreach",
                    event="email_sent",
                    message_id=result.get("message_id", ""),
                    source_ref=result.get("source_ref", ""),
                    subject=result.get("subject", ""),
                    from_address=result.get("from", ""),
                    header_date=time.strftime("%a, %d %b %Y %H:%M:%S %z"),
                    direction="outbound",
                    status="reported",
                    event_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    task_packet=result.get("task_packet") if isinstance(result.get("task_packet"), dict) else {},
                    metadata={
                        "to_count": result.get("to_count", 0),
                        "cc_count": result.get("cc_count", 0),
                        "bcc_count": result.get("bcc_count", 0),
                        "draft": result.get("draft", ""),
                    },
                ),
                task_packet=result.get("task_packet") if isinstance(result.get("task_packet"), dict) else {},
                details={"draft": result.get("draft", ""), "message_id": result.get("message_id", "")},
            )
            if shared_task_flow and isinstance(result.get("task_packet"), dict):
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", result["task_packet"], "email_sent", message_id=result.get("message_id"))
        for failure in failures:
            append_jsonl(state_dir / "send-failures.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **failure})
            if shared_task_flow:
                packet = shared_task_flow.build_packet(
                    source_ref=str(failure.get("draft") or ""),
                    intake_channel="approved-send:nationaloutreach",
                    responsible_worker_or_persona="nationaloutreach",
                    status="blocked",
                    verification_readback="email_send_blocked",
                    next_update="review failed draft and resend only after blocker is fixed",
                )
                shared_task_flow.append_event(state_dir / "task-flow-events.jsonl", packet, "email_send_blocked", error_type=failure.get("error_type"))
        return {"sent": len(sent), "failed": len(failures), "skipped_locked": False}
    finally:
        if lock_acquired:
            with contextlib.suppress(OSError):
                lock_dir.rmdir()


def main() -> int:
    args = parse_args()
    state_dir = Path(args.state_dir).expanduser()
    workspace_root = Path(args.workspace_root).expanduser()
    state_dir.mkdir(parents=True, exist_ok=True)
    state_dir.chmod(0o700)
    creds = load_credentials(Path(args.creds_file).expanduser())
    review = fetch_messages(creds, state_dir, workspace_root, args.limit, args.mailbox, args.search, args.review_old)
    archive_result = (
        archive_inbox_messages(
            creds,
            state_dir,
            load_active_inbox_db_first(state_dir, "nationaloutreach", state_dir / "active-inbox.json") if is_inbox_mailbox(args.mailbox) else {},
            args.archive_redundant_overdue_reports,
            args.archive_self_sent_inbox_copies,
            args.archive_replied_inbox,
        )
        if is_inbox_mailbox(args.mailbox)
        else {"archived": 0, "skipped": 0, "subjects": [], "reasons": {}}
    )
    scheduled_result = process_scheduled_actions(creds, state_dir) if args.send_approved else {"due": 0, "queued": 0, "skipped_resolved": 0, "failed": 0, "skipped_locked": False}
    send_result = send_approved(creds, state_dir, args.from_address) if args.send_approved else {"sent": 0, "failed": 0, "skipped_locked": False}
    scheduled_lock_health = scheduled_actions_lock_health(state_dir, bool(scheduled_result.get("skipped_locked"))) if args.send_approved else {"skip_streak": 0, "lock_age_seconds": 0, "actionable": False}
    summary = {
        "ok": True,
        "worker": "nationaloutreach",
        "mailbox": args.mailbox,
        "body_read": True,
        "reviewed": review["reviewed"],
        "new_items": review["new_items"],
        "mailbox_total": review["mailbox_total"],
        "active_inbox_count": review["active_inbox_count"],
        "seen_inbox_active_count": review["seen_inbox_active_count"],
        "active_inbox_logged": review["active_inbox_logged"],
        "route_counts": review["route_counts"],
        "active_route_counts": review["active_route_counts"],
        "active_inbox_subjects": review["active_inbox_subjects"],
        "skipped_seen_non_inbox": review["skipped_seen_non_inbox"],
        "queued_sends_sent": send_result["sent"],
        "queued_sends_failed": send_result["failed"],
        "queued_sends_skipped_locked": bool(send_result.get("skipped_locked")),
        "scheduled_actions_due": scheduled_result["due"],
        "scheduled_actions_queued": scheduled_result["queued"],
        "scheduled_actions_skipped_resolved": scheduled_result["skipped_resolved"],
        "scheduled_actions_failed": scheduled_result["failed"],
        "scheduled_actions_skipped_locked": bool(scheduled_result.get("skipped_locked")),
        "scheduled_actions_stale_lock_recovered": bool(scheduled_result.get("stale_lock_recovered")),
        "scheduled_actions_lock_skip_streak": scheduled_lock_health["skip_streak"],
        "scheduled_actions_lock_age_seconds": scheduled_lock_health["lock_age_seconds"],
        "scheduled_actions_lock_actionable": scheduled_lock_health["actionable"],
        "archived_inbox_count": archive_result["archived"],
        "archived_inbox_skipped": archive_result["skipped"],
        "archived_inbox_reasons": archive_result["reasons"],
        "archived_inbox_subjects": archive_result["subjects"],
        "mailbox_mutation": bool(archive_result["archived"]),
    }
    append_jsonl(state_dir / "cycle-log.jsonl", {"logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **summary})
    print(json.dumps(summary, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
