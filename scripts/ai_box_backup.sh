#!/usr/bin/env bash
set -euo pipefail

stamp="$(date +%Y%m%d-%H%M%S)"
backup_root="/Users/werkstatt/ai_box_backups"
dest="$backup_root/$stamp"
remote_push="${AI_BOX_BACKUP_PUSH_REMOTE:-1}"
remote_user="${AI_BOX_BACKUP_REMOTE_USER:-agent-codex}"
remote_host="${AI_BOX_BACKUP_REMOTE_HOST:-192.168.55.205}"
remote_path="${AI_BOX_BACKUP_REMOTE_PATH:-/home/agent-codex/backups}"
remote_target="${remote_user}@${remote_host}"
remote_dest="${remote_path}/${stamp}"
remote_transfer_mode="${AI_BOX_BACKUP_TRANSFER_MODE:-sftp}"
remote_key="${AI_BOX_BACKUP_SSH_KEY:-/Users/admin/.ssh/id_ed25519_github_modules}"
remote_askpass="${AI_BOX_BACKUP_SSH_ASKPASS:-/Users/werkstatt/ai_workspace/.private/scripts/ssh_askpass_claude_koval.sh}"
remote_ssh="env DISPLAY=:0 SSH_ASKPASS_REQUIRE=force SSH_ASKPASS=${remote_askpass} ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new"
remote_sftp="sftp -b - -i ${remote_key} -oBatchMode=yes -oConnectTimeout=10 -oStrictHostKeyChecking=accept-new"
warning_email_enabled="${AI_BOX_BACKUP_WARNING_EMAIL_ENABLED:-1}"
warning_email_to="${AI_BOX_BACKUP_WARNING_TO:-robert@kovaldistillery.com}"
warning_email_cc="${AI_BOX_BACKUP_WARNING_CC:-}"
warning_email_creds="${AI_BOX_BACKUP_WARNING_CREDS_FILE:-/Users/werkstatt/ai_workspace/.private/mailboxes/nationaloutreach/credential.txt}"
warning_email_sent_log="${AI_BOX_BACKUP_WARNING_SENT_LOG:-/Users/admin/.nationaloutreach-launch/state/sent-log.jsonl}"
warning_email_dry_run="${AI_BOX_BACKUP_WARNING_DRY_RUN:-0}"
warning_email_script="/Users/werkstatt/ai_workspace/scripts/send_codex_ops_email.py"
python_bin="${AI_BOX_BACKUP_PYTHON_BIN:-/usr/local/bin/python3.13}"
remote_push_status="skipped"
remote_push_error=0
warning_email_status="not_needed"
warning_email_message_id=""

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

write_manifest() {
  {
    echo "created=$stamp"
    echo "host=$(hostname)"
    echo "user=$(whoami)"
    echo "ai_workspace_head=$(git -C /Users/werkstatt/ai_workspace rev-parse --short HEAD 2>/dev/null || true)"
    echo "workspaceboard_head=$(git -C /Users/werkstatt/workspaceboard rev-parse --short HEAD 2>/dev/null || true)"
    echo "private_vault_present=$([ -d /Users/werkstatt/secure-vaults/ai-workspace-private.sparsebundle ] && echo yes || echo no)"
    echo "private_vault_mounted=$(mount | grep -q 'on /Volumes/AIWorkspacePrivate ' && echo yes || echo no)"
    echo "remote_push_requested=$remote_push"
    echo "remote_target=${remote_target}"
    echo "remote_dest=${remote_dest}"
    echo "remote_push_status=${remote_push_status}"
    echo "warning_email_enabled=${warning_email_enabled}"
    echo "warning_email_status=${warning_email_status}"
    echo "warning_email_message_id=${warning_email_message_id}"
  } > "$dest/MANIFEST.txt"
}

write_shasums() {
  find "$dest" -type f -print0 | xargs -0 shasum -a 256 > "$dest/SHA256SUMS.txt"
}

write_manifest
write_shasums

sftp_batch() {
  local script
  script="$(mktemp)"
  cat > "$script"
  if ! $remote_sftp "$remote_target" < "$script"; then
    rm -f "$script"
    return 1
  fi
  rm -f "$script"
}

if [ "$remote_push" != "0" ]; then
  if [ "$remote_transfer_mode" = "sftp" ]; then
    if sftp_batch <<EOF
-mkdir $remote_path
mkdir $remote_dest
put -pr $dest $remote_path/
EOF
    then
      remote_push_status="success"
    else
      remote_push_status="failed"
      remote_push_error=1
    fi
  else
    if $remote_ssh "$remote_target" "mkdir -p '$remote_path' '$remote_dest' && chmod 700 '$remote_path' '$remote_dest'"; then
      if rsync -a --delete -e "$remote_ssh" "$dest/" "${remote_target}:${remote_dest}/"; then
        remote_push_status="success"
      else
        remote_push_status="failed"
        remote_push_error=1
      fi
    else
      remote_push_status="failed"
      remote_push_error=1
    fi
  fi
fi

write_manifest
write_shasums

if [ "$remote_push" != "0" ] && [ "$remote_push_status" = "success" ]; then
  if [ "$remote_transfer_mode" = "sftp" ]; then
    sftp_batch <<EOF
put $dest/MANIFEST.txt $remote_dest/MANIFEST.txt
put $dest/SHA256SUMS.txt $remote_dest/SHA256SUMS.txt
-rm $remote_path/latest
ln -s $remote_dest $remote_path/latest
EOF
  else
    rsync -a -e "$remote_ssh" "$dest/MANIFEST.txt" "$dest/SHA256SUMS.txt" "${remote_target}:${remote_dest}/"
    $remote_ssh "$remote_target" "ln -sfn '$remote_dest' '$remote_path/latest'"
  fi
fi

send_warning_email() {
  local body_file
  local result_file
  local cmd=()
  body_file="$(mktemp)"
  result_file="$(mktemp)"
  cat > "$body_file" <<EOF
Hi Robert,

Today's AI box backup created the local snapshot successfully, but the remote push failed.

Local backup path: $dest
Remote target: $remote_target
Remote destination: $remote_dest
Remote push status: $remote_push_status

Please treat this as a backup warning until the next successful push is verified.

Codex
EOF
  cmd=(
    "$python_bin" "$warning_email_script"
    --creds-file "$warning_email_creds"
    --to "$warning_email_to"
    --subject "AI box backup warning: remote push failed on $stamp"
    --body-file "$body_file"
    --from-address "codex@kovaldistillery.com"
    --from-name "Codex Local Agent"
    --sent-log "$warning_email_sent_log"
  )
  if [ -n "$warning_email_cc" ]; then
    cmd+=(--cc "$warning_email_cc")
  fi
  if [ "$warning_email_dry_run" = "1" ]; then
    cmd+=(--dry-run)
  fi
  if "${cmd[@]}" > "$result_file"; then
    warning_email_status=$([ "$warning_email_dry_run" = "1" ] && printf 'dry_run' || printf 'sent')
    warning_email_message_id="$("$python_bin" - <<'PY' "$result_file"
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get("message_id", ""))
PY
)"
  else
    warning_email_status="failed"
  fi
  cp -f "$result_file" "$dest/status/warning-email-result.json" || true
  rm -f "$body_file" "$result_file"
}

if [ "$remote_push_error" -ne 0 ] && [ "$warning_email_enabled" != "0" ]; then
  warning_email_status="pending"
  if [ -x "$warning_email_script" ] || [ -f "$warning_email_script" ]; then
    send_warning_email || true
  else
    warning_email_status="script_missing"
  fi
fi

ln -sfn "$dest" "$backup_root/latest"
write_manifest
write_shasums
printf 'backup=%s\n' "$dest"
printf 'remote_push_status=%s\n' "$remote_push_status"
printf 'warning_email_status=%s\n' "$warning_email_status"
if [ -n "$warning_email_message_id" ]; then
  printf 'warning_email_message_id=%s\n' "$warning_email_message_id"
fi
if [ "$remote_push_error" -ne 0 ]; then
  printf 'remote_push_failed=%s\n' "$remote_target" >&2
  exit 1
fi
