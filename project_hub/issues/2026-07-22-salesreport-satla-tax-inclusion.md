# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260722-SALESREPORT-SATLA-TAX-INCLUSION-01`
- Date Opened: 2026-07-22
- Date Completed: 2026-07-22
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Restore SATLA warehouse invoices to the distributor view and tax totals on `wh_reporting_invoices.php` while continuing to exclude active DIST self-distribution accounts.

## Symptoms

SATLA invoices were absent from the distributor invoice report for July 2026, so their PG/WG gallonage was also absent from the page's tax summary.

## Root Cause

The shared WH sales exclusion helper introduced on 2026-07-15 excluded both active DIST accounts and SATLA. It removed SATLA account `373491` directly and also removed WH invoices linked to SATLA `/order` sources. Both the visible report queries and tax-total query used that helper.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-SATLA-TAX-INCLUSION-20260722`
- Commit SHA: `f226035`, `d6a358a`, `1ab0c55`
- Commit Date: 2026-07-22
- Change Summary: Narrowed the shared WH exclusion to active DIST self-distribution accounts only. A temporary account-specific market fallback was removed at Robert's direction; SATLA account `373491` now has CRM billing state `Illinois`, so the existing generic state/country grouping includes its invoices in market and matrix/analysis views.

## Verification Notes

- PHP syntax checks passed for the helper and both consuming report files.
- A focused assertion confirmed the deployed helper retains `account_self_distribution` exclusion logic and no longer contains the SATLA account or SATLA order-link exclusions.
- `origin/master` and the live Salesreport checkout were fast-forwarded to `f226035`.
- Live deployed source syntax and the focused SATLA-inclusion assertion passed.
- Initial live CRM readback confirmed SATLA's billing country was `United States` while its billing state was blank, which explained why the generic market query discarded the row.
- The Portal account controller updated SATLA SPIRITS account `373491` billing state from blank to `Illinois`; live account and data-history readback confirmed the write with Robert user id `1` attribution.
- A July 2026 database readback using the original generic market expression returned `Illinois`: 3 invoices, $120,010.00 subtotal, 729.9000 PG, and 932.1200 WG.
- The account-specific market helper was removed. The live Salesreport checkout was fast-forwarded to `1ab0c55`; syntax and deployed-source readback confirmed only the generic market grouping remains.
- Direct unauthenticated HTTP verification returns the site's `406` access gate, so no authenticated table-row readback was captured from that route.

## Rollback Plan

Revert commit `f226035` and fast-forward the live Salesreport checkout only if SATLA invoices must again be excluded from this tax-reporting lane.

## Follow-Ups

- Confirm the July 2026 authenticated report visibly includes SATLA sales in the `Illinois` market row during normal owner use.
