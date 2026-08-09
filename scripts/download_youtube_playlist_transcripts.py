#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, check=check)


def dump_json(cmd: list[str], cwd: Path) -> dict[str, Any]:
    return json.loads(subprocess.check_output(cmd, cwd=cwd, text=True))


def stable_playlist_manifest(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    out.pop("epoch", None)
    return out


def video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def course_paths(course_root: Path, slug: str) -> dict[str, Path]:
    raw = course_root / "raw-material" / "youtube"
    base = raw / "transcripts" / slug
    paths = {
        "raw_root": raw,
        "base": base,
        "raw_vtt": base / "raw-vtt",
        "clean": base / "clean",
        "cues": base / "cues",
        "metadata": raw / "metadata" / slug,
        "playlists": raw / "playlists",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def normalize_manifest_videos(manifest: dict[str, Any], playlist_data: dict[str, Any]) -> list[dict[str, Any]]:
    explicit_videos = manifest.get("videos")
    if explicit_videos:
        videos = []
        for index, video in enumerate(explicit_videos, 1):
            videos.append(
                {
                    "index": int(video.get("index", index)),
                    "id": video["id"],
                    "title": video.get("title") or video.get("expected_title") or f"Video {index}",
                    "url": video.get("url") or video_url(video["id"]),
                }
            )
        return videos

    entries = playlist_data.get("entries", [])
    videos = []
    for index, entry in enumerate(entries, 1):
        video_id = entry.get("id")
        if not video_id:
            continue
        videos.append(
            {
                "index": index,
                "id": video_id,
                "title": entry.get("title") or f"Video {index}",
                "url": entry.get("url") or video_url(video_id),
            }
        )
    return videos


def capture_playlist_manifest(course_root: Path, manifest: dict[str, Any], slug: str) -> dict[str, Any]:
    playlist_url = manifest.get("playlist_url")
    channel_url = manifest.get("channel_url")
    source_url = playlist_url or channel_url
    if not source_url:
        raise ValueError("Manifest must include playlist_url or channel_url")
    data = stable_playlist_manifest(
        dump_json(["yt-dlp", "--flat-playlist", "--dump-single-json", source_url], cwd=course_root)
    )
    out = course_paths(course_root, slug)["playlists"] / f"{slug}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def download_video(course_root: Path, slug: str, index: int, video_id: str) -> None:
    paths = course_paths(course_root, slug)
    output_tpl = str(paths["raw_vtt"] / f"{index:03d}-%(id)s-%(title).120B.%(ext)s")
    result = run(
        [
            "yt-dlp",
            "--skip-download",
            "--write-info-json",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "en,en-US,en-orig",
            "--sub-format",
            "vtt",
            "--sleep-requests",
            "1",
            "--sleep-interval",
            "1",
            "-o",
            output_tpl,
            video_url(video_id),
        ],
        cwd=course_root,
        check=False,
    )
    for info in paths["raw_vtt"].glob(f"{index:03d}-{video_id}-*.info.json"):
        target = paths["metadata"] / info.name
        if target.exists():
            target.unlink()
        info.replace(target)
    print(f"{index:03d} {video_id} rc={result.returncode}")


def parse_timestamp(value: str) -> float:
    hours, minutes, rest = value.split(":")
    seconds = float(rest)
    return int(hours) * 3600 + int(minutes) * 60 + seconds


def clean_line(line: str) -> str:
    line = re.sub(r"<[^>]+>", "", line)
    line = (
        line.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    return re.sub(r"\s+", " ", line).strip()


def parse_vtt(path: Path) -> tuple[str, list[dict[str, Any]]]:
    cues: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    text_lines: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:")):
            continue
        if "-->" in line:
            start, end = [part.strip().split(" ")[0] for part in line.split("-->", 1)]
            current = {
                "start": start,
                "end": end,
                "start_seconds": parse_timestamp(start),
                "end_seconds": parse_timestamp(end),
                "text": [],
            }
            cues.append(current)
            continue
        if re.match(r"^\d+$", line):
            continue
        cleaned = clean_line(line)
        if not cleaned:
            continue
        if current is not None:
            if not current["text"] or current["text"][-1] != cleaned:
                current["text"].append(cleaned)
        text_lines.append(cleaned)

    compact_cues: list[dict[str, Any]] = []
    for cue in cues:
        joined = " ".join(cue["text"]).strip()
        if not joined:
            continue
        compact_cues.append({**cue, "text": joined})

    deduped: list[str] = []
    for line in text_lines:
        if not deduped or deduped[-1] != line:
            deduped.append(line)
    return "\n".join(deduped).strip() + "\n", compact_cues


def choose_vtt(course_root: Path, slug: str, index: int, video_id: str) -> Path | None:
    candidates = sorted(course_paths(course_root, slug)["raw_vtt"].glob(f"{index:03d}-{video_id}-*.vtt"))
    if not candidates:
        return None
    ranks = []
    for item in candidates:
        name = item.name
        if name.endswith(".en-US.vtt"):
            rank = 0
        elif name.endswith(".en.vtt"):
            rank = 1
        elif name.endswith(".en-orig.vtt"):
            rank = 2
        else:
            rank = 9
        ranks.append((rank, item))
    return sorted(ranks, key=lambda pair: (pair[0], pair[1].name))[0][1]


def rebuild_index(course_root: Path, manifest: dict[str, Any], slug: str, videos: list[dict[str, Any]]) -> None:
    paths = course_paths(course_root, slug)
    records = []
    for video in videos:
        index = int(video["index"])
        video_id = video["id"]
        vtt = choose_vtt(course_root, slug, index, video_id)
        if vtt is None:
            records.append(
                {
                    "id": video_id,
                    "index": index,
                    "expected_title": video["title"],
                    "title": video["title"],
                    "url": video.get("url") or video_url(video_id),
                    "transcript_status": "missing",
                    "word_count": 0,
                    "cue_count": 0,
                }
            )
            continue

        clean_text, cues = parse_vtt(vtt)
        clean_path = paths["clean"] / f"{index:03d}-{video_id}.txt"
        cue_path = paths["cues"] / f"{index:03d}-{video_id}.json"
        clean_path.write_text(clean_text, encoding="utf-8")
        cue_path.write_text(json.dumps(cues, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        meta_files = sorted(paths["metadata"].glob(f"{index:03d}-{video_id}-*.info.json"))
        metadata = json.loads(meta_files[0].read_text(encoding="utf-8")) if meta_files else {}
        records.append(
            {
                "id": video_id,
                "slug": slug,
                "index": index,
                "expected_title": video["title"],
                "title": metadata.get("title", video["title"]),
                "url": video.get("url") or video_url(video_id),
                "duration": metadata.get("duration"),
                "channel": metadata.get("channel"),
                "clean_txt": str(clean_path.relative_to(course_root)),
                "cue_json": str(cue_path.relative_to(course_root)),
                "raw_vtt": str(vtt.relative_to(course_root)),
                "word_count": len(clean_text.split()),
                "cue_count": len(cues),
                "transcript_status": "available",
            }
        )

    index_output = paths["raw_root"] / "transcript-index.json"
    summary_output = paths["raw_root"] / "summary.json"
    index_output.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {
        "slug": slug,
        "title": manifest["title"],
        "videos": len(videos),
        "available_transcripts": sum(r["transcript_status"] == "available" for r in records),
        "total_words": sum(r.get("word_count", 0) for r in records),
        "total_cues": sum(r.get("cue_count", 0) for r in records),
    }
    summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"indexed {summary['available_transcripts']}/{summary['videos']} transcripts, "
        f"{summary['total_words']} words"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-root", default=".")
    parser.add_argument("--manifest", default="raw-material/youtube/course-manifest.json")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    course_root = Path(args.course_root).resolve()
    manifest_path = course_root / args.manifest if not Path(args.manifest).is_absolute() else Path(args.manifest)
    manifest = load_manifest(manifest_path)
    slug = manifest["slug"]

    playlist_data = capture_playlist_manifest(course_root, manifest, slug)
    videos = normalize_manifest_videos(manifest, playlist_data)

    if not args.summary_only:
        for video in videos:
            download_video(course_root, slug, int(video["index"]), video["id"])

    rebuild_index(course_root, manifest, slug, videos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
