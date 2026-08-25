# BID SATLA Live Order Sales

- Master Incident ID: `AI-INC-20260825-BID-SATLA-LIVE-ORDER-SALES-01`
- Date Opened: 2026-08-25
- Date Completed: 2026-08-25
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Correct the BID SATLA page so current-month sales are read live from the same DB-backed `/order` basis as the SATLA sales report, while preserving dated reconciliation snapshots for accounting close evidence.

## Symptoms

- `/order` showed roughly $64,000 of August SATLA delivered sales.
- BID showed $54,612.83 under a gross label, suggesting a stale or conflicting sales-period total.
- The BID amount was sales from July deliveries due for payment during August on the Net-30 cash schedule, rather than sales grouped into the August delivery/confirmation period.

## Root Cause

The BID page had no live `/order` monthly-sales card. It displayed a dated Salesreport reconciliation snapshot and labeled the due-month cash schedule `Gross scheduled`, making $54,612.83 of sales due for payment in August easy to mistake for sales delivered/confirmed in August. The August reconciliation snapshot was pulled August 24 while `/order` and MMK readbacks continued changing on August 25.

## Repo Logs

### bid

- Repo Log ID: `BID-SATLA-LIVE-SALES-20260825-01`
- Commit SHA: `7d9a46e` (through live-sales, complete-schedule, and actual-row commits beginning at `e919b27`)
- Commit Date: 2026-08-25
- Change Summary: Added a live `/order` monthly-sales query using the same confirmed-date and MMK-delivered fallback basis as the operational SATLA report; added live delivered sales, adjusted invoice total, invoice count, and source timestamps to BID; relabeled the cash schedule as sales due for payment in its Net-30 due-date month; and made the schedule start from every live `/order` invoice before overlaying Portal paid state.

## Verification Notes

- PHP lint passed for `satla.php`, `lib/satla_live_sales_model.php`, and its regression test.
- Existing SATLA forecast regression passed.
- New live-sales regression passed locally and from the live BID HTTP endpoint.
- Live DB readback for August at implementation time: 156 invoices, $64,966.53 delivered sales, $65,439.53 adjusted invoice total, latest MMK readback August 25 at 5:32 PM CT.
- Exact date-basis readback: all 145 invoices / $54,612.83 due in August were delivered in July; the 123 August-delivered Portal invoices then visible totaled $45,422.60 and were due in September.
- Coverage repair readback: the Portal-only schedule omitted 44 `/order` invoices totaling $23,341.61. After adding every live invoice and using the current `/order` delivered amount, 312 invoices classify without gaps as 139 paid, 155 open Net-30, and 18 overdue Net-30. August due sales are $54,825.80 and September due sales are $68,281.24, totaling exactly $123,107.04.
- Invoice `1258375` was the final $270 variance: current `/order` delivered value is $525.88 while the stale Portal billed value is $795.88. `/order` now controls scheduled sales value; Portal controls paid state.
- Historical-row repair: finalized July now displays 145 sales invoices / $54,038.00 sales, 34 invoices / $9,941.21 cash received by actual paid date, $9,808.76 final fees, and $132.45 closing due to KOVAL. Empty forecast zeros are no longer shown beside the actual closing balance.
- The new model endpoint returned HTTP 200 live; a deliberately nonexistent neighboring path returned HTTP 404, confirming the new release artifact is deployed.
- The authenticated page remains protected by the normal login redirect; no authentication control was changed.

## Rollback Plan

Revert BID commits through `7d9a46e` and redeploy. This removes only the live sales card/model and restores the former Portal-only cash schedule; it does not change any SATLA, `/order`, MMK, payment, fee, tax, or close data.

## Follow-Ups

- Keep snapshots for reconciliation and finalized close history.
- Keep current operational sales on a live DB read and preserve explicit date/basis labels for cash schedules.
