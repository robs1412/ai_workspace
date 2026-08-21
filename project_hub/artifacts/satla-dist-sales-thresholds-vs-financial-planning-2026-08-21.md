# Company Sales Coverage and Corrected SATLA + DIST Thresholds

Working report for team review

Corrected August 21, 2026 (America/Chicago)

OPS task: 379156

BID dashboard: https://bid.koval.lan/bid/sales_thresholds.php

## Correction to the first report

The earlier conclusion that KOVAL needed approximately **$300,000 per month from SATLA + DIST alone** was overstated. It applied the full company-level Financial Planning burn to the two current Illinois lanes and omitted continuing warehouse sales to distributors and accounts in other states.

The better interpretation is:

- approximately **$280,000–$300,000 per month is a reasonable total-company gross-sales run-rate range** under the current model;
- continuing other-WH sales supply part of that requirement; and
- the conservative residual target for **SATLA + Illinois DIST is approximately $180,000 per month**, not $300,000.

At August's unusually strong other-WH pace, the SATLA + DIST residual falls to approximately **$84,000 per month**. Until that other-WH pace repeats, use **$180,000 per month combined SATLA + DIST** as the planning target and treat roughly **$84,000–$182,000** as the live sensitivity range.

## Why the correction matters

KOVAL historically sold substantial Illinois volume through Heritage and later RNDC. That volume is historical context only because KOVAL is no longer distributed through Heritage or RNDC in Illinois, but it is the right scale comparison for the new SATLA/DIST lanes.

- Heritage averaged approximately **$100,155 per month in 2024**.
- Heritage was **$139,152 in January 2025**, **$135,548 in June 2025**, **$206,922 in September 2025**, and **$253,952 in October 2025**.
- RNDC IL was **$91,228 in January 2026**, **$87,912 in March**, **$113,514 in April**, and **$128,165 in May** before the current Illinois route change.

Those former Illinois sales must not be credited as current revenue, but they show that a roughly $100,000–$150,000 monthly Illinois lane was normal and that the original $300,000 SATLA/DIST-only conclusion was not a like-for-like replacement target.

## Current company sales pace

The DB-backed BID model separates four lanes:

1. SATLA retailer sell-through, sourced from the SATLA monthly reconciliation.
2. Illinois self-distribution, sourced from live WH invoices linked to the current DIST account/order set.
3. Other current WH sales to distributors, control states, duty-free accounts, export accounts, and other non-DIST customers.
4. Historical Illinois Heritage/RNDC, shown only for comparison and excluded from the current baseline.

August source readback:

| Channel | Source through | Actual / MTD | Monthly pace |
|---|---|---:|---:|
| SATLA retail sell-through | August 18 | $43,871 | $75,556 |
| Illinois DIST | August 21 | $24,545 | $36,232 |
| Other current WH distributors/states | August 21 | $127,707 | $188,519 |
| **Current company pace** | | | **$300,307** |

SATLA replenishment WH invoices are not counted as company sales in this table. They are inventory transfers into the SATLA lane; counting them along with SATLA retailer sell-through would double count the same commercial activity.

## Continuing other-WH baseline

Other-WH product sales excluding SATLA replenishment and historical Illinois Heritage/RNDC were:

| Month | Other current WH sales |
|---|---:|
| February 2026 | $133,745 |
| March 2026 | $125,318 |
| April 2026 | $50,443 |
| May 2026 | $73,540 |
| June 2026 | $103,120 |
| July 2026 | $112,974 |
| **Six-month average** | **$99,857** |

August is already $127,707 through the 21st because of current distributor/state sales including Whiskey Library, Utah, Vinocopia, Toko Trading, Florida, Wisconsin, Missouri, Hawaii, Colorado, Massachusetts, and others. Its projected $188,519 pace is therefore shown as an upside case, not yet the conservative baseline.

## Live Financial Planning requirement

The DB-backed Financial Planning scenario changed after the first report and now shows for September:

- beginning cash: **$183,673.68**;
- incoming cash: **$35,253.00**;
- outgoing cash: **$261,012.91**;
- net monthly burn: **$225,759.91**;
- ending cash: **negative $42,086.23**.

This replaces the older workbook figures used in the first draft. The Google Sheet remains historical; the dashboard reads the active BID Financial Planning scenario.

## Contribution assumptions

- Blended QBO 2026 cost of goods: **9.72%** of product sales as a temporary company-level proxy.
- Other-WH contribution: **85.28%**, after the COGS proxy and a **5% reserve** for freight, commissions, deductions, and collection variance.
- SATLA contribution: **73.33%**, based on the latest two DB-backed months after the COGS proxy, MMK charge, $8-per-case SATLA fee, and Illinois/Cook/Chicago taxes.
- DIST contribution: **84.8%**, using the existing planning treatment after the COGS proxy, embedded Illinois tax, and temporary handling allowance.

These are planning rates, not SKU/account profit margins.

## Corrected threshold calculation

Using the conservative continuing other-WH baseline:

- September net burn: **$225,760**.
- Other-WH baseline sales: **$99,857**.
- Modeled other-WH contribution: **$85,158**.
- Remaining contribution needed from SATLA + DIST: **$140,602**.
- At the current SATLA/DIST mix and contribution rate, required combined gross sales: **$182,484 per month**.

Using August's current other-WH pace:

- Other-WH sales pace: **$188,519**.
- Modeled other-WH contribution: **$160,769**.
- Remaining contribution needed from SATLA + DIST: **$64,991**.
- Required combined SATLA + DIST gross sales: **$84,350 per month**.

Current SATLA + DIST pace is approximately **$111,788 per month**. Current total-company pace contributes approximately **$246,901 per month**, about **$21,141 above** the current September net-burn model before collection-timing differences.

## Operating answer

Use these thresholds for team planning:

| Decision view | SATLA + DIST monthly gross-sales target |
|---|---:|
| Conservative continuing other-WH baseline | **$180,000** rounded target |
| Exact conservative model | $182,484 |
| August other-WH pace continues | $84,350 |
| Current SATLA + DIST pace | $111,788 |

The management target should remain **$180,000 combined SATLA + DIST per month** until other-WH sales consistently support a lower residual. Review it monthly in BID rather than keeping a fixed number in this document.

## Cash timing is still the gate

The September Financial Planning ending-cash gap is now approximately **$42,086**, not the older $112,524 figure.

If other-WH collections are already included in the $35,253 planned incoming, the remaining gap is equivalent to approximately **$54,623 of additional SATLA + DIST gross sales** at the current mix. If continuing other-WH collections are not included and arrive on time, the modeled baseline contribution is more than the cash gap.

Do not automatically subtract other-WH sales from the cash gap until expected QBO receipts are mapped into Financial Planning. Booked sales, WH invoices, QBO A/R, source-paid SATLA invoices, SATLA payouts, and bank receipts are different states.

## Recommended management use

1. Use the BID dashboard as the live source: https://bid.koval.lan/bid/sales_thresholds.php
2. Set the conservative SATLA + DIST operating target at **$180,000/month combined**.
3. Track a lower sensitivity case only when other-WH sales and expected receipts remain near the August pace.
4. Map other-WH QBO collection dates into Financial Planning so the operating contribution model and cash forecast converge.
5. Replace blended COGS and handling reserves with SKU standard cost, distributor freight/commission detail, and actual DIST route cost.

## Source record

- DB-backed BID Financial Planning active scenario 7, read August 21, 2026.
- BID/Salesreport SATLA monthly reconciliation snapshots for July and August 2026.
- Live WH invoice history and invoice item data through August 21, 2026.
- Current DIST account/order classification and historical Illinois Heritage/RNDC account history.
- OPS task 379156.
