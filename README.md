# Aswath Damodaran Courses Concepts Research

Reusable workspace for transcript-backed concept, theme, and subtheme builds
across multiple Aswath Damodaran courses.

Seeded courses:

- `investment-philosophies-2026/`
- `foundations-of-finance/`
- `valuation-mba-spring-2025/`
- `valuation-undergraduate-spring-2025/`
- `corporate-finance-spring-2025/`

The root is intentionally generic. Each course subfolder should carry its own:

- raw YouTube manifests and transcript assets
- cleaned transcript text and cue JSON
- analysis outputs for concepts, themes, subthemes, and evidence
- site or course exports

The broader goal is cross-course, not just per-course completion. The active
workspace is meant to connect:

- `foundations-of-finance` as the first-principles base layer
- `investment-philosophies-2026` as the investor-framework and market-behavior layer
- `valuation-undergraduate-spring-2025` and `valuation-mba-spring-2025` as the audience-comparison valuation pair
- `corporate-finance-spring-2025` as the operating, financing, governance, and capital-allocation layer

That combined structure should support richer synthesis around societal,
cultural, consumer, institutional, and industrial patterns across the courses,
not just isolated course summaries.

## Layout

- `scripts/`: reusable root-level tooling
- `templates/`: manifest templates for new Damodaran course folders
- `analysis/`: root-level workspace catalog and future cross-course artifacts
- `site/`: root-level HTML index across courses
- `investment-philosophies-2026/`: first course-specific workspace
- `foundations-of-finance/`: introductory finance course with partial transcript corpus, theme map, and reader-facing site
- `valuation-mba-spring-2025/`: full transcript corpus captured with rich theme, evidence, discussion, session, and 37-concept HTML atlas
- `valuation-undergraduate-spring-2025/`: full transcript corpus captured, hand-built theme map added, concept and evidence layer built, reader-facing site pages built
- `corporate-finance-spring-2025/`: transcript-backed Corporate Finance Spring 2025 workspace

## Transcript workflow

The transcript extractor is manifest-driven and designed to run inside a
course subfolder.

Example:

```bash
python3 ../scripts/download_youtube_playlist_transcripts.py \
  --course-root . \
  --manifest raw-material/youtube/course-manifest.json
```

Rebuild clean transcript text and indexes from files already on disk:

```bash
python3 ../scripts/download_youtube_playlist_transcripts.py \
  --course-root . \
  --manifest raw-material/youtube/course-manifest.json \
  --summary-only
```

Build the Corporate Finance theme/subtheme/discussion site:

```bash
python3 ../scripts/build_corporate_finance_course_site.py \
  --course-root .
```

Build the Foundations of Finance course site:

```bash
python3 scripts/build_foundations_course_site.py \
  --course-root foundations-of-finance
```

Build the root normalized concept atlas:

```bash
python3 scripts/build_root_workspace_artifacts.py
```

Scaffold a new course workspace:

```bash
python3 scripts/scaffold_course_workspace.py \
  --slug valuation-spring-2025 \
  --title "Valuation Spring 2025" \
  --playlist-url "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

This root rebuild command is the default cross-course path. It refreshes, in
order:

- `analysis/course-evidence-index.json`
- `analysis/course-file-evidence-index.json`
- `analysis/normalized-concepts-resolved.json`
- `site/normalized-concepts.html`
- `site/concepts/index.html`
- `site/concepts/*.html`
- `site/cross-course-comparison.html`
- `site/valuation-audience-comparison.html`
- `site/root-synthesis-essay.html`
- `site/sector-and-company-writeup-framework.html`
- `site/applied-analysis.html`
- `site/applied-evidence.html`
- `site/streaming-platforms-sector-brief.html`
- `site/netflix-company-brief.html`
- `site/enterprise-software-sector-brief.html`
- `site/costco-company-brief.html`

The practical source of truth for rendered root concept pages is now the
resolved registry at `analysis/normalized-concepts-resolved.json`, which keeps
canonical evidence ids while preserving fallback path references from
`analysis/normalized-concepts.json`.

The root workspace objective is documented at:

- `analysis/project-objective.md`

The root sector/company writing scaffold is documented at:

- `analysis/sector-and-company-writeup-framework.md`

The first applied downstream writeups are documented at:

- `analysis/applied-analysis-catalog.json`
- `analysis/applied-evidence-registry.json`
- `analysis/streaming-platforms-sector-brief.md`
- `analysis/netflix-company-brief.md`
- `analysis/enterprise-software-sector-brief.md`
- `analysis/costco-company-brief.md`

## Expected per-course structure

Each course subfolder should follow this shape:

- `raw-material/youtube/course-manifest.json`
- `raw-material/youtube/playlists/`
- `raw-material/youtube/metadata/<course-slug>/`
- `raw-material/youtube/transcripts/<course-slug>/raw-vtt/`
- `raw-material/youtube/transcripts/<course-slug>/clean/`
- `raw-material/youtube/transcripts/<course-slug>/cues/`
- `raw-material/youtube/transcript-index.json`
- `raw-material/youtube/summary.json`
- `analysis/`
- `site/`

## Next step

Run the transcript downloader inside each course folder, then build deeper
Damodaran-specific theme, subtheme, concept, and discussion layers on top of
that transcript index.

The root-level cross-course entry points now are:

- `analysis/course-catalog.json`
- `site/index.html`
