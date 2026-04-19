# Codex / Claude / Papers Integration Plan

- Master ID: `AI-INC-20260419-CODEX-CLAUDE-PAPERS-01`
- Date: 2026-04-19
- Owner: AI Workspace / Codex Integration Manager
- Repos/surfaces: `ai_workspace`, `workspaceboard`, future `ai-bridge`, future MI/Papers/.205 surfaces
- Status: planning and role-map registration started; live `.205`, MI, Papers, OAuth, Portal data, and mailbox runtime changes are not started

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

## Frank Email Brief

Subject: `Codex / Claude integration plan`

Robert,

Codex recommends starting with a read-only work-record projection before any live Papers or MI write path. The issue is not that Markdown is bad; it is that Markdown does not give Codex, Claude, Workspaceboard, MI, and Papers a shared owner/status/single-writer contract. I added the missing role map entries for Codex Integration Manager, Codex Local Agent, Claude Server Agent, Claude `.205` Structure, and Outreach Communicator, and registered them in the Workspaceboard organigram source.

Next implementation slice: build a sanitized no-write JSON projection from TODO/project-hub/Workspaceboard session metadata, display it in Workspaceboard, then decide whether MI/Papers should ingest it. Keep `.205`, Papers writes, OAuth, Portal/CRM mutation, mailbox runtime, and MCP exposure closed until separately approved. Monday follow-ups should cover Frank/Avignon OAuth planning and the Portal existing-account/contact summary workflow. April 27 should carry the Frank national-outreach/Macee handoff task.

Frank

## Open Gates

- No `.205` live access or mutation was performed.
- No MI/Papers registration or write was performed.
- No OAuth work was performed.
- No Portal/CRM lookup or mutation was performed.
- No mailbox runtime change was performed.
- Frank email send depends on an approved/safe send path being available from the active Frank host; if unavailable, use the email brief above as the draft.
