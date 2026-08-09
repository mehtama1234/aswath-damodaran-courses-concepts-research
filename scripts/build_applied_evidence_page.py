#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

import validate_applied_evidence


def esc(value: str) -> str:
    return html.escape(value)


def load_registry(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def page(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Applied Evidence Registry - Aswath Damodaran Courses Concepts Research</title>
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
        line-height: 1.62;
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
      .hero, .card {{ padding: 24px; }}
      .eyebrow {{
        display: inline-block; padding: 6px 10px; border-radius: 999px;
        background: var(--accent-soft); color: var(--accent); font-size: 12px;
        font-weight: 700; text-transform: uppercase;
      }}
      h1, h2, h3 {{ margin: 0; font-weight: 700; }}
      h1 {{ margin-top: 12px; font-size: clamp(2rem, 4vw, 3.15rem); line-height: 1.04; }}
      h2 {{ font-size: 1.36rem; margin-bottom: 10px; }}
      h3 {{ font-size: 1.02rem; margin-bottom: 8px; }}
      p {{ margin: 0; color: var(--muted); }}
      .lead {{ color: var(--ink); font-size: 1.05rem; max-width: 76ch; }}
      .meta, .chip-list {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
      .chip {{
        display: inline-flex; align-items: center; min-height: 30px; padding: 0 10px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel-alt);
        color: var(--muted); font-size: 0.84rem;
      }}
      .section {{ margin-top: 24px; }}
      .grid {{ display: grid; gap: 16px; }}
      .card a {{ color: var(--accent); font-weight: 700; text-decoration: none; }}
      ul {{ margin: 10px 0 0; padding-left: 18px; color: var(--muted); }}
      li + li {{ margin-top: 8px; }}
      code {{
        background: var(--panel-alt);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 1px 6px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 0.9em;
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
    registry = load_registry(workspace_root / "analysis/applied-evidence-registry.json")
    validate_applied_evidence.validate(workspace_root)
    briefs = registry["briefs"]
    cards: list[str] = []
    for brief in briefs:
        theme_cluster_section = ""
        if brief.get("theme_cluster_refs"):
            cluster_items = "".join(
                f"""<li><a href="{esc(Path(cluster["root_href"]).relative_to("site").as_posix())}">{esc(cluster["title"])}</a>: {esc(cluster["why_it_matters"])}</li>"""
                for cluster in brief["theme_cluster_refs"]
            )
            theme_cluster_section = f"""
            <div style="margin-top:16px">
              <h3>Root Theme Clusters</h3>
              <ul>{cluster_items}</ul>
            </div>"""
        anchor_sections: list[str] = []
        for anchor in brief["anchors"]:
            trail = "".join(f"<li><code>{esc(item)}</code></li>" for item in anchor["source_trail"])
            anchor_sections.append(
                f"""<div style="margin-top:16px">
              <h3><a href="{esc(Path(anchor["root_href"]).relative_to("site").as_posix())}">{esc(anchor["label"])}</a></h3>
              <p>{esc(anchor["why_it_matters"])}</p>
              <ul>{trail}</ul>
            </div>"""
            )
        cards.append(
            f"""        <article class="card">
          <a id="brief-{esc(brief["brief_id"])}"></a>
          <div class="chip-list">
            <span class="chip">Applied brief evidence</span>
            <span class="chip">{esc(brief["brief_id"])}</span>
          </div>
          <h2 style="margin-top:12px"><a href="{esc(Path(brief["brief_href"]).name)}">{esc(brief["brief_title"])}</a></h2>
          {theme_cluster_section}
          {''.join(anchor_sections)}
        </article>"""
        )

    body = f"""
      <a class="back" href="index.html">Back to root index</a>
      <section class="hero">
        <span class="eyebrow">Applied Evidence</span>
        <h1>Applied Evidence Registry</h1>
        <p class="lead">
          A structured root evidence layer mapping each applied brief to its
          root concept anchors, theme clusters, comparison pages, and named course-level source trails.
        </p>
        <div class="meta">
          <span class="chip">Updated August 9, 2026</span>
          <span class="chip">{len(briefs)} briefs covered</span>
          <span class="chip">Structured source trails</span>
        </div>
      </section>

      <section class="section">
        <div class="grid">
{''.join(cards)}
        </div>
      </section>
    """
    output = workspace_root / "site/applied-evidence.html"
    output.write_text(page(body), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the applied evidence registry page.")
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
