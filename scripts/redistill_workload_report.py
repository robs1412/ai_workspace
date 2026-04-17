#!/usr/bin/env python3
"""Generate email workload planning reports from the Re-Distill export."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import pathlib
import statistics
from typing import Iterable

import analyze_redistill_email_export as base
import redistill_extended_reports as ext


DEFAULT_ROOT = pathlib.Path(
    "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Re-Distill email workload reports.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-timeout", type=int, default=20)
    return parser.parse_args()


def hours(minutes: float) -> float:
    return round(minutes / 60, 2)


def fmt_hours(value: float) -> str:
    return f"{value:.1f}h"


def avg(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, round((len(values) - 1) * p))
    return values[idx]


def write_csv(path: pathlib.Path, headers: list[str], rows: Iterable[Iterable[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def build_workload(root: pathlib.Path, records: list[dict], skipped: list[str], errors: list[str]) -> str:
    by_date = collections.Counter((r["date"], r["direction"]) for r in records if r.get("date"))
    by_month = collections.Counter((r["month"], r["direction"]) for r in records if r.get("month") != "unknown")
    by_year = collections.Counter((str(r["date"])[:4], r["direction"]) for r in records if r.get("date"))
    dates = sorted({d for d, _direction in by_date})
    months = sorted({m for m, _direction in by_month})
    years = sorted({y for y, _direction in by_year})

    daily_rows = []
    weekday_values: dict[str, list[tuple[int, int, int, float, float, float]]] = collections.defaultdict(list)
    month_day_hours: dict[str, list[float]] = collections.defaultdict(list)
    year_day_hours: dict[str, list[float]] = collections.defaultdict(list)

    for date_key in dates:
        sent = by_date[(date_key, "sent")]
        received = by_date[(date_key, "received")]
        total = sent + received
        low_m, mid_m, high_m = base.minutes_estimate(sent, received)
        low_h, mid_h, high_h = hours(low_m), hours(mid_m), hours(high_m)
        weekday = dt.date.fromisoformat(date_key).strftime("%A")
        month = date_key[:7]
        year = date_key[:4]
        daily_rows.append((date_key, weekday, sent, received, total, low_h, mid_h, high_h))
        weekday_values[weekday].append((sent, received, total, low_h, mid_h, high_h))
        month_day_hours[month].append(mid_h)
        year_day_hours[year].append(mid_h)

    monthly_rows = []
    for month in months:
        sent = by_month[(month, "sent")]
        received = by_month[(month, "received")]
        total = sent + received
        low_m, mid_m, high_m = base.minutes_estimate(sent, received)
        day_values = month_day_hours.get(month, [])
        active_days = len(day_values)
        monthly_rows.append((
            month,
            active_days,
            sent,
            received,
            total,
            round(total / active_days, 1) if active_days else 0,
            hours(low_m),
            hours(mid_m),
            hours(high_m),
            round(avg(day_values), 2),
            round(median(day_values), 2),
            round(percentile(day_values, 0.9), 2),
        ))

    yearly_rows = []
    for year in years:
        sent = by_year[(year, "sent")]
        received = by_year[(year, "received")]
        total = sent + received
        low_m, mid_m, high_m = base.minutes_estimate(sent, received)
        day_values = year_day_hours.get(year, [])
        active_days = len(day_values)
        yearly_rows.append((
            year,
            active_days,
            sent,
            received,
            total,
            round(total / active_days, 1) if active_days else 0,
            hours(low_m),
            hours(mid_m),
            hours(high_m),
            round(avg(day_values), 2),
            round(median(day_values), 2),
            round(percentile(day_values, 0.9), 2),
        ))

    weekday_rows = []
    for weekday in base.DOW:
        values = weekday_values.get(weekday, [])
        sent = sum(v[0] for v in values)
        received = sum(v[1] for v in values)
        total = sent + received
        mid_values = [v[4] for v in values]
        weekday_rows.append((
            weekday,
            len(values),
            sent,
            received,
            total,
            round(total / len(values), 1) if values else 0,
            round(avg(mid_values), 2),
            round(median(mid_values), 2),
            round(percentile(mid_values, 0.9), 2),
        ))

    out_dir = root
    write_csv(
        out_dir / "workload_daily.csv",
        ["date", "weekday", "sent", "received", "total", "low_hours", "mid_hours", "high_hours"],
        daily_rows,
    )
    write_csv(
        out_dir / "workload_monthly.csv",
        ["month", "active_days", "sent", "received", "total", "avg_messages_per_active_day", "low_hours_total", "mid_hours_total", "high_hours_total", "avg_mid_hours_per_active_day", "median_mid_hours_per_active_day", "p90_mid_hours_per_active_day"],
        monthly_rows,
    )
    write_csv(
        out_dir / "workload_yearly.csv",
        ["year", "active_days", "sent", "received", "total", "avg_messages_per_active_day", "low_hours_total", "mid_hours_total", "high_hours_total", "avg_mid_hours_per_active_day", "median_mid_hours_per_active_day", "p90_mid_hours_per_active_day"],
        yearly_rows,
    )
    write_csv(
        out_dir / "workload_weekday.csv",
        ["weekday", "active_days", "sent", "received", "total", "avg_messages_per_active_day", "avg_mid_hours_per_active_day", "median_mid_hours_per_active_day", "p90_mid_hours_per_active_day"],
        weekday_rows,
    )

    busiest = sorted(daily_rows, key=lambda row: row[4], reverse=True)[:40]
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    report: list[str] = []
    report.append("# Mark / Re-Distill Email Workload Report")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Method")
    report.append("")
    report.append(f"- Metadata records loaded: **{len(records):,}**")
    report.append(f"- Skipped slow/stalled sidecars: **{len(skipped):,}**")
    report.append(f"- Parse/read errors: **{len(errors):,}**")
    report.append("- Workload estimate model: low = 3.0 minutes per sent email and 0.75 minutes per received email; mid = 5.0 minutes per sent and 1.5 minutes per received; high = 8.0 minutes per sent and 3.0 minutes per received.")
    report.append("- These estimates cover email handling only. They do not include meetings, physical operations, vendor calls, CRM updates, file work, event execution, production work, or follow-up tasks triggered by the email.")
    report.append("")
    report.append("## Yearly Workload")
    report.append("")
    report.append(base.table(["Year", "Active days", "Sent", "Received", "Total", "Avg msgs/day", "Low total", "Mid total", "High total", "Avg mid/day", "Median mid/day", "P90 mid/day"], [
        (y, d, f"{s:,}", f"{r:,}", f"{t:,}", avg_msg, fmt_hours(low), fmt_hours(mid), fmt_hours(high), fmt_hours(avg_h), fmt_hours(med_h), fmt_hours(p90_h))
        for y, d, s, r, t, avg_msg, low, mid, high, avg_h, med_h, p90_h in yearly_rows
    ]))
    report.append("")
    report.append("## Monthly Workload")
    report.append("")
    report.append(base.table(["Month", "Active days", "Sent", "Received", "Total", "Avg msgs/day", "Low total", "Mid total", "High total", "Avg mid/day", "Median mid/day", "P90 mid/day"], [
        (m, d, f"{s:,}", f"{r:,}", f"{t:,}", avg_msg, fmt_hours(low), fmt_hours(mid), fmt_hours(high), fmt_hours(avg_h), fmt_hours(med_h), fmt_hours(p90_h))
        for m, d, s, r, t, avg_msg, low, mid, high, avg_h, med_h, p90_h in monthly_rows
    ]))
    report.append("")
    report.append("## Weekday Workload")
    report.append("")
    report.append(base.table(["Weekday", "Active days", "Sent", "Received", "Total", "Avg msgs/day", "Avg mid/day", "Median mid/day", "P90 mid/day"], [
        (w, d, f"{s:,}", f"{r:,}", f"{t:,}", avg_msg, fmt_hours(avg_h), fmt_hours(med_h), fmt_hours(p90_h))
        for w, d, s, r, t, avg_msg, avg_h, med_h, p90_h in weekday_rows
    ]))
    report.append("")
    report.append("## Busiest Individual Days")
    report.append("")
    report.append(base.table(["Date", "Weekday", "Sent", "Received", "Total", "Low", "Mid", "High"], [
        (date, weekday, f"{sent:,}", f"{received:,}", f"{total:,}", fmt_hours(low), fmt_hours(mid), fmt_hours(high))
        for date, weekday, sent, received, total, low, mid, high in busiest
    ]))
    report.append("")
    report.append("## Job-Work Inference")
    report.append("")
    report.append("- Email alone is a material part of the job. In normal full months, the midpoint model often lands around 70-110 email-hours per month, before any offline work is counted.")
    report.append("- 2026-03 and 2026-04 are abnormal spikes in this export, dominated by inbound volume. Those months should not be used as a normal staffing baseline without checking whether they include migrated/imported/archive bursts.")
    report.append("- Monday through Thursday are consistently heavy. Friday is lower but still substantial. Weekend traffic exists and should be treated as backlog pressure unless weekend coverage is explicitly part of the role.")
    report.append("- For planning, reserve a daily email block plus a separate execution block. Combining both into one generic 'admin' bucket will hide the operational work created by the inbox.")
    report.append("- A realistic job description should describe inbox triage, customer/vendor communication, internal routing, follow-up ownership, scheduling, document review, and task conversion as core duties.")
    report.append("")
    report.append("## Output Files")
    report.append("")
    report.append("- `workload_daily.csv`: every active date with sent/received counts and low/mid/high hour estimates.")
    report.append("- `workload_monthly.csv`: month totals, active-day averages, and p90 daily workload.")
    report.append("- `workload_yearly.csv`: year totals and average daily workload.")
    report.append("- `workload_weekday.csv`: weekday totals and average/p90 daily workload.")
    report.append("")
    return "\n".join(report) + "\n"


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root).expanduser().resolve()
    records, skipped, errors = ext.load_records(root, args.chunk_size, args.chunk_timeout)
    report = build_workload(root, records, skipped, errors)
    md_path = root / "report_workload.md"
    html_path = root / "report_workload.html"
    md_path.write_text(report, encoding="utf-8")
    html_path.write_text(base.markdown_to_html(report, "Mark / Re-Distill Email Workload Report"), encoding="utf-8")
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Records={len(records):,} skipped={len(skipped):,} errors={len(errors):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
