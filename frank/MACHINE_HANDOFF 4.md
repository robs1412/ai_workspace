# Frank Machine Handoff

Last Updated: 2026-04-11

## Rule

Mac mini is the single writer for Frank mailbox send/check actions.

MacBook and other workspace sessions may draft, review, and transfer non-secret draft/reference files, but they should not start a competing live Frank mailbox process or send directly from Frank's mailbox while the Mac mini is the active host.

## Before Triggering Mailbox Work On Mac Mini

1. Confirm the active host and LaunchAgent state:

```bash
ssh admin-macmini 'hostname; launchctl print gui/$(id -u)/com.koval.frank-auto 2>/dev/null | awk "/state =|runs =|last exit code|run interval/ {print}"'
```

2. Check for an active lock before manual runs:

```bash
ssh admin-macmini 'find ~/.frank-launch/state -maxdepth 1 -name "*.lock" -print'
```

3. Check duplicate risk before any real send:

```bash
ssh admin-macmini 'grep -nE "SUBJECT|TASK_ID|DRAFT_FILENAME" ~/.frank-launch/state/sent-log.jsonl ~/.frank-launch/state/automation-log.jsonl 2>/dev/null || true'
```

For Avignon, also check the Avignon workspace logs:

```bash
ssh admin-macmini 'ROOT="$HOME/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace"; grep -nE "SUBJECT|TASK_ID|DRAFT_FILENAME" "$ROOT/avignon/sent-log.jsonl" "$ROOT/avignon/automation-log.jsonl" 2>/dev/null || true'
```

Duplicate checks should cover message IDs when known, task id, subject, recipient, and draft filename.

## Send Policy

- Use `draft-only` for scheduled automation unless Robert explicitly approves a narrower send action.
- Only send the specifically approved draft(s); do not use a mailbox check as permission to send arbitrary replies.
- If the draft file includes `To:` and `Subject:` headers, pass only the body text into `send_frank_email.py`; otherwise those headers will appear in the email body.
- Use the Mac mini credential-backed path and log the result in the Mac mini sent log.
- If credentials, sender identity, or log path are ambiguous, leave the draft unsent and report the exact command or boundary instead of improvising.

## Current Persona Outreach Status

- Frank to Robert, subject `Frank persona blurb`: sent from Mac mini on 2026-04-11 and logged in `~/.frank-launch/state/sent-log.jsonl` with task id `frank-2026-persona-blurb`.
- Avignon to Sonat, subject `Avignon persona blurb`: sent from Mac mini on 2026-04-11 and logged in `avignon/sent-log.jsonl` with task id `avignon-2026-persona-blurb`. The approved Mac mini Avignon credential reference used nonstandard keys; a temporary Mac mini-only `User:` / `App pw:` formatted file under `~/.frank-launch/private/` was derived for the send and removed immediately afterward.
