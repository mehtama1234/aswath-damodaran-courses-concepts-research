# Aswath Damodaran Courses Concepts Research

Reusable workspace for transcript-backed concept, theme, and subtheme builds
across multiple Aswath Damodaran courses, with one companion geometric deep
learning course using the same atlas pipeline.

Seeded courses:

- `investment-philosophies-2026/`
- `foundations-of-finance/`
- `valuation-mba-spring-2025/`
- `valuation-undergraduate-spring-2025/`
- `corporate-finance-spring-2025/`
- `ammi-geometric-deep-learning-2022/`

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
- `ammi-geometric-deep-learning-2022` as a companion structured-ML course that stress-tests the same transcript-to-atlas workflow outside the Damodaran corpus

That combined structure should support richer synthesis around societal,
cultural, consumer, institutional, and industrial patterns across the courses,
not just isolated course summaries.

The two newer course additions are now part of the core interpretation path,
not optional extras:

- `valuation-undergraduate-spring-2025` should keep strengthening the
  audience-translation comparison against the MBA valuation course.
- `corporate-finance-spring-2025` should keep strengthening the governance,
  reinvestment, financing, payout, and capital-allocation bridge back into
  valuation and investment philosophy.

The current next-phase target is to deepen the shared interpretive layer across
all five active Damodaran courses so the repository becomes more than a course
archive plus first-pass synthesis. The emphasis should now be on:

- richer theme and subtheme hierarchies within each course
- stronger root synthesis of societal, cultural, consumer, industrial,
  managerial, governance, and market patterns
- clearer cross-course explanation of where ideas align, diverge, simplify, or
  translate by audience
- stronger linkage from transcript-backed course concepts into sector and
  company writeups
- plain-language HTML and JSON artifacts that stay readable while becoming more
  interpretive and more detailed

The durable root objective is written out in:

- `GOAL.md`
- `analysis/project-objective.md`

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
- `ammi-geometric-deep-learning-2022/`: transcript-backed AMMI Geometric Deep Learning course workspace with a richer concept/site layer

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

Build the AMMI Geometric Deep Learning course site:

```bash
python3 scripts/build_ammi_geometric_deep_learning_2022_course_site.py \
  --course-root ammi-geometric-deep-learning-2022
```

Build the root normalized concept atlas:

```bash
python3 scripts/build_root_workspace_artifacts.py
```

Run the downstream applied-layer validators directly:

```bash
python3 scripts/validate_applied_analysis.py
python3 scripts/validate_applied_evidence.py
python3 scripts/validate_root_workspace.py
```

Run the compact root workspace integrity check:

```bash
bash scripts/check_root_workspace.sh
```

Scaffold a new course workspace:

```bash
python3 scripts/scaffold_course_workspace.py \
  --slug valuation-spring-2025 \
  --title "Valuation Spring 2025" \
  --playlist-url "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

This root rebuild command is the default cross-course path. It refreshes, in
order, then runs the downstream applied-layer validators:

- `analysis/course-evidence-index.json`
- `analysis/course-file-evidence-index.json`
- `analysis/normalized-concepts-resolved.json`
- `site/normalized-concepts.html`
- `site/concepts/index.html`
- `site/concepts/*.html`
- `site/cross-course-comparison.html`
- `site/valuation-audience-comparison.html`
- `site/root-synthesis-essay.html`
- `site/root-themes-atlas.html`
- `site/root-themes-registry.html`
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
- `analysis/root-themes-atlas.md`
- `analysis/root-themes-registry.json`

The root sector/company writing scaffold is documented at:

- `analysis/sector-and-company-writeup-framework.md`

The applied downstream writeups are documented at:

- `analysis/applied-analysis-catalog.json`
- `analysis/applied-evidence-registry.json`
- `site/applied-analysis.html`
- `site/applied-evidence.html`

The current applied set spans:

- streaming platforms and Netflix
- enterprise software
- payments infrastructure and Visa
- luxury goods and Hermes
- AI compute infrastructure and Nvidia
- integrated oil majors and ExxonMobil
- branded pharmaceuticals and Merck
- digital asset platforms and Coinbase
- airlines and Southwest Airlines
- office REITs and Boston Properties
- private equity firms and Blackstone
- quick service restaurants and McDonald's
- homebuilders and NVR
- defense primes and Lockheed Martin
- electric utilities and NextEra Energy
- property and casualty insurance and Chubb
- wireless carriers and T-Mobile
- sports betting platforms and DraftKings

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

Keep expanding the shared analytical layer across all active Damodaran courses:

- deepen themes, subthemes, and concepts within each course
- connect newer course additions into the root comparison and synthesis layer
- build richer cross-course interpretation of societal, cultural, consumer,
  industrial, managerial, and market themes
- make the downstream sector and company analysis more explicitly inherit from
  the course-backed concept and theme system
- extend the root site with more cross-course and applied downstream writeups

The root-level cross-course entry points now are:

- `analysis/course-catalog.json`
- `site/index.html`
