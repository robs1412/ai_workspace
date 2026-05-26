#!/usr/local/bin/python3.13
"""Private source-info intake helper.

Moves files from the approved private inbox into archive/processed storage and
writes one non-secret JSON sidecar per processed file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECURE_ROOT = ROOT / ".private" / "ai-workspace" / "secure-info"
INBOX = SECURE_ROOT / "inbox"
PROCESSED = SECURE_ROOT / "processed"
ARCHIVE = SECURE_ROOT / "archive"
METADATA = SECURE_ROOT / "metadata"

SOURCE_SYSTEMS = {
    "google_drive",
    "gmail_frank",
    "gmail_avignon",
    "papers",
    "manual_upload",
    "workspace_export",
    "other",
}


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return clean or "untagged"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 2
    while True:
        next_candidate = directory / f"{stem}-{index}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        index += 1


def chmod_private(path: Path) -> None:
    try:
        path.chmod(0o600 if path.is_file() else 0o700)
    except OSError:
        pass


def owner_default(source_system: str) -> str:
    if source_system == "gmail_frank":
        return "frank"
    if source_system == "gmail_avignon":
        return "avignon"
    return "ai-workspace"


def iter_inbox_files() -> list[Path]:
    return sorted(path for path in INBOX.iterdir() if path.is_file() and not path.name.startswith("."))


def ingest_file(path: Path, args: argparse.Namespace) -> dict:
    date_prefix = datetime.now(timezone.utc).strftime("%Y%m%d")
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", path.name).strip("-") or "source-file"
    processed_name = safe_name if safe_name.startswith(f"{date_prefix}-") else f"{date_prefix}-{safe_name}"
    archive_path = unique_path(ARCHIVE, safe_name)
    processed_path = unique_path(PROCESSED, processed_name)

    digest = sha256_file(path)
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    owner = slug(args.owner or owner_default(args.source_system))
    tags = [slug(tag) for tag in args.tags if tag.strip()]

    if args.dry_run:
        return {
            "source_path": str(path),
            "archive_path": str(archive_path),
            "processed_path": str(processed_path),
            "metadata_path": str(METADATA / f"{processed_path.stem}.json"),
            "sha256": digest,
            "dry_run": True,
        }

    shutil.copy2(path, archive_path)
    shutil.copy2(path, processed_path)
    path.unlink()

    for private_path in (archive_path, processed_path):
        chmod_private(private_path)

    sidecar = {
        "source_path": str(path),
        "archive_path": str(archive_path),
        "processed_path": str(processed_path),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source_system": args.source_system,
        "owner": owner,
        "tags": tags,
        "sha256": digest,
        "mime_type": mime_type,
        "notes": args.notes or "",
    }
    metadata_path = unique_path(METADATA, f"{processed_path.stem}.json")
    metadata_path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    chmod_private(metadata_path)
    sidecar["metadata_path"] = str(metadata_path)
    return sidecar


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest files from the private secure-info inbox.")
    parser.add_argument("--source-system", required=True, choices=sorted(SOURCE_SYSTEMS))
    parser.add_argument("--owner", default="", help="Owner slug; defaults from source system where possible.")
    parser.add_argument("--tag", dest="tags", action="append", default=[], help="Repeatable lowercase-slug tag.")
    parser.add_argument("--notes", default="", help="Non-secret note for metadata sidecar.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned archive/processed/metadata paths only.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for directory in (INBOX, PROCESSED, ARCHIVE, METADATA):
        directory.mkdir(parents=True, exist_ok=True)
        chmod_private(directory)

    files = iter_inbox_files()
    if not files:
        print(json.dumps({"ok": True, "ingested": 0, "inbox": str(INBOX)}, indent=2))
        return 0

    results = [ingest_file(path, args) for path in files]
    print(json.dumps({"ok": True, "ingested": len(results), "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
