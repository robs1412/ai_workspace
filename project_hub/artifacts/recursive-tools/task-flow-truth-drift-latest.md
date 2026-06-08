# Task Flow Truth Drift Check

- Recorded: 2026-06-08 13:37:12 
- Config: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- Board ok: `True`
- Managed sessions: `76`
- Task Flow rows scanned: `500`
- Proof rows scanned: `88`
- Drift count: `5`

## Summary

- scheduler_violations: `0`
- scheduler_route_candidates: `0`
- proof_closeout_issues: `34`

## Proof Issue Classes

- active_worker_missing_domain_task: `3`
- attention_missing_finish_link: `4`
- blocked_needs_owner_question_proof: `16`

## Proof Issue Samples

- blocked_needs_owner_question_proof: `blocked` taskflow-3981bd77dabf07ce
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-3981bd77dabf07ce`
- active_worker_missing_domain_task: `attention` taskflow-09043689ee2660fe
  - detail: working row has visible session 5bae2106 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-09043689ee2660fe`
  - session_id: `5bae2106`
  - owner_lane: `outreach-coordinator`
- blocked_needs_owner_question_proof: `blocked` taskflow-1513f992055a281d
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-1513f992055a281d`
- blocked_needs_owner_question_proof: `blocked` taskflow-1f6e3188f9c1c18f
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-1f6e3188f9c1c18f`
- blocked_needs_owner_question_proof: `blocked` taskflow-8019cf2410556f69
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-8019cf2410556f69`
- attention_missing_finish_link: `attention` OPS open shifts 5345, 5270
  - detail: attention row missing ops_portal_or_domain_task
  - dedupe_key: `taskflow-bb8c20b3438d70a7`
  - owner_lane: `outreach-coordinator`
- blocked_needs_owner_question_proof: `blocked` taskflow-88906a605debd945
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-88906a605debd945`
- blocked_needs_owner_question_proof: `blocked` taskflow-22b8a02dc900f954
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-22b8a02dc900f954`
- blocked_needs_owner_question_proof: `blocked` taskflow-66bff1533318e8e6
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-66bff1533318e8e6`
- blocked_needs_owner_question_proof: `blocked` taskflow-a9b9481a1663f2af
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-a9b9481a1663f2af`
- blocked_needs_owner_question_proof: `blocked` taskflow-bdb48fb8db67a6a6
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-bdb48fb8db67a6a6`
- active_worker_missing_domain_task: `attention` taskflow-6ea601be2d0823f4
  - detail: working row has visible session 413c02b9 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-6ea601be2d0823f4`
  - session_id: `413c02b9`
  - owner_lane: `outreach-coordinator`
- active_worker_missing_domain_task: `attention` taskflow-bb72fb37d3246552
  - detail: working row has visible session 8e2abb16 but lacks ops_portal_or_domain_task
  - dedupe_key: `taskflow-bb72fb37d3246552`
  - session_id: `8e2abb16`
  - owner_lane: `outreach-coordinator`
- attention_missing_finish_link: `attention` Event Schedule Request for Koval Inc. dba KOVAL Distillery
  - detail: attention row missing ops_portal_or_domain_task, due_or_trigger_or_scheduled_action
  - dedupe_key: `taskflow-f419b95a8de9650e`
  - owner_lane: `outreach-coordinator`
- blocked_needs_owner_question_proof: `blocked` taskflow-cb3650c4908af2d9
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-cb3650c4908af2d9`
- blocked_needs_owner_question_proof: `blocked` taskflow-dcd3b23df830b215
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-dcd3b23df830b215`
- blocked_needs_owner_question_proof: `blocked` taskflow-bb13c953755d0477
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-bb13c953755d0477`
- attention_missing_finish_link: `attention` Lifetime Fitness Tasting Dinner
  - detail: attention row missing ops_portal_or_domain_task, due_or_trigger_or_scheduled_action
  - dedupe_key: `taskflow-8dbdb0a71ae849d5`
  - owner_lane: `outreach-coordinator`
- attention_missing_finish_link: `attention` Gold Eagle Wine and Spirits
  - detail: attention row missing ops_portal_or_domain_task, due_or_trigger_or_scheduled_action
  - dedupe_key: `taskflow-ab214935d0184e17`
  - owner_lane: `outreach-coordinator`
- blocked_needs_owner_question_proof: `blocked` taskflow-5b6fa4efab572601
  - detail: blocked row is routed-needs-owner-question and needs owner-question/blocker proof
  - dedupe_key: `taskflow-5b6fa4efab572601`

## Drift

- active_missing_board_session: `high` worker-readback-next-check
  - detail: active Task Flow row references missing board session d5961eef
  - session_id: `d5961eef`
  - dedupe_key: `frank-direct-primary-CAAtX44Y-8zHhju0qwVuWateFAw16-W-N2iQ6UJ6Xu6wVBxCyCA-mail-gmail-com`
- active_missing_board_session: `high` worker-readback-next-check
  - detail: active Task Flow row references missing board session ebd7fa09
  - session_id: `ebd7fa09`
  - dedupe_key: `frank-direct-primary-CAAtX44aYkuTMHyrTPk3A5-453GYgsAccVMWrzVRDLVPvUDiwcQ-mail-gmail-com`
- active_missing_board_session: `high` worker-readback-next-check
  - detail: active Task Flow row references missing board session dbf9b169
  - session_id: `dbf9b169`
  - dedupe_key: `frank-direct-primary-CAAtX44YL-cdpejiaxMZ-Ad06b7ac76pkeV18jSWstXDwqSZ3Q-mail-gmail-com`
- active_missing_board_session: `high` worker-readback-next-check
  - detail: active Task Flow row references missing board session 0cdfa142
  - session_id: `0cdfa142`
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzzXU7SahfZ-4bUFts-K9fUAQDrKjM0Q54evGHWehxP-Cg-mail-gmail-com`
- active_missing_board_session: `high` Portal worker 9f0ae713
  - detail: active Task Flow row references missing board session 99671a25
  - session_id: `99671a25`
  - dedupe_key: `avignon-direct-owner-sonat-CALbLtzwALqFwLdxDd-JedrMiePpf3WhXJrvBavMDRwf2-EAhsA-mail-gmail-com`

## Recommendation

- Truth drift exists. Repair should stay targeted to the named contradiction classes, not broad queue mutation.
