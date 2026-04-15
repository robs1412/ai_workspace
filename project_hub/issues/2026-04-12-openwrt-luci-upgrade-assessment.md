# OpenWrt LuCI Upgrade Assessment

- Master Incident ID: `AI-INC-20260412-OPENWRT-LUCI-UPGRADE-01`
- Last Updated: 2026-04-13 21:32:14 CDT (Machine: Macmini.lan)
- Date Opened: 2026-04-12
- Owner: Codex / Robert approval gate
- Priority: High, network infrastructure
- Status: Validation-only staging complete; live preservation refresh captured; no upgrade/reload/reboot approved

## Scope

Assess the ToDo-append task to update the router to the latest OpenWrt and LuCI. This assessment is intentionally read-only: no firmware/package upgrades, backup creation, firewall reloads, VPN reloads, or router reboots were performed.

## Current Router State

- SSH alias used: `koval-openwrt`
- Device: Linksys WRT3200ACM
- OpenWrt target: `mvebu/cortexa9`
- Board name: `linksys,wrt3200acm`
- Current OpenWrt: `24.10.5` / `r29087-d9c5716d1d`
- Kernel: `6.6.119`
- Rootfs: `squashfs`
- LuCI packages are installed, including `luci`, `luci-ssl`, `luci-base`, `luci-app-firewall`, and `luci-app-package-manager`.
- Attended upgrade helpers `auc`, `owut`, and `luci-app-attendedsysupgrade` were not installed in the read-only package check.

## Latest Compatible Versions

- Latest same-series release found from official OpenWrt announcement: `24.10.6`.
- Latest stable release found from official OpenWrt announcement: `25.12.2`.
- Official `25.12.2` downloads include a compatible `mvebu/cortexa9` Linksys WRT3200ACM sysupgrade image: `linksys_wrt3200acm-squashfs-sysupgrade.bin`.
- Risk note: OpenWrt `25.12` switches from `opkg` to `apk`, so this should be treated as a major branch upgrade, not a routine LuCI package refresh.

## Active IKEv2 / Management Path

- Mac-side at `2026-04-12 11:06:43 CDT`: `ipsec0` is up with local address `10.57.57.12`; route to `192.168.55.1` uses `ipsec0`; public IP is `205.178.117.216`.
- `scutil --nc list` showed WireGuard `koval-robert-wg0-fresh` disconnected.
- Router-side `swanctl --list-sas` showed active IKEv2 SAs for `robert-macbook` (`10.57.57.12`) and `sonat` (`10.57.57.11`).
- Any router reboot or VPN/firewall reload can disrupt the current management path. Keep WireGuard and local/LAN recovery available until post-upgrade IKEv2 verification passes.

## Backup / Rollback Requirements

- `sysupgrade -l` lists the config set that would be backed up, including `/etc/config/firewall`, `/etc/config/network`, `/etc/config/wireless`, `/etc/config/uhttpd`, `/etc/config/luci`, `/etc/dropbear/authorized_keys`, `/etc/swanctl/*`, `/etc/strongswan.d/*`, and related keys/certs.
- Before any approved upgrade, create and copy off-router a sysupgrade backup that includes installed package list metadata, plus a separate manual export of the IKEv2/StrongSwan and Dropbear/SSH-critical files.
- Validate the exact target image before flashing with `sysupgrade -T`. Do not use `-F` unless Robert explicitly approves after seeing the exact validation failure.
- Rollback should account for the Linksys dual-partition layout. Current read-only boot env showed `boot_part=1`; confirm alternate partition status and recovery method before a major upgrade.

## Proposed Maintenance Plan

1. Choose target version:
   - Conservative path: OpenWrt `24.10.6` same-series service update for security fixes and lower migration risk.
   - Major path: OpenWrt `25.12.2` latest stable, with higher migration risk due to `opkg` to `apk` and branch-level changes.
2. Pick a maintenance window when Robert has local or alternate network recovery available.
3. Take and export backups before touching firmware or packages.
4. Download the exact Linksys WRT3200ACM `mvebu/cortexa9` sysupgrade image and verify hash.
5. Run image validation only, then stop for review if any warning appears.
6. After explicit Robert approval, run the upgrade during the maintenance window.
7. Verify router LAN, WAN, LuCI, SSH aliases, IKEv2, WireGuard fallback, DNS, and public IP path after reboot.

## 25.12.2 No-Flash Runbook For Tuesday 2026-04-14 10:00 CDT

Robert decision at `2026-04-12 11:27 CDT`: evaluate the larger OpenWrt `25.12.2` upgrade path first and target Tuesday `2026-04-14 10:00 CDT` for the maintenance/evaluation slot. This runbook is preparation only. It does not approve or perform a firmware flash, package upgrade, firewall reload, VPN reload, or reboot.

### Compatibility Verification

- Current router read-only facts: Linksys WRT3200ACM, board `linksys,wrt3200acm`, OpenWrt target `mvebu/cortexa9`, current OpenWrt `24.10.5`, rootfs `squashfs`, boot env `boot_part=1`.
- Official OpenWrt `25.12.2` `profiles.json` includes profile `linksys_wrt3200acm` with supported devices `linksys,wrt3200acm`, `armada-385-linksys-rango`, and `linksys,rango`.
- Correct image candidate for an in-place OpenWrt upgrade is `openwrt-25.12.2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`, SHA256 `cf1ab7a2cafd6e317afc76cf1653be774474ba9ca3f74e6cdf5bd26118c4640c`, size `9257608` bytes.
- Do not use the factory image for this in-place OpenWrt-to-OpenWrt upgrade path.
- Official `25.12.2` release notes say upgrades from `24.10` to `25.12` should be transparent on most devices, but this must still be validated on this router because the current VPN management path depends on non-default packages and configuration.

### Migration Risk From 24.10.5 To 25.12.2

- Branch jump: `24.10.5` to `25.12.2`, not a same-series service update.
- Package manager change: OpenWrt `25.12` moved from `opkg` to `apk`. That affects package listing, reinstall commands, and package preservation tooling.
- Package preservation risk: the plain official sysupgrade image can preserve configuration, but it should not be assumed to preserve every currently installed non-default package in the firmware image.
- Current installed package count from read-only router check: `251`.
- Current critical packages include LuCI, `uhttpd`, `dnsmasq`, `dropbear`, `firewall4`, `nftables-json`, `kmod-wireguard`, `wireguard-tools`, and a broad StrongSwan set including `strongswan`, `strongswan-default`, `strongswan-swanctl`, `strongswan-pki`, and required EAP/crypto modules.
- Official `25.12.2` target build config includes LuCI, `luci-ssl`, `luci-app-attendedsysupgrade`, and `owut` by default for this target set. Current router does not have `owut`, `auc`, or `luci-app-attendedsysupgrade` installed.
- Highest operational risk: a plain post-upgrade boot may preserve IKEv2/WireGuard config files but lack the required StrongSwan/WireGuard packages until they are reinstalled or included in a custom image. Do not rely on VPN remote management as the only recovery path.

### Backup / Export Plan

Before any approved upgrade, create and copy backups off-router. Do not print secrets in chat or logs.

1. Create a timestamped local folder on this MacBook under an approved private path, for example `.private/router/openwrt-upgrade-20260414-1000/`.
2. Capture non-secret metadata: `/etc/openwrt_release`, `ubus call system board`, `df -h`, `/proc/mtd`, `fw_printenv boot_part bootcount upgrade_available` when available, `sysupgrade -l`, `opkg list-installed`, and interface/service summaries without secrets.
3. Create a sysupgrade backup with installed package metadata using `sysupgrade -k -b /tmp/<timestamp>-sysupgrade-backup.tar.gz`, then copy it off-router to the private local folder.
4. Separately export critical config/credential-bearing paths into the private folder only, without displaying contents: `/etc/config/network`, `/etc/config/firewall`, `/etc/config/wireless`, `/etc/config/dhcp`, `/etc/config/dropbear`, `/etc/config/uhttpd`, `/etc/config/luci`, `/etc/dropbear/authorized_keys`, `/etc/swanctl/`, `/etc/strongswan.d/`, and `/etc/nftables.d/`.
5. Generate a local manifest of backup filenames, sizes, and hashes. Do not include secret file contents.
6. Confirm at least one non-VPN recovery path before upgrade approval: local LAN access, physical access, alternate partition boot plan, or another verified management route.

### Image / Hash Validation Plan

1. Download only from the official target path: `https://downloads.openwrt.org/releases/25.12.2/targets/mvebu/cortexa9/openwrt-25.12.2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`.
2. Fetch official hashes from `https://downloads.openwrt.org/releases/25.12.2/targets/mvebu/cortexa9/sha256sums`.
3. Verify the local SHA256 exactly equals `cf1ab7a2cafd6e317afc76cf1653be774474ba9ca3f74e6cdf5bd26118c4640c`.
4. After explicit approval for validation-only router staging, copy the image to `/tmp/` on the router and run `sysupgrade -T /tmp/openwrt-25.12.2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`.
5. Stop if `sysupgrade -T` reports any board mismatch, compatibility warning, forced-upgrade requirement, partition warning, or package/config warning. Do not use `-F` without a separate explicit Robert approval.

### Package Preservation Plan

Preferred path for the Tuesday slot: evaluate whether to build a custom `25.12.2` image that includes the current critical non-default packages rather than flashing the plain sysupgrade image.

- Critical package groups to preserve or reinstall immediately:
- Router management: `dropbear`, LuCI, `uhttpd`, `uhttpd-mod-ubus`, `rpcd`/LuCI dependencies.
- Firewall/routing: `firewall4`, nftables components, `dnsmasq`.
- WireGuard fallback: `kmod-wireguard`, `wireguard-tools`, `luci-proto-wireguard`.
- IKEv2: `strongswan`, `strongswan-default`, `strongswan-swanctl`, `strongswan-pki`, EAP-MSCHAPv2, VICI, kernel-netlink, KDF, crypto, X.509, and related modules currently installed.
- Because `25.12` uses `apk`, package names and dependency behavior must be checked against the `25.12.2` package index/custom image builder before flash approval.
- If a custom image cannot be validated cleanly, the safer alternative is to postpone the `25.12.2` flash or require local/LAN access and a post-boot reinstall plan that does not depend on IKEv2/WireGuard being available.

### Dual-Partition Rollback / Recovery Plan

- Current read-only boot env shows `boot_part=1`.
- The router uses a dual-firmware layout. `sysupgrade -h` shows `-s` can stay on the current partition for dual-firmware devices, but the final choice must be deliberate.
- Before upgrade approval, confirm current and alternate partition status, whether the upgrade will write the alternate partition or stay on current partition, the exact command or physical power-cycle sequence to boot the previous partition if the new image fails, and whether boot counter variables are available on this device.
- Lower remote-risk default: keep the known-good partition bootable and write the new image to the alternate partition if the device/image path supports that cleanly.
- Avoid any command that overwrites both partitions or makes the known-good `24.10.5` path unrecoverable without physical access.

### Post-Upgrade Verification Checklist

Run only after a separately approved upgrade/reboot.

1. Local reachability: ping `192.168.55.1`, SSH through `koval-openwrt` and `openwrt-router`, confirm `/etc/openwrt_release` reports `25.12.2`, and confirm `ubus call system board` still reports `linksys,wrt3200acm` and `mvebu/cortexa9`.
2. LuCI: verify HTTP/HTTPS to the router admin endpoint and confirm LuCI login works without exposing credentials.
3. WAN/public internet: confirm WAN interface up, router/client DNS works, and public IP is still `205.178.117.216` or the expected current WAN address.
4. Firewall: verify firewall service/rules include existing WAN/LAN/VPN allowances, including IKEv2 UDP `500`, UDP `4500`, ESP, IKEv2 pool to LAN/WAN, and WireGuard fallback rules.
5. IKEv2: verify StrongSwan/charon running, `swanctl --list-conns`, `swanctl --list-pools`, and `swanctl --list-sas` are sane, Mac route to `192.168.55.1` uses `ipsec0`, and the client gets an expected `10.57.57.0/24` pool address.
6. WireGuard fallback: verify WireGuard interface exists, expected peer config is present, and fallback tunnel can connect if needed.
7. Client path: verify Mac public IP, LAN reachability to `192.168.55.1`, DNS checks, and TCP checks for router `22`, `53`, `80`, and `443`.
8. Rollback readiness: do not erase backups until both VPN and local access paths are stable; if VPN packages/config are missing, fix from local/LAN path or roll back to the known-good partition.

## Validation-Only Staging Results

Robert approval update: backup creation and validation-only staging are approved for the Tuesday `2026-04-14 10:00 CDT` maintenance/evaluation slot. This remains not approved for firmware flash, reboot, firewall reload, VPN reload, or StrongSwan/WireGuard restart.

Completed at `2026-04-12 11:53:23 CDT`:

- Used the existing private router root: `.private/router`.
- Created staging folder: `.private/router/openwrt-upgrade-20260414-1000`.
- Downloaded official OpenWrt files into `.private/router/openwrt-upgrade-20260414-1000/official/`:
  - `openwrt-25.12.2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`
  - `sha256sums`
  - `profiles.json`
  - `config.buildinfo`
  - `target-index.html`
  - target/package feed index snapshots under `official/package-feeds/`
- Verified image hash against official `sha256sums`; expected and observed SHA256 is `cf1ab7a2cafd6e317afc76cf1653be774474ba9ca3f74e6cdf5bd26118c4640c`.
- Created private off-router backups in `.private/router/openwrt-upgrade-20260414-1000/router-backups/`:
  - `openwrt-20260414-1000-sysupgrade-backup.tar.gz`
  - `openwrt-20260414-1000-critical-config.tar.gz`
  - `openwrt-20260414-1000-remote-backup-sha256sums.txt`
- Created non-secret metadata snapshots in `.private/router/openwrt-upgrade-20260414-1000/metadata/`:
  - `openwrt_release.txt`
  - `system_board.json`
  - `sysupgrade-list.txt`
  - `opkg-list-installed-24.10.5.txt`
  - `storage-partitions-bootenv.txt`
  - `network-vpn-summary.txt`
  - `sysupgrade-T-25.12.2-output.txt`
  - `sysupgrade-T-25.12.2-exit-status.txt`
- Created aggregate manifest: `.private/router/openwrt-upgrade-20260414-1000/manifest-sha256sums.txt`.
- Copied the verified firmware image to router staging path `/tmp/codex-openwrt-20260414-1000/openwrt-25.12.2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`.
- Ran validation-only `sysupgrade -T` against the staged image. Exit status: `0`. Output contained the expected image SHA256 and no board/compatibility warning in the captured output.
- Removed generated secret-bearing backup tarballs from router `/tmp` after copying them off-router. The non-secret firmware image remains staged under `/tmp/codex-openwrt-20260414-1000/`.
- Moved the prior top-level workspace-sync folder from `/Users/robert/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/network_workspace` to `.private/router/network_workspace`. No destination conflict existed; the source path no longer exists. Contents were moved intact, without printing file contents.

### Custom Image / Package Preservation Options

The plain official image validates, but the remaining risk is package preservation. Current `24.10.5` package list is saved in `metadata/opkg-list-installed-24.10.5.txt`. Official `25.12.2` feed checks show these package families are available:

- Base feed: `dnsmasq`, `firewall4`, `uhttpd`, `uhttpd-mod-ubus`, `wireguard-tools`.
- LuCI feed: `luci-app-attendedsysupgrade`, `luci-proto-wireguard`.
- Packages feed: `owut` and the StrongSwan `6.0.3-r1` package family, including `strongswan`, `strongswan-default`, `strongswan-swanctl`, `strongswan-pki`, and the EAP/crypto/kernel-netlink modules needed by the current IKEv2 configuration.

Recommended next non-disruptive option before any flash: build or request a custom `25.12.2` image that includes the saved critical package set, then validate that custom image hash and run `sysupgrade -T` on that image. The current plain official image should be treated as a validated fallback only if Robert confirms local/LAN recovery and accepts possible post-boot package reinstall work.

## Current-State Preservation Checklist

Robert clarification at `2026-04-12 12:36 CDT`: the priority is not upgrading for its own sake; it is ensuring that after any eventual router restart or upgrade, the router behaves exactly as it does now: VPN behavior, routing tables, static IPs/leases, DNS/DHCP, firewall/NAT, WAN/LAN, SSH/LuCI access, IKEv2, WireGuard fallback, and current recovery paths.

The initial preservation checklist was based on the already-created private backups and metadata under `.private/router/openwrt-upgrade-20260414-1000` because the MacBook was temporarily off the IKEv2 path at `2026-04-12 12:37 CDT`. Robert reconnected IKEv2 later, and a live read-only refresh was captured at `2026-04-12 14:52 CDT`; see "Live Current-State Refresh" below.

### Captured Preservation Sources

- Full sysupgrade backup with installed package metadata: `.private/router/openwrt-upgrade-20260414-1000/router-backups/openwrt-20260414-1000-sysupgrade-backup.tar.gz`.
- Critical config backup: `.private/router/openwrt-upgrade-20260414-1000/router-backups/openwrt-20260414-1000-critical-config.tar.gz`.
- Non-secret metadata snapshots: `.private/router/openwrt-upgrade-20260414-1000/metadata/`.
- Preservation source summary: `.private/router/openwrt-upgrade-20260414-1000/metadata/preservation-checklist-source-summary.txt`.
- Critical package set for a custom image: `.private/router/openwrt-upgrade-20260414-1000/metadata/custom-image-critical-package-set.txt`.

### Items That Must Be Preserved

- Router identity and target: Linksys WRT3200ACM, board `linksys,wrt3200acm`, target `mvebu/cortexa9`, rootfs `squashfs`.
- WAN/LAN/network: private backup shows `6` network interface sections, `3` device sections, `0` explicit route sections, and `0` route6 sections. Preserve all interfaces and any runtime/default routes captured in `metadata/network-vpn-summary.txt` and `metadata/storage-partitions-bootenv.txt`.
- Static leases/DHCP/DNS: private backup shows `206` static host sections, `2` DHCP pool sections, and `1` dnsmasq section in `/etc/config/dhcp`. These must survive exactly, because they likely define the static IP/lease behavior Robert called out.
- Firewall/NAT: private backup shows `4` firewall zones, `5` forwardings, `19` rules, `34` redirects, and `1` include. Preserve firewall zones, NAT/redirects, custom nftables include file, and IKEv2/WireGuard allowances.
- Wireless: private backup shows `3` wifi-device sections and `3` wifi-iface sections. Preserve wireless device/interface behavior even if Wi-Fi is not the primary management path.
- SSH/LuCI: preserve `/etc/config/dropbear`, `/etc/dropbear/authorized_keys`, `/etc/config/uhttpd`, `/etc/config/luci`, LuCI packages, `uhttpd`, and `rpcd`/LuCI dependency packages.
- IKEv2: preserve `/etc/swanctl/`, `/etc/strongswan.d/`, StrongSwan service enablement, EAP/crypto modules, pool/config behavior, and firewall rules for UDP `500`, UDP `4500`, ESP, and IKEv2 pool forwarding/NAT behavior. Secret contents are backed up privately and must not be printed.
- WireGuard fallback: preserve `/etc/config/network` WireGuard definitions, `kmod-wireguard`, `wireguard-tools`, `luci-proto-wireguard`, related firewall rules, and current recovery path expectations.
- Dual-partition recovery: current captured boot env showed `boot_part=1`; preserve a known-good `24.10.5` rollback path and do not overwrite both partitions without explicit approval and local recovery access.

### Package-Preserving Image Confidence

Custom image work is useful only if it materially improves preservation confidence. Current critical package list is saved in `metadata/custom-image-critical-package-set.txt`. Official `25.12.2` sources confirm:

- `kmod-wireguard` appears in official `sha256sums` under `kmods/6.12.74-1-a1b7fd67aef9ff09b98d2d5a9698c83d/`.
- `wireguard-tools` appears in the official `base` package feed.
- `luci-proto-wireguard` appears in the official `luci` package feed.
- StrongSwan `6.0.3-r1` packages, including `strongswan-default`, `strongswan-swanctl`, `strongswan-pki`, and current EAP/crypto/kernel-netlink module families, appear in the official `packages` feed.

Preservation recommendation: evaluate/build a custom `25.12.2` image with the saved critical package set before any flash. Do not use the plain official image unless Robert confirms local/LAN recovery and accepts that missing VPN packages may need post-boot repair.

### Explicit Post-Restart / Post-Upgrade Verification Commands

Run only after a separately approved restart/upgrade. Do not run these as a service reload/restart substitute before approval.

```sh
cat /etc/openwrt_release
ubus call system board
fw_printenv boot_part bootcount upgrade_available 2>/dev/null || true
ip -brief addr
ip route
ip rule 2>/dev/null || true
uci show network
uci show dhcp
uci show firewall
uci show wireless
uci show dropbear
uci show uhttpd
uci show luci
opkg list-installed 2>/dev/null || apk list --installed
for s in network firewall dnsmasq dropbear uhttpd swanctl strongswan ipsec; do [ -x /etc/init.d/$s ] && /etc/init.d/$s enabled && echo "$s enabled" || true; done
ps w | grep -E '([d]nsmasq|[d]ropbear|[u]httpd|[c]haron|[s]wanctl|[n]etifd|[f]irewall)'
swanctl --list-conns
swanctl --list-pools
swanctl --list-sas
wg show
nft list ruleset
logread | tail -n 200
```

Mac/client checks after the router is reachable again:

```sh
route -n get 192.168.55.1
ifconfig ipsec0
ping -c 3 192.168.55.1
nc -vz -G 5 192.168.55.1 22
nc -vz -G 5 192.168.55.1 53
nc -vz -G 5 192.168.55.1 80
nc -vz -G 5 192.168.55.1 443
scutil --dns | sed -n '1,120p'
curl -fsS --max-time 8 https://ifconfig.me
scutil --nc list
```

Validation comparison after restart/upgrade:

- Compare DHCP/static lease count to `206` static host sections, `2` DHCP pools, and `1` dnsmasq section.
- Compare firewall structure to `4` zones, `5` forwardings, `19` rules, `34` redirects, and `1` include.
- Compare network structure to `6` interface sections, `3` device sections, and no explicit route/route6 sections unless intentionally changed.
- Confirm LuCI/SSH access still works through expected aliases and browser path.
- Confirm IKEv2 and WireGuard fallback both work, not just one of them.
- Confirm public IP and DNS behavior match pre-maintenance expectations.

### Gaps Before Tuesday

- The custom package-preserving `25.12.2` image is not built yet. This is the next non-disruptive confidence step if Robert wants to reduce risk that IKEv2/WireGuard packages are missing after first boot.
- The exact dual-partition rollback command/physical recovery sequence still needs confirmation from a live router session or local access before any flash approval.

## Live Current-State Refresh

Robert reconnected IKEv2 at `2026-04-12 14:52 CDT`, and the live refresh was completed with read-only probes only. No firmware flash, reboot, firewall reload, VPN reload, service restart, or config change was performed.

Artifacts:

- Live current-state capture: `.private/router/openwrt-upgrade-20260414-1000/metadata/live-current-state-20260412-1452.txt`.
- Live nftables ruleset capture: `.private/router/openwrt-upgrade-20260414-1000/metadata/live-nft-ruleset-20260412-1452.txt`.
- Live-vs-backup summary: `.private/router/openwrt-upgrade-20260414-1000/metadata/live-refresh-diff-20260412-1454.txt`.

Management path and reachability:

- Mac route to `192.168.55.1` uses `ipsec0`.
- `ipsec0` address is `10.57.57.12`.
- Router ping succeeded `3/3`.
- Router TCP `22`, `80`, `443`, and `53` were reachable from the MacBook.
- Public IP check returned `205.178.117.216`.
- WireGuard client service `koval-robert-wg0-fresh` remains disconnected locally, so current MacBook traffic is IKEv2, not WireGuard.

Live structural counts match the private backup capture:

- Static DHCP host sections: `206`.
- DHCP pool sections: `2`.
- dnsmasq sections: `1`.
- Runtime DHCP leases: `57`.
- Network interface sections: `6`.
- Explicit route sections: `0`.
- Firewall zones: `4`.
- Firewall forwardings: `5`.
- Firewall rules: `19`.
- Firewall redirects: `34`.
- Wireless devices/interfaces: `3` / `3`.

WAN/LAN current state:

- WAN is up with IPv4 `205.178.117.216/21`, default gateway `205.178.112.1`, and WAN DNS `208.59.247.45`, `208.59.247.46`.
- LAN is up at `192.168.55.1/24` with LAN DNS `8.8.8.8`, `8.8.4.4`.

VPN current state:

- IKEv2 has an active SA for `robert-macbook` at `10.57.57.12/32`.
- `swanctl` init service is enabled; `strongswan` and `ipsec` init service names are missing on the current router, so the current system should be treated as using the `swanctl` init path.
- WireGuard interfaces `wgmac` and `wg0` exist on the router. The most recent redacted WireGuard peer handshake for `10.55.55.10/32` was about `4h23m` before capture, so WireGuard remains present as fallback but not the active MacBook path at capture time.

DNS note:

- Direct TCP `53` to `192.168.55.1` succeeds, but a direct UDP `dig @192.168.55.1 koval-distillery.com A` timed out from the MacBook over IKEv2.
- The MacBook resolver list includes public DNS `1.1.1.1` and `8.8.8.8`, and routes to `1.1.1.1` / `8.8.8.8` use `ipsec0`.
- Treat this as current behavior to preserve: IKEv2 public-DNS behavior should continue unless Robert deliberately wants router UDP DNS over VPN changed.

Firewall/NAT current state:

- Captured live nftables ruleset privately.
- nftables summary: `3` tables, `46` chains, `232` rule lines.
- Ruleset SHA256: `1a69f2092b9c54a7440392988a2d886c3646da8874a8455817841b6ca2e1955e`.

## Custom Image Evaluation Package

Update at `2026-04-13 19:20 CDT`: Robert approved the next evaluation-only step: prepare the custom package-preserving OpenWrt `25.12.2` image checklist/package plan. No firmware flash, reboot, firewall reload, VPN reload, StrongSwan/WireGuard restart, live-router package install, or secret printing is approved.

Created evaluation checklist: `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-evaluation-checklist.md`.

Safe public read-only checks completed from this machine:

- Official `25.12.2` `sha256sums` includes WRT3200ACM squashfs sysupgrade SHA256 `cf1ab7a2cafd6e317afc76cf1653be774474ba9ca3f74e6cdf5bd26118c4640c`.
- Official `25.12.2` `sha256sums` includes `openwrt-imagebuilder-25.12.2-mvebu-cortexa9.Linux-x86_64.tar.zst` SHA256 `87fba1a44f6fa07660da4278bb4ef27e6aade813a7fde2cfe1dd81edcf09220f`.
- Official `profiles.json` profile `linksys_wrt3200acm` still lists supported device `linksys,wrt3200acm` and the expected sysupgrade image/hash/size.

Local sync caveat: the Google Drive-backed private artifacts under `.private/router/openwrt-upgrade-20260414-1000` currently show logical sizes but `0` local blocks on this machine, so direct reads can return empty content or `Resource deadlock avoided`. Before building or comparing a custom package list from local artifacts, hydrate the required non-secret metadata/official files and rerun hash checks. Do not print secret-bearing backup contents.

Next step requiring separate approval: hydrate the non-secret package metadata, then build or request a custom `25.12.2` WRT3200ACM image locally/from official builder using the critical package set, save its manifest/hash under `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/`, and stop for separate approval before any router-side staging or `sysupgrade -T`.

Update at `2026-04-13 20:04 CDT`: Robert asked to continue evaluation by producing a concrete upgrade/rollback guide and preparing the custom package-preserving build/evaluation plan. Created:

- `project_hub/issues/2026-04-14-openwrt-25.12.2-upgrade-rollback-guide.md`
- `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-build-evaluation-plan.md`
- `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-package-input.txt`

Safe public feed checks confirmed package availability for the package groups needed by the custom-image plan: base feed has `dnsmasq`, `firewall4`, `nftables-json`, `uhttpd`, `uhttpd-mod-ubus`, `rpcd`, and `wireguard-tools`; LuCI feed has `luci`, `luci-base`, `luci-app-firewall`, `luci-app-package-manager`, `luci-proto-wireguard`, `luci-app-uhttpd`, and `luci-app-strongswan-swanctl`; packages feed has `rpcd-mod-wireguard` and the StrongSwan `6.0.3-r1` package family; target `sha256sums` has `kmod-wireguard` and WRT3200ACM device kmods.

No custom image was built or requested. The checklist still requires this exact separate approval before build-only local evaluation:

> Approve local custom OpenWrt 25.12.2 WRT3200ACM image build/request evaluation. This approval allows hydrating non-secret package metadata, downloading/verifying ImageBuilder or using the official Firmware Selector/custom builder, generating a local custom image and manifest, and saving local artifacts under `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/`. It does not allow copying anything to the router, running `sysupgrade -T`, flashing firmware, rebooting, reloading firewall/VPN, restarting StrongSwan/WireGuard, installing live-router packages, or printing secrets.

Update at `2026-04-13 20:25 CDT`: Robert approved the exact build/request evaluation step above. Used the official OpenWrt ASU/custom image API from this macOS host and generated a custom `25.12.2` WRT3200ACM image locally under `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/`. No router-side staging, `sysupgrade -T`, flash, reboot, firewall/VPN reload, StrongSwan/WireGuard restart, live-router package install, or secret printing was performed.

Build result note: `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-build-result.md`.

Generated image:

- `openwrt-25.12.2-285891de87a2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`
- SHA256 `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029`
- size `11735688` bytes
- ASU request hash `e4cbf3a63c081b2096075aac200969b37c7c4595b73ad5079599f5eec40514fd`

Manifest comparison against the candidate package input: `62` requested packages, `62` present, `0` missing. Required preservation groups are present in the generated manifest: LuCI/uhttpd/dropbear, firewall/DNS, WireGuard, WRT3200ACM device defaults, and StrongSwan/IKEv2 package families. Caveat: Google Drive placeholder state still prevents local reconciliation against the full saved `opkg-list-installed-24.10.5.txt`; the build is acceptable against the candidate input and project-note requirements, not against a locally-hydrated full package list.

Next separate approval needed:

> Approve validation-only staging of custom OpenWrt image `openwrt-25.12.2-285891de87a2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin` with SHA256 `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029` to the router `/tmp` path, and approve running `sysupgrade -T` against that exact staged custom image. This does not approve flashing firmware, rebooting, reloading firewall/VPN, restarting StrongSwan/WireGuard, installing live-router packages, or printing secrets.

Update at `2026-04-13 20:35 CDT`: Robert approved the validation-only staging and `sysupgrade -T` step for the exact custom image/hash above. Local pre-staging verification passed:

- Image: `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/openwrt-25.12.2-285891de87a2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`
- Size: `11735688` bytes
- SHA256: `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029`
- Router network reachability: ping to `192.168.55.1` passed.

Validation is blocked at the authentication boundary on this Mac, before staging. The router SSH aliases/key used in earlier MacBook work are not available here, direct key auth as `root@192.168.55.1` fails, no matching local keychain metadata was found, and `.private/router/openwrt-root-password.txt` is a dataless Google Drive placeholder that cannot be safely read or copied here (`Resource deadlock avoided`). A temporary secret-materialization directory was removed. No password content or password hash was printed.

No custom image was copied to the router, no staged-file SHA256 was available, no `sysupgrade -T` was run for the custom image, and no router flash/reboot/firewall reload/VPN reload/StrongSwan restart/WireGuard restart/package install/config change occurred.

Next safe continuation: Robert should materialize or provide an approved router SSH key/password path on this Mac without printing secrets. Once authentication is available, the already-approved validation-only step can resume by copying only the exact custom image/hash to a router `/tmp` validation path and running only `sysupgrade -T`. Actual flash remains a separate approval gate.

Update at `2026-04-13 20:45 CDT`: Robert reconfirmed `.private/router/openwrt-root-password.txt` as the approved sensitive local credential reference for the validation-only access path. Retried only non-printing local use of that reference. File Provider still reports the file is not downloaded, setting local keep-downloaded metadata did not hydrate it, direct read/expect read/copy paths fail or return zero bytes, and copy attempts still report `Resource deadlock avoided`. A temporary secret test directory was removed. Validation remains blocked before router staging; no custom image was copied to the router, no staged router SHA256 was captured, no custom-image `sysupgrade -T` was run, and no router config/service/disruptive action occurred.

Update at `2026-04-13 20:52 CDT`: Robert suggested using Macmini Google Drive or SSH to the MacBook as credential-location hints. Checked only filename/path metadata, not credential contents. On this Macmini account, `/Users/robert` is absent, `/Users/werkstatt` has no ai_workspace credential copy, and the only local candidate remains the admin Google Drive placeholder (`blocks=0`, not downloaded). MacBook SSH probes to `macbookpro.lan` and `192.168.55.33` timed out or reported host down; `192.168.55.34` answered ping but refused SSH. No credential contents were read or printed. Validation remains blocked before staging.

Update at `2026-04-13 21:04 CDT`: Used the approved `/Users/werkstatt/.private/router/` credential reference only inside SSH/SCP validation helpers. No credential contents were printed, quoted, logged, committed, or stored in new files. Validation-only staging completed:

- Staged router path: `/tmp/codex-openwrt-20260414-custom-validation/openwrt-25.12.2-285891de87a2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`
- Expected/local/staged SHA256: `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029`
- Staged SHA256 check: matched.
- `sysupgrade -T` exit status: `0`.
- Captured `sysupgrade -T` output showed no compatibility warning text; output was otherwise quiet apart from the SSH prompt wrapper and exit marker.
- Result artifact: `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/custom-validation-result-20260413-2104.md`.

No firmware flash, reboot, firewall/VPN reload, StrongSwan/WireGuard restart, live-router package install, or router config change occurred. The staged image remains in router `/tmp` for the current validation window. Actual firmware flash requires a separate explicit Robert approval after rollback prerequisites are reviewed.

Closeout update at `2026-04-13 21:32 CDT`: Task Manager routed Robert's reminder request to Frank email worker `ec85e0c1` to email Robert tomorrow at `2026-04-15 09:00` local time. Evaluation-only work is complete and this OpenWrt board session can close. The next OpenWrt action remains gated on a separate explicit flash/reboot approval.

## Approval Gate

Update at `2026-04-13 21:32 CDT`: Custom package-preserving image evaluation is complete. Official and custom image `sysupgrade -T` checks both returned `0`; the custom image is the preferred candidate because it preserves the critical package set.

Needed: Robert approval before any disruptive action. Backups, metadata, rollback notes, official-image validation, custom-image build, custom-image staging, staged SHA256 check, and custom-image `sysupgrade -T` are complete.

Next: Robert should review rollback prerequisites and explicitly approve or defer flashing the staged custom image. The exact dual-partition rollback sequence/local recovery plan should be treated as a prerequisite before flash approval.

Decision gate: do not run firmware/package upgrades, firewall reloads, VPN reloads, StrongSwan/WireGuard restarts, router config changes, live-router package installs, or router reboots until Robert explicitly approves the final upgrade step.

## Sources

- Official OpenWrt `24.10.6` announcement: `https://lists.openwrt.org/pipermail/openwrt-announce/2026-March/000083.html`
- Official OpenWrt `25.12.2` announcement: `https://lists.openwrt.org/pipermail/openwrt-announce/2026-March/000084.html`
- Official `25.12.2` `mvebu/cortexa9` image index: `https://downloads.openwrt.org/releases/25.12.2/targets/mvebu/cortexa9/`
- Official `25.12.2` `profiles.json`: `https://downloads.openwrt.org/releases/25.12.2/targets/mvebu/cortexa9/profiles.json`
- Official `25.12.2` `sha256sums`: `https://downloads.openwrt.org/releases/25.12.2/targets/mvebu/cortexa9/sha256sums`
- Official OpenWrt `25.12.0` announcement for package-manager migration context: `https://lists.openwrt.org/pipermail/openwrt-announce/2026-March/000081.html`
