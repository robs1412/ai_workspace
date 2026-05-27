# Recursive Harness Verify From Worktree

- Recorded: 2026-05-26 20:17 CDT
- Scope: repo-local hardening follow-up after the Claude recursive update email.

## Change

`scripts/recursive_experiment_harness.py verify` now runs the immutable evaluator from the run's owned linked worktree instead of the main `ai_workspace` checkout.

This closes the remaining boundary gap after linked worktree creation: a run no longer merely owns a worktree on disk; its verifier execution now uses that worktree as `cwd`.

## Verification

- `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- Planner run attempt `verify-from-worktree-20260526` passed and was marked `keep`.
- Proof JSON records:
  - `returncode=0`
  - `metric=passed`
  - `evaluator_cwd=/Users/werkstatt/ai_workspace/project_hub/recursive-runs/planner-proof-harness-001/worktree`

Proof files:

- `project_hub/recursive-runs/planner-proof-harness-001/proofs/verify-from-worktree-20260526.json`
- `project_hub/recursive-runs/planner-proof-harness-001/proofs/verify-from-worktree-20260526.stdout.txt`
- `project_hub/recursive-runs/planner-proof-harness-001/proofs/verify-from-worktree-20260526.stderr.txt`

## Boundary

No mailbox, OPS/Portal, credential, daemon, production, or live mutator work was performed. The proof command was the existing read-only Planner proof evaluator.
