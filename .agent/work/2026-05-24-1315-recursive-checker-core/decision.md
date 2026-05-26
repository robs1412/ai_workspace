# Recursive Checker Core Decision

## Chosen Refactor

Extract a small shared registry validation core for the recursive checker lane, and stop there.

## Why It Wins Now

This option captures the real remaining duplication without forcing a shared checker framework too early.

The current repo evidence shows:

- registry ownership is already the main success
- the remaining duplication is at the config/schema validation seam
- `recursive_registry_lint.py` currently imports full checker modules only to call validation functions

So the winning move is to deepen the config-validation module boundary, not to generalize the entire checker architecture.

## Evidence That Changed Confidence

- `service_parity_check.py` now contains both runtime logic and config-schema logic at `734` lines
- `task_flow_truth_drift_check.py` also owns config-schema logic at `379` lines
- `recursive_registry_lint.py` imports those modules directly just to reuse validators

That means the next shared seam is not hypothetical. It already exists.

## Why the Runner-Ups Lost

### Do nothing

Reason it lost:

The system is in much better shape already, but the duplicated config-schema logic is real and cheap to remove safely.

### Deeper shared checker framework

Reason it lost:

The two operational checkers are not similar enough yet to justify a framework. That would likely create a shallow abstraction that hides little.

### Coverage manifests only

Reason it lost:

Useful later, but it does not address the current code duplication or the heavy lint import path.

## Success Criteria

- one shared helper module owns recursive registry loading and structural validation
- both operational checkers call that helper instead of owning duplicate schema helpers
- `recursive_registry_lint.py` uses the shared helper directly rather than importing whole checker modules just to validate configs
- checker command surfaces remain stable

## First Safe Slice

Add one helper module under `scripts/` that exposes:

- JSON load helper
- common assertion helper
- validator entry points for:
  - Task Flow truth registry
  - service parity registry

Then migrate `recursive_registry_lint.py` first, followed by the operational checkers.

## Abandonment Conditions

Abandon this refactor if:

- the helper starts forcing unrelated checker behavior into a fake common base
- moving validation out would make the checkers harder to read or reason about
- the implementation starts spreading into reporting or result-format layers without new evidence

## Hard Constraints for Planning

- keep the change repo-local and non-operational
- do not change AI Health invocation shape
- do not add automatic mutation behavior
- prefer a tiny shared core over a generic framework
