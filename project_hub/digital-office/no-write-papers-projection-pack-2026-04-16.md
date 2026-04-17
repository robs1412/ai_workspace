# Digital Office No-Write Papers Projection Pack

- Date: 2026-04-16
- Workspace: `ai_workspace`
- Master ID: `AI-INC-20260414-DIGITAL-OFFICE-WORK-RECORDS-01`
- Status: local planning/projection pack prepared
- Scope: local-only, no-write planning artifacts

## Task Manager Approval

Task Manager approved the safe local-only/no-write next slice on 2026-04-16.

Approved scope:

- Produce a local planning/projection pack for how project-hub, TODO, and Workspaceboard metadata can project into future Papers work records.
- Use existing local non-secret planning sources only.
- Keep the result reviewable as Markdown and JSON examples.
- Clearly mark any remaining human decision about Google Drive OAuth storage versus machine-local storage.

Closed gates for this slice:

- No live Papers writes.
- No `.205` or `.17` writes.
- No OPS/Portal database changes.
- No credential reads, printing, copying, or storage.
- No MCP exposure changes.
- No notifications or email sends.
- No Frank or Avignon runtime changes.
- No service restarts, background daemons, deploys, or live runtime mutation.

## Pack Contents

- `projection-schema-v0.json`: draft local schema for a generated projection export.
- `sample-projection-export-v0.json`: sample no-write export using current Digital Office sources.
- `papers-work-record-template.md`: Markdown template for a future Papers work record.
- `security-review-checklist.md`: Security Guard review checklist before any implementation or live writer.
- `storage-decision-needed.md`: explicit remaining human decision about OAuth/token storage.

## Source Inputs

Local sources used for this pack:

- `ai_workspace/ai-digital-office.md`
- `ai_workspace/TODO.md`
- `ai_workspace/HANDOFF.md`
- `ai_workspace/project_hub/INDEX.md`
- `ai_workspace/project_hub/issues/2026-04-14-digital-office-project-task-work-records-proposal.md`
- `/Users/werkstatt/workspaceboard/server/digital-office-index.js`

Sources intentionally not used:

- Papers authenticated UI or API.
- `.205` or `.17` remote files.
- OPS/Portal production database.
- Frank/Avignon runtime state.
- Credential, `.env`, OAuth, keychain, mailbox, or secret-bearing files.

## Projection Model

The projection pack treats existing systems as canonical sources and emits a rebuildable local export:

- `project_hub` owns cross-workspace project identity, approval state, and decisions.
- `TODO.md` owns short action queues and only projects active or recently completed summary items.
- Workspaceboard owns live execution/session metadata; transcripts stay in Workspaceboard unless explicitly summarized.
- Papers remains a future document/work-record projection target, not the source of truth.
- OPS/Portal remains the staff/business task source of truth and is linked only by non-secret aliases after separate approval.

The export should be disposable. If it is deleted, it must be rebuildable from the source files and Workspaceboard session metadata.

## Stable ID Rules

Use the strongest canonical source as the primary stable ID:

- Project-hub Master ID for cross-workspace initiatives.
- Workspace TODO slug for local action items.
- Workspaceboard session ID for live execution/session events.
- OPS task ID only after approved read-only OPS metadata intake.
- Papers ID only after approved Papers read/write behavior exists.

Titles are never identifiers by themselves.

## Duplicate Protection

Before any future live writer is proposed, the dry-run projection must check:

- `record_id`
- every `stable_alias`
- source reference tuple: source system, URI, title, and date
- normalized content hash

Dry-run decisions are limited to `create`, `update_candidate`, `skip_duplicate`, or `blocked_gate`. No writer may execute those decisions until live write approval exists.

## Redaction Rules

Default redaction level is `private_internal`.

Always exclude:

- credentials, tokens, OAuth refresh/access tokens, app passwords, private keys, `.env` values
- private mailbox body text
- raw command logs that might contain secrets
- database URLs or environment dumps
- unapproved `.205` inspection content
- customer/staff-sensitive OPS/Portal details beyond approved aliases

## Export/Review Flow

1. Generate or refresh a local export from safe local sources.
2. Validate schema and duplicate decisions.
3. Review the Security Guard checklist.
4. Review the storage decision note.
5. Only after separate explicit approval, route implementation to the owning repo or worker.

## Recommendation

Keep this as a local, rebuildable, no-write projection until Robert decides the storage question and approves a specific implementation surface.

Recommended next implementation owner, if approved later: `workspaceboard`, because it already has a read-only Digital Office index surface and local session metadata. That later implementation should still avoid Papers writes, `.205` writes, OPS/Portal writes, notifications, MCP exposure changes, and Frank/Avignon runtime changes unless separately approved.

## Remaining Human Decision

Robert needs to choose the storage rule for Google Drive OAuth/token material before any future Google Drive-backed ingestion/export automation is built:

- Option A, recommended: OAuth credentials and token cache stay machine-local, outside Google Drive and outside git.
- Option B: use a Google-managed service account or delegated app flow with approved secret storage, but still keep private keys/tokens out of Google Drive-synced planning files.
- Option C, not recommended without stronger controls: store OAuth material in Google Drive-synced paths.

Until Robert decides, the projection pack must not include Google Drive OAuth automation or any token storage path.
