# AMMI Geometric Deep Learning Course - Second Edition (2022)

Course-specific workspace for:

- `AMMI Geometric Deep Learning Course - Second Edition (2022)`
- instructor: `Michael Bronstein, Joan Bruna, Taco Cohen, Petar Veličković, and seminar speakers`
- source playlist: `https://www.youtube.com/watch?v=5c_-KX1sRDQ&list=PLn2-dEmQeTfSLXW8yXP4q_Ii58wFdxb3C`

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

Build the richer course atlas:

```bash
python3 ../scripts/build_ammi_geometric_deep_learning_2022_course_site.py \
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
- `analysis/course-thesis.md`
- `analysis/themes-and-subthemes.json`
- `analysis/concepts.json`
- `analysis/discussions.json`
- `analysis/sessions.json`
- `analysis/evidence-map.json`
- `site/index.html`
- `site/course-thesis.html`
- `site/themes.html`
- `site/subthemes.html`
- `site/discussions.html`
- `site/sessions.html`
- `site/concepts/`
