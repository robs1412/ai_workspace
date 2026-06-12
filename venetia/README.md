# Venetia Email Worker

Status: live body-read polling; approved send automation active; current Avignon/Sonat finish contract active
Created: 2026-04-27 CDT

This workspace is for the `venetia@thecultivater.com` email worker.

## Current State

- Private credentials are stored outside git under `.private/email-workers/venetia/credentials.txt`.
- IMAP and SMTP authentication were verified against the supplied mail server on 2026-04-27 without listing mailbox contents.
- Live body-read polling is enabled through `system/com.koval.venetia-auto`.
- Approved send automation and owner-question drafting are enabled through the worker runtime for approved task-specific sends.
- Safe filing/archive authority is limited to exact duplicates, no-action residue, already-sent self-copies, and proof-backed handled source copies; delete behavior remains prohibited.
- Current routine authority covers approved sends, Sonat owner-question/blocker packets, no-action/source-proof recording, and visible Workspaceboard/Task Flow routing for substantive work.
- Avignon is the managing assistant for this worker until Robert gives a different chain of command.
- Canonical persona source for calls/drafts/reviews: `../worker_roles/venetia-tempest-dunn/persona.yaml`.
- Companion readable persona note: `PERSONA.md`.

## Setup Boundary

This worker must not reuse Frank's Robert-facing persona or Avignon's Sonat-facing persona. Shared Frank/Avignon mechanics may be reused only as mechanics: source tracking, visible-worker routing, duplicate protection, approval gates, completion reports, and handled-mail filing after work is truly complete.

Current owner/report target is Sonat through Avignon-managed workflow unless Robert explicitly changes the chain. Automatic replies, unapproved external sends, credential/auth changes, destructive/bulk actions, and hidden substantive execution remain out of scope.
