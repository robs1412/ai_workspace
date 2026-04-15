# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260409-BID-BINNYS-REPORT-01`
- Date Opened: `2026-04-09`
- Date Completed: `2026-04-09`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Completed`

## Scope

Convert BID Binny's scraper analytics from an ad hoc / one-off analysis path into a repeatable recurring report workflow tied to the existing scraper CSV exports.

## Symptoms

- BID had raw Binny's scraper CSVs plus an interactive viewer/mapping overlay, but no durable recurring report artifact.
- Operators could inspect a run manually, but the output was not structured as a stable report for repeated use or downstream automation.
- The scraper-side normal path did not produce a single report-oriented handoff artifact.

## Root Cause

The current BID implementation centered on viewer-time calculations against a selected CSV. That made the analytics useful for exploration, but not reportable as a recurring run output with durable HTML/Markdown/JSON artifacts.

## Repo Logs

### bid

- Repo Log ID: `bid-binnys-recurring-report-20260409`
- Commit SHA: `26498f835fd6c8c551f3eb801dc528a983b2edc5`
- Commit Date: `2026-04-09`
- Change Summary:
  - Added `tools/generate_binnys_recurring_report.php` to turn one or more Binny's scraper CSVs into recurring `report.html`, `report.md`, and `report.json` artifacts under `intelligence/reports/binnys_recurring/`.
  - Reused existing BID product/store mapping tables plus CRM sales overlays to compute recurring metrics: mapped coverage, estimated inventory, stock stress, priority store alerts, top products, and mapping gaps.
  - Updated `csv_reports_viewer.php` to expose the latest recurring HTML/JSON report directly.
  - Updated BID docs/manual/TODO workflow for the new recurring-report run path.

### playwright-scraper

- Repo Log ID: `playwright-scraper-binnys-report-wrapper-20260409`
- Commit SHA: `6c3602f0733803171054b6ccd52b5c9d5ad1fdfa`
- Commit Date: `2026-04-09`
- Change Summary:
  - Added `binnys-report-exec` to run both Binny's scrapes, copy the timestamped CSVs into BID, and invoke the recurring report generator automatically.
  - Added npm scripts for primary, secondary, and recurring Binny's runs.

## Verification Notes

- Ran:
  - `php tools/generate_binnys_recurring_report.php intelligence/reports/2026-01-08-08-26-45-binnys_availability_by_store.csv intelligence/reports/2026-01-08-08-28-14-binnys_availability_by_store-second.csv`
- Verified generated artifacts:
  - `intelligence/reports/binnys_recurring/run-20260108-082645/report.html`
  - `intelligence/reports/binnys_recurring/run-20260108-082645/report.md`
  - `intelligence/reports/binnys_recurring/run-20260108-082645/report.json`
  - `intelligence/reports/binnys_recurring/latest.html`
- Verified the sample report summarized 47 stores, 22 products, 46 mapped stores, 22 mapped products, and populated priority alerts/top products from CRM-linked data.
- Did not execute the live Playwright scrape wrapper in this session; wrapper logic was added based on the observed scraper output contract and existing historical CSVs.

## Rollback Plan

- Remove `tools/generate_binnys_recurring_report.php` and the viewer/doc updates in `bid`.
- Remove `binnys-report-exec` and the npm script additions in `playwright-scraper`.
- Delete generated `intelligence/reports/binnys_recurring/` artifacts if the recurring report flow is being fully reverted.

## Follow-Ups

- Optionally add a dedicated BID page for recurring-report history instead of linking directly to static HTML/JSON artifacts.
- Consider wiring the recurring report generator into any server-side scheduled scraper execution path once the new wrapper is accepted as the operator standard.
