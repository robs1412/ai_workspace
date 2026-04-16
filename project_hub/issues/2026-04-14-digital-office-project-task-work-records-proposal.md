# Digital Office Project/Task/Work Record Source-of-Truth Proposal

- Last Updated: 2026-04-16 17:05:00 CDT (Machine: Macmini.lan)
- Date: 2026-04-14
- Workspace: `ai_workspace`
- Master ID: `AI-INC-20260414-DIGITAL-OFFICE-WORK-RECORDS-01`
- Status: local no-write projection pack prepared; live writer and OAuth/token storage decisions still gated
- Scope: docs-only planning and object-model/projection design

## Task

Group TODOs/tasks into projects and define DB-backed project/task/work recording for the KOVAL Digital Office model, without mutating Papers, `.205`, production databases, OPS/Portal schema, secrets, or runtime services.

## 2026-04-16 Local No-Write Projection Pack

Task Manager approved the safe local-only/no-write next slice. The local projection pack was prepared under `project_hub/digital-office/`:

- `no-write-papers-projection-pack-2026-04-16.md`
- `projection-schema-v0.json`
- `sample-projection-export-v0.json`
- `papers-work-record-template.md`
- `security-review-checklist.md`
- `storage-decision-needed.md`

This pack is planning/projection material only. It does not write to Papers, `.205`, `.17`, OPS/Portal databases, credentials, MCP exposure, notifications/email, Frank/Avignon runtime, services, deploy targets, or live runtime state.

Remaining human decision: choose Google Drive OAuth/token storage policy before any future Drive-backed projection automation. Current recommendation is machine-local or approved secret manager/keychain storage, not Google Drive-synced planning files or git.

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

## 2026-04-16 Papers Projection Design

This section defines how Markdown, Workspaceboard, OPS/Portal, and Papers should relate before any live Papers write path is enabled.

### System Responsibilities

- Markdown remains the authoring and audit layer for planning, decisions, handoffs, approval gates, and human-reviewable work logs. `project_hub` owns cross-workspace identity; workspace `TODO.md` files own short action queues; `HANDOFF.md` owns current-session continuity.
- Workspaceboard remains the live execution layer for Codex sessions, Task Manager routing, Decision Driver prompts, Summary Worker summaries, worker status, and implementation transcript history.
- OPS/Portal remains the staff/business operations layer for assigned work, due dates, staff-visible audit behavior, notifications, CRM/task ownership, and production workflows.
- Papers should be a durable document projection for completed work records, decisions, analysis, approvals, code/deploy summaries, and email-derived task outcomes. It should not become the canonical staff task queue or replace OPS/Portal until its API, auth, notification, and audit behavior are explicitly approved.

### Automatic Papers Record Events

When live writes are later approved, Papers records may be created automatically only for non-secret, non-sensitive, completed or decision-grade events:

- Completed project-hub work item or incident closeout.
- Approved architecture or operating decision that changes workflow, source-of-truth, auth boundaries, or agent role behavior.
- Completed analysis memo that should be discoverable outside one local repo.
- Approval record for a gated action, when the approval text is non-secret and safe to store.
- Code/deploy summary after commit, push, deploy, rollback, or verification is complete, excluding credentials, raw logs with secrets, and private runtime details.
- Email-derived task completion summary after Frank/Avignon has safely handled or routed the task, excluding private email body text unless separately approved.

Do not auto-create Papers records for raw command logs, full transcripts, private email bodies, `.env`/credential material, unapproved `.205` inspection output, draft-only analysis, blocked tasks with sensitive details, or OPS/Portal records that could trigger notifications or expose staff/customer data.

### Record Schema And Template

Recommended canonical fields for a projected Papers work record:

```yaml
record_id: papers-projection:<stable-id>
record_type: completed_work | decision | analysis | approval | code_deploy_summary | email_task
title:
status: proposed | approved | completed | superseded | blocked
source_system: project_hub | todo | workspaceboard | ops | portal | frank | avignon | ai_bridge
source_refs:
  - kind: file | board_session | ops_task | commit | url | email_metadata | project_id
    uri:
    title:
stable_aliases:
  - project:<master-id>
  - todo:<workspace>:<slug>
  - board:<session-id>
  - ops:<task-id>
owner_actor:
workspace:
created_at:
completed_at:
approval_state: none | needed | granted | rejected | expired
security_scope: normal | private_internal | secret_adjacent | production | destructive
redaction_level: public_internal | private_internal | secret_redacted
summary:
decision:
actions_taken:
verification:
rollback_or_recovery:
next_action:
human_decision_needed:
```

Template body:

```markdown
# {{title}}

- Record ID: `{{record_id}}`
- Type: `{{record_type}}`
- Source: `{{source_system}}`
- Owner: `{{owner_actor}}`
- Workspace: `{{workspace}}`
- Status: `{{status}}`
- Security Scope: `{{security_scope}}`
- Approval State: `{{approval_state}}`

## Summary

## Decision / Outcome

## Actions Taken

## Verification

## Source References

## Rollback / Recovery / Export

## Next Action
```

### Duplicate Protection And Stable IDs

- Use a deterministic projection ID from the strongest canonical source: project-hub Master ID, OPS task ID, Workspaceboard session ID, commit SHA, email task ID, or a normalized workspace TODO slug.
- Use aliases instead of overwriting source identity. A Papers record may carry `project:<master-id>`, `ops:<id>`, `board:<session>`, `commit:<sha>`, and `email-task:<id>` together.
- Before writing, check by `record_id`, all stable aliases, and a content hash of normalized title/source refs/date. If any match exists, update only through an approved append/update path or skip with a duplicate note.
- Do not use human-friendly titles alone as IDs because task names change and duplicate project names recur.
- Keep a local projection manifest/export so duplicate checks can be replayed after restore or migration.

### Permission, Auth, And Approval Model

- Default write authority is disabled. Papers writes require a Robert-approved implementation slice, an approved service identity, and a documented API-only mutation path.
- Security Guard must review any live Papers write path because it touches `.205`, auth/access, MCP-adjacent exposure, and internal durable records.
- Writes must use Papers API/tools, not direct file edits under Papers storage. Existing `.205` notes say API writes preserve author/timestamp tracking.
- Initial writer should be a narrow service identity or Workspaceboard-controlled local tool with least privilege to create/update the approved record type only.
- Human approval is required before enabling writes for private email-derived records, OPS/Portal-linked records, production/deploy records, auth/security decisions, or any external/MCP exposure.
- No credentials, tokens, `.env` values, private keys, private mailbox bodies, or raw secret-adjacent logs may be stored in Papers, Markdown, generated indexes, or chat.

### Write Path Options

1. `project_hub` to generated manifest to manual Papers import.
   - Lowest risk; no live API write; useful for schema validation and review.
2. Workspaceboard read-only dashboard to exported JSON/Markdown projection.
   - Recommended first implementation slice; validates source parsing, stable IDs, and duplicate checks without touching Papers.
3. Workspaceboard controlled API writer to Papers.
   - Candidate first live writer only after options 1 and 2 are accepted, Security Guard signs off, and API auth/write behavior is verified in a safe target.
4. OPS/Portal event projection to Papers.
   - Later phase; requires explicit review of notification side effects, permissions, staff/customer data exposure, and operational ownership.
5. Frank/Avignon email task projection to Papers.
   - Later phase; requires stricter redaction and private-body exclusion rules, plus duplicate protection from email task IDs/message metadata.

Safest first slice completed: a local no-write projection pack now lives under `project_hub/digital-office/` and outputs reviewable JSON and Markdown examples from `project_hub`, `TODO.md`, and Workspaceboard metadata, with stable ID rules, duplicate expectations, templates, export notes, and a Security Guard checklist. No `.205`, no Papers auth, no OPS/Portal DB, no notifications, no MCP exposure.

### Rollback, Recovery, And Export

- Generated projections must be rebuildable from canonical Markdown, Workspaceboard metadata, OPS/Portal aliases, commits, and email task metadata.
- Before any future live write batch, export the target Papers records or record IDs that may be touched, plus the local projection manifest and content hashes.
- Use append/update rather than destructive overwrite where possible. If a record is wrong, supersede it with a correction record unless the Papers API provides an audited update path approved for this use.
- Keep a dry-run diff mode showing create/update/skip decisions before every batch.
- Recovery path for bad writes: disable writer, export affected record IDs, create correction/supersession records or restore from Papers backup using approved Papers tools, then record the incident in `project_hub`.

### Task Manager And Decision Driver Behavior

Task Manager may independently:

- Route no-write projection planning to `ws ai` or `ws workspaceboard`.
- Keep TODO/project-hub/handoff state aligned.
- Ask Security Guard for a non-secret review of auth/write boundaries.
- Start a read-only worker after confirming scope excludes live Papers, `.205`, production DB writes, notifications, MCP exposure, commit/push/deploy, and credential printing.

Task Manager must escalate before:

- Any live Papers write, `.205` access, Papers authenticated UI/API use, OPS/Portal DB write, schema change, notification/email, MCP exposure change, deploy, commit, push, or production-impacting action.

Decision Driver may independently:

- Frame the next human decision as a concrete yes/no approval question.
- Push a worker forward on no-write schema/template/export planning if the task remains inside approved docs/prototype scope.

Decision Driver must escalate before:

- Choosing a live source of truth, enabling API credentials, approving automatic record creation categories, relaxing redaction rules, or allowing any writer that could change Papers, OPS/Portal, `.205`, or production systems.

### Existing Content Migration / Projection

- `project_hub/INDEX.md` projects to `digital_projects` and top-level Papers decision/completed-work records using Master IDs as stable IDs.
- `project_hub/issues/*.md` projects to detailed `analysis`, `decision`, `approval`, and `completed_work` records when the issue reaches a decision or closeout state.
- `TODO.md` projects only open action items and concise done entries; it remains an action queue and must not be expanded into a transcript.
- `HANDOFF.md` projects only current operational state and cross-machine/session continuity notes, not every historical line.
- Workspaceboard sessions project as execution events and source refs. Full transcripts stay in board/session history unless a sanitized summary is explicitly selected.
- OPS/Portal tasks project as aliases and non-secret metadata only after approved read-only intake. They remain canonical for staff-visible tasks.
- Frank/Avignon email-derived tasks project only sanitized task IDs, subjects when safe, owner, action taken, and completion state. Private email bodies stay out unless explicitly approved.

### Security Guard Coordination

Security Guard classification for the current design: safe to continue for local docs and no-write projection planning; human approval required for live Papers writes, `.205` access, API credential use, MCP exposure, OPS/Portal writes, production DB writes, or private email content projection.

Required boundaries for the next slice:

- No live Papers writes.
- No `.205` access or writes.
- No production DB writes.
- No credential printing or storage.
- No MCP exposure changes.
- No notifications/emails.
- No commit/push/deploy unless separately approved.

Security Guard should review the final no-write projection manifest before any live writer is built, specifically checking redaction, stable IDs, duplicate protection, export/rollback, least-privilege writer identity, and approval gates.

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

Resolve the current storage decision before any Drive-backed automation:

Choose Google Drive OAuth/token storage policy for future projection tooling. Current recommendation: machine-local storage or an approved secret manager/keychain path, not Google Drive-synced planning files or git.

The completed local pack remains docs-only and no-write; do not touch Papers or `.205`.

Exact decision needed before live Papers writes are enabled: approve which write authority, target Papers space, record types, redaction level, duplicate/update behavior, and rollback/export procedure should be used for a first live API-only Papers write test. Until that decision is explicit, live Papers writes remain disabled.

## Non-Actions

- Did not mutate Papers.
- Did not access `.205`.
- Did not read or print secrets.
- Did not mutate OPS/Portal schema or production databases.
- Did not create or complete OPS tasks.
- Did not start services, daemons, or background sync.
- Did not send notifications or emails.
- Did not change MCP exposure.
- Did not commit, push, deploy, or restart services.
