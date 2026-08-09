# Corporate Finance Spring 2025

Course-specific workspace for:

- `Corporate Finance Spring 2025`
- instructor: `Aswath Damodaran`
- source playlist: `PLUkh9m2Borqn549nqiEOyFRIvqs4_P3d0`

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

Build the theme, subtheme, and discussion pages:

```bash
python3 ../scripts/build_corporate_finance_course_site.py \
  --course-root .
```

## Outputs

- `raw-material/youtube/transcript-index.json`
- `analysis/themes.json`
- `analysis/subthemes.json`
- `analysis/discussions.json`
- `analysis/course-thesis.md`
- `analysis/session-briefs.md`
- `analysis/themes-and-subthemes.json`
- `analysis/concepts.json`
- `analysis/evidence-map.json`
- `site/index.html`
- `site/course-thesis.html`
- `site/themes.html`
- `site/subthemes.html`
- `site/evidence.html`
- `site/discussions.html`
- `site/sessions.html`
- `site/concepts/index.html`
- `site/concepts/*.html`
