# Local Planning Contract

Use ExecPlans in this repo as planning artifacts, not as the operational task system.

## Rule

- In DB-first repos such as `ai_workspace`, `.agent/` artifacts are for planning/refactor workflow only.
- OPS, Portal, Workspaceboard Task Flow, project_hub, and `HANDOFF.md` remain the real durable execution surfaces.

## Expectations

- Keep plans self-contained and code-grounded.
- Prefer bounded refactors over framework churn.
- Record the exact target files, current pain, intended simplification boundary, and validation path.
- Do not let plan artifacts compete with live task state.
