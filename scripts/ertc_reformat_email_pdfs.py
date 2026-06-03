#!/usr/bin/env python3
"""Reformat generated ERTC email PDFs after verifying against originals."""

from __future__ import annotations

import csv
import html
import re
import subprocess
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC/discovery-production-one-folder")
ORIGINALS = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC/discovery-production/E-mails_numbered")
MANIFEST = Path("/Users/werkstatt/ai_workspace/ertc-email-reformat-manifest-2026-05-17.csv")
INITIAL_RENUMBER_MANIFEST = Path("/Users/werkstatt/ai_workspace/ertc-renumber-manifest-2026-05-17.csv")
REMOVE_RENUMBER_MANIFEST = Path("/Users/werkstatt/ai_workspace/ertc-renumber-remove-483-484-513-manifest-2026-05-17.csv")


HEADER_RE = re.compile(r"^(Subject|Date|From|To|Cc|Bcc|Message-ID):\s*(.*)$", re.I)
THREAD_HEADER_RE = re.compile(r"^(From|Sent|To|Cc|Subject):\s*", re.I)


def run_text(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)


def pdf_title(path: Path) -> str:
    out = run_text(["pdfinfo", str(path)])
    for line in out.splitlines():
        if line.startswith("Title:"):
            return line.split(":", 1)[1].strip()
    return ""


def pdf_text(path: Path) -> str:
    return run_text(["pdftotext", "-layout", str(path), "-"])


def normalize_for_compare(text: str) -> str:
    lines = []
    for line in text.replace("\f", "\n").splitlines():
        lines.append(re.sub(r"\s+", " ", line).strip())
    return "\n".join(line for line in lines if line)


def clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.replace("\f", "\n").splitlines():
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if line == "Body":
            continue
        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        lines.append(line)
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def split_header_body(lines: list[str]) -> tuple[list[str], list[str]]:
    header: list[str] = []
    body: list[str] = []
    in_header = True
    for line in lines:
        if in_header and (HEADER_RE.match(line) or line.startswith("<") or line == ""):
            header.append(line)
            continue
        in_header = False
        body.append(line)
    while header and header[-1] == "":
        header.pop()
    return header, body


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(html.escape(text), style)


def line_space_after(line: str) -> int:
    if THREAD_HEADER_RE.match(line):
        return 5
    if re.match(r"^(On .+ wrote:|Begin forwarded message:)", line, re.I):
        return 8
    if re.match(r"^(Hi|Hey|Hello|Savannah|Stef|Robert|Sonat|Thanks|Thank you|Best|Warm regards|Regards|Sincerely)[,!.]?$", line, re.I):
        return 7
    if len(line) <= 34 and not line.endswith((".", "?", "!", ":")):
        return 4
    return 3


def build_pdf(source_text: str, output: Path, title: str) -> None:
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        "EmailHeader",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#222222"),
        spaceAfter=2,
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "EmailBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.black,
        spaceAfter=3,
        alignment=TA_LEFT,
    )
    divider_style = ParagraphStyle(
        "EmailDivider",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#444444"),
        spaceBefore=8,
        spaceAfter=5,
    )
    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=title,
        author="anonymous",
    )
    lines = clean_lines(source_text)
    header, body = split_header_body(lines)
    story = []
    for line in header:
        if line:
            story.append(para(line, header_style))
    if header and body:
        story.append(Spacer(1, 0.14 * inch))
    for line in body:
        if not line:
            story.append(Spacer(1, 0.08 * inch))
            continue
        style = divider_style if re.match(r"^(On .+ wrote:|From: .+)", line, re.I) else body_style
        item = para(line, style)
        item.style.spaceAfter = line_space_after(line)
        story.append(item)
    doc.build(story or [para("", body_style)])


def build_original_map() -> dict[str, Path]:
    """Map current K_ email filenames to preserved original email PDFs."""
    old_to_current: dict[int, int] = {}
    deleted: set[int] = set()
    if REMOVE_RENUMBER_MANIFEST.exists():
        with REMOVE_RENUMBER_MANIFEST.open() as f:
            for row in csv.DictReader(f):
                old = int(row["old_sequence"])
                if row["action"] == "delete":
                    deleted.add(old)
                elif row["action"] == "rename":
                    old_to_current[old] = int(row["new_sequence"])
    mapping: dict[str, Path] = {}
    with INITIAL_RENUMBER_MANIFEST.open() as f:
        for row in csv.DictReader(f):
            if row.get("action") != "move" or row.get("kind") != "email":
                continue
            old_seq = int(row["sequence"])
            if old_seq in deleted:
                continue
            current_seq = old_to_current.get(old_seq, old_seq)
            target_name = Path(row["target"]).name
            current_name = re.sub(r"^K_\d{3}-", f"K_{current_seq:03d}-", target_name)
            source = Path(row["source"])
            try:
                rel = source.relative_to("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC/discovery-production-one-folder")
            except ValueError:
                rel = Path("E-mails_numbered") / source.name
            mapping[current_name] = Path("/Users/robert/Library/CloudStorage/Dropbox/2026-ERTC/discovery-production") / rel
    return mapping


def main() -> int:
    rows: list[list[str]] = []
    email_pdfs = sorted(ROOT.glob("K_*-*_Email.pdf"))
    original_map = build_original_map()
    verified = 0
    rewritten = 0
    mismatches = 0
    missing = 0
    temp_outputs: list[tuple[Path, Path]] = []

    for pdf in email_pdfs:
        title = pdf_title(pdf)
        original = original_map.get(pdf.name)
        if not original or not original.exists():
            original = ORIGINALS / f"{title}.pdf" if title else Path()
        if not original.exists():
            missing += 1
            rows.append(["missing-original", pdf.name, title, str(original), "", ""])
            continue
        current_text = pdf_text(pdf)
        original_text = pdf_text(original)
        if normalize_for_compare(current_text) != normalize_for_compare(original_text):
            mismatches += 1
            rows.append(["text-mismatch", pdf.name, title, str(original), "", ""])
            continue
        verified += 1
        tmp = pdf.with_suffix(".tmp-reformatted.pdf")
        build_pdf(original_text, tmp, title)
        temp_outputs.append((tmp, pdf))
        rows.append(["rewritten", pdf.name, title, str(original), str(tmp), str(pdf)])

    if mismatches or missing:
        for tmp, _ in temp_outputs:
            tmp.unlink(missing_ok=True)
        with MANIFEST.open("w", newline="") as f:
            csv.writer(f).writerows([["status", "file", "original_title", "original_path", "temp", "target"], *rows])
        print(f"ABORT verified={verified} missing={missing} mismatches={mismatches} manifest={MANIFEST}")
        return 2

    for tmp, target in temp_outputs:
        tmp.replace(target)
        rewritten += 1

    with MANIFEST.open("w", newline="") as f:
        csv.writer(f).writerows([["status", "file", "original_title", "original_path", "temp", "target"], *rows])
    print(f"OK verified={verified} rewritten={rewritten} missing={missing} mismatches={mismatches} manifest={MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
