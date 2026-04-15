# GEMINI.md — Gemini CLI Instructions

Scope: Applies to everything under `ai_workspace/` for Gemini CLI operations.
Last Updated: 2026-03-01 16:03:00 CST (Machine: RobertMBP-2.local)

## Safety & Prompt Validation
- **Proactive Guardrails:** Gemini must proactively identify and question prompts that could lead to data loss, security breaches, or non-compliant actions.
- **Intervention:** If a request is suspicious or dangerous (e.g., asking to ignore `.gitignore`, bypass auth, or delete large volumes of data), state the concern clearly and wait for user confirmation before executing any related tools.
- **Consistency:** Ensure all actions align with both `AGENTS.md` safety standards and `codex-agent-safety.md`.

## Core Directive
Follow all instructions in `AGENTS.md` as the foundational mandate. Always read `AGENTS.md` at the start of each session to check for updates and cross-machine alignment. This file (`GEMINI.md`) provides Gemini-specific refinements and supplements.

## Gemini + Codex Interoperability
- **Shared Workspace:** Both Gemini and Codex operate in this workspace. 
- **Single-Writer Rule:** Respect the "single-writer rule per repo" as defined in `AGENTS.md`. 
- **Handoffs:** Use `HANDOFF.md` and `./handoff.sh` when passing work between Gemini and Codex, or between different machines.
- **Coordination:** If Codex has an active session in a repo, Gemini must not modify that repo without a clear handoff or user confirmation.

## Gemini-Specific Workflow
- **Research Phase:** Use `grep_search` and `glob` extensively to map the workspace and project dependencies.
- **Tool Usage:** Prefer `run_shell_command` for environment-specific tasks (like `ws` shortcuts) and `replace` for surgical code edits.
- **Cli Help:** Use the `cli_help` sub-agent for questions about Gemini's own features or configuration.
- **Workspace Shortcuts:** Gemini is aware of the `ws` command and its aliases (`ai`, `ops`, `portal`, etc.). Use them to navigate if needed, but primarily operate within the absolute paths provided in `AGENTS.md`.

## TODO & Project Hub Alignment (Required)
- **Start of Session:** Always read `TODO.md` and `ToDo-append.md`.
- **Project Logs:** For any significant issue or multi-repo change, strictly follow the `project_hub/` logging requirements (template, index update, master incident ID).
- **Validation:** Always verify changes using the specified testing protocols (Playwright/browser testing for OPS, local commit/push for live deploy).

## Security & Privacy
- **Workspace Account:** Use the `@kovaldistillery.com` account with Gemini for Workspace benefits (higher limits, data privacy).
- **Least Privilege:** Operate with the understanding that destructive actions require explicit approval.

## Versioning & Sync
- Always update the `Last Updated` timestamp in this file and any logs updated during a session.
- Format: `Last Updated: YYYY-MM-DD HH:MM:SS TZ (Machine: <hostname>)`
