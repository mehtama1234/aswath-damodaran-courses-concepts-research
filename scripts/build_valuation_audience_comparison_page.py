#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value))


def page(title: str, body: str) -> str:
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
      .page {{ width: min(1180px, calc(100% - 24px)); margin: 0 auto; padding: 24px 0 56px; }}
      .back {{
        display: inline-flex; align-items: center; min-height: 36px; padding: 0 12px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel);
        color: var(--muted); text-decoration: none; margin-bottom: 18px;
      }}
      .hero, .axis, .closeout, .pairs {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: var(--shadow);
        padding: 24px;
      }}
      .eyebrow {{
        display: inline-block; padding: 6px 10px; border-radius: 999px;
        background: var(--accent-soft); color: var(--accent); font-size: 12px;
        font-weight: 700; text-transform: uppercase;
      }}
      h1, h2, h3 {{ margin: 0; font-weight: 700; }}
      h1 {{ margin-top: 12px; font-size: clamp(2.1rem, 4vw, 3.3rem); line-height: 1.02; }}
      h2 {{ font-size: 1.34rem; margin-bottom: 10px; }}
      h3 {{ font-size: 1rem; margin-bottom: 8px; }}
      p {{ margin: 0; color: var(--muted); }}
      .lead {{ color: var(--ink); font-size: 1.05rem; max-width: 78ch; }}
      .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
      .chip {{
        display: inline-flex; align-items: center; min-height: 30px; padding: 0 10px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel-alt);
        color: var(--muted); font-size: 0.84rem;
      }}
      .stack {{ display: grid; gap: 18px; margin-top: 22px; }}
      .compare {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 16px;
      }}
      .course-card, .pair-card {{
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--panel-alt);
      }}
      .course-card a {{ color: var(--accent); font-weight: 700; text-decoration: none; }}
      .pair-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 16px;
      }}
      ul {{ margin: 10px 0 0; padding-left: 18px; color: var(--muted); }}
      li + li {{ margin-top: 8px; }}
      .takeaway {{
        margin-top: 16px;
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #1f2625;
      }}
      .takeaway p {{ color: #e5ece7; }}
      .takeaway strong {{ color: #ffffff; }}
      @media (max-width: 900px) {{
        .compare, .pair-grid {{ grid-template-columns: 1fr; }}
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


def card(title: str, href: str, focus: str, emphasis: str, evidence: list[str]) -> str:
    evidence_items = "".join(f"<li>{esc(item)}</li>" for item in evidence)
    return f"""
            <article class="course-card">
              <h3><a href="{esc(href)}">{esc(title)}</a></h3>
              <p><strong>{esc(focus)}</strong></p>
              <p style="margin-top:8px">{esc(emphasis)}</p>
              <ul>{evidence_items}</ul>
            </article>
"""


def build(workspace_root: Path) -> None:
    data = load_json(workspace_root / "analysis/valuation-audience-comparison.json")
    chips = "".join(
        f'<span class="chip">{esc(item)}</span>'
        for item in [
            "Audience-Level Comparison",
            f"Courses compared: {len(data['courses'])}",
            "Valuation Undergraduate Spring 2025",
            "Valuation MBA Spring 2025",
        ]
    )

    axes_html = []
    for index, axis in enumerate(data["comparison_axes"], start=1):
        ug = axis["undergraduate"]
        mba = axis["mba"]
        axes_html.append(
            f"""
        <section class="axis">
          <h2>{index}. {esc(axis['name'])}</h2>
          <p>{esc(axis['summary'])}</p>
          <div class="compare">
{card("Valuation Undergraduate Spring 2025", "../valuation-undergraduate-spring-2025/site/index.html", ug["focus"], ug["emphasis"], ug["evidence"])}
{card("Valuation MBA Spring 2025", "../valuation-mba-spring-2025/site/index.html", mba["focus"], mba["emphasis"], mba["evidence"])}
          </div>
          <div class="takeaway">
            <p><strong>Audience takeaway:</strong> {esc(axis['takeaway'])}</p>
          </div>
        </section>
"""
        )

    pair_cards = []
    for pair in data["concept_correspondences"]:
        pair_cards.append(
            f"""
          <article class="pair-card">
            <h3>{esc(pair['shared_idea'])}</h3>
            <p><strong>Undergraduate:</strong> {esc(pair['undergraduate_concept'])}</p>
            <p><strong>MBA:</strong> {esc(pair['mba_concept'])}</p>
            <p style="margin-top:10px">{esc(pair['difference'])}</p>
          </article>
"""
        )

    body = f"""
      <a class="back" href="index.html">Back to root index</a>
      <section class="hero">
        <span class="eyebrow">Valuation Audience Comparison</span>
        <h1>Undergraduate Versus MBA Valuation</h1>
        <p class="lead">
          These two valuation courses teach the same deep Damodaran machinery, but
          they do it at different audience levels. This page isolates how the
          intellectual core stays stable while the pedagogy, compression,
          project pressure, and framing change.
        </p>
        <div class="meta">{chips}</div>
      </section>

      <div class="stack">
{''.join(axes_html)}
        <section class="pairs">
          <h2>Concept Correspondences</h2>
          <p>The overlap below shows where the two courses are clearly teaching the same idea in different pedagogical registers.</p>
          <div class="pair-grid">
{''.join(pair_cards)}
          </div>
        </section>
        <section class="closeout">
          <h2>Big Takeaway</h2>
          <p>{esc(data['big_takeaway'])}</p>
        </section>
      </div>
"""

    write_text(
        workspace_root / "site/valuation-audience-comparison.html",
        page("Valuation Undergraduate vs MBA - Aswath Damodaran Courses Concepts Research", body),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the undergraduate-versus-MBA valuation comparison page.")
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
