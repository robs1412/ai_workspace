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
- Change Summary: Added `2026-IL-Top-Products.php`, registered it in the custom reports list and menu, and corrected the Top Accounts running-total sales column index from `9` to `10`.

## Verification Notes

- Local PHP syntax passed for `2026-IL-Top-Accounts.php`, `2026-IL-Top-Products.php`, `generated_reports.php`, and `_menu.php`.
- Local PHP render smoke for `2026-IL-Top-Products.php` with the 2025 Illinois all-products tab returned a non-empty page with title and Top-N summary present.
- Local PHP render smoke for `2026-IL-Top-Accounts.php` returned a non-empty page with the corrected running-total marker present.
- Pushed `897f9f8` to `origin/master`.
- Live Salesreport checkout fast-forwarded from `99f6f9b` to `897f9f8`.
- Live PHP syntax passed for the same touched files.
- Live PHP render smoke returned `title=present` and `summary=present` for the product report.
- Live PHP render smoke returned `sales_index=10` for the account report.

## Rollback Plan

Revert Salesreport commit `897f9f8` and fast-forward the live checkout to the revert commit.

## Follow-Ups

- None required for the delivered tabbed product report and running-total fix.
