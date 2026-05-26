# Shared Same-Thread Reply Behavior

Status: active shared directive
Owner: AI Workspace Task Manager / Email Coordinator
Applies to: Frank, Avignon, National Outreach, Vanessa, Naomi, Ezra, Asher, Venetia, Codex-routed mail, and future approved email-worker personas
Created: 2026-05-23

## Rule

When an email worker replies on an existing thread, the outbound message must stay on that thread instead of starting a fresh branch.

Required mechanics:

- set `In-Reply-To` to the current owner/source message being answered;
- set `References` to preserve the active thread chain that the owner is using;
- prefer the newest direct-owner message in the active thread as the reply anchor when the owner is correcting, clarifying, or advancing earlier work;
- if the worker is sending a completion or blocker report after routed work, send it on the same owner thread unless a safety gate requires a new thread.

## What This Prevents

- branching a direct-owner correction into a new thread after the owner already replied in place;
- sending a technically correct answer that later readers cannot match to the active mailbox thread;
- losing the newest owner correction because the durable note or report only reflects earlier thread state.

## Durable Note Requirement

If a later owner reply changes the intended route, role split, or next action, update the durable note before reporting completion so the final report and the durable note reflect the same newest correction.

## Classification

- `shared mechanic`

## Trace Metadata

- Source Message-ID: `<CAAtX44aeQrB3hmqSeE3VNJ0HdvTqrPRbYb6X=iy=U=sQXzoaTg@mail.gmail.com>`
- Dedupe key: `frank-direct-primary-CAAtX44aeQrB3hmqSeE3VNJ0HdvTqrPRbYb6X-iy-U-sQXzoaTg-mail-gmail-com`
- Workspaceboard session: `37effcf5` / `Frank direct Robert: Re: Blocked: naomi.stern@kovaldistillery.com: KOVAL AI Secretary & PM Agent`
- Classification reason: Robert's latest correction widens the thread-preservation fix from one Frank reply into a reusable all-email-worker mechanic.

## Current Implementation Note

The installed Frank and Avignon sender helpers now accept explicit reply headers, and the active Frank plus Avignon direct-owner closeout paths pass the current source thread through `In-Reply-To` and `References` instead of emitting a fresh unthreaded completion, blocker, or captured reply.

The other installed email-worker runtimes already carry the same thread headers through their active send paths:

- National Outreach uses `nationaloutreach_mail_cycle.py` and `email_worker_header_poll.py` to preserve `In-Reply-To` and `References`.
- Asher uses `email_worker_header_poll.py` to preserve `In-Reply-To` and `References`.
- Venetia uses `email_worker_header_poll.py` to preserve `In-Reply-To` and `References`.

As of Robert's follow-up approval on the same assessment thread, treat this as an installed shared runtime mechanic across the active email-worker lanes rather than a Frank-only or Avignon-only exception.

This slice is:

- `shared mechanic` for the cross-worker reply-thread rule
- `runtime change` for the installed sender and worker paths that enforce that rule automatically
