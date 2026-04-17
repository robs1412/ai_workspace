# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260416-EVENT-STRATEGY-COT-CONNECTEAM-01`
- Date Opened: `2026-04-16`
- Date Completed: `2026-04-16`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Source-context review completed; direct MacBook retrieval unavailable in this session`

## Scope

Read-only AI Workspace coordination review for event strategy notes and the COT/Connecteam replacement plan. Source requested:

- `https://docs.google.com/document/d/1EaHH97GJ_9ztMNtWaEp-abGUHdVqVcyvJWkUjko5euc/edit?tab=t.0`

Guardrails observed: no Google Docs mutation, credential request, OPS/Papers/Connecteam/notification/production-data access, code change, commit, push, deploy, or runtime change.

## Source Access

The Google Doc export endpoint was reachable but not anonymously readable. A read-only `curl` request to the text export URL returned `HTTP/2 401` and a Google sign-in/cookie-access page instead of document text.

Robert later supplied the source Markdown path:

- `/Users/robert/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/Downloads - shared/Implentation of Scheduling  .md`

Continuation check on 2026-04-16:

- The exact `/Users/robert/...` path was not present on this Mac mini.
- `MacBookPro.lan` did not resolve.
- SSH to `robert@192.168.55.180` timed out.

The direct source file could therefore not be read from the MacBook in this session.

However, OPS already contains a read-only incorporation of the relevant non-sensitive source context from that Markdown note. `ops/docs/2026-04-16-outreach-readiness-report.md` records that Robert supplied the source path on the M4 as:

- `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/Downloads - shared/Implentation of Scheduling  .md`

That OPS note records that the file was retrieved read-only over SSH from `kovaladmin@192.168.55.35` on 2026-04-16 and that one credential line was intentionally excluded. This AI Workspace review uses only the non-sensitive workflow content already incorporated into `ops/docs/2026-04-12-outreach-events-workflow-manual.md`, not the excluded credential material.

## Local Context Found

Local AI Workspace notes contain enough prior context to route an OPS-safe discovery slice:

- `project_list-import.txt` lists "Mark Ideas for events", "Manage COT team out of OPS", "replace Connecteam!", and market improvements around account/contact creation in OPS.
- `PROJECT_TODOS.md` frames the Connecteam replacement as OPS MVP parity for tasks, shifts, notifications, and check-ins.
- `TODO.md` tracks the implementation goal as Events plus Market Events parity, one-or-more linked shifts, existing shift-notification behavior, Connecteam replacement, account/login/activity linkage, and no second user system.
- `project_hub/issues/2026-04-09-ops-connecteam-outreach-visibility.md` records that prior staged Connecteam outreach imports normalized 151 rows and matched 151 OPS events plus linked shifts after the outreach calendar visibility fix.
- `trainual/ops-market-events/outline.md` defines the current Market Events user-facing concepts: event records, calendar/list navigation, linked shifts or staffing details, before-event checks, after-event updates, and avoiding duplicate accounts/contacts.
- `ops/docs/2026-04-12-outreach-events-workflow-manual.md` contains the relevant non-sensitive scheduling context from the supplied Markdown source: request and confirmation sources, fields OPS should preserve, staffing workflow, notification/reminder behavior, change/cancellation handling, Connecteam weaknesses, and future feature candidates.
- `ops/docs/2026-04-16-outreach-readiness-report.md` confirms that the supplemental source was retrieved read-only and that credential material was excluded.

## Actionable Strategy Points

- Treat OPS as the target operational surface for COT/event work instead of adding a second user system.
- Preserve existing shift-notification behavior while extending event support; replacement planning should start from parity rather than a new workflow.
- Model Events and Market Events together enough that users understand whether a record is a market-facing event, an outreach/event record, or a linked shift.
- Support one-or-more linked shifts per event and make staffing/check-in state visible from the event surface.
- Keep account, contact, activity, and login linkage explicit. OPS can be the working surface, but reporting/data ownership boundaries with Salesreport should be defined before implementation.
- Use existing Connecteam staging/parity checks as the baseline for future import/replacement verification.
- Use Trainual/user enablement notes to reduce confusion before or alongside implementation, especially around filters, linked shifts, after-event updates, and duplicate account/contact avoidance.
- Preserve source-specific tasting request flows:
  - Binny's tastings are requested about one month ahead through Rene Paquin, then confirmed with locations, dates, and times.
  - Whole Foods tastings use the WFM demo portal and approval/confirmation email.
  - Mariano's tastings use a demo request form emailed to ABS tasting contacts.
- Preserve required event fields in OPS: CRM account name, account address, tasting date/time, SKUs, SKU or seasonal focus, buyer name when known, and linked account/contact/activity context.
- Support the actual COT staffing model: staff usually choose their own shifts, management fills gaps, OND may require manager assignment to maximize coverage, territory/radius matters, and far-travel tastings should be confirmed before assignment.
- Notification/reminder parity needs more than a generic shift alert. Expected reminder points are 24 hours before, 1 hour before, and at tasting start time; admins should be notified when shifts are claimed, confirmed, unclaimed, or rejected.
- Unclaimed/rejected shifts should return to the open pool. Tastings still unclaimed two days before the event are candidates for cancellation or rescheduling.
- A known Connecteam weakness is unreliable manager notification when someone unclaims; OPS should make that case explicit rather than reproducing the weakness.
- Future candidates remain context until approved: separate Outreach calendar, group/individual messaging, confirm/deny/pick-up/swap actions, multiple staff per event or shift, reusable shift templates, batch upload, user-managed unavailability, mobile-friendly staffing, and an activity-report prompt before clock-out.

## Next OPS-Safe Steps

1. Treat the original Google Doc blocker as unblocked for planning because the supplied Markdown-derived scheduling context is now represented in OPS docs and summarized here.
2. In `ws ops`, continue only with implementation design or read-only dry-run follow-up until Robert approves final sync/live schedule/notifications/auth/canonical-rule changes.
3. Resolve the current approval decisions already tracked in `TODO.md`: zero-shift hard-block vs tentative holds, open-shift notification groups, claim approval behavior, unclaim cutoff, reminder channels/timing, final Connecteam re-sync/export timing, reviewed user crosswalk, and canonical account/activity rules.
4. Produce a proposed implementation plan with file ownership, data ownership, migration/import verification, and approval gates before any new code or data mutation.
5. Bring in Code and Git Manager before implementation. Bring in Security Guard only if auth/access, credentials, production data mutation, external sends, or approval-gated surfaces enter scope.

## Verification Notes

- Read `TODO.md` and `ToDo-append.md`.
- Confirmed the append queue is empty.
- Confirmed the Google Doc text export returned `HTTP/2 401`.
- Searched local AI Workspace notes for `Connecteam`, `COT`, `event strategy`, `Market Events`, linked shifts, shift notifications, and replacement-plan terms.
- Continuation on 2026-04-16 checked the Robert-supplied `/Users/robert/.../Implentation of Scheduling  .md` path locally, attempted `MacBookPro.lan`, and attempted `robert@192.168.55.180`; the MacBook source was not reachable.
- Read the OPS-incorporated supplemental scheduling context in `ops/docs/2026-04-12-outreach-events-workflow-manual.md` and source-handling note in `ops/docs/2026-04-16-outreach-readiness-report.md`.
- Scope stayed docs-only in `/Users/werkstatt/ai_workspace`.

## Follow-Ups

- The original event strategy source blocker can be closed for AI Workspace planning because the relevant non-sensitive Markdown-derived scheduling content is now summarized here with source attribution.
- The direct MacBook retrieval issue remains a separate machine reachability problem, not a blocker to this strategy review, because OPS already recorded the read-only source incorporation and excluded credential material.
- OPS implementation must still wait on the recorded product/approval decisions before final sync, live schedule, notifications, auth/access work, canonical rule changes, or data mutation.
