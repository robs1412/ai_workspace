# SATLA Reconciliation Ledger

- Master ID: `AI-INC-20260818-SATLA-RECONCILIATION-LEDGER-01`
- Date: 2026-08-18
- Repositories: `salesreport`, `bid`, `ai_workspace`
- OPS task: `378182`
- Status: completed implementation; July close remains waiting on external source support

## Objective

Create one DB-backed SATLA/MMK reconciliation that separates cash receipts from processed invoices, deducts MMK charges, KOVAL liquor taxes, the SATLA per-case fee, and payments already made to KOVAL, while retaining a running balance by sales month. Publish a finance-facing BID page, keep the operational edit/final-close surface in Salesreport, and establish twice-monthly preliminary reviews plus one final monthly close.

## July 2026 source readback

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
- Preliminary DB-backed balance due: `$24,603.34`.

Known exceptions remain visible rather than being forced into KOVAL revenue: `$205.47` short payment on Binny's advice 18365, `$137.97` paid against canceled local invoice 260157 on advice 18884, and `$210.00` Whole Foods payment above delivered value on cut invoice 260129.

## Implementation

- Salesreport remains the canonical operational entry and final-close surface.
- Remittances and SATLA payouts now retain their actual transaction date and an explicit sales-month application date.
- Source attachments can be linked from remittance, source-check, and MMK-cost rows.
- A monthly DB snapshot exposes source-pull time in Chicago time and the reconciliation totals to BID.
- BID has a finance-facing sortable SATLA page with the running balance, source status, source attachments, and links to the order/MMK and Salesreport controls.
- The month cannot be finalized while MMK is expected or required source checks remain pending.

## Verification

- PHP syntax checks passed for the changed Salesreport and BID files.
- `salesreport/tests/satla_reporting_test.php` passed.
- July seed completed transactionally and idempotently.
- Direct DB readback confirmed ten verified remittance rows, the expected MMK cost, four source checks, no payout, and the monthly snapshot.
- BID CLI render shows the Chicago source-pull timestamp, `$34,411.80` receipts, 299 cases, and `$24,603.34` due.

## Deployment and operational closeout

- Salesreport commit `16b56e6` was pushed and the live `/home/koval/public_html/salesreport` checkout fast-forwarded to the same SHA. Live PHP syntax passed for all three touched files.
- BID commit `6a67eb5` was pushed and both `/srv/development/bid` and `/srv/bid` fast-forwarded to the same SHA. Live PHP syntax passed for the new page and touched navigation/permission files; the authenticated BID URL returns the normal Login redirect.
- The project record was committed in `ai_workspace` as `cb9458e` before this closeout update.
- Notified shared OPS task `378314` performs the prior-month final close on the 3rd of every month.
- Notified shared OPS task `378315` performs the preliminary current/open-month refresh on the 18th of every month.
- OPS `378182` contains the exact source and deployment proof and remains `Waiting for input` because July must not be finalized without Dovid's receipt ledger and the KOVAL-specific MMK allocation.
- The detailed reconciliation request was sent to Dovid and copied to Robert under Message-ID `<178707745576.36268.15065934311676015390@kovaldistillery.com>`.

## Rollback

Revert the dedicated Salesreport and BID commits and fast-forward the live checkouts. Do not delete ledger rows; void/correct them through the audited operational page so the source trail remains intact.
