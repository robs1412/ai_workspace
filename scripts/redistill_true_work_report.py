#!/usr/bin/env python3
"""Estimate true email work after excluding March/April noise bursts."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import pathlib
import re
import statistics

import analyze_redistill_email_export as base
import redistill_email_quality_report as quality
import redistill_extended_reports as ext
import redistill_job_work_report as job


DEFAULT_ROOT = pathlib.Path(
    "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill"
)

PROMO_SPAM_PATTERNS = (
    "c0stc0",
    "costco",
    "sam's",
    "sams",
    "sam ",
    "tractor-supply",
    "tractor supply",
    "marriott",
    "meat box",
    "35oowatt",
    "3500watt",
    "generator",
    "roadside kit",
    "courtesy road kit",
    "aaa licensed",
    "tool set",
    "tupperware",
    "shopping card",
    "membership balance",
    "membership update",
    "membership expired",
    "welcome token",
    "flight is awaiting",
    "flight booking",
    "harbor freight",
    "ninja creami",
    "gift card",
    "weight loss",
    "home can pay you",
    "home that will pay",
    "package did not arrive",
    "lost your package",
    "fedex delivery",
    "pittsburgh tool",
    "blocked up?",
)

ROUTINE_AUTOMATION_PATTERNS = (
    "approval reminder",
    "delivery status notification",
    "calendar question",
    "accepted:",
    "declined:",
    "task status changed:",
)

SYSTEM_REPORT_PATTERNS = (
    "new report for review:",
    "new report submitted",
    "new report notes added",
    "daily overview",
)

BUSINESS_KEEP_PATTERNS = (
    "koval",
    "tasting",
    "tour",
    "event",
    "private",
    "invoice",
    "purchase order",
    " po ",
    "order",
    "shipment",
    "label",
    "labels",
    "proof",
    "preprint",
    "jas",
    "organic",
    "certification",
    "permit",
    "contract",
    "insurance",
    "tax",
    "visitor request",
    "marketing inquiry",
    "domestic trade credit",
    "credit insurance",
    "rmdc",
    "rndc",
    "sample",
    "production",
    "portal",
    "two-factor",
)

BUSINESS_DOMAINS = {
    "kovaldistillery.com",
    "koval-distillery.com",
    "kothe-distilling.com",
    "kothedistilling.com",
    "rndc-usa.com",
    "chrobinson.com",
    "adobesign.com",
    "google.com",
    "gmail.com",
    "distilledspirits.org",
    "mail.profoodworld.com",
    "go02.informamarkets.com",
    "mail.bidspotter.com",
    "properstonetv.name",
    "shared1.ccsend.com",
}

SUSPICIOUS_TLDS = (".pro", ".name", ".xyz", ".top", ".click", ".shop", ".club", ".live", ".info")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build true-work filtered email report.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-timeout", type=int, default=20)
    return parser.parse_args()


def haystack(subject: str) -> str:
    cleaned = subject.lower()
    cleaned = cleaned.replace("0", "o").replace("1", "l")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return f" {cleaned} "


def has_pattern(subject: str, patterns: tuple[str, ...]) -> bool:
    hay = haystack(subject)
    return any(pattern in hay for pattern in patterns)


def sender_domains(record: dict) -> list[str]:
    if record["direction"] == "received":
        return list(record.get("from_domains", []))
    return list(record.get("to_domains", []))


def suspicious_domain(domain: str) -> bool:
    return domain.endswith(SUSPICIOUS_TLDS)


def keep_reason(record: dict) -> str | None:
    subject = record["subject"]
    domains = sender_domains(record)
    category = job.category_for(record)

    if record["direction"] == "sent":
        return "manual outbound"
    if any(ext.is_internal_domain(domain) for domain in domains):
        return "internal/domain work"
    if has_pattern(subject, BUSINESS_KEEP_PATTERNS):
        return "business subject signal"
    if category != "General / mixed administration" and not has_pattern(subject, PROMO_SPAM_PATTERNS):
        return "business category"
    if any(domain in BUSINESS_DOMAINS for domain in domains):
        return "known business sender"
    return None


def exclude_reason(record: dict) -> str | None:
    subject = record["subject"]
    domains = sender_domains(record)
    if record["direction"] == "sent":
        return None
    if has_pattern(subject, PROMO_SPAM_PATTERNS):
        return "likely spam/promo burst"
    if has_pattern(subject, ROUTINE_AUTOMATION_PATTERNS):
        return "routine automation"
    if has_pattern(subject, SYSTEM_REPORT_PATTERNS):
        return "system report/notification"
    if domains and all(suspicious_domain(domain) for domain in domains) and not has_pattern(subject, BUSINESS_KEEP_PATTERNS):
        return "suspicious sender domain"
    if keep_reason(record) is None:
        return "no clear business signal"
    return None


def classify_true_work(record: dict) -> tuple[bool, str]:
    excluded = exclude_reason(record)
    if excluded:
        return False, excluded
    kept = keep_reason(record)
    if kept:
        return True, kept
    return False, "no clear business signal"


def hours(minutes: float) -> float:
    return round(minutes / 60, 2)


def fmt_hours(value: float) -> str:
    return f"{value:.1f}h"


def avg(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def write_csv(path: pathlib.Path, headers: list[str], rows: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def top_join(counter: collections.Counter[str], limit: int = 5) -> str:
    return "; ".join(f"{name} ({count:,})" for name, count in counter.most_common(limit))


def daily_rows(records: list[dict]) -> tuple[list[tuple[object, ...]], dict[str, list[dict]], dict[str, list[dict]], collections.Counter[str], collections.Counter[str]]:
    thread_sizes = collections.Counter(r["thread_hash"] for r in records)
    all_by_date: dict[str, list[dict]] = collections.defaultdict(list)
    kept_by_date: dict[str, list[dict]] = collections.defaultdict(list)
    excluded_by_date: dict[str, list[dict]] = collections.defaultdict(list)
    exclude_reasons = collections.Counter()
    keep_reasons = collections.Counter()

    for record in records:
        date_key = record.get("date")
        if not date_key or not ("2026-03-01" <= date_key <= "2026-04-30"):
            continue
        if date_key > "2026-04-17":
            continue
        all_by_date[date_key].append(record)
        keep, reason = classify_true_work(record)
        if keep:
            kept_by_date[date_key].append(record)
            keep_reasons[reason] += 1
        else:
            excluded_by_date[date_key].append(record)
            exclude_reasons[reason] += 1

    rows: list[tuple[object, ...]] = []
    for date_key in sorted(all_by_date):
        all_items = all_by_date[date_key]
        kept_items = kept_by_date[date_key]
        excluded_items = excluded_by_date[date_key]
        sent = sum(1 for r in kept_items if r["direction"] == "sent")
        received = sum(1 for r in kept_items if r["direction"] == "received")
        raw_sent = sum(1 for r in all_items if r["direction"] == "sent")
        raw_received = sum(1 for r in all_items if r["direction"] == "received")
        low_m, mid_m, high_m = base.minutes_estimate(sent, received)
        raw_low_m, raw_mid_m, raw_high_m = base.minutes_estimate(raw_sent, raw_received)
        q_minutes = 0.0
        scores: list[float] = []
        high_complexity = 0
        categories = collections.Counter()
        excluded_subjects = collections.Counter()
        kept_subjects = collections.Counter()
        for record in kept_items:
            score, _reasons = quality.quality_score(record, thread_sizes)
            q_minutes += quality.quality_minutes(record, score)
            scores.append(score)
            high_complexity += 1 if quality.tier(score) == "High-quality / high-complexity" else 0
            categories[job.category_for(record)] += 1
            kept_subjects[record["subject"]] += 1
        for record in excluded_items:
            excluded_subjects[record["subject"]] += 1
        rows.append((
            date_key,
            dt.date.fromisoformat(date_key).strftime("%A"),
            raw_sent,
            raw_received,
            raw_sent + raw_received,
            len(excluded_items),
            sent,
            received,
            sent + received,
            hours(raw_mid_m),
            hours(mid_m),
            hours(high_m),
            round(q_minutes / 60, 2),
            round(avg(scores), 2),
            round(median(scores), 2),
            high_complexity,
            top_join(categories, 4),
            top_join(kept_subjects, 4),
            top_join(excluded_subjects, 4),
        ))
    return rows, kept_by_date, excluded_by_date, keep_reasons, exclude_reasons


def period_summary(rows: list[tuple[object, ...]]) -> list[tuple[object, ...]]:
    periods = (
        ("March 1-16 pre-spike", "2026-03-01", "2026-03-16"),
        ("March 17-April 16 raw spike window", "2026-03-17", "2026-04-16"),
        ("April 1-17", "2026-04-01", "2026-04-17"),
    )
    out = []
    for label, start, end in periods:
        selected = [row for row in rows if start <= str(row[0]) <= end]
        if not selected:
            continue
        active_days = len(selected)
        raw_total = sum(int(row[4]) for row in selected)
        excluded = sum(int(row[5]) for row in selected)
        true_total = sum(int(row[8]) for row in selected)
        true_mid = sum(float(row[10]) for row in selected)
        true_high = sum(float(row[11]) for row in selected)
        q_hours = sum(float(row[12]) for row in selected)
        out.append((
            label,
            active_days,
            f"{raw_total:,}",
            f"{excluded:,}",
            f"{true_total:,}",
            f"{true_total / active_days:.1f}",
            fmt_hours(true_mid),
            fmt_hours(true_mid / active_days),
            fmt_hours(true_high / active_days),
            fmt_hours(q_hours / active_days),
        ))
    return out


def build_report(root: pathlib.Path, records: list[dict], skipped: list[str], errors: list[str]) -> tuple[str, list[tuple[object, ...]]]:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    rows, kept_by_date, excluded_by_date, keep_reasons, exclude_reasons = daily_rows(records)
    summary_rows = period_summary(rows)

    category_counter = collections.Counter()
    subject_counter = collections.Counter()
    excluded_subject_counter = collections.Counter()
    for items in kept_by_date.values():
        for record in items:
            category_counter[job.category_for(record)] += 1
            subject_counter[record["subject"]] += 1
    for items in excluded_by_date.values():
        for record in items:
            excluded_subject_counter[record["subject"]] += 1

    category_rows = [(category, f"{count:,}") for category, count in category_counter.most_common()]
    kept_subject_rows = [(f"{count:,}", subject, job.category_for({"subject": subject})) for subject, count in subject_counter.most_common(40)]
    excluded_subject_rows = [(f"{count:,}", subject, job.category_for({"subject": subject})) for subject, count in excluded_subject_counter.most_common(50)]
    keep_reason_rows = [(reason, f"{count:,}") for reason, count in keep_reasons.most_common()]
    exclude_reason_rows = [(reason, f"{count:,}") for reason, count in exclude_reasons.most_common()]

    display_rows = []
    for row in rows:
        display_rows.append((
            row[0],
            row[1],
            f"{row[4]:,}",
            f"{row[5]:,}",
            f"{row[6]:,}",
            f"{row[7]:,}",
            f"{row[8]:,}",
            fmt_hours(float(row[9])),
            fmt_hours(float(row[10])),
            fmt_hours(float(row[11])),
            fmt_hours(float(row[12])),
            row[16],
            row[17],
            row[18],
        ))

    report: list[str] = []
    report.append("# Re-Distill True Work Email Estimate")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Run Notes")
    report.append("")
    report.append(f"- Metadata records loaded: **{len(records):,}**")
    report.append(f"- Skipped slow/stalled sidecars: **{len(skipped):,}**")
    report.append(f"- Parse/read errors: **{len(errors):,}**")
    report.append("- This report keeps the March/April anomaly note from the deep dive, then estimates true work by excluding likely spam/promo bursts, routine automation, system report notifications, suspicious sender-domain bursts, and messages with no clear business signal.")
    report.append("- It is metadata/subject based. It does not read or quote message bodies.")
    report.append("- The filter is intentionally reviewable, not final: false positives are possible, especially for generic Gmail messages and legitimate vendors using marketing platforms.")
    report.append("")
    report.append("## Anomaly Note To Keep In The Main Report")
    report.append("")
    report.append("March/April 2026 contains a real export anomaly or inbound-mail hygiene problem. Raw volume spikes from 72.9 messages/day in the Jan 1-Mar 16 baseline to 368.9 messages/day in Mar 17-Apr 16, mainly from received mail. Many spike subjects/domains look promotional, spam-like, or automated. Raw March/April counts should not be used as normal job workload without filtering.")
    report.append("")
    report.append("## True Work Summary")
    report.append("")
    report.append(base.table(["Period", "Active days", "Raw messages", "Excluded", "True-work messages", "True msgs/day", "True mid hours", "Avg true mid/day", "Avg true high/day", "Avg quality-adjusted/day"], summary_rows))
    report.append("")
    report.append("## Daily True Work Hours")
    report.append("")
    report.append(base.table([
        "Date",
        "Weekday",
        "Raw total",
        "Excluded",
        "True sent",
        "True received",
        "True total",
        "Raw mid hours",
        "True mid hours",
        "True high hours",
        "Quality-adjusted hours",
        "Top true categories",
        "Top true subjects",
        "Top excluded subjects",
    ], display_rows))
    report.append("")
    report.append("## True Work Categories")
    report.append("")
    report.append(base.table(["Category", "True-work messages"], category_rows))
    report.append("")
    report.append("## Top Kept Subject Patterns")
    report.append("")
    report.append(base.table(["Count", "Subject", "Category"], kept_subject_rows))
    report.append("")
    report.append("## Top Excluded Subject Patterns")
    report.append("")
    report.append(base.table(["Count", "Subject", "Category"], excluded_subject_rows))
    report.append("")
    report.append("## Keep / Exclude Reasons")
    report.append("")
    report.append("Kept:")
    report.append("")
    report.append(base.table(["Reason", "Messages"], keep_reason_rows))
    report.append("")
    report.append("Excluded:")
    report.append("")
    report.append(base.table(["Reason", "Messages"], exclude_reason_rows))
    report.append("")
    report.append("## Interpretation")
    report.append("")
    report.append("- After filtering obvious March/April noise, the email workload is much closer to a normal job-planning number than the raw export suggested.")
    report.append("- Your intuition of about 2 hours/day is plausible for a clean true-work inbox on ordinary days. The filtered March 1-16 pre-spike period should be used as the best current sanity check.")
    report.append("- The spike window still has more than 2 hours/day of true-work signal because legitimate KOVAL/internal/vendor/order/event messages are mixed into the noise. That means the right answer is not simply to ignore March/April; it is to separate inbox hygiene from real operational work.")
    report.append("- For staffing and job description purposes, use filtered true-work hours as the baseline, and treat spam/promotional/system bursts as a separate mailbox-management problem.")
    report.append("")
    report.append("## Output Files")
    report.append("")
    report.append("- `report_true_work.html`")
    report.append("- `report_true_work.md`")
    report.append("- `true_work_daily.csv`")
    report.append("")
    return "\n".join(report) + "\n", rows


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root)
    records, skipped, errors = ext.load_records(root, args.chunk_size, args.chunk_timeout)
    report, rows = build_report(root, records, skipped, errors)
    md_path = root / "report_true_work.md"
    html_path = root / "report_true_work.html"
    csv_path = root / "true_work_daily.csv"
    md_path.write_text(report, encoding="utf-8")
    html_path.write_text(base.markdown_to_html(report, "Re-Distill True Work Email Estimate"), encoding="utf-8")
    write_csv(
        csv_path,
        [
            "date",
            "weekday",
            "raw_sent",
            "raw_received",
            "raw_total",
            "excluded",
            "true_sent",
            "true_received",
            "true_total",
            "raw_mid_hours",
            "true_mid_hours",
            "true_high_hours",
            "quality_adjusted_hours",
            "avg_quality_score",
            "median_quality_score",
            "high_complexity",
            "top_true_categories",
            "top_true_subjects",
            "top_excluded_subjects",
        ],
        rows,
    )
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Wrote {csv_path}")
    print(f"Records={len(records):,} skipped={len(skipped):,} errors={len(errors):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
