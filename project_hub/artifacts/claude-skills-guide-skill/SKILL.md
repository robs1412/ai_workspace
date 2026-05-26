---
name: claude-skills-guide
description: Reusable guide for Claude skill design and Google Drive SDK lookup patterns. Use when you need to recover or build repeatable workflow guidance for Claude skills, Google Drive docs, or AI Cloud guide files.
---

# Claude Skills Guide

Use this skill when the work is about:

- building or refining a reusable Claude skill
- turning a repeated how-to into a durable guide
- reading AI Cloud Google Docs or PDFs through the Google Drive SDK
- recovering a Google Drive doc, folder listing, or exported file body
- documenting a repeatable access pattern so the next run does not rediscover it

## Core Principles

- Think before coding.
- Keep the solution simple.
- Make surgical changes only.
- Define success criteria and verify the result.

## Reusable Skill Design Rules

1. Start with 2 to 3 concrete use cases.
2. Write the trigger conditions plainly in the skill description.
3. Keep the `SKILL.md` body focused on workflow steps.
4. Use linked files only when they reduce repetition.
5. Test one hard task first, then expand.
6. Make the skill say both what it does and when to use it.
7. Avoid vague triggers.
8. Add negative triggers if over-triggering becomes a problem.

## Google Drive SDK Lookup Pattern

Use the Drive SDK when a Google Drive link or folder needs direct verification.

Default flow:

1. Load the approved local OAuth client and token from `/.private/google-oauth/`.
2. Build the Drive client with `google.oauth2.credentials.Credentials` and `googleapiclient.discovery.build`.
3. Query the target folder or file with `supportsAllDrives=True`.
4. List the visible items in the folder before guessing at file contents.
5. If the item is a Google Doc, export the body with the Drive API.
6. If the item is a PDF, download it and extract text locally.
7. Record the result in durable workspace notes.

If a pasted link appears empty, do not assume the file is missing. Check the actual Drive SDK response first.

## Durable Recording Rule

When a workflow becomes repeatable:

- add a short guide entry in `project_hub`
- link the guide from the repeating-access note
- add a memory note only if the user explicitly wants it recorded for future sessions

## Existing Workspace References

- `project_hub/artifacts/repeating-access-guide-2026-05-20.md`
- `project_hub/artifacts/claude-skills-guide-2026-05-20.md`
- `project_hub/artifacts/google-drive-integration/google-drive-write-path-howto-2026-05-19.md`
