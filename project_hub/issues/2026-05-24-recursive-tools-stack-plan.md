# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260524-RECURSIVE-TOOLS-01`
- Date Opened: 2026-05-24
- Date Completed:
- Owner: Robert / Codex
- Priority: medium
- Status: in progress

## Scope

Assess whether recursive tooling belongs in the Codex stack, publish a durable recommendation, notify Robert and Sonat with the live Papers record, set up a first `recursive-improve` pilot sandbox, and create OPS follow-up tasks for the next few days.

## Decision

- Treat recursive tooling as an improvement lane, not a default execution mode for live operational work.
- Pull structured planning/refactor patterns from `useful-codex-skills` first.
- Use `recursive-improve` as the first contained sandbox test.
- Hold `recursive-codex` for a later UI-only evaluation rather than making it part of the default stack now.

## Initial Plan

1. Write the local durable assessment and publish it to Papers.
2. Send Robert and Sonat one Frank-routed status email with the full Papers link.
3. Create Codex-owned silent OPS tasks for the near-term follow-up slices.
4. Clone and install `recursive-improve` into a repo-local sandbox and capture the exact environment/result.
5. Record the resulting paths, task ids, and next-step notes in `HANDOFF.md` and this project note.

## Repo Logs

### ai_workspace

- Repo Log ID:
- Commit SHA:
- Commit Date:
- Change Summary: Added a durable recursive-tools assessment, a project-hub execution note, and follow-up records for Papers, Frank reporting, OPS tasks, and the first local pilot sandbox.

## Verification Notes

- The upstream recommendation basis is split across three repositories: `grp06/useful-codex-skills`, `kayba-ai/recursive-improve`, and `grp06/recursive-codex`.
- The AI Manager durable-input trail for this request is recorded in `koval_crm.ai_manager_inputs` rows `2113` and `2114` and in `daily-inputs/2026-05-24.md`.
- Live Papers publish succeeded: GUID `601a7e00-ad29-4bd8-bd47-aac20f2e998a`, path `ai-manager/durability/2026-05-24-recursive-tools-stack-assessment.md`, URL `https://papers.koval.lan/601a7e00-ad29-4bd8-bd47-aac20f2e998a`.
- Detailed Python migration Papers publish also succeeded: GUID `0f5cd8f1-7160-412d-948c-2e5bf2e5ce67`, path `ai-manager/durability/2026-05-24-python-3-13-migration-assessment.md`, URL `https://papers.koval.lan/0f5cd8f1-7160-412d-948c-2e5bf2e5ce67`.
- Local sandbox clones now exist at `sandboxes/recursive-improve` and `sandboxes/useful-codex-skills`.
- Repo-local `recursive-improve` setup now exists at `sandboxes/recursive-improve/.venv`; `recursive-improve init` completed in `sandboxes/recursive-improve-pilot-target`, creating `program.md`, `eval/traces/`, and the generated `.claude/skills` plus `.agents/skills` entries.
- Preferred runtime setup now also exists at `sandboxes/recursive-improve/.venv313`, built from `/usr/local/bin/python3.13`; `recursive-improve init` completed in `sandboxes/recursive-improve-pilot-target-313`, and the same base CLI smoke passed there.
- First real recursive test assets now exist in `sandboxes/recursive-improve-pilot-target-313`: `toy_agent.py`, `generate_test_traces.py`, generated trace JSON under `eval/traces/`, and evaluator outputs `eval/eval_results.json` plus `eval/benchmark_results.json`.
- CLI smoke proof from the pilot target:
  - `recursive-improve ratchet status --config program.md --eval-dir eval` returned a clean zero-iteration status object.
  - `recursive-improve benchmark -o eval list` returned `No benchmarks stored yet.`
- First real recursive-test readback on the 3.13 path:
  - sequential `recursive-improve eval eval/traces -o eval` evaluated `3` traces
  - `clean_success_rate = 66.7% (2/3)`
  - `error_rate = 0.0%`
  - first labeled benchmark `toy-smoke-2026-05-24` returned run id `0165fa1055e2` and score `9.5%`
- Compatibility note: upstream declares `requires-python >=3.12`. A temporary Python `3.9.6` smoke path exists from the earlier override install, but the preferred path is now the explicit Python `3.13.13` venv.
- Non-break proof for current automation: `python3 -m py_compile` still passed for the key AI Workspace and Workspaceboard health/task-flow scripts, and the default shell `python3` still resolves to `/usr/bin/python3` rather than the Homebrew interpreter.
- Silent Codex-owned OPS follow-up tasks were created and are now complete with live readback:
  - `370194` `Recursive-improve pilot smoke run and trace note` now `Completed`, `sendnotification=0`
  - `370195` `Pull useful-codex-skills patterns into local workflow` now `Completed`, `sendnotification=0`
  - `370196` `Decide whether recursive-codex merits a UI pilot` now `Completed`, `sendnotification=0`
- Dated Python migration OPS tasks were created with live readback:
  - `370198` `Python 3.13 migration inventory for ai_workspace and workspaceboard` due `2026-05-24`
  - `370199` `First low-risk Python 3.13 lane migration` due `2026-05-25`
- First low-risk lane migration is now complete for `scripts/papers_write_note.py`. The script is pinned to `#!/usr/local/bin/python3.13`, made executable for wrapper compatibility, and the Papers write path verified live with GUID `470bc2fa-7456-4252-ae47-9183af53cf6e`.
- Two additional low-risk lane migrations are now complete: `scripts/email_trace_recorder.py` with real event-log proof under `tmp/email-trace-python313-smoke/email-trace-events.jsonl`, and `scripts/send_codex_ops_email.py` with a successful 3.13 dry-run render. The real inventory now reads `env-python3 = 34`, `pinned-python3.13 = 3`, and recommends `scripts/backfill_email_trace.py` as the next bounded target.
- Frank owner-facing email send is complete. Frank sent `Recursive tools assessment and first pilot setup` to Robert with Sonat copied under Message-ID `<177962947005.14534.4346315973907816580@kovaldistillery.com>`, task id `frank-recursive-tools-stack-assessment-2026-05-24`, and sent-log proof in `/Users/admin/.frank-launch/state/sent-log.jsonl`.
- Recursive recommendation-quality benchmark is now in place under the 3.13 pilot target:
  - agent: `sandboxes/recursive-improve-pilot-target-313/recommendation_benchmark_agent.py`
  - runner: `sandboxes/recursive-improve-pilot-target-313/run_recommendation_benchmark.py`
  - durable note: `project_hub/artifacts/recursive-tools/recursive-recommendation-benchmark-2026-05-24.md`
  - eval output: `sandboxes/recursive-improve-pilot-target-313/eval/recommendation-benchmark/eval_results.json`
  - eval run id: `7596f83f91ec`
  - benchmark run id: `b3d095e7b2e4`
  - readback: `trace_count=5`, `clean_success_rate=100.0% (5/5)`
  - scenario classes: `cleanup-already-in-flight`, `truth-drift-needs-repair`, `parity-drift-first`, `registry-contract-broken`, `architecture-stable-benchmark-next`
- Live recursive recommendation snapshot is now also in place:
  - runner: `sandboxes/recursive-improve-pilot-target-313/run_live_recommendation_snapshot.py`
  - durable note: `project_hub/artifacts/recursive-tools/recursive-live-recommendation-snapshot-2026-05-24.md`
  - eval output: `sandboxes/recursive-improve-pilot-target-313/eval/live-recommendation-benchmark/eval_results.json`
  - eval run id: `cde619b65fda`
  - benchmark run id: `bc145700f885`
  - readback: `trace_count=1`, `clean_success_rate=100.0% (1/1)`
  - current live recommendation: `repair-truth-drift`
  - current live driver: `active_missing_board_session` on `salesreport-coteam-bonus-pioneer-date-filter-2026-05-05`
- Historical recommendation-quality corpus is now in place:
  - cases: `sandboxes/recursive-improve-pilot-target-313/recommendation_historical_cases.json`
  - runner: `sandboxes/recursive-improve-pilot-target-313/run_historical_recommendation_benchmark.py`
  - durable note: `project_hub/artifacts/recursive-tools/recursive-historical-recommendation-benchmark-2026-05-24.md`
  - eval output: `sandboxes/recursive-improve-pilot-target-313/eval/historical-recommendation-benchmark/eval_results.json`
  - eval run id: `305f1b72f49c`
  - benchmark run id: `3b31329dcd91`
  - readback: `trace_count=6`, `clean_success_rate=100.0% (6/6)`
  - current autonomy recommendation: build an approval-gated proposal queue before any automatic repair execution
- Approval queue ownership is now defined and published:
  - Frank owns the Robert-facing yes/no decision loop.
  - Codex generates proposal packets and executes only approved low-risk fixes.
  - Papers URL: `https://papers.koval.lan/89b2ac72-7476-4962-ad27-2b409a89554e`
  - local source: `project_hub/artifacts/recursive-tools/recursive-autonomy-approval-queue-2026-05-24.md`
- Claude comparison email is sent:
  - Corrected To: `claude@kovaldistillery.com`
  - Cc: `robert@kovaldistillery.com`
  - Subject: `Recursive improvement loop comparison`
  - Message-ID: `<177964800446.11583.9902601401452484732@kovaldistillery.com>`
  - Task id: `frank-claude-recursive-improvement-comparison-2026-05-24-corrected`
  - Supersedes earlier send to `claude@koval-distillery.com` under Message-ID `<177964786970.11134.2806295771480830949@kovaldistillery.com>`.
- Proposal queue implementation is now in place:
  - generator: `scripts/recursive_proposal_queue.py`
  - queue log: `project_hub/artifacts/recursive-tools/recursive-proposal-queue.jsonl`
  - first proposal: `recursive-proposal-20260524-134350-repair-truth-drift`
  - proposal artifact: `project_hub/artifacts/recursive-tools/proposals/recursive-proposal-20260524-134350-repair-truth-drift.md`
  - Frank approval email sent to Robert under Message-ID `<177964828163.12510.14353964488768279452@kovaldistillery.com>`
  - execution is pending Robert's yes/no reply.
- Proposal email template was improved after Robert replied and corrected readability/context:
  - `scripts/recursive_proposal_queue.py` now emits richer plain-text and separate HTML approval bodies.
  - upgraded current HTML body: `frank/drafts/recursive-proposals/recursive-proposal-20260524-134350-repair-truth-drift.html`
  - dry-run through Frank rendered successfully.
  - fresh queue readback generated `recursive-proposal-20260524-134813-monitor-recursive-lane` with `approval_required=false`, `service_parity_drift=0`, and `truth_drift_count=0`.
- Proposal decision/state recording is now in place:
  - recorder: `scripts/recursive_proposal_decisions.py`
  - decision log: `project_hub/artifacts/recursive-tools/recursive-proposal-decisions.jsonl`
  - Papers addendum: `https://papers.koval.lan/99336886-09d1-4a6d-b09d-f43093344bcd`
  - Changed stack Papers version sent to Claude: `https://papers.koval.lan/346f243c-b610-489c-8323-627df9ca9f8d`
  - Claude follow-up sent by Frank: Message-ID `<177964923221.16079.8878460685095716018@kovaldistillery.com>`
  - status command: `./scripts/recursive_proposal_decisions.py status --json`
  - decision command: `./scripts/recursive_proposal_decisions.py record-decision --proposal-id latest-pending --decision yes|no|unclear --source-message-id '<reply-message-id>' --notes '<non-secret note>'`
  - reconcile command: `./scripts/recursive_proposal_decisions.py reconcile-clean-monitor`
  - current readback: `pending_approval_count=0`; the original `repair-truth-drift` proposal is `superseded_by_clean_monitor` by `recursive-proposal-20260524-134813-monitor-recursive-lane`.
- Approved execution runner is now in place:
  - executor: `scripts/recursive_proposal_executor.py`
  - execution log: `project_hub/artifacts/recursive-tools/recursive-proposal-executions.jsonl`
  - Papers v3: `https://papers.koval.lan/89f95776-d0d4-47e2-94fc-c48064355ec2`
  - status command: `./scripts/recursive_proposal_executor.py status --json`
  - execution command: `./scripts/recursive_proposal_executor.py execute --proposal-id latest-approved --json`
  - live mutation gate: `--allow-live-mutation`
  - current readback: `approved_unexecuted_count=0`
  - allowlisted classes: `no-op-monitoring`, `registry-metadata-fix`, `recommendation-corpus-fix`, `source-runtime-parity-fix`, `truth-drift-single-item-repair`
  - caveat: `truth-drift-single-item-repair` currently records a blocker without a proposal-specific mutator; it does not run broad live Task Flow mutation.
  - Claude executor update sent by Frank: Message-ID `<177964957514.17815.13480250926490834788@kovaldistillery.com>`
- AI Health integration is now wired:
  - implementation: `scripts/ai_health_check.py`
  - decision: no separate recursive LaunchDaemon right now; use the existing AI Health cadence so recursive status cannot become a separate lost poller.
  - latest artifact: `tmp/ai-health-manager/latest.md`
  - Papers update: `https://papers.koval.lan/f95e7f60-fda6-495c-a485-b2c66ff29110`
  - latest live readback after scheduled run: `recursive_proposals=passed`, `pending=0`, `approved_unexecuted=0`, `blocked=0`.
  - important hardening: even board-down reports now include `recursive_proposals`; latest observed board state was `board down; status check failed: status endpoint failed: timed out`, but recursive status still showed `passed`.
  - current boundary: this is monitoring/visibility for the recursive queue, not continuous auto-generation or ungated live mutation.
- Claude Planner schema mapping is now ingested:
  - source Message-ID: `<62e95dd42623af2de8449e4c56816ac2.claude@kovaldistillery.com>`
  - local note: `project_hub/artifacts/recursive-tools/claude-planner-recursive-schema-2026-05-24.md`
  - Papers: `https://papers.koval.lan/1e7119d3-e2cc-4ff0-900f-d1251eaa5f0a`
  - mapped proof anchors: `plan_guid`, `worklog_guid`, stable `task_tags`, tester verification comments, delivery notification comments, and incident/crash tags for revert-required states.
  - explicit unstable fields to avoid: `previous_status`, `session_id`, `context_summary`.
  - Frank reply sent to Claude on the same thread under Message-ID `<177965118899.26351.4879639112037777951@kovaldistillery.com>`.
- Claude read-only export follow-up is now ingested:
  - source Message-IDs: `<533fe40a6a4bed94322d08f301ef647c.claude@kovaldistillery.com>` and `<3a64693314bf9406f597391c35582baf.claude@kovaldistillery.com>`.
  - current usable reads: `GET /api/tasks/{id}` and `GET /api/tasks/{id}/chain` on `https://planner.koval.lan`, plus search/list and Planner MCP tools.
  - current usable stable pieces: task by id, stable tags, parent/blocker linkage.
  - planned proof task: Claude Planner task `#1725`, active with `developer-agent`.
  - planned routes: `GET /api/tasks/{id}/proof` and `GET /api/proof?plan_guid={guid}`.
  - Papers update: `https://papers.koval.lan/9b30d986-1191-4629-9d17-0c84e0ae1bea`
  - local blocker: Codex curl probes to `https://planner.koval.lan/api/tasks/1725` and `/chain` timed out from this workstation.

## Rollback Plan

- If the pilot proves noisy or low-signal, keep the durable assessment and OPS tasks but remove the local sandbox without changing any live operational runtime.
- Do not promote recursive tooling into owner-visible lanes until a later approval-backed follow-up says to do so.

## Follow-Ups

- Revisit `recursive-codex` only if a UI repo later needs an explicit screenshot-feedback-edit loop.
- Next autonomy slice: add proposal-specific mutators for one low-risk approved fix class, then add keep/revert recording after execution proof. Start with a non-live or low-risk class such as `recommendation-corpus-fix` or `registry-metadata-fix`; defer broad Task Flow truth-drift mutation until a single-item mutator has exact source/readback proof.
- Next Claude bridge slice: the Codex-side schema verifier has been added at `scripts/claude_planner_proof_check.py` and wired into `scripts/ai_health_check.py`. It reports `claude_planner_proof=not-ready` until `/api/tasks/1725/proof` or `/api/proof?plan_guid={guid}` is reachable and clean. Do not claim Planner proof from the current broad `/chain` endpoint.
