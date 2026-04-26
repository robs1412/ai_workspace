# AI Health Manager LaunchAgent Activation

- Master Incident ID: `AI-INC-20260421-AI-HEALTH-MANAGER-LAUNCHAGENT-01`
- Date Opened: 2026-04-21 CDT
- Date Completed:
- Owner: AI Workspace / Task Manager
- Priority: Medium
- Status: Prepared; load blocked by unavailable GUI launchd domain and passwordless privileged path

## Scope

Robert approved a separate runtime activation slice for AI Health Manager at an approximately 15-minute cadence, scoped to non-secret Workspaceboard health checks. The slice must preserve standing monitors, mailbox boundaries, credentials, runtime boundaries, and existing dirty worktree state.

## Implementation

Added source-backed health-check tooling:

- `scripts/ai_health_check.py`: reads `http://127.0.0.1:17878/api/status`, classifies standing monitors, stale working sessions, review-ready sessions, needs-input/waiting sessions, and unhealthy sessions, then writes non-secret JSON/Markdown logs.
- `scripts/install_ai_health_manager_launchagent.sh`: generates `/Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` reproducibly from source.

The installed LaunchAgent is report-only by default. It runs:

```text
/usr/bin/python3 /Users/werkstatt/ai_workspace/scripts/ai_health_check.py --log-dir /Users/werkstatt/ai_workspace/tmp/ai-health-manager --status-url http://127.0.0.1:17878/api/status
```

Cadence: `StartInterval` `900` seconds with `RunAtLoad` enabled.

## Runtime State

Prepared and installed plist:

- Label: `com.koval.ai-health-manager`
- Path: `/Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist`
- Log directory: `/Users/werkstatt/ai_workspace/tmp/ai-health-manager`
- Latest report: `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/latest.md`

Actual launchd load is blocked from this session. `scripts/install_ai_health_manager_launchagent.sh --load` stopped before privileged/background fallback because `gui/501` is unavailable from the current background context:

```text
loaded=blocked
blocker=gui/501 launchd domain is unavailable from this session; Robert later clarified Health Manager should use Mac mini server-mode registration, so route Security Guard/runtime review before privileged system LaunchDaemon activation.
```

No `user/501` fallback, sudo, LaunchDaemon migration, Workspaceboard restart, unrelated LaunchAgent change, or privileged workaround was attempted.

2026-04-21 19:33 CDT recheck: the installed plist still linted clean, manual report-only health check succeeded, but `com.koval.ai-health-manager` is still not loaded in `user/501` or `system`. A scoped non-privileged `launchctl bootstrap user/501 /Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` failed with error `5: Input/output error`, and `gui/501` remained unavailable from the background session. No sudo/password path, LaunchDaemon migration, Workspaceboard restart, standing-monitor change, or unrelated LaunchAgent action was performed.

2026-04-21 continuation approval recheck: Robert approved continuing activation for Health Manager only, including a privileged/background-domain LaunchDaemon path if that is the only reliable hard-server option. The active Aqua/gui path is still unavailable from this background session. Manual report-only health check succeeded. Non-privileged `launchctl bootstrap user/501 /Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` and `launchctl bootstrap system /Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` both failed with error `5: Input/output error`. `sudo -n true` returned `sudo: a password is required`, so a privileged install/load cannot be completed from this chat session without interactive local admin password entry. No password was requested or handled, and no LaunchDaemon plist was installed.

2026-04-21/22 final activation attempt: repeated Health Manager-only activation checks after Robert's continuation approval. `gui/501` remained unavailable; `user/501` exists but `launchctl bootstrap user/501 /Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` still failed with error `5`; `launchctl asuser 501 ...` failed with `Operation not permitted`; `sudo -n true` still requires a password; `/Library/LaunchDaemons` is not writable from this session; and legacy `launchctl load -w /Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` did not load the label. `launchctl list`, `launchctl print gui/501/com.koval.ai-health-manager`, and `launchctl print user/501/com.koval.ai-health-manager` all show not loaded/running. No password prompt was handled and no root-owned LaunchDaemon was created.

2026-04-22 canonical registration clarification: Robert clarified Health Manager should be registered like the other Mac mini server-mode workers, not via Aqua login. This supersedes the active-Aqua fallback as the desired registration pattern. Implementation remains in session `c60c4c20` unless coordination is needed. The next implementation slice should create/load only `com.koval.ai-health-manager` as a system LaunchDaemon running as `admin`, preserving the existing source-backed command, `900` second cadence, report-only default, and log path. This clarification does not broaden scope to Frank/Avignon scheduled reports.

2026-04-22 server-mode preparation: inspected the existing worker system LaunchDaemons: `/Library/LaunchDaemons/com.koval.frank-auto.plist` and `/Library/LaunchDaemons/com.koval.avignon-auto.plist`. Both are system LaunchDaemons with `UserName` `admin`, `StartInterval` `15`, and `system/com.koval.*` domains. Updated `scripts/install_ai_health_manager_launchagent.sh` with an explicit `--system` mode. It prepares an analogous Health Manager system plist at `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/com.koval.ai-health-manager.system.plist` with `UserName` `admin`, `StartInterval` `900`, `RunAtLoad`, report-only ProgramArguments, and log paths under `/Users/werkstatt/ai_workspace/tmp/ai-health-manager`. The prepared plist linted clean. `scripts/install_ai_health_manager_launchagent.sh --system --load` stopped with `loaded=blocked` because `/Library/LaunchDaemons` is not writable from this session and no noninteractive privileged path is available. `launchctl print system/com.koval.ai-health-manager` still shows not loaded/running.

## Verification Notes

- `python3 -m py_compile scripts/ai_health_check.py`
- `bash -n scripts/install_ai_health_manager_launchagent.sh`
- `python3 scripts/ai_health_check.py --dry-run --log-dir tmp/ai-health-manager-dry-run`
- `python3 scripts/ai_health_check.py --log-dir tmp/ai-health-manager`
- `plutil -lint /Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist`
- `scripts/install_ai_health_manager_launchagent.sh --load` confirmed load blocker without falling through to privileged/background activation.
- `launchctl print gui/501/com.koval.ai-health-manager` returned `Domain does not support specified action`.
- `launchctl print user/501/com.koval.ai-health-manager` confirmed the service is not loaded.
- 2026-04-21 continuation approval check confirmed `launchctl print system/com.koval.ai-health-manager` also does not find the service.
- Final activation-attempt checks: `launchctl bootstrap user/501 ...`, `launchctl asuser 501 ...`, `sudo -n true`, `/Library/LaunchDaemons` writability check, legacy `launchctl load -w ...`, `launchctl list`, and launchd print checks for `gui/501`, `user/501`, and `com.koval.ai-health-manager`.
- Server-mode checks: inspected Frank/Avignon daemon plists; `launchctl print system/com.koval.frank-auto`; `launchctl print system/com.koval.avignon-auto`; `bash -n scripts/install_ai_health_manager_launchagent.sh`; `scripts/install_ai_health_manager_launchagent.sh --system`; `plutil -lint /Users/werkstatt/ai_workspace/tmp/ai-health-manager/com.koval.ai-health-manager.system.plist`; guarded `scripts/install_ai_health_manager_launchagent.sh --system --load`; `launchctl print system/com.koval.ai-health-manager`.

Latest successful manual report after the 2026-04-22 server-mode preparation: board OK, standing monitors visible, `0` unhealthy sessions, `9` stale working sessions, `17` review-ready sessions, `17` needs-input/waiting sessions, nudge disabled.

## Boundaries Preserved

No mailbox bodies, mailbox mutation, external email, credentials, tokens, private keys, OAuth, Keychain, Google Cloud/PubSub, `.205`, Papers/MI, production systems, deploy, commit, push, reset, clean, Workspaceboard restart, unrelated LaunchAgent mutation, standing-monitor closure, or worker nudge occurred.

## Rollback Plan

Remove `/Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` and the two source files added in `scripts/` if Robert rejects the prepared activation. If the LaunchAgent is later loaded, unload it first from the same launchd domain where it was loaded.

## Follow-Ups

- Preferred remaining physical/admin step after Robert's 2026-04-22 clarification: register Health Manager in Mac mini server mode as a root-owned system LaunchDaemon, running as `admin`, for only `com.koval.ai-health-manager`.
- Robert/admin must enter the admin password locally if needed and run: `sudo install -o root -g wheel -m 644 /Users/werkstatt/ai_workspace/tmp/ai-health-manager/com.koval.ai-health-manager.system.plist /Library/LaunchDaemons/com.koval.ai-health-manager.plist && sudo launchctl bootstrap system /Library/LaunchDaemons/com.koval.ai-health-manager.plist && sudo launchctl kickstart -k system/com.koval.ai-health-manager && launchctl print system/com.koval.ai-health-manager`. Do not request, print, or handle the password in chat.
