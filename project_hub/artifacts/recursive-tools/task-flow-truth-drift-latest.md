# Task Flow Truth Drift Check

- Recorded: 2026-06-07 12:36:41
- Config: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- Board ok: `True`
- Managed sessions: `194`
- Task Flow rows scanned: `500`
- Proof rows scanned: `39`
- Drift count: `0`

## Summary

- scheduler_violations: `0`
- scheduler_route_candidates: `0`
- proof_closeout_issues: `11`

## Proof Issue Classes

- active_worker_missing_domain_task: `3`
- blocked_missing_blocker_email: `4`
- blocked_needs_owner_question_proof: `4`

## Proof Issue Samples

- blocked_needs_owner_question_proof: `blocked` Follow up
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzybRf2Q7-v9Rk8DhHOVGUQXJ3ZzaQphge-pOiA07o9tg-mail-gmail-com`
  - owner_lane: `sonat`
- active_worker_missing_domain_task: `attention` taskflow-59994f5a1b3030bd
  - detail: working row has visible session cb6685a4 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-59994f5a1b3030bd`
  - session_id: `cb6685a4`
  - owner_lane: `naomi-stern`
- active_worker_missing_domain_task: `attention` Re: Contacts to add
  - detail: working row has visible session f8b455e5 but lacks ops_portal_or_domain_task
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzxzaiPHiDfb5nyrEFdRdtZAmm0iWC5rC0z4g0YUeSZUrg-mail-gmail-com`
  - session_id: `f8b455e5`
  - owner_lane: `sonat`
- blocked_needs_owner_question_proof: `blocked` Tasks
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzyBP2fzO-on-WRtBg5c-UrRObKV-xRTMJ99hoJ-BVCg-mail-gmail-com`
  - owner_lane: `sonat`
- blocked_missing_blocker_email: `blocked` taskflow-bdec436ccbf88991
  - detail: blocked row requires blocker email or equivalent source-backed blocker proof
  - dedupe_key: `taskflow-bdec436ccbf88991`
  - session_id: `5de66c59`
  - owner_lane: `outreach-coordinator`
- active_worker_missing_domain_task: `attention` taskflow-82e27c83e26920f1
  - detail: working row has visible session abbb9e24 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-82e27c83e26920f1`
  - session_id: `abbb9e24`
  - owner_lane: `outreach-coordinator`
- blocked_needs_owner_question_proof: `blocked` Fwd: KOVAL and Thresh and Winnow In Market Recap for 6/4
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzwz-wqeo3XaxhGUzVzHTLq6RC1Vt-DczdhwnX-qb4F6bg-mail-gmail-com`
  - owner_lane: `sonat`
- blocked_needs_owner_question_proof: `blocked` Mariano's Cancelation Process
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzzULHVdGbQa2wjAX-R4psjUwJp97eM7a2YQMA9tvhBswg-mail-gmail-com`
  - owner_lane: `sonat`
- blocked_missing_blocker_email: `blocked` portal work
  - detail: blocked row requires blocker email or equivalent source-backed blocker proof
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzwKJP87X89-LKAGGMXVQGtadoJKZrgCXSSyjbxKDDwCjw-mail-gmail-com`
  - session_id: `75c0fa6e`
  - owner_lane: `sonat`
- blocked_missing_blocker_email: `blocked` Re: Chat access
  - detail: blocked row requires blocker email or equivalent source-backed blocker proof
  - dedupe_key: `taskflow-owner-reply-db8df6401df47f3d`
  - session_id: `fd3b95b2`
  - owner_lane: `email-coordinator`
- blocked_missing_blocker_email: `blocked` taskflow-vanessa-open-cot-shifts-48h-2026-06-07-0800
  - detail: blocked row requires blocker email or equivalent source-backed blocker proof
  - dedupe_key: `taskflow-vanessa-open-cot-shifts-48h-2026-06-07-0800`
  - owner_lane: `outreach-coordinator`

## Drift

- None

## Recommendation

- Truth drift is clean, but proof issue classes remain. Classify or repair one named class before returning to monitor mode.
