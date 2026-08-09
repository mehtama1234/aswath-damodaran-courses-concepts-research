#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_markdown(title: str, brief_type: str) -> str:
    subject_word = "sector" if brief_type == "sector" else "company"
    return f"""# {title}

## {subject_word.title()} Thesis

Write the plain-English thesis here.

## {"Customer And Demand Layer" if brief_type == "sector" else "Business Model And Revenue Logic"}

Explain the core demand, business-model, and usage behavior here.

## Market Narrative

Explain the dominant market story, what the market is excited about, and where
the story may outrun the economics.

## {"Industry Structure" if brief_type == "sector" else "Customer Behavior And Habit Formation"}

Explain the operating system, competitive structure, and where fit matters.

## {"Reinvestment And Capital Allocation" if brief_type == "sector" else "Margin, Reinvestment, And Capital Allocation"}

Explain what has to be reinvested, how growth is funded, and where capital
allocation quality matters.

## Risk And Constraints

Write the risk, fit, ownership, and constraint logic here.

## Valuation Framing

Explain how a Damodaran-style analysis would translate the story into explicit
assumptions rather than stopping at category language.

## Root Concept Links

The most useful root Damodaran concepts for this {subject_word} are:

- [Valuation](concepts/valuation.html)
- [Narrative versus numbers](concepts/narrative-versus-numbers.html)
- [Fit and constraints](concepts/fit-and-constraints.html)

The most useful root comparison and synthesis pages are:

- [Root synthesis essay](root-synthesis-essay.html)
- [Cross-course comparison](cross-course-comparison.html)
- [Normalized concepts](normalized-concepts.html)

## Damodaran Evidence Anchors

The most important transcript-backed root evidence layers behind this brief are:

- [Valuation](concepts/valuation.html): explain why it matters here. Source trail:
  add named course-level sources here.
- [Narrative versus numbers](concepts/narrative-versus-numbers.html): explain
  why it matters here. Source trail: add named course-level sources here.
- [Fit and constraints](concepts/fit-and-constraints.html): explain why it
  matters here. Source trail: add named course-level sources here.

## Why This {"Sector" if brief_type == "sector" else "Company"} Matters

Explain why this is a good applied Damodaran test case.
"""


def build_catalog_entry(slug: str, title: str, brief_type: str) -> dict:
    return {
        "id": slug,
        "title": title,
        "type": brief_type,
        "status": "stub-created",
        "focus": "Replace this with the one-sentence focus of the brief.",
        "site_lead": "Replace this with a reader-facing lead for the generated page.",
        "analysis_source": f"analysis/{slug}.md",
        "site_output": f"site/{slug}.html",
        "evidence_registry_ref": {
            "brief_id": slug,
            "registry_path": "analysis/applied-evidence-registry.json",
            "site_page": "site/applied-evidence.html",
        },
        "root_concepts": [
            {"id": "valuation", "title": "Valuation", "href": "site/concepts/valuation.html"},
            {"id": "narrative-versus-numbers", "title": "Narrative Versus Numbers", "href": "site/concepts/narrative-versus-numbers.html"},
            {"id": "fit-and-constraints", "title": "Fit And Constraints", "href": "site/concepts/fit-and-constraints.html"},
        ],
        "root_pages": [
            "site/root-synthesis-essay.html",
            "site/cross-course-comparison.html",
            "site/normalized-concepts.html",
        ],
        "why_it_exists": "Replace this with why the brief belongs in the applied layer.",
    }


def build_evidence_entry(slug: str, title: str) -> dict:
    return {
        "brief_id": slug,
        "brief_title": title,
        "brief_href": f"site/{slug}.html",
        "anchors": [
            {
                "label": "Valuation",
                "root_href": "site/concepts/valuation.html",
                "why_it_matters": "Replace this with why valuation matters for the brief.",
                "source_trail": [
                    "add-course-slug::named source trail",
                ],
            },
            {
                "label": "Narrative Versus Numbers",
                "root_href": "site/concepts/narrative-versus-numbers.html",
                "why_it_matters": "Replace this with why narrative-versus-numbers matters for the brief.",
                "source_trail": [
                    "add-course-slug::named source trail",
                ],
            },
            {
                "label": "Fit And Constraints",
                "root_href": "site/concepts/fit-and-constraints.html",
                "why_it_matters": "Replace this with why fit-and-constraints matters for the brief.",
                "source_trail": [
                    "add-course-slug::named source trail",
                ],
            },
        ],
    }


def ensure_unique(items: list[dict], key: str, value: str) -> None:
    if any(item.get(key) == value for item in items):
        raise ValueError(f"{value} already exists in registry key {key}.")


def scaffold(workspace_root: Path, slug: str, title: str, brief_type: str, dry_run: bool, overwrite: bool) -> None:
    analysis_path = workspace_root / "analysis" / f"{slug}.md"
    catalog_path = workspace_root / "analysis" / "applied-analysis-catalog.json"
    evidence_path = workspace_root / "analysis" / "applied-evidence-registry.json"

    catalog = read_json(catalog_path)
    evidence = read_json(evidence_path)

    if not overwrite:
        ensure_unique(catalog["analyses"], "id", slug)
        ensure_unique(evidence["briefs"], "brief_id", slug)
        if analysis_path.exists():
            raise FileExistsError(f"{analysis_path} already exists. Use --overwrite to replace it.")

    catalog_entry = build_catalog_entry(slug, title, brief_type)
    evidence_entry = build_evidence_entry(slug, title)
    markdown = build_markdown(title, brief_type)

    if dry_run:
        print(f"[dry-run] would write {analysis_path}")
        print(f"[dry-run] would add catalog entry {slug} to {catalog_path}")
        print(f"[dry-run] would add evidence entry {slug} to {evidence_path}")
        return

    if analysis_path.exists() and overwrite:
        analysis_path.unlink()

    catalog["analyses"] = [item for item in catalog["analyses"] if item.get("id") != slug] + [catalog_entry]
    evidence["briefs"] = [item for item in evidence["briefs"] if item.get("brief_id") != slug] + [evidence_entry]

    write_text(analysis_path, markdown)
    write_json(catalog_path, catalog)
    write_json(evidence_path, evidence)
    print(f"Scaffolded applied {brief_type} brief at {analysis_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new applied sector or company brief.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    parser.add_argument("--slug", required=True, help="Slug for the brief, e.g. payments-infrastructure-sector-brief.")
    parser.add_argument("--title", required=True, help="Reader-facing brief title.")
    parser.add_argument("--type", required=True, choices=["sector", "company"], help="Applied brief type.")
    parser.add_argument("--dry-run", action="store_true", help="Preview the scaffold changes without writing files.")
    parser.add_argument("--overwrite", action="store_true", help="Allow an existing stub entry to be replaced.")
    args = parser.parse_args()
    scaffold(args.workspace_root.resolve(), args.slug, args.title, args.type, args.dry_run, args.overwrite)


if __name__ == "__main__":
    main()
