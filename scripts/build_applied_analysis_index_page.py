#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import html
from pathlib import Path


def esc(value: str) -> str:
    return html.escape(value)


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def page(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Applied Analysis - Aswath Damodaran Courses Concepts Research</title>
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
      .page {{ width: min(1100px, calc(100% - 24px)); margin: 0 auto; padding: 24px 0 56px; }}
      .back {{
        display: inline-flex; align-items: center; min-height: 36px; padding: 0 12px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel);
        color: var(--muted); text-decoration: none; margin-bottom: 18px;
      }}
      .hero, .card {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: var(--shadow);
      }}
      .hero {{ padding: 24px; }}
      .eyebrow {{
        display: inline-block; padding: 6px 10px; border-radius: 999px;
        background: var(--accent-soft); color: var(--accent); font-size: 12px;
        font-weight: 700; text-transform: uppercase;
      }}
      h1, h2, h3 {{ margin: 0; font-weight: 700; }}
      h1 {{ margin-top: 12px; font-size: clamp(2rem, 4vw, 3.15rem); line-height: 1.04; }}
      h2 {{ font-size: 1.36rem; margin-bottom: 10px; }}
      h3 {{ font-size: 1.04rem; margin-bottom: 8px; }}
      p {{ margin: 0; color: var(--muted); }}
      .lead {{ color: var(--ink); font-size: 1.05rem; max-width: 76ch; }}
      .meta, .chip-list {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
      .chip {{
        display: inline-flex; align-items: center; min-height: 30px; padding: 0 10px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel-alt);
        color: var(--muted); font-size: 0.84rem;
      }}
      .section {{ margin-top: 24px; }}
      .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
      .card {{ padding: 20px; }}
      .card a {{ color: var(--accent); font-weight: 700; text-decoration: none; }}
      ul {{ margin: 10px 0 0; padding-left: 18px; color: var(--muted); }}
      li + li {{ margin-top: 8px; }}
      @media (max-width: 900px) {{
        .grid {{ grid-template-columns: 1fr; }}
      }}
      @media (max-width: 720px) {{
        .hero, .card {{ padding: 18px; }}
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


def build(workspace_root: Path) -> None:
    catalog = load_catalog(workspace_root / "analysis/applied-analysis-catalog.json")
    analyses = catalog["analyses"]

    cards: list[str] = []
    for item in analyses:
        concept_items = "".join(
            f'<li><a href="{esc(Path(concept["href"]).relative_to("site").as_posix())}">{esc(concept["title"])}</a></li>'
            for concept in item["root_concepts"]
        )
        root_pages = "".join(
            f'<li><a href="{esc(Path(page).name)}">{esc(Path(page).stem.replace("-", " ").title())}</a></li>'
            for page in item["root_pages"]
        )
        cards.append(
            f"""        <article class="card">
          <div class="chip-list">
            <span class="chip">{esc(item["type"]).title()} brief</span>
            <span class="chip">{esc(item["status"])}</span>
          </div>
          <h3 style="margin-top:12px"><a href="{esc(Path(item["site_output"]).name)}">{esc(item["title"])}</a></h3>
          <p>{esc(item["focus"])}</p>
          <p style="margin-top:12px">{esc(item["why_it_exists"])}</p>
          <p style="margin-top:12px"><a href="{esc(Path(item["evidence_registry_ref"]["site_page"]).name)}#brief-{esc(item["evidence_registry_ref"]["brief_id"])}">Structured evidence for this brief</a></p>
          <h3 style="margin-top:16px">Root Concepts</h3>
          <ul>{concept_items}</ul>
          <h3 style="margin-top:16px">Linked Root Pages</h3>
          <ul>{root_pages}</ul>
        </article>"""
        )

    body = f"""
      <a class="back" href="index.html">Back to root index</a>
      <section class="hero">
        <span class="eyebrow">Applied Analysis</span>
        <h1>Applied Sector And Company Analysis</h1>
        <p class="lead">
          A growing root-level layer for sector briefs and company briefs built
          on the Damodaran concept atlas, comparison pages, and long-form synthesis.
        </p>
        <div class="meta">
          <span class="chip">Catalog updated August 9, 2026</span>
          <span class="chip">{len(analyses)} applied writeups</span>
          <span class="chip">Sector and company reuse layer</span>
        </div>
      </section>

      <section class="section">
        <h2>Current Applied Surface</h2>
        <div class="grid">
{''.join(cards)}
        </div>
      </section>
    """

    output = workspace_root / "site/applied-analysis.html"
    output.write_text(page(body), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the root applied analysis index page.")
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
