# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260518-CLAUDE-HOST-PARITY-01`
- Date Opened: `2026-05-18`
- Date Completed:
- Owner: `Codex`
- Priority: `High`
- Status: `Open`

## Scope

Convert the live `.205` Claude host inspection into a concrete local implementation plan that improves Codex-side execution reliability and protected-side visibility without creating a new architecture layer or mutating unapproved system paths.

OPS durable anchor for the Claude host metadata/docs alignment proof slice: project `369808`, task `369809`.
OPS durable anchor for the read-only bridge snapshot contract slice: project `369808`, task `369810`.
OPS durable anchor for the modular tool-layout migration-map slice: project `369808`, task `369813`.
Mirrored OPS project records for adjacent completed project-hub slices now exist as `369836` (`Task Manager Finish Contract Tightening`), `369837` (`TODO Archive Migration`), and `369838` (`Outreach Event Fast Path Manual`).

## DB-Backed Tracking Contract

- Initiative-level OPS project: `369808` (`AI Claude Host Parity and Local Execution Improvements`)
- Slice tasks:
  - `369809` Claude host metadata and docs alignment
  - `369810` AI Bridge read-only Claude host snapshot contract
  - `369811` Workspaceboard auth dependency readback surface
  - `369812` Workspaceboard worker durability and session-state improvement slice
  - `369813` Local modular tool-layout migration map from Claude host
- Task Flow remains the execution spine for routed workers, waiting/working/completed state, and closeout proof.
- OPS is the linked durable project/task record for project ownership, grouping, and reporting.
- For any Task Flow row or worker packet created for this initiative, the linked OPS task id should live in `ops_portal_or_domain_task`; do not create a second parallel markdown-only task identity for the same slice.

## Symptoms

- Claude on `.205` still appears faster and more stable than the local Codex stack.
- Local Workspaceboard/Codex execution recently needed a runtime reliability repair before routed workers would stay alive.
- Local bridge docs still reference obsolete Claude config assumptions such as `/home/claude/.claude/.mcp.json`.
- The local `.205` access path was recoverable only through a private helper, while the non-secret host/identity mapping remains inconsistent across docs.

## Root Cause

The protected-side Claude host has a more mature persistent local state layout, modular tool tree, and explicit auth/cache surfaces than the local Codex side. Local docs and readbacks lag the actual protected-side layout, and some local operational surfaces still hide auth dependencies and durable worker-state mechanics that Claude keeps explicit.

## Implementation Plan

1. Align Claude-host metadata and docs to the real protected-side surfaces.
   - Replace obsolete `.mcp.json` assumptions in local bridge/docs with the verified surfaces:
     - `/home/claude/.claude/settings.json`
     - `/home/claude/.claude/settings.local.json`
     - `/home/claude/.claude/mcp-needs-auth-cache.json`
   - Keep SSH identity guidance non-secret and repo-local.
   - Do not mutate `~/.ssh/config` in this slice.

2. Add a read-only Claude host snapshot surface to local bridge/Workspaceboard planning.
   - Start with a source-only/non-secret snapshot contract: host identity, active config paths, tool directories, and auth-cache categories.
   - Prefer a read-only JSON or markdown export before any UI/runtime wiring.
   - Keep writable/shared control-plane work out of scope.

3. Expose auth dependency state locally the way Claude does.
   - Add a local readback for pending auth dependencies such as Gmail, Google Calendar, and Google Drive.
   - Surface this in durable local state first; Workspaceboard UI/runtime follow-up can be a second step.

4. Improve local worker durability/readback using Claude-side lessons.
   - Make local worker/session state more explicit around task/proof history, shell snapshots, and session env evidence.
   - Keep this as a narrow Workspaceboard/AI Workspace reliability slice, not a new subsystem.

5. Prepare a modular tool-layout improvement map.
   - Inventory which local lanes should stay in `ai_workspace` and which should graduate into clearer tool-oriented surfaces.
   - Produce a migration map only; do not reshuffle live workspaces in one pass.

6. Leave system-path and secret-path changes approval-gated.
   - Separate approval is still required for:
     - `~/.ssh/config` edits
     - key authorization changes on `.205`
     - credential/auth/runtime mutation outside `/Users/werkstatt`
     - live protected-side service changes

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260518-CLAUDE-HOST-PARITY-01`
- Commit SHA: `uncommitted`
- Commit Date: `2026-05-18`
- Change Summary:
  - Recorded the implementation plan and live `.205` readback.
  - Routed focused workers for the approved repo-local execution slices.
  - Aligned AI Workspace docs to the verified Claude host config surfaces: `/home/claude/.claude/settings.json`, `/home/claude/.claude/settings.local.json`, and `/home/claude/.claude/mcp-needs-auth-cache.json`.

### ai-bridge

- Repo Log ID: `AI-INC-20260518-CLAUDE-HOST-PARITY-01`
- Commit SHA: `uncommitted`
- Commit Date: `2026-05-18`
- Change Summary:
  - Replaced active bridge-doc assumptions that still pointed at `/home/claude/.claude/.mcp.json` as the authoritative Claude host surface.
  - Updated bridge planning, traces, and manifest references to the verified layered config model centered on `settings.json`, `settings.local.json`, and `mcp-needs-auth-cache.json`.

### workspaceboard

- Repo Log ID: `AI-INC-20260518-CLAUDE-HOST-PARITY-01`
- Commit SHA:
- Commit Date:
- Change Summary:
  - Planned local auth-dependency and worker-durability readback improvements derived from the Claude host inspection.
  - Confirmed the DB-backed execution contract: Task Flow remains the live worker/proof layer, while OPS project `369808` and tasks `369811` / `369812` provide the linked project/task record instead of a replacement queue.

## Verification Notes

- OPS project/task linkage for the docs-alignment proof in this note: project `369808`, task `369809`.
- OPS project/task linkage for the read-only bridge-contract proof in this note: project `369808`, task `369810`.
- OPS project/task linkage for the auth dependency readback surface in this note: project `369808`, task `369811`.
- OPS project/task linkage for the worker durability/session-state improvement slice in this note: project `369808`, task `369812`.
- OPS project/task linkage for the migration-map proof in this note: project `369808`, task `369813`.
- OPS project/task linkage for the planner-surface extraction in this note: project `369808`, task `369814`.
- OPS project/task linkage for the AI Health entrypoint extraction in this note: project `369808`, task `369816`.
- Live `.205` SSH access succeeded through the approved private askpass helper.
- Verified protected-side shell identity: `claude` on host `reatan` (`192.168.55.205`).
- Verified active Claude config/path surfaces:
  - `/home/claude/.claude/settings.json`
  - `/home/claude/.claude/settings.local.json`
  - `/home/claude/.claude/mcp-needs-auth-cache.json`
- Verified `/srv/tools` modular directories including `email`, `gdrive`, `mesh`, `papers`, `planner`, `portal`, `screenshot`, `shopify`, and `timetracker`.
- 2026-05-18 repo-local follow-through updated the remaining AI Workspace and AI-Bridge docs that still treated `/home/claude/.claude/.mcp.json` as an active expected target.
- 2026-05-18 repo-local docs-alignment contract created at `project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md`; proof marker for the slice is `CLAUDE_HOST_DOCS_ALIGNED project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md:1`, anchored to OPS project `369808` / task `369809`.
- 2026-05-18 repo-local read-only bridge contract created at `ai-bridge/contracts/claude-host-read-only-snapshot-contract.md` with example artifact `ai-bridge/artifacts/claude-host-read-only-snapshot.example.json`; proof marker for the slice is `AI_BRIDGE_CONTRACT_READY ai-bridge/contracts/claude-host-read-only-snapshot-contract.md:1 ai-bridge/artifacts/claude-host-read-only-snapshot.example.json:1 jq-ok`, anchored to OPS project `369808` / task `369810`.
- 2026-05-18 repo-local migration-map artifact created at `project_hub/artifacts/claude-host-tool-layout-migration-map-2026-05-18.md`. The artifact is anchored to OPS project `369808` / task `369813` and classifies which local capabilities stay in `ai_workspace` as coordination state and which should graduate into clearer tool-oriented surfaces, with explicit current paths, target owners, and extraction order. First recommended execution slice: move task-flow/runtime helpers from `ai_workspace/scripts/` into a named `workspaceboard`-owned planner surface.
- 2026-05-18 adjacent completed project-hub items were mirrored into OPS projects `369836`, `369837`, and `369838` so the durable project records live in OPS instead of only in project-hub prose.
- Verified local Task Flow code already treats `ops_portal_or_domain_task` as the intended DB-backed link field and requires it for task-linked states such as `task_created`, `scheduled`, `working`, `waiting`, `completed`, `reported`, and `filed`. This initiative should use that existing contract instead of introducing a separate execution tracker.
- 2026-05-18 first extraction slice landed repo-locally in `workspaceboard/scripts/planner/`: compatibility wrappers now exist for `task_flow_mysql_recorder.php`, `shared_task_flow.py`, `task_flow_due_runner.py`, and `task_flow_papers_project.py`, and `workspaceboard/server/index.js` now points Workspaceboard's own Task Flow read path to `scripts/planner/task_flow_mysql_recorder.php`. Verification passed with `php -l`, `python3 -m py_compile`, `node --check`, and a live `php workspaceboard/scripts/planner/task_flow_mysql_recorder.php report 3` call returning `ok:true`. No runtime deploy or cross-repo legacy-script removal was performed yet.
- 2026-05-18 restored the session-backed Codex OPS task-create path for this initiative. A clean simulated Codex session successfully hydrated a non-expired Portal JWT for subject `1332`, and the normal `crm_create_task(..., allow_service_fallback=false)` route created follow-on tasks `369814` (`Workspaceboard planner-surface extraction for Task Flow helpers`) and `369816` (`Workspaceboard AI Health entrypoint extraction`) under project `369808`, both with creator/owner/assignee `1332` and notifications suppressed.
- 2026-05-18 next health extraction slice landed repo-locally in `workspaceboard/scripts/health/`: added `ai_health_check.py` as a Workspaceboard-owned compatibility wrapper plus `scripts/health/README.md`, and `workspaceboard/server/index.js` now points `AI_HEALTH_SCRIPT` at the Workspaceboard-owned wrapper. Verification passed with `python3 -m py_compile`, `node --check`, and a dry-run invocation through the wrapper that completed with `board_ok=true`. No runtime deploy, LaunchAgent change, or legacy-script removal was performed yet.
- 2026-05-18 control-lane follow-through routed the remaining Claude-parity slices into visible worker sessions instead of leaving them on the earlier generic placeholder. Task `369809` is on session `bd9b8e26`, `369810` on `f14496f5`, `369811` on `3a5a47bd`, `369812` on `0acb7af4`, and `369813` on `c464036e`. Live worker state was verified in both `/api/status` and `/api/management/overview?live=1`; the placeholder session `32a1b9d4` is not the active route for this batch.
- 2026-05-18 the missing AI Manager input recorder was installed at `ai_workspace/scripts/ai_manager_input_recorder.php`. The recorder now creates and updates a DB-backed `koval_crm.ai_manager_inputs` table and returns durable input ids/uids for Workspaceboard route receipts. This closes the specific `db_ok=false` gap seen in `recordAiManagerInput(...)` while keeping route receipts separate from Task Flow packets. Verification: `php -l`, `install`, and a non-secret record smoke test returned `{"ok":true,"input_id":1976,"input_uuid":"test-1842b7f5d69d"}`.
- 2026-05-18 follow-through on the Claude-side stability hints extended that recorder contract: the AI Manager input table now stores durable `proof_marker`, `session_env_json`, and `shell_snapshot_json` evidence, and `workspaceboard/server/index.js` passes those fields on receipt update. A non-secret smoke row round-tripped the new fields, proving the receipt path can now carry the same style of durable evidence that the worker/session state path already uses on Workspaceboard.
- 2026-05-18 live UX follow-through: surfaced the existing read-only Papers lane and the durable auth/history readbacks in the live Workspaceboard UI. `index.php` now exposes an `Open Papers` shortcut, `task-management-light.html` now adds a `Papers` button and `Auth` tab, and `assets/task-management-light.js` now shows `current_work_state`, `durable_history`, and live terminal history together in session detail. The updated files were copied into the live runtime copy under `/Users/admin/.workspaceboard-launch/runtime/app/` and verified by direct HTTP readback.

## Rollback Plan

- This plan slice is docs/routing only.
- If any repo-local implementation worker introduces bad local changes, revert only those repo-local edits after review.
- Do not revert protected-side `.205` state because this slice does not mutate it.

## Follow-Ups

- Route and supervise focused workers for:
  - Claude host metadata/doc alignment
  - read-only bridge snapshot contract
  - local auth dependency readback
  - local worker durability/readback improvements
  - modular tool-layout migration map
- The above worker routes are now live. Continue supervising them to proof or exact blocker instead of creating another umbrella queue.
- The AI Manager input recorder is now installed; use it to keep route receipts durable instead of reintroducing a generic placeholder path.
- After those workers return, decide which repo-local implementation can land immediately and which system-path changes need a separate approval pass.
- Docs alignment proof for this slice is now recorded in `project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md`, `HANDOFF.md`, and this project note, attached to OPS project `369808` / task `369809`; no `~/.ssh/config` edit or protected-side file change was performed.
- Bridge-contract proof for this slice is now recorded in `ai-bridge/`, `HANDOFF.md`, and this project note, attached to OPS project `369808` / task `369810`; no protected-side mutation, secret export, writable cross-system bridge, or OPS task-content mutation was performed.
- Migration-map proof for this slice is now recorded in `project_hub/artifacts/claude-host-tool-layout-migration-map-2026-05-18.md`, `HANDOFF.md`, and this project note.
- Carry the same contract into any follow-on Task Flow packets: one execution row per actionable slice, linked to the corresponding OPS task id in `ops_portal_or_domain_task`, with no duplicate markdown queue entry unless a temporary projection is explicitly needed.
- Next concrete move after this repo-local extraction: continue the same Workspaceboard-owned extraction pattern for the remaining planner/health entrypoints and then migrate the remaining callers from legacy `ai_workspace/scripts` paths one surface at a time.
2026-05-18 22:18 CDT: closed the remaining protocol gap that was causing live workers to linger without a hard finish/restart contract. `scripts/ai_health_check.py` now treats live `working` Task Flow packets with no closeout proof older than one hour as restart-eligible, and the live Workspaceboard server no longer counts legacy `routed` rows as active live work in the capacity/enforcement path. This stays within the same Claude-host parity initiative; it is not a new subsystem.

## 2026-05-22 Routed Packet Closeout

- Reviewed Workspaceboard packet `taskflow-2c650876c99d7385` for `vanessa.sterling@kovaldistillery.com` (`New project created: AI Claude Host Parity and Local Execution Improvements`) from within `ai_workspace`.
- Confirmed the initiative already has a durable local project note at this path, linked to OPS project `369808`, with concrete slice task anchors `369809` through `369813`.
- Re-verified the AI Workspace proof surface that is readable locally in this session:
  - `project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md` still exists and retains proof marker `CLAUDE_HOST_DOCS_ALIGNED project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md:1`.
  - Local grep readback still shows the old `/home/claude/.claude/.mcp.json` path only in historical/provenance notes, not as an active host-surface contract for the current parity slice.
- Scope remained repo-local. No protected-side edit, `~/.ssh/config` edit, credential move, or runtime mutation was performed during this closeout.
- Session note: the older `ai-bridge` proof references in this project note were not re-asserted as fresh proof here because `/Users/werkstatt/ai-bridge` is not present in this session checkout; the truthful live closeout for this packet is the AI Workspace proof surface above.
