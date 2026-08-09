# Investment Philosophies 2026

Course-specific workspace for:

- `Investment Philosophies - The 2026 Edition`
- instructor: `Aswath Damodaran`

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

## Intended next layers

- transcript-backed investment concepts
- recurring Damodaran themes
- subthemes across valuation, markets, narrative, pricing, and portfolio logic
- reader-facing course/site exports

## Current outputs

- course objective: `analysis/project-objective.md`
- analysis overview: `analysis/README.md`
- course thesis source: `analysis/course-thesis.md`
- concept registry: `analysis/concepts.json`
- session map: `analysis/session-briefs.md`
- session JSON: `analysis/sessions.json`
- discussion JSON: `analysis/discussions.json`
- theme tree: `analysis/themes-and-subthemes.json`
- HTML overview: `site/index.html`
- HTML themes: `site/themes.html`
- HTML subthemes: `site/subthemes.html`
- HTML discussions: `site/discussions.html`
- HTML sessions: `site/sessions.html`
- HTML concept atlas: `site/concepts/`
- HTML concept index: `site/concepts/index.html`
