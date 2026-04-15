# AI Memory Policy
Last Updated: 2026-04-07 09:37:08 CDT (Machine: Macmini.lan)

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

## Decision Rule

Choose:
- `MemPalace` for project-specific local recall
- `Mesh` for team/shared memory
- `agent-memory` for passive solo coding memory

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
