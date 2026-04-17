# OPS Market Events Trainual Acceptance Checklist

Status: planning-only draft

## Planning Slice Acceptance

- Module outline identifies audience, scope, out-of-scope boundaries, and lesson sequence.
- Walkthrough script is user-facing and avoids internal implementation detail.
- Recording checklist includes approval, privacy, credential, demo-data, and post-review gates.
- Safe demo-data notes define what can be shown and what must be avoided.
- Recording output convention points to `ai_workspace/recordings/` and keeps large media out of git.
- The pack explicitly excludes recording, publishing, code changes, live data mutation, email, secrets, deploys, and external-system writes.
- The pack aligns with the approved Trainual recording standard in `AGENTS.md`.

## Future Recording Readiness

- A safe demo event exists or has been requested.
- The target OPS environment is identified.
- The future recorder knows whether saving is allowed. Default is no.
- Any differences between demo and production behavior can be captured in notes.
- Robert has approved the specific recording attempt before recording begins.

## Next Decision After Acceptance

After Robert accepts this planning slice, decide whether to:

- create a future `ws ops` task to prepare safe demo records,
- create a future `ws ops` task to record the walkthrough,
- create a reusable Trainual skill/checklist for other modules,
- or keep this as a one-off planning pack until the Market Events workflow is more stable.
