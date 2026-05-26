# Extract Recursive Registry Validation Core

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document follows `.agent/PLANS.md`. In this repo, `.agent/` is planning artifact state only; operational truth remains in Task Flow, project_hub, and `HANDOFF.md`.

## Purpose / Big Picture

After this change, the recursive checker lane will have one small shared core for registry loading and structural validation instead of duplicating that logic inside both operational checkers and re-importing those whole checker modules from the lint tool. A developer changing checker registry shape will have one clearer validation seam to update, and the lint tool will validate those registries directly without loading the larger operational checkers just to reuse their helpers.

The user-visible result is modest but important: `./scripts/recursive_registry_lint.py --json` still succeeds, `./scripts/service_parity_check.py --mode all --fail-on-drift` still behaves the same, and the recursive checker internals become easier to change safely.

## Progress

- [x] (2026-05-24 18:15Z) Created the local work item, candidate brief, and locked decision for the recursive checker shared-core refactor target.
- [x] (2026-05-24 18:22Z) Audited the current checker lane and confirmed the duplicated seam is registry loading plus schema validation, not report formatting or drift logic.
- [x] (2026-05-24 18:29Z) Extracted `scripts/recursive_registry_core.py` with shared JSON load and explicit validator entry points for both registry files.
- [x] (2026-05-24 18:31Z) Updated `recursive_registry_lint.py` to use the shared core directly instead of importing full operational checkers for validation-only work.
- [x] (2026-05-24 18:32Z) Updated `scripts/service_parity_check.py` and `scripts/task_flow_truth_drift_check.py` to call the shared validation helpers while preserving their command surfaces.
- [x] (2026-05-24 18:34Z) Re-ran compile and checker verification and recorded the outcome.

## Surprises & Discoveries

- Observation: the current duplication is more about schema ownership than about report generation.
  Evidence: `service_parity_check.py` and `task_flow_truth_drift_check.py` each define local `require(...)` and `validate_config(...)`, while `recursive_registry_lint.py` imports whole checker modules only to call those validators.

- Observation: the current state is already good enough that a deeper shared framework would likely be premature.
  Evidence: the two operational checkers still differ significantly in flow and responsibility, while the lint tool only needs config validation.

- Observation: once the other terminal's live cleanup continued, the truth-drift readback fell quickly during this refactor.
  Evidence: `./scripts/task_flow_truth_drift_check.py --fail-on-drift || true` now returns `drift_count=3`, down from the earlier `16` baseline.

## Decision Log

- Decision: target only the shared registry validation seam, not a generic checker framework.
  Rationale: repo evidence shows the duplicated seam is real and safe to extract, while a framework move would likely create shallow abstraction.
  Date/Author: 2026-05-24 / Codex

## Outcomes & Retrospective

This plan succeeded as a bounded smoke and implementation pass for the new local skill chain.

What landed:

- `scripts/recursive_registry_core.py`
- `recursive_registry_lint.py` now validates both registries through the shared core
- both operational checkers now reuse that same validation seam

What did not change:

- AI Health invocation shape
- service parity output shape
- truth-drift checker command surface
- any live operational mutation behavior

Main lesson:

The local skill chain is good enough to produce a useful candidate -> decision -> plan -> implementation loop in this repo, as long as the target stays bounded and non-operational.

## Context and Orientation

There are three files in the current recursive checker lane:

- `scripts/service_parity_check.py`: the larger operational checker for runtime parity, deployment-state checks, installed runtime scans, optional fix modes, and reporting.
- `scripts/task_flow_truth_drift_check.py`: the read-only operational checker for contradictions across Workspaceboard, Task Flow, and proof surfaces.
- `scripts/recursive_registry_lint.py`: the non-operational lint script that validates the two registry files without touching live operational surfaces.

The current registry files are:

- `scripts/service_parity_surfaces.json`
- `scripts/task_flow_truth_surfaces.json`

Today, each operational checker owns its own JSON loader, assertion helper, and config validator. The lint tool then imports those whole checker modules only to call the validators. That means registry-schema knowledge is still spread across multiple files even after the surface ownership moved into JSON.

The change here is not meant to merge the operational checkers. It is meant to give them one smaller shared dependency for registry validation only.

## Plan of Work

Create a new helper module under `scripts/`, for example `scripts/recursive_registry_core.py`. This module should own the common low-level pieces:

- reading a JSON file from disk
- a simple `require(...)` helper that raises clear `ValueError` messages
- one validator function for the Task Flow truth registry
- one validator function for the service parity registry

Keep those validators explicit. Do not try to invent a schema DSL, shared generic validator table, or inheritance hierarchy. The point is to concentrate the duplicated seam, not to generalize all future checker behavior.

After the helper exists, update `scripts/recursive_registry_lint.py` first. That file should import the new helper directly and validate both JSON registries without loading the full operational checkers. This is the safest first migration because it is non-operational and already only cares about registry shape.

Then update `scripts/task_flow_truth_drift_check.py` and `scripts/service_parity_check.py` so they call the shared loader and validator helpers instead of keeping their own copies. Preserve their existing command-line behavior, report paths, and validation semantics. The operational logic that builds drift results or parity results should stay in those files.

Do not change AI Health integration, report schema, or fix behavior in this refactor. The intended simplification boundary is config validation only.

## Concrete Steps

Working directory: `/Users/werkstatt/ai_workspace`

1. Read the three current files again:

    sed -n '1,220p' scripts/service_parity_check.py
    sed -n '1,180p' scripts/task_flow_truth_drift_check.py
    sed -n '1,180p' scripts/recursive_registry_lint.py

2. Create `scripts/recursive_registry_core.py` with:

    - a JSON load helper
    - a common `require(...)`
    - `validate_task_flow_truth_config(...)`
    - `validate_service_parity_config(...)`

3. Patch `scripts/recursive_registry_lint.py` to import the new helper instead of importing the operational checkers for validation-only use.

4. Patch the two operational checkers to call the shared validators.

5. Verify:

    /usr/local/bin/python3.13 -m py_compile scripts/recursive_registry_core.py scripts/recursive_registry_lint.py scripts/service_parity_check.py scripts/task_flow_truth_drift_check.py
    ./scripts/recursive_registry_lint.py --json
    ./scripts/service_parity_check.py --mode all --fail-on-drift
    ./scripts/task_flow_truth_drift_check.py --fail-on-drift || true

Expected result:

- compile succeeds
- registry lint returns `ok: true`
- service parity still reports `drift=0`
- truth drift count may move as the other terminal continues cleanup, but the checker still runs successfully

## Validation and Acceptance

Accept this refactor when all of the following are true:

- `recursive_registry_lint.py` validates both registries without loading full operational checker modules
- both operational checkers still run successfully
- their output surfaces and invocation style remain unchanged
- the new shared helper is small and explicit enough that a new contributor can see exactly where registry-shape rules live

The acceptance target is maintainability, not a visible user-facing feature.

## Idempotence and Recovery

This refactor should be additive and safe to retry. If a migration step becomes confusing, restore the previous validator code from git diff context and reattempt one file at a time, starting with the lint script again. Do not mix this refactor with live operational fixes or AI Health command-surface edits.

## Artifacts and Notes

Important baseline evidence before implementation:

    wc -l scripts/service_parity_check.py scripts/task_flow_truth_drift_check.py scripts/recursive_registry_lint.py
         734 scripts/service_parity_check.py
         379 scripts/task_flow_truth_drift_check.py
          91 scripts/recursive_registry_lint.py

    ./scripts/recursive_registry_lint.py --json
      returns ok for both registry files

    ./scripts/task_flow_truth_drift_check.py --fail-on-drift || true
      returns drift_count=3 after the other terminal's cleanup continued

    ./scripts/service_parity_check.py --mode all --fail-on-drift
      returns surfaces_checked=91, drift=0, fix_failed=0

## Interfaces and Dependencies

The new helper module should expose explicit functions, not a framework. Stable examples:

    def load_json(path: Path) -> dict[str, Any]:
        ...

    def require(condition: bool, message: str) -> None:
        ...

    def validate_task_flow_truth_config(config: dict[str, Any]) -> dict[str, Any]:
        ...

    def validate_service_parity_config(config: dict[str, Any]) -> dict[str, Any]:
        ...

Each validator should hide the shape-checking detail from callers. Callers should only need to load the JSON and pass it to the correct validator.
