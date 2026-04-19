#!/usr/bin/env python3
"""Deep-dive March/April 2026 anomalies in the Re-Distill email export."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import pathlib
import statistics

import analyze_redistill_email_export as base
import redistill_email_quality_report as quality
import redistill_extended_reports as ext
import redistill_job_work_report as job


DEFAULT_ROOT = pathlib.Path(
    "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill"
)
TARGET_MONTHS = {"2026-03", "2026-04"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build March/April 2026 deep-dive report.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-timeout", type=int, default=20)
    return parser.parse_args()


def hours(minutes: float) -> float:
    return round(minutes / 60, 2)


def fmt_hours(value: float) -> str:
    return f"{value:.1f}h"


def fmt_pct(n: int, d: int) -> str:
    return "0.0%" if d == 0 else f"{(n / d) * 100:.1f}%"


def avg(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def top_join(counter: collections.Counter[str], limit: int = 5) -> str:
    return "; ".join(f"{name} ({count:,})" for name, count in counter.most_common(limit))


def write_csv(path: pathlib.Path, headers: list[str], rows: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def daily_summary(records: list[dict]) -> tuple[list[tuple[object, ...]], dict[str, dict[str, object]]]:
    by_date: dict[str, list[dict]] = collections.defaultdict(list)
    for record in records:
        if record.get("date") and record.get("month") in TARGET_MONTHS:
            by_date[record["date"]].append(record)

    thread_sizes = collections.Counter(r["thread_hash"] for r in records)
    rows: list[tuple[object, ...]] = []
    details: dict[str, dict[str, object]] = {}
    for date_key in sorted(by_date):
        items = by_date[date_key]
        sent = sum(1 for r in items if r["direction"] == "sent")
        received = sum(1 for r in items if r["direction"] == "received")
        low_m, mid_m, high_m = base.minutes_estimate(sent, received)
        scores: list[float] = []
        q_minutes = 0.0
        high_complexity = 0
        low_complexity = 0
        categories = collections.Counter()
        subjects = collections.Counter()
        inbound_subjects = collections.Counter()
        from_domains = collections.Counter()
        external_inbound = 0
        auto_noise = 0
        long_threads = 0

        for record in items:
            score, reasons = quality.quality_score(record, thread_sizes)
            tier = quality.tier(score)
            scores.append(score)
            q_minutes += quality.quality_minutes(record, score)
            high_complexity += 1 if tier == "High-quality / high-complexity" else 0
            low_complexity += 1 if tier == "Low-complexity / likely routine" else 0
            category = job.category_for(record)
            categories[category] += 1
            subjects[record["subject"]] += 1
            if record["direction"] == "received":
                inbound_subjects[record["subject"]] += 1
                for domain in record.get("from_domains", []):
                    from_domains[domain] += 1
                if quality.external_party(record):
                    external_inbound += 1
            if "automation/noise signal" in reasons:
                auto_noise += 1
            if thread_sizes[record["thread_hash"]] >= 10:
                long_threads += 1

        weekday = dt.date.fromisoformat(date_key).strftime("%A")
        row = (
            date_key,
            weekday,
            sent,
            received,
            sent + received,
            hours(low_m),
            hours(mid_m),
            hours(high_m),
            round(q_minutes / 60, 2),
            round(avg(scores), 2),
            round(median(scores), 2),
            high_complexity,
            low_complexity,
            external_inbound,
            auto_noise,
            long_threads,
            top_join(categories, 4),
            top_join(inbound_subjects, 4),
            top_join(from_domains, 4),
        )
        rows.append(row)
        details[date_key] = {
            "items": items,
            "categories": categories,
            "subjects": subjects,
            "inbound_subjects": inbound_subjects,
            "from_domains": from_domains,
            "external_inbound": external_inbound,
            "auto_noise": auto_noise,
            "long_threads": long_threads,
            "quality_hours": q_minutes / 60,
            "scores": scores,
        }
    return rows, details


def aggregate_period(records: list[dict], period_records: list[dict]) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]], list[tuple[object, ...]]]:
    thread_sizes = collections.Counter(r["thread_hash"] for r in records)
    by_category = collections.Counter()
    by_category_sent = collections.Counter()
    by_category_received = collections.Counter()
    by_subject = collections.Counter()
    by_inbound_subject = collections.Counter()
    by_domain = collections.Counter()
    by_quality_category = collections.defaultdict(float)
    by_high_category = collections.Counter()

    for record in period_records:
        category = job.category_for(record)
        score, _reasons = quality.quality_score(record, thread_sizes)
        by_category[category] += 1
        by_quality_category[category] += score
        by_high_category[category] += 1 if quality.tier(score) == "High-quality / high-complexity" else 0
        if record["direction"] == "sent":
            by_category_sent[category] += 1
        else:
            by_category_received[category] += 1
            by_inbound_subject[record["subject"]] += 1
            for domain in record.get("from_domains", []):
                by_domain[domain] += 1
        by_subject[record["subject"]] += 1

    category_rows = []
    for category, count in by_category.most_common():
        category_rows.append((
            category,
            f"{count:,}",
            f"{by_category_sent[category]:,}",
            f"{by_category_received[category]:,}",
            f"{by_quality_category[category]:,.1f}",
            f"{by_high_category[category]:,}",
        ))

    subject_rows = [(f"{count:,}", subject, job.category_for({"subject": subject})) for subject, count in by_inbound_subject.most_common(40)]
    domain_rows = [(f"{count:,}", domain) for domain, count in by_domain.most_common(40)]
    return category_rows, subject_rows, domain_rows


def compare_baseline(records: list[dict], target_records: list[dict]) -> list[tuple[object, ...]]:
    baseline = [r for r in records if r.get("date") and "2026-01-01" <= r["date"] <= "2026-03-16"]
    rows = []
    for label, items in (("2026-01-01 to 2026-03-16 baseline", baseline), ("2026-03-17 to 2026-04-16 spike", target_records)):
        active_dates = sorted({r["date"] for r in items if r.get("date")})
        sent = sum(1 for r in items if r["direction"] == "sent")
        received = sum(1 for r in items if r["direction"] == "received")
        low_m, mid_m, high_m = base.minutes_estimate(sent, received)
        day_count = len(active_dates)
        rows.append((
            label,
            day_count,
            f"{sent:,}",
            f"{received:,}",
            f"{sent + received:,}",
            f"{(sent + received) / day_count:.1f}" if day_count else "0.0",
            fmt_hours(hours(mid_m)),
            fmt_hours(hours(mid_m) / day_count if day_count else 0.0),
            fmt_hours(hours(high_m) / day_count if day_count else 0.0),
        ))
    return rows


def build_report(root: pathlib.Path, records: list[dict], skipped: list[str], errors: list[str]) -> tuple[str, list[tuple[object, ...]]]:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    daily_rows, details = daily_summary(records)
    period_records = [
        r for r in records
        if r.get("date") and "2026-03-17" <= r["date"] <= "2026-04-16"
    ]
    march_april_records = [r for r in records if r.get("month") in TARGET_MONTHS]
    category_rows, subject_rows, domain_rows = aggregate_period(records, period_records)
    compare_rows = compare_baseline(records, period_records)

    peak_rows = []
    for row in sorted(daily_rows, key=lambda r: int(r[4]), reverse=True)[:15]:
        peak_rows.append((
            row[0],
            row[1],
            f"{row[2]:,}",
            f"{row[3]:,}",
            f"{row[4]:,}",
            fmt_hours(float(row[6])),
            fmt_hours(float(row[7])),
            fmt_hours(float(row[8])),
            f"{row[11]:,}",
            row[16],
            row[17],
            row[18],
        ))

    month_counts = collections.Counter((r["month"], r["direction"]) for r in march_april_records)
    month_rows = []
    for month in sorted(TARGET_MONTHS):
        sent = month_counts[(month, "sent")]
        received = month_counts[(month, "received")]
        low_m, mid_m, high_m = base.minutes_estimate(sent, received)
        month_rows.append((month, f"{sent:,}", f"{received:,}", f"{sent + received:,}", fmt_hours(hours(mid_m)), fmt_hours(hours(high_m))))

    report: list[str] = []
    report.append("# March / April 2026 Re-Distill Email Deep Dive")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Run Notes")
    report.append("")
    report.append(f"- Metadata records loaded: **{len(records):,}**")
    report.append(f"- Skipped slow/stalled sidecars: **{len(skipped):,}**")
    report.append(f"- Parse/read errors: **{len(errors):,}**")
    report.append("- This report focuses on March and April 2026. It uses metadata, subjects, domains, direction, categories, thread depth, and quality scoring; it does not read or quote message bodies.")
    report.append("- Current analysis date is 2026-04-17. The export contains one 2026-04-20 record, which is listed in the daily CSV/report as a future-dated/export-timestamp anomaly rather than treated as normal completed work.")
    report.append("")
    report.append("## What Looks Odd")
    report.append("")
    report.append("- The spike begins around **2026-03-17**. Before that, March looks like a normal heavy business inbox: mostly 60-150 messages per weekday.")
    report.append("- From **2026-03-17 through 2026-04-16**, inbound volume jumps sharply while sent volume stays in a normal range. That means the oddity is mainly incoming mail, not a sudden increase in outbound replies.")
    report.append("- The highest days are concentrated in **2026-03-26 to 2026-03-31** and **2026-04-07 to 2026-04-14**, including weekend spikes. That pattern suggests a burst/import/campaign/reporting/list event or external intake surge, not a steady staffing pattern.")
    report.append("- Even after quality weighting, April remains heavy: high-complexity messages rose, especially around shipping/logistics, finance, compliance, events, and order-related threads.")
    report.append("")
    report.append("## Baseline Versus Spike")
    report.append("")
    report.append(base.table(["Period", "Active days", "Sent", "Received", "Total", "Avg messages/day", "Mid email hours", "Avg mid/day", "Avg high/day"], compare_rows))
    report.append("")
    report.append("## March / April Monthly Totals")
    report.append("")
    report.append(base.table(["Month", "Sent", "Received", "Total", "Mid email hours", "High email hours"], month_rows))
    report.append("")
    report.append("## Peak Daily Hours And Drivers")
    report.append("")
    report.append(base.table(["Date", "Weekday", "Sent", "Received", "Total", "Mid hours", "High hours", "Quality-adjusted hours", "High-complexity", "Top categories", "Top inbound subjects", "Top sender domains"], peak_rows))
    report.append("")
    report.append("## Spike Period Categories")
    report.append("")
    report.append(base.table(["Category", "Messages", "Sent", "Received", "Quality units", "High-complexity"], category_rows))
    report.append("")
    report.append("## Spike Period Inbound Subject Concentration")
    report.append("")
    report.append(base.table(["Received count", "Subject", "Category"], subject_rows))
    report.append("")
    report.append("## Spike Period Sender Domain Concentration")
    report.append("")
    report.append(base.table(["Received count", "Sender domain"], domain_rows))
    report.append("")
    report.append("## Daily Detail")
    report.append("")
    report.append(base.table(
        [
            "Date",
            "Weekday",
            "Sent",
            "Received",
            "Total",
            "Low hours",
            "Mid hours",
            "High hours",
            "Quality-adjusted hours",
            "Avg score",
            "Median score",
            "High-complexity",
            "Low-complexity",
            "External inbound",
            "Automation/noise",
            "Long-thread msgs",
            "Top categories",
            "Top inbound subjects",
            "Top sender domains",
        ],
        daily_rows,
    ))
    report.append("")
    report.append("## Interpretation")
    report.append("")
    report.append("- For daily staffing, use the **mid hours** column for direct email time and the **quality-adjusted hours** column to identify judgment-heavy days.")
    report.append("- The spike should be audited before using March/April as a normal job baseline. The key question is whether the inbound burst is operationally real, automated/reporting noise, a mailbox import/sync artifact, or a campaign/contact-form/listing issue.")
    report.append("- If the inbound subjects/domains are real external work, March/April require temporary triage support. If they are automated/noise/report bursts, the fix is filters, dashboards, batched review, or task conversion rather than more manual inbox time.")
    report.append("- Future-dated or out-of-window records should be checked against export rules and mail client timezone/date handling before drawing daily conclusions for the current week.")
    report.append("")
    report.append("## Output Files")
    report.append("")
    report.append("- `report_march_april_deep_dive.html`")
    report.append("- `report_march_april_deep_dive.md`")
    report.append("- `march_april_daily_deep_dive.csv`")
    report.append("")
    return "\n".join(report) + "\n", daily_rows


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root)
    records, skipped, errors = ext.load_records(root, args.chunk_size, args.chunk_timeout)
    report, daily_rows = build_report(root, records, skipped, errors)
    md_path = root / "report_march_april_deep_dive.md"
    html_path = root / "report_march_april_deep_dive.html"
    csv_path = root / "march_april_daily_deep_dive.csv"
    md_path.write_text(report, encoding="utf-8")
    html_path.write_text(base.markdown_to_html(report, "March / April 2026 Re-Distill Email Deep Dive"), encoding="utf-8")
    write_csv(
        csv_path,
        [
            "date",
            "weekday",
            "sent",
            "received",
            "total",
            "low_hours",
            "mid_hours",
            "high_hours",
            "quality_adjusted_hours",
            "avg_quality_score",
            "median_quality_score",
            "high_complexity",
            "low_complexity",
            "external_inbound",
            "automation_noise",
            "long_thread_messages",
            "top_categories",
            "top_inbound_subjects",
            "top_sender_domains",
        ],
        daily_rows,
    )
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Wrote {csv_path}")
    print(f"Records={len(records):,} skipped={len(skipped):,} errors={len(errors):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
