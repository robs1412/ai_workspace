# Salesreport DIST Invoice Link Fallback

- Master Incident ID: `AI-INC-20260824-SALESREPORT-DIST-INVOICE-LINK-FALLBACK-01`
- Date Opened: 2026-08-24
- Date Completed: 2026-08-24
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Stop approved DIST order invoices from appearing in the broad WH Distributor Sales report when the cached `/order` to WH invoice link has not refreshed yet.

## Symptoms

WH invoice `8324` for Access Contemporary Music appeared in the August Distributor Sales view even though `/order` order `412` was an approved DIST exception.

## Root Cause

The exclusion predicate matched DIST orders only through `order_wh_incoming_order_links.wh_invoice_number`. For order `412`, that cached field remained null even though the authoritative WH chain was incoming order `6754`, picklist `7480`, invoice `8324`.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-20260824-DIST-INVOICE-LINK-FALLBACK-01`
- Commit SHA: `2bac4fa`
- Commit Date: 2026-08-24
- Change Summary: Added an authoritative incoming-order/picklist invoice fallback to both WH DIST exclusion predicates and regression assertions for both SATLA-toggle states.

## Verification Notes

- Local PHP lint passed.
- Focused `wh_reporting_invoice_exclusions_test.php` passed locally and live.
- Live Salesreport checkout fast-forwarded from `0dceae6` to `2bac4fa`.
- The production report predicate for the exact August filters returns `0` visible rows for invoice `8324`.
- No invoice, order, exception, or cached link data was mutated.

## Rollback Plan

Revert Salesreport commit `2bac4fa` and fast-forward the live Salesreport checkout to the resulting commit.

## Follow-Ups

- Separately consider refreshing cached WH picklist/invoice link fields automatically when WH fulfillment advances; the report no longer depends on that cache being current for correct DIST exclusion.
