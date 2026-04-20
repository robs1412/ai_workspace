# Codex / Claude / Papers Integration Plan

- Master ID: `AI-INC-20260419-CODEX-CLAUDE-PAPERS-01`
- Date: 2026-04-19
- Owner: AI Workspace / Codex Integration Manager
- Repos/surfaces: `ai_workspace`, `workspaceboard`, future `ai-bridge`, future MI/Papers/.205 surfaces
- Status: no-write/read-only plan approved for docs/task-record continuation; live `.205`, MI, Papers, OAuth, Portal data, and mailbox runtime changes are not started

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

Current next safe action: resolve `bridge-20260419-workspaceboard-exporter-file-ownership-request` through Code/Git Manager and the Workspaceboard owner before any code implementation. If Robert asks for a status email, Frank should use the completion/blocker report from the AI-Bridge session rather than treating the approval as a fresh request.

| Task id | Owner / workspace | Status | Next action | Approval boundary | Source pointer |
| --- | --- | --- | --- | --- | --- |
| `bridge-20260419-work-record-schema` | Codex Integration Manager + AI-Bridge worker / `ai-bridge`; visible session `82027764` | Local contract ready; 2026-04-20 source-map implementation added. | Use `bridge/schemas/work-record.schema.json` plus `bridge/memory/work-record-projection-source-map.json` as the contract for exporter/view planning. | Schema/docs/source-map only; no `.205`, MI/Papers write, MCP exposure, OAuth, Portal/CRM mutation, mailbox content read, deploy/live pull, service restart, or credential exposure. | This note, sections `Claude Task-Record Pattern To Adopt`, `Phase 2`, and `Immediate Next Build`; AI-Bridge session `82027764`; approval source `<CAAtX44ZYxUpzOLz1UXNUT-C8CnQSXxGy0hge3ojxW+f3PwBHWw@mail.gmail.com>`. |
| `bridge-20260419-readonly-exporter-plan` | Codex Integration Manager + Code/Git Manager / `workspaceboard`; visible scoping session `657f4780` | Scoping complete; specific file-ownership request created. | Use session `657f4780` output as the implementation-ready brief and resolve `bridge-20260419-workspaceboard-exporter-file-ownership-request` before opening an implementation worker. | Planning/docs/scoping only until Code/Git Manager assigns file ownership; no dirty-file discard, no pull over dirty trees, no deploy/live pull, no service restart, no runtime change, no shared-system write. | This note, `Phase 2: No-Write Papers/MI Projection`; AI-Bridge schema `bridge/schemas/work-record.schema.json`; Workspaceboard scoping session `657f4780`. |
| `bridge-20260419-workspaceboard-exporter-implementation-brief` | Code/Git Manager + Workspaceboard worker / `workspaceboard` | Implementation-ready, not approved to code yet. | After AI-Bridge schema output is reviewed, create a Workspaceboard worker brief for a read-only JSON exporter/view using `bridge/schemas/work-record.schema.json`; Code/Git Manager must assign file ownership before edits. | No implementation until Code/Git Manager approves dirty-worktree ownership; no runtime change, deploy/live pull, service restart, MCP change, MI/Papers write, `.205` access, OAuth, Portal/CRM mutation, or credential exposure. | Derived from `bridge-20260419-readonly-exporter-plan` and Robert's read-only actionability directive. |
| `bridge-20260419-workspaceboard-exporter-file-ownership-request` | Code/Git Manager + Workspaceboard owner / `workspaceboard` | Specific request task from scoping session `657f4780`. | Decide whether implementation may touch `server/digital-office-index.js` or must add `server/bridge-work-record-exporter.js`; decide endpoint shape (`/api/bridge/work-records` vs `/api/digital-office-index`); decide non-canonical projection ID policy; confirm active session `8c23b19d` does not own related files. | No implementation, dirty-file discard, git pull over dirty tree, commit, push, deploy/live pull, service restart, runtime change, MCP exposure, `.205`, OAuth, Papers/MI write/read, Portal/CRM mutation, mailbox/private-body access, or credential exposure. | Workspaceboard scoping session `657f4780`; derived from `bridge-20260419-readonly-exporter-plan`. |
| `bridge-20260419-codex-claude-handoff-template` | AI-Bridge worker / `ai-bridge`; visible session `82027764` | Review-ready from no-write session output. | Review `bridge/templates/codex-claude-handoff.md`; use it for future Claude roundtrip tasks after source verification. | Template/docs only; Claude output remains analysis until verified by Codex or target worker; no `.205`, MCP, OAuth, Papers/MI write, Portal/CRM mutation, deploy/live pull, or service restart. | This note, `Phase 3: Codex-Claude Handoff Contract`; AI-Bridge session `82027764`. |
| `bridge-20260419-claude-task-logging-roundtrip` | Frank + Codex Integration Manager / `frank`, `ai` | Waiting on Claude response. | When Claude replies to Frank's corrected bridge note, map Claude's task id/status fields into this register or a successor task record and route any implementable work to a visible worker. | No mailbox credential/private body exposure; no external resend unless separately approved; no `.205`, Papers/MI write, Portal/CRM mutation, MCP exposure, deploy/live pull, or service restart. | Frank task `frank-2026-claude-codex-organigram-work-record-bridge-cc-follow-up`; Message-ID `<177661269639.29604.14362403569930801531@kovaldistillery.com>`. |
| `bridge-20260419-claude-task-logging-response-request` | Frank / `frank`; visible session `86f1b736` | Frank nudge sent; waiting on Claude response, not Robert. | Watch for Claude's reply; when it arrives, map task id/source ref/owner/status/next action/approval gates into this register or successor task records. | No mailbox credential/private body exposure; no broad resend; no external-sensitive content; no `.205`, Papers/MI write, MCP exposure, deploy/live pull, service restart, or credential exposure. | Derived from `bridge-20260419-claude-task-logging-roundtrip`; original Frank Message-ID `<177661269639.29604.14362403569930801531@kovaldistillery.com>`; nudge Message-ID `<177661959602.5921.17895643980954120746@kovaldistillery.com>`; nudge session `86f1b736`. |
| `bridge-20260419-portal-existing-summary` | Portal design + Frank summary path / `portal`, `frank` | Fixture-only dry run completed or parked for review; live path blocked. | Use the fixture output to create a live-read approval request and implementation-ready brief rather than leaving the design passive. | No Portal/CRM mutation, no production DB write, no private contact detail broadcast, no email send, no deploy/live pull/restart. | Task `ai-cim-20260419-portal-existing-account-summary`; sessions `ba888628`, `d3f5b188`; `Phase 4`. |
| `bridge-20260419-portal-live-lookup-approval-request` | Portal owner + Frank / `portal`, `frank` | Specific approval request task. | Ask Robert/source owner to approve or reject a read-only Portal/CRM lookup path, allowed account/contact fields, link format, recipient/copy behavior for Frank's summary, and whether fixture wording is acceptable. | Until approved: no live Portal/CRM read, no mutation, no private details in chat/email, no send, no deploy/live pull/restart. | Derived from read-only Portal summary packet and Robert's read-only actionability directive. |
| `bridge-20260420-papers-readonly-wrapper-approval` | Workspaceboard + Security Guard / `workspaceboard`, `ai` | Specific approval request task dated 2026-04-20. | Ask Robert to approve or reject live read-only Workspaceboard access to Papers through the deny-by-default wrapper and name initial allowed scopes/collections/document IDs. | No Papers writes, credential/auth handling, `.205` access, MCP config change, LaunchAgent/runtime change, production mutation, private mailbox-body exposure, deploy, push, or live pull. | Source/access blocker; Papers scoping sessions `c6421ac1`, `778ef252`; Security Guard `c2e66c43`; Code/Git Manager `9a4787cd`. |
| `bridge-20260419-security-205-papers-access-note` | Security Guard / `ai`; visible session `99244c6e` | Closed as security decision record. | If `.205`/Papers access is still needed, ask Robert/Security to approve a separate workflow that names host, identity, allowed scope, secure credential channel, audit logging, recovery path, and exact execution gate before access. | No `.private` read, credential/token/key/password inspection or printing, SSH, `.205` access, live Papers/MI access, MCP config change, AGENTS operational access-note, auth change, service/runtime change, deploy/live pull, or destructive action. | Frank direct-email source Message-ID `<CAAtX44aR35SbgE+bSb7w_KKqXPvZ8-xt7xM8waJUzoRLV0gpqg@mail.gmail.com>`; dedupe key `frank-direct-email:CAAtX44aR35SbgE+bSb7w_KKqXPvZ8-xt7xM8waJUzoRLV0gpqg:205-papers-access-note`; `AGENTS.md` non-secret access-documentation rule. |
| `bridge-20260420-frank-avignon-oauth-health` | Security Guard + Frank/Avignon / `ai`, `frank`, `avignon` | Dated follow-up for Monday 2026-04-20. | Verify polling health first; only then decide whether Gmail API push/OAuth is still needed. | No OAuth, Google auth, Pub/Sub/IAM, mailbox content read, token/path disclosure, runtime cadence change, deploy/live pull/restart, or external send before explicit approval. | Task `ai-cim-20260419-oauth-monday-follow-up`; project log `2026-04-18-frank-avignon-gmail-push-plan.md`. |
| `bridge-20260427-macee-outreach-template-review` | Frank/Outreach Communicator / `frank`, future `ops` if approved | Dated follow-up for 2026-04-27 unless Robert approves earlier sanitized-source review. | Review whether supplied sanitized examples or approved mailbox-owner/OAuth path exists for Macee usual-booking templates; create a worker only when source access is approved. | No Macee OAuth, mailbox content read, credential exposure, external send, Portal/CRM mutation, deploy/live pull/restart. | Task `ai-cim-20260419-macee-outreach-templates`; Frank task `frank-2026-04-19-outreach-macee-inbox-oauth-template-security-review`. |
| `bridge-20260427-national-outreach-brief` | Frank/Outreach Communicator / `frank` | Dated follow-up for 2026-04-27. | Prepare or route the national outreach task brief; draft-only if recipient/content/send authority is unclear. | No email send until audience/copy/sender/timing are approved or covered by standing workflow. | Task `ai-cim-20260419-national-outreach-20260427`; Frank task `frank-2026-04-19-national-outreach-email-macee-leave-2026-04-27`. |
| `bridge-20260419-readonly-registration-schema` | AI-Bridge worker + Codex Integration Manager / `ai-bridge`, `ai`; visible session `82027764` | Review-ready from no-write session output; live registration blocked. | Review `bridge/schemas/readonly-registration-records.json`, then route Workspaceboard/MI publication only if Robert separately approves a live read-only path. | No `.205`, MI/Papers write, MCP exposure/config change, OAuth, Portal/CRM mutation, mailbox credential/content exposure, deploy/live pull/restart. | Task `ai-cim-20260419-active-registration-readonly`; trace `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-19-read-only-registration-design.md`; AI-Bridge session `82027764`. |
| `bridge-20260419-role-validation` | Codex Integration Manager / `ai`, `workspaceboard` | Closed for source validation; monitor for live drift. | Reopen only if Workspaceboard live organigram drifts from source or role docs lose the AI Manager/Codex/Claude entries. | No Workspaceboard runtime/restart/deploy or live mutation from this closed validation task. | Task `ai-cim-20260419-role-validation`; `Role And Organigram Updates`. |

Visible worker/session routing at 2026-04-19 12:13 CDT:

- Reused Codex Integration Manager session `b66fdade` as the coordinating session for this task register and future bridge-status conversion; prompt delivery was verified and the session entered `working`.
- Created AI-Bridge worker session `82027764`, `AI Bridge no-write task-record schema and handoff templates`, for the currently safe no-write bundle: `bridge-20260419-work-record-schema`, `bridge-20260419-codex-claude-handoff-template`, and `bridge-20260419-readonly-registration-schema`. Prompt delivery was verified and the session entered `working`.
- Created Workspaceboard scoping session `657f4780`, `Workspaceboard Code/Git scope for bridge readonly exporter`, for the read-only Code/Git/file-ownership pass on `bridge-20260419-readonly-exporter-plan`. Prompt delivery was verified. The session produced an implementation-ready brief and specific request task `bridge-20260419-workspaceboard-exporter-file-ownership-request`.
- Frank visible session `86f1b736`, `Frank nudge Claude on bridge and Avignon context`, sent the specific Claude response request for `bridge-20260419-claude-task-logging-response-request`; the task is now waiting on Claude response rather than Robert input.
- Defer Workspaceboard exporter/view code implementation until `bridge-20260419-workspaceboard-exporter-file-ownership-request` is resolved, Code/Git Manager assigns file ownership against the dirty worktrees, and Robert separately approves any code/runtime step.
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
