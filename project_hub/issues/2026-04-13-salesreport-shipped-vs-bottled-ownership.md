# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260413-SALESREPORT-SHIPPED-BOTTLED-OWNERSHIP-01`
- Date Opened: 2026-04-13
- Date Completed:
- Owner: Codex / Robert
- Priority: Medium
- Status: Planning, blocked pending migration approval

## Scope

Assess whether the shipped-vs-bottled mismatch report created during the Portal production audit incident should move from Portal Warehouse routing to the Salesreport `/salesreport` workspace.

## Symptoms

Robert noted that "these reports shipped v bottled should move to /salesreport" after the Portal dev deploy/login incident for the shipped-vs-bottled mismatch report.

## Root Cause

The report was implemented in Portal as a Vue MetaModel route under `/warehouse/inventory/shipped-vs-bottled-mismatches`, backed by a shared MySQL view `koval_distillery.vw_warehouse_shipped_vs_bottled_mismatches` and Portal role permission updates for `H2`/`H9`.

Salesreport already owns several adjacent warehouse/PHP report surfaces under `/salesreport`, including `wh_available_products.php`, `wh_reporting_production.php`, `wh_barrel_program_bottling.php`, and the WH Reporting / WH Management menu groups in `_menu.php`. A PHP read-only Salesreport page is the cleaner ownership target for an operational warehouse audit list, but the migration is not a local-only change.

## Repo Logs

### portal

- Repo Log ID: `PORTAL-SHIPPED-BOTTLED-AUDIT`
- Commit SHA inspected: `7557c00d918abe31a673b4515c0555394abfb0ec` on `origin/dev`
- Related production record inspected: `46a11989e0eaac19f20384e407d8db566a1949d5` on `origin/main`
- Change Summary: Added Portal MetaModel config, Vue model/service/view, warehouse router entry, SQL view creation, and Portal `role_permissions2` route grants for `H2`/`H9`.
- Local status note: `/Users/werkstatt/portal` was `dev...origin/dev [behind 5]` with pre-existing deletion `D backend/README.md`; no Portal files edited.

### salesreport

- Repo Log ID: `SALESREPORT-WH-REPORT-PATTERN-REVIEW`
- Commit SHA: Not changed in this slice
- Change Summary: Reviewed Salesreport warehouse report patterns and navigation only. `/Users/werkstatt/salesreport` was clean on `master...origin/master`; no Salesreport app files edited.

## Verification Notes

- Portal report data source: `koval_distillery.vw_warehouse_shipped_vs_bottled_mismatches`.
- Portal route: `/warehouse/inventory/shipped-vs-bottled-mismatches`.
- Portal frontend files to retire or redirect after migration:
  - `frontend/src/views/Warehouse/Inventory/ShippedVsBottledMismatches.vue`
  - `frontend/src/models/Warehouse/shipped-vs-bottled-mismatches.model.js`
  - `frontend/src/services/Warehouse/shipped-vs-bottled-mismatches.service.js`
  - route entry in `frontend/src/router/warehouse.router.js`
  - export wiring in `frontend/src/models/Warehouse/warehouse.model.js`
- Portal backend/config files involved:
  - `backend/config/MetaModels/warehouse-shipped-vs-bottled-mismatches.json`
  - MetaModel index entry (`backend/config/MetaModels/index_json` on `origin/dev`; `backend/config/MetaModels/index.json` in prior main commit)
  - shared controller quote fix in `backend/app/Http/Controllers/MetaModels/MetaModelsController.php`, which should not be reverted because it is generally useful for backticked view columns.
- SQL view should remain shared in `koval_distillery` at least through the move, so Salesreport and Portal can overlap during transition.
- Salesreport auth fit: Salesreport pages inherit login enforcement from `header.php`, but Salesreport does not have Portal route-level role permission equivalent for `H2`/`H9`. A restricted Salesreport admin/warehouse access helper should be added before exposing the link broadly, or the route should remain unlinked until approved.

## Recommended Migration Plan

1. Add a read-only Salesreport page, likely `wh_shipped_vs_bottled_mismatches.php`, that queries `koval_distillery.vw_warehouse_shipped_vs_bottled_mismatches`, supports column filtering/sorting/date/product/warehouse filters, and links bottling IDs to the relevant Portal/Salesreport detail where appropriate.
2. Add a small Salesreport permission helper for this page, initially matching the known intended audience (`H2`/`H9` equivalent or explicit approved user IDs) rather than exposing it to every authenticated Salesreport user.
3. Add the Salesreport link under `_menu.php` in `WH Reporting` or `WH Management` after permission gating is decided.
4. Keep the SQL view shared and do not duplicate the SQL logic in PHP until the Portal route is safely retired.
5. In Portal, either keep a temporary menu link/route that redirects users to `/salesreport/wh_shipped_vs_bottled_mismatches.php`, or remove the menu entry while leaving a documented redirect fallback for old bookmarks.
6. After Salesreport verification, remove or hide the Portal MetaModel route and revoke/stop adding the Portal `role_permissions2` route entry in a separate approved Portal change.
7. Coordinate deploy order: Salesreport first, then Portal redirect/removal. Do not change live containers or live DB state without explicit deploy approval.

## Rollback Plan

If the Salesreport page has access or query issues, keep Portal as the owner and leave the existing Portal route/view/permissions in place. If Portal redirect/removal has already been deployed, restore the Portal route and `role_permissions2` entry from the original Portal implementation commit.

## Follow-Ups

- Approval needed before implementation because the full move affects live routing, auth/permissions, the shared DB view, and cross-repo deploy order.
- Decide whether Salesreport should enforce access by Portal role mapping, explicit Salesreport user ID allowlist, or an existing Salesreport admin helper.
- Decide whether Portal keeps a redirect, a menu link to Salesreport, or no route after migration.
