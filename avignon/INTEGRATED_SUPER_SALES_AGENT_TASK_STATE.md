# Integrated Super Sales Agent Task State

Durable Avignon working notes for Sonat's Integrated Super Sales Agent project.
Keep entries concise, dated, and decision-oriented. Record substantive
conversations, calibration decisions, next actions, and approval gates here so
the project state survives beyond chat.

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
