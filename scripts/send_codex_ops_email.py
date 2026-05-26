#!/usr/local/bin/python3.13

from __future__ import annotations

import argparse
import json
import smtplib
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate, getaddresses, make_msgid
from pathlib import Path

DEFAULT_FROM = "codex@kovaldistillery.com"
DEFAULT_FROM_NAME = "Codex Local Agent"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a plain-text Codex ops email.")
    parser.add_argument("--creds-file", required=True, help="Credential file with User and App password.")
    parser.add_argument("--to", action="append", required=True, help="Recipient email. Can be repeated or comma-separated.")
    parser.add_argument("--cc", action="append", default=[], help="CC recipient email. Can be repeated or comma-separated.")
    parser.add_argument("--bcc", action="append", default=[], help="BCC recipient email. Can be repeated or comma-separated.")
    parser.add_argument("--subject", required=True, help="Email subject.")
    parser.add_argument("--body-file", required=True, help="Plain-text body file.")
    parser.add_argument("--from-address", default=DEFAULT_FROM, help="Visible From address.")
    parser.add_argument("--from-name", default=DEFAULT_FROM_NAME, help="Visible From display name.")
    parser.add_argument("--sent-log", default="", help="Optional JSONL log path for sent metadata.")
    parser.add_argument("--in-reply-to", default="", help="Optional In-Reply-To header for threaded replies.")
    parser.add_argument("--references", default="", help="Optional References header for threaded replies.")
    parser.add_argument("--dry-run", action="store_true", help="Print send metadata without sending.")
    return parser.parse_args()


def parse_recipient_list(entries: list[str], label: str) -> list[str]:
    values: list[str] = []
    for entry in entries or []:
        values.extend(part.strip() for part in str(entry).split(",") if part.strip())
    recipients: list[str] = []
    for display_name, addr in getaddresses(values):
        normalized = addr.strip().lower()
        if display_name and not addr:
            raise ValueError(f"Invalid {label} recipient: {display_name}")
        if not normalized or "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError(f"Invalid {label} recipient: {addr or display_name}")
        recipients.append(normalized)
    if label == "To" and not recipients:
        raise ValueError("At least one To recipient is required.")
    return recipients


def load_credentials(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    user = values.get("user", "").strip()
    password = (
        values.get("app password")
        or values.get("app pw")
        or values.get("app-pw")
        or values.get("app_pw")
        or values.get("password")
        or ""
    ).strip()
    if not user or not password:
        raise ValueError("Credential file must contain User and App password entries.")
    return {
        "user": user,
        "password": password,
        "smtp_server": values.get("smtp server", "").strip() or "smtp.gmail.com",
        "smtp_port": values.get("smtp ssl port", "").strip() or "465",
    }


def append_jsonl(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def build_message(args: argparse.Namespace, to_addrs: list[str], cc_addrs: list[str], bcc_addrs: list[str], body: str) -> EmailMessage:
    from_addr = str(args.from_address).strip().lower()
    from_name = str(args.from_name).strip()
    msg = EmailMessage()
    msg["From"] = formataddr((from_name, from_addr)) if from_name else from_addr
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    msg["Subject"] = str(args.subject).strip()
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=from_addr.split("@", 1)[1])
    in_reply_to = str(args.in_reply_to or "").strip()
    references = str(args.references or "").strip()
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references
    msg.set_content(body)
    return msg


def main() -> int:
    args = parse_args()
    to_addrs = parse_recipient_list(args.to, "To")
    cc_addrs = parse_recipient_list(args.cc, "Cc")
    bcc_addrs = parse_recipient_list(args.bcc, "Bcc")
    body = Path(args.body_file).read_text(encoding="utf-8")
    if not body.strip():
        raise ValueError("Body file must not be empty.")
    creds = load_credentials(Path(args.creds_file))
    msg = build_message(args, to_addrs, cc_addrs, bcc_addrs, body)
    recipients = [*to_addrs, *cc_addrs, *bcc_addrs]

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "from": str(msg["From"]),
                    "to": to_addrs,
                    "cc": cc_addrs,
                    "bcc_count": len(bcc_addrs),
                    "subject": str(msg["Subject"]),
                    "message_id": str(msg["Message-ID"]),
                    "in_reply_to": str(msg.get("In-Reply-To", "")),
                    "references": str(msg.get("References", "")),
                    "sent_log": args.sent_log,
                },
                ensure_ascii=True,
            )
        )
        return 0

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(creds["smtp_server"], int(creds["smtp_port"]), timeout=25, context=context) as conn:
        conn.login(creds["user"], creds["password"])
        conn.send_message(msg, from_addr=str(args.from_address).strip().lower(), to_addrs=recipients)

    if args.sent_log:
        append_jsonl(
            Path(args.sent_log),
            {
                "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "source": "send_codex_ops_email.py",
                "from": str(args.from_address).strip().lower(),
                "to": to_addrs,
                "cc": cc_addrs,
                "bcc_count": len(bcc_addrs),
                "subject": str(msg["Subject"]),
                "message_id": str(msg["Message-ID"]),
                "in_reply_to": str(msg.get("In-Reply-To", "")),
                "references": str(msg.get("References", "")),
            },
        )

    print(json.dumps({"message_id": str(msg["Message-ID"]), "to_count": len(to_addrs), "cc_count": len(cc_addrs)}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"send_codex_ops_email.py: {exc}", file=sys.stderr)
        raise
