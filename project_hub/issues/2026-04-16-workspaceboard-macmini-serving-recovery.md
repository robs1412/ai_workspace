# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260416-WORKSPACEBOARD-MACMINI-SERVING-01`
- Date Opened: 2026-04-16
- Date Completed: 2026-04-16
- Owner: Codex
- Priority: High
- Status: Completed

## Scope

Recover Mac mini Workspaceboard serving at `http://192.168.55.17/workspaceboard/` while preserving Portal-auth-protected access. Work was limited to the Mac mini Workspaceboard LaunchAgent/runtime configuration and verification.

## Symptoms

- SSH to `admin-macmini` worked.
- `com.koval.workspaceboard` was running, but `/api/status` appeared unavailable under short curl timeouts.
- Node was listening only on `127.0.0.1:17878`, while the intended Mac mini serving shape required LAN bind for the classic board iframe/WebSocket path behind Portal auth.
- `Macmini.lan` did not resolve from the MacBook shell; `192.168.55.17` was reachable.

## Root Cause

The live LaunchAgent had `CODEX_DASHBOARD_HOST=127.0.0.1`, which prevented direct LAN runtime access needed by the classic Workspaceboard path. The status endpoint was also slow, returning in about 8 seconds, which made short health checks look like a hard failure.

## Repo Logs

### workspaceboard

- Repo Log ID: `WORKSPACEBOARD-MACMINI-LAUNCHAGENT-20260416`
- Commit SHA: none
- Commit Date: n/a
- Change Summary: Reinstalled the Mac mini machine-local LaunchAgent runtime from `/Users/werkstatt/workspaceboard` with `CODEX_DASHBOARD_HOST=0.0.0.0 ./scripts/install_codex_dashboard_launchagent.sh 17878`. No git commit, push, source edit, or credential exposure was performed. The Mac mini source tree already contained uncommitted Workspaceboard changes before reinstall.

## Verification Notes

- `launchctl list` showed `com.koval.workspaceboard` running after reinstall.
- `/Users/admin/Library/LaunchAgents/com.koval.workspaceboard.plist` now contains `CODEX_DASHBOARD_HOST=0.0.0.0`.
- `lsof -nP -iTCP:17878 -sTCP:LISTEN` showed Node listening on `*:17878`.
- Local runtime check `http://127.0.0.1:17878/api/status` returned `HTTP/1.1 200 OK`.
- Direct unauthenticated LAN checks to `http://192.168.55.17:17878/` and `/api/status` returned `401 Unauthorized` with a Portal login URL.
- Apache front-door check `http://192.168.55.17/workspaceboard/` returned `302 Found` to `/login/index.php?referrer=workspaceboard%2F`, confirming Portal auth protection for unauthenticated access.

## 2026-04-18 Hostname Follow-Up

- Request: make Workspaceboard reachable by a VPN-friendly name after `http://192.168.55.17/workspaceboard/` worked but `macmini.lan` did not resolve remotely.
- Diagnosis: `macmini.lan` failed from the VPN client because the active IKEv2 DNS path used public resolvers; Mac mini Apache accepted the requested host header when forced against `192.168.55.17`.
- Initial Reatan/`.205` reverse-proxy attempt failed because the credential reference was first interpreted incorrectly. Recheck showed the working SSH path is `claude@192.168.55.205` using the second line of the two-line credential reference as the password.
- Credential handling note: during structural parsing, part of the credential was accidentally printed once. Treat the `.205` Claude credential as exposed until it is rotated/replaced.
- Reatan Traefik route was then completed and later shortened to `wb.koval.lan`:
  - config: `/srv/traefik/dynamic.yml`
  - backup: `/srv/traefik/dynamic.yml.bak.workspaceboard-20260418-080809`
  - short-host backup: `/srv/traefik/dynamic.yml.bak.wb-koval-lan-*`
  - route: `wb.koval.lan` on web/websecure, with `workspaceboard.koval.lan` retained as a compatibility alias
  - middleware: `mi-auth`
  - service: `workspaceboard-macmini -> http://192.168.55.17`
  - Traefik container restarted to load the updated bind-mounted file
- Router local DNS was updated:
  - backup: `/etc/hosts.bak.workspaceboard-koval-lan-20260418-075414`
  - later proxy backup: `/etc/hosts.bak.workspaceboard-proxy-20260418-081001`
  - short-host backup: `/etc/hosts.bak.wb-koval-lan-*`
  - current mapping: `wb.koval.lan workspaceboard.koval.lan -> 192.168.55.205`
  - current mapping: `wb-direct.koval.lan -> 192.168.55.17`
  - restarted `dnsmasq`
- Router-local verification now resolves:
  - `wb.koval.lan -> 192.168.55.205`
  - `workspaceboard.koval.lan -> 192.168.55.205`
  - `wb-direct.koval.lan -> 192.168.55.17`
- Backend verification: Mac mini Apache accepts the forwarded host and returns a Workspaceboard wrapper when trusted `X-User-*` headers arrive from Reatan `192.168.55.205`.
- HTTPS proxy verification: unauthenticated `https://wb.koval.lan/workspaceboard/` resolves to Reatan/`.205`, uses the trusted `*.koval.lan` mkcert certificate, and redirects to `https://mi.koval.lan/login?redirect=...`.
- Mac mini live source update:
  - file backups: `index.php.bak.forward-auth-20260418-082717`, `workspaceboard_auth.php.bak.forward-auth-20260418-082717`, and `index.php.bak.wb-koval-lan-*`
  - `workspaceboard_auth.php` trusts `X-User-*` headers only from Reatan `192.168.55.205` and bypasses the timed-out legacy `/login/checklogin.php` portal-api path after `mi-auth` succeeds.
  - `index.php` maps Reatan-authenticated requests for `wb.koval.lan` or `workspaceboard.koval.lan` to iframe/runtime origin `http://wb-direct.koval.lan:17878/`.
  - `/usr/local/bin/php -l index.php` and `/usr/local/bin/php -l workspaceboard_auth.php` pass on the Mac mini.
- Simulated authenticated verification from Reatan to Mac mini returned `200 OK` and iframe `http://wb-direct.koval.lan:17878/`.
- Follow-up direct-HTTP lockout:
  - `workspaceboard_auth.php` now denies non-local, non-Reatan-forward-auth requests before the legacy Portal session path and returns `403` with the instruction to use `https://wb.koval.lan/workspaceboard/`.
  - Verified `http://192.168.55.17/workspaceboard/` returns `403 Forbidden`.
  - Localhost remains allowed; remote HTTPS access must arrive through Reatan `192.168.55.205` with trusted `mi-auth` headers.
- Follow-up runtime HTTPS proxy:
  - A first Traefik runtime/root redirect attempt caused the existing Traefik container to enter an exit `137` restart loop. The file was restored and only the Traefik container was recreated from `/srv/traefik/docker-compose.yml`; no other containers were recreated.
  - The stable dynamic file now keeps `wb.koval.lan` and `workspaceboard.koval.lan` on the Workspaceboard Mac mini service with `mi-auth`.
  - Added `/wb-runtime` routers with `mi-auth` and `stripPrefix` to proxy `https://wb.koval.lan/wb-runtime/` to `http://192.168.55.17:17878`.
  - Added root `/api/*` and `/ws` routers for `wb.koval.lan` / `workspaceboard.koval.lan` to the same MI-authenticated runtime service because Workspaceboard frontend requests use root API paths.
  - The live Node runtime source and installed runtime copy trust `X-User-*` only from Reatan `192.168.55.205` for allowlisted users `1` and `165`; localhost remains allowed.
  - Verified unauthenticated `https://wb.koval.lan/wb-runtime/api/status` and `https://wb.koval.lan/api/management/overview` redirect to MI login, and simulated Reatan-authenticated runtime API access returns `200 OK`.
- MacBook local `/etc/hosts` was updated via macOS administrator prompt:
  - backup: `/etc/hosts.bak.workspaceboard-koval-lan-20260418-080230`
  - proxy update backup: `/etc/hosts.bak.workspaceboard-proxy-20260418-081007`
  - dedupe backup: `/etc/hosts.bak.workspaceboard-dedupe-20260418-081041`
  - short-host backup: `/etc/hosts.bak.wb-koval-lan-*`
  - current mapping: `wb.koval.lan workspaceboard.koval.lan -> 192.168.55.205`
  - current mapping: `wb-direct.koval.lan -> 192.168.55.17`
  - `https://wb.koval.lan/workspaceboard/` returns the expected MI login redirect
- Remaining browser follow-up: if the page returns after MI login but the board iframe is blank, the likely blocker is browser mixed-content handling for the HTTP runtime iframe. The durable fix would be an HTTPS proxy for the runtime as well.
- Remaining network-wide follow-up: other VPN clients still need either their own local hosts entry or a deliberate IKEv2/router DNS change to use router DNS for internal names.

## Rollback Plan

Reinstall the LaunchAgent with localhost-only binding if LAN runtime exposure must be disabled:

```bash
cd /Users/werkstatt/workspaceboard
CODEX_DASHBOARD_HOST=127.0.0.1 ./scripts/install_codex_dashboard_launchagent.sh 17878
```

## Follow-Ups

- Review the preexisting dirty `/Users/werkstatt/workspaceboard` source tree before any commit or deploy coordination.
- Consider reducing `/api/status` latency or increasing health-check timeouts so an 8-second successful response is not misclassified as an outage.
