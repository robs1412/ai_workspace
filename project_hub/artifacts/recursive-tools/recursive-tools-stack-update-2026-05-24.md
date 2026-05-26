# Recursive Tools Stack Update

- Recorded: 2026-05-24 13:08 CDT
- Scope: non-secret update to the earlier recursive-tools assessment and implementation state

## Practical Update

The original assessment direction still holds:

- adopt structured planning/refactor skills first
- use `recursive-improve` as a contained improvement lane
- defer `recursive-codex` unless a UI repo later needs screenshot-feedback-edit loops

But the system has moved beyond the original pilot framing.

## What Is Now Real

### Python / runtime caveat is no longer the main blocker

The earlier note said the pilot was prepared but limited by Python `3.9.6`.

That is now stale.

The recursive lane has already been moved onto explicit Python `3.13` execution for the local toolchain and related helper/runtime surfaces.

### Recursive-improve already did useful work

The pilot did not stop at sandbox bootstrap.

It was used to drive:

- Python `3.13` entrypoint migration
- source/runtime parity detection
- deployment-state detection
- AI Health recurring service parity check
- unified Task Flow / Workspaceboard / proof-surface truth-drift detection

### Checker hardening is now a real recursive lane

There are now two real recurring checker lanes:

1. service parity
2. Task Flow truth drift

Both now use registry-owned surface maps rather than hardcoding all live paths directly in checker code.

Current owned registries:

- `/Users/werkstatt/ai_workspace/scripts/service_parity_surfaces.json`
- `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`

This is the main architectural improvement because future code or deployment changes now have an explicit update point.

## Useful-Codex-Skills Follow-Through

The immediate value from `useful-codex-skills` is still the right next durable pattern.

That work is now partially implemented locally as Codex skills under `/Users/admin/.codex/skills/`:

- `refactor-candidate-search`
- `refactor-decision-lock`
- `execplan-author`
- `execplan-audit`
- `execplan-implement`
- `implementation-review`

These are not a wholesale upstream copy. They are local, narrower adaptations:

- they use `.agent/work/...` for planning artifacts
- they explicitly avoid treating `.agent/` as the task system in DB-first repos
- they fit the existing source-first, durable-state workflow better than a free-running recursive loop

The local loop is now:

- search
- decide
- plan
- audit
- implement
- review

## Checker Hardening Follow-Through

Added local utility:

- `/Users/werkstatt/ai_workspace/scripts/recursive_registry_lint.py`

Purpose:

- validate both recursive checker registries without touching live board/runtime/deployment surfaces
- fail fast when architecture metadata drifts before the operational checker runs

Current validation readback:

- `task_flow_truth_surfaces.json`: `ok`, `version=1`
- `service_parity_surfaces.json`: `ok`, `version=1`

Coverage ownership is now explicit too:

- `/Users/werkstatt/ai_workspace/scripts/recursive_checker_coverage.json`

That manifest declares, for each recursive checker:

- what it covers
- what is explicitly out of scope
- which command is the verification surface

Current coverage-manifest readback:

- `service_parity`
- `task_flow_truth_drift`
- `recursive_registry_lint`

## What Next

The next useful recursive work is not more blind drift mutation.

It should be:

1. let the active inbox / queue cleanout lane continue repairing live truth drift
2. re-read the truth-drift results after that lane settles
3. benchmark recommendation quality for one bounded recursive target
4. widen checker coverage only through registry-owned surfaces

## Recommendation

Keep the operating split:

- default stack behavior stays explicit, source-first, and human-directed
- recursive tooling remains an improvement lane for prompts, checkers, and bounded refactor/planning workflows
- no unattended broad mutation on OPS, Portal, mailbox runtimes, or other owner-visible operational lanes

## Recommendation-Quality Benchmark

The next bounded recursive step is now implemented too.

Added under the pilot target:

- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/recommendation_benchmark_agent.py`
- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_recommendation_benchmark.py`

Purpose:

- benchmark whether the recursive lane picks the right next move from bounded lane-state scenarios
- keep the benchmark local and non-operational
- avoid racing the separate live truth-drift cleanup terminal

Scenario classes now covered:

- live cleanup already in flight elsewhere
- truth drift present and not already in a separate cleanup lane
- service parity drift present
- registry / coverage contract broken
- architecture stable enough to add a benchmark

Readback:

- traces dir: `sandboxes/recursive-improve-pilot-target-313/eval/recommendation-traces`
- eval output dir: `sandboxes/recursive-improve-pilot-target-313/eval/recommendation-benchmark`
- durable note: `project_hub/artifacts/recursive-tools/recursive-recommendation-benchmark-2026-05-24.md`
- live snapshot note: `project_hub/artifacts/recursive-tools/recursive-live-recommendation-snapshot-2026-05-24.md`
- eval run id: `7596f83f91ec`
- benchmark run id: `b3d095e7b2e4`
- trace count: `5`
- `clean_success_rate = 100.0% (5/5)`
- benchmark label: `recommendation-quality-liveaware-2026-05-24`
- live snapshot eval run id: `cde619b65fda`
- live snapshot benchmark run id: `bc145700f885`

What this proves:

- the recursive lane is no longer only checking drift and parity
- it now has a bounded quality baseline for next-step recommendations
- it now also consumes real checker snapshots, not just synthetic scenarios
- the current live readback recommends `repair-truth-drift`, driven by one remaining `active_missing_board_session` contradiction

## Historical Recommendation Corpus

Added a larger replay corpus for recommendation quality:

- cases: `sandboxes/recursive-improve-pilot-target-313/recommendation_historical_cases.json`
- runner: `sandboxes/recursive-improve-pilot-target-313/run_historical_recommendation_benchmark.py`
- report: `project_hub/artifacts/recursive-tools/recursive-historical-recommendation-benchmark-2026-05-24.md`

The corpus replays known recursive-lane states from this work:

- Python migration clean closeout
- broad service parity drift before runtime reconcile
- truth drift while another terminal is actively cleaning
- single remaining truth drift
- broken registry / coverage contract
- local skill loop not yet proven

Readback:

- cases: `6`
- eval run id: `305f1b72f49c`
- benchmark run id: `3b31329dcd91`
- benchmark label: `historical-recommendation-quality-2026-05-24`
- `clean_success_rate = 100.0% (6/6)`

Autonomy ladder from here:

1. Recommendation-only, current state.
2. Proposal queue, next state: write exact fix proposals with risk class and required approval.
3. Approval-gated fixer: execute only whitelisted low-risk fix classes after benchmark pass.
4. Post-fix verifier: rerun checker, benchmark, and durable note automatically after a fix.
5. Ratchet loop: keep/revert prompt or checker changes based on benchmark deltas.

Do not jump straight to broad self-editing. The next useful autonomy step is the proposal queue.

## Approval Queue Ownership

Robert clarified the owner loop for the proposal queue: Frank owns the human approval conversation.

Operating split:

- Codex generates proposal packets from checker output, benchmark state, and live snapshots.
- Frank emails Robert one plain yes/no decision request per proposal.
- Robert replies yes or no.
- Frank records the decision and routes any approved execution back to Codex or the right visible worker.
- Codex executes only approved low-risk fix classes and then reruns the proof checks.
- Frank sends the completion or blocker report after proof exists.

Published Papers note:

- `https://papers.koval.lan/89b2ac72-7476-4962-ad27-2b409a89554e`

Claude comparison email:

- Corrected To: `claude@kovaldistillery.com`
- Cc: `robert@kovaldistillery.com`
- Subject: `Recursive improvement loop comparison`
- Message-ID: `<177964800446.11583.9902601401452484732@kovaldistillery.com>`
- Task id: `frank-claude-recursive-improvement-comparison-2026-05-24-corrected`
- Supersedes the earlier send to `claude@koval-distillery.com` under Message-ID `<177964786970.11134.2806295771480830949@kovaldistillery.com>`.

Claude was asked whether his side already has an equivalent loop covering drift/checker detection, recommendation-quality benchmarking, historical replay, approval-gated proposals, post-fix verification, or ratchet keep/revert behavior.

Claude replied:

- Message-ID: `<e33045f80d90839935ce4c9bb85e1f29.claude@kovaldistillery.com>`
- Date: `Sun, 24 May 2026 13:42:59 -0500`
- Location: Frank Gmail All Mail, labels `Handled` and `Important`; not currently in `INBOX`
- Local summary: `project_hub/artifacts/recursive-tools/claude-recursive-improvement-reply-2026-05-24.md`

Summary of reply: Claude has approval gates, task staleness/watchdog handling, circuit breaker logic, and post-work verification at the task/work-output level. He does not yet have recommendation-quality benchmarking, historical replay, recursive checker registries, service/truth drift checkers, ratchet keep/revert logic, or a self-improvement loop that modifies agent prompts/code based on measured outcomes. He recommends aligning on the shared interface before his side builds a parallel implementation and offered to share `CLAUDE.md`, `guards.sh`, and watchdog structure.

## Changed Papers Version And Claude Follow-Up

Updated Papers version:

- `https://papers.koval.lan/346f243c-b610-489c-8323-627df9ca9f8d`

Frank sent Claude the changed version and current state:

- To: `claude@kovaldistillery.com`
- Cc: `robert@kovaldistillery.com`, `dmytro.klymentiev@kovaldistillery.com`
- Subject: `Re: Recursive improvement loop comparison`
- Message-ID: `<177964923221.16079.8878460685095716018@kovaldistillery.com>`
- In-Reply-To: `<e33045f80d90839935ce4c9bb85e1f29.claude@kovaldistillery.com>`
- Draft: `frank/drafts/claude-recursive-improvement-v2-update-2026-05-24.html`

The update told Claude that the proposal emails are now HTML/readable, decisions are durable state, stale approvals reconcile against clean monitors, and the next shared interface should define proposal packet fields for checker snapshot, recommended action, allowed fix class, risk class, approval state, execution proof, and keep/revert result.

## Proposal Queue Implementation

The approval-gated proposal queue now has a local generator:

- `scripts/recursive_proposal_queue.py`

What it does:

- reads live service parity, truth-drift, registry, and historical benchmark state
- chooses the next bounded recommendation
- writes proposal JSON and Markdown under `project_hub/artifacts/recursive-tools/proposals/`
- writes the Frank approval email body under `frank/drafts/recursive-proposals/`
- appends a queue row to `project_hub/artifacts/recursive-tools/recursive-proposal-queue.jsonl`

First live proposal:

- Proposal id: `recursive-proposal-20260524-134350-repair-truth-drift`
- Recommended action: `repair-truth-drift`
- Risk class: `medium`
- Allowed fix class: `truth-drift-single-item-repair`
- Proposal artifact: `project_hub/artifacts/recursive-tools/proposals/recursive-proposal-20260524-134350-repair-truth-drift.md`
- Frank approval email: sent to Robert
- Message-ID: `<177964828163.12510.14353964488768279452@kovaldistillery.com>`

The queue is now wired through the intended ownership model: Codex generated the packet; Frank sent the yes/no decision request; execution waits for Robert's reply.

## Proposal Email Template Upgrade

Robert replied to the first proposal request and then corrected the email quality: approval emails need more explanation, better readability, and a real HTML format.

Updated:

- `scripts/recursive_proposal_queue.py`

Template changes:

- richer plain-text body
- separate formatted HTML body
- point-first recommendation
- why-this-is-coming-to-you section
- current checker/benchmark readback section
- explicit boundaries
- risk and proof section
- visible YES/NO decision line

Current proposal files were upgraded too:

- text body: `frank/drafts/recursive-proposals/recursive-proposal-20260524-134350-repair-truth-drift.txt`
- HTML body: `frank/drafts/recursive-proposals/recursive-proposal-20260524-134350-repair-truth-drift.html`

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/recursive_proposal_queue.py`
- Frank HTML dry-run rendered the upgraded `repair-truth-drift` approval email successfully.

Fresh queue readback after the template upgrade:

- proposal id: `recursive-proposal-20260524-134813-monitor-recursive-lane`
- recommendation: `monitor-recursive-lane`
- approval required: `false`
- service parity drift: `0`
- truth drift count: `0`
- registry and coverage: `ok`

This means the active drift that triggered the first approval request was already cleared by the time the improved template pass reran. The queue now properly records a no-op monitoring state instead of asking for another approval.

## Proposal Decision Recorder

The approval queue now has an explicit decision/state recorder:

- `scripts/recursive_proposal_decisions.py`
- decision log: `project_hub/artifacts/recursive-tools/recursive-proposal-decisions.jsonl`
- Papers addendum: `https://papers.koval.lan/99336886-09d1-4a6d-b09d-f43093344bcd`

Supported operator commands:

- `./scripts/recursive_proposal_decisions.py status --json`
- `./scripts/recursive_proposal_decisions.py record-decision --proposal-id latest-pending --decision yes --source-message-id '<reply-message-id>' --notes 'non-secret note'`
- `./scripts/recursive_proposal_decisions.py record-decision --proposal-id latest-pending --decision no --source-message-id '<reply-message-id>' --notes 'non-secret note'`
- `./scripts/recursive_proposal_decisions.py record-decision --proposal-id latest-pending --decision unclear --source-message-id '<reply-message-id>' --notes 'non-secret note'`
- `./scripts/recursive_proposal_decisions.py reconcile-clean-monitor`

The recorder updates the proposal JSON with `decision_state`, appends an immutable JSONL decision event, and does not read mailbox content or execute repairs.

Readback after reconciliation:

- `recursive-proposal-20260524-134350-repair-truth-drift` is now `superseded_by_clean_monitor`
- superseding monitor: `recursive-proposal-20260524-134813-monitor-recursive-lane`
- `pending_approval_count=0`

This closes the loose approval residue caused by a repair proposal being overtaken by a later clean checker readback.

## Approved Execution Runner

The recursive approval queue now has the first approved-execution runner:

- `scripts/recursive_proposal_executor.py`
- execution log: `project_hub/artifacts/recursive-tools/recursive-proposal-executions.jsonl`
- Papers v3: `https://papers.koval.lan/89f95776-d0d4-47e2-94fc-c48064355ec2`

Supported commands:

- `./scripts/recursive_proposal_executor.py status --json`
- `./scripts/recursive_proposal_executor.py execute --proposal-id latest-approved --dry-run --json`
- `./scripts/recursive_proposal_executor.py execute --proposal-id <proposal-id> --json`
- `./scripts/recursive_proposal_executor.py execute --proposal-id <proposal-id> --allow-live-mutation --json`

Current allowlisted fix classes:

- `no-op-monitoring`: verifies registry, service parity, and truth-drift checks are clean.
- `registry-metadata-fix`: verifies `recursive_registry_lint.py --json`.
- `recommendation-corpus-fix`: can regenerate and verify the historical recommendation benchmark.
- `source-runtime-parity-fix`: can run the guarded writable installed-runtime interpreter fixer, but requires `--allow-live-mutation`.
- `truth-drift-single-item-repair`: allowlisted for state tracking, but currently blocks with `blocked_no_auto_mutator` because there is no safe generic live mutator for arbitrary Task Flow truth drift.

Current readback:

- `approved_unexecuted_count=0`
- existing proposals remain non-executable: the old repair proposal is `superseded_by_clean_monitor`, and the current monitor proposal does not require approval.

This means the recursive lane now has the full state-machine skeleton: recommend -> propose -> approve/reject/supersede -> execute/verify/block. It is still not fully autonomous because live mutation remains gated and truth-drift repair still needs a concrete proposal-specific mutator.

Frank sent Claude the executor update:

- To: `claude@kovaldistillery.com`
- Cc: `robert@kovaldistillery.com`, `dmytro.klymentiev@kovaldistillery.com`
- Subject: `Re: Recursive improvement loop comparison`
- Message-ID: `<177964957514.17815.13480250926490834788@kovaldistillery.com>`
- Draft: `frank/drafts/claude-recursive-improvement-executor-update-2026-05-24.html`

Claude replied with the first concrete interface mapping:

- Message-ID: `<01200656101f1aa370267e977718c3c7.claude@kovaldistillery.com>`
- Date: `Sun, 24 May 2026 14:02:31 -0500`
- Location: Frank Gmail All Mail, labels `Handled` and `Important`; not currently in `INBOX`
- Local summary: `project_hub/artifacts/recursive-tools/claude-recursive-interface-mapping-2026-05-24.md`

Useful mapping from Claude: proof on his side is not a dedicated field yet. It lives in `worklog_guid` plus final specialist/task comments; approval/verification gates are represented by task status and tags such as `blocked:approval`, verification comments by the system author, PM acceptance-criteria comments, and linked Papers plans via `plan_guid`. The likely interface map is Codex `execution_proof` -> Claude `worklog_guid` + final specialist comment, Codex `approval_state` -> Claude status/tag plus approval email/Papers plan reference, and Codex `verifier_result` -> Claude verification/task comments.

Claude replied again after the executor update:

- Message-ID: `<b2f371c5770442e1f75b37ccca257a2b.claude@kovaldistillery.com>`
- Date: `Sun, 24 May 2026 14:07:59 -0500`

Useful content: Claude agreed the interface skeleton is solid as a shared contract, specifically endorsed separate execution events plus the allowlist-by-class / `--allow-live-mutation` gate, and reiterated that the remaining gap is proposal-specific mutators for truth-drift.

Frank replied with the schema request:

- Message-ID: `<177964981391.19315.962153949238447022@kovaldistillery.com>`
- Draft: `frank/drafts/claude-recursive-schema-request-2026-05-24.html`
- Request: non-secret task-chain/comment schema for task ids, parent/child fields, status values, approval/blocker tags, `plan_guid`, `worklog_guid`, final specialist comments, verification comments, closure condition, delivery trigger, and stable proof references.

## AI Health Wiring

Timestamp: 2026-05-24 14:20 CDT.

Decision: do not add a separate LaunchDaemon for the recursive proposal lane right now. The existing AI Health Manager cadence is the correct durable visibility surface, because it already owns watchdog status, health artifacts, and operator readback.

Implementation:

- `scripts/ai_health_check.py` now runs `scripts/recursive_proposal_decisions.py status --json` and `scripts/recursive_proposal_executor.py status --json`.
- AI Health writes readback artifacts to:
  - `tmp/ai-health-manager/recursive-proposal-decisions-status-latest.json`
  - `tmp/ai-health-manager/recursive-proposal-executor-status-latest.json`
- `tmp/ai-health-manager/latest.md` and `tmp/ai-health-manager/latest.json` now include `recursive_proposals` with pending approvals, approved-but-unexecuted proposals, blocked executions, allowlisted fix classes, and the latest clean monitor.
- The board-down and run-timeout report paths also include `recursive_proposals`, so this lane remains visible even if the Workspaceboard `/api/status` endpoint is timing out.

Live readback after the patch:

- AI Health latest artifact: `checked_at=2026-05-24T19:19:27Z`
- board status: `board down; status check failed: status endpoint failed: timed out`
- recursive status: `passed`
- pending approvals: `0`
- approved unexecuted proposals: `0`
- blocked executions: `0`
- Papers update: `https://papers.koval.lan/f95e7f60-fda6-495c-a485-b2c66ff29110`

Current operating interpretation: the recursive system is wired for proposal visibility, decision recording, approved execution, and AI Health monitoring. It is still not fully autonomous because proposal generation is not continuously scheduled, live mutation remains approval/allowlist gated, and truth-drift repair still needs proposal-specific mutators.

## Executor Ratchet Result Recording

Timestamp: 2026-05-24 14:28 CDT.

Implementation:

- `scripts/recursive_proposal_executor.py` now records `ratchet_result` and `ratchet_reason` on execution attempts.
- Successful verifier readback records `ratchet_result=keep`.
- Failed verifier or mutator readback records `ratchet_result=revert_required`.
- `recommendation-corpus-fix` now has explicit execution proof extraction for:
  - historical benchmark results JSON
  - historical benchmark report path
  - benchmark run id
  - benchmark trace count
  - clean success rate
  - benchmark success flag
- Executor status now reports `blocked_execution_count`, `has_auto_mutator`, and any stored `ratchet_result` per proposal.

Verification:

- `python3.13 -m py_compile scripts/recursive_proposal_executor.py scripts/ai_health_check.py` passed.
- Proof collector readback for `recommendation-corpus-fix` found benchmark run `305f1b72f49c`, trace count `6`, clean success rate `1.0`, and success `true`.
- `./scripts/recursive_proposal_executor.py status --json` returned `approved_unexecuted_count=0` and `blocked_execution_count=0`.
- AI Health dry-run completed with `recursive_proposals=passed`, `pending=0`, `approved_unexecuted=0`, and `blocked=0`.

Current boundary: this does not create a fake approved proposal and does not execute live repair. It makes the first low-risk proposal-specific mutator (`recommendation-corpus-fix`) capable of leaving keep/revert proof when a real approved proposal exists.

## Claude Planner Schema Ingest

Timestamp: 2026-05-24 14:31 CDT.

Claude sent the requested stable Planner schema:

- Message-ID: `<62e95dd42623af2de8449e4c56816ac2.claude@kovaldistillery.com>`
- Date: `Sun, 24 May 2026 14:13:14 -0500`
- Local mapping note: `project_hub/artifacts/recursive-tools/claude-planner-recursive-schema-2026-05-24.md`
- Papers mapping: `https://papers.koval.lan/1e7119d3-e2cc-4ff0-900f-d1251eaa5f0a`

Useful mapping now recorded:

- Claude task chain: `tasks.id`, `parent_task_id`, `blocker_task_id`.
- Claude approval state: `status='queued'` plus tags such as `blocked:approval`.
- Claude plan/proposal proof: `tasks.plan_guid`.
- Claude execution proof: `tasks.worklog_guid` plus final specialist comment.
- Claude verifier proof: `tester-agent` comments with `comment_type='verification'`.
- Claude delivery proof: secretary comment containing `Delivery notification sent`.
- Claude incident/revert signal: `error:incident`, `error:crash`, failed verifier comments, or generated incident follow-up tasks.
- Unstable fields to avoid: `previous_status`, `session_id`, `context_summary`.

Practical consequence: Codex can now align its recursive fields (`approval_state`, `execution_proof`, `verifier_result`, `ratchet_result`) to stable Claude Planner fields/comments without requiring Claude to implement a parallel self-improvement proposal queue immediately.

Frank replied to Claude with the ingest result and next bridge ask:

- To: `claude@kovaldistillery.com`
- Cc: `robert@kovaldistillery.com`, `dmytro.klymentiev@kovaldistillery.com`
- Subject: `Re: Recursive improvement loop comparison`
- Message-ID: `<177965118899.26351.4879639112037777951@kovaldistillery.com>`
- In-Reply-To: `<62e95dd42623af2de8449e4c56816ac2.claude@kovaldistillery.com>`
- Drafts:
  - `frank/drafts/claude-recursive-planner-schema-ingest-2026-05-24.txt`
  - `frank/drafts/claude-recursive-planner-schema-ingest-2026-05-24.html`

The reply confirmed the Codex mapping, shared the Papers link, and asked whether Claude already has, or can expose, a read-only export keyed by `tasks.id` or `plan_guid` that returns only stable task fields, stable tags, and proof comments.

Claude replied with the read-only export status:

- Current endpoint base: `https://planner.koval.lan`
- Current usable reads:
  - `GET /api/tasks/{id}`
  - `GET /api/tasks/{id}/chain`
  - `GET /api/tasks/search?q=&limit=`
  - `GET /api/tasks?status=&assignee=&project=&limit=&offset=`
  - MCP tools on `POST /mcp/`: `planner_get_task`, `planner_list_tasks`, `planner_get_chain`, `planner_search`
- Current available proof-adjacent fields: task by `tasks.id`, stable tags, and parent/blocker linkage.
- Current caveat: existing reads are not proof-filtered and are not keyed by `plan_guid`.
- Planned bridge task: Claude created task `#1725`.
- Planned proof routes:
  - `GET /api/tasks/{id}/proof`
  - `GET /api/proof?plan_guid={guid}`
- Planned `/proof` fields: stable task fields plus proof comments only, including `worklog_guid`, verification comments, and delivery-notification comments.
- Explicitly omitted from `/proof`: `previous_status`, `session_id`, `context_summary`.
- Latest Claude source messages:
  - `<533fe40a6a4bed94322d08f301ef647c.claude@kovaldistillery.com>` at `Sun, 24 May 2026 14:37:11 -0500`
  - `<3a64693314bf9406f597391c35582baf.claude@kovaldistillery.com>` at `Sun, 24 May 2026 14:41:57 -0500`
- Papers proof-export update: `https://papers.koval.lan/9b30d986-1191-4629-9d17-0c84e0ae1bea`

Local live probe note: `curl --max-time 10 https://planner.koval.lan/api/tasks/1725` and `/api/tasks/1725/chain` both timed out from this workstation on 2026-05-24. Do not claim endpoint readback from Codex until connectivity works or Claude provides another reachable route.

Frank replied to the latest availability map:

- Message-ID: `<177965381868.36443.15285911562337380720@kovaldistillery.com>`
- In-Reply-To: `<3a64693314bf9406f597391c35582baf.claude@kovaldistillery.com>`
- Drafts:
  - `frank/drafts/claude-recursive-proof-endpoint-ack-2026-05-24.txt`
  - `frank/drafts/claude-recursive-proof-endpoint-ack-2026-05-24.html`

The reply confirms Codex will use `/api/tasks/{id}` and `/chain` only as read-only context for now, will not use volatile fields as proof, and will wait for `/proof` before claiming cross-system recursive proof from Planner.

## Claude Planner Proof Verifier Wired

Timestamp: 2026-05-24 15:25 CDT.

Codex now has the verifier that was listed as the next Claude bridge slice:

- standalone checker: `scripts/claude_planner_proof_check.py`
- AI Health integration: `scripts/ai_health_check.py`
- local note: `project_hub/artifacts/recursive-tools/claude-planner-proof-verifier-wired-2026-05-24.md`
- Papers: `https://papers.koval.lan/542f8733-3aef-4cde-ad65-0da61d6b9781`
- default proof URL: `https://planner.koval.lan/api/tasks/1725/proof`
- optional plan-guid proof URL: `https://planner.koval.lan/api/proof?plan_guid={guid}`

Verifier rule: only `/proof` routes count as proof. `/api/tasks/{id}` and `/chain` remain context-only.

Verification:

- `python3.13 -m py_compile scripts/claude_planner_proof_check.py scripts/ai_health_check.py` passed.
- Direct checker readback returned `status=not-ready`, `http_status=0`, reason `<urlopen error timed out>`, and forbidden fields `0`.
- AI Health dry-run now emits `claude_planner_proof=not-ready`, `claude_planner_proof_forbidden_fields=0`, and `Claude Planner proof not-ready` in the canonical status.

Next bridge condition: wait for Claude task `#1725` or Planner connectivity to make `/proof` reachable, then rerun the verifier with `--fail-on-not-ready`. Do not claim Planner proof from the current broad `/chain` endpoint.

## Claude Planner Proof Endpoint Implemented, Local Readback Blocked

Timestamp: 2026-05-24 18:40 CDT.

Frank tracked All Mail, not INBOX, contains Claude's later reply:

- Source Message-ID: `<ad6b80c98868baff10ed7e5a7b42f0b4.claude@kovaldistillery.com>`
- Date: `Sun, 24 May 2026 18:30:36 -0500`
- Subject: `Re: Recursive improvement loop comparison`

Claude says task `#1725` is complete and the Planner bridge contract is now live:

- `GET /api/tasks/{id}/proof`
- `GET /api/proof?plan_guid={guid}`
- stable fields: `id`, `title`, `status`, `project_slug`, `tags`, `plan_guid`, `worklog_guid`
- proof comments: `proof_comments`
- volatile fields excluded: `previous_status`, `session_id`, `context_summary`
- implementation commit: `1bd0314`
- worklog: `https://papers.koval.lan/c1a9312f-6468-4ec2-ba5e-b58df6bb6cd8`
- Codex Papers note: `https://papers.koval.lan/2ec5be87-f979-4768-9263-9fa3c35d6e42`
- Corrected readback Papers note: `https://papers.koval.lan/0b415627-732b-4781-a608-89252fb29d21`

Codex reran the proof verifier because Claude said task `#1725` is live:

- Command: `/usr/local/bin/python3.13 scripts/claude_planner_proof_check.py --timeout-seconds 8 --json tmp/ai-health-manager/claude-planner-proof-latest.json --report tmp/ai-health-manager/claude-planner-proof-latest.md --fail-on-not-ready`
- Checked at: `2026-05-24 18:40:52 CDT`
- Result: `status=not-ready`, `http_status=0`, reason `<urlopen error timed out>`, forbidden fields `0`.
- Output JSON: `tmp/ai-health-manager/claude-planner-proof-latest.json`
- Output report: `tmp/ai-health-manager/claude-planner-proof-latest.md`

Conclusion: treat the bridge contract as implemented on Claude's side, but do not claim Codex-side Planner proof until the `/proof` payload is reachable and passes the verifier.

## Autoresearch Source Check

Timestamp: 2026-05-24 18:57 CDT.

Robert asked to check `https://github.com/karpathy/autoresearch` as another source alongside the GitHub sources already considered.

Local read-only clone: `tmp/autoresearch-check`.

Assessment: useful as a recursive-loop operating pattern, not as code to import.

Portable ideas:

- one mutable implementation surface
- immutable verifier/evaluation surface
- fixed experiment budget
- simple canonical metric
- explicit keep/discard/crash ledger
- Markdown `program.md` as lightweight agent/org code
- simplicity criterion when deciding whether to keep an improvement

KOVAL adaptation:

- Use the pattern only inside an approved harness/worktree.
- Replace `val_bpb` with lane-specific proof metrics such as `/proof` pass/fail, AI Health status, Task Flow truth-drift count, or live readback fields.
- Replace indefinite autonomous mutation with permission-gated proposal/run loops where the mutable surface and rollback path are explicit.

Detailed note: `project_hub/artifacts/recursive-tools/autoresearch-source-review-2026-05-24.md`.

Papers: `https://papers.koval.lan/e1b5946c-f8fb-40b8-9345-d29451278e8d`.

Expanded Papers note after Robert's clarification that autoresearch should be mined for concrete ideas: `https://papers.koval.lan/87076e7c-6c90-4b84-aa0b-ffc1392ff14e`.

## Recursive Experiment Harness Implementation Plan

Timestamp: 2026-05-24 19:07 CDT.

Robert asked for a full implementation plan to Papers and a Tuesday OPS task for after Claude enables Planner access.

- Local plan: `project_hub/artifacts/recursive-tools/recursive-experiment-harness-implementation-plan-2026-05-24.md`
- Papers plan: `https://papers.koval.lan/1cd480c5-6d62-4589-8592-97d77343e781`
- Final Papers copy with OPS task id: `https://papers.koval.lan/d7c535a6-3b9e-41d3-8474-961c8c4da2c0`
- Confirmed Papers copy: `https://papers.koval.lan/7f76ab59-6627-44d4-8248-882076566d2d`
- OPS task: `370208`
- Due: `2026-05-26`
- Title: `Implement recursive experiment harness after Planner proof access`
- Owner/assignee: Codex user `1332`
- Creator: Robert/admin user `1`
- Notifications: suppressed

Task dependency: wait for Claude task `#1726` to enable Codex access to Planner `/proof` or provide an approved reachable read-only route. If still unavailable on Tuesday, run only the local truth-drift baseline dry pilot.

## Planner Proof Explicit Resolve Check

Timestamp: 2026-05-24 19:10 CDT.

Claude replied that task `#1726` is ready for review. Root cause from Claude: pfSense DNS returns stale `planner.koval.lan -> 192.168.55.9`; expected host is `192.168.55.205`.

Codex did not edit `/etc/hosts` because that is a system path outside `/Users/werkstatt` and needs explicit approval. A non-mutating `curl --resolve planner.koval.lan:443:192.168.55.205` check returned HTTP `200` for `https://planner.koval.lan/api/tasks/1725/proof`.

Validation against `scripts/claude_planner_proof_check.py` rules passed:

- status: `passed`
- task_id: `1725`
- status_value: `done`
- plan/worklog GUIDs present
- proof_comment_count: `1`
- forbidden_fields: `0`

Artifacts:

- `project_hub/artifacts/recursive-tools/claude-planner-proof-explicit-resolve-2026-05-24.md`
- `tmp/ai-health-manager/planner-proof-curl-resolve-2026-05-24.json`
- `tmp/ai-health-manager/claude-planner-proof-resolve-latest.json`
- `tmp/ai-health-manager/claude-planner-proof-resolve-latest.md`

Durable access was accepted through the workstation `/etc/hosts` path. After Robert corrected the mapping, `planner.koval.lan` resolved to `192.168.55.205`, direct curl returned HTTP `200`, and the canonical verifier passed:

- checked_at: `2026-05-24 19:19:27 CDT`
- status: `passed`
- http_status: `200`
- proof_comment_count: `1`
- forbidden_fields: `0`

Frank sent Claude `DONE` for task `#1726`:

- Outbound Message-ID: `<177966837736.631.1728653542409716614@kovaldistillery.com>`
- In-Reply-To: `<a1cd0029dcd79e75d6e331ea71565518.claude@kovaldistillery.com>`

## Tuesday Start Context

Timestamp: 2026-05-24 19:28 CDT.

Robert asked to preserve the explanation of what today's recursive scripts already do and how this helps Codex and Claude work together.

- Local note: `project_hub/artifacts/recursive-tools/recursive-stack-tuesday-start-context-2026-05-24.md`
- Papers: `https://papers.koval.lan/c6d75317-97bd-4e12-aa24-ed48edf4f99a`

Summary: Tuesday's work should wrap today's first-generation recursive scripts (`recursive_proposal_queue.py`, `recursive_proposal_decisions.py`, `recursive_proposal_executor.py`, `task_flow_truth_drift_check.py`, `service_parity_check.py`, and `claude_planner_proof_check.py`) into the autoresearch-style harness. The Codex-Claude cooperation model is now proof-backed: Claude owns Planner-side tasks and worklogs; Codex verifies completion through Planner `/proof` and turns local gaps into bounded recursive proposals or harness attempts.
