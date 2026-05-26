# Recursive Recommendation Benchmark

- Recorded: 2026-05-24 14:05 CDT
- Scope: bounded recommendation-quality scenarios for the recursive lane

## Totals

- Scenarios: 5
- Passed: 5
- Failed: 0

## Scenario Readback

- cleanup-already-in-flight: `pass`
  - Expected: `do-not-race-live-cleanup`
  - Observed: `do-not-race-live-cleanup`
  - Rationale: When live truth drift is already being repaired elsewhere, the bounded recursive move is to stay out of that operational lane and work on checker architecture or re-read later.
  - State: `expected=do-not-race-live-cleanup; observed=do-not-race-live-cleanup; parity_drift=0; truth_drift=3; cleanup_active_elsewhere=True; registry_ok=True; coverage_ok=True; skill_loop_proven=True`
- truth-drift-needs-repair: `pass`
  - Expected: `repair-truth-drift`
  - Observed: `repair-truth-drift`
  - Rationale: When truth drift is present and there is no separate cleanup lane already carrying it, the next recursive move should be to repair the contradiction instead of expanding the checker.
  - State: `expected=repair-truth-drift; observed=repair-truth-drift; parity_drift=0; truth_drift=2; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=True`
- parity-drift-first: `pass`
  - Expected: `fix-service-parity-drift`
  - Observed: `fix-service-parity-drift`
  - Rationale: Interpreter or installed-runtime drift should outrank new recursive expansion because the checker is already proving a concrete mismatch.
  - State: `expected=fix-service-parity-drift; observed=fix-service-parity-drift; parity_drift=4; truth_drift=0; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=True`
- registry-contract-broken: `pass`
  - Expected: `repair-registry-contract`
  - Observed: `repair-registry-contract`
  - Rationale: If registry or coverage ownership is broken, fix the checker contract first so later recursive readbacks remain trustworthy.
  - State: `expected=repair-registry-contract; observed=repair-registry-contract; parity_drift=0; truth_drift=0; cleanup_active_elsewhere=False; registry_ok=False; coverage_ok=False; skill_loop_proven=True`
- architecture-stable-benchmark-next: `pass`
  - Expected: `add-recommendation-quality-benchmark`
  - Observed: `add-recommendation-quality-benchmark`
  - Rationale: Once drift is clean and the checker architecture is stable, the next useful recursive move is a bounded recommendation-quality benchmark.
  - State: `expected=add-recommendation-quality-benchmark; observed=add-recommendation-quality-benchmark; parity_drift=0; truth_drift=0; cleanup_active_elsewhere=False; registry_ok=True; coverage_ok=True; skill_loop_proven=True`

## Recommendation

- The recursive lane now has a bounded recommendation-quality baseline. Next useful work is to feed real checker snapshots into this benchmark family instead of adding more synthetic checker plumbing.

## Verification

- Trace directory: `sandboxes/recursive-improve-pilot-target-313/eval/recommendation-traces`
- Eval output directory: `sandboxes/recursive-improve-pilot-target-313/eval/recommendation-benchmark`
- Eval run id: `7596f83f91ec`
- Benchmark run id: `b3d095e7b2e4`
- Benchmark label: `recommendation-quality-liveaware-2026-05-24`
- `clean_success_rate = 100.0% (5/5)`
- Benchmark score: `14.3%`
