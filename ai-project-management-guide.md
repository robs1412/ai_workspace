# AI Project Management Guide
Last Updated: 2026-04-08 14:37:34 CDT (Machine: RobertMBP-2.local)

## Purpose

Keep the AI strategy/tooling review as evergreen guidance instead of a one-off dated reminder.

## Current Decisions

- Codex primary workflow: CLI via Workspace Board.
- Gemini CLI: tested; not currently useful enough to be a primary workflow.
- Active Codex skills/tools in use:
  - `playwright` is useful and in active use.
  - `openai-docs` is available as a system skill.
  - `openaiDeveloperDocs` MCP was added locally on `2026-04-08` so OpenAI docs lookups are now usable from this machine.
- AI email-account path:
  - current mailbox candidates are `frank.cannoli@kovaldistillery.com` and `claude@koval-distillery.com`
  - Codex email operations are allowed in the Frank workspace path
  - approval, sending, and logging guardrails should continue to live in the Frank workspace policy/docs

## Use This Guide For Review Sessions

When reviewing AI strategy or tooling, separate:

- current operating decisions that are already made
- items that still need implementation
- exploratory ideas that belong in planning, not immediate TODO execution

## Evergreen Review Prompts

- What else can we do now with the current AI/tool stack?
- What are we still missing operationally?
- What can push sales in the next 30 days?
- Should any work move from manual execution into Codex-run task sessions?
- Where should Claude/Codex integration actually happen: shared repo, MCP tools, memory layer, or mailbox workflow?
- Is there any real need for extra tooling such as `openclaw`, or is it just noise right now?

## Current Operating Defaults

- Prefer Codex CLI over VS Code when the work is already flowing through Workspace Board.
- Treat Gemini CLI as secondary until it proves a concrete recurring advantage.
- Use `openai-docs` when current OpenAI product guidance matters.
- Use the KOVAL 2026 Management Planner as guide material for management-process reviews, role-map/organigram updates, task-management docs, owner clarity, cadence, decision gates, and closure criteria. It is guidance only; it does not authorize email sends, external-system mutation, credential exposure, production action, or unrelated code edits.
- Keep email automation conservative unless the Frank workspace policy explicitly allows more:
  - read
  - draft
  - triage
  - send only within Frank-defined guardrails and logging

## Review Output Template

Every AI/project-management review should end with:

1. Top 3 initiatives.
2. Owner for each initiative.
3. Workspace for each initiative.
4. Success metric for each initiative.
5. Which items belong in `TODO.md` now.
6. Which items stay as guide-level strategy only.

## Reminder Session Prompt

Review the AI reminder project from `ai_workspace/TODO.md`, `recommendations.md`, and this guide. Summarize what has been implemented since the March 2026 recommendation pass, identify what is still unverified or not adopted, re-evaluate Codex CLI vs VS Code, Gemini CLI, email-account management by Codex, installable skills/agents, and any overlapping planning items, then produce the top 3 next actions with owners, guardrails, and `TODO.md` updates.
