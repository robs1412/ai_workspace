# National Outreach AI Worker Inbox

Status: setup verified 2026-04-27 CDT

Mailbox: `nationaloutreach@kovaldistillery.com`

This is the shared AI-worker inbox for worker-addressed mail that should not belong to Frank or Avignon directly. Email Coordinator owns intake/routing decisions. Outreach Coordinator owns tasting, scheduling, and outreach coordination work routed from this inbox.

Inbox-zero is mandatory for this mailbox and its persona aliases. Keep the active inbox at `0` open / `0` unread by filing handled, no-action, duplicate, already-routed, completed, and logged items out of INBOX. Leave messages open only for real unprocessed work, blockers, decisions, or named dependencies. Use one operational archive folder for old/resolved shared-inbox residue rather than multiplying worker-specific handled folders; worker routing belongs in durable logs and visible task state.

Open, missed, blocked, or waiting email-derived items require an owner-facing email from the responsible persona, not only a TODO/HANDOFF note. Vanessa, Naomi, Ezra, or the assigned persona should send Robert or the relevant owner the current state, the exact decision/dependency, the next action, and the original source email quoted or forwarded in the body for review unless a safety gate blocks sending.

Outside-dependency follow-ups must be logged as one-item reminders with a due time, normally 24 hours for urgent items or 48 hours for lower-urgency items. Scheduled items, such as a Monday 8:00 AM draft, should be logged as scheduled actions and executed at that time rather than producing separate reminder emails.

National Outreach reminder storage must include both a durable task record and an executable reminder surface. Use OPS tasks when the follow-up belongs in OPS, and use the National Outreach scheduled-action runtime for automatic due-time checks. The shared National Outreach Google Calendar surface is `KOVAL Outreach Events` for Vanessa, Ezra, Naomi, and other shared-inbox personas when the work belongs in that lane. Calendar events may supplement reminders, but they do not replace the OPS/task record or scheduled-action record.

Use `../docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` as the canonical flow for National Outreach intake, email clarifications, timed reminders, completion reports, and Papers projection packets.

The runtime writes task-flow packets and events for classified mail, scheduled actions, queued reminder drafts, sent emails, and send failures. Private runtime state keeps a JSONL audit at `task-flow-events.jsonl`; queryable task-flow state is stored in the existing MySQL `koval_crm` database tables `ai_task_flow_packets` and `ai_task_flow_events` through the OPS bootstrap connection. These records supplement OPS/Portal/domain tasks; they do not replace the authoritative task record when an OPS/Portal/domain task is required.

Do not store credentials, private mailbox bodies, OAuth tokens, app passwords, private keys, or private SOP text in this folder.

## Current Send-From Identities

- Outreach Coordinator persona: Vanessa Sterling `<vanessa.sterling@kovaldistillery.com>`, sent through the approved National Outreach mailbox/runtime route.
- Shared inbox route: `nationaloutreach@kovaldistillery.com`
- Codex route: `codex@kovaldistillery.com`

Do not send as `macee.maddox@kovaldistillery.com`. Macee has left; treat that address only as inbound legacy-recipient context when reviewing old mail.

The authoritative send-from registry is `../worker_roles/send-from-personas.md`.

Vanessa's normal external/staff-facing signature should be:

Best,

Vanessa

Vanessa Sterling

Outreach Coordinator
KOVAL Distillery
4241 N Ravenswood Ave
Chicago, IL 60613
312 878 7988
http://www.koval-distillery.com

X | Instagram | Facebook

Use the full Vanessa signature block by default. The closing should be `Best,`, a blank line, `Vanessa`, then a blank line and `Vanessa Sterling`. Keep the phone number, website, and `X | Instagram | Facebook` social-label set on separate lines. In HTML email, link the platform names and do not print raw social URLs next to the labels.

## Vanessa Response Style

For account-facing event-detail checks, keep the Maker's Mart reply/request as the model. Open with the practical context, ask for exact missing details, and use old thread history as confirmable context rather than guessing. Example facts to ask for: projected guest count, best day-of point of contact, arrival/setup instructions, table/material expectations, and updated product priorities.

Keep the body concise and account-facing:

- who is being prepared for the event;
- what details are needed to prepare correctly;
- what older thread notes already say;
- what the recipient should confirm or update.

Do not include internal routing, board/session details, Message-IDs, or approval-gate language in the external email.

When Robert provides draft language and says to use it, send the substance through Vanessa's persona rather than forwarding or reproducing Robert's voice/signature as the visible sender. Translate owner-supplied text into a normal Vanessa email unless Robert explicitly requires a direct quote or a different signature treatment, and keep Robert copied only when the packet or instruction says to do so.

## Tasting Prep Product Reminders

For ordinary retail tastings and chain-account prep, Vanessa should include a short product-carry/sample note in taster reminders when account history is available. Use the Salesreport Chain Store Intelligence page and the existing Chain Invoice Report as the practical source for what the account likely carries; this is good enough for reminder/sample-planning purposes and should not become an overbuilt scraper-comparison project.

For Binny's-specific prep, the recent Binny's scraper output is the fresher current-placement reference when needed, but the reminder goal is still simple: tell the person working the tasting what products the account appears to carry and what samples/materials to bring.

The Monday Mitch weekly tastings draft generated by `scripts/build_mitch_weekly_report.php` includes a `Product / sample prep` column. For direct staff reminders, use `templates/taster-reminder-product-carry.md` as the line-level pattern.

## Weekly COT Activity Report Follow-Through

Portal weekly COT Activity reminders sent to `codex@kovaldistillery.com` belong to the National Outreach lane. Treat the newest `Overdue Reports Summary` message as the active intake item and archive older redundant summaries so INBOX reflects only the live reminder being worked.

Weekly COT reports must be completed through Portal's real submit path, not only by drafting content or updating DB rows. The repeating proof standard is:

- Portal report row shows `submitted=1` with the correct Portal-owned week.
- The overdue/reminder notification row links to the submitted `report_id`.
- Reviewer notification proof exists through Portal's runtime path, for example `notifications_logs` rows showing `reports.new_for_review` with `status=sent`.

The May 17-18, 2026 overdue-summary recovery is the model workflow for future follow-through:

- keep only the newest overdue-summary message in INBOX while older redundant summaries are archived with durable archive proof;
- submit the overdue weekly report(s) through the live Portal submit/API path with the full payload Portal expects, not an id-only shortcut;
- record the exact report ids, covered Portal periods, linked overdue-notification ids, and reviewer-notification proof in `TODO.md` / `HANDOFF.md`;
- after submission proof exists, clear the worked overdue-summary message from INBOX and keep the audit trail in local handoff state plus `/Users/admin/.nationaloutreach-launch/state/archive-log.jsonl`.

Do not mark weekly COT follow-through complete until both proof classes exist: Portal submission proof and inbox-clearing proof.

## Private Runtime State

Private credential and setup state are machine-local under `.private/mailboxes/nationaloutreach/`.

Non-secret verification status may be summarized here or in project-hub notes, but secret values and mailbox bodies must never be copied here.

## Report Templates

- Whole Foods OPS coverage reports: `templates/whole-foods-ops-coverage-report.md`
- Binny's OPS coverage reports: `templates/binnys-ops-coverage-report.md`

Use HTML table email for these coverage reports. Highlight unassigned, open, partially assigned, missing OPS, or missing linked-shift rows in light red: `#fce4e4`.

## Illinois Tasting Compliance

Use `ILLINOIS_TASTING_COMPLIANCE_DIRECTIVE.md` for Illinois tasting events where sample-provider responsibility or CDTPL timing is relevant. Regular retail tastings such as Binny's, Mariano's, Whole Foods, and similar ordinary account tastings do not need Sebastian notification solely because a tasting is happening. For non-routine events, if KOVAL supplies or transports spirits samples directly, or if the sample-provider path is unclear, flag the event for Sebastian / CAO review; preferred notice is 14 calendar days, with minimum internal cutoffs of 2 business days for Chicago and 3 business days outside Chicago.

## Bulk Mailings

Broad staff or audience mailings, including requests such as "email everyone for May," should be routed to `/Users/werkstatt/lists` for PHPList audience and campaign handling. Vanessa can ask the owner questions and prepare the brief; do not use the National Outreach mailbox route for one-off individual sends to simulate a list mailing.

## Specialist Routing

The National Outreach mailbox classifier should route finance-operations items to Naomi Stern and special-project/legal-affairs coordination items to Ezra Katz when the message facts are clear enough to classify. These are advisory/triage routes only:

- Naomi Stern: finance operations, cash/control cadence, payables/receivables, invoices, collections, month-end close, reconciliation, budgets/forecasts, missing-source finance follow-up.
- Ezra Katz: special projects, legal-affairs coordination, document follow-through, approval tracking, contract/policy questions, permits/licenses, TTB/COLA/label approval, insurance/vendor terms, counsel-ready business briefs.

Finance account-system setup must not be handled as hidden National Outreach inbox work. QuickBooks invite follow-up, BID access, Portal/login setup, payroll, banking, and finance-permission requests should be captured by the mailbox worker and routed to Task Manager/Workspaceboard as a visible BID/Portal/OPS lane with the current state, next owner, and blocker recorded.

Security-sensitive finance/legal mail still routes to Security Guard first when it involves credentials, OAuth/tokens, 2FA, bank/routing details, urgent payment pressure, private IDs, or suspicious requests. Naomi and Ezra do not send external replies, approve legal/regulatory action, move money, change finance records, or mutate live systems without separate approval and the proper routed workspace.
