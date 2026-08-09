# Valuation Undergraduate Spring 2025

Course-specific workspace for:

- `Valuation Undergraduate Spring 2025`
- instructor: `Aswath Damodaran`
- source playlist: `https://www.youtube.com/playlist?list=PLUkh9m2BorqkYrFjNdut81IIcYdLfgqNd`

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

- transcript-backed session map
- themes and subthemes
- normalized concepts that can roll into the root registry
- reader-facing HTML outputs

## Expected outputs

- `raw-material/youtube/transcript-index.json`
- `raw-material/youtube/summary.json`
- `analysis/session-briefs.md`
- `analysis/sessions.json`
- `analysis/discussions.json`
- `analysis/`
- `site/themes.html`
- `site/subthemes.html`
- `site/discussions.html`
- `site/sessions.html`
- `site/`
