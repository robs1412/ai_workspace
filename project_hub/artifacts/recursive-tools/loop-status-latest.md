# Loop Status

- Recorded: 2026-06-09 19:36:11 CDT
- Schema version: `2`
- Mode: `read-only-loop-status`
- Mutation allowed: `False`
- Next action: `review_dirty_repositories`

## Workspaceboard

- ok: `True`
- checked_at: `2026-06-09 19:36:17 CDT`
- checks: `18`
- by_status: `{"green": 18}`
- error: ``

## Recursive Executor

- approved_unexecuted_count: `0`
- blocked_execution_count: `0`

## Truth And Proof Repair

- drift_count: `0`
- proof_issue_count: `5`
- proof_repair_candidate_count: `5`
- proof_repair_packet_count: `5`
- proof_repair_needs_approval_count: `0`
- candidates_source_mtime: `2026-06-09 19:36:16 CDT`
- packets_source_mtime: `2026-06-09 16:09:56 CDT`
- packet_pending_review_count: `0`

## Git Hygiene

- repos_scanned: `31`
- dirty_repos: `2`
- dirty_repo_pending_review_count: `2`
- dirty_repo_blocked_review_count: `0`
- buckets: `{"active-lane-work": 1, "finance-lane-review": 1}`

## Degraded Sources

- count: `0`
## Boundary

- This status is read-only. It does not send email, mutate Task Flow, update OPS/Portal, commit, push, pull, or clean repositories.
