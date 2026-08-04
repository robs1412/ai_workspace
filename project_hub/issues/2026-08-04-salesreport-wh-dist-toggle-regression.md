# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260804-SALESREPORT-WH-DIST-TOGGLE-REGRESSION-01`
- Date Opened: 2026-08-04
- Date Completed: 2026-08-04
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Correct the Salesreport warehouse invoice display so enabling SATLA visibility does not also expose DIST warehouse invoices. Preserve the separate DIST Sales Report and warehouse tax-total behavior.

## Symptoms

The July 2026 warehouse report with `exclude_satla=0` displayed six approved DIST exception invoices (`8159`, `8161`, `8165`, `8189`, `8190`, and `8203`) that belong only in the separate DIST report.

## Root Cause

The SATLA toggle selected `wh_reporting_general_sales_exclusion_sql()` when SATLA was included. That broader tax-oriented predicate excluded permanent self-distribution accounts but did not exclude order-level DIST fulfillment exceptions, bypassing the stricter display predicate deployed on 2026-08-03.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-20260804-WH-DIST-TOGGLE-01`
- Commit SHA: `85de5e7`
- Commit Date: 2026-08-04
- Change Summary: Added a DIST-only warehouse display predicate and a toggle-aware selector so DIST fulfillment remains excluded whether SATLA is included or excluded. Added regression coverage for both toggle states.

## Verification Notes

- Local and live PHP lint passed for both touched report files.
- Local and live `wh_reporting_invoice_exclusions_test.php` passed.
- Live `il_self_distro_report_helpers_test.php` passed.
- Live render using the exact July URL parameters showed all six DIST exception invoice links absent.
- The same live render retained SATLA Spirits invoice links `8128`, `8129`, `8130`, and `8208`.
- The separate DIST report retained `Approved DIST Exceptions`, 16.00 cases, and `$2,447.00`.
- Live Salesreport checkout fast-forwarded cleanly to `85de5e7`.

## Rollback Plan

Revert commit `85de5e7` and fast-forward the live Salesreport checkout only if the toggle-aware predicate causes a verified reporting error. The prior behavior would reintroduce DIST invoice leakage whenever `exclude_satla=0`.

## Follow-Ups

None. The regression is covered by an automated helper test and exact production readback.
