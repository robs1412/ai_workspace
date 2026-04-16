# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260416-EVENT-STRATEGY-COT-CONNECTEAM-01`
- Date Opened: `2026-04-16`
- Date Completed: `2026-04-16`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Blocked on external source access; local coordination review completed`

## Scope

Read-only AI Workspace coordination review for event strategy notes and the COT/Connecteam replacement plan. Source requested:

- `https://docs.google.com/document/d/1EaHH97GJ_9ztMNtWaEp-abGUHdVqVcyvJWkUjko5euc/edit?tab=t.0`

Guardrails observed: no Google Docs mutation, credential request, OPS/Papers/Connecteam/notification/production-data access, code change, commit, push, deploy, or runtime change.

## Source Access

The Google Doc export endpoint was reachable but not anonymously readable. A read-only `curl` request to the text export URL returned `HTTP/2 401` and a Google sign-in/cookie-access page instead of document text.

Exact access needed before a full source review: a non-secret, read-only copy/export of the document text, or document sharing that allows this environment to read the doc without requesting or handling credentials.

## Local Context Found

Local AI Workspace notes contain enough prior context to route an OPS-safe discovery slice:

- `project_list-import.txt` lists "Mark Ideas for events", "Manage COT team out of OPS", "replace Connecteam!", and market improvements around account/contact creation in OPS.
- `PROJECT_TODOS.md` frames the Connecteam replacement as OPS MVP parity for tasks, shifts, notifications, and check-ins.
- `TODO.md` tracks the implementation goal as Events plus Market Events parity, one-or-more linked shifts, existing shift-notification behavior, Connecteam replacement, account/login/activity linkage, and no second user system.
- `project_hub/issues/2026-04-09-ops-connecteam-outreach-visibility.md` records that prior staged Connecteam outreach imports normalized 151 rows and matched 151 OPS events plus linked shifts after the outreach calendar visibility fix.
- `trainual/ops-market-events/outline.md` defines the current Market Events user-facing concepts: event records, calendar/list navigation, linked shifts or staffing details, before-event checks, after-event updates, and avoiding duplicate accounts/contacts.

## Actionable Strategy Points

- Treat OPS as the target operational surface for COT/event work instead of adding a second user system.
- Preserve existing shift-notification behavior while extending event support; replacement planning should start from parity rather than a new workflow.
- Model Events and Market Events together enough that users understand whether a record is a market-facing event, an outreach/event record, or a linked shift.
- Support one-or-more linked shifts per event and make staffing/check-in state visible from the event surface.
- Keep account, contact, activity, and login linkage explicit. OPS can be the working surface, but reporting/data ownership boundaries with Salesreport should be defined before implementation.
- Use existing Connecteam staging/parity checks as the baseline for future import/replacement verification.
- Use Trainual/user enablement notes to reduce confusion before or alongside implementation, especially around filters, linked shifts, after-event updates, and duplicate account/contact avoidance.

## Next OPS-Safe Steps

1. In `ws ops`, run a read-only discovery slice for current Events, Market Events, linked shifts, task/check-in/notification flows, and account/contact/activity linkage.
2. Compare the discovery result against MVP parity: tasks, shifts, notifications, check-ins, account/contact/activity linkage, and no second user system.
3. Produce a proposed implementation plan with file ownership, data ownership, migration/import verification, and approval gates before any code or data mutation.
4. Bring in Code and Git Manager before implementation. Bring in Security Guard only if auth/access, credentials, production data mutation, external sends, or approval-gated surfaces enter scope.

## Verification Notes

- Read `TODO.md` and `ToDo-append.md`.
- Confirmed the append queue is empty.
- Confirmed the Google Doc text export returned `HTTP/2 401`.
- Searched local AI Workspace notes for `Connecteam`, `COT`, `event strategy`, `Market Events`, linked shifts, shift notifications, and replacement-plan terms.
- Scope stayed docs-only in `/Users/werkstatt/ai_workspace`.

## Follow-Ups

- Task Manager can count one real blocker: the Google Doc needs read-only access or a supplied text export before the external-source strategy review can be completed.
- OPS implementation should not start from this note alone if the Google Doc contains requirements that are not represented in local AI Workspace notes.
