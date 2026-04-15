# AI Workspace

This is the git-backed coordination workspace for KOVAL AI work.

It is intended for safe text artifacts only:

- policy and operating docs
- TODO and handoff records
- project hub notes
- worker role documentation
- non-secret Frank and Avignon planning docs

Large files should be stored outside this repo and referenced with a manifest. See `ARTIFACTS.md`.

Keep out of this repo:

- secrets, credentials, tokens, `.env` files, private keys, OAuth material, VPN/router passwords, and mailbox credentials
- runtime state, LaunchAgent runtime copies, tmux/session state, caches, dependency folders, virtualenvs, and generated output
- implementation code that belongs in a dedicated `/Users/werkstatt/<repo>` repository

The previous Google Drive `ai_workspace` was moved on Mac mini to `/Users/werkstatt/ai_workspace_google_drive_archive_20260415` as a local archive during migration. Treat it as legacy/source material, not an active workspace.
