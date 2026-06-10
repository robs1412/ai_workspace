# Task Mode Startup

Use this file as the thin bootstrap for new WS AI / Workspaceboard task-mode terminals.

## Startup Budget

- Start with the task pointer, not the whole workspace history.
- Load only:
  - root `AGENTS.md`
  - this file
  - the current Task Flow / OPS / Portal / Workspaceboard packet when one exists
  - the local `AGENTS.md` for the target workspace if the task is inside a subfolder such as `frank/` or `avignon/`
- Do not preload `HANDOFF.md`, project-hub indexes, TODO archives, mailbox SOPs, full role maps, old transcripts, or large logs.

## Proof And Output Budget

- Gather proof metadata-first: exact Task Flow key, session id, Message-ID, OPS/Portal id, body filename, or source ref before broader search.
- Use bounded commands first: `rg --max-count`, `head`, `tail`, targeted line ranges, `wc`, `jq` projections, and exact DB recorder readbacks.
- Do not dump full `/api/status`, full session-history JSON, recursive launch-state searches, full `HANDOFF.md`, project-hub indexes, old transcripts, or mailbox logs unless the exact-id checks miss and the larger read is necessary.
- For process or memory diagnostics, use `scripts/compact_process_memory.py` or `ps` projections that omit full command arguments. Full `ps ... args` output can leak long prompts and burn tokens.
- For Workspaceboard proof, prefer exact `/api/session-history?session_id=...`, projected `/api/management/overview`, Task Flow recorder reads, or session work-state history. Return one proof marker, one exact blocker, or one owner question.

## Minimal Launch Prompt Shape

New automated task-mode terminals should receive a compact prompt with:

- task id, Task Flow key, OPS id, Portal id, or Workspaceboard session id when available
- workspace path
- one-sentence goal
- exact approved scope
- approval gates or "no external sends / no production mutation / no secrets" constraints
- expected durable state surface
- final report target

Example:

```text
Task mode. Workspace: /Users/werkstatt/workspaceboard.
Goal: Fix the Task Flow stats readback mismatch.
Scope: repo-local code and docs only; no production deploy without approval.
Pointer: Task Flow key <key> / Workspaceboard session <id>.
Startup: read root AGENTS.md, docs/task-mode-startup.md, then the Task Flow packet only.
Record: update Task Flow/project note with proof and final verification.
```

## Lazy Loading Rules

- If a task names Frank, Avignon, National Outreach, Naomi, Asher, Venetia, OPS, Portal, Forge, BID, or Workspaceboard, load that workspace's local instructions after the compact root file.
- If a task touches auth, credentials, OAuth, 2FA, `.205`, Papers/MI writes, macOS permissions, SSH config, system LaunchAgents, production data, destructive data, or external sends, pause and route through the relevant safety/approval path before acting.
- If a task is pure docs or repo-local startup policy, do not read mailbox runtime logs, old handoffs, or project histories unless the diff cannot be made safely without them.

## Verification

- For docs/startup changes: use `git diff --stat`, targeted file readback, and line counts.
- For code changes: run the repo's narrow syntax/tests/checks.
- For live state changes: verify the live owner surface such as Workspaceboard, Task Flow, OPS, Portal, or sent-log proof before claiming completion.
