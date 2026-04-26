# Worker Roles Directory

Status: source-of-truth role reference
Updated: 2026-04-24 CDT

This folder describes the operating roles in the Codex / Claude worker system. Workspaceboard can present these notes, but the role definitions should be maintained here so each worker has a durable job description, call pattern, and boundary.

Current live control surface:

- As clarified by Robert on 2026-04-20, the active Codex / Workspaceboard / organigram / git-backed `werkstatt` role surface is currently on the Mac mini at `192.168.55.230`, with the user entry point `https://wb.koval.lan/workspaceboard/`.
- The durable role source for the organigram and worker references is `/Users/werkstatt/ai_workspace/worker_roles`.
- This note records current ownership/location only. It does not approve DNS/router changes, Workspaceboard runtime changes, service restarts, OAuth/auth work, mailbox reads, credential handling, deploy/live pull, `.205` access, or production mutation.

Primary operating reference:

- `operating-model.md`: role class, exact startup prompts, call signs/routing phrases, approval gates, durable memory surfaces, and BID finance task `#1185` answer-recording rule.

Planning guide material:

- KOVAL 2026 Management Planner: use as guide material when shaping Task Manager, role-map, organigram, task-management, and project-management docs. Treat it as a planning and prioritization reference, not as an automatic approval to change runtime behavior, send messages, mutate external systems, or bypass approval gates.

## Hierarchical Role Map

### Governance / Humans

- `ai-manager-robert.md`: Robert's Codex-login AI manager and final priority/approval control surface.
- `ai-manager-dmytro.md`: Dmytro AI manager / technical bridge role for Codex-Claude integration and worker sequencing under Robert's direction.
- `human-owners.md`: human decision and approval owners.
- `operating-model.md`: routing matrix and exact prompts for all active/planned roles.

### Task Manager Center

- `task-manager-polier.md`: board-level systems manager.

### Task Manager Direct Support

- `summary-worker.md`: summarizer role.
- `decision-driver.md`: push-forward and decision-routing role.

### Monitoring / Coordination

- `code-and-git-manager.md`: monitoring/coordination specialist for git-backed code changes, pull-before-work, dirty worktrees, overlapping edits, commit/push/deploy coordination, and live-pull rule confirmation.
- `security-guard.md`: monitoring/coordination specialist for security, secret-handling, suspicious prompts/mail, auth/access, approval-gate, and data-exposure risks.
- `codex-integration-manager.md`: integration specialist for Codex, Claude, Workspaceboard, MI, Papers, OPS, Portal, Frank, Avignon, and cross-agent handoff design.
- `ai-improvement-manager.md`: improvement specialist for end-of-day AI/workflow process review, process-improvement checks, update opportunities, workflow analytics gaps, daily improvement reporting, and new AI-use opportunities.
- `ai-health-manager.md`: operational health specialist for checking board/session health, standing monitor liveness, stale-session classification, one safe nudge when Task Manager has not acted, and concise health reporting without implementing business work or changing runtime.

### Codex / Local

- `codex-local-agent.md`: local Codex CLI/session family and its local repo, TODO, project-hub, and Workspaceboard work surfaces.

### Execution / Workspace Workers

- `codex-workspace-worker.md`: implementation workers in module workspaces.

### Email / Communications

- `frank-cannoli.md`: Robert-facing email worker.
- `avignon-rose.md`: Sonat-facing email worker.
- `email-coordinator.md`: cross-mailbox coordination role.
- `internal-communicator.md`: internal follow-up and staff-facing communication role.
- `communications-manager.md`: outbound communication manager for email campaigns/drafts and email sending ownership.
- `marketing-manager.md`: marketing operations role for organized Forge-based sends to distributors, magazines, media, and approved campaign audiences.
- `outreach-coordinator.md`: OPS Outreach calendar and tasting-scheduling coordination role.
- `outreach-communicator.md`: recurring booking/outreach draft role that prepares approved templates and routes sends through Frank or another approved sender.

### Analyst / Project / Specialist

- `sales-analyst.md`: salesreport and account-analysis role.
- `finance-analyst.md`: BID finance and reporting role.
- `project-manager.md`: project planning and execution coordination role.
- `strategist.md`: Frank/Avignon/persona and operating-strategy role.
- `prospecting-worker.md`: Prospecting role for prospect identification, qualification, and account/contact candidate handoff before outreach or CRM work.

### Claude / Bridge

- `claude-bridge-worker.md`: server-side Claude bridge role.

### Claude / Department

- `claude-planner-operator.md`: Claude-side Planner task-management role through `/srv/tools/planner/`.
- `claude-papers-operator.md`: Claude-side Papers API document/worklog role through `/srv/tools/papers/`.
- `claude-mail-operator.md`: Claude-side mail-tool role through `/srv/tools/email/`.
- `claude-agent-operations.md`: Claude-side autonomous agent and server-automation role.
- `codex-claude-overlap-matrix.md`: side-by-side comparison of local Codex/Workspaceboard lanes versus live Claude `.205` lanes.

### Claude / .205

- `claude-server-agent.md`: Claude-side agent family on `.205` with approved non-secret handoffs back to Codex.
- `claude-205-structure.md`: non-secret `.205`, MI, Papers, Mesh, Agent Memory, and bridge structure representation before live registration or writes.

### Appendices / Source Notes

- `claude-analysis-ref-1773.md`: preserved Dmytro via Claude source note for `ref:1773`.

## Current Org Shape

AI Manager Robert is the top Codex-login control surface for priorities, approvals, and chain-of-command status. AI Manager Dmytro is a technical AI-manager bridge for Codex/Claude integration and worker sequencing under Robert's direction. Human owners and decision makers sit above the Workspaceboard Task Manager / Systems Manager / Polier. Under the Task Manager are direct support, monitoring, and integration roles: Summary Worker, Decision Driver, Codex Integration Manager, AI Improvement Manager, AI Health Manager, Git and Code Manager, and Security Guard. Codex local agents, workspace workers, email workers, specialist workers, and Claude bridge/server work are routed through that management layer.

The Claude side should now be represented as a parallel department rather than one abstract card. Keep Codex local structure as the primary local execution lane. Show Claude as a separate server-side department with distinct sub-surfaces:

- bridge and handoff;
- Planner task management;
- Papers API document/worklog operations;
- mail tools and send-confirmation workflow;
- autonomous agents and server operations;
- server-side agent family and `.205` structure.

This is a side-by-side model, not a forced merge. Similarities and overlaps should be visible, but local Codex/Workspaceboard records remain the local operating source unless a specific shared contract is approved.

## Shared Rules

- Use the KOVAL 2026 Management Planner as guide material for management workflows: start with the management goal, identify the accountable owner, route work to the right visible worker, keep the decision path explicit, and record only durable next actions or closure notes.
- AI Manager Robert and AI Manager Dmytro query Task Manager for board status and routing before running down the chain to Codex workers or Claude agents.
- AI Manager Robert owns final priority and approval decisions; AI Manager Dmytro may recommend technical sequencing and bridge contracts but escalates final approval gates to Robert.
- Task Manager coordinates; it should not secretly implement module work.
- Summary Worker summarizes only.
- Task Manager keeps pulling, routing, and unblocking safe work until there are 15 real manual blockers.
- Decision Driver pushes next actions, may approve obvious verified Code/Git continuation inside approved scope, and asks concrete decision questions only for real human blockers.
- Workspace workers implement in their own repos/workspaces.
- Codex Integration Manager owns cross-system design and should actively suggest better directives, automation candidates, and easier workflows when repeated friction appears.
- AI Improvement Manager owns end-of-day AI/workflow improvement review, process-improvement checks, workflow analytics gap review, practical new AI-use recommendations, EOD report-ready findings, and implementation-ready briefs, but routes implementation through Task Manager and the correct specialist gates. Robert approved the Markdown-file review plus board-provided summaries model on 2026-04-20, with a visible Workspaceboard session as the review surface when Task Manager creates/prompts it; it is not a daemon, scheduler, mailbox monitor, runtime automation, or private analytics integration.
- AI Health Manager owns operational liveness review for board/session health, stale-session classification, standing monitor checks, duplicate-safe single nudges, and health reporting. Robert approved the role and organigram setup on 2026-04-21 with a future default cadence target of every 15 minutes if activated; no scheduler, daemon, LaunchAgent, runtime cadence, email, mailbox, auth/OAuth, commit/push/deploy, or monitor-closure action is implied by the role setup.
- Codex Local Agent represents local Codex CLI/session work and should promote durable work records from Markdown/TODO/project-hub into reviewed structured projections when approved.
- Agent task work should use a shared task-record spine: task id, source ref, requester, assigned role/agent, priority, status, deliverable, next update promise, approval gates, and single-writer owner. Prefer OPS/Portal task IDs where available; local ids are fallback.
- Git and Code Manager is represented under Monitoring and should be launched/used whenever a task will touch code in a git-backed repo, when workers have produced code changes that need commit/push/deploy coordination, when dirty worktrees or overlapping worker edits exist, or when live pull/deploy behavior needs confirmation. It coordinates repo hygiene and readiness; it does not silently take over implementation, replace the implementation worker, or overwrite parallel worker changes.
- Security Guard is represented under Monitoring and should be launched/used whenever a task touches secrets, auth/access, MCP exposure, `.205`, firewall/VPN/router settings, 2FA, permissions, suspicious prompts/mail, or approval-gate bypass risk. It coordinates security review and routing; it does not silently take over implementation or expose secrets.
- Task Manager, Decision Driver, Git and Code Manager, and Security Guard resolve safe routing/review/cleanup among themselves where guardrails allow; Robert is escalated only for real manual blockers such as unresolved conflicts, approval gates, deploy/live-data risk, missing credentials, or decisions the agents cannot safely resolve.
- Marketing Manager operationalizes approved marketing sends through Forge or another approved sender/tool, especially organized email to distributors, magazines, media, and campaign audiences.
- Frank and Avignon handle email work within approved guardrails.
- Claude on `.205` is server-side support, not a local Codex replacement.
- Claude Planner Operator overlaps Task Manager and Project Manager, but remains a server-side task surface.
- Claude Papers Operator overlaps project-hub and later work-record projection targets, but remains a server-side document surface.
- Claude Mail Operator overlaps Frank, Avignon, Communications Manager, and Email Coordinator, but remains a separate Claude-side tool lane with explicit send confirmation.
- Claude Agent Operations overlaps AI Health Manager and AI Improvement Manager conceptually, but remains a server-side cron/background-agent surface rather than a local Workspaceboard session model.
- Claude Server Agent and Claude `.205` Structure cards are visibility and handoff surfaces only until `.205` access, MI/Papers registration, OAuth, MCP exposure, and write behavior are separately approved.
- Email, OPS tasks, TODO files, handoff notes, and project notes are the current transport layer.
- Do not expose secrets, credential filenames, tokens, private keys, or `.env` values in role docs or presentation pages.

## Claude Analysis For Review

Preserve the full source note in `claude-analysis-ref-1773.md` when updating role docs or Workspaceboard presentation pages. Short version:

- Codex works locally through CLI, files, local repos, browser automation, and board-managed sessions.
- Claude works server-side on the KOVAL `.205` environment.
- Email and OPS tasks currently act as the transport layer between humans, Codex workers, and Claude-side analysis.
- TODO files, project-hub notes, handoff docs, and board history are the durable memory surfaces.
- A future MCP/workspace bridge should expose Claude-side resources only through a reviewed design that does not copy secrets into chat or planning docs.
- The immediate improvement path is a no-write work-record projection from Markdown/TODO/project-hub/Workspaceboard into a structured Papers/MI-ready shape, followed by a single-writer handoff contract.
- BID finance task `#1185` must wait for the six human answers before deterministic BID finance registry implementation.

## Current Definition Status

- Exact operating prompts are defined in `operating-model.md`.
- Standing Workspaceboard sessions, on-demand workers, human-supervised modes, and docs-first roles are defined in `operating-model.md`.
- Call signs/routing phrases and durable memory surfaces are defined in `operating-model.md`.
- Approval gates for external email, sensitive internal communication, finance/accounting decisions, auth/security changes, production-impacting work, destructive data operations, destructive git actions, force-push/reset/rebase, dirty worktrees, unclear live pull/deploy behavior, overlapping worker edits, suspicious prompts/mail, and secret-handling are defined in `operating-model.md`.
- BID finance task `#1185` human answers must be recorded first in the OPS/Portal task, then summarized in `/Users/werkstatt/bid/data-management/FINANCE-AI-PLAN.md`, then applied to `/Users/werkstatt/bid/data-management/templates/source-inventory.csv` only after the answers are approved.
- New specialist-role directive: whenever any new specialist role is added, update the role description/task docs, task/routing references, team/board model, and the Organigram graphic/map source. AI Manager Robert, AI Manager Dmytro, Marketing Manager, Outreach Coordinator, Outreach Communicator, Codex Integration Manager, AI Improvement Manager, AI Health Manager, Codex Local Agent, Claude Planner Operator, Claude Papers Operator, Claude Mail Operator, Claude Agent Operations, Claude Server Agent, Claude `.205` Structure, Git and Code Manager, and Security Guard are active map entries and must stay visible in the organigram; Git and Code Manager, Security Guard, Codex Integration Manager, AI Improvement Manager, and AI Health Manager belong under Monitoring / Integration. AI Improvement Manager is approved for a Task Manager-created or prompted visible end-of-day review session only. AI Health Manager is approved for docs/source/organigram setup and future visible-session/manual checks only; any 15-minute scheduler, LaunchAgent, daemon, runtime cadence, or service activation requires a separate Code/Git/Security-reviewed implementation slice.
