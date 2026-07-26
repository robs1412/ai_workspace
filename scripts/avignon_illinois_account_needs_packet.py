#!/usr/local/bin/python3.13
"""Build Sonat's read-only Illinois Account Needs Packet.

The source ledger is the last verified Illinois top-200 export. The packet
applies Sonat's July 22 operating rules without guessing ordering route,
territory ownership, or current post-export activity.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


SOURCE = Path(
    "/Users/werkstatt/salesreport/doc/"
    "avignon-sonat-illinois-top200-account-contact-sheet-2026-06-09.csv"
)
OUT_MD = Path(
    "/Users/werkstatt/ai_workspace/avignon/docs/"
    "integrated-super-sales-agent-illinois-account-needs-2026-07-22.md"
)
OUT_CSV = Path(
    "/Users/werkstatt/ai_workspace/avignon/docs/"
    "integrated-super-sales-agent-illinois-account-needs-2026-07-22.csv"
)
AS_OF = date(2026, 7, 22)

CORPORATE_CHAIN_KEYWORDS = (
    "binny",
    "whole foods",
    "mariano",
    "jewel",
    "target",
    "costco",
    "sam's club",
    "aldi",
    "trader joe",
)
STORE_LED_KEYWORDS = (
    "woodman",
    "heinen",
    "tony",
    "caputo",
    "fresh thyme",
    "pete's",
)
MAIN_PRODUCTS = ("Bourbon", "Cranberry Gin", "Thresh & Winnow", "Rye", "Dry Gin")


def number(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def has_contact(row: dict[str, str]) -> bool:
    return bool(
        row["Primary Contact"].strip()
        and (row["Primary Contact Email"].strip() or row["Primary Contact Phone"].strip())
    )


def account_type(account: str) -> str:
    lowered = account.lower()
    if any(term in lowered for term in STORE_LED_KEYWORDS):
        return "store-led local chain"
    if any(term in lowered for term in CORPORATE_CHAIN_KEYWORDS):
        return "corporate/program chain"
    return "independent/local"


def product_flags(products: str) -> list[str]:
    lowered = products.lower()
    present: list[str] = []
    if "bourbon" in lowered:
        present.append("Bourbon")
    if "cranberry gin" in lowered:
        present.append("Cranberry Gin")
    if "t&w" in lowered or "thresh" in lowered:
        present.append("Thresh & Winnow")
    if "rye" in lowered:
        present.append("Rye")
    if "dry gin" in lowered:
        present.append("Dry Gin")
    if "chrysanthemum" in lowered or "liqueur ginger" in lowered:
        present.append("Priority Liqueur")
    return present


def contact_summary(row: dict[str, str]) -> str:
    if not row["Primary Contact"].strip():
        return "missing"
    values = [row["Primary Contact"].strip()]
    values.extend(
        value.strip()
        for value in (row["Primary Contact Email"], row["Primary Contact Phone"])
        if value.strip()
    )
    return " / ".join(values)


def base_score(row: dict[str, str]) -> float:
    spend = number(row["2026 Purchased"])
    cases = number(row["2026 Cases"])
    invoices = number(row["2026 Invoice Count"])
    latest = iso_date(row["Latest 2026 Invoice"])
    days = (AS_OF - latest).days if latest else 999
    overdue = min(max(days - 21, 0), 90)
    return spend * 0.65 + cases * 55 + invoices * 275 + overdue * 28


def initial_need(row: dict[str, str]) -> str:
    kind = account_type(row["Account"])
    spend = number(row["2026 Purchased"])
    invoices = number(row["2026 Invoice Count"])
    latest = iso_date(row["Latest 2026 Invoice"])
    days = (AS_OF - latest).days if latest else 999
    if kind == "corporate/program chain":
        return "chain/program work"
    if kind == "store-led local chain":
        return "local-chain store-level work"
    if not has_contact(row):
        return "contact cleanup first"
    if spend < 500 and invoices <= 2:
        return "lower-priority watchlist"
    if days >= 30 or invoices >= 3:
        return "reorder/order-taking follow-up"
    return "SKU expansion opportunity"


def next_action(row: dict[str, str], need: str) -> str:
    account = row["Account"]
    latest = iso_date(row["Latest 2026 Invoice"])
    days = (AS_OF - latest).days if latest else 999
    if need == "call today":
        return (
            f"Check live invoices and activities first, then contact {account} on its recorded cadence; "
            "confirm inventory, ordering preference, buyer route, and next reorder date."
        )
    if need == "contact cleanup first":
        return (
            "Send the most recent visiting rep back for buyer name plus phone or email; "
            "if unavailable, assign geographically before outreach."
        )
    if need == "reorder/order-taking follow-up":
        return (
            f"Refresh live cadence and activities; the verified ledger is {days} days past its latest invoice. "
            "Schedule the check-in by the account's stated visit/phone ordering preference."
        )
    if need == "SKU expansion opportunity":
        return (
            "Review live placements and activity context, then prepare a human-reviewed expansion prompt "
            "for missing priority products."
        )
    if need == "local-chain store-level work":
        return (
            "Confirm the location-level buyer and current order status; keep the store high priority until "
            "it is ordering for fall, then monitor cadence and shelf execution."
        )
    if need == "chain/program work":
        return (
            "Keep program decisions with Sonat and Robert. COT may check shelf condition, facings, MIR/POS, "
            "and buyer relationship signals; do not turn this into ordinary rep outreach."
        )
    return "Sprinkle into reactivation work without displacing current high-value ordering accounts."


def recommended_owner(row: dict[str, str], need: str) -> str:
    if need == "chain/program work":
        return "Sonat and Robert"
    if need == "local-chain store-level work":
        return "Prior visiting/order-taking rep; otherwise geographic assignment"
    if need == "contact cleanup first":
        return "Most recent visiting rep; otherwise geographic assignment"
    return "Sales-team territory/relationship assignment pending"


def markdown_cell(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))

    rows: list[dict[str, str]] = []
    for source in source_rows:
        row = dict(source)
        kind = account_type(row["Account"])
        need = initial_need(row)
        score = base_score(row)
        if kind == "store-led local chain":
            score += 5000
        row.update(
            {
                "Account Type": kind,
                "Primary Need": need,
                "Priority Score": f"{score:.2f}",
                "Contact Ready": "yes" if has_contact(row) else "no",
                "Contact Summary": contact_summary(row),
                "Priority Products Present": ", ".join(product_flags(row["2026 Products"])) or "none identified",
                "Priority Products To Review": ", ".join(
                    product for product in MAIN_PRODUCTS if product not in product_flags(row["2026 Products"])
                )
                or "none from verified history",
                "Ordering Route": "live Salesreport/OPS lookup required",
            }
        )
        rows.append(row)

    # Sonat's first lane is local chains. The remaining call-today slots are
    # the strongest contact-ready independents that are already beyond the
    # default 30-day reorder checkpoint in the verified ledger.
    call_candidates = sorted(
        (
            row
            for row in rows
            if row["Primary Need"] == "reorder/order-taking follow-up"
            and row["Contact Ready"] == "yes"
        ),
        key=lambda row: -float(row["Priority Score"]),
    )[:12]
    call_ids = {row["Account ID"] for row in call_candidates}
    for row in rows:
        if row["Account ID"] in call_ids:
            row["Primary Need"] = "call today"
        row["Recommended Owner"] = recommended_owner(row, row["Primary Need"])
        row["Next Action"] = next_action(row, row["Primary Need"])

    lane_order = {
        "local-chain store-level work": 0,
        "call today": 1,
        "contact cleanup first": 2,
        "reorder/order-taking follow-up": 3,
        "service/order-route help": 4,
        "SKU expansion opportunity": 5,
        "chain/program work": 6,
        "lower-priority watchlist": 7,
    }
    rows.sort(key=lambda row: (lane_order[row["Primary Need"]], -float(row["Priority Score"])))

    fields = [
        "Primary Need",
        "Priority Score",
        "Account ID",
        "Account",
        "Category",
        "City",
        "2026 Purchased",
        "2026 Cases",
        "2026 Invoice Count",
        "Latest 2026 Invoice",
        "Account Type",
        "Contact Ready",
        "Contact Summary",
        "Ordering Route",
        "Priority Products Present",
        "Priority Products To Review",
        "Recommended Owner",
        "Next Action",
        "Portal Account URL",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)

    by_lane: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_lane[row["Primary Need"]].append(row)
    counts = Counter(row["Primary Need"] for row in rows)
    total_spend = sum(number(row["2026 Purchased"]) for row in rows)
    missing_contacts = sum(row["Contact Ready"] == "no" for row in rows)

    lines = [
        "# Integrated Super Sales Agent: Illinois Account Needs Packet",
        "",
        "- Built: `2026-07-22`",
        "- Direction: Sonat's answers to the Illinois build questionnaire",
        f"- Verified account source: `{SOURCE}`",
        "- Source invoice window: `2026-01-01` through `2026-05-31`",
        "- Mode: planning/reporting only; read-only analysis",
        "",
        "## Point",
        "",
        "Illinois field time should start with store-led local chains, then current high-value independents that need cadence-based reorder attention. Lapsed accounts belong in the mix, but not at the expense of getting current and historically strong accounts ordering under SATLA/self-distribution. Corporate chains stay in Sonat and Robert's program lane while COT supplies shelf intelligence.",
        "",
        "## Current Packet Readback",
        "",
        f"- Accounts ranked: **{len(rows)}**",
        f"- Verified 2026 purchased value: **${total_spend:,.2f}**",
        f"- Accounts without a verified buyer plus phone/email route: **{missing_contacts}**",
        "- Ordering route, visit cadence, recent activities, barrel timing, and post-May invoices require a live Salesreport/OPS refresh before a rep acts.",
        "",
        "| Primary need | Accounts | Operating meaning |",
        "| --- | ---: | --- |",
    ]
    meanings = {
        "local-chain store-level work": "High priority until ordering for fall; confirm the buyer at each location and monitor orders.",
        "call today": "Strong contact-ready independents beyond the default 30-day checkpoint; validate live cadence before contact.",
        "contact cleanup first": "Historically valuable accounts lacking a buyer plus phone/email route.",
        "reorder/order-taking follow-up": "Refresh cadence and activities, then schedule the preferred visit/phone check-in.",
        "service/order-route help": "Use only after live OPS/Salesreport finds an ordering-route or service problem; none inferred from stale data.",
        "SKU expansion opportunity": "Review live placements and activity context before proposing missing priority products.",
        "chain/program work": "Sonat/Robert program lane; COT shelf checks remain useful field intelligence.",
        "lower-priority watchlist": "Light reactivation seasoning; do not displace active high-value account work.",
    }
    for lane in lane_order:
        lines.append(f"| {lane} | {counts.get(lane, 0)} | {meanings[lane]} |")

    lines.extend(
        [
            "",
            "## Sonat's Rules Applied",
            "",
            "1. Store-led local chains come first and remain high priority until they are ordering for fall.",
            "2. High-value independent retail and on-premise accounts follow, especially where ordering slowed after the SATLA/self-distribution change.",
            "3. Reorder timing starts at 30 days, tightens to 21 days for high-volume accounts, and should ultimately follow each account's observed order cadence plus activity notes.",
            "4. Missing-contact work requires a named buyer (owner, beverage director, manager, or equivalent) plus phone or email.",
            "5. Main product priorities are Bourbon, Cranberry Gin, Thresh & Winnow, Rye, and Dry Gin; Chrysanthemum Honey and Ginger follow. Gift packs wait until fall and other seasonal pushes wait until September.",
            "6. Binny's is handled through Brett Pantoni/SATLA or Sonat and Robert. Whole Foods buying is corporate; COT tasting staff should still report shelf condition, facings, POS, MIRs, and buyer signals.",
            "7. Corporate/program chains remain Sonat and Robert's lane. Robert is consulted on pass-through support questions.",
            "8. The next build remains planning/reporting only. No external outreach or CRM/Portal/OPS writes are authorized by this packet.",
            "",
        ]
    )

    def add_table(title: str, lane: str, limit: int) -> None:
        lines.extend(
            [
                f"## {title}",
                "",
                "| Rank | Account | City | 2026 purchased | Latest invoice | Contact | Products to review | Next action |",
                "| ---: | --- | --- | ---: | --- | --- | --- | --- |",
            ]
        )
        for index, row in enumerate(by_lane.get(lane, [])[:limit], 1):
            lines.append(
                "| {index} | [{account}]({url}) | {city} | ${spend:,.2f} | {latest} | {contact} | {products} | {action} |".format(
                    index=index,
                    account=markdown_cell(row["Account"]),
                    url=row["Portal Account URL"],
                    city=markdown_cell(row["City"]),
                    spend=number(row["2026 Purchased"]),
                    latest=row["Latest 2026 Invoice"],
                    contact=markdown_cell(row["Contact Summary"]),
                    products=markdown_cell(row["Priority Products To Review"]),
                    action=markdown_cell(row["Next Action"]),
                )
            )
        lines.append("")

    add_table("1. Local-Chain Store-Level Work", "local-chain store-level work", 20)
    add_table("2. Call Today After Live Refresh", "call today", 12)
    add_table("3. Contact Cleanup First", "contact cleanup first", 20)
    add_table("4. Reorder / Order-Taking Follow-Up", "reorder/order-taking follow-up", 20)
    add_table("5. SKU Expansion Review", "SKU expansion opportunity", 15)
    add_table("6. Chain / Program Work", "chain/program work", 20)
    add_table("7. Lower-Priority Watchlist", "lower-priority watchlist", 15)

    lines.extend(
        [
            "## Live Refresh Checklist Before Assignment",
            "",
            "For each account selected from this packet, the Integrated Super Sales Agent should read the current Sales Analytics, Hitlist Optimization, Whitespace Lift, Chain Store Intelligence, barrel review, OPS activity, and applicable DIST/SATLA order route. It should then replace the provisional next action with the account's actual cadence, current ordering method, last team interaction, seasonal context, barrel need, and territory/relationship owner.",
            "",
            "No account should be labeled `unclear route` without first checking DIST and SATLA. If those sources still disagree, ask one concrete route question rather than guessing.",
            "",
            "## Outcome Loop",
            "",
            "Use: reached; not reached; buyer/contact confirmed; reorder placed; no reorder needed; wants follow-up; wants samples; pricing/distributor issue; ordering-route confusion; product availability question; follow-up date; next owner.",
            "",
            "For this packet, **next owner** means the named person responsible for the next dated action after the current touch. This should become a controlled activity field or documented standard after Sonat and Robert confirm the workflow; no Portal field change is included here.",
            "",
            "## What Was Not Done",
            "",
            "- No CRM, Portal, OPS, DIST, SATLA, pricing, sample, allocation, account-commitment, or external-account mutation.",
            "- No territory owner was guessed where relationship/geography assignment is not yet settled.",
            "- No ordering route was guessed from account name or category.",
            "- No post-May invoice/activity claim was made because the live report requires authenticated readback.",
            "",
            "## Remaining Decisions",
            "",
            "1. Confirm whether `next owner` should mean the person accountable for the next dated action; recommended default: yes.",
            "2. Decide with Robert whether the outcome terms should be a controlled Portal activity dropdown, a documented required vocabulary, or both.",
            "3. Run the authenticated live refresh and settle territory/relationship ownership before issuing rep assignments.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_CSV}")
    print("counts " + ", ".join(f"{key}={counts.get(key, 0)}" for key in lane_order))


if __name__ == "__main__":
    main()
