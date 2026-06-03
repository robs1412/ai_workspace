#!/usr/bin/env python3
import csv
import hashlib
import html
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path


ROOT = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC")
PROD = ROOT / "discovery-production-one-folder"
HTML_OUT = ROOT / "discovery-production-duplicate-report.html"
CSV_OUT = ROOT / "discovery-production-duplicate-report.csv"

DOC_EXTS = {".pdf", ".docx", ".xlsx", ".txt"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".bmp"}


def k_number(name: str) -> int:
    match = re.match(r"K_(\d+)", name)
    return int(match.group(1)) if match else 999999


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9$%.,:/@#&+() -]", "", text)
    return text.strip()


def pdf_text(path: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        subprocess.run(
            ["pdftotext", "-layout", str(path), tmp.name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            return Path(tmp.name).read_text(errors="ignore")
        except OSError:
            return ""


def title_from_filename(name: str) -> str:
    base = Path(name).stem
    base = re.sub(r"^K_\d+-\d{4}-\d{2}_", "", base)
    base = re.sub(r"-att$", "", base)
    return base.replace("_", " ")


def group_rows(label, groups, reason):
    rows = []
    for idx, members in enumerate(groups, 1):
        members = sorted(members, key=lambda p: k_number(p.name))
        rows.append(
            {
                "group": f"{label}-{idx:03d}",
                "reason": reason,
                "count": len(members),
                "files": members,
                "title": title_from_filename(members[0].name),
            }
        )
    return rows


def main():
    files = sorted([p for p in PROD.iterdir() if p.is_file()], key=lambda p: k_number(p.name))
    docs = [p for p in files if p.suffix.lower() in DOC_EXTS]
    images = [p for p in files if p.suffix.lower() in IMAGE_EXTS]
    other = [p for p in files if p.suffix.lower() not in DOC_EXTS | IMAGE_EXTS]

    by_hash = defaultdict(list)
    for path in docs:
        by_hash[sha256(path)].append(path)
    exact_groups = [v for v in by_hash.values() if len(v) > 1]

    exact_members = {p for members in exact_groups for p in members}
    by_pdf_text = defaultdict(list)
    for path in docs:
        if path in exact_members or path.suffix.lower() != ".pdf":
            continue
        text = normalize_text(pdf_text(path))
        if len(text) >= 200:
            by_pdf_text[hashlib.sha256(text.encode("utf-8")).hexdigest()].append(path)
    text_groups = [v for v in by_pdf_text.values() if len(v) > 1]

    report_groups = []
    report_groups.extend(group_rows("EXACT", exact_groups, "Exact duplicate file bytes"))
    report_groups.extend(group_rows("PDFTEXT", text_groups, "Same extracted PDF text"))
    report_groups.sort(key=lambda g: k_number(g["files"][0].name))

    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Group", "Reason", "Count", "K #", "File", "Size Bytes", "Title"])
        for group in report_groups:
            for path in group["files"]:
                writer.writerow(
                    [
                        group["group"],
                        group["reason"],
                        group["count"],
                        path.name.split("-", 1)[0],
                        path.name,
                        path.stat().st_size,
                        group["title"],
                    ]
                )

    total_duplicate_files = sum(len(g["files"]) for g in report_groups)
    html_parts = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        "<title>Discovery Production Duplicate Report</title>",
        "<style>",
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:28px;color:#1f2933}",
        "h1{font-size:24px;margin:0 0 8px} h2{font-size:18px;margin-top:28px}",
        "p{line-height:1.45} table{border-collapse:collapse;width:100%;font-size:13px}",
        "th,td{border:1px solid #d8dee4;padding:7px 8px;vertical-align:top}",
        "th{background:#f3f4f6;text-align:left}.num{text-align:right;white-space:nowrap}",
        ".muted{color:#667085}.group{background:#fafafa;font-weight:600}",
        "</style></head><body>",
        "<h1>Discovery Production Duplicate Report</h1>",
        f"<p class='muted'>Folder: {html.escape(str(PROD))}</p>",
        "<p>This report checks document-like files only: PDF, DOCX, XLSX, and TXT. "
        "Image attachments were excluded so repeated signature/logo images do not dominate the duplicate list.</p>",
        "<table><tr><th>Metric</th><th class='num'>Count</th></tr>",
        f"<tr><td>Total files in production folder</td><td class='num'>{len(files)}</td></tr>",
        f"<tr><td>Document files checked</td><td class='num'>{len(docs)}</td></tr>",
        f"<tr><td>Image attachments ignored</td><td class='num'>{len(images)}</td></tr>",
        f"<tr><td>Other files ignored</td><td class='num'>{len(other)}</td></tr>",
        f"<tr><td>Duplicate groups found</td><td class='num'>{len(report_groups)}</td></tr>",
        f"<tr><td>Files in duplicate groups</td><td class='num'>{total_duplicate_files}</td></tr>",
        "</table>",
        "<h2>Duplicate Groups</h2>",
    ]
    if not report_groups:
        html_parts.append("<p>No duplicate document groups found.</p>")
    else:
        html_parts.append("<table><tr><th>Group</th><th>Reason</th><th>K #</th><th>File</th><th class='num'>Size</th><th>Title</th></tr>")
        for group in report_groups:
            first = True
            for path in group["files"]:
                html_parts.append("<tr>")
                if first:
                    html_parts.append(
                        f"<td class='group' rowspan='{len(group['files'])}'>{html.escape(group['group'])}</td>"
                    )
                    html_parts.append(
                        f"<td rowspan='{len(group['files'])}'>{html.escape(group['reason'])}</td>"
                    )
                    first = False
                html_parts.append(f"<td>{html.escape(path.name.split('-', 1)[0])}</td>")
                html_parts.append(f"<td>{html.escape(path.name)}</td>")
                html_parts.append(f"<td class='num'>{path.stat().st_size:,}</td>")
                html_parts.append(f"<td>{html.escape(group['title'])}</td>")
                html_parts.append("</tr>")
        html_parts.append("</table>")
    html_parts.append("</body></html>")
    HTML_OUT.write_text("\n".join(html_parts), encoding="utf-8")

    print(f"HTML={HTML_OUT}")
    print(f"CSV={CSV_OUT}")
    print(
        f"FILES={len(files)} DOCS_CHECKED={len(docs)} IMAGES_IGNORED={len(images)} "
        f"DUPLICATE_GROUPS={len(report_groups)} DUPLICATE_FILES={total_duplicate_files}"
    )


if __name__ == "__main__":
    main()
