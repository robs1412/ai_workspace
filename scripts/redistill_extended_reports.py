#!/usr/bin/env python3
"""Build extended reports for the 2026 Re-Distill email export.

This script reads JSON sidecars in bounded subprocess chunks. If Google Drive
File Provider stalls on a sidecar, the chunk is split and the single stuck file
is skipped instead of hanging the whole report.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import email.utils
import json
import os
import pathlib
import re
import subprocess
import sys
from typing import Iterable

import analyze_redistill_email_export as base


DEFAULT_ROOT = pathlib.Path(
    "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill"
)
INTERNAL_DOMAINS = {"kovaldistillery.com", "koval-distillery.com", "kothe-distilling.com"}
DOCUMENT_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Invoices / payments", ("invoice", "payment", "receipt", "statement", "bill", "credit card")),
    ("Purchase orders / orders", ("purchase order", " po ", "order", "orders")),
    ("Contracts / agreements", ("contract", "agreement", "esign", "signature request", "sign")),
    ("Certificates / permits / compliance", ("certificate", "permit", "license", "inspection", "audit", "ttb", "mosa")),
    ("Artwork / labels / proofs", ("artwork", "label", "labels", "proof", "preprint", "design", "drawing")),
    ("Reports / spreadsheets", ("report", "spreadsheet", "forecast", "list", "analytics")),
    ("Shipping docs", ("shipment", "shipping", "tracking", "bol", "packing list", "delivery")),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build extended Re-Distill email reports.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--output", default=None, help="Default: ROOT/report_extended.md")
    parser.add_argument("--chunk-size", type=int, default=750)
    parser.add_argument("--chunk-timeout", type=int, default=30)
    parser.add_argument("--worker", action="store_true")
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


def domains(value: str) -> list[str]:
    found: list[str] = []
    for _name, addr in email.utils.getaddresses([value]):
        if "@" in addr:
            found.append(addr.rsplit("@", 1)[1].lower().strip())
    return found


def addresses(value: str) -> list[str]:
    found: list[str] = []
    for _name, addr in email.utils.getaddresses([value]):
        addr = addr.lower().strip()
        if addr:
            found.append(addr)
    return found


def is_internal_domain(domain: str) -> bool:
    return domain in INTERNAL_DOMAINS or domain.endswith(".kovaldistillery.com")


def scan_jobs(root: pathlib.Path) -> list[tuple[str, str, str]]:
    jobs: list[tuple[str, str, str]] = []
    for year in ("2024", "2025", "2026"):
        for direction in ("sent", "received"):
            folder = root / year / direction
            if not folder.is_dir():
                continue
            with os.scandir(folder) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.endswith(".json"):
                        jobs.append((year, direction, entry.path))
    return jobs


def worker_main() -> int:
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        year, direction, path = line.split("\t", 2)
        p = pathlib.Path(path)
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            print(json.dumps({"error": type(exc).__name__, "path": path}), flush=True)
            continue
        parsed = parse_message_datetime(meta)
        stem_subject = base.subject_from_export_name(p)
        subject = base.normalize_subject(str(meta.get("subject") or stem_subject))
        from_value = str(meta.get("from") or "")
        to_value = str(meta.get("to") or "")
        cc_value = str(meta.get("cc") or "")
        thread_hash = str(meta.get("thread_hash") or "")
        if not thread_hash:
            thread_hash = "subject:" + subject.lower()
        record = {
            "year_bucket": year,
            "direction": direction,
            "path": path,
            "subject": subject,
            "from": from_value,
            "to": to_value,
            "cc": cc_value,
            "from_domains": domains(from_value),
            "to_domains": domains(to_value + ", " + cc_value),
            "from_addresses": addresses(from_value),
            "to_addresses": addresses(to_value + ", " + cc_value),
            "thread_hash": thread_hash,
            "timestamp": parsed.timestamp() if parsed else None,
            "date": parsed.date().isoformat() if parsed else None,
            "month": parsed.strftime("%Y-%m") if parsed else "unknown",
            "weekday": base.DOW[parsed.weekday()] if parsed else "Unknown",
            "hour": parsed.hour if parsed else None,
        }
        print(json.dumps(record, ensure_ascii=False), flush=True)
    return 0


def run_worker_chunk(jobs: list[tuple[str, str, str]], timeout: int) -> tuple[list[dict], list[str], list[str]]:
    payload = "".join("\t".join(job) + "\n" for job in jobs)
    try:
        result = subprocess.run(
            [sys.executable, __file__, "--worker"],
            input=payload,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        if len(jobs) == 1:
            return [], [jobs[0][2]], []
        mid = len(jobs) // 2
        left_records, left_skips, left_errors = run_worker_chunk(jobs[:mid], timeout)
        right_records, right_skips, right_errors = run_worker_chunk(jobs[mid:], timeout)
        return left_records + right_records, left_skips + right_skips, left_errors + right_errors

    records: list[dict] = []
    errors: list[str] = []
    for line in result.stdout.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            errors.append(line[:200])
            continue
        if "error" in row:
            errors.append(f"{row.get('error')} {row.get('path')}")
        else:
            records.append(row)
    if result.stderr.strip():
        errors.append(result.stderr.strip()[:500])
    return records, [], errors


def load_records(root: pathlib.Path, chunk_size: int, timeout: int) -> tuple[list[dict], list[str], list[str]]:
    jobs = scan_jobs(root)
    records: list[dict] = []
    skipped: list[str] = []
    errors: list[str] = []
    for start in range(0, len(jobs), chunk_size):
        chunk_records, chunk_skipped, chunk_errors = run_worker_chunk(jobs[start : start + chunk_size], timeout)
        records.extend(chunk_records)
        skipped.extend(chunk_skipped)
        errors.extend(chunk_errors)
        print(f"processed {min(start + chunk_size, len(jobs))}/{len(jobs)} records={len(records)} skipped={len(skipped)}", file=sys.stderr)
    return records, skipped, errors


def fmt_pct(n: int, d: int) -> str:
    return "0.0%" if d == 0 else f"{(n / d) * 100:.1f}%"


def fmt_hours(hours: float | None) -> str:
    if hours is None:
        return ""
    if hours < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"


def median(values: list[float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    mid = len(values) // 2
    if len(values) % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    idx = min(len(values) - 1, round((len(values) - 1) * p))
    return values[idx]


def table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    return base.table(headers, rows)


def build_report(root: pathlib.Path, records: list[dict], skipped: list[str], errors: list[str]) -> str:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    total = len(records)
    by_month = collections.Counter((r["month"], r["direction"]) for r in records)
    by_weekday = collections.Counter((r["weekday"], r["direction"]) for r in records)
    by_hour = collections.Counter((r["hour"], r["direction"]) for r in records if r["hour"] is not None)
    by_date = collections.Counter((r["date"], r["direction"]) for r in records if r["date"])
    domain_flow = collections.Counter()
    external_sender_domains = collections.Counter()
    external_recipient_domains = collections.Counter()
    document_types = collections.Counter()
    category_by_month = collections.Counter()

    for r in records:
        from_internal = all(is_internal_domain(d) for d in r["from_domains"]) if r["from_domains"] else False
        to_internal = all(is_internal_domain(d) for d in r["to_domains"]) if r["to_domains"] else False
        if r["direction"] == "received":
            if from_internal:
                domain_flow["internal inbound"] += 1
            else:
                domain_flow["external inbound"] += 1
                external_sender_domains.update(d for d in r["from_domains"] if not is_internal_domain(d))
        else:
            if to_internal:
                domain_flow["internal outbound"] += 1
            else:
                domain_flow["external outbound"] += 1
                external_recipient_domains.update(d for d in r["to_domains"] if not is_internal_domain(d))
        hay = f" {r['subject'].lower()} "
        for doc_type, needles in DOCUMENT_RULES:
            if any(n in hay for n in needles):
                document_types[(doc_type, r["direction"])] += 1
                break
        category = base.classify(r["subject"], base.CATEGORY_RULES, "General / mixed administration")
        category_by_month[(r["month"], category)] += 1

    month_rows = []
    for month in sorted({m for m, _d in by_month if m != "unknown"}):
        sent = by_month[(month, "sent")]
        received = by_month[(month, "received")]
        low, mid, high = base.minutes_estimate(sent, received)
        month_rows.append((month, f"{sent:,}", f"{received:,}", f"{sent + received:,}", base.fmt_hours(low), base.fmt_hours(mid), base.fmt_hours(high)))

    weekday_rows = []
    for day in base.DOW:
        sent = by_weekday[(day, "sent")]
        received = by_weekday[(day, "received")]
        weekday_rows.append((day, f"{sent:,}", f"{received:,}", f"{sent + received:,}"))

    hour_rows = []
    for hour in range(24):
        sent = by_hour[(hour, "sent")]
        received = by_hour[(hour, "received")]
        if sent or received:
            hour_rows.append((f"{hour:02d}:00", f"{sent:,}", f"{received:,}", f"{sent + received:,}"))

    daily_rows = []
    for day in sorted({d for d, _dir in by_date}):
        sent = by_date[(day, "sent")]
        received = by_date[(day, "received")]
        low, mid, high = base.minutes_estimate(sent, received)
        daily_rows.append((day, sent, received, sent + received, low, mid, high))
    busiest_rows = [
        (d, f"{s:,}", f"{r:,}", f"{t:,}", base.fmt_hours(low), base.fmt_hours(mid), base.fmt_hours(high))
        for d, s, r, t, low, mid, high in sorted(daily_rows, key=lambda row: row[3], reverse=True)[:30]
    ]

    thread_records = collections.defaultdict(list)
    for r in records:
        if r["timestamp"] is not None:
            thread_records[r["thread_hash"]].append(r)
    reply_hours: list[float] = []
    unreplied_external = 0
    for thread, items in thread_records.items():
        items.sort(key=lambda x: x["timestamp"])
        sent_times = [x["timestamp"] for x in items if x["direction"] == "sent"]
        for item in items:
            if item["direction"] != "received":
                continue
            if all(is_internal_domain(d) for d in item["from_domains"]):
                continue
            later = next((s for s in sent_times if s > item["timestamp"]), None)
            if later is None:
                unreplied_external += 1
            else:
                reply_hours.append((later - item["timestamp"]) / 3600)
    replied = len(reply_hours)
    within_24 = sum(1 for h in reply_hours if h <= 24)
    within_48 = sum(1 for h in reply_hours if h <= 48)
    within_week = sum(1 for h in reply_hours if h <= 168)

    doc_rows = []
    for doc_type in sorted({k[0] for k in document_types}):
        sent = document_types[(doc_type, "sent")]
        received = document_types[(doc_type, "received")]
        doc_rows.append((doc_type, f"{sent:,}", f"{received:,}", f"{sent + received:,}"))
    doc_rows.sort(key=lambda row: int(str(row[3]).replace(",", "")), reverse=True)

    peak_category_rows = []
    for (month, category), count in category_by_month.most_common(60):
        if month != "unknown":
            peak_category_rows.append((month, category, f"{count:,}"))
        if len(peak_category_rows) >= 30:
            break

    report: list[str] = []
    report.append("# Mark / Re-Distill Extended Email Reports")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Run Notes")
    report.append("")
    report.append(f"- JSON metadata records loaded: **{total:,}**")
    report.append(f"- Skipped slow/stalled sidecars: **{len(skipped):,}**")
    report.append(f"- Parse/read errors: **{len(errors):,}**")
    report.append("- OPS/CRM task correlation was intentionally not run because reliable task tracking only started recently for this history.")
    report.append("- Reply timing is approximate. It uses exported thread hashes where present and normalized subject fallback; it does not inspect message bodies.")
    report.append("")
    report.append("## Month Stats")
    report.append("")
    report.append(table(["Month", "Sent", "Received", "Total", "Low time", "Mid time", "High time"], month_rows))
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
    report.append(table(["Date", "Sent", "Received", "Total", "Low time", "Mid time", "High time"], busiest_rows))
    report.append("")
    report.append("## Internal Vs External Flow")
    report.append("")
    flow_total = sum(domain_flow.values())
    report.append(table(["Flow", "Count", "Share"], [(k, f"{v:,}", fmt_pct(v, flow_total)) for k, v in domain_flow.most_common()]))
    report.append("")
    report.append("## Reply-Time Estimate")
    report.append("")
    report.append(table(["Metric", "Value"], [
        ("External received messages with detected later same-thread/subject sent reply", f"{replied:,}"),
        ("External received messages without detected later same-thread/subject sent reply", f"{unreplied_external:,}"),
        ("Median detected reply time", fmt_hours(median(reply_hours))),
        ("90th percentile detected reply time", fmt_hours(percentile(reply_hours, 0.9))),
        ("95th percentile detected reply time", fmt_hours(percentile(reply_hours, 0.95))),
        ("Replied within 24h", f"{within_24:,} ({fmt_pct(within_24, replied)})"),
        ("Replied within 48h", f"{within_48:,} ({fmt_pct(within_48, replied)})"),
        ("Replied within 7d", f"{within_week:,} ({fmt_pct(within_week, replied)})"),
    ]))
    report.append("")
    report.append("## Top External Sender Domains")
    report.append("")
    report.append(table(["Count", "Domain"], [(f"{c:,}", d) for d, c in external_sender_domains.most_common(60)]))
    report.append("")
    report.append("## Top External Recipient Domains")
    report.append("")
    report.append(table(["Count", "Domain"], [(f"{c:,}", d) for d, c in external_recipient_domains.most_common(60)]))
    report.append("")
    report.append("## Document / Attachment-Like Signals")
    report.append("")
    report.append("This uses subject-line signals only. It does not parse attachments from `.eml` bodies.")
    report.append("")
    report.append(table(["Document signal", "Sent", "Received", "Total"], doc_rows))
    report.append("")
    report.append("## Peak Month / Category Combinations")
    report.append("")
    report.append(table(["Month", "Category", "Messages"], peak_category_rows))
    report.append("")
    return "\n".join(report) + "\n"


def main() -> int:
    args = parse_args()
    if args.worker:
        return worker_main()
    root = pathlib.Path(args.root).expanduser().resolve()
    output = pathlib.Path(args.output).expanduser().resolve() if args.output else root / "report_extended.md"
    records, skipped, errors = load_records(root, args.chunk_size, args.chunk_timeout)
    report = build_report(root, records, skipped, errors)
    output.write_text(report, encoding="utf-8")
    html_path = output.with_suffix(".html")
    html_path.write_text(base.markdown_to_html(report, "Mark / Re-Distill Extended Email Reports"), encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Wrote {html_path}")
    print(f"Records={len(records):,} skipped={len(skipped):,} errors={len(errors):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
