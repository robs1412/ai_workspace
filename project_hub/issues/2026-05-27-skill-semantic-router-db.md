# Skill Semantic Router Database

Date: 2026-05-27

## Goal

Build a metadata-first semantic router/database for Codex skills so the full skill catalog does not need to live in startup context. The intended first index fields are skill name, description, path, and tags, with top-candidate retrieval followed by reading only the selected `SKILL.md` body.

## Current State

- Robert asked Codex to take Dmytro's suggestion and first ask Claude how he is already handling skill indexing/routing.
- Frank emailed Claude, copied Robert and Dmytro, asking for implementation details: store/schema, embedded fields, refresh cadence, retrieval API/command, false-positive filtering, runtime candidate count, and failure modes.
- Claude email proof: Message-ID `<177989532315.92775.9949112713099748975@kovaldistillery.com>`.
- Task-mode durable input recorder row: `2347`.
- Task Flow source ref: `chat-robert-skill-semantic-router-2026-05-27`.

## OPS Task

Requested OPS due date: `2026-05-28`.

Initial create attempt was blocked:

- `/Users/werkstatt/ops/scripts/create_codex_task.php` returned `CRM API error: HTTP 500` on the Codex impersonation path.
- Explicit service fallback also failed because the service login reports mandatory password reset for `testuser2`.
- No raw direct OPS task DB insert was performed because that bypasses the normal CRM/Portal task behavior.

Retry succeeded after the OPS helper path recovered:

- OPS task: `370302`
- Title: `Build semantic Codex skill database after Claude readback`
- Status: `Not Started`
- Due/start: `2026-05-28`
- Creator: Robert `1`
- Owner/assignee: Codex `1332`
- Readback: `smcreatorid=1`, `smownerid=1332`, `assigned_user_ids=1332`, `deleted=0`.

## Next Step

1. Wait for Claude's reply on `Skill semantic router question`.
2. Build the first Codex skill index/router from Claude's readback under OPS task `370302`, keeping diagnostics metadata-first and avoiding full catalog prompt injection.
