# IKEv2 VPN DNS For koval.lan

- Master Incident ID: `AI-INC-20260419-IKEV2-VPN-DNS-01`
- Date Opened: 2026-04-19
- Date Completed: 2026-04-19
- Owner: Robert / Codex
- Priority: High
- Status: Completed

## Scope

Read-only diagnosis and minimal runtime config change on OpenWrt `192.168.55.1` so IKEv2 VPN clients can resolve `mi.koval.lan` and `wb.koval.lan`.

## Symptoms

Robert's iPhone was connected to IKEv2 VPN as `10.57.57.12`, but Safari could not open `https://mi.koval.lan/login` or `https://wb.koval.lan/workspaceboard/`.

## Root Cause

- StrongSwan IKEv2 pool config pushed public DNS (`1.1.1.1`, `8.8.8.8`) to VPN clients.
- Router `dnsmasq` was listening on `192.168.55.1:53`, but `localservice=1` caused it to ignore DNS queries from the VPN pool `10.57.57.0/24`.
- Router DNS itself had correct host mappings for `mi.koval.lan` and `wb.koval.lan` to `192.168.55.205`.

## Runtime Logs

### OpenWrt Router

- Router: `192.168.55.1`
- Runtime config changed:
  - `dhcp.@dnsmasq[0].localservice` set to `0`
  - `/etc/swanctl/conf.d/koval-ikev2.conf` pool DNS changed to `192.168.55.1`
- Backups were created on the router with `vpn-dns` timestamp suffixes before edits.
- Commands intentionally avoided IPsec restart or tunnel termination.

## Verification Notes

- Active IKEv2 sessions remained established after the change:
  - Robert iPhone: `10.57.57.12`
  - Robert MacBook: `10.57.57.11`
  - Sonat: `10.57.57.10`
- `swanctl --load-pools` reported the IKEv2 pool loaded successfully.
- From the existing MacBook VPN session, `dig @192.168.55.1 mi.koval.lan` resolved `192.168.55.205`.
- From the existing MacBook VPN session, `dig @192.168.55.1 wb.koval.lan` resolved `192.168.55.205`.
- `https://mi.koval.lan/login` returned HTTP 200 from the MacBook.
- `https://wb.koval.lan/workspaceboard/` returned the expected HTTP 307 redirect to MI login.

## Rollback Plan

- Restore `/etc/config/dhcp` from the matching `dhcp.bak.vpn-dns-*` backup, then reload dnsmasq.
- Restore `/etc/swanctl/conf.d/koval-ikev2.conf` from the matching `koval-ikev2.conf.bak.vpn-dns-*` backup, then reload StrongSwan pools.
- If a later full IPsec restart is required, schedule it explicitly because it will interrupt VPN clients.

## Follow-Ups

- Existing clients may need to disconnect/reconnect VPN once to receive the newly pushed DNS attribute.
- Confirm on iPhone that `https://mi.koval.lan/login` opens after reconnect, then test `https://wb.koval.lan/workspaceboard/`.
