# KOVAL Integrated Super Sales Agent Phase 1 Next Action

Date: 2026-05-27
Owner: Sonat Birnecker Hart
Workspaceboard session: 5eeff9b2
Source Message-ID: <CALbLtzyb6C6nkZ0esP=+f41=sHY09SWQf98+=yrQwCAs8sT3Jw@mail.gmail.com>

## Point

Start Phase 1 as a two-week sales-ledger prototype, not as a full agent build.

The concrete next action is to pick one pilot territory, assemble the minimum account ledger, and produce one weekly ranked account-priority report that Sonat can review and correct.

## Phase 1 Sprint

1. Select one pilot territory.
2. Build or connect the central account ledger in Postgres or Supabase.
3. Import the minimum useful data:
   - CRM accounts and contacts
   - territories and account ownership
   - product order or depletion history
   - activity history
   - account type and tier fields
4. Define the first KOVAL scoring rules:
   - reorder risk
   - lost or lapsed account risk
   - account value
   - strategic account tier
   - brand-fit indicators
   - next useful sales action
5. Produce the first weekly account-priority report.

## First Deliverable

The first deliverable should be a ranked list of 25 accounts with:

- account name
- owner/territory
- reason it is on the list
- evidence from sales/activity history
- recommended next action
- suggested KOVAL or Thresh & Winnow pitch
- CRM note to log after the call

## Acceptance Test

Phase 1 is successful only if Sonat can look at the weekly list and say:

- these accounts are real priorities
- the reasons are useful
- the recommendations are specific enough for field action
- the evidence is visible
- the bad recommendations are easy to correct

## What Not To Do Yet

Do not start with route optimization, voice, consumer widgets, broad scraping, or a complex multi-agent framework. Those should wait until the weekly priority list is accurate enough to trust.

