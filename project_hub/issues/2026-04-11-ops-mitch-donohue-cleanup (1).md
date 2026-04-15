# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260411-OPS-MITCH-DONOHUE-CLEANUP-01
- Date Opened: 2026-04-11
- Date Completed: 2026-04-11
- Owner: Codex / OPS
- Priority: Medium
- Status: Completed

## Scope

OPS-only investigation for stale Mitch/Mitchell Donohue visibility after departure from KOVAL.

## Symptoms

Example event `Voucher Private Tour Monika Swift` on 2026-04-10 15:00-16:00 still lists `Mitchell Donohue (Store)` as staff.

## Root Cause

No hardcoded OPS repo references to Mitch/Mitchell/Donohue were found. The visible name is coming from live DB assignment rows tied to inactive/deleted CRM users:

- CRM user `1241` `mitchelldonohue` / `Mitchell Donohue (Store)` is `Inactive`, `deleted=1`.
- CRM user `1295` `mitchelldonohue-bartender` / `Mitch Donohue (Bartender)` is `Inactive`, `deleted=1`.
- CRM user `1301` `mitchelldonohue-barback` / `Mitchell Donohue (Barback)` is `Inactive`, `deleted=1`.

## Repo Logs

### ops

- Repo Log ID: OPS-20260411-MITCH-DONOHUE-CLEANUP
- Commit SHA: pending
- Commit Date: pending
- Change Summary: Fast-forwarded local `main` to `origin/main`, preserved existing local Outreach changes, then performed approved live DB cleanup of stale Donohue event staff/host and active task assignee rows.

## Verification Notes

Dry-run counts from 2026-04-11:

- `event_booking_staff`: user `1241` has 159 total rows, 18 today/future rows, 25 rows in the recent-7-days-plus-future window. Users `1295` and `1301` have 0 event staff rows.
- `event_bookings.event_host_user_id`: user `1241` has 163 total rows, 17 today/future rows, 24 rows in the recent-7-days-plus-future window. Users `1295` and `1301` have 0 event host rows.
- `event_booking_tasks.assigned_user_id`: user `1241` has 2 total rows, 0 today/future event rows. Users `1295` and `1301` have 0 rows.
- `koval_tracktime.shift2user`: user `1241` has 88 total rows, user `1295` has 1 total row, user `1301` has 53 total rows; all are historical with 0 future/current active shift rows.
- `koval_crm.activity2user`: user `1241` has 54 active task assignee rows across all due dates, 38 active task assignee rows in the recent-7-days-plus-future/null-due window, and 34 active task assignee rows due today/future.
- `koval_crm.vtiger_crmentity` task ownership: user `1241` has 129 active task owner rows across all due dates, but 0 in the recent-7-days-plus-future/null-due window.
- Example event lookup confirmed event id `504` includes `Christina Pinciotti #1253`, `Jack Dempsey #1167`, and `Mitchell Donohue (Store) #1241`.

DB cleanup committed on 2026-04-11:

- Deleted 25 `event_booking_staff` rows for Donohue users in the `2026-04-04+` operational window.
- Updated 24 `event_bookings.event_host_user_id` rows to `NULL` for Donohue users in the `2026-04-04+` operational window.
- Updated 2 `event_booking_tasks.assigned_user_id` rows to `NULL`.
- Deleted 54 active `koval_crm.activity2user` task assignee rows for Donohue users.
- Rollback SQL captured at `project_hub/issues/2026-04-11-ops-mitch-donohue-cleanup-rollback.sql`.

Post-cleanup verification:

- `event_booking_staff` Donohue rows in the `2026-04-04+` window: 0.
- `event_bookings.event_host_user_id` Donohue rows in the `2026-04-04+` window: 0.
- `event_booking_tasks.assigned_user_id` Donohue rows: 0.
- Active `koval_crm.activity2user` Donohue rows: 0.
- Event `504` (`Voucher Private Tour Monika Swift`, 2026-04-10 15:00-16:00) now has `event_host_user_id = NULL` and staff `Christina Pinciotti #1253, Jack Dempsey #1167`.
- Residual note: 129 active `koval_crm.vtiger_crmentity.smownerid` owner rows remain for user `1241`; none are in the recent-7-days-plus-future/null-due window, and they were not changed because task ownership needs an explicit replacement owner.

## Rollback Plan

Use `project_hub/issues/2026-04-11-ops-mitch-donohue-cleanup-rollback.sql` to restore the exact deleted/updated event staff, event host, event task, and CRM assignee rows if needed.

## Follow-Ups

- Decide whether the 129 remaining active CRM task owner rows for `smownerid = 1241` should be reassigned to a specific active owner; no recent/future/null-due owner rows were found.
