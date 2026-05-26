# Deployment State Inventory

- Recorded: 2026-05-24 12:28 CDT
- Scope: installed launchd plists, wrapper targets, and visible launchctl readback

## Totals

- Surfaces checked: 13
- OK: 11
- Drift: 2
- Optional missing: 0

## Results

- AI Health system plist exists: `ok`
  - Expectation: `exists`
  - Note: AI Health is currently installed as a system LaunchDaemon on this machine.
  - Observed: `exists`
  - Path: `/Library/LaunchDaemons/com.koval.ai-health-manager.plist`
- AI Health system plist interpreter: `drift`
  - Expectation: `/usr/local/bin/python3.13`
  - Note: Installed AI Health daemon plist should match the pinned 3.13 launch template.
  - Observed: `expected text not present`
  - Path: `/Library/LaunchDaemons/com.koval.ai-health-manager.plist`
- AI Health live launchctl interpreter: `drift`
  - Expectation: `program = /usr/local/bin/python3.13`
  - Note: Running AI Health daemon should expose the pinned interpreter in live launchctl readback.
  - Observed: `expected text not present`
  - Command: `launchctl print system/com.koval.ai-health-manager`
- National Outreach daemon plist exists: `ok`
  - Expectation: `exists`
  - Note: National Outreach service should be installed as a system LaunchDaemon.
  - Observed: `exists`
  - Path: `/Library/LaunchDaemons/com.koval.nationaloutreach-auto.plist`
- National Outreach wrapper target: `ok`
  - Expectation: `/Library/KOVAL/bin/nationaloutreach-auto`
  - Note: National Outreach daemon should launch through the approved wrapper path.
  - Observed: `/Library/KOVAL/bin/nationaloutreach-auto`
  - Path: `/Library/LaunchDaemons/com.koval.nationaloutreach-auto.plist`
- National Outreach wrapper exists: `ok`
  - Expectation: `exists`
  - Note: The wrapper referenced by the LaunchDaemon should exist on disk.
  - Observed: `exists`
  - Path: `/Library/KOVAL/bin/nationaloutreach-auto`
- Task Flow daemon plist exists: `ok`
  - Expectation: `exists`
  - Note: Task Flow reminders should be installed as a system LaunchDaemon.
  - Observed: `exists`
  - Path: `/Library/LaunchDaemons/com.koval.task-flow-reminders.plist`
- Task Flow wrapper target: `ok`
  - Expectation: `/Users/admin/.task-flow-launch/runtime/run_task_flow_due_runner.sh`
  - Note: Task Flow daemon should point at the installed runtime wrapper.
  - Observed: `/Users/admin/.task-flow-launch/runtime/run_task_flow_due_runner.sh`
  - Path: `/Library/LaunchDaemons/com.koval.task-flow-reminders.plist`
- Task Flow wrapper exists: `ok`
  - Expectation: `exists`
  - Note: The Task Flow installed runtime wrapper should exist on disk.
  - Observed: `exists`
  - Path: `/Users/admin/.task-flow-launch/runtime/run_task_flow_due_runner.sh`
- Workspaceboard user plist exists: `ok`
  - Expectation: `exists`
  - Note: Workspaceboard user LaunchAgent should exist on disk.
  - Observed: `exists`
  - Path: `/Users/admin/Library/LaunchAgents/com.koval.workspaceboard.plist`
- Workspaceboard automation user plist exists: `ok`
  - Expectation: `exists`
  - Note: Workspaceboard automation LaunchAgent should exist on disk.
  - Observed: `exists`
  - Path: `/Users/admin/Library/LaunchAgents/com.koval.workspaceboard-automation.plist`
- Workspaceboard launch wrapper exists: `ok`
  - Expectation: `exists`
  - Note: Workspaceboard installed launch wrapper should exist on disk.
  - Observed: `exists`
  - Path: `/Users/admin/.workspaceboard-launch/runtime/scripts/launch_codex_dashboard_agent.sh`
- Workspaceboard automation wrapper exists: `ok`
  - Expectation: `exists`
  - Note: Workspaceboard automation wrapper should exist on disk.
  - Observed: `exists`
  - Path: `/Users/admin/.workspaceboard-launch/runtime/scripts/run_workspaceboard_automation.sh`

## Recommendation

- Deployment drift exists even though source/runtime code parity is clean. The next recursive step should be a narrow deployment reconcile plan for the drifted service surfaces, starting with AI Health.
