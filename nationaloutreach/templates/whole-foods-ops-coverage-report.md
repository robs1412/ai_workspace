# Whole Foods OPS Coverage Report Template

Use this template for Whole Foods / WFM portal-to-OPS coverage checks.

## Send Rules

- Send as an HTML table email with a plain-text fallback.
- Send from Vanessa Sterling `<vanessa.sterling@kovaldistillery.com>` through the approved National Outreach route unless a different approved sender route is explicitly assigned.
- Default recipients: Robert and Sonat when the report covers WFM portal/OPS scheduling state.
- Use greeting/signoff: `Hi Sonat and Robert,` / `Best,` / `Vanessa`.
- Highlight unassigned, open, partially assigned, missing OPS, or missing linked-shift rows in light red: `#fce4e4`.
- Keep credentials, cookies, portal session values, private SOP text, and raw portal exports out of the email and broad docs.

## Summary Block

I refreshed the Whole Foods portal rows and checked them against OPS Outreach.

Summary: `{portal_rows_checked}` portal rows checked; `{in_ops}` are in OPS; `{missing_ops}` are missing from OPS; `{linked_shift_count}` have linked Outreach shifts; `{fully_assigned}` are fully assigned; `{open_unassigned}` still have open/unassigned linked shifts.

Open or partially assigned rows are highlighted in light red below.

## HTML Columns

| Column | Meaning |
| --- | --- |
| Date | WFM portal row date |
| Request | WFM request number |
| Store | WFM store number and store name |
| Time | WFM portal time slot |
| Portal buyer field | WFM request/detail buyer field |
| Linked in portal | Whether request detail page was found |
| OPS status | `In OPS` or `Missing from OPS` |
| OPS match | OPS event ID and event name |
| Staffing coverage | Linked-shift assignment state |
| Assigned | Assigned COTeam names from OPS |
| Timing note | Past/upcoming note as of report date |

Use `<tr style="background:#fce4e4;">` for `Linked shift open/unassigned`, `Partially assigned`, `Needs linked shift`, and `Missing from OPS`.
