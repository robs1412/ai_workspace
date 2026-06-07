# Recursive Improvement Project Status

- Date: 2026-06-07
- Scope: non-secret status summary for the recursive improvement lane in `ai_workspace`
- Practical status: the recursive system is now useful as a verifier and proposal loop, but it is not yet a self-repairing autonomous worker.

## Current State

The project has moved from loose structure to a measurable recursive loop:

- Registry-backed checkers exist for recursive surfaces.
- Service parity is clean across the configured surface set.
- Task Flow truth drift is clean for hard contradictions.
- The proposal queue can generate bounded next actions from current checker state.
- The executor can verify no-live-mutation proposals and record keep/supersede outcomes.
- Historical recommendation coverage now includes the important state where truth drift is clean but proof-closeout issues remain.

The latest verified readback is:

- `service_parity_check.py --mode all --fail-on-drift`: `surfaces_checked=91`, `drift=0`, `fix_failed=0`
- `task_flow_truth_drift_check.py --fail-on-drift`: `drift_count=0`
- `recursive_proposal_executor.py status --json`: `approved_unexecuted_count=0`, `blocked_execution_count=0`
- proof issue count after the latest repair: `7`

## What Improved Today

Two commits landed before this note:

- `414c668` `Strengthen recursive proposal loop`
- `44f7da7` `Classify recursive proof closeout issues`

Those commits made the loop stop treating `drift_count=0` as a clean bill of health. The checker now separates hard truth drift from proof-closeout work, and the proposal queue recommends `classify-proof-closeout-issues` when proof classes remain.

A follow-up repair then fixed a false-positive class in `scripts/task_flow_truth_drift_check.py`: rows with `blocked_resolution_state=blocker_email_required` were still counted as `blocked_missing_blocker_email` even when live Task Flow already had `completion_or_blocker_email` or `clarification_email`. The checker now honors those proof markers, and regression coverage lives in `tests/test_task_flow_truth_drift_check.py`.

That reduced proof issues from `11` to `7` and removed the `blocked_missing_blocker_email` class.

## What Is Still Missing

The remaining proof classes are concrete:

- `active_worker_missing_domain_task=3`
- `blocked_needs_owner_question_proof=4`

The first class means visible worker rows still need an OPS, Portal, CRM, scheduled-action, or other domain-task anchor. The second class means blocked Avignon/Sonat owner-question rows still need explicit clarification/blocker proof attached, not just a route label.

The larger missing pieces are:

- No generic safe mutator exists for live Task Flow proof repair.
- Domain-specific repairs still need lane-aware verification before mutation.
- The loop can classify and verify, but it cannot yet choose and perform every repair without an approval or lane-specific helper.
- Papers/project summaries are now being added, but project state still depends on local handoff plus checker artifacts unless future sessions look at both.

## Next Real Step

Do not add more recursive scaffolding first.

The next useful recursive slice is to reduce one remaining class with source-first proof:

1. Pick one `blocked_needs_owner_question_proof` Avignon row.
2. Read the exact source body or sent/blocker trace.
3. Attach the correct `clarification_email` or `completion_or_blocker_email` proof if it already exists, or leave one exact owner-question blocker if it does not.
4. Rerun `task_flow_truth_drift_check.py --fail-on-drift`.
5. Accept the repair only if `drift_count` stays `0` and the target class count drops.

After that, repeat on `active_worker_missing_domain_task` by attaching or creating the proper domain-task anchor for one visible worker.

## Operating Rule

The recursive project should be judged by count-reducing proof, not by the presence of framework pieces. A good recursive step either:

- lowers a verified drift/proof class count,
- prevents a known false positive with regression coverage, or
- adds a bounded executor action with proof that it keeps the queue clean.

Anything else is structure, not recursive improvement.
