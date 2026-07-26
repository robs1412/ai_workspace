#!/usr/local/bin/python3.13
"""Toy no-API prompt harness for the Family AI Class.

This script does not call any AI service. It scores prompt drafts for useful
signals so students can see how a harness makes an AI workflow repeatable.
"""

from __future__ import annotations


PROMPTS = [
    "Tell me about AI.",
    (
        "Act as a patient tutor. Explain AI to a beginner in 5 bullets. "
        "Include 2 risks and one safe practice exercise."
    ),
    (
        "You are a coding assistant. In this local demo folder, add one button "
        "to index.html and app.js. Do not add dependencies. After editing, tell "
        "me how to verify it at http://127.0.0.1:8000."
    ),
]

RUBRIC = {
    "role": ["act as", "you are"],
    "task": ["explain", "rewrite", "add", "create", "review", "compare"],
    "audience": ["beginner", "student", "family", "audience"],
    "constraints": ["do not", "include", "only", "5 bullets", "one"],
    "output": ["bullets", "table", "checklist", "verify", "exercise"],
}


def score(prompt: str) -> tuple[int, list[str]]:
    text = prompt.lower()
    hits: list[str] = []
    for category, needles in RUBRIC.items():
        if any(needle in text for needle in needles):
            hits.append(category)
    return len(hits), hits


def main() -> int:
    print("Prompt harness: clarity signal check\n")
    for number, prompt in enumerate(PROMPTS, start=1):
        points, hits = score(prompt)
        print(f"Prompt {number}: {points}/5")
        print(f"Signals: {', '.join(hits) if hits else 'none'}")
        print(prompt)
        print("-" * 72)
    print("Lesson: a harness needs inputs, a rubric, output, and a stop condition.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
