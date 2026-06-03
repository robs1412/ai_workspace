#!/usr/bin/env python3

from __future__ import annotations

import csv
import html
import sys
from pathlib import Path


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(csv_path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "Start K",
        "End K",
        "Month",
        "Type",
        "File",
        "Subject / Title",
        "Description",
        "From",
        "To",
        "Original File",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{k: row.get(k, "") for k in fieldnames} for row in rows])


def render_html(rows: list[dict[str, str]], html_path: Path, folder_path: Path) -> None:
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
        "tr.main:nth-of-type(4n+1), tr.main:nth-of-type(4n+2){background:#fbfbfc}",
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
        href = "file://" + str(folder_path / row["File"])
        subject_html = html.escape(row["Subject / Title"])
        if row.get("Type", "").strip().lower() == "email":
            from_text = row.get("From", "").strip()
            to_text = row.get("To", "").strip()
            meta_parts: list[str] = []
            if from_text:
                meta_parts.append(
                    f'<div class="email-meta"><span class="label">From:</span> {html.escape(from_text)}</div>'
                )
            if to_text:
                meta_parts.append(
                    f'<div class="email-meta"><span class="label">To:</span> {html.escape(to_text)}</div>'
                )
            if meta_parts:
                subject_html += "".join(meta_parts)
        lines.append(
            "<tr class=\"main\">"
            f"<td class=\"num\">{html.escape(row['Start K'])}</td>"
            f"<td class=\"num\">{html.escape(row['End K'])}</td>"
            f"<td>{html.escape(row['Month'])}</td>"
            f"<td>{html.escape(row['Type'])}</td>"
            f"<td class=\"file\"><a href=\"{html.escape(href)}\">{html.escape(row['File'])}</a></td>"
            f"<td class=\"subject\">{subject_html}</td>"
            "</tr>"
        )

    lines.append("</tbody></table></body></html>")
    html_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print("Usage: rebuild_ertc_index.py <csv> <html> <pdf> <folder>", file=sys.stderr)
        return 2

    csv_path = Path(argv[1]).resolve()
    html_path = Path(argv[2]).resolve()
    pdf_path = Path(argv[3]).resolve()
    folder_path = Path(argv[4]).resolve()

    rows = load_rows(csv_path)
    write_csv(csv_path, rows)
    render_html(rows, html_path, folder_path)

    renderer = Path("/Users/werkstatt/ai_workspace/.pdf_renderer/html_to_pdf.js")
    import subprocess

    subprocess.run(
        ["node", str(renderer), str(html_path), str(pdf_path), "landscape"],
        check=True,
        text=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
