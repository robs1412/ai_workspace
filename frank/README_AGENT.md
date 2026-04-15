# Frank Cannoli Mail Agent

Last Updated: 2026-04-07 12:08:00 CDT (Machine: Macmini.lan)

## Purpose

This folder holds the lightweight local workflow for running Frank Cannoli's mailbox as a task-driven communication agent.

Current design:

- outbound messages are sent through Gmail SMTP using Frank's mailbox
- sent messages are logged for reply tracking
- inbox checks can surface replies tied to tracked outbound messages
- task records live locally and can be expanded as the workflow matures

This is manual by default. An optional scheduled `launchd` runner now exists for controlled inbox triage, but the default deployment mode remains `draft-only`.

## Files

- `tasks.json`: local task registry
- `sent-log.jsonl`: append-only outbound message log created by the sender script
- `scripts/frank_ops_digest.php`: on-demand digest of open OPS tasks for a target user
- `scripts/frank_autodraft.py`: generates drafts from recent inbox messages using Frank's rules
- `scripts/frank_portal_receipt.py`: creates Portal receipt records from receipt emails and attaches receipt URLs
- `scripts/frank_auto_runner.py`: one scheduled inbox-review cycle with dedupe logging and escalation
- `scripts/install_frank_launchagent.sh`: installs a 15-minute local LaunchAgent
- `scripts/uninstall_frank_launchagent.sh`: removes the LaunchAgent
- mailbox credentials remain outside this folder in `../frank-pw.html`

## Workflow

1. Add or update a task in `tasks.json`.
2. Send the outbound message with `scripts/send_frank_email.py`, ideally with `--task-id`.
3. Check for replies with `scripts/frank_inbox_monitor.py`.
4. Update the task status based on the reply or next action needed.

OPS-specific loop:

1. Generate a task digest for Robert from OPS.
2. Decide whether Frank should send a reminder, ask for prioritization, or follow up on a specific task.
3. Send a tracked outbound email tied to the relevant Frank task id.
4. Monitor replies and update the local task record.

Receipt-specific loop:

1. Detect incoming receipt emails from Square or similar providers.
2. Extract merchant, amount, transaction date, and card last 4.
3. Check BID `recipients.csv` for cardholder mapping.
4. Draft a response telling Robert what to do in Portal.
5. If the card is unmatched, tell Robert not to guess and to confirm the owner.

Scheduled loop:

1. Run `scripts/frank_auto_runner.py` from `ai_workspace`.
2. Check unseen inbox items.
3. Treat receipt emails as clear operational items and generate drafts.
4. Escalate suspicious mail and unclear messages to the configured primary recipient.
5. Record one decision per source email in `frank/automation-log.jsonl`.

Loop guard:

- Replies from the configured primary recipient to `Frank inbox review...` messages are logged as `assistant-review-reply` with decision `logged-local-follow-up` and do not generate another inbox-review escalation.
- This includes tracked replies to messages logged with an `*-auto-escalation` task id, even when the reply is not a simple acknowledgement.
- Mail from the assistant's own mailbox is logged as `assistant-self-mail` and does not self-escalate.
- The same runner can be configured for Avignon by setting the assistant name, sender display name, primary recipient, sent log, automation log, drafts directory, and credential path through CLI options or `FRANK_AUTO_*` environment variables.

## Commands

Send a tracked task email:

```bash
python3 scripts/send_frank_email.py \
  --to robert@kovaldistillery.com \
  --subject "Reminder: 2026 Company Party Invite" \
  --template-file .private/email-backup/templates/company-party-reminder.txt \
  --var first_name=Robert \
  --var event_date="May 18, 2026" \
  --var list_id=128 \
  --var list_name="2026 Company Party Invite" \
  --task-id frank-2026-001
```

Check recent inbox messages:

```bash
python3 scripts/frank_inbox_monitor.py --limit 20
```

Check unread inbox messages only:

```bash
python3 scripts/frank_inbox_monitor.py --unseen-only
```

Generate an OPS digest for Robert:

```bash
php scripts/frank_ops_digest.php --owner-id=1 --limit=10
```

Generate an email-ready OPS summary:

```bash
php scripts/frank_ops_digest.php --owner-id=1 --limit=10 --email-style > /tmp/frank_ops_digest.txt
python3 scripts/send_frank_email.py \
  --to robert@kovaldistillery.com \
  --subject "OPS Task Digest" \
  --body-file /tmp/frank_ops_digest.txt \
  --task-id frank-2026-ops-digest
```

Generate the latest receipt autodraft:

```bash
python3 scripts/frank_autodraft.py --write-file
```

Create the latest receipt in Portal:

```bash
python3 scripts/frank_portal_receipt.py --dry-run
python3 scripts/frank_portal_receipt.py
```

Run one scheduled inbox cycle:

```bash
python3 scripts/frank_auto_runner.py --mode draft-only --json
```

Run one Avignon-style scheduled inbox cycle with the shared loop guard:

```bash
FRANK_AUTO_NOTIFY=sonat@kovaldistillery.com \
FRANK_AUTO_PRIMARY_EMAIL=sonat@kovaldistillery.com \
FRANK_AUTO_ASSISTANT_NAME=Avignon \
FRANK_AUTO_FROM_NAME="Avignon Rose" \
FRANK_AUTO_TASK_ID=avignon-auto-escalation \
FRANK_SENT_LOG=avignon/sent-log.jsonl \
FRANK_AUTOMATION_LOG=avignon/automation-log.jsonl \
FRANK_DRAFTS_DIR=avignon/drafts \
FRANK_CYCLE_LOCK_DIR=tmp/avignon-auto.lock \
FRANK_CREDS_FILE=/path/to/approved/private/avignon-credential-file \
./scripts/run_frank_auto.sh
```

Install the 15-minute LaunchAgent on the chosen host:

```bash
./scripts/install_frank_launchagent.sh draft-only
```

Remove the LaunchAgent:

```bash
./scripts/uninstall_frank_launchagent.sh
```
