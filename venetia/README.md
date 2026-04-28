# Venetia Email Worker

Status: live header-only polling; action policy gated
Created: 2026-04-27 CDT

This workspace is for the `venetia@thecultivater.com` email worker.

## Current State

- Private credentials are stored outside git under `.private/email-workers/venetia/credentials.txt`.
- IMAP and SMTP authentication were verified against the supplied mail server on 2026-04-27 without listing mailbox contents.
- Live header-only polling is enabled through `system/com.koval.venetia-auto`.
- Mailbox body reads, automatic filing, delete/archive behavior, and send automation are not enabled yet.
- Avignon is the managing assistant for this worker until Robert gives a different chain of command.
- Sonat's Venetia directive/persona packet is incorporated in `PERSONA.md`.

## Setup Boundary

This worker must not reuse Frank's Robert-facing persona or Avignon's Sonat-facing persona. Shared Frank/Avignon mechanics may be reused only as mechanics: source tracking, visible-worker routing, duplicate protection, approval gates, completion reports, and handled-mail filing after work is truly complete.

Before body reads, filing, external replies, or routine action authority start, Robert still needs to approve the action policy: primary owner/report target, allowed routine actions, external-send policy, filing policy, and escalation path.
