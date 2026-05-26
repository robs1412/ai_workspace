---
name: naomi-finance-planning
description: Use for recurring Naomi QuickBooks pulls that must keep the Financial Planning workbook honest by replacing stale past-dated forecasts with actuals once fresh QBO data exists.
---

# Naomi Finance Planning

Use this skill when the Naomi finance lane includes a Financial Planning workbook rerun.

## Rule

When fresh QuickBooks actuals exist for a dated planning row, do not leave the older forecast in place for that same already-passed window.

- Past-dated forecast rows should be replaced by actuals or cleared.
- Future-dated rows can remain forecast.
- Store / bar / events actuals should follow QuickBooks actuals once available, not stale separate Square assumptions.
- Every Financial Planning update run must leave one visible dated summary line in the `Running Balance` tab itself with the run date, QBO bank cash from the Balance Sheet bank accounts, the workbook `Running Balance` planning balance if different, QBO source cutoff, actualized incoming/outgoing rows, and remaining forecast rows. `AI Source Sync` can carry proof details, but it is not enough for the visible operator summary.
- Do not label the workbook `Running Balance` formula as actual cash unless it reconciles to QBO bank-account cash. If the numbers differ, show both: `QBO bank cash <amount>; Running Balance planning balance <amount>`.
- Future warehouse/distributor incoming projections should come from real invoice data, not rough customer guesses. Use `salesreport` warehouse invoice data (`wh_invoices` when available, or the warehouse invoice reporting tables/views that back `wh_reporting_invoices.php`) to project expected cash by invoice date plus payment terms, then verify open/paid status against QBO invoices/A/R when possible.

## Required QBO export package for planning work

Do not rerun the Financial Planning workbook from P&L / Balance Sheet / A/R / A/P alone when dated cash-planning rows still need actualization.

Export all of these in the same QBO run:

1. `Profit and Loss`
2. `Balance Sheet`
3. `Accounts receivable aging summary`
4. `Accounts payable aging summary`
5. `Transaction List by Date`
6. `Deposit Detail`
7. `General Ledger`

The ledger/detail package is mandatory for Financial Planning updates. Rows such as Visa, payroll, insurance, store/bar/events receipts, and other dated inflow/outflow lines should be updated from transaction-level QBO evidence, not left as stale forecasts once the date has passed.

## QBO login recovery pattern

Use the file-based code waiters for Intuit MFA. Do not use long-running terminal `stdin` prompts for codes; that path previously caused stale challenge/code mismatches.

Preferred order:

1. Run the saved-state recovery path first:

```bash
node /Users/admin/.codex/skills/qbo-naomi-recovery/scripts/qbo_naomi_saved_state_login.js
```

2. If SMS is required, run the file-based SMS waiter and wait for `ready.json`:

```bash
node /Users/werkstatt/ai_workspace/.private/scripts/qbo_naomi_live_code_file_waiter.js
```

When Robert provides the code, write it to the exact waiter file:

```bash
printf '%s\n' '<six-digit-code>' > /Users/werkstatt/ai_workspace/.private/finance/qbo-live-code-file-waiter/code.txt
```

3. If Intuit asks for a second verification factor or SMS delivery is unreliable, use the email-code waiter:

```bash
node /Users/werkstatt/ai_workspace/.private/scripts/qbo_naomi_email_code_file_waiter.js
```

Then write the email code to:

```bash
printf '%s\n' '<six-digit-code>' > /Users/werkstatt/ai_workspace/.private/finance/qbo-email-code-file-waiter/code.txt
```

The waiter must remain open between challenge creation and code submission. Do not open another QBO login page, trigger another code, or close the waiter before writing the matching code file.

## QBO report export notes

- The summary helper can export the standard finance package after saved-state recovery.
- The transaction-detail helper must prefer saved browser state and dated output directories.
- If the direct `Transaction List by Date` report-builder URL returns `We couldn't load your report`, do not waste time repeatedly trying the same URL. Continue with `General Ledger` and `Deposit Detail` when they export cleanly, and record the failed transaction-list attempt in the run status.
- For Financial Planning cash rows, `General Ledger` bank-account rows are sufficient proof for actualized Visa/credit-card payments, payroll debits, insurance, Store/Bar/Events deposits, and other cash movement.

## Future incoming projection rule

Use real warehouse invoice data before inventing future incoming rows.

- Primary projection source: `salesreport` `wh_invoices` if present.
- Fallback source: the invoice data behind `/Users/werkstatt/salesreport/.mempalace/full-src/wh_reporting_invoices.php`, especially `koval_distillery.invoice_history`, `koval_distillery.vw_invoice_items`, and linked account names/QB invoice numbers.
- Required invoice fields: invoice number, QB number when present, invoice date, account/distributor, invoice total after discount/exchange rate, and paid/open evidence when available.
- Default due-date assumption: most warehouse invoices are projected at invoice date plus 30 days.
- Known exceptions to record explicitly: Lanterna approximately 60 days; Toko approximately 45 days unless QBO/customer history proves a better term.
- Exclude Iowa / IA and Michigan / MI from normal near-term cash-incoming projections unless Robert explicitly says to include them for a specific run. These control-state / timing items should not inflate the standard June-style cash forecast.
- QBO check: when QBO invoice/A/R data is available, use QBO to confirm whether each invoice is open, partially paid, or already paid. Actual QBO payments override projected invoice due dates.
- Avoid double-counting: if a salesreport invoice due-date check is being used as supporting detail for a QBO A/R bucket, keep it informational or replace the QBO bucket with the invoice-derived amount. Do not add both as separate incoming rows for the same receivables.
- Running Balance labels should say `invoice projection` and include the source basis, for example `Warehouse invoice projection: Lanterna invoice <QB #> due ~60d`.

## Why

- `Profit and Loss` and summary reports give month-to-date truth.
- `Transaction List by Date`, `Deposit Detail`, and `General Ledger` provide the transaction-level proof needed for rows like payroll, Visa, insurance, store income, and other dated inflow/outflow lines in `Running Balance`.

## Workflow

1. Pull the fresh summary package.
2. Pull the transaction-detail package in the same login session.
3. Update append-only QBO source rows first.
4. Use transaction detail / ledger evidence to replace or clear past-dated forecast rows that now have QBO actual evidence.
5. Pull or query real salesreport warehouse invoices for future incoming projection rows, then check QBO invoices/A/R for paid/open status when possible.
6. Recalculate the Financial Planning workbook so actual incoming/outgoing values supersede stale forecasts.
7. Keep only future rows as forecast, with projection assumptions clearly labeled.
8. Add one dated run-summary line directly in the `Running Balance` tab near the affected month summary, for example: `<YYYY-MM-DD> update: QBO bank cash <amount>; Running Balance planning balance <amount>; QBO actuals through <date>; actualized <rows/amounts>; remaining forecasts <rows/amounts>`.
9. Save a readback artifact under `bid/data-management/historical-analysis/snapshots/2026-financial-planning/<run-date>/`.

## Current local entry points

- Summary report helper: `.private/scripts/qbo_naomi_export_reports_tty.js`
- Transaction-detail helper: `.private/scripts/qbo_naomi_export_may_bank_transactions.js`
- Planning source sync: `.private/scripts/update_financial_planning_live_positions.py`
- Planning receipt reconciliation: `.private/scripts/reconcile_financial_planning_income_actuals.py`
- May 23 ledger actual reconciliation: `.private/scripts/reconcile_financial_planning_may23_ledger_actuals.py`
- SMS login waiter: `.private/scripts/qbo_naomi_live_code_file_waiter.js`
- Email login waiter: `.private/scripts/qbo_naomi_email_code_file_waiter.js`

## May 23, 2026 readback pattern

After QBO login succeeds:

1. Run summary export:

```bash
QBO_RUN_DATE=2026-05-23 node /Users/werkstatt/ai_workspace/.private/scripts/qbo_naomi_export_reports_tty.js
```

2. Run ledger/detail export:

```bash
QBO_RUN_DATE=2026-05-23 QBO_TXN_FROM=05/01/2026 QBO_TXN_TO=05/23/2026 node /Users/werkstatt/ai_workspace/.private/scripts/qbo_naomi_export_may_bank_transactions.js
```

3. Actualize past-dated Financial Planning rows from ledger proof:

```bash
python3 /Users/werkstatt/ai_workspace/.private/scripts/reconcile_financial_planning_may23_ledger_actuals.py
```

Known May 23 proof:

- `General Ledger` exported to `.private/finance/qbo-bank-transactions-2026-05-23/exports/general-ledger-05-01-2026-to-05-23-2026.xlsx`.
- `Deposit Detail` exported to `.private/finance/qbo-bank-transactions-2026-05-23/exports/deposit-detail-05-01-2026-to-05-23-2026.xlsx`.
- `Transaction List by Date` direct URL returned `We couldn't load your report`; do not retry that stale direct URL without changing route/search method.
- QBO Balance Sheet bank-account cash readback: `$16,004.70` as of May 23, 2026 (`Chase Checking $597.86`, `UNB Checking $15,406.84`, `Wintrust Bank $0.00`).
- `Running Balance!A130:D130` readback: `QBO ledger actual Store/Bar/Events cash 05/15-05/23`, `$33,276.68`.
- `Running Balance!A132:D132` readback: `QBO ledger actual Visa/credit-card payment 05/18`, `$38,177.32`.
- `Running Balance!A142:D142` visible summary must distinguish actual QBO bank cash `$16,004.70` from workbook planning balance `$102,473.21`.
- Proof artifact: `/Users/werkstatt/bid/data-management/historical-analysis/snapshots/2026-financial-planning/2026-05-23/financial-planning-may23-ledger-actuals-readback-2026-05-23.json`.
