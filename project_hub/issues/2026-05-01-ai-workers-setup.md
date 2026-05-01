# AI Workers Setup

- Master Incident ID: `AI-INC-20260501-AI-WORKERS-SETUP-01`
- Date Opened: 2026-05-01 CDT
- Date Completed:
- Owner: AI Manager control lane / Task Manager routing
- Priority: High
- Status: Open; planning packet created, implementation lanes not started

## Scope

Robert asked on 2026-05-01 to add a project/task titled `AI workers Setup` and build it out as a durable AI Workspace packet and actionable task structure.

This slice is planning and routing only. It must not mutate external systems, send email, browse external sources, change credentials, run live OAuth/auth setup, alter LaunchAgents/runtimes, create OPS/Portal tasks, or change production data unless a later approval explicitly opens that lane.

## Original Robert Text

```text
*(to be built out) - AI workers Setup>


General
- calendar access (Frank -> Robert, Frank -> own, Avignon -> Sonat, Avignon -> own, Nationaloutreach -> Events etc.)
- Reminders (how set ... auto runners to send reminders)
- Email polling (15sec and 1min)

Customer Service
connect the inbox
- create FAQs based on questions that have come in
- use FOH guide for answers
- Sales in Europe (see Sebastian E-mail May 1, 2026 and https://www.weisshaus.it/)

AI Worker buildout
- add what to do by worker, what job roles they currently perform and what we are missing still
- check with job descriptions that were created for these roles (check off by worker individually and record google doc link to job description when done) + updated new 2026 job description for AI worker if applicable

Naomi
- bid reporting and mangement
- Financial reports in Portal (currently assigned to Oleg)
- send out overdue invoice reminders
- create invoices from Portal invoices

Ezra
- support on projected / need basis

Vanessa
- correspond regarding tastings
- E-mail out reminders to team
- E-mail out group messages about open tastings
- book tastings (need directives for Whole Foods, Marianos, Binnys etc)
- organize tastings in OPS (download, update, add to Google calendar)
- send Mitch Conti at Heritage a weekly overview (only include staffed tastings!)
```

## Current Open TODO Context

Relevant active AI Workspace TODO families at intake:

- Shared task-flow stabilization remains active; Papers projection is still blocked by `papers_create` permission or an approved write client.
- Whole Foods / National Outreach sync remains approval-gated for pending buyer-approval requests.
- Claude/Papers durable runtime cleanup remains open for preferred Infisical-backed loading and some Google admin/API enablement.
- Frank/Avignon Gmail push planning remains a future auth/runtime lane; current practical path is polling.
- Secure files/context intake, Salesreport audit gaps, pricing scope, and related source-access items remain separate open projects and should not be folded into this setup project unless Robert explicitly widens scope.

## Workstreams To Route

### 1. Calendar/Auth Mapping Lane

Goal: inventory current worker calendar access and produce the desired worker-to-calendar map before any auth setup.

Capture at minimum:

- Frank -> Robert calendar.
- Frank -> Frank's own calendar.
- Avignon -> Sonat calendar.
- Avignon -> Avignon's own calendar.
- National Outreach / Vanessa -> `KOVAL Outreach Events`.
- Similar worker calendar mappings for Naomi, Ezra, Customer Service, Asher, Venetia, or future workers if applicable.

Known non-secret context:

- National Outreach / Vanessa calendar reminders currently use the OPS-linked `KOVAL Outreach Events` calendar path.
- Frank/Avignon Drive/OAuth and Gmail push are separate from simple polling and should remain approval-gated.

Lane output:

- A non-secret calendar matrix with worker, calendar, current status, intended status, source docs, auth/storage boundary, and next approved action.
- A list of auth work that needs Security Guard and Code/Git Manager review before execution.

### 2. Reminder Runner Mapping Lane

Goal: document how reminders are created, which auto runners send reminders, and how delivery is verified.

Capture at minimum:

- Shared task-flow reminders and scheduled actions.
- Frank due runner behavior and throttle.
- National Outreach / Vanessa reminder behavior for tasting follow-ups and Mitch weekly overview drafts.
- Calendar reminder events versus email reminders.
- Verification/readback points: task-flow event rows, scheduled-action IDs, sent-log or skip-log, calendar event IDs where applicable.

Lane output:

- Reminder-runner map by worker and reminder type.
- Required verification checklist for each reminder path.
- Gaps where reminder delivery is not yet auditable.

### 3. Email Polling And Inbox Lane

Goal: document current polling paths and identify which workers use 15-second, 60-second, or other polling.

Capture at minimum:

- Frank current polling path.
- Avignon current polling path.
- National Outreach / Vanessa current polling path.
- Asher and Venetia header-only polling status if still relevant.
- Any Customer Service inbox connection plan.

Known non-secret context:

- Frank and Avignon have used the 15-second polling path.
- National Outreach has a full-body/send-capable runtime with approved queued-send processing, plus inbox-poll hardening noted in National Outreach TODO.
- Asher and Venetia were previously verified as 60-second header-only polling routes.

Lane output:

- Polling matrix with worker, mailbox, poll interval, body/header scope, send authority, filing authority, current runtime source, and approval gates.
- Customer Service inbox connection requirements before any mailbox auth or body reads.

### 4. Customer Service Inbox And FAQ Lane

Goal: prepare Customer Service setup without connecting or reading an inbox until approved.

Capture at minimum:

- Inbox to connect and whether it is new or existing.
- Source approval needed for mailbox auth/body reads.
- FAQ build process from incoming questions.
- FOH guide location/source need for answer authority.
- Sales in Europe investigation source need: Sebastian email dated 2026-05-01 and `https://www.weisshaus.it/`.

Boundaries:

- Do not browse `weisshaus.it` or any external site in this planning slice.
- Do not read private mailbox bodies, connect an inbox, send replies, create external FAQs, or publish customer-facing answers until separately approved.

Lane output:

- Customer Service setup brief.
- FAQ source-register structure.
- FOH-guide answer-policy checklist.
- Exact approval gates for inbox connection, body review, external browsing, and external customer replies.

### 5. Worker Role / Job Description Audit Lane

Goal: inventory what each worker does now, compare current work to job descriptions, and record individual check-offs.

Workers to include initially:

- Frank.
- Avignon.
- National Outreach / Vanessa.
- Naomi.
- Ezra.
- Customer Service worker, if a role exists or needs creation.
- Asher.
- Venetia.
- AI Manager.
- Task Manager / Polier.
- Decision Driver.
- AI Health Manager.
- Other worker roles in `worker_roles/` as needed.

Current source docs to check first:

- `worker_roles/*.md`.
- Role persona YAMLs under `worker_roles/*/persona.yaml`.
- Worker-local `PERSONA.md`, `JOB_DESCRIPTION.md`, `AGENTS.md`, `TODO.md`, and `HANDOFF.md` where present.

Lane output:

- Per-worker checklist: current duties, actual current jobs performed, missing duties, current job-description source, Google Doc link if available, whether a 2026 job description exists, and action needed.
- Proposed 2026 job-description updates as docs-only drafts unless approved for Google Docs write/update.

### 6. Naomi Finance Setup Lane

Goal: define Naomi's finance setup tasks and gates.

Capture at minimum:

- BID reporting and management.
- Financial reports in Portal, currently assigned to Oleg.
- Overdue invoice reminder process.
- Invoice creation from Portal invoices.
- QuickBooks/API/AP/AR work already in progress should be treated as related context, not duplicated.

Boundaries:

- No money movement, accounting/tax decisions, bank/vendor/payroll changes, live finance-system mutation, external finance reminders, or QuickBooks/API/auth setup without separate approval.

Lane output:

- Naomi finance task map with owner, data source, workspace, approval gate, and first safe read-only deliverable.
- Recommendation for whether to route implementation through `ws bid`, `ws portal`, `ws ops`, or a finance-specific visible worker.

### 7. Vanessa Tasting Directives Lane

Goal: consolidate Vanessa's tasting duties, directives, and recurring outputs.

Capture at minimum:

- Correspond regarding tastings.
- Email reminders to the team.
- Email group messages about open tastings.
- Book tastings with directives for Whole Foods, Mariano's, Binny's, and similar accounts.
- Organize tastings in OPS: download, update, add to Google Calendar.
- Send Mitch Conti at Heritage a weekly overview including only staffed tastings.
- Product-carry notes for taster reminders using Salesreport Chain Store Intelligence / Chain Invoice Report where appropriate.

Boundaries:

- Do not send external account replies, mutate OPS schedules, create calendar events, or queue group emails unless the specific workflow is already approved or a later worker lane receives approval.

Lane output:

- Vanessa tasting directive index.
- Account-specific tasting rule matrix.
- Mitch weekly overview verification checklist.
- Open-tastings group-message approval path.

### 8. Ezra Project Support Lane

Goal: define Ezra's project/support role for ad hoc project work and legal-affairs-adjacent routing.

Capture at minimum:

- Project/on-need support model.
- Source doc/status-email reminder work.
- What Ezra can triage versus what needs Security Guard, counsel, Robert, Sonat, Naomi, or a workspace worker.

Boundaries:

- No legal advice, legal/regulatory external communications, privileged/private material exposure, live-system mutation, or source-doc access beyond approved scope.

Lane output:

- Ezra project-support intake checklist.
- Escalation matrix.
- Recommended worker handoff template.

## Proposed OPS/Portal Task Packet

Do not silently create this in OPS/Portal. If Robert approves an OPS/Portal task, use this packet:

Title: `AI workers Setup`

Recommended owner/assignee: `Codex` user id `1332` for planning/routing ownership unless Robert wants a human-owned OPS task. If a project owner field is required, recommend Robert as business owner and Codex as execution assignee.

Body:

```text
Build out the AI workers Setup project packet and route scoped implementation lanes. Planning first: no external sends, mailbox connection/body reads, auth/OAuth/credential changes, runtime/LaunchAgent changes, OPS/Portal mutations, Google Doc writes, or production data changes without separate approval.

Scope:
- Calendar/auth mapping for Frank, Avignon, National Outreach/Vanessa, Naomi, Ezra, Customer Service, and similar workers.
- Reminder runner mapping: how reminders are created, which runners send them, and delivery/readback verification.
- Email polling map: 15-second and 60-second paths, body/header scope, send/file authority by worker.
- Customer Service inbox/FAQ setup plan using incoming-question source, FOH guide, Sebastian 2026-05-01 Europe-sales source, and weisshaus.it investigation source, with no browsing/sending until approved.
- Worker-role/job-description audit: current duties, missing duties, individual check-off, Google Doc job-description link if available, and 2026 job-description update needs.
- Naomi finance setup: BID reporting/management, Portal financial reports currently assigned to Oleg, overdue invoice reminders, Portal invoice creation.
- Vanessa tasting directives: correspondence, team reminders, open tasting group messages, Whole Foods/Mariano's/Binny's directives, OPS/calendar organization, Mitch weekly staffed-tastings overview.
- Ezra project-support model.

Deliverable:
Create/update the AI Workspace project-hub packet, TODO pointer, lane briefs, approval gates, and implementation worker recommendations. Report changed files, any created IDs, and the next blocker/route decision.
```

## Worker Lanes Needed

- `Calendar/Auth Mapping Worker`: read-only inventory and matrix.
- `Reminder Runner Mapping Worker`: read-only scheduler/reminder map and verification checklist.
- `Email Polling/Inbox Worker`: read-only runtime/polling map and Customer Service inbox prerequisites.
- `Customer Service FAQ Worker`: docs-only setup brief, FAQ register, FOH guide/source plan.
- `Worker Role Audit Worker`: per-worker current-role/job-description audit and 2026 JD gap list.
- `Naomi Finance Setup Worker`: finance task map and approval-gated implementation plan.
- `Vanessa Tasting Directives Worker`: tasting directive index, account rules, Mitch/open-tasting recurring flow.
- `Ezra Project Support Worker`: project-support checklist and escalation matrix.
- `Security Guard`: review any later auth, credential, mailbox-body, private source, external browsing, finance/legal, or runtime-change lane before execution.
- `Code/Git Manager`: review any later source/runtime changes, Google Doc API write tooling, polling changes, or automation runner changes before implementation.

## Repo Logs

### ai_workspace

- Repo Log ID: `ai-workers-setup-planning-20260501`
- Commit SHA: not committed
- Commit Date: n/a
- Change Summary: Created this project-hub planning packet, added an open project index entry, and added a concise TODO pointer.

## Verification Notes

- Read AI Workspace `TODO.md`, append queues, project-hub template/index, and existing role docs for Naomi, Ezra, Vanessa/Outreach, Frank, and Avignon.
- No external systems were mutated.
- No OPS/Portal task was created.
- No external browsing was performed.
- No mailbox bodies, secrets, credentials, tokens, private auth paths, or credential file contents were printed.

## Rollback Plan

If Robert cancels this project, remove this issue file, remove the project-hub index entry, and remove the TODO pointer. Do not alter unrelated open TODOs or active project records.

## Follow-Ups

- AI Manager should approve or adjust the worker lane split before Task Manager starts visible workers.
- If Robert wants an OPS/Portal task, create it from the packet above only after explicit approval.
- First implementation step should be read-only lane creation for calendar/auth mapping, reminder runner mapping, email polling/inbox mapping, Customer Service FAQ setup, worker-role audit, Naomi finance setup, Vanessa tasting directives, and Ezra project support.

## 2026-05-01 Task Flow Routing Readback

Robert asked to make sure Vanessa, Naomi, Ezra, and similar workers are properly routed to Workspaceboard Task Flow.

Actions taken:

- Updated current Vanessa/National Outreach inbox packets from passive `classified` state to explicit `routed` state in Task Flow.
- Reclassified the Saturday May 2 Maker's Market staffing item from generic `marketing-manager` to `outreach-coordinator` with Vanessa as responsible persona.
- Updated current Naomi packet to `naomi.stern@kovaldistillery.com` with the BID/finance route context.
- Updated current Ezra packets to `ezra.katz@kovaldistillery.com` with special-project/legal-affairs route context.
- Preserved approval gates: no external sends, legal/regulatory replies, finance mutations, or production changes are implied by Task Flow routing.
- Fixed the Workspaceboard Task Flow page asset to fetch `api/task-flow/report.php` instead of the extensionless PHP source path, then bumped the JS asset version so the browser gets the corrected fetch path.

Verification:

- `php scripts/task_flow_mysql_recorder.php report 200` shows the routed records for Vanessa, Naomi, and Ezra with responsible worker/persona populated.
- `php -l /Users/werkstatt/workspaceboard/api/task-flow/report` and `php -l /Users/werkstatt/workspaceboard/api/task-flow/report.php` pass.
- Workspaceboard source commits pushed: `9c66587` and `911b367`.

Remaining issue:

- The National Outreach polling runtime still creates `classified` records first. A separate Email Polling lane should make the runtime create or update visible route/session/task fields automatically for actionable worker mail instead of leaving repeated active-inbox items in `classified`.
