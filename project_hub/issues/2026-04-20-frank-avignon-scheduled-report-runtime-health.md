# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260420-FRANK-AVIGNON-SCHEDULED-REPORTS-01`
- Date Opened: 2026-04-20
- Date Completed: 2026-04-22
- Owner: Frank/Avignon runtime worker, Code/Git/runtime closeout as needed
- Priority: High
- Status: Completed / accepted for monitoring; no further immediate launchd action unless a scheduled send actually fails

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
  - 2026-04-21 canonical email-auto registration cleanup did not change the system LaunchDaemon plist contents for `com.koval.frank-auto` or `com.koval.avignon-auto`; it quarantined only the stale duplicate user LaunchAgent plist files to `/Users/admin/Library/LaunchAgents/quarantine-frank-avignon-auto-20260421/`.

## Verification Notes

- 2026-04-22 06:56 CDT approved canonical registration-fix attempt:
  - Robert approved proceeding from diagnosis/recommendation to a scoped Frank/Avignon registration fix.
  - Confirmed `com.koval.frank-auto` and `com.koval.avignon-auto` remain canonical system LaunchDaemons in `/Library/LaunchDaemons`, running as `admin`, run interval `15` seconds, last exit `0`. Latest check saw Frank between interval runs (`runs = 11097`) and Avignon running (`pid = 8330`, `runs = 11825`).
  - Confirmed stale duplicate auto user plists remain absent from `/Users/admin/Library/LaunchAgents`; preserved quarantined backups remain under `/Users/admin/Library/LaunchAgents/quarantine-frank-avignon-auto-20260421/`.
  - Confirmed report labels are still not loaded: `launchctl print system/com.koval.frank-morning-overview`, `launchctl print user/501/com.koval.frank-morning-overview`, `launchctl print system/com.koval.avignon-morning-overview`, and `launchctl print user/501/com.koval.avignon-morning-overview` could not find the services.
  - Existing user LaunchAgent report plists still exist and lint clean, but no system LaunchDaemon report plists exist under `/Library/LaunchDaemons`.
  - Prepared server-mode plist payloads:
    - `/Users/werkstatt/ai_workspace/tmp/frank-avignon-registration/com.koval.frank-morning-overview.system.plist`
    - `/Users/werkstatt/ai_workspace/tmp/frank-avignon-registration/com.koval.avignon-morning-overview.system.plist`
  - Both prepared plists lint clean, include `UserName=admin`, use existing helper scripts, existing log paths, and the existing 06:00/18:00 schedules, and omit `RunAtLoad` to avoid immediate send at bootstrap.
  - Helper verification completed with no send: Frank morning dry-run, Frank EOD dry-run, Avignon morning dry-run, and Avignon EOD dry-run.
  - Board standing sessions remained open: `eadc2912` / Frank and `cf7294fb` / Avignon, both `working` / `monitoring`.
  - Inbox/log metadata after the attempt: Frank still holds the routed `Re: Frank morning catch-up: Tuesday, April 21` item in session `163484af` and does not archive it; Avignon latest cycles still report `inbox_count_start = 2`, `inbox_count_end = 2`, `handled_archived_count = 0`.
  - Blocker: `/Library/LaunchDaemons` is not writable from this session and `sudo -n` is unavailable. No password was requested or handled, no report LaunchDaemon was installed/loaded, and no mailbox content was printed or changed.
  - Exact physical commands for Robert/admin:

```bash
sudo install -o root -g wheel -m 644 /Users/werkstatt/ai_workspace/tmp/frank-avignon-registration/com.koval.frank-morning-overview.system.plist /Library/LaunchDaemons/com.koval.frank-morning-overview.plist
sudo install -o root -g wheel -m 644 /Users/werkstatt/ai_workspace/tmp/frank-avignon-registration/com.koval.avignon-morning-overview.system.plist /Library/LaunchDaemons/com.koval.avignon-morning-overview.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.koval.frank-morning-overview.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.koval.avignon-morning-overview.plist
launchctl print system/com.koval.frank-morning-overview
launchctl print system/com.koval.avignon-morning-overview
```

- 2026-04-21 21:00 CDT canonical email-auto registration cleanup:
  - Canonical labels and paths are `system/com.koval.frank-auto` from `/Library/LaunchDaemons/com.koval.frank-auto.plist` and `system/com.koval.avignon-auto` from `/Library/LaunchDaemons/com.koval.avignon-auto.plist`.
  - `plutil -lint` passed for both system LaunchDaemons and for both quarantined backup plists.
  - Both system LaunchDaemons run as `admin`, have `StartInterval`/run interval `15`, use runtime scripts under `/Users/admin/.frank-launch/runtime/scripts/` and `/Users/admin/.avignon-launch/runtime/scripts/`, and write logs under `/Users/admin/.frank-launch/state/` and `/Users/admin/.avignon-launch/state/`.
  - Post-cleanup `launchctl print system/com.koval.frank-auto`: state `not running` between interval runs, `runs = 9483`, `last exit code = 0`.
  - Post-cleanup `launchctl print system/com.koval.avignon-auto`: state `running` during the check, `pid = 43438`, `runs = 10437`, `last exit code = 0`.
  - Stale duplicate user LaunchAgent plists were moved, not deleted: `/Users/admin/Library/LaunchAgents/quarantine-frank-avignon-auto-20260421/com.koval.frank-auto.plist.quarantined-20260421` and `/Users/admin/Library/LaunchAgents/quarantine-frank-avignon-auto-20260421/com.koval.avignon-auto.plist.quarantined-20260421`.
  - No active duplicate user plist remains at `/Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist` or `/Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist`; `launchctl print user/501/com.koval.frank-auto` and `launchctl print user/501/com.koval.avignon-auto` could not find user-domain services.
  - Standing monitor sessions were preserved: `eadc2912` / `Frank email worker - inbox and task flow restart` and `cf7294fb` / `Avignon email worker - inbox and task flow restart`, both `working` / `monitoring`.
  - Inbox/log reconciliation used non-secret metadata only. Frank remains `1` open / `1` unread because source `Re: Frank morning catch-up: Tuesday, April 21` is still routed pending completion in session `163484af` (`working`) and is not archivable yet. Avignon remains `2` open / `2` unread because stale Meet Statio direct-owner wrapper sessions are still held by the runtime even though local Avignon state records completion reports and the actual work session `e8c478ac` is `finished` / `review-ready`; no bulk filing was performed.
  - Remaining blocker from this slice: Avignon needs a narrow worker/runtime-state reconciliation for the two Meet Statio holds before they can be filed under the direct-owner guardrails; Frank's held item must complete or block in its visible worker before filing.
  - No sudo/password prompt, LaunchDaemon restart/reload, Workspaceboard restart, OAuth/Google Cloud/PubSub/IAM, DNS/TLS/router/`.205`, deploy, commit/push, scheduled-report LaunchAgent or Health Manager change, mailbox body output, credential output, standing-monitor closure, or bulk mailbox filing was performed.

- 2026-04-22 06:43 CDT no-morning-update registration gap:
  - Task Manager reported Robert received no morning update on 2026-04-22.
  - `launchctl print system/com.koval.frank-morning-overview` and `launchctl print user/501/com.koval.frank-morning-overview` could not find the service; `gui/501` was unavailable from this session.
  - `launchctl print system/com.koval.avignon-morning-overview` and `launchctl print user/501/com.koval.avignon-morning-overview` could not find the service; `gui/501` was unavailable from this session.
  - User LaunchAgent plist files exist and lint clean: `/Users/admin/Library/LaunchAgents/com.koval.frank-morning-overview.plist` and `/Users/admin/Library/LaunchAgents/com.koval.avignon-morning-overview.plist`. Both contain 06:00 and 18:00 `StartCalendarInterval` entries and point to the existing morning overview helper scripts.
  - No system LaunchDaemon plist exists at `/Library/LaunchDaemons/com.koval.frank-morning-overview.plist` or `/Library/LaunchDaemons/com.koval.avignon-morning-overview.plist`.
  - Sent-log/log metadata did not show a 2026-04-22 Frank morning overview send or a 2026-04-22 Avignon morning summary send. One-time catch-up report workers were routed separately as `a321d491` / Frank and `eecdae66` / Avignon and were not handled in this cleanup slice.
  - No report-service load, migration, privileged action, runtime edit, scheduled-send attempt, or catch-up send was performed.
  - Recommended fix: run a separate runtime/Security Guard-approved implementation slice to make report services canonical. Preferred durable hard-server fix is to create/load system LaunchDaemons for only `com.koval.frank-morning-overview` and `com.koval.avignon-morning-overview`, running as `admin`, preserving existing helper scripts, environment, duplicate protection, and log paths, with dry-run/no-send verification before live schedule enablement. Alternative documented path is an active-Aqua/gui load procedure Robert/admin runs after login/reboot, but that does not solve logged-out reboot durability.

- 2026-04-21 19:33 CDT scoped hard-server remediation recheck:
  - `com.koval.frank-auto` and `com.koval.avignon-auto` are loaded as system LaunchDaemons from `/Library/LaunchDaemons`, running as user `admin`, with `StartInterval`/run interval `15` seconds and last exit code `0`.
  - Non-privileged `launchctl kickstart -k system/com.koval.frank-auto` and `launchctl kickstart -k system/com.koval.avignon-auto` were attempted inside the approved label scope and failed with `Operation not permitted`; no sudo/password path was used. Both labels were already running afterward.
  - No system LaunchDaemon exists for `com.koval.frank-morning-overview`, `com.koval.avignon-morning-overview`, or `com.koval.ai-health-manager`.
  - User-domain `launchctl bootstrap user/501` still failed with error `5` for the scheduled-report labels and Health Manager label. `gui/501` remains unavailable from this background session.
  - `launchctl print user/501/<label>` could not find the scheduled-report labels or Health Manager label. `launchctl print system/<label>` could not find those three labels either.
  - Metadata-only inbox counts after the recheck: Frank `INBOX=1`, unread `1`; Avignon `INBOX=2`, unread `2`.
  - Frank standing board worker `eadc2912` / `Frank email worker - inbox and task flow restart` is visible, live, and monitoring.
  - Non-secret dry-runs for the Frank and Avignon report helpers completed without sending.
  - No mailbox bodies, credentials, OAuth/PubSub/IAM/Google Cloud, DNS/TLS/router, `.205`, Workspaceboard runtime, production deploy, code commit/push, broad mailbox filing, standing monitor closure, or unrelated LaunchAgent change was performed.

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

- 2026-04-22 Robert response for launchd blocker item 3: current state is fine; if Robert does not get the scheduled report, he will let us know. Reconciled as no further immediate blocker. Current registered server-mode workers are the canonical Frank/Avignon auto system LaunchDaemons:
  - `system/com.koval.frank-auto`: `/Library/LaunchDaemons/com.koval.frank-auto.plist`, user `admin`, run interval `15`, runs `11982`, last exit `0`.
  - `system/com.koval.avignon-auto`: `/Library/LaunchDaemons/com.koval.avignon-auto.plist`, user `admin`, run interval `15`, runs `12891`, last exit `0`.
  - AI Health Manager manual check at `2026-04-22T20:17:50Z`: board OK, `0` unhealthy, board remediation not needed.
  - Prepared scheduled-report server-mode plists remain available under `/Users/werkstatt/ai_workspace/tmp/frank-avignon-registration/`, but no further launchd registration/loading should be attempted unless a scheduled send actually fails.
  - No launchd changes, service restart, deploy, commit/push, mailbox move, OAuth/PubSub, Workspaceboard restart, credential access, or standing monitor closure was performed for this reconciliation.

- 2026-04-21 Frank direct-owner continuation source `<CAAtX44aGBmmx-JgqXBYAzwdO3TSifKpcO_hmr53ZSyFtKozc6g@mail.gmail.com>` was routed into visible AI Workspace session `75421822` / `Frank hard-server launchd remediation intake`. The worker inspected only non-secret local TODO/HANDOFF/project state and confirmed this remains a privileged runtime blocker, not a normal Frank/Avignon code fix. No runtime/system state changed.
- Historical blocker: load/reload required either an active Aqua/gui user session or a human-entered privileged launchd action. Per Robert's 2026-04-22 response, do not continue this as an immediate blocker unless a scheduled send actually fails.
- Safe future action if reopened by a missed scheduled report: Robert/admin can either log into the Mac mini Aqua/gui session and load the two existing LaunchAgents there, or enter the admin password locally for a narrowly scoped privileged action that migrates/loads only `com.koval.frank-morning-overview` and `com.koval.avignon-morning-overview`.
- Durable logged-out reboot behavior remains a prepared option, not an active blocker, until a scheduled send actually fails.
- Completion report should state that no secrets, credential contents, mailbox bodies, OAuth, Google Cloud/PubSub/IAM, DNS/TLS/router, `.205`, Workspaceboard runtime, production deployments, code commits/pushes, polling cadence, or Frank/Avignon inbox polling daemons were changed.
