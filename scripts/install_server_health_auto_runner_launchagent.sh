#!/usr/bin/env bash
set -euo pipefail

label="com.koval.server-health-auto-runner"
root="/Users/werkstatt/ai_workspace"
script="$root/scripts/server_health_auto_runner.py"
log_dir="$root/tmp/ai-health-manager"
plist="$HOME/Library/LaunchAgents/$label.plist"
interval="${1:-900}"
load_agent="0"

usage() {
  cat <<USAGE
Usage: $0 [interval_seconds] [--load]

Installs a metadata-only Server Health Auto Runner LaunchAgent.
Default interval: 900 seconds.
The runner records bounded server-health, memory, process, disk, and repo metadata only.
USAGE
}

while (($#)); do
  case "$1" in
    --load)
      load_agent="1"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    ''|*[!0-9]*)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 64
      ;;
    *)
      interval="$1"
      shift
      ;;
  esac
done

if [[ "$interval" -lt 300 ]]; then
  echo "interval_seconds must be >= 300 for this report-only runner" >&2
  exit 64
fi

if [[ ! -x "$script" ]]; then
  chmod 755 "$script"
fi

mkdir -p "$HOME/Library/LaunchAgents" "$log_dir"
tmp_plist="$(mktemp "$plist.tmp.XXXXXX")"
cat > "$tmp_plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$label</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/python3.13</string>
    <string>$script</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$root</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>/Users/admin</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>$interval</integer>
  <key>StandardOutPath</key>
  <string>$log_dir/server-health-auto-runner.launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>$log_dir/server-health-auto-runner.launchd.err.log</string>
</dict>
</plist>
PLIST

plutil -lint "$tmp_plist" >/dev/null
mv "$tmp_plist" "$plist"
chmod 644 "$plist"

echo "installed_plist=$plist"
echo "label=$label"
echo "interval_seconds=$interval"
echo "mode=metadata-only"

if [[ "$load_agent" != "1" ]]; then
  echo "loaded=not_requested"
  exit 0
fi

uid="$(id -u)"
if launchctl print "gui/$uid" >/dev/null 2>&1; then
  launchctl bootout "gui/$uid/$label" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$uid" "$plist"
  launchctl kickstart -k "gui/$uid/$label"
  echo "loaded=gui/$uid/$label"
  exit 0
fi

echo "loaded=blocked"
echo "blocker=gui/$uid launchd domain is unavailable from this session; load from an active user session."
exit 75
