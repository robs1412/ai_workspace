# Claude Host Read-Only Snapshot Contract

Status: approved for repo-local planning and durable proof only
Updated: 2026-05-18 CDT
Owner: Codex local bridge planning

## Purpose

Define the first narrow, non-secret export shape for the Claude host snapshot.

This contract exists so local Codex and Workspaceboard planning can reference protected-side Claude host facts without creating:

- a writable cross-system bridge
- a secret-bearing export
- a shared Codex/Claude work record
- a stale assumption about old Claude config paths

## Scope

Allowed in the snapshot:

- host identity metadata
- read-only config-path inventory
- tool-directory inventory
- auth-cache category names
- capture metadata and source labels

Explicitly excluded:

- passwords, tokens, cookies, keys, or `.env` values
- file contents from protected config or cache files
- mailbox bodies, task bodies, document bodies, or private prompts
- writable endpoints or action instructions
- process arguments that could expose secrets
- absolute credential paths outside the approved non-secret host/config/tool inventory

## Contract Rules

1. Export is read-only and descriptive.
2. Export is metadata only; no protected file bodies.
3. Export may name categories of pending auth, but not cache values.
4. Export may list active config paths and tool directories, but not full recursive file inventories.
5. Export must preserve uncertainty instead of guessing.
6. Export must include a `single_writer_contract` section that states this artifact does not authorize shared writes.
7. Export must include `source_basis` so later readers know whether the snapshot came from live readback, local notes, or a derived example.

## Recommended JSON Shape

```json
{
  "schema_version": "2026-05-18.claude-host-readonly.v1",
  "snapshot_kind": "claude_host_read_only",
  "captured_at": "2026-05-18T11:45:00-05:00",
  "source_basis": {
    "mode": "live_readback",
    "local_evidence_refs": [
      "HANDOFF.md#2026-05-18-1145-cdt"
    ],
    "notes": "Non-secret metadata only."
  },
  "host_identity": {
    "login_user": "claude",
    "hostname": "reatan",
    "address": "192.168.55.205",
    "label": "koval.lan",
    "identity_confidence": "verified_live_readback"
  },
  "active_config_paths": {
    "home_root": "/home/claude/.claude",
    "files": [
      {
        "path": "/home/claude/.claude/settings.json",
        "kind": "primary_settings",
        "status": "observed"
      }
    ],
    "directories": [
      {
        "path": "/home/claude/.claude/tasks",
        "kind": "runtime_history",
        "status": "observed"
      }
    ]
  },
  "tool_directories": {
    "root": "/srv/tools",
    "entries": [
      {
        "name": "email",
        "status": "observed"
      }
    ]
  },
  "auth_cache_categories": {
    "path": "/home/claude/.claude/mcp-needs-auth-cache.json",
    "categories": [
      "gmail",
      "google_calendar",
      "google_drive"
    ],
    "values_exported": false
  },
  "single_writer_contract": {
    "shared_write_enabled": false,
    "approved_use": "read_only_projection",
    "writes_require_separate_review": true
  }
}
```

## Field Guidance

### `schema_version`

- Required.
- Bump when the allowed export shape changes.

### `snapshot_kind`

- Required.
- Fixed value: `claude_host_read_only`.

### `captured_at`

- Required.
- ISO-8601 timestamp for the observed snapshot or derived artifact.

### `source_basis`

- Required.
- Must identify whether the artifact is:
  - `live_readback`
  - `local_durable_note`
  - `derived_example`
- `local_evidence_refs` should point to repo-local proof surfaces when available.

### `host_identity`

- Required.
- Allowed fields:
  - `login_user`
  - `hostname`
  - `address`
  - `label`
  - `identity_confidence`
- Do not add SSH keys, password guidance, askpass helper locations, or connection commands here.

### `active_config_paths`

- Required.
- Split between `files` and `directories`.
- Each entry should use:
  - `path`
  - `kind`
  - `status`
- `kind` should be descriptive and non-secret, for example:
  - `primary_settings`
  - `local_settings`
  - `auth_cache`
  - `history_log`
  - `task_history`
  - `session_history`
  - `session_env`
  - `shell_snapshots`
  - `telemetry`

### `tool_directories`

- Required.
- Keep this to top-level service/tool directory names under the approved root.
- Do not recursively enumerate protected-side contents in this first contract.

### `auth_cache_categories`

- Required.
- Export category names only.
- Do not export tokens, opaque IDs, email addresses, refresh state, or cache payloads.

### `single_writer_contract`

- Required.
- Must remain:
  - `shared_write_enabled: false`
  - `approved_use: "read_only_projection"`
- This contract is descriptive evidence, not write authority.

## Verified Local Basis For Version 1

This contract version is grounded in repo-local durable state already recorded from non-secret live readback:

- host identity verified as `claude` on `reatan` (`192.168.55.205`)
- active config surfaces observed under `/home/claude/.claude`
- tool root observed under `/srv/tools`
- pending auth categories observed for Gmail, Google Calendar, and Google Drive

## First Approved Uses

- local bridge planning in `ai_workspace`
- Workspaceboard planning for future read-only UI/readback work
- overlap-matrix and handoff alignment

## Not Approved Yet

- automatic polling or sync from protected-side state
- any writable shared task/document bridge
- MI/Papers shared writes
- auth repair or cache mutation
- protected-side runtime control

## Durable Proof

Initial repo-local contract files:

- `ai-bridge/contracts/claude-host-read-only-snapshot-contract.md`
- `ai-bridge/artifacts/claude-host-read-only-snapshot.example.json`
