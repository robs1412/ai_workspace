# Recursive-Improve Pilot Setup

- Recorded: 2026-05-24 08:24 CDT
- Sandbox root: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve`
- Pilot target: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target`

## What Landed

- Cloned upstream `kayba-ai/recursive-improve` into the local sandbox.
- Cloned upstream `grp06/useful-codex-skills` into the local sandbox for pattern review.
- Created a repo-local virtual environment at `sandboxes/recursive-improve/.venv`.
- Created a Python 3.13 repo-local virtual environment at `sandboxes/recursive-improve/.venv313`.
- Installed `recursive-improve` into that venv with `pip install --ignore-requires-python -e .`.
- Installed `recursive-improve` into the 3.13 venv with a normal editable install.
- Ran `recursive-improve init` from `sandboxes/recursive-improve-pilot-target`.
- Ran `recursive-improve init` from `sandboxes/recursive-improve-pilot-target-313`.

## Smoke Proof

- `recursive-improve init` created:
  - `.claude/skills/recursive-improve/SKILL.md`
  - `.claude/skills/ratchet/SKILL.md`
  - `.claude/skills/benchmark/SKILL.md`
  - `.claude/skills/evolve/SKILL.md`
  - matching `.agents/skills/...` entries
  - `program.md`
  - `eval/traces/`
- `recursive-improve ratchet status --config program.md --eval-dir eval` returned a clean zero-iteration status object.
- `recursive-improve benchmark -o eval list` returned `No benchmarks stored yet.`
- The same smoke passed again under the explicit 3.13 venv in `sandboxes/recursive-improve-pilot-target-313`.

## First Recursive Test Pass

The first real local recursive test pass now exists under:

- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/toy_agent.py`
- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/generate_test_traces.py`

Generated traces:

- `eval/traces/inventory-fast-path.json`
- `eval/traces/global-relink-too-early.json`
- `eval/traces/explicit-venv-migration.json`

Evaluator artifacts:

- `eval/eval_results.json`
- `eval/benchmark_results.json`

Readback from the first sequential eval:

- `trace_count = 3`
- `clean_success_rate = 66.7% (2/3)`
- `error_rate = 0.0%`
- `give_up_rate = 0.0%`
- `duration_outlier = 0.0%`

First labeled benchmark:

- label: `toy-smoke-2026-05-24`
- run id: `0165fa1055e2`
- score: `9.5%`

Important note:

- the first parallel eval attempt ran before traces were fully written and returned `Evaluated 0 traces`; the sequential rerun used for the real readback succeeded and is the authoritative result

## First Real Lane Migration

The first low-risk migration target from the real inventory run is now implemented:

- target: `/Users/werkstatt/ai_workspace/scripts/papers_write_note.py`
- change: shebang pinned from `#!/usr/bin/env python3` to `#!/usr/local/bin/python3.13`
- follow-through: file mode updated to executable so wrapper-based direct execution still works

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/papers_write_note.py`
- dry-run write path succeeded through `scripts/mcp_runtime_env.py exec -- /Users/werkstatt/ai_workspace/scripts/papers_write_note.py ... --dry-run`
- live write path succeeded through the same wrapper and created Papers GUID `470bc2fa-7456-4252-ae47-9183af53cf6e`

## Additional Low-Risk Lane Migrations

Two more standalone helpers now use explicit Python 3.13:

- `/Users/werkstatt/ai_workspace/scripts/email_trace_recorder.py`
- `/Users/werkstatt/ai_workspace/scripts/send_codex_ops_email.py`

Verification:

- `email_trace_recorder.py`
  - `/usr/local/bin/python3.13 -m py_compile`
  - real smoke event written to `/Users/werkstatt/ai_workspace/tmp/email-trace-python313-smoke/email-trace-events.jsonl`
  - event row shows `db_write_ok: true`
- `send_codex_ops_email.py`
  - `/usr/local/bin/python3.13 -m py_compile`
  - dry-run render succeeded with temp local creds/body files

Inventory shift after the three low-risk migrations:

- `env-python3`: `37 -> 34`
- `pinned-python3.13`: `0 -> 3`
- next recommended target from the real inventory run: `/Users/werkstatt/ai_workspace/scripts/backfill_email_trace.py`

## Fourth Low-Risk Lane Migration

One more standalone helper now uses explicit Python 3.13:

- `/Users/werkstatt/ai_workspace/scripts/backfill_email_trace.py`

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/backfill_email_trace.py`
- runtime proof: `/usr/local/bin/python3.13 /Users/werkstatt/ai_workspace/scripts/backfill_email_trace.py --days 0 --owner-only`
- recent readback rows landed in:
  - `/Users/admin/.nationaloutreach-launch/state/email-trace-events.jsonl`
  - `/Users/admin/.avignon-launch/state/email-trace-events.jsonl`
  - `/Users/admin/.frank-launch/state/email-trace-events.jsonl`
- sample rows show `db_write_ok: true`

Inventory shift after the fourth low-risk migration:

- `env-python3`: `34 -> 33`
- `pinned-python3.13`: `3 -> 4`
- next recommended target from the real inventory run: `/Users/werkstatt/ai_workspace/scripts/backfill_header_worker_seen.py`

Recursive-improve readback after the refreshed real inventory pass:

- `eval/real-inventory/eval_results.json`
- run id: `62c78e04ac1b`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

Important correction:

- the inventory counts were already correct after the `backfill_email_trace.py` migration
- the stale behavior was only in the recommendation logic, which had been hardcoded to the first four helper scripts
- the pilot inventory agent now falls back to a generic helper-first heuristic once those four initial targets are exhausted

## Fifth Low-Risk Lane Migration

One more standalone helper now uses explicit Python 3.13:

- `/Users/werkstatt/ai_workspace/scripts/backfill_header_worker_seen.py`

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/backfill_header_worker_seen.py`
- bounded smoke run:
  - `/usr/local/bin/python3.13 /Users/werkstatt/ai_workspace/scripts/backfill_header_worker_seen.py --worker asher --state-dir /Users/werkstatt/ai_workspace/tmp/backfill-header-worker-seen-smoke --email-account asher@kovaldistillery.com`
- local smoke log:
  - `/Users/werkstatt/ai_workspace/tmp/backfill-header-worker-seen-smoke/email-trace-events.jsonl`
- recorded smoke row shows `db_write_ok: true`

Inventory shift after the fifth low-risk migration:

- `env-python3`: `33 -> 32`
- `pinned-python3.13`: `4 -> 5`
- next recommended target from the real inventory run: `/Users/werkstatt/ai_workspace/scripts/backfill_nationaloutreach_email_trace.py`

Recursive-improve readback after the second refreshed real inventory pass:

- `eval/real-inventory/eval_results.json`
- run id: `5733a3942f7f`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

## Sixth Low-Risk Lane Migration

One more standalone helper now uses explicit Python 3.13:

- `/Users/werkstatt/ai_workspace/scripts/backfill_nationaloutreach_email_trace.py`

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/backfill_nationaloutreach_email_trace.py`
- bounded smoke run:
  - `/usr/local/bin/python3.13 /Users/werkstatt/ai_workspace/scripts/backfill_nationaloutreach_email_trace.py --state-dir /Users/werkstatt/ai_workspace/tmp/backfill-nationaloutreach-email-trace-smoke`
- local smoke log:
  - `/Users/werkstatt/ai_workspace/tmp/backfill-nationaloutreach-email-trace-smoke/email-trace-events.jsonl`
- recorded smoke rows show `db_write_ok: true` for:
  - `email_reviewed`
  - `email_archived`
  - `email_resolved_not_in_inbox`

Smoke run readback:

- `reviewed_backfilled = 2`
- `archived_backfilled = 1`
- `resolved_backfilled = 1`
- `active_inbox_records = 2`

Inventory shift after the sixth low-risk migration:

- `env-python3`: `32 -> 31`
- `pinned-python3.13`: `5 -> 6`
- next recommended target from the real inventory run: `/Users/werkstatt/ai_workspace/scripts/analyze_redistill_email_export.py`

Recursive-improve readback after the third refreshed real inventory pass:

- `eval/real-inventory/eval_results.json`
- run id: `99dbbf7cf10c`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

## Seventh Low-Risk Lane Migration

One more standalone helper now uses explicit Python 3.13:

- `/Users/werkstatt/ai_workspace/scripts/analyze_redistill_email_export.py`

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/analyze_redistill_email_export.py`
- bounded smoke run:
  - `/usr/local/bin/python3.13 /Users/werkstatt/ai_workspace/scripts/analyze_redistill_email_export.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --output /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke/report.md --workers 2`
- smoke readback:
  - `Wrote /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke/report.md`
  - `Records: 2`
  - `Sent: 1`
  - `Received: 1`

## Next Five Automatic Migrations

The next five helper-tier scripts were migrated in one bounded batch after Robert requested automatic looping unless an error appeared:

- `/Users/werkstatt/ai_workspace/scripts/ertc_discovery_export.py`
- `/Users/werkstatt/ai_workspace/scripts/ertc_gmail_direct_export.py`
- `/Users/werkstatt/ai_workspace/scripts/gmail_export.py`
- `/Users/werkstatt/ai_workspace/scripts/gmail_extract_attachments.py`
- `/Users/werkstatt/ai_workspace/scripts/google_docs_export.py`

Verification:

- all five passed `/usr/local/bin/python3.13 -m py_compile`
- argument-path / bounded proof:
  - `ertc_discovery_export.py --help`
  - `ertc_gmail_direct_export.py --help`
  - `gmail_export.py --help`
  - `gmail_extract_attachments.py --input /Users/werkstatt/ai_workspace/tmp/gmail-attachments-smoke --output /Users/werkstatt/ai_workspace/tmp/gmail-attachments-smoke-out`
  - `google_docs_export.py scan /Users/werkstatt/ai_workspace/tmp/google-doc-export-smoke --limit 10`

Bounded smoke readback:

- Gmail attachment extraction:
  - `messages_scanned = 1`
  - `attachments_saved = 1`
  - `signature_inline_files_skipped = 0`
  - summary: `/Users/werkstatt/ai_workspace/tmp/gmail-attachments-smoke-out/attachments-summary.json`
- Google Docs pointer scan:
  - found `2` pointer files
  - mapped:
    - `subdir/sample.gdoc -> subdir/sample.txt`
    - `subdir/sheet.gsheet -> subdir/sheet.csv`

Inventory shift after the sixth migration plus the five-script automatic batch:

- `env-python3`: `31 -> 25`
- `pinned-python3.13`: `6 -> 12`
- next recommended target from the real inventory run: `/Users/werkstatt/ai_workspace/scripts/redistill_email_quality_report.py`

Recursive-improve readback after the batch refresh:

- `eval/real-inventory/eval_results.json`
- run id: `e02f27b8ed6e`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

## Safe Eight Batch

The next safe eight helper-tier scripts were migrated in one bounded batch:

- `/Users/werkstatt/ai_workspace/scripts/redistill_email_quality_report.py`
- `/Users/werkstatt/ai_workspace/scripts/redistill_extended_reports.py`
- `/Users/werkstatt/ai_workspace/scripts/redistill_full_email_work_report.py`
- `/Users/werkstatt/ai_workspace/scripts/redistill_job_work_report.py`
- `/Users/werkstatt/ai_workspace/scripts/redistill_march_april_deep_dive.py`
- `/Users/werkstatt/ai_workspace/scripts/redistill_true_work_report.py`
- `/Users/werkstatt/ai_workspace/scripts/redistill_workload_report.py`
- `/Users/werkstatt/ai_workspace/scripts/ai_transfer_fetch.py`

Verification:

- all eight passed `/usr/local/bin/python3.13 -m py_compile`
- bounded smoke / argument-path proof:
  - `redistill_extended_reports.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --output /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke/report_extended.md --chunk-size 10 --chunk-timeout 5`
  - `redistill_job_work_report.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --chunk-size 10 --chunk-timeout 5`
  - `redistill_email_quality_report.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --chunk-size 10 --chunk-timeout 5`
  - `redistill_true_work_report.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --chunk-size 10 --chunk-timeout 5`
  - `redistill_workload_report.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --chunk-size 10 --chunk-timeout 5`
  - `redistill_full_email_work_report.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --start 2026-01-01 --end 2026-12-31 --output-prefix smoke_full_email_work --body-workers 2 --chunk-size 10 --chunk-timeout 5`
  - `redistill_march_april_deep_dive.py --root /Users/werkstatt/ai_workspace/tmp/redistill-export-smoke --chunk-size 10 --chunk-timeout 5`
  - `ai_transfer_fetch.py --help`

Bounded smoke readback:

- every `redistill_*` smoke run completed with `Records=2 skipped=0 errors=0`
- generated smoke artifacts under `/Users/werkstatt/ai_workspace/tmp/redistill-export-smoke`, including:
  - `report_extended.md`
  - `report_job_work.md`
  - `report_email_quality.md`
  - `report_true_work.md`
  - `report_workload.md`
  - `report_smoke_full_email_work.md`
  - `report_march_april_deep_dive.md`
- `ai_transfer_fetch.py` passed real argument-path execution and rendered the expected usage text

Inventory shift after the safe eight batch:

- `env-python3`: `25 -> 17`
- `pinned-python3.13`: `12 -> 20`
- next recommended target from the real inventory run: `/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py`

Recursive-improve readback after the batch refresh:

- `eval/real-inventory/eval_results.json`
- run id: `41f297bc2912`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

## Controlled Runtime Batch

The first shared-runtime batch was kept narrow and completed without error:

- `/Users/werkstatt/ai_workspace/scripts/ai_worker_mailbox_setup.py`
- `/Users/werkstatt/ai_workspace/scripts/mcp_runtime_env.py`
- `/Users/werkstatt/ai_workspace/scripts/secure_info_intake.py`
- `/Users/werkstatt/ai_workspace/scripts/shared_task_flow.py`

Verification:

- all four passed `/usr/local/bin/python3.13 -m py_compile`
- bounded proof:
  - `ai_worker_mailbox_setup.py --help`
  - local credential-parse probe against `/Users/werkstatt/ai_workspace/tmp/runtime-migration-smoke/mailbox-creds.txt`
  - `mcp_runtime_env.py --local-env /Users/werkstatt/ai_workspace/tmp/runtime-migration-smoke/mcp.env status`
  - `shared_task_flow.build_packet(...)` import/probe check
  - `secure_info_intake.py --source-system other --owner smoke --tag python313 --notes 'smoke dry run' --dry-run`

Bounded smoke readback:

- `ai_worker_mailbox_setup.py`
  - parsed temp credentials to `smoke@example.com`, `imap.example.com`, `smtp.example.com`
- `mcp_runtime_env.py`
  - returned `ok: true`
  - both required keys present from local temp env
  - local temp env mode read back as `0o600`
- `shared_task_flow.py`
  - built packet with status `captured`
  - emitted a deterministic `dedupe_key`
  - applied owner-visible SLA defaults `120` / `300`
- `secure_info_intake.py`
  - dry-run returned `ingested: 1`
  - projected archive/processed/metadata paths without moving the file
  - temporary inbox smoke file was removed after verification

Inventory shift after the controlled runtime batch:

- `env-python3`: `16 -> 12`
- `pinned-python3.13`: `21 -> 25`
- next recommended target from the real inventory run: `/Users/werkstatt/ai_workspace/scripts/run_ai_box_backup_daily_task.py`

Recursive-improve readback after the runtime batch refresh:

- `eval/real-inventory/eval_results.json`
- run id: `05e4a0dcd747`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

## Ops-Coupled Follow-Through

One more ops-coupled helper now uses explicit Python 3.13:

- `/Users/werkstatt/ai_workspace/scripts/run_ai_box_backup_daily_task.py`

Verification stayed non-destructive by design:

- `/usr/local/bin/python3.13 -m py_compile scripts/run_ai_box_backup_daily_task.py`
- function-level logic probe only:
  - `parse_key_value_output(...)`
  - `compute_next_due(...)` for daily / weekly / monthly / annual recurrence

Bounded readback:

- parsed sample backup output into:
  - `backup`
  - `remote_push_status`
  - `warning_email_status`
  - `warning_email_message_id`
- recurring-date probe returned:
  - daily -> `2026-05-25`
  - weekly -> `2026-05-27`
  - monthly -> `2026-06-20`
  - yearly -> `2027-05-20`

Important limitation:

- `main()` was intentionally not run because it can execute the live backup shell path and advance live OPS recurring task `369899`

Inventory shift after this follow-through:

- `env-python3`: `12 -> 11`
- `pinned-python3.13`: `25 -> 26`
- next recommended target from the real inventory run: none automatically selected

Recursive-improve readback after the refresh:

- `eval/real-inventory/eval_results.json`
- run id: `9a3af06a73c5`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

Current interpretation:

- the helper-first migration lane is exhausted
- remaining repo-local `env-python3` entrypoints are now shared-runtime or installed-runtime mirrors:
  - `ai_health_check.py`
  - `email_worker_header_poll.py`
  - `email_worker_threads.py`
  - `mailbox_imap_helpers.py`
  - `nationaloutreach_mail_cycle.py`
  - `task_flow_due_runner.py`
  - `task_flow_papers_project.py`
  - `workspaceboard/scripts/health/ai_health_check.py`
  - related remaining workspaceboard/runtime mirrors

## Final Runtime Drain

The remaining `env-python3` entrypoints in the bounded scan are now migrated:

- `/Users/werkstatt/ai_workspace/scripts/email_worker_threads.py`
- `/Users/werkstatt/ai_workspace/scripts/mailbox_imap_helpers.py`
- `/Users/werkstatt/ai_workspace/scripts/task_flow_due_runner.py`
- `/Users/werkstatt/ai_workspace/scripts/ai_health_check.py`
- `/Users/werkstatt/ai_workspace/scripts/email_worker_header_poll.py`
- `/Users/werkstatt/ai_workspace/scripts/nationaloutreach_mail_cycle.py`
- `/Users/werkstatt/workspaceboard/scripts/planner/shared_task_flow.py`
- `/Users/werkstatt/workspaceboard/scripts/planner/task_flow_due_runner.py`
- `/Users/werkstatt/workspaceboard/scripts/planner/task_flow_papers_project.py`
- `/Users/werkstatt/workspaceboard/scripts/health/ai_health_check.py`

Verification:

- all remaining Python entrypoints passed `/usr/local/bin/python3.13 -m py_compile`
- bounded helper/runtime proof:
  - `email_worker_threads.py` import/probe for subject normalization and status suffix detection
  - `mailbox_imap_helpers.py` import/probe for message-id normalization and sender parsing
  - `task_flow_due_runner.py --dry-run --limit 5 --scheduler-limit 5`
  - `ai_health_check.py --dry-run` with a widened `--max-run-seconds 90`
  - `workspaceboard/scripts/health/ai_health_check.py --dry-run` with the same bounded flags
  - `email_worker_header_poll.py --help` plus temp credential parse and HTML helper probe
  - `nationaloutreach_mail_cycle.py --help` plus temp credential parse and HTML helper probe
  - workspaceboard planner wrappers through compile plus `--help` path checks on the mirrored runners

Important readback:

- `task_flow_due_runner.py --dry-run` returned:
  - `due_count = 1`
  - `recorded = 0`
  - `skipped_existing = 1`
- `ai_health_check.py` initially hit the 20-second watchdog under migration proof, then passed cleanly once the bounded proof cap was widened to 90 seconds
- `workspaceboard/scripts/health/ai_health_check.py` also passed dry-run readback

Final inventory state for the bounded scan:

- `env-python3 = 0`
- `pinned-python3.13 = 37`
- `no-python-call = 13`
- `shell-calls-env-python3 = 1`
- `shell-calls-system-python3 = 2`
- `high-risk = 1`
- automatic low-risk recommendation: none

Recursive-improve readback after the final refresh:

- `eval/real-inventory/eval_results.json`
- run id: `d54d863e86dc`
- `trace_count = 1`
- `clean_success_rate = 100.0% (1/1)`

Current interpretation:

- the Python entrypoint migration lane is complete for the bounded `ai_workspace/scripts` + `workspaceboard/scripts` scan
- remaining interpreter risk now sits in shell wrappers, especially:
  - `/Users/werkstatt/ai_workspace/scripts/ai_box_backup.sh`

## Wrapper Follow-Through

Remaining executable `python3` call sites were also tightened after the Python-entrypoint lane closed:

- `/Users/werkstatt/ai_workspace/scripts/ai_box_backup.sh`
  - now uses `AI_BOX_BACKUP_PYTHON_BIN`, defaulting to `/usr/local/bin/python3.13`
- `/Users/werkstatt/ai_workspace/scripts/task_flow_due_runner.py`
  - subprocess calls now use `sys.executable`
- `/Users/werkstatt/ai_workspace/scripts/ai_health_check.py`
  - task-flow follow-through subprocess now uses `sys.executable`
- `/Users/werkstatt/ai_workspace/scripts/run_nationaloutreach_auto.sh`
  - now calls `/usr/local/bin/python3.13` for the mail cycle
- `/Users/werkstatt/ai_workspace/scripts/install_ai_health_manager_launchagent.sh`
  - launchagent template now emits `/usr/local/bin/python3.13`
- `/Users/werkstatt/ai_workspace/scripts/ai_manager_chat_entry_adapter.php`
  - Papers writer path now calls `/usr/local/bin/python3.13`
- `/Users/werkstatt/workspaceboard/scripts/workspaceboard_supervisor.php`
  - owner email helper path now calls `/usr/local/bin/python3.13`

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/task_flow_due_runner.py scripts/ai_health_check.py`
- `php -l scripts/ai_manager_chat_entry_adapter.php`
- `php -l /Users/werkstatt/workspaceboard/scripts/workspaceboard_supervisor.php`
- `grep` readback over `scripts` + `workspaceboard/scripts`

Executable-state interpretation:

- remaining `python3` hits are documentation examples and one explanatory report string
- runtime execution surfaces in the bounded lane are now pinned to Python 3.13 or `sys.executable`

## Python 3.13 Readback

- Homebrew `python@3.13` is already installed on this machine.
- Verified executable: `/usr/local/bin/python3.13`
- Verified venv interpreter: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve/.venv313/bin/python`
- Version: `Python 3.13.13`

## Constraint

Upstream declares `requires-python >=3.12`, while the default local interpreter in this shell is still `Python 3.9.6`.

Current interpretation:

- the repo-local smoke setup also works under Python 3.9 for the base CLI path used here
- the preferred path going forward is the explicit 3.13 venv, not the 3.9 override
- the shell default `python3` did not change during this pass; it still resolves to the system interpreter
- the first real follow-up should capture whether trace capture, eval, and any target-specific loop behave correctly under the 3.13 path

## Non-Break Verification

- `python3 -m py_compile` still passed for:
  - `scripts/ai_health_check.py`
  - `scripts/task_flow_due_runner.py`
  - `/Users/werkstatt/workspaceboard/scripts/health/ai_health_check.py`
  - `/Users/werkstatt/workspaceboard/scripts/planner/task_flow_due_runner.py`
- `which python3` in this shell still resolves to `/usr/bin/python3`
- `python3 --version` in this shell still reads `3.9.6`
- There is no `/usr/local/bin/python3` symlink in this environment, so Homebrew Python 3.13 did not take over the unversioned `python3` command

## Useful-Codex-Skills Pull List

The immediate reusable patterns from `grp06/useful-codex-skills` are:

- `find-refactor-candidates`
- `select-refactor`
- `execplan-create`
- `execplan-improve`
- `implement-execplan`

These map cleanly to a local planning/refactor workflow review, not to unattended recursion.

## Installed Runtime Reconciliation

The source-tree migration was not the whole runtime story. A direct verification pass against the installed launch/runtime copies under `/Users/admin` found stale interpreter paths still in active runtime mirrors, and those were patched in place.

Installed runtime changes:

- `/Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py`
  - shebang pinned to `#!/usr/local/bin/python3.13`
  - internal Python subprocess calls changed from bare `python3` to `sys.executable`
- `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py`
  - shebang pinned to `#!/usr/local/bin/python3.13`
- `/Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_supervisor.php`
  - owner email helper path now calls `/usr/local/bin/python3.13`
- `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js`
  - AI Manager escalation SMTP helper now uses `/usr/local/bin/python3.13`
  - AI Health sweep launcher now uses `/usr/local/bin/python3.13`

Runtime verification:

- grep readback on the installed files now returns only explicit 3.13 paths for those execution sites:
  - `/Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py:1:#!/usr/local/bin/python3.13`
  - `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py:1:#!/usr/local/bin/python3.13`
  - `/Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_supervisor.php:785: '/usr/local/bin/python3.13',`
  - `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js:1118: spawnSync('/usr/local/bin/python3.13', ...)`
  - `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js:10757: spawn('/usr/local/bin/python3.13', ...)`
- syntax and compile proof passed:
  - `php -l /Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_supervisor.php`
  - `node --check /Users/admin/.workspaceboard-launch/runtime/app/server/index.js`
  - `/usr/local/bin/python3.13 -m py_compile /Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py /Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py`

Current interpretation:

- the bounded migration lane is now reconciled at both source level and the main installed runtime copies that were still drifting
- the next recursive target should not be more shebang churn in this lane
- the next useful recursive slice is parity and drift detection: prove that source, installed runtime, and launch templates stay aligned instead of letting them drift again

## Runtime Parity Detector

The next recursive slice is now implemented as a bounded parity/drift detector:

- detector: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/runtime_parity_agent.py`
- runner: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_runtime_parity_test.py`
- artifact: `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/runtime-parity-inventory-2026-05-24.md`

What it checks:

- repo-local source entrypoints and wrappers
- installed runtime mirrors under `/Users/admin`
- launch-template parity for the AI Health launchagent path

First detector readback found one real code drift:

- `/Users/werkstatt/workspaceboard/server/index.js`
- `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js`

Both still used `/usr/bin/python3` for:

- AI Manager escalation SMTP helper
- AI Health sweep launcher

That drift is now fixed in both source and installed runtime copies.

Current parity readback after the fix:

- `Surfaces checked: 12`
- `In parity: 11`
- `Drifted or missing: 0`
- `Optional installed surfaces absent: 1`

Remaining gap:

- `/Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` is absent, so the detector records it as `missing-optional`
- that is deployment-state absence, not source/runtime code drift

Current interpretation:

- the bounded Python 3.13 lane is now in source/runtime code parity
- the recursive loop has moved from migration to regression detection
- the next useful recursive slice is to expand this detector to more installed mirrors and separate deployment-state checks from code-parity checks

## Deployment State Detector

The next bounded recursive slice is now implemented as a deployment-state detector:

- detector: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/deployment_state_agent.py`
- runner: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_deployment_state_test.py`
- artifact: `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/deployment-state-inventory-2026-05-24.md`

What it checks:

- installed launchd plists
- wrapper target existence
- visible `launchctl print` readback for AI Health

Current deployment-state readback:

- `Surfaces checked: 13`
- `OK: 11`
- `Drift: 2`
- `Optional missing: 0`

The drift is now isolated to AI Health deployment state:

- `/Library/LaunchDaemons/com.koval.ai-health-manager.plist` still points at `/usr/bin/python3`
- live `launchctl print system/com.koval.ai-health-manager` still reports `program = /usr/bin/python3`

Everything else in the bounded deployment slice read back cleanly:

- National Outreach system LaunchDaemon exists and points at `/Library/KOVAL/bin/nationaloutreach-auto`
- Task Flow reminders system LaunchDaemon exists and points at `/Users/admin/.task-flow-launch/runtime/run_task_flow_due_runner.sh`
- Workspaceboard user LaunchAgents exist
- Workspaceboard installed launch wrappers exist

Current interpretation:

- source/runtime code parity is now a separate solved slice
- the remaining interpreter risk is one installed service definition, not a broad codebase problem
- the next recursive step should be a narrow AI Health deployment reconcile plan, not more migration churn elsewhere

## Repo-Local Service Parity Tool

The recursive pattern has now moved out of the sandbox into a repo-local tool:

- tool: `/Users/werkstatt/ai_workspace/scripts/service_parity_check.py`
- latest Markdown report: `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/service-parity-check-latest.md`
- latest JSON report: `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/service-parity-check-latest.json`

Command modes:

- `--mode parity`
- `--mode deployment`
- `--mode installed`
- `--mode all`

Guarded fix modes:

- `--fix-ai-health-interpreter`
  - only patches the named AI Health plist interpreter when permissions allow
- `--fix-installed-interpreters`
  - patches writable installed runtime Python shebangs and shell wrapper Python calls
  - does not edit root-owned plists

Current broadened readback after running the installed runtime fixer:

- `surfaces_checked = 91`
- `drift = 0`
- `fix_failed = 0`

What changed:

- writable installed runtime drift across National Outreach, Task Flow, Frank, Avignon, Asher, and Venetia was patched to `/usr/local/bin/python3.13`
- active internal bare `python3` subprocess calls were also fixed in:
  - `/Users/admin/.nationaloutreach-launch/runtime/scripts/ai_health_check.py`
  - `/Users/admin/.task-flow-launch/runtime/scripts/ai_health_check.py`
  - `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`

Final root-owned drift closeout:

- Robert applied the narrow interpreter-only fix to:
  - `/Library/LaunchDaemons/com.koval.frank-morning-overview.plist`
  - `/Library/LaunchDaemons/com.koval.avignon-morning-overview.plist`
- both now show `/usr/local/bin/python3.13` in `plutil -p`
- both now show `program = /usr/local/bin/python3.13` in `launchctl print`
- calendar triggers at `06:00` and `18:00` remain intact
- neither scheduled job was kickstarted

The service parity lane is clean at current coverage.

## Recurring Read-Only Check

Service parity is now wired into AI Health as a recurring read-only check:

- source: `/Users/werkstatt/ai_workspace/scripts/ai_health_check.py`
- checker: `/Users/werkstatt/ai_workspace/scripts/service_parity_check.py`
- AI Health local report:
  - `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/service-parity-latest.md`
  - `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/service-parity-latest.json`

Behavior:

- AI Health runs `service_parity_check.py --mode all`
- no fix flags are passed from AI Health
- drift appears in:
  - `tmp/ai-health-manager/latest.json`
  - `tmp/ai-health-manager/latest.md`
  - AI Health stdout
  - canonical status line

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/ai_health_check.py scripts/service_parity_check.py`
- dry-run AI Health readback:
  - `service_parity = passed`
  - `service_parity_checked = 91`
  - `service_parity_drift = 0`

This turns the recursive service parity work from a one-time cleanup into a recurring regression detector.

## Task Flow Truth Drift Lane

The next recursive lane is now implemented in the same recurring-check shape, but aimed at state contradictions rather than interpreter drift.

What was added:

- registry/config surface: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- read-only checker: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_drift_check.py`
- AI Health integration in `/Users/werkstatt/ai_workspace/scripts/ai_health_check.py`

Why the registry matters:

- the checker is no longer hardcoded to one frozen architecture shape
- if Workspaceboard, Task Flow, proof reports, or command paths change, update the registry file first
- this is the explicit guard against recursive checkers drifting behind code or architecture changes

Current coverage:

- Workspaceboard `/api/status`
- `workspaceboard_db_recorder.php task-flow-report`
- `task_flow_mysql_recorder.php report`

Current rule families:

- active Task Flow row references missing board session
- closed Task Flow row still has a live board session
- closed row lacks closeout proof in proof report
- reported/completed email row lacks sent proof in proof report
- scheduler violations present
- scheduler route candidates present
- proof-report closeout issues present

AI Health wiring:

- new flags:
  - `--disable-task-flow-truth-drift-check`
  - `--task-flow-truth-drift-check-script`
  - `--task-flow-truth-drift-timeout-seconds`
- new AI Health fields:
  - `task_flow_truth_drift`
  - `task_flow_truth_drift_count`
  - `task_flow_truth_drift_checked`

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/ai_health_check.py scripts/task_flow_truth_drift_check.py`
- `./scripts/task_flow_truth_drift_check.py --fail-on-drift`
  - `drift_count=17`
- `./scripts/ai_health_check.py --dry-run --max-run-seconds 90`
  - `task_flow_truth_drift=drift`
  - `task_flow_truth_drift_count=17`
  - `task_flow_truth_drift_checked=500`
  - `service_parity=passed`
  - `service_parity_drift=0`

Current contradiction classes from the live check:

- `closed_without_closeout_proof = 14`
- `scheduler_violations_present = 1`
- `scheduler_route_candidates_present = 1`
- `proof_report_closeout_issues = 1`

This means the recursive lane has now moved from migration/parity into recurring truth-drift detection with one config-owned update point.

## Service Parity Registry Refactor

The service parity lane now follows the same registry-driven pattern.

What was added:

- registry/config surface: `/Users/werkstatt/ai_workspace/scripts/service_parity_surfaces.json`

What changed:

- `/Users/werkstatt/ai_workspace/scripts/service_parity_check.py` no longer owns the surface map inline
- parity checks, deployment checks, installed runtime scan roots, plist scan roots, report defaults, and fix targets now come from the registry
- the command surface did not change, so AI Health can keep calling the checker the same way

Why this matters:

- code/architecture shifts now have one update point for both recursive checker lanes
- `task_flow_truth_drift_check.py` and `service_parity_check.py` now both follow the same pattern: stable checker code, registry-owned surfaces

Verification:

- `/usr/local/bin/python3.13 -m py_compile scripts/service_parity_check.py scripts/ai_health_check.py`
- `./scripts/service_parity_check.py --mode all --fail-on-drift`
  - `surfaces_checked=91`
  - `drift=0`
  - `fix_failed=0`

AI Health note:

- a dry-run attempt during this slice returned `skipped_locked=true` because another AI Health run already held the run lock
- that is not a parity regression; it only means the direct service parity proof is the fresh verification surface for this pass

## Recommendation-Quality Benchmark

Added bounded recommendation benchmarking under the same 3.13 pilot target:

- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/recommendation_benchmark_agent.py`
- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_recommendation_benchmark.py`

This benchmark is synthetic by design. It does not mutate live queue or service state. It only asks whether the recursive lane chooses the right next step for a few known state classes.

Verification:

- `/usr/local/bin/python3.13 -m py_compile sandboxes/recursive-improve-pilot-target-313/recommendation_benchmark_agent.py sandboxes/recursive-improve-pilot-target-313/run_recommendation_benchmark.py`
- `../recursive-improve/.venv313/bin/python run_recommendation_benchmark.py`
  - wrote `5` traces to `eval/recommendation-traces`
- `recursive-improve eval eval/recommendation-traces --output-dir eval/recommendation-benchmark`
  - run id `7596f83f91ec`
  - `clean_success_rate = 100.0% (5/5)`
- `recursive-improve benchmark --label recommendation-quality-liveaware-2026-05-24 --traces-dir eval/recommendation-traces -o eval/recommendation-benchmark`
  - benchmark run id `b3d095e7b2e4`
  - score `14.3%`

Durable note:

- `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/recursive-recommendation-benchmark-2026-05-24.md`

Interpretation:

- the recursive lane now has a bounded quality baseline for next-step recommendations
- it now includes an explicit `repair-truth-drift` branch in addition to `do-not-race-live-cleanup`
- the next useful upgrade is to keep feeding real checker snapshots into this benchmark family instead of expanding synthetic checker plumbing indefinitely

## Live Recommendation Snapshot

Added a second runner that consumes the real checker surfaces directly:

- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_live_recommendation_snapshot.py`

Verification:

- `../recursive-improve/.venv313/bin/python run_live_recommendation_snapshot.py`
  - wrote `1` trace to `eval/live-recommendation-traces`
  - expected action `repair-truth-drift`
  - observed action `repair-truth-drift`
- `recursive-improve eval eval/live-recommendation-traces --output-dir eval/live-recommendation-benchmark`
  - run id `cde619b65fda`
  - `clean_success_rate = 100.0% (1/1)`
- `recursive-improve benchmark --label live-recommendation-snapshot-2026-05-24 --traces-dir eval/live-recommendation-traces -o eval/live-recommendation-benchmark`
  - benchmark run id `bc145700f885`
  - score `14.3%`

Current live state that drove the recommendation:

- service parity drift: `0`
- registry lint: `ok`
- truth drift count: `1`
- current truth drift kind: `active_missing_board_session`
- current affected title: `salesreport-coteam-bonus-pioneer-date-filter-2026-05-05`

Durable note:

- `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/recursive-live-recommendation-snapshot-2026-05-24.md`

## Historical Recommendation Corpus

Added a replayable corpus of known recursive-lane states:

- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/recommendation_historical_cases.json`
- `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_historical_recommendation_benchmark.py`

Verification:

- `/usr/local/bin/python3.13 -m py_compile sandboxes/recursive-improve-pilot-target-313/run_historical_recommendation_benchmark.py sandboxes/recursive-improve-pilot-target-313/recommendation_benchmark_agent.py`
- `../recursive-improve/.venv313/bin/python run_historical_recommendation_benchmark.py`
  - wrote `6` traces to `eval/historical-recommendation-traces`
- `recursive-improve eval eval/historical-recommendation-traces --output-dir eval/historical-recommendation-benchmark`
  - run id `305f1b72f49c`
  - `clean_success_rate = 100.0% (6/6)`
- `recursive-improve benchmark --label historical-recommendation-quality-2026-05-24 --traces-dir eval/historical-recommendation-traces -o eval/historical-recommendation-benchmark`
  - benchmark run id `3b31329dcd91`
  - score `14.3%`

Durable note:

- `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/recursive-historical-recommendation-benchmark-2026-05-24.md`

Interpretation:

- this is still recommendation-only
- it expands the quality baseline from one live snapshot and five synthetic scenarios to six historically grounded cases
- the next autonomy step should be a proposal queue, not automatic mutation
