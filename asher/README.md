# Asher Email Worker

Status: live body-read polling; approved send automation active; filing/deletes still gated
Created: 2026-04-27 CDT

This workspace is for the `asher@thecultivater.com` email worker.

## Current State

- Private credentials are stored outside git under `.private/email-workers/asher/credentials.txt`.
- IMAP and SMTP authentication were verified against the supplied mail server on 2026-04-27 without listing mailbox contents.
- Live body-read polling is enabled through `system/com.koval.asher-auto`.
- Approved send automation and owner-question drafting are enabled through the worker runtime for approved task-specific sends.
- Mailbox filing, delete/archive behavior, and routine authority remain gated.
- Avignon is the managing assistant for this worker until Robert gives a different chain of command.
- Canonical persona source for calls/drafts/reviews: `../worker_roles/asher-wilde/persona.yaml`.
- Companion readable persona note: `PERSONA.md`.

## Setup Boundary

This worker must not reuse Frank's Robert-facing persona or Avignon's Sonat-facing persona. Shared Frank/Avignon mechanics may be reused only as mechanics: source tracking, visible-worker routing, duplicate protection, approval gates, completion reports, and handled-mail filing after work is truly complete.

Before filing, delete/archive, or routine action authority start, Robert still needs to approve the action policy: primary owner/report target, allowed routine actions, filing policy, and escalation path. Approved send automation is already active for task-specific sends.
