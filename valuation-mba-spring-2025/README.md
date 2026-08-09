# Valuation MBA Spring 2025

Course-specific workspace for:

- `Valuation MBA Spring 2025`
- instructor: `Aswath Damodaran`
- source playlist: `https://www.youtube.com/playlist?list=PLUkh9m2BorqkgpNyRpP-NL3BS4yvFabXk`

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

Session briefs are maintained at:

```text
analysis/session-briefs.md
```

Build the rich course overview, thesis, theme, evidence, discussion, session, and concept-atlas pages:

```bash
python3 ../scripts/build_valuation_course_site.py \
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
- `analysis/themes-and-subthemes.json`
- `analysis/sessions.json`
- `analysis/themes.json`
- `analysis/subthemes.json`
- `analysis/discussions.json`
- `analysis/concepts.json`
- `analysis/evidence-map.json`
- `analysis/course-thesis.md`
- `site/index.html`
- `site/course-thesis.html`
- `site/themes.html`
- `site/subthemes.html`
- `site/evidence.html`
- `site/discussions.html`
- `site/sessions.html`
- `site/concepts/index.html`
- `site/concepts/*.html`
- `analysis/`
- `site/`
