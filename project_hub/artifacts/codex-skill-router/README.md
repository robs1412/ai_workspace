# Codex Skill Router

This is the first repo-local metadata-first skill router for Codex.

Claude's readback for the comparable Claude-side pattern was logged through Frank on 2026-05-27 as:

- Source Message-ID: `<3e097d60f906a33671a657b2623fff0a.claude@kovaldistillery.com>`
- Subject: `Re: Skill semantic router question`
- Runtime summary: no vector database; two-tier lazy loading; the LLM acts as router.

## Contract

- Build an index from `SKILL.md` frontmatter and paths only.
- Store skill `name`, `description`, `path`, and inferred `tags`.
- Do not load full skill bodies during candidate retrieval.
- Read a selected `SKILL.md` body only through an explicit `show` command.

## Commands

```sh
/usr/local/bin/python3.13 scripts/codex_skill_router.py build
/usr/local/bin/python3.13 scripts/codex_skill_router.py query 'Workspaceboard stats read model mismatch' --limit 5
/usr/local/bin/python3.13 scripts/codex_skill_router.py show workspaceboard-stats-read-model
```

The default index path is `project_hub/artifacts/codex-skill-router/skill-index.json`.
