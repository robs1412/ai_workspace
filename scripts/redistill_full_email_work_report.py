#!/usr/bin/env python3
"""Full-body March/April 2026 true-work report for Re-Distill emails."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
from email import policy
from email.parser import BytesParser
import html
import os
import pathlib
import re
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import analyze_redistill_email_export as base
import redistill_extended_reports as ext
import redistill_job_work_report as job
import redistill_true_work_report as truework


DEFAULT_ROOT = pathlib.Path(
    "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill"
)

DEFAULT_START_DATE = "2025-01-01"
DEFAULT_END_DATE = "2025-12-31"

THANK_ACK_PATTERNS = (
    "thank you",
    "thanks",
    "thank-you",
    "thx",
    "got it",
    "received",
    "sounds good",
    "ok",
    "okay",
    "perfect",
    "will do",
    "no problem",
    "you're welcome",
    "you are welcome",
    "much appreciated",
)

ACTION_PATTERNS = (
    "please",
    "can you",
    "could you",
    "need",
    "needs",
    "review",
    "approve",
    "approval",
    "send",
    "schedule",
    "confirm",
    "question",
    "issue",
    "problem",
    "urgent",
    "deadline",
    "invoice",
    "payment",
    "order",
    "purchase order",
    "shipment",
    "permit",
    "contract",
    "label",
    "proof",
    "attached",
    "attachment",
    "quote",
    "proposal",
)

PROMO_BODY_PATTERNS = truework.PROMO_SPAM_PATTERNS + (
    "unsubscribe",
    "special offer",
    "limited time",
    "claim your",
    "you were selected",
    "act now",
    "click here",
    "congratulations",
    "complimentary",
    "reward",
    "membership reward",
)

BODY_KEEP_PATTERNS = truework.BUSINESS_KEEP_PATTERNS + (
    "attached",
    "proposal",
    "quote",
    "sku",
    "warehouse",
    "barrel",
    "bottling",
    "production",
    "compliance",
    "distillery",
    "distributor",
    "customer",
    "calendar",
    "availability",
    "reservation",
    "classroom",
    "tasting room",
)

HIGH_RISK_CATEGORIES = {
    "Compliance / legal / insurance",
    "Finance / accounting / payments",
    "Production / operations",
    "Shipping / logistics",
    "International / export",
}

MAX_EML_TEXT_BYTES = 1_500_000

QUOTE_BOUNDARY_RE = re.compile(
    r"^\s*(on .+ wrote:|from:|sent:|to:|subject:|-----original message-----|_{5,}|>{1,})",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build full-body true-work weekly report.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--start", default=DEFAULT_START_DATE)
    parser.add_argument("--end", default=DEFAULT_END_DATE)
    parser.add_argument("--output-prefix", default="full_email_work_2025")
    parser.add_argument("--body-workers", type=int, default=16)
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-timeout", type=int, default=20)
    return parser.parse_args()


def clean_html(value: str) -> str:
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    value = re.sub(r"(?is)<br\s*/?>", "\n", value)
    value = re.sub(r"(?is)</p\s*>", "\n", value)
    value = re.sub(r"(?is)<.*?>", " ", value)
    return html.unescape(value)


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def strip_quoted(text: str) -> str:
    kept: list[str] = []
    for line in text.splitlines():
        if QUOTE_BOUNDARY_RE.match(line):
            break
        kept.append(line)
    fresh = "\n".join(kept).strip()
    fresh = re.split(r"(?i)\n\s*(best|regards|sincerely|cheers|thank you),?\s*\n", fresh, maxsplit=1)[0].strip()
    return normalize_text(fresh)


def body_from_eml(path: pathlib.Path) -> tuple[str, str | None]:
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            if size > MAX_EML_TEXT_BYTES:
                raw = handle.read(MAX_EML_TEXT_BYTES)
                truncated = True
            else:
                raw = handle.read()
                truncated = False
        msg = BytesParser(policy=policy.default).parsebytes(raw)
    except Exception as exc:
        return "", type(exc).__name__

    parts: list[str] = []
    if msg.is_multipart():
        plain = msg.get_body(preferencelist=("plain",))
        if plain is not None:
            try:
                parts.append(plain.get_content())
            except Exception:
                pass
        if not parts:
            html_part = msg.get_body(preferencelist=("html",))
            if html_part is not None:
                try:
                    parts.append(clean_html(html_part.get_content()))
                except Exception:
                    pass
        if not parts:
            for part in msg.walk():
                if part.get_content_maintype() == "text":
                    try:
                        value = part.get_content()
                    except Exception:
                        continue
                    if part.get_content_subtype() == "html":
                        value = clean_html(value)
                    parts.append(value)
    else:
        try:
            value = msg.get_content()
            if msg.get_content_subtype() == "html":
                value = clean_html(value)
            parts.append(value)
        except Exception as exc:
            return "", type(exc).__name__

    full = normalize_text("\n\n".join(parts))
    note = "truncated_large_eml" if truncated else None
    return strip_quoted(full), note


def words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9][a-zA-Z0-9'/-]*", text.lower())


def contains(text: str, patterns: Iterable[str]) -> bool:
    hay = " " + text.lower().replace("0", "o").replace("1", "l") + " "
    return any(pattern in hay for pattern in patterns)


def sent_is_reply(record: dict, thread_records: dict[str, list[dict]]) -> bool:
    if record["direction"] != "sent" or record.get("timestamp") is None:
        return False
    for other in thread_records.get(record["thread_hash"], []):
        if other["direction"] == "received" and other.get("timestamp") is not None and other["timestamp"] < record["timestamp"]:
            return True
    return False


def domain_signal(record: dict) -> str:
    domains = truework.sender_domains(record)
    if any(ext.is_internal_domain(domain) for domain in domains):
        return "internal"
    if any(domain in truework.BUSINESS_DOMAINS for domain in domains):
        return "known_business"
    if domains and all(truework.suspicious_domain(domain) for domain in domains):
        return "suspicious"
    return "external"


def classify_body(record: dict, body: str, reply: bool) -> tuple[str, str, float]:
    subject = record["subject"]
    combined = f"{subject}\n{body}"
    word_count = len(words(body))
    category = job.category_for(record)
    domain = domain_signal(record)
    true_keep, metadata_reason = truework.classify_true_work(record)

    is_ack = (
        word_count <= 35
        and contains(combined, THANK_ACK_PATTERNS)
        and not contains(combined, ACTION_PATTERNS)
    )
    if is_ack:
        return "tiny acknowledgment / thank-you", "body acknowledgment", 10 / 60

    if record["direction"] == "received":
        if contains(combined, PROMO_BODY_PATTERNS) and not contains(combined, BODY_KEEP_PATTERNS):
            return "excluded noise/spam/promo", "body promotional/noise", 0.0
        if domain == "suspicious" and not contains(combined, BODY_KEEP_PATTERNS):
            return "excluded noise/spam/promo", "suspicious sender/body", 0.0
        if not true_keep and not contains(combined, BODY_KEEP_PATTERNS):
            return "excluded non-work", metadata_reason, 0.0
        if contains(combined, ACTION_PATTERNS):
            if word_count > 180 or category in HIGH_RISK_CATEGORIES:
                return "actionable incoming", "body action request", 1.75
            return "actionable incoming", "body action request", 1.25
        if word_count <= 45:
            return "simple incoming", "short business message", 0.5
        return "review/read incoming", "business message review", 0.9

    if contains(combined, PROMO_BODY_PATTERNS) and not contains(combined, BODY_KEEP_PATTERNS):
        return "excluded sent noise/unsubscribe", "sent promo/noise handling", 0.0
    if not true_keep and not contains(combined, BODY_KEEP_PATTERNS):
        return "excluded sent non-work", metadata_reason, 0.0
    if word_count <= 20 and not contains(combined, ACTION_PATTERNS):
        return "tiny acknowledgment / thank-you", "short sent response", 10 / 60
    if reply:
        if word_count <= 60:
            return "simple sent reply", "short reply", 1.25
        if contains(combined, ACTION_PATTERNS) or word_count > 180:
            return "substantive sent reply", "body substantive reply", 4.0
        return "normal sent reply", "reply", 2.25
    if word_count <= 80:
        return "simple outbound", "short outbound", 1.5
    return "substantive outbound", "body substantive outbound", 4.0


def week_start(date_key: str) -> dt.date:
    date_obj = dt.date.fromisoformat(date_key)
    return date_obj - dt.timedelta(days=date_obj.weekday())


def fmt_hours(value: float) -> str:
    return f"{value:.2f}h"


def top_join(counter: collections.Counter[str], limit: int = 5) -> str:
    return "; ".join(f"{name} ({count:,})" for name, count in counter.most_common(limit))


def write_csv(path: pathlib.Path, headers: list[str], rows: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def build_report(root: pathlib.Path, records: list[dict], skipped: list[str], errors: list[str], start_date: str, end_date: str, body_workers: int) -> tuple[str, list[tuple[object, ...]], list[tuple[object, ...]]]:
    target = [
        record for record in records
        if record.get("date") and start_date <= record["date"] <= end_date
    ]
    thread_records: dict[str, list[dict]] = collections.defaultdict(list)
    for record in records:
        if record.get("timestamp") is not None:
            thread_records[record["thread_hash"]].append(record)
    for items in thread_records.values():
        items.sort(key=lambda r: r["timestamp"])

    def process_record(record: dict) -> dict:
        eml_path = pathlib.Path(record["path"]).with_suffix(".eml")
        body, err = body_from_eml(eml_path)
        reply = sent_is_reply(record, thread_records)
        bucket, reason, minutes = classify_body(record, body, reply)
        return {
            "record": record,
            "body_words": len(words(body)),
            "reply": reply,
            "bucket": bucket,
            "reason": reason,
            "minutes": minutes,
            "error": err,
        }

    body_errors = collections.Counter()
    classified: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, body_workers)) as executor:
        futures = [executor.submit(process_record, record) for record in target]
        for idx, future in enumerate(as_completed(futures), 1):
            item = future.result()
            classified.append(item)
            if item["error"]:
                body_errors[item["error"]] += 1
            if idx % 500 == 0:
                print(f"body processed {idx}/{len(target)}", flush=True)

    by_date: dict[str, list[dict]] = collections.defaultdict(list)
    by_week: dict[dt.date, list[dict]] = collections.defaultdict(list)
    for item in classified:
        date_key = item["record"]["date"]
        by_date[date_key].append(item)
        by_week[week_start(date_key)].append(item)

    daily_rows: list[tuple[object, ...]] = []
    for date_key in sorted(by_date):
        items = by_date[date_key]
        raw = len(items)
        excluded = sum(1 for item in items if item["minutes"] == 0)
        incoming = sum(1 for item in items if item["record"]["direction"] == "received" and item["minutes"] > 0)
        sent_replies = sum(1 for item in items if item["record"]["direction"] == "sent" and item["reply"] and item["minutes"] > 0)
        sent_other = sum(1 for item in items if item["record"]["direction"] == "sent" and not item["reply"] and item["minutes"] > 0)
        ack = sum(1 for item in items if item["bucket"] == "tiny acknowledgment / thank-you")
        minutes = sum(item["minutes"] for item in items)
        buckets = collections.Counter(item["bucket"] for item in items)
        subjects = collections.Counter(item["record"]["subject"] for item in items if item["minutes"] > 0)
        excluded_subjects = collections.Counter(item["record"]["subject"] for item in items if item["minutes"] == 0)
        daily_rows.append((
            date_key,
            dt.date.fromisoformat(date_key).strftime("%A"),
            raw,
            excluded,
            incoming,
            sent_replies,
            sent_other,
            ack,
            round(minutes / 60, 2),
            top_join(buckets, 5),
            top_join(subjects, 4),
            top_join(excluded_subjects, 4),
        ))

    weekly_rows: list[tuple[object, ...]] = []
    for start in sorted(by_week):
        items = by_week[start]
        end = start + dt.timedelta(days=6)
        active_dates = sorted({item["record"]["date"] for item in items})
        raw = len(items)
        excluded = sum(1 for item in items if item["minutes"] == 0)
        incoming = sum(1 for item in items if item["record"]["direction"] == "received" and item["minutes"] > 0)
        sent_replies = sum(1 for item in items if item["record"]["direction"] == "sent" and item["reply"] and item["minutes"] > 0)
        sent_other = sum(1 for item in items if item["record"]["direction"] == "sent" and not item["reply"] and item["minutes"] > 0)
        ack = sum(1 for item in items if item["bucket"] == "tiny acknowledgment / thank-you")
        minutes = sum(item["minutes"] for item in items)
        weekday_count = sum(1 for i in range(7) if (start + dt.timedelta(days=i)).isoformat() in active_dates and (start + dt.timedelta(days=i)).weekday() < 5)
        calendar_days_present = len(active_dates)
        divisor = calendar_days_present or 1
        buckets = collections.Counter(item["bucket"] for item in items)
        weekly_rows.append((
            f"{start.isoformat()} to {end.isoformat()}",
            f"{start.isocalendar().year}-W{start.isocalendar().week:02d}",
            calendar_days_present,
            weekday_count,
            raw,
            excluded,
            incoming,
            sent_replies,
            sent_other,
            ack,
            round(minutes / 60, 2),
            round((minutes / 60) / divisor, 2),
            round((minutes / 60) / max(1, weekday_count), 2),
            top_join(buckets, 5),
        ))

    bucket_rows = []
    bucket_counts = collections.Counter(item["bucket"] for item in classified)
    bucket_minutes = collections.Counter()
    for item in classified:
        bucket_minutes[item["bucket"]] += item["minutes"]
    for bucket, count in bucket_counts.most_common():
        bucket_rows.append((bucket, f"{count:,}", fmt_hours(bucket_minutes[bucket] / 60)))

    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    report: list[str] = []
    report.append("# Re-Distill Full-Email Work Report")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Run Notes")
    report.append("")
    report.append(f"- Metadata records loaded: **{len(records):,}**")
    report.append(f"- Date range: **{start_date} to {end_date}**")
    report.append(f"- Full `.eml` messages read for selected range: **{len(target):,}**")
    report.append(f"- Body extraction workers: **{body_workers}**")
    report.append(f"- Skipped slow/stalled sidecars: **{len(skipped):,}**")
    report.append(f"- Parse/read errors from metadata: **{len(errors):,}**")
    truncated_count = body_errors.pop("truncated_large_eml", 0)
    report.append(f"- Large `.eml` files read in text-only truncated mode: **{truncated_count:,}**")
    report.append(f"- Body parse errors: **{sum(body_errors.values()):,}**")
    report.append("- This version reads the actual current message body text to classify acknowledgments, replies, action requests, promotional/noise mail, and substantive work. Attachments are not decoded as email-work text.")
    report.append("- It does not quote private message bodies. Subject patterns are shown only to make the classification auditable.")
    report.append("- Short acknowledgment/thank-you style messages are counted at **10 seconds**.")
    report.append("")
    report.append("## Method")
    report.append("")
    report.append("- Parse each `.eml` file in the selected date range.")
    report.append("- Extract the current message body, stripping quoted prior thread text where detectable.")
    report.append("- Classify true work from body text plus metadata: incoming work, sent replies, substantive outbound work, tiny acknowledgments, automation, spam/promo, and non-work.")
    report.append("- Estimate time from body-level class rather than raw count. Promotional/spam/non-work is zeroed for job-work purposes; acknowledgments are 10 seconds.")
    report.append("- Group results by ISO calendar week and by day.")
    report.append("")
    report.append("## Weekly Calendar Averages")
    report.append("")
    report.append(base.table([
        "Calendar week",
        "ISO week",
        "Calendar days present",
        "Weekdays present",
        "Raw msgs",
        "Excluded",
        "Incoming work",
        "Sent replies",
        "Other sent",
        "Tiny thanks/acks",
        "Total hours",
        "Avg hours/calendar day",
        "Avg hours/weekday",
        "Top body classes",
    ], weekly_rows))
    report.append("")
    report.append("## Daily Body-Based Hours")
    report.append("")
    report.append(base.table([
        "Date",
        "Weekday",
        "Raw msgs",
        "Excluded",
        "Incoming work",
        "Sent replies",
        "Other sent",
        "Tiny thanks/acks",
        "Body-based hours",
        "Top body classes",
        "Top counted subjects",
        "Top excluded subjects",
    ], daily_rows))
    report.append("")
    report.append("## Body Classification Totals")
    report.append("")
    report.append(base.table(["Class", "Messages", "Hours"], bucket_rows))
    report.append("")
    report.append("## Interpretation")
    report.append("")
    report.append("- The raw March/April spike is still real as an inbox hygiene problem, but the full-body work estimate is much lower than the count-based estimate.")
    report.append("- Acknowledgments and thank-you messages are no longer treated as multi-minute work.")
    report.append("- Use the weekly average table for job planning. Use the daily table to spot unusual days where real incoming work or replies were actually high.")
    report.append("")
    report.append("## Output Files")
    report.append("")
    report.append("- Markdown report, HTML report, daily CSV, and weekly CSV using the selected output prefix.")
    report.append("")
    return "\n".join(report) + "\n", daily_rows, weekly_rows


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root)
    records, skipped, errors = ext.load_records(root, args.chunk_size, args.chunk_timeout)
    report, daily_rows, weekly_rows = build_report(root, records, skipped, errors, args.start, args.end, args.body_workers)
    prefix = args.output_prefix
    md_path = root / f"report_{prefix}.md"
    html_path = root / f"report_{prefix}.html"
    daily_path = root / f"{prefix}_daily.csv"
    weekly_path = root / f"{prefix}_weekly.csv"
    md_path.write_text(report, encoding="utf-8")
    html_path.write_text(base.markdown_to_html(report, "Re-Distill Full-Email Work Report"), encoding="utf-8")
    write_csv(daily_path, [
        "date",
        "weekday",
        "raw_messages",
        "excluded",
        "incoming_work",
        "sent_replies",
        "other_sent",
        "tiny_thanks_acks",
        "body_based_hours",
        "top_body_classes",
        "top_counted_subjects",
        "top_excluded_subjects",
    ], daily_rows)
    write_csv(weekly_path, [
        "calendar_week",
        "iso_week",
        "calendar_days_present",
        "weekdays_present",
        "raw_messages",
        "excluded",
        "incoming_work",
        "sent_replies",
        "other_sent",
        "tiny_thanks_acks",
        "total_hours",
        "avg_hours_per_calendar_day",
        "avg_hours_per_weekday",
        "top_body_classes",
    ], weekly_rows)
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Wrote {daily_path}")
    print(f"Wrote {weekly_path}")
    print(f"Records={len(records):,} skipped={len(skipped):,} errors={len(errors):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
