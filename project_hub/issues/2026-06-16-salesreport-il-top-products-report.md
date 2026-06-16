# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260616-SALESREPORT-IL-TOP-PRODUCTS-01`
- Date Opened: 2026-06-16
- Date Completed: 2026-06-16
- Owner: Robert
- Priority: Normal
- Status: Completed

## Scope

Create a new Salesreport page modeled after `2026-IL-Top-Accounts.php`, but grouped as Sales by Product. Keep the same Illinois preset tab structure for 2026 Jan-May, 2025 full year, and 2024 full year with All/Retail/Bar variants. Fix the Top Accounts running total issue in the source page.

## Symptoms

`2026-IL-Top-Accounts.php` recalculated the visible running total client-side from column index `9`, which is the WG column. The Sales column is index `10`, so after page load/filter/sort the running total could be rewritten from WG instead of dollars.

## Root Cause

The interactive table script had a stale `salesColumnIndex` value after the table grew to include the WG column before Sales.

## Repo Logs

### salesreport

- Repo Log ID: `salesreport-20260616-il-top-products`
- Commit SHA: `897f9f8`
- Commit Date: `2026-06-16`
- Change Summary: Added `2026-IL-Top-Products.php`, registered it in the custom reports list and menu, and corrected the Top Accounts running-total sales column index from `9` to `10`. Follow-up commits `618692f`, `ac79d4f`, `be199a8`, `91da778`, `90b2e2b`, `86f1874`, `7c04692`, `30303e2`, `88fdf2c`, `95c0c7c`, `bd5461d`, `35e8918`, `fa667a7`, `5f9f791`, and `eaa22ab` added the product payout calculator, changed both product report Top-N summaries to `5, 10, 15, 20, 25, 30, 40, 50`, added filtered footer totals, added total shipping cost, added commission input units, restored final percent-column behavior on both product pages, renamed Product and Calculator footer labels to `Total Sales`, corrected the calculator margin formula to use `price / (1 - margin)`, and recalculated taxes per invoice line by ABV, account channel, and Chicago/Cook/outside-Cook location.

## Verification Notes

- Local PHP syntax passed for `2026-IL-Top-Accounts.php`, `2026-IL-Top-Products.php`, `generated_reports.php`, and `_menu.php`.
- Local PHP render smoke for `2026-IL-Top-Products.php` with the 2025 Illinois all-products tab returned a non-empty page with title and Top-N summary present.
- Local PHP render smoke for `2026-IL-Top-Accounts.php` returned a non-empty page with the corrected running-total marker present.
- Pushed `897f9f8` to `origin/master`.
- Live Salesreport checkout fast-forwarded from `99f6f9b` to `897f9f8`.
- Live PHP syntax passed for the same touched files.
- Live PHP render smoke returned `title=present` and `summary=present` for the product report.
- Live PHP render smoke returned `sales_index=10` for the account report.
- Live Salesreport fast-forwarded to `618692f` for `2026-IL-Product-Payout-Calculator.php`; live PHP syntax passed and render smoke returned calculator title, selling price, tax, net price, and KOVAL net markers.
- Live Salesreport fast-forwarded to `ac79d4f` for the Product and Calculator Top-N summary changes; live PHP syntax passed for both product pages.
- Live Salesreport fast-forwarded to `be199a8` for the corrected margin formula; local arithmetic readback confirmed `144 / 0.70 = 205.71`, live PHP syntax passed, and live render smoke returned `Selling price uses margin math`, `Top-N Payout Summary`, and `% of Total Filtered Sales`.
- Live Salesreport fast-forwarded to `91da778` for the calculator total shipping cost card; live PHP syntax passed and render smoke returned `Total shipping cost`.
- Live Salesreport fast-forwarded to `90b2e2b` for filtered footer totals and commission input units; live PHP syntax passed and render smoke returned `Filtered Total`, `commission-value-prefix`, and `commission-value-suffix`.
- Live Salesreport fast-forwarded to `86f1874` for the static `% of Sales` Top Products column; live PHP syntax passed and render smoke returned `% of Sales=present`, `% of Shown Total Sales=missing`, and `running-pct-total=missing`.
- Live Salesreport fast-forwarded to `7c04692` for location/channel/ABV-based calculator tax logic; live PHP syntax passed and render smoke returned `Tax is calculated per invoice line`, `Total tax estimate`, `Tax / Case`, and `KOVAL Net Total`.
- Live Salesreport fast-forwarded to `30303e2` for restored server-rendered Top Products `Running % of Sales`; live PHP syntax passed and render smoke returned `Running % of Sales=present`, `% of Sales=present`, `running-pct-total=missing`, and `% of Shown Total Sales=missing`.
- Live Salesreport fast-forwarded to `88fdf2c` for the Top Products footer label change from `Filtered Total` to `Total Sales`; live PHP syntax passed and render smoke returned `Total Sales=present` and `Filtered Total=missing`.
- Live Salesreport fast-forwarded to `95c0c7c` for Product Payout Calculator label changes; live PHP syntax passed and render smoke returned `% of Total Sales=present`, `% of Total Filtered Sales=missing`, `Total Sales=present`, and `Filtered Total=missing`.
- Live Salesreport fast-forwarded to `bd5461d` for restored percent-column coverage on both product pages; live PHP syntax passed and live source readback confirmed `Running % of Filtered Sales`, `Running % of Total Sales`, `% of Filtered Sales`, and `% of Total Sales` on both `2026-IL-Top-Products.php` and `2026-IL-Product-Payout-Calculator.php`.
- Live Salesreport fast-forwarded to `35e8918` for active-view running percent behavior; live PHP syntax passed and live source readback confirmed Top-N only shows `Running % of Total Sales`, detail shows `% of Filtered Sales` and `% of Total Sales`, and `Running % of Filtered Sales` is an `.active-view-col` recalculated by `recalculateRunningColumns()`.
- Live Salesreport fast-forwarded to `fa667a7` for separated product percent denominators; live PHP syntax passed and live source readback confirmed `% of Filtered Sales` uses the filtered report total, `% of Total Sales` uses `totalSalesSummary`, and the appearing running column is labeled `Running % of Active View`.
- Live Salesreport fast-forwarded to `5f9f791` for client-filtered product percent behavior; live PHP syntax passed and live source readback confirmed `% of Filtered Sales` cells use `filtered-pct` recalculated from `visibleTotal`, `% of Total Sales` cells use separate `total-pct`, and `totalSalesSummary` is no longer present.
- Live Salesreport fast-forwarded to `eaa22ab` for final product percent-column layout; live PHP syntax passed and live source readback confirmed default columns are `Running Sales %` and `% of Total Sales`, the running header changes to `Running Active View` for an active table view, and `% of Filtered Sales` is hidden as `filtered-view-col` until `filtered-view-active` is set.

## Rollback Plan

Revert Salesreport commit `897f9f8` and fast-forward the live checkout to the revert commit.

## Follow-Ups

- None required for the delivered tabbed product report and running-total fix.
