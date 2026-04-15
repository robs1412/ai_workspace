# Digital Office Project/Task/Work Record Source-of-Truth Proposal

- Last Updated: 2026-04-14 12:05:01 CDT (Machine: Macmini.lan)
- Date: 2026-04-14
- Workspace: `ai_workspace`
- Master ID: `AI-INC-20260414-DIGITAL-OFFICE-WORK-RECORDS-01`
- Status: proposal complete; implementation pending approval
- Scope: docs-only planning and object-model prototype

## Task

Group TODOs/tasks into projects and define DB-backed project/task/work recording for the KOVAL Digital Office model, without mutating Papers, `.205`, production databases, OPS/Portal schema, secrets, or runtime services.

## Inputs Reviewed

- `TODO.md`
- `ToDo-append.md`
- `HANDOFF.md`
- `ai-digital-office.md`
- `project_hub/INDEX.md`
- `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-claude-papers-durable-tracking-plan.md`
- `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-digital-office-routing-closeout.md`
- `worker_roles/operating-model.md`

## Open TODO Reminder

Current open AI Workspace work at proposal time:

- Disable Codex daily notifications to Robert.
- Digital Office DB-backed project/task/work recording.
- KOVAL VPN / Bitdefender takeover follow-up.
- Communications Manager task reassignment and newsletter workflows.
- Earth Day newsletter distributor/account workflow.
- OpenWrt and LuCI update task.
- Email archive transfer follow-up.
- Backlog items including outreach events module, Trainual video workflow, PHP list cleanup, distributor cleanup, BID/importer work, IT planning docs, SSO persistence, unified activity reporting, usage cadences, Postmaster monitoring, and Google Cloud security hardening.

## Source-Of-Truth Decision

Use a layered source-of-truth model instead of immediately moving every existing task system into one writable database.

1. `project_hub` is the canonical human-readable source of truth for cross-workspace projects, decisions, approval gates, migration plans, and implementation ownership.
2. Workspace-local `TODO.md` files remain the canonical short action queues for humans and Codex workers until a DB-backed system is proven and approved.
3. OPS/Portal tasks remain the canonical operational/business task records where staff assignment, due dates, notifications, and CRM-side audit behavior already matter.
4. Workspaceboard remains the canonical live session/work-execution surface for Codex workers, session status, and transcript history.
5. Papers should initially be a durable document/work-record surface and index target, not an unapproved replacement for OPS/Portal or local TODO files.
6. A generated read-only index should bridge the above records before any writable project/task database is introduced.

Rationale: current systems already have business ownership boundaries and approval gates. A direct DB migration would risk notification side effects, broken staff workflows, duplicate task state, and accidental production/schema changes. The safe first step is to standardize objects and indexes around existing records, then make one small implementation surface prove the model.

## Object Model

### Core Tables / Documents

`digital_workspaces`

- `id`: stable slug, for example `ai`, `ops`, `portal`, `workspaceboard`, `papers`
- `name`
- `kind`: `repo`, `workspace`, `service`, `host`, `mailbox`, `paper_space`
- `canonical_uri`
- `owner_actor_id`
- `status`

`digital_actors`

- `id`: stable slug or external actor ref
- `name`
- `kind`: `human`, `codex_role`, `claude_role`, `mailbox_worker`, `service_account`
- `external_refs`: OPS user id, board role id, email alias, or service account ref
- `status`

`digital_projects`

- `id`: stable project id, preferably matching project-hub Master ID for cross-workspace initiatives
- `title`
- `summary`
- `status`: `proposed`, `open`, `blocked`, `review`, `completed`, `superseded`
- `lead_workspace_id`
- `owner_actor_id`
- `approval_state`: `none`, `needed`, `granted`, `rejected`, `expired`
- `security_scope`: `normal`, `sensitive`, `secret_adjacent`, `production`, `destructive`
- `created_at`, `updated_at`, `completed_at`

`digital_work_items`

- `id`: stable item id, with `ops:<id>`, `todo:<workspace>:<slug>`, `board:<session>`, or `paper:<id>` external aliases
- `project_id`
- `title`
- `summary`
- `status`: `backlog`, `ready`, `in_progress`, `blocked`, `needs_input`, `review_ready`, `done`, `superseded`
- `workspace_id`
- `owner_actor_id`
- `source_system`: `todo`, `ops`, `workspaceboard`, `papers`, `project_hub`, `email`
- `source_uri`
- `priority`
- `due_at`
- `current_next_action`
- `approval_state`
- `created_at`, `updated_at`, `completed_at`

`digital_work_events`

- `id`
- `project_id`
- `work_item_id`
- `actor_id`
- `event_type`: `note`, `status_change`, `command`, `observation`, `blocker`, `handoff`, `artifact_created`, `approval_requested`, `approval_granted`, `approval_rejected`, `check_passed`, `check_failed`
- `body`
- `redaction_level`: `public_internal`, `private_internal`, `secret_redacted`
- `created_at`

`digital_artifacts`

- `id`
- `project_id`
- `work_item_id`
- `kind`: `markdown`, `paper`, `trace`, `decision`, `handoff`, `commit`, `patch`, `url`, `database_record`, `report`, `email_metadata`
- `uri`
- `content_hash`
- `workspace_id`
- `created_at`, `updated_at`

`digital_source_refs`

- `id`
- `kind`: `file`, `url`, `host_path`, `command`, `table`, `api_endpoint`, `ops_task`, `email_metadata`, `paper`
- `uri`
- `description`
- `redaction_level`

`digital_relationships`

- `from_type`, `from_id`
- `to_type`, `to_id`
- `type`: `blocks`, `depends_on`, `supersedes`, `implements`, `documents`, `generated`, `references`, `handoff_to`, `validated_by`, `mirrors`, `indexed_from`
- `source_ref_id`
- `created_at`

### Required Invariants

- Work events are append-only.
- Destructive or production-sensitive work must have an approval event before execution events.
- Secret material is never stored in work events, source refs, Papers, TODO, project-hub, or chat.
- External IDs are aliases, not replacements. OPS task IDs, Workspaceboard session IDs, Papers IDs, file paths, and commits must remain traceable.
- Generated indexes may be rebuilt from canonical sources; canonical records must not depend on generated index state.

## Where Records Live

Phase 0, current state:

- `project_hub/issues/*.md`: canonical project proposals, decisions, approval gates, migration notes.
- `TODO.md` / workspace `TODO.md`: canonical short action queue.
- OPS/Portal DB: canonical staff/business task records.
- Workspaceboard DB/runtime/history: canonical live execution/session state.
- Papers: candidate document/work-record surface; do not mutate until approved.

Phase 1, first safe implementation:

- Add a docs-only JSON Schema or SQLite DDL draft under `ai_workspace/project_hub/digital-office/`.
- Build a read-only local indexer in a git-backed implementation repo, not in production DBs. The indexer should ingest `project_hub`, AI Workspace `TODO.md`, and Workspaceboard exported/session metadata first.
- Store generated local prototype data under a machine-local or explicitly ignored path until Robert approves a durable location.

Phase 2, approved prototype:

- Choose a single owning service for write API experiments. Recommended first owner: `/Users/werkstatt/workspaceboard`, because it already owns live Codex session state and dashboard rollups.
- Keep writes local/prototype-only. Do not write to OPS/Portal, Papers, `.205`, or production databases.
- Expose a read-only project/task/work-record dashboard and export.

Phase 3, later integration:

- Add Papers as a durable document projection after read-only Papers schema/API inspection is approved.
- Add OPS/Portal links as external aliases and read-only task metadata first.
- Add write-back only after notification behavior, audit side effects, permissions, and ownership rules are explicitly approved.

## Interoperation Rules

### Papers

- First role: durable document projection and work-record reader.
- Do not treat Papers as task source of truth until its schema/API/storage model is inspected and approved.
- Do not write to Papers or `.205` from this initiative without a separate approval gate.

### Workspaceboard

- First implementation workspace for a prototype because it already models sessions, roles, status, summaries, and history.
- Should display project grouping and work-record rollups from a read-only index before it owns writable project/task records.
- Must preserve Task Manager/Summary Worker separation and session traceability.

### OPS/Portal

- Continue to own staff-visible operational tasks, assignments, due dates, notification behavior, and CRM audit side effects.
- Digital Office should link to OPS tasks by `ops:<task_id>` and ingest non-secret task metadata only after the existing Codex auth/notification repairs are stable.
- No OPS/Portal schema changes in the first slice.

### TODO Files

- Continue as local action queues.
- Add optional structured front matter only after a parser/indexer proves it can preserve current human workflow.
- Do not turn TODO into an audit log; detailed work records belong in project-hub, Papers, Workspaceboard history, or the future event store.

### Project Hub

- Project hub remains the source of truth for cross-workspace project identity and approval state.
- Each major initiative should have one Master ID and link all tasks, board sessions, papers, commits, and checks from there.

## Migration Approach

1. Inventory current project-hub Master IDs, open TODO items, and visible Workspaceboard sessions into a generated read-only index.
2. Assign stable project IDs for open cross-workspace initiatives without changing existing files beyond explicit links.
3. Map local TODO bullets to `digital_work_items` using deterministic slugs; do not delete or rewrite TODO entries during indexing.
4. Map OPS tasks only as external aliases after a read-only metadata path is approved and notification side effects are understood.
5. Map Workspaceboard sessions to work items by workspace, title, and session ID; keep transcript as source evidence, not duplicated full content.
6. Add Papers links only after approved read-only structure inspection confirms safe IDs and storage semantics.
7. Run the index in dry-run/report mode until Robert approves a writable prototype.

## Approval Gates

Separate approval is required before:

- Reading or writing `.205`, `/srv`, Papers internals, Papers authenticated UI, Papers API, or Papers database/storage.
- Mutating Papers records.
- Mutating OPS/Portal schema or production database records.
- Creating/updating OPS tasks from this project except through approved silent Codex task paths.
- Sending notifications or emails.
- Starting background sync daemons.
- Exposing MCP endpoints or connecting external agents to internal records.
- Storing credential material or private email body content in any project/task/work record.

## First Safe Implementation Slice

Recommended route:

1. Workspace: `ws workspaceboard`.
2. Role: Code and Git Manager first, then a Workspaceboard implementation worker.
3. Work scope:
   - Add a read-only `digital-office` prototype module or script that parses AI Workspace `project_hub/INDEX.md`, selected project detail logs, `TODO.md`, and Workspaceboard session metadata.
   - Produce a generated local JSON index with `projects`, `work_items`, `events`, `artifacts`, and `relationships`.
   - Add a read-only dashboard/endpoint that shows grouped TODOs/tasks by project without creating or updating any external system.
4. Explicit non-scope:
   - No Papers writes.
   - No `.205` access.
   - No OPS/Portal schema or production DB writes.
   - No notification/email side effects.
   - No background daemon.
5. Verification:
   - Unit/parser checks for Markdown input.
   - Dry-run fixture output review.
   - Workspaceboard local status check.
   - Confirm no secret-bearing files are read.

## Agents / Skills That Accelerate The Plan

- Project Manager: own the source-of-truth model, migration phases, and approval gates in `ai_workspace`.
- Code and Git Manager: coordinate Workspaceboard repo state, active sessions, pull-before-work, and commit readiness.
- Security Guard: review Papers, `.205`, MCP exposure, OPS/Portal DB, credentials, and secret-adjacent gates before any integration.
- Workspaceboard worker: implement the first read-only index/dashboard slice.
- OPS worker: later read-only OPS task metadata mapping after Codex auth/notification fixes are stable.
- AI-Bridge worker: later Papers/Claude bridge trace mapping and read-only Papers investigation after approval.

## Decision Needed

Approve the first implementation worker route:

`ws workspaceboard` -> Code and Git Manager preflight -> Workspaceboard implementation worker for a read-only Digital Office project/task/work-record index and dashboard prototype.

Do not approve Papers, `.205`, OPS/Portal schema, production DB, notification, or MCP write work as part of this first slice.

## Non-Actions

- Did not mutate Papers.
- Did not access `.205`.
- Did not read or print secrets.
- Did not mutate OPS/Portal schema or production databases.
- Did not create or complete OPS tasks.
- Did not start services, daemons, or background sync.
