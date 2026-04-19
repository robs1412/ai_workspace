# AI Manager Robert

## Purpose

Represent Robert's Codex-login control surface as the top AI-manager role for priorities, approvals, chain-of-command queries, and final business direction.

## Call This Role When

- Robert is using Codex or Workspaceboard as the AI management console.
- A task needs priority, scope, approval, or escalation from the human owner.
- The board needs a top-level status request: query Task Manager, then route down to Codex workers or Claude agents.
- A role, directive, or chain-of-command change needs final owner approval.

## Responsibilities

- Ask the Task Manager for current status and routing.
- Approve or reject work that crosses human approval gates.
- Set priorities across Codex, Claude, Frank, Avignon, OPS, Portal, MI/Papers, and Workspaceboard.
- Keep AI-manager requests visible in Workspaceboard instead of hidden in ad hoc terminal work.
- Delegate implementation to Task Manager and the appropriate worker chain.

## Who Calls It

- Task Manager / Polier.
- Decision Driver.
- Security Guard when Robert-level approval is required.
- Codex Integration Manager for cross-agent operating-model decisions.
- Human owner directly through the active Codex login.

## Inputs

- One concrete decision request.
- Task Manager status or routed worker summary.
- Approval gate, risk, and recommended next action.

## Outputs

- Priority decision.
- Approval, rejection, or requested revision.
- Permission to route work to a specific worker or specialist.
- Human-level answer for blockers that agents cannot resolve.

## Boundaries

- AI Manager Robert is a human/control role, not an autonomous background worker.
- The role can direct Task Manager, but should not bypass Task Manager visibility for multi-step work.
- Approval must remain explicit for external sends, finance/legal/HR, auth/security, production, destructive data, live MI/Papers writes, OAuth, `.205`, MCP exposure, or shared-write behavior.

## Workspace / Session Home

- Current Robert Codex login, Workspaceboard AI management view, and `ws ai` Task Manager surface.

## Handoff Surfaces

- Workspaceboard session transcript.
- `ai_workspace/TODO.md`.
- `ai_workspace/HANDOFF.md`.
- Project-hub notes.
- OPS/Portal tasks when operational tracking is required.

## Operating Reference

- Exact startup prompt, class, call signs/routing phrases, approval gates, and durable memory surfaces are defined in `operating-model.md`.
- Chain of command: AI Manager Robert -> Task Manager / Polier -> direct support / monitoring / integration -> Codex workspace workers or Claude bridge/server agents.
