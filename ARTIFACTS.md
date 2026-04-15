# Artifact Handling

This repository is the coordination index, not bulk storage.

## Default Rule

Commit small, reviewable text records to git. Do not commit large binaries, generated files, runtime state, dependency folders, recordings, archives, mailbox exports, database dumps, screenshots, videos, PDFs, or secret-adjacent outputs unless Robert explicitly approves a narrow exception.

## Large File Pattern

Store large non-secret files outside this repo, then commit a small manifest that records:

- artifact title
- owner/workspace
- storage location
- size
- SHA-256 checksum
- created date
- retention decision
- whether the file is safe to share with Codex, Claude, Papers, or humans only

Use `project_hub/` for the human-readable project context and link to the manifest from the relevant project note.

## Storage Classes

- `git`: small markdown/json/text coordination records only.
- `local-artifact`: machine-local or LAN/NAS file storage for large non-secret files.
- `papers`: human-readable shared documents or curated work records, with a single-writer rule until Codex/Claude conflict handling is designed.
- `private`: credentials, secrets, OAuth tokens, private keys, password-like outputs, mailbox credentials, and private MCP config. These do not belong in git, Papers, or normal artifact manifests.
- `runtime`: LaunchAgent runtimes, logs, tmux/session state, caches, dependency folders, virtualenvs, generated output, and temp files. These stay machine-local unless deliberately archived.

## Manifest Template

```markdown
# Artifact: <title>

- Owner/workspace:
- Storage class:
- Location:
- Size:
- SHA-256:
- Created:
- Retention:
- Share scope:
- Related project:
- Notes:
```
