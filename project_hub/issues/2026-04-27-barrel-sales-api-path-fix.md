# Barrel Sales API Path Fix

Master ID: `AI-INC-20260427-BARREL-SALES-API-PATH-01`

Date: 2026-04-27 CDT

## Summary

Robert asked to fix the approved path after Avignon reported that marking barrels sold through Salesreport stopped at a mandatory service-account reset gate.

The Salesreport WH barrel pages were still falling back to the default CRM service-account token after the session-token attempt failed. That fallback can hit the reset gate and is not the intended Codex/browser-auth route for barrel state writes.

Follow-up functionality review found a second issue in the Portal sold-button path: `sellBarrel()` committed the barrel sale, then sent the sale notification before creating the barrel project/tasks. If notification failed, the barrel could remain sold while the project/task workflow was skipped.

## Changes

- Updated `/Users/werkstatt/salesreport/wh_barrel_program_management.php`.
- Updated `/Users/werkstatt/salesreport/wh_barrel_detail.php`.
- Both pages now prefer the active Salesreport session username.
- CLI/worker execution can use `CODEX_AGENT_USERNAME` through the approved Codex identity.
- Barrel-state writes now fail with a clear approved-path message if no user identity is available instead of silently using the stale default service account.
- Updated `/Users/werkstatt/portal/backend/app/Http/Controllers/BarrelsController.php`.
- Updated `/Users/werkstatt/portal/backend/app/Http/Controllers/ProjectController.php`.
- Portal now creates the barrel project/tasks before sending the sold notification, catches notification failures so they cannot skip task creation, treats project creation as idempotent when a project already exists, and attributes project/task creation to `barrel_details.sold_by`.
- Project creation now supports an explicit `_current_user` for internal controller calls and returns the project id before attempting project-created notifications.

## Live Action

- Used the approved Codex portal token path without printing tokens or credentials.
- Marked barrels `9513` and `9346` sold on sample request `2678` for Beatrix - Fulton Market.
- API responses for both barrel item updates returned HTTP `200` with `Updated successfully!`.
- Robert clarified the sale should be attributed to Sonat. The two affected current barrel rows and their latest sold-history rows were corrected to Sonat user id `3`.
- Backfilled the missing barrel program projects and child tasks:
  - Barrel `9513`: active project `367538`, 15 active child tasks.
  - Barrel `9346`: active project `367554`, 15 active child tasks.
  - Matt Andrews bottling tasks are `367552` / `Bottle Product Barrel 9513` and `367568` / `Bottle Product Barrel 9346`.
- Corrected all live created-record attribution for those projects/tasks to Sonat user id `3`, including `vtiger_crmentity.smcreatorid`, `smownerid`, `modifiedby`, and the 30 task `data_history.modified_by` rows.
- Robert then clarified that generic promote/social tasks should be removed from the barrel program workflow because they do not help sales. The four Beatrix promote tasks were canceled and removed from active workflow:
  - `367546` / `Promote on social media #9513`
  - `367547` / `Promote Barrel #9513`
  - `367562` / `Promote on social media #9346`
  - `367563` / `Promote Barrel #9346`
- Deployed the Portal backend-only fix on the VPS as Docker image `koval-crm-backend:v20260427barrel`. Previous live backend image was `v20260422c`.
- Follow-up backend deploy for the marketing assignment rule is live as Docker image `koval-crm-backend:v20260427barrelb`.
- Avignon emailed Claude, copied Sonat and Robert, with the four assigned marketing task IDs and instruction to get creative direction/timing/preferred language from Sonat. Message-ID `<177733982019.33970.4278400179209097075@kovaldistillery.com>`.
- Follow-up backend deploy removed the promote/social task creation from future sold-button projects. Live backend is now Docker image `koval-crm-backend:v20260427barrelc`.
- Avignon sent Claude a correction, copied Sonat and Robert, telling him not to work from the four promote task IDs because those tasks were removed. Message-ID `<177734061637.39598.2000560111728562721@kovaldistillery.com>`.

## Verification

- `php -l /Users/werkstatt/salesreport/wh_barrel_program_management.php`
- `php -l /Users/werkstatt/salesreport/wh_barrel_detail.php`
- `git -C /Users/werkstatt/salesreport diff --check -- wh_barrel_program_management.php wh_barrel_detail.php`
- `php -l /Users/werkstatt/portal/backend/app/Http/Controllers/BarrelsController.php`
- `php -l /Users/werkstatt/portal/backend/app/Http/Controllers/ProjectController.php`
- `git -C /Users/werkstatt/portal diff --check -- backend/app/Http/Controllers/BarrelsController.php backend/app/Http/Controllers/ProjectController.php`
- Live VPS deploy status: backend version `v20260427barrelc`, containers running.
- Live container lint passed for `/var/www/app/Http/Controllers/BarrelsController.php` and `/var/www/app/Http/Controllers/ProjectController.php`.
- Codex identity hydration check returned `hydrated: true` and `token_present: true` without printing token values.
- Database readback:
  - Barrel `9513`: `selection_status = 2`, `sample_request_id = 2678`, `sold_by = 3`, `updated_by = 3`, latest sold history `modified_by = 3`.
  - Barrel `9346`: `selection_status = 2`, `sample_request_id = 2678`, `sold_by = 3`, `updated_by = 3`, latest sold history `modified_by = 3`.
  - Project `367538`: `smcreatorid = 3`, `smownerid = 3`, `modifiedby = 3`, active, linked to barrel `9513`.
  - Project `367554`: `smcreatorid = 3`, `smownerid = 3`, `modifiedby = 3`, active, linked to barrel `9346`.
  - Each project now has 13 active child tasks after the two generic promote/social tasks per barrel were canceled and deleted from active workflow.
  - Matt task `367552` is assigned to user `147` / Matt Andrews under project `367538`.
  - Matt task `367568` is assigned to user `147` / Matt Andrews under project `367554`.
  - Promote tasks `367546`, `367547`, `367562`, and `367563` have `status = Canceled` and `deleted = 1`.

## Boundaries

- No credential, password, token, session cookie, or private 2FA value was printed or stored in notes.
- No password reset, OAuth change, broad auth repair, live pull, commit, push, pricing decision, account commitment, or unrelated barrel/program mutation was performed.
- Portal deploy was backend-only. It used a live controller-file backup under `/home/koval/dockerportal/backups/barrel-fix-20260427/`, committed Docker images `koval-crm-backend:v20260427barrel`, `koval-crm-backend:v20260427barrelb`, and `koval-crm-backend:v20260427barrelc`, and the existing VPS `deploy-prod.sh backend` path.
