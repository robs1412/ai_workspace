# AI Workers Setup Calendar / Auth Matrix

Project: `AI-INC-20260501-AI-WORKERS-SETUP-01`
Date: 2026-05-17 CDT
Scope: non-secret planning/readback only

## Purpose

Capture the current source-backed calendar path for each worker lane, the intended target, the auth/storage boundary, and the next safe approved action.

## Matrix

| Worker / lane | Calendar target | Current source-backed status | Intended status | Source docs | Auth / storage boundary | Next approved action |
| --- | --- | --- | --- | --- | --- | --- |
| Frank | Robert calendar | Verified through Frank helper/config path. Robert shared his calendar to `frank.cannoli@kovaldistillery.com`, and Frank-side readback already showed Robert calendar visibility. | Frank can use Robert calendar for approved lookups, reminders, and follow-ups. | `frank/GOOGLE_CALENDAR_SETUP.md`; `frank/TODO.md`; `frank/HANDOFF.md` | Frank desktop OAuth client and machine-local Frank token only. Keep token off synced workspace docs. | No auth change needed for planning. Open a separate narrow runtime lane only if broader default reporting or mutation behavior is wanted. |
| Frank | Frank own calendar | Partially sourced. Frank account is the consent identity, but this pass did not find a separate readback line proving a Frank-primary event workflow. | Frank-owned reminder and follow-up path when a workflow should use Frank's own calendar rather than Robert's. | `frank/GOOGLE_CALENDAR_SETUP.md`; `frank/AGENTS.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Same Frank client/token path as above. | Do one narrow helper readback against the Frank primary calendar before claiming this path as verified. |
| Avignon | Sonat calendar | Verified only through the Frank helper route. Shared docs permit an Avignon-specific individual path, but no separate Avignon helper/runtime is source-verified today. | Avignon should support Sonat reminders and follow-ups, either through the verified Frank helper path or a separately approved Avignon path. | `frank/TODO.md`; `frank/HANDOFF.md`; `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Current verified visibility depends on the Frank machine-local client/token path. A separate Avignon helper/runtime is a new auth/runtime slice. | Keep using the verified Frank-helper route for planning/readback. If a separate Avignon helper is required, route Security Guard and Code/Git Manager review first. |
| Avignon | Avignon own calendar | Not source-verified. Shared docs allow it when available, but no distinct Avignon-primary helper/readback is named in current non-secret sources. | Avignon-owned reminder path if a separate Avignon calendar becomes part of the approved workflow. | `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Would require a separate Avignon auth/runtime slice if not routed through the existing Frank helper path. | Keep blocked until a distinct Avignon calendar/helper is actually sourced and approved. |
| National Outreach / Vanessa | `KOVAL Outreach Events` | Verified. Existing Outreach reminder/calendar work already uses the OPS-linked `KOVAL Outreach Events` path. | Shared Outreach calendar for tasting follow-up, team reminders, and calendar-backed Outreach organization. | `nationaloutreach/WHOLE_FOODS_TASTING_PLANNING.md`; `nationaloutreach/TODO.md`; `nationaloutreach/HANDOFF.md` | Existing National Outreach machine-local runtime/auth path. | No new auth decision is needed for planning. Use existing shared Outreach path for approved reminder workflows. |
| Naomi | Shared National Outreach calendar lane | Policy-defined, not separately verified in this pass. Shared docs route Naomi-owned reminders through shared reminder/calendar support when needed. | Shared reminder/calendar support for Naomi tasks that need calendar backing. | `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Shared National Outreach helper path, not a Naomi-specific client. | Keep as shared-lane planning until a Naomi-specific reminder workflow needs a concrete readback. |
| Ezra | Shared National Outreach calendar lane | Policy-defined, not separately verified in this pass. Shared docs route Ezra-owned reminders through shared reminder/calendar support when needed. | Shared reminder/calendar support for Ezra tasks that need calendar backing. | `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Shared National Outreach helper path, not an Ezra-specific client. | Keep as shared-lane planning until an Ezra-specific reminder workflow needs a concrete readback. |
| Customer Service | `customerservice@kovaldistillery.com` local OPS event-support candidate | Partially sourced. The current local OPS event-support path points to `customerservice@kovaldistillery.com`, but no separate calendar/helper path is documented yet. | A dedicated or shared calendar path only if Customer Service later needs calendar-backed reminders. | `project_hub/issues/2026-05-01-ai-workers-setup.md`; `ops/event_support/action_handler.php` | No approved auth/calendar path yet; mailbox identity is locally sourced but answer-authority and any calendar-helper path remain undefined. | Keep blocked until the FOH answer source is named and any real reminder/calendar need is approved. |

## Exact Remaining Gaps

- Frank-own-calendar workflow still needs one narrow readback proof.
- A separate Avignon helper/runtime remains unsourced and would need a new auth/runtime approval slice.
- Customer Service now has a local inbox candidate, but still has no named FOH answer source or approved auth/calendar path.

## Boundary

- No calendar event bodies were read.
- No events were created, edited, or deleted.
- No OAuth scope, token storage, or runtime change was performed.
