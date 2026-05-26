#!/bin/zsh
set -euo pipefail

OPS_ROOT="/Users/werkstatt/ops"
CAPTURE_SCRIPT="$OPS_ROOT/tmp/project_management_manual_capture.js"
ENV_FILE="$OPS_ROOT/.env"
PLAYWRIGHT_NODE_MODULES="/Users/werkstatt/playwright-scraper/node_modules"

echo "Checking OPS manual capture prerequisites..."

if [[ ! -f "$CAPTURE_SCRIPT" ]]; then
  echo "Missing capture script: $CAPTURE_SCRIPT"
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Missing node in PATH"
  exit 1
fi

if ! NODE_PATH="$PLAYWRIGHT_NODE_MODULES" node -e "require.resolve('playwright')" >/dev/null 2>&1; then
  echo "Playwright is not available through NODE_PATH=$PLAYWRIGHT_NODE_MODULES"
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

if ! grep -q '^CODEX_AGENT_USERNAME=' "$ENV_FILE"; then
  echo "Missing CODEX_AGENT_USERNAME in $ENV_FILE"
  exit 1
fi

if ! command -v php >/dev/null 2>&1; then
  echo "Missing php in PATH"
  exit 1
fi

php -r '
require "/Users/werkstatt/ops/bootstrap.php";
require "/Users/werkstatt/ops/crm_integration.php";
$username = trim((string) getenv("CODEX_AGENT_USERNAME"));
$userId = (int) (function_exists("find_crm_user_id_by_username") ? (find_crm_user_id_by_username($username) ?: 0) : 0);
$jwt = function_exists("crm_lookup_recent_sso_jwt") ? crm_lookup_recent_sso_jwt($username, $userId > 0 ? $userId : null) : "";
if ($username === "" || $userId <= 0 || $jwt === "") {
    fwrite(STDERR, "No recent SSO JWT is available for the Codex OPS capture path\n");
    exit(1);
}
' >/dev/null

echo "OPS manual capture preflight passed."
