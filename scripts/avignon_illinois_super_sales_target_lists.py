#!/usr/local/bin/python3.13
"""Build Illinois target lists for the Integrated Super Sales Agent."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path("/Users/werkstatt/ai_workspace")
SOURCE = Path("/Users/werkstatt/salesreport/doc/avignon-sonat-illinois-top200-account-contact-sheet-2026-06-09.csv")
OUT_MD = ROOT / "avignon/docs/integrated-super-sales-agent-illinois-target-lists-2026-07-05.md"
OUT_CSV = ROOT / "avignon/docs/integrated-super-sales-agent-illinois-target-lists-2026-07-05.csv"

TODAY = date(2026, 7, 5)

CHAIN_KEYWORDS = (
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
    "tony",
    "caputo",
    "fresh thyme",
    "pete's",
    "heinen",
)


def money(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def has_contact(row: dict[str, str]) -> bool:
    return bool(row["Primary Contact"].strip() and (row["Primary Contact Email"].strip() or row["Primary Contact Phone"].strip()))


def chain_type(account: str) -> str:
    account_l = account.lower()
    if any(k in account_l for k in STORE_LED_KEYWORDS):
        return "store-led local chain"
    if any(k in account_l for k in CHAIN_KEYWORDS):
        return "chain/program"
    return "independent/local"


def product_family(products: str) -> str:
    p = products.lower()
    flags = []
    if "bourbon" in p:
        flags.append("bourbon")
    if "rye" in p:
        flags.append("rye")
    if "dry gin" in p or "gin" in p:
        flags.append("gin")
    if "cranberry" in p or "spritz" in p or "rtd" in p:
        flags.append("cran/RTD")
    if "vodka" in p:
        flags.append("vodka")
    return ", ".join(flags[:5]) if flags else "review product set"


def reorder_score(row: dict[str, str]) -> float:
    latest = parse_date(row["Latest 2026 Invoice"])
    days = (TODAY - latest).days if latest else 999
    spend = money(row["2026 Purchased"])
    invoices = money(row["2026 Invoice Count"])
    cases = money(row["2026 Cases"])
    recency_weight = 1.0 if days >= 35 else 0.45 if days >= 21 else 0.15
    return spend * 0.55 + cases * 70 + invoices * 250 + recency_weight * 2500


def lane_for(row: dict[str, str]) -> tuple[str, str]:
    ctype = chain_type(row["Account"])
    contact = has_contact(row)
    latest = parse_date(row["Latest 2026 Invoice"])
    days = (TODAY - latest).days if latest else 999
    spend = money(row["2026 Purchased"])
    invoices = money(row["2026 Invoice Count"])

    if ctype == "chain/program":
        return "chain-program planning", "Confirm buyer/program route, authorized SKUs, distributor/pass-through support, and store-level execution limits."
    if ctype == "store-led local chain":
        return "store-led local chain", "Treat as local/store-led: verify buyer per location, then prepare reorder/order-taking prompt for the store."
    if not contact:
        return "contact cleanup", "Find or verify buyer/order contact before outreach; this account cannot be worked reliably without a route."
    if days >= 35 or (spend >= 2000 and invoices >= 3):
        return "reorder/order-taking", "Sales team should verify current inventory, ask for reorder timing, and capture any customer-service or order-taking need."
    return "watchlist", "Keep in Illinois account ledger; revisit after the next invoice/activity refresh."


def contact_summary(row: dict[str, str]) -> str:
    name = row["Primary Contact"].strip()
    email = row["Primary Contact Email"].strip()
    phone = row["Primary Contact Phone"].strip()
    if not name:
        return "missing"
    parts = [name]
    if email:
        parts.append(email)
    if phone:
        parts.append(phone)
    return " / ".join(parts)


def main() -> None:
    with SOURCE.open(newline="") as f:
        rows = list(csv.DictReader(f))

    enriched: list[dict[str, str]] = []
    for row in rows:
        lane, next_action = lane_for(row)
        row = dict(row)
        row["Lane"] = lane
        row["Chain Type"] = chain_type(row["Account"])
        row["Contact Route"] = "yes" if has_contact(row) else "no"
        row["Contact Summary"] = contact_summary(row)
        row["Product Family"] = product_family(row["2026 Products"])
        row["Next Sales Action"] = next_action
        row["Priority Score"] = f"{reorder_score(row):.2f}"
        enriched.append(row)

    enriched.sort(key=lambda r: (r["Lane"] != "reorder/order-taking", -float(r["Priority Score"])))

    fields = [
        "Lane",
        "Rank",
        "Account ID",
        "Account",
        "Category",
        "City",
        "2026 Purchased",
        "2026 Cases",
        "2026 Invoice Count",
        "Latest 2026 Invoice",
        "Chain Type",
        "Contact Route",
        "Contact Summary",
        "Product Family",
        "Next Sales Action",
        "Portal Account URL",
    ]
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in enriched:
            writer.writerow({field: row.get(field, "") for field in fields})

    by_lane: dict[str, list[dict[str, str]]] = {}
    for row in enriched:
        by_lane.setdefault(row["Lane"], []).append(row)

    lines = [
        "# Integrated Super Sales Agent Illinois Target Lists",
        "",
        "- Generated: `2026-07-05`",
        f"- Source CSV: `{SOURCE}`",
        "- Mode: read-only target-list generation",
        "- Mutations: none; no CRM, Portal, OPS, pricing, sample, allocation, account-commitment, or external-send mutation",
        "",
        "## Operating Focus",
        "",
        "Illinois is the priority market for the next Integrated Super Sales Agent slice. Because KOVAL is now operating with part local self-distribution and part pass-through distribution, the sales team needs target lists that are practical for human follow-through: who likely needs a reorder, who lacks a usable buyer/order contact, who needs customer-service/order-taking attention, and which chains require buyer/program handling instead of normal store outreach.",
        "",
        "## Summary",
        "",
        "| Lane | Count | Purpose |",
        "| --- | ---: | --- |",
    ]
    purposes = {
        "reorder/order-taking": "Contact-ready independent/local accounts where the sales team can verify inventory, reorder timing, and service needs.",
        "contact cleanup": "Valuable accounts that cannot be worked reliably until buyer/order-contact data is found or verified.",
        "store-led local chain": "Local chains that need store-level buyer/contact handling and location-specific prompts.",
        "chain-program planning": "Corporate or program-led chains that need buyer/program route, distributor/pass-through support, and SKU authorization context.",
        "watchlist": "Lower-immediacy accounts to keep in the Illinois ledger for the next refresh.",
    }
    for lane in ["reorder/order-taking", "contact cleanup", "store-led local chain", "chain-program planning", "watchlist"]:
        lines.append(f"| {lane} | {len(by_lane.get(lane, []))} | {purposes[lane]} |")

    def table(title: str, lane: str, limit: int) -> None:
        lines.extend(["", f"## {title}", "", "| Priority | Account | City | 2026 Purchased | Latest Invoice | Contact | Product Set | Next Action |", "| ---: | --- | --- | ---: | --- | --- | --- | --- |"])
        for idx, row in enumerate(by_lane.get(lane, [])[:limit], 1):
            lines.append(
                "| {idx} | {account} | {city} | ${purchased} | {latest} | {contact} | {products} | {action} |".format(
                    idx=idx,
                    account=row["Account"].replace("|", "/"),
                    city=row["City"].replace("|", "/"),
                    purchased=f"{money(row['2026 Purchased']):,.2f}",
                    latest=row["Latest 2026 Invoice"],
                    contact=row["Contact Summary"].replace("|", "/"),
                    products=row["Product Family"].replace("|", "/"),
                    action=row["Next Sales Action"].replace("|", "/"),
                )
            )

    table("Contact-Ready Reorder / Order-Taking Targets", "reorder/order-taking", 25)
    table("Contact Cleanup Targets", "contact cleanup", 25)
    table("Store-Led Local Chain Targets", "store-led local chain", 20)
    table("Chain / Program Planning Targets", "chain-program planning", 25)

    lines.extend([
        "",
        "## Sales-Team Use",
        "",
        "1. Start with the contact-ready reorder/order-taking lane and turn each row into a human sales prompt: verify current inventory, ask for reorder timing, confirm who places orders, and capture service problems.",
        "2. Run contact cleanup in parallel for the highest-value accounts with no usable buyer/order route.",
        "3. Treat store-led local chains as location-level work, not broad corporate outreach, unless Sonat supplies a buyer/program route.",
        "4. Keep corporate/program chains separate so the team does not waste store calls where SKU authorization or distributor support is the real gate.",
        "",
        "## Approval Gates",
        "",
        "This packet does not authorize external buyer outreach, pricing, sample promises, allocation commitments, account commitments, distributor-sensitive commitments, or CRM/Portal/OPS mutations. It is a target-list and sales-prep artifact for Sonat/sales-team review.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
