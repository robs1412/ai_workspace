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

The 2026-08-10 follow-up also makes Cook County Schedule C source-aware: `source=satla` now lists SATLA/MMK retailer deliveries outside Cook County instead of always displaying DIST invoices.

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

## 2026-08-10 Schedule C SATLA follow-up

- Root cause: `wh_reporting_cookcounty.php` selected SATLA for the local-tax table but called a DIST-only outside-Cook helper unconditionally for Schedule C.
- Fix: Salesreport commit `ef2aec6e9cba61620b74cfdd645fee0e8b524a28` makes the helper source-aware and applies the established SATLA MMK invoice/delivery date, reconciliation, Product Cut, no-charge replacement, and approved DIST-exception gates.
- July 2026 production readback: DIST remains 4 invoices / 52.420000 WG; SATLA now reads 48 invoices / 131.026688 WG, split into 27.008950 WG at or below 14% and 104.017738 WG at or above 20%.
- Verification: focused PHP syntax checks and `tests/wh_reporting_tax_recommendations_test.php` passed locally and live. Live Salesreport fast-forwarded cleanly to `ef2aec6e9cba61620b74cfdd645fee0e8b524a28`, and the live server-side source comparison returned the same DIST and SATLA totals.
- No return was filed and no payment was made.

## 2026-08-10 Dovid communication draft

- Live AI Cloud path verified as `Satla Spirits / Reporting / 2026 July`; the communication document is under `SATLA Tax Reporting / July` at `https://docs.google.com/document/d/1B_b-zgyMisX5SCBWup-t6Uy_XhgzWYfmQHmxEnm2bc4/edit`.
- The current AI Cloud sales workbook still contains the original 301 cases / 378.211610 WG and therefore was not copied unfiltered into Schedule C.
- Added a draft-only English email to Dovid at the top of the `Communication` document. Its Google Docs table contains 48 live Schedule C invoices plus a total row: 27.008950 WG at or below 14%, 0.000000 WG over 14% and under 20%, 104.017738 WG at or above 20%, total 131.026688 WG.
- Filled three Portal `N/A` ZIP values from the live AI Cloud RL-26-R CSV: invoices `1236765`, `1238243`, and `1247882`. The table and all three corrections were read back through the Docs API.
- No email was sent, no return was filed, and no payment was made.

## 2026-08-10 corrected reporting copy

- Preserved the original `Satla Reporting July 2026` Google Doc and created one corrected copy in the owner-supplied AI Cloud `July` folder: `https://docs.google.com/document/d/1J03BBFJyevDkVCHV68G9Eq1Nw7hIH54qE2NA8vWOuBw/edit`.
- Corrected both received-gallon sections to the purchase-source values: `112.537300`, `35.663220`, `863.842560`, total `1,012.043080`; the Cook combined `20% or More` amount is `899.505780`.
- Docs API readback confirmed all seven intended replacements, no old received values remain in the copy, and the original retains its prior values.
- No email was sent, no return was filed, and no payment was made.

## Rollback

Revert the relevant Salesreport commits, including `ef2aec6` for the Schedule C follow-up, and fast-forward the live Salesreport checkout. Do not roll back the fresh MMK source readback data; it is authoritative evidence used by other reporting workflows.
