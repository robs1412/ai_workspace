#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import html
import io
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas

from ertc_renumber import OutputItem, render_suggestion_html, update_crosswalk_rows, write_csv


CURRENT_FILE_RE = re.compile(r"^(K\d{4})-(K\d{4})-(?:(K_\d{3})-)?(.+)$")
ORIGINAL_K_PREFIX_RE = re.compile(r"^K_\d{3}-")
REF_K_RE = re.compile(r"\bK_(\d{3})\b")
EXPLICIT_REMOVE_PAGES = {
    128, 148, 157, 159, 185, 186, 187, 312, 321, 328, 337, 338, 346,
    408, 409, 412, 418, 419, 420, 421, 428, 429, 430, 431, 432, 433, 434,
    647, 648, 649, 660, 693, 694, 702, 703, 704, 712, 713, 714, 723, 724, 725,
    737, 746, 758, 866, 867, 868, 869, 870, 871, 955,
}


@dataclass
class CurrentRow:
    start_k: str
    end_k: str
    month: str
    doc_type: str
    file: str
    title: str
    description: str
    from_field: str
    to_field: str
    original_file: str
    old_k: str


def k_label(page_num: int) -> str:
    return f"K{page_num:04d}"


def strip_original_k(name: str) -> str:
    return ORIGINAL_K_PREFIX_RE.sub("", name, count=1)


def load_rows(index_csv: Path) -> list[CurrentRow]:
    with index_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    rows: list[CurrentRow] = []
    for row in raw_rows:
        match = CURRENT_FILE_RE.match(row["File"])
        if not match:
            raise ValueError(f"Unrecognized current file format: {row['File']}")
        old_k = match.group(3)
        if not old_k:
            original_file = row["Original File"]
            old_k_match = re.match(r"^(K_\d{3})-(.+)$", original_file)
            if not old_k_match:
                raise ValueError(f"Unrecognized original file format: {original_file}")
            old_k = old_k_match.group(1)
        rows.append(
            CurrentRow(
                start_k=row["Start K"],
                end_k=row["End K"],
                month=row["Month"],
                doc_type=row["Type"],
                file=row["File"],
                title=row["Subject / Title"],
                description=row["Description"],
                from_field=row["From"],
                to_field=row["To"],
                original_file=row["Original File"],
                old_k=old_k,
            )
        )
    return rows


def build_stamp_overlay(width: float, height: float, label: str) -> PdfReader:
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFillColor(white)
    c.rect((width / 2) - 34, 10, 68, 14, stroke=0, fill=1)
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, 14, label)
    c.showPage()
    c.save()
    packet.seek(0)
    return PdfReader(packet)


def restamp_pdf(input_pdf: Path, out_pdf: Path, starting_page_num: int) -> int:
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()
    page_num = starting_page_num
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay_page = build_stamp_overlay(width, height, k_label(page_num)).pages[0]
        page.merge_page(overlay_page)
        writer.add_page(page)
        page_num += 1
    with out_pdf.open("wb") as handle:
        writer.write(handle)
    return len(reader.pages)


def single_image_hash(pdf_path: Path) -> str | None:
    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        return None
    images = list(reader.pages[0].images)
    if len(images) != 1:
        return None
    return hashlib.md5(images[0].data).hexdigest()


def find_remove_files(rows: list[CurrentRow], folder: Path) -> tuple[set[str], dict[str, str]]:
    explicit_files: set[str] = set()
    remove_hashes: set[str] = set()
    reasons: dict[str, str] = {}

    for row in rows:
        start_page = int(row.start_k[1:])
        if start_page not in EXPLICIT_REMOVE_PAGES:
            continue
        explicit_files.add(row.file)
        reasons[row.file] = f"explicit removal page {row.start_k}"
        file_hash = single_image_hash(folder / row.file)
        if file_hash:
            remove_hashes.add(file_hash)

    remove_files = set(explicit_files)
    for row in rows:
        file_hash = single_image_hash(folder / row.file)
        if file_hash and file_hash in remove_hashes:
            remove_files.add(row.file)
            reasons.setdefault(row.file, f"duplicate Leyton image hash {file_hash}")
    return remove_files, reasons


def new_pdf_name(row: CurrentRow, start_page: int, end_page: int) -> str:
    suffix = strip_original_k(row.original_file)
    prefix = f"{k_label(start_page)}-{k_label(end_page)}"
    if suffix.lower().endswith(".pdf"):
        return f"{prefix}-{suffix}"
    return f"{prefix}-{suffix}.pdf"


def current_sidecar_name(row: CurrentRow) -> str:
    return f"{row.start_k}-{row.end_k}-{row.original_file}"


def new_sidecar_name(row: CurrentRow, start_page: int, end_page: int) -> str:
    suffix = strip_original_k(row.original_file)
    return f"{k_label(start_page)}-{k_label(end_page)}-{suffix}"


def render_index_html(rows: list[OutputItem], html_path: Path, folder_path: Path) -> None:
    lines = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Discovery Production One-Folder New Index</title>",
        "<style>",
        "@page { size: letter landscape; margin: 0.35in; }",
        "body{font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Arial,sans-serif;margin:0;color:#111}",
        "h1{font-size:18px;margin:0 0 6px}",
        ".meta{font-size:11px;color:#555;margin:0 0 12px;line-height:1.35}",
        "table{border-collapse:collapse;width:100%;font-size:10px;line-height:1.22}",
        "th{background:#f3f5f7;border:1px solid #d8dde3;padding:5px;text-align:left}",
        "td{border:1px solid #e1e4e8;padding:5px;vertical-align:top}",
        "tr.main:nth-of-type(2n){background:#fbfbfc}",
        ".num{white-space:nowrap}",
        ".file{font-family:Menlo,Consolas,monospace;font-size:9px;word-break:break-word}",
        ".subject{font-weight:600}",
        ".email-meta{font-weight:400;font-size:9px;line-height:1.3;color:#444;margin-top:4px}",
        ".label{font-weight:600;color:#444}",
        "a{color:#0645ad;text-decoration:none}",
        "</style></head><body>",
        "<h1>Discovery Production One-Folder New Index</h1>",
        (
            f"<p class=\"meta\">Folder: <code>{html.escape(str(folder_path))}</code><br>"
            f"Rows: {len(rows)}. Every retained page is Bates-numbered sequentially.</p>"
        ),
        "<table><thead><tr>"
        "<th>Start</th><th>End</th><th>Month</th><th>Type</th><th>File</th><th>Subject / Title</th>"
        "</tr></thead><tbody>",
    ]
    for row in rows:
        href = "file://" + str(folder_path / row.new_name)
        subject_html = html.escape(row.title)
        if row.doc_type.strip().lower() == "email":
            parts: list[str] = []
            if row.from_field.strip():
                parts.append(
                    f'<div class="email-meta"><span class="label">From:</span> {html.escape(row.from_field)}</div>'
                )
            if row.to_field.strip():
                parts.append(
                    f'<div class="email-meta"><span class="label">To:</span> {html.escape(row.to_field)}</div>'
                )
            subject_html += "".join(parts)
        lines.append(
            "<tr class=\"main\">"
            f"<td class=\"num\">{html.escape(row.start_k)}</td>"
            f"<td class=\"num\">{html.escape(row.end_k)}</td>"
            f"<td>{html.escape(row.month)}</td>"
            f"<td>{html.escape(row.doc_type)}</td>"
            f"<td class=\"file\"><a href=\"{html.escape(href)}\">{html.escape(row.new_name)}</a></td>"
            f"<td class=\"subject\">{subject_html}</td>"
            "</tr>"
        )
    lines.append("</tbody></table></body></html>")
    html_path.write_text("\n".join(lines), encoding="utf-8")


def render_pdf_from_html(html_path: Path, pdf_path: Path, orientation: str = "landscape") -> None:
    renderer = Path("/Users/werkstatt/ai_workspace/.pdf_renderer/html_to_pdf.js")
    subprocess.run(
        ["node", str(renderer), str(html_path), str(pdf_path), orientation],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: rebuild_ertc_v2.py", file=sys.stderr)
        return 2

    v2_root = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC/v2")
    folder = v2_root / "discovery-production-one-folder-new"
    addl = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC/v2_additional")
    index_csv = addl / "discovery-production-one-folder-new-index.csv"
    index_html = addl / "discovery-production-one-folder-new-index.html"
    index_pdf = v2_root / "Discovery Production One-Folder New Index.pdf"
    suggestion_csv = addl / "discovery-response-request-suggestion-renumbered.csv"
    suggestion_html = addl / "discovery-response-request-suggestion-renumbered.html"
    suggestion_pdf = v2_root / "Discovery Response Request Suggestions.pdf"
    removed_dir = folder / "__removed_from_production"
    removed_dir.mkdir(exist_ok=True)
    removed_manifest = folder / "__removed_from_production_manifest.csv"

    rows = load_rows(index_csv)
    remove_files, remove_reasons = find_remove_files(rows, folder)
    kept_rows = [row for row in rows if row.file not in remove_files]

    with suggestion_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        suggestion_rows = list(csv.DictReader(handle))

    with tempfile.TemporaryDirectory(prefix="ertc-v2-rebuild-") as tmp:
        tmp_dir = Path(tmp)
        staged_dir = tmp_dir / "staged"
        staged_dir.mkdir()

        output_rows: list[OutputItem] = []
        page_counter = 1
        for row in kept_rows:
            source_pdf = folder / row.file
            pages = len(PdfReader(str(source_pdf)).pages)
            start_page = page_counter
            end_page = page_counter + pages - 1
            new_name = new_pdf_name(row, start_page, end_page)
            restamp_pdf(source_pdf, staged_dir / new_name, start_page)
            output_rows.append(
                OutputItem(
                    old_k=row.old_k,
                    old_name=row.original_file,
                    new_name=new_name,
                    start_k=k_label(start_page),
                    end_k=k_label(end_page),
                    start_page=start_page,
                    end_page=end_page,
                    pages=pages,
                    month=row.month,
                    doc_type=row.doc_type,
                    title=row.title,
                    description=row.description,
                    from_field=row.from_field,
                    to_field=row.to_field,
                )
            )
            if row.original_file.lower().endswith((".xlsx", ".xls")):
                sidecar = folder / current_sidecar_name(row)
                if sidecar.exists():
                    shutil.copy2(sidecar, staged_dir / new_sidecar_name(row, start_page, end_page))
            page_counter = end_page + 1

        removed_records: list[dict[str, str]] = []
        for file_name in sorted(remove_files):
            src = folder / file_name
            if src.exists():
                shutil.move(str(src), str(removed_dir / file_name))
            removed_records.append({"File": file_name, "Reason": remove_reasons.get(file_name, "removed")})

        for path in list(folder.iterdir()):
            if not path.is_file():
                continue
            if path.name == ".DS_Store":
                continue
            if path.name.startswith("K"):
                path.unlink()

        for path in staged_dir.iterdir():
            shutil.move(str(path), str(folder / path.name))

    output_map = {row.old_k: row for row in output_rows}
    updated_crosswalk = update_crosswalk_rows(suggestion_rows, output_map)

    index_rows: list[dict[str, str]] = []
    for row in output_rows:
        index_rows.append(
            {
                "Start K": row.start_k,
                "End K": row.end_k,
                "Month": row.month,
                "Type": row.doc_type,
                "File": row.new_name,
                "Subject / Title": row.title,
                "Description": row.description,
                "From": row.from_field,
                "To": row.to_field,
                "Original File": row.old_name,
            }
        )

    write_csv(
        index_csv,
        index_rows,
        ["Start K", "End K", "Month", "Type", "File", "Subject / Title", "Description", "From", "To", "Original File"],
    )
    render_index_html(output_rows, index_html, folder)
    render_pdf_from_html(index_html, index_pdf, "landscape")

    write_csv(
        suggestion_csv,
        updated_crosswalk,
        ["Request No.", "Request", "Draft Response", "Documents Produced / K Numbers", "Mapping Note"],
    )
    render_suggestion_html(updated_crosswalk, suggestion_html)
    render_pdf_from_html(suggestion_html, suggestion_pdf, "portrait")

    write_csv(removed_manifest, removed_records, ["File", "Reason"])

    print(f"Removed files: {len(remove_files)}")
    print(f"Kept production rows: {len(output_rows)}")
    print(f"Total pages: {output_rows[-1].end_page if output_rows else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
