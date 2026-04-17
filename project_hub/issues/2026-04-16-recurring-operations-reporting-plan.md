# Recurring Operations Reporting Plan

- Master Incident ID: `AI-INC-20260416-RECURRING-OPERATIONS-REPORTING-01`
- Date Opened: 2026-04-16
- Date Completed: 2026-04-16 for this planning slice
- Owner: AI Workspace planning; implementation split by owner module
- Priority: Planning
- Status: Planning slice complete; no implementation started

## Scope

Define a local, no-write plan for recurring operations reporting. This slice records owner modules, read-only source surfaces, cadence, approval gates, the first no-write slice, and notification/email boundaries for future reporting around monthly task stats send-out, events/task stats review cadence, and the barrel sample page manual/follow-up.

This pass is documentation only. It does not inspect credentials, connect to production databases, read production rows, send email, create notifications, modify tasks, implement code, deploy, restart services, schedule jobs, or commit changes.

## Reporting Goals

- Give operations owners a predictable view of task throughput, event activity, and follow-up health.
- Keep monthly task stats separate from event review and barrel sample follow-up until source ownership and send authority are approved.
- Identify manual follow-up work without silently creating tasks, emails, reminders, or production records.
- Define a first no-write inventory that can be reviewed before any live data, report generation, or staff-facing distribution begins.

## Owner Modules

| Area | Owner module | Supporting owner | Future worker route | Notes |
| --- | --- | --- | --- | --- |
| Monthly task stats | `ops` | `ai` for planning and metric contract | `ws ops` after `ws ai` planning | Covers task created/completed counts, owner/assignee queues, overdue/open-aging bands, and Codex-owned silent bookkeeping visibility. |
| Events/task stats review | `ops` | Outreach Coordinator for calendar/tasting state | `ws ops`; Outreach Coordinator only for scheduling interpretation | Covers events, market events, linked shifts, event task completion, and follow-up state. Does not approve or change schedules. |
| Portal shift/check-in context | `portal` | `login` for identity joins | `ws portal` with `ws login` source review as needed | Only aggregate check-in/shift context if approved; personnel-sensitive details require redaction review. |
| Barrel sample page manual/follow-up | likely `portal` or `ops`, to be confirmed in source inventory | `salesreport` or `contactreport` only if account/customer follow-up crosses into those modules | First slice stays in `ws ai`; later source owner worker after ownership is confirmed | Ownership is not assumed. Inventory must identify where the barrel sample page lives, who owns follow-up, and whether the page produces tasks, leads, reports, or manual review items. |
| Sales/account follow-up context | `salesreport` / `contactreport` | Communications Manager if outbound copy is needed later | `ws sales` or `ws contactreport` only after source ownership is known | Future reporting may include account follow-up counts, but no sales strategy inference or external communication in this plan. |
| Identity and access joins | `login` | Security Guard for auth/privacy gates | `ws login` | Defines canonical user IDs, active/inactive users, roles, and access state. No token/session inspection in this planning slice. |
| Reporting coordination | `ai_workspace` | Task Manager, Summary Worker | `ws ai` | Owns this project-hub record, TODO/HANDOFF pointers, routing plan, metric contract template, and first-slice coordination. |
| Security/privacy review | Security Guard | Code and Git Manager if code/repo changes begin later | `ws ai` Monitoring layer | Required before production data access, staff-facing reporting, mailbox/admin overlays, scheduled sends, or credential/auth changes. |

## Read-Only Source Surfaces

Allowed for this planning slice:

- Local AI Workspace docs: `TODO.md`, `ToDo-append.md`, `HANDOFF.md`, `project_hub/INDEX.md`, and this project-hub note.
- Existing project-hub records that describe related reporting or task-stat work.
- Local module docs, TODOs, handoffs, and code references in future source inventory work, after routing to the owner workspace.
- Existing app-level report descriptions or screenshots supplied by a human owner.
- Schema/table/report names found in code during a later no-production-data inventory.
- Aggregated, non-sensitive Workspaceboard session metadata only if the report later includes automation routing counts.

Allowed only after a later explicit approval:

- Read-only production `SELECT` queries or app-level exports.
- OPS task/report exports containing user-level operational data.
- Portal shift/check-in or production-audit aggregates.
- Login user/access exports.
- Barrel sample page submissions, leads, or follow-up records.
- Any Google Workspace, Gmail, Admin, or mailbox metadata overlays.

Disallowed in this planning slice:

- Credential lookup, `.env` inspection, OAuth token inspection, app password use, private key access, or Keychain access.
- Production database connections, production row dumps, live API calls, or report generation against live systems.
- Email/mailbox reads, email sends, notifications, reminders, or staff-facing report distribution.
- Task creation/completion, schedule edits, CRM/customer/account writes, or barrel sample follow-up writes.
- Code changes, migrations, deploys, service restarts, LaunchAgent changes, background polling, commits, or pushes.

## Cadence

Recommended future cadence, pending approval:

| Cadence | Report | Audience | Owner | Boundary |
| --- | --- | --- | --- | --- |
| Weekly | Events/task stats review | Operations owner or Task Manager summary surface | `ops` | Review-only. No schedule or task mutation without separate approval. |
| Monthly | Task stats send-out | Robert/approved operations recipients | `ops` with `ai` coordination | Send-out is not approved by this plan. Recipient list, copy, delivery method, and duplicate protection must be approved first. |
| Monthly | Barrel sample page manual/follow-up review | Source owner once confirmed | owner module TBD | First live version should identify pending manual follow-up only; no automatic outreach or CRM/task creation. |
| Quarterly | Metric and source review | AI Workspace plus module owners | `ai` | Confirm source ownership, retired reports, redaction level, and approval gates. |

No recurring job, daemon, scheduled email, reminder, or notification is authorized by this planning slice.

## Approval Gates

Human approval is required before:

- Any production data access, export, live API read, SQL query, or report run.
- Any staff-facing or management-facing report distribution.
- Any monthly task stats email, notification, reminder, or scheduled send.
- Any new recipient list, CC list, subject line, report copy, or automatic duplicate-protection mechanism.
- Any barrel sample follow-up task creation, CRM/contact/account write, or outbound communication.
- Any event, market event, shift, calendar, or tasting state change.
- Any credential, OAuth, service-account, Keychain, `.env`, mailbox, Google Admin, Gmail, or permission-scope work.
- Any code change, deploy, database migration, service restart, LaunchAgent/runtime change, commit, or push.

Security Guard must review any future slice touching credentials, auth/access, Google Workspace/Admin/Gmail, mailbox surfaces, OAuth scopes, production permissions, cross-machine access, sensitive personnel data, or approval-gate ambiguity.

Code and Git Manager must review any future code-producing slice in a git-backed repo before implementation and again before any commit, push, deploy, live pull, or cleanup.

## First No-Write Slice

When Robert approves moving beyond this planning record, the first slice should still be no-write:

1. Keep coordination in `ws ai`.
2. Create a metric contract template with columns for report name, metric, owner module, source candidate, join key, time grain, privacy level, verification method, cadence, audience, and approval gate.
3. Route source-inventory workers to owner modules only for docs/code/schema-reference inspection, not production data access.
4. Confirm barrel sample page ownership and whether its follow-up belongs to `portal`, `ops`, `salesreport`, `contactreport`, or another module.
5. Produce a candidate monthly task stats report spec with no recipients, no delivery job, and no live data.
6. Produce a candidate events/task stats review checklist with no schedule or task mutation.
7. Run Security Guard review before any live data, email, notification, mailbox/admin overlay, or credential-bearing work.

Exit criteria for the no-write slice:

- Owner module is named for each report line.
- Every source surface is classified as docs-only, code/schema-reference-only, app-level export, production read, or disallowed.
- Every future live read has an approval owner and privacy level.
- Notification/email boundaries are explicit enough that a worker cannot accidentally send a report.

## Notification And Email Boundaries

- This plan does not authorize any outgoing email, Portal notification, OPS reminder, calendar invite, Slack/chat message, or staff-facing distribution.
- Monthly task stats send-out remains a future design item, not an active send.
- Before any send-out exists, a later slice must define owner, audience, sender identity, recipients, CC/BCC rules, copy, cadence, opt-out/disable path, duplicate protection, dry-run procedure, and rollback.
- Frank and Avignon must not send operations reporting summaries from this plan. They may only use a separately approved task-specific completion confirmation or morning-summary rule within their existing boundaries.
- Task completion confirmations are not substitutes for reporting send-out approval.
- If a future report is generated but send authority is unclear, it must stay as a local draft/spec and the blocker must be surfaced to Robert.

## Open Decisions For A Later Slice

- Which owner should receive monthly task stats: Robert only, operations managers, module owners, or a broader team list?
- Should monthly task stats be a Markdown report, dashboard, CSV export, Portal page, OPS page, or email?
- What is the canonical definition of a completed task for monthly stats, especially for silent Codex bookkeeping tasks?
- Which event states count as active, completed, canceled, or needing follow-up?
- Where does the barrel sample page live, and who owns manual follow-up?
- Should barrel sample follow-up create OPS tasks, Portal tasks, sales/account follow-up, or only a review list?
- What redaction level is acceptable for user-level operational stats?

## Verification Notes

- Read `TODO.md`, `ToDo-append.md`, `HANDOFF.md`, `project_hub/INDEX.md`, and the existing unified user activity reporting plan.
- Confirmed the active append queue is empty.
- Confirmed this pass stayed local and docs-only.
- No OPS intake, production source access, credentials, email, notification, code, deploy, runtime change, commit, or push was performed.

## Rollback Plan

This is a docs-only planning slice. To roll back, remove this project-hub file and the corresponding `TODO.md`, `HANDOFF.md`, and `project_hub/INDEX.md` entries.

## Follow-Ups

- Ask Robert to approve or reject the first no-write source inventory slice.
- If approved, keep the next slice no-write and route source inventory to owner modules with explicit no-production-data instructions.
- Defer any recurring send/report automation until after source inventory, Security Guard review, and explicit send-boundary approval.
