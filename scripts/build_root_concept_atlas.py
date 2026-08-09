#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value))


def slug_to_label(value: str) -> str:
    return value.replace("-", " ").title()


def root_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{esc(title)}</title>
    <style>
      :root {{
        --bg: #f4f1ea;
        --panel: #fffdf8;
        --panel-alt: #f8f4ed;
        --ink: #1f1f1b;
        --muted: #605b52;
        --line: #d7d0c4;
        --accent: #0b6b6f;
        --accent-soft: #d8ecec;
        --shadow: 0 16px 40px rgba(32, 26, 16, 0.08);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--ink);
        line-height: 1.6;
      }}
      .page {{
        width: min(1180px, calc(100% - 24px));
        margin: 0 auto;
        padding: 24px 0 56px;
      }}
      .back {{
        display: inline-flex;
        align-items: center;
        min-height: 36px;
        padding: 0 12px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel);
        color: var(--muted);
        text-decoration: none;
        margin-bottom: 18px;
      }}
      .hero, .card, .section, .takeaway {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: var(--shadow);
      }}
      .hero, .section {{
        padding: 24px;
      }}
      .eyebrow {{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
      }}
      h1, h2, h3 {{
        margin: 0;
        font-weight: 700;
      }}
      h1 {{
        margin-top: 12px;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.02;
      }}
      h2 {{
        font-size: 1.3rem;
        margin-bottom: 10px;
      }}
      h3 {{
        font-size: 1rem;
        margin-bottom: 8px;
      }}
      p {{
        margin: 0;
        color: var(--muted);
      }}
      .lead {{
        color: var(--ink);
        font-size: 1.05rem;
        max-width: 78ch;
      }}
      .meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }}
      .chip {{
        display: inline-flex;
        align-items: center;
        min-height: 30px;
        padding: 0 10px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-alt);
        color: var(--muted);
        font-size: 0.84rem;
      }}
      .stack {{
        display: grid;
        gap: 18px;
        margin-top: 22px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
      }}
      .compare {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 16px;
      }}
      .card {{
        padding: 16px;
        background: var(--panel-alt);
      }}
      .card a, a.link {{
        color: var(--accent);
        font-weight: 700;
        text-decoration: none;
      }}
      .takeaway {{
        margin-top: 16px;
        padding: 16px;
        background: #1f2625;
      }}
      .takeaway p {{
        color: #e5ece7;
      }}
      .takeaway strong {{
        color: #ffffff;
      }}
      .section-head {{
        margin-bottom: 14px;
      }}
      .list {{
        margin: 10px 0 0;
        padding-left: 18px;
        color: var(--muted);
      }}
      .list li + li {{
        margin-top: 8px;
      }}
      @media (max-width: 980px) {{
        .grid, .compare {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="page">
{body}
    </main>
  </body>
</html>
"""


def render_concept_atlas(registry: dict[str, Any]) -> str:
    cards = []
    for concept in registry["concepts"]:
        cards.append(
            f"""          <article class="card">
            <h3><a href="{esc(concept['id'])}.html">{esc(concept['name'])}</a></h3>
            <p>{esc(concept['why_it_matters'])}</p>
          </article>"""
        )
    body = f"""      <a class="back" href="../index.html">Back to root index</a>
      <section class="hero">
        <span class="eyebrow">Concept Atlas</span>
        <h1>Shared Damodaran Concepts</h1>
        <p class="lead">
          Root-level concept pages that compare how recurring Damodaran ideas are
          treated across multiple courses. This concept-first layer is generated
          from the normalized registry rather than hand-authored one page at a
          time.
        </p>
        <div class="meta">
          <span class="chip">Concept pages: {len(registry['concepts'])}</span>
          <span class="chip">Courses connected: {len({item['slug'] for concept in registry['concepts'] for item in concept['courses']})}</span>
        </div>
      </section>
      <section class="section stack">
        <div class="section-head">
          <h2>Concepts</h2>
          <p>Each concept page compares course-specific variants and links back into the underlying course sites.</p>
        </div>
        <div class="grid">
{chr(10).join(cards)}
        </div>
      </section>"""
    return root_page("Concept Atlas - Aswath Damodaran Courses Concepts Research", body)


def session_titles_for(course_slug: str, indexes: list[int], evidence_index: dict[str, Any]) -> list[str]:
    course = next((item for item in evidence_index.get("courses", []) if item["slug"] == course_slug), None)
    if not course:
        return []
    lookup = {session["index"]: session["title"] for session in course.get("sessions", [])}
    titles = []
    for index in indexes:
        title = lookup.get(index)
        if title:
            titles.append(f"{index}: {title}")
        else:
            titles.append(str(index))
    return titles


def file_evidence_for(course_slug: str, refs: list[str], file_evidence_index: dict[str, Any]) -> list[dict[str, str]]:
    course = next((item for item in file_evidence_index.get("courses", []) if item["slug"] == course_slug), None)
    if not course:
        return []
    lookup = {item["path"]: item for item in course.get("items", [])}
    resolved = []
    for ref in refs:
        item = lookup.get(ref)
        if item:
            resolved.append(item)
        else:
            resolved.append(
                {
                    "path": ref,
                    "label": Path(ref).name,
                    "kind": "unknown",
                    "href": f"../{course_slug}/{ref}",
                }
            )
    return resolved


def file_evidence_for_ids(ids: list[str], file_evidence_index: dict[str, Any]) -> list[dict[str, str]]:
    lookup = {
        item["id"]: item
        for course in file_evidence_index.get("courses", [])
        for item in course.get("items", [])
        if "id" in item
    }
    return [lookup[item_id] for item_id in ids if item_id in lookup]


def render_session_list(course_slug: str, indexes: list[int], evidence_index: dict[str, Any]) -> str:
    titles = session_titles_for(course_slug, indexes, evidence_index)
    if not titles:
        return ""
    items = "\n".join(f"              <li>{esc(title)}</li>" for title in titles)
    return f"""
            <details style="margin-top:10px">
              <summary>Session evidence</summary>
              <ul class="list">
{items}
              </ul>
            </details>"""


def render_file_links(course_slug: str, refs: list[str], file_evidence_index: dict[str, Any], depth_prefix: str) -> str:
    items = file_evidence_for(course_slug, refs, file_evidence_index)
    if not items:
        return ""
    links = []
    for item in items:
        href = item["href"]
        if depth_prefix == "../../":
            href = href.replace("../", "../../", 1)
        links.append(f'<a class="link" href="{esc(href)}">{esc(item["label"])}</a>')
    return " · ".join(links)


def render_file_links_from_ids(ids: list[str], file_evidence_index: dict[str, Any], depth_prefix: str) -> str:
    items = file_evidence_for_ids(ids, file_evidence_index)
    if not items:
        return ""
    links = []
    for item in items:
        href = item["href"]
        if depth_prefix == "../../":
            href = href.replace("../", "../../", 1)
        links.append(f'<a class="link" href="{esc(href)}">{esc(item["label"])}</a>')
    return " · ".join(links)


def render_normalized_concepts_overview(
    registry: dict[str, Any],
    evidence_index: dict[str, Any],
    file_evidence_index: dict[str, Any],
    source_label: str,
) -> str:
    sections = []
    for concept in registry["concepts"]:
        cards = []
        for course in concept["courses"]:
            analysis_links = render_file_links_from_ids(course.get("analysis_evidence_ids", []), file_evidence_index, "../") or render_file_links(course["slug"], course.get("analysis_refs", []), file_evidence_index, "../")
            site_links = render_file_links_from_ids(course.get("site_evidence_ids", []), file_evidence_index, "../") or render_file_links(course["slug"], course.get("site_refs", []), file_evidence_index, "../")
            cards.append(
                f"""          <article class="card">
            <h3>{esc(course['course_title'])}</h3>
            <p><strong>{esc(course['variant_name'])}</strong></p>
            <p>{esc(course['treatment'])}</p>
            <p style="margin-top:10px">Evidence sessions: {esc(", ".join(str(x) for x in course.get('evidence_sessions', [])))}</p>
{render_session_list(course['slug'], course.get('evidence_sessions', []), evidence_index)}
            <p style="margin-top:10px">{analysis_links}</p>
            <p style="margin-top:10px">{site_links}</p>
          </article>"""
            )
        sections.append(
            f"""        <section class="section">
          <h2>{esc(concept['name'])}</h2>
          <p>{esc(concept['why_it_matters'])}</p>
          <div class="compare">
{chr(10).join(cards)}
          </div>
          <div class="takeaway">
            <p><strong>Cross-course pattern:</strong> {esc(concept['cross_course_pattern'])}</p>
          </div>
        </section>"""
        )

    body = f"""      <a class="back" href="index.html">Back to root index</a>
      <section class="hero">
        <span class="eyebrow">Normalized Registry</span>
        <h1>Shared Damodaran Concepts Across Courses</h1>
        <p class="lead">
          This page is generated from the normalized concept registry and maps
          stable Damodaran ideas across the active course set. Each concept can
          then be browsed through the concept atlas as its own root page.
        </p>
        <div class="meta">
          <span class="chip">Concepts normalized: {len(registry['concepts'])}</span>
          <span class="chip">Courses connected: {len({item['slug'] for concept in registry['concepts'] for item in concept['courses']})}</span>
          <span class="chip">Source: {esc(source_label)}</span>
        </div>
      </section>
      <div class="stack">
{chr(10).join(sections)}
      </div>"""
    return root_page("Normalized Concepts - Aswath Damodaran Courses Concepts Research", body)


def render_concept_page(concept: dict[str, Any], evidence_index: dict[str, Any], file_evidence_index: dict[str, Any]) -> str:
    cards = []
    for course in concept["courses"]:
        analysis_links = render_file_links_from_ids(course.get("analysis_evidence_ids", []), file_evidence_index, "../../") or render_file_links(course["slug"], course.get("analysis_refs", []), file_evidence_index, "../../")
        site_links = render_file_links_from_ids(course.get("site_evidence_ids", []), file_evidence_index, "../../") or render_file_links(course["slug"], course.get("site_refs", []), file_evidence_index, "../../")
        cards.append(
            f"""          <article class="card">
            <h3>{esc(course['course_title'])}</h3>
            <p><strong>{esc(course['variant_name'])}</strong></p>
            <p>{esc(course['treatment'])}</p>
            <p style="margin-top:10px">Evidence sessions: {esc(", ".join(str(x) for x in course.get('evidence_sessions', [])))}</p>
{render_session_list(course['slug'], course.get('evidence_sessions', []), evidence_index)}
            <p style="margin-top:10px">{analysis_links}</p>
            <p style="margin-top:10px">{site_links}</p>
          </article>"""
        )
    body = f"""      <a class="back" href="index.html">Back to concept atlas</a>
      <section class="hero">
        <span class="eyebrow">Normalized Concept</span>
        <h1>{esc(concept['name'])}</h1>
        <p class="lead">{esc(concept['why_it_matters'])}</p>
      </section>
      <div class="stack">
        <section class="section">
          <h2>Across Courses</h2>
          <div class="compare">
{chr(10).join(cards)}
          </div>
          <div class="takeaway">
            <p><strong>Cross-course pattern:</strong> {esc(concept['cross_course_pattern'])}</p>
          </div>
        </section>
      </div>"""
    return root_page(f"{concept['name']} - Concept Atlas", body)


def build(workspace_root: Path) -> None:
    resolved_registry = workspace_root / "analysis/normalized-concepts-resolved.json"
    registry_path = resolved_registry if resolved_registry.exists() else workspace_root / "analysis/normalized-concepts.json"
    registry = load_json(registry_path)
    evidence_index = load_json(workspace_root / "analysis/course-evidence-index.json")
    file_evidence_index = load_json(workspace_root / "analysis/course-file-evidence-index.json")
    concept_dir = workspace_root / "site/concepts"
    concept_dir.mkdir(parents=True, exist_ok=True)

    (workspace_root / "site/normalized-concepts.html").write_text(
        render_normalized_concepts_overview(
            registry,
            evidence_index,
            file_evidence_index,
            registry_path.relative_to(workspace_root).as_posix(),
        ),
        encoding="utf-8",
    )
    (concept_dir / "index.html").write_text(
        render_concept_atlas(registry),
        encoding="utf-8",
    )
    for concept in registry["concepts"]:
        (concept_dir / f"{concept['id']}.html").write_text(
            render_concept_page(concept, evidence_index, file_evidence_index),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the root concept atlas from normalized concepts JSON.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    args = parser.parse_args()
    build(args.workspace_root.resolve())


if __name__ == "__main__":
    main()
