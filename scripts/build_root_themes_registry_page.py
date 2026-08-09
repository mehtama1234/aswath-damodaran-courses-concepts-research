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


def page(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Root Themes Registry - Aswath Damodaran Courses Concepts Research</title>
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
      .page {{ width: min(1180px, calc(100% - 24px)); margin: 0 auto; padding: 24px 0 56px; }}
      .back {{
        display: inline-flex; align-items: center; min-height: 36px; padding: 0 12px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel);
        color: var(--muted); text-decoration: none; margin-bottom: 18px;
      }}
      .hero, .section, .cluster, .takeaway {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: var(--shadow);
      }}
      .hero, .section {{ padding: 24px; }}
      .stack {{ display: grid; gap: 18px; margin-top: 22px; }}
      .cluster {{ padding: 20px; background: var(--panel-alt); }}
      .eyebrow {{
        display: inline-block; padding: 6px 10px; border-radius: 999px;
        background: var(--accent-soft); color: var(--accent); font-size: 12px;
        font-weight: 700; text-transform: uppercase;
      }}
      h1, h2, h3 {{ margin: 0; font-weight: 700; }}
      h1 {{ margin-top: 12px; font-size: clamp(2rem, 4vw, 3.2rem); line-height: 1.02; }}
      h2 {{ font-size: 1.3rem; margin-bottom: 10px; }}
      h3 {{ font-size: 1rem; margin-bottom: 8px; }}
      p {{ margin: 0; color: var(--muted); }}
      .lead {{ color: var(--ink); font-size: 1.05rem; max-width: 76ch; }}
      .meta, .chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
      .chip {{
        display: inline-flex; align-items: center; min-height: 30px; padding: 0 10px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel);
        color: var(--muted); font-size: 0.84rem;
      }}
      .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
      .subgrid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }}
      ul {{ margin: 10px 0 0; padding-left: 18px; color: var(--muted); }}
      li + li {{ margin-top: 8px; }}
      .takeaway {{ padding: 16px; background: #1f2625; margin-top: 16px; }}
      .takeaway p {{ color: #e5ece7; }}
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--ink); font-size: 0.9rem; }}
      @media (max-width: 980px) {{
        .grid, .subgrid {{ grid-template-columns: 1fr; }}
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
    registry = load_json(workspace_root / "analysis/root-themes-registry.json")
    clusters_html = []
    for cluster in registry["clusters"]:
        course_items = "".join(
            f"<li><strong>{esc(item['slug'])}</strong>: {esc(item['focus'])}</li>"
            for item in cluster["course_links"]
        )
        question_items = "".join(
            f"<li>{esc(question)}</li>"
            for question in cluster["guiding_questions"]
        )
        clusters_html.append(
            f"""        <section class="cluster" id="{esc(cluster['id'])}">
          <div class="chips">
            <span class="chip mono">{esc(cluster['id'])}</span>
            <span class="chip">{esc(cluster['domain'])}</span>
          </div>
          <h2 style="margin-top:12px">{esc(cluster['name'])}</h2>
          <p style="margin-top:10px">{esc(cluster['summary'])}</p>
          <div class="subgrid">
            <div>
              <h3>Why It Matters</h3>
              <p>{esc(cluster['why_it_matters'])}</p>
              <h3 style="margin-top:14px">Guiding Questions</h3>
              <ul>{question_items}</ul>
            </div>
            <div>
              <h3>Course Links</h3>
              <ul>{course_items}</ul>
            </div>
          </div>
        </section>"""
        )

    body = f"""      <a class="back" href="index.html">Back to root index</a>
      <section class="hero">
        <span class="eyebrow">Themes Registry</span>
        <h1>Structured Root Themes Registry</h1>
        <p class="lead">
          A JSON-backed registry of reusable root theme clusters for later
          sector, company, and curriculum work. This is the structured
          companion to the prose themes atlas.
        </p>
        <div class="meta">
          <span class="chip">Clusters: {len(registry['clusters'])}</span>
          <span class="chip">Source: analysis/root-themes-registry.json</span>
          <span class="chip">Updated: {esc(registry['updated_on'])}</span>
        </div>
      </section>
      <section class="section stack">
        <div>
          <h2>How To Use It</h2>
          <p>
            Use the cluster ids here as stable references when later analysis
            needs to point to a named societal, cultural, consumer, industrial,
            institutional, or pedagogical theme instead of only citing prose.
          </p>
        </div>
{''.join(clusters_html)}
        <div class="takeaway">
          <p><strong>Practical role:</strong> This registry is the structured bridge from Damodaran course interpretation into reusable applied-analysis lenses.</p>
        </div>
      </section>"""
    output = workspace_root / "site/root-themes-registry.html"
    output.write_text(page(body), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the root themes registry page.")
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
