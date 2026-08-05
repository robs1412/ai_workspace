# MMK Dual-Date Illinois Tax Reporting

- Master ID: `AI-INC-20260805-MMK-DUAL-DATE-REPORTING-01`
- Opened: 2026-08-05
- Completed: 2026-08-05
- Owner: Robert
- Priority: High
- Status: Completed
- OPS task: `376620`
- Task Flow: `taskflow-ops-ai-worker-pickup-376620-2026-08-05`

## Outcome

July 2026 SATLA/MMK Illinois, Cook County, and Chicago reporting now uses the actual MMK invoice date and delivery date. An invoice is included in the selected reporting month only when both dates fall in that month. Cross-period invoices remain visible in a dedicated exception table.

## Source readback

The fresh MMK run completed at 2026-08-05 11:30 CDT with 273 unique invoices and 795 invoice lines. It found three invoices dated in July but delivered on 2026-08-05:

- `1246684` — Hairy Cow Brewing Company — invoice 2026-07-27, delivery 2026-08-05
- `1248842` — Brookfield Liquors — invoice 2026-07-29, delivery 2026-08-05
- `1249720` — Red Violin Wine & Spirits — invoice 2026-07-30, delivery 2026-08-05

## Verified July result

- Illinois: 143 included invoices, 375.834907 gallons, $2,820.40 represented state tax
- Cook County: 242.430674 gallons, $555.07 tax
- Chicago: 16.642837 gallons, $44.60 tax
- Change from invoice-date-only: Illinois -9.510193 gallons / -$64.28; Cook County -8.321419 gallons / -$20.80; Chicago unchanged

## Implementation and proof

- Salesreport commits: `f1527634b61441beb736df2d28d3641ff8ff3cf0`, `caa7ae2f3f7df3fcaf956b676ff9d54e630c4d36`
- Production PHP lint passed for the Illinois, Cook County, Chicago, monthly SATLA, and shared helper paths.
- Focused tax recommendation, SATLA reporting, and invoice-exclusion tests passed.
- Authenticated live server-side July renders passed with both-date predicates and cross-period exception markers.
- Browser verification reached the required 2FA gate; no authentication control was bypassed. Authenticated server-side readback supplied the live render proof.
- OPS task `376620` was advanced to its next monthly due date, 2026-09-05, and its completion proof was read back. The normal Portal notification route had an expired service session, so the existing OPS database fallback was used; no separate email was sent.
- No return was filed and no payment was made.

## Rollback

Revert the two Salesreport commits and fast-forward the live Salesreport checkout. Do not roll back the fresh MMK source readback data; it is authoritative evidence used by other reporting workflows.
