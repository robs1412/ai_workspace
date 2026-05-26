# Recursive Proposal Decision Recorder

Date: 2026-05-24
Papers: https://papers.koval.lan/99336886-09d1-4a6d-b09d-f43093344bcd

## Decision

The recursive improvement proposal queue now has a durable decision/state recorder. Proposal generation, human approval, and repair execution are separate steps.

## Why This Matters

The first approval-required proposal was overtaken by later clean checker state. Without a decision recorder, it would have stayed as false approval residue even though there was nothing left to execute.

## Current Implementation

- Proposal generator: `scripts/recursive_proposal_queue.py`
- Decision recorder: `scripts/recursive_proposal_decisions.py`
- Queue log: `project_hub/artifacts/recursive-tools/recursive-proposal-queue.jsonl`
- Decision log: `project_hub/artifacts/recursive-tools/recursive-proposal-decisions.jsonl`
- Proposal packets: `project_hub/artifacts/recursive-tools/proposals/`

The recorder updates proposal JSON with `decision_state`, appends an immutable JSONL decision event, and does not read mailbox content or execute repairs.

## Operator Commands

```bash
./scripts/recursive_proposal_decisions.py status --json
./scripts/recursive_proposal_decisions.py record-decision --proposal-id latest-pending --decision yes --source-message-id '<reply-message-id>' --notes '<non-secret note>'
./scripts/recursive_proposal_decisions.py record-decision --proposal-id latest-pending --decision no --source-message-id '<reply-message-id>' --notes '<non-secret note>'
./scripts/recursive_proposal_decisions.py record-decision --proposal-id latest-pending --decision unclear --source-message-id '<reply-message-id>' --notes '<non-secret note>'
./scripts/recursive_proposal_decisions.py reconcile-clean-monitor
```

## Current Readback

- `recursive-proposal-20260524-134350-repair-truth-drift` is `superseded_by_clean_monitor`.
- Superseding proposal: `recursive-proposal-20260524-134813-monitor-recursive-lane`.
- Current decision status reports `pending_approval_count=0`.

## Next Slice

The next autonomy step should be a narrow approved-execution runner for whitelisted `approved` proposal states. It should require a post-run checker proof and should record `executed`, `blocked`, or `verified` without silently broadening the repair class.
