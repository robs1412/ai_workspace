# Task Flow Truth Drift Check

- Recorded: 2026-06-07 14:42:07
- Config: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- Board ok: `True`
- Managed sessions: `199`
- Task Flow rows scanned: `500`
- Proof rows scanned: `35`
- Drift count: `0`

## Summary

- scheduler_violations: `0`
- scheduler_route_candidates: `0`
- proof_closeout_issues: `10`

## Proof Issue Classes

- active_worker_missing_domain_task: `2`
- blocked_needs_owner_question_proof: `5`

## Proof Issue Samples

- blocked_needs_owner_question_proof: `blocked` taskflow-fe3920e9e9ebb56b
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-fe3920e9e9ebb56b`
- blocked_needs_owner_question_proof: `blocked` taskflow-b4e191619e3f6349
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-b4e191619e3f6349`
- blocked_needs_owner_question_proof: `blocked` taskflow-9b2842a7eb885dc2
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-9b2842a7eb885dc2`
- blocked_needs_owner_question_proof: `blocked` Follow up
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzybRf2Q7-v9Rk8DhHOVGUQXJ3ZzaQphge-pOiA07o9tg-mail-gmail-com`
  - owner_lane: `sonat`
- active_worker_missing_domain_task: `attention` taskflow-59994f5a1b3030bd
  - detail: working row has visible session cb6685a4 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-59994f5a1b3030bd`
  - session_id: `cb6685a4`
  - owner_lane: `naomi-stern`
- active_worker_missing_domain_task: `attention` taskflow-82e27c83e26920f1
  - detail: working row has visible session abbb9e24 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-82e27c83e26920f1`
  - session_id: `abbb9e24`
  - owner_lane: `outreach-coordinator`
- blocked_needs_owner_question_proof: `blocked` Fwd: KOVAL and Thresh and Winnow In Market Recap for 6/4
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzwz-wqeo3XaxhGUzVzHTLq6RC1Vt-DczdhwnX-qb4F6bg-mail-gmail-com`
  - owner_lane: `sonat`

## Drift

- None

## Recommendation

- Truth drift is clean, but proof issue classes remain. Classify or repair one named class before returning to monitor mode.
