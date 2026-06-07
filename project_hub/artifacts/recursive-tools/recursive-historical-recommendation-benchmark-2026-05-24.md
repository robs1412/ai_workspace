# Recursive Historical Recommendation Benchmark

- Recorded: 2026-05-24 13:30 CDT
- Scope: replay known recursive-lane states and score next-action recommendations

## Totals

- Cases: `7`
- Passed: `7`
- Failed: `0`

## Cases

- python-migration-complete-clean: `pass`
  - Source: 2026-05-24 python entrypoint migration closeout
  - Expected: `add-recommendation-quality-benchmark`
  - Observed: `add-recommendation-quality-benchmark`
  - State: `parity_drift=0; truth_drift=0; proof_closeout_issues=0; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=True`
  - Rationale: After interpreter migration and parity cleanup are complete, the next recursive value is measuring recommendation quality.
- service-parity-drift-broad-runtime: `pass`
  - Source: 2026-05-24 pre-runtime-reconcile service parity scan
  - Expected: `fix-service-parity-drift`
  - Observed: `fix-service-parity-drift`
  - State: `parity_drift=48; truth_drift=0; proof_closeout_issues=0; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=False`
  - Rationale: Concrete runtime drift should be reconciled before adding new recursive surfaces.
- truth-drift-cleanout-active: `pass`
  - Source: 2026-05-24 concurrent inbox and truth-drift cleanup
  - Expected: `do-not-race-live-cleanup`
  - Observed: `do-not-race-live-cleanup`
  - State: `parity_drift=0; truth_drift=17; proof_closeout_issues=0; cleanup_active_elsewhere=True; registry_ok=True; coverage_ok=True; skill_loop_proven=True`
  - Rationale: When another terminal is already repairing live truth drift, the recursive lane should avoid duplicate mutation.
- truth-drift-single-open-item: `pass`
  - Source: 2026-05-24 live recommendation snapshot
  - Expected: `repair-truth-drift`
  - Observed: `repair-truth-drift`
  - State: `parity_drift=0; truth_drift=1; proof_closeout_issues=0; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=True`
  - Rationale: A remaining contradiction with no active cleanup owner should become the next repair or exact-blocker target.
- truth-clean-proof-issues-remain: `pass`
  - Source: 2026-06-07 truth-drift clean with proof-closeout issue classes
  - Expected: `classify-proof-closeout-issues`
  - Observed: `classify-proof-closeout-issues`
  - State: `parity_drift=0; truth_drift=0; proof_closeout_issues=11; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=True`
  - Rationale: Zero contradiction drift is not a clean recursive state when proof issue classes remain; classify the issue classes before returning to monitor mode.
- registry-coverage-contract-added: `pass`
  - Source: 2026-05-24 registry and coverage hardening
  - Expected: `repair-registry-contract`
  - Observed: `repair-registry-contract`
  - State: `parity_drift=0; truth_drift=0; proof_closeout_issues=0; cleanup_active_elsewhere=False; registry_ok=False; coverage_ok=False; skill_loop_proven=True`
  - Rationale: Checker metadata drift invalidates later automation, so the registry contract must be repaired first.
- local-skill-loop-not-yet-proven: `pass`
  - Source: 2026-05-24 before local useful-codex-skills smoke
  - Expected: `prove-local-skill-loop`
  - Observed: `prove-local-skill-loop`
  - State: `parity_drift=0; truth_drift=0; proof_closeout_issues=0; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=False`
  - Rationale: When drift is clean but the planning/refactor chain has not been tested, prove the skill loop before more autonomous execution.

## Autonomy Readback

- This is the first larger recommendation-quality corpus for the recursive lane.
- It is still recommendation-only; it does not execute repairs.
- The next autonomy step is an approval-gated proposal queue for fix classes that have passing historical and live recommendation coverage.
