# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260316-OPS-RECURRING-POSTPONE-01`
- Date Opened: `2026-03-16`
- Date Completed: `2026-03-16`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Fix OPS recurring-task postpone drift where daily tasks could jump forward by one week instead of one day when the submit path lost recurrence context.

## Symptoms

- Mark reported that a task configured as `Daily` moved from `2026-03-16` to `2026-03-23`.
- Data History on task `#358756` showed both `Start Date` and `Due Date` advancing by 7 days even though the task recurrence remained `Daily`.
- The issue could recur when OPS had to recompute the next due date server-side from an incomplete CRM detail payload.

## Root Cause

- `action_handler.php` `postpone_task` trusted the CRM `/tasks/{id}` detail response as the source of truth for recurrence.
- Some submit paths could reach the handler without a populated `next_due_date`, and the CRM detail payload is not guaranteed to carry `recurringtype` in a stable shape.
- When recurrence was missing, OPS defaulted to `+7 days`, which is correct for weekly tasks but wrong for daily tasks.

## Repo Logs

### ops

- Repo Log ID: `OPS-2026-03-16-RECURRING-POSTPONE`
- Commit SHA: `7a6f306`
- Commit Date: `2026-03-16`
- Change Summary:
  - added recurrence-label extraction helpers in `action_handler.php` so `postpone_task` prefers explicit UI recurrence context before falling back to CRM detail fields.
  - updated dashboard postpone forms in `start.php` to always submit both `recurring_type` and `next_due_date`, including dynamically rendered task rows.
  - updated `tasks.php` AJAX postpone requests to include `recurring_type`.
  - recorded the completed fix in `TODO.md`.

## Verification Notes

- `php -l /Applications/MAMP/htdocs/ops/action_handler.php`
- `php -l /Applications/MAMP/htdocs/ops/start.php`
- `php -l /Applications/MAMP/htdocs/ops/tasks.php`
- Direct local DB inspection of task `#358756` confirmed:
  - `recurringtype = Daily`
  - post-incident due/start date currently stored as `2026-03-23`
- Browser automation reached `http://localhost/login/index.php?referrer=ops%2Fstart.php`, but the local automation session did not advance beyond the login form during this turn, so functional browser confirmation of the postpone click remains pending.
- Local code-path verification confirms the fixed handler now resolves `Daily` cadence from explicit submit payloads instead of falling back to weekly when CRM detail recurrence is absent.
- Live deployment:
  - `2026-03-16 22:28:18 CDT`
  - host: `ftp.koval-distillery.com`
  - path: `/home/koval/public_html/ops`
  - `git pull --ff-only origin main` fast-forwarded cleanly from `a88d9f1` to `7a6f306`
  - live HEAD: `7a6f30676c8a1efa128095e418c3794618ad84bd`

## Rollback Plan

- Revert ops commit `7a6f306` if recurring-task postpone behavior regresses.
- Temporary fallback: keep the previous submit path and force all recurring postpones to require a client-provided `next_due_date`.

## Follow-Ups

- Re-run browser verification against localhost with a working automation login session and confirm a daily recurring task advances by exactly one day.
- If any remaining drift reports appear, log the raw `/tasks/{id}` detail payload shape for affected tasks without exposing secrets.
