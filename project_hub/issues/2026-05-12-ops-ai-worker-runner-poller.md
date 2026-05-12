# Incident / Project Slice Log

- Master Incident ID: `AI-20260512-OPS-AI-WORKER-RUNNER-POLLER-01`
- Date Opened: `2026-05-12`
- Owner: `Robert`
- Priority: `High`
- Status: `Blocked`

## Scope

- Add a durable 15-minute poller for OPS tasks using the existing one-shot `ops_ai_worker_runner_bridge.php`.
- Keep the bridge one-shot and let launchd handle cadence/activation.
- Preserve the current Task Manager ownership model: the bridge should route tasks, not create hidden worker closeout or auto-complete work.

## Owner Workspace

- Primary owner workspace: `ws ops`
- Responsible worker/persona: `Task Manager -> OPS bridge / AI worker runner`
- Route mode: `source-backed activation slice`
- Output channel: `Workspaceboard / AI Manager page`

## Requested Deliverable

- Install and load a 15-minute system LaunchDaemon poller for OPS tasks.
- Return the plist path, launch proof, and one exact blocker if the poller cannot be loaded live.

## Finish Contract

- Proof required: installer path, plist path, launchctl load proof, and bridge dry-run proof.
- Blocker allowed: one exact activation blocker only.
- Next update: either loaded LaunchAgent proof or the exact load blocker.

## Verification Notes

- The bridge dry-run is healthy and returns current OPS task candidates:
  - `php /Users/werkstatt/ops/scripts/ops_ai_worker_runner_bridge.php --dry-run --limit=3`
  - dry-run returned `ok: true`, `candidate_count: 3`, and routed packets for AI-worker tasks including Naomi, Ezra, and Frank.
- Added wrapper and installer scripts:
  - [`/Users/werkstatt/ops/scripts/run_ops_ai_worker_runner_bridge.sh`](/Users/werkstatt/ops/scripts/run_ops_ai_worker_runner_bridge.sh)
  - [`/Users/werkstatt/ops/scripts/install_ops_ai_worker_runner_bridge_launchagent.sh`](/Users/werkstatt/ops/scripts/install_ops_ai_worker_runner_bridge_launchagent.sh)
- The installer wrote the prepared system daemon plist to:
  - `/Users/werkstatt/ops/tmp/ops-ai-worker-runner-bridge/com.koval.ops-ai-worker-runner-bridge.system.plist`
- Local script validation passed:
  - `php -l /Users/werkstatt/ops/scripts/ops_ai_worker_runner_bridge.php`
  - `zsh -n /Users/werkstatt/ops/scripts/run_ops_ai_worker_runner_bridge.sh`
  - `zsh -n /Users/werkstatt/ops/scripts/install_ops_ai_worker_runner_bridge_launchagent.sh`
- Exact live blocker:
  - `launchctl bootstrap system` is unavailable from this shell, so the LaunchDaemon could not be loaded into the active system domain here.

## Notes

- The poller is intentionally still one-shot at the bridge layer; launchd supplies the 15-minute cadence.
- No OPS task completion, external send, credential/auth change, deploy, or production mutation was performed by the poller slice itself.
