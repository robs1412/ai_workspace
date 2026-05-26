# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260519-AVIGNON-WI-SALES-REPORT-01`
- Date Opened: `2026-05-19`
- Date Completed: `2026-05-19`
- Owner: `Codex`
- Priority: `Medium`
- Status: `completed`

## Scope

Deliver Sonat's Wisconsin sales report from Avignon using Salesreport and CRM invoice history as the source of truth for the exact window `2025-01-01` through `2026-04-30`, then record the owner-visible result and durable local trace.

## Symptoms

Sonat requested a Wisconsin report covering all KOVAL and Thresh and Winnow products and asked which products performed best in market during the requested window.

## Root Cause

No reusable Wisconsin report artifact existed yet for this exact Avignon request shape, so the work needed a narrow read-only Salesreport generator on the same invoice-history seam used for the prior Minnesota report.

## Repo Logs

### salesreport

- Repo Log ID: `AI-INC-20260519-AVIGNON-WI-SALES-REPORT-01-SALESREPORT`
- Commit SHA: `not committed`
- Commit Date: `2026-05-19`
- Change Summary: Added `scripts/generate_wi_sales_report.php` and generated `doc/avignon-sonat-wi-sales-report-2026-05-19.md` with Wisconsin totals, top products, year-by-product/SKU totals, and top 20 accounts for the exact requested window.

### ai_workspace

- Repo Log ID: `AI-INC-20260519-AVIGNON-WI-SALES-REPORT-01-AI-WORKSPACE`
- Commit SHA: `not committed`
- Commit Date: `2026-05-19`
- Change Summary: Recorded the Avignon closeout in `avignon/HANDOFF.md` and `avignon/EMAIL_DERIVED_DECISIONS.md`, staged Sonat-facing completion draft `avignon/drafts/sonat-wi-sales-report-complete-2026-05-19.txt`, and logged this completed slice in project hub.

## Verification Notes

- `php -l /Users/werkstatt/salesreport/scripts/generate_wi_sales_report.php`
- `php /Users/werkstatt/salesreport/scripts/generate_wi_sales_report.php`
- Verified report readback in `salesreport/doc/avignon-sonat-wi-sales-report-2026-05-19.md`:
  - `274` buying accounts
  - `764` invoices
  - `1,034.67` cases
  - `$135,452.90` revenue
  - top product `KOVAL Cranberry Gin Liqueur [G 30% 6x750ML]` at `292.50` cases
  - top account `Otto's Wine Cask` at `35.50` cases

## Rollback Plan

Remove the Wisconsin generator, generated report artifact, Avignon draft, and project-hub / handoff entries if this slice is superseded by a different approved reporting format.

## Follow-Ups

- If Sonat wants a shorter summary, derive it from `salesreport/doc/avignon-sonat-wi-sales-report-2026-05-19.md` without changing the underlying numbers.
- If Sonat wants a live refresh beyond April 30, 2026, rerun the report with an explicitly approved new end date.
