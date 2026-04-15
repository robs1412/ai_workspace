# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260302-OPS-SHIFT-PARENTID-01
- Date Opened: 2026-03-02
- Date Completed: 2026-03-02
- Owner: Codex
- Priority: P1
- Status: Completed

## Scope

Fix live shift creation failures after quick-create rollout.

## Symptoms

- On create shift from new calendar quick-create button: 
  - `SQLSTATE[23000]: Integrity constraint violation: 1048 Column 'parent_id' cannot be null`

## Root Cause

- Live `koval_tracktime.shifts.parent_id` rejects `NULL`.
- Several shift insert paths in `action_handler.php` used `parent_id = NULL` or nullable parent values.

## Repo Logs

### ops

- Repo Log ID: OPS-2026-03-02-SHIFT-PARENTID
- Commit SHA: bb9358b
- Commit Date: 2026-03-02
- Change Summary:
  - Set non-null parent defaults for shift inserts (`parent_id = 0`) in quick-create and related copy/generate paths.
  - Coerced nullable parent values to `0` before inserts.

## Verification Notes

- `php -l action_handler.php` passes.
- User should retest quick-create and outreach/create-copy flows.

## Rollback Plan

- Revert commit in `ops` and pull live if any regressions appear.

## Follow-Ups

- Add integration coverage for DB schemas where `shifts.parent_id` is NOT NULL.
