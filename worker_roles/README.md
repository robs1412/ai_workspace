# Worker Roles Directory

Status: source-of-truth role reference
Updated: 2026-05-19 CDT

This folder is the durable role reference for the Codex / Claude worker system. Keep role definitions, personas, call patterns, and boundaries here so the organigram and Workspaceboard can point back to a single source of truth.

## What Lives Here

- Role docs for standing sessions, on-demand workers, specialists, and support lanes.
- Persona files for workers that need a distinct voice or signature.
- Claude-side comparison notes and bridge references that affect routing.
- Non-secret operating rules, approval gates, and durable role boundaries.

## What Does Not Belong Here

- Secrets, tokens, private keys, credential paths, or mailbox bodies.
- Runtime changes, auth/OAuth changes, router/DNS edits, or service restarts.
- Production mutation or live-pull actions.
- Hidden implementation notes that should instead live in TODO, HANDOFF, OPS, or project-hub records.

## Current Live Control Surface

- As clarified by Robert on 2026-04-20, the active Codex / Workspaceboard / organigram / git-backed `werkstatt` role surface is currently on the Mac mini at `192.168.55.230`, with the user entry point `https://wb.koval.lan/workspaceboard/`.
- The durable role source for the organigram and worker references is `/Users/werkstatt/ai_workspace/worker_roles`.
- This note records current ownership/location only. It does not approve DNS/router changes, Workspaceboard runtime changes, service restarts, OAuth/auth work, mailbox reads, credential handling, deploy/live pull, `.205` access, or production mutation.

## Primary References

- `operating-model.md`: role class, startup prompts, call signs, routing phrases, approval gates, and durable memory surfaces.
- `send-from-personas.md`: send-from registry and email ownership rules.
- `human-owners.md`: decision and approval owners.
- `codex-claude-overlap-matrix.md`: local-versus-Claude routing comparison.
- Shared worker background sources: `project_hub/artifacts/ai-workers-setup/foh-handbook-2-guide.md`, Google Drive folder `https://drive.google.com/drive/folders/1-5zAmaDT8cTKrQM3oFBKToXnh5w-qWvt`, and `https://www.koval-distillery.com/` for public KOVAL context.

## Shared Worker Background Rule

The shared handbook and KOVAL guide apply to all workers, not just one persona. Workers may use the FOH handbook export, the verified Drive docs listed below, and the public KOVAL website as general background for KOVAL facts, products, guest experience, and brand language.

Verified live Drive docs from `https://drive.google.com/drive/folders/1-5zAmaDT8cTKrQM3oFBKToXnh5w-qWvt`:

- `2026 Koval Manual.md`
- `Koval Employee Handbook 2024-08-01.md`
- `Google Drive Public BA Folder` with `General information`

These sources improve context and consistency. They do not authorize workers to invent commitments, override approval gates, guess pricing, or mutate OPS/Portal/live scheduling state without the normal routed workflow.

## Active Structure

- Governance / Humans
- Task Manager Center
- Task Manager Direct Support
- Monitoring / Coordination
- Codex / Local
- Execution / Workspace Workers
- Email / Communications
- Analyst / Project / Specialist
- Claude / Bridge
- Claude / Department
- Claude / `.205`
- Appendices / Source Notes

## Usage Rule

When a role changes, update the role doc, the persona file if one exists, the routing references, and the organigram/README summary together. Avoid partial updates that leave the directory inconsistent.
