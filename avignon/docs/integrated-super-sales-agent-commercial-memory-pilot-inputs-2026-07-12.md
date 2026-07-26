# Integrated Super Sales Agent: Commercial Memory Pilot Inputs

Date: 2026-07-12
Owner: Sonat Birnecker Hart
Source: `Re: Integrated Super Sales Agent: Commercial Memory & Action Engine`
Source Message-ID: `<CALbLtzyFVohXdxY27dzHd+9Uvu_xqJzX_CHZ1rM6XBTNi4-zZA@mail.gmail.com>`
Task Flow: `taskflow-01ed76f3ec730817`

## Decision

Use a four-mile straight-line pilot radius from KOVAL Distillery, 4241 N Ravenswood Ave, Chicago. All 15 accounts Sonat selected match to active Portal account surfaces within that radius. Treat this as the first Commercial Memory & Action Engine account set.

The radius result uses the Portal coordinate for the exact distillery address (`41.9590972, -87.6735194`) and each matched account's Portal coordinates, calculated with the Haversine great-circle formula. This is a territory screen, not drive-time routing.

## Pilot account match

| Sonat's account | Portal match | Portal ID | Miles | Radius result |
| --- | --- | ---: | ---: | --- |
| Andersonville Wine and Spirits | Andersonville Wine & Spirits | 2837 | 1.22 | Inside |
| Gideon Wells | Gideon Welles Craft Beer and Kitchen | 40266 | 0.68 | Inside |
| Gene's Sausage Shop | Gene's Sausage Shop Lincoln | 629 | 0.96 | Inside |
| Paulina Meat Market | Paulina Meat Market | 44998 | 0.95 | Inside |
| Little Bad Wolf | Little Bad Wolf | 38134 | 1.69 | Inside |
| Lady Gregory's | Lady Gregory's - N. Clark | 3059 | 1.32 | Inside |
| O'Shaughnessy's Public House | O'Shaughnessy's Public House | 143619 | 0.41 | Inside |
| Chicago Magic Lounge | Chicago Magic Lounge | 114394 | 1.06 | Inside |
| Rayan's on Clark | Rayan's Wine & Fine Spirits, 4559 N Clark | 14609 | 0.54 | Inside |
| J&B Food and Liquor | J & B Food & Liquors | 2802 | 0.72 | Inside |
| Sky's Beverage Depot | Sky's Beverage Depot | 190808 | 0.95 | Inside |
| Mariano's Lawrence | Mariano's - Lawrence (8515) | 31739 | 0.74 | Inside |
| Whole Foods Market Lakeview | Whole Foods - Lakeview | 9163 | 1.26 | Inside |
| Whole Foods Market Edgewater | Whole Foods - Edgewater | 45401 | 2.32 | Inside |
| Bottles & Cans | Bottles and Cans, 4109 N Lincoln | 14138 | 0.39 | Inside |

Rayan's has a newer duplicate-looking Portal surface at the same Clark Street address. The pilot uses established account `14609`; no account merge or CRM mutation was made.

## Commercial operating rules

### Reorder timing

- Mariano's and Whole Foods: flag at 30 days without reorder.
- On-premise accounts: review between 30 and 45 days.
- Smaller accounts: flag at 45 days.
- Independent liquor stores: warning at 45 days and urgent review at 60 days until Sonat chooses one final threshold.

### Distribution model

- `SATLA` means pass-through distribution.
- Accounts that place orders through KOVAL's self-distribution path are self-distribution accounts.
- Follow-up expectations are the same for both models; fulfillment route must not suppress commercial follow-through.

### Post-sale follow-through

- At end of day, connect new orders to recent OPS account activities. Notify the KOVAL representative who visited the account when an order follows one or two weeks later.
- Produce a next-day order digest for Sonat so she can convert relevant connections into Distribution Chat notifications.
- Seven days after an order, remind the owning representative to check movement and support needs.
- Independents, restaurants, bars, and hotels get relationship follow-up. Chains generally require shelf checks instead of calls.
- Preserve Gene's Sausage Shop as the model for maintenance-led service: visit, inspect shelf condition and out-of-stocks, and help the account manage replenishment.

### Tastings

- A promised tasting recorded in OPS activities is an immediate candidate and routes to Vanessa.
- Trigger proactive tasting outreach after the first SATLA order for Heinen's, Pete's, Caputo's, Fresh Market, Niemann's/County Market, Woodman's, Whole Foods, and Mariano's.
- Binny's tastings remain quarterly planning.
- A tasting recommendation is still approval-gated; the agent does not promise or schedule externally on its own.

### Seasonal support

- MIR, TPR, display support, and chain-push recommendations should be planned for November-December and April-May.
- Outside those windows, surface only evidence-backed exceptions for Sonat's review.

### Product priority

1. KOVAL Bourbon and KOVAL Cranberry Gin, both on- and off-premise.
2. KOVAL Rye and KOVAL Dry Gin.
3. Thresh & Winnow Foret Gin and Citrine Gin.

### Chain behavior

- Store-led: Woodman's; Heinen's after corporate activation.
- Buyer-led smaller chains requiring more mapping: Fresh Thyme, Pete's, County Market/Niemann's, Caputo's, and similar regional groups.
- Corporate-led: Hy-Vee, Mariano's, Target, and Whole Foods.
- Sonat owns high-level corporate outreach, including Costco, Mariano's, and Whole Foods.

### Ownership and approvals

- Infer the working follow-up owner from recent OPS activities tied to the account.
- Keep Sonat informed on sales-team actions and copied where appropriate.
- The agent may calculate, match, monitor, rank, and recommend. It must ask Sonat before pricing, samples, MIR/TPR, distributor communication, external account email, allocation commitments, or any other commercial decision until she explicitly delegates a named decision class.

## Daily action-worthy signals

Rank these signals by urgency, account value, evidence strength, and team capacity; do not create a task for every signal.

1. Yesterday's order follows a rep visit or OPS activity within the prior 14 days: notify that rep and include it in Sonat's order digest.
2. Seven days after order: independent/on-premise movement check or chain shelf-check reminder.
3. Reorder threshold crossed: 30 days for Mariano's/Whole Foods, 30-45 days on-premise, 45-day warning and 60-day urgent for independent liquor.
4. First SATLA order at a tasting-trigger chain: recommend Vanessa tasting follow-up.
5. Promised tasting appears in an OPS activity without a scheduled/completed tasting.
6. Shelf-maintenance account has no recent visit, an out-of-stock note, or an order gap.
7. Priority-product gap: an active account lacks Bourbon or Cranberry Gin; secondarily Rye, Dry Gin, Foret, or Citrine.
8. New order contains only a narrow product set: recommend one evidence-backed adjacent priority SKU for Sonat's approval.
9. Chain order appears at one store but not peer stores: separate store-level execution from corporate/buyer follow-up.
10. Seasonal window opens: surface MIR/TPR/display candidates in April-May and November-December based on slow movement or weak repeat orders.
11. Owner gap: action-worthy account has no recent OPS activity owner or usable buyer/contact route.
12. Data conflict: duplicate account, conflicting distribution model, missing coordinates, missing product lines, or chain relationship ambiguity; route for internal repair before outreach.

## Source map

- OPS activities and provisional account ownership: `https://portal.koval-distillery.com/#/account-touchpoints/my-activities`
- Orders: `https://www.koval-distillery.com/order/review.php?include_approved=1`
- Onboarding: `https://www.koval-distillery.com/order/onboarding-management.php?scope=order`
- Product/order lines: use the order review/order-detail data tied to each order; validate the exact stable detail route during implementation.
- Geography: Portal account billing address plus stored latitude/longitude; calculate straight-line distance for territory membership and defer drive-time routing.
- Chain relationships: use existing Portal account/contact records and the Integrated Super Sales Agent chain guidance ledger; a single canonical chain-parent field is not yet confirmed.

## Focused confirmations still needed

1. Should independent liquor stores become actionable at 45 days, or should 45 days be a warning and 60 days the urgent threshold? The recommended default is 45-day warning / 60-day urgent.
2. For chain relationships, should the first implementation maintain a controlled chain map in the sales ledger, or is there an existing Portal field/report Sonat wants treated as authoritative? The recommended default is a controlled chain map seeded from the existing Portal and Avignon chain guidance.
3. For the daily order digest, confirm whether Sonat wants one consolidated morning email covering the prior day's orders and rep/activity matches. The recommended default is one morning digest, with no external sends or automatic Distribution Chat post.

## Next build slice

Build the read-only daily pilot digest for these 15 accounts using order, product-line, OPS activity, distribution-model, and Portal geography inputs. Score only the highest-value signals, show evidence and recommended owner, and keep all external or commitment-making actions approval-gated.
