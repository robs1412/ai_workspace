# Codex / Claude / Papers Integration Plan

- Last Updated: 2026-04-26 CDT (Machine: Macmini.lan)

- Master ID: `AI-INC-20260419-CODEX-CLAUDE-PAPERS-01`
- Date: 2026-04-19
- Owner: AI Workspace / Codex Integration Manager
- Repos/surfaces: `ai_workspace`, `workspaceboard`, future `ai-bridge`, future MI/Papers/.205 surfaces
- Status: no-write/read-only plan approved for docs/task-record continuation; source-only Papers read-only wrapper code/tests are implemented in Workspaceboard; unauthenticated Papers connectivity reaches MI login; Robert's 2026-04-23 approval now clears the next Claude-facing protected-side access packet only; live `.205`, authenticated MI/Papers reads, Papers writes, OAuth, Portal data, and mailbox runtime changes are not started

## 2026-04-26 Protected-Side Packet Follow-Up Status

Local status check performed without crossing the protected/auth boundary:

- read the required local notes: `AGENTS.md`, `TODO.md`, `HANDOFF.md`, `frank/HANDOFF.md`, and this project note;
- read `ToDo-append.md`, which has no new queued item for this lane;
- searched local AI Workspace and Frank records for `frank-claude-protected-side-email-followup-2026-04-25`, `#1425`, `#1429`, `ALLOWED_PATHS`, Mesh, Agent Memory, Screenbox, and the known `#1425` Papers link id.

Result:

- no newer usable Claude technical packet is locally recorded;
- no email-body response with MI auth path, Papers first body-read scope/document IDs/`ALLOWED_PATHS`, Mesh read-only surface, Agent Memory read-only surface, Screenbox endpoint/MCP path, or remaining Robert sign-off boundaries was found in local durable notes;
- the April 25 Frank follow-up remains the active request;
- task `#1425/#1429` remains a protected-side packet source that must not be read through MI/Papers auth unless that access path is separately approved.

Next safe action:

- wait for Claude to reply with the technical packet in the email body, or ask Robert/Frank for explicit approval to perform a narrowly scoped status-only mailbox check that does not expose private bodies in chat;
- if Robert wants movement before Claude replies, request a separate Security Guard-approved gate for the exact authenticated `#1425/#1429` read path, allowed identity, allowed document IDs, storage/logging class, and no-write boundary.

Scope preserved:

- no `.205`, MI, Papers private body, credential/token/session storage, mailbox body, MCP/runtime config, deploy, commit, push, reset, clean, or external-sensitive send was performed.

## 2026-04-26 Direct Claude Follow-Up

Robert approved asking Claude again if the protected-side packet was not in Frank's INBOX. A header-only INBOX check found `0` current messages from `claude@koval-distillery.com`; no mailbox body was printed.

Frank sent a direct follow-up to Claude copied to Robert and Dmytro:

- task id: `frank-claude-protected-side-direct-request-2026-04-26`
- subject: `Re: Frank follow-up: protected-side bridge instructions for MI / Papers / Mesh / Agent Memory / Screenbox`
- Message-ID: `<177723408566.76935.17105607660659250669@kovaldistillery.com>`

The ask is for Claude to reply in email body with the MI auth path, Papers first body-read scope/document IDs/`ALLOWED_PATHS`, Mesh read-only surface, Agent Memory read-only surface, Screenbox endpoint/MCP path, and any remaining Robert sign-off items. The email explicitly asks Claude not to send credentials, tokens, private keys, session cookies, or broad access instructions.

## 2026-04-26 Packet Received And First Tool Check

Claude replied at 15:14 CDT. The message was found in Gmail All Mail, not Frank INBOX or Handled.

Trace:

- Message-ID: `<ced9d6f4a696eecd49cb9c94ea4586dd.claude@kovaldistillery.com>`
- subject: `Re: Frank follow-up: protected-side bridge instructions for MI / Papers / Mesh / Agent Memory / Screenbox`

Non-secret packet summary:

- MI, Papers, Mesh, Agent Memory, Screenbox, and Rein surfaces are marked ready.
- Papers allowed paths are `teams/ai-team` and `teams/it`.
- Claude says no remaining Robert sign-off items for those named surfaces.
- Access beyond Papers / Mesh / MI / Screenbox / Rein requires new Robert approval.
- Unified single-key auth is not available yet; Claude references task `#1438`.

First live checks:

- `http://papers.koval.lan/mcp` is reachable but returns `401 Unauthorized: Bearer token required`.
- `http://mesh.koval.lan/mcp` is reachable but returns `401 Unauthorized: Bearer token required`.
- `http://screenbox.koval.lan/mcp` initializes successfully with MCP protocol `2025-03-26`.
- `screenbox_info` succeeded and returned running desktop/tool inventory.

Current boundary:

- Do not use Papers/Mesh/Rein write or mutation-capable tools until the token path is available and the specific logging/write slice is scoped.
- The current shell has no `infisical` binary and no relevant token environment variables, so Papers reads/writes and Papers logging are blocked on approved Infisical/token availability.

## 2026-04-26 Token Setup Request

Frank sent Claude a token setup request at 15:39 CDT, copied to Robert and Dmytro:

- task id: `frank-claude-mcp-token-setup-request-2026-04-26`
- subject: `Frank follow-up: MCP token setup for Codex/Frank runtime`

The request asks for non-secret setup metadata only: Infisical project/environment/path, expected environment variable names, Mac mini loading method, any `infisical` CLI install step, minimum read-only scope, separate Papers logging/write scope if different, and the approved first Papers write-log target. It explicitly asks Claude not to send raw token values or other secret material in email.

## 2026-04-24 `.205` Login Metadata Correction

Source: local approved private reference surface under `ws ai`, file `/Users/werkstatt/ai_workspace/.private/passwords/claude-user.txt`.

Non-secret result recorded from that source:

- the file exists on this machine;
- it records the `.205` Claude-side user as `claude@kovaldistillery.com`.

Correction from earlier session state:

- the earlier statement that the Claude-user credential file was missing on this machine was incorrect;
- the blocker is not "missing local file" anymore;
- the blocker is now the unresolved executable auth path from this shell plus a user-identity mismatch.

Current discrepancy requiring confirmation:

- Robert's 2026-04-24 chat instruction in this session said `claude@koval.lan`;
- the local private metadata says `claude@kovaldistillery.com`.

Current transport state:

- `ssh admin@192.168.55.205` failed in this session;
- `ssh claude@192.168.55.205` failed in this session;
- no secret value was printed, copied into chat, or written to records.

Operational effect:

- treat `claude@kovaldistillery.com` as the current local-source candidate user for `.205`;
- treat `claude@koval.lan` as an unverified alternate identifier until Robert or a live `.205` login confirms which one is authoritative;
- keep `.205` reads blocked until the approved executable auth path is confirmed.

## 2026-04-24 Live `.205` Directive Read

Approved path used in this session:

- password note fetched from the MacBook through the approved `ai-transfer-gate` shared-file path;
- shell login to `192.168.55.205` succeeded as SSH user `claude`.

Live source facts now verified:

1. `/srv/CLAUDE.md` exists and is readable.
2. Actual shell login is `claude`, not the email-style account labels.
3. `/home/claude/.claude/.mcp.json` was not present, so the local bridge expectation of that path is stale.
4. Tool directories confirmed present:
   - `/srv/tools/planner`
   - `/srv/tools/papers`
   - `/srv/tools/email`

Most important Claude-side directives for Codex/Workspaceboard alignment:

1. Store all secrets in Infisical; do not hardcode credentials.
2. Never send email without explicit user confirmation; show a draft first.
3. Never sign emails as other people; Claude-sent mail must be signed as Claude.
4. Always use the Papers API and `/srv/tools/papers/` scripts; do not edit `/srv/papers/files/` directly.
5. Use Planner for task management; do not edit queue files manually on the Claude side.
6. Push immediately after commit to avoid diverged branches.
7. For dashboard/stats requests, use one background agent rather than noisy shell work in the main conversation.

Integration effect:

- Our local bridge assumptions should stop treating email-address strings like `claude@koval.lan` or `claude@kovaldistillery.com` as the likely SSH user.
- The local bridge should treat `claude` as the verified shell login unless a later server-side source supersedes it.
- The local expected MCP config path needs to be replaced with the actual Claude-side configuration source because `/home/claude/.claude/.mcp.json` is absent.
- Codex-side bridge work should align to the same high-level rules where they are compatible: Infisical-first secret handling, explicit email-send confirmation, API-based Papers operations, and stronger structured task management.

## 2026-04-24 Side-By-Side Organigram Expansion

Decision: keep Codex / Workspaceboard as the primary local operating structure, but expand the organigram so Claude is shown as a parallel department rather than only an abstract bridge/server card.

Concrete Claude-side lanes now identified from live `.205` reads:

1. Planner task management via `/srv/tools/planner/`
2. Papers API document/worklog operations via `/srv/tools/papers/`
3. Mail tools and send-confirmation workflow via `/srv/tools/email/`
4. Autonomous agents and server automation
5. Claude Server Agent family
6. Claude `.205` structure and integration surface

Overlap model to preserve:

- Codex local structure remains authoritative for local TODO/project-hub/Workspaceboard execution.
- Claude task, document, mail, and automation lanes should be visible beside the local roles so similarities and collisions are easier to see.
- Shared contracts should exist only where needed: task-record spine, handoff schema, Infisical-first secret handling, Papers API rule, and explicit send confirmation.
- The systems may live side by side; they do not need to collapse into one control plane before that adds real value.

Scope preserved in this read:

- no secret value recorded in chat or docs;
- no server-side file edits;
- no Planner/Papers/email mutations;
- no deploy/restart/runtime change;
- no commit/push on `.205`.

## 2026-04-24 Remaining Claude Directive Coverage And Real Config Surfaces

Core live directive coverage is now good enough for bridge planning, but not complete enough to claim total Claude-side coverage.

Additional Claude-side docs read after the first `.205` access:

- `/srv/tools/planner/CLAUDE.md`
- `/srv/tools/papers/CLAUDE.md`
- `/srv/tools/email/CLAUDE.md`
- `/srv/agents/CLAUDE.md`
- agent-local summaries read from:
  - `/srv/agents/secretary/CLAUDE.md`
  - `/srv/agents-v2/secretary/CLAUDE.md`
  - `/srv/agents-v2/pm/CLAUDE.md`
  - `/srv/agents-v2/developer/CLAUDE.md`
  - `/srv/agents-v2/tester/CLAUDE.md`
  - `/srv/agents-v2/marketer/CLAUDE.md`
  - `/srv/agents-v2/webmaster/CLAUDE.md`

Highest-value additional rules now extracted:

1. Secretary is a dispatcher and inbox/router surface, not a hidden implementation lane.
2. PM plans work and assessment quality; it should not quietly execute the work itself.
3. Developer executes against the PM packet, stays away from production deploys, and should not push before testing.
4. Tester is intentionally adversarial and should verify rather than assume.
5. Marketer is a department-head planner, not just a copy-writing role.
6. Webmaster is SEO/read-only biased and should not mutate production directly.
7. Claude autonomous agents are first-class and email should flow through the secretary/mail lane instead of arbitrary agents.

Real current Claude-side config surfaces identified from live `.205` reads:

1. `/home/claude/.claude/settings.json`
   - includes hooks;
   - includes a local `mcpServers` object;
   - includes a permissions allow-list with `Bash`.
2. `/home/claude/.claude.json`
   - carries the broader project and MCP registration state;
   - includes top-level project entries for `/home/claude`, `/srv`, `/srv/agents`, `/srv/development/portal`, `/srv/papers/files`, `/srv/scripts/ai-gateway`, `/srv/scripts/screenbox`, and `/srv/sites/koval-distillery.com`;
   - includes top-level MCP keys `mesh`, `rein`, and `screenbox`.
3. `/home/claude/.claude/mcp-needs-auth-cache.json`
   - confirms Claude-side auth-needed entries for Gmail, Google Calendar, and Google Drive.
4. plugin-local `.mcp.json` files and MCP log/cache directories under Claude's plugin/cache paths.

Integration consequence:

- the older bridge expectation of one authoritative `/home/claude/.claude/.mcp.json` file is now definitively obsolete;
- current local bridge docs should treat Claude config as a layered surface across `.claude/settings.json`, `.claude.json`, and plugin/cache state, with auth-needed state tracked separately.

What remains unread enough to matter later:

1. the remaining non-core `/srv/**/CLAUDE.md` files;
2. any agent-local docs beyond the high-value first pass above;
3. the specific Google Drive, Mesh, and AI Gateway docs that likely affect the next bridge slice;
4. any service-local rules that narrow protected-side read/write approval further than the top-level docs.

## 2026-04-24 Deeper Integration Plan From Live Claude State

The correct model is no longer "make Codex behave like Claude." The correct model is "keep the systems side by side, then align the narrow contracts that actually reduce friction."

### Layer 1: Preserve Separate Control Planes

Keep these independent by default:

1. Codex / Workspaceboard local execution
   - local repos;
   - local TODO / HANDOFF / project-hub;
   - visible Workspaceboard sessions.
2. Claude protected-side execution
   - Planner;
   - Papers API tools;
   - Claude mail lane;
   - autonomous agents;
   - `.205` runtime/config.

Reason:

- Claude is tool-first and agent-first on `.205`;
- Codex is repo-first and workspace-first under `/Users/werkstatt`;
- forcing one shared live control plane now would create ownership collisions faster than it adds value.

### Layer 2: Adopt The Claude Progress That Clearly Improves Local Operation

Codex-side changes or policy alignment that now make sense:

1. Stronger task-record spine
   - every real routed task should carry requester, source ref, assigned role, status, priority, deliverable, next update, and approval gate.
2. Explicit send-confirmation behavior
   - keep Frank/Avignon/local communication flows draft-first where approval is required;
   - do not blur "drafted," "ready," and "sent."
3. API-only document mutation rule
   - the Claude-side Papers rule maps to a local rule: do not treat filesystem edits as equivalent to safe record mutation when a structured API/work-record surface exists.
4. Infisical-first default for new shared-secret workflows
   - with exceptions recorded explicitly when Claude-side tools still use local credential storage.
5. Clear role separation
   - planner, implementer, tester, and mail/router roles should stay distinct in the organigram and in routing prompts.

### Layer 3: Shared Bridge Contracts Only Where Needed

The next bridge should be narrow and explicit:

1. Shared task-record projection
   - map local TODO/project-hub/Workspaceboard items into a stable structured packet without creating a shared writable task DB.
2. Single-writer ownership
   - any given task or record needs one active owning system at a time: local Codex side or Claude side.
3. Read-only bridge first
   - do not add a two-way mutation path between Codex and Planner/Papers until ownership, audit, and rollback are explicit.
4. Protected-side packet format
   - when Codex needs Claude-side help, send a bounded packet with source ref, owner, requested action, allowed scope, approval gate, and expected return artifact.
5. Non-secret audit trail
   - keep the local record of what was asked, what system owns it, and what remains blocked.

### Layer 4: Recommended Implementation Sequence

Recommended order from the live Claude state:

1. Finish the Claude-side directive inventory for the next-most-relevant protected surfaces:
   - Google Drive
   - Mesh
   - AI Gateway
2. Replace stale local bridge assumptions
   - stop referencing `/home/claude/.claude/.mcp.json` as authoritative;
   - document the layered config surface instead.
3. Strengthen the local task-record packet
   - make the local projection match the useful Claude task shape without requiring live Papers/Planner writes.
4. Define the first real bridge packet formats
   - task-routing packet;
   - protected-read request packet;
   - completion/blocker return packet.
5. Only after that, implement one narrow protected integration slice
   - likely Papers read-only bridge continuation or the approved Google Drive intake lane, depending on Robert's priority.

### Layer 5: What Still Does Not Have Approval

This plan does not imply approval for:

1. direct Planner mutation from Codex;
2. Papers writes from Codex;
3. protected Claude mail sends from local prompts without the Claude-side send gate;
4. `.205` config/runtime/LaunchAgent mutation;
5. broad OAuth/token work;
6. two-way live sync between Codex and Claude task stores.

## 2026-04-24 User-Supplied Claude MCP Endpoint Note

Robert supplied Claude's owner-facing note that these unified MCP endpoints are now available:

- `papers.koval.lan/mcp`
- `mesh.koval.lan/mcp`
- `screenbox.koval.lan/mcp`
- `rein.koval.lan/mcp`

Robert also supplied Claude's Codex config/access packet reference:

- `https://papers.koval.lan/b46ee853-96aa-4181-a6c2-a947517df78f`

Current handling:

- treat this as fresh non-secret integration input from Robert until read/verified against the protected-side packet or approved local configuration path;
- do not assume current local Codex runtime is already wired to these endpoints;
- use this note as the next source packet for MCP-side bridge planning.

## 2026-04-23 Robert Access-Packet Approval

Source Message-ID: `<CAAtX44aMxx6qRPNu6NUw5WmfSmQh=KqW2pAcAwoepqzkWOoTDA@mail.gmail.com>`

Frank direct-owner intake treated Robert's note as approval to send the narrowest next-step MI / Papers / Mesh bridge packet, not as approval for live auth, protected reads, or `.205` work.

Concrete handling:

- Visible AI Workspace route `2894c746` / `Claude MI Papers Mesh access packet` was created and prompt delivery returned `delivered=true`.
- Frank drafted the Claude-facing packet at `frank/drafts/claude-mi-papers-mesh-access-instructions-2026-04-23.txt`.
- The packet asks Claude for:
  - the exact MI/Papers access or session path Codex/Frank should use next;
  - the approved initial Papers scopes / collections / document IDs if body-level reads are intended;
  - the exact Mesh / Agent Memory / other `.205` read-only endpoints, MCP surfaces, or integration targets to wire next;
  - any remaining non-secret configuration or approval-boundary details still needed from Claude's side.

What this approval changed:

- The next safe action is no longer "wait for approval to ask."
- The next safe action is now "send the narrow protected-side access packet and wait for the implementation-oriented reply."

What this approval did not change:

- no `.205` direct access;
- no MI/Papers auth or body-level reads;
- no OAuth/token/credential work;
- no MCP/runtime/deploy change;
- no Portal/CRM/OPS mutation;
- no external-sensitive send beyond the approved internal packet.

## 2026-04-24 Robert Follow-Up: Make The Question Explicit

Source Message-ID: `<CAAtX44Y15n-eHNaKF66rwAeUBjw5rGo9A+XzWi59KbRDQ_VUTQ@mail.gmail.com>`

Robert's follow-up made clear that the prior Frank closeout described routing work but did not ask the concrete question he needed to answer.

Concrete correction:

- Frank kept the existing active route `2894c746` / `Claude MI Papers Mesh access packet` rather than creating a duplicate worker.
- The Robert-facing reply was rewritten as a direct decision request instead of a status summary.
- The concrete question is now: should Frank send Claude the narrow access-packet request now, limited to the exact MI/Papers access path, the initial approved Papers body-read scope or document IDs if any, and the Mesh / Agent Memory read-only surfaces to wire next?

What this clarification changed:

- This thread now has one explicit yes/no next step for Robert.
- The integration lane records that a routing summary alone is not sufficient closeout for this source; the owner-facing reply must carry the actual decision request.

What this clarification did not change:

- no Claude send yet;
- no `.205` direct access;
- no MI/Papers auth or body-level reads;
- no OAuth/token/credential work;
- no MCP/runtime/deploy change;
- no Portal/CRM/OPS mutation.

## Robert Request

Robert wants Codex and Claude integrated better. The immediate concern is that Codex still produces Markdown/TODO/project-hub records rather than first-class Papers/MI work records. Requested starting actions:

- Add Codex and Claude to the organigram.
- Add Claude agents and `.205` structure.
- Ask Codex where to improve and what to implement next.
- Write a plan, have Frank email it, and record it.
- Add follow-up tasks for Portal account/contact summaries, better directives, automation suggestions, OAuth for Frank/Avignon/Macee, national outreach, active Workspaceboard/MI registration, and a Codex Integration Manager role.

## Current Diagnosis

Codex is effective at local execution because it can edit files, inspect git worktrees, run tests, drive browser automation, and update Workspaceboard/TODO/project-hub records. The weakness is that these durable records are mostly Markdown. Markdown is useful for local audit and handoff, but it is not enough for shared agent operation because Papers/MI cannot reliably treat every Markdown note as an active work object with owner, status, due date, source, permissions, and single-writer state.

Claude is useful as server-side analysis and orchestration support on `.205`, but it must not be allowed to collide with local Codex work. The bridge needs explicit contracts:

- which side owns the work record at any moment;
- what metadata is safe to share;
- which system is read-only versus writable;
- which approval gates apply before `.205`, MI, Papers, OAuth, MCP, mailbox, or production surfaces are touched.

## Codex Recommendation

Implement a read-only work-record projection before any shared write path. Do not replace Markdown immediately. Instead, use Markdown/TODO/project-hub/Workspaceboard as current source material and project selected fields into a structured, MI/Papers-ready shape:

- title;
- owner role;
- source workspace;
- source record path;
- status;
- next action;
- due date when present;
- approval gate;
- single-writer owner;
- related agent roles;
- safe public/internal summary;
- blocked-by field.

This gives MI/Papers a structure to consume without letting Codex or Claude write live shared records prematurely.

## Claude Task-Record Pattern To Adopt

Robert supplied a current Claude response pattern from `ref:2379`:

- Claude created task `#1361`.
- The response named the requester, Sonat.
- It listed the requested changes as concrete bullets.
- It assigned the work to a specific agent, `Marketing Director agent`.
- It marked priority as high.
- It promised an update when revised images are ready.
- It included the source reference `ref:2379`.

This is cleaner than a plain Markdown note because the response carries a task id, owner, priority, action list, status/update promise, and reference. Codex should converge on the same task-record spine. For every routed AI task, the durable projection should include:

- Portal/OPS task id when available, otherwise a local stable task id;
- source ref or email/message id;
- requester;
- assigned agent/role;
- priority;
- status;
- concrete deliverable or requested changes;
- next update promise;
- source links or non-secret file refs;
- approval gates;
- single-writer owner.

OPS/Portal task records should remain the preferred operational source when a real task exists. Workspaceboard and project-hub can project/summarize those records; they should not create competing task identities.

## Role And Organigram Updates

Added or registered these role definitions:

- `AI Manager Robert`: Robert's Codex-login control surface for priorities, approvals, and chain-of-command status.
- `AI Manager Dmytro`: technical AI-manager bridge for Codex/Claude sequencing and directive translation under Robert's direction.
- `Codex Integration Manager`: owns cross-agent integration design, directive improvement, automation recommendations, and safe handoff contracts.
- `Codex Local Agent`: represents the local Codex CLI/Workspaceboard/repo/TODO/project-hub work family.
- `Claude Server Agent`: represents Claude-side `.205` agents and their approved handoffs.
- `Claude .205 Structure`: documents MI/Papers/Mesh/Agent Memory/bridge structure without live `.205` mutation.
- `Outreach Communicator`: prepares booking/outreach templates and routes sends through Frank or approved senders.

Workspaceboard organigram source now includes these as visible cards through `worker-organigram.php`. The HTML hierarchy now has an AI Manager row above the human/Task Manager chain, a dedicated bridge row for Claude server/.205 structure, and a support row that includes Codex Integration Manager.

## AI Manager Chain Of Command

Robert's current Codex login is treated as `AI Manager Robert`. Dmytro is represented as `AI Manager Dmytro` for technical bridge sequencing. The status and execution path should be:

1. AI Manager Robert or AI Manager Dmytro queries Task Manager.
2. Task Manager reports board/TODO/project-hub state and routes the task.
3. Support and monitoring roles review gates: Codex Integration Manager, Security Guard, Code and Git Manager, Decision Driver, and Summary Worker.
4. Execution goes to a visible Codex workspace worker or to Claude Bridge Worker / Claude Server Agent through approved non-secret transport.
5. Approval-gated work returns to AI Manager Robert for final decision.

## Implementation Plan

### Phase 1: Role Map And Directive Alignment

Status: started in this pass.

Actions:

- Keep Codex Integration Manager visible in the organigram.
- Add Codex Local Agent, Claude Server Agent, Claude `.205` Structure, and Outreach Communicator.
- Update the operating model so integration work routes through Codex Integration Manager before code, OAuth, Papers, MI, or `.205` changes.
- Record that Workspaceboard role visibility is allowed, but MI/Papers live actor registration requires separate approval.

### Phase 2: No-Write Papers/MI Projection

Next implementable slice.

Actions:

- Define a small JSON work-record schema.
- Include the Claude-style task fields: task id, source ref, requester, assigned role/agent, priority, status, deliverable bullets, next update promise, source links, approval gates, and single-writer owner.
- Build a read-only exporter from AI Workspace TODO/project-hub and Workspaceboard session metadata.
- Include OPS/Portal task ids and links wherever available; use local stable ids only as fallback.
- Include role IDs and source paths, but no secrets, private email bodies, tokens, `.env` values, credentials, or private mailbox content.
- Display the projection in Workspaceboard first.
- Only then decide whether MI/Papers should ingest it.

Approval gates:

- No Papers write.
- No `.205` direct access.
- No MCP exposure.
- No OAuth.
- No Portal/OPS production mutation.

### Phase 3: Codex-Claude Handoff Contract

Actions:

- Create a handoff template with:
  - source refs;
  - owner;
  - single-writer state;
  - allowed reads;
  - disallowed writes;
  - expected output;
  - return contract;
  - approval gates.
- Store handoffs in `ai-bridge` and link them from project-hub.
- Require Claude output to return as analysis until Codex or the target worker verifies it.

### Phase 4: Portal Account/Contact Summary Workflow

Robert requested: when an account already exists in Portal, email a summary of existing accounts/contacts, especially when multiple were supposed to be entered, including links and info.

Recommended owner path:

- `ws ops` or `ws portal` for deterministic account/contact lookup logic.
- Frank for Robert-facing summary email after the lookup output is approved.
- Codex Integration Manager for the directive: avoid duplicate CRM entry; summarize existing records with stable links and non-private metadata.

Approval gates:

- Read-only Portal/CRM path must be approved or already available.
- Do not print private contact details broadly.
- Do not mutate CRM/account/contact data in this slice.

### Phase 5: OAuth And Mailbox Follow-Ups

Robert requested:

- OAuth Frank and Avignon; push as a Monday task.
- OAuth Macee's inbox and derive standard emails for usual bookings for Outreach Communicator.
- Make national outreach an email for Frank for April 27 when Macee leaves.

Recommended treatment:

- These are dated, approval-gated follow-up tasks, not immediate runtime changes.
- Security Guard must review OAuth scope/storage.
- Use least privilege and machine-local token storage.
- Derive templates from sanitized or explicitly approved mailbox examples.
- Frank sends/drafts only under approved sender/audience/copy/timing rules.

### Phase 6: Active Registration Without Interaction

Robert requested active registration of Claude agents in Workspaceboard and Codex in `mi.koval.lan`, while making sure work does not interact accidentally.

Safe order:

1. Register roles in Workspaceboard only. Completed for role docs and organigram source.
2. Add read-only activity metadata that labels Codex and Claude agents but marks writes disabled.
3. Define single-writer locking/ownership per work record.
4. Only after approval, expose a read-only MI/Papers registration.
5. Only after a second approval, enable any write path.

Do not let Codex and Claude both update the same work item until the single-writer field is enforced.

## Immediate Next Build

Build the no-write work-record projection:

- source: TODO/project-hub/Workspaceboard session metadata;
- output: sanitized JSON and Workspaceboard view;
- no `.205` access;
- no Papers write;
- no OAuth;
- no mailbox send;
- no Portal/OPS mutation.

This is the lowest-risk step that moves Codex away from "just Markdown" toward Papers/MI-ready structured records.

## 2026-04-20 Conditional HTTP Access Note

Robert replied on Tue, 21 Apr 2026 00:02:04 +0000 / Mon, 20 Apr 2026 19:02:04 CDT in the existing `Re: Thoughts on our AI workspace setup` thread: Papers access over HTTP is "probably also an option" if the Codex user has access.

Concrete interpretation:

- Treat HTTP-based Papers access as a viable transport option for the already-routed read-only Papers integration path.
- Do not treat this message as approval to start auth work, test live access, probe Papers over HTTP, or touch `.205`.
- Keep the next safe action tied to the existing read-only wrapper decision: name the exact Codex user/service identity, the allowed read-only scopes/collections, and any initial document IDs approved for body-level reads before any live HTTP/MCP check is attempted.

Current gating remains:

- no live Papers writes;
- no `.205` direct access;
- no OAuth/auth setup or token work;
- no MCP exposure change;
- no mailbox/runtime/service/deploy mutation from this note alone.

## Frank Email Brief

Subject: `Codex / Claude integration plan`

Robert,

Codex recommends starting with a read-only work-record projection before any live Papers or MI write path. The issue is not that Markdown is bad; it is that Markdown does not give Codex, Claude, Workspaceboard, MI, and Papers a shared owner/status/single-writer contract. I added the missing role map entries for Codex Integration Manager, Codex Local Agent, Claude Server Agent, Claude `.205` Structure, and Outreach Communicator, and registered them in the Workspaceboard organigram source.

Next implementation slice: build a sanitized no-write JSON projection from TODO/project-hub/Workspaceboard session metadata, display it in Workspaceboard, then decide whether MI/Papers should ingest it. Keep `.205`, Papers writes, OAuth, Portal/CRM mutation, mailbox runtime, and MCP exposure closed until separately approved. Monday follow-ups should cover Frank/Avignon OAuth planning and the Portal existing-account/contact summary workflow. April 27 should carry the Frank national-outreach/Macee handoff task.

Frank

## Durable Robert Input Trace

Source: Robert chat directives in the active Codex Integration Manager task on 2026-04-19.

Status at 2026-04-19 10:12 CDT: Robert's notes were converted into durable action records and routed into visible Workspaceboard sessions. Frank created the dated Outreach records, Security Guard added the OAuth planning checklist, Portal produced the read-only existing-record summary design, and AI-Bridge produced the read-only registration design. All work remains design, planning, or local task-record creation only unless a later explicit approval opens a gated surface.

| Local task id | Robert input / decision | Owner and session | Status | Next step | Approval gates |
| --- | --- | --- | --- | --- | --- |
| `ai-cim-20260419-portal-existing-account-summary` | When a Portal/CRM account already exists, especially when multiple accounts/contacts were supposed to be entered, create a workflow so Frank can send a summary with links and non-private info instead of silently duplicating or stopping. | Portal design worker `ba888628`; replacement dry-run worker `d3f5b188`; Codex Integration Manager session `b66fdade`. | Robert approved fixture-only dry run; replacement worker `d3f5b188` accepted the brief after `ba888628` was no longer visible in the board API. | Produce fixture-only dry-run output from fabricated records and report field/wording adjustments. | No Portal/CRM mutation, no live lookup, no production DB read/write, no private contact details, no email send, no deploy/live pull/restart. |
| `ai-cim-20260419-directive-automation-improvements` | Codex Integration Manager must actively suggest better directives, automation candidates, easier workflow, and take on safe action work instead of only summarizing. | Codex Integration Manager session `b66fdade`; role doc `worker_roles/codex-integration-manager.md`; organigram source `/Users/werkstatt/workspaceboard/worker-organigram.php`. | Verified present in role docs and organigram source. | Keep using this trace format for Robert inputs: source/date, action, owner/session/task id, status, next step, gate. | No hidden implementation; code/auth/runtime work must route to the owning visible worker and matching specialist gate. |
| `ai-cim-20260419-oauth-monday-follow-up` | Frank/Avignon OAuth and Gmail push must remain a Monday 2026-04-20 follow-up; no OAuth before explicit approval. | Security Guard OAuth review worker `71ab6f94`; existing OAuth planning worker `f67d82e4`; Frank TODO Monday row. | Non-secret checklist recorded; parked behind Monday health check. | On 2026-04-20 verify polling health first, then ask Robert for explicit OAuth/PubSub decisions only if still needed. | No OAuth, Google auth, Pub/Sub/IAM, mailbox content read, token/path disclosure, runtime cadence change, deploy/live pull/restart, or external send. |
| `ai-cim-20260419-macee-outreach-templates` | Create a future/security-reviewed Macee inbox task for Outreach Communicator to derive usual-booking email templates. | Frank/Outreach worker `2e9c321b`; Outreach Communicator role doc `worker_roles/outreach-communicator.md`. | Durable Frank record created: `frank-2026-04-19-outreach-macee-inbox-oauth-template-security-review`. | Wait for explicit Robert plus mailbox-owner approval and Security Guard scope/storage review; prefer supplied sanitized examples/export before OAuth. | No Macee OAuth, mailbox content read, credential exposure, external send, Portal/CRM mutation, deploy/live pull/restart. |
| `ai-cim-20260419-national-outreach-20260427` | Create a national outreach email task for Frank for 2026-04-27 when Macee leaves. | Frank/Outreach worker `2e9c321b`. | Durable Frank record created: `frank-2026-04-19-national-outreach-email-macee-leave-2026-04-27`; due 2026-04-27. | Frank prepares or routes the national outreach task brief on 2026-04-27; draft-only if recipient/content/send authority is unclear. | No email send until audience/copy/sender/timing are approved or already covered by a standing workflow. |
| `ai-cim-20260419-active-registration-readonly` | Register Claude agents in Workspaceboard and Codex in `mi.koval.lan` as active while preventing accidental interaction. | AI-Bridge worker `f66bd3cb`; Codex Integration Manager session `b66fdade`. | Read-only design produced in `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-19-read-only-registration-design.md`; worker waiting for approval/input. | Decide whether to proceed with concrete read-only schema design for `registration:workspaceboard:claude:readonly` and `registration:mi:codex:readonly`. | No `.205` access, no MI/Papers write, no MCP exposure change, no OAuth, no Portal/CRM mutation, no mailbox credential/content exposure, no deploy/live pull/restart. |
| `ai-cim-20260419-role-validation` | Verify Codex Integration Manager exists and Workspaceboard organigram includes Codex/Claude/Integration roles including Outreach Communicator. | Codex Integration Manager session `b66fdade`. | Verified from local source. | Keep role visible; route a Workspaceboard fix only if later evidence shows live board drift from source. | No Workspaceboard runtime/restart/deploy; source validation only. |

Evidence captured:

- `worker_roles/codex-integration-manager.md` exists and assigns cross-system design, directive improvement, automation recommendations, and safe handoff contracts to Codex Integration Manager.
- `worker_roles/outreach-communicator.md` exists and defines approved booking/outreach template preparation with OAuth and external-send gates.
- `/Users/werkstatt/workspaceboard/worker-organigram.php` includes `Codex Integration Manager`, `Outreach Communicator`, `Codex Local Agent`, `Claude Server Agent`, `Claude .205 Structure`, `AI Manager Robert`, and `AI Manager Dmytro`.
- Workspaceboard API accepted and started worker sessions `ba888628`, `2e9c321b`, `f66bd3cb`, and `71ab6f94`; the prompt-delivery checks reported the task briefs landed in each session transcript.
- The existing Integration Manager session is `b66fdade`. A follow-up coordination message was attempted there, but the board API did not show it in the transcript after delivery; this project-hub trace is therefore the canonical durable coordination record for the 2026-04-19 routing pass.
- Frank worker `2e9c321b` updated `frank/TODO.md` and `frank/HANDOFF.md` with the two dated local task records.
- Security Guard worker `71ab6f94` updated `project_hub/issues/2026-04-18-frank-avignon-gmail-push-plan.md`, `HANDOFF.md`, `TODO.md`, and `project_hub/INDEX.md` with the planning-only OAuth checklist.
- Portal worker `ba888628` produced a read-only existing-record summary design in the Portal workspace handoff.
- Robert approved a fixture-only dry run for the Portal existing-account/contact summary format in Codex chat on 2026-04-19. Original worker `ba888628` was no longer visible in the board API, so replacement worker `d3f5b188` was created and accepted the dry-run brief.
- AI-Bridge worker `f66bd3cb` produced `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-19-read-only-registration-design.md`.

## Concrete Bridge Task Register

Source: Robert directive at 2026-04-19 12:13 CDT: convert bridge plan into concrete tasks and visible worker/session routes.

Register status: active. These task records are the durable source for the Codex/Claude/Papers/MI bridge until they are superseded by real OPS/Portal records or an approved shared work-record system. They preserve the closed gates: no `.205` writes, OAuth, Papers/MI writes, Portal/CRM mutation, MCP exposure, deploy/live pull, service restart, mailbox credential exposure, or credential/private-mailbox content exposure without separate approval.

Read-only actionability rule, added from Robert's 2026-04-19 directive: read-only does not mean passive. Every read-only audit, design, or fixture packet must end with owner, workspace, status, next safe action, approval boundary, and either a visible worker/session route or a dated follow-up/request task. If the next step is blocked by missing source/export/approval, create a specific request task naming the needed source/export/approval. If implementation is safe but not approved, create an implementation-ready task brief with closed gates listed.

## 2026-04-20 Approval / Dedupe Attachment

Source Message-ID: `<CAAtX44bSgMHtL+Y96sCn+g63U7FLpzbYQ0fCCm48Gc4vtA1QUA@mail.gmail.com>`; classification `tracked-primary-instruction`; source subject `Re: Blocker 4: Claude and AI Bridge context`; from/date Robert Birnecker `<robert@kovaldistillery.com>` / Mon, 20 Apr 2026 09:33:19 -0700.

Robert wrote: "Hi, I think I approved a plan already." This source is attached to the existing integration task/dedupe state and does not create a duplicate work item.

Additional implementation approval source Message-ID: `<CAAtX44ZYxUpzOLz1UXNUT-C8CnQSXxGy0hge3ojxW+f3PwBHWw@mail.gmail.com>`; classification `tracked-primary-instruction`; source subject `Re: AI bridge status: Claude, integration state, next 5 steps`; from/date Robert Birnecker `<robert@kovaldistillery.com>` / Mon, 20 Apr 2026 10:29:27 -0700. Robert wrote: "Great. Let's add to plan and implement." This source attaches to the same no-write/read-only bridge plan and does not create a duplicate work item.

The already-approved plan, as reflected in this register, is:

- use a no-write/read-only work-record projection before any shared write path;
- use AI Workspace TODO, project-hub, and Workspaceboard metadata as the current source material;
- use `/Users/werkstatt/ai-bridge/bridge/schemas/work-record.schema.json`, `/Users/werkstatt/ai-bridge/bridge/templates/codex-claude-handoff.md`, `/Users/werkstatt/ai-bridge/bridge/schemas/readonly-registration-records.json`, and `/Users/werkstatt/ai-bridge/bridge/memory/work-record-projection-source-map.json` as the local contract/artifact bundle;
- route Workspaceboard exporter/view implementation only after Code/Git Manager resolves file ownership, endpoint shape, non-canonical projection ID policy, and dirty-worktree ownership;
- keep live `.205`, Papers/MI, OAuth, Portal/CRM, mailbox credential/content, MCP exposure, deploy/live pull, service restart, and external email send gates closed until separately approved.

Safe internal implementation completed from the new approval: AI-Bridge added `/Users/werkstatt/ai-bridge/bridge/memory/work-record-projection-source-map.json` and `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-20-approved-next-steps-implementation.md`. These are local non-secret planning/source-map artifacts only.

Current safe implementation branches: review the source-only Workspaceboard exporter output and decide whether to approve a separate runtime deploy/restart/live-publication slice or a Workspaceboard view; review the 2026-04-22 source-only Papers read-only wrapper implementation before any commit/push/runtime wiring. The exporter code implementation has been committed and pushed, but it has not been installed into the running LaunchAgent/runtime copy.

## 2026-04-22 Papers API Access Approval Intake

Source Message-ID: `<CAAtX44YuOqo8n3pjaX7oSeUXHZ22E=__SQe6XZbgvHa=QmwmgA@mail.gmail.com>`; dedupe key `frank-direct-primary-CAAtX44YuOqo8n3pjaX7oSeUXHZ22E-SQe6XZbgvHa-QmwmgA-mail-gmail-com`; owner/source Robert via Frank direct-owner intake; subject `Re: AI bridge / Papers status`.

Robert supplied the Papers pointer `https://papers.koval.lan/e4bd10fa-b121-435f-b5c4-d5d2ec74948c`, summarized as `Papers API Access for Codex/Frank Runtime`, task `#1372`, status `Active`, date `2026-04-20`. This record was not opened or read by this worker; only the non-secret metadata supplied in the routing prompt was recorded.

Decision: this satisfies the prior approval gate only for the next source-only Workspaceboard implementation route for a deny-by-default read-only Papers wrapper. It is not approval for credentials/OAuth, token storage, Papers mutation tools, `.205` access, MCP config/runtime/LaunchAgent changes, deploy/live pull, Portal/CRM/OPS mutation, external-sensitive replies, private Papers body reads, or broad document/collection access.

Exact next implementation route now allowed: create or reuse a visible `workspaceboard` worker, with Security Guard review, to implement source-only wrapper code/tests using the existing context from Workspaceboard scoping worker `c6421ac1`, Security Guard `c2e66c43`, Code/Git Manager `9a4787cd`, wrapper design worker `778ef252`, AI-Bridge worker `82027764`, and Frank status route `f0ab7450`. The implementation must preserve the Security Guard requirements: fixed endpoint, server-side allow policy, hard denial of `create_document`, `update_document`, `delete_document`, and `set_key_document`, audit logging, rate/volume limits, secret redaction, and default-deny behavior. Until Robert names initial allowed scopes/collections/document IDs, the wrapper should only support metadata/tool-schema or explicitly named non-body probes.

Remaining decisions/approval gates: initial allowed Papers scopes/collections/document IDs for body-level reads; separate runtime deploy/restart/live-publication approval; any MCP config/runtime/LaunchAgent path; any auth/token/storage path; any `.205` access; and any Papers/MI write path.

## 2026-04-22 Papers Option B Source Slice

Source Message-ID: `<CAAtX44aEoCLf0Mfc2xv-xuGQ0yc4dkn=n3XKQuLOEG_6po6nrg@mail.gmail.com>`; dedupe key `frank-direct-primary-CAAtX44aEoCLf0Mfc2xv-xuGQ0yc4dkn-n3XKQuLOEG-6po6nrg-mail-gmail-com`; visible Workspaceboard route `cb518c23` / `Papers read-only wrapper source slice`.

Result: the source-only deny-by-default wrapper is implemented in `/Users/werkstatt/workspaceboard/server/papers-readonly-wrapper.js` with focused tests in `/Users/werkstatt/workspaceboard/server/test/papers-readonly-wrapper.test.js`. The wrapper exposes fixed endpoint metadata, approved read-only tool schemas, hard-denies `create_document`, `update_document`, `delete_document`, and `set_key_document`, default-denies unapproved tools, returns metadata-only document list/get records, redacts audit values and source host/root metadata, and applies rate/volume limits.

Verification passed: `node --check server/papers-readonly-wrapper.js`; `node --test server/test/papers-readonly-wrapper.test.js` passed 9/9; `npm test` in `/Users/werkstatt/workspaceboard/server` passed 37/37.

Not done: no live Papers body read, credentials/OAuth/auth/token work, `.205`, MCP config/runtime/LaunchAgent/deploy/restart/live-pull, Papers/MI write, Portal/CRM/OPS mutation, commit, push, reset, clean, or unrelated dirty-file cleanup. Remaining gates: Code/Git review before commit/push, separate approval before runtime install/restart/deploy, and separate approval for any auth/token/session storage, `.205`, MCP config, live Papers body reads, or Papers/MI writes.

| Task id | Owner / workspace | Status | Next action | Approval boundary | Source pointer |
| --- | --- | --- | --- | --- | --- |
| `bridge-20260419-work-record-schema` | Codex Integration Manager + AI-Bridge worker / `ai-bridge`; visible session `82027764` | Local contract ready; 2026-04-20 source-map implementation added. | Use `bridge/schemas/work-record.schema.json` plus `bridge/memory/work-record-projection-source-map.json` as the contract for exporter/view planning. | Schema/docs/source-map only; no `.205`, MI/Papers write, MCP exposure, OAuth, Portal/CRM mutation, mailbox content read, deploy/live pull, service restart, or credential exposure. | This note, sections `Claude Task-Record Pattern To Adopt`, `Phase 2`, and `Immediate Next Build`; AI-Bridge session `82027764`; approval source `<CAAtX44ZYxUpzOLz1UXNUT-C8CnQSXxGy0hge3ojxW+f3PwBHWw@mail.gmail.com>`. |
| `bridge-20260419-readonly-exporter-plan` | Codex Integration Manager + Code/Git Manager / `workspaceboard`; visible scoping session `657f4780` | Scoping complete; specific file-ownership request created. | Use session `657f4780` output as the implementation-ready brief and resolve `bridge-20260419-workspaceboard-exporter-file-ownership-request` before opening an implementation worker. | Planning/docs/scoping only until Code/Git Manager assigns file ownership; no dirty-file discard, no pull over dirty trees, no deploy/live pull, no service restart, no runtime change, no shared-system write. | This note, `Phase 2: No-Write Papers/MI Projection`; AI-Bridge schema `bridge/schemas/work-record.schema.json`; Workspaceboard scoping session `657f4780`. |
| `bridge-20260419-workspaceboard-exporter-implementation-brief` | Code/Git Manager + Workspaceboard worker / `workspaceboard` | Source implementation complete; runtime publication not done. | Review commit `74fd65f` and decide whether to approve a separate deploy/restart/live-publication slice or a Workspaceboard view for the JSON output. | Source commit/push only; no runtime change, deploy/live pull, service restart, MCP change, MI/Papers write, `.205` access, OAuth, Portal/CRM mutation, or credential exposure. | Derived from `bridge-20260419-readonly-exporter-plan` and Robert's read-only actionability directive. |
| `bridge-20260419-workspaceboard-exporter-file-ownership-request` | Code/Git Manager + Workspaceboard owner / `workspaceboard` | Closed for source implementation by commit `74fd65f` on 2026-04-20. | Source now adds `server/bridge-work-record-exporter.js`, touches `server/index.js` only for `GET /api/bridge/work-records`, and adds focused tests. Non-canonical discovered sources go to `unmapped_sources[]` with deterministic `projection_ref`; no parallel task IDs are minted. | No dirty-file discard, git pull over dirty tree, deploy/live pull, service restart, runtime reinstall, MCP exposure/config change, `.205`, OAuth, Papers/MI write/read, Portal/CRM mutation, mailbox/private-body access, credential exposure, or external send. | Workspaceboard scoping session `657f4780`; Code/Git ownership session `fc01a91d`; commit `74fd65f`; derived from `bridge-20260419-readonly-exporter-plan`. |
| `bridge-20260419-codex-claude-handoff-template` | AI-Bridge worker / `ai-bridge`; visible session `82027764` | Review-ready from no-write session output. | Review `bridge/templates/codex-claude-handoff.md`; use it for future Claude roundtrip tasks after source verification. | Template/docs only; Claude output remains analysis until verified by Codex or target worker; no `.205`, MCP, OAuth, Papers/MI write, Portal/CRM mutation, deploy/live pull, or service restart. | This note, `Phase 3: Codex-Claude Handoff Contract`; AI-Bridge session `82027764`. |
| `bridge-20260419-claude-task-logging-roundtrip` | Frank + Codex Integration Manager / `frank`, `ai` | Waiting on Claude response. | When Claude replies to Frank's corrected bridge note, map Claude's task id/status fields into this register or a successor task record and route any implementable work to a visible worker. | No mailbox credential/private body exposure; no external resend unless separately approved; no `.205`, Papers/MI write, Portal/CRM mutation, MCP exposure, deploy/live pull, or service restart. | Frank task `frank-2026-claude-codex-organigram-work-record-bridge-cc-follow-up`; Message-ID `<177661269639.29604.14362403569930801531@kovaldistillery.com>`. |
| `bridge-20260419-claude-task-logging-response-request` | Frank / `frank`; visible session `86f1b736` | Frank nudge sent; waiting on Claude response, not Robert. | Watch for Claude's reply; when it arrives, map task id/source ref/owner/status/next action/approval gates into this register or successor task records. | No mailbox credential/private body exposure; no broad resend; no external-sensitive content; no `.205`, Papers/MI write, MCP exposure, deploy/live pull, service restart, or credential exposure. | Derived from `bridge-20260419-claude-task-logging-roundtrip`; original Frank Message-ID `<177661269639.29604.14362403569930801531@kovaldistillery.com>`; nudge Message-ID `<177661959602.5921.17895643980954120746@kovaldistillery.com>`; nudge session `86f1b736`. |
| `bridge-20260419-portal-existing-summary` | Portal design + Frank summary path / `portal`, `frank` | Fixture-only dry run completed or parked for review; live path blocked. | Use the fixture output to create a live-read approval request and implementation-ready brief rather than leaving the design passive. | No Portal/CRM mutation, no production DB write, no private contact detail broadcast, no email send, no deploy/live pull/restart. | Task `ai-cim-20260419-portal-existing-account-summary`; sessions `ba888628`, `d3f5b188`; `Phase 4`. |
| `bridge-20260419-portal-live-lookup-approval-request` | Portal owner + Frank / `portal`, `frank` | Specific approval request task. | Ask Robert/source owner to approve or reject a read-only Portal/CRM lookup path, allowed account/contact fields, link format, recipient/copy behavior for Frank's summary, and whether fixture wording is acceptable. | Until approved: no live Portal/CRM read, no mutation, no private details in chat/email, no send, no deploy/live pull/restart. | Derived from read-only Portal summary packet and Robert's read-only actionability directive. |
| `bridge-20260420-papers-readonly-wrapper-approval` | Workspaceboard + Security Guard / `workspaceboard`, `ai` | Source-only wrapper code/tests complete in route `cb518c23`; live/body/auth/runtime gates remain closed. | Route Code/Git review for `server/papers-readonly-wrapper.js` and `server/test/papers-readonly-wrapper.test.js`; keep body-level reads to explicitly named scopes/collections/document IDs only after separate approval. | No Papers writes or mutation tools, no credential/auth/token handling, no `.205` access, no MCP config/runtime/LaunchAgent change, no deploy/live pull/restart, no Portal/CRM/OPS mutation, no private mailbox-body exposure, no broad/private Papers body reads, no external-sensitive reply. | Source/access blocker; Papers scoping sessions `c6421ac1`, `778ef252`; Security Guard `c2e66c43`; Code/Git Manager `9a4787cd`; approval source `<CAAtX44YuOqo8n3pjaX7oSeUXHZ22E=__SQe6XZbgvHa=QmwmgA@mail.gmail.com>`; option B source `<CAAtX44aEoCLf0Mfc2xv-xuGQ0yc4dkn=n3XKQuLOEG_6po6nrg@mail.gmail.com>`; route `cb518c23`; Papers pointer `https://papers.koval.lan/e4bd10fa-b121-435f-b5c4-d5d2ec74948c` / task `#1372`. |

| `bridge-20260419-security-205-papers-access-note` | Security Guard / `ai`; visible session `99244c6e` | Closed as security decision record. | If `.205`/Papers access is still needed, ask Robert/Security to approve a separate workflow that names host, identity, allowed scope, secure credential channel, audit logging, recovery path, and exact execution gate before access. | No `.private` read, credential/token/key/password inspection or printing, SSH, `.205` access, live Papers/MI access, MCP config change, AGENTS operational access-note, auth change, service/runtime change, deploy/live pull, or destructive action. | Frank direct-email source Message-ID `<CAAtX44aR35SbgE+bSb7w_KKqXPvZ8-xt7xM8waJUzoRLV0gpqg@mail.gmail.com>`; dedupe key `frank-direct-email:CAAtX44aR35SbgE+bSb7w_KKqXPvZ8-xt7xM8waJUzoRLV0gpqg:205-papers-access-note`; `AGENTS.md` non-secret access-documentation rule. |
| `bridge-20260420-frank-avignon-oauth-health` | Security Guard + Frank/Avignon / `ai`, `frank`, `avignon` | Dated follow-up for Monday 2026-04-20. | Verify polling health first; only then decide whether Gmail API push/OAuth is still needed. | No OAuth, Google auth, Pub/Sub/IAM, mailbox content read, token/path disclosure, runtime cadence change, deploy/live pull/restart, or external send before explicit approval. | Task `ai-cim-20260419-oauth-monday-follow-up`; project log `2026-04-18-frank-avignon-gmail-push-plan.md`. |
| `bridge-20260427-macee-outreach-template-review` | Frank/Outreach Communicator / `frank`, future `ops` if approved | Dated follow-up for 2026-04-27 unless Robert approves earlier sanitized-source review. | Review whether supplied sanitized examples or approved mailbox-owner/OAuth path exists for Macee usual-booking templates; create a worker only when source access is approved. | No Macee OAuth, mailbox content read, credential exposure, external send, Portal/CRM mutation, deploy/live pull/restart. | Task `ai-cim-20260419-macee-outreach-templates`; Frank task `frank-2026-04-19-outreach-macee-inbox-oauth-template-security-review`. |
| `bridge-20260427-national-outreach-brief` | Frank/Outreach Communicator / `frank` | Dated follow-up for 2026-04-27. | Prepare or route the national outreach task brief; draft-only if recipient/content/send authority is unclear. | No email send until audience/copy/sender/timing are approved or covered by standing workflow. | Task `ai-cim-20260419-national-outreach-20260427`; Frank task `frank-2026-04-19-national-outreach-email-macee-leave-2026-04-27`. |
| `bridge-20260419-readonly-registration-schema` | AI-Bridge worker + Codex Integration Manager / `ai-bridge`, `ai`; visible session `82027764` | Review-ready from no-write session output; live registration blocked. | Review `bridge/schemas/readonly-registration-records.json`, then route Workspaceboard/MI publication only if Robert separately approves a live read-only path. | No `.205`, MI/Papers write, MCP exposure/config change, OAuth, Portal/CRM mutation, mailbox credential/content exposure, deploy/live pull/restart. | Task `ai-cim-20260419-active-registration-readonly`; trace `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-19-read-only-registration-design.md`; AI-Bridge session `82027764`. |
| `bridge-20260419-role-validation` | Codex Integration Manager / `ai`, `workspaceboard` | Closed for source validation; monitor for live drift. | Reopen only if Workspaceboard live organigram drifts from source or role docs lose the AI Manager/Codex/Claude entries. | No Workspaceboard runtime/restart/deploy or live mutation from this closed validation task. | Task `ai-cim-20260419-role-validation`; `Role And Organigram Updates`. |

## 2026-04-22 Metadata-Only Connectivity Check

Robert asked Frank to read the Papers record and try to connect. Frank did not open or read the Papers document body. Metadata-only `GET` checks to `https://papers.koval.lan/mcp` and the supplied Papers task URL both reached the Papers host and returned `HTTP/2 307` redirects to `https://mi.koval.lan/login?...` with zero response body bytes.

Result: Papers is reachable, but the current Frank/Codex path is stopped at MI login. The source-only wrapper slice is now implemented; body-level reads still need the approved Codex/Frank access identity and exact allowed scopes, collections, or document IDs. No OAuth, token, credential, `.205`, Papers body read/write, MCP config/runtime, deploy, Portal/CRM/OPS mutation, or external-sensitive send occurred.

Visible worker/session routing at 2026-04-19 12:13 CDT:

- Reused Codex Integration Manager session `b66fdade` as the coordinating session for this task register and future bridge-status conversion; prompt delivery was verified and the session entered `working`.
- Created AI-Bridge worker session `82027764`, `AI Bridge no-write task-record schema and handoff templates`, for the currently safe no-write bundle: `bridge-20260419-work-record-schema`, `bridge-20260419-codex-claude-handoff-template`, and `bridge-20260419-readonly-registration-schema`. Prompt delivery was verified and the session entered `working`.
- Created Workspaceboard scoping session `657f4780`, `Workspaceboard Code/Git scope for bridge readonly exporter`, for the read-only Code/Git/file-ownership pass on `bridge-20260419-readonly-exporter-plan`. Prompt delivery was verified. The session produced an implementation-ready brief and specific request task `bridge-20260419-workspaceboard-exporter-file-ownership-request`.
- Frank visible session `86f1b736`, `Frank nudge Claude on bridge and Avignon context`, sent the specific Claude response request for `bridge-20260419-claude-task-logging-response-request`; the task is now waiting on Claude response rather than Robert input.
- Defer Workspaceboard exporter/view code implementation until `bridge-20260419-workspaceboard-exporter-file-ownership-request` is resolved, Code/Git Manager assigns file ownership against the dirty worktrees, and Robert separately approves any code/runtime step.
- 2026-04-20 update: `bridge-20260419-workspaceboard-exporter-file-ownership-request` is resolved for ownership/scoping only. File ownership recommendation is `server/bridge-work-record-exporter.js` plus a minimal `server/index.js` route for `GET /api/bridge/work-records`; keep `server/digital-office-index.js` and current dirty Workspaceboard UI/auth/nav/organigram/TODO/HANDOFF/backup files out of scope. Workspaceboard exporter implementation still requires separate code approval and normal verification/commit/deploy gates.
- Keep OAuth, Macee mailbox/template, national outreach, Portal live lookup, Papers/MI ingestion, and Claude roundtrip items as dated or response-blocked task records rather than freeform notes.

## 2026-04-19 Open TODO Worker Push

Source: Robert chat directive on 2026-04-19 to work faster across the `17` open TODO items and open at least `10` more workers.

Action taken: created or advanced `12` additional visible workers, all bounded to no-write/read-only/planning or fixture-only scopes unless separately approved.

| Session | Workspace | Task | Status seen after launch | Gate |
| --- | --- | --- | --- | --- |
| `b1f985fa` | `ai` | AI source/access blockers no-write status sweep | finished / review-ready | no credentials, mailbox bodies, source APIs, production DB, live exports, OAuth, Papers/MI writes, `.205`, deploy/live pull/restart, or external sends |
| `91aa5377` | `ai` | AI sales analytics decisions no-write packet | blocked / waiting-on-external after producing decision packet | no saved_reports writes/runs, production data mutation, CRM/account/tracking changes, deploy, external analytics writes, or credentials |
| `0efd199e` | `ops` | OPS outreach Connecteam final read-only packet prep | launched / needs-input | no `--apply`, decommission, OPS/Portal/CRM mutation, Google sync mutation, notification send, auth/canonical-rule change, deploy, push, live pull, or source task closure |
| `cd9281a6` | `frank` | Frank Monday polling health prep no-auth | launched / needs-input | no OAuth, Google auth, mailbox content read, credential/token access, LaunchAgent/runtime/cadence change, deploy/restart, or email send |
| `1bf2890e` | `frank` | Frank Mac mini hard-server-mode Monday note prep | finished / review-ready | no service migration, logout, LaunchDaemon/LaunchAgent change, restart, deploy/live pull, OAuth, mailbox read, credential access, or Workspaceboard mutation |
| `328c03ee` | `frank` | Outreach Communicator Macee no-access template brief | finished / review-ready | no Macee OAuth, mailbox login/search/read/export, private examples, credential exposure, external send, Portal/CRM mutation, or runtime change |
| `a032c582` | `frank` | Frank national outreach April 27 draft brief prep | launched / needs-input | no email send, mailbox read/file, Portal/CRM mutation, credentials, OAuth, deploy/live pull, or restart |
| `66c61d55` | `workspaceboard` | Workspaceboard page consolidation design only | finished / review-ready | no code implementation, runtime reinstall, deploy/live pull, service restart, auth/session change, or page removal |
| `9d707523` | `bid` | BID import finance CLI maintenance gate design | launched / needs-input | no DB writes, imports, scrapers, live pulls, deploys, pushes, delete/move, emails, credential access, production mutation, or `.205` |
| `6be8c383` | `bid` | BID finance action-report owner decision packet | launched / needs-input | no finance credentials, QuickBooks, live/current package reads, imports, scrapers, emails, deploys, commits/pushes, production writes, or `.205` |
| `657a7024` | `bid` | BID payroll reimbursement owner decision packet | finished / review-ready | no payroll credentials, live Portal/payroll access, email send, imports, production validation, deploy, commit/push, or production writes |
| `dd9187e4` | `avignon` | Avignon CRM recovery blocker action-plan review | launched / needs-input | no private body/contact-field printing, phpList, broad import, Portal/CRM mutation, mailbox filing, credential work, destructive change, or external-sensitive send |

## 2026-04-19 Directive Revision

Source: Robert chat directive on 2026-04-19: review the directives again, improve the plan, and make the whole worker/TODO/fan-out flow more fluid.

Observed friction:

- Robert chat instructions can become ephemeral if they are not converted immediately into task-record rows and project-hub traces.
- Short-lived workers can disappear from the board API after producing files or useful output.
- Opening many workers is not the same as completion; the batch needs prompt verification, status sweeps, safe nudges, blocker recording, and Code/Git closeout.
- Waiting states were sometimes treated as parking instead of a cue to push the safe next action.
- Closeout ownership was unclear for doc/planning workers that changed git-backed files but did not produce application code.

Directive updates made:

- `AGENTS.md`: added the Fast fan-out control-loop rule, Orphaned-output rule, and Codex Integration Manager fluidity rule.
- `worker_roles/codex-integration-manager.md`: expanded responsibilities and outputs to include fan-out batch traces, closeout maps, durable control-loop rules, and orphaned-output recovery.
- `worker_roles/task-manager-polier.md`: added fast fan-out and orphaned-output operating references for Task Manager.
- `worker_roles/decision-driver.md`: clarified that waiting workers in fan-out should receive one safe bounded continuation or an internal route before surfacing Robert decisions.
- `worker_roles/operating-model.md`: updated the Task Manager and Codex Integration Manager startup prompts with the fan-out, sweep, orphaned-output recovery, and directive-revision expectations.

Next safe automation candidate:

- Workspaceboard should eventually expose a first-class fan-out batch object that tracks source/date, launched worker IDs, prompt-delivery state, latest status, changed files, Code/Git closeout route, and real blockers. That would reduce manual API/status sweeps and make the open-worker pattern easier to audit. This is a design recommendation only; no Workspaceboard runtime/code change was performed in this directive pass.


## Open Gates

- No `.205` live access or mutation was performed.
- No MI/Papers registration or write was performed.
- No OAuth work was performed.
- No Portal/CRM lookup or mutation was performed.
- No mailbox runtime change was performed.
- Frank email send depends on an approved/safe send path being available from the active Frank host; if unavailable, use the email brief above as the draft.
