# SATLA Monthly Reconciliation

- Master Incident ID: `AI-INC-20260727-SATLA-MONTHLY-RECONCILIATION-01`
- Date Opened: 2026-07-27
- Date Completed: 2026-07-27
- Owner: Robert
- Priority: Normal
- Status: Completed

## Scope

Create a private Salesreport page for monthly SATLA cash reconciliation. Limit the page to Robert, Sonat, Mark, and Sebastian; add cash remittances and the monthly MMK charge; subtract $8 per MMK-invoiced case and the established Illinois, Cook County, and Chicago liquor-tax amounts.

## Placement Decision

Salesreport is the correct home because the calculation combines the reconciled MMK retailer-invoice read model with the existing Salesreport tax reports. `/order` remains the source for SATLA order, invoice, and payment-follow-up workflows.

## Repo Log

### salesreport

- Repo Log ID: `SALESREPORT-SATLA-MONTHLY-RECONCILIATION-20260727`
- Commit SHA: `61c58cddae2dabd5b90728b0ac591f0fd0a64e4e`
- Commit Date: 2026-07-27
- Change Summary: Added `satla_reporting.php`, exact page-level access control for user IDs `1`, `3`, `21`, and `144`, an audited manual remittance ledger, a monthly MMK-charge ledger, the $8-per-case calculation, existing Illinois/Cook/Chicago tax deductions, invoice detail, and restricted menu visibility.

## Data Basis

- Retailer invoice date, cases, product subtotal, and invoice total come from matched or matched-exception MMK invoice readbacks.
- No-charge replacement invoices and DIST-routed exceptions remain excluded by the established shared reporting rules.
- Illinois, Cook County, and Chicago deductions reuse the current Salesreport tax helpers.
- Remittances are manual audited entries until the requested bank-account readout is defined.
- The MMK monthly charge is entered for the selected month; no amount was assumed.
- Invoice totals remain visible for reconciliation but are not treated as cash received.

## Verification Notes

- Verified the exact active users: Robert `1`, Sonat `3`, Mark `21`, Sebastian `144`.
- PHP lint passed locally and in the live Salesreport checkout.
- The focused calculation test passed locally and live.
- July 2026 readback returned 107 reconciled retailer invoices, 215.00 cases, $39,846.46 invoice total, $2,089.91 Illinois tax, $394.86 Cook County tax, and $41.41 Chicago tax.
- An authorized live CLI render contained the report title, access note, $8-per-case calculation, and tax-detail links.
- An unauthorized user-ID probe returned the access-denied page without rendering report content.
- The unauthenticated HTTPS route returned the expected site access gate.
- Live Salesreport was fast-forwarded cleanly to `61c58cddae2dabd5b90728b0ac591f0fd0a64e4e`.

## Rollback Plan

Revert Salesreport commit `61c58cddae2dabd5b90728b0ac591f0fd0a64e4e` and fast-forward the live checkout. The two SATLA reporting ledger tables can remain as inactive audit history; remove them only after confirming they contain no production entries.

## Follow-Up

Define the approved bank source, transaction matcher, and review behavior before replacing manual remittance entry with bank-account readout. Do not infer account access or matching rules from this first version.
