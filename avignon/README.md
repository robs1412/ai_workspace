# Avignon Workspace

Last Updated: 2026-04-22 CDT (Machine: Macmini.lan)

This workspace is for `Avignon Rose`, Sonat's chief-of-staff style assistant.

## Purpose

- Support `sonat@kovaldistillery.com` first.
- Mirror proven operational patterns from `frank/` when they make sense.
- Keep mailbox, task, and assistant workflows traceable in this workspace.

## Local Setup Status

- Local Avignon setup/conventions docs are complete for the current docs-only slice.
- Canonical workspace root: `/Users/werkstatt/ai_workspace/avignon`.
- Expected board/sidebar identity: Avignon workspace session, separate from the standing Avignon inbox monitor.
- Core local records: `AGENTS.md`, `TODO.md`, `HANDOFF.md`, `PERSONA.md`, and `EMAIL_DERIVED_DECISIONS.md`.
- Global workspace policy already records `avignon -> /Users/werkstatt/ai_workspace/avignon` as the Avignon local workspace mapping.
- This local docs pass did not modify launcher aliases, Workspaceboard runtime records, LaunchAgents, mailbox state, credentials, or send paths.

## Mail Sender Usage

Use `scripts/send_avignon_email.py` from the `ai_workspace` root, or `../scripts/send_avignon_email.py` from this Avignon workspace. It delegates to the shared sender with the Avignon profile, so it defaults to Avignon's approved private credential reference, `avignon/sent-log.jsonl`, the `Avignon Rose` From name, and a Sonat-only recipient guard.

The installed Avignon sender supports repeated or comma-separated `--to`, `--cc`, and `--bcc` values. All To/Cc/Bcc recipients are checked against the same Sonat-only default guard; any recipient outside Sonat's default audience requires a clear approval basis plus `--allow-non-primary`. Sent logs record To/Cc addresses and Bcc presence/count, but not Bcc addresses.

Safe render-only check:

```bash
python3 scripts/send_avignon_email.py \
  --to sonat@kovaldistillery.com \
  --subject "Draft subject" \
  --body-file avignon/drafts/example.txt \
  --dry-run
```

Only send after the draft and authority are clear:

```bash
python3 scripts/send_avignon_email.py \
  --to sonat@kovaldistillery.com \
  --subject "Approved subject" \
  --body-file avignon/drafts/approved-message.txt \
  --task-id avignon-approved-task-id
```

For any recipient outside Sonat's default audience, confirm authorization first and then add `--allow-non-primary`.

## Mailbox Triage And Follow-Up

- Treat inbound email as intake. Small clear mailbox/logging actions may be handled directly by Avignon; substantive work should be routed to a visible worker/session in the correct workspace and logged here.
- Avignon is a full-time Sonat-facing chief of staff. For clear low-risk internal work, create or reuse the correct visible board-managed worker, inject a full task brief, verify it started, monitor completion, update local TODO/HANDOFF/project notes and handled-mail state, and send Sonat or the relevant approved owner a clear completion report.
- Direct Sonat emails that report breakage, give approval, ask for status, or give an instruction are actionable intake, not silent `local-routing/no-email`. Quick-answer items should be answered directly in the same pass without a separate captured/routed receipt. For substantive work, invisible work, or anything not immediately answerable, create/reuse a visible route and send the captured/routed acknowledgement only after the visible route exists and the prompt has landed. Apply the same behavior to direct Robert instructions when Robert owns or approves the Avignon workflow.
- Completion report email is mandatory by default unless the task explicitly says to suppress email. Include what was done, what changed, relevant links/session IDs/task IDs, what was not done, and any remaining decisions or approval gates. Avignon reports to Sonat by default; include Robert only when the task context or approval path requires it.
- Clear Sonat requests to enter/update Portal or CRM records, create/update OPS tasks, or handle calendar items are approved routine internal work. Route them to the correct visible workspace worker and execute without a second approval check. Escalate only when the target/action remains ambiguous after deterministic checks or a normal safety gate applies.
- Keep the standing Avignon inbox monitor separate from implementation work. It should classify, route, log, and file handled mail rather than silently doing multi-step work inside the monitor.
- Routine handled/log-only messages should not generate scheduled review prompts. Send Sonat a decision email only for a real Sonat decision/approval boundary that Avignon cannot safely resolve.
- Tie completion notes to a stable source: OPS/Portal task id when available, otherwise a local Avignon task id plus the source email `Message-ID` or tracked outbound `task_id`.
- After a task is completed and the task-specific completion note is sent or drafted, log the result and file the source item to `Handled` unless Sonat or Robert explicitly wants it left in the inbox.
- Preserve Sonat-specific gates: external-sensitive sends, finance/legal/security/auth, credentials, production-impacting work, destructive operations, unusual vendor/payment instructions, suspicious mail, ambiguous ownership, or unclear recipient intent require escalation instead of auto-handling.

## Task And Follow-Up Conventions

- Use one stable task id per source task. Prefer the upstream OPS/Portal task id when present; otherwise use an `avignon-...-YYYY-MM-DD` id and tie it to the source `Message-ID` or tracked outbound `task_id`.
- Route implementation to the correct workspace instead of doing hidden multi-step work inside the Avignon monitor. Examples: CRM/import work to `importer`, sales list work to `salesreport`, Portal work to `portal`, and Avignon-only communication setup/convention work here.
- Log routed work in `HANDOFF.md` when it changes operating state, closes a meaningful follow-up, or creates a durable convention.
- Keep `TODO.md` as the action queue. Move finished items out of open sections and add only concise Done entries that prove closure.
- Keep `EMAIL_DERIVED_DECISIONS.md` for deduped decision items and handled email-derived decisions. Do not use it as a transcript.
- Escalate one concrete question when blocked; do not create repeated decision prompts for the same thread or already-tracked source.
- Record a dedupe key for each routed, handled, blocked, no-action, or completed source. If a real decision blocks work for more than 24 hours, send one follow-up with detailed instructions, concrete questions, the original reference, and the approval boundary.

## Scheduled Summary Boundary

Avignon's current installed scheduled cadence is Sonat-only morning overview. Robert clarified on 2026-04-17 that morning summary means upcoming work and evening summary means accomplished Task Manager/board work, superseding the prior morning-only policy interpretation.

Robert clarified on 2026-04-22 that Sonat-facing end-of-day updates must not be Frank-style technical implementation reports. EOD content should summarize Avignon-owned Sonat tasks: completed or advanced market, CRM, distributor, account, calendar, sample, and follow-through work; what changed for Sonat's work; plain-English blockers; and the recommended next action needed from Sonat, Robert, or another owner. Technical runtime, git, docs, LaunchAgent, or assistant-maintenance details belong in internal handoff or Robert-supervision notes only when relevant, not as Sonat's EOD headline.

Do not add Avignon evening runtime, LaunchAgent, Papers-link runtime hooks, or new report/runtime behavior without a separate implementation worker and explicit approval for that runtime slice.
