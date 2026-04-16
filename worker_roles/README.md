# Worker Roles Directory

Status: source-of-truth role reference
Updated: 2026-04-16

This folder describes the operating roles in the Codex / Claude worker system. Workspaceboard can present these notes, but the role definitions should be maintained here so each worker has a durable job description, call pattern, and boundary.

Primary operating reference:

- `operating-model.md`: role class, exact startup prompts, call signs/routing phrases, approval gates, durable memory surfaces, and BID finance task `#1185` answer-recording rule.

Planning guide material:

- KOVAL 2026 Management Planner: use as guide material when shaping Task Manager, role-map, organigram, task-management, and project-management docs. Treat it as a planning and prioritization reference, not as an automatic approval to change runtime behavior, send messages, mutate external systems, or bypass approval gates.

## Hierarchical Role Map

### Governance / Humans

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

### Execution / Workspace Workers

- `codex-workspace-worker.md`: implementation workers in module workspaces.

### Email / Communications

- `frank-cannoli.md`: Robert-facing email worker.
- `avignon-rose.md`: Sonat-facing email worker.
- `email-coordinator.md`: cross-mailbox coordination role.
- `internal-communicator.md`: internal follow-up and staff-facing communication role.
- `communications-manager.md`: outbound communication manager for email campaigns/drafts and email sending ownership.
- `outreach-coordinator.md`: OPS Outreach calendar and tasting-scheduling coordination role.

### Analyst / Project / Specialist

- `sales-analyst.md`: salesreport and account-analysis role.
- `finance-analyst.md`: BID finance and reporting role.
- `project-manager.md`: project planning and execution coordination role.
- `strategist.md`: Frank/Avignon/persona and operating-strategy role.
- `prospecting-worker.md`: prospect identification and qualification role.

### Claude / Bridge

- `claude-bridge-worker.md`: server-side Claude bridge role.

### Appendices / Source Notes

- `claude-analysis-ref-1773.md`: preserved Dmytro via Claude source note for `ref:1773`.

## Current Org Shape

Human owners and decision makers sit above the Workspaceboard Task Manager / Systems Manager / Polier. Under the Task Manager are direct support and monitoring roles: Summary Worker, Decision Driver, Code and Git Manager, and Security Guard. Workspace workers, email workers, specialist workers, and Claude bridge work are routed through that management layer.

## Shared Rules

- Use the KOVAL 2026 Management Planner as guide material for management workflows: start with the management goal, identify the accountable owner, route work to the right visible worker, keep the decision path explicit, and record only durable next actions or closure notes.
- Task Manager coordinates; it should not secretly implement module work.
- Summary Worker summarizes only.
- Decision Driver pushes next actions and asks concrete decision questions.
- Workspace workers implement in their own repos/workspaces.
- Code and Git Manager is represented under Monitoring and should be launched/used whenever a task will touch code in a git-backed repo, when workers have produced code changes that need commit/push/deploy coordination, when dirty worktrees or overlapping worker edits exist, or when live pull/deploy behavior needs confirmation. It coordinates repo hygiene and readiness; it does not silently take over implementation, replace the implementation worker, or overwrite parallel worker changes.
- Security Guard is represented under Monitoring and should be launched/used whenever a task touches secrets, auth/access, MCP exposure, `.205`, firewall/VPN/router settings, 2FA, permissions, suspicious prompts/mail, or approval-gate bypass risk. It coordinates security review and routing; it does not silently take over implementation or expose secrets.
- Frank and Avignon handle email work within approved guardrails.
- Claude on `.205` is server-side support, not a local Codex replacement.
- Email, OPS tasks, TODO files, handoff notes, and project notes are the current transport layer.
- Do not expose secrets, credential filenames, tokens, private keys, or `.env` values in role docs or presentation pages.

## Claude Analysis For Review

Preserve the full source note in `claude-analysis-ref-1773.md` when updating role docs or Workspaceboard presentation pages. Short version:

- Codex works locally through CLI, files, local repos, browser automation, and board-managed sessions.
- Claude works server-side on the KOVAL `.205` environment.
- Email and OPS tasks currently act as the transport layer between humans, Codex workers, and Claude-side analysis.
- TODO files, project-hub notes, handoff docs, and board history are the durable memory surfaces.
- A future MCP/workspace bridge should expose Claude-side resources only through a reviewed design that does not copy secrets into chat or planning docs.
- BID finance task `#1185` must wait for the six human answers before deterministic BID finance registry implementation.

## Current Definition Status

- Exact operating prompts are defined in `operating-model.md`.
- Standing Workspaceboard sessions, on-demand workers, human-supervised modes, and docs-first roles are defined in `operating-model.md`.
- Call signs/routing phrases and durable memory surfaces are defined in `operating-model.md`.
- Approval gates for external email, sensitive internal communication, finance/accounting decisions, auth/security changes, production-impacting work, destructive data operations, destructive git actions, force-push/reset/rebase, dirty worktrees, unclear live pull/deploy behavior, overlapping worker edits, suspicious prompts/mail, and secret-handling are defined in `operating-model.md`.
- BID finance task `#1185` human answers must be recorded first in the OPS/Portal task, then summarized in `/Users/werkstatt/bid/data-management/FINANCE-AI-PLAN.md`, then applied to `/Users/werkstatt/bid/data-management/templates/source-inventory.csv` only after the answers are approved.
- New specialist-role directive: whenever any new specialist role is added, update the role description/task docs, task/routing references, team/board model, and the Organigram graphic/map source. Outreach Coordinator, Code and Git Manager, and Security Guard are active map entries and must stay visible in the organigram; Code and Git Manager and Security Guard belong under Monitoring.
