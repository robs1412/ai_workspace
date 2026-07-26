# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260704-SATLA-DIST-DASHBOARD-SCOPE-01
- Date Opened: 2026-07-04
- Date Completed: 2026-07-04
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Keep SATLA `/order` dashboard order metrics/recent orders from showing DIST orders, and keep `/dist` dashboard fulfillment/invoice metrics/recent rows tied to linked DIST orders.

## Symptoms

Robert reported that the SATLA dashboard should not show DIST orders and vice versa.

## Root Cause

`/order/index.php` counted all `koval_crm.order_orders` rows without excluding `source_surface='dist'`. `/dist/index.php` counted fulfillments and WH invoices by fulfillment/invoice/account paths instead of requiring a linked `order_orders` row with `source_surface='dist'`.

## Repo Logs

### order

- Repo Log ID: satla-dashboard-scope-20260704
- Commit SHA: not committed because local and live checkouts already had unrelated dirty work.
- Change Summary: Live `/order/index.php` now filters order metrics and recent orders with `COALESCE(source_surface, source, '') NOT IN ('dist', 'self_service_dist')`.

### dist

- Repo Log ID: dist-dashboard-scope-20260704
- Commit SHA: not committed because local and live checkouts already had unrelated dirty work.
- Change Summary: Live `/dist/index.php` now filters fulfillment and WH invoice dashboard metrics through linked `order_orders` rows with `COALESCE(source_surface, source) = 'dist'`; recent fulfillment/invoice lists use the same DIST-linked basis.

## Verification Notes

- Live `git apply --check` passed for both dashboard-only patches before applying.
- Live PHP syntax checks passed for `/home/koval/public_html/order/index.php` and `/home/koval/public_html/dist/index.php`.
- Live CLI entrypoint checks for both dashboards completed without fatal errors.
- Live readback before/after basis:
  - `/order`: current-month all orders `12`; SATLA/order rows `4`; excluded DIST rows `8`.
  - `/dist`: current-month linked-DIST WH invoices `6`; recent invoice rows with linked DIST order `6`.

## Rollback Plan

Revert the live `index.php` dashboard-only diffs in `/home/koval/public_html/order` and `/home/koval/public_html/dist`.

## Follow-Ups

- These live changes should be folded into the appropriate branch/commit after the existing unrelated dirty work in both repositories is normalized.
