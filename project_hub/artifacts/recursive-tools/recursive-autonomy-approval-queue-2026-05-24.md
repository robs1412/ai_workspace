# Recursive Autonomy Approval Queue

- Recorded: 2026-05-24 13:40 CDT
- Owner model: Codex generates proposals; Frank owns the human approval loop.
- Scope: recursive-improvement autonomy for local checker, benchmark, and repair lanes.

## Decision

The next autonomy layer is an approval-gated proposal queue, not direct autonomous mutation.

Frank is the right owner for the human approval loop because this is a Robert-facing decision lane:

- Codex reads checker output, historical benchmark results, and live snapshot state.
- Codex writes a proposal packet with one recommended fix class, expected effect, risk class, required proof, and rollback note.
- Frank emails Robert a plain yes/no decision request.
- Robert replies yes/no.
- Frank records the decision and routes the approved execution back to Codex or the correct visible worker.
- Codex executes only approved low-risk fix classes, then reruns the checker and benchmark.
- Frank sends the completion or blocker report when execution proof exists.

## Approval Email Shape

Each approval email should be one clear decision, not a batch of vague options.

Required fields:

- Recommendation: the exact proposed action.
- Why now: the live checker or benchmark state that triggered it.
- Risk class: low, medium, or high.
- What changes if approved: the exact surface class that may be modified.
- What will not change: explicit non-scope boundaries.
- Proof after execution: the checker, benchmark, sent log, OPS/Portal readback, or Papers artifact that must exist after the fix.
- Decision line: `Reply YES to approve this fix, or NO to leave it as a recorded recommendation.`

## Fix Class Policy

Allowed for approval-gated execution:

- registry metadata fixes for recursive checker configs
- non-operational checker/report note updates
- source/runtime parity fixes that do not restart services
- stale recommendation-corpus updates
- proposal queue bookkeeping

Still blocked from automatic execution:

- live OPS/Portal mutation
- mailbox archive/send actions
- service restarts
- LaunchDaemon/LaunchAgent edits
- broad Task Flow closeout mutation
- credential, token, OAuth, Keychain, or private-mailbox work

Those require a separate explicit approval and should not be bundled into the recursive improvement lane.

## Current State

Already wired:

- read-only recursive checkers
- registry-owned checker config
- coverage manifest
- synthetic recommendation benchmark
- live checker snapshot benchmark
- historical recommendation-quality corpus

Current benchmark readback:

- synthetic recommendation benchmark: `5/5`
- live recommendation snapshot: `1/1`
- historical recommendation corpus: `6/6`

Current live recommendation:

- `repair-truth-drift`
- driver: one remaining `active_missing_board_session` contradiction

That repair can be picked up by another terminal. This note defines the next autonomy layer after that: approval-gated proposal generation.

## External Comparison Ask

Claude should be asked whether his side already has an equivalent loop:

- checker or drift detector
- recommendation-quality benchmark
- historical replay corpus
- approval-gated proposal queue
- post-fix verification loop
- ratchet/keep-or-revert logic

GitHub references for the comparison:

- `https://github.com/grp06/useful-codex-skills`
- `https://github.com/kayba-ai/recursive-improve`
- `https://github.com/grp06/recursive-codex`

Related Papers records:

- Recursive tools stack assessment: `https://papers.koval.lan/601a7e00-ad29-4bd8-bd47-aac20f2e998a`
- Recursive tools stack update: `https://papers.koval.lan/3af10e66-59b1-4bce-8543-2ad0366022cd`
- Recursive checker shared-core implementation: `https://papers.koval.lan/71fed84c-69b5-4ecd-ad33-8a7b33afe547`
