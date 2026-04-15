# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260302-OPS-SHIFT-ACCOUNTID-01
- Date Opened: 2026-03-02
- Date Completed: 2026-03-02
- Owner: Codex
- Priority: P1
- Status: Completed

## Scope

Fix live shift creation failures where `account_id` was inserted as `NULL` from quick-create and related shift flows.

## Symptoms

- On create shift from calendar/outreach/new shift paths:
  - `SQLSTATE[23000]: Integrity constraint violation: 1048 Column 'account_id' cannot be null`

## Root Cause

- Live `koval_tracktime.shifts.account_id` rejects `NULL`.
- Multiple shift insert/update paths in `action_handler.php` still used nullable account/activity values:
  - hardcoded `NULL, NULL` for `(account_id, activity_id)` in some insert statements
  - template copy/create paths passing nullable `account_id` / `activity_id`

## Repo Logs

### ops

- Repo Log ID: OPS-2026-03-02-SHIFT-ACCOUNTID
- Commit SHA: 998f42b
- Commit Date: 2026-03-02
- Change Summary:
  - Replaced remaining `NULL` defaults with `0` for `(account_id, activity_id)` in shift create inserts.
  - Coerced template-derived `account_id` / `activity_id` to integer `0` when source values are null.
  - Updated template save/copy account handling to persist `0` instead of `NULL`.

## Verification Notes

- `php -l action_handler.php` passes.
- Commit pushed and pulled live (`origin/main` -> live OPS).
- `ops/error_log` shows prior `account_id` errors before deploy; user retest required to confirm no new occurrences.

## Rollback Plan

- Revert commit `998f42b` in `ops` and pull live if regressions appear.

## Follow-Ups

- Add schema-aware guardrails/tests for NOT NULL columns in `koval_tracktime.shifts` (`parent_id`, `account_id`, `activity_id`).
