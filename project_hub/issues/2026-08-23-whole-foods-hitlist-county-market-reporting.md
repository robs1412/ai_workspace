# Whole Foods IL Hitlist And County Market Reporting

- Master Incident ID: `AI-INC-20260823-WHOLE-FOODS-HITLIST-COUNTY-MARKET-01`
- Date Opened: 2026-08-23
- Date Completed: 2026-08-23
- Owner: Robert
- Priority: Normal
- Status: Completed

## Scope

Add chain-specific Illinois views to the SATLA hitlist with durable last-order visibility and sortable columns. Use one canonical CRM chain mapping shared with Salesreport for Whole Foods, Mariano's, County Market, Binny's, Garfield's, The Fresh Market, Heinen's, and Woodman's. Binny's must be tasting-only, with no calling or order-entry controls. Preserve the existing Mariano's reporting option; no future Mariano's orders were synthesized. Remove two records marked Former Location from the current-store hitlist and transfer their invoice ownership to the matching current Wheaton and Willowbrook accounts.

## Symptoms

The general SATLA call hitlist excluded chain accounts by default and did not offer an actionable Whole Foods view. Salesreport already supported Whole Foods and Mariano's but omitted County Market.

## Root Cause

The hitlist had only a generic chain-exclusion toggle. Its oldest-order server sort used CRM invoice history while the visible last-order value came only from `/order` rows since July 1, so sorting and display could disagree. The Salesreport chain map simply lacked County Market.

## Repo Logs

### order

- Repo Log ID: `ORDER-WHOLE-FOODS-HITLIST-20260823-01`
- Commit SHA: `a339b6f` (feature commits through the shared-chain follow-up)
- Commit Date: 2026-08-23
- Change Summary: Added shared CRM chain-ID views for the eight requested Illinois chains, a dedicated Binny's tasting-only table linked to OPS Outreach, all-history SATLA/CRM last-order reconciliation, sortable tables, explicit Former Location exclusion, guarded invoice-transfer and chain-sync tooling, and focused regression coverage.

### salesreport

- Repo Log ID: `SALESREPORT-COUNTY-MARKET-20260823-01`
- Commit SHA: `0dceae61ede195839c72505f2950f4a033772e15`
- Commit Date: 2026-08-23
- Change Summary: Uses the same canonical CRM chain IDs as the hitlist, with fallback names, and adds County Market, The Fresh Market, Heinen's, and Woodman's to the existing chain reporting selector and all-supported rollup.

## Verification Notes

- Full local PHP regression suites passed in both repositories.
- Both commits were pushed to `origin/master`.
- Order was pushed to its live bare remote and `/home/koval/public_html/order` fast-forwarded cleanly through `a339b6f`; live PHP lint and the chain regression test passed.
- `/home/koval/public_html/salesreport` fast-forwarded cleanly to `0dceae6`; live PHP lint and the chain regression test passed.
- Initial read-only live DB readback found 31 non-self-distribution Illinois retail/bar CRM accounts matching Whole Foods. The follow-up excludes the two rows explicitly named Former Location, leaving 29 current-store rows in the live hitlist.
- Guarded transaction moved all 40 Wheaton-former invoice rows (`$16,510.98`, 39 valid plus one historical orphan row) from account `22486` to current Wheaton `153455`, and all 12 Willowbrook-former invoice rows (`$6,066.66`, all valid) from account `30854` to current Willowbrook `153456`.
- Post-write readback shows both former accounts at zero invoice rows. Current Wheaton now has 132 valid invoices and current Willowbrook has 111 valid invoices.
- A conflict-free dry run preceded the CRM mapping write. Canonical live chain counts now read back as: Binny's 49, Garfield's 11, The Fresh Market 5, Heinen's 5, Woodman's 9, Whole Foods 29 current stores, Mariano's 50, and County Market 14.
- Binny's renders a separate tasting-only table with no call, onboarding, payment, delivery, CRM activity-entry, or order controls; it links to OPS Outreach tasting creation and review.
- Owner routes: `https://www.koval-distillery.com/order/call-hitlist.php?chain=binnys&sort=oldest_order`, `https://www.koval-distillery.com/order/call-hitlist.php?chain=whole_foods&sort=oldest_order`, and `https://www.koval-distillery.com/salesreport/chain_store_intelligence.php?chain=county_market&state=Illinois`.

## Invoice Transfer Evidence

- Wheaton former `22486` -> current `153455`, invoice IDs: `22487, 23671, 23741, 24784, 25945, 27079, 27567, 28542, 30853, 33566, 34795, 35769, 36883, 37995, 38547, 40680, 41940, 42800, 43772, 45252, 47194, 47706, 48891, 50947, 51628, 52735, 54253, 54940, 56725, 56726, 59248, 60287, 62744, 63471, 65855, 67271, 69276, 71139, 72174, 73161`.
- Willowbrook former `30854` -> current `153456`, invoice IDs: `30855, 33567, 34796, 35770, 36882, 38548, 40681, 41941, 42799, 43773, 161727, 349992`.

## Rollback Plan

Revert Order commits through `a339b6f` plus Salesreport commit `0dceae6`, push the reverts, and fast-forward both live checkouts. If the CRM chain assignments must be reversed, clear only the exact accounts recorded by the dry-run output and remove newly created chain IDs 81 and 86 only after confirming they have no remaining account references. If the invoice ownership must be reversed, use the exact invoice-ID lists above in one guarded transaction, requiring each row to belong to the stated current account before restoring the former account ID.

## Follow-Ups

- Mariano's remains supported in Chain Store Intelligence. Recheck live order activity after the expected restart rather than recording an unverified future order now.
