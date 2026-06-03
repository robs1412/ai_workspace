#!/usr/bin/env python3
import csv
import html
import re
import subprocess
from pathlib import Path


ROOT = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC")
DOCX = ROOT / "5-17-26 DRAFT Response L&L Request For Documents.docx"
PRODUCTION = ROOT / "discovery-production-one-folder"
PRODUCTION_INDEX = ROOT / "discovery-production-one-folder-index.csv"
HTML_OUT = ROOT / "discovery-response-request-suggestion.html"
CSV_OUT = ROOT / "discovery-response-request-suggestion.csv"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".bmp"}


def load_renumber_map() -> dict[str, str]:
    manifests = sorted(ROOT.glob("discovery-production-renumber-after-duplicate-removal-*.csv"))
    manifests += sorted((ROOT / "_backup").glob("discovery-production-renumber-after-duplicate-removal-*.csv"))
    if not manifests:
        return {}
    latest = manifests[-1]
    with latest.open(newline="", encoding="utf-8") as f:
        return {row["Old K #"]: row["New K #"] for row in csv.DictReader(f)}


def docx_text() -> str:
    result = subprocess.run(
        ["textutil", "-convert", "txt", "-stdout", str(DOCX)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.replace("\xa0", " ")


def parse_requests(text: str) -> dict[int, dict[str, str]]:
    section = text.split("REQUESTS FOR PRODUCTION", 1)[1]
    starts = list(re.finditer(r"(?m)^\s*(\d+)\.\s+", section))
    parsed: dict[int, dict[str, str]] = {}
    for i, match in enumerate(starts):
        number = int(match.group(1))
        end = starts[i + 1].start() if i + 1 < len(starts) else len(section)
        block = section[match.end() : end].strip()
        if "RESPONSE:" in block:
            request, response = block.split("RESPONSE:", 1)
        else:
            request, response = block, ""
        parsed[number] = {
            "request": clean_space(request),
            "response": clean_space(response),
        }
    return parsed


def clean_space(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def k_int(k: str) -> int:
    return int(k.split("_", 1)[1])


def k_label(n: int) -> str:
    return f"K_{n:03d}"


def expand(spec: str) -> list[str]:
    values: list[str] = []
    for part in re.split(r"[, ]+", spec.strip()):
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            for n in range(int(start), int(end) + 1):
                values.append(k_label(n))
        else:
            values.append(k_label(int(part)))
    return values


def load_rows() -> dict[str, dict[str, str]]:
    with PRODUCTION_INDEX.open(newline="", encoding="utf-8") as f:
        return {row["K #"]: row for row in csv.DictReader(f)}


def is_image(row: dict[str, str]) -> bool:
    return Path(row["File"]).suffix.lower() in IMAGE_EXTS


def existing(
    rows: dict[str, dict[str, str]],
    spec: str,
    *,
    include_images: bool = False,
    renumber: dict[str, str] | None = None,
) -> list[str]:
    renumber = renumber or {}
    out = []
    seen = set()
    for k in expand(spec):
        if renumber:
            if k not in renumber:
                continue
            k = renumber[k]
        row = rows.get(k)
        if not row or k in seen:
            continue
        if not include_images and is_image(row):
            continue
        out.append(k)
        seen.add(k)
    return out


def unique_sorted(groups: list[list[str]]) -> list[str]:
    seen = set()
    out = []
    for group in groups:
        for k in group:
            if k not in seen:
                seen.add(k)
                out.append(k)
    return sorted(out, key=k_int)


def join_ks(ks: list[str]) -> str:
    return ", ".join(ks) if ks else "None listed"


def linked_k_cell(rows: dict[str, dict[str, str]], ks: list[str]) -> str:
    if not ks:
        return "None listed"
    links = []
    for k in ks:
        row = rows[k]
        href = (PRODUCTION / row["File"]).as_uri()
        links.append(f'<a href="{html.escape(href)}">{html.escape(k)}</a>')
    return ", ".join(links)


def main() -> None:
    rows = load_rows()
    requests = parse_requests(docx_text())
    renumber = load_renumber_map()

    claim_941x = existing(rows, "004-006,016,272-276", renumber=renumber)
    transcripts = existing(rows, "507-510", renumber=renumber)
    form_941_returns = existing(rows, "001-003,015,179-184", renumber=renumber)
    employee_spreadsheets = existing(rows, "020,082,101", renumber=renumber)
    eoy_financial_attachments = existing(rows, "080-081,084,099-100,103", renumber=renumber)
    leyton_core = existing(rows, "018-024,053,082-083,101-102,134", renumber=renumber)
    leyton_early_emails = existing(rows, "022-036,042-043,054,060,066-070,078,113,116,119,122,125", renumber=renumber)
    leyton_question_emails = existing(
        rows,
        "152-153,156,158,163,171-178,185-200,211-213,234-235,242,249-250,254,280,286,292,313,338,363,389,398,407,411,432",
        renumber=renumber,
    )
    ll_tax_communications = existing(rows, "008,010,012,079,085-098,104-112,115,130-132,135,137-151,194-210,214-232", renumber=renumber)
    irs_resubmission = existing(rows, "443-482", renumber=renumber)
    malpractice_claim = existing(rows, "483-506", renumber=renumber)
    damages = existing(rows, "475-490,506", renumber=renumber)
    breach_core = unique_sorted([claim_941x, transcripts, leyton_core, leyton_question_emails, ll_tax_communications, eoy_financial_attachments, irs_resubmission, malpractice_claim])
    ll_communications = unique_sorted([ll_tax_communications, eoy_financial_attachments, irs_resubmission, malpractice_claim])
    leyton_all = unique_sorted([leyton_core, leyton_early_emails, leyton_question_emails, claim_941x, form_941_returns, employee_spreadsheets, eoy_financial_attachments])

    mappings = {
        1: (unique_sorted([claim_941x, transcripts]), "Draft response says only the 2020 Q1, 2020 Q2, 2020 Q4, and 2021 Q1 Form 941-X documents will be produced, with corresponding IRS transcript information."),
        2: (breach_core, "Broad support set for the Complaint allegations: ERTC claim documents, Leyton materials, L&L communications, IRS resubmission/denial materials, demand/claim materials, and transcripts."),
        3: (damages, "Damage-related production: interest/principal calculations and IRS disallowance/denial letters."),
        4: ([], "Draft response objects as premature; no production set listed."),
        5: ([], "Draft response states none."),
        6: (unique_sorted([form_941_returns, employee_spreadsheets, eoy_financial_attachments]), "Draft response identifies Forms 941, EOY financial materials, and spreadsheets identifying Koval employees by quarter."),
        7: (unique_sorted([leyton_core, leyton_early_emails, leyton_question_emails]), "Draft response identifies Leyton ERTC study materials and emails from/to Leyton regarding ERTC."),
        8: ([], "Draft response states there is no express contract, agreement, or engagement letter with Defendant."),
        9: (leyton_all, "Leyton ERC claim production, including Leyton emails, ERTC study/questionnaire/breakdown materials, engagement/LOE, and related Forms 941/941-X materials sent in the Leyton thread."),
        10: (unique_sorted([claim_941x, transcripts]), "Draft response limits payroll tax return production to 2020 Q1, 2020 Q2, 2020 Q4, and 2021 Q1 Form 941-X documents and IRS transcripts."),
        11: (breach_core, "Documents relating to discovery of the alleged wrongful acts: Leyton follow-up, L&L ERTC/tax communications, IRS resubmission and denial materials, and demand/claim communications."),
        12: (ll_communications, "Documents provided to Defendant or communications with Defendant relating to the ERTC services and claim."),
        13: (ll_communications, "Draft response says this duplicates request 12; same K numbers are listed for review."),
        14: (breach_core, "Documents supporting the duty-of-care breach theory: Form 941-X/transcript materials, Leyton/L&L ERTC communications, IRS denial/resubmission records, and demand/claim records."),
        15: (ll_communications, "Communications between Defendant and anyone acting on behalf of Plaintiff, limited here to ERTC-related L&L/Stef/Stuart communications in the production folder."),
        16: ([], "Draft response says none as of yet and references pleadings not present in this production folder."),
        17: (unique_sorted([irs_resubmission, transcripts, damages]), "IRS/taxing-authority materials relating to ERTC refunds, including resubmission, POA, denial/disallowance letters, damages calculation, and transcripts."),
    }

    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Request No.", "Request", "Draft Response", "Documents Produced / K Numbers", "Mapping Note"])
        for number in range(1, 18):
            ks, note = mappings[number]
            writer.writerow([
                number,
                requests.get(number, {}).get("request", ""),
                requests.get(number, {}).get("response", ""),
                join_ks(ks),
                note,
            ])

    css = """
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;margin:24px;color:#111}
h1{font-size:22px;margin:0 0 8px}.meta{font-size:13px;color:#555;line-height:1.4;margin:0 0 18px}
table{border-collapse:collapse;width:100%;font-size:12px;line-height:1.35}
th{position:sticky;top:0;background:#f3f5f7;border:1px solid #d8dde3;padding:6px;text-align:left}
td{border:1px solid #e1e4e8;padding:6px;vertical-align:top}tr:nth-child(even){background:#fbfbfc}
.num{white-space:nowrap;text-align:right}.ks{min-width:210px}.request,.response{min-width:260px}.note{min-width:240px}
a{color:#0645ad;text-decoration:none}a:hover{text-decoration:underline}
"""
    html_rows = []
    for number in range(1, 18):
        ks, note = mappings[number]
        req = requests.get(number, {}).get("request", "")
        resp = requests.get(number, {}).get("response", "")
        html_rows.append(
            "<tr>"
            f'<td class="num">{number}</td>'
            f'<td class="request">{html.escape(req)}</td>'
            f'<td class="response">{html.escape(resp)}</td>'
            f'<td class="ks">{linked_k_cell(rows, ks)}</td>'
            f'<td class="note">{html.escape(note)}</td>'
            "</tr>"
        )

    doc = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Discovery Response Request Crosswalk</title><style>{css}</style></head>
<body>
<h1>Discovery Response Request Crosswalk</h1>
<p class="meta">Draft source: <code>{html.escape(str(DOCX))}</code><br>
Production index: <code>{html.escape(str(PRODUCTION_INDEX))}</code><br>
This is a draft working crosswalk from each request/response to K-numbered production files. Broad ranges exclude image attachments/signature graphics unless specifically selected.</p>
<table>
<thead><tr><th>No.</th><th>Request</th><th>Draft Response</th><th>Documents Produced / K Numbers</th><th>Mapping Note</th></tr></thead>
<tbody>
{chr(10).join(html_rows)}
</tbody>
</table>
</body></html>
"""
    HTML_OUT.write_text(doc, encoding="utf-8")

    print(f"HTML={HTML_OUT}")
    print(f"CSV={CSV_OUT}")
    for number in range(1, 18):
        ks, _ = mappings[number]
        print(f"RFP {number}: {len(ks)} K numbers")


if __name__ == "__main__":
    main()
