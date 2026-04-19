#!/usr/bin/env python3
"""Build a quality/complexity report for the Re-Distill email export."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import math
import pathlib
import statistics

import analyze_redistill_email_export as base
import redistill_extended_reports as ext
import redistill_job_work_report as job


DEFAULT_ROOT = pathlib.Path(
    "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill"
)

HIGH_RISK_CATEGORIES = {
    "Compliance / legal / insurance",
    "Finance / accounting / payments",
    "Production / operations",
    "Shipping / logistics",
    "International / export",
}

ACTION_KEYWORDS = (
    "urgent",
    "issue",
    "problem",
    "missing",
    "error",
    "fix",
    "claim",
    "review",
    "approve",
    "approval",
    "proof",
    "draft",
    "final",
    "contract",
    "agreement",
    "permit",
    "license",
    "inspection",
    "audit",
    "invoice",
    "payment",
    "receipt",
    "purchase order",
    " po ",
    "order",
    "shipment",
    "tracking",
    "delivery",
    "schedule",
    "meeting",
    "event",
    "tasting",
    "quote",
    "pricing",
)

AUTOMATION_KEYWORDS = (
    "notification",
    "reminder",
    "report submitted",
    "new report",
    "task status changed",
    "accepted:",
    "declined:",
    "calendar",
    "automated",
    "no-reply",
    "noreply",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build email quality/complexity report.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-timeout", type=int, default=20)
    return parser.parse_args()


def has_any(subject: str, words: tuple[str, ...]) -> bool:
    hay = f" {subject.lower()} "
    return any(word in hay for word in words)


def recipient_count(record: dict) -> int:
    return len(set(record.get("to_addresses", [])))


def external_party(record: dict) -> bool:
    if record["direction"] == "received":
        return any(not ext.is_internal_domain(d) for d in record.get("from_domains", []))
    return any(not ext.is_internal_domain(d) for d in record.get("to_domains", []))


def quality_score(record: dict, thread_sizes: dict[str, int]) -> tuple[float, list[str]]:
    subject = record["subject"]
    category = job.category_for(record)
    score = 1.0
    reasons: list[str] = []

    if record["direction"] == "sent":
        score += 1.0
        reasons.append("manual outbound/follow-up")
    if external_party(record):
        score += 1.5
        reasons.append("external party")
    if category in HIGH_RISK_CATEGORIES:
        score += 1.5
        reasons.append("higher-risk category")
    if has_any(subject, ACTION_KEYWORDS):
        score += 1.5
        reasons.append("action/decision signal")
    if has_any(subject, AUTOMATION_KEYWORDS):
        score -= 0.8
        reasons.append("automation/noise signal")

    rcpt_count = recipient_count(record)
    if rcpt_count >= 5:
        score += 1.0
        reasons.append("many recipients")
    elif rcpt_count >= 3:
        score += 0.5
        reasons.append("multiple recipients")

    thread_size = thread_sizes.get(record["thread_hash"], 1)
    if thread_size >= 10:
        score += 1.5
        reasons.append("long thread")
    elif thread_size >= 4:
        score += 0.8
        reasons.append("multi-message thread")

    return max(0.3, round(score, 2)), reasons


def tier(score: float) -> str:
    if score >= 5.5:
        return "High-quality / high-complexity"
    if score >= 3.5:
        return "Medium-quality / actionable"
    return "Low-complexity / likely routine"


def fmt_hours(value: float) -> str:
    return f"{value:.1f}h"


def fmt_units(value: float) -> str:
    return f"{value:,.1f}"


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, round((len(values) - 1) * p))
    return values[idx]


def quality_minutes(record: dict, score: float) -> float:
    received_base = 1.5
    sent_base = 5.0
    base_minutes = sent_base if record["direction"] == "sent" else received_base
    return base_minutes * (0.65 + 0.18 * score)


def build_report(root: pathlib.Path, records: list[dict], skipped: list[str], errors: list[str]) -> str:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    thread_sizes = collections.Counter(r["thread_hash"] for r in records)

    scored: list[tuple[dict, float, list[str]]] = []
    for record in records:
        score, reasons = quality_score(record, thread_sizes)
        scored.append((record, score, reasons))

    by_tier = collections.Counter()
    by_month = collections.defaultdict(lambda: collections.Counter())
    by_category = collections.defaultdict(lambda: collections.Counter())
    score_by_month: dict[str, list[float]] = collections.defaultdict(list)
    score_by_category: dict[str, list[float]] = collections.defaultdict(list)
    examples_by_tier: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    reason_counts = collections.Counter()

    for record, score, reasons in scored:
        category = job.category_for(record)
        label = tier(score)
        minutes = quality_minutes(record, score)
        by_tier[label] += 1
        by_tier[(label, "minutes")] += minutes
        by_month[record["month"]]["count"] += 1
        by_month[record["month"]]["quality_units"] += score
        by_month[record["month"]]["quality_minutes"] += minutes
        by_month[record["month"]][label] += 1
        by_category[category]["count"] += 1
        by_category[category]["quality_units"] += score
        by_category[category]["quality_minutes"] += minutes
        by_category[category][label] += 1
        score_by_month[record["month"]].append(score)
        score_by_category[category].append(score)
        examples_by_tier[label][record["subject"]] += 1
        for reason in reasons:
            reason_counts[reason] += 1

    tier_rows = []
    for label in ("High-quality / high-complexity", "Medium-quality / actionable", "Low-complexity / likely routine"):
        count = int(by_tier[label])
        tier_rows.append((
            label,
            f"{count:,}",
            f"{(count / len(records)) * 100:.1f}%" if records else "0.0%",
            fmt_hours(by_tier[(label, "minutes")] / 60),
            "; ".join(subject for subject, _count in examples_by_tier[label].most_common(5)),
        ))

    month_rows = []
    for month in sorted(m for m in by_month if m != "unknown"):
        counter = by_month[month]
        count = int(counter["count"])
        month_rows.append((
            month,
            f"{count:,}",
            fmt_units(counter["quality_units"]),
            f"{counter['quality_units'] / count:.2f}" if count else "0.00",
            f"{median(score_by_month[month]):.2f}",
            f"{percentile(score_by_month[month], 0.90):.2f}",
            fmt_hours(counter["quality_minutes"] / 60),
            f"{int(counter['High-quality / high-complexity']):,}",
        ))

    category_rows = []
    for category, counter in sorted(by_category.items(), key=lambda item: item[1]["quality_units"], reverse=True):
        count = int(counter["count"])
        category_rows.append((
            category,
            f"{count:,}",
            fmt_units(counter["quality_units"]),
            f"{counter['quality_units'] / count:.2f}" if count else "0.00",
            f"{median(score_by_category[category]):.2f}",
            f"{percentile(score_by_category[category], 0.90):.2f}",
            fmt_hours(counter["quality_minutes"] / 60),
            f"{int(counter['High-quality / high-complexity']):,}",
            f"{int(counter['Low-complexity / likely routine']):,}",
        ))

    reason_rows = [(reason, f"{count:,}") for reason, count in reason_counts.most_common()]

    high_subject_rows = []
    high_records = sorted(scored, key=lambda item: (item[1], thread_sizes[item[0]["thread_hash"]]), reverse=True)
    seen_subjects: set[str] = set()
    for record, score, reasons in high_records:
        subject = record["subject"]
        if subject in seen_subjects:
            continue
        seen_subjects.add(subject)
        high_subject_rows.append((
            f"{score:.2f}",
            job.category_for(record),
            record["direction"],
            str(thread_sizes[record["thread_hash"]]),
            subject,
            ", ".join(reasons[:5]),
        ))
        if len(high_subject_rows) >= 50:
            break

    automation_rows = []
    auto_subjects = collections.Counter()
    for record, score, reasons in scored:
        if "automation/noise signal" in reasons:
            auto_subjects[record["subject"]] += 1
    for subject, count in auto_subjects.most_common(40):
        automation_rows.append((f"{count:,}", subject, job.category_for({"subject": subject})))

    report: list[str] = []
    report.append("# Mark / Re-Distill Email Quality Report")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Run Notes")
    report.append("")
    report.append(f"- Metadata records loaded: **{len(records):,}**")
    report.append(f"- Skipped slow/stalled sidecars: **{len(skipped):,}**")
    report.append(f"- Parse/read errors: **{len(errors):,}**")
    report.append("- March and April 2026 are included.")
    report.append("- This report scores email quality/complexity from metadata, subjects, direction, recipients, domains, categories, and thread depth. It does not read, quote, or summarize private message bodies.")
    report.append("")
    report.append("## Answer")
    report.append("")
    report.append("The earlier workload reports counted messages and estimated time, but only partly considered quality. This report adds a quality-weighted view: external, manual, high-risk, action-heavy, multi-recipient, and long-thread messages count more than routine notifications or repeated automated messages.")
    report.append("")
    report.append("## Quality Tiers")
    report.append("")
    report.append(base.table(["Tier", "Messages", "Share", "Quality-adjusted email hours", "Common examples"], tier_rows))
    report.append("")
    report.append("## Month Quality Trend")
    report.append("")
    report.append(base.table(["Month", "Messages", "Quality units", "Avg score", "Median score", "P90 score", "Quality-adjusted hours", "High-complexity messages"], month_rows))
    report.append("")
    report.append("## Category Quality Weight")
    report.append("")
    report.append(base.table(["Category", "Messages", "Quality units", "Avg score", "Median score", "P90 score", "Quality-adjusted hours", "High-complexity", "Low-complexity"], category_rows))
    report.append("")
    report.append("## Score Drivers")
    report.append("")
    report.append(base.table(["Signal", "Messages affected"], reason_rows))
    report.append("")
    report.append("## Highest-Complexity Subject Patterns")
    report.append("")
    report.append("These are subject-level patterns, not message-body summaries. They are useful for deciding which work requires judgment, escalation rules, or a backup owner.")
    report.append("")
    report.append(base.table(["Score", "Category", "Direction", "Thread messages", "Subject", "Score reasons"], high_subject_rows))
    report.append("")
    report.append("## Automation / Routine Noise Candidates")
    report.append("")
    report.append("These patterns may still matter, but they are candidates for dashboards, filters, automatic task creation, or batched review instead of interrupt-driven manual email handling.")
    report.append("")
    report.append(base.table(["Count", "Subject", "Category"], automation_rows))
    report.append("")
    report.append("## Management Interpretation")
    report.append("")
    report.append("- Count understates the load when messages involve external parties, decisions, documents, legal/finance/compliance risk, production blockers, or long threads.")
    report.append("- Count overstates the load when messages are routine notifications, report alerts, calendar notices, or repeated low-decision updates.")
    report.append("- For job design, use both raw volume and quality-weighted load: raw count determines triage capacity; quality score determines who must handle the work and what SLA is realistic.")
    report.append("- High-complexity categories should have named backup owners and escalation paths. Low-complexity routine patterns should be templated, filtered, or converted to task/dashboard workflows.")
    report.append("- March/April 2026 should be treated as a qualitative workload spike, not only a volume spike, because the period contains high inbound volume plus many external/actionable/document-heavy threads.")
    report.append("")
    return "\n".join(report) + "\n"


def write_html(md_path: pathlib.Path, md_text: str) -> pathlib.Path:
    html_path = md_path.with_suffix(".html")
    html_path.write_text(base.markdown_to_html(md_text, "Mark / Re-Distill Email Quality Report"), encoding="utf-8")
    return html_path


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root)
    records, skipped, errors = ext.load_records(root, args.chunk_size, args.chunk_timeout)
    md_text = build_report(root, records, skipped, errors)
    md_path = root / "report_email_quality.md"
    md_path.write_text(md_text, encoding="utf-8")
    html_path = write_html(md_path, md_text)
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Records={len(records):,} skipped={len(skipped):,} errors={len(errors):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
