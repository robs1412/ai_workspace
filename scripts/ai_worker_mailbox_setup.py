#!/usr/bin/env python3

from __future__ import annotations

import argparse
import imaplib
import json
import smtplib
import ssl
import time
from pathlib import Path


DEFAULT_LABELS = [
    "Handled - AI Workers",
    "Handled - National Outreach",
    "Handled - Marketing",
    "Handled - Internal Communicator",
    "Handled - Frank Route",
    "Handled - Avignon Route",
    "Waiting - AI Workers",
    "Blocked - AI Workers",
    "Needs Robert",
    "Needs Sonat",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify and prepare an AI-worker mailbox without reading message bodies.")
    parser.add_argument("--worker", default="nationaloutreach", help="Worker slug for state records.")
    parser.add_argument("--creds-file", required=True, help="Private credential file.")
    parser.add_argument("--state-dir", required=True, help="Machine-local private state directory.")
    parser.add_argument("--imap-server", default="", help="IMAP server override. Defaults to credential Mail server or imap.gmail.com.")
    parser.add_argument("--smtp-server", default="", help="SMTP server override. Defaults to credential SMTP server or smtp.gmail.com.")
    parser.add_argument("--ensure-labels", action="store_true", help="Create the standard AI-worker labels if missing.")
    return parser.parse_args()


def load_credentials(path: Path, imap_server: str = "", smtp_server: str = "") -> dict[str, str]:
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
        "imap_server": imap_server or values.get("mail server", "") or values.get("imap server", "") or "imap.gmail.com",
        "imap_port": values.get("imap ssl port", "993") or "993",
        "smtp_server": smtp_server or values.get("smtp server", "") or "smtp.gmail.com",
        "smtp_port": values.get("smtp ssl port", "465") or "465",
    }


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def decode_mailbox_name(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    if ' "/" ' in text:
        return text.rsplit(' "/" ', 1)[1].strip().strip('"')
    return text.rsplit(" ", 1)[-1].strip().strip('"')


def quote_mailbox(name: str) -> str:
    escaped = name.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def verify_imap(creds: dict[str, str], ensure_labels: bool) -> dict[str, list[str]]:
    created: list[str] = []
    present: list[str] = []
    conn = imaplib.IMAP4_SSL(creds["imap_server"], int(creds["imap_port"]), timeout=25)
    try:
        conn.login(creds["user"], creds["password"])
        status, data = conn.list()
        if status != "OK":
            raise RuntimeError(f"IMAP list failed: {status}")
        existing = {decode_mailbox_name(item) for item in data or [] if isinstance(item, bytes)}
        if ensure_labels:
            for label in DEFAULT_LABELS:
                if label in existing:
                    present.append(label)
                    continue
                create_status, _ = conn.create(quote_mailbox(label))
                if create_status == "OK":
                    created.append(label)
                else:
                    status, data = conn.list()
                    existing_after = {decode_mailbox_name(item) for item in data or [] if isinstance(item, bytes)}
                    if label in existing_after:
                        present.append(label)
                    else:
                        raise RuntimeError(f"Could not create label {label}: {create_status}")
    finally:
        try:
            conn.logout()
        except Exception:
            pass
    return {"labels_created": created, "labels_present": present}


def verify_smtp(creds: dict[str, str]) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(creds["smtp_server"], int(creds["smtp_port"]), timeout=25, context=context) as conn:
        conn.login(creds["user"], creds["password"])


def main() -> int:
    args = parse_args()
    state_dir = Path(args.state_dir).expanduser()
    creds = load_credentials(Path(args.creds_file).expanduser(), args.imap_server, args.smtp_server)
    started = time.time()
    result = verify_imap(creds, args.ensure_labels)
    verify_smtp(creds)
    row = {
        "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "worker": args.worker,
        "email": creds["user"],
        "event": "mailbox_setup_verified",
        "imap_server": creds["imap_server"],
        "smtp_server": creds["smtp_server"],
        "labels_created": result["labels_created"],
        "labels_present": result["labels_present"],
        "body_read": False,
        "mail_sent": False,
        "duration_seconds": round(time.time() - started, 3),
    }
    append_jsonl(state_dir / "setup-log.jsonl", row)
    print(json.dumps({key: row[key] for key in row if key != "duration_seconds"}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
