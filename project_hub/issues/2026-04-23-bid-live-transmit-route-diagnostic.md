- Master Incident ID: `AI-INC-20260423-BID-LIVE-TRANSMIT-ROUTE-01`
- Date Opened: `2026-04-23`
- Date Completed: `2026-04-23`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Recover the canonical approved BID live transmit route to `.205` from this machine using read-only inspection only. Do not publish files, change SSH config, alter credentials, or mutate live BID state.

## Symptoms

- BID finance intake session `68b9bed9` staged/imported monthly P&L and Balance Sheet CSVs locally, but live BID publish remained blocked.
- BID docs named alias `bid-intelligence-205`, but this machine could not resolve that host.
- Direct noninteractive SSH to `claude@192.168.55.205` and `admin@192.168.55.205` failed with `Permission denied (publickey,password)`.

## Root Cause

The canonical route is documented, but this machine is missing the local access material needed to use it now:

- Repo docs identify the intended live target as host `192.168.55.205`, alias `bid-intelligence-205`, account `claude`, canonical path `/srv/development/bid/intelligence`, and live path `/srv/bid/intelligence`.
- Local `~/.ssh/config` and its backups contain no `.205`/BID/Reatan host entry, so the alias is absent rather than mis-resolving.
- Local SSH-known-host state proves this machine has seen `192.168.55.205` before, and TCP `22` is reachable, so the blocker is not basic network reachability.
- The documented private credential references `raetan.txt` and `claude-user.txt` are not present in the currently mounted local paths, and no SSH agent identities are loaded.
- Prior workspace notes show the working historical SSH path was `claude@192.168.55.205` when the approved private reference was available and parsed correctly. Without that reference or an already-configured alias/identity, this machine cannot authenticate now.

## Repo Logs

### bid

- Repo Log ID: `BID-2026-04-23-LIVE-TRANSMIT-ROUTE-DIAGNOSTIC`
- Commit SHA: `none`
- Commit Date: `n/a`
- Change Summary: read-only recovery of the canonical `.205` BID live transmit route from local docs/config/history; no repo code or live data changes.

### ai_workspace

- Repo Log ID: `AIW-2026-04-23-BID-LIVE-TRANSMIT-ROUTE-DIAGNOSTIC`
- Commit SHA: `none`
- Commit Date: `n/a`
- Change Summary: project-hub incident log for the `.205` BID live transmit route diagnostic; no auth/config/runtime changes.

## Verification Notes

- `bid/data-management/DOWNLOAD-PLAN.md` records the verified route details and approved dry-run shape:
  - host `192.168.55.205`
  - alias `bid-intelligence-205`
  - user `claude`
  - canonical target `/srv/development/bid/intelligence`
  - live path `/srv/bid/intelligence`
- `bid/HANDOFF.md` records that the alias is not configured on this machine and that direct noninteractive SSH attempts failed for both `claude` and `admin`.
- `~/.ssh/config` and `~/.ssh/config.bak.*` contain no `.205`/BID host alias.
- `~/.ssh/known_hosts` contains host keys for `192.168.55.205`.
- `ssh -G 192.168.55.205` resolves the default user as `admin` on this machine when no alias overrides it.
- `nc -vz 192.168.55.205 22` succeeded.
- `ssh -o BatchMode=yes -o PreferredAuthentications=publickey -o PasswordAuthentication=no -o ConnectTimeout=5 claude@192.168.55.205 true` failed with `Permission denied (publickey,password)`.
- Documented private reference paths checked read-only and found missing:
  - `/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/.private/passwords/raetan.txt`
  - `/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/.private/passwords/claude-user.txt`
  - `/Users/werkstatt/.private/passwords/raetan.txt`
  - `/Users/werkstatt/.private/passwords/claude-user.txt`
- Prior non-secret workspace evidence still shows the working historical auth shape:
  - `ai_workspace/project_hub/issues/2026-04-16-workspaceboard-macmini-serving-recovery.md`
  - `ai_workspace/ai-digital-office.md`

## Rollback Plan

No rollback required. This slice was read-only and made no config, credential, repo, or live-system changes.

## Follow-Ups

- Materialize the approved private credential reference for the `claude@192.168.55.205` route on this machine through the approved non-printing channel, or use the already-approved machine/session where that reference is available.
- Add the missing local SSH alias `bid-intelligence-205` outside the repo, pointed at `claude@192.168.55.205`, using the approved credential material.
- Before any publish, run the documented read-only verification command against both `/srv/development/bid/intelligence` and `/srv/bid/intelligence`.
- If the read-only verification succeeds, session `68b9bed9` can resume with dry-run `rsync` first, then the actual publish and BID validation checks.
