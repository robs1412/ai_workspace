# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260302-GITAUTH-SSHCTX-01
- Date Opened: 2026-03-02 08:56:00 CST
- Date Completed: 2026-03-02 09:55:47 CST
- Owner: Codex (admin@Macmini.lan session)
- Priority: High
- Status: Completed (with follow-up)

## Scope

Fix multi-repo git sync interruption across `ops`, `portal`, `forge`, `importer`, `contactreport` when operating cross-machine via SSH-driven Codex sessions.

## Symptoms

- SSH into laptop worked.
- Git push/pull from that SSH context failed with:
  - `failed to get: -25308`
  - `fatal: could not read Username for 'https://github.com': Device not configured`
- `contactreport` could still be pushed successfully from interactive laptop context.

## Root Cause

- Repos were using HTTPS remotes requiring GitHub credential helper.
- In non-interactive/headless SSH context, macOS keychain-backed credential lookup failed (`-25308`).
- SSH fallback to GitHub also failed initially due missing/unauthorized GitHub key setup.

## Repo Logs

### ops

- Repo Log ID: AI-INC-20260302-GITAUTH-SSHCTX-01-OPS
- Commit SHA: c3805f9
- Commit Date: 2026-03-02
- Change Summary: cleaned commit to exclude `.playwright-cli` and `output/2026-Sonat-business-cards3.pdf`; kept intended outreach/module changes.

### portal

- Repo Log ID: AI-INC-20260302-GITAUTH-SSHCTX-01-PORTAL
- Commit SHA: 88fdd30e
- Commit Date: 2026-03-02
- Change Summary: synced open `ToDo-append.md` updates.

### forge

- Repo Log ID: AI-INC-20260302-GITAUTH-SSHCTX-01-FORGE
- Commit SHA: 509f616
- Commit Date: 2026-03-02
- Change Summary: synced open `ToDo-append.md` updates.

### importer

- Repo Log ID: AI-INC-20260302-GITAUTH-SSHCTX-01-IMPORTER
- Commit SHA: 8964958
- Commit Date: 2026-03-02
- Change Summary: synced open importer feature/content changes and TODO queue files.

### contactreport

- Repo Log ID: AI-INC-20260302-GITAUTH-SSHCTX-01-CONTACTREPORT
- Commit SHA: a98244e
- Commit Date: 2026-03-02
- Change Summary: synced open `ToDo-append.md` updates; confirmed pushed successfully.

## Verification Notes

- Laptop module divergence check now reports `0 0` for all target repos:
  - `ops` `main`
  - `portal` `main`
  - `forge` `main`
  - `importer` `main`
  - `contactreport` `master`
- Macmini local hardening step completed:
  - created `~/.ssh/id_ed25519_github_modules`
  - added `Host github.com` block in `~/.ssh/config`
- Follow-up still pending:
  - add Macmini public key to GitHub account SSH keys to enable non-interactive SSH git auth on this machine.

## Rollback Plan

- Revert per-repo commits using standard `git revert <sha>` if needed.
- Restore previous SSH config from `~/.ssh/config.bak.<timestamp>` if GitHub host entry needs rollback.

## Follow-Ups

- Add `admin@Macmini.lan` public key to GitHub SSH keys and validate:
  - `ssh -o BatchMode=yes -T git@github.com`
- Optionally convert module remotes to SSH after key authorization, then validate:
  - `git ls-remote origin`
  - `git push --dry-run origin <branch>`
