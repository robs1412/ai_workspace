#!/usr/bin/env python3

from __future__ import annotations

import csv
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ertc_renumber import (
    OutputItem,
    convert_docx,
    convert_xlsx,
    k_label,
    render_index_html,
    render_suggestion_html,
    stamp_pdf,
    update_crosswalk_rows,
    write_csv,
)
from pypdf import PdfReader


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
    original_k: str
    original_file: str


def load_current_rows(path: Path) -> list[CurrentRow]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: list[CurrentRow] = []
    for row in rows:
        out.append(
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
                original_k=row["Original K"],
                original_file=row["Original File"],
            )
        )
    return out


def new_name_for_row(row: CurrentRow, start_page: int, end_page: int) -> str:
    original_file = row.original_file
    if original_file.lower().endswith(".pdf"):
        stem = original_file[:-4]
        return f"{k_label(start_page)}-{k_label(end_page)}-{stem}.pdf"
    return f"{k_label(start_page)}-{k_label(end_page)}-{original_file}.pdf"


def current_index_rows(output_rows: list[OutputItem]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in output_rows:
        rows.append(
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
                "Original K": row.old_k,
                "Original File": row.old_name,
            }
        )
    return rows


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("Usage: ertc_resequence_current.py <source_dir> <current_index_csv> <v1_suggestion_csv>", file=sys.stderr)
        return 2

    source_dir = Path(argv[1]).resolve()
    current_index_csv = Path(argv[2]).resolve()
    v1_suggestion_csv = Path(argv[3]).resolve()
    parent_dir = source_dir.parent
    originals_dir = source_dir / "__original_nonpdf_sources"

    current_rows = load_current_rows(current_index_csv)
    with v1_suggestion_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        suggestion_rows = list(csv.DictReader(handle))

    with tempfile.TemporaryDirectory(prefix="ertc-resequence-") as tmp:
        tmp_dir = Path(tmp)
        staged_dir = tmp_dir / "staged"
        staged_dir.mkdir()

        output_rows: list[OutputItem] = []
        page_counter = 1
        for row in current_rows:
            base_pdf = tmp_dir / f"{row.original_k}.pdf"
            if row.original_file.lower().endswith(".xlsx"):
                convert_xlsx(originals_dir / row.original_file, base_pdf, tmp_dir)
            elif row.original_file.lower().endswith(".docx"):
                convert_docx(originals_dir / row.original_file, base_pdf, tmp_dir)
            else:
                shutil.copy2(source_dir / row.file, base_pdf)

            pages = len(PdfReader(str(base_pdf)).pages)
            start_page = page_counter
            end_page = page_counter + pages - 1
            new_name = new_name_for_row(row, start_page, end_page)
            stamped_pdf = staged_dir / new_name
            stamp_pdf(base_pdf, stamped_pdf, start_page)

            output_rows.append(
                OutputItem(
                    old_k=row.original_k,
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
            page_counter = end_page + 1

        for path in source_dir.iterdir():
            if path.is_file() and path.name.startswith("K") and not path.name.startswith("K_"):
                path.unlink()
        for path in staged_dir.iterdir():
            shutil.move(str(path), str(source_dir / path.name))

    output_map = {row.old_k: row for row in output_rows}
    updated_crosswalk = update_crosswalk_rows(suggestion_rows, output_map)

    index_csv = parent_dir / "discovery-production-one-folder-new-index.csv"
    index_html = parent_dir / "discovery-production-one-folder-new-index.html"
    suggestion_csv = parent_dir / "discovery-response-request-suggestion-renumbered.csv"
    suggestion_html = parent_dir / "discovery-response-request-suggestion-renumbered.html"

    write_csv(
        index_csv,
        current_index_rows(output_rows),
        [
            "Start K",
            "End K",
            "Month",
            "Type",
            "File",
            "Subject / Title",
            "Description",
            "From",
            "To",
            "Original K",
            "Original File",
        ],
    )
    render_index_html(output_rows, index_html, source_dir)
    write_csv(
        suggestion_csv,
        updated_crosswalk,
        [
            "Request No.",
            "Request",
            "Draft Response",
            "Documents Produced / K Numbers",
            "Mapping Note",
        ],
    )
    render_suggestion_html(updated_crosswalk, suggestion_html)

    print(f"Resequenced files: {len(output_rows)}")
    print(f"Total pages: {output_rows[-1].end_page if output_rows else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
