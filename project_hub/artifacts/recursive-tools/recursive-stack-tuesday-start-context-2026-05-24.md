# Recursive Stack Tuesday Start Context

Timestamp: 2026-05-24 19:27 CDT.

Papers: `https://papers.koval.lan/c6d75317-97bd-4e12-aa24-ed48edf4f99a`

## Point

Tuesday's work should not start from scratch. Codex already has a first-generation recursive improvement stack. The Tuesday harness task should wrap and discipline today's scripts, then use the Claude/Planner `/proof` bridge as the cross-system proof source.

## What Exists Now

### Local Codex Self-Improvement Sensors

- `scripts/task_flow_truth_drift_check.py`
  - Detects Task Flow / scheduler truth drift.
  - Current role: local source-of-truth checker for stale route candidates, scheduler residue, and drift between durable task state and board/runtime surfaces.

- `scripts/service_parity_check.py`
  - Checks parity across service/runtime surfaces.
  - Current role: detects service layout, runtime, or contract drift that can become recursive improvement candidates.

- `scripts/claude_planner_proof_check.py`
  - Verifies Claude Planner `/proof` payloads.
  - Current role: external proof checker for Claude-side task claims.
  - Current status: canonical verifier passes against `https://planner.koval.lan/api/tasks/1725/proof` after the workstation host mapping fix.

### Local Proposal and Decision Machinery

- `scripts/recursive_proposal_queue.py`
  - Records improvement proposals.
  - Existing queue includes `repair-truth-drift` and `monitor-recursive-lane`.

- `scripts/recursive_proposal_decisions.py`
  - Records proposal decisions.
  - Existing decision example: `repair-truth-drift` was superseded by a clean monitor once truth-drift was no longer present.

- `scripts/recursive_proposal_executor.py`
  - Starts to execute approved proposal classes.
  - This is early-stage and should stay approval-gated.

- `scripts/recursive_registry_core.py`
  - Shared registry logic for recursive tooling.

- `scripts/recursive_registry_lint.py`
  - Validates registry/coverage consistency.

### Current Artifacts

- `project_hub/artifacts/recursive-tools/recursive-proposal-queue.jsonl`
- `project_hub/artifacts/recursive-tools/recursive-proposal-decisions.jsonl`
- `project_hub/artifacts/recursive-tools/task-flow-truth-drift-latest.json`
- `project_hub/artifacts/recursive-tools/service-parity-check-latest.json`
- `tmp/ai-health-manager/claude-planner-proof-latest.json`

## What Today's Setup Has Already Done

1. It gave Codex local sensors for self-improvement candidates.
2. It created a proposal queue instead of letting agents mutate code ad hoc.
3. It recorded decisions and superseded stale proposals when live proof changed.
4. It added a Planner `/proof` verifier so Claude-side claims can be verified directly by Codex.
5. It established a recurring rule: email text is not proof; `/proof`, AI Health, Task Flow, or live readback is proof.

## What Is Missing

The current stack is not yet an autoresearch-style experiment harness.

Missing pieces:

- one mutable surface per run;
- immutable evaluator per run;
- fixed budget;
- isolated worktree ownership;
- baseline attempt record;
- keep/discard/crash ledger;
- proof bundle per attempt;
- final compact wake-up report.

That is what OPS task `370208` should implement.

## How This Helps Codex and Claude Work Together

The goal is not just self-improvement inside Codex. The goal is a verifiable Codex-Claude loop where each side does the work it is best positioned to do.

### Claude's Role

Claude owns or coordinates Planner-side tasks, assessments, and specialist/sysadmin work.

Examples from today:

- Claude created Planner task `#1725` for the `/proof` endpoint.
- Claude reported `/proof` implementation completion.
- Claude created task `#1726` for Codex workstation reachability.
- Claude returned worklogs, task status, and closeout prompts.

### Codex's Role

Codex owns local verification, repo-local tooling, Workspaceboard/Task Flow alignment, and bounded implementation work.

Examples from today:

- Codex built `scripts/claude_planner_proof_check.py`.
- Codex validated Planner `/proof` only after the endpoint was reachable.
- Codex detected the DNS/hosts gap by comparing normal verifier failure with explicit-resolve success.
- Codex wrote the recursive harness plan and created OPS task `370208`.

### Bridge Contract

The bridge between Claude and Codex is Planner `/proof`.

Codex should not treat these as proof:

- Claude email text alone;
- broad `/api/tasks/{id}` context;
- `/chain` context;
- volatile fields such as `previous_status`, `session_id`, `context_summary`.

Codex can treat this as proof:

- `GET /api/tasks/{id}/proof`;
- `GET /api/proof?plan_guid={guid}`;
- stable fields such as `id`, `status`, `tags`, `plan_guid`, `worklog_guid`;
- proof comments, verifier comments, and delivery-notification comments.

### Practical Cooperation Loop

1. Claude proposes or completes a Planner task.
2. Codex asks for or identifies the Planner task ID.
3. Codex runs `scripts/claude_planner_proof_check.py`.
4. If `/proof` passes, Codex can close the local side and, when appropriate, send Claude `DONE`.
5. If `/proof` fails, Codex records one exact blocker and asks Claude for a specific fix or route.
6. If the issue is local Codex tooling, Codex routes it into the recursive proposal/harness stack.

## Tuesday Implementation Goal

OPS task `370208` should convert today's pieces into a controlled harness:

- reuse `task_flow_truth_drift_check.py`, `service_parity_check.py`, and `claude_planner_proof_check.py` as evaluator candidates;
- add `scripts/recursive_experiment_harness.py`;
- initialize a baseline run with no mutation;
- prove that the harness can record baseline, proof, status, and next step;
- only then allow a bounded worker to mutate one approved surface in an isolated worktree.

## First Suggested Tuesday Sequence

1. Verify Planner `/proof` still passes:

```bash
/usr/local/bin/python3.13 scripts/claude_planner_proof_check.py \
  --timeout-seconds 8 \
  --json tmp/ai-health-manager/claude-planner-proof-latest.json \
  --report tmp/ai-health-manager/claude-planner-proof-latest.md \
  --fail-on-not-ready
```

2. Run local sensors:

```bash
/usr/local/bin/python3.13 scripts/task_flow_truth_drift_check.py --fail-on-drift
/usr/local/bin/python3.13 scripts/service_parity_check.py
```

3. Build harness scaffolding:

```text
project_hub/recursive-runs/<run-id>/
  program.md
  evaluator.json
  attempts.tsv
  proofs/
  worktree/
```

4. Record a baseline run.

5. Only after baseline proof, pick one small mutable surface and one evaluator.

## Recommendation

Use the recursive harness first to improve the recursive tooling itself, not business workflows. Start with local truth-drift or proof-report clarity, because those have low blast radius and strong proof surfaces.

Once the harness proves reliable, use Claude Planner `/proof` as the coordination layer for cross-agent work: Claude creates and proves Planner tasks; Codex verifies them and turns local improvement needs into bounded, ledgered experiments.
