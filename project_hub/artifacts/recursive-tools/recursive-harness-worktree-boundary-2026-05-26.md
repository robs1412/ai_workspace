# Recursive Harness Worktree Boundary

- Recorded: 2026-05-26 20:12 CDT
- Scope: repo-local recursive experiment harness hardening while waiting for the BID Square API secure runtime reply from Claude.

## Change

`scripts/recursive_experiment_harness.py` now creates and verifies a real Git linked worktree for each run instead of treating an empty `worktree/` directory under the main checkout as isolated.

The harness now:

- resolves each run's worktree path through `worktree_path(run_id)`;
- treats a worktree as valid only when `git rev-parse --show-toplevel` equals the run's `worktree/` directory and `.git` exists there;
- removes only empty placeholder worktree directories before creating a linked worktree;
- refuses a non-empty path that is not an owned Git worktree;
- creates a branch named `recursive/<run-id>` when a run first needs a worktree;
- records `worktree_state` in each run report.

`.gitignore` now ignores `project_hub/recursive-runs/*/worktree/` so nested worktree contents do not pollute the main ai_workspace checkout.

## Readback

Owned worktrees were created for the existing baseline runs:

- `planner-proof-harness-001` on branch `recursive/planner-proof-harness-001`
- `truth-drift-harness-001` on branch `recursive/truth-drift-harness-001`

Both now appear in `git worktree list --porcelain`, and both report their own `worktree/` directory as the Git top-level.

## Verification

- `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- `scripts/recursive_experiment_harness.py --help`
- Re-running `init` for both existing runs created/verified owned linked worktrees.
- Negative evaluator-mutation check returned `run already has an immutable evaluator; create a new run for changes`.
- Negative surface-mismatch check returned `attempt surface must match run surface: scripts/task_flow_truth_drift_check.py`.
- Planner proof attempt `worktree-boundary-20260526` passed and was marked `keep`.

Proof files:

- `project_hub/recursive-runs/planner-proof-harness-001/proofs/worktree-boundary-20260526.json`
- `project_hub/recursive-runs/planner-proof-harness-001/proofs/worktree-boundary-20260526.stdout.txt`
- `project_hub/recursive-runs/planner-proof-harness-001/proofs/worktree-boundary-20260526.stderr.txt`

## Boundary

No mailbox, OPS/Portal, credential, daemon, production, or live mutator work was performed. The only live-ish proof was the existing read-only Planner proof evaluator.
