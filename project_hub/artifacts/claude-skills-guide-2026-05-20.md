# Claude Skills Guide

Source folder:
- `AI Cloud / IT / Claude Guides`
- Google Drive folder id: `1MQPnuBzLbeTA7iuYtAm3ho8ubgw8vOK2`

Source files:
- `CLAUDE.md`
- `The-Complete-Guide-to-Building-Skill-for-Claude.pdf`

## What the doc says

`CLAUDE.md` is a short behavioral guide for coding work:
- think before coding
- keep the solution simple
- make surgical changes only
- define success criteria and verify the result

## What the PDF adds

The PDF is the useful reusable part for setup work. Its main points:

- A skill is a folder with `SKILL.md` plus optional `scripts/`, `references/`, and `assets/`.
- Use progressive disclosure:
  - frontmatter is always loaded
  - `SKILL.md` body loads when relevant
  - linked files are only opened as needed
- Write skills around 2 to 3 concrete use cases.
- Good skills are either:
  - document/asset creation
  - workflow automation
  - MCP enhancement
- Test skills in layers:
  - manual conversation testing
  - scripted repeatable testing
  - programmatic evaluation when needed
- Iterate on one hard task first, then expand coverage.
- Good skill descriptions must say both what the skill does and when to use it.
- Avoid vague triggers; add negative triggers when overloading is a risk.
- `SKILL.md` must be named exactly that.
- No `README.md` inside the skill folder.

## Why it helps us

This is useful for recurring how-to workflows in the workspace:
- Google Drive access
- Portal sample-request handling
- signature and reply templates
- reusable inbox/ops instructions
- skill creation for new repeatable agent behaviors

## Practical pattern to reuse

For a new skill or guide:
1. identify 2 to 3 concrete use cases
2. write a short `SKILL.md` frontmatter trigger
3. keep the body focused on the workflow steps
4. add scripts or references only when they reduce repetition
5. test one task first, then expand

## Recorded takeaway

This folder is a good reusable reference for future agent-memory and skill-design work, especially when the goal is to stop re-explaining the same workflow every time.
