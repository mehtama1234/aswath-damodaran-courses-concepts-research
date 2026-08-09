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
    catalog = load_json(workspace_root / "analysis/course-catalog.json")
    courses_out: list[dict[str, Any]] = []

    for course in catalog["courses"]:
        slug = course["slug"]
        course_root = workspace_root / slug
        transcript_index = load_json(course_root / "raw-material/youtube/transcript-index.json")

        sessions = []
        for record in transcript_index:
          sessions.append(
              {
                  "index": record.get("index"),
                  "id": record.get("id"),
                  "title": record.get("title"),
                  "url": record.get("url"),
                  "transcript_status": record.get("transcript_status"),
                  "word_count": record.get("word_count", 0),
                  "theme_name": record.get("theme_name"),
                  "subtheme_name": record.get("subtheme_name"),
              }
          )

        courses_out.append(
            {
                "slug": slug,
                "title": course["title"],
                "instructor": course.get("instructor"),
                "videos": course.get("videos"),
                "available_transcripts": course.get("available_transcripts"),
                "sessions": sessions,
            }
        )

    return {
        "workspace": catalog["workspace"]["name"],
        "updated_on": catalog["workspace"]["updated_on"],
        "courses": courses_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a root session evidence index across Damodaran courses.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    args = parser.parse_args()
    workspace_root = args.workspace_root.resolve()
    data = build(workspace_root)
    write_json(workspace_root / "analysis/course-evidence-index.json", data)


if __name__ == "__main__":
    main()
