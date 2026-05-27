# Recursive Harness Status Cycle - 2026-05-26

- recorded_input: `ai_manager_inputs` row `2294`
- taskflow_key: `taskmode-recursive-cycle-2026-05-26`
- run_id: `recursive-harness-status-001`
- attempt_id: `add-status-command-20260526`
- mutable_surface: `scripts/recursive_experiment_harness.py`
- evaluator: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- metric: `returncode`
- outcome: `keep`

## What Changed

Added a read-only `status` command to the recursive experiment harness. It summarizes the run directory, immutable evaluator, metric, owned worktree state, branch, head, dirty file list, and recent attempts as JSON.

`update_run_report()` now includes worktree branch, head, and dirty-file count so the Markdown report is useful without opening the worktree.

## Proof

- Isolated worktree: `project_hub/recursive-runs/recursive-harness-status-001/worktree`
- Branch: `recursive/recursive-harness-status-001`
- Proof file: `project_hub/recursive-runs/recursive-harness-status-001/proofs/add-status-command-20260526.json`
- Evaluator cwd: `/Users/werkstatt/ai_workspace/project_hub/recursive-runs/recursive-harness-status-001/worktree`
- Evaluator return code: `0`
- Main checkout verification: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- Main status command verified: `/usr/local/bin/python3.13 scripts/recursive_experiment_harness.py status --run-id recursive-harness-status-001 --limit 3`

## Cleanup

During the same pass, stale Avignon blocker session `2fe8ff17` was closed as superseded. The underlying Lipman/Dylan activity was already completed as Portal CRM activity `370283` and reported to Sonat with Message-ID `<177984356636.14277.11377624022039235908@kovaldistillery.com>`.

## Next

The next recursive expansion should add a promotion/apply step that can move a kept worktree patch into the main checkout with a recorded diff hash, while still requiring the immutable evaluator to pass before promotion.
