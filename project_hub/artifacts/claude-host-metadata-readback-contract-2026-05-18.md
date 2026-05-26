# Claude Host Metadata Readback Contract

Date: `2026-05-18`
Master Incident ID: `AI-INC-20260518-CLAUDE-HOST-PARITY-01`
OPS durable anchor: project `369808`, task `369809`

## Purpose

Record the exact non-secret Claude host metadata surface that local AI Workspace docs may cite as current.

This artifact exists so docs alignment for task `369809` points at one narrow contract instead of scattering the same path correction across handoff prose, bridge notes, and worker-role comparisons.

## Verified Host Facts

- Shell user: `claude`
- Hostname: `reatan`
- Host IP: `192.168.55.205`
- Active Claude state root: `/home/claude/.claude`

## Current Config Surface

Treat these three files as the current authoritative host-level Claude config/readback surface:

1. `/home/claude/.claude/settings.json`
2. `/home/claude/.claude/settings.local.json`
3. `/home/claude/.claude/mcp-needs-auth-cache.json`

## Interpretation Rules

- Do not treat `/home/claude/.claude/.mcp.json` as the current host-level source of truth.
- Plugin-local `.mcp.json` files may still exist, but they are narrower plugin artifacts rather than the authoritative host-level config surface.
- `mcp-needs-auth-cache.json` is the readback surface for pending auth dependencies; it is not a secret export target.
- This contract is read-only and documentation-oriented. It does not authorize protected-side edits, SSH config mutation, or credential movement.

## Local Documentation Rule

When AI Workspace or AI Bridge docs describe the Claude host config surface, they should:

- cite the three verified files above;
- describe the surface as layered rather than singular;
- distinguish host-level config from plugin-local MCP files;
- keep secret-bearing contents out of repo docs, chat, and handoff records.

## Verification

- Verified previously from approved live `.205` readback captured in the parity project note and `HANDOFF.md`.
- Rechecked locally on `2026-05-18` by confirming repo docs now align to this contract and no active local note still depends on `/home/claude/.claude/.mcp.json` as the host-level target.

## Proof Marker

`CLAUDE_HOST_DOCS_ALIGNED project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md:1`
