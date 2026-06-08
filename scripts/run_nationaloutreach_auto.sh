#!/bin/sh

cycles="${NATIONALOUTREACH_CYCLES_PER_LAUNCH:-1}"
interval="${NATIONALOUTREACH_INNER_INTERVAL_SECONDS:-15}"
state_dir="${NATIONALOUTREACH_STATE_DIR:-/Users/admin/.nationaloutreach-launch/state}"
export NATIONALOUTREACH_DISABLE_WORKSPACEBOARD_ROUTES="${NATIONALOUTREACH_DISABLE_WORKSPACEBOARD_ROUTES:-1}"
export NATIONALOUTREACH_WORKER_ROUTE_LIMIT_PER_CYCLE="${NATIONALOUTREACH_WORKER_ROUTE_LIMIT_PER_CYCLE:-0}"
export NATIONALOUTREACH_ARCHIVE_REDUNDANT_OVERDUE_REPORTS="${NATIONALOUTREACH_ARCHIVE_REDUNDANT_OVERDUE_REPORTS:-1}"
export NATIONALOUTREACH_ARCHIVE_SELF_SENT_INBOX_COPIES="${NATIONALOUTREACH_ARCHIVE_SELF_SENT_INBOX_COPIES:-1}"
export NATIONALOUTREACH_ARCHIVE_REPLIED_INBOX="${NATIONALOUTREACH_ARCHIVE_REPLIED_INBOX:-1}"
script_dir="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
workspace_root="$(CDPATH= cd -- "$script_dir/.." && pwd)"
export NATIONALOUTREACH_RUNTIME_ROOT="${NATIONALOUTREACH_RUNTIME_ROOT:-$script_dir}"
lock_dir="$state_dir/nationaloutreach-cycle.lock"
lock_max_age="${NATIONALOUTREACH_CYCLE_LOCK_MAX_AGE_SECONDS:-900}"

mkdir -p "$state_dir"
if ! mkdir "$lock_dir" 2>/dev/null; then
  now="$(date +%s)"
  lock_mtime="$(stat -f %m "$lock_dir" 2>/dev/null || echo "$now")"
  lock_age=$((now - lock_mtime))
  lock_pid=""
  if [ -f "$lock_dir/pid" ]; then
    lock_pid="$(cat "$lock_dir/pid" 2>/dev/null || true)"
  fi
  if [ "$lock_age" -lt "$lock_max_age" ]; then
    echo "National Outreach cycle already running; skipping this launch." >&2
    exit 0
  fi
  if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
    kill -TERM "$lock_pid" 2>/dev/null || true
    sleep 2
    if kill -0 "$lock_pid" 2>/dev/null; then
      kill -KILL "$lock_pid" 2>/dev/null || true
    fi
  fi
  rm -f "$lock_dir/pid"
  rmdir "$lock_dir" 2>/dev/null || true
  if ! mkdir "$lock_dir" 2>/dev/null; then
    echo "National Outreach cycle lock is busy; skipping this launch." >&2
    exit 0
  fi
fi
echo "$$" > "$lock_dir/pid"
trap 'rm -f "$lock_dir/pid"; rmdir "$lock_dir" 2>/dev/null || true' EXIT INT TERM

php_bin="${PHP_BIN:-}"
if [ -z "$php_bin" ]; then
  if command -v php >/dev/null 2>&1; then
    php_bin="$(command -v php)"
  elif [ -x /usr/local/bin/php ]; then
    php_bin=/usr/local/bin/php
  elif [ -x /usr/local/opt/php@8.1/bin/php ]; then
    php_bin=/usr/local/opt/php@8.1/bin/php
  elif [ -x /opt/homebrew/bin/php ]; then
    php_bin=/opt/homebrew/bin/php
  fi
fi

count=1
last_status=0
generator_script="$script_dir/sync_day_of_cot_event_details.php"
post_tasting_generator_script="$script_dir/sync_vanessa_post_tasting_checkin.php"
open_shift_generator_script="$script_dir/sync_vanessa_open_shift_reminder.php"
mitch_weekly_generator_script="$script_dir/sync_vanessa_mitch_weekly_report.php"
marianos_cancellation_fallback_script="$workspace_root/nationaloutreach/scripts/sync_vanessa_marianos_cancellation_fallback.php"
mail_cycle_script="$script_dir/nationaloutreach_mail_cycle.py"
if [ ! -f "$generator_script" ] && [ -f "/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_day_of_cot_event_details.php" ]; then
  generator_script="/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_day_of_cot_event_details.php"
fi
if [ ! -f "$post_tasting_generator_script" ] && [ -f "/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_post_tasting_checkin.php" ]; then
  post_tasting_generator_script="/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_post_tasting_checkin.php"
fi
if [ ! -f "$open_shift_generator_script" ] && [ -f "/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_open_shift_reminder.php" ]; then
  open_shift_generator_script="/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_open_shift_reminder.php"
fi
if [ ! -f "$mitch_weekly_generator_script" ] && [ -f "/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_mitch_weekly_report.php" ]; then
  mitch_weekly_generator_script="/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_mitch_weekly_report.php"
fi
if [ ! -f "$marianos_cancellation_fallback_script" ] && [ -f "/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_marianos_cancellation_fallback.php" ]; then
  marianos_cancellation_fallback_script="/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_vanessa_marianos_cancellation_fallback.php"
fi
if [ ! -f "$mail_cycle_script" ] && [ -f "/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py" ]; then
  mail_cycle_script="/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py"
fi

while [ "$count" -le "$cycles" ]; do
  cycle_started="$(date +%s)"
  generator_status=0
  if [ -n "$php_bin" ] && [ -x "$php_bin" ]; then
    "$php_bin" "$generator_script" \
      --date "$(date +%F)" \
      --state-dir "$state_dir" || generator_status=$?
    "$php_bin" "$post_tasting_generator_script" \
      --date "$(date +%F)" \
      --state-dir "$state_dir" || generator_status=$?
    "$php_bin" "$open_shift_generator_script" \
      --date "$(date +%F)" \
      --state-dir "$state_dir" || generator_status=$?
    "$php_bin" "$mitch_weekly_generator_script" \
      --date "$(date +%F)" \
      --state-dir "$state_dir" || generator_status=$?
    if [ -f "$marianos_cancellation_fallback_script" ]; then
      if [ "${NATIONALOUTREACH_MARIANOS_CANCELLATION_QUEUE_APPROVED:-1}" = "1" ]; then
        "$php_bin" "$marianos_cancellation_fallback_script" \
          --state-dir "$state_dir" \
          --queue-approved || generator_status=$?
      else
        "$php_bin" "$marianos_cancellation_fallback_script" \
          --state-dir "$state_dir" || generator_status=$?
      fi
    fi
  else
    echo "PHP executable not found for National Outreach COT generator" >&2
    generator_status=127
  fi
  /usr/local/bin/python3.13 "$mail_cycle_script" \
    --creds-file "${NATIONALOUTREACH_CREDS_FILE:-/Users/werkstatt/ai_workspace/.private/mailboxes/nationaloutreach/credential.txt}" \
    --workspace-root "${NATIONALOUTREACH_WORKSPACE_ROOT:-/Users/werkstatt/ai_workspace/nationaloutreach}" \
    --state-dir "$state_dir" \
    --limit "${NATIONALOUTREACH_LIMIT:-250}" \
    $( [ "${NATIONALOUTREACH_ARCHIVE_REDUNDANT_OVERDUE_REPORTS}" = "1" ] && printf '%s' '--archive-redundant-overdue-reports' ) \
    $( [ "${NATIONALOUTREACH_ARCHIVE_SELF_SENT_INBOX_COPIES}" = "1" ] && printf '%s' '--archive-self-sent-inbox-copies' ) \
    $( [ "${NATIONALOUTREACH_ARCHIVE_REPLIED_INBOX}" = "1" ] && printf '%s' '--archive-replied-inbox' ) \
    --send-approved
  last_status=$?
  if [ "$generator_status" -ne 0 ] && [ "$last_status" -eq 0 ]; then
    last_status="$generator_status"
  fi
  if [ "$count" -lt "$cycles" ]; then
    now="$(date +%s)"
    elapsed=$((now - cycle_started))
    remaining=$((interval - elapsed))
    if [ "$remaining" -gt 0 ]; then
      sleep "$remaining"
    fi
  fi
  count=$((count + 1))
done

exit "$last_status"
