# Avignon Runtime Source Mirror

This directory preserves git-backed source copies for installed Avignon runtime files.

## Current Source

- `avignon-launch/scripts/avignon_inbox_cycle.py`
  - Installed runtime path: `/Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py`
  - Preserved source hash, SHA-256: `2655a463f17f79eac24746894807100c0cdfc99f4f4bfa353b4752bc4924fc30`
  - Source-preserved: 2026-04-20 after live Avignon direct-owner follow-through incident fixes for Robert-only report targeting and pending-state preservation.

## Gates

- Do not reinstall, restart, reload LaunchAgents, run a live mailbox cycle, send mail, move mailbox state, change OAuth/auth/credentials, or mutate CRM/Portal/OPS from this source mirror without explicit Robert approval.
- Treat `/Users/admin/.avignon-launch/` as installed runtime state. Syncing from this mirror back into that installed path is a separate runtime action and needs an approved implementation prompt.
- Keep secrets, credential paths, tokens, private mailbox bodies, and private source captures out of this directory.
