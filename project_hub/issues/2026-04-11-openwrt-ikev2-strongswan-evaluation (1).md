# Incident / Project Slice Log
Last Updated: 2026-04-12 10:31:48 CDT (Machine: RobertMBP-2.local)

- Master Incident ID: `AI-INC-20260411-OPENWRT-IKEV2-STRONGSWAN-01`
- Date Opened: `2026-04-11 15:57:44 CDT`
- Date Completed: `2026-04-11 16:37:08 CDT`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Completed / IKEv2 verified as primary-capable with WireGuard retained as fallback`

## Scope

Evaluate replacing or supplementing the unstable Mac WireGuard path with OpenWrt-hosted IPsec/IKEv2 via StrongSwan, with native iOS/macOS/Android/Windows client compatibility as a goal.

## Symptoms

- WireGuard has a prior open stability incident under `AI-INC-20260315-WIREGUARD-STABILITY-01`.
- User requested trying IPsec/IKEv2 via StrongSwan on the OpenWrt router as a non-WireGuard VPN path.

## Root Cause

Not applicable yet for IKEv2. Prior WireGuard investigation pointed toward a macOS WireGuard/NetworkExtension data-plane stall rather than a router-side WireGuard root cause.

## Repo Logs

### ai_workspace / OpenWrt Router

- Repo Log ID: `OPENWRT-IKEV2-20260411-DISCOVERY-01`
- Commit SHA:
- Commit Date:
- Change Summary:
  - Performed read-only SSH discovery against OpenWrt at `192.168.55.1`.
  - Confirmed OpenWrt `24.10.5` on target `mvebu/cortexa9`.
  - Confirmed StrongSwan/IPsec packages are not installed.
  - Confirmed WireGuard remains configured on `wg0`/`51820` and `wgmac`/`51821`.
  - Confirmed existing firewall rules include legacy IPsec ESP and UDP `500`, but no visible UDP `4500` NAT-T allow rule in the filtered read-only view.

## Verification Notes

- Local default route at discovery time was through WireGuard `utun6`.
- SSH to `192.168.4.1:22` was refused.
- SSH to `192.168.55.1:22` succeeded through the current tunnel.
- Router WAN public address in read-only status output was `205.178.117.216`.
- Router storage/memory appeared adequate for package evaluation: overlay roughly `50.6M` available, memory roughly `275M` available.
- Initial read-only discovery made no router configuration, package install, firewall reload, or service restart changes.
- 2026-04-11 16:00-16:08 CDT changes:
  - Backed up router config to `/root/codex-backups/ikev2-20260411-160059`.
  - Installed StrongSwan package set including `strongswan-default`, `strongswan-swanctl`, `strongswan-pki`, EAP-MSCHAPv2 support, OpenSSL/GCM modules, and IPsec kernel modules.
  - Generated CA/server certificates for remote ID `vpn.koval-distillery.local`.
  - Moved the CA private signing key out of `/etc/swanctl/private` to `/root/codex-backups/ikev2-ca/koval-ikev2-ca-key.pem` so the runtime only loads the server key.
  - Created `swanctl` connection `koval-ikev2`.
  - Created EAP user `robert`; secret is stored locally in `.private/ikev2/robert-eap-secret.txt` and on router in `/etc/swanctl/conf.d/koval-ikev2.secrets.conf`.
  - Added firewall rules `Allow-IKEv2-IKE`, `Allow-IKEv2-NAT-T`, `Allow-IKEv2-ESP`, `Allow-IKEv2-Pool-to-LAN`, and `Allow-IKEv2-Pool-to-WAN`.
  - `fw4 check` passed and firewall reload completed.
  - `swanctl --load-all` loaded one pool and one connection.
  - `charon` listens on UDP `500` and `4500` for IPv4 and IPv6.
  - No active IKE SAs yet; client-side test remains pending.
- Public CA certificate exported locally:
  - `.private/ikev2/koval-ikev2-ca-cert.pem`
  - `.private/ikev2/koval-ikev2-ca-cert.cer`
  - SHA-256 fingerprint: `5B:56:F6:22:D1:92:96:37:52:31:D5:3D:3E:9C:48:36:4B:9C:82:92:F2:94:2C:84:7B:F7:08:C0:46:F2:6B:21`
- 2026-04-11 16:09-16:18 CDT Mac client setup:
  - Generated `.private/ikev2/KOVAL-IKEv2.mobileconfig` and `.private/ikev2/KOVAL-IKEv2.redacted.mobileconfig`.
  - User installed profile `com.koval.ikev2`; `profiles` confirms it is installed for user `robert`.
  - `scutil --nc list` does not expose a `KOVAL IKEv2` service yet, so `scutil --nc start "KOVAL IKEv2"` returns `No service`.
  - Attempted System Settings UI automation to toggle the VPN, but macOS blocked Apple Events to System Events with `Not authorized ... (-1743)`.
  - Current next step is a manual user toggle in System Settings > VPN while router logs are monitored.
  - First Mac attempt failed. macOS reported `PeerDidNotRespond` / `The VPN server did not respond`; router log showed the Mac reached StrongSwan but `IKE_AUTH` failed because `KDF_PRF with PRF_HMAC_SHA2_256 not supported`.
  - Installed missing package `strongswan-mod-kdf`, restarted `swanctl`, and reloaded the connection. StrongSwan remains running/listening on UDP `500` and `4500`.
  - Second Mac attempt connected and received `ipsec0` address `10.57.57.10`. LAN ping to `192.168.55.1` succeeded through `ipsec0`, but DNS/public internet traffic timed out.
  - Added WAN masquerade source restriction `firewall.@zone[1].masq_src='10.57.57.0/24'`, ran `fw4 check`, and reloaded firewall. Reconnect/retest is pending because the firewall reload cleared the active IKEv2 SA.
  - After reconnect, raw public IP traffic worked: `ping 1.1.1.1` succeeded through `ipsec0`, but DNS to router `192.168.55.1` still timed out.
  - Changed `koval-ikev2-pool` DNS from `192.168.55.1` to `1.1.1.1, 8.8.8.8` and reloaded StrongSwan pools/connections. Client reconnect is pending to pick up the new DNS attributes.
  - 2026-04-11 16:27:03 CDT: user confirmed the IKEv2 tunnel is working. Local verification showed `ipsec0` address `10.57.57.10`, DNS `1.1.1.1` / `8.8.8.8`, and public IP `205.178.117.216`.
  - Opened `/System/Library/CoreServices/Menu Extras/VPN.menu`; `com.apple.systemuiserver` now lists `/System/Library/CoreServices/Menu Extras/VPN.menu` in `menuExtras`.
  - 2026-04-11 16:37:08 CDT: configured Sonat IKEv2 access after explicit approval.
  - Created router EAP user `sonat`; the secret is stored locally in `.private/ikev2/sonat-eap-secret.txt` and on router in `/etc/swanctl/conf.d/koval-ikev2.secrets.conf`.
  - Created Sonat macOS profile `.private/ikev2/KOVAL-IKEv2-Sonat.mobileconfig` and redacted review copy `.private/ikev2/KOVAL-IKEv2-Sonat.redacted.mobileconfig`; both pass `plutil -lint`.
  - Loaded router credentials with `swanctl --load-creds`; output confirmed `eap-robert` and `eap-sonat` loaded.
  - Per the user's direction, the Sonat router change did not use the old WireGuard config. Direct router SSH over IKEv2 refused on `192.168.55.1:22`, so management used the working IKEv2 tunnel to `admin-macmini` and a temporary SSH local forward to router SSH.
  - 2026-04-11 16:44:10 CDT: user reported Sonat profile stuck on connecting. Router diagnostics showed Sonat was established, not auth-failing: EAP identity `sonat`, EAP-MSCHAPv2 success, virtual IP `10.57.57.11`, CHILD_SA installed, and packet counters increasing.
  - 2026-04-11 16:56:07 CDT: created separate MacBook credential/profile `robert-macbook` so this MacBook does not share the phone or original Robert profile. Password is stored locally in `.private/ikev2/robert-macbook-eap-secret.txt`; profile is `.private/ikev2/KOVAL-IKEv2-Robert-MacBook.mobileconfig`; redacted review copy is `.private/ikev2/KOVAL-IKEv2-Robert-MacBook.redacted.mobileconfig`.
  - Added router EAP secret `eap-robert-macbook` via the IKEv2-to-`admin-macmini` management path and reloaded credentials; `swanctl --load-creds` confirmed `eap-robert`, `eap-sonat`, and `eap-robert-macbook`.
  - 2026-04-11 17:00:54 CDT: created additional per-person IKEv2 credentials/profiles matching the WireGuard access group: `sebastian`, `dmytro`, and `mark`.
  - Password files are stored locally in `.private/ikev2/sebastian-eap-secret.txt`, `.private/ikev2/dmytro-eap-secret.txt`, and `.private/ikev2/mark-eap-secret.txt`.
  - Profiles are stored locally in `.private/ikev2/KOVAL-IKEv2-Sebastian.mobileconfig`, `.private/ikev2/KOVAL-IKEv2-Dmytro.mobileconfig`, and `.private/ikev2/KOVAL-IKEv2-Mark.mobileconfig`, with redacted review copies alongside them.
  - Added router EAP secrets `eap-sebastian`, `eap-dmytro`, and `eap-mark` via the IKEv2-to-`admin-macmini` management path and reloaded credentials; `swanctl --load-creds` confirmed all six current EAP secrets: `eap-robert`, `eap-sonat`, `eap-robert-macbook`, `eap-sebastian`, `eap-dmytro`, and `eap-mark`.
  - Removed temporary router upload files from `/tmp`, including a leftover `/tmp/sonat-eap-secret.txt` from the prior Sonat setup.
  - 2026-04-11 17:15:21 CDT: user reported bar iPads connecting but not receiving data. Found the WAN zone still had the VPN-specific source NAT restriction `masq_src='10.57.57.0/24'`, which could prevent normal LAN-to-WAN NAT for non-VPN clients. Removed that restriction, committed firewall config, passed `fw4 check`, and reloaded firewall. WAN source NAT now shows normal unrestricted IPv4 masquerading for the WAN zone.
  - Post-fix snapshot: `62` DHCP leases, `96` non-failed LAN neighbor entries, and `2` active IKEv2 SAs (`robert`, `sonat`). `BariPad2` (`192.168.55.220`) and Square POS devices (`192.168.55.217`, `192.168.55.218`) responded to ping; `BariPad1` (`192.168.55.219`) and `BariPad3` (`192.168.55.152`) did not respond to ping from the VPN path.
  - 2026-04-11 17:52-17:54 CDT: user reported Sonat cannot get into the VPN after the bar iPad fix. Local MacBook IKEv2 tunnel still had `ipsec0` address `10.57.57.10` and could ping router `192.168.55.1`. Direct router SSH from MacBook over IKEv2 was still refused, matching earlier behavior. `admin-macmini` was reachable and could reach router SSH on `192.168.55.1:22`, but non-interactive router SSH authentication failed from the current credential path, so live `swanctl --list-sas` / `logread` inspection could not be completed without refreshed router management auth or local console access. No router config changes were made during this follow-up.
  - 2026-04-12 06:48-06:50 CDT (Machine: RobertMBP-2.local): user enabled WireGuard, which made router SSH at `192.168.55.1:22` reachable from MacBook again.
  - Router logs showed active IKEv2 SAs for `robert` / `robert-macbook`; `robert-macbook` received `10.57.57.12` and later went offline when WireGuard was enabled, while the remaining active SA showed `remote 10.57.57.10/32`.
  - Router DHCP leases showed `192.168.55.17 Macmini`, but router neighbor table marked both `192.168.55.16` and `192.168.55.17` as `FAILED`; router-side ping to `192.168.55.17` failed, so the Mac mini was not reachable on LAN from the router at that moment.
  - Added firewall backup `/root/codex-backups/ikev2-mgmt-20260412-064921/firewall`, then added `Allow-IKEv2-Pool-to-Router-SSH` for source `10.57.57.0/24` to router-local TCP `22`; `fw4 check` passed and firewall reloaded.
  - Added firewall backup `/root/codex-backups/ikev2-router-access-20260412-065009/firewall`, then added broader `Allow-IKEv2-Pool-to-Router` for source `10.57.57.0/24` to router-local `proto all`; `fw4 check` passed and firewall reloaded. This was to ensure IKEv2 clients have router management access, matching WireGuard's intended management behavior.
  - Credential handling correction: moved the local router credential reference from root-level `router.md` into `.private/router/openwrt-root-password.txt` and replaced `router.md` with a non-secret pointer. A credential-looking value had been exposed during attempted redaction, so rotation was attempted. Rotation did not complete cleanly; the current private reference no longer authenticated afterward, blank password did not work, and local SSH keys did not work. Router management access is currently blocked until the current router password is recovered/reset through local console/LuCI or another valid management path.
  - 2026-04-12 08:52-08:53 CDT (Machine: RobertMBP-2.local): investigation-only parity check made no router/firewall/VPN configuration or credential changes. The KOVAL IKEv2 profile was installed locally (`com.koval.ikev2.robert-macbook`), but the IKEv2 tunnel was not active: no `ipsec0` interface appeared and `scutil --nc list` did not expose a startable IKEv2 service. WireGuard `koval-robert-wg0-fresh` was also disconnected. Route checks sent `192.168.55.1` via `en0` through local gateway `192.168.4.1`, so the failed ping and TCP `22`/`80`/`443` timeouts were not valid IKEv2-path failures. TCP `53` connected, and public IP was `168.91.196.90` rather than router WAN IP `205.178.117.216`. Parity verification remains blocked until Robert manually enables IKEv2 or approves/provides another startable client path, then the route/interface/reachability probes can be rerun.
  - 2026-04-12 10:08-10:12 CDT (Machine: RobertMBP-2.local): resumed after Robert updated the router password reference. Created dedicated local key `~/.ssh/id_ed25519_openwrt_192_168_55_1`, authenticated once using `.private/router/openwrt-root-password.txt`, backed up `/etc/dropbear/authorized_keys` to `/root/codex-backups/sshkey-20260412-100945/authorized_keys`, appended only the public key, and verified key-only BatchMode SSH. Added local SSH aliases `koval-openwrt` and `openwrt-router` in `~/.ssh/config`. Router password was not changed/reset and no secret was printed.
  - 2026-04-12 10:10-10:12 CDT read-only VPN snapshot: this MacBook is currently on WireGuard, not IKEv2. Local route to `192.168.55.1` uses `utun7`; `utun7` address is `10.55.55.10`; public IP is `205.178.117.216`. Router `wg0` shows the `10.55.55.10/32` peer with a fresh handshake, while `swanctl --list-sas` shows no active IKEv2 SA. StrongSwan/charon is running and listening on UDP `500` and `4500`; `swanctl --list-conns` shows `koval-ikev2` with pool `10.57.57.10-10.57.57.60`, DNS `1.1.1.1, 8.8.8.8`, and `local_ts = 0.0.0.0/0`. Firewall rules are present for IKEv2 WAN entry (`500`, `4500`, ESP) and source `10.57.57.0/24` to router/LAN/WAN; nft counters show historical IKEv2 pool traffic and `fw4 check` passes. No firewall, VPN, StrongSwan, WireGuard, or network service reload/restart was performed.
  - Stop point: the router-side read-only evidence does not identify a clear low-risk router change. The remaining discrepancy cannot be closed from the current state because the MacBook is on WireGuard and no `ipsec0` path exists. Next valid parity test requires Robert to manually switch/enable the KOVAL IKEv2 profile, or provide an approved startable IKEv2 client path, then rerun route/interface/ping/port probes without disrupting current key-based router management access.
  - 2026-04-12 10:31 CDT: Robert manually connected IKEv2 and immediate parity probes passed. Local `ipsec0` was present with address `10.57.57.12`, matching the expected `10.57.57.0/24` pool; `scutil --nc list` showed WireGuard `koval-robert-wg0-fresh` disconnected. Route checks to `192.168.55.1`, `192.168.55.205`, `1.1.1.1`, `10.57.57.1`, and `10.55.55.1` all used `ipsec0`. Public IP was `205.178.117.216`. Router reachability over IKEv2 passed for ping and TCP `22`, `53`, `80`, and `443`. Key SSH through both `koval-openwrt` and `openwrt-router` succeeded.
  - Router `swanctl --list-sas` showed `koval-ikev2` established for EAP identity `robert-macbook`, remote virtual IP `10.57.57.12/32`, `local 0.0.0.0/0`, and packet counters increasing. `swanctl --list-pools` showed `koval-ikev2-pool 10.57.57.10` with `1 / 2 / 51`, confirming one active lease from the expected IKEv2 pool. Firewall nft counters showed IKEv2 source-pool hits for router SSH, router-local, LAN, and WAN rules. Router WireGuard still showed recent peer handshake history for `10.55.55.10/32`, but the local route in this test used `ipsec0`, not WireGuard.
  - No WireGuard disable, firewall reload, VPN reload, StrongSwan restart, router password change, or other disruptive router/client change was performed. Result: IKEv2 can replace WireGuard as the primary MacBook path; WireGuard should remain configured as fallback.

## Rollback Plan

Before any approved StrongSwan change:

- Back up `/etc/config/firewall`, `/etc/config/network`, `/etc/ipsec.conf`, `/etc/ipsec.secrets`, and `/etc/swanctl` when present.
- Keep current WireGuard management access active until IKEv2 is verified from a client.
- Avoid restarting network/firewall services until syntax and package state are verified.
- If IKEv2 changes break access, use the existing WireGuard route or local LAN access to restore the pre-change backups.

## Follow-Ups

- Client settings are recorded in `.private/ikev2/CLIENT-SETUP.md`.
- Share Sonat's profile and password through an approved secure channel; do not paste the secret in chat.
- Keep per-device/per-person profiles separate where practical (`robert`, `robert-macbook`, `sonat`, `sebastian`, `dmytro`, `mark`) so individual devices or users can be revoked without breaking others.
- If client auth fails, inspect `logread | grep -Ei 'charon|ike|eap|mschap'` on the router while attempting connection.
- If a future client can authenticate but cannot pass traffic, first confirm it received DNS `1.1.1.1` / `8.8.8.8` and an address from `10.57.57.10-10.57.57.60`.
