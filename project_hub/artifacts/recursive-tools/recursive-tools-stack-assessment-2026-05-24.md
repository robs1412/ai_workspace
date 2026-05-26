# Recursive Tools Stack Assessment

- Recorded: 2026-05-24 08:24 CDT
- Scope: non-secret assessment of recursive tooling for Codex and adjacent agent workflows

## Recommendation

Adopt recursive tooling as a narrow improvement lane, not as a default operating mode across the stack.

## Current Read

- `grp06/useful-codex-skills` is the lowest-risk immediate addition. Its value is structured planning, refactor candidate selection, ExecPlan creation, and plan execution discipline. It fits the existing source-first, explicit-state workflow better than open-ended autonomous recursion.
- `kayba-ai/recursive-improve` is the strongest first experiment for agent self-improvement, but only inside a sandbox with explicit evals, branch isolation, and keep-or-revert gates.
- `grp06/recursive-codex` is a specialized frontend improvement loop. It is potentially useful for UI-heavy repos such as `forge` or `workspaceboard`, but it should not be treated as general stack infrastructure.

## Operating Split

- Default lane: keep existing explicit worker/task flow with human-directed execution.
- Improvement lane: use recursive tooling only to improve the tools, prompts, and repo-local workflows themselves.
- Production-facing lanes: do not allow unattended recursive mutation on OPS, Portal, mailbox runtimes, or other owner-visible operational surfaces.

## First Pilot

Use `recursive-improve` as the first contained test.

Pilot shape:

1. Create a repo-local sandbox under `ai_workspace`.
2. Clone the upstream repository and install it into a local virtual environment instead of making a machine-global tool change.
3. Keep trace capture and eval artifacts local to the sandbox.
4. Limit the first run to one narrow target: improve a non-secret local helper or worker prompt packet, not an owner-facing runtime.
5. Require manual review before merging any generated changes into a real workspace.

## Guardrails

- No secret-bearing traces in the pilot dataset.
- No automatic merge or deploy behavior.
- No runtime edits outside the selected sandbox target.
- Benchmark/eval output must be readable and durable before any claim that the recursive pass helped.
- Keep task/project tracking in OPS plus local project-hub notes; do not let the recursive loop become the task system.

## Follow-Up Items

- Pull the actionable patterns from `useful-codex-skills` into local planning/refactor workflow.
- Complete the first `recursive-improve` smoke run and document what the trace/eval loop actually produces in this environment.
- Decide later whether `recursive-codex` is worth a UI-only pilot for `forge` or `workspaceboard`.
