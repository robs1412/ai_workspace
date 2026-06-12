#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


BLANK = Path("tmp/utah-sond/2026_Product_Listing_Application_blank.pdf")
OUT_DIR = Path("tmp/utah-sond/filled")


COMMON = {
    "Text1": "KOVAL Distillery",
    "Dropdown1": "1 - General",
    "Dropdown5": "Whiskey",
    "Text7": "KOVAL Distillery",
    "Dropdown8": "No",
    "Dropdown9": "No",
    "Text23": "United States",
    "Dropdown32": "Freight Added",
    "Text34": "Chicago, IL",
    "Text35": "Chicago, IL",
    "Dropdown40": "Hold retail price (FOB cost will be adjusted to achieve the target retail)",
    "Dropdown41": "Bailment",
    "Text45": "No current Utah DABS listing/history found in the June 2026 Alpha Price List.",
    "Dropdown47": "Yes",
    "Text56": "Product information cards/sell sheets, brand website and social support, broker/distributor support, and licensee education/placement outreach.",
}


PRODUCTS = [
    {
        "slug": "koval-rye",
        "fields": {
            "Text2": "KOVAL Rye",
            "Text3": "850786006006",
            "Text4": "181-27087-75",
            "Text6": "750",
            "Text10": "40",
            "Text11": "80",
            "Text12": "3.66",
            "Text13": "3.66",
            "Text14": "9.25",
            "Text24": "11.5",
            "Text25": "8.0",
            "Text26": "9.50",
            "Text27": "19.84",
            "Text28": "6",
            "Text29": "20",
            "Text30": "100",
            "Text31": "50 cases",
            "Text36": "145.00",
            "Text39": "45.99",
            "Text44": "80",
            "Text48": "Illinois, California, Maryland, New York, Oklahoma, Wisconsin, Georgia, New Mexico, District of Columbia, Washington, Missouri, Texas, Colorado, Delaware, Minnesota, Connecticut, Rhode Island, New Jersey, Hawaii, Michigan, Tennessee, Massachusetts, Kansas.",
            "Text49": "Whiskey consumers and licensees seeking an approachable rye for sipping and classic cocktails.",
            "Text50": "100% rye mash bill; 80 proof; organic grain; versatile spice profile for Manhattans, Old Fashioneds, and neat pours.",
            "Text51": "Awards/press available on request.",
            "Text57": "Rye whiskey remains a growth and cocktail-standard category; this adds an organic, craft rye with broad proven account traction.",
            "Text58": "Fits DABS whiskey focus with proven multi-state demand, 6x750 pack, approachable proof, and strong cocktail utility for retail and licensee customers.",
        },
    },
    {
        "slug": "tw-brandy-finished-bourbon",
        "fields": {
            "Text2": "T&W Straight Bourbon Whiskey Finished in Brandy Casks",
            "Text3": "850061123251",
            "Text4": "N/A",
            "Text6": "750",
            "Text10": "50",
            "Text11": "100",
            "Text12": "3.75",
            "Text13": "3.75",
            "Text14": "8.75",
            "Text24": "11.5",
            "Text25": "8.0",
            "Text26": "12.00",
            "Text27": "19.15",
            "Text28": "6",
            "Text29": "20",
            "Text30": "100",
            "Text31": "50 cases",
            "Text36": "314.00",
            "Text39": "99.99",
            "Text44": "40",
            "Text48": "Illinois, Maryland, California, Oklahoma, Texas, Delaware, Colorado, Wisconsin, Missouri, District of Columbia, Massachusetts.",
            "Text49": "Premium bourbon buyers, whiskey collectors, cocktail bars, and licensees seeking distinctive finished American whiskey.",
            "Text50": "100 proof straight bourbon finished in fruit brandy casks; organic corn and millet base; premium craft story and differentiated finish.",
            "Text51": "Awards/press available on request.",
            "Text57": "Premium finished bourbon addresses consumer demand for distinctive barrel-finishing and craft whiskey discovery.",
            "Text58": "Fits DABS whiskey focus with a premium finished bourbon that adds a unique brandy-cask point of difference and verified demand in comparable markets.",
        },
    },
    {
        "slug": "tw-bib-millet",
        "fields": {
            "Text2": "T&W Millet Bottled in Bond Whiskey",
            "Text3": "850061123053",
            "Text4": "N/A",
            "Text6": "750",
            "Text10": "50",
            "Text11": "100",
            "Text12": "3.75",
            "Text13": "3.75",
            "Text14": "8.75",
            "Text24": "11.5",
            "Text25": "8.0",
            "Text26": "12.00",
            "Text27": "19.15",
            "Text28": "6",
            "Text29": "20",
            "Text30": "100",
            "Text31": "50 cases",
            "Text36": "314.00",
            "Text39": "99.99",
            "Text44": "40",
            "Text48": "Illinois, California, Oklahoma, Texas, Wisconsin, Colorado, Maryland, Delaware, District of Columbia, Missouri, New Jersey, Michigan.",
            "Text49": "Premium whiskey consumers, collectors, and craft accounts seeking unusual grain expressions and bottled-in-bond credibility.",
            "Text50": "100 proof Bottled in Bond Millet Whiskey; uncommon grain profile; organic grain; distinctive alternative to standard bourbon/rye sets.",
            "Text51": "Awards/press available on request.",
            "Text57": "Consumers are seeking differentiated American whiskey beyond standard mash bills; millet offers a rare grain story and shelf distinction.",
            "Text58": "Fits DABS whiskey focus by filling a clear assortment gap: bottled-in-bond craft whiskey built around millet, with proven out-of-state demand.",
        },
    },
]


CHECKED = {
    "Check Box15": "/Yes",
    "Check Box16": "/Yes",
    "Check Box52": "/Yes",
    "Check Box54": "/Yes",
    "Check Box55": "/Yes",
}


def fill_pdf(product: dict[str, object]) -> Path:
    reader = PdfReader(str(BLANK))
    writer = PdfWriter()
    writer.append(reader)
    if "/AcroForm" in reader.trailer["/Root"]:
        writer._root_object.update({NameObject("/AcroForm"): reader.trailer["/Root"]["/AcroForm"]})
        writer.set_need_appearances_writer(True)
        writer._root_object["/AcroForm"].update({NameObject("/NeedAppearances"): BooleanObject(True)})

    fields = dict(COMMON)
    fields.update(product["fields"])  # type: ignore[arg-type]
    fields.update(CHECKED)

    for page in writer.pages:
        writer.update_page_form_field_values(page, fields, auto_regenerate=True)
        for annot_ref in page.get("/Annots", []):
            annot = annot_ref.get_object()
            name = annot.get("/T")
            if name in CHECKED:
                annot.update({NameObject("/V"): NameObject(CHECKED[name]), NameObject("/AS"): NameObject(CHECKED[name])})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"2026_Product_Listing_Application_{product['slug']}.pdf"
    with out_path.open("wb") as fh:
        writer.write(fh)
    return out_path


def main() -> None:
    for product in PRODUCTS:
        print(fill_pdf(product))


if __name__ == "__main__":
    main()
