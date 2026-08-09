# Foundations of Finance

Course-specific workspace for:

- `Foundations of Finance`
- instructor: `Aswath Damodaran`
- source playlist: `https://www.youtube.com/playlist?list=PLUkh9m2BorqndWimijiJ-VCAXjJUrzJQU`

## Commands

Run transcript capture from inside this folder:

```bash
python3 ../scripts/download_youtube_playlist_transcripts.py \
  --course-root . \
  --manifest raw-material/youtube/course-manifest.json
```

Rebuild transcript text and indexes from downloaded files:

```bash
python3 ../scripts/download_youtube_playlist_transcripts.py \
  --course-root . \
  --manifest raw-material/youtube/course-manifest.json \
  --summary-only
```

Build the first-pass session inventory:

```bash
python3 ../scripts/build_course_session_inventory.py \
  --course-root .
```

Build the reader-facing course site from the transcript-backed theme map:

```bash
python3 ../scripts/build_foundations_course_site.py \
  --course-root .
```

## Intended next layers

- transcript-backed session map
- themes and subthemes
- normalized concepts that can roll into the root registry
- reader-facing HTML outputs

## Expected outputs

- `raw-material/youtube/transcript-index.json`
- `raw-material/youtube/summary.json`
- `analysis/session-inventory.md`
- `analysis/session-briefs.md`
- `analysis/sessions.json`
- `analysis/discussions.json`
- `analysis/themes-and-subthemes.json`
- `analysis/`
- `site/`
