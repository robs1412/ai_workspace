#!/usr/local/bin/python3.13
"""Build a standalone HTML handout from the class Markdown packet."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


DEFAULT_SOURCE = Path("2026-family-ai-class-expanded.md")
DEFAULT_OUTPUT = Path("2026-family-ai-class-expanded.html")


def slugify(text: str, used: set[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    base = slug
    index = 2
    while slug in used:
        slug = f"{base}-{index}"
        index += 1
    used.add(slug)
    return slug


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def close_lists(stack: list[tuple[int, str]], out: list[str], target_indent: int = -1) -> None:
    while stack and stack[-1][0] > target_indent:
        _indent, tag = stack.pop()
        out.append(f"</{tag}>")


def build(source: Path, output: Path, include_static_toc: bool = True, google_doc_mode: bool = False) -> None:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    used: set[str] = set()
    headings: list[tuple[int, str, str]] = []

    out: list[str] = []
    list_stack: list[tuple[int, str]] = []
    in_code = False
    code_lines: list[str] = []
    paragraph: list[str] = []
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    while index < len(lines):
        line = lines[index]

        if in_code:
            if line.startswith("```"):
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                code_lines.append(line)
            index += 1
            continue

        if line.startswith("```"):
            flush_paragraph()
            close_lists(list_stack, out)
            in_code = True
            index += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_lists(list_stack, out)
            level = len(heading.group(1))
            title = heading.group(2).strip()
            slug = slugify(re.sub(r"`([^`]+)`", r"\1", title), used)
            headings.append((level, title, slug))
            if google_doc_mode:
                out.append(f"<h{level}>{inline(title)}</h{level}>")
            else:
                out.append(f'<h{level} id="{slug}">{inline(title)}</h{level}>')
            index += 1
            continue

        if "|" in line and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            flush_paragraph()
            close_lists(list_stack, out)
            headers = split_table_row(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1
            out.append("<table>")
            out.append("<thead><tr>" + "".join(f"<th>{inline(cell)}</th>" for cell in headers) + "</tr></thead>")
            out.append("<tbody>")
            for row in rows:
                out.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>")
            out.append("</tbody></table>")
            continue

        list_match = re.match(r"^(\s*)([-*]|\d+\.)\s+(.+)$", line)
        if list_match:
            flush_paragraph()
            indent = len(list_match.group(1))
            marker = list_match.group(2)
            tag = "ol" if marker.endswith(".") and marker[:-1].isdigit() else "ul"
            while list_stack and list_stack[-1][0] > indent:
                _old_indent, old_tag = list_stack.pop()
                out.append(f"</{old_tag}>")
            if not list_stack or list_stack[-1][0] < indent or list_stack[-1][1] != tag:
                out.append(f"<{tag}>")
                list_stack.append((indent, tag))
            out.append(f"<li>{inline(list_match.group(3).strip())}</li>")
            index += 1
            continue

        if not line.strip():
            flush_paragraph()
            close_lists(list_stack, out)
            index += 1
            continue

        close_lists(list_stack, out)
        paragraph.append(line.strip())
        index += 1

    flush_paragraph()
    close_lists(list_stack, out)

    toc_html = ""
    if include_static_toc:
        toc_lines = ['<nav class="toc" aria-label="Table of contents">', "<h2>Contents</h2>", "<ol>"]
        for level, title, slug in headings:
            if level <= 1:
                continue
            css_level = min(max(level - 2, 0), 4)
            toc_lines.append(f'<li class="toc-l{css_level}"><a href="#{slug}">{inline(title)}</a></li>')
        toc_lines.extend(["</ol>", "</nav>"])
        toc_html = "".join(toc_lines)

    if google_doc_mode:
        contents = ["<h2>Contents</h2>", "<ul>"]
        for level, title, _slug in headings:
            if level <= 1:
                continue
            indent = "&nbsp;" * max(0, (level - 2) * 4)
            contents.append(f"<li>{indent}{inline(title)}</li>")
        contents.append("</ul>")
        body_parts = list(out)
        insert_at = 1 if body_parts and body_parts[0].startswith("<h1") else 0
        body_parts[insert_at:insert_at] = contents
        document = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>2026 Family AI Class</title>
  </head>
  <body>
    {''.join(body_parts)}
  </body>
</html>
"""
        output.write_text(document, encoding="utf-8")
        print(f"Wrote {output} with {len(headings)} headings")
        return

    document = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>2026 Family AI Class - Expanded Teaching Packet</title>
    <style>
      :root {{
        --ink: #17202a;
        --muted: #5b6672;
        --paper: #f7f5ef;
        --panel: #ffffff;
        --line: #d8dee6;
        --accent: #28666e;
        --gold: #a97922;
        --code: #f1f4f6;
      }}
      * {{ box-sizing: border-box; }}
      html {{ scroll-behavior: smooth; }}
      body {{
        margin: 0;
        color: var(--ink);
        background: var(--paper);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.55;
      }}
      .layout {{
        display: grid;
        grid-template-columns: minmax(260px, 340px) minmax(0, 1fr);
        gap: 28px;
        width: min(1360px, calc(100% - 32px));
        margin: 0 auto;
        padding: 24px 0 56px;
      }}
      .toc {{
        position: sticky;
        top: 16px;
        max-height: calc(100vh - 32px);
        overflow: auto;
        align-self: start;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 18px;
      }}
      .toc h2 {{
        margin: 0 0 10px;
        font-size: 1rem;
      }}
      .toc ol {{
        list-style: none;
        padding: 0;
        margin: 0;
      }}
      .toc li {{
        margin: 0;
        padding: 3px 0;
        font-size: 0.92rem;
      }}
      .toc a {{
        color: var(--accent);
        text-decoration: none;
      }}
      .toc a:hover {{ text-decoration: underline; }}
      .toc-l1 {{ padding-left: 14px !important; }}
      .toc-l2 {{ padding-left: 28px !important; font-size: 0.86rem !important; }}
      .toc-l3 {{ padding-left: 42px !important; font-size: 0.82rem !important; }}
      .content {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: clamp(24px, 4vw, 56px);
      }}
      h1 {{
        font-size: clamp(2.2rem, 6vw, 4.8rem);
        line-height: 1;
        margin: 0 0 16px;
        padding-bottom: 18px;
        border-bottom: 4px solid var(--accent);
      }}
      h2 {{
        margin-top: 42px;
        padding-top: 18px;
        border-top: 1px solid var(--line);
        font-size: 1.8rem;
      }}
      h3 {{ margin-top: 28px; font-size: 1.25rem; color: var(--accent); }}
      h4, h5, h6 {{ margin-top: 22px; }}
      p, li {{ color: var(--ink); }}
      a {{ color: var(--accent); }}
      table {{
        width: 100%;
        border-collapse: collapse;
        margin: 18px 0 24px;
        font-size: 0.95rem;
      }}
      th, td {{
        border: 1px solid var(--line);
        padding: 10px 12px;
        vertical-align: top;
      }}
      th {{
        background: #eef4f4;
        text-align: left;
      }}
      pre {{
        overflow: auto;
        background: var(--code);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px;
      }}
      code {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 0.92em;
      }}
      p code, li code {{
        background: var(--code);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 1px 4px;
      }}
      blockquote {{
        border-left: 4px solid var(--gold);
        margin-left: 0;
        padding-left: 16px;
        color: var(--muted);
      }}
      @media (max-width: 900px) {{
        .layout {{ display: block; }}
        .toc {{
          position: static;
          max-height: none;
          margin-bottom: 18px;
        }}
      }}
      @media print {{
        body {{ background: white; }}
        .layout {{ display: block; width: auto; padding: 0; }}
        .toc {{
          position: static;
          max-height: none;
          border: 0;
          page-break-after: always;
        }}
        .content {{ border: 0; padding: 0; }}
        a {{ color: black; text-decoration: none; }}
        h2 {{ page-break-after: avoid; }}
        pre, table {{ page-break-inside: avoid; }}
      }}
    </style>
  </head>
  <body>
    <div class="layout">
      {toc_html}
      <main class="content">
        {''.join(out)}
      </main>
    </div>
  </body>
</html>
"""
    output.write_text(document, encoding="utf-8")
    print(f"Wrote {output} with {len(headings)} headings")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build class HTML from Markdown.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-static-toc", action="store_true")
    parser.add_argument("--google-doc-mode", action="store_true")
    args = parser.parse_args()
    build(
        Path(args.source),
        Path(args.output),
        include_static_toc=not args.no_static_toc,
        google_doc_mode=args.google_doc_mode,
    )
