# Avignon Workspace

Last Updated: 2026-04-10 13:09:02 CDT (Machine: Macmini.lan)

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
