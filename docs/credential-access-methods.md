# Credential Access Methods

Last updated: 2026-04-26 CDT

## Purpose

This note records the approved non-secret method for Robert to access machine-local credentials without moving secrets into shared folders, chat, git, logs, or project notes.

## Approved Pattern: Public-Key SSH + Interactive Read

When a credential exists only on the Mac mini, the safe owner-access method is:

1. Robert authorizes his workstation public SSH key on the Mac mini account that owns the credential.
2. Robert connects over SSH from his workstation to the Mac mini.
3. Robert opens the credential file interactively in an editor such as `nano`.
4. Robert types the credential directly into the target login or consent screen.

This keeps the secret on the source machine and avoids copying it through `Downloads-shared`, chat, email, git, task notes, or normal command output.

## Rules

- Do not print passwords, private keys, OAuth refresh tokens, API keys, auth codes, `.env` values, or app passwords to chat.
- Do not move credential files into shared folders such as `Downloads-shared`.
- Do not use `cat`, `grep`, `sed`, `pbcopy`, screenshots, or shared files to transfer credential values unless a separate approved encrypted channel is established.
- Public keys are not secrets and may be added to `authorized_keys` after confirming the key line starts with `ssh-ed25519` or another expected public-key prefix.
- Keep actual credential paths out of broad policy docs when possible; use them only in immediate operational chat or private runbooks where the owner needs local access.

## 2026-04-26 Application

Robert's MacBook public key was added to the Mac mini `admin` account `authorized_keys` so he could SSH into `admin@192.168.55.230` and read the Avignon credential interactively. No private key or password value was printed or stored in documentation.
