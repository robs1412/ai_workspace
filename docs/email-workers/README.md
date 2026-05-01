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

## Owner-Facing Clarity Rule

Do not put opaque internal labels in owner-facing summaries, blocker emails, morning/evening updates, or Task Manager status lines. Source-index labels, Message-IDs, session IDs, task IDs, and internal blocker codes are trace references, not the explanation.

Write the plain-English business context first: person, company, account, requested action, current blocker, missing decision, recommended next step, and what the assistant will do after the answer arrives. If the business details are unknown, say that and ask for a simple human-readable packet or table instead of asking the owner to resolve an internal id.

## First-Person Self-Reference Rule

When an email worker writes as itself, it should refer to itself in the first person, not the third person. For example, write "here is my internal memo" instead of "here is Asher's internal memo" when the message is sent from Asher's persona. Names remain appropriate in signatures, role labels, headers, or when one worker is describing another worker.

## Current Source Reference

- Source Message-ID: `<CAAtX44a6UFPuHJd7tn83fsMjAiV+mbesOk35=r23yDTvY4u=bw@mail.gmail.com>`
- Source subject: `Fwd: Activity check`
- Routed worker session: `0a741b92` / `Shared email-worker how-to memory path`
- Related visible Avignon Activity check sessions found in Workspaceboard status during this task on 2026-04-20: `77ab92b0`, `b41fd0c0`, `302c78cd`, `872a7398`, `e2e4211f`, `f026a3fe`, `b606a500`, `77c34016`

The related Avignon sessions were recorded as visible references only. They were not closed, steered, or treated as completed by this docs task.

## Current Notes

- `2026-04-30-shared-intake-task-completion-flow.md`: canonical intake-to-closeout flow for terminal/chat, Workspaceboard, Frank, Avignon, National Outreach, Vanessa, Naomi, Ezra, Codex-routed mail, report-triggered work, OPS/Portal task storage, email clarifications, timed reminders/calendars, completion reports, and Papers projection packets.
- `2026-04-30-shared-inbox-zero.md`: shared inbox-zero directive for all email workers and approved send-from personas. Frank, Avignon, National Outreach, Vanessa, Naomi, Ezra, Asher, Venetia, Codex-routed mail, and future personas should keep active inboxes at `0` open / `0` unread by filing handled/no-action/duplicate/routed/completed mail out of the inbox while leaving only real blockers, decisions, or active dependencies open. Before filing, workers must investigate the safe full thread/body context, split multiple instructions into separate dispositions, and route account-access/finance/legal/auth setup through visible Task Manager/Workspaceboard lanes instead of hidden inbox work.
- `2026-04-30-shared-koval-signature-format.md`: shared non-secret signature-format mechanic for all approved email-worker personas. Emails close with `Best,`, blank line, worker first name, blank line, then the full signature block. KOVAL signatures keep the phone number, website, and linked `X | Instagram | Facebook` social-label set on separate lines; worker-specific voice and role titles stay in local persona docs, and runtime/send-helper changes remain separately approval-gated.
- `2026-04-30-shared-open-item-owner-email.md`: shared directive that recording open, missed, blocked, or waiting email-derived items is not enough. The responsible worker persona must email the owner with the business context, current state, exact decision/next action, and the original source email included for review, unless a safety gate blocks sending. Open dependency reminders need both durable task storage and an executable reminder surface; Frank and Avignon may use their individual Google Calendar paths when verified, while National Outreach uses the shared National Outreach calendar for Vanessa/Ezra/Naomi reminders when that helper path is available.
- `2026-04-30-shared-sample-request-notification-verification.md`: shared Frank/Avignon mechanic requiring Portal sample-request routes to verify notification delivery or return a blocker before completion.
- `2026-04-20-shared-captured-routed-receipts.md`: non-secret Frank/Avignon captured-routed receipt parity finding, including the Avignon direct-owner runtime-patch source of the newer receipt behavior and the approval-gated Frank runtime path if parity is required.
- 2026-04-20 follow-up `220cf4d4` confirmed the reusable template rule: owner-facing captured/routed acknowledgements for routed work must include the visible work session ID plus session title/task name after prompt delivery.
- 2026-04-22 Frank acknowledgement-delay correction: Frank direct-owner routed-work receipts are held for 10 minutes. If the worker completes or blocks first, send only the completion/blocker report; if still pending after 10 minutes, send one captured/routed receipt. Avignon runtime was not changed in this slice.
- 2026-04-22 follow-up `7e96ac60` recorded the acknowledgement-delay rule: hold direct primary-owner captured/routed receipts for 10 minutes, suppress them when completion/blocker closeout is ready first, and send one delayed receipt only if the worker is still pending.
- `2026-04-20-shared-reminder-approval-request-clarity.md`: non-secret reminder and approval-request clarity rule for Claude/bridge/email workers. Use a real approved Papers/work-record link when allowed, or a clear human-readable item description, requested approval, and safe next action. Do not send context-poor Message-ID-only reminders.
- 2026-04-22 clarification: Summary Worker, Frank, and Avignon must translate internal source labels into plain-English business context before owner-facing output. Example shape: "Stephen Beck already exists in CRM; decide whether to leave him as-is or link/update that existing contact under a named account," not an internal source-index blocker label.
- `2026-04-22-shared-email-worker-customization-boundary.md`: Frank and Avignon share mechanics, not persona. Robert approved automatic enforcement on 2026-04-22: classify each operating change as `shared mechanic`, `Frank customization`, `Avignon customization`, or `runtime change` before implementation. Shared routing/reporting/dedupe mechanics live here or in shared policy; Frank customization stays in Frank docs, Avignon customization stays in Avignon docs and must respect Sonat's SOP/persona references without exposing private source text.
- `2026-04-27-shared-first-person-self-reference.md`: all email workers and approved send-from personas should refer to themselves in first person when writing as themselves, such as "my internal memo" rather than "Asher's internal memo."
