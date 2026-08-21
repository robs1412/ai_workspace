# Dufry Duty-Free Market Classification

- Master Incident ID: `AI-INC-20260821-DUFRY-DUTY-FREE-MARKET-01`
- Date Opened: 2026-08-21
- Date Completed: 2026-08-21
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Correct Dufry T5 account `70251` so sales reports classify it as `Duty Free`, customer invoices charge no tax, and Cook County, Chicago, Illinois/RL-26, Schedule C, FET/tax-withdrawal, and related exception reports exclude it entirely, without changing its physical Illinois shipping address.

## Symptoms

The August 2026 WH Invoices Sales by Market report showed Illinois at `$6,599.64` / `5.17%`. The entire row came from Dufry T5 WH invoices `8284` (`$1,693.68`) and `8285` (`$4,905.96`).

## Root Cause

Salesreport and Portal sales reports commonly use `vtiger_accountbillads.bill_state` as the reporting market. Dufry T5 stored `Illinois` there even though account `70251` is the established Avolta/Dufry duty-free account and is explicitly exempt from Cook County and Chicago gallonage tax in DIST.

## Repo Logs

### Shared CRM data

- Repo Log ID: `DUFRY-MARKET-STATE-20260821`
- Commit SHA: Not applicable; guarded live CRM data correction only
- Commit Date: 2026-08-21
- Change Summary: The initial billing-state change was rolled back after downstream review showed operational consumers use that field. Billing and shipping states remain `Illinois`; dedicated `account_preferences.reporting_state` is now `Duty Free` for report-only use.

### Salesreport

- Repo Log ID: `DUFRY-REPORTING-ADDRESS-SALESREPORT-20260821`
- Commit SHAs: `9b32567`, `d79cc18`
- Commit Date: 2026-08-21
- Change Summary: Report-only market, state, city, account, product, goal, and sales-analysis consumers now join `koval_crm.vw_account_reporting_address`. A shared account-ID exemption now removes Dufry from every tax-report population while tax calculations retain physical addresses for non-exempt accounts. Both commits are pushed to `master` and deployed to `/home/koval/public_html/salesreport`.

### Portal

- Repo Log ID: `DUFRY-REPORTING-ADDRESS-PORTAL-20260821`
- Commit SHA: `4b3fe130`
- Commit Date: 2026-08-21
- Change Summary: All Portal report models now use `koval_crm.vw_account_reporting_address`. The commit is pushed to `dev` and deployed as backend image `koval-crm-backend:v20260821reportingstate`.

## Verification Notes

- Exact preflight found no open Dufry incoming orders or picklists.
- Corrected live account readback: billing state `Illinois`, shipping state `Illinois`, dedicated reporting state `Duty Free`.
- Downstream review found billing state feeds Portal territory routing, Illinois compliance scans, geographic permissions, and future DIST/QBO billing-address payloads, so it must remain physical-address truth.
- The exact production August WH report aggregation now returns `Duty Free` at `$6,599.64` / `5.17%`; the contributing invoices remain WH `8284` / QB `6655` at `$1,693.68` and WH `8285` / QB `6656` at `$4,905.96`.
- Live DIST totals for WH `8284` and `8285` show Cook tax `$0.00`, Chicago tax `$0.00`, total tax `$0.00`, and no stored tax lines. QBO `6655` and `6656` both show `TotalTax=0`, no tax lines, and `NON` tax codes on every sales and packaging line.
- Production August readback returns zero Dufry rows in Cook DIST, Chicago DIST, Illinois DIST, RL-26 DIST, Schedule C DIST, all SATLA equivalents, and the SATLA tax-readiness, missing-MMK, and period-mismatch exception tables. The WH FET/tax-withdrawal summary uses the same shared account-ID exclusion.
- Salesreport lint, the reporting-address boundary regression test, the existing WH invoice-exclusion regression test, and `git diff --check` passed. Portal report-model lint and `git diff --check` passed.
- Live Salesreport HEAD is `d79cc18`. The Portal backend is running image `koval-crm-backend:v20260821reportingstate`; its health checks, live request traffic, and application database migration readback passed.
- No invoices, QBO records, shipping addresses, tax rows, email, or money movement were changed.

## Rollback Plan

Guardedly clear `account_preferences.reporting_state` only for account `70251` if Robert reverses the reporting classification, then read back the reporting view plus physical billing and shipping states and rerun the exact August market query. Revert Salesreport `9b32567` and Portal `4b3fe130` only if the report-wide boundary itself must be rolled back.

## Follow-Ups

No implementation follow-up remains. Keep future sales and market reporting on `koval_crm.vw_account_reporting_address`. Keep physical addresses for fulfillment and ordinary account tax-location logic, but always apply the account `70251` duty-free exemption before invoice-tax calculation or tax-report population.
