# AI Workers Setup

- Master Incident ID: `AI-INC-20260501-AI-WORKERS-SETUP-01`
- Date Opened: 2026-05-01 CDT
- Date Completed:
- Owner: AI Manager control lane / Task Manager routing
- Priority: High
- Status: Open; local setup bundle completed, live activation still blocked on named business inputs and approval-gated auth/runtime/send lanes

## Scope

Robert asked on 2026-05-01 to add a project/task titled `AI workers Setup` and build it out as a durable AI Workspace packet and actionable task structure.

This slice is planning and routing only. It must not mutate external systems, send email, browse external sources, change credentials, run live OAuth/auth setup, alter LaunchAgents/runtimes, create OPS/Portal tasks, or change production data unless a later approval explicitly opens that lane.

## Current Owner Follow-Up

Assigned to Robert for 2026-05-27 after Robert deferred the remaining open owner-input follow-up by one week on 2026-05-18:

1. Authoritative FOH guide source.
2. Google Doc or other authoritative 2026 JD links for workers that should be checked off.

OPS task records for the remaining owner-input follow-up:

- `369792` — `AI Workers Setup: Provide Customer Service inbox address` — completed silently on 2026-05-17 after source-first verification of the local OPS event-support inbox candidate `customerservice@kovaldistillery.com`
- `369793` — `AI Workers Setup: Provide authoritative FOH guide source` — due date moved from 2026-05-20 to 2026-05-27 on 2026-05-18
- `369794` — `AI Workers Setup: Provide worker 2026 JD links` — due date moved from 2026-05-20 to 2026-05-27 on 2026-05-18

Shared Google Doc source link supplied on 2026-05-19 and available via Frank, Avignon, and National Outreach:

`https://docs.google.com/document/d/1d1jZ2kYZQKHjDJQeK5KP7RetT-D76gspeNGsVa113cQ/edit?tab=t.9kpfoptryfb4`

Google Docs API body-read result on 2026-05-19:

- Title: `FOH Handbook 2`
- The extractable body text is only the cover/title page and contact block.
- The body text does not include worker names, role guidance, or persona guidance.
- The first paragraph includes one inline object, likely the cover image/logo.

Working synthesis note created on 2026-05-19:

`project_hub/artifacts/ai-workers-setup/shared-worker-persona-guidance-2026-05-19.md`

Local progress note on 2026-05-19: Frank now has a concrete local JD source at `frank/JOB_DESCRIPTION.md`, National Outreach / Vanessa now has `nationaloutreach/JOB_DESCRIPTION.md`, Asher and Venetia now have local JD sources too, and Naomi, Ezra, Task Manager, Decision Driver, AI Manager Robert, and AI Health Manager have been given local JD sources as well. The shared Google Doc source link above is the durable canonical FOH source reference, but its body read did not contain the missing worker-role guidance.

FOH Handbook 2 general guide source supplied on 2026-05-19 and exported locally:

`https://docs.google.com/document/d/1TYYcUs0aywlVpGRTgItzGrP5Lt_pCPkeOZ1sEYHq0b0/edit?tab=t.0#heading=h.8l2kjwu7nqdf`

Local markdown guide:

`project_hub/artifacts/ai-workers-setup/foh-handbook-2-guide.md`

Source note:

`project_hub/artifacts/ai-workers-setup/foh-handbook-2-guide-source-2026-05-19.md`

Guide summary:

`project_hub/artifacts/ai-workers-setup/foh-handbook-2-guide-summary-2026-05-19.md`

This second doc is the actual full FOH guide. It now serves as the general KOVAL reference for brand language, service standards, internal communications, email FAQ, Portal reporting, and back-bar/service setup.

## Reconciled Audit Pass

- All named workers now have a current local `JOB_DESCRIPTION.md` source on disk.
- The FOH guide is now sourced and exported locally, so the general-reference gap is closed.
- The remaining audit work is bookkeeping only: normalize any final Google Doc link references if you want them recorded, and keep Customer Service blocked until the role itself is named or approved.
- The supporting communications stack was normalized in the source docs too: `communications-manager.md`, `email-coordinator.md`, `internal-communicator.md`, `marketing-manager.md`, `frank/PERSONA.md`, and `nationaloutreach/PERSONA.md` were expanded to match the current guide-level detail.
- The remaining persona files now match that same level of detail too: `worker_roles/asher-wilde/persona.yaml`, `worker_roles/venetia-tempest-dunn/persona.yaml`, `worker_roles/naomi-stern/persona.yaml`, `worker_roles/ezra-katz/persona.yaml`, and `worker_roles/outreach-coordinator.md` were tightened to the same operating-spec style.
- The mixed-format Asher and Venetia worker docs were also normalized: `worker_roles/asher.md` and `worker_roles/venetia.md` now use the same scaffold style as the other mailbox worker docs.
- The directory-level reference docs were tightened as well: `worker_roles/README.md` and `worker_roles/human-owners.md` now read as concise operating references instead of mixed note formats.

## Current JDs Guide

Created in the JDs folder on 2026-05-19:

Google Doc:
`https://docs.google.com/document/d/1YWnwhGK491GCPqR3MYzkshThLVWO5UOlaLYpi-EScEc/edit?usp=drivesdk`

HTML mirror:
`project_hub/artifacts/ai-workers-setup/ai-workers-jds-guide.html`

This is the current working guide for the active worker set. It now includes the expanded role families, the outreach-role correction for Vanessa Sterling, and the same rule that the full FOH guide plus local `JOB_DESCRIPTION.md` files are the source of record instead of the long source material being duplicated here.

## Persona Gap Check

- No additional personas are clearly required for the currently named worker set.
- Customer Service remains the only obvious future persona candidate, but only if the role is approved and the inbox connection is opened. Working name in the guide: `Guest Experience`.
- Communications Manager, Email Coordinator, Internal Communicator, Marketing Manager, and Outreach Coordinator are already distinct roles, so they do not need new personas unless a later role split creates a genuinely different voice or approval boundary.
- If the later 2026 vs 2023 comparison shows a truly distinct voice or approval boundary, add a persona only for that distinct lane rather than expanding the current set by default.

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

## 2026-05-17 Naomi Finance Setup Lane Readback

Due-worker item `taskflow-ai-workers-setup-naomi-finance-2026-05-12` was completed as a docs-only planning slice.

Artifacts created:

- `project_hub/artifacts/ai-workers-setup/naomi-finance-task-map-2026-05-17.md`

What this lane now records:

- Naomi finance task map for BID reporting/management, Portal financial reports, overdue invoice reminders, Portal invoice creation, and related QuickBooks/AP/AR context.
- Recommended workspace split: `ws bid` for BID finance evidence/cadence, `ws portal` for approved Portal finance writes, and `ws ai` / Task Manager for owner decisions and routing.
- Explicit approval gates for live finance mutation, Portal writes, external finance reminders, invoice creation, accounting/tax decisions, and credentials/OAuth/private finance sources.
- First safe read-only deliverable for each Naomi task area so later implementation lanes have a bounded starting point.

Source basis used:

- `worker_roles/naomi-stern.md` and `worker_roles/naomi-stern/persona.yaml`
- BID handoff notes for 2026-05-14 live QBO/workbook/report work and 2026-04-30 onboarding/QBO setup state
- `bid/data-management/finance-action-reports/NAOMI-FINANCE-CADENCE-REQUIREMENTS-2026-05-01.md`
- `bid/data-management/finance-action-reports/NAOMI-CREDIT-CARD-TAX-RECORDING-AUTOMATION-PROPOSAL-2026-05-15.md`

No external sends, Portal/BID/QuickBooks mutation, credential handling, or auth/runtime changes were performed in this lane.

## 2026-05-01 National Outreach Task Flow Runtime Fix

Robert approved fixing the remaining polling/runtime gap.

Actions taken:

- Patched `scripts/nationaloutreach_mail_cycle.py` so actionable National Outreach intake for Vanessa/Outreach, internal COTeam communication, Naomi finance, and Ezra special-project/legal-affairs routes now emits Task Flow packets with `status=routed` instead of passive `classified`.
- Mapped routed worker identities to the actual personas:
  - Vanessa/Outreach/Internal: `vanessa.sterling@kovaldistillery.com`
  - Naomi finance: `naomi.stern@kovaldistillery.com`
  - Ezra special projects/legal affairs: `ezra.katz@kovaldistillery.com`
- Added a staffing/team-message classifier before generic marketing classification so shift/team messages such as the Maker's Market staffing case route to Vanessa/Outreach even if the message also contains promotion/event wording.
- Changed the Task Flow event emitted for routed records from `email_classified` to `email_routed`.
- Synced the patched source into the installed National Outreach runtime copy at `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py`.

Verification:

- `python3 -m py_compile scripts/nationaloutreach_mail_cycle.py` passed.
- `python3 -m py_compile /Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py` passed.
- Runtime classifier spot-check for `Fwd: Saturday 5/2 Makers Market Shift 12-6` returns `outreach-coordinator`, `routed`, `vanessa.sterling@kovaldistillery.com`, `email_routed`.

Boundary:

- No external email was sent.
- No mailbox message bodies were printed.
- No hidden Workspaceboard sessions were created from the poller. The poller now records correct Task Flow route state; Task Manager still owns creating/reusing visible worker routes and recording completion/blocker readback.

## 2026-05-16 Task Flow Scheduler-Bridge Readback

Workspaceboard session `2443a392` took over the unscheduled AI Workers Setup Task Flow rows and verified the source packet before rewriting the next action for each lane.

Per-lane readback:

- `taskflow-ai-workers-setup-calendar-auth-mapping-2026-05-12`: source packet already defines the calendar/auth inventory scope and existing non-secret context; keep this as a read-only planning lane with next check `2026-05-17 09:50 CDT`.
- `taskflow-ai-workers-setup-email-polling-inbox-2026-05-12`: source packet plus AI Workspace handoff/TODO already confirm Frank/Avignon 15-second polling, National Outreach active inbox runtime, and Asher/Venetia header-only references; keep this as a read-only polling-map lane with next check `2026-05-17 09:40 CDT`.
- `taskflow-ai-workers-setup-customer-service-inbox-faq-2026-05-12`: exact blocker confirmed from source review: the planning packet still does not name the Customer Service inbox to connect or the authoritative FOH guide source, so the lane cannot move past setup planning until those two source facts are supplied.
- `taskflow-ai-workers-setup-ezra-project-support-2026-05-12`: Ezra role doc exists and the planning packet defines a docs-only intake/escalation lane; keep this as an `Ezra Katz` planning lane with next check `2026-05-17 10:20 CDT`.
- `taskflow-ai-workers-setup-reminder-runner-mapping-2026-05-12`: Task Flow/due-runner and reminder verification surfaces already exist; keep this as a read-only reminder-map lane with next check `2026-05-17 09:30 CDT`.
- `taskflow-ai-workers-setup-worker-role-audit-2026-05-12`: worker role docs/personas already exist for the named roles; keep this as the role-audit lane with next check `2026-05-17 10:30 CDT`.
- `taskflow-ai-workers-setup-naomi-finance-2026-05-12`: Naomi role docs plus BID/Portal/National Outreach finance readbacks already exist; keep this as a `Naomi Stern` planning lane with next check `2026-05-17 10:10 CDT`.
- `taskflow-ai-workers-setup-vanessa-tasting-directives-2026-05-12`: National Outreach directive sources already exist, including the Illinois tasting compliance directive and OPS/tasting route context; keep this as a `Vanessa Sterling` planning lane with next check `2026-05-17 10:00 CDT`.
- `taskflow-ai-workers-setup-internal-communicator-weekly-recap-2026-05-12`: the Internal Communicator role doc exists, but the weekly-recap lane depends on the Vanessa directive index plus reminder-runner mapping for its source packet; keep this waiting on those internal planning dependencies with next check `2026-05-17 10:45 CDT`.

## 2026-05-17 Vanessa Tasting Directives Lane Output

Completed docs-only lane output:

- Artifact: `project_hub/artifacts/ai-workers-setup/vanessa-tasting-directive-index-2026-05-17.md`
- Scope covered: directive index, account rule matrix, Mitch weekly overview verification checklist, and open-tastings group-message approval path.
- Source basis: `nationaloutreach/ILLINOIS_TASTING_COMPLIANCE_DIRECTIVE.md`, `nationaloutreach/WHOLE_FOODS_TASTING_PLANNING.md`, `nationaloutreach/TODO.md`, `nationaloutreach/HANDOFF.md`, `nationaloutreach/PERSONA.md`, `worker_roles/outreach-coordinator.md`, and the 2026-05-01 Salesreport chain-store product-carry note.
- Readback: this lane stayed within the approved planning boundary. No OPS mutation, calendar write, mailbox action, Portal write, external send, auth/OAuth work, or runtime change was performed.
- Dependency impact: the Internal Communicator weekly-recap lane no longer needs to wait on the Vanessa directive index portion of its packet; any remaining dependency is now only the reminder-runner mapping lane.

Verification:

- Reviewed `worker_roles/internal-communicator.md`, `worker_roles/naomi-stern.md`, `worker_roles/ezra-katz.md`, and `worker_roles/operating-model.md`.
- Reviewed AI Workspace handoff/TODO references for polling, Naomi finance, Vanessa tasting/compliance, and Ezra project-support context.
- Live Task Flow queue readback on `2026-05-16 21:27 CDT` showed all nine AI Workers Setup keys tied to Workspaceboard session `2443a392`; the scheduler-bridge pass replaced the generic routed placeholder with lane-specific waiting/blocker follow-up.

Boundary:

- This pass stayed inside docs/routing/state only.
- No OPS/Portal task was created.
- No mailbox body reads, sends, auth changes, runtime changes, Google Doc writes, or production mutations were performed.

## 2026-05-17 Calendar/Auth Mapping Readback

Workspaceboard due-worker session `ab21fe4c` verified the current non-secret calendar/auth sources before closing `taskflow-ai-workers-setup-calendar-auth-mapping-2026-05-12`.

Calendar/auth matrix:

| Worker / lane | Calendar target | Current source-backed status | Intended status | Source docs | Auth / storage boundary | Next approved action |
| --- | --- | --- | --- | --- | --- | --- |
| Frank | Robert calendar | Verified. Frank's approved helper/config path documents Robert sharing his calendar to `frank.cannoli@kovaldistillery.com`, and later read-only verification showed Robert's calendar visible through the Frank helper path. | Frank can use the shared Robert calendar for approved lookups, reminders, and follow-ups. | `frank/GOOGLE_CALENDAR_SETUP.md`; `frank/TODO.md`; `frank/HANDOFF.md` | Frank desktop OAuth client plus machine-local Frank token. Keep token local to the Frank host; do not move token storage into synced workspace docs. | No auth change is needed for this planning lane. Route a separate runtime/code slice only if Robert wants broader default multi-calendar reporting or new mutation behavior. |
| Frank | Frank's own calendar | Partially sourced. The auth model clearly uses the Frank Google account as the consent identity, so Frank's primary calendar is the intended base path, but this pass did not find a separate readback line proving a Frank-primary event workflow. | Frank individual calendar path for Frank-owned reminders and follow-ups when the workflow calls for Frank's own calendar instead of Robert's. | `frank/GOOGLE_CALENDAR_SETUP.md`; `frank/AGENTS.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Same Frank desktop OAuth client and machine-local Frank token path as above. | Before any Frank-own-calendar workflow is relied on, do one narrow helper readback against the Frank primary calendar and record it in Frank handoff/TODO state. |
| Avignon | Sonat calendar | Verified only through Frank's helper path. Read-only Frank-side verification showed Sonat's calendar visible, and shared docs say Avignon may use an individual calendar path when available, but no separate Avignon helper is currently sourced. | Avignon should have Sonat/Avignon reminder and follow-up support, either through a verified Avignon individual path or the already-approved Frank helper path. | `frank/TODO.md`; `frank/HANDOFF.md`; `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Current verified visibility depends on the Frank machine-local client/token path. A separate Avignon helper/runtime would be a new auth/runtime slice. | Keep using the verified Frank-helper route for planning/readback. If Robert wants a separate Avignon runtime/helper, route Security Guard and Code/Git Manager review before implementation. |
| Avignon | Avignon's own calendar | Not source-verified. Shared docs allow an Avignon individual path when available, but this pass found no non-secret source that names or verifies a distinct Avignon-primary calendar/helper. | Avignon individual calendar path for Sonat/Avignon reminders if a separate Avignon calendar identity is later approved and implemented. | `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | No verified separate Avignon auth client/token path is documented in current non-secret sources. | Exact current gap: missing verified Avignon-specific helper/identity mapping for an Avignon-primary calendar. Do not guess the calendar identity; keep reminder execution on scheduled-action or Frank-helper paths until a separate Avignon path is explicitly sourced. |
| National Outreach / Vanessa | `KOVAL Outreach Events` | Verified. OPS-linked calendar inventory and shared email-worker docs both point to `KOVAL Outreach Events` as the current shared Outreach calendar. | Shared National Outreach calendar for Vanessa reminders, tastings, and outreach follow-up when calendar execution is appropriate. | `frank/TODO.md`; `frank/HANDOFF.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Shared National Outreach calendar path supplements the durable task/scheduled-action record; it does not replace OPS/task state. | No auth change is needed in this planning lane. Use the shared Outreach path for future verified reminder/event workflows. |
| Naomi | Shared National Outreach calendar lane | Policy-defined, not separately verified in this pass. Shared docs explicitly route Naomi and other shared-inbox personas to the National Outreach calendar path when available. | Shared reminder/calendar support through the Outreach lane when Naomi-owned reminders need calendar backing. | `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Shared National Outreach helper path, not a Naomi-specific auth client. | Keep this as shared-lane planning until a Naomi-specific reminder workflow needs a concrete calendar readback. |
| Ezra | Shared National Outreach calendar lane | Policy-defined, not separately verified in this pass. Shared docs explicitly route Ezra and other shared-inbox personas to the National Outreach calendar path when available. | Shared reminder/calendar support through the Outreach lane when Ezra-owned reminders need calendar backing. | `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`; `docs/email-workers/2026-04-30-shared-intake-task-completion-flow.md` | Shared National Outreach helper path, not an Ezra-specific auth client. | Keep this as shared-lane planning until an Ezra-specific reminder workflow needs a concrete calendar readback. |

Auth/setup work that still needs reviewed implementation before execution:

- A separate Avignon helper/runtime remains unsourced in current non-secret docs. If Robert wants Avignon to stop depending on the Frank helper path for Sonat calendar visibility, that implementation should be routed as a new auth/runtime slice with Security Guard and Code/Git Manager review first.
- Frank-own-calendar workflows should get one narrow readback proof before they are used as a claimed verified path in later packets.
- Calendar-backed reminders should continue following the shared rule: durable task or scheduled-action record first, calendar second. If the calendar route is not verified for that identity, record the blocker and use the scheduled-action path instead.

Current gaps / boundaries:

- This pass did not read calendar event bodies, create/edit/delete events, change OAuth scopes, move token storage, or perform any Google auth/runtime mutation.
- Customer Service, Asher, and Venetia do not add new calendar/auth facts in the currently sourced planning docs, so they remain outside this lane's verified matrix for now.

## 2026-05-17 Reminder Runner Mapping Readback

Workspaceboard due-worker session `7dc067f2` verified the current reminder-runner sources before closing the `taskflow-ai-workers-setup-reminder-runner-mapping-2026-05-12` next check.

## 2026-05-17 Ezra Project Support Lane Readback

Due-worker item `taskflow-ai-workers-setup-ezra-project-support-2026-05-12` was completed as a docs-only planning slice.

Artifact created:

- `project_hub/artifacts/ai-workers-setup/ezra-project-support-intake-checklist-2026-05-17.md`

What this lane now records:

- Ezra intake checklist for project-support and legal-affairs-adjacent work: project name, parties, requested action, source of truth, deadline, sensitivity, approval boundary, and deliverable.
- Escalation matrix covering cross-functional project routing, contract/regulatory/policy questions, privacy/security issues, finance overlap, implementation handoff, and protected-material stop conditions.
- Recommended Task Manager -> Ezra handoff template so future packets include the exact fields Ezra needs before triage begins.
- Safe-default rule that Ezra stays on docs-only triage, business briefing, and escalation framing unless a separate implementation or secure-access lane is explicitly approved.

Source basis used:

- `worker_roles/ezra-katz.md`
- Existing AI Workers Setup planning packet in this project log
- Current AI Workspace TODO context for the project boundaries and active implementation gates

Boundary:

- No mailbox-body review, external send, legal advice, auth/runtime change, credential handling, or live-system mutation was performed in this lane.

Reminder-runner map:

- Shared Task Flow scheduled reminders are stored in the shared MySQL Task Flow tables and read back through `scripts/task_flow_mysql_recorder.php report` / `due`. The report exposes runner state, due-now preview, and upcoming reminder rows.
- The active due-runner execution path is Frank's auto runner: `frank/runtime-source/frank-launch/scripts/frank_auto_runner.py` calls `/Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py` no more than once every `60` seconds and uses `/Users/admin/.task-flow-launch/state/frank-due-runner-last.txt` as the throttle marker.
- The due runner writes durable runner state to `/Users/admin/.task-flow-launch/state/task-flow-due-runner-last.json` with `checked_at`, `due_count`, `recorded`, `skipped_existing`, `actions`, and notification outcome, and it can route due items into a visible Workspaceboard worker session instead of leaving them as silent due rows.
- Workspaceboard's Task Flow page reads the same runner-state and due/upcoming preview surfaces and displays `Last Runner`, `Notification`, `Actions`, and the next due records so reminder verification is visible without opening raw logs.

Verification/readback checklist:

- Task Flow row: verify the packet key, current status, `scheduled_action`, and next update in `scripts/task_flow_mysql_recorder.php report`.
- Due-runner state: verify `/Users/admin/.task-flow-launch/state/task-flow-due-runner-last.json` for the last `checked_at`, due count, newly recorded items, skipped duplicates, and notification result.
- Visible-worker handoff proof: when a due item is routed instead of externally emailed, verify the routed Workspaceboard session id in the runner summary and the packet `verification_readback`.
- UI/operator surface: verify `workspaceboard/task-flow.html` via `assets/task-flow.js` rendering of reminder-runner stats and due/upcoming rows.

Current live readback on `2026-05-17 09:32 CDT`:

- Due runner state showed `checked_at=2026-05-17T09:32:47-0500`, `due_count=1`, `recorded=1`, `skipped_existing=0`, `notification.reason=no_owner_visible_due_items`.
- The due item was this exact planning lane, and the due runner routed it into visible Workspaceboard session `7dc067f2` with prompt delivery confirmed instead of sending external email.
- Immediate follow-up `due` readback returned `due_count=0`; the next scheduled AI Workers Setup reminder lane is the polling/inbox map at `2026-05-17 09:40 CDT`.

Current gaps / boundaries:

- Internal planning reminders like this one are auditable through Task Flow state and visible-worker routing, but they intentionally suppress owner-visible email when `notification.reason=no_owner_visible_due_items`.
- Calendar-native reminder creation and calendar event ID verification are still separate work under the calendar/auth lane; this reminder-runner mapping only covers the current Task Flow and worker-driven reminder surfaces.
- The due-runner summary currently reports `watchdog_script_missing` for `/Users/werkstatt/ai_workspace/scripts/automation_health_watchdog.py`; that does not block reminder routing, but it means watchdog readback is not part of the active reminder verification path today.

Boundary:

- This pass stayed inside docs/routing/state only.
- No external email was sent.
- No runtime, LaunchAgent, auth, mailbox, OPS, Portal, Google Doc, or production data mutation was performed.

## 2026-05-17 Internal Communicator Weekly Recap Readback

Due-worker item `taskflow-ai-workers-setup-internal-communicator-weekly-recap-2026-05-12` was completed as a docs-only planning slice after verifying that its two named dependencies were now present.

Artifact created:

- `project_hub/artifacts/internal-communicator/weekly-internal-recap-workflow-packet-2026-05-07.md`

What this lane now records:

- A reusable source packet for Internal Communicator weekly recap drafting on AI Workers Setup.
- The dependency clear for the Vanessa directive artifact and the reminder-runner mapping readback.
- A verified list of safe recap talking points: completed planning packets, the exact Customer Service blocker, and the remaining live-send approval gates.
- A short internal recap structure so future recap work can be drafted without re-deriving the source packet.

Current readback:

- The earlier project index pointed to a weekly recap packet path that was not present on disk at the start of this pass; this pass wrote that missing packet at the referenced path so the source-of-truth pointer is now real.
- The lane is no longer blocked on the Vanessa directive index or the reminder-runner mapping. Both dependencies now exist in the project packet.
- The first live weekly recap remains approval-gated on previous examples, approved image source rules/folders when applicable, and final audience/sender/approval cadence. This pass did not send or queue any internal email.

Boundary:

- This pass stayed inside docs/routing/state only.
- No mailbox-body review, send, auth/runtime change, Google Doc write, or production mutation was performed.

## 2026-05-17 Worker Role / Job Description Audit Lane Readback

Due-worker item `taskflow-ai-workers-setup-worker-role-audit-2026-05-12` was completed as a docs-only audit slice.

Artifact created:

- `project_hub/artifacts/ai-workers-setup/worker-role-job-description-audit-checklist-2026-05-17.md`

What this lane now records:

- A per-worker audit for Frank, Avignon, National Outreach / Vanessa, Naomi, Ezra, Customer Service, Asher, Venetia, AI Manager, Task Manager / Polier, Decision Driver, and AI Health Manager.
- For each worker: current duties, checked local role/persona/job-description sources, whether a Google Doc link is already recorded, whether a 2026 JD source is currently visible, and the next docs-only gap.
- A clear split between workers that already have substantial local role material but still lack a recorded JD source link, and Customer Service, which is still blocked at the role-definition layer.

Current readback:

- Avignon is the strongest current lane for job-description coverage because it already has a local `JOB_DESCRIPTION.md` plus role/persona sources.
- Frank, Vanessa/National Outreach, Naomi, Ezra, Asher, Venetia, AI Manager, Task Manager, Decision Driver, and AI Health Manager all have enough local role/persona material to audit current duties, but this pass did not find a recorded Google Doc link or clearly named 2026 JD check-off source for them.
- Customer Service remains an exact source blocker for this audit family: no worker role doc, persona file, or job-description source was found in the checked local sources, so the lane cannot advance beyond "define the worker and source of authority first."

Boundary:

- This pass stayed inside docs/routing/state only.
- No Google Doc writes, mailbox actions, auth/runtime changes, or external sends were performed.

## 2026-05-17 Email Polling And Inbox Readback

Workspaceboard due-worker session `3cfe18b1` verified the current polling/inbox sources before closing `taskflow-ai-workers-setup-email-polling-inbox-2026-05-12`.

Polling and inbox map:

- Frank: current practical mailbox path remains 15-second polling, not Gmail push. AI Workspace TODO/HANDOFF records the current `15` second mail-polling path, while `frank/runtime-source/frank-launch/scripts/frank_auto_runner.py` also shows the shared Task Flow due-runner check riding inside Frank's auto runner on its own `60` second throttle. Authority today is full Frank email-worker behavior, including body review, routed follow-through, approved send/report paths, and handled filing under Frank guidance; Gmail API push/OAuth remains a separate approval-gated lane.
- Avignon: current mailbox path remains 15-second polling. AI Workspace TODO/HANDOFF records the current `15` second Avignon polling path, and `avignon/runtime-source/avignon-launch/scripts/avignon_inbox_cycle.py` is the active full-body inbox cycle/source mirror. Authority today includes Avignon direct-owner/body review, approved completion/blocker reporting, and handled filing under Avignon SOP guidance; Gmail push/OAuth remains separate and approval-gated.
- National Outreach: shared inbox is `nationaloutreach@kovaldistillery.com`, with Email Coordinator owning intake/routing and worker personas routed from that shared inbox. `docs/email-workers/2026-04-27-nationaloutreach-ai-worker-inbox.md` plus the staged plist `tmp/nationaloutreach-launch/com.koval.nationaloutreach-auto.plist` show a `StartInterval` `60` second LaunchDaemon path using `scripts/nationaloutreach_mail_cycle.py`. That runtime has full-body review, private-state capture, route suggestion/classification, and approved queued-send capability, but it still does not move, delete, or file mailbox messages automatically.
- Asher: current state remains one separate Asher mailbox on a 60-second header-only polling route. `docs/email-workers/2026-04-27-asher-venetia-setup.md` records a live `60` second LaunchDaemon with header metadata only. Body reads, filing, deletes, routine action authority, and send behavior remain explicitly blocked pending final policy approval.
- Venetia: current state mirrors Asher as a separate Venetia mailbox on a 60-second header-only polling route. The same setup doc records live `60` second header-only polling only, with body reads, filing, deletes, routine action authority, and send behavior still approval-gated.
- Customer Service inbox: no mailbox is connected yet in this planning slice. The inbox identity to connect is still unnamed, and the authoritative FOH guide source is still unspecified. Until those two source facts exist, this lane can document prerequisites but cannot move into mailbox auth, body review, FAQ extraction, or customer-response authority.

Authority and approval-gate summary:

- Frank and Avignon are the only current KOVAL inbox workers in this lane with documented 15-second practical polling and end-to-end worker authority for review/routing/reporting under existing guidance.
- National Outreach has broader shared-inbox/body-read capability than Asher/Venetia and can send only through approved queued-send paths and allowed send-from identities; auto filing/moves remain out of scope.
- Asher and Venetia are intentionally limited to header-only polling and source tracking until Robert/Sonat/Avignon provide the final persona/action policy for body reads, filing, deletes, replies, and routine send authority.
- Customer Service remains planning-only until the inbox, FOH answer source, and browsing/reply boundaries are named and approved.

Verification/readback checklist:

- Frank/Avignon cadence and current-practical-path proof: `TODO.md`, `HANDOFF.md`, and worker handoff records showing the 15-second mail-polling path plus the separate 60-second Task Flow due-runner throttle inside Frank's auto runner.
- National Outreach cadence and scope proof: `docs/email-workers/2026-04-27-nationaloutreach-ai-worker-inbox.md`, `tmp/nationaloutreach-launch/com.koval.nationaloutreach-auto.plist`, and `scripts/nationaloutreach_mail_cycle.py`.
- Asher/Venetia cadence and scope proof: `docs/email-workers/2026-04-27-asher-venetia-setup.md`.
- Shared closeout/task-flow surfaces: `scripts/task_flow_mysql_recorder.php report`, the Task Flow page, and the packet `verification_readback`.

Current result:

- The polling/inbox map is now written from current source/docs state with cadence, read scope, send/follow-through authority, and approval gates separated by worker.
- No new source blocker remains for this lane. The remaining Customer Service inbox facts are already captured as a separate planning blocker under `taskflow-ai-workers-setup-customer-service-inbox-faq-2026-05-12`, not as a blocker for closing this polling-map lane.

Boundary:

- This pass stayed inside docs/routing/state only.
- No external email was sent.
- No mailbox bodies were printed.
- No runtime, LaunchAgent, auth, OAuth, Google Doc, OPS, Portal, or production data mutation was performed.
