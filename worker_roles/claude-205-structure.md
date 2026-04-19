# Claude `.205` Structure

## Purpose

Document the non-secret structure that should be represented for Claude-side work on `.205` before any live integration, MI registration, Papers write path, or MCP bridge is enabled.

## Current Known Structure

- `.205` is the KOVAL server-side environment where Claude-side work and MI/Papers-facing services live.
- `mi.koval.lan` is the authenticated management surface that can front approved internal tools.
- Papers, Mesh Memory, Agent Memory, and future MCP/workspace bridge candidates are server-side resources and must be treated as sensitive until reviewed.
- Workspaceboard can reference sanitized metadata snapshots and role records, but should not directly write `.205` records unless a single-writer contract is approved.

## Representation Goal

- Register Claude-side agents and `.205` structure in Workspaceboard as visible roles and planning surfaces.
- Register Codex integration state in MI/Papers only after a reviewed read-only projection and write contract exist.
- Keep Codex local work and Claude server work from interacting accidentally.

## Safe First Implementation

1. Keep this role doc and organigram card as the current source-of-truth representation.
2. Build a read-only work-record projection from TODO/project-hub/Workspaceboard to a sanitized metadata surface.
3. Define a Codex-to-Claude and Claude-to-Codex handoff schema.
4. Add MI/Papers registration only after approval for auth, source ownership, and write behavior.

## Boundaries

- No `.205` SSH, auth, service, DNS, Traefik, Papers, Mesh, Agent Memory, MCP, or database change is implied by this document.
- No secrets or credential paths belong here.
- No shared write path should be enabled until Codex Integration Manager and Security Guard record the single-writer and data-exposure decisions.

## Approval Gates

- `.205` access, MCP exposure, Papers writes, OAuth, live MI registration, credential handling, service restarts, or production-visible changes require explicit human approval and Security Guard review.

## Handoff Surfaces

- `worker_roles/claude-bridge-worker.md`.
- `worker_roles/claude-server-agent.md`.
- `worker_roles/codex-integration-manager.md`.
- `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`.
