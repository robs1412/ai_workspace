# OPS Market Events Trainual Planning Pack

Status: planning-only draft
Owner/workspace: AI Workspace planning; implementation and later recording belong in `ws ops` after approval
Last updated: 2026-04-16

## Purpose

Prepare the first Trainual slice for OPS Market Events so a future recording session can be run safely, consistently, and without exposing live data or secrets.

This pack is intentionally limited to local planning documents. It does not authorize or perform recording, publishing, code changes, live data mutation, email, credential access, or deploys.

## Files

- `outline.md` - module scope, audience, learning goals, and lesson sequence.
- `walkthrough-script.md` - user-facing narration and step flow for the future recording.
- `recording-checklist.md` - preflight, during-recording, and post-recording checks.
- `safe-demo-data-notes.md` - guidance for demo records, redaction, and mocked/seeded flow labeling.
- `recordings-output-convention.md` - naming and manifest convention for future outputs under `ai_workspace/recordings/`.
- `acceptance-checklist.md` - criteria for accepting this planning slice and deciding the next step.

## Guardrails

- Use the approved Trainual recording standard from `AGENTS.md`.
- Keep future user-facing recordings manual-paced with visible pointer movement and no overlays unless Robert explicitly requests them.
- Prefer safe demo or seeded data. If actual workflow data is used, verify that it is safe for training distribution first.
- Do not record credentials, 2FA, tokens, secret calendar links, private mailbox contents, personal contact details, payment data, or admin-only screens.
- Do not mutate live OPS, Portal, Salesreport, Login, CRM, or calendar data during planning.
- Do not publish or upload outputs until Robert approves the specific recording result.
