# OPS overdue AI-worker task triage - 2026-05-26

Source: local OPS `workflow_load_tasks` using the same AI-worker overdue filter as `/ops/tasks.php`: `filter=overdue-oldest`, all AI worker ids/labels, completed excluded, limit 500. Public curl to `https://www.koval-distillery.com/ops/tasks.php` returned the site security 406 page, so this readback used the local OPS DB path.

## Counts

- Total overdue AI-worker rows: 56
- Robert-created rows eligible for normal OPS intake after approval: 35
- Codex-created bookkeeping/projection rows to clean separately: 21
- Status mix: Not Started=52, In Progress=3, Deferred=1
- Worker mix: Agent Codex=38, Sterling Vanessa=12, Agent Codex, Birnecker Robert=2, Stern Naomi=1, Agent Codex, Birnecker Robert, Saller Sebastian=1, Katz Ezra=1, Cannoli Frank=1
- Due month mix: 2026-03=4, 2026-04=21, 2026-05=31
- Workspace guess mix: ops=21, unknown=11, bid=6, workspaceboard=5, forge=4, frank=4, salesreport=3, portal=2

## Robert-created oldest/high-signal rows

- OPS 363052 | due 2026-03-06 | Not Started | Agent Codex | bid | Forge task ... donations
- OPS 363053 | due 2026-03-06 | Not Started | Agent Codex | forge | forge task... barrel contact list
- OPS 334481 | due 2026-03-06 | Not Started | Agent Codex, Birnecker Robert | salesreport | DA and incentive strategy
- OPS 363191 | due 2026-03-10 | Not Started | Agent Codex | unknown | Square list
- OPS 366460 | due 2026-04-10 | Not Started | Agent Codex | bid | BID finance/report workflow follow-up
- OPS 366486 | due 2026-04-11 | Not Started | Agent Codex | bid | BID improvement follow-up from Papers note 3a05a0dd
- OPS 366563 | due 2026-04-14 | Not Started | Agent Codex | unknown | OpenWrt/LuCI 25.12.2 custom image evaluation follow-up
- OPS 366584 | due 2026-04-15 | Not Started | Agent Codex | bid | BID data-import-2 finance CSV preflight profiles
- OPS 366583 | due 2026-04-18 | Not Started | Agent Codex | ops | Finish in-house Outreach events module parity
- OPS 366461 | due 2026-04-20 | Not Started | Agent Codex | salesreport | Refine Salesreport AI reports with Sonat and Frank
- OPS 366581 | due 2026-04-22 | Not Started | Agent Codex | unknown | Review client-side SSH hardening across Mac mini, M4 Mac mini, and MacBook
- OPS 367057 | due 2026-04-24 | Not Started | Agent Codex | ops | Google Takeout backup - Robert
- OPS 366809 | due 2026-04-29 | Not Started | Agent Codex | ops | Re-check Portal password rollout reset flags
- OPS 367972 | due 2026-05-01 | In Progress | Stern Naomi | bid | Naomi: Financial Planning, QuickBooks, and Square data buildout
- OPS 366499 | due 2026-05-01 | Not Started | Agent Codex, Birnecker Robert, Saller Sebastian | ops | Start Trainual videos for core systems
- OPS 367378 | due 2026-05-01 | Not Started | Agent Codex | frank | Review MD docs and Frank inbox for missed TODOs and ideas
- OPS 367840 | due 2026-05-04 | Not Started | Katz Ezra | unknown | Ezra: email Robert and Sebastian status/top 5 from Google Doc
- OPS 368768 | due 2026-05-06 | Not Started | Sterling Vanessa | ops | Vanessa: continuous National Outreach email polling and routing
- OPS 368769 | due 2026-05-06 | Not Started | Sterling Vanessa | ops | Vanessa: continuous tasting schedule change session routing
- OPS 368516 | due 2026-05-17 | Not Started | Sterling Vanessa | ops | Vanessa: submit or close overdue COT Activity weekly report 6147830
- OPS 334480 | due 2026-05-18 | Not Started | Agent Codex, Birnecker Robert | bid | Scraper Analytics
- OPS 367971 | due 2026-05-24 | Not Started | Sterling Vanessa | ops | Vanessa: automate 8 AM day-of COT event detail emails
- OPS 368772 | due 2026-05-24 | Not Started | Sterling Vanessa | ops | Vanessa: daily noon tasting schedule change check
- OPS 368770 | due 2026-05-24 | Not Started | Sterling Vanessa | ops | Vanessa: daily 9:30 PM taster check-in after last tasting
- OPS 368771 | due 2026-05-24 | Not Started | Sterling Vanessa | unknown | Vanessa: daily 11 PM post-tasting activity review

## Codex-created projection rows

- OPS 366206 | due 2026-04-11 | Not Started | unknown | hitlist optimization
- OPS 366207 | due 2026-04-11 | Not Started | forge | forge emails
- OPS 366208 | due 2026-04-11 | Not Started | unknown | ai data analytics
- OPS 366209 | due 2026-04-11 | Not Started | portal | duplicates in portal
- OPS 366210 | due 2026-04-11 | Not Started | salesreport | salesreport AI reporting workflow
- OPS 366211 | due 2026-04-11 | Not Started | ops | Outreach reliability and admin stats
- OPS 366212 | due 2026-04-11 | Deferred | ops | AI task kanban in OPS
- OPS 366213 | due 2026-04-11 | Not Started | forge | Communications setup strategy
- OPS 366218 | due 2026-04-18 | Not Started | frank | Audit CPanel forwarders for koval-distillery.com
- OPS 366219 | due 2026-04-18 | Not Started | frank | Audit Google default routing for kovaldistillery.com
- OPS 366220 | due 2026-04-18 | Not Started | frank | Document mail routing map and gap analysis
- OPS 366221 | due 2026-04-18 | Not Started | forge | Audit group-mail strategy across Portal, Forge, and Lists
- OPS 368727 | due 2026-05-06 | Not Started | ops | Design PM follow-up: Milestone needs readback: matching OPS task, date, owner - Kickoff and target date
- OPS 368728 | due 2026-05-06 | Not Started | ops | Design PM follow-up: Milestone needs readback: date, owner, blocker readback - File register and version control
- OPS 369809 | due 2026-05-18 | Not Started | unknown | Claude host metadata and docs alignment
- OPS 369810 | due 2026-05-18 | Not Started | unknown | AI Bridge read-only Claude host snapshot contract
- OPS 369811 | due 2026-05-18 | Not Started | ops | Workspaceboard auth dependency readback surface
- OPS 369812 | due 2026-05-18 | Not Started | workspaceboard | Workspaceboard worker durability and session-state improvement slice
- OPS 369813 | due 2026-05-18 | Not Started | unknown | Local modular tool-layout migration map from Claude host
- OPS 369814 | due 2026-05-25 | In Progress | workspaceboard | Workspaceboard planner-surface extraction for Task Flow helpers
- OPS 369816 | due 2026-05-25 | In Progress | workspaceboard | Workspaceboard AI Health entrypoint extraction

## Recommended handling

1. Do not auto-execute all 56 in one hidden pass. Use the manual OPS intake approval gate.
2. Prioritize the 35 Robert-created rows first, grouped by workspace, because those match the current OPS intake rule.
3. Treat the 21 Codex-created rows as projection hygiene: verify whether work is already done, duplicated in Task Flow, or still useful before completing/rescheduling them silently.
4. Start with the oldest Robert-created Codex-owned rows, then active owner-specific standing rows such as Vanessa/Naomi/Frank only after checking their live worker lanes.

## Started Cleanup

- 2026-05-26 16:14 CDT: Closed OPS `363052` (`Forge task ... donations`) as stale completed work. Proof: live Forge `/home/koval/public_html/forge` contains `donations_approved` source workflow and README `Approved Donation Requests`; source DB readback for `koval_donations.donationrequests_approved` returned 3,692 approved rows and 3,009 distinct emails. OPS status changed from `Not Started` to `Completed` with notification suppressed.
- 2026-05-26 16:17 CDT: Closed OPS `363053` (`forge task... barrel contact list`) as stale completed work. Proof: live Forge contains `barrel_contacts` source workflow and README `Barrel Buyers Re-Engagement`; OPS status changed from `Not Started` to `Completed` with notification suppressed.
- Current overdue AI-worker count after those closeouts: 54. Next oldest row is OPS `334481` (`DA and incentive strategy`), which is not a stale implementation row and should be handled as a real Salesreport strategy/reporting execution pass rather than silently closed.
