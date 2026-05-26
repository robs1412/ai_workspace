# Recursive Run truth-drift-harness-001

- updated_at: `2026-05-26 17:20:11 CDT`
- surface: `scripts/task_flow_truth_drift_check.py`
- metric: `drift_count`
- evaluator: `/usr/local/bin/python3.13 scripts/task_flow_truth_drift_check.py --fail-on-drift`

## Attempts

| attempt | status | metric | proof | reason |
| --- | --- | --- | --- | --- |
| baseline-20260526 | needs-approval | 5 | proofs/baseline-20260526.json | Baseline proof found drift_count=5 under --fail-on-drift; keep proof for follow-up instead of mutating during evening cleanup. |
