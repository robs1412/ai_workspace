# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260417-AI-TRANSFER-GATE-01`
- Date Opened: 2026-04-17 16:32 CDT
- Date Completed:
- Owner: Codex
- Priority: High
- Status: Partially complete; M4 enforced, MacBook pending reachability

## Scope

Add a manual approval gate for file pulls from front-facing workstations to the primary AI worker (`Macmini.lan`; current Ethernet source `.230`, historical Wi-Fi source `.17`) so the Mac mini cannot use its workstation SSH key for unrestricted shell access.

## Symptoms

Robert noted that dragging a file into the M4 surface and telling the Mac mini to fetch it was convenient, but unchecked Mac mini access into the M4/MacBook was not acceptable.

## Root Cause

The M4 `authorized_keys` file contained the Mac mini public key as a normal unrestricted SSH key. That allowed direct shell commands from the Mac mini to the M4 with no per-transfer human approval.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260417-AI-TRANSFER-GATE-01-ai-workspace`
- Commit SHA: local `5887df7`, `4552e52`, follow-up local commit pending for shared-folder access
- Commit Date:
- Change Summary: Added `scripts/ai_transfer_gate.py`, `scripts/ai_transfer_fetch.py`, and `docs/ai-transfer-gate.md`.

## Verification Notes

- M4 receiver gate installed at `/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py`.
- Mac mini fetch helper installed at `/Users/werkstatt/ai_workspace/scripts/ai_transfer_fetch.py`.
- M4 double-click approval launcher added at `/Users/werkstatt/ai_workspace/scripts/approve_ai_fetch.command`; it opens a file picker, creates a one-time grant, prints the grant id/code, and copies the grant id/code to clipboard.
- Mac mini wrapper added at `/Users/werkstatt/ai_workspace/scripts/fetch_from_m4.sh` for the common M4 fetch path.
- M4 always-allowed shared folder added: `/Users/kovaladmin/Downloads - shared`.
- Mac mini can fetch regular files from the shared folder without a code using `fetch_from_m4.sh --shared <relative_file_path> <output_path>`.
- Mac mini can fetch files or folders from the shared folder as a gzip tar archive using `fetch_from_m4.sh --shared-archive <relative_path> <output_tar_gz>`.
- Mac mini can list the shared folder using `fetch_from_m4.sh --shared-list [relative_path] <output_json>`.
- Replaced only the matching M4 `authorized_keys` line for public key comment `macmini-to-kovaladmin`.
- M4 `authorized_keys` backup created: `/Users/kovaladmin/.ssh/authorized_keys.bak.20260417163618`.
- Restricted line includes `from="192.168.55.17"`, `restrict`, `no-agent-forwarding`, `no-X11-forwarding`, `no-port-forwarding`, `no-pty`, and forced command `/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py serve`.
- Direct shell test from `.17` to M4 now fails at the gate with `Unsupported command. Expected: fetch <grant_id> <code>`.
- Temporary approved-transfer test succeeded from `.17` to M4: fetched file SHA-1 matched source SHA-1.
- Reusing or consuming grants is blocked; local test confirmed a second use returns `Grant has already been used`.
- Shared-folder file fetch from `.17` succeeded and source/fetched SHA-1 matched.
- Shared-folder folder archive fetch from `.17` succeeded and tar listing contained the expected nested file.
- Shared-folder list from `.17` succeeded and included the expected test file/folder.
- Shared-folder path escape attempt with `../.ssh/authorized_keys` was rejected with `Shared path escapes the allowed folder`.
- 2026-04-22 source restriction cleanup: Robert approved moving the Mac mini transfer-gate source from Wi-Fi `.17` to Ethernet `.230`. Updated only the existing M4 Mac mini transfer-gate public-key line in `/Users/kovaladmin/.ssh/authorized_keys` using the existing installer. Backup created: `/Users/kovaladmin/.ssh/authorized_keys.bak.20260422161146`.
- Current M4 restricted line outcome is `.230` only: `from="192.168.55.230"`, `restrict`, `no-agent-forwarding`, `no-X11-forwarding`, `no-port-forwarding`, `no-pty`, and forced command `/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py serve`.
- Verification after the `.230` cleanup: `/Users/werkstatt/ai_workspace/scripts/fetch_from_m4.sh --shared-list /tmp/m4-transfer-post-default.json` succeeded over the default Ethernet route and produced valid JSON; binding the transfer key to `.17` now fails with publickey rejection; direct shell over the transfer key still fails at the gate with the unsupported-command error.
- MacBook was not changed because SSH timed out at remembered/current addresses: `192.168.55.38`, `192.168.55.44`, and `192.168.55.11`.
- Wrapper verification: `zsh -n` passed for `approve_ai_fetch.command` and `fetch_from_m4.sh`; Mac mini copy of `fetch_from_m4.sh` passed syntax/help smoke.
- Mac mini Workspaceboard TODO now tracks installing the same transfer gate and `Downloads - shared` behavior on MacBook once SSH/LAN reachability is restored.

## Rollback Plan

Restore the M4 backup if unrestricted Mac mini SSH is explicitly needed again:

```bash
cp /Users/kovaladmin/.ssh/authorized_keys.bak.20260417163618 /Users/kovaladmin/.ssh/authorized_keys
chmod 600 /Users/kovaladmin/.ssh/authorized_keys
```

Rollback restores the prior broader access and should be treated as a security decision.

For the 2026-04-22 `.230` source cleanup only, rollback to the immediately previous transfer-gate source restriction:

```bash
cp /Users/kovaladmin/.ssh/authorized_keys.bak.20260422161146 /Users/kovaladmin/.ssh/authorized_keys
chmod 600 /Users/kovaladmin/.ssh/authorized_keys
```

## Follow-Ups

- Install the same receiver gate on MacBook once it is reachable.
- Commit/push the AI Workspace tooling after reconciling the current local branch divergence with `origin/main`.
- Consider a dedicated transfer-only key per workstation so normal machine-to-machine admin keys can be retired or kept separate from transfer grants.
