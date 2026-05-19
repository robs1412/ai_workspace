# Square Manual Task Lane

Updated: 2026-05-19

## Purpose

Keep Square direct-send work explicitly manual so it does not get picked up as an AI-runner task.

## Decision

- `Mark DeSimone` owns the Square direct-send lane.
- `Claude` does not own this lane.
- `Codex` does not own this lane.
- The lane should stay manual unless Robert approves a separate automation plan.
- Forge should still list the row, but OPS should not treat it as an autonomous AI-runner lane.

## Proposed Task Shape

- Forge planner row: `26` / `Square Events push`
- Forge planner row: `27` / `Square General`
- Task owner: `Mark DeSimone`
- Role owner: `Manual`
- Human owner / approver: `Mark DeSimone` or Robert, depending on the send authority for the specific row
- Cadence: monthly / bi-weekly as set on the row
- Deliverable: a manual send confirmation or prepared draft for human send
- Proof: manual confirmation plus the row status update, or one exact blocker

## Working Rules

- Do not route Square direct-send rows into Claude or Codex queues.
- Do not create OPS runner tasks for Square unless the task is explicitly approved as automation.
- Keep the planner row clear about the manual owner so the board does not imply autonomous execution.

## Mirror Later

If Square ever becomes partially automated, update the live planner row and create a new OPS task lane instead of reusing the Claude or Codex lanes.
