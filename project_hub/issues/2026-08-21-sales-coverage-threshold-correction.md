# Sales Coverage Threshold Correction And BID Dashboard

- Master Incident ID: `AI-INC-20260821-SALES-COVERAGE-THRESHOLD-01`
- Date Opened: 2026-08-21
- Date Completed:
- Owner: Robert
- Priority: High
- Status: In progress

## Scope

Correct the SATLA/DIST sales-threshold report so it includes continuing WH sales to other distributors and states, retains Heritage/RNDC Illinois only as historical context, publishes a DB-backed auto-refreshing BID dashboard, revises the team Google Doc, and uploads the new DIST QBO invoice PDFs to AI Cloud `invoices to add`.

## Symptoms

The first report labeled approximately `$300,000/month` as a SATLA + DIST-only requirement. That applied the full Financial Planning burn to the Illinois lanes and omitted other current WH sales. It also failed to show that former Heritage/RNDC Illinois volume often ran near or above `$100,000/month` before the 2026 route change.

## Root Cause

The first model combined detailed SATLA and DIST economics with company-level Financial Planning cash pressure but did not add the remaining warehouse channel. SATLA replenishment invoices also require separate treatment so inventory transfers are not double counted with SATLA retail sell-through.

## Repo Logs

### bid

- Repo Log ID: `BID-20260821-SALES-THRESHOLDS-01`
- Commit SHA: pending
- Commit Date: pending
- Change Summary: Added normalized BID snapshots, assumptions, monthly channel rows, live refresh tools, a finance-authorized dashboard, historical Illinois comparison, current/continuing other-WH baselines, and regression tests.

### ai_workspace

- Repo Log ID: `AI-20260821-SALES-THRESHOLDS-01`
- Commit SHA: pending
- Commit Date: pending
- Change Summary: Corrected the team report source, recorded implementation evidence, and maintained this project-hub log.

## Verification Notes

- Live DB readback on 2026-08-21: other current WH sales `$127,706.68` MTD / `$188,519.38` pace; DIST `$24,544.50` MTD / `$36,232.36` pace; SATLA `$43,871.00` through August 18 / `$75,555.61` pace.
- Six completed months of continuing other-WH sales, excluding historical Illinois Heritage/RNDC and SATLA replenishment, average `$99,856.75/month`.
- Heritage/RNDC Illinois is historical only; Heritage averaged `$100,154.83/month` in 2024.
- Current DB-backed September Financial Planning scenario 7 reads incoming `$35,253.00`, outgoing `$261,012.91`, net burn `$225,759.91`, and ending cash `-$42,086.23`.
- Corrected SATLA + DIST residual range is about `$84,350` at August's other-WH pace to `$182,484` using the conservative six-completed-month other-WH baseline.
- AI Cloud invoice PDFs uploaded with exact size readback: QBO 6682 / WH 8311, QBO 6683 / WH 8313, QBO 6684 / WH 8315.

## Rollback Plan

Revert the dedicated BID commit and fast-forward both BID live checkouts. The dashboard tables are additive and may remain for audit; they can be dropped only with separate destructive-action approval. Restore the prior Google Doc body from Docs revision history if necessary. Do not delete the invoice PDFs without owner approval.

## Follow-Ups

- Replace the blended COGS proxy with SKU-level standard cost.
- Map other-WH expected receipts into Financial Planning to remove the remaining cash-timing ambiguity.
- Replace the DIST handling proxy with actual route labor, mileage, vehicle, and failed-delivery cost.
