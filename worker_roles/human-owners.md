# Human Owners / Decision Makers

## Purpose

Own business priorities, sensitive approvals, and final judgment where AI workers should not decide.

AI Manager Robert is Robert's Codex-login control surface for asking Task Manager for status, setting priority, and approving or rejecting gated work. AI Manager Dmytro is a technical AI-manager bridge for Codex/Claude integration and worker sequencing under Robert's direction.

## When To Call It

- A worker needs policy, finance, legal, HR, personnel, or sensitive communication approval.
- BID finance task `#1185` needs the six human answers before deterministic implementation.
- A project needs priority or scope clarification.
- AI Manager Robert or AI Manager Dmytro needs a chain-of-command status request routed through Task Manager.

## Who Calls It

- Decision Driver.
- Task Manager / Polier.
- Project Manager.
- AI Manager Robert.
- AI Manager Dmytro.
- Security Guard, Frank, Avignon, Communications Manager, Finance Analyst, or workspace workers when approval gates apply.

## Inputs

- One concrete decision question.
- Relevant worker output and blocker summary.
- Clear recommended next action when available.

## Outputs

- Decision, approval, rejection, or requested revision.
- Priority order when multiple projects compete.
- Human-supplied answers needed for deterministic implementation.

## Boundaries

- Humans are not expected to inspect every terminal detail; workers should summarize clearly.
- Workers should not bury multiple decisions in one question.
- AI-manager requests should query Task Manager first, then route down to Codex workers or Claude agents through visible worker sessions.

## Approval Gates

- External sends, sensitive internal communication, finance policy, irreversible data changes, auth/security changes, and production-impacting actions.

## Workspace / Session Home

- Human decisions are captured in the relevant board session, TODO, project-hub issue, OPS task, or role doc.

## Handoff Surfaces

- Workspace Board transcript.
- `ai_workspace/TODO.md`.
- Project-hub issue notes.
- OPS tasks when operational tracking is needed.

## Open Definition Questions

- Which decisions can Decision Driver resolve without asking?
- Which approval wording should be treated as sufficient for security-sensitive credential/auth changes?
- What approval words count as send approval for Frank/Avignon/Communications Manager?
