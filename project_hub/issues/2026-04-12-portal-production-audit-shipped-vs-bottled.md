# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260412-PORTAL-AUDIT-SHIPPED-BOTTLED-01
- Date Opened: 2026-04-12
- Date Completed: 2026-04-12
- Owner: Codex / Robert
- Priority: Production audit enhancement
- Status: Completed with hostname-routing follow-up

## Scope

Implement Robert-approved first slice of the Portal production audit enhancements: a read-only shipped-vs-bottled mismatch report using a committed SQL view plus the existing meta-model/report UI. No production data write paths were added.

## Symptoms

Portal needed a decision-ready, auditable report to identify mismatches between bottling remain counts and shipped/open-picklist/loss usage counts.

## Root Cause

No existing read-only meta-model report exposed shipped-vs-bottled mismatch logic or the related permission route for the approved Warehouse/Production audience.

## Repo Logs

### portal

- Repo Log ID: PORTAL-AUDIT-SHIPPED-BOTTLED-20260412
- Commit SHA: 29e4e902
- Commit Date: 2026-04-12
- Change Summary: Added shipped-vs-bottled mismatch SQL view, Warehouse read-only report route/client/model/view, meta-model config, controller quoting support for spaced view columns, and TODO note.

- Repo Log ID: PORTAL-AUDIT-FRONTEND-BUILD-20260412-A
- Commit SHA: 08eae89d
- Commit Date: 2026-04-12
- Change Summary: Tried locked frontend dependency install for production build.

- Repo Log ID: PORTAL-AUDIT-FRONTEND-BUILD-20260412-B
- Commit SHA: 51ab3c3e
- Commit Date: 2026-04-12
- Change Summary: Tried npm version adjustment for lockfile-compatible frontend build.

- Repo Log ID: PORTAL-AUDIT-FRONTEND-BUILD-20260412-C
- Commit SHA: 2c16012c
- Commit Date: 2026-04-12
- Change Summary: Added fast-png transpilation for production frontend build.

- Repo Log ID: PORTAL-AUDIT-FRONTEND-BUILD-20260412-D
- Commit SHA: 128814b6
- Commit Date: 2026-04-12
- Change Summary: Added iobuffer transpilation; final pushed/deployed commit.

- Repo Log ID: PORTAL-AUDIT-TODO-20260412
- Commit SHA: 46a11989
- Commit Date: 2026-04-12
- Change Summary: Recorded deployed report status and hostname-routing follow-up in TODO only; not a runtime deploy commit.

## Verification Notes

- Local checks: PHP lint passed for `MetaModelsController.php`; meta-model JSON files parsed successfully; `git diff --check` passed before commit.
- Local frontend lint could not run because local `node_modules` lacked `webpack-auto-inject-version`.
- Live Docker build/deploy tag: `v20260412-audit-128814b6`.
- Live containers after deploy: `koval-crm-frontend` and `koval-crm-backend` running final image tag; backend nginx sidecar running.
- Live deployment history recorded backend and frontend success for `v20260412-audit-128814b6`.
- Live SQL applied from committed update file: `koval_distillery.vw_warehouse_shipped_vs_bottled_mismatches`.
- Live view verification: `view-count=767`.
- Live permission verification: H2 permission present, H9 permission present.
- Verified built frontend bundle contains `/warehouse/inventory/shipped-vs-bottled-mismatches`.
- Verified live frontend responds on `http://portal.koval-distillery.com:8082/` and report hash URL `http://portal.koval-distillery.com:8082/#/warehouse/inventory/shipped-vs-bottled-mismatches`.
- Bare `https://portal.koval-distillery.com/` still returns a separate nginx 404. A narrow live `.htaccess` proxy attempt was backed up at `/home/koval/portal.koval-distillery.com/.htaccess.pre-portal-frontend-proxy-20260412-2009`, but the active public HTTPS path did not appear to use that file.

## Rollback Plan

- Application rollback: redeploy previous Portal backend/frontend image tags through `/home/koval/dockerportal/portal/deploy/scripts/deploy-prod.sh`.
- SQL rollback: drop or replace `koval_distillery.vw_warehouse_shipped_vs_bottled_mismatches`; remove the inserted `Shipped vs bottled mismatches` route permission JSON entries for H2/H9 if requested.
- Live vhost rollback: restore `/home/koval/portal.koval-distillery.com/.htaccess` from `/home/koval/portal.koval-distillery.com/.htaccess.pre-portal-frontend-proxy-20260412-2009`.

## Follow-Ups

- Decide whether the intended user-facing URL should remain the verified production port URL or whether server/cPanel/nginx ownership should fix bare `https://portal.koval-distillery.com/` to the frontend container.
