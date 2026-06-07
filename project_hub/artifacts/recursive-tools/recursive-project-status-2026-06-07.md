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
- proof issue count after the latest repair: `7`

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

## What Is Still Missing

The remaining proof classes are concrete:

- `active_worker_missing_domain_task=2`
- `blocked_needs_owner_question_proof=5`

The first class means visible worker rows still need an OPS, Portal, CRM, scheduled-action, or other domain-task anchor. The second class means blocked Avignon/Sonat owner-question rows still need explicit clarification/blocker proof attached, not just a route label.

The larger missing pieces are:

- No generic safe mutator exists for live Task Flow proof repair.
- Domain-specific repairs still need lane-aware verification before mutation.
- The loop can classify and verify, but it cannot yet choose and perform every repair without an approval or lane-specific helper.
- Papers/project summaries are now being added, but project state still depends on local handoff plus checker artifacts unless future sessions look at both.

## Next Real Step

Do not add more recursive scaffolding first.

The latest repair removed the remaining hard scheduler contradiction. The next useful recursive slice is now proof-only:

1. Pick one `active_worker_missing_domain_task` row.
2. Attach or create the proper OPS, Portal, CRM, scheduled-action, or other domain-task anchor.
3. Rerun `task_flow_truth_drift_check.py --fail-on-drift`.
4. Accept the repair only if the target class count drops and no new hard contradiction is introduced.

Or, if staying in the blocked-owner-question class:

1. Pick one remaining `blocked_needs_owner_question_proof` Avignon row.
2. Read the exact source body or sent/blocker trace.
3. Attach the correct `clarification_email` or `completion_or_blocker_email` proof if it already exists, or leave one exact owner-question blocker if it does not.
4. Rerun `task_flow_truth_drift_check.py --fail-on-drift`.
5. Accept the repair only if the target class count drops.

## Operating Rule

The recursive project should be judged by count-reducing proof, not by the presence of framework pieces. A good recursive step either:

- lowers a verified drift/proof class count,
- prevents a known false positive with regression coverage, or
- adds a bounded executor action with proof that it keeps the queue clean.

Anything else is structure, not recursive improvement.
