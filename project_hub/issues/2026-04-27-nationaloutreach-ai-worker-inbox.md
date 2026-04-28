# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260427-NATIONALOUTREACH-AI-WORKER-INBOX-01`
- Date Opened: 2026-04-27
- Date Completed: 2026-04-27
- Owner: AI Workspace Task Manager / Email Coordinator
- Priority: Medium
- Status: Completed; full-body/send-capable runtime installed; Codex/National Outreach Drive OAuth and write test completed

## Scope

Set up `nationaloutreach@kovaldistillery.com` as the main shared AI-worker inbox while keeping Frank and Avignon separate. Add the send-from persona registry so every allowed worker `From` identity maps to an organigram role/persona before use. After Robert's follow-up, widen the prepared National Outreach runtime from header-only to full-body review plus approved queued send capability. Robert later clarified not to send as Macee Maddox because she has left, and requested Drive API setup for Codex/National Outreach.

## Symptoms

Robert wanted the National Outreach mailbox to become the central AI-worker inbox without giving each AI worker a separate mailbox account, and wanted allowed send-from addresses tied to worker personas in the organigram.

## Root Cause

The existing role docs treated Outreach Coordinator as Frank-routed only and had no single send-from registry. The existing header-only poll helper also required a `Mail server` field and did not prefer the `App password` credential key.

## Repo Logs

### ai_workspace

- Repo Log ID: local-docs-and-helper-slice
- Commit SHA: not committed in this slice
- Commit Date: n/a
- Change Summary: Added National Outreach worker folder/persona, send-from registry, shared setup note, mailbox setup verifier, header-poll parser updates, full-body/send-capable National Outreach mail cycle, prepared runtime under `/Users/admin/.nationaloutreach-launch/`, and staged LaunchDaemon plist/install helper. Removed Macee as an outbound send-from identity. Prepared Codex/National Outreach Drive API bundle. Updated Outreach Coordinator, Email Coordinator, README, operating model, and `.gitignore`.

## Verification Notes

- Private credential file permissions were tightened before setup verification.
- IMAP SSL login succeeded.
- SMTP SSL login succeeded.
- Standard AI-worker labels were created.
- Header-only polling succeeded for 25 recent headers.
- Manual runtime runner verification succeeded for 200 recent headers.
- Full-body review succeeded for 300 recent INBOX messages.
- Prepared LaunchDaemon runner now uses full-body review plus approved queued send processing.
- No mail was sent because no approved queued send drafts existed.
- `/Library/LaunchDaemons` was not writable from this noninteractive shell and `sudo -n` requires a password, so the system LaunchDaemon was staged but not bootstrapped.
- Later system LaunchDaemon install succeeded after Robert ran the helper.
- `macee.maddox@kovaldistillery.com` is removed from the runtime send allow-list; manual full-body cycle passed after the change.
- Drive API config inspection passed for the Codex/National Outreach bundle.
- Codex/National Outreach Drive OAuth completed for `nationaloutreach@kovaldistillery.com` with the private callback-file method because direct high-port callbacks were blocked and the attempted Workspaceboard relay served PHP source instead of executing it.
- Non-secret `whoami` verification confirms Drive authentication for `nationaloutreach@kovaldistillery.com`.
- Initial shared Drive test reached Drive API but failed for `0AP-Yf32mH4IHUk9PVA` with `teamDriveMembershipRequired`.
- After Robert added National Outreach to the shared Drive, upload succeeded for `nationaloutreach-codex-write-test-2026-04-27.txt`; Drive file ID `10KLYqHsIF3yyvYC2CUZdv8aHIMFDWipH`; link `https://drive.google.com/file/d/10KLYqHsIF3yyvYC2CUZdv8aHIMFDWipH/view?usp=drivesdk`.
- Read-after-write metadata listing confirmed the National Outreach test file is present in shared Drive `0AP-Yf32mH4IHUk9PVA`.
- Robert later named the Outreach Coordinator persona Vanessa Sterling and provided `vanessa.sterling@kovaldistillery.com`. The send-from registry and installed National Outreach send helper now allow Vanessa Sterling as the default Outreach sender through the approved National Outreach mailbox/runtime route.

First body-read review counts:

- Outreach Coordinator: 222.
- Marketing Manager: 49.
- Email Coordinator: 11.
- Internal Communicator: 5.
- Security Guard / sensitive-review: 13.

## Rollback Plan

- Remove the National Outreach send-from entries from `worker_roles/send-from-personas.md`.
- Revert Outreach Coordinator / Email Coordinator routing docs to Frank-only routing if Robert changes the model.
- Boot out `system/com.koval.nationaloutreach-auto` and remove `/Library/LaunchDaemons/com.koval.nationaloutreach-auto.plist` if the staged LaunchDaemon is later installed and needs rollback.

## Follow-Ups

- Add any future Google Workspace send-from aliases to `worker_roles/send-from-personas.md` before enabling them.
- Install the staged LaunchDaemon when an interactive admin prompt is available: `tmp/nationaloutreach-launch/install-launchdaemon.sh`.
- Continue old-mail review in batches beyond the first 300 messages and convert missed work into Outreach/Marketing/Internal task packets.
- If automatic filing or generated external replies are needed, route a separate action-policy/runtime slice through Email Coordinator and Security Guard.
- Migrate the local National Outreach refresh token to the approved Infisical secret path when the non-secret Infisical loader contract is available.
