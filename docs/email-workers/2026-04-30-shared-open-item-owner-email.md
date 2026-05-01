# Shared Open-Item Owner Email Directive

Status: active shared directive
Owner: AI Workspace Task Manager / Email Coordinator
Applies to: Frank, Avignon, National Outreach, Vanessa Sterling, Naomi Stern, Ezra Katz, Asher, Venetia, Codex-routed mail, and future approved email-worker personas
Created: 2026-04-30

## Rule

Recording an open, missed, blocked, or waiting email-derived item in TODO/HANDOFF/log state is not enough.

When an email worker finds an item that remains open, was missed/underlogged, needs a human decision, or is waiting on a named human/system dependency, the responsible worker persona must send the owner a normal owner-facing email about that item unless a safety gate blocks sending.

The email must include:

- the plain-English business context;
- the responsible worker/persona and current owner;
- what is open, missed, blocked, or waiting;
- the exact decision or next action needed, when there is one;
- what the worker will do after the answer or dependency arrives;
- the original source email included below the update for owner review, quoted or forwarded in the message body when attachments are not available;
- trace references such as Message-ID, task ID, report ID, or session ID only after the business context.

If the source is not an email, say that clearly and include the best available original source link or packet reference instead.

## Routing

- Vanessa sends outreach, COT, tasting, account, and National Outreach owner updates.
- Naomi sends finance-operations, QuickBooks, BID finance/access, receivables/payables, and close-readiness owner updates.
- Ezra sends special-project, legal-affairs, document, regulatory, approval-tracking, and counsel-ready business-packet owner updates.
- Frank and Avignon use their own owner routes and persona rules for Robert/Sonat direct-owner work.
- Security-sensitive, finance/legal-sensitive, external-sensitive, suspicious, credential/auth, destructive, or production-impacting items still respect the existing approval gates. If an email cannot be sent safely, draft/log the owner email and surface the blocker.

## Filing Condition

Do not file an open or missed source item as handled merely because it was recorded locally. It may be filed only after one of these is true:

- the responsible owner email was sent with the original source included;
- the item was converted into a visible task/session and the owner email or approved summary includes the source;
- the item is genuinely no-action, duplicate, or already completed, with durable state explaining that disposition;
- a safety gate prevents sending, and the blocker has been surfaced in plain English.

## Reminder / Scheduled-Action Rule

Open items should not become recurring owner-email bundles when inbox workers are monitoring the mailbox. If a remaining open item is waiting on an outside party or named dependency, create one reminder for that one item only and schedule the responsible worker to check it automatically at the due time.

Use 24 hours for urgent or near-date items and 48 hours for less urgent outside-dependency items unless Robert gives a different cadence. At reminder time, the worker must first check whether the dependency has replied or the item has resolved. If it has resolved, log the skip and do not email Robert. If it is still unresolved, send one owner email for that one item with the original source included.

If an item is already scheduled for a specific date/time, do not add a separate reminder nag. Log the scheduled action and let the worker run it at the scheduled time.

Each reminder/scheduled action needs both:

- an OPS task or other reasonable task record with owner, due date/time, and status; and
- a worker-executable scheduled action record so the email worker can run at the set time without a manual prompt.

Calendar reminders are an approved execution surface when the worker has a verified calendar path:

- Frank may use Frank's individual Google Calendar path for Robert/Frank reminders and calendar-backed follow-ups.
- Avignon may use Avignon/Sonat's individual Google Calendar path for Sonat/Avignon reminders and calendar-backed follow-ups.
- National Outreach may use the shared National Outreach calendar for Vanessa, Ezra, Naomi, and other shared-inbox persona reminders.

Calendar events supplement the task/scheduled-action record; they do not replace durable task storage. If calendar creation is blocked by auth, missing helper support, unavailable scopes, or duplicate ambiguity, log the blocker and use the local scheduled-action record or OPS task until the calendar path is verified.
