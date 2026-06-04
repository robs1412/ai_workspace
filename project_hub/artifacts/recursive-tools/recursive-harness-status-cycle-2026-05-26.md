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

## 2026-06-03 Status Check

- recorded_input: `ai_manager_inputs` row `2565`
- current_main_head: `6ea99df`
- status_readback: `/usr/local/bin/python3.13 scripts/recursive_experiment_harness.py status --run-id recursive-harness-status-001 --limit 5`
- readback_result: `ok=true`, `attempt_count=1`, kept attempt `add-status-command-20260526`
- worktree_state: owned worktree still exists on branch `recursive/recursive-harness-status-001`, head `b7c7b73`, with `scripts/recursive_experiment_harness.py` dirty
- promotion_status: stale old worktree patch; `promote --dry-run` failed because the patch no longer applies to current `main`
- recursive_improvement_started: promotion proof now records apply-check status and failure detail instead of leaving a success-shaped proof before `git apply --check`
- verification: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`

## Token Boundary

Use a 4k-token soft cap per recursive attempt, with a 6k hard stop unless Robert explicitly expands scope. Each attempt should include one hypothesis, one mutable surface, one immutable evaluator, one compact proof JSON, and a short final status. If the attempt needs more than 6k tokens to explain, split it into a new run or a follow-up attempt instead of expanding the current attempt.

## Next 2026-06-03

Commit or otherwise settle the in-progress `scripts/recursive_experiment_harness.py` promotion-proof change, then rerun `promote --dry-run` from a clean main checkout. Expected proof outcome for the old May worktree is `promotion_status=apply_check_failed`, which cleanly documents that the May patch is stale rather than promotable.

## 2026-06-03 Promotion Dry-Run Proof

- recorded_input: `ai_manager_inputs` row `2567`
- committed_harness_update: `1dc565a`
- command: `/usr/local/bin/python3.13 scripts/recursive_experiment_harness.py promote --run-id recursive-harness-status-001 --attempt-id add-status-command-20260526 --dry-run`
- result: `ok=false`, `promotion_status=apply_check_failed`
- proof: `project_hub/recursive-runs/recursive-harness-status-001/proofs/add-status-command-20260526-promote.json`
- patch_sha256: `9f8174e25bb9ebd1a63bd442b108b7b1b4494a2add55ca9c2a2d0a428aa86bf8`
- apply_check_error: `scripts/recursive_experiment_harness.py: patch does not apply`
- interpretation: the old May kept patch is stale against current `main`; do not promote it. Start the next recursive improvement as a fresh run against current `main`.

## 2026-06-03 Fresh Recursive Improvement

- run_id: `recursive-promotion-status-001`
- attempt_id: `add-promotion-proof-status-20260603`
- hypothesis: status output should include latest promotion proof summaries so stale recursive patches are visible without opening proof JSON
- evaluator: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- verification_metric: `0`
- promotion: `applied`
- promotion_patch_sha256: `c00c1aaf22ab330df1bc0bfbd453631ae8c53265cbbee540d3cdd2da11abc80e`
- readback: `/usr/local/bin/python3.13 scripts/recursive_experiment_harness.py status --run-id recursive-harness-status-001 --limit 2` now includes `promotion_proofs[0].promotion_status=apply_check_failed`

## 2026-06-03 Worktree Retirement Readback

- recorded_input: `ai_manager_inputs` row `2569`
- run_id: `recursive-worktree-retire-status-001`
- attempt_id: `add-worktree-retire-status-20260603`
- hypothesis: a bounded `retire-worktree` command can report stale owned worktrees and blockers without manual filesystem inspection or accidental deletion
- evaluator: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- verification_metric: `0`
- promotion: `applied`
- promotion_patch_sha256: `7f29124f17e6153db8c495321798917a6dc851fadff618643ec29582cf7c4d46`
- readback: `/usr/local/bin/python3.13 scripts/recursive_experiment_harness.py retire-worktree --run-id recursive-harness-status-001` returns `can_retire=false`, `blockers=["worktree_dirty"]`, `latest_promotion_proof.promotion_status=apply_check_failed`
- apply_gate: `retire-worktree --apply` refuses with `worktree is not retireable: worktree_dirty`

## 2026-06-03 Dirty Worktree Diff Readback

- recorded_input: `ai_manager_inputs` row `2571`
- run_id: `recursive-worktree-diff-status-001`
- attempt_id: `add-worktree-diff-status-20260603`
- hypothesis: a read-only `worktree-diff` command can summarize dirty recursive worktrees with file list, patch bytes, preview, and patch hash before any retirement decision
- evaluator: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- verification_metric: `0`
- promotion: `applied`
- promotion_patch_sha256: `696391547e53f86ea612b0db8fd29e3988f970ffe82a3b2051ad2c0139570c2c`
- readback: `/usr/local/bin/python3.13 scripts/recursive_experiment_harness.py worktree-diff --run-id recursive-harness-status-001 --preview-lines 8`
- dirty_patch_sha256: `9f8174e25bb9ebd1a63bd442b108b7b1b4494a2add55ca9c2a2d0a428aa86bf8`
- dirty_patch_bytes: `3729`
- dirty_files: `["M scripts/recursive_experiment_harness.py"]`
- interpretation: the dirty May worktree patch hash matches the stale promotion proof hash, so the next step can safely add a superseded-patch retirement gate keyed to that hash.

## 2026-06-03 Superseded Patch Retirement

- recorded_input: `ai_manager_inputs` row `2572`
- run_id: `recursive-superseded-retire-001`
- attempt_id: `add-superseded-retire-gate-20260603`
- hypothesis: a hash-keyed superseded-patch gate can retire stale dirty recursive worktrees only when the dirty patch hash matches recorded proof
- evaluator: `/usr/local/bin/python3.13 -m py_compile scripts/recursive_experiment_harness.py`
- verification_metric: `0`
- promotion: `applied`
- promotion_patch_sha256: `23e4ef40a87df5e67d64a80053fd5220e9734e13d29d3028413dd2473628e9fc`
- dry_run: `retire-worktree --run-id recursive-harness-status-001 --superseded-patch-sha256 9f8174e25bb9ebd1a63bd442b108b7b1b4494a2add55ca9c2a2d0a428aa86bf8` returned `can_retire=true`, `dirty_is_superseded=true`, `blockers=[]`
- apply: `retire-worktree --run-id recursive-harness-status-001 --superseded-patch-sha256 9f8174e25bb9ebd1a63bd442b108b7b1b4494a2add55ca9c2a2d0a428aa86bf8 --apply` returned `retired=true`
- readback: `project_hub/recursive-runs/recursive-harness-status-001/worktree` is removed; subsequent `retire-worktree --run-id recursive-harness-status-001` reports `worktree_missing_or_unowned`

## 2026-06-03 Git Hygiene Inventory Script

- recorded_input: `ai_manager_inputs` row `2587`
- script: `scripts/git_hygiene_inventory.py`
- mode: read-only; no fetch, clean, reset, stash, commit, push, or delete
- default_readback: `/usr/local/bin/python3.13 scripts/git_hygiene_inventory.py --root /Users/werkstatt --dirty-only`
- default_result: `repos_scanned=30`, `dirty_repos=3`
- dirty_repos: `/Users/werkstatt/ai_workspace`, `/Users/werkstatt/bid`, `/Users/werkstatt/salesreport`
- worktree_mode: `--include-worktrees` intentionally includes recursive run worktrees
- worktree_mode_result: `repos_scanned=36`, `dirty_repos=7`, including four dirty recursive worktrees from prior promoted runs
- next: add proof-backed retirement for promoted recursive worktrees, then use this inventory script as the regular "clean all repos?" starting point

## 2026-06-04 Promoted Recursive Worktree Retirement

- recorded_input: `ai_manager_inputs` row `2657`
- scope: proof-backed retirement only for owned recursive worktrees whose dirty patch hash exactly matched an applied promotion proof
- retired_run_ids: `recursive-git-hygiene-file-groups-001`, `recursive-git-hygiene-group-detail-001`, `recursive-git-hygiene-plan-001`, `recursive-git-hygiene-repo-detail-001`, `recursive-promotion-status-001`, `recursive-superseded-retire-001`, `recursive-worktree-diff-status-001`, `recursive-worktree-retire-status-001`
- proof_gate: for each run, `worktree-diff --preview-lines 0` patch hash matched `status` latest `promotion_proofs[0].patch_sha256`; each `retire-worktree --superseded-patch-sha256 <hash>` dry-run returned `can_retire=true` and `blockers=[]`
- apply_readback: each `retire-worktree --apply` returned `retired=true`; follow-up `git worktree list --porcelain` shows only the main checkout plus `planner-proof-harness-001` and `truth-drift-harness-001`; follow-up `retire-worktree --run-id recursive-git-hygiene-file-groups-001` reports `worktree_missing_or_unowned`
- inventory_readback: `/usr/local/bin/python3.13 scripts/git_hygiene_inventory.py --root /Users/werkstatt --dirty-only --include-worktrees` now returns `repos_scanned=32`, `dirty_repos=5`, matching the normal dirty-repo set; no dirty recursive worktrees remain in inventory
- remaining_git_hygiene: read-only plan still shows dirty normal repos `/Users/werkstatt/ai_workspace`, `/Users/werkstatt/bid`, `/Users/werkstatt/ops`, `/Users/werkstatt/salesreport`, and `/Users/werkstatt/workspaceboard`; no fetch, reset, stash, commit, push, or cleanup was run on those repos
