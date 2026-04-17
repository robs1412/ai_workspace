#!/usr/bin/env python3
"""Extract non-signature attachments from Gmail `.eml` exports.

The script is intentionally conservative: it keeps normal attachments and skips
common inline signature/logo images. It does not print message body content.
"""

from __future__ import annotations

import argparse
import csv
import email
import email.policy
import hashlib
import json
import mimetypes
import re
import shutil
import time
from pathlib import Path


SIGNATURE_NAME_RE = re.compile(
    r"(?i)(^image\d+\.(?:png|jpe?g|gif)$|logo|signature|sig-|facebook|linkedin|"
    r"instagram|twitter|youtube|social|icon|banner|spacer|pixel|cid)"
)
IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"}


def safe_filename(value: str, limit: int = 140) -> str:
    value = re.sub(r"[/:\\\0]+", " - ", value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return (value[:limit].strip() or "attachment")


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()[:16]


def header_value(msg: email.message.EmailMessage, name: str) -> str:
    return str(msg.get(name, "")).replace("\n", " ").replace("\r", " ").strip()


def likely_signature_part(part: email.message.Message, filename: str, payload: bytes) -> tuple[bool, str]:
    content_type = part.get_content_type().lower()
    disposition = (part.get_content_disposition() or "").lower()
    content_id = str(part.get("Content-ID", "")).strip()
    content_location = str(part.get("Content-Location", "")).strip()
    name = filename or content_id or content_location
    lower_name = name.lower()

    if content_type in IMAGE_TYPES:
        if disposition == "inline":
            return True, "inline-image"
        if content_id and len(payload) <= 200_000:
            return True, "cid-image"
        if SIGNATURE_NAME_RE.search(lower_name) and len(payload) <= 250_000:
            return True, "signature-image-name"
        if len(payload) <= 8_000:
            return True, "tiny-image"

    if SIGNATURE_NAME_RE.search(lower_name) and len(payload) <= 50_000:
        return True, "signature-name-small-file"

    return False, ""


def attachment_filename(part: email.message.Message, index: int) -> str:
    filename = part.get_filename()
    if filename:
        return safe_filename(filename)
    ext = mimetypes.guess_extension(part.get_content_type()) or ".bin"
    return f"attachment-{index:02d}{ext}"


def extract(input_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_root = output_dir / "attachments"
    saved_root.mkdir(parents=True, exist_ok=True)

    attachment_rows: list[dict] = []
    skipped_rows: list[dict] = []
    message_count = 0

    for eml_path in sorted(input_dir.glob("*.eml")):
        message_count += 1
        raw = eml_path.read_bytes()
        msg = email.message_from_bytes(raw, policy=email.policy.default)
        message_hash = eml_path.name.split("-", 2)[1] if "-" in eml_path.name else hash_bytes(raw)
        subject = header_value(msg, "Subject")
        message_prefix = safe_filename(f"{eml_path.stem}", 170)
        message_dir = saved_root / message_prefix
        saved_in_message = 0

        part_index = 0
        for part in msg.walk():
            if part.is_multipart():
                continue
            filename = part.get_filename() or ""
            disposition = (part.get_content_disposition() or "").lower()
            content_type = part.get_content_type().lower()
            if not filename and disposition not in {"attachment", "inline"}:
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            part_index += 1
            candidate_name = attachment_filename(part, part_index)
            skip, reason = likely_signature_part(part, candidate_name, payload)
            row = {
                "message_hash": message_hash,
                "message_file": str(eml_path),
                "date": header_value(msg, "Date"),
                "from": header_value(msg, "From"),
                "to": header_value(msg, "To"),
                "cc": header_value(msg, "Cc"),
                "subject": subject,
                "content_type": content_type,
                "content_disposition": disposition,
                "original_filename": filename,
                "size_bytes": len(payload),
                "payload_hash": hash_bytes(payload),
            }
            if skip:
                row["skip_reason"] = reason
                skipped_rows.append(row)
                continue

            saved_in_message += 1
            message_dir.mkdir(parents=True, exist_ok=True)
            target = message_dir / f"{saved_in_message:02d}-{safe_filename(candidate_name)}"
            dedupe_counter = 2
            while target.exists() and target.read_bytes() != payload:
                target = message_dir / f"{saved_in_message:02d}-{dedupe_counter}-{safe_filename(candidate_name)}"
                dedupe_counter += 1
            target.write_bytes(payload)
            row["attachment_file"] = str(target)
            attachment_rows.append(row)

        if saved_in_message == 0 and message_dir.exists():
            shutil.rmtree(message_dir)

    attachment_manifest = output_dir / "attachments-manifest.csv"
    skipped_manifest = output_dir / "skipped-signature-inline-manifest.csv"
    attachment_fields = [
        "message_hash",
        "date",
        "from",
        "to",
        "cc",
        "subject",
        "original_filename",
        "content_type",
        "content_disposition",
        "size_bytes",
        "payload_hash",
        "attachment_file",
        "message_file",
    ]
    skipped_fields = [
        "message_hash",
        "date",
        "from",
        "to",
        "cc",
        "subject",
        "original_filename",
        "content_type",
        "content_disposition",
        "size_bytes",
        "payload_hash",
        "skip_reason",
        "message_file",
    ]
    with attachment_manifest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=attachment_fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in attachment_fields} for row in attachment_rows)
    with skipped_manifest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=skipped_fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in skipped_fields} for row in skipped_rows)

    summary = {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "messages_scanned": message_count,
        "attachments_saved": len(attachment_rows),
        "signature_inline_files_skipped": len(skipped_rows),
        "attachment_manifest": str(attachment_manifest),
        "skipped_manifest": str(skipped_manifest),
        "exported_at": int(time.time()),
    }
    summary_path = output_dir / "attachments-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract non-signature attachments from Gmail .eml exports.")
    parser.add_argument("--input", required=True, help="Directory containing exported .eml files")
    parser.add_argument("--output", required=True, help="Output directory for extracted attachments")
    args = parser.parse_args()

    summary = extract(Path(args.input).expanduser().resolve(), Path(args.output).expanduser().resolve())
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
