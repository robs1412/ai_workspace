#!/bin/bash
set -u

log="/Users/admin/Library/Logs/koval-macmini-network-watchdog.log"
stamp="$(date '+%Y-%m-%d %H:%M:%S %Z')"
host="$(hostname 2>/dev/null || true)"
ip="$(ipconfig getifaddr en1 2>/dev/null || true)"
router_ok="fail"
board_ok="fail"

if /sbin/ping -q -c 1 -W 1000 192.168.55.1 >/dev/null 2>&1; then
  router_ok="ok"
fi

if /usr/bin/curl -fsS --max-time 5 http://127.0.0.1:17878/api/status >/dev/null 2>&1; then
  board_ok="ok"
fi

{
  printf '%s host=%s en1_ip=%s router=%s board=%s\n' "$stamp" "$host" "${ip:-none}" "$router_ok" "$board_ok"
  if [ "$router_ok" != "ok" ] || [ -z "$ip" ]; then
    /sbin/ifconfig en1 2>&1 | /usr/bin/sed 's/^/  /'
    /usr/sbin/netstat -rn -f inet 2>&1 | /usr/bin/sed 's/^/  /'
  fi
} >> "$log"
