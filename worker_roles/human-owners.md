# Human Owners / Decision Makers

## Purpose

Own business priorities, sensitive approvals, and final judgment where AI workers should not decide.

## When To Call It

- A worker needs policy, finance, legal, HR, personnel, or sensitive communication approval.
- BID finance task `#1185` needs the six human answers before deterministic implementation.
- A project needs priority or scope clarification.

## Who Calls It

- Decision Driver.
- Task Manager / Polier.
- Project Manager.
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
