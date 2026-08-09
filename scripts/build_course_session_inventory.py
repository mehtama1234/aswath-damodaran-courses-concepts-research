#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def format_duration(seconds: int | None) -> str:
    if not seconds:
        return "-"
    minutes, remainder = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def build_inventory(course_root: Path) -> str:
    manifest = load_json(course_root / "raw-material" / "youtube" / "course-manifest.json")
    summary = load_json(course_root / "raw-material" / "youtube" / "summary.json")
    records = load_json(course_root / "raw-material" / "youtube" / "transcript-index.json")

    lines = [
        f"# {manifest['title']} Session Inventory",
        "",
        "Transcript-backed session map for first-pass analysis.",
        "",
        f"- instructor: `{manifest.get('instructor', '')}`",
        f"- playlist: `{manifest.get('playlist_url', '')}`",
        f"- videos: `{summary.get('videos', 0)}`",
        f"- transcripts available: `{summary.get('available_transcripts', 0)}`",
        f"- total words: `{summary.get('total_words', 0):,}`",
        f"- total cues: `{summary.get('total_cues', 0):,}`",
        "",
        "## Sessions",
        "",
        "| # | Title | Duration | Words | Cues | Transcript |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for record in records:
        title = record.get("title") or record.get("expected_title") or f"Session {record.get('index', '')}"
        duration = format_duration(record.get("duration"))
        words = f"{record.get('word_count', 0):,}"
        cues = f"{record.get('cue_count', 0):,}"
        transcript = f"`{record.get('clean_txt', '-')}`"
        lines.append(
            f"| {record.get('index', '')} | {title} | {duration} | {words} | {cues} | {transcript} |"
        )

    lines.extend(
        [
            "",
            "## Use",
            "",
            "- group sessions into major valuation arcs before writing themes",
            "- spot unusually dense sessions for deeper concept extraction",
            "- trace where valuation moves from framing, to inputs, to pricing, to options, to control",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a markdown session inventory for a course transcript corpus.")
    parser.add_argument(
        "--course-root",
        type=Path,
        required=True,
        help="Path to the course workspace root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path. Defaults to analysis/session-inventory.md within the course root.",
    )
    args = parser.parse_args()

    course_root = args.course_root.resolve()
    output = args.output.resolve() if args.output else course_root / "analysis" / "session-inventory.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_inventory(course_root), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
