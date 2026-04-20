# Shared Email-Worker How-To Memory

Status: active shared docs path
Owner: AI Workspace Task Manager / Email Coordinator
Applies to: Frank and Avignon email-worker how-to notes
Created: 2026-04-20

## Purpose

Use this directory for reusable, non-secret email-worker how-to notes that apply to both Frank and Avignon, or that should be mirrored between them after persona-specific review.

This is a shared memory path for mechanics, not a mailbox archive. Do not copy forwarded private mailbox bodies, customer/vendor private content, credentials, tokens, app passwords, OAuth details, private keys, `.env` values, private SOP text, or operational bypass instructions into this directory.

## What Belongs Here

- Reusable classification patterns for internal email-derived tasks.
- Safe routing mechanics that apply to both Frank and Avignon.
- Non-secret checklists for captured/routed acknowledgements, completion reports, blocker reports, duplicate protection, and handled-mail filing.
- Sanitized examples written from scratch using placeholder names, when an example would prevent repeated mistakes.
- Links or trace references to local non-secret TODO/HANDOFF/project-hub records.

## What Does Not Belong Here

- Raw forwarded email content unless it is already explicitly non-secret in local docs.
- Private mailbox excerpts or body dumps.
- Secrets, credential paths, passwords, tokens, OAuth grants, private keys, or `.env` values.
- Avignon's private Sonat SOP text or Frank/Robert private mailbox content.
- Runtime, LaunchAgent, mailbox-cadence, OAuth/auth, production, deploy, or external-send instructions that have not been separately approved.

## Naming Rules

Name files with a date, a short topic, and the worker scope:

```text
YYYY-MM-DD-shared-<topic>.md
YYYY-MM-DD-frank-to-avignon-<topic>.md
YYYY-MM-DD-avignon-to-frank-<topic>.md
```

Use `shared` only when the guidance is persona-neutral mechanics. Use `frank-to-avignon` or `avignon-to-frank` when one worker's lesson needs review before being mirrored.

## Ownership Rules

- AI Workspace Task Manager or Email Coordinator owns this directory and decides whether a note is truly shared.
- Frank may propose or add notes for Robert-facing lessons that are reusable, then must keep Robert-specific voice and private context out of the shared note.
- Avignon may propose or add notes for Sonat-facing lessons that are reusable, then must keep Sonat-specific persona, private SOP text, and private account context out of the shared note.
- Security Guard reviews any note that touches suspicious mail, credential/auth boundaries, external-sensitive sends, private mailbox content risk, or cross-system access.
- Code/Git Manager is needed only if the change becomes a code/runtime/git closeout task. Normal docs-only notes in this directory do not imply commit/push approval.

## How Frank And Avignon Should Use It

1. Before creating a new how-to from an email-derived lesson, check this directory for an existing shared note.
2. If the lesson is reusable and non-secret, add a concise note here or ask Task Manager/Email Coordinator to add it.
3. Record the source `Message-ID`, session id/title, and any related local TODO/HANDOFF references as trace metadata only.
4. Keep worker-specific persona and recipient behavior in `frank/` or `avignon/` docs. Link to the shared note instead of duplicating shared mechanics.
5. If private source content is needed to understand the lesson, keep it in the approved private source path and write only a sanitized rule here.

## Current Source Reference

- Source Message-ID: `<CAAtX44a6UFPuHJd7tn83fsMjAiV+mbesOk35=r23yDTvY4u=bw@mail.gmail.com>`
- Source subject: `Fwd: Activity check`
- Routed worker session: `0a741b92` / `Shared email-worker how-to memory path`
- Related visible Avignon Activity check sessions found in Workspaceboard status during this task on 2026-04-20: `77ab92b0`, `b41fd0c0`, `302c78cd`, `872a7398`, `e2e4211f`, `f026a3fe`, `b606a500`, `77c34016`

The related Avignon sessions were recorded as visible references only. They were not closed, steered, or treated as completed by this docs task.

## Current Notes

- `2026-04-20-shared-captured-routed-receipts.md`: non-secret Frank/Avignon captured-routed receipt parity finding, including the Avignon direct-owner runtime-patch source of the newer receipt behavior and the approval-gated Frank runtime path if parity is required.
