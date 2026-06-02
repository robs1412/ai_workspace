# Integrated Super Sales Agent Task State

Durable Avignon working notes for Sonat's Integrated Super Sales Agent project.
Keep entries concise, dated, and decision-oriented. Record substantive
conversations, calibration decisions, next actions, and approval gates here so
the project state survives beyond chat.

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
