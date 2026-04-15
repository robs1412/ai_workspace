# AI Workspace Legacy Archives

Created: 2026-04-15
Project: AI workstation and sync transition

## Purpose

Track the legacy Google Drive `ai_workspace` archives after active coordination moved to `/Users/werkstatt/ai_workspace`.

Git remains the coordination index only. These archives are legacy source/retention bundles and may contain private material. Do not ingest, sync, print, or copy secret-bearing contents into Git, Papers, Workspaceboard summaries, or chat.

## Archives

| Machine | Archive path | Status |
| --- | --- | --- |
| Mac mini | `/Users/werkstatt/ai_workspace_google_drive_archive_20260415` | Present, permission-hardened |
| MacBook | `/Users/werkstatt/ai_workspace_google_drive_archive_20260415_macbook` | Present, permission-hardened |
| M4 | none retained | Old Drive path removed; no archive retained |

## Mac Mini Inventory

Total size: about `443M`.

Largest retained items:

- `.venvs` - about `299M`; regenerated Python environment, deletion candidate after confirmation.
- `.venv_pdf` - about `100M`; regenerated Python environment, deletion candidate after confirmation.
- `.private` - about `23M`; private/secret-bearing material, secure-storage decision required.
- `project_hub` - about `7.1M`; mostly safe text already migrated, keep archive for traceability until spot-checked.
- `screenbox` - about `4.0M`; embedded implementation clone, decide separately.
- `.playwright-cli` - about `2.4M`; generated/runtime cache, deletion candidate after confirmation.
- `external` - about `2.3M`; embedded implementation clone, decide separately.
- `tmp` - about `1.8M`; generated/runtime temp, deletion candidate after confirmation.
- `LOG_imapsync` - about `1.1M`; email archive logs, retain until email archive projects are closed.

Secret-looking paths by name include:

- `.env`
- `.env.md`
- `.private/`
- `.private/google-oauth/`
- `.private/passwords/`
- `.private/ikev2/*-secret.txt`
- `.private/router/openwrt-root-password.txt`
- `.private/router/.../private-config-review/`
- `output/portal-account-passwords-2026-03-27.md`
- `screenbox/.env`
- `avignon/.private-work`

Those paths were identified by filename only. Contents were not read.

## MacBook Inventory

Total size is materially the same as Mac mini; top-level sizes show the same large retention categories:

- `.venvs` - about `299M`; regenerated Python environment, deletion candidate after confirmation.
- `.venv_pdf` - about `100M`; regenerated Python environment, deletion candidate after confirmation.
- `.private` - about `23M`; private/secret-bearing material, secure-storage decision required.
- `project_hub` - about `7.1M`; mostly safe text already migrated, keep archive for traceability until spot-checked.
- `screenbox` - about `4.0M`; embedded implementation clone, decide separately.
- `.playwright-cli` - about `2.4M`; generated/runtime cache, deletion candidate after confirmation.
- `external` - about `2.3M`; embedded implementation clone, decide separately.
- `tmp` - about `1.8M`; generated/runtime temp, deletion candidate after confirmation.
- `LOG_imapsync` - about `1.1M`; email archive logs, retain until email archive projects are closed.

Secret-looking paths by name match the Mac mini categories, including `.env`, `.env.md`, `.private/`, OAuth/password/IKEv2/router private paths, `output/portal-account-passwords-2026-03-27.md`, `screenbox/.env`, and `avignon/.private-work`.

Those paths were identified by filename only. Contents were not read.

## Permissions Applied

On Mac mini and MacBook:

- archive root set to owner-only access: `700`
- `.private` set to owner-only access: `700`
- `.env` and `.env.md` set to owner-only read/write: `600`

## Retention Plan

Recommended next actions:

1. Keep both archives intact until Robert approves cleanup categories.
2. Delete regenerated environments and caches after approval:
   `.venvs`, `.venv_pdf`, `.playwright-cli`, `tmp`, `tmp-staging`, `tmp_il_report`.
3. Retain `LOG_imapsync`, `output`, and `recordings` until related email/archive and reporting projects are confirmed closed.
4. Move `.private`, `.env*`, password-like outputs, OAuth/mailbox material, and router/VPN credential material into the approved secure-storage path once chosen.
5. Review `screenbox` and `external/mempalace` as code projects, not as AI Workspace coordination content.
6. After the secure/private items and retention artifacts are handled, delete or compress the remaining legacy archives.

## Current Decision Needed

Choose the secure storage target for private material:

- machine-local encrypted archive,
- a dedicated password/vault system,
- or another approved secure location.

Until that decision is made, leave private material inside the owner-only legacy archives and do not copy it into the Git-backed workspace.
