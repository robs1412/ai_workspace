# AI Workspace Project Hub
Last Updated: 2026-04-15 18:25:58 CDT (Machine: Macmini.lan)

## Open

- **2026-04-15 Login Portal Security Rollout Activation**
  - Master ID: `AI-INC-20260415-LOGIN-PORTAL-SECURITY-ROLLOUT-01`
  - Detail log: `project_hub/issues/2026-04-15-login-portal-security-rollout-activation.md`
  - Repos: `login`, `ai_workspace`, live Login/Portal auth database state
  - Status: activated and notification emails sent on 2026-04-15; 47 Portal users tracked, 47 reset confirmations outstanding, 47 emailed, 0 send failures

- **2026-04-14 Macmini, M4, And MacBook SSH Key Exchange**
  - Master ID: `AI-INC-20260414-MACMINI-M4-SSH-KEY-EXCHANGE-01`
  - Detail log: `project_hub/issues/2026-04-14-macmini-m4-ssh-key-exchange.md`
  - Repos: `ai_workspace`, workstation SSH state on `Macmini.lan`, M4 Mac, and MacBook
  - Status: Macmini <-> M4 and M4 <-> MacBook direction-specific keys generated, appended on endpoints, and verified with explicit identities

- **2026-04-14 Digital Office Project/Task/Work Records**
  - Master ID: `AI-INC-20260414-DIGITAL-OFFICE-WORK-RECORDS-01`
  - Detail log: `project_hub/issues/2026-04-14-digital-office-project-task-work-records-proposal.md`
  - Repos: `ai_workspace`, `workspaceboard`
  - Status: read-only Workspaceboard prototype implemented and pushed as commit `68df99c`; live dashboard `http://localhost/workspaceboard/digital-office.html` indexes project-hub, TODO, and board/session metadata before any Papers, `.205`, OPS/Portal schema, production DB, notification, or MCP write work

- **2026-04-13 Salesreport Shipped-vs-Bottled Ownership**
  - Master ID: `AI-INC-20260413-SALESREPORT-SHIPPED-BOTTLED-OWNERSHIP-01`
  - Detail log: `project_hub/issues/2026-04-13-salesreport-shipped-vs-bottled-ownership.md`
  - Repos: `salesreport`, `portal`, shared `koval_distillery` view and Portal/Salesreport auth surfaces
  - Status: planning complete; recommendation is to move report ownership to Salesreport, but implementation is blocked pending approval because it affects live routing, auth/permissions, a shared DB view, and cross-repo deploy order

- **2026-04-12 AI Workstation And Sync Transition**
  - Master ID: `AI-INC-20260412-AI-WORKSTATION-SYNC-01`
  - Detail log: `project_hub/issues/2026-04-12-ai-workstation-sync-transition.md`
  - Repos: `ai_workspace`, `ai-bridge`, `/Users/werkstatt` workspace roots, Workspaceboard host state
  - Status: planning approved; 2026-04-14 audit completed and legacy synced `ai_workspace/codex_dashboard` deleted after dependency checks; `/Users/werkstatt/workspaceboard` remains the source of truth and active Workspaceboard v0.69 stayed healthy

- **2026-04-09 Werkstatt Path Unification**
  - Master ID: `AI-INC-20260409-WERKSTATT-PATHS-01`
  - Detail log: `project_hub/issues/2026-04-09-werkstatt-path-unification.md`
  - Repos: `ai_workspace`, `workspaceboard`, local workspace roots on Mac mini and MacBook

- **2026-04-07 MemPalace Salesreport Pilot**
  - Master ID: `AI-INC-20260407-MEMPALACE-SALESREPORT-01`
  - Detail log: `project_hub/issues/2026-04-07-mempalace-salesreport-pilot.md`
  - Repos: `ai_workspace`, `salesreport`

- **2026-03-15 WireGuard Stability Monitoring**
  - Master ID: `AI-INC-20260315-WIREGUARD-STABILITY-01`
  - Detail log: `project_hub/issues/2026-03-15-wireguard-stability-monitoring.md`
  - Repos: `ai_workspace`, workstation network stack, Linksys/OpenWrt WireGuard config

- **2026-03-12 OPS Portal Session Rehydration**
  - Master ID: `AI-INC-20260312-OPS-SESSION-REHYDRATE-01`
  - Detail log: `project_hub/issues/2026-03-12-ops-portal-session-rehydration.md`
  - Repos: `ops`, `login`

- **2026-03-07 Module Policy Hub Consolidation**
  - Master ID: `AI-INC-20260307-POLICY-HUB-01`
  - Detail log: `project_hub/issues/2026-03-07-module-policy-hub-consolidation.md`
  - Repos: `ai_workspace`, `ops`, `forge`, `login`, `bid`, `lists`, `importer`, `salesreport`, `portal`, `contactreport`, `donations`, `eventmanagement`

- **2026-03-06 OPS Task Creator Auth Regression**
  - Master ID: `AI-INC-20260306-OPS-TASK-CREATOR-01`
  - Detail log: `project_hub/issues/2026-03-06-ops-task-creator-auth-regression.md`
  - Repos: `ops`

- **2026-03-02 Portal Weekly Shift Digest Vacation Precedence**
  - Master ID: `AI-INC-20260302-PORTAL-SHIFT-VACATION-01`
  - Detail log: `project_hub/issues/2026-03-02-portal-weekly-shift-vacation-digest.md`
  - Repos: `koval-crm` (portal notifications backend)

- **2026-02-26 Logout Reliability Regression (Portal/OPS/Login SSO)**
  - Master ID: `AI-INC-20260226-LOGOUT-02`
  - Detail log: `project_hub/issues/2026-02-26-logout-reliability-regression.md`
  - Repos: `login` (shared SSO/logout layer affecting `portal` and `ops`)

## Completed

- **2026-04-12 Codex Portal Auth Repair**
  - Master ID: `AI-INC-20260412-CODEX-PORTAL-AUTH-01`
  - Detail log: `project_hub/issues/2026-04-12-codex-portal-auth-repair.md`
  - Repos: `ops`, `ai_workspace`, Portal API auth/database state
  - Status: completed 2026-04-15; Codex user id `1332` credential verifier fields reconciled to the approved local automation credential, and `crm_hydrate_session_portal_token("Codex")` now returns a non-expired Portal JWT for subject `1332`. Service-user impersonation policy for user id `167` was intentionally unchanged.

- **2026-04-12 OpenWrt LuCI Upgrade Assessment**
  - Master ID: `AI-INC-20260412-OPENWRT-LUCI-UPGRADE-01`
  - Detail log: `project_hub/issues/2026-04-12-openwrt-luci-upgrade-assessment.md`
  - Repos: `ai_workspace`, Linksys/OpenWrt router config, workstation VPN client state
  - Status: completed 2026-04-15; custom package-preserving `25.12.2` image flashed, router returned on boot partition `2`, and LAN/WAN/LuCI/SSH/core package/service and preservation-count checks passed

- **2026-04-07 Email User Archive Transfer (Mitch Donohue)**
  - Master ID: `AI-INC-20260407-EMAIL-ARCHIVE-TRANSFER-01`
  - Detail log: `project_hub/issues/2026-04-07-email-user-archive-transfer-mitch-donohue.md`
  - Repos: `ai_workspace`, Gmail IMAP archive path in `tastingroom`
  - Status: closed by Robert on 2026-04-15; no further mailbox, credential, or `imapsync` work is active

- **2026-04-14 Codex Daily Check-In Notifications**
  - Master ID: `AI-INC-20260414-CODEX-DAILY-CHECKIN-NOTIFICATIONS-01`
  - Detail log: `project_hub/issues/2026-04-14-codex-daily-checkin-notifications.md`
  - Repos: `ops`, `portal`, live Portal notification database state
  - Status: completed; Portal `checkins.reminder` personal setting for Codex user `1332` changed from enabled/email on to disabled/email off, with global human notification rules untouched

- **2026-03-07 Security Hardening Review (SSH + Malicious Prompt Handling)**
  - Master ID: `AI-INC-20260307-SEC-HARDEN-01`
  - Detail log: `project_hub/issues/2026-03-07-security-hardening-review.md`
  - Repos: `ai_workspace` (policy/docs), workstation SSH config, live SSH access path
  - Status: completed docs-only on 2026-04-13; no SSH config/server changes made. MacBook publickey-only access to `admin-macmini` at `192.168.55.17` works; live `koval@ftp.koval-distillery.com` key access works but server still advertises password and uses OpenSSH `8.0p1` / non-PQ `curve25519-sha256`. Client-config hardening across Mac mini, M4 Mac mini, and MacBook is deferred to silent Codex OPS task `366581` due `2026-04-22`.

- **2026-04-14 Communications Manager Newsletter Task Routing**
  - Master ID: `AI-INC-20260414-COMMS-MANAGER-NEWSLETTER-ROUTING-01`
  - Detail log: `project_hub/issues/2026-04-14-communications-manager-newsletter-task-routing.md`
  - Repos: `ops`, `ai_workspace`, pending separate `forge`/`lists` worker
  - Status: completed for OPS registration; `363191`, `360626`, and `363052` now verify as creator `1`, owner `1332`, assignee `1332`; no newsletter/email send or Forge/lists implementation was performed

- **2026-04-13 Portal Dev Deploy Branch Correction**
  - Master ID: `AI-INC-20260413-PORTAL-DEV-DEPLOY-CORRECTION-01`
  - Detail log: `project_hub/issues/2026-04-13-portal-dev-deploy-branch-correction.md`
  - Repos: `portal`, Portal live Docker deployment, Portal live auth/frontend runtime config
  - Status: completed; report/build fixes ported to `origin/dev` at `34ce6758500eeb7b4ac249420d26174a50caef79`, deployed from dev as backend `v20260413-dev-34ce6758`, then frontend-only env-fix tag `v20260413-dev-34ce6758-envfix` after `/undefined/auth/login` was traced to missing frontend production env in the first clean build

- **2026-04-12 Portal Production Audit Shipped vs Bottled**
  - Master ID: `AI-INC-20260412-PORTAL-AUDIT-SHIPPED-BOTTLED-01`
  - Detail log: `project_hub/issues/2026-04-12-portal-production-audit-shipped-vs-bottled.md`
  - Repos: `portal`, Portal live Docker deployment, Portal live database view/permissions
  - Status: completed with hostname-routing follow-up; report deployed at commit `128814b6` / tag `v20260412-audit-128814b6`, TODO note pushed at `46a11989`, SQL view count verified at 767 rows, H2/H9 permissions applied, production port URL verified while bare `https://portal.koval-distillery.com/` still returns a separate nginx 404

- **2026-04-11 OpenWrt IKEv2 / StrongSwan Evaluation**
  - Master ID: `AI-INC-20260411-OPENWRT-IKEV2-STRONGSWAN-01`
  - Detail log: `project_hub/issues/2026-04-11-openwrt-ikev2-strongswan-evaluation.md`
  - Repos: `ai_workspace`, Linksys/OpenWrt router config, workstation VPN client state
  - Status: completed; 2026-04-12 MacBook parity probe verified IKEv2 on `ipsec0` / `10.57.57.12` can replace WireGuard as primary while WireGuard remains configured as fallback

- **2026-04-11 OPS Calendar Display Rendering**
  - Master ID: `AI-INC-20260411-OPS-CALENDAR-DISPLAY-01`
  - Detail log: `project_hub/issues/2026-04-11-ops-calendar-display-rendering.md`
  - Repos: `ops`

- **2026-04-11 OPS Mitch Donohue Cleanup**
  - Master ID: `AI-INC-20260411-OPS-MITCH-DONOHUE-CLEANUP-01`
  - Detail log: `project_hub/issues/2026-04-11-ops-mitch-donohue-cleanup.md`
  - Repos: `ops`, OPS/Event/CRM live database state

- **2026-04-11 Barrel-Sales Forge/PHPList Audience**
  - Master ID: `AI-INC-20260411-BARREL-SALES-AUDIENCE-01`
  - Detail log: `project_hub/issues/2026-04-11-barrel-sales-audience-list.md`
  - Repos: `salesreport`, `ai_workspace`, Forge/PHPList database state, Avignon/Mac mini email route

- **2026-04-10 OPS Codex Task Creation Fix**
  - Master ID: `AI-INC-20260410-OPS-CODEX-TASK-01`
  - Detail log: `project_hub/issues/2026-04-10-ops-codex-task-creation-fix.md`
  - Repos: `ops`

- **2026-04-09 OPS Outreach Live Gating + Market Sync Dedupe**
  - Master ID: `AI-INC-20260409-OPS-OUTREACH-LIVE-GATING-01`
  - Detail log: `project_hub/issues/2026-04-09-ops-outreach-live-gating-and-market-sync-dedupe.md`
  - Repos: `ops`

- **2026-04-09 BID Binny's Recurring Report**
  - Master ID: `AI-INC-20260409-BID-BINNYS-REPORT-01`
  - Detail log: `project_hub/issues/2026-04-09-bid-binnys-recurring-report.md`
  - Repos: `bid`, `playwright-scraper`

- **2026-04-09 OPS Task Stats Credential Lookup**
  - Master ID: `AI-INC-20260409-OPS-TASK-STATS-CREDS-01`
  - Detail log: `project_hub/issues/2026-04-09-ops-task-stats-credential-lookup.md`
  - Repos: `ops`

- **2026-04-09 OPS Connecteam Outreach Visibility**
  - Master ID: `AI-INC-20260409-OPS-OUTREACH-CONNECTEAM-01`
  - Detail log: `project_hub/issues/2026-04-09-ops-connecteam-outreach-visibility.md`
  - Repos: `ops`

- **2026-04-09 Login Token 2FA Hardening**
  - Master ID: `AI-INC-20260409-LOGIN-TOKEN-2FA-01`
  - Detail log: `project_hub/issues/2026-04-09-login-token-2fa-hardening.md`
  - Repos: `login`

- **2026-03-15 Salesreport Report Automation + Hitlist Optimization**
  - Master ID: `AI-INC-20260315-SALESREPORT-AUTOMATION-01`
  - Detail log: `project_hub/issues/2026-03-15-salesreport-report-automation-and-hitlist-optimization.md`
  - Repos: `salesreport`, `login`

- **2026-04-08 Multi-Repo Git Cleanup**
  - Master ID: `AI-INC-20260408-MULTI-REPO-GIT-01`
  - Detail log: `project_hub/issues/2026-04-08-multi-repo-git-cleanup.md`
  - Repos: `salesreport`, `ops`, `bid`, `lists`, `forge`, `portal`, `login`, `ai_workspace`

- **2026-04-08 Auth Initiative Scope: Lists Logout vs Cross-Module SSO**
  - Master ID: `AI-INC-20260408-AUTH-SCOPE-01`
  - Detail log: `project_hub/issues/2026-04-08-auth-initiative-scope-lists-vs-sso.md`
  - Repos: `lists`, `login`, `ops`, downstream impact on `portal`, `forge`, `salesreport`

- **2026-03-06 AI Reminder Review Project**
  - Master ID: `AI-INC-20260306-AI-REVIEW-01`
  - Detail log: `project_hub/issues/2026-03-06-ai-reminder-review-project.md`
  - Repos: `ai_workspace`

- **2026-04-07 Frank Workspace Automation + Sync**
  - Master ID: `AI-INC-20260407-FRANK-AUTO-01`
  - Detail log: `project_hub/issues/2026-04-07-frank-workspace-automation-and-sync.md`
  - Repos: `ai_workspace`, Mac mini LaunchAgent runtime

- **2026-04-07 Codex Dashboard Session-State Recovery**
  - Master ID: `AI-INC-20260407-CODEX-DASH-SESSION-01`
  - Detail log: `project_hub/issues/2026-04-07-codex-dashboard-session-state-recovery.md`
  - Repos: `ai_workspace`

- **2026-04-07 Three-Repo Live/GitHub Sync Confirmation**
  - Master ID: `AI-INC-20260407-THREE-REPO-SYNC-01`
  - Detail log: `project_hub/issues/2026-04-07-three-repo-live-github-sync-confirmation.md`
  - Repos: `lists`, `eventmanagement`, `donations`

- **2026-03-30 Eventmanagement Public Notification Recipient**
  - Master ID: `AI-INC-20260330-EVENTMGMT-NOTIFY-01`
  - Detail log: `project_hub/issues/2026-03-30-eventmanagement-public-notification-recipient.md`
  - Repos: `eventmanagement`

- **2026-03-27 Portal User Create parent_id NOT NULL**
  - Master ID: `AI-INC-20260327-PORTAL-USER-CREATE-01`
  - Detail log: `project_hub/issues/2026-03-27-portal-user-create-parent-id-null.md`
  - Repos: `portal` / `koval-crm` live production database path

- **2026-03-27 Donations requesteventcause Truncation Fix**
  - Master ID: `AI-INC-20260327-DONATIONS-EVENTCAUSE-01`
  - Detail log: `project_hub/issues/2026-03-27-donations-requesteventcause-truncation.md`
  - Repos: `donations`

- **2026-03-16 OPS Recurring Task Postpone Cadence**
  - Master ID: `AI-INC-20260316-OPS-RECURRING-POSTPONE-01`
  - Detail log: `project_hub/issues/2026-03-16-ops-recurring-task-postpone-cadence.md`
  - Repos: `ops`

- **2026-03-15 Illinois Strategy HTML Report**
  - Master ID: `AI-INC-20260315-IL-REPORT-01`
  - Detail log: `project_hub/issues/2026-03-15-illinois-strategy-html-report.md`
  - Repos: `ai_workspace`, `salesreport`

- **2026-03-12 Multi-Module Pull + AGENTS Merge**
  - Master ID: `AI-INC-20260312-MODULE-PULL-01`
  - Detail log: `project_hub/issues/2026-03-12-multi-module-pull-and-agents-merge.md`
  - Repos: `ops`, `bid`, `portal`, `login`, `forge`, `salesreport`, `importer`, `eventmanagement`, `contactreport`, `donations`, `lists`

- **2026-03-07 Codex Login Process Module Push**
  - Master ID: `AI-INC-20260307-CODEX-PUSH-01`
  - Detail log: `project_hub/issues/2026-03-07-codex-login-process-module-push.md`
  - Repos: `forge`, `login`, `bid`, `importer`, `portal`, `contactreport`, `donations`, `eventmanagement`

- **2026-03-04 Eventmanagement Event Support Module (Donations Migration Slice)**
  - Master ID: `AI-INC-20260304-EVENTMGMT-SUPPORT-01`
  - Detail log: `project_hub/issues/2026-03-04-eventmanagement-event-support-module.md`
  - Repos: `eventmanagement` (module path `event_support`), `ops`

- **2026-03-04 Session-Start OPS Task Pull Policy (No Background Polling)**
  - Master ID: `AI-INC-20260304-TASK-PULL-POLICY-01`
  - Detail log: `project_hub/issues/2026-03-04-session-start-task-pull-policy.md`
  - Repos: `ops`, `lists`, `login`, `forge`, `salesreport`, `importer`, `bid`, `contactreport`

- **2026-03-02 OPS Shift Create account_id NOT NULL**
  - Master ID: `AI-INC-20260302-OPS-SHIFT-ACCOUNTID-01`
  - Detail log: `project_hub/issues/2026-03-02-ops-shift-create-account-id-not-null.md`
  - Repos: `ops`

- **2026-03-02 OPS Force PHP 8.3 Handler**
  - Master ID: `AI-INC-20260302-OPS-PHP-HANDLER-01`
  - Detail log: `project_hub/issues/2026-03-02-ops-force-php83-handler.md`
  - Repos: `ops`

- **2026-03-02 OPS Shift Create parent_id NOT NULL**
  - Master ID: `AI-INC-20260302-OPS-SHIFT-PARENTID-01`
  - Detail log: `project_hub/issues/2026-03-02-ops-shift-create-parent-id-not-null.md`
  - Repos: `ops`

- **2026-03-02 OPS Outreach Calendar Sync 500 (PHP 7.4 Compatibility)**
  - Master ID: `AI-INC-20260302-OPS-OUTREACH-SYNC-500-01`
  - Detail log: `project_hub/issues/2026-03-02-ops-outreach-calendar-sync-500-php74-compat.md`
  - Repos: `ops` (auth bootstrap compatibility shim)

- **2026-03-02 OPS Outreach Calendar Live Visibility**
  - Master ID: `AI-INC-20260302-OPS-OUTREACH-LIVE-01`
  - Detail log: `project_hub/issues/2026-03-02-ops-outreach-live-visibility.md`
  - Repos: `ops`

- **2026-03-02 Cross-Machine Git Auth (SSH Context)**
  - Master ID: `AI-INC-20260302-GITAUTH-SSHCTX-01`
  - Detail log: `project_hub/issues/2026-03-02-cross-machine-git-auth-ssh-context.md`
  - Repos: `ops`, `portal`, `forge`, `importer`, `contactreport`

- **2026-02-26 Lists Image Browser White Page**
  - Master ID: `AI-INC-20260226-LISTS-KCFINDER-01`
  - Detail log: `project_hub/issues/2026-02-26-lists-image-browser-white-page.md`
  - Repos: `lists`

- **2026-03-01 Playwright Skill and Browser Fix**
  - Master ID: `AI-INC-20260301-PLAYWRIGHT-FIX-01`
  - Detail log: `project_hub/issues/2026-03-01-playwright-skill-and-browser-fix.md`
  - Repos: `ai_workspace` (skill install fix)

- **2026-03-01 ToDo-append Cross-Module Alignment (OPS/LISTS/CONTACTREPORT/IMPORTER/PORTAL/FORGE)**
  - Master ID: `AI-INC-20260301-TODO-ALIGN-01`
  - Detail log: `project_hub/issues/2026-03-01-todo-append-cross-module-alignment.md`
  - Repos: `ops`, `lists`, `contactreport`, `importer`, `portal`, `forge`

- **2026-02-28 TODO Workflow Standardization (All Modules; Live Pull Excludes bid/portal)**
  - Master ID: `AI-INC-20260228-TODO-WORKFLOW-01`
  - Detail log: `project_hub/issues/2026-02-28-todo-workflow-standardization-all-modules.md`
  - Repos: `ops`, `bid`, `portal`, `login`, `salesreport`, `importer`, `lists`, `contactreport` (`forge` live pull check only)

- **2026-02-27 Append File Access Hardening (OPS + Related Modules)**
  - Master ID: `AI-INC-20260227-APPEND-LOCKDOWN-01`
  - Detail log: `project_hub/issues/2026-02-27-append-file-access-hardening.md`
  - Repos: `ops`, `login`, `forge`, `salesreport`, `lists`, `bid` (MAMP path)

- **2026-02-27 Live Modules: ToDo-append Access Lockdown + Multi-Repo Sync**
  - Master ID: `AI-INC-20260227-LIVE-MODULES-02`
  - Detail log: `project_hub/issues/2026-02-27-live-modules-todo-append-block-and-sync.md`
  - Repos: `ops`, `portal`, `forge`, `importer`, `lists` (+ live pull validation on `login`, `salesreport`, `contactreport`)

- **2026-02-27 Cross-Machine Git Auth Verification + SSH Access**
  - Master ID: `AI-INC-20260227-GITAUTH-01`
  - Detail log: `project_hub/issues/2026-02-27-cross-machine-git-auth-verification.md`
  - Repos: `ops`, `bid`, `portal`, `login`, `forge`, `salesreport`, `importer`, `lists`

- **2026-02-27 OPS Git Verification + Live Pull Access**
  - Master ID: `AI-INC-20260227-OPS-GIT-01`
  - Detail log: `project_hub/issues/2026-02-27-ops-live-git-verification-and-live-pull-access.md`
  - Repos: `ops`

- **2026-02-26 Logout Reliability / Shared Machine**
  - Master ID: `AI-INC-20260226-LOGOUT-01`
  - Detail log: `project_hub/issues/2026-02-26-logout-reliability.md`
  - Repos: `ops`, `login`, `portal`

- **2026-03-06 Codex Login Process + Env Standardization (All Modules + ai_workspace)**
  - Master ID: AI-INC-20260306-CODEX-LOGIN-PROCESS-01
  - Detail log: project_hub/issues/2026-03-06-codex-login-process-standardization.md
  - Repos: ai_workspace, ops, salesreport, contactreport, lists, importer, login, donations, eventmanagement, bid
