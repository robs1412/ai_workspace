# Recursive Program planner-proof-harness-001

- created_at: `2026-05-26 17:19:27 CDT`
- mutable_surface: `scripts/claude_planner_proof_check.py`
- immutable_evaluator: `/usr/local/bin/python3.13 scripts/claude_planner_proof_check.py --timeout-seconds 8 --json tmp/ai-health-manager/claude-planner-proof-latest.json --report tmp/ai-health-manager/claude-planner-proof-latest.md --fail-on-not-ready`
- metric: `proof_status`

## Boundary

One mutable surface, one immutable proof command, compact ledger only.
