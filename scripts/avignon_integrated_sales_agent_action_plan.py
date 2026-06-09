#!/usr/local/bin/python3.13
"""Build a read-only Integrated Super Sales Agent action plan from top-200 CSV."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = Path(
    "/Users/werkstatt/salesreport/doc/"
    "avignon-sonat-illinois-top200-account-contact-sheet-2026-06-09.csv"
)
OUT_MD = ROOT / "avignon/docs/integrated-super-sales-agent-top50-action-plan-2026-06-09.md"
OUT_CSV = ROOT / "avignon/docs/integrated-super-sales-agent-top50-action-plan-2026-06-09.csv"


CHAIN_PATTERNS = {
    "costco": "Costco",
    "whole foods": "Whole Foods Market",
    "target": "Target",
    "trader joe": "Trader Joe's",
    "binny's": "Binny's",
    "binnys": "Binny's",
    "mariano": "Mariano's",
    "jewel": "Jewel-Osco",
    "aldi": "ALDI",
    "walmart": "Walmart",
    "wal-mart": "Walmart",
    "total wine": "Total Wine",
    "sam's club": "Sam's Club",
    "sams club": "Sam's Club",
}


@dataclass(frozen=True)
class Account:
    rank: int
    account_id: str
    account: str
    category: str
    city: str
    state: str
    purchased: float
    cases: float
    invoice_count: int
    latest_invoice: str
    products: str
    primary_contact: str
    contact_title: str
    contact_email: str
    contact_phone: str
    portal_url: str
    chain_program: str

    @property
    def has_contact(self) -> bool:
        return bool(self.primary_contact or self.contact_email or self.contact_phone)

    @property
    def has_contact_route(self) -> bool:
        return bool(self.contact_email or self.contact_phone)

    @property
    def is_chain(self) -> bool:
        return bool(self.chain_program)


def money(value: float) -> str:
    return f"${value:,.2f}"


def cell(value: object) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip()


def chain_program_name(account: str) -> str:
    normalized = account.lower()
    for needle, label in CHAIN_PATTERNS.items():
        if needle in normalized:
            return label
    return ""


def strategic_tier(account: Account) -> str:
    if account.purchased >= 7500:
        return "A"
    if account.purchased >= 3500:
        return "B"
    return "C"


def product_gap(products: str) -> str:
    core = ["Bourbon", "Rye", "Dry Gin", "Vodka", "Cranberry"]
    missing = [name for name in core if name.lower() not in products.lower()]
    return ", ".join(missing[:3]) if missing else "none obvious from 2026 products"


def pitch(account: Account) -> str:
    products = account.products.lower()
    is_retail = "retail" in account.category.lower()
    if "dry gin" not in products or "cranberry" not in products:
        return (
            "Retail gin set: KOVAL Dry Gin plus Cranberry Gin Liqueur."
            if is_retail
            else "Cocktail gin story: KOVAL Dry Gin plus Cranberry Gin Liqueur."
        )
    if "bourbon" not in products or "rye" not in products:
        return "Core whiskey repair: Bourbon and Rye as the simplest set repair."
    if "t&w" not in products and "thresh" not in products:
        return "Premium story basket: qualify for Thresh & Winnow after core set is stable."
    return "Portfolio reinforcement: protect the current set and ask for one incremental placement."


def next_action(account: Account) -> str:
    if account.is_chain:
        if account.chain_program == "Binny's":
            return "Confirm buyer-level versus store-level treatment before rep outreach."
        return "Route as chain/program review: confirm authorized SKUs, buyer owner, and distributor support."
    if not account.has_contact:
        return "Research and add a buyer/contact before field follow-up planning."
    if not account.has_contact_route:
        return "Verify usable email or phone for the named contact before outreach."
    return "Prepare rep touch using 2026 purchases, current products, and one SKU/story ask."


def briefing(account: Account) -> dict[str, str]:
    gap = product_gap(account.products)
    why = (
        f"{money(account.purchased)} / {account.cases:,.2f} cases in 2026 through "
        f"{account.latest_invoice}; tier {strategic_tier(account)} account."
    )
    evidence = (
        f"{account.invoice_count} 2026 invoices; current products include "
        f"{account.products[:220]}{'...' if len(account.products) > 220 else ''}"
    )
    ask = (
        "Verify current placement, confirm reorder timing, and ask for one specific SKU/story expansion."
    )
    crm_note = (
        "Logged Integrated Super Sales Agent field review: verified current placement, "
        "buyer/contact status, pitch, outcome, and next follow-up date."
    )
    return {
        "why_now": why,
        "evidence": evidence,
        "ask": ask,
        "sku_gap": gap,
        "pitch": pitch(account),
        "crm_note": crm_note,
    }


def load_accounts(path: Path) -> list[Account]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        accounts = []
        for row in reader:
            account = row["Account"].strip()
            accounts.append(
                Account(
                    rank=int(row["Rank"]),
                    account_id=row["Account ID"].strip(),
                    account=account,
                    category=row["Category"].strip(),
                    city=row["City"].strip(),
                    state=row["State"].strip(),
                    purchased=float(row["2026 Purchased"] or 0),
                    cases=float(row["2026 Cases"] or 0),
                    invoice_count=int(row["2026 Invoice Count"] or 0),
                    latest_invoice=row["Latest 2026 Invoice"].strip(),
                    products=row["2026 Products"].strip(),
                    primary_contact=row["Primary Contact"].strip(),
                    contact_title=row["Primary Contact Title"].strip(),
                    contact_email=row["Primary Contact Email"].strip(),
                    contact_phone=row["Primary Contact Phone"].strip(),
                    portal_url=row["Portal Account URL"].strip(),
                    chain_program=chain_program_name(account),
                )
            )
    return accounts


def write_csv(rows: list[Account]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "action_rank",
                "source_rank",
                "lane",
                "account_id",
                "account",
                "category",
                "city",
                "purchased_2026",
                "cases_2026",
                "tier",
                "chain_program",
                "primary_contact",
                "contact_email",
                "contact_phone",
                "next_action",
                "portal_url",
            ]
        )
        for idx, account in enumerate(rows, start=1):
            lane = "chain_program" if account.is_chain else "rep_ready" if account.has_contact_route else "contact_cleanup"
            writer.writerow(
                [
                    idx,
                    account.rank,
                    lane,
                    account.account_id,
                    account.account,
                    account.category,
                    account.city,
                    f"{account.purchased:.2f}",
                    f"{account.cases:.2f}",
                    strategic_tier(account),
                    account.chain_program,
                    account.primary_contact,
                    account.contact_email,
                    account.contact_phone,
                    next_action(account),
                    account.portal_url,
                ]
            )


def md_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return lines


def write_markdown(accounts: list[Account]) -> None:
    top50 = accounts[:50]
    rep_ready = [account for account in top50 if not account.is_chain and account.has_contact_route]
    contact_cleanup = [account for account in top50 if not account.is_chain and not account.has_contact_route]
    chain = [account for account in top50 if account.is_chain]
    briefing_accounts = rep_ready[:10]
    cleanup_targets = sorted(
        [account for account in accounts if not account.is_chain and not account.has_contact_route],
        key=lambda item: item.purchased,
        reverse=True,
    )[:25]

    lines = [
        "# Integrated Super Sales Agent Top-50 Action Plan",
        "",
        "- Generated: `2026-06-09`",
        f"- Source CSV: `{SOURCE_CSV}`",
        "- Source request: Sonat direct-owner `Account list` request, Message-ID `<CALbLtzzN6cRfQccuB_1xaKvTSnbVAATtMsqORPX2xZJyY=hRPQ@mail.gmail.com>`",
        "- Mode: read-only analysis/reporting",
        "- Mutations: none; no CRM, Portal, OPS, saved-report, auth/OAuth, pricing, sample, allocation, account-commitment, or external-send mutation",
        "",
        "## Summary",
        "",
    ]
    lines += md_table(
        ["Metric", "Value"],
        [
            ["Top-50 accounts reviewed", len(top50)],
            ["Rep-ready non-chain accounts with email/phone", len(rep_ready)],
            ["Non-chain accounts needing contact cleanup", len(contact_cleanup)],
            ["Chain/program accounts", len(chain)],
            ["Initial field briefings generated", len(briefing_accounts)],
            ["Contact-cleanup targets generated", len(cleanup_targets)],
        ],
    )
    lines += [
        "",
        "## Operating Split",
        "",
        "Use this as the next supervised Phase I operating split. The top-200 sheet is the current account ledger for Illinois 2026 purchases; this artifact narrows it into immediate action lanes without sending emails or changing CRM.",
        "",
        "## Top-50 Action Lanes",
        "",
    ]
    lines += md_table(
        [
            "Action Rank",
            "Source Rank",
            "Lane",
            "Account",
            "City",
            "2026 Purchased",
            "Tier",
            "Contact",
            "Next Action",
        ],
        [
            [
                idx,
                account.rank,
                "chain/program" if account.is_chain else "rep-ready" if account.has_contact_route else "contact-cleanup",
                account.account,
                account.city,
                money(account.purchased),
                strategic_tier(account),
                account.primary_contact or account.contact_email or account.contact_phone or "none found",
                next_action(account),
            ]
            for idx, account in enumerate(top50, start=1)
        ],
    )
    lines += ["", "## Initial Rep-Ready Field Briefings", ""]
    for idx, account in enumerate(briefing_accounts, start=1):
        data = briefing(account)
        contact_bits = [account.primary_contact, account.contact_title, account.contact_email, account.contact_phone]
        contact = " / ".join([bit for bit in contact_bits if bit]) or "contact route needs verification"
        lines += [
            f"### {idx}. {account.account}",
            "",
            f"- Account ID: `{account.account_id}`",
            f"- Category/location: {account.category or 'uncategorized'} / {account.city}, {account.state}",
            f"- Contact: {contact}",
            f"- Why now: {data['why_now']}",
            f"- Evidence: {data['evidence']}",
            f"- SKU gap: {data['sku_gap']}",
            f"- Suggested pitch: {data['pitch']}",
            f"- Next ask: {data['ask']}",
            f"- CRM note to log after call: {data['crm_note']}",
            "",
        ]
    lines += [
        "## Contact-Cleanup Targets",
        "",
        "These are high-value non-chain accounts from the top-200 sheet that lack a usable CRM email or phone route. They should be researched or cleaned before external account follow-up is planned.",
        "",
    ]
    lines += md_table(
        ["Priority", "Source Rank", "Account", "City", "2026 Purchased", "Cases", "Portal"],
        [
            [
                idx,
                account.rank,
                account.account,
                account.city,
                money(account.purchased),
                f"{account.cases:,.2f}",
                account.portal_url,
            ]
            for idx, account in enumerate(cleanup_targets, start=1)
        ],
    )
    lines += [
        "",
        "## Chain / Program Lane",
        "",
        "These accounts stay visible but should not be treated as normal store-level rep tasks until Sonat confirms buyer-level versus store-level handling and distributor support.",
        "",
    ]
    lines += md_table(
        ["Source Rank", "Program", "Account", "City", "2026 Purchased", "Next Action"],
        [
            [account.rank, account.chain_program, account.account, account.city, money(account.purchased), next_action(account)]
            for account in chain
        ],
    )
    lines += [
        "",
        "## Recommended Next Build Slice",
        "",
        "Turn the available initial field briefings into the first rep-review packet and run a contact-cleanup pass for the 25 highest-value non-chain accounts without usable contact routes. Keep both lanes review-only until Sonat approves CRM updates or external sends.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(SOURCE_CSV)
    accounts = load_accounts(SOURCE_CSV)
    if not accounts:
        raise RuntimeError("No accounts loaded from source CSV.")
    write_csv(accounts[:50])
    write_markdown(accounts)
    print(f"markdown={OUT_MD}")
    print(f"csv={OUT_CSV}")
    print(f"generated_at={datetime.now().isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
