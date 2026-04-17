# Frank Cannoli Mail Agent

Last Updated: 2026-04-16 16:11:36 CDT (Machine: Macmini.lan)

## Purpose

This folder holds the lightweight local workflow for running Frank Cannoli's mailbox as a task-driven communication agent.

Current design:

- outbound messages are sent through Gmail SMTP using Frank's mailbox
- sent messages are logged for reply tracking
- inbox checks can surface replies tied to tracked outbound messages
- task records live locally and can be expanded as the workflow matures
- task-specific completion confirmations are policy-approved only when tied to a stable task/email id, logged, duplicate-checked, and allowed by recipient/approval gates

This is manual by default. An optional scheduled `launchd` runner now exists for controlled inbox triage, but the default deployment mode remains `draft-only`.

## Files

- `tasks.json`: local task registry
- `sent-log.jsonl`: append-only outbound message log created by the sender script
- `scripts/frank_ops_digest.php`: on-demand digest of open OPS tasks for a target user
- `scripts/frank_autodraft.py`: generates drafts from recent inbox messages using Frank's rules
- `scripts/frank_portal_receipt.py`: creates Portal receipt records from receipt emails and attaches receipt URLs
- `scripts/frank_auto_runner.py`: one scheduled inbox-review cycle with dedupe logging and escalation
- `scripts/frank_papers_links.py`: local formatter for appending verified Papers URLs to approved Frank email bodies
- `frank/scripts/frank_completion_confirmation.py`: dry-run-only completion confirmation helper; creates a local preview and duplicate-check log, never sends mail
- `frank/scripts/frank_daily_report.py`: dry-run-only morning-priority and end-of-day completed-work report helper; reads approved local Frank notes, never sends mail
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

Current behavior found on 2026-04-16:

- `frank_auto_runner.py` reads unseen mail and skips source messages already present in the automation log by normalized `Message-ID`.
- Primary-recipient instructions, forwards, and tracked corrections are logged for local routing instead of generating another `Frank inbox review` email back to Robert.
- `frank_morning_overview.py` sends only the approved morning overview and duplicate-checks by generated overview task id or matching subject/recipient in the sent logs.
- There is no approved generalized runtime that sends completion confirmations for every completed task or writes to Papers. Those remain manual/policy behavior unless Robert approves a specific runtime slice.
- Morning task selection should use active local work only: `In Progress`, `Waiting for Next Step`, and useful `Backlog` items. It should not pull from `Done` or from completed/closed/filed/superseded task history.
- End-of-day completed-work reporting is wired into the installed Mac mini runtime as of 2026-04-17. It uses the existing Frank send helper, existing credential path, existing sent log, and the existing `com.koval.frank-morning-overview` LaunchAgent with a second 18:00 calendar trigger.

Completion confirmation rule:

1. Use an OPS/Portal task id when available; otherwise create/use a local Frank task id.
2. Link the source email `Message-ID` or tracked outbound `task_id` in the local log.
3. Check `sent-log.jsonl`, source `Message-ID`, task id, subject, recipient, and draft filename before any send.
4. Send or draft only one concise task-specific completion confirmation when approval gates allow it.
5. Mark the task/email handled after the confirmation is logged so the same task is not resurfaced.

Dry-run completion helper usage:

```bash
python3 frank/scripts/frank_completion_confirmation.py \
  --task-id frank-2026-example \
  --source-message-id '<source-message-id@example>' \
  --tracked-task-id frank-2026-example-worker \
  --done 'The worker completed the requested internal routing and no approval blocker remains.' \
  --worker 'workspace/session-id' \
  --json
```

The local helper:

- requires either `--source-message-id` or `--tracked-task-id`
- creates a stable `confirmation_key`
- checks the live Frank sent log plus local dry-run completion log for duplicate confirmation identifiers
- writes a preview draft under `frank/drafts/` and a dry-run JSONL row to `frank/completion-confirmation-log.jsonl`
- exits with `3` and writes nothing when a duplicate confirmation key/source is found
- never sends mail, reads credentials, connects to IMAP/SMTP, files messages, changes polling cadence, or edits LaunchAgents

Future workflow fit: when Robert emails Frank and Frank routes a worker, use this helper only after the worker reports completion with no remaining approval blocker. If the worker reports that approval is needed, use the separate decision-email path instead of a completion confirmation.

Remaining approval boundary: turning this into send-enabled runtime requires separate approval for the exact send hook, recipient policy, mailbox filing behavior, credential path, and duplicate-confirmation fields to add to the real sent log.

Communication intake fit: tasks emailed to Frank should be routed into a visible worker/session when they need implementation or investigation beyond a small mailbox action. The standing Frank inbox monitor remains the control surface, while the worker reports back to Frank with either completion or a real approval blocker.

Daily report helper usage:

```bash
python3 scripts/frank_daily_report.py --type morning --date 2026-04-17 --json
python3 scripts/frank_daily_report.py --type eod --date 2026-04-17 --json
```

The helper:

- reads `TODO.md` by default
- selects morning work only from active TODO sections
- selects end-of-day accomplishments only from same-date `Done` entries
- accepts optional approved Papers metadata through `--papers-metadata-file`
- writes a local draft unless `--preview-only` is used
- never sends mail, reads credentials, connects to IMAP/SMTP, changes LaunchAgents, or reads live Papers

Installed runtime status:

- 06:00: `frank_morning_overview.py` sends the morning overview.
- 18:00: the same script auto-selects the EOD report and sends `Frank End-of-Day Update: ...`.
- Duplicate protection checks the sent log by report `task_id` and subject/recipient before sending.
- Morning OPS task selection is today's tasks first, then the most recent overdue tasks, up to 10.
- Frank's runtime signature is plain text with clean social-link labels, not angle-bracket URL formatting.

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

Append a verified Papers link to an approved completion/report body:

```bash
python3 scripts/send_frank_email.py \
  --to robert@kovaldistillery.com \
  --subject "Task complete: example" \
  --body-file /path/to/approved-body.txt \
  --task-id frank-example-task \
  --papers-link "https://papers.koval.lan/example-record|Papers work record" \
  --dry-run
```

The Papers hook only formats explicitly supplied or approved metadata URLs for `papers.koval` / `papers.koval.lan`. It does not create Papers records, read live Papers, send unless the normal send command is run without `--dry-run`, or change the LaunchAgent schedule.

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
