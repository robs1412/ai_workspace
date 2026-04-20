# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260420-FRANK-AVIGNON-SCHEDULED-REPORTS-01`
- Date Opened: 2026-04-20
- Date Completed:
- Owner: Frank/Avignon runtime worker, Code/Git/runtime closeout as needed
- Priority: High
- Status: Open / blocked on human-entered privileged launchd action or Aqua/user-session service loading

## Scope

Bounded Robert-approved runtime-health/remediation task for Frank/Avignon scheduled reports on the Mac mini.

Approved actions were limited to inspecting existing Frank/Avignon scheduled-report LaunchAgents, updating installed non-secret LaunchAgent plist metadata/environment/log-path configuration as needed, reloading/kickstarting only those existing scheduled-report LaunchAgents as needed, fixing scheduled-report helper environment/log path issues, ensuring Avignon has its own scheduled-report path/status, verifying health, and recording state.

## Symptoms

- Sunday EOD and Monday AM reports were missing after Mac mini reboot.
- Prior incident work found manual catch-up sends already completed.
- Installed scheduled-report plists were enabled but not loaded as launchd services from the current shell context after reboot/logged-out state.
- Only installed report labels found were `com.koval.frank-morning-overview` and `com.koval.avignon-morning-overview`; no installed `*-evening-roundup` labels were present.

## Root Cause

Primary finding: user LaunchAgents did not load after reboot/logged-out/non-Aqua state. `launchctl print-disabled user/501` showed both report labels enabled, but `launchctl print user/501/<label>` could not find either service, and `launchctl print gui/501/<label>` reported that the domain did not support the action.

Secondary finding: installed Avignon scheduled-report plist had only a 06:00 `StartCalendarInterval`, while the existing runtime template already had both 06:00 and 18:00 entries.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260420-FRANK-AVIGNON-SCHEDULED-REPORTS-01`
- Commit SHA: not committed
- Commit Date:
- Change Summary: updated local non-secret TODO/HANDOFF/project state only.

### Machine-Local Runtime

- Repo Log ID: `AI-INC-20260420-FRANK-AVIGNON-SCHEDULED-REPORTS-01-RUNTIME`
- Commit SHA: not applicable
- Commit Date:
- Change Summary:
  - Updated installed plist `/Users/admin/Library/LaunchAgents/com.koval.avignon-morning-overview.plist` so `StartCalendarInterval` now includes both 06:00 and 18:00, matching the existing runtime template.
  - Left `/Users/admin/Library/LaunchAgents/com.koval.frank-morning-overview.plist` functionally unchanged after testing; it already had both 06:00 and 18:00.
  - Did not change `com.koval.frank-auto` or `com.koval.avignon-auto`.

## Verification Notes

- `plutil -lint` passed for both installed scheduled-report plists.
- State/log directories for Frank and Avignon exist and are writable by `admin`.
- Recent launchd stdout logs show scheduled report sends through Sunday, April 19, but no Monday scheduled run.
- Installed plists now show:
  - `com.koval.frank-morning-overview`: 06:00 and 18:00, existing Frank runtime/log paths.
  - `com.koval.avignon-morning-overview`: 06:00 and 18:00, Avignon-specific runtime/log paths.
- Dry-run helper invocations completed for both assistants using explicit EOD report mode and installed environment paths. No report email was sent.
  - Dry-run artifacts: `/Users/admin/.frank-launch/state/drafts/frank-eod-summary-2026-04-20.txt`, `/Users/admin/.avignon-launch/state/drafts/avignon-eod-summary-2026-04-20.txt`, and dry-run automation-log entries in the corresponding machine-local state logs.
- `launchctl enable user/501/<label>` completed for both labels.
- `launchctl bootstrap user/501 <plist>` failed with error `5: Input/output error` for both labels.
- `launchctl bootstrap gui/501 <plist>` failed with error `125: Domain does not support specified action` for both labels.
- Legacy `launchctl load -w <plist>` exited `134` for both labels.
- Non-interactive privileged bootstrap was not available: `sudo -n` returned `sudo: a password is required`.
- 2026-04-20 privileged-slice recheck from source `<CAAtX44aeM-Rb_Oo0Hw=iS2ALsjOprLqHk09xmn5snW2rd=_HXA@mail.gmail.com>`:
  - `user/501` exists as a background launchd domain, but neither scheduled-report label is loaded.
  - `gui/501` remains unavailable from this session.
  - Non-sudo `launchctl bootstrap user/501` still fails with error `5` for both labels.
  - `launchctl asuser 501 ...` fails because switching to the audit session is not permitted.
  - `sudo -n launchctl bootstrap user/501 ...` fails because sudo requires a password.
  - Explicit EOD dry-runs for both helpers completed with exit `0` and did not send.

## Rollback Plan

If needed, revert the installed Avignon plist schedule to a single 06:00 `StartCalendarInterval`. No credential, mailbox, OAuth, Google Cloud, daemon cadence, production deploy, code push, or polling daemon setting was changed.

## Follow-Ups

- Remaining blocker: load/reload requires either an active Aqua/gui user session or a human-entered privileged launchd action. Do not prompt for or handle a password in chat.
- Safe human action: Robert/admin can either log into the Mac mini Aqua/gui session and load the two existing LaunchAgents there, or enter the admin password locally for a narrowly scoped privileged action that migrates/loads only `com.koval.frank-morning-overview` and `com.koval.avignon-morning-overview`.
- Durable logged-out reboot behavior still needs the approved hard-server-mode approach executed from a privileged local context, such as a LaunchDaemon-compatible scheduled-report wrapper for only these two jobs, with dry-run/no-send verification before enabling live scheduled sends.
- Completion report should state that no secrets, credential contents, mailbox bodies, OAuth, Google Cloud/PubSub/IAM, DNS/TLS/router, `.205`, Workspaceboard runtime, production deployments, code commits/pushes, polling cadence, or Frank/Avignon inbox polling daemons were changed.
