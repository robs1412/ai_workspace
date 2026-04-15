# AI Workspace Legacy Archives

Created: 2026-04-15
Project: AI workstation and sync transition

## Purpose

Track the legacy Google Drive `ai_workspace` archives after active coordination moved to `/Users/werkstatt/ai_workspace`.

Git remains the coordination index only. These archives are legacy source/retention bundles and may contain private material. Do not ingest, sync, print, or copy secret-bearing contents into Git, Papers, Workspaceboard summaries, or chat.

## Archives

| Machine | Archive path | Status |
| --- | --- | --- |
| Mac mini | `/Users/werkstatt/secure-vaults/ai-workspace-private.sparsebundle` -> `macmini-legacy-archive/` | Retained in encrypted Mac mini vault |
| Mac mini loose archive | `/Users/werkstatt/ai_workspace_google_drive_archive_20260415` | Removed after vault copy verification |
| MacBook loose archive | `/Users/werkstatt/ai_workspace_google_drive_archive_20260415_macbook` | Removed as duplicate loose legacy material; no separate `macbook-legacy-archive/` payload was found in the vault during recovery check |
| M4 | none retained | Old Drive path removed; no archive retained |

## Mac Mini Inventory

Original size: about `443M`. Current size after approved generated/cache cleanup and private-material vault move: about `17M`.

Largest retained items:

- `.venvs` - about `299M`; deleted 2026-04-15 after Robert approval.
- `.venv_pdf` - about `100M`; deleted 2026-04-15 after Robert approval.
- `.private` - about `23M`; moved to Mac mini encrypted vault 2026-04-15.
- `project_hub` - about `7.1M`; mostly safe text already migrated, keep archive for traceability until spot-checked.
- `screenbox` - about `4.0M`; embedded implementation clone, decide separately.
- `.playwright-cli` - about `2.4M`; deleted 2026-04-15 after Robert approval.
- `external` - about `2.3M`; embedded implementation clone, decide separately.
- `tmp` - about `1.8M`; deleted 2026-04-15 after Robert approval.
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

Original size was materially the same as Mac mini. Current size after approved generated/cache cleanup: about `40M`. Top-level sizes showed the same large retention categories:

- `.venvs` - about `299M`; deleted 2026-04-15 after Robert approval.
- `.venv_pdf` - about `100M`; deleted 2026-04-15 after Robert approval.
- `.private` - about `23M`; private/secret-bearing material, secure-storage decision required.
- `project_hub` - about `7.1M`; mostly safe text already migrated, keep archive for traceability until spot-checked.
- `screenbox` - about `4.0M`; embedded implementation clone, decide separately.
- `.playwright-cli` - about `2.4M`; deleted 2026-04-15 after Robert approval.
- `external` - about `2.3M`; embedded implementation clone, decide separately.
- `tmp` - about `1.8M`; deleted 2026-04-15 after Robert approval.
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
2. Completed 2026-04-15 after Robert approval: deleted regenerated environments and caches from Mac mini and MacBook archives: `.venvs`, `.venv_pdf`, `.playwright-cli`, `tmp`, `tmp-staging`, `tmp_il_report`.
3. Retain `LOG_imapsync`, `output`, and `recordings` until related email/archive and reporting projects are confirmed closed.
4. Mac mini completed 2026-04-15: moved `.private`, `.env*`, password-like outputs, OAuth/mailbox material, router/VPN credential material, `screenbox/.env`, and `avignon/.private-work` into encrypted vault. MacBook remains pending local/GUI-approved vault creation.
5. Review `screenbox` and `external/mempalace` as code projects, not as AI Workspace coordination content.
6. After the secure/private items and retention artifacts are handled, delete or compress the remaining legacy archives.

## Current Decision Needed

Mac mini secure-storage target is selected and active: a machine-local encrypted sparsebundle with its passphrase in the admin login Keychain.

No current cleanup decision is pending for the loose legacy archive folders on Mac mini; both known loose legacy archive paths are gone. If MacBook-specific archive material is later found elsewhere, handle it through the same vault/manifest workflow before deletion.

## Cleanup Record

2026-04-15: Robert approved deleting generated/cache folders. Removed `.venvs`, `.venv_pdf`, `.playwright-cli`, `tmp`, `tmp-staging`, and `tmp_il_report` from both Mac mini and MacBook archives. Verified both archives were about `40M` afterward. Secret/private, log, output, recordings, `screenbox`, and `external` folders were left intact at that stage.

2026-04-15: Created Mac mini encrypted private archive vault `/Users/werkstatt/secure-vaults/ai-workspace-private.sparsebundle`, with the passphrase stored in the admin user's macOS Keychain item `KOVAL_AI_WORKSPACE_PRIVATE_VAULT`. Moved Mac mini archive private paths into the mounted vault under `macmini-legacy-archive/`, then detached the vault. Moved paths: `.private`, `.env`, `.env.md`, `screenbox/.env`, `avignon/.private-work`, and `output/portal-account-passwords-2026-03-27.md`. Verified those paths are gone from the Mac mini legacy archive. Mac mini legacy archive is now about `17M`; vault payload is about `23M`.

MacBook private paths remain in its owner-only archive because macOS refused non-interactive Keychain item creation over SSH (`User interaction is not allowed`). Complete the MacBook vault step locally or during a GUI-approved session.

2026-04-15 recovery/cleanup pass at 15:25 CDT: after a failed/background cleanup attempt, verified the encrypted vault was mounted at `/Volumes/AIWorkspacePrivate` and no live `rsync`, `ditto`, or `hdiutil` copy process remained. The loose Mac mini and MacBook archive folders were already absent. The vault contains `macmini-legacy-archive/` with `944` files and about `40M` of payload; the sparsebundle is about `60M` on disk. A separate `macbook-legacy-archive/` payload was not present. Embedded code copies are retained only inside the encrypted legacy archive payload: `screenbox` points at `https://github.com/dklymentiev/screenbox`, and `external/mempalace` points at `https://github.com/milla-jovovich/mempalace.git` with local modifications in `mempalace/entity_detector.py` and `mempalace/miner.py`. These are classified as vaulted legacy/audit material, not active AI Workspace source. No secret contents were read or printed.
