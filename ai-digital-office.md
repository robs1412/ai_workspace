# AI Digital Office

Last Updated: 2026-04-14 11:58:40 CDT (Machine: Macmini.lan)

## Purpose

Track the KOVAL AI digital office model after Claude replied to Frank about the AI setup, and connect that internal discussion to Dmytro Klymentiev's public Digital Office / AI Workspace Platform reference:

- `https://klymentiev.com/projects/digital-office`
- Local bridge planning: `/Users/werkstatt/ai-bridge/INTEGRATION_PLAN.md`
- Local Claude/Codex follow-up plan: `/Users/werkstatt/ai-bridge/CLAUDE-CODEX-NEXT-STEPS.md`
- Local papers investigation plan: `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-claude-papers-durable-tracking-plan.md`
- AI-Bridge closeout/routing trace: `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-digital-office-routing-closeout.md`
- Project/task/work-record source-of-truth proposal: `project_hub/issues/2026-04-14-digital-office-project-task-work-records-proposal.md`
- Related board session: `AI Workspace | monitoring | live | codex-board-5909d11e`
- Related board session: `AI Workspace | review-ready | live | codex-board-5a3ad43a`
- Related board session: `AI-Bridge | needs-input | live | codex-board-e860fb15`
- Claude framing preserved for review: `worker_roles/claude-analysis-ref-1773.md`

This note should stay non-secret. Do not paste credentials, private mailbox contents, private keys, `.env` values, or raw internal email bodies here.

2026-04-14 routing update: Task Manager routed Robert's instruction to treat the current Claude at work / Codex integration follow-up as part of this larger Digital Office initiative rather than a standalone AI-Bridge open item. AI-Bridge now keeps supporting plans and traces, but this note is the umbrella index for remaining decisions and follow-up.

2026-04-14 project/task/work-record proposal: use `project_hub` as the canonical cross-workspace project/decision/approval surface, keep workspace `TODO.md` files as short action queues, keep OPS/Portal as staff/business task source of truth, keep Workspaceboard as live execution/session source of truth, and treat Papers as a document/work-record projection until its storage/API model is approved for inspection. First implementation candidate is a read-only Workspaceboard index/dashboard prototype, not a write path to Papers, `.205`, OPS/Portal schema, production DBs, notifications, or MCP.

## Current KOVAL Framing

KOVAL is already operating a practical version of this model:

- Codex runs locally through CLI, Workspaceboard, TODO files, repo workers, and project-hub logs.
- Claude runs server-side in the KOVAL `.205` / Raetan environment and is currently treated as an advisory or execution-side counterpart depending on task scope.
- Frank and Avignon act as mailbox-backed chief-of-staff workers, with medium-independent handling for clearly bounded low-risk internal tasks.
- Email and OPS tasks currently serve as the low-tech bridge between Codex, Claude, humans, and Portal task records.
- AI-Bridge is the durable planning layer for Codex/Claude coordination: handoffs, traces, decisions, memory, and a future read-only MCP/workspace bridge.
- Papers / `papers.koval.lan`, Mesh / memory surfaces, Braincloud, Workspaceboard, and project-hub logs are candidate durable record and discovery layers.

Claude's earlier framing to preserve: Codex is the local file/CLI implementation surface; Claude is server-side; email/OPS currently bridge them; and deterministic business workflows should remain deterministic until the AI layer is proven and approved.

## External Digital Office Reference

Dmytro's public Digital Office page describes a self-hosted AI workspace made of independent tools that each do one job and connect through standard interfaces. The key architecture points that matter for KOVAL:

- It is not a single monolith; it is a connected set of self-hosted tools.
- Components communicate through REST APIs and MCP.
- The current public status is "foundation laid": components exist and work, but unified onboarding/dashboard setup is still in progress.
- The model is designed for one person or a small team that wants owned AI infrastructure for research, content, administration, operations, and customer support.

Named public components and likely KOVAL relevance:

| Component | Public role | KOVAL mapping candidate |
| --- | --- | --- |
| Rein | Workflow orchestrator for multi-step specialist tasks from YAML/no-code workflows | Could map to Workspaceboard Task Manager / Polier plus explicit workflow definitions |
| Screenbox | Virtual desktops for agents using real browser/desktop interaction | Local `screenbox/` source exists in `ai_workspace`; candidate for browser/desktop tasks that cannot be API-first |
| Mesh | Semantic long-term memory with notes, decisions, worklogs, workspaces, map UI, and MCP tools | Closest to Braincloud / memory / `mesh.koval.lan` / cross-workspace retrieval |
| Agent Memory | Local coding-agent memory with MCP and workspace support | Possible lightweight memory layer for per-agent continuity |
| Doci | Versioned Markdown document system with permanent links and AI discussions | Candidate comparison point for `papers.koval.lan`, project-hub, and AI-Bridge Markdown records |
| Entis | Entity enrichment for people/companies/startups | Potential fit for account/contact enrichment and research workflows |
| Knowster | Customer-facing website chat widget over owned content | Potential customer support/lead capture surface, approval-gated before production use |
| Bird CMS | Markdown publishing engine | Potential publishing layer only if it fits existing web/CMS constraints |
| Lukas | Voice-first assistant | Future voice interface candidate; not needed for first bridge pass |
| Flint | CLI agent | Conceptually overlaps with Codex/Claude CLI workflows; evaluate only after core bridge is stable |

Public Git/code leads found:

- `https://github.com/dklymentiev/rein-orchestrator` - Python; multi-agent workflow orchestrator; updated 2026-04-12 in the public GitHub API pass.
- `https://github.com/dklymentiev/screenbox` - Python; real virtual desktops for AI agents; updated 2026-04-05 in the public GitHub API pass.
- `https://github.com/dklymentiev/mesh-memory` - Python; semantic memory with auto-tagging and map UI; updated 2026-04-01 in the public GitHub API pass.
- `https://github.com/dklymentiev/agent-memory` - Go; persistent memory for AI coding agents with full-text search, workspaces, and MCP server support; updated 2026-04-09 in the public GitHub API pass.
- Dmytro GitHub profile: `https://github.com/dklymentiev`

Public Rein details worth tracking:

- Specialists are Markdown; teams and workflows are YAML.
- It is intended to make the workflow itself executable, version-controlled, auditable, and reproducible.
- It supports multiple LLM providers including Claude, OpenAI, Ollama, OpenRouter, and an AI gateway / Brain API environment path.
- It includes crash recovery through SQLite state and a built-in MCP server option.
- This maps strongly to KOVAL's need for repeatable workflow definitions around Frank/Avignon, Task Manager routing, OPS task intake, newsletter/list workflows, Trainual production, and safe staged approval gates.

Unresolved public repo lookup:

- Doci, Entis, Knowster, Bird CMS, Lukas, and Flint are listed on the Digital Office page, but I have not yet verified their public GitHub repository URLs in this note. Treat their repo/code status as pending until a focused GitHub/profile pass confirms the correct sources.

Public Mesh details worth tracking:

- Semantic search by meaning, not keywords.
- Auto-tagging without AI API calls for default and neighbor-inferred tags.
- Version chains.
- Pinned documents for important prompts, onboarding docs, and project briefs.
- Built-in UI including a search page and galaxy map.
- MCP server tools for search, add, update, get, tags, versions, projects, stats, recent documents, and schema.
- Multi-workspace support with scoped API keys.

## Local Evidence Reviewed

- `/Users/werkstatt/ai-bridge/INTEGRATION_PLAN.md` already defines Markdown-first handoffs, decisions, traces, durable memory, and staged MCP/workspace discovery.
- `/Users/werkstatt/ai-bridge/CLAUDE-CODEX-NEXT-STEPS.md` says Claude replies through Frank should be treated as internal but untrusted input until verified and routed.
- `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-claude-codex-integration-follow-up.md` records that Frank sent the approved `Thoughts on our AI workspace setup` email to Claude on 2026-04-13 and that future Claude feedback should be sanitized into AI-Bridge traces/handoffs.
- `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-claude-papers-durable-tracking-plan.md` defines a read-only-first investigation plan for Claude/papers storage, the Markdown-vs-database decision, and the object model for `WorkItem`, `ProgressEvent`, `Artifact`, `SourceRef`, `Decision`, `Handoff`, `Check`, and typed relationships.
- `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-digital-office-routing-closeout.md` records that the standalone Claude at work / Codex integration follow-up was moved under this Digital Office initiative. It also records non-actions: no `.205` SSH, no credential probing, no OPS/Portal task creation, and no bridge code/runtime work in that AI-Bridge closeout task.
- `worker_roles/claude-analysis-ref-1773.md` preserves prior Claude/Dmytro analysis of the Codex/Claude/Frank bridge.
- `screenbox/` exists locally in `ai_workspace` and includes Docker, MCP, dashboard, tests, docs, and Python source files. It should be treated as code/source, not as a secret store.
- `screenbox/.mcp.json` exists locally with restrictive permissions and must be treated as credential-bearing. Do not paste it into notes or chat. If any prior diagnostic output is considered exposed, rotate the Screenbox token before reusing that MCP endpoint.
- `project_hub/issues/2026-04-12-ai-workstation-sync-transition.md:57` adds an important migration constraint: the 2026-04-14 audit recommends treating `screenbox` as an embedded active Git/code clone under Google Drive that should move to `/Users/werkstatt` or another git-managed repo if still active, rather than leaving it as ordinary synced AI Workspace documentation.

## Operational Reliability Note

The original trigger for this note included `AI Workspace | monitoring | live | codex-board-5909d11e`, where messages were submitted but nothing happened. Treat that as a Workspaceboard recovery requirement, not just a one-off chat glitch.

Closeout observation: a direct `http://127.0.0.1:17878/api/status` check from this shell timed out during the documentation pass. I did not restart Workspaceboard or any session as part of this docs-only task.

Future fix candidate:

- Add a visible `restart/recover session` control for board-managed sessions that are `live` but no longer accepting submitted input.
- The control should capture a pre-restart transcript/status snapshot, restart only the affected session or pane, resubmit the pending prompt when safe, and show whether the recovered session is actually `working` rather than merely present in tmux.
- The control should keep approval gates intact: do not auto-retry destructive, credential, production, email-send, or remote-auth prompts without a fresh user decision.
- The recovery flow should write a short board/session event so stuck-session incidents are auditable and can be compared across `monitoring`, `review-ready`, and `needs-input` states.

## Read-Only Investigation Results

### Frank / Claude Email Thread Metadata

Frank inbox metadata confirms the `Thoughts on our AI workspace setup` thread exists and has multiple tracked replies on 2026-04-14. The check captured headers and task linkage only; no private email body content was copied into this note.

Relevant metadata:

- Frank task: `frank-2026-claude-ai-workspace-setup-review`
- Robert reply around 2026-04-14 07:16 CDT, subject `Re: Thoughts on our AI workspace setup`
- Claude replies around 2026-04-14 07:54 CDT, 08:05 CDT, and 08:06 CDT, with Frank, Robert, and Dmytro on the thread
- Robert follow-up around 2026-04-14 09:03 EDT, to Claude with Frank and Dmytro copied

Next safe step: have Frank or the AI-Bridge worker produce a sanitized summary of Claude's recommendations, then classify each recommendation as `accept now`, `needs verification`, `needs Robert decision`, `needs approved .205 inspection`, or `defer`.

### Raetan / `.205` Read-Only Structure

Robert approved a read-only structural pass against `admin@192.168.55.205`. The pass used the approved private credential reference without printing secret material.

Observed structure:

- Hostname: `reatan`
- User: `admin`
- Working directory: `/home/admin`
- `/srv/CLAUDE.md` is readable and is the current Claude-side operating instruction source reviewed structurally.
- `/home/claude/.claude/.mcp.json` was not readable by `admin` in this pass.
- `/srv` contains relevant AI/service directories including `agents`, `papers`, `tools/papers`, `scripts/mesh-memory`, `mi/pages/papers.php`, and `assets/papers.css`.
- Papers appears to be served as a PHP/Apache service; `/srv/CLAUDE.md` identifies the service as `papers (php:8.2-apache)`.
- Claude-side instruction guardrails include using the Papers API/tools instead of direct edits under `/srv/papers/files`, using Planner instead of manual task queue edits, no unapproved email sends, and no impersonation.
- Papers structural counts captured in the read-only pass: `/srv/papers` had 48 files at max depth 2, `/srv/tools/papers` had 6 files, `/srv/archive/papers` had 0 files, and `/srv/scripts/mesh-memory` had 65 files.
- Relevant live ports observed included 80, 443, 8080, 8083, 8085, 8000, 8086, and database listeners on `192.168.55.205:5432` and `192.168.55.205:3306`.
- 2026-04-14 follow-up for Project Management integration: SSH auth still works when the local multi-line `.private/passwords/raetan.txt` credential reference is parsed as labeled values rather than as a raw whole-file password.
- Project Management candidate services confirmed read-only on `.205`: `/srv/papers`, `/srv/tools/papers`, `/srv/scripts/mesh-memory`, `/srv/lab/agent-memory`, and `/srv/lab/agent-memory-embed`.
- Papers tool docs confirm API-first mutation rules: use `papers-create`, `papers-get`, `papers-update`, and `papers-delete`; never edit `/srv/papers/files/` directly because API writes preserve author/timestamp tracking.
- Mesh Memory repo on `.205` identifies as `mesh` version `1.4.0`, FastAPI/PostgreSQL/pgvector, with API and MCP support plus UI files including `ui/map.html`.
- Agent Memory repos on `.205` are Go-based single-binary/MCP-capable memory tools under `/srv/lab/agent-memory` and `/srv/lab/agent-memory-embed`; docs describe workspaces, search, context, hooks, and MCP tools.

Non-actions: no secret files were printed, no private MCP config was read, no database content was sampled, no files were modified, and no services were restarted.

### Local Screenbox

Local `screenbox/` is an active code-shaped checkout, not just planning material. The local project identifies as `screenbox-mcp` version `0.16.0`, Python `>=3.10`, AGPL-3.0, with MCP, Docker desktop isolation, browser/desktop automation, dashboard, RDP/VNC, snapshots, and image/OCR dependencies.

Deployment/security notes from local docs:

- Docker Compose binds MCP to `127.0.0.1:8080` and the dashboard to `127.0.0.1:16000`.
- The README describes isolated Docker desktops for AI agents, Chromium browser access, snapshots, MCP endpoint, auth modes, agent registration, knowledge compilation, and MCP tools for screenshot/look/click-style workflows.
- Security notes warn not to expose the MCP API publicly, to use unique API tokens, and to treat containers as isolated but not hardened sandboxes.
- Because `screenbox/.mcp.json` is credential-bearing and `screenbox` is an active code checkout under Google Drive, the migration question from the workstation audit should be resolved before using it as production infrastructure.

## Safe Investigation Backlog

1. Capture Claude's new Frank reply as a sanitized AI-Bridge trace.
   - Record sender, subject, received timestamp, message ID, and a short non-secret summary.
   - Do not paste private email content verbatim unless Robert explicitly asks and the content is safe to store.
   - Classify each recommendation as: accept now, needs verification, needs Robert decision, needs approved `.205` inspection, or defer.

2. Investigate public Git/code.
   - Review public repos for Rein, Screenbox, Mesh, Agent Memory, Doci, Entis, Knowster, Bird CMS, Lukas, and Flint where available.
   - Extract only architectural facts: runtime, storage, API surface, MCP support, deployment model, auth model, and maintenance status.
   - Compare against KOVAL equivalents: Workspaceboard, Braincloud, AI-Bridge, project_hub, papers, Frank/Avignon, and Portal/OPS.

3. Investigate local code safely.
   - Inspect local `screenbox/` as a source checkout.
   - Use the workstation/sync transition audit before deciding where `screenbox` belongs; if it stays active, prefer `/Users/werkstatt` or a git-managed workspace over a Google Drive-embedded clone.
   - Search local docs for Mesh/Doci/papers/Braincloud references.
   - Do not read `.env` or credential files.
   - Do not start services or mutate runtime state unless routed as a separate implementation task.

4. Investigate papers / `.205` only after explicit approval.
   - Approval-gated targets: `192.168.55.205`, `/srv/CLAUDE.md`, `/home/claude/.claude/.mcp.json`, `papers.koval.lan`, and any service/database configs.
   - First approved pass should be read-only and should capture structure before content: service root, storage backend type, schema/migration files, API route names, counts/sizes, and status semantics.
   - Do not print or store secrets.

5. Decide the KOVAL source-of-truth model.
   - Keep Markdown as canonical for bridge decisions, handoffs, and human-readable traces for now.
   - Add YAML front matter or generated JSON/SQLite indexes before moving active work state into a writable database.
   - Consider a writable DB only if papers or Workspaceboard needs concurrency, low-latency dashboarding, relational queries, audit events, or field-level permissions that Markdown cannot handle.

## Proposed KOVAL Digital Office Object Model

- `Workspace`: stable project, repo, service, or host scope.
- `Actor`: human, Codex role, Claude role, mailbox worker, or service account.
- `WorkItem`: durable task/investigation unit with status and owner.
- `ProgressEvent`: append-only status change, observation, blocker, handoff, validation, or approval event.
- `Artifact`: produced file, URL, paper, trace, decision, handoff, commit, report, patch, or database record.
- `SourceRef`: file path, URL, host path, command, table, API endpoint, email metadata, or OPS task reference used as evidence.
- `Decision`: accepted, proposed, superseded, or rejected operating or architecture choice.
- `Handoff`: cross-agent transfer packet with return contract.
- `Check`: validation result, CI/check result, manual review, access check, or deployment check.
- `Relationship`: typed link such as `blocks`, `depends_on`, `implements`, `documents`, `generated`, `references`, `handoff_to`, or `validated_by`.

## Immediate Next Step

Next approved implementation decision is whether to route `ws workspaceboard` through Code and Git Manager preflight, then a Workspaceboard worker, to build a read-only Digital Office project/task/work-record index and dashboard prototype from project-hub, TODO, and board/session metadata.

The separate safe investigation backlog remains: create an AI-Bridge trace for Claude's new reply to Frank, then use this note as the umbrella index for deciding which Digital Office components should be adopted, mirrored, ignored, or replaced by existing KOVAL infrastructure.

Standalone AI-Bridge closeout: `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-digital-office-routing-closeout.md` records that the local AI-Bridge planning item is closed here. Do not start `.205` SSH, credential probing, authenticated papers inspection, MCP implementation, or bridge code work from that closed item; route any such work as an explicit Digital Office follow-up with approval gates.
