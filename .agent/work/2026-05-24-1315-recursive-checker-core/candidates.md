# Recursive Checker Core Candidates

## Scope and Constraints

Target scope is the non-operational recursive checker lane only:

- `scripts/service_parity_check.py`
- `scripts/task_flow_truth_drift_check.py`
- `scripts/recursive_registry_lint.py`
- registry files:
  - `scripts/service_parity_surfaces.json`
  - `scripts/task_flow_truth_surfaces.json`

Hard constraints:

- no mutation of live OPS, Portal, mailbox, or Task Flow state
- no change to AI Health command surfaces unless there is a strong reason
- keep registry-driven ownership

Soft guidance:

- the other terminal is already handling live truth-drift cleanup
- this lane should improve maintainability and coverage, not race operational fixes

## First-Principles Repo Model

The recursive checker lane now has two independent operational checkers and one non-operational lint tool.

- `service_parity_check.py` is the larger checker at `734` lines. It owns runtime parity, deployment-state checks, installed runtime scans, fix modes, reporting, and config validation.
- `task_flow_truth_drift_check.py` is `379` lines. It owns one read-only contradiction detector over board, Task Flow, and proof surfaces plus config validation.
- `recursive_registry_lint.py` is `91` lines. It imports both checkers just to reuse their config validators.

The current architectural improvement is real: both operational checkers are registry-driven. But the code still has a second layer of duplication:

- both checkers own JSON loading plus `require(...)` plus `validate_config(...)`
- the lint tool imports both modules to reuse those validators
- config-schema knowledge is now partly in registry JSON and partly in checker code

## Ranked Shortlist

### 1. Minimal surgical change: extract shared registry validation helpers

Problem hypothesis:

The current duplication is small but meaningful. A tiny shared helper module for registry loading/validation would simplify both checkers and the lint tool without reopening the operational checker boundaries.

Supporting evidence:

- both checkers now have local `require(...)` helpers
- both checkers have top-level config validation functions
- the lint tool imports full checker modules only to call those validators

Weakening evidence:

- the duplication is still bounded
- an overly generic abstraction could be worse than the current explicit code

Cheapest useful probe:

- extract only the schema-loading/validation seam into one helper module and leave checker-specific business logic alone

Expected payoff:

- fewer schema edits in multiple places
- simpler lint path
- less need to import heavy checker modules for config-only validation

Blast radius:

- low

### 2. Do nothing beyond current registries and lint

Problem hypothesis:

The current state may already be good enough. The main risk was hardcoded surface ownership, and that is now addressed.

Supporting evidence:

- both checkers are already registry-driven
- the new lint tool already validates both registries
- live parity checks are green

Weakening evidence:

- config-schema knowledge is still duplicated across tools
- importing full checker modules for lint-only validation is heavier than needed

Expected payoff:

- zero refactor risk

Blast radius:

- none

### 3. Deeper shared recursive checker framework

Problem hypothesis:

A shared framework could unify config loading, result formatting, reporting, fix handling, and output conventions across the recursive lane.

Supporting evidence:

- both checkers produce reports and JSON
- both now have registry-driven ownership
- a shared framework could make future recursive checks faster to add

Weakening evidence:

- `service_parity_check.py` and `task_flow_truth_drift_check.py` solve materially different problems
- a framework move now risks shallow abstraction and premature generalization
- the operational code is still young; constraints are not fully stable

Cheapest useful probe:

- do not build the framework yet; first extract only the registry validation seam and see whether deeper commonality remains

Expected payoff:

- medium if it works, but uncertain

Blast radius:

- medium to high

### 4. Expand coverage manifests only, no code refactor

Problem hypothesis:

The next gain may come from explicit coverage declarations rather than shared code.

Supporting evidence:

- the system now needs stronger statements about what each checker does and does not watch
- coverage gaps can create false confidence even when checks are green

Weakening evidence:

- coverage manifests do not reduce the current code duplication
- they are additive documentation unless tied to validation rules

Expected payoff:

- medium

Blast radius:

- low

## Provisional Leader

The provisional leader is the minimal surgical change: extract shared registry validation helpers.

Why:

- it addresses the real remaining duplication
- it keeps the deeper checker boundaries intact
- it improves the lint path immediately
- it avoids building a speculative framework too early

## Why the Others Stay Alive

- `do nothing` remains a serious option because the current state is already materially better than the original hardcoded version
- `coverage manifests` may still be the next step after the validation seam is cleaned up
- the shared framework option stays alive only as a later possibility, not the next move
