# SATLA Reconciliation Ledger

- Master ID: `AI-INC-20260818-SATLA-RECONCILIATION-LEDGER-01`
- Date: 2026-08-18
- Repositories: `salesreport`, `bid`, `ai_workspace`
- OPS task: `378182`
- Status: completed; July portal-backed reconciliation finalized

## Objective

Create one DB-backed SATLA/MMK reconciliation that separates cash receipts from processed invoices, deducts MMK charges, KOVAL liquor taxes, the SATLA per-case fee, and payments already made to KOVAL, while retaining a running balance by sales month. Publish a finance-facing BID page, keep the operational edit/final-close surface in Salesreport, and establish twice-monthly preliminary reviews plus one final monthly close.

## Initial July 2026 source readback (superseded by portal)

- Operational invoices: 143 invoices, 299 cases, invoice total `$54,612.83`.
- KOVAL liquor taxes: Illinois `$2,820.39`, Cook County `$558.04`, Chicago `$44.60`; total `$3,423.03`.
- Verified eligible retailer cash from source attachments through 2026-08-14:
  - Binny's: `$29,763.99`.
  - Whole Foods: `$4,647.81`.
  - Total: `$34,411.80`.
- Fintech FMS bank activity: no SATLA Fintech credits from 2026-07-01 through the 2026-08-18 pull. Processed Fintech invoices remain expected receivables, not cash.
- MMK invoice `1256804`: `$5,393.70` for all SATLA suppliers. The proposed KOVAL allocation of `$3,993.43` is retained as expected pending allocation support.
- SATLA fee: 299 cases x `$8.00` = `$2,392.00`.
- No SATLA-to-KOVAL payout is recorded for July.
- Preliminary pre-portal DB balance was `$24,603.34`. It was superseded after SATLA portal access became available and must not be used as the July close.

Known exceptions remain visible rather than being forced into KOVAL revenue: `$205.47` short payment on Binny's advice 18365, `$137.97` paid against canceled local invoice 260157 on advice 18884, and `$210.00` Whole Foods payment above delivered value on cut invoice 260129.

## Authoritative SATLA portal readback

The approved Infisical credential provides read-only access to `https://orders.satlaspirits.com/`. DB table `salesreport_satla_portal_monthly_readbacks` now persists hashed monthly readbacks from the three controlling portal tabs.

- `RL-26` controls KOVAL sales, ordered/cut/shipped cases, and Illinois/Cook/Chicago taxes.
- `MMK Fees` controls KOVAL storage, delivery/fuel, inbound, and other MMK charges.
- `KOVAL Payments` controls paid and unpaid KOVAL invoice totals. Advice-level Drive attachments remain audit support and do not override the portal monthly paid total.

Final July 2026:

- 300 ordered - 1 cut = 299 shipped cases; case fee `$2,392.00`.
- 93 paid invoices totaling `$32,734.01`; 52 unpaid invoices totaling `$21,878.82`.
- MMK fees `$3,993.43`: storage `$0.00`, delivery/fuel `$1,604.68`, inbound `$2,268.75`, other `$120.00`.
- Taxes `$3,423.33`: Illinois `$2,820.55`, Cook `$558.18`, Chicago `$44.60`.
- SATLA-to-KOVAL payouts recorded `$0.00`; locked July closing balance `$22,925.25`.

Preliminary August 2026:

- 230 ordered - 5 cuts = 225 shipped cases; case fee `$1,800.00`.
- 23 paid invoices totaling `$6,641.40`; 84 unpaid invoices totaling `$29,412.72`.
- Taxes `$2,615.49`; no August MMK Fees statement is available yet.
- Cumulative running balance before August MMK costs is `$25,151.16`, including the finalized July carry.

## Implementation

- Salesreport remains the canonical operational entry and final-close surface.
- Remittances and SATLA payouts now retain their actual transaction date and an explicit sales-month application date.
- Source attachments can be linked from remittance, source-check, and MMK-cost rows.
- A monthly DB snapshot exposes the actual portal pull time in Chicago time and the reconciliation totals to BID.
- BID has a finance-facing sortable SATLA page with the running balance, source status, source attachments, and links to the order/MMK and Salesreport controls.
- Portal-backed months cannot be finalized until that month's MMK Fees statement exists. Final close uses portal paid totals, taxes, shipped cases, and MMK allocation rather than attachment aggregates.

## Verification

- PHP syntax checks passed for the changed Salesreport and BID files.
- `salesreport/tests/satla_reporting_test.php` passed.
- July seed completed transactionally and idempotently.
- Direct DB readback confirmed ten verified remittance rows, the expected MMK cost, four source checks, no payout, and the monthly snapshot.
- BID CLI render shows July finalized at `$22,925.25` and August preliminary at `$25,151.16` before August MMK costs, with ordered-minus-cut case math and the Chicago portal pull timestamp.

## Deployment and operational closeout

- Salesreport commits through `f358dfb` were pushed and the live `/home/koval/public_html/salesreport` checkout fast-forwarded to the same SHA. Live PHP syntax passed for the portal importer, snapshot refresh, finalizer, and reporting page.
- BID commit `dddbfe8` was pushed and both `/srv/development/bid` and `/srv/bid` fast-forwarded to the same SHA. Live PHP syntax passed; the authenticated BID URL returns the normal Login redirect.
- The project record was committed in `ai_workspace` as `cb9458e` before this closeout update.
- Notified shared OPS task `378314` performs the prior-month final close on the 3rd of every month.
- Notified shared OPS task `378315` performs the preliminary current/open-month refresh on the 18th of every month.
- OPS `378182` contains exact portal/source/deployment proof and is completed after the July DB close.
- Daily MMK task `376462` records the fresh 2026-08-18 19:03:53 InvoiceView/Product Cuts readback, 31 cut rows, and eight authenticated documents.
- The original pre-portal email was corrected on the same Dovid/Robert thread under Message-ID `<178708122499.52735.17575079027554326897@kovaldistillery.com>`.

## Rollback

Revert the dedicated Salesreport and BID commits and fast-forward the live checkouts. Do not delete ledger rows; void/correct them through the audited operational page so the source trail remains intact.
