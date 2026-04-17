# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260417-AI-TRANSFER-GATE-01`
- Date Opened: 2026-04-17 16:32 CDT
- Date Completed:
- Owner: Codex
- Priority: High
- Status: Partially complete; M4 enforced, MacBook pending reachability

## Scope

Add a manual approval gate for file pulls from front-facing workstations to the primary AI worker (`Macmini.lan` / `.17`) so `.17` cannot use its workstation SSH key for unrestricted shell access.

## Symptoms

Robert noted that dragging a file into the M4 surface and telling `.17` to fetch it was convenient, but unchecked Mac mini access into the M4/MacBook was not acceptable.

## Root Cause

The M4 `authorized_keys` file contained the Mac mini public key as a normal unrestricted SSH key. That allowed direct shell commands from `.17` to the M4 with no per-transfer human approval.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260417-AI-TRANSFER-GATE-01-ai-workspace`
- Commit SHA:
- Commit Date:
- Change Summary: Added `scripts/ai_transfer_gate.py`, `scripts/ai_transfer_fetch.py`, and `docs/ai-transfer-gate.md`.

## Verification Notes

- M4 receiver gate installed at `/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py`.
- Mac mini fetch helper installed at `/Users/werkstatt/ai_workspace/scripts/ai_transfer_fetch.py`.
- Replaced only the matching M4 `authorized_keys` line for public key comment `macmini-to-kovaladmin`.
- M4 `authorized_keys` backup created: `/Users/kovaladmin/.ssh/authorized_keys.bak.20260417163618`.
- Restricted line includes `from="192.168.55.17"`, `restrict`, `no-agent-forwarding`, `no-X11-forwarding`, `no-port-forwarding`, `no-pty`, and forced command `/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py serve`.
- Direct shell test from `.17` to M4 now fails at the gate with `Unsupported command. Expected: fetch <grant_id> <code>`.
- Temporary approved-transfer test succeeded from `.17` to M4: fetched file SHA-1 matched source SHA-1.
- Reusing or consuming grants is blocked; local test confirmed a second use returns `Grant has already been used`.
- MacBook was not changed because SSH timed out at remembered/current addresses: `192.168.55.38`, `192.168.55.44`, and `192.168.55.11`.

## Rollback Plan

Restore the M4 backup if unrestricted Mac mini SSH is explicitly needed again:

```bash
cp /Users/kovaladmin/.ssh/authorized_keys.bak.20260417163618 /Users/kovaladmin/.ssh/authorized_keys
chmod 600 /Users/kovaladmin/.ssh/authorized_keys
```

Rollback restores the prior broader access and should be treated as a security decision.

## Follow-Ups

- Install the same receiver gate on MacBook once it is reachable.
- Commit/push the AI Workspace tooling after reconciling the current local branch divergence with `origin/main`.
- Consider a dedicated transfer-only key per workstation so normal machine-to-machine admin keys can be retired or kept separate from transfer grants.
