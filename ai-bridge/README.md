# AI Bridge

This directory holds repo-local bridge planning artifacts for Codex and Claude coordination.

Current scope is intentionally narrow:

- read-only, non-secret metadata contracts
- local planning and example artifacts
- no writable shared task/document bridge
- no protected-side mutation

Authoritative local policy remains in:

- `AGENTS.md`
- `worker_roles/claude-bridge-worker.md`
- `worker_roles/codex-claude-overlap-matrix.md`
- `HANDOFF.md`

Current artifact set:

- `contracts/claude-host-read-only-snapshot-contract.md`
- `artifacts/claude-host-read-only-snapshot.example.json`
