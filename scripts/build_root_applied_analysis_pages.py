#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import html
import re
from pathlib import Path


def esc(value: str) -> str:
    return html.escape(value)


def render_inline(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def load_markdown_sections(path: Path) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = ""
    current_lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current_title:
                sections.append((current_title, current_lines))
            current_title = line[3:].strip()
            current_lines = []
        elif line.startswith("# "):
            continue
        else:
            current_lines.append(line)
    if current_title:
        sections.append((current_title, current_lines))
    return sections


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_lines(lines: list[str]) -> str:
    parts: list[str] = []
    in_list = False
    in_ordered = False
    para: list[str] = []
    current_li: list[str] | None = None
    current_ol_li: list[str] | None = None
    ordered_prefix = re.compile(r"^(\d+)\.\s+(.*)$")

    def flush_para() -> None:
        nonlocal para
        if para:
            parts.append(f"<p>{render_inline(' '.join(item.strip() for item in para if item.strip()))}</p>")
            para = []

    def flush_list_item() -> None:
        nonlocal current_li
        if current_li:
            parts.append(f"<li>{render_inline(' '.join(item.strip() for item in current_li if item.strip()))}</li>")
            current_li = None

    def flush_ordered_item() -> None:
        nonlocal current_ol_li
        if current_ol_li:
            parts.append(f"<li>{render_inline(' '.join(item.strip() for item in current_ol_li if item.strip()))}</li>")
            current_ol_li = None

    def close_lists() -> None:
        nonlocal in_list, in_ordered
        flush_list_item()
        if in_list:
            parts.append("</ul>")
            in_list = False
        flush_ordered_item()
        if in_ordered:
            parts.append("</ol>")
            in_ordered = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_para()
            close_lists()
            continue
        if current_li is not None and line.startswith("  "):
            current_li.append(stripped)
            continue
        if current_ol_li is not None and line.startswith("  "):
            current_ol_li.append(stripped)
            continue
        if stripped.startswith("- "):
            flush_para()
            flush_ordered_item()
            if in_ordered:
                parts.append("</ol>")
                in_ordered = False
            if not in_list:
                parts.append("<ul>")
                in_list = True
            flush_list_item()
            current_li = [stripped[2:].strip()]
            continue
        match = ordered_prefix.match(stripped)
        if match:
            flush_para()
            flush_list_item()
            if in_list:
                parts.append("</ul>")
                in_list = False
            if not in_ordered:
                parts.append("<ol>")
                in_ordered = True
            flush_ordered_item()
            current_ol_li = [match.group(2).strip()]
            continue
        close_lists()
        para.append(stripped)

    flush_para()
    close_lists()
    return "\n".join(parts)


def page(title: str, eyebrow: str, lead: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{esc(title)} - Aswath Damodaran Courses Concepts Research</title>
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
        line-height: 1.68;
      }}
      .page {{ width: min(1000px, calc(100% - 24px)); margin: 0 auto; padding: 24px 0 56px; }}
      .back {{
        display: inline-flex; align-items: center; min-height: 36px; padding: 0 12px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel);
        color: var(--muted); text-decoration: none; margin-bottom: 18px;
      }}
      .hero, .section {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: var(--shadow);
        padding: 24px;
      }}
      .stack {{ display: grid; gap: 18px; margin-top: 22px; }}
      .eyebrow {{
        display: inline-block; padding: 6px 10px; border-radius: 999px;
        background: var(--accent-soft); color: var(--accent); font-size: 12px;
        font-weight: 700; text-transform: uppercase;
      }}
      h1, h2 {{ margin: 0; font-weight: 700; }}
      h1 {{ margin-top: 12px; font-size: clamp(2rem, 4vw, 3.15rem); line-height: 1.04; }}
      h2 {{ font-size: 1.36rem; margin-bottom: 14px; }}
      p {{ margin: 0 0 14px; color: var(--muted); }}
      .lead {{ color: var(--ink); font-size: 1.06rem; max-width: 76ch; }}
      .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
      .chip {{
        display: inline-flex; align-items: center; min-height: 30px; padding: 0 10px;
        border: 1px solid var(--line); border-radius: 999px; background: var(--panel-alt);
        color: var(--muted); font-size: 0.84rem;
      }}
      ul, ol {{ margin: 0; padding-left: 20px; color: var(--muted); }}
      li + li {{ margin-top: 8px; }}
      @media (max-width: 720px) {{
        .hero, .section {{ padding: 18px; }}
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


def default_eyebrow(item_type: str) -> str:
    return "Applied Sector Analysis" if item_type == "sector" else "Applied Company Analysis"


def build_page(workspace_root: Path, config: dict[str, object]) -> None:
    sections = load_markdown_sections(workspace_root / str(config["analysis_source"]))
    eyebrow = str(config.get("eyebrow") or default_eyebrow(str(config["type"])))
    lead = str(config.get("site_lead") or config["focus"])
    hero = f"""
      <a class="back" href="index.html">Back to root index</a>
      <section class="hero">
        <span class="eyebrow">{esc(eyebrow)}</span>
        <h1>{esc(str(config["title"]))}</h1>
        <p class="lead">
          {esc(lead)}
        </p>
        <div class="meta">
          <span class="chip">Applied analysis</span>
          <span class="chip">Transcript-backed framework reuse</span>
          <span class="chip">Updated August 9, 2026</span>
        </div>
      </section>
    """
    section_html = []
    for title, lines in sections:
        section_html.append(
            f"""      <section class="section">
        <h2>{esc(title)}</h2>
        {render_lines(lines)}
      </section>"""
        )
    body = hero + '\n      <div class="stack">\n' + "\n".join(section_html) + "\n      </div>"
    output = workspace_root / str(config["site_output"])
    output.write_text(page(str(config["title"]), eyebrow, lead, body), encoding="utf-8")


def build(workspace_root: Path) -> None:
    catalog = load_catalog(workspace_root / "analysis/applied-analysis-catalog.json")
    for item in catalog["analyses"]:
        build_page(workspace_root, item)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build root applied analysis pages.")
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
