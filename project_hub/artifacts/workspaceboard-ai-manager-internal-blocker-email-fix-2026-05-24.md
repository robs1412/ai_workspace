# Workspaceboard AI Manager Internal Blocker Email Fix - 2026-05-24

Robert received a Workspaceboard blocker email that exposed internal session mechanics for AI Manager Control `c689155f` and worker `f27a3d04`.

## Finding

The worker `f27a3d04` had actually received the prompt and later completed with proof, but the immediate hard-start receipt check did not see a working or finished transcript state quickly enough. That temporary proof delay was converted into:

- a blocked AI Manager session
- an owner question asking Robert for a worker/session path
- an owner email through the supervisor path

That was wrong. Internal route/proof timing is Task Manager repair work, not a Robert decision.

## Repair

- Downgraded AI Manager Control `c689155f` back to `working`; no Robert reply is needed.
- Changed the AI Manager route code so hard-start proof delays become `startup_warning` on the route receipt instead of `blocked-exact`.
- Changed the Workspaceboard supervisor so internal route/proof blockers matching hard-start/session-path language are not emailed to owners.
- Tightened AI Manager session detection so a worker title containing `AI Manager` cannot replace the actual AI Manager Control session in `/api/management/overview`.

## Live Readback

After restart:

- `/api/status`: `ok=true`, board `1.09-db`, `tmux_available=true`
- `ai_manager_session`: `c689155f`, `codex-board-c689155f`, `AI Manager Control`, live/working
- `task_manager_session`: `f545298d`, `codex-board-f545298d`, `AI Workspace Task Manager`, live/monitoring

## Files Updated

- `/Users/werkstatt/workspaceboard/server/index.js`
- `/Users/werkstatt/workspaceboard/scripts/workspaceboard_supervisor.php`
- runtime copies under `/Users/admin/.workspaceboard-launch/runtime/app/`
