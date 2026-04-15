# Cross-Machine Git Auth Verification and SSH Access Confirmation

- Master Incident ID: `AI-INC-20260227-GITAUTH-01`
- Date Opened: `2026-02-27`
- Date Completed: `2026-02-27`
- Owner: `Codex`
- Priority: `P2`
- Status: `Completed`

## Scope

- Validate laptop SSH access to `ftp.koval-distillery.com` as `koval`.
- Validate cross-machine GitHub read/write auth indicators for active module repos.
- Determine whether previous failures were auth failures or repo divergence.

## Symptoms

- Prior report indicated git auth worked on one machine and failed on another.
- Need canonical verification from the laptop environment.

## Root Cause

- SSH access to live host is configured and works on this machine with dedicated key auth.
- GitHub auth is functioning for all checked repos (`ls-remote` succeeded everywhere).
- Push failures on `bid`, `forge`, and `lists` were not credential failures; they were non-fast-forward rejections (`fetch first`) caused by remote branch divergence.

## Repo Logs

### ops

- Repo Log ID: `GITAUTH-20260227-OPS`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin main`: success

### bid

- Repo Log ID: `GITAUTH-20260227-BID`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin main`: rejected `fetch first` (non-fast-forward)

### portal

- Repo Log ID: `GITAUTH-20260227-PORTAL`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin main`: success

### login

- Repo Log ID: `GITAUTH-20260227-LOGIN`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin master`: success

### forge

- Repo Log ID: `GITAUTH-20260227-FORGE`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin main`: rejected `fetch first` (non-fast-forward)

### salesreport

- Repo Log ID: `GITAUTH-20260227-SALESREPORT`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin master`: success

### importer

- Repo Log ID: `GITAUTH-20260227-IMPORTER`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin main`: success

### lists

- Repo Log ID: `GITAUTH-20260227-LISTS`
- Commit SHA: `N/A`
- Commit Date: `N/A`
- Change Summary:
  - `git ls-remote --heads origin`: success
  - `git push --dry-run origin main`: rejected `fetch first` (non-fast-forward)

## Verification Notes

- Runtime check timestamp: `2026-02-27 10:20:20 CST`
- Machine: `MacBookPro.lan`
- User: `robert`
- Live SSH check:
  - `ssh -o BatchMode=yes ftp.koval-distillery.com 'hostname; whoami'`
  - returned host `vps125145.inmotionhosting.com` and user `koval`.
- Cross-workstation key-only checks (2026-02-27):
  - `ssh -o BatchMode=yes admin-macmini 'hostname; whoami; pwd'`: success.
  - From admin machine: `ssh -o BatchMode=yes macbookpro.lan 'hostname; whoami; pwd'`: success.
  - Client fallback hardening applied on both machines:
    - `~/.ssh/config` now uses `PreferredAuthentications publickey` for workstation host entries.
    - Backups created: `~/.ssh/config.bak.20260227102513` on both machines.
- SSHD auth-method probe timestamp: `2026-02-27 10:38:45 CST`
  - MacBook -> admin (`PubkeyAuthentication=no`, password-only attempt):
    - `Authentications that can continue: publickey`
  - Admin -> MacBook (`PubkeyAuthentication=no`, password-only attempt):
    - `Authentications that can continue: publickey,password,keyboard-interactive`
  - Result:
    - admin SSH server hardening active
    - MacBook SSH server hardening not yet active

## Rollback Plan

- Not applicable; verification-only changes, no deployment actions executed.

## Follow-Ups

- For `bid`, `forge`, `lists`: run `git fetch origin` + fast-forward/local reconciliation before next push.
- Keep `~/.ssh/config` host entries under change control to avoid cross-machine drift.
- Server-side hardening still pending on both machines (requires local admin password/sudo):
  - set `PasswordAuthentication no`
  - set `KbdInteractiveAuthentication no`
  - keep `PubkeyAuthentication yes`
  - reload sshd after config validation.
