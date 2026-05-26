# Claude Host Tool-Layout Migration Map

Date: 2026-05-18
Status: planning artifact for execution sequencing
Reference: Claude host `.205` tool tree under `/srv/tools` and local parity note `project_hub/issues/2026-05-18-claude-host-parity-and-execution-plan.md`
OPS anchor: project `369808`, task `369813`

## Purpose

This map answers one narrow question: which current local capabilities should remain in `ai_workspace` as coordination state, and which ones should graduate toward clearer tool-oriented surfaces modeled after the Claude host's explicit `/srv/tools/...` layout.

This is not a mass restructure plan. It is an execution-oriented extraction order and ownership map so future implementation workers can move one capability at a time without turning `ai_workspace` into a second runtime repo.

## Local Rule

`ai_workspace` should stay the coordination and policy layer.

That means it remains the right home for:

- cross-repo planning and incident logs
- role, persona, and operating-policy docs
- durable non-secret handoff records
- bridge contracts and migration specs

It should stop being the long-term home for shared runtime code, daemon helpers, mailbox tooling, auth/export utilities, and service logic that really belongs to a named tool surface.

## Reference Pattern From Claude Host

Verified Claude-side modular surfaces:

- `/srv/tools/planner`
- `/srv/tools/papers`
- `/srv/tools/email`
- `/srv/tools/gdrive`
- `/srv/tools/portal`
- `/srv/tools/screenshot`
- `/srv/tools/timetracker`
- `/srv/tools/mesh`
- `/srv/tools/shopify`

The useful lesson is not "copy the same tree exactly." The useful lesson is:

1. keep coordination docs separate from tool code
2. make each capability visible as an owned surface
3. keep auth/readback state explicit
4. avoid burying runtime behavior in a general planning repo

## Decision Table

| Capability | Current local surface | Claude-side analogue | Decision | Target surface | First practical move |
| --- | --- | --- | --- | --- | --- |
| Cross-repo policy and operating rules | `AGENTS.md`, `README.md`, `docs/`, `worker_roles/` | top-level `/srv/CLAUDE.md` plus tool docs | Stay in `ai_workspace` | Keep in `ai_workspace` | No move. Continue using this repo as the policy/control layer. |
| Durable planning and incident history | `project_hub/`, `HANDOFF.md`, `daily-inputs/` | Papers-style work record role, but local side is Markdown-first | Stay in `ai_workspace` | Keep in `ai_workspace` | No move. Add links out to tool owners instead of embedding runtime logic here. |
| Claude/Codex overlap and bridge contracts | `worker_roles/codex-claude-overlap-matrix.md`, parity notes, bridge planning docs | bridge-facing tool docs | Stay in `ai_workspace` | Keep in `ai_workspace`, with implementation in `ai-bridge` or owner repo | Keep specs here; do not add live runtime code here. |
| Task-flow shared logic and due-runner behavior | `scripts/shared_task_flow.py`, `scripts/task_flow_mysql_recorder.php`, `scripts/task_flow_due_runner.py`, `scripts/task_flow_papers_project.py` | `/srv/tools/planner` | Graduate | `workspaceboard` as the local planner/runtime surface | Create a `workspaceboard`-owned task-flow tool area and move shared runtime code there first, leaving thin docs or wrappers in `ai_workspace` only if needed. |
| Worker/session durability and health readback | `scripts/ai_health_check.py`, `scripts/install_ai_health_manager_launchagent.sh`, worker-state notes in `HANDOFF.md` | Claude agent-operations and explicit session state under `/home/claude/.claude/...` | Graduate | `workspaceboard` | Move health/runtime implementation beside Workspaceboard session state and API code; keep only policy and operator notes here. |
| Shared mailbox polling/thread helpers | `scripts/email_worker_header_poll.py`, `scripts/email_worker_threads.py` | `/srv/tools/email` | Graduate | shared email-tool surface owned by mailbox runtimes, not root `ai_workspace/scripts` | First extract the shared helpers into a named mail-tool package used by Frank/Avignon/National Outreach runtimes; leave persona docs here. |
| Worker-specific mail runtimes | `frank/runtime-source/...`, `avignon/runtime-source/...`, `scripts/nationaloutreach_mail_cycle.py`, `scripts/run_nationaloutreach_auto.sh` | `/srv/tools/email` with agent-specific behavior layered above it | Graduate | per-worker runtime surfaces plus a shared mail-tool layer | Standardize the shared library first, then keep only worker-specific launch/runtime wiring under each worker lane. |
| Google export and attachment utilities | `scripts/gmail_export.py`, `scripts/ertc_gmail_direct_export.py`, `scripts/google_docs_export.py`, `scripts/gmail_extract_attachments.py` | `/srv/tools/gdrive` and adjacent service tools | Graduate | `ai-bridge` or a dedicated export tool surface outside `ai_workspace` root | Group these under a named export/drive surface with explicit auth expectations and avoid scattering them in `scripts/`. |
| Secure transfer and intake helpers | `scripts/ai_transfer_fetch.py`, `scripts/ai_transfer_gate.py`, `scripts/secure_info_intake.py`, `docs/secure-info-intake.md` | secure sidecar tooling, not a general planning concern | Graduate implementation, keep policy here | `ai-bridge` or a dedicated secure-transfer tool surface | Split docs from code: keep approval/policy docs in `ai_workspace`, move executable tooling to the bridge/security owner surface. |
| National Outreach workflow-specific automation | `nationaloutreach/scripts/...`, `nationaloutreach/README.md`, reminders and templates | local equivalent of a dedicated domain tool, not a Claude core tool | Mixed: docs stay, runtime graduates | `nationaloutreach/` runtime surface or eventual module repo | Keep templates/guidance in `ai_workspace/nationaloutreach`; move generic automation out of root `scripts/` and keep only lane-owned code near that lane. |
| Ad hoc reports and analysis scripts | `scripts/redistill_*`, `scripts/ertc_discovery_export.py` | domain-specific tool bundles | Graduate when reused; otherwise keep as one-off artifacts | owning workspace or a named report-tool bundle | Do not keep growing `ai_workspace/scripts` as a report graveyard. Rehome only the scripts that prove reusable. |
| Safety and credential handling guidance | `codex-agent-safety.md`, `AI_BOX_SECURITY.md`, `docs/credential-access-methods.md` | host-level policy docs | Stay in `ai_workspace` | Keep in `ai_workspace` | No move. These are policy, not tools. |

## Concrete Extraction Sequence

### Phase 0: Freeze the Role of `ai_workspace`

Treat `ai_workspace` as the source of truth for:

- policy
- planning
- handoff
- role docs
- non-secret bridge contracts

Do not add new shared runtime helpers to `ai_workspace/scripts` unless they are clearly temporary and already have an identified destination owner.

### Phase 1: Pull Out Planner/Runtime Code First

First graduation target:

- `scripts/shared_task_flow.py`
- `scripts/task_flow_mysql_recorder.php`
- `scripts/task_flow_due_runner.py`
- `scripts/task_flow_papers_project.py`
- `scripts/ai_health_check.py`

Why first:

- these are already shared operational surfaces
- they align most directly with the Claude host's explicit `planner` and agent-operations structure
- they are tightly coupled to Workspaceboard runtime truth, not just planning

Execution shape:

1. create a named tool area in `workspaceboard`
2. move implementation there without changing behavior
3. leave compatibility wrappers or updated call sites only where necessary
4. update project docs in `ai_workspace` to point at the new owner

### Phase 2: Normalize Email Tooling

Second graduation target:

- `scripts/email_worker_header_poll.py`
- `scripts/email_worker_threads.py`
- `scripts/nationaloutreach_mail_cycle.py`
- duplicated or near-duplicated mail helpers inside `frank/runtime-source` and `avignon/runtime-source`

Why second:

- these already behave like a tool family
- the current root-level placement hides ownership
- Claude's `/srv/tools/email` makes the capability boundary explicit

Execution shape:

1. define a shared mail-tool layer
2. make Frank, Avignon, and National Outreach import from that layer
3. keep persona rules and owner-facing docs in `ai_workspace`
4. keep send-policy approval logic documented here, but not the runtime code

### Phase 3: Pull Security/Transfer/Export Helpers Behind Named Surfaces

Third graduation target:

- `scripts/ai_transfer_fetch.py`
- `scripts/ai_transfer_gate.py`
- `scripts/secure_info_intake.py`
- `scripts/google_docs_export.py`
- `scripts/gmail_export.py`
- `scripts/gmail_extract_attachments.py`
- `scripts/ertc_gmail_direct_export.py`

Why third:

- these tools are useful but cross too many concerns when left in one generic script bucket
- they need explicit ownership and auth/readback contracts
- they should not look like "just random scripts in the planning repo"

Execution shape:

1. group by capability, not by historical origin
2. choose an owner surface such as `ai-bridge` for bridge/export/secure-transfer tooling
3. leave a stable doc pointer in `ai_workspace`
4. only then remove the old root-level copies

### Phase 4: Clean Up the Remaining `scripts/` Bucket

After the first three phases, review what remains in `ai_workspace/scripts/`:

- keep only planning-safe helpers that truly belong to the coordination repo
- move reusable domain automation to the owning lane
- archive or delete dead one-off scripts after verifying they are not referenced

## Naming Guidance For Future Local Tool Surfaces

Use the Claude host as a naming discipline, not as a rigid directory template.

Preferred local surface names:

- planner / task-flow
- email
- auth-status or auth-readback
- bridge-transfer
- drive-export
- health

Avoid vague buckets such as:

- `misc`
- `helpers`
- `automation2`
- ever-growing root `scripts/`

## Guardrails

- Do not move policy docs out of `ai_workspace`.
- Do not move secrets, caches, or machine-local runtime state into git-backed planning repos.
- Do not use this map as approval for a bulk restructure.
- Prefer one capability at a time, with owner repo, compatibility plan, and rollback note.
- For cross-repo changes, record the move in `project_hub/` with the owning repo and commit SHAs.

## Recommended Next Worker Packet

If this map is used immediately, the next implementation slice should be:

`Extract task-flow runtime helpers from ai_workspace/scripts into a named workspaceboard-owned planner surface without changing behavior.`

That slice is the best first move because it reduces the largest current mismatch between the coordination repo and the runtime/tooling boundary.
