# Recovery backup controller

The controller creates **two independent encrypted restic repositories**, one on
.205 over SFTP and one in the AI Cloud shared Drive through rclone. Either
repository can restore without the other. Existing daily metadata backup remains
untouched. No LaunchDaemon or retention deletion is enabled. On October 21,
both live encrypted repositories were initialized after the recovery key was
independently saved and verified. PostgreSQL rehearsal exports passed; these
temporary exports were removed and are not completed backups.

## First production launch

`launch_backup.py --now --allow-database-write-locks` requires administrator
execution and explicit approval for the write-lock window. It verifies the
saved-key and database-preflight receipts, then runs the first backup detached
from SSH. `--at HH:MM` selects the next occurrence in the Mac's local timezone.
The process survives SSH disconnect, but not reboot. No recurring job is installed.
Read `tmp/recovery-backup-review/activation-status.json` for metadata-only status;
only `verified_both` means both destinations passed snapshot and restore checks.

The launch helper supplies one-run authorization in memory; the stored controller
configuration remains disabled for unattended generic invocations. It checks at
least 25 GiB free initially, and database/SQLite staging continuously preserves
15 GiB free. This is an enforced ceiling on staging use, not a promise that all
exports will fit. Exhaustion aborts the run and removes only that run's temporary
files. No additional source cleanup is automatic.

When run as root for complete source coverage, SSH exports and SFTP use the
existing approved account identity. Root does not get a new SSH authorization.
The native MySQL client has passed a representative schema-only export check;
the full dump of all 19 schemas is still required for production success.

## Execution contract

A private JSON configuration must specify `execution_enabled: true`; every
non-estimate command also requires `--approved`. Database write locks require
`--allow-database-write-locks`. These are operator gates, not authorization grants.
Do not turn them on until Robert approves the reviewed scope and destinations.

Commands: `estimate`, `init`, `run`, `check`, `retention-preview`. `check` reads all
stored data; normal runs check a 1% data sample plus restore a random probe from
each exact completed snapshot. A run is `verified_both` only when both repositories
pass. One successful destination and one failure is explicitly incomplete. No
`prune`, real `forget`, production restore, or source deletion command exists.

Use the dedicated Python interpreter with `runner.py ACTION --config PRIVATE_CONFIG`.
Do not paste private configuration or child command output into tickets/chat.
All child errors are reduced to non-secret summaries. Receipts include repository
labels, exact snapshot IDs, and verification results, not contents or credentials.

## Coverage and consistency

- Include source trees, `.git`, uncommitted files, working documents, transcripts,
  runtime state and service definitions. Do not broadly exclude `tmp`: it contains
  business evidence. Exclude only regenerable dependencies/cache folders and this
  controller's staging/test area.
- Symlinks are preserved, not traversed. External targets need separate source
  roots; broken links and external mounts are not silently equivalent to data.
- Regular file backup is a live filesystem read, **not a coherent whole-machine
  point-in-time snapshot or bootable clone**. Stop writers or use a separately
  approved consistent filesystem snapshot if simultaneous multi-file recovery is
  required. An unreadable source or restic exit 3 fails the run.
- SQLite candidates (`.db`, `.sqlite`, `.sqlite3`) are checked for the SQLite header,
  copied with SQLite's online backup API, and checked with `quick_check`. Original
  database/WAL files are excluded; private restore mapping is inside the backup.
  Databases with unconventional filenames need explicit inventory before enabling.
- SQL exports run through explicit argv arrays into gzip-compressed private 0600 staging files. A streaming free-space check stops before consuming the reserve.
  MariaDB needs `--lock-all-tables` for the observed non-InnoDB tables; this may
  pause writes and needs an approved window. PostgreSQL `pg_dumpall` includes roles
  and per-database consistent exports, not a cross-database transaction boundary.
- A mounted encrypted disk image blocks the run until safely unmounted. The
  encryption password must be escrowed independently of the Mac and both backup
  repositories before first use. Losing it loses both copies. Restic encrypts all
  file data and metadata before SFTP/Drive upload.
- Remote applications, Docker volumes, file uploads, other servers, cloud-native
  documents, and external production databases are not covered merely because
  source code or a DB export from .205 is included. Inventory those as separate
  scopes before calling this an organization-wide backup.

## Restore procedure

1. On an isolated recovery host, install the pinned restic/rclone tools and obtain
   the independently escrowed key and destination access. Use either destination.
2. Select the recorded snapshot ID and run `restic check --read-data`.
3. Restore into a **new empty directory**, never over live application files.
4. Verify representative source, conversation, and attachment checksums. Use
   `sqlite-restore-map.json` to place SQLite copies at their original paths only
   after stopping the corresponding application. Run SQLite `integrity_check`.
5. Import decompressed SQL dumps into disposable matching-version database servers; verify
   schema/table counts and representative records before restoring production.
6. Reinstall dependencies and service definitions; reconnect permissions and
   secrets through normal approved procedures. Running tmux processes and active
   shells themselves cannot be restored; persistent conversations can be resumed.
7. Two independently verified end-to-end production pushes and a real restore
   drill are required before retiring the older backup lane.

The synthetic integration test initializes two **local fixture repositories**,
backs up generated files and a SQLite database, restores from each, compares data,
and checks that a second-destination failure is never reported as redundant.
Run: `python3.13 -m unittest discover -s tests/recovery_backup -v`.

References: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
https://restic.readthedocs.io/en/stable/040_backup.html
https://restic.readthedocs.io/en/stable/050_restore.html
https://rclone.org/drive/
