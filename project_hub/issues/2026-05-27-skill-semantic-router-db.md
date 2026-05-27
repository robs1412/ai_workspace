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

## 2026-05-27 18:23 CDT Implementation

Claude's reply was found in Frank runtime proof:

- Source Message-ID: `<3e097d60f906a33671a657b2623fff0a.claude@kovaldistillery.com>`
- Subject: `Re: Skill semantic router question`
- Runtime summary: no vector database; two-tier lazy loading; the LLM acts as router.
- Frank proof: `/Users/admin/.frank-launch/state/email-trace-events.jsonl` logged the reply at `2026-05-27T10:25:37-0500`; `/Users/admin/.frank-launch/state/automation-log.jsonl` recorded the source filed to `Handled` at `2026-05-27T10:26:03-0500`.

Built the first repo-local Codex skill router:

- Script: `scripts/codex_skill_router.py`
- Index: `project_hub/artifacts/codex-skill-router/skill-index.json`
- Notes: `project_hub/artifacts/codex-skill-router/README.md`

Verification:

- `/usr/local/bin/python3.13 scripts/codex_skill_router.py build` returned `skill_count=39` and `body_loaded=false`.
- Query `Workspaceboard stats read model mismatch top-level api fields` returned `workspaceboard-stats-read-model` as the top candidate.
- Query `create or update a Codex skill for a reusable workflow` returned `skill-creator` as the top candidate.

The implementation keeps retrieval metadata-only and reads the selected `SKILL.md` body only through the explicit `show` command.
