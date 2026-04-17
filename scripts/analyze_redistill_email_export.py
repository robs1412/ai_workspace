#!/usr/bin/env python3
"""Analyze the 2026 Re-Distill email export and write a Markdown report.

The script reads exported `.json` metadata sidecars and folder direction
(`sent`/`received`). It does not read message bodies and does not modify the
exported `.eml` files.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import email.utils
import html
import json
import math
import os
import pathlib
import re
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Iterable


DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
STOPWORDS = {
    "the", "and", "for", "with", "from", "your", "you", "are", "our", "this",
    "that", "have", "has", "will", "about", "into", "koval", "distillery",
    "inc", "re", "fw", "fwd", "aw", "wg", "external", "spam", "please",
    "thank", "thanks", "hello", "hi", "new",
}

CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Events / tastings / private bookings", ("event", "events", "tasting", "tour", "private party", "private event", "booking", "wedding", "market", "festival", "gala", "bbq", "workshop")),
    ("Marketing / creative / brand", ("marketing", "social", "media", "brand", "asset", "design", "flyer", "campaign", "website", "photo", "photography", "press", "toolkit", "pos")),
    ("Sales / distributors / orders", ("purchase order", " po ", "order", "orders", "rmdc", "rndc", "sgws", "southern", "distributor", "distribution", "sales", "quote", "pricing", "customer", "account")),
    ("Production / operations", ("production", "bottling", "distilling", "ferment", "barrel", "batch", "tank", "mash", "warehouse", "inventory", "sample", "samples")),
    ("Shipping / logistics", ("ship", "shipment", "shipping", "delivery", "pickup", "container", "freight", "tracking", "bol", "pallet", "appointment")),
    ("Finance / accounting / payments", ("invoice", "payment", "payroll", "receipt", "credit card", "statement", "balance", "accounting", "bill", "tax", "refund", "quickbooks")),
    ("Compliance / legal / insurance", ("legal", "contract", "agreement", "insurance", "inspection", "license", "permit", "certificate", "mosa", "ttb", "audit", "wosb", "trademark")),
    ("HR / staffing / benefits", ("vacation", "benefits", "hire", "hiring", "employee", "staff", "payroll", "training", "onboarding", "schedule", "shift")),
    ("IT / systems / reports", ("crm", "portal", "ops", "report", "login", "password", "security", "website", "system", "database", "google", "suspicious login")),
    ("International / export", ("japan", "china", "canada", "export", "international", "container", "saq", "eu", "germany", "kefla")),
    ("Donations / community", ("donation", "fundraiser", "nonprofit", "charity", "sponsor", "sponsorship", "community")),
]

TASK_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Reply / follow-up", ("re ", "fwd", "fw ", "follow", "checking", "status", "update")),
    ("Scheduling / calendar", ("invitation", "accepted", "schedule", "meeting", "calendar", "availability", "appointment")),
    ("Quote / pricing / proposal", ("quote", "pricing", "proposal", "estimate")),
    ("Order / purchase order", ("purchase order", " po ", "order", "invoice", "shipment")),
    ("Review / approval", ("review", "approve", "approval", "proof", "draft", "final")),
    ("Issue resolution", ("issue", "problem", "missing", "urgent", "error", "fix", "repair", "claim")),
    ("Report / data", ("report", "analytics", "list", "summary", "forecast")),
    ("Documentation / compliance", ("certificate", "license", "permit", "inspection", "contract", "agreement", "audit")),
]


@dataclass(frozen=True)
class Record:
    year_bucket: str
    direction: str
    path: pathlib.Path
    message_hash: str
    dt_value: dt.datetime | None
    subject: str
    from_value: str
    to_value: str
    cc_value: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Re-Distill email export metadata.")
    parser.add_argument(
        "--root",
        default="/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill",
        help="Export root containing YYYY/sent and YYYY/received folders.",
    )
    parser.add_argument("--output", default=None, help="Markdown output path. Default: ROOT/report.md")
    parser.add_argument("--workers", type=int, default=24, help="Concurrent metadata readers.")
    parser.add_argument("--filenames-only", action="store_true", help="Fast report from folder/file names only.")
    parser.add_argument("--html", action="store_true", help="Also write an HTML report next to the Markdown report.")
    return parser.parse_args()


def parse_message_datetime(meta: dict) -> dt.datetime | None:
    internal = meta.get("internal_date")
    if internal:
        try:
            return dt.datetime.fromtimestamp(int(internal) / 1000, tz=dt.timezone.utc).astimezone()
        except (TypeError, ValueError, OSError):
            pass
    date_text = str(meta.get("date") or "").strip()
    if not date_text:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(date_text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone()
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def normalize_subject(subject: str) -> str:
    subject = re.sub(r"^\s*(re|fw|fwd|aw|wg)\s*[:\-]\s*", "", subject, flags=re.I)
    subject = re.sub(r"^\s*(\*\*\*spam\*\*\*\s*)+", "", subject, flags=re.I)
    subject = re.sub(r"\s+", " ", subject).strip()
    return subject or "(no subject)"


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9&'-]{2,}", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) >= 3]


def address_domains(value: str) -> list[str]:
    pairs = email.utils.getaddresses([value])
    domains = []
    for _name, addr in pairs:
        if "@" in addr:
            domain = addr.rsplit("@", 1)[1].lower().strip(" >")
            if domain:
                domains.append(domain)
    return domains


def address_labels(value: str) -> list[str]:
    pairs = email.utils.getaddresses([value])
    labels = []
    for name, addr in pairs:
        label = (name or addr or "").strip().strip('"')
        if label:
            labels.append(label[:80])
    return labels


def classify(text: str, rules: list[tuple[str, tuple[str, ...]]], default: str) -> str:
    hay = f" {text.lower()} "
    for category, needles in rules:
        if any(needle in hay for needle in needles):
            return category
    return default


def load_records(root: pathlib.Path, workers: int = 24) -> tuple[list[Record], dict[str, int]]:
    records: list[Record] = []
    audit = collections.Counter()
    seen_hashes: set[str] = set()
    parse_jobs: list[tuple[str, str, pathlib.Path]] = []
    for year_dir in sorted(p for p in root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}", p.name)):
        for direction in ("sent", "received"):
            folder = year_dir / direction
            if not folder.is_dir():
                audit[f"missing_folder_{year_dir.name}_{direction}"] += 1
                continue
            eml_stems: set[str] = set()
            json_stems: set[str] = set()
            json_paths: list[pathlib.Path] = []
            with os.scandir(folder) as entries:
                for entry in entries:
                    if not entry.is_file():
                        continue
                    name = entry.name
                    stem, ext = os.path.splitext(name)
                    if ext == ".eml":
                        eml_stems.add(stem)
                        try:
                            if entry.stat().st_size == 0:
                                audit["zero_byte_eml"] += 1
                        except OSError:
                            audit["eml_stat_failures"] += 1
                    elif ext == ".json":
                        json_stems.add(stem)
                        path = pathlib.Path(entry.path)
                        json_paths.append(path)
                        try:
                            if entry.stat().st_size == 0:
                                audit["zero_byte_json"] += 1
                        except OSError:
                            audit["json_stat_failures"] += 1
            audit[f"{year_dir.name}_{direction}_eml"] += len(eml_stems)
            audit[f"{year_dir.name}_{direction}_json"] += len(json_stems)
            audit["missing_json_for_eml"] += len(eml_stems - json_stems)
            audit["missing_eml_for_json"] += len(json_stems - eml_stems)
            parse_jobs.extend((year_dir.name, direction, path) for path in json_paths)

    def parse_one(job: tuple[str, str, pathlib.Path]) -> tuple[Record | None, str | None]:
        year_bucket, direction, path = job
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None, "json_parse_failures"
        if "-" in path.stem:
            fallback_hash = path.stem.split("-", 2)[1]
        else:
            fallback_hash = path.stem
        message_hash = str(meta.get("message_hash") or fallback_hash)
        parsed_dt = parse_message_datetime(meta)
        error = "date_parse_failures" if parsed_dt is None else None
        return (
            Record(
                year_bucket=year_bucket,
                direction=direction,
                path=path,
                message_hash=message_hash,
                dt_value=parsed_dt,
                subject=str(meta.get("subject") or ""),
                from_value=str(meta.get("from") or ""),
                to_value=str(meta.get("to") or ""),
                cc_value=str(meta.get("cc") or ""),
            ),
            error,
        )

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [executor.submit(parse_one, job) for job in parse_jobs]
        for future in as_completed(futures):
            record, error = future.result()
            if error:
                audit[error] += 1
            if record is None:
                continue
            if record.message_hash in seen_hashes:
                audit["duplicate_message_hashes"] += 1
            seen_hashes.add(record.message_hash)
            records.append(record)

    audit["records_loaded"] = len(records)
    audit["unique_hashes"] = len(seen_hashes)
    return records, dict(audit)


def table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(out)


def markdown_to_html(markdown: str, title: str) -> str:
    lines = markdown.splitlines()
    body: list[str] = []
    in_ul = False
    in_table = False

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            body.append("</ul>")
            in_ul = False

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            body.append("</tbody></table>")
            in_table = False

    def render_inline(text: str) -> str:
        escaped = html.escape(text)
        escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
        escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
        return escaped

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            close_ul()
            close_table()
            continue
        if stripped.startswith("| ") and stripped.endswith(" |"):
            close_ul()
            cells = [render_inline(c.strip()) for c in stripped.strip("|").split("|")]
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if not in_table:
                body.append("<table>")
                if next_line.startswith("| ---"):
                    body.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr></thead><tbody>")
                    in_table = True
                else:
                    body.append("<tbody><tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
                    in_table = True
            elif not all(set(c.replace(" ", "")) <= {"-"} for c in cells):
                body.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            continue
        close_table()
        if stripped.startswith("# "):
            close_ul()
            body.append(f"<h1>{render_inline(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            close_ul()
            body.append(f"<h2>{render_inline(stripped[3:])}</h2>")
        elif stripped.startswith("- "):
            if not in_ul:
                body.append("<ul>")
                in_ul = True
            body.append(f"<li>{render_inline(stripped[2:])}</li>")
        else:
            close_ul()
            body.append(f"<p>{render_inline(stripped)}</p>")

    close_ul()
    close_table()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --text: #1e2328;
      --line: #d9dee5;
      --band: #f4f7fa;
      --head: #eaf2f2;
    }}
    body {{
      margin: 0;
      font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background: #fff;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 24px 56px;
    }}
    h1 {{
      font-size: 32px;
      line-height: 1.15;
      margin: 0 0 20px;
      color: #111820;
    }}
    h2 {{
      font-size: 21px;
      margin: 34px 0 12px;
      padding-top: 14px;
      border-top: 2px solid var(--line);
      color: #17202a;
    }}
    p {{
      margin: 10px 0;
      max-width: 960px;
    }}
    ul {{
      margin: 8px 0 16px 22px;
      padding: 0;
      max-width: 980px;
    }}
    li {{ margin: 5px 0; }}
    code {{
      padding: 1px 5px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: var(--band);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.92em;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 24px;
      font-size: 14px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 8px 10px;
      vertical-align: top;
      text-align: left;
    }}
    th {{
      background: var(--head);
      color: #0b3f43;
      font-weight: 650;
    }}
    tr:nth-child(even) td {{ background: #fafbfc; }}
    strong {{ color: #101820; }}
    @media print {{
      main {{ max-width: none; padding: 16px; }}
      h2 {{ break-after: avoid; }}
      table {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
<main>
{chr(10).join(body)}
</main>
</body>
</html>
"""


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    pos = (len(values) - 1) * pct
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def minutes_estimate(sent: int, received: int) -> tuple[float, float, float]:
    low = sent * 3.0 + received * 0.75
    mid = sent * 5.0 + received * 1.5
    high = sent * 8.0 + received * 3.0
    return low, mid, high


def fmt_hours(minutes: float) -> str:
    return f"{minutes / 60:.1f}h"


def build_report(root: pathlib.Path, records: list[Record], audit: dict[str, int]) -> str:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    total = len(records)
    sent_total = sum(1 for r in records if r.direction == "sent")
    received_total = total - sent_total

    by_year_dir = collections.Counter((r.year_bucket, r.direction) for r in records)
    by_month = collections.Counter((r.year_bucket, r.dt_value.strftime("%Y-%m") if r.dt_value else "unknown", r.direction) for r in records)
    by_dow = collections.Counter((DOW[r.dt_value.weekday()] if r.dt_value else "Unknown", r.direction) for r in records)
    by_hour = collections.Counter((r.dt_value.hour if r.dt_value else -1, r.direction) for r in records)
    by_day = collections.Counter((r.dt_value.date().isoformat() if r.dt_value else "unknown", r.direction) for r in records)

    categories = collections.Counter()
    category_subjects: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    task_types = collections.Counter()
    task_subjects: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    normalized_subjects = collections.Counter()
    words = collections.Counter()
    sender_domains = collections.Counter()
    recipient_domains = collections.Counter()
    senders = collections.Counter()
    recipients = collections.Counter()

    for r in records:
        normalized = normalize_subject(r.subject)
        normalized_subjects[normalized] += 1
        category = classify(normalized, CATEGORY_RULES, "General / mixed administration")
        categories[(category, r.direction)] += 1
        category_subjects[category][normalized] += 1
        task_type = classify(normalized, TASK_RULES, "General coordination")
        task_types[(task_type, r.direction)] += 1
        task_subjects[task_type][normalized] += 1
        words.update(tokenize(normalized))
        sender_domains.update(address_domains(r.from_value))
        recipient_domains.update(address_domains(r.to_value + ", " + r.cc_value))
        senders.update(address_labels(r.from_value))
        recipients.update(address_labels(r.to_value + ", " + r.cc_value))

    daily_rows = []
    daily_minutes_mid: list[float] = []
    for date_key in sorted({k[0] for k in by_day if k[0] != "unknown"}):
        sent = by_day[(date_key, "sent")]
        received = by_day[(date_key, "received")]
        low, mid, high = minutes_estimate(sent, received)
        daily_minutes_mid.append(mid)
        daily_rows.append((date_key, sent, received, sent + received, fmt_hours(low), fmt_hours(mid), fmt_hours(high)))

    monthly_rows = []
    for month in sorted({k[1] for k in by_month if k[1] != "unknown"}):
        sent = sum(by_month[(year, month, "sent")] for year in ("2024", "2025", "2026"))
        received = sum(by_month[(year, month, "received")] for year in ("2024", "2025", "2026"))
        low, mid, high = minutes_estimate(sent, received)
        monthly_rows.append((month, sent, received, sent + received, fmt_hours(low), fmt_hours(mid), fmt_hours(high)))

    weekday_rows = []
    for day in DOW:
        sent = by_dow[(day, "sent")]
        received = by_dow[(day, "received")]
        weekday_rows.append((day, sent, received, sent + received))

    hour_rows = []
    for hour in range(24):
        sent = by_hour[(hour, "sent")]
        received = by_hour[(hour, "received")]
        if sent or received:
            hour_rows.append((f"{hour:02d}:00", sent, received, sent + received))

    category_rows = []
    for category in sorted({k[0] for k in categories}):
        sent = categories[(category, "sent")]
        received = categories[(category, "received")]
        examples = "; ".join(s for s, _count in category_subjects[category].most_common(3))
        category_rows.append((category, sent, received, sent + received, examples))
    category_rows.sort(key=lambda r: int(r[3]), reverse=True)

    task_rows = []
    for task_type in sorted({k[0] for k in task_types}):
        sent = task_types[(task_type, "sent")]
        received = task_types[(task_type, "received")]
        examples = "; ".join(s for s, _count in task_subjects[task_type].most_common(3))
        task_rows.append((task_type, sent, received, sent + received, examples))
    task_rows.sort(key=lambda r: int(r[3]), reverse=True)

    top_day_rows = sorted(daily_rows, key=lambda r: int(r[3]), reverse=True)[:25]
    active_days = len(daily_rows)
    avg_mid = statistics.mean(daily_minutes_mid) if daily_minutes_mid else 0.0
    median_mid = statistics.median(daily_minutes_mid) if daily_minutes_mid else 0.0
    p90_mid = percentile(daily_minutes_mid, 0.9)
    p95_mid = percentile(daily_minutes_mid, 0.95)

    month_by_year_rows = []
    for year in ("2024", "2025", "2026"):
        for month in sorted({k[1] for k in by_month if k[0] == year and k[1] != "unknown"}):
            sent = by_month[(year, month, "sent")]
            received = by_month[(year, month, "received")]
            month_by_year_rows.append((year, month, sent, received, sent + received))

    report: list[str] = []
    report.append("# Mark / Re-Distill Email Review")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("Scope: local exported email metadata and folder structure from `2026 Re-Distill`. This report uses `.json` sidecars plus `sent`/`received` folder placement. It does not quote message bodies.")
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append(f"- Total exported messages analyzed: **{total:,}**")
    report.append(f"- Sent: **{sent_total:,}**")
    report.append(f"- Received: **{received_total:,}**")
    report.append(f"- Active dated days: **{active_days:,}**")
    report.append(f"- Estimated average daily email workload: **{fmt_hours(avg_mid)}** at the midpoint assumption.")
    report.append(f"- Median daily email workload: **{fmt_hours(median_mid)}**; 90th percentile: **{fmt_hours(p90_mid)}**; 95th percentile: **{fmt_hours(p95_mid)}**.")
    report.append("")
    report.append("The volume pattern points to an operations-heavy role with recurring event/tasting coordination, sales/distributor/order follow-up, production/warehouse/vendor coordination, finance/compliance touchpoints, and broad internal task routing. For job-description work, the strongest signal is not one narrow department function; it is a cross-functional coordinator/operator role that turns inbound requests into scheduled work, vendor/customer follow-up, internal approvals, and status tracking.")
    report.append("")
    report.append("## Dataset Audit")
    report.append("")
    report.append(table(["Check", "Count"], [
        ("Records loaded", f"{audit.get('records_loaded', 0):,}"),
        ("Unique message hashes", f"{audit.get('unique_hashes', 0):,}"),
        ("Duplicate message hashes", f"{audit.get('duplicate_message_hashes', 0):,}"),
        ("Missing JSON for EML", f"{audit.get('missing_json_for_eml', 0):,}"),
        ("Missing EML for JSON", f"{audit.get('missing_eml_for_json', 0):,}"),
        ("Zero-byte EML", f"{audit.get('zero_byte_eml', 0):,}"),
        ("Zero-byte JSON", f"{audit.get('zero_byte_json', 0):,}"),
        ("JSON parse failures", f"{audit.get('json_parse_failures', 0):,}"),
        ("Date parse failures", f"{audit.get('date_parse_failures', 0):,}"),
    ]))
    report.append("")
    report.append("## Counts By Export Folder")
    report.append("")
    report.append(table(["Year folder", "Sent", "Received", "Total"], [
        (year, f"{by_year_dir[(year, 'sent')]:,}", f"{by_year_dir[(year, 'received')]:,}", f"{by_year_dir[(year, 'sent')] + by_year_dir[(year, 'received')]:,}")
        for year in ("2024", "2025", "2026")
    ]))
    report.append("")
    report.append("## Monthly Volume")
    report.append("")
    report.append(table(["Month", "Sent", "Received", "Total", "Low time", "Mid time", "High time"], monthly_rows))
    report.append("")
    report.append("## Monthly Volume By Year Folder")
    report.append("")
    report.append(table(["Year folder", "Message month", "Sent", "Received", "Total"], month_by_year_rows))
    report.append("")
    report.append("## Day Of Week")
    report.append("")
    report.append(table(["Day", "Sent", "Received", "Total"], weekday_rows))
    report.append("")
    report.append("## Hour Of Day")
    report.append("")
    report.append(table(["Hour", "Sent", "Received", "Total"], hour_rows))
    report.append("")
    report.append("## Busiest Days")
    report.append("")
    report.append(table(["Date", "Sent", "Received", "Total", "Low time", "Mid time", "High time"], top_day_rows))
    report.append("")
    report.append("## Daily Time Estimate Method")
    report.append("")
    report.append("- Low estimate: sent messages at 3.0 minutes each, received messages at 0.75 minutes each.")
    report.append("- Mid estimate: sent messages at 5.0 minutes each, received messages at 1.5 minutes each.")
    report.append("- High estimate: sent messages at 8.0 minutes each, received messages at 3.0 minutes each.")
    report.append("- These are email-handling estimates only. They do not include the offline work that many emails trigger: meetings, vendor calls, CRM updates, document creation, warehouse work, design review, or event execution.")
    report.append("")
    report.append("## Project / Responsibility Grouping")
    report.append("")
    report.append("Grouping is inferred from subject lines and participant metadata, not from full body review.")
    report.append("")
    report.append(table(["Project / responsibility family", "Sent", "Received", "Total", "Representative subjects"], category_rows))
    report.append("")
    report.append("## Task-Type Grouping")
    report.append("")
    report.append(table(["Task type", "Sent", "Received", "Total", "Representative subjects"], task_rows))
    report.append("")
    report.append("## Top Repeated Subject Threads")
    report.append("")
    report.append(table(["Count", "Normalized subject"], [(f"{count:,}", subject) for subject, count in normalized_subjects.most_common(60)]))
    report.append("")
    report.append("## Top Terms In Subjects")
    report.append("")
    report.append(table(["Count", "Term"], [(f"{count:,}", term) for term, count in words.most_common(80)]))
    report.append("")
    report.append("## Top Sender Domains")
    report.append("")
    report.append(table(["Count", "Domain"], [(f"{count:,}", domain) for domain, count in sender_domains.most_common(40)]))
    report.append("")
    report.append("## Top Recipient Domains")
    report.append("")
    report.append(table(["Count", "Domain"], [(f"{count:,}", domain) for domain, count in recipient_domains.most_common(40)]))
    report.append("")
    report.append("## Top Sender Labels")
    report.append("")
    report.append(table(["Count", "Sender"], [(f"{count:,}", sender) for sender, count in senders.most_common(50)]))
    report.append("")
    report.append("## Top Recipient Labels")
    report.append("")
    report.append(table(["Count", "Recipient"], [(f"{count:,}", rec) for rec, count in recipients.most_common(50)]))
    report.append("")
    report.append("## What Appears To Have Been Accomplished")
    report.append("")
    report.append("The following is inferred from repeated subjects and task categories. It should be reviewed against actual message bodies before being treated as a formal performance record.")
    report.append("")
    report.append("- Regular event and tasting-room coordination: private event inquiries, tours, workshops, market/festival participation, and calendar invitations appear repeatedly.")
    report.append("- Sales and distributor operations: purchase orders, shipping questions, distributor/customer follow-up, samples, forecasts, and price/quote threads appear as a major recurring workload.")
    report.append("- Production and product operations: barrels, bottling/packaging, labels, samples, warehouse/inventory, and vendor coordination show up across all three years.")
    report.append("- Finance/compliance support: invoices, payroll, payments, inspection/certification, insurance, and audit-adjacent threads appear often enough to be part of the role surface.")
    report.append("- Internal coordination: reports, CRM/OPS references, scheduling, approvals, document review, and follow-up threads suggest a large amount of routing work across departments.")
    report.append("")
    report.append("## Job Description Signals")
    report.append("")
    report.append("- Core function: cross-functional operations coordinator handling inbound requests, outbound follow-up, scheduling, and status tracking.")
    report.append("- Strong recurring domains: events/tastings, customer/vendor communication, distributor/order support, production/logistics coordination, compliance paperwork, and internal reporting.")
    report.append("- Important skills implied by the email mix: disciplined inbox triage, written follow-up, calendar control, vendor/customer professionalism, CRM/task-system usage, document proofing, and escalation judgment.")
    report.append("- Management need: this role should not be managed only by email volume. A task board with project families, due dates, owner, source email/thread, next action, and completion state would reduce hidden work.")
    report.append("")
    report.append("## Task-Management Recommendations")
    report.append("")
    report.append("- Convert recurring subject families into standing queues: Events/Tastings, Distributor Orders, Production/Vendors, Finance/Compliance, Internal Systems/Reports, HR/Scheduling.")
    report.append("- Track each email-derived task with fields: source thread, requester, account/vendor, due date, promised next step, owner, status, and completion evidence.")
    report.append("- Add weekly review of high-volume threads and unresolved external requests. Friday/Monday comparison should be used to decide whether weekend backlog or Monday planning time is needed.")
    report.append("- Use templates for common repeated work: event inquiry response, purchase-order follow-up, sample request, invoice/payment question, inspection/compliance request, and internal approval request.")
    report.append("- Separate communication work from execution work in workload planning. Email handling alone averages several hours on busy days; the triggered offline work likely needs separate capacity blocks.")
    report.append("")
    report.append("## Follow-Up Analysis That Would Make Sense")
    report.append("")
    report.append("- Thread-level aging: identify requests that had no outbound reply within 1, 2, or 5 business days.")
    report.append("- External vs internal split by domain, excluding `kovaldistillery.com`.")
    report.append("- Body-level action extraction for a reviewed subset only, to avoid over-collecting private content.")
    report.append("- Attachment audit by category: invoices, POs, contracts, certificates, labels/artwork, reports.")
    report.append("- Calendar correlation: compare meeting invitations with heavy email days.")
    report.append("- CRM/OPS correlation: match email-derived work to existing tasks, accounts, orders, events, and reports.")
    report.append("- SLA report: average reply time by project family and requester/domain.")
    report.append("")
    return "\n".join(report) + "\n"


def subject_from_export_name(path: pathlib.Path) -> str:
    stem = path.stem
    parts = stem.split("-", 2)
    if len(parts) == 3:
        return normalize_subject(parts[2])
    return normalize_subject(stem)


def scan_filename_records(root: pathlib.Path) -> tuple[list[tuple[str, str, pathlib.Path, str]], collections.Counter]:
    rows: list[tuple[str, str, pathlib.Path, str]] = []
    audit = collections.Counter()
    for year in ("2024", "2025", "2026"):
        for direction in ("sent", "received"):
            folder = root / year / direction
            if not folder.is_dir():
                audit[f"missing_{year}_{direction}"] += 1
                continue
            eml: set[str] = set()
            json_sidecars: set[str] = set()
            with os.scandir(folder) as entries:
                for entry in entries:
                    if not entry.is_file():
                        continue
                    stem, ext = os.path.splitext(entry.name)
                    if ext == ".eml":
                        eml.add(stem)
                        subject = subject_from_export_name(pathlib.Path(entry.name))
                        rows.append((year, direction, pathlib.Path(entry.path), subject))
                        try:
                            if entry.stat().st_size == 0:
                                audit["zero_byte_eml"] += 1
                        except OSError:
                            audit["eml_stat_failures"] += 1
                    elif ext == ".json":
                        json_sidecars.add(stem)
                        try:
                            if entry.stat().st_size == 0:
                                audit["zero_byte_json"] += 1
                        except OSError:
                            audit["json_stat_failures"] += 1
            audit[f"{year}_{direction}_eml"] = len(eml)
            audit[f"{year}_{direction}_json"] = len(json_sidecars)
            audit["missing_json_for_eml"] += len(eml - json_sidecars)
            audit["missing_eml_for_json"] += len(json_sidecars - eml)
    audit["records_loaded"] = len(rows)
    return rows, audit


def build_filename_report(root: pathlib.Path) -> str:
    rows, audit = scan_filename_records(root)
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    by_year_dir = collections.Counter((year, direction) for year, direction, _path, _subject in rows)
    categories = collections.Counter()
    category_subjects: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    task_types = collections.Counter()
    task_subjects: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    normalized_subjects = collections.Counter()
    words = collections.Counter()
    for year, direction, _path, subject in rows:
        normalized_subjects[subject] += 1
        category = classify(subject, CATEGORY_RULES, "General / mixed administration")
        categories[(category, direction)] += 1
        category_subjects[category][subject] += 1
        task_type = classify(subject, TASK_RULES, "General coordination")
        task_types[(task_type, direction)] += 1
        task_subjects[task_type][subject] += 1
        words.update(tokenize(subject))

    total = len(rows)
    sent_total = sum(1 for _year, direction, _path, _subject in rows if direction == "sent")
    received_total = total - sent_total
    year_rows = []
    workload_rows = []
    for year in ("2024", "2025", "2026"):
        sent = by_year_dir[(year, "sent")]
        received = by_year_dir[(year, "received")]
        low, mid, high = minutes_estimate(sent, received)
        year_rows.append((year, f"{sent:,}", f"{received:,}", f"{sent + received:,}"))
        workload_rows.append((year, f"{sent:,}", f"{received:,}", f"{fmt_hours(low)}", f"{fmt_hours(mid)}", f"{fmt_hours(high)}"))

    category_rows = []
    for category in sorted({k[0] for k in categories}):
        sent = categories[(category, "sent")]
        received = categories[(category, "received")]
        examples = "; ".join(s for s, _count in category_subjects[category].most_common(4))
        category_rows.append((category, f"{sent:,}", f"{received:,}", f"{sent + received:,}", examples))
    category_rows.sort(key=lambda r: int(str(r[3]).replace(",", "")), reverse=True)

    task_rows = []
    for task_type in sorted({k[0] for k in task_types}):
        sent = task_types[(task_type, "sent")]
        received = task_types[(task_type, "received")]
        examples = "; ".join(s for s, _count in task_subjects[task_type].most_common(4))
        task_rows.append((task_type, f"{sent:,}", f"{received:,}", f"{sent + received:,}", examples))
    task_rows.sort(key=lambda r: int(str(r[3]).replace(",", "")), reverse=True)

    report: list[str] = []
    report.append("# Mark / Re-Distill Email Review")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Status")
    report.append("")
    report.append("This is the first completed report pass. It uses verified folder structure, `.eml`/`.json` parity, and exported filenames/subjects. A deeper metadata pass was started for exact month and day-of-week tables, but Google Drive file-provider reads stalled on the many small JSON sidecars. For exact monthly and weekday statistics, copy or hydrate the JSON sidecars locally and rerun `python3 scripts/analyze_redistill_email_export.py` without `--filenames-only`.")
    report.append("")
    report.append("The current report is still useful for job-description and task-management review because it captures total volume, sent/received load, project families, task types, and repeated subject clusters without reading message bodies.")
    report.append("")
    report.append("## Dataset Audit")
    report.append("")
    report.append(table(["Check", "Count"], [
        ("EML records loaded", f"{audit.get('records_loaded', 0):,}"),
        ("Missing JSON for EML", f"{audit.get('missing_json_for_eml', 0):,}"),
        ("Missing EML for JSON", f"{audit.get('missing_eml_for_json', 0):,}"),
        ("Zero-byte EML", f"{audit.get('zero_byte_eml', 0):,}"),
        ("Zero-byte JSON", f"{audit.get('zero_byte_json', 0):,}"),
        ("EML stat failures", f"{audit.get('eml_stat_failures', 0):,}"),
        ("JSON stat failures", f"{audit.get('json_stat_failures', 0):,}"),
    ]))
    report.append("")
    report.append("## Counts By Year")
    report.append("")
    report.append(table(["Year", "Sent", "Received", "Total"], year_rows))
    report.append("")
    report.append("## Email Handling Time Estimate By Year")
    report.append("")
    report.append(table(["Year", "Sent", "Received", "Low", "Mid", "High"], workload_rows))
    report.append("")
    report.append("Assumptions: low = 3.0 minutes per sent email and 0.75 minutes per received email; mid = 5.0 minutes per sent and 1.5 minutes per received; high = 8.0 minutes per sent and 3.0 minutes per received. These estimates cover email handling only, not the offline work triggered by the emails.")
    report.append("")
    report.append("## Month And Day-Of-Week Stats")
    report.append("")
    report.append("Pending exact metadata pass. The export folders are split by year, but month/day-of-week require reading each JSON sidecar's `internal_date` or `date`. The first full metadata pass was started and then stopped because synced Google Drive reads stalled. Recommendation: hydrate/copy the `2026 Re-Distill` JSON sidecars to a local SSD path and rerun the full analyzer.")
    report.append("")
    report.append("## Project / Responsibility Grouping")
    report.append("")
    report.append("Grouping is inferred from exported subject filenames. It should be treated as a management-review signal, not a legal or HR finding.")
    report.append("")
    report.append(table(["Project / responsibility family", "Sent", "Received", "Total", "Representative subjects"], category_rows))
    report.append("")
    report.append("## Task-Type Grouping")
    report.append("")
    report.append(table(["Task type", "Sent", "Received", "Total", "Representative subjects"], task_rows))
    report.append("")
    report.append("## Top Repeated Subject Threads")
    report.append("")
    report.append(table(["Count", "Normalized subject"], [(f"{count:,}", subject) for subject, count in normalized_subjects.most_common(100)]))
    report.append("")
    report.append("## Top Terms In Subjects")
    report.append("")
    report.append(table(["Count", "Term"], [(f"{count:,}", term) for term, count in words.most_common(100)]))
    report.append("")
    report.append("## What Appears To Have Been Accomplished")
    report.append("")
    report.append("Inferred from subject clusters and direction counts:")
    report.append("")
    report.append("- Handled a very large volume of inbound operational requests and outbound follow-ups across three years.")
    report.append("- Coordinated events, tours, tastings, private bookings, workshops, markets, and calendar scheduling.")
    report.append("- Managed sales/order/distributor communication: purchase orders, quotes, pricing, shipments, samples, and customer/account follow-up.")
    report.append("- Supported production and vendor operations: barrels, bottling, packaging, labels, inventory, samples, warehouse and logistics coordination.")
    report.append("- Touched finance/compliance workflows: invoices, payments, payroll, inspection/certification, insurance, taxes/audits, and related documentation.")
    report.append("- Acted as an internal router: report review, CRM/OPS references, approvals, document proofing, scheduling, and status updates.")
    report.append("")
    report.append("## Job Description Signals")
    report.append("")
    report.append("- The work pattern looks like a cross-functional operations coordinator role, not a single-department inbox.")
    report.append("- Core duties likely include inbox triage, external communication, internal routing, task follow-up, scheduling, vendor/customer coordination, and proof/document review.")
    report.append("- The role needs authority and tooling to convert emails into tasks with owner, due date, status, source thread, and completion evidence.")
    report.append("- A daily capacity model should reserve explicit time for email handling and separate time for the work created by those emails.")
    report.append("")
    report.append("## Task-Management Recommendations")
    report.append("")
    report.append("- Create standing queues: Events/Tastings, Distributor Orders, Production/Vendors, Finance/Compliance, Internal Systems/Reports, HR/Scheduling, and General Admin.")
    report.append("- For each email-derived item, track: source thread, requester, account/vendor, due date, promised next step, owner, status, and completion evidence.")
    report.append("- Use templates for repeated subjects: event inquiry, PO/order follow-up, sample request, invoice/payment question, inspection/compliance request, and internal approval request.")
    report.append("- Weekly review should focus on unresolved repeated threads, high-volume requesters, and subjects that show many forwards/replies without clear closure.")
    report.append("")
    report.append("## Next Analysis That Makes Sense")
    report.append("")
    report.append("- Full exact month/day-of-week/hour report after local JSON hydration.")
    report.append("- Reply-time/SLA analysis by matching received threads to next sent reply.")
    report.append("- External vs internal split by sender/recipient domain.")
    report.append("- Attachment category audit: invoices, POs, contracts, certificates, label/artwork, reports.")
    report.append("- Body-level action extraction on a reviewed subset only, to avoid over-collecting private content.")
    report.append("- Correlate with OPS/CRM tasks to show which email-derived work became tracked work and which stayed hidden in the inbox.")
    report.append("")
    return "\n".join(report) + "\n"


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root).expanduser().resolve()
    output = pathlib.Path(args.output).expanduser().resolve() if args.output else root / "report.md"
    if args.filenames_only:
        report = build_filename_report(root)
        output.write_text(report, encoding="utf-8")
        if args.html:
            html_path = output.with_suffix(".html")
            html_path.write_text(markdown_to_html(report, "Mark / Re-Distill Email Review"), encoding="utf-8")
            print(f"Wrote {html_path}")
        print(f"Wrote {output}")
        print("Mode: filenames-only")
        return 0
    records, audit = load_records(root, workers=int(args.workers))
    report = build_report(root, records, audit)
    output.write_text(report, encoding="utf-8")
    if args.html:
        html_path = output.with_suffix(".html")
        html_path.write_text(markdown_to_html(report, "Mark / Re-Distill Email Review"), encoding="utf-8")
        print(f"Wrote {html_path}")
    print(f"Wrote {output}")
    print(f"Records: {len(records):,}")
    print(f"Sent: {sum(1 for r in records if r.direction == 'sent'):,}")
    print(f"Received: {sum(1 for r in records if r.direction == 'received'):,}")
    print(f"Audit: missing_json={audit.get('missing_json_for_eml', 0)} missing_eml={audit.get('missing_eml_for_json', 0)} zero_eml={audit.get('zero_byte_eml', 0)} zero_json={audit.get('zero_byte_json', 0)} date_parse_failures={audit.get('date_parse_failures', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
