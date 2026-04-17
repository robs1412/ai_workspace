# Avignon Workspace

Last Updated: 2026-04-17 10:59 CDT (Machine: Macmini.lan)

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

## Scheduled Summary Boundary

Avignon's approved scheduled cadence is Sonat-only morning overview. Do not mirror Frank's Robert-approved 18:00 end-of-day report path, Papers-link runtime hooks, or new report/runtime behavior into Avignon without a separate explicit approval for Avignon.
