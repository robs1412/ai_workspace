# Recursive Run recursive-superseded-retire-001

- updated_at: `2026-06-03 14:59:02 CDT`
- surface: `scripts/recursive_experiment_harness.py`
- metric: `returncode`
- evaluator: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- worktree: `worktree`
- worktree_state: `owned_git_worktree`
- worktree_branch: `recursive/recursive-superseded-retire-001`
- worktree_head: `a2157c3`
- worktree_dirty_files: `1`

## Attempts

| attempt | status | metric | proof | reason |
| --- | --- | --- | --- | --- |
| add-superseded-retire-gate-20260603 | keep | 0 | proofs/add-superseded-retire-gate-20260603.json | Kept: evaluator passed and dry-run only retires dirty stale worktrees when supplied superseded patch hash matches. |
