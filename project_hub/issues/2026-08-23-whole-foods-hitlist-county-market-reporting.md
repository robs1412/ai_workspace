# Whole Foods IL Hitlist And County Market Reporting

- Master Incident ID: `AI-INC-20260823-WHOLE-FOODS-HITLIST-COUNTY-MARKET-01`
- Date Opened: 2026-08-23
- Date Completed: 2026-08-23
- Owner: Robert
- Priority: Normal
- Status: Completed

## Scope

Add a Whole Foods-specific Illinois view to the SATLA call hitlist with durable last-order visibility and sortable columns. Add County Market to the existing Salesreport Chain Store Intelligence selector and the all-supported-chains rollup. Preserve the existing Mariano's reporting option; no future Mariano's orders were synthesized.

## Symptoms

The general SATLA call hitlist excluded chain accounts by default and did not offer an actionable Whole Foods view. Salesreport already supported Whole Foods and Mariano's but omitted County Market.

## Root Cause

The hitlist had only a generic chain-exclusion toggle. Its oldest-order server sort used CRM invoice history while the visible last-order value came only from `/order` rows since July 1, so sorting and display could disagree. The Salesreport chain map simply lacked County Market.

## Repo Logs

### order

- Repo Log ID: `ORDER-WHOLE-FOODS-HITLIST-20260823-01`
- Commit SHA: `62f9e85ff6d57f4b6c91942d2f892ccc1e24b091`
- Commit Date: 2026-08-23
- Change Summary: Added the Whole Foods IL hitlist route, all-history SATLA/CRM last-order reconciliation, oldest/newest server sorting, clickable table sorting, and focused regression coverage.

### salesreport

- Repo Log ID: `SALESREPORT-COUNTY-MARKET-20260823-01`
- Commit SHA: `0533ef5a9d806c05a197c823f6c16ea008387ebb`
- Commit Date: 2026-08-23
- Change Summary: Added County Market to the chain selector and all-supported-chains patterns with regression coverage.

## Verification Notes

- Full local PHP regression suites passed in both repositories.
- Both commits were pushed to `origin/master`.
- Order was pushed to its live bare remote and `/home/koval/public_html/order` fast-forwarded cleanly to `62f9e85`; live PHP lint and the new regression test passed.
- `/home/koval/public_html/salesreport` fast-forwarded cleanly to `0533ef5`; live PHP lint and the new regression test passed.
- Read-only live DB readback found 31 non-self-distribution Illinois retail/bar CRM accounts matching Whole Foods, with last SATLA-order and last valid CRM-invoice dates available to the view.
- Owner routes: `https://www.koval-distillery.com/order/call-hitlist.php?chain=whole_foods&sort=oldest_order` and `https://www.koval-distillery.com/salesreport/chain_store_intelligence.php?chain=county_market&state=Illinois`.

## Rollback Plan

Revert Order commit `62f9e85` and Salesreport commit `0533ef5`, push the reverts, and fast-forward both live checkouts. No schema or business-data mutation needs reversal.

## Follow-Ups

- Mariano's remains supported in Chain Store Intelligence. Recheck live order activity after the expected restart rather than recording an unverified future order now.
