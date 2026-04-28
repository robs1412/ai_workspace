# Binny's OPS Coverage Report Template

Use this template for Binny's Connecteam-to-OPS Outreach coverage checks.

## Send Rules

- Send as an HTML table email with a plain-text fallback.
- Send from Vanessa Sterling `<vanessa.sterling@kovaldistillery.com>` through the approved National Outreach route unless a different approved sender route is explicitly assigned.
- Default recipient is Robert unless the request asks to copy Sonat or another owner.
- Highlight unassigned, open, partially assigned, missing OPS, or missing linked-shift rows in light red: `#fce4e4`.
- Keep credentials, cookies, session values, private SOP text, and raw private exports out of the email and broad docs.

## Source And Matching

- Use the latest approved Connecteam normalized COT export as the source set when available.
- Filter source rows to Binny's events.
- Match to OPS Outreach by Connecteam import key first.
- If the import key is absent, use a conservative fallback on date, start time, end time, and event title.

## Summary Block

I checked the Binny's source rows against OPS Outreach.

Summary: `{source_rows_checked}` Binny's source rows checked; `{in_ops}` are in OPS; `{missing_ops}` are missing from OPS; `{linked_shift_count}` have linked Outreach shifts; `{fully_assigned}` are fully assigned; `{open_unassigned}` still have open/unassigned linked shifts.

Open or partially assigned rows are highlighted in light red below.

## HTML Columns

| Column | Meaning |
| --- | --- |
| Date | Binny's event date |
| Binny's event | Source event title |
| Time | Source event time slot |
| Connecteam staff | Staff listed in the source export |
| OPS status | `In OPS` or `Missing from OPS` |
| OPS match | OPS event ID and event name |
| Staffing coverage | Linked-shift assignment state |
| Assigned in OPS | Assigned COTeam names from OPS |
| Products / notes | Source products or note text when present |
| Address | Source event address |

Use `<tr style="background:#fce4e4;">` for `Linked shift open/unassigned`, `Partially assigned`, `Needs linked shift`, and `Missing from OPS`.
