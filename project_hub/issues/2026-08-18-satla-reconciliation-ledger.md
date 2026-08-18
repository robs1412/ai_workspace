# SATLA Reconciliation Ledger

- Master ID: `AI-INC-20260818-SATLA-RECONCILIATION-LEDGER-01`
- Date: 2026-08-18
- Repositories: `salesreport`, `bid`, `order`, `ai_workspace`
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
- `KOVAL Payments` open view controls current OPEN / OVERDUE status. Its corrected `Paid in a month` view controls PAID status, actual received amount, and the date the money was received; invoice and delivery dates are not payment dates. Advice-level Drive attachments remain audit support.

Final July 2026, corrected to payment-date cash basis:

- 300 ordered - 1 cut = 299 shipped cases; case fee `$2,392.00`.
- 34 invoices produced `$9,941.21` of cash actually received in July. Separately, 93 July-delivered invoices totaling `$32,734.01` have been paid across July and later payment months; 52 remain unpaid totaling `$21,878.82`.
- MMK fees `$3,993.43`: storage `$0.00`, delivery/fuel `$1,604.68`, inbound `$2,268.75`, other `$120.00`.
- Taxes `$3,423.33`: Illinois `$2,820.55`, Cook `$558.18`, Chicago `$44.60`.
- SATLA-to-KOVAL payouts recorded `$0.00`. The locked close was audit-revised from `$22,925.25` to `$132.45`; revision ledger row `1` preserves prior and replacement values and the reason.

Preliminary August 2026:

- 237 ordered - 5 cuts = 232 shipped cases; case fee `$1,856.00`.
- 82 invoices produced `$29,490.54` of cash actually received in August. Separately, 23 August-delivered invoices totaling `$6,641.40` are paid and 84 totaling `$29,412.72` remain unpaid.
- Taxes `$2,714.25`; no August MMK Fees statement is available yet.
- Expected MMK fees are `$2,214.70`: storage `$447.10`, delivery/fuel `$1,245.10` (232 shipped cases at the July KOVAL blended delivery/fuel rate), inbound `$522.50`, and other `$0.00` until statement-only adjustments arrive.
- Cumulative running balance after the explicitly labeled August MMK estimate is `$22,838.04`, including the corrected July carry. The final portal MMK statement replaces the estimate.

## SATLA invoice follow-up in `/order`

- `order_satla_portal_invoice_readbacks` stores the complete all-open list plus every available source-paid month; `order_satla_portal_invoice_sync_runs` stores pull counts, received totals, and timestamps.
- The August 18 15:08:12 CT pull imported 252 invoices: 128 open, 8 overdue, and 116 source-paid. All 252 matched an existing `/order` confirmed order through the MMK invoice readback. Source-paid invoices total `$39,431.75` actually received against `$39,375.41` billed.
- The invoice-payment page shows delivery date, Net 30 due date, actual Paid Date, MMK invoice, PO, customer, cases, billed and received totals, payer, portal status, follow-up classification, linked order, and last pull in Chicago time. Paid Date is the portal deposit/payment date, never the invoice or delivery date.
- Binny's and Whole Foods remain visible as automatic-payment accounts but are excluded from follow-up totals. Eight non-automatic invoices totaling `$3,012.08` currently require follow-up.
- Payment is never inferred from disappearance. A row absent from both the complete open view and the source-paid views becomes `UNKNOWN` for review. Page filters recalculate visible invoice, case, billed, received, paid, and balance totals.

## Implementation

- Salesreport remains the canonical operational entry and final-close surface.
- Remittances and SATLA payouts now retain their actual transaction date and an explicit sales-month application date.
- Source attachments can be linked from remittance, source-check, and MMK-cost rows.
- A monthly DB snapshot exposes the actual portal pull time in Chicago time and the reconciliation totals to BID.
- BID has a finance-facing sortable SATLA page with the running balance, source status, source attachments, and links to the order/MMK and Salesreport controls. Its invoice table defaults to the selected month by actual Paid Date and supports Paid/Delivered/Due date From/To filters with live visible totals.
- Portal-backed months cannot be finalized until that month's MMK Fees statement exists. Final close uses portal paid totals, taxes, shipped cases, and MMK allocation rather than attachment aggregates.
- Expected fee components are stored separately and displayed as estimated in BID; a final portal statement overwrites the estimate and its component breakdown.

## Verification

- PHP syntax checks passed for the changed Salesreport and BID files.
- `salesreport/tests/satla_reporting_test.php` passed.
- `/order` SATLA portal invoice-status, MMK Product Cut import, and delivered-sales regression tests passed.
- July seed completed transactionally and idempotently.
- Direct DB readback confirmed ten verified remittance rows, the expected MMK cost, four source checks, no payout, and the monthly snapshot.
- BID CLI render shows July finalized at `$132.45` after the audited cash-date correction and August preliminary at `$22,838.04` after the `$2,214.70` explicitly labeled MMK estimate, with its component basis and replacement-by-final-statement note.

## Deployment and operational closeout

- Salesreport commits through `f358dfb` were pushed and the live `/home/koval/public_html/salesreport` checkout fast-forwarded to the same SHA. Live PHP syntax passed for the portal importer, snapshot refresh, finalizer, and reporting page.
- BID commit `dddbfe8` was pushed and both `/srv/development/bid` and `/srv/bid` fast-forwarded to the same SHA. Live PHP syntax passed; the authenticated BID URL returns the normal Login redirect.
- Follow-up extension commits: `/order` `67920d5`, Salesreport `a4226ab`, and BID `f7b5a7b`. All were pushed; live `/order`, live Salesreport, `/srv/development/bid`, and `/srv/bid` were fast-forwarded to those exact SHAs without altering unrelated live backup files.
- Live `/order` readback confirms the 2026-08-18 15:08:12 CT combined portal pull: 252 matched invoices, 128 open totaling `$48,279.46`, 8 overdue totaling `$3,012.08`, and 116 source-paid totaling `$39,431.75` received. Paid dates span July 18 through August 17. The route remains access-controlled through the normal `/order` login.
- BID's authenticated route returns the normal login redirect; the DB-backed render readback shows `$29,490.54` received across 82 invoices by August Paid Date, the `$2,214.70` estimated MMK charge, and the `$22,838.04` running balance.
- The project record was committed in `ai_workspace` as `cb9458e` before this closeout update.
- Notified shared OPS task `378314` performs the prior-month final close on the 3rd of every month.
- Notified shared OPS task `378315` performs the preliminary current/open-month refresh on the 18th of every month.
- OPS `378182` contains exact portal/source/deployment proof and is completed after the July DB close.
- Daily MMK task `376462` records the fresh 2026-08-18 19:03:53 InvoiceView/Product Cuts readback, 31 cut rows, and eight authenticated documents.
- Daily MMK task `376462` now requires both the complete SATLA open import and every available source-paid month, with actual Paid Date/received amount and `/order` open/overdue/paid/match readback. Mid-month task `378315` requires an explicitly labeled fee-schedule estimate when the MMK statement is missing and forbids overwriting a final statement.
- DB-backed handoff `2254` records the four deployed commit proofs, invoice counts, estimate, running balance, and the no-Dovid-email boundary.
- The original pre-portal email was corrected on the same Dovid/Robert thread under Message-ID `<178708122499.52735.17575079027554326897@kovaldistillery.com>`.
- No additional email was sent. The owner's current instruction is to stop emailing Dovid unless a specific future message is explicitly authorized.

## Rollback

Revert the dedicated Salesreport and BID commits and fast-forward the live checkouts. Do not delete ledger rows; void/correct them through the audited operational page so the source trail remains intact.
