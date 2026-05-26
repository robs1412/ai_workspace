# Recursive-Improve Intermediate Handoff

- Recorded: 2026-05-24 11:57 CDT
- Scope: repo-local `recursive-improve` pilot plus bounded Python 3.13 migration lane in `ai_workspace/scripts`

## Current State

- `recursive-improve` pilot root:
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve`
- preferred Python 3.13 venv:
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve/.venv313`
- active pilot target:
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313`
- latest inventory report:
  - `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/python-entrypoint-inventory-2026-05-24.md`
- latest pilot log:
  - `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/recursive-improve-pilot-setup-2026-05-24.md`

## Why This Helps The Recursive Item

- The pilot is no longer just bootstrap; it is generating a real inventory/eval loop and then using that loop to choose bounded migration targets.
- It already caught real tooling defects:
  - the inventory agent recommendation logic stalled after the first four hardcoded helpers
  - that was fixed in `sandboxes/recursive-improve-pilot-target-313/python_entrypoint_inventory_agent.py`
- It also proved the helper lane can be pushed far before hitting real shared-runtime risk:
  - `ai_transfer_gate.py` is now migrated and verified
- It is also producing measurable progress:
  - inventory moved from `env-python3=37` / `pinned-python3.13=0`
- to `env-python3=0` / `pinned-python3.13=37`
- So yes: this is helping the recursive item. It is acting as a constrained self-improvement loop for a real local migration lane, not as abstract recursion.

## Latest Readback

- latest eval file:
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/eval/real-inventory/eval_results.json`
- latest eval run id:
  - `6f82a995ebaa`
- latest eval status:
  - `trace_count=1`
  - `clean_success_rate=100.0% (1/1)`
- latest inventory:
- `env-python3=0`
- `pinned-python3.13=37`
  - `high-risk=1`

Installed runtime reconciliation is also complete for the main drift surfaces:

- `/Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py`
- `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py`
- `/Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_supervisor.php`
- `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js`

Those installed copies now read back with explicit `/usr/local/bin/python3.13` execution paths and passed Python compile, `php -l`, and `node --check` validation.

## Exactly What Is Next

Completed milestones:

- bounded Python entrypoint migration lane for `ai_workspace/scripts` and `workspaceboard/scripts`
- wrapper follow-through in source
- installed runtime reconciliation for the main launch/runtime mirrors

Current next recursive target:

- runtime parity and drift detection between source, installed runtime copies, and launch templates

Why this is next:

- the migration lane itself is finished
- the remaining risk is regression by drift, not missing 3.13 pins in the bounded lane
- the recursive loop is now more useful as an audit/regression detector than as a bulk editor for this slice

## Suggested Next Recursive Slice

Build a second bounded recursive lane around deployment parity:

- inventory source:
  - repo-local scripts and launch templates
- parity targets:
  - installed launch/runtime mirrors under `/Users/admin`
- desired loop behavior:
  - detect source/runtime interpreter drift
  - recommend the smallest safe reconciliation step
  - require proof from both source and installed copies

This keeps the recursive item grounded in measurable infrastructure hygiene instead of reaching immediately for a broader self-editing loop.

Current implementation status:

- detector implemented at:
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/runtime_parity_agent.py`
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_runtime_parity_test.py`
- current artifact:
  - `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/runtime-parity-inventory-2026-05-24.md`
- first detector run forced one real parity fix:
  - source and installed `/workspaceboard/.../server/index.js` were still using `/usr/bin/python3` for the AI Manager escalation helper and AI Health sweep launcher
  - both now read back with `/usr/local/bin/python3.13`
- current detector totals:
  - `Surfaces checked: 12`
  - `In parity: 11`
  - `Drifted or missing: 0`
  - `Optional installed surfaces absent: 1`
- remaining optional gap:
  - `/Users/admin/Library/LaunchAgents/com.koval.ai-health-manager.plist` is absent
  - treat that as deployment-state absence, not source/runtime code drift

The deployment-state slice is now implemented separately:

- detector:
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/deployment_state_agent.py`
  - `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313/run_deployment_state_test.py`
- artifact:
  - `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/deployment-state-inventory-2026-05-24.md`
- current detector totals:
  - `Surfaces checked: 13`
  - `OK: 11`
  - `Drift: 2`
  - `Optional missing: 0`

Current bounded deployment drift:

- `/Library/LaunchDaemons/com.koval.ai-health-manager.plist` still contains `/usr/bin/python3`
- live `launchctl print system/com.koval.ai-health-manager` also reports `/usr/bin/python3`

Interpretation:

- the remaining recursive target is now a narrow AI Health deployment reconcile slice
- National Outreach, Task Flow, and Workspaceboard deployment surfaces in this bounded pass are present and read back cleanly

## Resume Steps

1. Read:
   - `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/python-entrypoint-inventory-2026-05-24.md`
   - `/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/recursive-improve-pilot-setup-2026-05-24.md`
2. Treat the Python-entrypoint milestone as complete.
3. If continuing recursively, start a parity/drift loop rather than more shebang migration:
   - compare repo-local source against installed runtime copies
   - compare launch templates against installed runtime copies
   - flag remaining executable `python3` drift only when it is real runtime, not docs/examples
   - verify with compile/lint/readback on the installed copy as well as source
4. Refresh the loop:
   - `cd /Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313`
   - `../recursive-improve/.venv313/bin/python run_real_inventory_test.py`
   - `../recursive-improve/.venv313/bin/recursive-improve eval eval/real-traces -o eval/real-inventory`
5. Record new counts and recommendation into:
   - `project_hub/artifacts/recursive-tools/recursive-improve-pilot-setup-2026-05-24.md`
   - `project_hub/INDEX.md`
   - `HANDOFF.md`

## New Boundary

The recursive item has now completed the bounded Python-entrypoint lane successfully:

- standalone helpers and report generators were migrated
- shared-runtime entrypoints were migrated with bounded proof
- installed workspaceboard mirror entrypoints were migrated too
- wrapper/runtime source call sites were tightened
- installed runtime mirror drift was reconciled on the main active copies

That means the recursive loop is still useful, but the evaluation standard should get stricter from here:

- proof should favor real runtime readback over synthetic fixtures when possible
- changes may need paired verification against installed/runtime copies, not just repo-local source
- future value is more likely in drift detection and deployment parity than more one-off shebang edits

## Stop Condition

Pause the automatic helper loop when either of these becomes true:

- the next target mutates live OPS/runtime/private data in a way that cannot be smoke-tested safely
- the next target is a shared runtime dependency used by active worker lanes, where a local shebang change alone is not enough proof
