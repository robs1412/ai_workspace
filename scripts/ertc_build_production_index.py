#!/usr/bin/env python3
"""Build an HTML index from the flattened ERTC discovery production folder.

The .eml originals are used only to verify the email PDFs already present in
the production folder.
"""

from __future__ import annotations

import csv
import html
import os
import re
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path


PRODUCTION = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC/discovery-production-one-folder")
GDRIVE_ROOT = Path("/Users/robert/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work")
EML_DIR = GDRIVE_ROOT / "02_Communications/discovery_export/production_nonprivileged/eml"
OUTDIR = GDRIVE_ROOT / "00_README_AND_INDEX"
HTML_OUT = OUTDIR / "discovery-production-one-folder-index.html"
CSV_OUT = OUTDIR / "discovery-production-one-folder-index.csv"


K_RE = re.compile(r"^K_(\d{3})-(\d{4}-\d{2}|undated)_(.+)$")
EMAIL_RE = re.compile(r"^K_(\d{3})-(\d{4}-\d{2}|undated)_(.+)_Email\.pdf$")
HEADER_RE = re.compile(r"^(Subject|Date|From|To|Cc|Bcc|Message-ID):\s*(.*)$", re.I)


@dataclass
class EmlRecord:
    path: Path
    message_id: str
    subject: str
    sender: str
    to: str
    cc: str
    date: str
    body: str
    source_scope: str


def shell_text(args: list[str], timeout: int = 20) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL, timeout=timeout)


def pdf_text(path: Path, max_chars: int = 20000) -> str:
    try:
        return shell_text(["pdftotext", "-layout", str(path), "-"], timeout=30)[:max_chars]
    except Exception:
        return ""


def norm_message_id(value: str) -> str:
    return (value or "").strip().strip("<>").lower()


def norm_subject(value: str) -> str:
    value = re.sub(r"(?i)^(re|fw|fwd):\s*", "", value or "").strip()
    value = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def norm_addr(value: str) -> str:
    m = re.search(r"<([^>]+)>", value or "")
    return (m.group(1) if m else value).strip().lower()


def norm_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"https?://\S+", " ", value)
    value = re.sub(r"[\W_]+", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def clean_title(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"^K_\d{3}-(?:\d{4}-\d{2}|undated)_", "", stem)
    stem = re.sub(r"_Email$", "", stem)
    stem = re.sub(r"-att$", "", stem)
    return re.sub(r"\s+", " ", stem.replace("_", " ")).strip()


def first_sentences(text: str, max_chars: int = 300) -> str:
    text = re.sub(r"\s+", " ", html.unescape(text or "")).strip()
    text = re.sub(r"(?i)^body\s+", "", text).strip()
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(parts[:2]).strip() or text
    if len(out) > max_chars:
        out = out[: max_chars - 1].rsplit(" ", 1)[0] + "..."
    return out


def parse_pdf_headers(text: str) -> tuple[dict[str, str], str]:
    headers: dict[str, str] = {}
    body_lines: list[str] = []
    last_key = ""
    in_headers = True
    for raw in text.replace("\f", "\n").splitlines():
        line = raw.strip()
        if in_headers:
            if not line:
                if {"subject", "date", "from", "to"} <= set(headers):
                    in_headers = False
                continue
            match = HEADER_RE.match(line)
            if match:
                key = match.group(1).lower()
                if key in headers:
                    in_headers = False
                    body_lines.append(line)
                    continue
                last_key = key
                headers[last_key] = match.group(2).strip()
                continue
            if last_key == "subject" and "date" not in headers:
                headers[last_key] = (headers[last_key] + " " + line).strip()
                continue
            if last_key in {"from", "to", "cc", "bcc"} and "message-id" not in headers:
                headers[last_key] = (headers[last_key] + " " + line).strip()
                continue
            if last_key == "message-id":
                headers[last_key] = (headers[last_key] + " " + line).strip()
                continue
            in_headers = False
        if line == "Body":
            continue
        body_lines.append(line)
    return headers, "\n".join(body_lines)


def message_body(msg) -> str:
    plain_bodies: list[str] = []
    html_bodies: list[str] = []
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        disp = (part.get("Content-Disposition") or "").lower()
        if "attachment" in disp:
            continue
        ctype = part.get_content_type()
        if ctype not in {"text/plain", "text/html"}:
            continue
        try:
            content = str(part.get_content())
        except Exception:
            continue
        if ctype == "text/html":
            content = re.sub(r"(?is)<(script|style).*?</\1>", " ", content)
            content = re.sub(r"(?is)<br\s*/?>", "\n", content)
            content = re.sub(r"(?is)</p>", "\n", content)
            content = re.sub(r"(?is)<[^>]+>", " ", content)
            html_bodies.append(content)
        else:
            plain_bodies.append(content)
    bodies = plain_bodies if plain_bodies else html_bodies
    return re.sub(r"\n{3,}", "\n\n", html.unescape("\n".join(bodies))).strip()


def load_emls() -> tuple[dict[str, EmlRecord], list[EmlRecord]]:
    by_id: dict[str, EmlRecord] = {}
    records: list[EmlRecord] = []
    for path in sorted(EML_DIR.glob("*.eml")):
        try:
            with path.open("rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)
        except Exception:
            continue
        rec = EmlRecord(
            path=path,
            message_id=norm_message_id(str(msg.get("Message-ID", ""))),
            subject=str(msg.get("Subject", "") or ""),
            sender=str(msg.get("From", "") or ""),
            to=str(msg.get("To", "") or ""),
                cc=str(msg.get("Cc", "") or ""),
                date=str(msg.get("Date", "") or ""),
                body=message_body(msg),
                source_scope="production_nonprivileged",
            )
        records.append(rec)
        if rec.message_id:
            by_id[rec.message_id] = rec
    return by_id, records


def load_all_eml_headers() -> tuple[dict[str, EmlRecord], list[EmlRecord]]:
    """Load lightweight metadata for all Google Drive EMLs as fallback matches."""
    by_id: dict[str, EmlRecord] = {}
    records: list[EmlRecord] = []
    for path in sorted(GDRIVE_ROOT.rglob("*.eml")):
        if EML_DIR in path.parents:
            continue
        try:
            with path.open("rb") as f:
                msg = BytesParser(policy=policy.default).parse(f, headersonly=True)
        except Exception:
            continue
        rec = EmlRecord(
            path=path,
            message_id=norm_message_id(str(msg.get("Message-ID", ""))),
            subject=str(msg.get("Subject", "") or ""),
            sender=str(msg.get("From", "") or ""),
            to=str(msg.get("To", "") or ""),
            cc=str(msg.get("Cc", "") or ""),
            date=str(msg.get("Date", "") or ""),
            body="",
            source_scope="google_drive_fallback",
        )
        records.append(rec)
        if rec.message_id:
            by_id[rec.message_id] = rec
    return by_id, records


def parse_date_ts(value: str) -> float | None:
    try:
        return parsedate_to_datetime(value).timestamp()
    except Exception:
        return None


def fallback_match(headers: dict[str, str], records: list[EmlRecord]) -> EmlRecord | None:
    subj = norm_subject(headers.get("subject", ""))
    sender = norm_addr(headers.get("from", ""))
    ts = parse_date_ts(headers.get("date", ""))
    best_score = 0
    best = None
    for rec in records:
        score = 0
        if subj and norm_subject(rec.subject) == subj:
            score += 45
        if sender and norm_addr(rec.sender) == sender:
            score += 25
        rec_ts = parse_date_ts(rec.date)
        if ts is not None and rec_ts is not None:
            delta = abs(ts - rec_ts)
            if delta <= 60:
                score += 45
            elif delta <= 3600:
                score += 25
            elif delta <= 86400:
                score += 10
        if score > best_score:
            best_score = score
            best = rec
    return best if best_score >= 90 else None


def verification_status(pdf_body: str, eml: EmlRecord | None) -> tuple[str, str]:
    if eml is None:
        return "No .eml match", "No matching original .eml found in the checked Google Drive EML sources."
    pdf_norm = norm_text(pdf_body)
    eml_norm = norm_text(eml.body)
    if not eml_norm:
        return "Original has no body text", "Matched .eml, but no body text could be extracted."
    # Coverage check is more useful than full similarity because email PDFs often
    # include quoted history, while EML body extraction may surface only one MIME
    # alternative or normalize quote blocks differently.
    eml_tokens = eml_norm.split()
    pdf_tokens = pdf_norm.split()
    if eml_tokens:
        lead = " ".join(eml_tokens[: min(45, len(eml_tokens))])
        if lead and lead in pdf_norm:
            return "OK", f"Matched .eml lead text is present in the PDF ({eml.source_scope})."
    if pdf_tokens:
        lead = " ".join(pdf_tokens[: min(45, len(pdf_tokens))])
        if lead and lead in eml_norm:
            return "OK", f"PDF lead text is present in the matched .eml ({eml.source_scope})."
    if eml_norm in pdf_norm or pdf_norm in eml_norm:
        return "OK", f"Matched .eml text is present in the production PDF ({eml.source_scope})."
    ratio = SequenceMatcher(None, pdf_norm[:10000], eml_norm[:10000]).ratio()
    if ratio >= 0.82:
        return "OK", f"Matched .eml text is substantially present in the PDF (similarity {ratio:.2f})."
    if ratio >= 0.65:
        return "Review", f"Matched .eml, but text comparison is only partial (similarity {ratio:.2f})."
    return "Check content", f"Matched .eml, but PDF text differs materially (similarity {ratio:.2f})."


def document_description(path: Path, previous_email: str) -> str:
    title = clean_title(path.name)
    lower = title.lower()
    if path.name.endswith("-att" + path.suffix):
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            base = "Image attachment"
        elif path.suffix.lower() == ".xlsx":
            base = "Spreadsheet attachment"
        elif path.suffix.lower() == ".docx":
            base = "Word document attachment"
        elif path.suffix.lower() == ".pdf":
            base = "PDF attachment"
        else:
            base = "Attachment"
        return f"{base} associated with the preceding email" + (f" about {previous_email}." if previous_email else ".")
    text = pdf_text(path, 2500) if path.suffix.lower() == ".pdf" else ""
    sample = first_sentences(text, 240)
    if sample and len(sample) > 40:
        return sample
    if "941-x" in lower:
        return "Signed amended Form 941-X payroll tax return for an ERTC claim quarter."
    if "941" in lower and "transcript" in lower:
        return "IRS account transcript for a Form 941 payroll tax quarter relevant to ERTC status."
    if "941" in lower:
        return "Form 941 payroll tax return for a quarter relevant to the ERTC claim."
    if "ppp" in lower:
        return "PPP loan or forgiveness document included as COVID-era relief background."
    if "study report" in lower or "breakdown" in lower:
        return "Leyton ERTC study support document showing the claim analysis or calculations."
    if "demand letter" in lower:
        return "Levin & Levy demand letter concerning the ERTC dispute."
    if "denial" in lower:
        return "IRS denial letter concerning the claimed ERTC refund."
    if "interest" in lower:
        return "Interest calculation document related to the ERTC dispute."
    return f"Document titled {title}."


def file_uri(path: Path) -> str:
    return path.as_uri()


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    by_id, eml_records = load_emls()
    all_by_id, all_eml_records = load_all_eml_headers()
    rows: list[dict[str, str]] = []
    previous_email = ""

    files = sorted(
        PRODUCTION.glob("K_*"),
        key=lambda p: int(K_RE.match(p.name).group(1)) if K_RE.match(p.name) else 9999,
    )
    for path in files:
        match = K_RE.match(path.name)
        if not match:
            continue
        k_num, month, _ = match.groups()
        row = {
            "K #": f"K_{int(k_num):03d}",
            "Month": month,
            "Type": "Document",
            "File": path.name,
            "Subject / Title": clean_title(path.name),
            "From": "",
            "To": "",
            "Original .eml": "",
            "Content Check": "",
            "Check Notes": "",
            "Description": "",
        }
        if EMAIL_RE.match(path.name):
            text = pdf_text(path)
            headers, body = parse_pdf_headers(text)
            msg_id = norm_message_id(headers.get("message-id", ""))
            eml = by_id.get(msg_id) if msg_id else None
            if eml is None and msg_id:
                eml = all_by_id.get(msg_id)
            if eml is None:
                eml = fallback_match(headers, eml_records)
            if eml is None:
                eml = fallback_match(headers, all_eml_records)
            if eml is not None and not eml.body:
                try:
                    with eml.path.open("rb") as f:
                        msg = BytesParser(policy=policy.default).parse(f)
                    eml.body = message_body(msg)
                except Exception:
                    pass
            status, notes = verification_status(body, eml)
            row.update(
                {
                    "Type": "Email",
                    "Subject / Title": headers.get("subject", row["Subject / Title"]),
                    "From": headers.get("from", ""),
                    "To": headers.get("to", ""),
                    "Original .eml": str(eml.path) if eml else "",
                    "Content Check": status,
                    "Check Notes": notes,
                    "Description": first_sentences(eml.body if eml else body, 300)
                    or f"Email concerning {headers.get('subject', row['Subject / Title'])}.",
                }
            )
            previous_email = row["Subject / Title"]
        else:
            row["Description"] = document_description(path, previous_email)
            if row["Type"] != "Attachment" and not path.name.endswith("-att" + path.suffix):
                previous_email = ""
            if path.name.endswith("-att" + path.suffix):
                row["Type"] = "Attachment"
        rows.append(row)

    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "K #",
            "Month",
            "Type",
            "File",
            "Subject / Title",
            "Description",
            "From",
            "To",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    css = """
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;margin:24px;color:#111}
h1{font-size:22px;margin:0 0 8px}.meta{font-size:13px;color:#555;margin:0 0 18px}
table{border-collapse:collapse;width:100%;font-size:12px;line-height:1.35}
th{position:sticky;top:0;background:#f3f5f7;border:1px solid #d8dde3;padding:6px;text-align:left}
td{border:1px solid #e1e4e8;padding:6px;vertical-align:top}tr:nth-child(even){background:#fbfbfc}
.num,.month,.type,.status{white-space:nowrap}.desc{min-width:280px}.ok{color:#176b32;font-weight:600}.review{color:#9a5b00;font-weight:600}.bad{color:#a12121;font-weight:600}
a{color:#0645ad;text-decoration:none}a:hover{text-decoration:underline}
"""
    html_rows = []
    for row in rows:
        prod_path = PRODUCTION / row["File"]
        eml_cell = ""
        if row["Original .eml"]:
            eml_path = Path(row["Original .eml"])
            eml_cell = f'<a href="{html.escape(file_uri(eml_path))}">{html.escape(eml_path.name)}</a>'
        status = row["Content Check"]
        status_class = "ok" if status == "OK" else "review" if status == "Review" else "bad" if status else ""
        html_rows.append(
            "<tr>"
            f'<td class="num">{html.escape(row["K #"])}</td>'
            f'<td class="month">{html.escape(row["Month"])}</td>'
            f'<td class="type">{html.escape(row["Type"])}</td>'
            f'<td><a href="{html.escape(file_uri(prod_path))}">{html.escape(row["File"])}</a></td>'
            f'<td>{html.escape(row["Subject / Title"])}</td>'
            f'<td class="desc">{html.escape(row["Description"])}</td>'
            f'<td>{html.escape(row["From"])}</td>'
            f'<td>{html.escape(row["To"])}</td>'
            "</tr>"
        )

    emails = [r for r in rows if r["Type"] == "Email"]
    ok_count = sum(1 for r in emails if r["Content Check"] == "OK")
    review_count = sum(1 for r in emails if r["Content Check"] == "Review")
    bad_count = sum(1 for r in emails if r["Content Check"] not in {"OK", "Review"})
    doc = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Discovery Production One-Folder Index</title><style>{css}</style></head>
<body>
<h1>Discovery Production One-Folder Index</h1>
<p class="meta">Built from <code>{html.escape(str(PRODUCTION))}</code>. Email verification uses only <code>{html.escape(str(EML_DIR))}</code>. Rows: {len(rows)}. Email PDFs: {len(emails)}. OK: {ok_count}. Review: {review_count}. Needs check/no match: {bad_count}.</p>
<table>
<thead><tr><th>K #</th><th>Month</th><th>Type</th><th>File</th><th>Subject / Title</th><th>Description</th><th>From</th><th>To</th></tr></thead>
<tbody>
{chr(10).join(html_rows)}
</tbody>
</table>
</body></html>
"""
    HTML_OUT.write_text(doc, encoding="utf-8")
    print(f"HTML={HTML_OUT}")
    print(f"CSV={CSV_OUT}")
    print(f"ROWS={len(rows)} EMAILS={len(emails)} EMLS_AVAILABLE={len(eml_records)} FALLBACK_EMLS={len(all_eml_records)} OK={ok_count} REVIEW={review_count} NEEDS_CHECK={bad_count}")


if __name__ == "__main__":
    main()
