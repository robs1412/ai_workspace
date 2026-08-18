# Salesperson SATLA Cut And Attribution Repair

- Master ID: `AI-INC-20260818-SALESPERSON-SATLA-ATTRIBUTION-01`
- Opened: 2026-08-18
- Completed: 2026-08-18
- Owner: Robert
- Priority: High
- Status: Completed

## Outcome

The Sales by Salesperson summary and detail reports now exclude `/order` CRM invoices whose linked SATLA confirmed order was canceled or returned. Active salesperson-entered `/order` invoices are credited to the user who entered the order; admin-entered and external invoices retain the existing activity-owner fallback.

Live report: `https://www.koval-distillery.com/salesreport/byuser_detail.php?from=2026-08-01&to=2026-08-18&bill_state=Illinois&bill_city=%25&category=%25&chainfilterset=0&zipterritoryset=0&user_id=1351&limit=50`

## Source readback

- Fresh MMK pull at 2026-08-18 17:37:11 UTC imported 320 invoices, 886 lines, and 20 product-cut rows with zero invoice-detail errors.
- Sushi U.N.I confirmed order `238` / review order `310` is `returned_cut` / `returned`; MMK cut evidence shows zero invoiced units for all five product lines.
- Sushi U.N.I replacement confirmed order `273` is active and links to CRM invoice `378260` for 6 cases / $1,278.
- Caputo's Naperville confirmed order `244` / review order `316` is active, was entered by Maria Veleshnja (`1351`), and links to CRM invoice `377827` for 2 cases / $337.50.
- Caputo's South Elgin confirmed order `248` is active and links to CRM invoice `377917` for 5 cases / $900.
- Caputo's Carol Stream confirmed order `249` is `returned_cut` / `returned` and remains excluded.

## Implementation and proof

- Salesreport commit: `6e9a6cf6c6b7bb63bf74526ab4d5c66f93ccf461`
- Local and live PHP syntax checks passed for `byuser.php`, `byuser_detail.php`, and `tests/byuser_satla_attribution_test.php`.
- The focused regression test passed locally and live.
- The live Salesreport checkout fast-forwarded cleanly from `85615f2` to `6e9a6cf`.
- Authenticated live render for Maria (`1351`) reads Sushi U.N.I as 6 cases / $1,278 and includes Caputo's Naperville at 2 cases / $337.50 plus South Elgin at 5 cases / $900. The cut Sushi invoice and cut Carol Stream invoice are absent.
- No order, CRM invoice, activity, payment, or external communication data was changed by the report repair.

## Rollback

Revert Salesreport commit `6e9a6cf` and fast-forward the live Salesreport checkout. Do not roll back the fresh MMK source readback data.
