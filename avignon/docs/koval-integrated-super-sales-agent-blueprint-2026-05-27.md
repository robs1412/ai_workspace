# KOVAL Integrated Super Sales Agent Blueprint

Date: 2026-05-27
Prepared for: Sonat Birnecker Hart
Source reviewed: `Integrated Super Sales Agent - Possible Structure.pdf`

## Executive Summary

The reviewed document has the right strategic direction: KOVAL should not build a generic sales chatbot. The best structure is a supervised sales intelligence system that turns sales history, distributor data, CRM notes, territory context, brand pillars, and field activity into specific account actions.

The first useful version should focus on weekly account prioritization and field-call preparation. Scraping, route optimization, voice, and consumer-facing widgets are useful later, but they should sit on top of a reliable sales ledger and clear KOVAL-specific account logic.

## Recommended Architecture

Use a three-layer system:

1. Core Sales Intelligence Layer

This is the source of truth. It should hold accounts, contacts, distributor, territory, SKU history, depletion/order trends, visit history, buyer notes, brand-fit indicators, and compliance constraints.

2. Specialist Agent Layer

Specialist agents should produce account-level signals:

- Depletion and reorder-risk agent: identifies accounts likely due for reorder, lapsed velocity, lost placements, and urgent follow-up.
- Account health agent: summarizes relationship history, last activity, prior commitments, samples, meetings, and unresolved follow-ups.
- Brand-alignment agent: scores accounts for KOVAL and Thresh & Winnow fit using organic, kosher, regenerative, farm-to-table, woman-owned, craft cocktail, premium spirits, local sourcing, and sustainability signals.
- Smart basket agent: proposes SKU-level pitches and curated portfolio baskets based on account type, prior purchases, brand fit, seasonality, and allocation rules.
- Territory planner: ranks accounts by opportunity score, groups them by geography, and creates weekly or daily target lists.
- New account scout: monitors new openings, liquor licenses, hospitality news, Google Maps/new-place signals, and social bios for aligned prospects.
- Competitive/menu intelligence agent: tracks cocktail menus and account websites for competitor placement, missing category opportunities, and KOVAL-friendly menu language.

3. Field Activation Layer

This is what Sonat and reps should actually use. It should produce:

- Monday territory game plan
- Daily route priority list
- Account stop briefing
- Three-sentence pitch
- Recommended SKU or basket
- Objection-handling notes
- Follow-up draft
- CRM activity summary after the call

## Operating Model

The Supervisor Sales Agent should not make unsupported decisions. It should compile signals, rank opportunities, and produce recommendations with proof.

Every recommendation should answer:

- Why this account now?
- What changed since the last touch?
- What should we pitch?
- Which KOVAL or Thresh & Winnow story matters here?
- What is the evidence?
- What should be logged after the call?

The recommended opportunity score should combine:

- Reorder risk
- Account value
- Brand alignment
- Relationship strength
- Strategic importance
- Distributor incentive or timing
- Route efficiency
- Allocation eligibility
- Compliance restrictions

## KOVAL-Specific Field Brief Format

Each field stop should be reduced to a practical briefing:

Account: Alice's Table
Why now: Organic food program, no organic whiskey on current menu, last KOVAL order 7 weeks ago.
Pitch: Pioneer Flight: KOVAL Bourbon, KOVAL Cranberry Gin, Thresh & Winnow Rye.
Proof: Their menu leads with farm sourcing and seasonal pairings.
Ask: Taste through the flight and commit to one cocktail placement or back-bar set.
Follow-up: Send cocktail spec sheet and log buyer feedback in CRM.

This is the core product. If this output is useful, the system is working.

## Phased Build Plan

Phase 1: Sales Ledger and Weekly Account Prioritization

- Build or connect a central Postgres/Supabase account ledger.
- Import CRM accounts, contacts, territories, product history, distributor/order/depletion files, and activity history.
- Define the KOVAL account tiers and brand-fit fields.
- Produce a weekly ranked account list for Sonat: action needed, reason, evidence, recommended next step.

Phase 2: Field Briefing Agent

- Convert account intelligence into a rep-ready stop briefing.
- Add pitch templates for retail, on-premise, distributor, chain, independent, and premium allocation accounts.
- Add post-call logging prompts so field activity turns back into structured CRM data.

Phase 3: Smart Basket and Story Basket Builder

- Create curated SKU recommendations by account type and brand fit.
- Prefer portfolio story baskets over bulk-volume baskets.
- Add allocation logic so rare Thresh & Winnow expressions are recommended only for qualified tier-one accounts.

Phase 4: Brand-Pillar Scouting

- Add website/menu/social scraping for account alignment signals.
- Score prospects for organic, kosher, regenerative, farm-to-table, woman-owned, premium/craft, and sustainability fit.
- Add new-opening alerts for high-fit accounts.

Phase 5: Route Optimization and Mobile Delivery

- Group priority accounts by geography.
- Add route optimization after scoring is trusted.
- Deliver daily briefings by mobile digest first; add voice only once the written briefing is proven.

Phase 6: Later-Stage B2B2C Tools

- Consider a retailer-facing digital mixologist only after internal field execution is reliable.
- Use it selectively for top retail partners where KOVAL can influence sell-through and account loyalty.

## Tooling Recommendation

Recommended first-stack:

- Postgres or Supabase for the account ledger
- Python + Polars for distributor/depletion file processing
- n8n for controlled CRM and workflow sync
- LLM structured outputs with Pydantic for account scoring and brief generation
- Firecrawl or Jina Reader for website/brand-pillar extraction
- PostGIS and OR-Tools for later route grouping and optimization

Defer until later:

- Multi-agent frameworks like LangGraph or CrewAI
- Real-time voice assistant
- Embeddable consumer widget
- Large-scale menu scraping across all territories

## Compliance And Approval Gates

The agent must not automatically send external account emails, quote pricing, promise samples, make allocation commitments, or issue distributor-sensitive instructions without approval.

Required gates:

- State-specific alcohol rules
- Distributor and pricing restrictions
- Sample and event policy
- Allocation eligibility
- Human approval for external account communication
- Clear source evidence for any sales recommendation

## First 30 Days

Week 1:

- Define account ledger fields.
- Select one pilot territory.
- Import CRM/account history and current distributor/order data.
- Define tiering and account-fit rules with Sonat.

Week 2:

- Build the first weekly account priority report.
- Produce the first field briefing format for the top 25 accounts.
- Review with Sonat and tune scoring.

Week 3:

- Add smart basket recommendations.
- Add post-call CRM summary prompts.
- Add basic reorder-risk detection.

Week 4:

- Run a field pilot.
- Compare recommendations against actual rep judgment.
- Decide whether to expand into brand-pillar scraping or route optimization next.

## Best Next Step

Do not start by building the full multi-agent system. Start with the weekly account priority engine and field briefing output. That will prove whether the intelligence is operationally useful. Once that works, add scraping, routing, voice, and consumer-facing tools in sequence.
