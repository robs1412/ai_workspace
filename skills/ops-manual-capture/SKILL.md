---
name: ops-manual-capture
description: Use for `/Users/werkstatt/ops` manual refreshes that need screenshot capture, screen-recording prep, or OPS workflow documentation updates. Trigger when the user asks to update an OPS manual, recapture manual screenshots, create a short recording/still workflow, or document project-management/design-mode flows from the real OPS UI.
---

# OPS Manual Capture

Use this skill for the OPS documentation lane when the work includes any of:

- refreshing `/Users/werkstatt/ops/docs/project_management_manual.php`
- recapturing screenshots in `/Users/werkstatt/ops/docs/assets/project_management_manual/`
- preparing a short OPS walkthrough recording
- documenting design-mode, task-detail, project-detail, or task-file-link workflows

## Workflow

1. Start from the real OPS code and handoff state.
   - Read `/Users/werkstatt/ops/HANDOFF.md`.
   - Read the target manual page under `/Users/werkstatt/ops/docs/`.
   - Verify the current code paths that the manual claims to describe.

2. Pick stable demo records before capture.
   - Prefer one real design-tracked project, one non-design project, and one linked task that render cleanly.
   - Record the exact IDs used in the handoff or manual note when they matter for future recapture.

3. Run the capture preflight before trying screenshots.
   - Use `scripts/check_prereqs.sh`.
   - If Playwright, local login env, or the 2FA lookup path is missing, stop and report the exact blocker.
   - Do not claim screenshots were refreshed unless the files were actually regenerated.

4. Use the OPS capture script instead of rebuilding the flow by hand.
   - Current entry point: `/Users/werkstatt/ops/tmp/project_management_manual_capture.js`
   - If the capture set changes, update that script rather than inventing a one-off command in chat.

5. Manual refresh order:
   - update the durable handoff first
   - revise the manual text to match the actual UI
   - capture or refresh screenshots
   - re-check the manual for stale claims or missing views

## Current OPS Project Manual Surfaces

- Manual page:
  - `/Users/werkstatt/ops/docs/project_management_manual.php`
- Screenshot asset folder:
  - `/Users/werkstatt/ops/docs/assets/project_management_manual/`
- Capture script:
  - `/Users/werkstatt/ops/tmp/project_management_manual_capture.js`

## Required UI Coverage

When the user asks for a full refresh, check these surfaces explicitly:

- Tasks main page
- Tasks in Design Mode
- Calendar
- Project detail view
- Task detail view
- Enable Design Mode flow on a project, including the finish-task gate popup/form
- Design-specific task creation/filter fields such as `Family`, `Component`, and `Size`
- Task file links using Google Drive URLs
- Project Files section, including files inherited from linked tasks

## Screen Recording Convention

For approved recordings, follow `/Users/werkstatt/ai_workspace/recordings/README.md`.

- Keep large media out of git unless a narrow exception is approved.
- Store recordings under:
  - `recordings/trainual/ops-project-management/YYYY-MM-DD/`
- Pair the media with a small manifest.
- Use `scripts/init_recording_manifest.sh YYYY-MM-DD` to create the folder and manifest stub.

## Notes

- This skill is OPS-specific; do not use it for unrelated websites or generic screenshot work.
- Keep secrets out of the skill, the manifest, and git.
- If the capture environment is broken, document the blocker in the OPS handoff so the next pass starts from the real failure instead of rediscovering it.
