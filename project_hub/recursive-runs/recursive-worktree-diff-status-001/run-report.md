# Recursive Run recursive-worktree-diff-status-001

- updated_at: `2026-06-03 14:48:55 CDT`
- surface: `scripts/recursive_experiment_harness.py`
- metric: `returncode`
- evaluator: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- worktree: `worktree`
- worktree_state: `owned_git_worktree`
- worktree_branch: `recursive/recursive-worktree-diff-status-001`
- worktree_head: `316d255`
- worktree_dirty_files: `1`

## Attempts

| attempt | status | metric | proof | reason |
| --- | --- | --- | --- | --- |
| add-worktree-diff-status-20260603 | keep | 0 | proofs/add-worktree-diff-status-20260603.json | Kept: evaluator passed and worktree-diff reports dirty file list, patch bytes, preview, and patch hash for stale recursive worktrees. |
