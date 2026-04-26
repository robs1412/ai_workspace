# Codex / Claude Overlap Matrix

Status: working comparison note
Updated: 2026-04-24 CDT

This note is the fast comparison layer between the local Codex / Workspaceboard structure and the live Claude-side `.205` structure.

Use it to answer three questions quickly:

1. Which side should own the work right now?
2. Where are the similar roles or surfaces?
3. What should be shared by contract, and what should stay independent?

## Core Rule

The systems can live side by side.

- Codex / Workspaceboard remains the primary local execution and management surface.
- Claude remains a server-side department with its own task, document, mail, and agent surfaces.
- Shared contracts should be narrow and explicit, not assumed.

## Role / Surface Matrix

| Local Codex / Workspaceboard | Claude-side parallel | Similarity | Important difference | Bridge point |
| --- | --- | --- | --- | --- |
| Task Manager / Polier | Claude Planner Operator | Both manage task routing and state | Local side is Workspaceboard/TODO/project-hub driven; Claude side is Planner DB driven | Shared task-record spine and handoff ids |
| Project Manager | Claude Planner Operator | Both scope work into owned tasks | Project Manager is cross-workspace planning; Planner is the live server-side task register | Task-to-task mapping only when needed |
| project_hub / HANDOFF / TODO | Claude Papers Operator | Both are durable work context surfaces | Local side is Markdown-first; Claude side is Papers API-first | Read-only work-record projection before any shared write path |
| Frank / Avignon / Communications Manager / Email Coordinator | Claude Mail Operator | Both handle drafting, routing, and send-readiness concerns | Claude mail uses `/srv/tools/email/`; local side uses mailbox-worker workflows and separate persona rules | Shared send-confirmation rule and no-impersonation rule |
| AI Health Manager | Claude Agent Operations | Both care about operational visibility and stale-state risk | Local side is visible-session/manual health; Claude side includes cron/background agents | Shared health vocabulary only, not a merged runtime |
| AI Improvement Manager | Claude Agent Operations | Both touch recurring process review and workflow improvement | Local side is visible EOD review; Claude side includes recurring autonomous agents | Shared improvement reporting format when useful |
| Codex Integration Manager | Claude Bridge Worker | Both own cross-system coordination | Codex side integrates and routes locally; Claude bridge returns server-side analysis and handoffs | Handoff packet contract |
| Codex Local Agent / workspace workers | Claude Server Agent | Both can produce implementation-oriented work | Codex edits local repos directly; Claude works server-side on `.205` and should not collide | Single-writer ownership and bounded handoffs |
| Security Guard | Claude `.205` Structure | Both protect sensitive boundaries | Security Guard is an active routing gate; `.205` Structure is a documentation/visibility surface | Approval gates and boundary records |

## Directives Already Read Live

These Claude-side directives are now confirmed from live `.205` reads:

- `/srv/CLAUDE.md`
- `/srv/tools/planner/CLAUDE.md`
- `/srv/tools/papers/CLAUDE.md`
- `/srv/tools/email/CLAUDE.md`
- `/srv/agents/CLAUDE.md`

Most important live rules already extracted:

- secrets belong in Infisical as the default rule;
- email requires explicit send confirmation;
- Claude must not sign as other people;
- Papers work goes through the API tools, not direct file edits;
- Planner is the Claude-side task-management system;
- autonomous agents are a first-class Claude-side operating surface;
- actual shell login is `claude`;
- `/home/claude/.claude/.mcp.json` was not present, so older bridge expectations around that path are stale.

## Additional Claude Coverage

We now have more than the top-level directive set.

High-value additional agent docs read in summary form:

- `secretary`
- `pm`
- `developer`
- `tester`
- `marketer`
- `webmaster`

Most useful extra takeaways:

- Claude separates router, planner, implementer, tester, and mail lanes more aggressively than our local stack.
- Autonomous agents are real operating units, but email and task-routing still have centralized control surfaces.
- The local Codex side should imitate the separation where useful, not the exact runtime.

## Real Config Surfaces

The real current Claude-side config surface is layered:

- `/home/claude/.claude/settings.json`
- `/home/claude/.claude.json`
- `/home/claude/.claude/mcp-needs-auth-cache.json`
- plugin-local `.mcp.json` files and MCP cache/log state

Confirmed implication:

- `/home/claude/.claude/.mcp.json` is not the current authoritative bridge target.

## What We Still Have Not Read Completely

We still have not claimed full Claude-side instruction coverage.

Remaining likely instruction surfaces:

- other `/srv/.../CLAUDE.md` files outside the core and high-value agent surfaces already read;
- specific service docs for Google Drive, Mesh, and AI Gateway;
- deeper agent-local docs where a later bridge slice depends on stricter local rules;
- any service- or project-specific `CLAUDE.md` files that materially affect bridge behavior.

## What Is Actionable Now

Safe alignment work that can proceed now:

1. Keep Codex local structure intact.
2. Show Claude as a parallel department in the organigram.
3. Align shared rules where they are clearly beneficial:
   - Infisical-first secret handling
   - explicit email send confirmation
   - API-only Papers mutation
   - stronger structured task records
4. Keep task, document, mail, and agent lanes visible as separate surfaces.
5. Use bridge handoffs instead of pretending both systems share one live task store already.

## What Still Needs More Claude Reading Before We Implement Deeper

Do not claim final integration design until we verify:

1. the actual Claude-side MCP/config source;
2. whether specific agents have stricter local rules than `/srv/agents/CLAUDE.md`;
3. which Claude-side project/service `CLAUDE.md` files matter for Workspaceboard, MI, or bridge work;
4. whether Planner/Papers/mail/agent flows have additional tool-local approval rules beyond the top-level docs already read.

## Deeper Integration Direction

The current best-fit model is:

1. keep Codex local execution and Claude protected-side execution as separate control planes;
2. share a narrow task-record spine and handoff packet format;
3. adopt the Claude-side gains that clearly improve local work:
   - stronger task packets
   - explicit send confirmation
   - API-only structured record mutation
   - planner / implementer / tester separation
4. avoid shared live writes until a single-writer contract exists.

## Recommended Next Reads

1. Read the Claude-side Google Drive, Mesh, and AI Gateway docs next.
2. Replace stale local bridge references to `.mcp.json` with the layered config surface.
3. Define the first local-to-Claude packet formats before any deeper protected-side integration.
