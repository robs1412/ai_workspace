# Task Flow Truth Drift Check

- Recorded: 2026-06-08 22:36:26 CDT
- Config: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- Board ok: `True`
- Managed sessions: `108`
- Task Flow rows scanned: `500`
- Proof rows scanned: `43`
- Drift count: `0`

## Summary

- scheduler_violations: `0`
- scheduler_route_candidates: `0`
- proof_closeout_issues: `7`

## Proof Issue Classes

- blocked_needs_owner_question_proof: `5`

## Proof Issue Samples

- blocked_needs_owner_question_proof: `blocked` taskflow-5cfd58716334576b
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-5cfd58716334576b`
- blocked_needs_owner_question_proof: `blocked` taskflow-bf15206feb1385cf
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-bf15206feb1385cf`
- blocked_needs_owner_question_proof: `blocked` taskflow-a151053058c9c6c0
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-a151053058c9c6c0`
- blocked_needs_owner_question_proof: `blocked` taskflow-760a7508ffeabfe5
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-760a7508ffeabfe5`
- blocked_needs_owner_question_proof: `blocked` taskflow-1db47dff91264646
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-1db47dff91264646`

## Drift

- None

## Recommendation

- Truth drift is clean, but proof issue classes remain. Classify or repair one named class before returning to monitor mode.
