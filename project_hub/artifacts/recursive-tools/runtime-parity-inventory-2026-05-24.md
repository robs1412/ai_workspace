# Runtime Parity Inventory

- Recorded: 2026-05-24 12:20 CDT
- Scope: repo-local source, installed runtime mirrors, and launch template surfaces

## Totals

- Surfaces checked: 12
- In parity: 11
- Drifted or missing: 0
- Optional installed surfaces absent: 1

## Results

- Source task-flow due runner: `ok`
  - Path: `/Users/werkstatt/ai_workspace/scripts/task_flow_due_runner.py`
  - Expectation: `#!/usr/local/bin/python3.13`
  - Note: Repo-local source should pin the executable interpreter.
- Installed task-flow due runner: `ok`
  - Path: `/Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py`
  - Expectation: `#!/usr/local/bin/python3.13`
  - Note: Installed runtime mirror should match the repo-local pin.
- Source National Outreach cycle: `ok`
  - Path: `/Users/werkstatt/ai_workspace/scripts/nationaloutreach_mail_cycle.py`
  - Expectation: `#!/usr/local/bin/python3.13`
  - Note: Repo-local source should pin the executable interpreter.
- Installed National Outreach cycle: `ok`
  - Path: `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py`
  - Expectation: `#!/usr/local/bin/python3.13`
  - Note: Installed runtime mirror should match the repo-local pin.
- Source AI Health launch template: `ok`
  - Path: `/Users/werkstatt/ai_workspace/scripts/install_ai_health_manager_launchagent.sh`
  - Expectation: `/usr/local/bin/python3.13`
  - Note: Launch template should emit the pinned interpreter.
- Installed AI Health launchagent plist: `missing-optional`
  - Path: `/Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist`
  - Expectation: `/usr/local/bin/python3.13`
  - Note: Installed launchagent should match the template interpreter path.
  - Observed: `missing`
- Source Workspaceboard supervisor helper: `ok`
  - Path: `/Users/werkstatt/workspaceboard/scripts/workspaceboard_supervisor.php`
  - Expectation: `/usr/local/bin/python3.13`
  - Note: Source supervisor should use the pinned helper interpreter.
- Installed Workspaceboard supervisor helper: `ok`
  - Path: `/Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_supervisor.php`
  - Expectation: `/usr/local/bin/python3.13`
  - Note: Installed supervisor should match the repo-local helper interpreter.
- Source Workspaceboard server escalation path: `ok`
  - Path: `/Users/werkstatt/workspaceboard/server/index.js`
  - Expectation: `spawnSync('/usr/local/bin/python3.13'`
  - Note: Source server should pin the AI Manager escalation helper interpreter.
- Source Workspaceboard server AI Health path: `ok`
  - Path: `/Users/werkstatt/workspaceboard/server/index.js`
  - Expectation: `spawn('/usr/local/bin/python3.13'`
  - Note: Source server should pin the AI Health sweep interpreter.
- Installed Workspaceboard server escalation path: `ok`
  - Path: `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js`
  - Expectation: `spawnSync('/usr/local/bin/python3.13'`
  - Note: Installed server should match the escalation helper interpreter pin.
- Installed Workspaceboard server AI Health path: `ok`
  - Path: `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js`
  - Expectation: `spawn('/usr/local/bin/python3.13'`
  - Note: Installed server should match the AI Health interpreter pin.

## Recommendation

- Source and installed runtime code paths are in parity. The next recursive slice should expand this detector and treat missing launch/install state as a separate deployment check.
