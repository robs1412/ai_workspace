# AI Workstation And Sync Plan

Status: approved planning direction
Updated: 2026-04-15 18:35:52 CDT (Machine: Macmini.lan)
Owner: Robert / Decision Driver

## Recommendation

Robert's front-facing workstation role is shared by the Mac Mini M4 2025 and MacBook, with the M4 as the stronger desk workstation. Keep the Mac mini 2018 (`.17`) as the near-term main AI station/server and worker host on macOS. Defer any Linux migration for the 2018 Mac mini until it is tested as a separate pilot with a rollback path.

This keeps the snappiest current macOS machine in front of Robert for foreground work while preserving the 2018 Mac mini's 64GB RAM for long-running Codex workers, Workspaceboard, Frank, Avignon, Polier, Summarizer, and Decision Driver sessions. Slight worker startup or execution delay on the Intel host is acceptable because worker sessions are asynchronous; foreground responsiveness for Robert is more valuable on the M4. The 2018 Mac mini cannot remain on the latest macOS track indefinitely, but switching it to Linux now would add T2 and service-migration risk before the current hosting/sync boundaries are fully settled.

## Machine Roles

| Machine | Recommended role | Notes |
| --- | --- | --- |
| Mac Mini M4 2025, 16GB observed on `.35` | Front-facing desk workstation / supplemental worker | Use for current macOS, foreground work, reviews, browser/admin work, approvals, and interactive control surfaces. It can run local tasks from its own git-backed checkouts, but do not make it the main multi-worker AI host unless memory pressure proves acceptable. |
| Mac mini 2018, 64GB, macOS, `.17` | Main AI station and primary worker/server host for now | Host Workspaceboard, Frank/Avignon, Polier, Summarizer, Decision Driver, and long-running Codex workers. Treat it as always-on and service-oriented; background worker delay is acceptable if it keeps Robert's front-facing workstation sessions responsive. |
| Mac mini 2018, 64GB, Linux pilot | Future option only | Evaluate later if macOS security/support limits become the dominant risk. Pilot should verify Codex, Workspaceboard, Node/PHP/Apache, tmux, SSH, git, task intake, and mailbox worker constraints before any cutover. |
| MacBook Pro 2019, 32GB | Front-facing portable workstation / supplemental worker | Use for home/mobile work, emergency fallback, and occasional local tasks from its own git-backed checkouts. Avoid making it the second live writer for the same workspace unless file ownership is explicit. |
| Raetan / Claude server | Server-side analysis layer | Keep Claude as separate reasoning/planning support. Bridge through durable notes, OPS/email, TODOs, handoffs, and later a reviewed MCP/workspace bridge. |

## Current Sync Boundary

### Git-Backed AI Workspace

- AI coordination policy and planning docs now live locally on Mac mini, M4, and MacBook in the private git-backed `/Users/werkstatt/ai_workspace` repo: `AGENTS.md`, `HANDOFF.md`, `TODO.md`, `ToDo-append.md`, `PROJECT_TODOS.md`, `ai-memory-policy.md`, and approved planning notes.
- Worker role docs under `worker_roles/`, including Frank/Avignon/persona/role guidance that needs to follow Robert between machines.
- Project hub records under `project_hub/`, because they are durable cross-machine status and decision logs rather than runtime state.
- Frank/Avignon planning notes, TODOs, approved drafts, and non-secret handoff records.
- Append-only intake queues and lightweight handoff files should move by normal git pull/commit/push flow.

Google Drive is now archive/fallback for the old AI Workspace, not the active sync mechanism.

### Belongs In `/Users/werkstatt` Repos

- Code and implementation workspaces: `workspaceboard`, `ops`, `salesreport`, `bid`, `portal`, `login`, `forge`, `importer`, `lists`, `contactreport`, `eventmanagement`, `donations`, and `braincloud`.
- Repo-local TODOs, module docs, source code, tests, scripts, and deterministic artifacts that belong with the code.
- Workspaceboard source and UI/runtime source. The installed runtime copy remains machine-local.

The default `ws <name>` target should continue to resolve code work to `/Users/werkstatt/<repo>`.

### Git-Only By Default

- Source code, migrations, docs that live with code, tests, scripts, Workspaceboard source, and module-specific implementation changes.
- Cross-machine code and planning movement between M4, 2018 Mac mini, and MacBook should use `git pull --ff-only` / commit / push workflows when the repo has a remote. Mac mini `.17` remains the main AI station and service host; M4 and MacBook remain local front-facing workstations and backup/supplemental worker surfaces.
- If a repo is dirty, inspect before pulling or pushing. Do not overwrite another worker or user's local edits.

### SSH / Rsync / Handoff

- Use SSH or `rsync` for deliberate transfer of non-git artifacts, large generated files, or one-time handoff packages.
- Use written handoff notes in `ai_workspace/HANDOFF.md` or project hub issues when a task crosses machines.
- Avoid silent bidirectional sync of active workspaces. Prefer one named active writer per workspace.

### Machine-Local Only

- LaunchAgents, launchd plists, installed runtime copies, tmux sessions, process state, caches, `node_modules`, virtualenvs, build outputs that can be regenerated, local logs, browser profiles, SSH private keys, API tokens, app passwords, keychain items, OAuth refresh tokens, and `.env` files.
- Frank/Avignon live mailbox automation credentials and live send/check processes should remain on the active host and should not be synced through Drive.
- Do not copy secrets into planning docs. Record only non-secret status and approved credential-reference labels when needed.

## What Else To Move Out Of `ws ai`

- Any code-like external package or prototype that is being edited should become a `/Users/werkstatt/<repo>` workspace or a clearly named external repo clone, not remain buried under `ai_workspace`.
- Browser/board implementation work should live in `/Users/werkstatt/workspaceboard`; any remaining `ai_workspace/codex_dashboard` copy should be treated as legacy/read-only until retired.
- Module-specific implementation notes should move to that module's repo TODO/docs, with only cross-module status and routing decisions summarized back into AI Workspace.
- Large logs, generated output, archives, and reproducible build artifacts should not keep accumulating in `ai_workspace` unless they are intentionally retained as an audit record.

First audit candidates observed in the AI Workspace root:

- `codex_dashboard`: likely legacy board source; confirm whether `/Users/werkstatt/workspaceboard` fully replaces it, then mark read-only or retire.
- `screenbox` and `external/`: code-like packages should be git clones outside Drive if they are still being edited.
- `htdocs`: should not be an active implementation root if the equivalent workspaces now live under `/Users/werkstatt`.
- `.venvs`, `.venv_pdf`, `.playwright-cli`, `tmp`, `tmp-staging`, and `tmp_il_report`: likely machine-local/runtime or temporary material unless a specific audit record says otherwise.
- `recordings` / `recordings 2` and `LOG_imapsync`: keep only intentional audit records in Drive; move bulky generated artifacts out of `ws ai` when they are reproducible or machine-specific.
- `worker_roles (1)`: apparent duplicate of `worker_roles`; review and remove only after confirming it has no unique current role docs.
- `scripts`: audit before moving, because some scripts may still be policy/intake helpers while runtime launch scripts should belong with the relevant repo or machine-local runtime.
- Private credential storage: do not migrate by ad hoc copy. Keep approved credential handling separate from this planning pass and never print secret material in docs or chat.

## Workspaceboard / Phone Access Reliability

- Keep one canonical board host: the Mac mini 2018 on macOS for now.
- Keep Node bound to `127.0.0.1:17878`; expose only the narrow authenticated Apache Workspaceboard path over LAN/VPN.
- Treat remote phone access as a service-health problem: stable VPN hostname/IP, sleep/update discipline, status check for `/api/status`, and clear record of which host is authoritative.
- Do not split Workspaceboard frontend and worker execution across machines until remote worker routing is explicitly designed.
- Use the M4 primarily as the human-facing workstation/client. Let it drive reviews and decisions, while the 2018 Mac mini continues to own long-running board-managed worker execution unless Robert explicitly changes the hosting decision.

## 2026-04-13 Codex Benchmark Note

- `.35` / `Mac.lan` is Apple M4 with 16GB RAM; current Intel Mac mini has an Intel i3-8100B and 64GB RAM.
- Codex CLI startup was faster on `.35`: about `0.05-0.08s` versus about `0.18-0.35s` on the Intel Mac mini.
- A tiny `codex exec` prompt was slightly faster on `.35`: about `4.48s` versus `4.88-6.44s` locally.
- A 100-file shell/file-inspection Codex task was mixed but favored `.35` on the cleaner shell-only pass: first comparable run was effectively tied (`7.94s` remote versus `7.90s` local), while the shell-only pass was faster on `.35` (`6.63s` remote versus `11.06s` local).
- Decision interpretation: use the M4 for Robert's foreground workstation experience, but keep the 64GB Intel Mac mini as the worker/server host because background worker latency matters less than keeping Robert's active workstation responsive.

## Linux Decision

Do not move the 2018 Mac mini to Linux as part of the current transition.

Linux may become attractive if the 2018 Mac mini becomes a headless-only AI appliance and macOS support/security becomes the main constraint. The pilot should be staged on spare disk or an explicitly reversible install, verify all worker and board services, and prove that T2 Mac hardware support does not create operational regressions. Until then, macOS preserves the current known-good LaunchAgent, Homebrew, Apache, browser, mailbox, and Workspaceboard assumptions.

## Next Steps

1. Robert moves daily workstation activity to the M4 and treats it as the main foreground control surface.
2. Keep the 2018 Mac mini as the canonical AI server and Workspaceboard host during the transition.
3. Audit `ai_workspace` for code-like folders and generated/log-heavy folders that should move to `/Users/werkstatt` repos, git remotes, or machine-local storage.
4. Retire or mark legacy/read-only any old `ai_workspace/codex_dashboard` surface after confirming `/Users/werkstatt/workspaceboard` is the source of truth on both machines.
5. For each active repo, confirm whether the authoritative sync path is git remote, SSH/rsync handoff, or local-only runtime.
6. After the M4 is in use, decide whether the 2019 MacBook remains a fallback client or is removed from the active worker set.

## Decision Driver Questions

1. Which machine should be the named canonical Workspaceboard host after Robert starts using the M4: the 2018 Mac mini only, or the 2018 Mac mini with M4 as a manual failover?
2. Should `ai_workspace/codex_dashboard` be marked legacy/read-only now, with all board source work routed to `/Users/werkstatt/workspaceboard`?
3. Which `ai_workspace` subfolders are still active code/prototype work and should be migrated into `/Users/werkstatt` or a git repo first?
