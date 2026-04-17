#!/usr/bin/env python3
"""Build ERTC discovery email exports from local table docs and EML archives.

Outputs are case files, not repo artifacts. This script does not print message
content. It creates .eml copies, readable .txt bodies, attachment folders, and
CSV manifests. Alan Borlack / aborlack material is separated as privileged.
"""

from __future__ import annotations

import argparse
import csv
import email
import email.policy
import hashlib
import html
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path
from typing import Iterable

CASE_ROOT = Path('/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work')
EXPORT_DOC_ROOT = CASE_ROOT / '00_README_AND_INDEX/google-doc-exports'
COMM_DOCS = [
    EXPORT_DOC_ROOT / '02_Communications/communication_summaries/2025 ERTC issue E-mail communication 1 (before July 28, 2025).txt',
    EXPORT_DOC_ROOT / '02_Communications/communication_summaries/2025 ERTC issue E-mail communication 2 (after Jul 28, 2025).txt',
    EXPORT_DOC_ROOT / '02_Communications/communication_summaries/2025 ERTC issue E-mail communication 3 - updated 2026.txt',
]
MISSING_DOC = EXPORT_DOC_ROOT / '06_Working_Files/external_workspace_archive/ertc_workspace/2026 ERTC/2026 missing E-mails from original google docs.txt'
INDEX_ROOT = CASE_ROOT / '02_Communications/email_exports/by_source/emails/robert'
DEFAULT_OUTPUT = CASE_ROOT / '02_Communications/discovery_export'
PRIVILEGE_RE = re.compile(r'\bborlack\b|aborlack@bbn-law\.com', re.I)


@dataclass
class TableHeader:
    source_doc: str
    ordinal: int
    from_line: str = ''
    date_line: str = ''
    subject: str = ''
    to_line: str = ''
    cc_line: str = ''

    @property
    def from_emails(self) -> set[str]:
        return extract_emails(self.from_line)

    @property
    def all_text(self) -> str:
        return ' '.join([self.from_line, self.date_line, self.subject, self.to_line, self.cc_line])


@dataclass
class IndexRow:
    source_index: Path
    base_dir: Path
    row: dict
    eml_path: Path

    @property
    def message_key(self) -> str:
        raw = self.row.get('gmail_id') or self.row.get('message_id') or str(self.eml_path)
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]

    @property
    def subject(self) -> str:
        return self.row.get('subject', '')

    @property
    def normalized_subject(self) -> str:
        return normalize_subject(self.subject)

    @property
    def people_text(self) -> str:
        return ' '.join(self.row.get(k, '') for k in ('from', 'to', 'cc'))

    @property
    def all_text(self) -> str:
        return ' '.join(str(v) for v in self.row.values())

    @property
    def is_privileged(self) -> bool:
        return bool(PRIVILEGE_RE.search(self.all_text))


def extract_emails(value: str) -> set[str]:
    return {addr.lower() for _name, addr in getaddresses([value]) if addr and '@' in addr}


def normalize_subject(value: str) -> str:
    value = html.unescape(value or '')
    value = re.sub(r'\s+', ' ', value).strip().lower()
    while True:
        new = re.sub(r'^(re|fwd|fw)\s*:\s*', '', value).strip()
        if new == value:
            break
        value = new
    return value


def parse_date(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    value = re.sub(r'^(date|sent):\s*', '', value, flags=re.I).strip()
    value = value.replace('\u202f', ' ').replace('\xa0', ' ')
    try:
        dt = parsedate_to_datetime(value)
        return dt.replace(tzinfo=None)
    except Exception:
        pass
    patterns = [
        '%b %d, %Y at %H:%M:%S',
        '%b %d, %Y at %H:%M',
        '%B %d, %Y at %I:%M %p',
        '%B %d, %Y at %I:%M:%S %p',
        '%Y-%m-%d %I:%M %p',
        '%Y-%m-%d %H:%M:%S',
    ]
    cleaned = re.sub(r'\s+', ' ', value)
    cleaned = re.sub(r'\s*(CST|CDT|UTC|GMT)$', '', cleaned, flags=re.I)
    for pat in patterns:
        try:
            return datetime.strptime(cleaned, pat)
        except ValueError:
            continue
    return None


def parse_table_headers(path: Path) -> list[TableHeader]:
    headers: list[TableHeader] = []
    current: TableHeader | None = None
    ordinal = 0
    for line in path.read_text(errors='replace').splitlines():
        stripped = line.strip()
        m = re.match(r'^(From|Date|Sent|Subject|To|Cc):\s*(.*)$', stripped, flags=re.I)
        if not m:
            continue
        key = m.group(1).lower()
        value = m.group(2).strip()
        if key == 'from':
            if current and current.subject:
                headers.append(current)
            ordinal += 1
            current = TableHeader(path.name, ordinal, from_line=value)
        elif current:
            if key in ('date', 'sent') and not current.date_line:
                current.date_line = value
            elif key == 'subject' and not current.subject:
                current.subject = value
            elif key == 'to' and not current.to_line:
                current.to_line = value
            elif key == 'cc' and not current.cc_line:
                current.cc_line = value
    if current and current.subject:
        headers.append(current)
    return headers


def load_indexes() -> list[IndexRow]:
    rows: list[IndexRow] = []
    for index in INDEX_ROOT.rglob('index.csv'):
        base_dir = index.parent
        with index.open(newline='', errors='replace') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                rel = row.get('path') or ''
                eml_path = base_dir.parent / rel if rel else Path('')
                if eml_path.exists():
                    rows.append(IndexRow(index, base_dir, row, eml_path))
    return rows


def header_matches_row(header: TableHeader, row: IndexRow) -> bool:
    if normalize_subject(header.subject) != row.normalized_subject:
        return False
    header_from = header.from_emails
    if header_from and not (header_from & extract_emails(row.row.get('from', ''))):
        return False
    hdate = parse_date(header.date_line)
    rdate = parse_date(row.row.get('date_chicago') or row.row.get('date') or '')
    if hdate and rdate and abs(hdate - rdate) > timedelta(days=1):
        return False
    return True


def missing_doc_paths() -> list[Path]:
    paths: list[Path] = []
    text = MISSING_DOC.read_text(errors='replace') if MISSING_DOC.exists() else ''
    for rel in re.findall(r'\(((?:levinlevy|leyton)/(?:sent|received)/[^)]+?\.eml)\)', text):
        for root in (INDEX_ROOT / 'levinlevy', INDEX_ROOT / 'leyton'):
            candidate = root.parent / rel
            if candidate.exists():
                paths.append(candidate)
                break
    return paths


def html_to_text(value: str) -> str:
    value = re.sub(r'(?is)<(script|style).*?>.*?</\1>', '', value)
    value = re.sub(r'(?i)<br\s*/?>', '\n', value)
    value = re.sub(r'(?i)</p\s*>', '\n\n', value)
    value = re.sub(r'<[^>]+>', '', value)
    return html.unescape(value)


def message_body_text(msg: email.message.EmailMessage) -> str:
    plain_parts: list[str] = []
    html_parts: list[str] = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        disposition = (part.get_content_disposition() or '').lower()
        if disposition == 'attachment':
            continue
        ctype = part.get_content_type()
        try:
            content = part.get_content()
        except Exception:
            payload = part.get_payload(decode=True) or b''
            content = payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
        if ctype == 'text/plain':
            plain_parts.append(str(content))
        elif ctype == 'text/html':
            html_parts.append(html_to_text(str(content)))
    return '\n\n'.join(plain_parts or html_parts).strip()


def safe_filename(value: str, limit: int = 120) -> str:
    value = re.sub(r'[/:\\\0]+', ' - ', value or '').strip()
    value = re.sub(r'\s+', ' ', value)
    return (value[:limit].strip() or 'message')


def export_message(row: IndexRow, out_root: Path, bucket: str, sequence: int, reasons: list[str]) -> dict:
    raw = row.eml_path.read_bytes()
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    subject = str(msg.get('Subject', row.subject or 'no-subject'))
    date = str(msg.get('Date', row.row.get('date_chicago', '')))
    prefix = f'{sequence:05d}-{row.message_key}-{safe_filename(subject, 80)}'
    bucket_root = out_root / bucket
    eml_dir = bucket_root / 'eml'
    txt_dir = bucket_root / 'txt'
    meta_dir = bucket_root / 'metadata'
    attach_dir = bucket_root / 'attachments' / prefix
    for d in (eml_dir, txt_dir, meta_dir, attach_dir):
        d.mkdir(parents=True, exist_ok=True)
    eml_out = eml_dir / f'{prefix}.eml'
    txt_out = txt_dir / f'{prefix}.txt'
    meta_out = meta_dir / f'{prefix}.json'
    shutil.copy2(row.eml_path, eml_out)
    body = message_body_text(msg)
    header_text = '\n'.join([
        f'From: {msg.get("From", row.row.get("from", ""))}',
        f'To: {msg.get("To", row.row.get("to", ""))}',
        f'Cc: {msg.get("Cc", row.row.get("cc", ""))}',
        f'Date: {date}',
        f'Subject: {subject}',
        f'Source EML: {row.eml_path}',
        f'Discovery Bucket: {bucket}',
        f'Match Reasons: {"; ".join(reasons)}',
        '',
        '--- BODY ---',
        '',
    ])
    txt_out.write_text(header_text + body + '\n', encoding='utf-8', errors='replace')
    attachments = []
    attachment_count = 0
    for part in msg.walk():
        if part.is_multipart():
            continue
        filename = part.get_filename()
        disposition = part.get_content_disposition()
        if not filename and disposition != 'attachment':
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        attachment_count += 1
        name = safe_filename(filename or f'attachment-{attachment_count}', 160)
        target = attach_dir / f'{attachment_count:02d}-{name}'
        target.write_bytes(payload)
        attachments.append(str(target))
    if not attachments:
        try:
            attach_dir.rmdir()
        except OSError:
            pass
    meta = {
        'message_hash': row.message_key,
        'source_eml': str(row.eml_path),
        'source_index': str(row.source_index),
        'gmail_id_hash': hashlib.sha256(row.row.get('gmail_id', '').encode('utf-8')).hexdigest()[:16] if row.row.get('gmail_id') else '',
        'date_chicago': row.row.get('date_chicago', ''),
        'from': row.row.get('from', ''),
        'to': row.row.get('to', ''),
        'cc': row.row.get('cc', ''),
        'subject': row.subject,
        'bucket': bucket,
        'match_reasons': reasons,
        'eml_export': str(eml_out),
        'txt_export': str(txt_out),
        'attachments': attachments,
    }
    meta_out.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding='utf-8')
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default=str(DEFAULT_OUTPUT))
    args = ap.parse_args()
    out_root = Path(args.output)
    out_root.mkdir(parents=True, exist_ok=True)

    rows = load_indexes()
    by_path = {r.eml_path: r for r in rows}
    targets: dict[Path, tuple[IndexRow, set[str]]] = {}

    headers: list[TableHeader] = []
    for doc in COMM_DOCS:
        if doc.exists():
            headers.extend(parse_table_headers(doc))
    for header in headers:
        matches = [row for row in rows if header_matches_row(header, row)]
        for row in matches:
            targets.setdefault(row.eml_path, (row, set()))[1].add(f'table:{header.source_doc}#{header.ordinal}')

    for path in missing_doc_paths():
        row = by_path.get(path)
        if row:
            targets.setdefault(path, (row, set()))[1].add('missing-email-list')

    for row in rows:
        if row.is_privileged:
            targets.setdefault(row.eml_path, (row, set()))[1].add('privileged-borlack-index')

    manifests = []
    nonpriv_seq = 0
    priv_seq = 0
    for path, (row, reasons_set) in sorted(targets.items(), key=lambda item: (item[1][0].row.get('date_chicago', ''), str(item[0]))):
        privileged = row.is_privileged
        bucket = 'privileged_alan_borlack' if privileged else 'production_nonprivileged'
        if privileged:
            priv_seq += 1
            seq = priv_seq
        else:
            nonpriv_seq += 1
            seq = nonpriv_seq
        meta = export_message(row, out_root, bucket, seq, sorted(reasons_set))
        manifests.append(meta)

    manifest_path = out_root / 'discovery_manifest.csv'
    with manifest_path.open('w', newline='', encoding='utf-8') as fh:
        fields = ['bucket', 'date_chicago', 'from', 'to', 'cc', 'subject', 'message_hash', 'source_eml', 'eml_export', 'txt_export', 'attachments_count', 'match_reasons']
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for meta in manifests:
            wr.writerow({
                'bucket': meta['bucket'],
                'date_chicago': meta['date_chicago'],
                'from': meta['from'],
                'to': meta['to'],
                'cc': meta['cc'],
                'subject': meta['subject'],
                'message_hash': meta['message_hash'],
                'source_eml': meta['source_eml'],
                'eml_export': meta['eml_export'],
                'txt_export': meta['txt_export'],
                'attachments_count': len(meta['attachments']),
                'match_reasons': '; '.join(meta['match_reasons']),
            })
    summary = {
        'table_headers_parsed': len(headers),
        'local_index_rows': len(rows),
        'targets_exported': len(manifests),
        'production_nonprivileged': sum(1 for m in manifests if m['bucket'] == 'production_nonprivileged'),
        'privileged_alan_borlack': sum(1 for m in manifests if m['bucket'] == 'privileged_alan_borlack'),
        'attachments_saved': sum(len(m['attachments']) for m in manifests),
        'manifest': str(manifest_path),
    }
    (out_root / 'discovery_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
