#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_KEYS = {"title", "kind", "status", "evidence_grade", "scope", "last_verified"}
ALLOWED_GRADES = {
    "structural",
    "documented",
    "source-verified",
    "test-verified",
    "primary-law",
    "project-decision",
    "researching",
}
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
SHA_PERMALINK = re.compile(r"https://github\.com/frappe/[^/]+/(?:blob|tree)/[0-9a-f]{40}(?:/|\b)")
SHA_BLOB_WITH_LINE = re.compile(
    r"https://github\.com/frappe/[^/]+/blob/[0-9a-f]{40}/[^\s)]+#L\d+(?:-L\d+)?"
)
OFFICIAL_DOCS = re.compile(r"https://docs\.frappe\.io/")
PRIMARY_LAW_SOURCE = re.compile(
    r"https://(?:e-sbirka\.gov\.cz|www\.mfcr\.cz|financnisprava\.gov\.cz|eur-lex\.europa\.eu)/"
)
REFERENCE_HEADINGS = {"## Direct answer", "## Verification", "## Source map"}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def internal_targets(path: Path, text: str) -> set[Path]:
    targets: set[Path] = set()
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        if resolved.suffix == ".md" and resolved.is_relative_to(ROOT):
            targets.add(resolved)
    return targets


def main() -> int:
    errors: list[str] = []
    graph: dict[Path, set[Path]] = {}
    notes = sorted(ROOT.rglob("*.md"))

    for path in notes:
        text = path.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        missing = REQUIRED_KEYS - set(meta)
        if missing:
            errors.append(f"{path.relative_to(ROOT)}: missing metadata {sorted(missing)}")
        grade = meta.get("evidence_grade")
        if grade and grade not in ALLOWED_GRADES:
            errors.append(f"{path.relative_to(ROOT)}: invalid evidence_grade '{grade}'")
        if meta.get("status") == "verified":
            errors.append(f"{path.relative_to(ROOT)}: ambiguous status 'verified' is prohibited")
        if grade in {"source-verified", "test-verified"} and not SHA_PERMALINK.search(text):
            errors.append(f"{path.relative_to(ROOT)}: {grade} note lacks an immutable Frappe GitHub permalink")
        if grade in {"source-verified", "test-verified"}:
            if not SHA_BLOB_WITH_LINE.search(text):
                errors.append(f"{path.relative_to(ROOT)}: {grade} note lacks a pinned source line anchor")
            if not OFFICIAL_DOCS.search(text):
                errors.append(f"{path.relative_to(ROOT)}: {grade} note lacks an official Frappe documentation link")
            missing_headings = sorted(REFERENCE_HEADINGS - set(text.splitlines()))
            if missing_headings:
                errors.append(
                    f"{path.relative_to(ROOT)}: {grade} note lacks required headings {missing_headings}"
                )
        if grade == "primary-law":
            if not PRIMARY_LAW_SOURCE.search(text):
                errors.append(f"{path.relative_to(ROOT)}: primary-law note lacks an official legal source")
            missing_headings = sorted(REFERENCE_HEADINGS - set(text.splitlines()))
            if missing_headings:
                errors.append(
                    f"{path.relative_to(ROOT)}: primary-law note lacks required headings {missing_headings}"
                )

        graph[path] = internal_targets(path, text)
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link '{target}'")

    entry = ROOT / "INDEX.md"
    reachable: set[Path] = set()
    pending = [entry]
    while pending:
        current = pending.pop()
        if current in reachable:
            continue
        reachable.add(current)
        pending.extend(graph.get(current, set()) - reachable)

    for path in notes:
        if path not in reachable:
            errors.append(f"{path.relative_to(ROOT)}: orphaned from root INDEX.md")

    if errors:
        print("KB validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"KB validation passed: {len(notes)} notes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
