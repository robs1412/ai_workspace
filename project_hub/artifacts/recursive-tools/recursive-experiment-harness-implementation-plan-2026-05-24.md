# Recursive Experiment Harness Implementation Plan

Timestamp: 2026-05-24 19:02 CDT.

Papers: `https://papers.koval.lan/1cd480c5-6d62-4589-8592-97d77343e781`
Final Papers copy with OPS task ID: `https://papers.koval.lan/d7c535a6-3b9e-41d3-8474-961c8c4da2c0`
Confirmed Papers copy: `https://papers.koval.lan/7f76ab59-6627-44d4-8248-882076566d2d`
Tuesday start context: `https://papers.koval.lan/c6d75317-97bd-4e12-aa24-ed48edf4f99a`
OPS task: `370208`

## Decision

Implement the `karpathy/autoresearch` idea as a bounded recursive experiment harness, not as open-ended autonomous code mutation.

The harness should let Codex/worker agents run controlled improvement attempts only inside an owned worktree, against one approved mutable surface, judged by one immutable proof command. The output is a compact attempt ledger, not a transcript.

## Dependency

Planner `/proof` access is the gating dependency for any Claude/Planner-backed pilot.

- Claude Planner task `#1725`: `/proof` endpoint implemented.
- Claude reachability task `#1726`: enable Codex workstation access to `planner.koval.lan` or provide an approved read-only route for the same `/proof` payload.
- Current Codex verifier: `scripts/claude_planner_proof_check.py`.
- Current blocker: `planner.koval.lan` times out from this workstation because it is internal-LAN only.

Until `#1726` is resolved, use only local proof surfaces for dry pilots.

## Harness Shape

Each recursive run gets a dedicated directory:

```text
project_hub/recursive-runs/<run-id>/
  program.md        # manager-owned instructions and boundaries
  evaluator.json    # immutable proof command and metric parser
  attempts.tsv      # attempt_id, hypothesis, surface, metric, status, proof
  proofs/           # raw verifier outputs
  worktree/         # isolated branch/worktree for agent mutations
```

The harness owns autonomy; the agent does not.

## Core Rules

1. One mutable implementation surface per run.
2. One immutable evaluator/proof command per run.
3. All mutations happen in an owned branch/worktree.
4. The main workspace must not be reset or cleaned by the harness.
5. Each attempt records `keep`, `discard`, `crash`, or `needs-approval`.
6. Losing or crashing attempts stay in the ledger with a short reason.
7. Equal or tiny-positive metric changes only win when they reduce complexity or improve proof clarity.
8. Any verifier change is a separate proposal, never part of the same run.
9. Any live-service, daemon, network, credential, OPS/Portal, mailbox, or production-impacting change remains approval-gated.

## Script

Add `scripts/recursive_experiment_harness.py` with these initial commands:

```bash
init \
  --run-id <run-id> \
  --surface <relative/path/to/mutable/file> \
  --evaluator '<proof command>' \
  --metric <metric-name>

record-attempt \
  --run-id <run-id> \
  --hypothesis '<what this attempt is testing>' \
  --surface <relative/path/to/mutable/file>

verify \
  --run-id <run-id> \
  --attempt-id <attempt-id>

decide \
  --run-id <run-id> \
  --attempt-id <attempt-id> \
  --status keep|discard|crash|needs-approval \
  --reason '<short reason>'
```

The script should:

- create the run directory and templates;
- create or verify the owned worktree;
- refuse absolute mutable paths outside `/Users/werkstatt`;
- refuse multiple mutable surfaces in one run;
- store evaluator config once and refuse later mutation unless a new run is created;
- run evaluator commands with timeouts;
- save JSON/Markdown/stdout/stderr proof files under `proofs/`;
- append `attempts.tsv`;
- emit a compact final run report.

## First Dry Pilot

Use a local proof surface before Planner reachability is fixed.

Recommended first dry pilot:

- Run ID: `truth-drift-harness-001`
- Surface: `scripts/task_flow_truth_drift_check.py`
- Evaluator: `/usr/local/bin/python3.13 scripts/task_flow_truth_drift_check.py --fail-on-drift`
- Metric: `drift_count`
- Goal: prove the harness can initialize, record a baseline, run proof, and write a ledger without code mutation.

This first pilot must be baseline-only: no mutation, no daemon/runtime changes, no OPS/Portal mutation, no mailbox mutation.

## Planner Pilot After Claude Task #1726

Once Claude confirms access for task `#1726`, run a Planner-backed pilot:

- Run ID: `planner-proof-harness-001`
- Surface: `scripts/claude_planner_proof_check.py`
- Evaluator: `/usr/local/bin/python3.13 scripts/claude_planner_proof_check.py --timeout-seconds 8 --json tmp/ai-health-manager/claude-planner-proof-latest.json --report tmp/ai-health-manager/claude-planner-proof-latest.md --fail-on-not-ready`
- Metric: `proof_status`
- Goal: verify that the harness can treat Planner `/proof` as an immutable proof surface and record pass/fail attempts.

Initial target is proof-read reliability and reporting clarity, not changing the bridge contract.

## Acceptance Criteria

The first implementation is complete when:

- `scripts/recursive_experiment_harness.py --help` works.
- `init` creates the expected run directory with templates.
- baseline `verify` saves proof outputs.
- `attempts.tsv` records a baseline attempt.
- the harness refuses a second mutable surface for the same run.
- the harness refuses evaluator mutation inside the same run.
- the harness does not alter main-workspace git state.
- a short run report is written under the run directory.
- local handoff and Papers cite the run path and proof.

## Tuesday Follow-Up Task

Create a silent Codex-owned OPS task due Tuesday, 2026-05-26:

Title: `Implement recursive experiment harness after Planner proof access`

Description:

```text
Implement the recursive experiment harness from Papers once Claude task #1726 has enabled Codex access to Planner /proof or provided an approved reachable read-only route. Start with a local truth-drift baseline dry pilot if Planner access is still not available; otherwise run the Planner proof harness pilot. Do not mutate daemons, credentials, production services, OPS/Portal state, mailbox state, or shared git history without separate approval.

Papers plan: https://papers.koval.lan/1cd480c5-6d62-4589-8592-97d77343e781
Related Claude tasks: #1725 (/proof endpoint), #1726 (Codex reachability)
```

Owner/assignee: Codex user `1332`.
Creator: Robert/admin user `1`.
Notifications: suppressed.
Created OPS task: `370208`.

## Non-Goals

- Do not import `karpathy/autoresearch` code.
- Do not run indefinite autonomous loops.
- Do not use `git reset` in the shared main workspace.
- Do not change the `/proof` contract as part of the first harness run.
- Do not create a general scheduler/daemon from this slice.

## Source References

- `https://github.com/karpathy/autoresearch`
- Local source review: `project_hub/artifacts/recursive-tools/autoresearch-source-review-2026-05-24.md`
- Expanded Papers source review: `https://papers.koval.lan/87076e7c-6c90-4b84-aa0b-ffc1392ff14e`
- Planner proof note: `https://papers.koval.lan/0b415627-732b-4781-a608-89252fb29d21`
