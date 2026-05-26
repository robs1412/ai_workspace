# AI Memory Policy
Last Updated: 2026-05-21 14:58 CDT (Machine: Macmini.lan)

## Recommended Use

### MemPalace

Use for:
- local deep recall on one active repo or initiative
- mining old project docs and chat exports when exact historical context matters
- MCP-assisted project search on a workstation

Do not use for:
- live server runtime
- default memory layer for every repo
- shared production service for the team

Current approved use here:
- local `salesreport` recall from this workstation
- local MCP server `mempalace-salesreport`

### Mesh

Use for:
- shared team memory
- hosted or production-style knowledge service
- multi-workspace search and browsing
- cases where auth, UI, API, and policy controls matter

Preferred when:
- multiple people or agents need the same memory system
- memory should be browsable in a web UI
- organization-wide structure matters more than local simplicity

### agent-memory

Use for:
- solo coding-session capture
- low-friction always-on local memory
- environments where secret scrubbing and lightweight setup matter

Preferred when:
- the goal is passive session memory, not project archive mining
- setup speed matters more than rich taxonomy or benchmarked retrieval
- the task is a repeated operational recipe that should point at a durable runbook instead of being rediscovered

Recommended local runbook for repeated operational recipes:
- `project_hub/artifacts/repeating-access-guide-2026-05-20.md`

Use this runbook when a task repeats across:
- Google Drive / Docs access
- Portal entity creation or repair
- sample-request workflows
- SSH to the approved Claude backup lane

## Decision Rule

Choose:
- `MemPalace` for project-specific local recall
- `Mesh` for team/shared memory
- `agent-memory` for passive solo coding memory

## AI Manager Rule Set

Use this when the task is about memory, durability, or repeatable agent behavior:

1. Do the work directly when it is one-off, context-specific, and not something a future session needs to rediscover.
2. Promote a repeated procedure to a skill when it has been re-instructed or run at least twice across sessions, and the steps must stay consistent.
3. Write an assessment to Papers when it is a non-trivial conclusion, a future session would not reasonably rediscover it, and it affects multiple sessions or agents. Store the decision, rationale, confirming person, and date. Do not store the procedural steps there.
4. Mirror AI Manager mode prompts, corrections, and confirmed decisions through the AI Manager control-lane recorder hook, not chat history alone. The approved path is the AI Manager mode hook into `scripts/ai_manager_chat_entry_adapter.php` / `ai_manager_input_recorder.php`, which keeps the DB trail and daily-input log in sync.

Practical boundary:
- use a skill for repeatable how-to behavior
- use the recorder trail for prompt and decision durability
- use Papers for durable cross-session assessments and policy rulings
- keep the hook in AI Manager mode configuration, not as a global hook

## Deployment Rule

Keep memory infrastructure off live app servers unless there is a direct runtime need.

For `salesreport` specifically:
- keep `.mempalace/` local and untracked
- keep MemPalace helper scripts in `ai_workspace`, not in `salesreport`
- do not install or run MemPalace on live by default

## Claude Integration Rule

Preferred path:
- use Claude Code or Claude Desktop as the client
- connect Claude to local tools through MCP
- point Claude at the same local MemPalace corpus used by Codex

Do not assume Codex and Claude need direct model-to-model coupling.
The useful integration layer is usually:
- shared repo
- shared local memory corpus
- shared MCP-accessible tools
