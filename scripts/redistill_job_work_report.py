#!/usr/bin/env python3
"""Infer job/work design signals from the Re-Distill email export."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import pathlib
import statistics

import analyze_redistill_email_export as base
import redistill_extended_reports as ext


DEFAULT_ROOT = pathlib.Path(
    "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 Re-Distill"
)

CATEGORY_OFFLINE_MINUTES: dict[str, tuple[float, float]] = {
    "Events / tastings / private bookings": (10.0, 18.0),
    "Sales / distributors / orders": (6.0, 10.0),
    "Production / operations": (8.0, 14.0),
    "Shipping / logistics": (5.0, 8.0),
    "Finance / accounting / payments": (6.0, 10.0),
    "Marketing / creative / brand": (8.0, 16.0),
    "Compliance / legal / insurance": (10.0, 20.0),
    "HR / staffing / benefits": (6.0, 12.0),
    "IT / systems / reports": (6.0, 12.0),
    "International / export": (8.0, 16.0),
    "Donations / community": (5.0, 10.0),
    "General / mixed administration": (2.0, 5.0),
}

SLA_TARGETS: dict[str, str] = {
    "Events / tastings / private bookings": "same business day for new inquiries; 24h for follow-up",
    "Sales / distributors / orders": "same business day for purchase orders, shipment issues, distributor questions",
    "Production / operations": "same business day when production/shipping is blocked; 48h otherwise",
    "Shipping / logistics": "same business day, often within hours when pickup/delivery is active",
    "Finance / accounting / payments": "24-48h depending on invoice/payment urgency",
    "Marketing / creative / brand": "48h unless tied to active print/deadline",
    "Compliance / legal / insurance": "same business day for regulatory/legal deadlines; 48h for routine paperwork",
    "HR / staffing / benefits": "same business day for scheduling/coverage; 48h for routine HR",
    "IT / systems / reports": "same business day for access/report blockers; 48h for routine requests",
    "International / export": "same business day when shipping/label/regulatory timing is active",
    "Donations / community": "2-3 business days unless event date is near",
    "General / mixed administration": "triage daily; route or close within 48h",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build job/work inference report.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-timeout", type=int, default=20)
    return parser.parse_args()


def h(minutes: float) -> float:
    return round(minutes / 60, 1)


def fmt_hours(hours: float) -> str:
    return f"{hours:.1f}h"


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


def category_for(record: dict) -> str:
    return base.classify(record["subject"], base.CATEGORY_RULES, "General / mixed administration")


def external_inbound(record: dict) -> bool:
    return record["direction"] == "received" and any(not ext.is_internal_domain(d) for d in record.get("from_domains", []))


def sent_record(record: dict) -> bool:
    return record["direction"] == "sent"


def build_reply_hours(records: list[dict]) -> dict[str, list[float]]:
    thread_records: dict[str, list[dict]] = collections.defaultdict(list)
    for record in records:
        if record.get("timestamp") is not None:
            thread_records[record["thread_hash"]].append(record)
    by_category: dict[str, list[float]] = collections.defaultdict(list)
    for items in thread_records.values():
        items.sort(key=lambda row: row["timestamp"])
        sent_times = [row["timestamp"] for row in items if row["direction"] == "sent"]
        for row in items:
            if not external_inbound(row):
                continue
            later = next((sent_time for sent_time in sent_times if sent_time > row["timestamp"]), None)
            if later is None:
                continue
            by_category[category_for(row)].append((later - row["timestamp"]) / 3600)
    return by_category


def build_report(root: pathlib.Path, records: list[dict], skipped: list[str], errors: list[str]) -> str:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    by_category = collections.Counter()
    by_category_dir = collections.Counter()
    category_subjects: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    by_month_category = collections.Counter()
    by_date = collections.Counter()
    by_weekday = collections.Counter()
    by_week = collections.defaultdict(lambda: collections.Counter())
    work_months = collections.defaultdict(lambda: collections.Counter())

    for record in records:
        category = category_for(record)
        direction = record["direction"]
        by_category[category] += 1
        by_category_dir[(category, direction)] += 1
        category_subjects[category][record["subject"]] += 1
        by_month_category[(record["month"], category)] += 1
        if record.get("date"):
            date_obj = dt.date.fromisoformat(record["date"])
            by_date[(record["date"], direction)] += 1
            by_weekday[(date_obj.strftime("%A"), direction)] += 1
            iso_year, iso_week, _ = date_obj.isocalendar()
            by_week[(iso_year, iso_week)][direction] += 1
            by_week[(iso_year, iso_week)][date_obj.strftime("%A") + "_" + direction] += 1
        work_months[record["month"]][direction] += 1

    reply_by_category = build_reply_hours(records)

    category_rows = []
    for category, total in by_category.most_common():
        sent = by_category_dir[(category, "sent")]
        received = by_category_dir[(category, "received")]
        email_low, email_mid, email_high = base.minutes_estimate(sent, received)
        offline_low_per_msg, offline_high_per_msg = CATEGORY_OFFLINE_MINUTES.get(category, (2.0, 5.0))
        offline_low = total * offline_low_per_msg
        offline_high = total * offline_high_per_msg
        examples = "; ".join(subject for subject, _count in category_subjects[category].most_common(5))
        replies = reply_by_category.get(category, [])
        category_rows.append((
            category,
            f"{sent:,}",
            f"{received:,}",
            f"{total:,}",
            fmt_hours(h(email_mid)),
            f"{fmt_hours(h(offline_low))}-{fmt_hours(h(offline_high))}",
            fmt_hours(median(replies)) if replies else "",
            SLA_TARGETS.get(category, "daily triage"),
            examples,
        ))

    month_category_rows = []
    for (month, category), count in by_month_category.most_common(40):
        if month != "unknown":
            month_category_rows.append((month, category, f"{count:,}"))

    month_work_rows = []
    for month in sorted(m for m in work_months if m != "unknown"):
        sent = work_months[month]["sent"]
        received = work_months[month]["received"]
        low, mid, high = base.minutes_estimate(sent, received)
        month_work_rows.append((month, f"{sent:,}", f"{received:,}", f"{sent + received:,}", fmt_hours(h(mid)), fmt_hours(h(high))))

    weekday_rows = []
    for weekday in base.DOW:
        sent = by_weekday[(weekday, "sent")]
        received = by_weekday[(weekday, "received")]
        low, mid, high = base.minutes_estimate(sent, received)
        weekday_rows.append((weekday, f"{sent:,}", f"{received:,}", f"{sent + received:,}", fmt_hours(h(mid)), fmt_hours(h(high))))

    backlog_rows = []
    for week_key, counter in sorted(by_week.items()):
        weekend_inbound = counter["Saturday_received"] + counter["Sunday_received"]
        monday_total = counter["Monday_sent"] + counter["Monday_received"]
        if weekend_inbound or monday_total:
            backlog_rows.append((f"{week_key[0]}-W{week_key[1]:02d}", f"{weekend_inbound:,}", f"{monday_total:,}"))
    backlog_rows = sorted(backlog_rows, key=lambda row: int(row[1].replace(",", "")) + int(row[2].replace(",", "")), reverse=True)[:30]

    delegation_rows = []
    for category, subjects in category_subjects.items():
        for subject, count in subjects.most_common(8):
            if count >= 25:
                delegation_rows.append((category, f"{count:,}", subject, suggested_delegate(category, subject)))
    delegation_rows.sort(key=lambda row: int(row[1].replace(",", "")), reverse=True)
    delegation_rows = delegation_rows[:60]

    report: list[str] = []
    report.append("# Mark / Re-Distill Job Work Inference Report")
    report.append("")
    report.append(f"Generated: {now}")
    report.append(f"Export root: `{root}`")
    report.append("")
    report.append("## Run Notes")
    report.append("")
    report.append(f"- Metadata records loaded: **{len(records):,}**")
    report.append(f"- Skipped slow/stalled sidecars: **{len(skipped):,}**")
    report.append(f"- Parse/read errors: **{len(errors):,}**")
    report.append("- March and April 2026 are included. This report treats them as real workload signal, not as outliers to remove.")
    report.append("- Inference is based on subjects, metadata, direction, domains, and thread timing. It does not quote or summarize private message bodies.")
    report.append("")
    report.append("## What Else We Can Infer")
    report.append("")
    report.append("- The job is not just 'answer email.' It is an intake and coordination surface for events, orders, production, vendors, finance/compliance, shipping, marketing, HR/scheduling, and internal systems.")
    report.append("- Email creates hidden execution work: scheduling, checking inventory/order state, vendor/customer calls, document review, CRM/task entry, event staffing, production follow-up, and internal escalation.")
    report.append("- A fair workload model needs two buckets: direct email handling and downstream task execution. The category table below estimates both.")
    report.append("- March/April 2026 show a high-inbound period where email alone can exceed a normal workday on peak dates. That should trigger triage/delegation/support rules rather than assuming one person can both process and execute everything.")
    report.append("")
    report.append("## Category Workload And Hidden Work")
    report.append("")
    report.append("Email mid-hours use 5 minutes per sent message and 1.5 minutes per received message. Hidden-work range is a planning estimate by category for non-email execution triggered by the messages.")
    report.append("")
    report.append(base.table(["Category", "Sent", "Received", "Total", "Email mid-hours", "Hidden-work range", "Median reply", "Suggested SLA", "Examples"], category_rows))
    report.append("")
    report.append("## Month Workload Including March / April")
    report.append("")
    report.append(base.table(["Month", "Sent", "Received", "Total", "Email mid-hours", "Email high-hours"], month_work_rows))
    report.append("")
    report.append("## Weekday Workload")
    report.append("")
    report.append(base.table(["Weekday", "Sent", "Received", "Total", "Email mid-hours", "Email high-hours"], weekday_rows))
    report.append("")
    report.append("## Weekend / Monday Backlog Pressure")
    report.append("")
    report.append("Weekend inbound plus Monday volume is a rough pressure indicator: weekend emails can create Monday triage debt before Monday's own requests arrive.")
    report.append("")
    report.append(base.table(["ISO week", "Weekend inbound", "Monday total"], backlog_rows))
    report.append("")
    report.append("## Delegation / Template Candidates")
    report.append("")
    report.append(base.table(["Category", "Count", "Repeated subject", "Recommended handling"], delegation_rows))
    report.append("")
    report.append("## Job Description Draft Language")
    report.append("")
    report.append("A realistic job description should say that the role owns cross-functional email intake and follow-through, including:")
    report.append("")
    report.append("- Triage inbound customer, vendor, distributor, event, production, finance/compliance, and internal requests.")
    report.append("- Convert email requests into trackable tasks with requester, owner, due date, next action, source thread, and closure evidence.")
    report.append("- Maintain timely external follow-up for orders, events, vendor questions, shipping/logistics, and production blockers.")
    report.append("- Coordinate with internal teams to resolve requests rather than leaving decisions buried in the inbox.")
    report.append("- Use templates and routing rules for repeated inquiries while escalating exceptions and deadline-sensitive work.")
    report.append("- Review recurring workload reports weekly to identify backlog, delegation needs, and process improvements.")
    report.append("")
    report.append("## Management Recommendations")
    report.append("")
    report.append("- Treat email as scheduled work. On normal weekdays, reserve 3-5 hours for direct email triage/response; on high-volume March/April-style periods, reserve a dedicated triage block plus support coverage.")
    report.append("- Add a daily intake cutoff: urgent same-day work, standard 24-48h follow-up, and backlog routing should be separated.")
    report.append("- Create shared queues by category so repeated tasks are not dependent on one person's inbox memory.")
    report.append("- Use recurring templates for the highest-volume repeated subjects, but preserve human review for legal/compliance, finance, HR, production blockers, and high-value customer/vendor requests.")
    report.append("- Review this report with the actual job owner to validate which categories are truly owned, assisted, delegated, or only copied for visibility.")
    report.append("")
    return "\n".join(report) + "\n"


def suggested_delegate(category: str, subject: str) -> str:
    low = subject.lower()
    if "contact form" in low or "inquiry" in low:
        return "Template first response + task routing by category."
    if "order" in low or "purchase order" in low:
        return "Order/distributor queue with same-day SLA."
    if "tasting" in low or "event" in low or "private" in low:
        return "Events queue; template intake plus calendar/task handoff."
    if "invoice" in low or "receipt" in low or "payment" in low:
        return "Finance/compliance queue; avoid burying in general inbox."
    if "report" in low:
        return "Internal reporting queue; summarize and assign owner."
    if category == "General / mixed administration":
        return "Triage daily; convert repeat pattern into named queue or template."
    return "Create category-specific SOP/template and assign backup owner."


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root).expanduser().resolve()
    records, skipped, errors = ext.load_records(root, args.chunk_size, args.chunk_timeout)
    report = build_report(root, records, skipped, errors)
    md_path = root / "report_job_work.md"
    html_path = root / "report_job_work.html"
    md_path.write_text(report, encoding="utf-8")
    html_path.write_text(base.markdown_to_html(report, "Mark / Re-Distill Job Work Inference Report"), encoding="utf-8")
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Records={len(records):,} skipped={len(skipped):,} errors={len(errors):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
