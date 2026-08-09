#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_INSTRUCTOR = "Aswath Damodaran"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def build_manifest(
    slug: str,
    title: str,
    instructor: str,
    playlist_url: str,
    channel_url: str,
    source_note: str,
) -> dict:
    return {
        "slug": slug,
        "title": title,
        "instructor": instructor,
        "playlist_url": playlist_url,
        "channel_url": channel_url,
        "source_note": source_note,
        "videos": [],
    }


def build_readme(slug: str, title: str, instructor: str, playlist_url: str) -> str:
    playlist_line = f"- source playlist: `{playlist_url}`\n" if playlist_url else ""
    return f"""# {title}

Course-specific workspace for:

- `{title}`
- instructor: `{instructor}`
{playlist_line}
## Commands

Run transcript capture from inside this folder:

```bash
python3 ../scripts/download_youtube_playlist_transcripts.py \\
  --course-root . \\
  --manifest raw-material/youtube/course-manifest.json
```

Rebuild transcript text and indexes from downloaded files:

```bash
python3 ../scripts/download_youtube_playlist_transcripts.py \\
  --course-root . \\
  --manifest raw-material/youtube/course-manifest.json \\
  --summary-only
```

## Intended next layers

- transcript-backed session map
- themes and subthemes
- normalized concepts that can roll into the root registry
- reader-facing HTML outputs

## Expected outputs

- `raw-material/youtube/transcript-index.json`
- `raw-material/youtube/summary.json`
- `analysis/`
- `site/`
"""


def build_analysis_readme(title: str) -> str:
    return f"""# {title} Analysis

This folder is for transcript-backed synthesis artifacts for the course:

- session briefs
- themes
- subthemes
- concepts
- evidence notes
"""


def ensure_dirs(course_root: Path, slug: str) -> None:
    dirs = [
        course_root / "analysis",
        course_root / "site",
        course_root / "raw-material" / "youtube" / "playlists",
        course_root / "raw-material" / "youtube" / "metadata" / slug,
        course_root / "raw-material" / "youtube" / "transcripts" / slug / "raw-vtt",
        course_root / "raw-material" / "youtube" / "transcripts" / slug / "clean",
        course_root / "raw-material" / "youtube" / "transcripts" / slug / "cues",
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)


def create_course_workspace(
    workspace_root: Path,
    slug: str,
    title: str,
    instructor: str,
    playlist_url: str,
    channel_url: str,
    source_note: str,
    overwrite: bool,
) -> Path:
    course_root = workspace_root / slug
    if course_root.exists() and not overwrite:
        raise FileExistsError(f"{course_root} already exists. Use --overwrite to refresh scaffold files.")

    ensure_dirs(course_root, slug)
    write_json(
        course_root / "raw-material" / "youtube" / "course-manifest.json",
        build_manifest(slug, title, instructor, playlist_url, channel_url, source_note),
    )
    write_text(course_root / "README.md", build_readme(slug, title, instructor, playlist_url))
    write_text(course_root / "analysis" / "README.md", build_analysis_readme(title))
    write_text(course_root / "site" / ".gitkeep", "")
    return course_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new Damodaran course workspace.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    parser.add_argument("--slug", required=True, help="Course folder slug, e.g. valuation-spring-2025.")
    parser.add_argument("--title", required=True, help="Reader-facing course title.")
    parser.add_argument(
        "--instructor",
        default=DEFAULT_INSTRUCTOR,
        help="Instructor name stored in the manifest and README.",
    )
    parser.add_argument(
        "--playlist-url",
        default="",
        help="YouTube playlist URL for the course.",
    )
    parser.add_argument(
        "--channel-url",
        default="https://www.youtube.com/@AswathDamodaranonValuation",
        help="YouTube channel URL for the course source.",
    )
    parser.add_argument(
        "--source-note",
        default="Scaffolded course workspace; verify playlist ordering and transcript coverage before analysis.",
        help="Short note stored in the manifest.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow scaffold files to be rewritten if the target folder already exists.",
    )
    args = parser.parse_args()

    course_root = create_course_workspace(
        workspace_root=args.workspace_root.resolve(),
        slug=args.slug,
        title=args.title,
        instructor=args.instructor,
        playlist_url=args.playlist_url,
        channel_url=args.channel_url,
        source_note=args.source_note,
        overwrite=args.overwrite,
    )
    print(f"Created course workspace scaffold at {course_root}")


if __name__ == "__main__":
    main()
