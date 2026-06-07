# Recursive Improvement Project Status

- Date: 2026-06-07
- Scope: non-secret status summary for the recursive improvement lane in `ai_workspace`
- Papers: `https://papers.koval.lan/4e450bfc-b985-47a1-aca8-8e99c91b34d3`
- Practical status: the recursive system is now useful as a verifier and proposal loop, but it is not yet a self-repairing autonomous worker.

## Current State

The project has moved from loose structure to a measurable recursive loop:

- Registry-backed checkers exist for recursive surfaces.
- Service parity is clean across the configured surface set.
- Task Flow truth drift can now separate hard contradictions from proof-closeout residue.
- The proposal queue can generate bounded next actions from current checker state.
- The executor can verify no-live-mutation proposals and record keep/supersede outcomes.
- Historical recommendation coverage now includes the important state where truth drift is clean but proof-closeout issues remain.

The latest verified readback is:

- `service_parity_check.py --mode all --fail-on-drift`: `surfaces_checked=91`, `drift=0`, `fix_failed=0`
- `task_flow_truth_drift_check.py --timeout 30 --fail-on-drift`: `drift_count=0`
- `recursive_proposal_executor.py status --json`: `approved_unexecuted_count=0`, `blocked_execution_count=0`
- proof issue count after the latest repair: `0`

## What Improved Today

Two commits landed before this note:

- `414c668` `Strengthen recursive proposal loop`
- `44f7da7` `Classify recursive proof closeout issues`

Those commits made the loop stop treating `drift_count=0` as a clean bill of health. The checker now separates hard truth drift from proof-closeout work, and the proposal queue recommends `classify-proof-closeout-issues` when proof classes remain.

A follow-up repair then fixed a false-positive class in `scripts/task_flow_truth_drift_check.py`: rows with `blocked_resolution_state=blocker_email_required` were still counted as `blocked_missing_blocker_email` even when live Task Flow already had `completion_or_blocker_email` or `clarification_email`. The checker now honors those proof markers, and regression coverage lives in `tests/test_task_flow_truth_drift_check.py`.

That reduced proof issues from `11` to `7` and removed the `blocked_missing_blocker_email` class. A follow-up source-first Task Flow repair then attached existing completion proof to two stale Avignon/Sonat packets:

- `KY Eagle Activity`: Portal activity `371570` plus Sonat completion Message-ID `<178085614085.96265.7791391698608742343@kovaldistillery.com>`.
- `Tasks`: OPS tasks `367583`, `367597`, `367611`, `367625`, and `367799` plus Sonat completion Message-ID `<178076346914.56897.10310241233963174526@kovaldistillery.com>`.

A second source-first repair then attached existing blocker proof to the `Mariano's Cancelation Process` packet:

- `Mariano's Cancelation Process`: Avignon sent Sonat the blocker/clarification on 2026-06-05, Message-ID `<178068148523.2815.2228444141886654458@kovaldistillery.com>`.

The next repair normalized the remaining scheduler-route contradiction. The sole scheduler candidate was `taskflow-ad4ec9e8dbd14f77`, tied to stale Workspaceboard session `f0332e78` for Robert's COTeam tasting-photo policy direction. Live Workspaceboard readback shows it as a waiting owner question, with blocker text, owner question, next-check metadata, and proof marker `blocker-email-required sent: <177991223121.75304.8927004146996372329@kovaldistillery.com>`. The queue report now reads `scheduler_route_candidates=0`.

The next proof repair reduced the active-worker domain-anchor class. The `Re: Contacts to add` Avignon/Sonat row already had an email-trace domain anchor for source Message-ID `<CALbLtzxzaiPHiDfb5nyrEFdRdtZAmm0iWC5rC0z4g0YUeSZUrg@mail.gmail.com>` and Workspaceboard session `f8b455e5`, but the current Task Flow packet had lost the `ops_portal_or_domain_task` value. The repair restored the existing source-backed anchor and validator returned `missing_fields=[]`.

The latest checker readback is now `drift_count=0`, `proof_issue_count=7`, `active_worker_missing_domain_task=2`, and `blocked_needs_owner_question_proof=5`. Hard Task Flow / Workspaceboard contradiction is clean, and the proof residue is still concrete but smaller.

Another source-first proof repair normalized the Naomi/BID scheduler-bridge residue for `taskflow-59994f5a1b3030bd`. Live Workspaceboard readback for session `cb6685a4` showed the worker already closed with proof marker `taskflow-59994f5a1b3030bd:naomi_finance_ops_triage_row_verified_visible_worker_cb6685a4_no_finance_mutation`. The Task Flow packet was updated from stale `working` state to proof-backed `completed`, with the Workspaceboard proof marker attached as the domain anchor. Verification readback now shows `drift_count=0`, `proof_issue_count=8`, `active_worker_missing_domain_task=1`, and `blocked_needs_owner_question_proof=7`.

A second scheduler-bridge proof repair normalized the National Outreach row `taskflow-82e27c83e26920f1`. Live Workspaceboard readback for session `abbb9e24` showed `status=blocked`, `status_label=blocked-question-required`, and a concrete owner question asking for the missing source body/details or target OPS/Outreach event fields. The Task Flow packet was updated from stale `working` state to proof-backed `blocked`, with domain anchor `taskflow-82e27c83e26920f1:workspaceboard_blocked_owner_question_event_54382` and blocker proof in the clarification/blocker fields. Verification readback now shows `drift_count=0`, `proof_issue_count=7`, `active_worker_missing_domain_task=0`, and `blocked_needs_owner_question_proof=7`.

Two more source-first repairs normalized National Outreach approved-send failures that were real failed-draft blockers, not owner-question packets with no proof:

- `taskflow-ba6476bb78a0fea6`: failed Sonat draft `vanessa-sonat-wholefoods-binnys-cancellation-instructions-20260607.failed-1780862943.json`; owner lane `outreach-coordinator`, responsible worker `vanessa.sterling@kovaldistillery.com`, and domain anchor `Vanessa cancellation automation / Whole Foods and Binnys instructions` came from the failed artifact. The row now records that no Message-ID was produced and the draft must be reviewed/resubmitted only through the approved sender path.
- `taskflow-30d49867a47b3e48`: failed Sonat owner-question draft `vanessa-sonat-tasting-selection-cancellation-instructions-20260607.failed-1780861912.json`; owner lane `outreach-coordinator`, responsible worker `vanessa.sterling@kovaldistillery.com`, and `owner_question=true` came from the failed artifact. The row now records the failed draft as the blocker proof without claiming a sent email.

Latest verification now reads `drift_count=0`, `proof_issue_count=5`, `active_worker_missing_domain_task=0`, and `blocked_needs_owner_question_proof=5`.

The next pass completed the remaining National Outreach failed-send proof rows from source artifacts:

- `taskflow-fe3920e9e9ebb56b`: failed reply artifact for `Re: 6/23 and 6/24 work withs in Wisconsin`; owner lane `outreach-coordinator`; domain anchor `OPS Market Events 996,997,998,999; Portal tasks 371622,371623,371624,371625`; no Message-ID present.
- `taskflow-b4e191619e3f6349`: failed Wild Onion open-shift artifact; owner lane `outreach-coordinator`; domain anchor `OPS Outreach event 1054 / COT shift 5582`; no Message-ID present.
- `taskflow-9b2842a7eb885dc2`: failed Wild Onion open-shift artifact; owner lane `outreach-coordinator`; domain anchor `OPS Outreach event 1054 / shift 5582 / Google UID ops-outreach-1054@koval-distillery.com`; no Message-ID present.

Latest verification now reads `drift_count=0`, `proof_issue_count=3`, `active_worker_missing_domain_task=1`, and `blocked_needs_owner_question_proof=2`. The new active-worker item is `taskflow-ae81653c00a5b9c3` / session `7042867f`, a fresh scheduler-bridge worker with due time `2026-06-07 15:25:37`; the Workspaceboard API timed out during source readback, so it should be rechecked after the worker has a domain proof, blocker, or closeout.

The final repair pass cleared the remaining proof classes:

- `taskflow-ae81653c00a5b9c3`: Workspaceboard session `7042867f` later read back as `finished` / `closed_with_proof` with proof marker `NO_ACTION_DUPLICATE_MITCH_JUNE_XLSX_SENT_178033448573_ARCHIVED_SOURCE_SJ0PR10_20260607`. The Task Flow packet now records `no_action_closed`, the proof marker as the domain anchor, and the readback that no resend or OPS mutation was needed.
- `avignon-direct-owner-sonat-CALbLtzybRf2Q7-v9Rk8DhHOVGUQXJ3ZzaQphge-pOiA07o9tg-mail-gmail-com`: Avignon task-flow event `avignon_message_action` on 2026-06-07 recorded `direct-owner-route-blocked-local-no-email`, route blocker `timed out`, source not archived, and completion target `visible-worker-completion-or-blocker`. The Task Flow packet now carries that as blocker proof and keeps the item blocked until a visible Avignon worker completes or sends a real blocker report.
- `avignon-direct-owner-sonat-CALbLtzwz-wqeo3XaxhGUzVzHTLq6RC1Vt-DczdhwnX-qb4F6bg-mail-gmail-com`: Avignon task-flow event `avignon_message_action` on 2026-06-05 recorded the same route-timeout blocker for `Fwd: KOVAL and Thresh and Winnow In Market Recap for 6/4`. The Task Flow packet now carries that blocker proof without claiming a sent email or handled filing.

Latest verification now reads `drift_count=0`, `proof_issue_count=0`, `active_worker_missing_domain_task=0`, and `blocked_needs_owner_question_proof=0`.

Recurring OPS coverage was also added so the loop does not depend on ad hoc chat prompts:

- OPS task `371626`: `Daily recursive improvement proof check`, Codex-owned, silent, `21:30-21:55`, `recurringtype=1 day`.
- OPS task `371627`: `Weekly recursive improvement rollup`, Codex-owned, silent, Sunday `20:30-21:15`, `recurringtype=weekly`.
- Both recurrence strings were verified through the OPS recurrence parser, and both rows read back with `sendnotification=0`, creator Robert `1`, owner/assignee Codex `1332`.

## What Is Still Missing

No remaining proof classes are currently reported by the recursive checker.

The larger missing pieces are:

- No generic safe mutator exists for live Task Flow proof repair.
- Domain-specific repairs still need lane-aware verification before mutation.
- The loop can classify and verify, but it cannot yet choose and perform every repair without an approval or lane-specific helper.
- Papers/project summaries are now being added, but project state still depends on local handoff plus checker artifacts unless future sessions look at both.

## Next Real Step

Do not add more recursive scaffolding first.

The latest repairs cleared all current proof classes. The next useful recursive slice was monitor mode plus one targeted improvement: turn the repeated source-first repair pattern for failed approved-send artifacts and route-timeout blockers into a bounded, dry-run proposal that can identify repair candidates without mutating them automatically.

That detector now exists as `scripts/task_flow_proof_repair_candidates.py`.

It is deliberately read-only. It scans live Task Flow report rows, then proposes source-backed repair fields only when a row still needs proof and one of these source patterns is present:

- National Outreach approved-send failure artifacts in `.nationaloutreach-launch/state/failed`, using only top-level metadata plus `task_packet` fields. It does not copy message bodies.
- Avignon/Sonat direct-owner route-timeout events in `.avignon-launch/state/task-flow-events.jsonl`, using only matching event metadata for `timed out` / `direct-owner-route-blocked-local-no-email` blockers.

Regression coverage was added in `tests/test_task_flow_proof_repair_candidates.py` for both positive patterns and for the negative case where an already proof-backed Avignon row must not be proposed again.

Current verification:

- `python3.13 -m py_compile scripts/task_flow_proof_repair_candidates.py tests/test_task_flow_proof_repair_candidates.py`: pass.
- `python3.13 -m unittest tests.test_task_flow_proof_repair_candidates`: pass, 3 tests.
- `python3.13 scripts/task_flow_proof_repair_candidates.py --print-json`: scanned `500` Task Flow rows, `candidate_count=0`, `mutation_allowed=false`.
- `./scripts/service_parity_check.py --mode all --fail-on-drift`: `surfaces_checked=91`, `drift=0`, `fix_failed=0`.
- `./scripts/task_flow_truth_drift_check.py`: `drift_count=0`, `proof_issue_count=0`, `proof_issue_class_counts={}`.

The detector is now wired into the recursive proposal queue:

- `scripts/recursive_proposal_queue.py` runs `scripts/task_flow_proof_repair_candidates.py --print-json` as part of the snapshot.
- If candidates appear, `choose_action` now emits `review-source-backed-proof-repair-candidates` with approval required, risk `low`, and fix class `source-backed-proof-repair-candidate`.
- `scripts/recursive_proposal_executor.py` allowlists `source-backed-proof-repair-candidate`, marks it as live-state-mutating, and intentionally provides no generic auto-mutator. Execution therefore remains approval- and lane-repair-gated.
- Regression coverage lives in `tests/test_recursive_proposal_queue.py` and `tests/test_recursive_proposal_executor.py`.

This wiring also exposed and fixed a queue snapshot bug: raw `proof_closeout_issues` must not override an explicit classified `proof_issue_count=0`. The bad intermediate proposal `recursive-proposal-20260607-155628-classify-proof-closeout-issues` was marked superseded by the corrected monitor proposal `recursive-proposal-20260607-155717-monitor-recursive-lane`.

Current proposal verification:

- `python3.13 -m unittest tests.test_recursive_proposal_queue tests.test_recursive_proposal_executor`: pass, 10 tests.
- `python3.13 scripts/recursive_proposal_queue.py --skip-historical-benchmark-refresh --json`: emitted `monitor-recursive-lane`, `proof_issue_count=0`, `proof_repair_candidate_count=0`.
- `python3.13 scripts/recursive_proposal_executor.py status --json`: new fix class `source-backed-proof-repair-candidate` is allowlisted, live-state-mutating, and has no auto-mutator.
- `python3.13 scripts/recursive_proposal_executor.py execute --proposal-id recursive-proposal-20260607-155717-monitor-recursive-lane --json`: `execution_state=verified`, `ratchet_result=keep`, verifier return code `0`.

The recurring daily command contract now exists as `scripts/recursive_daily_run.py`.

Daily behavior:

- Generate a fresh recursive proposal snapshot.
- Auto-execute only no-op monitor proposals.
- Leave approval-required or non-monitor proposals queued for source-first review.
- Write durable run artifacts to `project_hub/artifacts/recursive-tools/recursive-daily-run-latest.json` and `.md`.

Regression coverage was added in `tests/test_recursive_daily_run.py` so only `monitor-recursive-lane` / `no-op-monitoring` can auto-execute. Source-backed proof repair candidates and proof-classification proposals do not auto-run.

First live daily run found a real new proof issue:

- `taskflow-nationaloutreach-google-chat-send-allowlist-2026-06-07`
- class `attention_missing_finish_link`
- missing `ops_portal_or_domain_task`
- source: `project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/README.md` and `chat-send.py`

Source-first repair filled only the Task Flow domain anchor:

- `National Outreach Google Chat send allowlist / chat.messages.create OAuth setup`

The row remains `waiting` for Robert's browser OAuth re-consent. No Google Chat auth, token read, Chat readback, or Chat send action was performed.

Post-repair verification:

- Task Flow validator returned `missing_fields=[]`.
- Live row readback shows the new domain anchor and `missing_fields=[]`.
- `python3.13 scripts/recursive_daily_run.py --print-json` then emitted `monitor-recursive-lane`.
- Latest daily run artifact: `outcome=monitor_verified`, `auto_executed=true`, proposal `recursive-proposal-20260607-160438-monitor-recursive-lane`, `proof_issue_count=0`, `proof_repair_candidate_count=0`, `execution_state=verified`, `ratchet_result=keep`.
- The pre-repair proposal `recursive-proposal-20260607-160304-classify-proof-closeout-issues` was marked `superseded_by_verified_retry`.
- Executor status now shows `approved_unexecuted_count=0` and `blocked_execution_count=0`.
- `python3.13 -m unittest tests.test_recursive_daily_run tests.test_recursive_proposal_queue tests.test_recursive_proposal_executor`: pass, 13 tests.

## Operating Rule

The recursive project should be judged by count-reducing proof, not by the presence of framework pieces. A good recursive step either:

- lowers a verified drift/proof class count,
- prevents a known false positive with regression coverage, or
- adds a bounded executor action with proof that it keeps the queue clean.

Anything else is structure, not recursive improvement.
