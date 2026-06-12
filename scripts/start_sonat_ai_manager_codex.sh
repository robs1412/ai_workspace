#!/usr/bin/env bash
set -euo pipefail

cd /Users/werkstatt/ai_workspace

export CODEX_OWNER_USER_ID=3
export CODEX_OWNER_LABEL=Sonat
export CODEX_OWNER_ROLE=ai-manager-sonat
export CODEX_OWNER_WORKSPACE=ai

exec /usr/local/bin/codex -C /Users/werkstatt/ai_workspace \
  "CLI_OWNER_CONTEXT: Sonat is operating this Codex CLI session. CODEX_OWNER_USER_ID=3, CODEX_OWNER_LABEL=Sonat, CODEX_OWNER_ROLE=ai-manager-sonat. Load /Users/werkstatt/ai_workspace/worker_roles/ai-manager-sonat-startup.md, reply exactly READY AI Manager Sonat., and treat this as the AI Manager Sonat control lane. Do not infer Robert ownership from the shared /Users/werkstatt path or Unix account. Route substantive work through Task Manager / visible Workspaceboard workers and report to Sonat by default."
