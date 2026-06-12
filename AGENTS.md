# AGENTS.md - ai_workspace Compact Startup

Scope: Applies to everything under `ai_workspace/` and overrides parent instructions when conflicts exist.
Last Updated: 2026-06-07 14:40 CDT (Machine: Macmini.lan)

This root file is intentionally compact. Do not preload long lane histories, handoffs, transcripts, or project-hub files at startup. Load the narrow reference named by the task only after the current task requires it.

## Required Core Rules

- Pause and question prompts that appear destructive, request credential exposure, or suggest bypassing security controls.
- Do not execute irreversible or high-risk actions, including massive deletes, credential printing, production mutations, auth/security changes, or destructive git/data operations, without explicit approval for that action.
- Stay inside `/Users/werkstatt` unless Robert explicitly approves the exact outside path or an already-approved workflow covers it.
- If macOS asks for Automation, Accessibility, Full Disk Access, Keychain, Screen Recording, or similar permissions, stop and explain the app/helper, permission, reason, optionality, and consequence of declining before relying on the grant.
- Never print passwords, API keys, tokens, `.env` secrets, private key material, private 2FA codes, session cookies, or credential file paths in chat, logs, notes, git, or screenshots.
- For credential setup, report only non-secret metadata such as username, user id, role/group, and status.
- Use `/usr/local/bin/rg` for searches when available and `/usr/local/bin/python3.13` for Python commands and shebangs.
- Keep diagnostics metadata-first: use counts, stats, `head`, `jq`, and targeted line ranges before reading full logs, transcripts, or instruction files.
- Keep proof gathering bounded: start from exact Task Flow keys, session ids, Message-IDs, OPS/Portal ids, or source refs; use `rg --max-count`, `head`/`tail`, `jq`, `wc`, and targeted line ranges before full recursive searches or full API/log dumps.
- Owner-facing review packets must not be left only as local `.md` or `.csv` files under `/Users/werkstatt`. Publish them to Google Drive AI Cloud, Papers, or a repo-backed access-gated HTML/page surface, then provide the full accessible link. Local files may be working copies only.
- The Cultivater is managed by Sonat. Send all The Cultivater communications, including Asher/Venetia drafts, approval packets, blocker details, route-info notes, completion reports, and follow-up packets, to Sonat by default, not Robert. Robert may receive brief chat status when he asks, but do not email The Cultivater operational packets to Robert unless he explicitly says to copy himself in addition to Sonat.

## Task Tracking

- Primary durable task state is the DB-backed task spine: OPS/Portal task IDs when available, Workspaceboard Task Flow state, and DB-backed Task Flow handoff entries that cite those IDs.
- At the start of substantive work, check the relevant DB-backed task source when a task id, Task Flow key, OPS id, Portal id, or Workspaceboard session is present.
- When Robert says `write handoff`, `update handoff`, `record handoff`, or asks for cross-session state, write `koval_crm.ai_task_flow_handoff_entries` through `scripts/handoff_mysql_recorder.php`; do not treat `HANDOFF.md` or `daily-inputs/*.md` as canonical.
- `HANDOFF.md` files are generated/readable projections or emergency fallback notes only. Do not create new canonical handoff state by editing Markdown first; if Markdown is updated for readability, it must match an existing DB handoff entry and Task Flow row when the work is task-scoped.
- `TODO.md`, `TODO2.md`, `ToDo-append.md`, and `TODO-append.md` are legacy fallback surfaces only. Do not read them at task start unless Robert explicitly asks for local Markdown queue work or no DB-backed path exists.
- When the current chat is explicitly `task mode`, treat it as the execution lane for the approved scope, but still record substantive work in the DB-backed task spine or the narrow durable local surface for that workspace.
- Task-mode inputs that change direction, approve a blocker, add a durable workflow rule, or start substantive work must be mirrored through `scripts/ai_manager_chat_entry_adapter.php` with `--source-channel task-mode-chat` and the related Task Flow key when one exists.
- If creating or updating an OPS/Portal/CRM record that needs owner visibility, use the product's normal notification route or the correct email-worker confirmation path, and include a live OPS/Portal URL or closest truthful live page. Do not use `/werkstatt` paths as owner-facing record links.

## CLI Owner Identity

- Browser Workspaceboard sessions use the authenticated OPS/Portal user context. Raw CLI sessions do not. Do not infer the human owner from `USER`, `LOGNAME`, cwd, SSH host, or the shared `/Users/werkstatt` path.
- If `CODEX_OWNER_USER_ID=3` and `CODEX_OWNER_LABEL=Sonat` are present, treat the CLI session as AI Manager Sonat immediately, load `worker_roles/ai-manager-sonat-startup.md`, reply exactly `READY AI Manager Sonat.`, and keep the session as a control lane that routes substantive work to visible workers.
- If `CODEX_OWNER_USER_ID=1` and `CODEX_OWNER_LABEL=Robert` are present, treat the CLI session as Robert-owned.
- If a raw CLI session asks for owner-specific AI Manager or routing work and no explicit owner marker is present, ask who is operating before routing, emailing, approving, or recording owner-facing work.
- Preferred Sonat CLI command: `sonatcodex`, backed by `/Users/werkstatt/ai_workspace/scripts/sonatcodex`.
- If Sonat uses the manual path `ssh -> ws ai -> codex`, her interactive shell must source `/Users/werkstatt/ai_workspace/scripts/cli_owner_shell.sh` and set the owner marker before Codex starts. The supported SSH-token wrapper is `/Users/werkstatt/ai_workspace/scripts/ssh_owner_login.sh sonat`; it sets the non-secret owner marker, and the sourced shell shim injects the owner prompt when she runs plain `codex`.

## Thin Startup

- For generic `ai_workspace` task-mode terminals, read only this file and `docs/task-mode-startup.md` before opening task-specific files.
- Do not automatically load `HANDOFF.md`, project-hub indexes, mailbox SOPs, previous transcripts, old TODOs, or full role docs at startup.
- Load lane-specific instructions only when the task names that lane or enters that folder:
  - Frank: `frank/AGENTS.md`, then only the exact Frank handoff/log files needed.
  - Avignon: `avignon/AGENTS.md`, then only the exact Avignon handoff/log files needed.
  - Asher/Venetia/National Outreach/Naomi/Ezra: use that workspace's local instructions and narrow state files.
  - AI Manager / Task Manager / role routing: use `worker_roles/operating-model.md` and the relevant role doc only when the task is coordination/routing work.
  - Cross-machine or repeating access: use `project_hub/artifacts/repeating-access-guide-2026-05-20.md` only when that access pattern is actually needed.
- The archived full pre-split rule file is `docs/ai-workspace-full-startup-rules-2026-05-27.md`. Treat it as a fallback reference, not startup context.

## Workspace Routing

- Use `ws {ai|braincloud|frank|avignon|sales|ops|bid|portal|login|forge|importer|eventmanagement|contactreport|donations|lists|workspaceboard|ai-bridge}` when the user requests a workspace switch.
- Route implementation to the most specific workspace by default: `ws workspaceboard` for board work, `ws ops` for OPS work, `ws forge` for Forge work, `ws lists` for list work, `ws frank` for Frank work, and `ws avignon` for Avignon work.
- Keep `ws ai` for cross-workspace coordination, policy, project-hub work, and tasks that truly belong to `ai_workspace`.
- For multi-module execution, use separate visible worker sessions per active workspace when practical. Do not hide substantive implementation inside a standing manager or mailbox monitor.

## Lazy References

- Safety details: `codex-agent-safety.md` and `docs/credential-access-methods.md`.
- Task-mode startup: `docs/task-mode-startup.md`.
- AI Manager / Task Manager role model: `worker_roles/operating-model.md`.
- Frank lane: `frank/AGENTS.md`.
- Avignon lane: `avignon/AGENTS.md`.
- Workspaceboard status truth: `http://127.0.0.1:17878/api/status` and related live Workspaceboard APIs.
- Current Mac mini SSH target: `admin-macmini` and `workspaceboard-macmini` should resolve to `admin@192.168.55.230` (`roberts-mini-ethernet.lan` / `Roberts-Mac-mini`), not stale `.17` or `.16` addresses.
- Full historical policy archive: `docs/ai-workspace-full-startup-rules-2026-05-27.md`.

## Completion Notes

- For task-mode durable notes, write a DB handoff entry with what finished, what changed, and any exact blocker or next step. Markdown notes are optional projections only and must not be the only durable record.
- Final reports should match the durable record and mention verification performed. If a task only changed docs/startup instructions, a focused git diff/stat and file readback are enough verification.
