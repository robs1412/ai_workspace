#!/usr/bin/env bash
set -euo pipefail

stamp="$(date +%Y%m%d-%H%M%S)"
backup_root="/Users/werkstatt/ai_box_backups"
dest="$backup_root/$stamp"
mkdir -p "$dest/launchagents" "$dest/git" "$dest/status"
chmod 700 "$backup_root" "$dest"

copy_if_exists() {
  local src="$1"
  local dst="$2"
  if [ -e "$src" ]; then
    cp -p "$src" "$dst"
  fi
}

for plist in \
  /Users/admin/Library/LaunchAgents/com.koval.workspaceboard.plist \
  /Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist \
  /Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist \
  /Users/admin/Library/LaunchAgents/com.koval.frank-morning-overview.plist; do
  copy_if_exists "$plist" "$dest/launchagents/$(basename "$plist")"
done

copy_if_exists /Users/admin/.bashrc "$dest/status/admin-bashrc.txt"

for repo in /Users/werkstatt/ai_workspace /Users/werkstatt/workspaceboard; do
  name="$(basename "$repo")"
  if [ -d "$repo/.git" ]; then
    {
      echo "repo=$repo"
      git -C "$repo" rev-parse --abbrev-ref HEAD
      git -C "$repo" rev-parse HEAD
      git -C "$repo" status --short
    } > "$dest/git/$name.txt"
  fi
done

uid="$(id -u)"
for label in \
  com.koval.workspaceboard \
  com.koval.frank-auto \
  com.koval.avignon-auto \
  com.koval.frank-morning-overview; do
  launchctl print "gui/$uid/$label" > "$dest/status/$label.launchctl.txt" 2>&1 || true
done

{
  echo "created=$stamp"
  echo "host=$(hostname)"
  echo "user=$(whoami)"
  echo "ai_workspace_head=$(git -C /Users/werkstatt/ai_workspace rev-parse --short HEAD 2>/dev/null || true)"
  echo "workspaceboard_head=$(git -C /Users/werkstatt/workspaceboard rev-parse --short HEAD 2>/dev/null || true)"
  echo "private_vault_present=$([ -d /Users/werkstatt/secure-vaults/ai-workspace-private.sparsebundle ] && echo yes || echo no)"
  echo "private_vault_mounted=$(mount | grep -q 'on /Volumes/AIWorkspacePrivate ' && echo yes || echo no)"
} > "$dest/MANIFEST.txt"

find "$dest" -type f -print0 | xargs -0 shasum -a 256 > "$dest/SHA256SUMS.txt"
ln -sfn "$dest" "$backup_root/latest"
printf 'backup=%s\n' "$dest"
