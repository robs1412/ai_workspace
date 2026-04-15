# Email Backup / User Transfer Runbook

Last updated: 2026-04-07 CDT

Purpose: back up a departing user's Gmail mailbox into a shared archive mailbox without filling the live shared inbox.

## Files

- Runbook source files with account-specific credentials live in:
  - `/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/.private/email-backup/`
- Do not paste passwords or app passwords into chat.

## Standard Pattern

Archive into `tastingroom@kovaldistillery.com` under:

- `UserArchive/<First_Last>/Mitch-Inbox`
- `UserArchive/<First_Last>/Mitch-Sent`
- `UserArchive/<First_Last>/[Gmail]/All Mail`
- `UserArchive/<First_Last>/[Gmail]/Drafts`
- `UserArchive/<First_Last>/[Gmail]/Spam`
- `UserArchive/<First_Last>/[Gmail]/Trash`

Avoid syncing directly into the live `INBOX` on the shared mailbox.

## Process

1. Confirm the source mailbox login and app password.
2. Confirm the destination shared mailbox login and app password.
3. Use `imapsync` folder mappings so source `INBOX` maps to `UserArchive/<First_Last>/<Name>-Inbox`.
4. Map source `[Gmail]/Sent Mail` to `UserArchive/<First_Last>/<Name>-Sent`.
5. Sync Gmail system folders into `UserArchive/<First_Last>/[Gmail]/...`.
6. Verify destination counts after sync starts and again when sync ends.
7. Keep optional label-heavy folders separate unless there is a specific need to preserve them.

## Example Folder Mappings

- `INBOX -> UserArchive/Mitch_Donohue/Mitch-Inbox`
- `[Gmail]/Sent Mail -> UserArchive/Mitch_Donohue/Mitch-Sent`
- `[Gmail]/All Mail -> UserArchive/Mitch_Donohue/[Gmail]/All Mail`
- `[Gmail]/Drafts -> UserArchive/Mitch_Donohue/[Gmail]/Drafts`
- `[Gmail]/Spam -> UserArchive/Mitch_Donohue/[Gmail]/Spam`
- `[Gmail]/Trash -> UserArchive/Mitch_Donohue/[Gmail]/Trash`

## Example `imapsync` Shape

Use per-folder syncs when Gmail is slow or when you want tighter control:

```bash
imapsync \
  --gmail1 \
  --user1 SOURCE_USER \
  --passfile1 /path/to/source.pass \
  --gmail2 \
  --user2 DEST_USER \
  --passfile2 /path/to/dest.pass \
  --folder 'INBOX' \
  --f1f2 'INBOX=UserArchive/First_Last/User-Inbox' \
  --maxsize 50000000 \
  --skipsize \
  --nofoldersizes
```

Repeat for `[Gmail]/Sent Mail`, `[Gmail]/All Mail`, `[Gmail]/Drafts`, `[Gmail]/Spam`, and `[Gmail]/Trash`.

## Verification

Check destination message counts by folder over IMAP:

- `UserArchive/<First_Last>/<Name>-Inbox`
- `UserArchive/<First_Last>/<Name>-Sent`
- `UserArchive/<First_Last>/[Gmail]/All Mail`
- `UserArchive/<First_Last>/[Gmail]/Drafts`
- `UserArchive/<First_Last>/[Gmail]/Spam`
- `UserArchive/<First_Last>/[Gmail]/Trash`

## Notes

- `Important` and `Starred` often duplicate content already present in `All Mail`; only sync them if there is a real need.
- Gmail can be slow on large folders. Parallel per-folder syncs are often easier to monitor than one monolithic run.
- Keep credential-bearing files in the hidden private folder only.
