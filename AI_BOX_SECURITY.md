# AI Box Security Notes

Current AI box: Mac mini (`Macmini.lan`).

## Active Storage Model

- Coordination source: `/Users/werkstatt/ai_workspace`, synced through private GitHub repo `robs1412/ai_workspace`.
- Code repositories: `/Users/werkstatt/<repo>`, synced through their own Git remotes.
- Runtime state: machine-local under `~/.workspaceboard-launch`, `~/.frank-launch`, and `~/.avignon-launch`.
- Private archive vault: `/Users/werkstatt/secure-vaults/ai-workspace-private.sparsebundle`.
- Vault passphrase storage: macOS login Keychain item `KOVAL_AI_WORKSPACE_PRIVATE_VAULT` for user `admin`.

## Private Material

Mac mini legacy archive private paths were moved into the encrypted vault without printing contents. The vault should stay detached except during deliberate private-material maintenance.

MacBook private material remains in its owner-only legacy archive because non-interactive SSH could not create a Keychain-backed vault there. Complete that step locally on the MacBook or with a GUI-approved Keychain session.

## Backups

Run:

```bash
/Users/werkstatt/ai_workspace/scripts/ai_box_backup.sh
```

Backups are written to `/Users/werkstatt/ai_box_backups/<timestamp>` with `latest` pointing at the newest backup. These backups include active LaunchAgent plists, shell mapping, git heads, and launchctl status. They do not copy private runtime directories, mailbox credentials, OAuth tokens, `.private`, `.env`, or the encrypted vault contents.

## Operational Rules

- Keep Google Drive off this Mac mini unless a separate non-AI need requires it.
- Keep secrets out of Git, Papers, Workspaceboard summaries, and chat.
- Keep large artifacts out of Git; use manifests under `project_hub/artifacts/`.
- Keep active services on machine-local runtime/state paths.
- Prefer SSH key-only access and stable LAN hostnames/IPs.
