# Shared Intake -> Task -> Completion Flow

Status: active shared directive
Owner: AI Manager / Task Manager / Email Coordinator
Applies to: terminal intake, Workspaceboard intake, Frank, Avignon, National Outreach, Vanessa, Naomi, Ezra, Codex-routed mail, and future email-worker personas
Created: 2026-04-30

Implementation status as of 2026-04-30: National Outreach, Frank, and Avignon now write shared task-flow capture events through `scripts/shared_task_flow.py` into existing OPS/CRM MySQL tables `koval_crm.ai_task_flow_packets` and `koval_crm.ai_task_flow_events`, with local JSONL audit fallback in each worker state directory. The same helper and MySQL recorder now enforce closeout guards for `completed`, `reported`, and `filed` packets, mark closed packets without projection as `papers_pending`, and expose due reminders through the shared report layer. This capture layer does not replace authoritative OPS/Portal/domain tasks.

## Purpose

This note defines the required end-to-end path for work that arrives through chat/terminal, Workspaceboard, or email. The goal is one traceable lane from intake to execution to owner clarification to timed reminders to completion record.

Markdown files are allowed as indexes and handoffs. They are not the authoritative execution record when the task needs durable follow-up, a due date, a reminder, or another worker to act. Use OPS, Portal, or the appropriate operational system for that record whenever available.

Papers is the target completion/projection layer for clean work records and institutional memory. Do not treat local Markdown as the final long-term record when the work should become part of Papers. Robert has approved Papers writes for this task-flow lane, but the current Codex MCP client must still have `papers_create` / projection write permission enabled before live writes can complete.

## Intake Surfaces

- Terminal/chat: Robert may direct Codex/AI Manager directly. Substantive work should be routed through Task Manager into a visible Workspaceboard worker unless it is a quick safe answer or one safe command.
- Workspaceboard: Task Manager owns visible routing, worker focus, board hygiene, blocker surfacing, and closeout verification.
- Email to Frank: Robert-facing owner intake. Frank captures, clarifies by email when needed, routes visible work, monitors to completion, and reports back to Robert.
- Email to Avignon: Sonat-facing owner intake. Avignon uses the same mechanics through Avignon's persona/SOP boundaries, reporting to Sonat by default and copying Robert only when he is actively supervising or approval context requires it.
- Email to National Outreach: shared worker intake for `nationaloutreach@kovaldistillery.com` and related send-from personas. Email Coordinator classifies the work, then routes Vanessa for outreach/COT/tasting/account work, Naomi for finance-operations follow-up, Ezra for special-project/legal-affairs coordination, Codex for technical/local-agent work, or a module worker when the work belongs in OPS, Portal, lists, forge, or another workspace.
- Portal/report-triggered intake: Portal reports, OPS reports, scheduled report reminders, and calendar due events can create work even when no new email arrives. Treat them as intake records with the same task-storage and completion rules.

## Classification

Classify each intake item before acting:

- FYI/no-action: log if useful, then file/archive.
- Duplicate/already-routed: attach the source to the existing task/session record, then file/archive.
- Quick safe answer: answer through the same owner channel and log the source.
- Substantive work: create or reuse a visible Workspaceboard worker and verify prompt delivery.
- Operational follow-up, reminder, or due-date work: create an OPS task, Portal task, or domain-specific operational task record with owner, due time, status, and source reference.
- External-sensitive, finance/legal/HR, auth/security, credential, production-impacting, destructive/bulk, or suspicious work: route to the relevant owner and Security Guard/approval path before action.

## State Machine

Use these states. Do not invent vague alternatives such as "noted," "logged," or "seen" as completion states.

- `captured`: source received and dedupe key/source reference recorded.
- `classified`: owner lane and task type are known.
- `routed`: visible Workspaceboard worker or owning role is assigned.
- `task_created`: authoritative OPS/Portal/domain task exists when durable execution is needed.
- `scheduled`: due date, scheduled action, calendar event, or report-trigger is recorded when time matters.
- `clarification_needed`: a human answer is required before safe execution.
- `clarification_sent`: the blocker question was sent through the owning channel, normally email for email-owned lanes.
- `working`: an owner/worker is actively executing.
- `waiting`: the task is waiting on a named person/system/dependency with a due check.
- `blocked`: execution cannot continue without a real approval, access, safety, duplicate-target, or missing-fact decision.
- `completed`: the work itself is done and verified from the real system.
- `reported`: required owner completion/blocker email or status report has been sent.
- `filed`: source email/item has been archived/handled after a valid stop condition.
- `papers_pending`: non-secret Papers projection packet exists or is ready, but live write/projection is not yet approved or available.
- `projected`: Papers/MI projection is complete and GUID/path is recorded.

Allowed closeout states are `filed`, `papers_pending`, and `projected`. A task cannot move to `filed` until any required owner report has been sent or the item is documented as no-action/duplicate/already-routed.

## Required Task Packet

Every substantive task must carry this packet, either in OPS/Portal/domain task fields or in the linked handoff when the system lacks a field:

```text
source_ref:
dedupe_key:
intake_channel:
requester:
owner_lane:
responsible_worker_or_persona:
workspaceboard_session:
ops_portal_or_domain_task:
status:
due_or_trigger:
scheduled_action:
calendar_event:
clarification_email:
completion_or_blocker_email:
source_links:
approval_gates:
verification_readback:
papers_projection:
next_update:
```

Leave unknown fields blank only when they truly do not apply. If a required field is missing because a system failed, record the blocker in that field.

## Clarifications

Clarifications should use the same channel that owns the intake unless a safer or clearer channel is explicitly named.

- Email-originated task: send the clarification by email from the responsible persona. Include the original source email quoted or forwarded in the body when the owner needs to review it, unless a safety gate blocks including it.
- Terminal/chat-originated task: ask in chat only when the answer is an immediate blocker. If the work has already moved into an email-owned lane, send the clarification by email and log that email.
- Workspaceboard-originated task: Task Manager or the owning worker asks the smallest exact blocker question, then records the answer on the session/task.
- Portal/report-triggered task: ask by email if a human owner needs to provide missing business context; otherwise record the blocker on the operational task.

Do not ask humans to resolve a Message-ID, source id, session id, or internal blocker code without plain-English context. Lead with the person, account, event, requested action, missing fact, and what will happen after the answer arrives.

## Routing And Task Storage

Use this order for anything beyond a quick safe response:

1. Capture the source: Message-ID, report id, Portal/OPS id, board session, chat date, or source path.
2. Route the work: Task Manager creates or reuses a visible Workspaceboard worker in the correct workspace.
3. Create the operational task record: OPS task is preferred for operational follow-ups, outreach/COT work, reminders, and cross-worker execution; Portal tasks are preferred when the work belongs to a Portal CRM/contact/account/project object; another domain system may be used when it is clearly authoritative.
4. Link the records: source reference, Workspaceboard session id/title, OPS/Portal task id, due date, owner, status, and next update target must point to the same work item.
5. Use Markdown only as an index/handoff: TODO, HANDOFF, project-hub, and worker logs should reference the operational id rather than replacing it.

If deterministic duplicate checks do not identify a safe target record, stop and ask for the missing decision before creating another CRM/contact/account/project record.

## Timed Reminders And Calendars

Reminders must be executable. A note in Markdown is not enough.

- Create a one-item OPS/Portal/domain task with owner, due time, status, and source reference.
- Add a worker-executable scheduled action where the runtime supports it.
- Add a calendar event when the worker has a verified calendar route for that identity or shared lane.
- Use the calendar/report trigger as a wake-up signal, not as the only record. The OPS/Portal/domain task remains the execution source.
- For scheduled deliverables such as "Monday 8:00 AM draft," create a scheduled action that runs or queues the draft at that time; do not convert it into a generic reminder email.
- For report-driven reminders, such as a Portal report that should trigger a review, record the report name/source, expected cadence, due time, owning persona, and next action.

Current calendar routing:

- Frank uses Frank's verified individual calendar path when available.
- Avignon uses Avignon's verified individual calendar path when available.
- National Outreach, Vanessa, Naomi, Ezra, and other shared-inbox personas use the shared National Outreach calendar path when available; the current shared Outreach calendar is `KOVAL Outreach Events`.

If the calendar route is blocked, create the operational task and scheduled-action record anyway, record the calendar blocker, and surface only the real missing setup item.

## Reminder Trigger Registry

Use one of these trigger types so reminders are not confused with generic notes:

| Trigger type | Example | Required execution surface |
| --- | --- | --- |
| fixed_time | `Monday 8:00 AM draft` | OPS/Portal/domain task plus scheduled action; calendar event when available |
| dependency_check | `check whether Loretta/Rick replied in 24 hours` | OPS/Portal/domain task plus scheduled action; email owner only after checking the dependency |
| calendar_event | `event starts in 48 hours` | OPS/Portal/domain task plus calendar event or report-triggered scheduled action |
| report_trigger | `Portal report shows open item due today` | report name/source plus OPS/Portal/domain task and scheduled/report-run action |
| recurring_report | `weekly Monday Outreach draft` | recurring scheduled action or report job plus task/status record |
| escalation_window | `unclaimed shift inside 48 hours` | OPS/domain task or notification log plus duplicate-prevention key |

For each trigger, record the owning persona, expected check time, data source to inspect before sending, and stop condition.

## Owner And Channel Matrix

Default routing:

| Intake | Owner lane | Clarification channel | Completion channel |
| --- | --- | --- | --- |
| Robert email | Frank | email from Frank | email to Robert |
| Sonat email | Avignon | email from Avignon | email to Sonat; copy Robert only when he is supervising or approval context requires it |
| National Outreach/shared inbox | Email Coordinator -> Vanessa/Naomi/Ezra/Codex/module worker | email from responsible persona when clarification is needed | email/status from responsible persona; operational status in OPS/Portal/domain task |
| terminal/chat | AI Manager -> Task Manager | chat only for immediate blocker; email if the work moved into an email-owned lane | chat summary or responsible owner email depending lane |
| Workspaceboard | Task Manager/owning worker | smallest exact blocker question in the owning channel | Workspaceboard closeout plus owner email when required |
| Portal/report/calendar trigger | owning persona or module worker | email when human context is missing; otherwise task blocker/status | task/report closeout plus owner email when required |

## Execution And Monitoring

The owning worker must follow the task until it is completed, blocked, or intentionally transferred:

- Verify the visible worker prompt actually started.
- Monitor or re-check the worker/task at the promised time or trigger.
- Keep the active inbox clear after durable routing; do not leave source mail in INBOX just because the work was logged.
- If a dependency is waiting, check whether it resolved before emailing the owner.
- If an item remains blocked past its reminder interval, send one useful owner email with the original source included for review, not repeated context-poor nags.

## Failure Handling

If one part of the route fails, create the next best durable record and record the exact blocker:

- OPS task creation fails: use Portal/domain task if authoritative, otherwise create a local handoff packet tagged `ops_task_blocked` and surface the OPS blocker.
- Portal task or CRM target is ambiguous: do not create a duplicate record; ask the owner for the exact target and leave the task in `clarification_needed`.
- Workspaceboard route fails: create the OPS/Portal/domain task if safe, record `workspaceboard_route_blocked`, and ask Task Manager to re-route.
- calendar creation fails: keep the OPS/Portal/domain task and scheduled-action record, record `calendar_blocked`, and surface only the calendar setup/access blocker.
- scheduled-action runtime fails: keep the OPS/Portal/domain task and calendar event if available, record `scheduled_action_blocked`, and route a runtime fix if approved.
- email send fails: keep the task open, save or record the intended clarification/completion email, mark `email_send_blocked`, and do not file the source email as handled.
- Papers projection is unavailable: keep the non-secret packet in OPS/project-hub/HANDOFF, mark `papers_pending`, and do not claim projection completed.
- read-back verification fails: keep the task in `blocked` or `waiting`; do not mark completed from assumptions.

## Completion And Filing

A task is not complete until the execution record and owner-visible closeout are both handled when required.

Required closeout steps:

1. Verify the actual work result from the operational system, worker output, sent-log, mailbox state, report output, or live read-back surface.
2. Update the OPS/Portal/domain task status to completed, blocked, or transferred.
3. Send the responsible owner a completion or blocker email when the lane requires it. Use the responsible persona and include what was done, what changed, what was not done, relevant IDs/links, remaining approvals, and the original source email when the owner needs to review it.
4. File/archive the source email only when it is no-action, duplicate/already-routed, completed-with-report, or blocked-with-report.
5. Update TODO/HANDOFF/project-hub as a concise index, not as a substitute for the operational task record.
6. Prepare the Papers projection packet when the work should become long-term institutional memory.

Closeout checklist before filing:

- state is `completed`, `reported`, `papers_pending`, or `projected`, or the item is explicitly no-action/duplicate/already-routed;
- real read-back was checked from the execution surface;
- OPS/Portal/domain task status is updated;
- reminder is closed, rescheduled, or left waiting with a next check;
- required clarification, completion, or blocker email was sent or recorded as blocked;
- source email is filed only after the valid stop condition;
- Papers packet is created, projected, or marked `papers_pending`;
- remaining owner decision, if any, is plain-English and traceable.

## Papers Projection Packet

When the work is completed or reaches a durable blocker, prepare a non-secret packet suitable for Papers/MI projection:

- title and date;
- owner and responsible worker/persona;
- source references without private body dumps;
- OPS/Portal/task/session ids;
- changed records, files, or systems;
- verification/read-back evidence;
- sent Message-ID or report reference when applicable;
- remaining gates or next owner;
- privacy/security exclusions.

Do not include credentials, raw tokens, private keys, private mailbox body dumps, private SOP text, payment details, or unauthorized access instructions. If live Papers write access is unavailable for the lane, keep the packet in project-hub/HANDOFF/OPS as the local durable source and mark Papers projection pending.

## Required Trace IDs

Use as many of these as apply:

- source Message-ID, report id, source path, or chat date;
- dedupe key;
- Workspaceboard session id and title;
- OPS/Portal/domain task id;
- calendar id and event id for timed work;
- scheduled-action id/path for runtime-triggered work;
- sent Message-ID for owner clarification, completion, or blocker email;
- Papers GUID/path when projected.

## Boundaries

- Do not hide substantive work inside standing inbox monitors.
- Do not rely on Markdown-only reminders for time-sensitive work.
- Do not file direct-owner work to Handled merely because it was seen or logged.
- Do not send external business commitments, finance/legal decisions, auth/credential instructions, or production-impacting approvals without the applicable approval.
- Do not create duplicate CRM/account/contact/task records when the target is ambiguous.
- Do not claim a task is complete without read-back from the real execution surface.
