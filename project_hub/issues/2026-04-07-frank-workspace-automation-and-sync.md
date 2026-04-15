# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260407-FRANK-AUTO-01
- Date Opened: 2026-04-07
- Date Completed: 2026-04-08
- Owner: Codex
- Priority: Medium
- Status: Completed

## Scope

Keep Codex sessions anchored to their correct workspaces from the AI workspace board, add a safe first-pass scheduled Frank inbox runner, and define Mac mini sync rules for single-host automation.

## Symptoms

- Board-managed workspace launches were not yet complete for every active workspace.
- Frank mailbox tooling still depended on `/Users/admin/...` path assumptions.
- Frank was documented as manual-only, but the desired operating model now includes controlled scheduled inbox review.

## Root Cause

The board and Frank tooling evolved locally first, then machine-specific paths and automation constraints were left implicit instead of being encoded into shared launch and policy files.

## Repo Logs

### ai_workspace

- Repo Log ID: AI-INC-20260407-FRANK-AUTO-01-AI
- Commit SHA: not a git repo on this machine
- Commit Date: 2026-04-07
- Change Summary:
  - added portable Frank path resolution helpers
  - added `frank_auto_runner.py` plus LaunchAgent install/uninstall scripts
  - expanded dashboard workspace coverage to include Frank and the remaining mapped workspaces
  - documented single-writer Mac mini automation rules

## Verification Notes

- `python3 scripts/frank_auto_runner.py --mode draft-only --dry-run --json` was validated on the intended host during the Mac mini rollout.
- `./scripts/install_frank_launchagent.sh draft-only` installs and loads cleanly on the Mac mini with runtime/state rooted under `~/.frank-launch/`.
- Verified on 2026-04-08 that this MacBook is not running `com.koval.frank-auto`.
- Verified the Mac mini is the intended and active single automation host for Frank.
- Board cards expose `frank`, `ops`, `bid`, and the other mapped target workspaces on this machine.

## Rollback Plan

- Unload and remove `com.koval.frank-auto` with `./scripts/uninstall_frank_launchagent.sh`.
- Revert Frank automation docs to manual-only mode if scheduled behavior is not wanted.
- Remove the new workspace cards if they produce incorrect path mappings on a given machine.

## Follow-Ups

- Decide when `send-clear` should be enabled for a narrow set of receipt/internal follow-up cases.
- Add stronger Robert-only enforcement and richer inbox classification before broader autonomy.
- The Mac mini host verification and single-writer status were recorded in `frank/HANDOFF.md` on 2026-04-08.
