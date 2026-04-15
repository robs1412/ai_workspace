# Incident / Project Slice Log

Last Updated: 2026-03-07 08:01:47 CST (Machine: RobertMBP-2.local)

- Master Incident ID: AI-INC-20260307-SEC-HARDEN-01
- Date Opened: 2026-03-07
- Date Completed:
- Owner: Codex
- Priority: High
- Status: Open

## Scope

Review and, if approved, implement safe hardening steps for:

- Codex/agent malicious prompt handling and local safety directives
- SSH between MacBook and `admin-macmini` in both directions
- live SSH access to `koval@ftp.koval-distillery.com`
- local SSH client config and key usage patterns that affect deploy/auth workflows

## Symptoms

- Security guidance exists in `AGENTS.md`, but the hardening posture has not yet been consolidated into a single tracked project with explicit follow-through.
- Cross-machine SSH and live SSH are functional, but current hardening deltas and remaining risks still need a focused review.

## Root Cause

- Prior work established connectivity and baseline docs, but not a full hardening pass with explicit recommendations, validation steps, and completion tracking.

## Repo Logs

### ai_workspace

- Repo Log ID: RL-20260307-01
- Commit SHA:
- Commit Date:
- Change Summary: Track security review scope, policy updates, and any resulting documentation changes.

## Verification Notes

- Initial local review confirms `AGENTS.md` already contains sections for suspicious prompts, credential handling, cross-machine SSH, macOS SSHD hardening notes, and live deploy SSH flow.
- Local SSH config currently defines dedicated host entries for `admin-macmini`, `github.com`, and `ftp.koval-distillery.com`.
- Local MacBook SSH client config is reasonably tight: dedicated `IdentityFile` entries plus `IdentitiesOnly yes` for `admin-macmini`, `github.com`, and `ftp.koval-distillery.com`.
- Local MacBook SSHD hardening drop-in exists at `/etc/ssh/sshd_config.d/90-local-hardening.conf` with:
  - `PasswordAuthentication no`
  - `KbdInteractiveAuthentication no`
  - `PubkeyAuthentication yes`
- Loopback auth probe to `127.0.0.1` returned `Permission denied (publickey)`, which is consistent with key-only auth on the MacBook.
- `AGENTS.md` currently contains a stale interpretation saying local MacBook SSHD hardening is not yet active; that note should be corrected before using it as source of truth.
- Direct SSH from this MacBook to `admin-macmini` (`192.168.55.16`) timed out on 2026-03-07, so cross-machine verification could not be completed from the current network path.
- After VPN/network path change on 2026-03-07, direct SSH from this MacBook to `admin-macmini` succeeded:
  - `hostname`: `Macmini.lan`
  - `whoami`: `admin`
  - `pwd`: `/Users/admin`
- Auth probe from MacBook to `admin-macmini` returned `Permission denied (publickey)`, consistent with key-only auth.
- Remote inspection of `admin-macmini` confirms `/etc/ssh/sshd_config.d/90-local-hardening.conf` contains:
  - `PasswordAuthentication no`
  - `KbdInteractiveAuthentication no`
  - `PubkeyAuthentication yes`
- Reverse `admin-macmini` -> MacBook probe to `192.168.6.93:22` timed out, so bidirectional verification is still blocked by reachability/network path from the admin machine back to the laptop.
- Direct SSH from this MacBook to `ftp.koval-distillery.com` succeeded for a non-interactive host probe.
- Live host auth-method probe returned `publickey,gssapi-keyex,gssapi-with-mic,password`, which means password auth is still advertised server-side.
- Live host reports `OpenSSH_8.0`.
- Live host negotiation selected `curve25519-sha256` and emitted an OpenSSH warning that the session is not using a post-quantum key exchange algorithm.

## Rollback Plan

- Revert only documentation/config changes that are explicitly approved and applied.
- For SSH hardening, validate with `sshd -t` and non-interactive `ssh -o BatchMode=yes ...` probes before and after each change.

## Follow-Ups

- Compare current workstation and live SSH posture against the documented target state.
- Identify safe hardening changes that preserve deploy and cross-machine access.
- Decide whether `codex-agent-safety.md` should become a stricter enforced checklist referenced from `AGENTS.md`.
- Recommended hardening order:
  - update stale `AGENTS.md` MacBook SSH hardening note to match current state
  - re-test `admin-macmini` -> MacBook after confirming MacBook Remote Login reachability from the admin-side network path
  - if admin-to-MacBook later advertises password auth, align the remote MacBook SSHD with the documented key-only drop-in and validate with `sshd -t` plus non-interactive probes
  - review live host SSHD for `PasswordAuthentication no` if operationally safe, after confirming key coverage and break-glass access
  - review live host OpenSSH version/KEX support; add a post-quantum hybrid KEX if supported by the server version
  - formalize a short malicious-prompt escalation checklist in `codex-agent-safety.md` and reference it from `AGENTS.md`
