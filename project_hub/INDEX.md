# AI Workspace Project Hub
Last Updated: 2026-06-16 CDT (Machine: Macmini.lan)

## Completed

- **2026-06-16 Salesreport Illinois Top Products Report**
  - Master ID: `AI-INC-20260616-SALESREPORT-IL-TOP-PRODUCTS-01`
  - Detail log: `project_hub/issues/2026-06-16-salesreport-il-top-products-report.md`
  - Repos: `salesreport`, live Salesreport checkout
  - Status: completed. Added a tabbed Illinois top-products report at `2026-IL-Top-Products.php`, registered it in Custom Reports and the Salesreport menu, and fixed the existing `2026-IL-Top-Accounts.php` running total script so it recalculates from the Sales column instead of WG. Added the tabbed `2026-IL-Product-Payout-Calculator.php` with adjustable margin, shipping, fixed/percent commission, tax, net price, and KOVAL net calculations. Follow-up updates changed both product-page Top-N summaries to `5, 10, 15, 20, 25, 30, 40, 50`, added footer totals including unique accounts and cases, renamed Product and Calculator footer labels to `Total Sales`, restored explicit filtered-sales, total-sales, and running-sales percent columns on both product pages, added total shipping cost, added commission input units, corrected margin math to `price / (1 - margin)`, and recalculated calculator taxes per invoice line using ABV, account channel, and Chicago/Cook/outside-Cook location. Salesreport commits through `bd5461d` are pushed to `origin/master` and live Salesreport fast-forwarded to `bd5461d`; live syntax and source readback checks passed.

- **2026-06-16 OPS Stay Logged In Session Cookie Fix**
  - Master ID: `AI-INC-20260616-OPS-STAY-LOGGED-IN-SESSION-COOKIE-01`
  - Detail log: `project_hub/issues/2026-06-16-ops-stay-logged-in-session-cookie-fix.md`
  - Repos: `login`, observed through `ops`
  - Status: pushed; live pull blocked. Patched the shared Login session helper so PHPSESSID retry recomputes authenticated state and so login, remember-device recovery, and OPS SSO recovery refresh PHPSESSID/alias cookies only after authenticated identity is written into the session. Login commit `669b448` is pushed to `origin/master`; live SSH port 22 is reachable, but SSH command execution to `ftp.koval-distillery.com` timed out/exited `255` before checkout readback, so no live pull, credential change, or production session mutation was performed.

- **2026-04-19 IKEv2 VPN DNS For koval.lan**
  - Master ID: `AI-INC-20260419-IKEV2-VPN-DNS-01`
  - Detail log: `project_hub/issues/2026-04-19-ikev2-vpn-dns-koval-lan.md`
  - Repos: `ai_workspace`; runtime config on OpenWrt `192.168.55.1`
  - Status: completed. Router DNS now answers VPN clients and future IKEv2 clients should receive `192.168.55.1` as DNS; active tunnels were not restarted.

- **2026-05-27 OPS Page Width Overflow Fix**
  - Master ID: `AI-INC-20260527-OPS-PAGE-WIDTH-OVERFLOW-01`
  - Detail log: `project_hub/issues/2026-05-27-ops-page-width-overflow-fix.md`
  - Repos: `ops`, live OPS checkout
  - Status: completed. Fixed shared OPS shell CSS so `/ops/start.php` and other OPS pages no longer expand the body horizontally. Commits `8c56687` and `6a8f25d` were pushed to `origin/main` and fast-forwarded live to `/home/koval/public_html/ops`; live authenticated Chromium checks on Start, Tasks, and Task Stats read `docScrollWidth == innerWidth` at desktop and mobile widths.

- **2026-05-26 Login / OPS DB Host Production Fix**
  - Master ID: `AI-INC-20260526-LOGIN-OPS-DBHOST-01`
  - Detail log: `project_hub/issues/2026-05-26-login-ops-dbhost-production-fix.md`
  - Repos/surfaces: live `login`, live `ops`, `ai_workspace` Task Flow
  - Status: completed. Robert requested restoring the live DB host to `localhost`; live `/login/.env` and `/ops/.env` now read `localhost`, app-side DB identity reads `koval_crm2@localhost`, and public `/login/index.php?referrer=salesreport`, `/salesreport/`, and `/ops/start.php` all return the expected login flow with referrers preserved. Task Flow packet `taskmode-login-ops-salesreport-dbhost-2026-05-26` carries the closeout proof.

- **2026-05-20 Avignon Brooklyn Account Visit Recap**
  - Master ID: `AVIGNON-BROOKLYN-ACCOUNT-VISIT-20260520-01`
  - Detail log: `project_hub/issues/2026-05-20-avignon-brooklyn-account-visit-recap.md`
  - Repos: `avignon`, `portal`, `ai_workspace`
  - Status: completed. Sonat's Brooklyn recap was readable in AI Cloud after all, so the prior access blocker was stale. Avignon created the missing Brooklyn venue accounts/leads, related contacts, and dated `2026-06-19` market-visit activities in Portal, then prepared the Sonat completion reply with Robert copied.

- **2026-05-19 Avignon Wisconsin Sales Report**
  - Master ID: `AI-INC-20260519-AVIGNON-WI-SALES-REPORT-01`
  - Detail log: `project_hub/issues/2026-05-19-avignon-wi-sales-report.md`
  - Repos: `salesreport`, `ai_workspace`
  - Status: completed. Added a narrow Wisconsin Salesreport generator and produced Sonat's requested `2025-01-01` through `2026-04-30` report artifact with market totals, top products, year-by-product/SKU totals, and top 20 accounts. Durable Avignon closeout notes and a Sonat-facing completion draft were recorded off the verified readback.

- **2026-05-18 Task Manager Finish Contract Tightening**
  - Master ID: `AI-INC-20260518-TASK-MANAGER-FINISH-CONTRACT-01`
  - Detail log: `project_hub/issues/2026-05-18-task-manager-finish-contract-tightening.md`
  - OPS project: `369836`
  - Repos: `workspaceboard`
  - Status: completed. Workspaceboard Task Manager enforcement now treats live routed/working Task Flow rows without closeout proof as unfinished proof-repair work while preserving dead-session reroute priority. Added a regression test and verified the updated server file with `node --check` and `node --test`.

- **2026-05-18 TODO Archive Migration**
  - Master ID: `AI-INC-20260518-TODO-ARCHIVE-MIGRATION-01`
  - Detail log: `project_hub/issues/2026-05-18-todo-archive-migration.md`
  - OPS project: `369837`
  - Repos: `ai_workspace`, `ops`, `portal`, `workspaceboard`, `lists`, `login`, `forge`, `salesreport`, `importer`, `bid`, `eventmanagement`, `donations`, `contactreport`, `ai-bridge`, `braincloud`
  - Status: completed. Archived legacy `TODO.md`, `ToDo.md`, and `ToDo-append.md` surfaces across `/Users/werkstatt` so the DB-backed Task Flow / OPS / project-hub spine is the only live task-management source. All touched files now contain archive stubs only and no longer function as active intake or queue surfaces.

- **2026-05-18 Outreach Event Fast Path Manual**
  - Master ID: `AI-INC-20260518-OUTREACH-EVENT-FAST-PATH-01`
  - Detail log: `project_hub/issues/2026-05-18-outreach-event-fast-path-manual.md`
  - OPS project: `369838`
  - Repos: `ops`, `ai_workspace`
  - Status: completed. Added a repeatable Outreach tasting/event fast-path to the OPS Events manual, including Outreach-specific quick links, the OPS-first intake checklist, and Outreach Calendar Feed guidance so the recurring booking workflow is explicit without relying on inbox re-derivation.

- **2026-05-18 OPS Login Trusted-Device IP Fix**
  - Master ID: `AI-INC-20260518-OPS-LOGIN-TRUSTED-DEVICE-IP-01`
  - Detail log: `project_hub/issues/2026-05-18-ops-login-trusted-device-ip-fix.md`
  - Repos: `login`, `ops`
  - Status: completed. Verified OPS only calls `remember_try_silent_login()` while the actual trusted-device logic lives in `login/auth_helpers.php`; patched that owner file so remember-device acceptance ignores IP churn while still storing `ip_prefix` for audit/readback. Commit `9956992` was pushed to `origin/master`, live `/home/koval/public_html/login` fast-forwarded from `8c338d8` to `9956992`, live PHP lint passed, and linked OPS task `369822` is now `Completed`.

- **2026-05-18 Workspaceboard Live Session Startup Fix**
  - Master ID: `AI-INC-20260518-WORKSPACEBOARD-SESSION-STARTUP-01`
  - Detail log: `project_hub/issues/2026-05-18-workspaceboard-live-session-startup-fix.md`
  - Repos: `workspaceboard`, `ai_workspace`, installed Workspaceboard runtime state
  - Status: completed. Fixed the reusable-prompt startup misclassification that was persisting fresh live Codex workers as `finished` and feeding the fast-close path. Verified with `node --check`, `node --test` (`64/64`), a live smoke worker that first stayed `working/live`, and a controlled relaunch batch of four real workers that remained live after the verification window.

- **2026-05-17 OPS TrackTime Login Route Repair**
  - Master ID: `AI-INC-20260517-OPS-TRACKTIME-LOGIN-ROUTE-01`
  - Detail log: `project_hub/issues/2026-05-17-ops-tracktime-login-route-repair.md`
  - Repos: `ops`, `ai_workspace`
  - Status: completed. Repaired hourly OPS login routing for National Outreach task `368517` by making `login_router.php` route non-exempt users to `my_clocks`, treating generic `/ops/start.php` login handoffs as TrackTime landings for hourly staff, and stopping the router from counting missing daily check-ins against hourly users. Verified on `http://localhost` with authenticated simulated hourly sessions: first portal-style login now returns `reason=missing_clock` to `/ops/index.php?view=my_clocks`, and a generic `/ops/start.php` referrer now resolves to the same TrackTime page. OPS commit `19b53ae` is pushed to `origin/main`; no live pull was performed.

- **2026-05-17 Morning Automation Reliability Hardening**
  - Master ID: `AI-INC-20260517-MORNING-AUTOMATION-RELIABILITY-01`
  - Detail log: `project_hub/issues/2026-05-17-morning-automation-reliability-hardening.md`
  - Repos: `ai_workspace`, `workspaceboard`, machine-local National Outreach runtime state
  - Status: completed. National Outreach runtime install now refreshes its runtime script bundle before LaunchDaemon reload, the installed due-runner suppresses daemon-owned Vanessa scheduled actions instead of spawning visible due-worker wrappers, and the live Workspaceboard closed-session readback for the misleading May 17 rows is corrected to the real short durations (`d91e3385` 10:33:38 -> 10:33:48, `89d6ffd6` 10:34:16 -> 10:34:20). Follow-up repair restored the shared Frank/Avignon runtime helper, corrected Workspaceboard mailbox monitor heartbeat sources, fixed AI Health canary/validator proof handling, and hardened AI Health standing/stale classification plus status retries. Live direct verification now reads `board_ok = true`, `mailbox_canaries = passed`, `unhealthy = 0`, while remaining residue is stale-session cleanup rather than send-path/runtime failure.

- **2026-04-30 OPS Project Task Autosave Fix**
  - Master ID: `AI-INC-20260430-OPS-PROJECT-TASK-AUTOSAVE-01`
  - Detail log: `project_hub/issues/2026-04-30-ops-project-task-autosave-fix.md`
  - Repos: `ops`, `ai_workspace`
  - Status: completed. Fixed live task-detail autosave by moving top-field metadata saving onto `projects/task.php` itself and then fixing the browser save URL shadowing bug that posted to `/ops/projects/[object HTMLInputElement]`; committed and pushed `b89896c` and `b0f5caa`, fast-forwarded live OPS to `b0f5caa`, and verified live syntax/source plus a Codex-authenticated save response.

- **2026-05-07 OPS Live Git Cleanup**
  - Master ID: `AI-INC-20260507-OPS-LIVE-GIT-CLEANUP-01`
  - Detail log: `project_hub/issues/2026-05-07-ops-live-git-cleanup.md`
  - Repos: `ops`, live OPS checkout
  - Status: completed. The live OPS checkout at `/home/koval/public_html/ops` fast-forwarded cleanly to `5d008fe77b1563e11201332946c7bf3e072c12c6`, matching `origin/main`. No live stash, reset, clean, overwrite, or file deletion was needed.

- **2026-05-06 AI Manager Response Reliability And Repeating Tasks**
  - Master ID: `AI-INC-20260506-AI-MANAGER-RESPONSE-RELIABILITY-01`
  - Detail log: `project_hub/repeating-tasks.json`
  - Repos: `ai_workspace`, National Outreach runtime state, Workspaceboard/AI Health runtime
  - Status: completed. Structured recurrence fields now flow through the Task Flow report and the repeating-tasks / Task Flow pages. The report now emits `parent_packet_id` plus `recurrence_*` fields, and the live runtime copies were synced with the updated page assets. Task Flow response defaults remain first check within 2 minutes and result email, owner question, or exact blocker within 5 minutes for owner-visible email lanes.

## Completed

- **2026-05-20 Login 2FA Regression Handoff**
  - Master ID: `AI-INC-20260520-LOGIN-2FA-REGRESSION-01`
  - Detail log: `project_hub/issues/2026-05-20-2fa-login-regression-handoff.md`
  - Repos: `login`, `ops`, `workspaceboard`, `ai_workspace`
  - Status: completed. OPS task `369936` was silently completed after the live Portal backend was patched, rebuilt, and deployed as `koval-crm-backend:authfix-20260520`. Workspaceboard session `285827f3` remains the blocker proof trail, but the task itself is now closed against the same incident record.

## Open

- **2026-05-24 Recursive Tools Stack Plan**
  - Master ID: `AI-INC-20260524-RECURSIVE-TOOLS-01`
  - Detail log: `project_hub/issues/2026-05-24-recursive-tools-stack-plan.md`
  - Repos: `ai_workspace`; follow-up execution may touch local sandbox tooling, Frank owner reporting, and silent Codex-owned OPS tasks
	  - Status: in progress. Durable assessment, Papers publish, Frank link email, silent Codex OPS follow-up tasks, and the first repo-local `recursive-improve` pilot are complete. The bounded Python 3.13 entrypoint migration lane is finished for `ai_workspace/scripts` plus `workspaceboard/scripts`: the refreshed inventory reads `env-python3=0` / `pinned-python3.13=37`. The recursive pattern has now graduated into `scripts/service_parity_check.py`, which checks source/runtime parity, deployment-state plists/wrappers, installed runtime scripts, and KOVAL plists, then writes `project_hub/artifacts/recursive-tools/service-parity-check-latest.*`. Guarded installed-runtime fixing patched writable National Outreach, Task Flow, Frank, Avignon, Asher, and Venetia runtime script drift; Robert then applied the two root-owned Frank/Avignon morning-overview plist interpreter fixes without kickstarting the scheduled jobs. Current broadened readback is `surfaces_checked=91`, `drift=0`, `fix_failed=0`. Service parity is now wired into AI Health as a recurring read-only check and dry-run verification returned `service_parity=passed`, `service_parity_checked=91`, `service_parity_drift=0`. The recursive recommendation lane now has synthetic, live, and historical baselines: synthetic eval `7596f83f91ec` / benchmark `b3d095e7b2e4` at `5/5`, live eval `cde619b65fda` / benchmark `bc145700f885` at `1/1`, and historical eval `305f1b72f49c` / benchmark `3b31329dcd91` at `6/6`. Frank owns the Robert-facing yes/no approval loop; Codex generates proposals and executes only approved low-risk fixes. Papers ownership note: `https://papers.koval.lan/89b2ac72-7476-4962-ad27-2b409a89554e`. Frank emailed Claude for comparison at the corrected address `claude@kovaldistillery.com`, copied Robert, under Message-ID `<177964800446.11583.9902601401452484732@kovaldistillery.com>`. Proposal queue generator `scripts/recursive_proposal_queue.py` is now live. First proposal `recursive-proposal-20260524-134350-repair-truth-drift` was generated and Frank sent the approval request to Robert under Message-ID `<177964828163.12510.14353964488768279452@kovaldistillery.com>`. After Robert corrected the email quality, the generator was upgraded to emit richer plain text plus a formatted HTML body. Fresh queue readback now shows `recursive-proposal-20260524-134813-monitor-recursive-lane` with `approval_required=false`, `service_parity_drift=0`, and `truth_drift_count=0`.
	  - 2026-05-24 13:54 CDT update: proposal decision/state recording is now live in `scripts/recursive_proposal_decisions.py`, with immutable events in `project_hub/artifacts/recursive-tools/recursive-proposal-decisions.jsonl` and Papers addendum `https://papers.koval.lan/99336886-09d1-4a6d-b09d-f43093344bcd`. The old `repair-truth-drift` approval request is now `superseded_by_clean_monitor` because the later monitor proposal proved clean, and `./scripts/recursive_proposal_decisions.py status --json` reports `pending_approval_count=0`.
	  - 2026-05-24 14:01 CDT update: changed stack Papers version published at `https://papers.koval.lan/346f243c-b610-489c-8323-627df9ca9f8d` and Frank sent it to Claude on the existing comparison thread under Message-ID `<177964923221.16079.8878460685095716018@kovaldistillery.com>`.
	  - 2026-05-24 14:05 CDT update: approved proposal executor added at `scripts/recursive_proposal_executor.py`. It enforces fix-class allowlists, blocks live mutation without `--allow-live-mutation`, runs post-execution verifiers, and reports `approved_unexecuted_count=0` on the current clean queue. Papers v3: `https://papers.koval.lan/89f95776-d0d4-47e2-94fc-c48064355ec2`.
	  - 2026-05-24 14:06 CDT update: Frank sent Claude the executor update on the existing comparison thread under Message-ID `<177964957514.17815.13480250926490834788@kovaldistillery.com>`.

- **2026-05-19 Communications Planner Buildout**
  - Master ID: `AI-INC-20260519-COMMS-PLANNER-BUILDOUT-01`
  - Detail log: `project_hub/issues/2026-05-19-communications-planner-buildout.md`
  - Repos: `ai_workspace`
  - Status: in progress. Communications planner role split is now explicit: `Marketing Manager` owns weekly highlights and campaign-style sends, `Vanessa Sterling` stays on the National Outreach/outreach route, `Communications Manager` handles copy/tone/approval shaping, and `Email Coordinator` handles send-from and durable routing. Live Google Doc write still needs a writable Docs-scope auth path in this session before the final live edit can be mirrored.

- **2026-05-19 Task Flow Blocked Resolution Split**
  - Master ID: `AI-INC-20260519-TASK-FLOW-BLOCKED-RESOLUTION-SPLIT-01`
  - Detail log: `project_hub/issues/2026-05-19-task-flow-blocked-resolution-split.md`
  - Repos: `ai_workspace`, `workspaceboard`
  - Status: in progress. Added explicit blocked-resolution classification to the Task Flow recorder and Workspaceboard worker prompts so `blocked` packets now split into `no-action/filed`, `blocker-email-required`, or `routed-needs-owner-question`. Ran the existing no-action repair and converted 38 silent blocked rows to durable `no_action_closed` records. Remaining live blocked packets still need a follow-up pass to decide whether they are true blockers or owner-question routes.

- **2026-05-18 Claude Host Parity And Execution Plan**
  - Master ID: `AI-INC-20260518-CLAUDE-HOST-PARITY-01`
  - Detail log: `project_hub/issues/2026-05-18-claude-host-parity-and-execution-plan.md`
  - Repos: `ai_workspace`, `ai-bridge`, `workspaceboard`, protected-side `.205` readback only
  - Status: implementation planning and worker routing started. DB-backed proof for the Claude host metadata/docs alignment slice now points to OPS project `369808` / task `369809`, with repo-local contract artifact `project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md` and proof marker `CLAUDE_HOST_DOCS_ALIGNED project_hub/artifacts/claude-host-metadata-readback-contract-2026-05-18.md:1`. The read-only bridge-contract slice now points to task `369810`, and the separate migration-map artifact remains anchored to task `369813`. Live `.205` inspection confirmed the real Claude-side config surfaces are `/home/claude/.claude/settings.json`, `settings.local.json`, and `mcp-needs-auth-cache.json`, not the old `.mcp.json` path. The bridge-contract proof marker is `AI_BRIDGE_CONTRACT_READY ai-bridge/contracts/claude-host-read-only-snapshot-contract.md:1 ai-bridge/artifacts/claude-host-read-only-snapshot.example.json:1 jq-ok`. A concrete local migration-map artifact now exists at `project_hub/artifacts/claude-host-tool-layout-migration-map-2026-05-18.md`, classifying what stays in `ai_workspace` versus what should graduate into named tool surfaces. Current repo-local next steps are local auth-dependency surfacing, worker-durability/readback improvements, and the first extraction slice for task-flow/runtime helpers. System-path changes such as `~/.ssh/config` edits or `.205` key authorization remain separate approval-gated work.

- **2026-05-01 AI Workers Setup**
  - Master ID: `AI-INC-20260501-AI-WORKERS-SETUP-01`
  - Detail log: `project_hub/issues/2026-05-01-ai-workers-setup.md`
  - Repos: `ai_workspace`; future approved implementation may touch `workspaceboard`, `ops`, `portal`, `bid`, `salesreport`, `lists`, worker-local runtime state, Google Calendar/Drive/Docs, and mailbox runtimes only after separate approvals
  - Status: local setup bundle completed. Calendar/auth, reminder-runner, polling/inbox, Customer Service setup brief, worker-role/JD audit, Naomi finance, Vanessa tasting directives, Ezra project support, and Internal Communicator recap packets now exist on disk. Frank now has a local `frank/JOB_DESCRIPTION.md` source, National Outreach / Vanessa now has `nationaloutreach/JOB_DESCRIPTION.md`, Asher and Venetia now have local JD sources too, and Naomi, Ezra, AI Manager Robert, Task Manager, Decision Driver, and AI Health Manager now have local JD sources as well. A shared Google Doc source link was supplied on 2026-05-19 and recorded at `project_hub/artifacts/ai-workers-setup/shared-google-doc-source-2026-05-19.md`; a local synthesis note now captures the usable worker/persona guidance at `project_hub/artifacts/ai-workers-setup/shared-worker-persona-guidance-2026-05-19.md`. The remaining work is now content reconciliation for FOH/JD follow-up plus approval-gated auth/runtime/send/finance activation lanes. On 2026-05-18 Robert deferred the two remaining open owner-input OPS tasks by one week, so `369793` and `369794` now read back due `2026-05-27` while completed task `369792` remains closed. No OPS/Portal task, external send, external browse, mailbox connection/body read, auth/OAuth/credential change, runtime/LaunchAgent change, Google Doc write, or production mutation has been performed.

- **2026-05-03 Design & Media Project Manager Agent**
  - Master ID: `AI-INC-20260503-DESIGN-MEDIA-PM-01`
  - Detail log: `project_hub/issues/2026-05-03-design-media-project-manager-agent.md`
  - Repos: `ai_workspace`; future approved implementation may touch `portal`, `workspaceboard`, design-file storage, mailbox source review, OPS/production planning, Forge/media/ad workflows, or worker runtime state only after separate approvals
  - Status: read-only intake reported. Ezra sent Robert the owner-facing completion report on 2026-05-03, subject `Design & Media PM intake complete`, Message-ID `<177783573635.18682.17199363336245390427@kovaldistillery.com>`. On 2026-05-16, the stranded `Fwd: NEW LABELS` intake was converted into a durable internal brief at `project_hub/artifacts/design-media-pm/ezra-new-labels-special-project-brief-2026-05-16.md` using Task Flow event history plus local Drive exports. Next step remains Robert approval for the Portal project/task skeleton and source-of-truth file model. No Portal mutation, design-file change, compliance approval, ordering action, production schedule change, external stakeholder email, Google Doc write, auth/OAuth, deploy, commit, push, or live-system mutation has been performed.

- **2026-04-27 Whole Foods Portal to OPS Outreach Sync**
  - Master ID: `AI-INC-20260427-WHOLE-FOODS-OPS-SYNC-01`
  - Detail log: `project_hub/issues/2026-04-27-whole-foods-ops-sync.md`
  - Repos: `ai_workspace`; future approved implementation may touch `ops` and authenticated WFM demo portal state
  - Status: first approved import complete. Import rule is approved-only: buyer-pending or otherwise not-approved Whole Foods events must be noted but not imported as confirmed OPS Outreach events. Credential blocker resolved and private portal crawl covered April-June. Robert supplied buyer-approval evidence for Request `312022`; six OPS Outreach events `857`-`862` and linked shifts `5184`-`5189` were created, with deterministic account/product links. Confirmation was sent from National Outreach to Sonat and Robert. Remaining sync work: requests `310465`, `310468`, `310470`, and `310472` remain pending/not approved and must not be imported until buyer approval evidence exists.

- **2026-04-21 AI Health Manager System LaunchDaemon Activation**
  - Master ID: `AI-INC-20260421-AI-HEALTH-MANAGER-LAUNCHAGENT-01`
  - Detail log: `project_hub/issues/2026-04-21-ai-health-manager-launchagent-activation.md`
  - Repos: `ai_workspace`, machine-local LaunchAgent state
  - Status: source-backed report-only health check and system LaunchDaemon plist are prepared. Robert clarified server mode only, and the LaunchAgent path is superseded. Health Manager now has an analogous prepared system LaunchDaemon plist at `/Users/werkstatt/ai_workspace/tmp/ai-health-manager/com.koval.ai-health-manager.system.plist`, label `com.koval.ai-health-manager`, `UserName=admin`, cadence `900` seconds, report-only. It is not loaded because `/Library/LaunchDaemons` is root-owned and noninteractive sudo is unavailable. Next step is local admin install/bootstrap/kickstart for this Health-Manager-only system daemon; do not handle the password in chat.

- **2026-04-20 Workspaceboard / AI Work Product Backup Plan**
  - Master ID: `AI-INC-20260420-WORKSPACEBOARD-AI-BACKUP-01`
  - Detail log: `project_hub/issues/2026-04-20-workspaceboard-ai-backup-plan.md`
  - Repos: `ai_workspace`, `workspaceboard`, `ai-bridge`; future approved implementation may touch machine-local Workspaceboard/Frank/Avignon runtime metadata and an approved external/offsite target such as `.200`
  - Status: planning complete and implementation blocked pending explicit approvals. The plan recommends git for committed source/planning records, encrypted artifact snapshots for approved non-git assistant work product, restore testing to an approved temporary path, and an external/offsite mirror only after Robert/Claude/Dmytro confirm target, encryption, retention, cadence, and runtime-state boundaries. No backup, rsync, tar, mount, `.200`/`.205` access, credential access, runtime copy, schedule, deploy, commit, push, or live pull was performed.

- **2026-04-20 Secure Info / Files Context Intake Plan**
  - Master ID: `AI-INC-20260420-INFO-FILES-CONTEXT-INTAKE-01`
  - Detail log: `project_hub/issues/2026-04-20-secure-info-files-context-intake-plan.md`
  - Repos: `ai_workspace`; future approved implementation may touch `ai-bridge`, Workspaceboard, machine-local token storage, and Google Drive API/Google Cloud only after explicit approval
  - Status: docs-only plan added from Robert/Frank source Message-ID `<CAAtX44ZX0u0toGJ7O4grpZY7j6MW9n_S=Anj8M8k-sQhY4gZXQ@mail.gmail.com>` in session `516e1be9`; file-management worker session `0774d4a8` is attached here, not opened as a separate project, because the available excerpt was truncated after `Project: File management.` and overlaps the secure files/context plan. Robert's 2026-04-22 `Next project` request, source Message-ID `<CAAtX44a=rFARtKyiDJ8Ha45KiH+AkJhNXPeaTJ1_UYifyY9LqQ@mail.gmail.com>`, is also attached here because it continues the same file/folder management lane; Frank visible route `b7f9729b` and AI Workspace planning route `f0846b6f` are the related sessions. The first-slice plan is docs-only: login-named user-root file spaces, one shared/general Drive area, a non-secret folder register, human-created folders first, metadata-only test folder, and staged copy planning before any transfer. Robert's continuation source `<CAAtX44YSN9Mr+xcP9woKfcKhONgVYYU73bV7xhqFkf1Nkue52A@mail.gmail.com>` approved that docs-only model. Robert's clarification source `<CAAtX44a4y1DxTkza-T-Eg0huGXDOvzgO4wC7EPZUdG0KCs3Wrw@mail.gmail.com>` says user-root folders are named by login, for example `admin` and `sonat`; arbitrary top-level folders are not the user-root model; and the next test stays inside the approved shared Drive model. Robert's 2026-04-24 clarification further narrowed the access question: both `frank.cannoli@kovaldistillery.com` and `avignon.rose@kovaldistillery.com` already have access to the approved shared Drive, so shared-drive entitlement is no longer the main blocker for those assistant identities. Robert then replied to Frank's approval packet and approved the execution model for the first live slice: first OAuth path `Frank`, reuse the Claude Drive OAuth app/client tied to Task `#1326`, Infisical-backed secret model approved, Infisical preferred for token storage with temporary Mac mini local storage allowed if needed, revocation owner `Codex / Frank`, non-secret audit log `on Mac mini`, and the recommended first slice as proposed (`drive.metadata.readonly` only, shared Drive `0AP-Yf32mH4IHUk9PVA` only, metadata-only, no content reads/writes). Claude Task `#1326` `Google Drive integration via Claude Google Workspace account` remains the current implementation-shape packet, but the cited staging path `/tmp/gdrive-impl/` was not present locally, so it is still summary-backed rather than file-verified. Remaining blocker is now operational rather than policy: the `#1326` implementation bundle or equivalent approved local review path still needs to be available on this machine before the live Frank metadata-only slice can be wired and verified here.

- 2026-04-24 Claude then returned the missing `#1326` handoff details: OAuth app `KOVAL Agents Drive`, client id `872255708765-krtm0oc44ajdbi7sivqb5kpp2hpanjqg.apps.googleusercontent.com`, server-side bundle paths `/srv/tools/gdrive/` and `/tmp/gdrive-impl/`, file set `CLAUDE.md`, `drive.py`, `list.sh`, `download.sh`, `upload.sh`, `test.sh`, staging helper `migrate-credentials-to-infisical.sh`, and package reference `https://papers.koval.lan/67dcb57a-2552-4d35-80cc-f14768934002`. Current blocker is now concrete Mac mini execution prep: adapt credential sourcing away from `/srv/secrets/machine-identity.env`, run Frank's metadata-only OAuth consent, store a Frank-specific refresh token in Infisical, and narrow the runtime scope to `drive.metadata.readonly`.

- **2026-04-19 Codex / Claude / Papers Integration Plan**
  - Master ID: `AI-INC-20260419-CODEX-CLAUDE-PAPERS-01`
  - Detail log: `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`
  - Repos: `ai_workspace`, `workspaceboard`, `ai-bridge`; future approved implementation may touch MI/Papers and `.205`
  - Status: read-only bridge/task-record planning remains active. On 2026-04-24 the local `ws ai` private reference surface corrected the `.205` auth metadata, and a later live read succeeded: SSH access to `192.168.55.205` works as shell user `claude` when using the approved shared password note fetched from the MacBook transfer gate. Live top-level and high-value Claude-side docs are now partly absorbed: `/srv/CLAUDE.md`, Planner, Papers, Email, Agents, plus summary reads of `secretary`, `pm`, `developer`, `tester`, `marketer`, and `webmaster`. Real current config surfaces are now recorded as layered (`/home/claude/.claude/settings.json`, `/home/claude/.claude/settings.local.json`, `mcp-needs-auth-cache.json`, and plugin-local MCP/cache state), so the older `.mcp.json` expectation is stale. The bridge plan now explicitly recommends a side-by-side model with narrow shared contracts: stronger task-record packets, explicit send-confirmation behavior, API-only structured mutation, Infisical-first default for new shared-secret workflows, and single-writer/read-only bridge rules before any shared writable path. The first organigram expansion is already recorded with Claude as a parallel department. No secret value was printed or stored in these records.

- **2026-04-19 Salesreport Audit Gaps Project**
  - Master ID: `AI-INC-20260419-SALESREPORT-AUDIT-GAPS-PROJECT-01`
  - Detail log: `project_hub/issues/2026-04-19-salesreport-audit-gaps-project.md`
  - Repos: `salesreport`, `ai_workspace`; linked routing context in Frank session `58df8905` and Login auth-review session `3b39ab64`
  - Status: docs-only Salesreport project/TODO/HANDOFF setup recorded from source Message-ID `<CAAtX44bsQgSRQbpS4126g-DtLhDoyXvYK0=f0t9FM5us-mvvwQ@mail.gmail.com>` and routed session `53d9ca8f`. Known audit gaps and approval gates are documented; no report code, production data, saved reports, CRM/account records, auth/password state, external sends, deploy, live pull, commit, or push changed. Clarification remains needed for the truncated `But - I mea...` source tail before expanding scope.

- **2026-04-19 Pricing Unification / Portal Pricing Scope**
  - Master ID: `AI-INC-20260419-PRICING-UNIFICATION-PORTAL-01`
  - Detail log: `project_hub/issues/2026-04-19-pricing-unification-portal-scope.md`
  - Repos: `ops`, `ai_workspace`, `avignon`; future approved implementation may involve `portal`, `salesreport`, and pricing source systems
  - Status: local OPS/Codex scope artifact created and Sonat-facing Avignon email sent. Real OPS/Portal task ID is pending because current task-create auth/session path failed before creation. No production pricing data, Portal pricing behavior, customer terms, credentials, deploy, push, live pull, or pricing/CRM records were changed.

- **2026-04-19 Codex / Claude / Papers Integration Plan**
  - Master ID: `AI-INC-20260419-CODEX-CLAUDE-PAPERS-01`
  - Detail log: `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`
  - Repos: `ai_workspace`, `workspaceboard`, `ai-bridge`, future MI/Papers/.205 surfaces
  - Status: Robert's 2026-04-20 blocker-thread reply `<CAAtX44bSgMHtL+Y96sCn+g63U7FLpzbYQ0fCCm48Gc4vtA1QUA@mail.gmail.com>` and follow-up approval `<CAAtX44ZYxUpzOLz1UXNUT-C8CnQSXxGy0hge3ojxW+f3PwBHWw@mail.gmail.com>` are attached as approval/dedupe evidence for the existing no-write/read-only integration plan, not duplicate tasks. 2026-04-22 Papers API approval intake `<CAAtX44YuOqo8n3pjaX7oSeUXHZ22E=__SQe6XZbgvHa=QmwmgA@mail.gmail.com>` supplied Papers pointer `https://papers.koval.lan/e4bd10fa-b121-435f-b5c4-d5d2ec74948c` / task `#1372` (`Papers API Access for Codex/Frank Runtime`, Active, 2026-04-20) and cleared only the next source-only Workspaceboard route for a deny-by-default read-only Papers wrapper. Robert's option B follow-up `<CAAtX44aEoCLf0Mfc2xv-xuGQ0yc4dkn=n3XKQuLOEG_6po6nrg@mail.gmail.com>` is now complete at source/test level in Workspaceboard route `cb518c23`: added `server/papers-readonly-wrapper.js` and `server/test/papers-readonly-wrapper.test.js`; verification passed `node --check`, focused 9/9 test, and full server `npm test` 37/37. Robert's 2026-04-23 approval `<CAAtX44aMxx6qRPNu6NUw5WmfSmQh=KqW2pAcAwoepqzkWOoTDA@mail.gmail.com>` now clears the next Claude-facing access-packet request only: visible AI Workspace route `2894c746` / `Claude MI Papers Mesh access packet` is open with prompt delivery verified, and the packet draft asks Claude for the exact MI/Papers access path, initial body-read scope or document IDs if any, and the exact Mesh / Agent Memory read-only surfaces to wire next. Codex/Claude/Integration roles are present in local role docs and Workspaceboard organigram source; AI-Bridge schema/template/registration artifacts are produced; safe AI-Bridge-local implementation added `bridge/memory/work-record-projection-source-map.json` and `bridge/traces/2026-04-20-approved-next-steps-implementation.md`; Workspaceboard work-record exporter source commit `74fd65f` is complete but not live; Portal existing-account summary and read-only MI/Papers registration designs are produced. Next safe action is Claude's protected-side packet reply, then Code/Git review before any commit/push or runtime wiring for the Papers wrapper. Live `.205`, Papers/MI writes, private Papers body reads without named scope/document IDs, OAuth/auth/token work, Portal/CRM/OPS mutation, mailbox credential/content access, MCP config/runtime changes, deploy/live pull, LaunchAgent/service restart, and external-sensitive replies remain closed.

- **2026-04-18 Frank / Workspaceboard Response Recovery**
  - Master ID: `AI-INC-20260418-FRANK-WB-RESPONSE-01`
  - Detail log: `project_hub/issues/2026-04-18-frank-workspaceboard-response-incident.md`
  - Repos: `ai_workspace`, `workspaceboard`, `login`, machine-local Frank runtime, Mac mini Workspaceboard LaunchAgent
  - Status: Frank direct-email routing/ack recovery is complete and Workspaceboard runtime is rebound to `0.0.0.0:17878`; Robert's phone still failed through the MI auth gateway. Phone send UX fix commit `60277b5d5c5fbea14a5fe86ef1ecf7cb701a9c82` is pushed and verified present in local Apache and Node runtime routes, but no fresh LaunchAgent reinstall was run during closeout because the Workspaceboard checkout has unrelated dirty work and the installer rsyncs the whole tree. Local Login source now accepts the gateway `redirect=` handoff for approved Workspaceboard URLs, and the 2026-04-20 Login/Auth owner pass classified the remaining approval path 3 as mixed but likely blocked on live Login/MI cookie-domain runtime config or `.205` proxy/TLS/iPhone behavior rather than another broad Login code edit. Exact next action is Security Guard plus `.205`/MI owner approved non-secret live config/header check for `.koval.lan` cookie metadata and `wb.koval.lan` forward-auth behavior; any config/proxy/DNS/TLS/session-policy/service change still needs separate narrow approval and rollback. Monday update should also include the Mac mini hard-server-mode path: wire Mac mini, migrate/verify Workspaceboard/Frank/Avignon critical services before Aqua/GUI logout, then only consider old workstation GUI logout; no service migration/restart/logout/LaunchDaemon change is approved by this note.

- **2026-04-18 Frank/Avignon Gmail Push Planning**
  - Master ID: `AI-INC-20260418-FRANK-AVIGNON-GMAIL-PUSH-01`
  - Detail log: `project_hub/issues/2026-04-18-frank-avignon-gmail-push-plan.md`
  - Repos: `ai_workspace`, future approved work may touch Frank/Avignon machine-local runtime state and Google Cloud Pub/Sub/Gmail API
  - Status: OAuth continuation approved by Robert after Monday polling health, reaffirmed in source `<CAAtX44ZUHKpHbNWANyLc8bA9wK3X5bxqnUfPP3QrCm9zyJrhnQ@mail.gmail.com>`, and Robert provided approved OAuth client/source metadata for project `gmailconnector-485021` with client id `261057116535-9gf1pqfg090mm2038sackt82p1r8t8i9.apps.googleusercontent.com`. Execution remains blocked because no documented approved Frank/Avignon token storage path/storage class or exact minimum Gmail API scope has been approved. Keep `com.koval.frank-auto` and `com.koval.avignon-auto` on the current 15-second duplicate-protected polling path. No OAuth flow, token write, mailbox read, Pub/Sub/IAM/project/subscriber mutation, cadence/runtime/production change, external send, deploy, push, or live pull was performed in the 2026-04-20 continuation.

- **2026-04-17 Frank/Avignon Runtime CRM Intake Audit**
  - Master ID: `AI-INC-20260417-FRANK-AVIGNON-RUNTIME-CRM-INTAKE-01`
  - Detail log: `project_hub/issues/2026-04-17-frank-avignon-runtime-crm-intake-audit.md`
  - Repos: `ai_workspace`, `frank`, `avignon`, machine-local Frank/Avignon LaunchAgent/runtime state, pending `importer` recovery queue
  - Status: auto polling restored to 60 seconds and Frank runtime bugs patched. Avignon CRM recovery has completed the importer-safe rows plus bounded Portal work recorded in the detail log; remaining blockers are source `1` target/contact ambiguity and source `10` target distributor-account ambiguity, with source `7` held until those decisions close. Future runtime prevention still needs a separate safe CRM-intake routing patch.

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
  - Status: local no-write projection pack prepared under `project_hub/digital-office/`; OAuth/token rejected storage targets are closed as policy, default storage class is machine-local keychain/private path for per-machine automation or approved secret manager/service-account/keychain-backed path for shared automation, and all live Papers, `.205`, `.17`, OPS/Portal DB, credential, MCP, notification/email, Frank/Avignon runtime, commit/push/deploy gates remain closed

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

## Completed

- **2026-03-15 WireGuard Stability Monitoring**
  - Master ID: `AI-INC-20260315-WIREGUARD-STABILITY-01`
  - Detail log: `project_hub/issues/2026-03-15-wireguard-stability-monitoring.md`
  - Repos: `ai_workspace`, workstation network stack, Linksys/OpenWrt WireGuard config
  - Status: canceled by request on 2026-05-19; no further stability monitoring is needed from this record unless it is reopened.

- **2026-04-27 Barrel Sales API Path Fix**
  - Master ID: `AI-INC-20260427-BARREL-SALES-API-PATH-01`
  - Detail log: `project_hub/issues/2026-04-27-barrel-sales-api-path-fix.md`
  - Repos: `salesreport`, `portal`, `ai_workspace`
  - Status: completed. Repaired the WH barrel Salesreport CRM wrapper so barrel write actions prefer the active Salesreport session/Codex identity instead of falling through to the stale service-account path. Then fixed and deployed the Portal sold-button path so barrel project/tasks are created before notification send, notification failure cannot skip task creation, and project/task creator attribution follows `barrel_details.sold_by`. Barrels `9513` and `9346` on sample request `2678` are sold by Sonat user id `3`, linked to active projects `367538` and `367554`, and each project now has 13 active child tasks after the two generic promote/social tasks per barrel were canceled and removed from active workflow. All project/task creator, owner, modified, and task-history rows were corrected to Sonat; Matt bottling tasks are `367552` and `367568`; removed promote tasks are `367546`, `367547`, `367562`, and `367563`. Live backend is `koval-crm-backend:v20260427barrelc`, and future sold-button projects no longer create promote/social tasks. Avignon emailed Claude with Sonat and Robert copied, then sent a correction telling Claude not to work from the removed promote task IDs. No credential/token value was printed and no password reset, OAuth change, live pull, commit, push, pricing/account commitment, or unrelated production mutation was performed.

- **2026-04-27 Barrel Sales Manager Role Setup**
  - Master ID: `AI-INC-20260427-BARREL-SALES-MANAGER-ROLE-01`
  - Detail log: `project_hub/issues/2026-04-27-barrel-sales-manager-role.md`
  - Repos: `ai_workspace`, `workspaceboard`
  - Status: completed docs/source/organigram setup from Robert's direct chat request. Added the Barrel Sales Manager role for WH Barrel Program reservations, barrel sample requests, sold/unsold state, bottling details, task flow, and Avignon/Sonat barrel-program follow-through. Added Avignon barrel-program guidance and registered the role in the Workspaceboard organigram feed. No live Salesreport/Portal/OPS action, email send, auth/OAuth, deploy, live pull, commit, push, reset, clean, or production mutation was performed.

- **2026-04-27 National Outreach AI Worker Inbox**
  - Master ID: `AI-INC-20260427-NATIONALOUTREACH-AI-WORKER-INBOX-01`
  - Detail log: `project_hub/issues/2026-04-27-nationaloutreach-ai-worker-inbox.md`
  - Repos: `ai_workspace`, machine-local National Outreach mailbox setup state
  - Status: completed; full-body/send-capable runtime installed; Codex/National Outreach Drive API OAuth pending. `nationaloutreach@kovaldistillery.com` is documented as the main shared AI-worker inbox while Frank and Avignon remain separate. Send-from identities now have a registry at `worker_roles/send-from-personas.md`, mapped to worker roles/personas before use; `macee.maddox@kovaldistillery.com` is no longer allowed as a send-from identity because Macee has left. IMAP/SMTP setup verification succeeded, standard AI-worker labels were created, full-body review succeeded for 300 recent messages, and approved queued send processing is enabled. First route counts: Outreach Coordinator `222`, Marketing Manager `49`, Email Coordinator `11`, Internal Communicator `5`, Security Guard/sensitive-review `13`. Robert installed `com.koval.nationaloutreach-auto`. Codex/National Outreach Drive API bundle is prepared under `project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/`; OAuth for `nationaloutreach@kovaldistillery.com` remains the next interactive step.

- **2026-04-26 phpList COT Campaign Send Screen**
  - Master ID: `AI-INC-20260426-PHPLIST-COT-SEND-SCREEN-01`
  - Detail log: `project_hub/issues/2026-04-26-phplist-cot-campaign-send-screen.md`
  - Repos: `lists`, live phpList database
  - Status: completed. Draft campaign `552` was structurally normalized for phpList send/test handling, internal lists `72` and `73` were assigned owner `1`, and a defensive ownerless-list guard was added in `sendemaillib.php`. One requested test for campaign `552` was sent to Robert. Dmytro's sendable phpList subscriber was added to list `95` (`Management Group incl Dmytro`), and Workspaceboard now reports Lists open count `0`. Local commit `c9373b2` exists; GitHub push was blocked by credential-helper error `-25308`, so the one-file live patch was deployed over SSH with a live backup.

- **2026-04-26 Avignon Live Data Reports**
  - Master ID: `AI-INC-20260426-AVIGNON-LIVE-DATA-REPORTS-01`
  - Detail log: `project_hub/issues/2026-04-26-avignon-live-data-reports.md`
  - Repos: `salesreport`, `contactreport`, `ai_workspace`
  - Status: completed. Live Salesreport is at `409e791`, live Contactreport is at `4d81ec2`, unauthenticated checks land on the Salesreport login gate without exposing report content, and Sonat was sent the corrected gated links plus four additional live strategic/outreach report links.

- **2026-02-26 Logout Reliability Regression (Portal/OPS/Login SSO)**
  - Master ID: `AI-INC-20260226-LOGOUT-02`
  - Detail log: `project_hub/issues/2026-02-26-logout-reliability-regression.md`
  - Repos: `login` (shared SSO/logout layer affecting `portal` and `ops`)
  - Status: default OPS/Portal persistence policy approved 2026-04-17; explicit logout revokes Login/OPS/Portal artifacts globally, and next-day Portal/OPS access requires a fresh Login handoff/user action unless longer app persistence is explicitly approved. Implementation remains gated on Security Guard review and no live/session/credential/deploy action is approved by this policy record.

- **2026-04-23 BID Live Transmit Route Diagnostic**
  - Master ID: `AI-INC-20260423-BID-LIVE-TRANSMIT-ROUTE-01`
  - Detail log: `project_hub/issues/2026-04-23-bid-live-transmit-route-diagnostic.md`
  - Repos: `bid`, `ai_workspace`, machine-local SSH client config/history
  - Status: completed read-only route recovery. Canonical BID live transmit path is still `.205` via alias `bid-intelligence-205` to account `claude`, canonical target `/srv/development/bid/intelligence`, live path `/srv/bid/intelligence`, and dry-run-first `rsync` over SSH. This machine can reach `192.168.55.205:22` and already trusts the host key, but it has no local `.205` alias, no matching SSH identity/agent state, and none of the documented private credential-reference files are present in the checked local paths, so authentication remains blocked until the approved credential reference or approved access-bearing session is used. No SSH config, key, credential, rsync, publish, deploy, commit, or push change was performed.

- **2026-04-23 Avignon Calendar Confirmation Dedupe Live Fix**
  - Master ID: `AI-INC-20260423-AVIGNON-CALENDAR-DEDUPE-01`
  - Detail log: `project_hub/issues/2026-04-23-avignon-calendar-confirmation-dedupe-live-fix.md`
  - Repos: `ai_workspace`, machine-local Avignon runtime
  - Status: completed 2026-04-23; Avignon now dedupes Sonat calendar confirmations by meeting slot in both the source mirror and installed `/Users/admin` runtime, so an already-confirmed `Meeting with Robert` slot no longer sends another identical owner confirmation.

- **2026-04-22 Salesreport Coverage Colors Live Deploy**
  - Master ID: `AI-INC-20260422-SALESREPORT-COVERAGE-COLORS-LIVE-DEPLOY-01`
  - Detail log: `project_hub/issues/2026-04-22-salesreport-coverage-colors-live-deploy.md`
  - Repos: `salesreport`, live Salesreport worktree
  - Status: completed from Robert's `Push to live` approval. Local/origin/live all verified at `d94a8ced60cc8a9295a1f0b02f78dffc981d24f4` (`Clarify coverage audit colors`), touching only `sales_report_coverage_audit.php`; live PHP lint, menu evidence, and authenticated CLI render passed; the pre-existing live `.htaccess` modification was preserved.

- **2026-04-22 Frank/Avignon Scheduled Report Runtime Health**
  - Master ID: `AI-INC-20260420-FRANK-AVIGNON-SCHEDULED-REPORTS-01`
  - Detail log: `project_hub/issues/2026-04-20-frank-avignon-scheduled-report-runtime-health.md`
  - Repos: `ai_workspace`, machine-local Frank/Avignon LaunchAgent/runtime state
  - Status: Robert accepted the current state as no further immediate blocker: if a scheduled report does not arrive, he will let us know. Current server-mode email workers are registered as system LaunchDaemons with last exit `0`: `com.koval.frank-auto` runs from `/Library/LaunchDaemons/com.koval.frank-auto.plist`, `runs=11982`; `com.koval.avignon-auto` runs from `/Library/LaunchDaemons/com.koval.avignon-auto.plist`, `runs=12891`. Health check was clean: board OK, `0` unhealthy, remediation not needed. Prepared scheduled-report server-mode plist payloads remain available under `/Users/werkstatt/ai_workspace/tmp/frank-avignon-registration/`, but no further launchd action should be taken unless a scheduled send actually fails.

- **2026-04-21 AI Health Manager Role Setup**
  - Master ID: `AI-INC-20260421-AI-HEALTH-MANAGER-ROLE-SETUP-01`
  - Detail log: `project_hub/issues/2026-04-21-ai-health-manager-role-setup.md`
  - Repos: `ai_workspace`, `workspaceboard`
  - Status: completed docs/source/organigram setup from Robert's direct chat request on 2026-04-21. Added the AI Health Manager role for board/session health checks, stale-session classification, one safe focused nudge, standing monitor liveness review, and concise health reports. Added the role to the Workspaceboard organigram feed. No live scheduler, daemon, LaunchAgent, runtime cadence, service restart, mailbox mutation, email send, auth/OAuth, commit, push, deploy, reset, clean, or production change was performed.

- **2026-04-20 AI Improvement Manager Role Expansion**
  - Master ID: `AI-INC-20260420-AI-IMPROVEMENT-MANAGER-ROLE-EXPANSION-01`
  - Detail log: `project_hub/issues/2026-04-20-ai-improvement-manager-role-expansion.md`
  - Repos: `ai_workspace`
  - Status: completed docs/planning expansion from source Message-ID `<CAAtX44Z0DxQ+ruJfOY2fSA2Un617-dfQiF3BQ7R8aaxDiQiQrA@mail.gmail.com>` in session `124bba8f`. Expanded the existing AI Improvement Manager role with concrete process-improvement checks, update opportunities, workflow analytics review, EOD inputs/outputs, routing boundaries, report structure, examples, and approval gates. No runtime, scheduler, mailbox, analytics integration, production, deploy, commit, or push action was performed.

- **2026-04-19 Codex User Password-Reset Gate Review**
  - Master ID: `AI-INC-20260419-CODEX-PASSWORD-RESET-GATE-01`
  - Detail log: `project_hub/issues/2026-04-19-codex-user-password-reset-gate-review.md`
  - Repos: `login`, `ai_workspace`, shared CRM/Login auth database state for Codex user id `1332`
  - Status: completed after Robert approval on 2026-04-20; updated only Codex user id `1332` password verifier fields from the approved local credential source and verified `reset_required=0`. No password/hash/token/.env content, unrelated user, accessmatrix flag, code, commit, push, deploy, live session, routing, DNS/TLS, or auth policy change was performed. If OPS task creation remains blocked, user id `1332` currently has non-secret access metadata `koval_portal=0`, `koval_ops=0`, and blank `portal_status`; changing those flags needs separate explicit approval.

- **2026-04-18 Salesreport Market Events Static HTML Cleanup**
  - Master ID: `AI-INC-20260418-SALESREPORT-MARKET-EVENTS-STATIC-HTML-CLEANUP-01`
  - Detail log: `project_hub/issues/2026-04-18-salesreport-market-events-static-html-cleanup.md`
  - Repos: `salesreport`, live Salesreport worktree
  - Status: completed; moved the untracked live static Sonat market-events HTML snapshot out of `/home/koval/public_html/salesreport` to a private backup path, preserved the gated PHP report files, and verified the public `.html` URL no longer serves report content

- **2026-04-18 Salesreport Market Events Live Deploy**
  - Master ID: `AI-INC-20260418-SALESREPORT-MARKET-EVENTS-LIVE-DEPLOY-01`
  - Detail log: `project_hub/issues/2026-04-18-salesreport-market-events-live-deploy.md`
  - Repos: `salesreport`, live Salesreport worktree
  - Status: completed; live `/home/koval/public_html/salesreport` fast-forwarded to `fe268bc4126537432302452e2a41541d077d93b1`, Market Events Report menu/source checks passed, unauthenticated direct report and old `.html` Sonat URL redirect to Login, and full non-interactive Codex credential login remained blocked before 2FA

- **2026-04-17 OPS Dashboard Task Creation Session Credential Error**
  - Master ID: `AI-INC-20260417-OPS-DASHBOARD-TASK-CREATE-SESSION-CREDS-01`
  - Detail log: `project_hub/issues/2026-04-17-ops-dashboard-task-creation-session-credential-error.md`
  - Repos: `ops`, `login`, Portal/CRM task API session state
  - Status: investigation complete; local config booleans show Portal API config present, dashboard task-create path traced, and simulated Robert/admin OPS session hydrates a matching non-expired SSO JWT. No credential/auth config/session handling code change, production session mutation, task-create write test, deploy, live pull, push, or commit performed

- **2026-04-16 Event Strategy COT Connecteam Review**
  - Master ID: `AI-INC-20260416-EVENT-STRATEGY-COT-CONNECTEAM-01`
  - Detail log: `project_hub/issues/2026-04-16-event-strategy-cot-connecteam-review.md`
  - Repos: `ai_workspace`; future implementation belongs in `ops` after read-only OPS discovery and Code and Git Manager preflight
  - Status: source-context review completed docs-only. Google Doc returned `HTTP/2 401`, and direct MacBook retrieval of Robert's Markdown path was unavailable in this session, but OPS already records read-only incorporation of the non-sensitive Markdown scheduling context with credential material excluded. No source mutation, mailbox state change, Google Docs mutation, credentials, OPS/Papers/Connecteam/notification/production-data mutation, code change, commit, push, deploy, or runtime change was performed

- **2026-04-16 Google Cloud Security Hardening Plan**
  - Master ID: `AI-INC-20260416-GOOGLE-CLOUD-SECURITY-HARDENING-01`
  - Detail log: `project_hub/issues/2026-04-16-google-cloud-security-hardening-plan.md`
  - Repos: `ai_workspace`; future approved audit may touch Google Cloud admin/billing/IAM surfaces only after explicit human approval
  - Status: planning slice completed docs-only; no Google Cloud console, credentials, keychain, OAuth files, secrets, billing accounts, IAM, live admin surfaces, email, deploys, runtime services, or external-system changes were accessed or performed

- **2026-04-16 Recurring Operations Reporting Plan**
  - Master ID: `AI-INC-20260416-RECURRING-OPERATIONS-REPORTING-01`
  - Detail log: `project_hub/issues/2026-04-16-recurring-operations-reporting-plan.md`
  - Repos: `ai_workspace`; future source ownership split across `ops`, `portal`, `login`, `salesreport`, `contactreport`, and possibly other owner modules after barrel sample ownership is confirmed
  - Status: planning slice completed docs-only; no code, production data, email, notifications, credentials, scheduled jobs, commits, pushes, deploys, or runtime changes were performed

- **2026-04-16 AI-Assisted Salesreport Data Import Plan**
  - Master ID: `AI-INC-20260416-SALESREPORT-AI-DATA-IMPORT-PLAN-01`
  - Detail log: `project_hub/issues/2026-04-16-ai-assisted-salesreport-data-import-plan.md`
  - Repos: `ai_workspace`; future prototype owner `salesreport`, with `importer` and `bid` only as source-side collaborators if approved
  - Status: planning slice completed docs-only; first approved next step would be a no-write prototype with deterministic preflight, AI-generated summaries/mapping suggestions only, and explicit gates for raw data, credentials, production reads, code, email, commits, imports, deploys, and automation

- **2026-04-16 Unified User Activity Reporting Plan**
  - Master ID: `AI-INC-20260416-UNIFIED-USER-ACTIVITY-REPORTING-01`
  - Detail log: `project_hub/issues/2026-04-16-unified-user-activity-reporting-plan.md`
  - Repos: `ai_workspace`; future source ownership split across `login`, `portal`, `ops`, `salesreport`, `contactreport`, `bid`, `importer`, `workspaceboard`, `frank`, and `avignon`
  - Status: planning slice completed docs-only; implementation, production data access, Gmail/Admin overlays, email sends, deploys, and scheduled reports remain unstarted and approval-gated

- **2026-04-09 Werkstatt Path Unification**
  - Master ID: `AI-INC-20260409-WERKSTATT-PATHS-01`
  - Detail log: `project_hub/issues/2026-04-09-werkstatt-path-unification.md`
  - Repos: `ai_workspace`, `workspaceboard`, local workspace roots on Mac mini and MacBook
  - Status: completed; canonical local module roots now use `/Users/werkstatt/<repo>`, with remaining cross-machine sync/runtime follow-up tracked under the AI workstation/sync transition record

- **2026-04-07 MemPalace Salesreport Pilot**
  - Master ID: `AI-INC-20260407-MEMPALACE-SALESREPORT-01`
  - Detail log: `project_hub/issues/2026-04-07-mempalace-salesreport-pilot.md`
  - Repos: `ai_workspace`, `salesreport`
  - Status: completed by Robert decision on 2026-04-12; local Salesreport MemPalace pilot should not be expanded

- **2026-04-16 Workspaceboard Remote Classic Board**
  - Master ID: `AI-INC-20260416-WORKSPACEBOARD-REMOTE-CLASSIC-BOARD-01`
  - Detail log: `project_hub/issues/2026-04-16-workspaceboard-remote-classic-board.md`
  - Repos: `workspaceboard`, `ai_workspace`, Mac mini LaunchAgent/runtime auth state
  - Status: completed; 2026-04-17 relapse after relaunch traced to LaunchAgent host reverting to `127.0.0.1` and fixed by reloading `com.koval.workspaceboard` with `CODEX_DASHBOARD_HOST=0.0.0.0`; authenticated classic-board access remains at `http://192.168.55.17/workspaceboard/`, with unauthenticated direct LAN runtime requests verified as `401` / login redirect

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
  - 2026-04-30 pickup update: Salesreport barrel contact review now has a primary-contact override path, the rebuild honors those selections, Forge `barrel_contacts` reads the same override table, current Portal relationship-management links are recorded, and the six-month refresh path is documented.
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

- **2026-05-24 Recursive Truth-Drift Checker + AI Health Integration**
  - Master ID: `AI-INC-20260524-RECURSIVE-TRUTH-DRIFT-01`
  - Detail log: `project_hub/artifacts/recursive-tools/recursive-improve-pilot-setup-2026-05-24.md`
  - Repos: `ai_workspace`, `workspaceboard`

- **2026-05-24 Recursive Tools Stack Update + Local Codex Skills Pull-In**
  - Master ID: `AI-INC-20260524-RECURSIVE-TOOLS-UPDATE-01`
  - Detail log: `project_hub/artifacts/recursive-tools/recursive-tools-stack-update-2026-05-24.md`
  - Repos: `ai_workspace`, `workspaceboard`
  - Latest: AI Health now records recursive proposal status on its existing cadence, including board-down reports. No separate recursive LaunchDaemon was added. Papers update: `https://papers.koval.lan/f95e7f60-fda6-495c-a485-b2c66ff29110`.
  - Claude bridge: Planner schema mapping recorded at `project_hub/artifacts/recursive-tools/claude-planner-recursive-schema-2026-05-24.md`; Papers `https://papers.koval.lan/1e7119d3-e2cc-4ff0-900f-d1251eaa5f0a`. The Codex-side `/proof` verifier is now wired at `scripts/claude_planner_proof_check.py` and AI Health reports `claude_planner_proof=not-ready` until `https://planner.koval.lan/api/tasks/1725/proof` is reachable and clean. Local note: `project_hub/artifacts/recursive-tools/claude-planner-proof-verifier-wired-2026-05-24.md`; Papers `https://papers.koval.lan/542f8733-3aef-4cde-ad65-0da61d6b9781`.
