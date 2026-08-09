#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def label_for_path(relpath: str) -> str:
    path = Path(relpath)
    parts = path.parts
    if len(parts) >= 2 and parts[0] == "analysis":
        stem = path.stem.replace("-", " ").replace("_", " ").title()
        return f"Analysis: {stem}"
    if len(parts) >= 2 and parts[0] == "site":
        if parts[1] == "index.html":
            return "Site: Main Overview"
        if parts[1] == "course-thesis.html":
            return "Site: Course Thesis"
        if parts[1] == "themes.html":
            return "Site: Themes"
        if parts[1] == "subthemes.html":
            return "Site: Subthemes"
        if parts[1] == "discussions.html":
            return "Site: Discussions"
        if parts[1] == "sessions.html":
            return "Site: Sessions"
        if parts[1] == "concepts" and len(parts) >= 3:
            stem = Path(parts[2]).stem.replace("-", " ").replace("_", " ").title()
            return f"Site Concept: {stem}"
        stem = path.stem.replace("-", " ").replace("_", " ").title()
        return f"Site: {stem}"
    stem = path.stem.replace("-", " ").replace("_", " ").title()
    return stem


def evidence_id(course_slug: str, relpath: str) -> str:
    return f"{course_slug}::{relpath}"


def build(workspace_root: Path) -> dict[str, Any]:
    catalog = load_json(workspace_root / "analysis/course-catalog.json")
    out_courses = []
    for course in catalog["courses"]:
        course_root = workspace_root / course["slug"]
        items = []
        for relpath in course.get("analysis_outputs", []):
            items.append(
                {
                    "id": evidence_id(course["slug"], relpath),
                    "path": relpath,
                    "label": label_for_path(relpath),
                    "kind": "analysis",
                    "href": f"../{course['slug']}/{relpath}",
                }
            )
        for relpath in course.get("site_outputs", []):
            if relpath.endswith("/"):
                rel_dir = Path(relpath)
                abs_dir = course_root / rel_dir
                if abs_dir.is_dir():
                    for file_path in sorted(p for p in abs_dir.rglob("*") if p.is_file()):
                        nested_relpath = file_path.relative_to(course_root).as_posix()
                        items.append(
                            {
                                "id": evidence_id(course["slug"], nested_relpath),
                                "path": nested_relpath,
                                "label": label_for_path(nested_relpath),
                                "kind": "site",
                                "href": f"../{course['slug']}/{nested_relpath}",
                            }
                        )
                continue
            items.append(
                {
                    "id": evidence_id(course["slug"], relpath),
                    "path": relpath,
                    "label": label_for_path(relpath),
                    "kind": "site",
                    "href": f"../{course['slug']}/{relpath}",
                }
            )
        out_courses.append(
            {
                "slug": course["slug"],
                "title": course["title"],
                "items": items,
            }
        )
    return {
        "workspace": catalog["workspace"]["name"],
        "updated_on": catalog["workspace"]["updated_on"],
        "courses": out_courses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a root file evidence index across Damodaran courses.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    args = parser.parse_args()
    workspace_root = args.workspace_root.resolve()
    data = build(workspace_root)
    write_json(workspace_root / "analysis/course-file-evidence-index.json", data)


if __name__ == "__main__":
    main()
