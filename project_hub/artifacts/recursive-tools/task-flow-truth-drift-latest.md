# Task Flow Truth Drift Check

- Recorded: 2026-06-08 18:07:13 
- Config: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- Board ok: `True`
- Managed sessions: `100`
- Task Flow rows scanned: `500`
- Proof rows scanned: `44`
- Drift count: `0`

## Summary

- scheduler_violations: `0`
- scheduler_route_candidates: `0`
- proof_closeout_issues: `6`

## Proof Issue Classes

- active_worker_missing_domain_task: `1`
- blocked_needs_owner_question_proof: `3`

## Proof Issue Samples

- blocked_needs_owner_question_proof: `blocked` taskflow-760a7508ffeabfe5
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-760a7508ffeabfe5`
- blocked_needs_owner_question_proof: `blocked` taskflow-1db47dff91264646
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-1db47dff91264646`
- blocked_needs_owner_question_proof: `blocked` taskflow-3981bd77dabf07ce
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-3981bd77dabf07ce`
- active_worker_missing_domain_task: `attention` taskflow-09043689ee2660fe
  - detail: working row has visible session 5bae2106 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-09043689ee2660fe`
  - session_id: `5bae2106`
  - owner_lane: `outreach-coordinator`

## Drift

- None

## Recommendation

- Truth drift is clean, but proof issue classes remain. Classify or repair one named class before returning to monitor mode.
