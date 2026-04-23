# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260423-AVIGNON-CALENDAR-DEDUPE-01`
- Date Opened: `2026-04-23`
- Date Completed: `2026-04-23`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Completed`

## Scope

Deploy the Avignon calendar-directive dedupe fix so Sonat does not receive repeated `Meeting with Robert scheduled` confirmations when the same meeting slot is reprocessed.

## Symptoms

Avignon could find an existing Sonat/Robert calendar event and still send another confirmation email with the same `Done. I created the Monday morning meeting with Robert.` wording. Sonat replied on April 23, 2026 that Avignon had already said this a number of times.

## Root Cause

The Sonat/Robert calendar-directive path deduped event creation but not owner confirmation sends. When an existing event was found, the runtime still called the confirmation sender instead of checking whether that meeting slot had already been confirmed.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260423-AVIGNON-CALENDAR-DEDUPE-01`
- Commit SHA: `uncommitted`
- Commit Date: `2026-04-23`
- Change Summary: patched the Avignon source mirror and local planning records so calendar confirmations are deduped by slot-specific task id.

### machine-local Avignon runtime

- Repo Log ID: `AI-INC-20260423-AVIGNON-CALENDAR-DEDUPE-01`
- Commit SHA: `n/a`
- Commit Date: `2026-04-23`
- Change Summary: patched `/Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py` so the installed runtime skips confirmation sends when the same meeting slot already has a sent-log record.

## Verification Notes

- `python3 -m py_compile /Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py /Users/werkstatt/ai_workspace/avignon/runtime-source/avignon-launch/scripts/avignon_inbox_cycle.py`
- Confirmed the installed runtime now contains `calendar_confirmation_task_id()`, `calendar_confirmation_already_sent()`, and sent-log checks before the existing-event and event-created confirmation sends.
- Confirmed the installed/runtime source diff for this slice is reduced to an unrelated older quick-answer prompt line, not the calendar dedupe logic.
- Confirmed scheduled Frank and Avignon overview LaunchDaemons are healthy enough to leave as-is: both `system/com.koval.frank-morning-overview` and `system/com.koval.avignon-morning-overview` show `runs = 2`, `last exit code = 0`, and fresh `06:00` output logs on `2026-04-23`.

## Rollback Plan

Restore the previous `/Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py` logic from local history or source mirror if the slot-based dedupe suppresses a confirmation that should be sent. No database, mailbox state, or calendar event mutation needs rollback for this slice.

## Follow-Ups

- If desired later, sync the unrelated quick-answer acknowledgement prompt line from the source mirror into the installed `/Users/admin` runtime in a separate approved slice.
- Keep Gmail push/OAuth work parked until Robert provides the missing token-storage and OAuth approvals.
