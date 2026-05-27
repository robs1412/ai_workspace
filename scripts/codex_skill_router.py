#!/usr/local/bin/python3.13
"""Metadata-first Codex skill index and router.

The index stores only skill metadata. Skill bodies are read only by the
explicit `show` command after a candidate has been selected.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_INDEX = Path("project_hub/artifacts/codex-skill-router/skill-index.json")
DEFAULT_ROOTS = (
    Path("/Users/admin/.codex/skills"),
    Path("/Users/admin/.codex/plugins/cache"),
)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "codex",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "use",
    "when",
    "with",
}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]{1,}")


@dataclass(frozen=True)
class SkillMeta:
    name: str
    description: str
    path: str
    tags: list[str]

    def searchable_text(self) -> str:
        return " ".join([self.name, self.description, self.path, " ".join(self.tags)])


def tokenize(value: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(value.lower()):
        for token in re.split(r"[-_]", raw):
            if len(token) > 1 and token not in STOP_WORDS:
                tokens.append(token)
    return tokens


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip("\"'")
        if key in {"name", "description"}:
            fields[key] = value
    return fields


def infer_name(skill_path: Path, root: Path) -> str:
    try:
        rel = skill_path.parent.relative_to(root)
    except ValueError:
        rel = skill_path.parent
    parts = [part for part in rel.parts if part not in {".system", "skills"}]
    if not parts:
        return skill_path.parent.name
    if len(parts) >= 2 and parts[-2] == "skills":
        return parts[-1]
    if "skills" in parts:
        idx = parts.index("skills")
        return ":".join(parts[:idx] + parts[idx + 1 :])
    return ":".join(parts)


def derive_tags(name: str, description: str, path: Path) -> list[str]:
    weighted = Counter(tokenize(name) * 3 + tokenize(description) + tokenize(str(path)))
    tags = [token for token, _ in weighted.most_common(10)]
    return tags


def discover_skill_files(roots: Iterable[Path]) -> list[tuple[Path, Path]]:
    found: list[tuple[Path, Path]] = []
    for root in roots:
        if not root.exists():
            continue
        for skill_path in root.rglob("SKILL.md"):
            if any(part.startswith(".git") for part in skill_path.parts):
                continue
            found.append((root, skill_path))
    return sorted(found, key=lambda item: str(item[1]))


def build_index(roots: Iterable[Path]) -> dict[str, object]:
    skills: list[SkillMeta] = []
    for root, skill_path in discover_skill_files(roots):
        text = skill_path.read_text(encoding="utf-8", errors="replace")
        fields = parse_frontmatter(text)
        name = fields.get("name") or infer_name(skill_path, root)
        description = fields.get("description", "")
        skills.append(
            SkillMeta(
                name=name,
                description=description,
                path=str(skill_path),
                tags=derive_tags(name, description, skill_path),
            )
        )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_roots": [str(root) for root in roots],
        "body_loaded": False,
        "skill_count": len(skills),
        "skills": [skill.__dict__ for skill in sorted(skills, key=lambda item: item.name)],
    }


def load_index(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_index(index: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def score(query: str, skills: list[dict[str, object]]) -> list[dict[str, object]]:
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return []

    docs = [tokenize(" ".join([str(skill.get("name", "")), str(skill.get("description", "")), " ".join(skill.get("tags", []))])) for skill in skills]
    doc_freq: Counter[str] = Counter()
    for doc in docs:
        doc_freq.update(set(doc))

    ranked: list[dict[str, object]] = []
    total_docs = max(len(docs), 1)
    for skill, doc in zip(skills, docs):
        term_freq = Counter(doc)
        raw_score = 0.0
        for term, query_weight in query_terms.items():
            if not term_freq.get(term):
                continue
            inverse_doc_freq = math.log((1 + total_docs) / (1 + doc_freq[term])) + 1
            raw_score += query_weight * (1 + math.log(term_freq[term])) * inverse_doc_freq
        if raw_score <= 0:
            continue
        ranked.append(
            {
                "score": round(raw_score, 4),
                "name": skill.get("name", ""),
                "description": skill.get("description", ""),
                "path": skill.get("path", ""),
                "tags": skill.get("tags", []),
            }
        )
    return sorted(ranked, key=lambda item: (-float(item["score"]), str(item["name"])))


def command_build(args: argparse.Namespace) -> int:
    roots = tuple(Path(root).expanduser() for root in args.root)
    index = build_index(roots)
    save_index(index, Path(args.index))
    print(
        json.dumps(
            {
                "ok": True,
                "index": str(args.index),
                "skill_count": index["skill_count"],
                "body_loaded": index["body_loaded"],
            },
            sort_keys=True,
        )
    )
    return 0


def command_query(args: argparse.Namespace) -> int:
    index = load_index(Path(args.index))
    ranked = score(args.query, list(index.get("skills", [])))[: args.limit]
    print(json.dumps({"ok": True, "query": args.query, "matches": ranked}, indent=2, sort_keys=True))
    return 0


def command_show(args: argparse.Namespace) -> int:
    index = load_index(Path(args.index))
    skills = list(index.get("skills", []))
    matches = [
        skill
        for skill in skills
        if str(skill.get("name", "")) == args.name or str(skill.get("path", "")) == args.name
    ]
    if not matches:
        ranked = score(args.name, skills)[:1]
        if ranked:
            matches = [ranked[0]]
    if not matches:
        print(json.dumps({"ok": False, "error": "skill not found"}, sort_keys=True), file=sys.stderr)
        return 1
    path = Path(str(matches[0]["path"]))
    body = path.read_text(encoding="utf-8", errors="replace")
    print(body)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", default=os.fspath(DEFAULT_INDEX))
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build a metadata-only skill index.")
    build.add_argument("--root", action="append", default=[os.fspath(root) for root in DEFAULT_ROOTS])
    build.set_defaults(func=command_build)

    query = subparsers.add_parser("query", help="Return top metadata matches for a task.")
    query.add_argument("query")
    query.add_argument("--limit", type=int, default=5)
    query.set_defaults(func=command_query)

    show = subparsers.add_parser("show", help="Read the selected SKILL.md body.")
    show.add_argument("name")
    show.set_defaults(func=command_show)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
