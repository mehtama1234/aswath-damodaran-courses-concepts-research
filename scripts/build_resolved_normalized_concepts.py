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


def build(workspace_root: Path) -> dict[str, Any]:
    registry = load_json(workspace_root / "analysis/normalized-concepts.json")
    file_index = load_json(workspace_root / "analysis/course-file-evidence-index.json")
    per_course_lookup = {
        course["slug"]: {item["path"]: item["id"] for item in course.get("items", [])}
        for course in file_index.get("courses", [])
    }

    resolved = {
        "workspace": registry["workspace"],
        "updated_on": registry["updated_on"],
        "description": registry["description"],
        "concepts": [],
        "next_registry_expansions": registry.get("next_registry_expansions", []),
    }

    for concept in registry.get("concepts", []):
        new_concept = {k: v for k, v in concept.items() if k != "courses"}
        new_courses = []
        for course in concept.get("courses", []):
            lookup = per_course_lookup.get(course["slug"], {})
            analysis_ids = [lookup[path] for path in course.get("analysis_refs", []) if path in lookup]
            site_ids = [lookup[path] for path in course.get("site_refs", []) if path in lookup]
            new_course = dict(course)
            new_course["analysis_evidence_ids"] = analysis_ids
            new_course["site_evidence_ids"] = site_ids
            new_courses.append(new_course)
        new_concept["courses"] = new_courses
        resolved["concepts"].append(new_concept)

    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve normalized concepts to canonical file evidence ids.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    args = parser.parse_args()
    workspace_root = args.workspace_root.resolve()
    data = build(workspace_root)
    write_json(workspace_root / "analysis/normalized-concepts-resolved.json", data)


if __name__ == "__main__":
    main()
