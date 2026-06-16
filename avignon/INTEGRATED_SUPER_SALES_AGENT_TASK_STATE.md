# Integrated Super Sales Agent Task State

Durable Avignon working notes for Sonat's Integrated Super Sales Agent project.
Keep entries concise, dated, and decision-oriented. Record substantive
conversations, calibration decisions, next actions, and approval gates here so
the project state survives beyond chat.

## 2026-06-16

- Source: Sonat direct-owner email, subject `Heinens and Woodmans`, Message-ID `<CALbLtzymzc3jD0qSxsi0WLHMzWAQDsLb4j1XpzjcQMjBaoGH2g@mail.gmail.com>`; dedupe key `avignon-direct-owner-sonat-CALbLtzymzc3jD0qSxsi0WLHMzWAQDsLb4j1XpzjcQMjBaoGH2g-mail-gmail-com`; Workspaceboard session `5c27b015`.
- Topic: Woodman's operating model for the Integrated Super Sales Agent.
- Decision: Treat Woodman's as a store-by-store purchasing-manager opportunity, not as a single corporate-buyer lane. Sonat's note says Woodman's stores are run by each store's purchasing manager; she has reached out to the DMs to secure buyer information, but the field plan should still include store-specific visits.
- What changed: Future Integrated Super Sales Agent logic should tag Woodman's as a local chain/store-led account type. For Woodman's rows, the next action should be buyer discovery by store, DM buyer-info follow-up, and store-specific visit planning rather than corporate-only chain outreach.
- Current source-data readback: the 2026 Illinois top-200 account sheet already includes Woodman's Buffalo Grove, Carpentersville, North Aurora, and Bloomingdale rows, plus Heinen's Glenview and Lake Bluff rows. This update changes only Woodman's operating guidance because this packet provided no separate Heinen's operating instruction.
- Concrete next action: On the next account-action-plan revision, add a `store-led local chain` treatment for Woodman's with per-location buyer-contact fields, visit prompts, and DM follow-up notes.
- Remaining approval gates: no external account outreach, CRM/Portal contact updates, pricing/sample/allocation/account commitments, or Heinen's treatment change until Sonat approves a specific execution lane or provides the missing operating facts.
- Boundaries observed: durable Avignon ledger/decision update and Sonat completion report only. No CRM/Portal/OPS mutation, auth/OAuth/token work, credential exposure, external reply, Robert copy, pricing/sample/allocation/account commitment, or live data mutation.

## 2026-06-10

- Source: Robert task-mode chat asked to send Sonat the list of decisions needed to move the Integrated Super Sales Agent forward.
- Topic: Sonat next-decision packet for Illinois execution.
- What changed: Sent Sonat a concise next-action list covering approval for the five-account field-review packet, approval for contact-cleanup research, Binny's/local-chain treatment, and recommended execution order.
- Outbound proof: Codex Local Agent sent `Integrated Super Sales Agent: decisions needed to move Illinois forward` to Sonat at `2026-06-10 18:09 CDT`, Message-ID `<178113297762.45012.14107824674434327833@kovaldistillery.com>`. Sent-folder header readback confirmed To `sonat@kovaldistillery.com`.
- Remaining approval gates: wait for Sonat's decisions before external account emails, CRM/Portal updates, pricing/sample/allocation/account commitments, or chain/program outreach.
- Note: The installed Avignon sender was not executable from this shell because an installed runtime import is admin-only. The message was sent transparently as a Codex coordination note carrying Avignon's next-action list.

## 2026-06-09

- Source: Sonat direct-owner email, subject `Account list`, Message-ID `<CALbLtzzN6cRfQccuB_1xaKvTSnbVAATtMsqORPX2xZJyY=hRPQ@mail.gmail.com>`; AI Manager input `3017`; visible worker session `afc3565b`.
- Topic: Current Illinois operating account ledger for the Integrated Super Sales Agent.
- What changed: Salesreport generated a 2026 Illinois top-200 account contact sheet from read-only Salesreport/CRM invoice, account, address, product, and contact tables. The output includes purchase amount, purchased products, address where available, CRM contact information where available, and Portal account URLs.
- New source artifacts: `/Users/werkstatt/salesreport/doc/avignon-sonat-illinois-top200-account-contact-sheet-2026-06-09.md` and `/Users/werkstatt/salesreport/doc/avignon-sonat-illinois-top200-account-contact-sheet-2026-06-09.csv`; generator `/Users/werkstatt/salesreport/scripts/generate_avignon_illinois_top200_account_sheet.php`.
- Readback: 200 Illinois accounts; 43 accounts with at least one CRM contact; 157 accounts without CRM contact; combined 2026 purchased amount `$329,928.03`; combined 2026 cases `2,813.33`; invoice window `2026-01-01` through `2026-05-31`.
- Current follow-through: Built a read-only top-50 action split from the top-200 CSV at `/Users/werkstatt/ai_workspace/avignon/docs/integrated-super-sales-agent-top50-action-plan-2026-06-09.md` and `/Users/werkstatt/ai_workspace/avignon/docs/integrated-super-sales-agent-top50-action-plan-2026-06-09.csv`; generator `/Users/werkstatt/ai_workspace/scripts/avignon_integrated_sales_agent_action_plan.py`.
- Action-plan readback: top 50 reviewed; 5 rep-ready non-chain accounts with email/phone routes; 16 non-chain accounts needing contact cleanup; 29 chain/program accounts; 5 initial field briefings; 25 contact-cleanup targets.
- Owner-facing packet: Avignon emailed Sonat the current action packet on 2026-06-09 with subject `Integrated Super Sales Agent: Illinois action packet`, Message-ID `<178102847118.48164.8463415706429370315@kovaldistillery.com>`, no cc/bcc.
- Concrete next action: Convert the available initial field briefings into a Sonat/rep review packet, and run a contact-cleanup research pass for the 25 highest-value non-chain accounts without usable contact routes.
- Remaining approval gates: no CRM/Portal contact creation or updates, no external account email, no pricing/sample/allocation/account commitments, and no chain/program outreach until Sonat approves the specific next action lane.
- Boundaries observed: read-only analysis/report generation and Avignon ledger update only. No external sends, CRM/Portal/OPS mutation, auth/OAuth/token work, pricing/sample/allocation/account commitments, or credential exposure.

## 2026-06-07

- Source: Workspaceboard session `f2536c08`, scheduler-bridge packet `scheduler-bridge-avignon-20260607-115920`, AI Manager input `2826` / UUID `ai-manager-chat-20260607165744-1299c29cd296`.
- Topic: Integrated Super Sales Agent Phase I Illinois chain revision implementation.
- What changed: Updated the read-only Salesreport Phase I Illinois generator so the main ranked top-25 excludes chain/program-managed accounts and focuses on independent or locally influenceable Illinois accounts. Costco, Whole Foods Market, Binny's, and similar chain/program rows are now split into a separate distributor-support lane with corporate/program questions instead of normal store-level reorder actions.
- New report artifact: `/Users/werkstatt/salesreport/doc/avignon-sonat-integrated-super-sales-agent-phase1-illinois-2026-06-07.md`.
- Baseline comparison: the 2026-05-28 report put Costco stores in 20 of the top 21 positions; the 2026-06-07 revision moves those chain signals out of the main list while preserving them for distributor/corporate follow-up.
- Remaining Sonat calibration question: Binny's and similar local chains may need a hybrid treatment. Sonat should decide whether they stay in the chain/program lane, return selected stores to the local-action lane, or show both store-level and buyer-level tasks.
- Verification: `php -l /Users/werkstatt/salesreport/scripts/generate_avignon_phase1_illinois_priority.php`; `php /Users/werkstatt/salesreport/scripts/generate_avignon_phase1_illinois_priority.php`; targeted report readback confirmed 25 independent ranked accounts and 40 chain/program accounts.
- Boundaries observed: read-only Salesreport analysis/report generation plus Avignon ledger update only. No external sends, CRM/Portal/OPS mutation, auth/OAuth/token work, pricing/sample/allocation/account commitments, or credential exposure.

- Source: Robert task-mode chat in AI Workspace, mirrored to AI Manager input `2826` / UUID `ai-manager-chat-20260607165744-1299c29cd296`.
- Topic: Next implementation slice for the Integrated Super Sales Agent.
- Direction: Robert wants Avignon actively working the next steps so the overall sales-agent plan progresses.
- Concrete next action: Revise the Phase I Illinois logic and report so the main ranked top-25 focuses on independent or locally influenceable accounts, while Costco, Whole Foods Market, and similar corporate/chain accounts are split into a separate chain/program section.
- Expected deliverable: Updated read-only Salesreport generator/report artifacts, with a concise Avignon summary explaining the independent-account ranking, the chain/program lane, evidence used, scoring changes, and any remaining Sonat calibration questions.
- Suggested implementation sequence: classify chain/corporate accounts; adjust the independent-account score; add a separate chain/program lane with distributor-support notes and corporate-decision questions; regenerate the Illinois report; compare against the May 28 baseline; record what changed and what still needs Sonat review.
- Routed worker: Workspaceboard session `f2536c08` / `Avignon: Integrated Super Sales Agent Phase I Chain Revision`; attachment group `76a1b3fe-069`; prompt delivery verified and session-history readback showed `work_state=working` at `2026-06-07 11:59 CDT`.
- Boundaries: Read-only analysis/report generation unless separately approved. No external sends, pricing commitments, sample commitments, allocation commitments, account commitments, OAuth/token/auth work, or CRM/Portal/OPS mutation beyond safe readback.

## 2026-05-31

- Source: Sonat direct-owner email, subject `Re: Integrated Super Sales Agent`, Message-ID `<CALbLtzxMQAs-tBgQo46mDRzAA_XJ9N_56nV_MdanRN-pjR96mw@mail.gmail.com>`.
- Topic: Chain-account handling for the Integrated Super Sales Agent scoring model.
- Decision: Chains should be addressed separately from independent accounts because they usually require distributor help and SKU changes are harder to influence at the store level. Whole Foods Market belongs in this corporate/chain lane because decisions are made centrally.
- What changed: The prior open Costco-heavy lapsed-order question is no longer just a calibration uncertainty. The next model iteration should split chain/program accounts out of the regular Illinois priority list, keep them visible in a dedicated chain lane, and score them on chain-readiness signals instead of treating them as normal store-level reorder opportunities.
- Concrete next action: Update the Phase I Illinois logic and report format so the main top-25 list focuses on independent or locally influenceable accounts, while Costco, Whole Foods Market, and similar chain/corporate accounts appear in a separate chain/program section with distributor-support notes and open corporate-decision questions.
- Linked state: Workspaceboard session `903eb064`; dedupe key `avignon-direct-owner-sonat-CALbLtzxMQAs-tBgQo46mDRzAA-XJ9N-56nV-MdanRN-pjR96mw-mail-gmail-com`; AI Manager input `2427`.
- Boundaries: No CRM/Portal/OPS mutation, OAuth/token/auth work, external replies, pricing commitments, sample commitments, account commitments, or Robert copy were authorized by this decision update.

- Source: Sonat direct-owner email, subject `Integrated Super Sales Agent`, Message-ID `<CALbLtzwopwVi+xASHU7AU5_rsXtg_h+xLKq_j36JsnKsLcOudg@mail.gmail.com>`.
- Topic: Durable recordkeeping for Integrated Super Sales Agent work.
- Decision: For every substantive conversation or decision on this project, Avignon will add a concise dated note to this task-state file and cross-reference the relevant Avignon handoff/event log when a source email, Workspaceboard session, report artifact, or owner-visible closeout exists.
- Current continuity anchor: Phase I Illinois Google Doc was completed and reported on 2026-05-28 from Workspaceboard session `a895aed7`; Sonat's remaining calibration decision is whether the top-25 list is true priority versus false positive, and whether the Costco-heavy lapsed-order signal should be capped or split into a chain/program lane.
- Next action: Treat this file as the project ledger before any future Integrated Super Sales Agent substantive closeout; add the goal/topic, decision, what changed, remaining approvals, and any linked source/session/report IDs.
- Boundaries: No CRM/Portal/OPS mutation, OAuth/token/auth work, external replies, pricing commitments, sample commitments, or account commitments were authorized by this recordkeeping request.
