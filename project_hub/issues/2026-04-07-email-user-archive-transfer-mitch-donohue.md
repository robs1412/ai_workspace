# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260407-EMAIL-ARCHIVE-TRANSFER-01
- Date Opened: 2026-04-07
- Date Completed: 2026-04-15
- Owner: Codex
- Priority: Medium
- Status: Completed by Robert decision

## Scope

Archive `mitchell.donohue@kovaldistillery.com` into `tastingroom@kovaldistillery.com` under `UserArchive/Mitch_Donohue/...` without filling the live tastingroom inbox.

Also document the workflow in `ai_workspace` and move credential-bearing reference files from Desktop into a safer workspace location.

## Symptoms

- Need to preserve a departing user's mailbox.
- Shared destination inbox must stay usable and must not receive the archived mail directly.
- Source reference files initially lived on Desktop.

## Root Cause

No existing local runbook in `ai_workspace` for this transfer pattern, and the initial raw credential/reference files were stored in an unsafe transient location.

## Repo Logs

### ai_workspace

- Repo Log ID: AI-INC-20260407-EMAIL-ARCHIVE-TRANSFER-01-AI
- Commit SHA:
- Commit Date:
- Change Summary:
  - Added `email-backup-transfer-runbook.md`.
  - Moved source/reference files into `.private/email-backup/` with restricted permissions.
  - Started controlled `imapsync` transfer into `UserArchive/Mitch_Donohue/...`.

## Verification Notes

- Destination path uses archive-only folders:
  - `UserArchive/Mitch_Donohue/Mitch-Inbox`
  - `UserArchive/Mitch_Donohue/Mitch-Sent`
  - `UserArchive/Mitch_Donohue/[Gmail]/All Mail`
  - `UserArchive/Mitch_Donohue/[Gmail]/Drafts`
  - `UserArchive/Mitch_Donohue/[Gmail]/Spam`
  - `UserArchive/Mitch_Donohue/[Gmail]/Trash`
- Live `tastingroom` inbox is not the target of the transfer.
- Current status snapshot at 2026-04-07 13:05:26 CDT:
  - Running:
    - `INBOX -> Mitch-Inbox`
    - `Sent Mail -> Mitch-Sent`
    - `All Mail -> [Gmail]/All Mail`
  - Destination counts:
    - `Mitch-Inbox`: 1449
    - `Mitch-Sent`: 943
    - `All Mail`: 2330
    - `Drafts`: 2
    - `Spam`: 11
    - `Trash`: 38
- Verification review update: `2026-04-08 13:23:39 CDT` (Machine: `RobertMBP-2.local`)
  - Reviewed all local Mitch `imapsync` logs under `LOG_imapsync/`.
  - Dry-run sizing log shows source counts for the key mapped folders:
    - `INBOX`: 1941
    - `[Gmail]/Sent Mail`: 2465
    - `[Gmail]/All Mail`: 9563
    - `[Gmail]/Drafts`: 3
    - `[Gmail]/Spam`: 11
    - `[Gmail]/Trash`: 38
  - The only non-dry-run transfer logs both ended early with `Exiting with return value 6 (EXIT_BY_SIGNAL)`.
  - Logged partial results show the archive was still incomplete when those runs stopped:
    - `09:25` run synced only `2/24` folders and reported `1501` messages still missing from `Charitable`.
    - `09:28` run synced only `1/8` folders and reported `1935` messages still missing from `Mitch-Inbox`.
  - The last project snapshot destination counts also remain below source counts for the major mapped folders:
    - `Mitch-Inbox`: `1449` vs source `INBOX` `1941`
    - `Mitch-Sent`: `943` vs source `[Gmail]/Sent Mail` `2465`
    - `All Mail`: `2330` vs source `[Gmail]/All Mail` `9563`
    - `Drafts`: `2` vs source `3`
    - `Spam`: `11` vs source `11`
    - `Trash`: `38` vs source `38`
  - Conclusion: the archive cannot be confirmed complete from the available logs and notes, so `mitchell.donohue@kovaldistillery.com` should not be deleted yet.
- Restart attempt update: `2026-04-08 14:01:01 CDT` (Machine: `Macmini.lan`)
  - Relaunched `imapsync` on the Mac mini using the intended Mitch archive folder mappings.
  - Source login for `mitchell.donohue@kovaldistillery.com` succeeded.
  - Destination login for `tastingroom@kovaldistillery.com` failed with `AUTHENTICATIONFAILED`.
  - Conclusion: the current secure destination app-password reference for `tastingroom@kovaldistillery.com` appears stale and must be refreshed before the archive sync can continue.
  - Project state changed to postponed / waiting-for-next-step until the destination credential reference is refreshed.
- Reassessment update: `2026-04-10` (Machine: `Macmini.lan`)
  - Re-read the current secure email secret references and verified live IMAP login again.
  - Source login for `mitchell.donohue@kovaldistillery.com` now succeeds.
  - Destination login for `tastingroom@kovaldistillery.com` now also succeeds with the current secured secret reference.
  - No active `imapsync` process was running at the time of reassessment.
  - Current live counts:
    - Source `INBOX`: `1941`
    - Source `[Gmail]/Sent Mail`: `2465`
    - Source `[Gmail]/All Mail`: `9563`
    - Source `[Gmail]/Drafts`: `3`
    - Source `[Gmail]/Spam`: `7`
    - Source `[Gmail]/Trash`: `28`
    - Destination `UserArchive/Mitch_Donohue/Mitch-Inbox`: `46`
    - Destination `UserArchive/Mitch_Donohue/Mitch-Sent`: `29`
    - Destination `UserArchive/Mitch_Donohue/[Gmail]/All Mail`: `9562`
    - Destination `UserArchive/Mitch_Donohue/[Gmail]/Drafts`: `0`
    - Destination `UserArchive/Mitch_Donohue/[Gmail]/Spam`: `11`
    - Destination `UserArchive/Mitch_Donohue/[Gmail]/Trash`: `38`
  - Additional destination folders currently present:
    - `UserArchive/Mitch_Donohue/[Gmail]/Important`: `0`
    - `UserArchive/Mitch_Donohue/[Gmail]/Starred`: `0`
  - Conclusion: the prior destination-credential blocker is cleared, so the transfer can now proceed. The remaining blocker is operational verification and rerun work: `Mitch-Inbox`, `Mitch-Sent`, `Drafts`, `Spam`, and `Trash` are not aligned with source counts, and `[Gmail]/All Mail` is still short by `1`.

## Rollback Plan

- Stop the active `imapsync` processes if needed.
- Delete the `UserArchive/Mitch_Donohue/...` folder tree from `tastingroom@kovaldistillery.com` if a clean restart is required.
- Re-run only the intended archive folder mappings.

## Follow-Ups

- Closed by Robert on 2026-04-15. Do not run additional mailbox, credential, or `imapsync` work for this project unless Robert reopens it explicitly.
- Historical count gaps above remain as recorded audit context, not an active task queue.
