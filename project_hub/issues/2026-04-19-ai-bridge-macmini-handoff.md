# AI Bridge Mac Mini Handoff

- Master ID: `AI-INC-20260419-CODEX-CLAUDE-PAPERS-01`
- Date: 2026-04-19
- Source machine: `RobertMBP-2.local`
- Target handoff host: Mac mini `.17`
- Status: local docs/organigram/drafts prepared; Mac mini direct SSH was reachable but rejected this machine's key

## What Changed Locally

- Added AI Manager roles:
  - `worker_roles/ai-manager-robert.md`
  - `worker_roles/ai-manager-dmytro.md`
- Updated the active worker operating model so AI Manager Robert/Dmytro query Task Manager first, then Task Manager routes down to Codex workers or Claude agents.
- Added the shared task-record spine based on Claude's `task #1361` / `ref:2379` response pattern:
  - task id;
  - source ref;
  - requester;
  - assigned role/agent;
  - priority;
  - status;
  - deliverable bullets;
  - next update promise;
  - source links;
  - approval gates;
  - single-writer owner.
- Updated the Codex/Claude/Papers integration plan to prefer OPS/Portal task IDs as canonical task identities when available.
- Updated Workspaceboard organigram source in the `workspaceboard` repo so AI Manager Robert and AI Manager Dmytro show above the Task Manager chain.
- Prepared a Frank-to-Claude draft:
  - `frank/drafts/claude-codex-organigram-work-record-bridge-2026-04-19.txt`
  - local task id `frank-2026-claude-codex-organigram-work-record-bridge`

## Runtime Checks From MacBook

- `.17` is reachable again by ping.
- `.17` ports `22`, `80`, and `17878` are open or responding.
- Direct unauthenticated Workspaceboard API returns the expected auth gate.
- `wb.koval.lan/workspaceboard/api/status` redirects to `mi.koval.lan` login as expected.
- Direct SSH from this MacBook as `admin@192.168.55.17` failed with `Permission denied (publickey)`, so no Mac mini files, LaunchAgents, mailbox state, runtime state, or services were changed from this handoff pass.

## Mac Mini Next Steps

When working directly on `.17`:

1. Pull the latest `ai_workspace` and `workspaceboard` commits.
2. In `workspaceboard`, reinstall/restart the local Workspaceboard runtime only if the pulled source changed the installed runtime:
   - `./scripts/install_codex_dashboard_launchagent.sh 17878`
   - verify `http://127.0.0.1:17878/api/status`
3. Verify `worker-organigram.php` includes:
   - `ai-manager-robert`
   - `ai-manager-dmytro`
   - `codex-integration-manager`
   - `codex-local-agent`
   - `claude-server-agent`
   - `claude-205-structure`
4. Restart or recreate the standing Frank worker if it is not live, without closing other standing monitors.
5. Send the queued Frank draft to Claude only through the approved Frank send helper/runtime:
   - source draft: `frank/drafts/claude-codex-organigram-work-record-bridge-2026-04-19.txt`
   - recipient: Claude
   - copy Robert and Dmytro if the approved existing-thread recipient resolution supports it
   - record sent Message-ID and sent-log task id in `frank/HANDOFF.md`
6. Do not touch `.205`, OAuth, MI/Papers writes, Portal/CRM mutation, mailbox credentials, MCP exposure, or production services from this handoff unless Robert separately approves.

## Recommended Next Local/Runtime Slice

Build the no-write Workspaceboard work-record projection using the shared task-record spine. It should read TODO/project-hub/Workspaceboard metadata and emit sanitized JSON. It should not write Papers/MI until the schema, single-writer contract, and Security Guard gates are approved.
