# Task Flow Truth Drift Handoff

- Recorded: 2026-05-24 12:53 CDT
- Scope: recursive checker follow-through for Task Flow / Workspaceboard / proof-surface contradictions

## Current State

The unified read-only truth-drift lane is live and already wired into AI Health.

Primary surfaces:

- checker: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_drift_check.py`
- registry: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- AI Health integration: `/Users/werkstatt/ai_workspace/scripts/ai_health_check.py`

AI Health now records:

- `task_flow_truth_drift`
- `task_flow_truth_drift_count`
- `task_flow_truth_drift_checked`

Readback surfaces:

- `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/latest.json`
- `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/latest.md`
- `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/task-flow-truth-drift-latest.json`
- `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/task-flow-truth-drift-latest.md`

## Verified Readback

- `./scripts/task_flow_truth_drift_check.py --fail-on-drift`
  - `drift_count=17`
- `./scripts/ai_health_check.py --dry-run --max-run-seconds 90`
  - `task_flow_truth_drift=drift`
  - `task_flow_truth_drift_count=17`
  - `task_flow_truth_drift_checked=500`
  - `service_parity=passed`
  - `service_parity_drift=0`

Current drift classes:

- `closed_without_closeout_proof = 14`
- `scheduler_violations_present = 1`
- `scheduler_route_candidates_present = 1`
- `proof_report_closeout_issues = 1`

## Important Coordination Note

Do not assume the current `17` truth drifts are static residue that this lane should immediately mutate.

There is already active inbox / queue cleanout work happening elsewhere, and some of these contradiction classes may already be in the process of being repaired by that live execution lane.

That means:

- re-read the latest truth-drift JSON before changing anything
- prefer proving that a drift item is still real right now
- do not race a live inbox cleanout or queue drain by bulk-closing rows from the recursive lane

## Next Step

Do the next recursive hardening step, not broad queue mutation:

apply the same registry-driven pattern to `service_parity_check.py`.

Reason:

- `task_flow_truth_drift_check.py` now has a cleaner architecture-change response model because its owned surfaces live in one registry file
- `service_parity_check.py` still carries more hardcoded surface knowledge
- if code paths, installed-runtime paths, or deployment surfaces shift again, the parity lane should update through a registry/config seam rather than another round of direct code edits

## Recommended Follow-Through

1. Create a parity registry file describing:
   - source/runtime parity surfaces
   - installed runtime mirrors
   - deployment-state plists/wrappers
   - optional vs required surfaces
2. Refactor `scripts/service_parity_check.py` to load that registry instead of owning path knowledge inline.
3. Keep AI Health calling the same stable command surface.
4. Only after that, re-check whether the `17` truth drifts remain real and unclaimed by the inbox cleanout lane.

## Constraints

- keep this read-only by default
- do not add automatic closeout/fix behavior to AI Health for the truth-drift lane
- do not regress the existing service parity AI Health integration
- use the registry file as the first update point when architecture changes
