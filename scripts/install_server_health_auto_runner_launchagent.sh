#!/usr/bin/env bash
set -euo pipefail

label="com.koval.server-health-auto-runner"
root="/Users/werkstatt/ai_workspace"
script="$root/scripts/server_health_auto_runner.py"
log_dir="$root/tmp/ai-health-manager"
user_plist="$HOME/Library/LaunchAgents/$label.plist"
system_plist="/Library/LaunchDaemons/$label.plist"
prepared_system_plist="$log_dir/$label.system.plist"
plist="$system_plist"
interval="${1:-900}"
load_agent="0"
system_daemon="1"

usage() {
  cat <<USAGE
Usage: $0 [interval_seconds] [--load] [--user-agent]

Installs a metadata-only Server Health Auto Runner launchd job.
Default: no-GUI system LaunchDaemon running as admin.
--user-agent: install an active-user LaunchAgent instead.
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
    --user-agent)
      system_daemon="0"
      plist="$user_plist"
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
if [[ "$system_daemon" == "1" ]]; then
  tmp_plist="$(mktemp "$prepared_system_plist.tmp.XXXXXX")"
else
  tmp_plist="$(mktemp "$plist.tmp.XXXXXX")"
fi

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
PLIST

if [[ "$system_daemon" == "1" ]]; then
  cat >> "$tmp_plist" <<PLIST
  <key>UserName</key>
  <string>admin</string>
PLIST
fi

cat >> "$tmp_plist" <<PLIST
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

if [[ "$system_daemon" == "1" ]]; then
  if [[ "$(id -u)" == "0" || -w "$(dirname "$system_plist")" ]]; then
    mv "$tmp_plist" "$system_plist"
    chown root:wheel "$system_plist" 2>/dev/null || true
    chmod 644 "$system_plist"
    installed_path="$system_plist"
  else
    mv "$tmp_plist" "$prepared_system_plist"
    chmod 644 "$prepared_system_plist"
    installed_path="$prepared_system_plist"
  fi
else
  mv "$tmp_plist" "$plist"
  chmod 644 "$plist"
  installed_path="$plist"
fi

echo "installed_plist=$installed_path"
echo "label=$label"
echo "interval_seconds=$interval"
echo "mode=metadata-only"
if [[ "$system_daemon" == "1" ]]; then
  echo "domain=system"
  echo "username=admin"
else
  echo "domain=user"
fi

if [[ "$load_agent" != "1" ]]; then
  echo "loaded=not_requested"
  if [[ "$system_daemon" == "1" && "$installed_path" != "$system_plist" ]]; then
    echo "blocker=/Library/LaunchDaemons is not writable from this session; install the prepared plist with the local_admin_command below."
    echo "local_admin_command=sudo install -o root -g wheel -m 644 '$prepared_system_plist' '$system_plist' && sudo launchctl bootstrap system '$system_plist' && sudo launchctl kickstart -k system/$label"
  fi
  exit 0
fi

if [[ "$system_daemon" == "1" ]]; then
  if [[ "$installed_path" != "$system_plist" ]]; then
    echo "loaded=blocked"
    echo "blocker=/Library/LaunchDaemons is not writable from this session and no noninteractive privileged path is available."
    echo "local_admin_command=sudo install -o root -g wheel -m 644 '$prepared_system_plist' '$system_plist' && sudo launchctl bootstrap system '$system_plist' && sudo launchctl kickstart -k system/$label"
    exit 75
  fi
  launchctl bootout "system/$label" >/dev/null 2>&1 || true
  launchctl bootstrap system "$system_plist"
  launchctl kickstart -k "system/$label"
  echo "loaded=system/$label"
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
echo "blocker=gui/$uid launchd domain is unavailable from this session; use default system mode for no-GUI operation."
exit 75
