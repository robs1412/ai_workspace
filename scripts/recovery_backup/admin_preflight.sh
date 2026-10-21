#!/bin/bash
# Read-only privileged coverage check. No backup, credentials, or permission changes.
set -euo pipefail
workspace=/Users/werkstatt/ai_workspace
if [ "$(id -u)" -ne 0 ]; then
  exec sudo /bin/bash "$workspace/scripts/recovery_backup/admin_preflight.sh"
fi
umask 077
output="$workspace/tmp/recovery-backup-review/admin-inventory.json"
/usr/local/bin/python3.13 "$workspace/scripts/recovery_backup/runner.py" estimate \
  --config "$workspace/tmp/recovery-backup-review/disabled-config.json" > "$output"
/usr/local/bin/python3.13 - "$output" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
print(json.dumps({'admin_inventory_complete':True,'unreadable':r['unreadable'],
 'logical_gib':round(r['total_logical_bytes']/1024**3,2)}))
PY
