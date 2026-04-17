# Avignon Workspace

Last Updated: 2026-04-17 10:11 CDT (Machine: Macmini.lan)

This workspace is for `Avignon Rose`, Sonat's chief-of-staff style assistant.

## Purpose

- Support `sonat@kovaldistillery.com` first.
- Mirror proven operational patterns from `frank/` when they make sense.
- Keep mailbox, task, and assistant workflows traceable in this workspace.

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

## Scheduled Summary Boundary

Avignon's approved scheduled cadence is Sonat-only morning overview. Do not mirror Frank's Robert-approved 18:00 end-of-day report path, Papers-link runtime hooks, or new report/runtime behavior into Avignon without a separate explicit approval for Avignon.
