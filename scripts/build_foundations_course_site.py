#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


THEME_SECTIONS: dict[str, list[dict[str, str]]] = {
    "finance-is-a-forward-looking-language-of-business": [
        {
            "title": "What This Theme Is Really Doing",
            "body": "Damodaran starts below valuation technique. He defines finance as the language that explains how a business turns resources, ambition, and uncertainty into value claims. That keeps the beginner from treating finance as a detached stack of formulas.",
        },
        {
            "title": "Why It Matters Outside The Classroom",
            "body": "This frame is useful for founders, operators, investors, and students because it links strategy, execution, and ownership back to future cash generation and financing choices.",
        },
        {
            "title": "The Hidden Discipline",
            "body": "The discipline underneath the theme is simplification without distortion. Assets become assets in place and growth assets. Financing becomes debt and equity. The goal is to isolate the value drivers that matter most.",
        },
    ],
    "cash-flows-and-time-translate-economic-choices-into-value": [
        {
            "title": "The Economic Core",
            "body": "This theme teaches that finance cares about what cash a business can generate and when that cash arrives. Accounting labels can help organize the story, but they do not determine value on their own.",
        },
        {
            "title": "Why Beginners Get Stuck Here",
            "body": "Many people learn discounting mechanically before they understand it intuitively. Damodaran starts from the idea that delay has a cost, uncertainty changes the worth of future dollars, and claims with different timing patterns need different valuation treatment.",
        },
        {
            "title": "Where It Leads",
            "body": "Once cash flow and time are in place, the student can move cleanly into bonds, equity, and options. The valuation problem becomes easier to reason about because each asset can be described by the shape and uncertainty of its future payoffs.",
        },
    ],
    "risk-is-inescapable-but-it-must-be-measured-through-the-right-eyes": [
        {
            "title": "Risk Is Not Just Danger",
            "body": "The course resists the simplistic version of finance where risk is merely a bad outcome. Risk is the condition that makes return possible. The real question is which risks matter, to whom they matter, and how they should be priced.",
        },
        {
            "title": "The Investor Lens",
            "body": "Required return is not a random hurdle picked from convention. It is tied to the kind of claim an investor owns and to how exposed that investor is to uncertain outcomes.",
        },
        {
            "title": "Why This Theme Travels Well",
            "body": "This is one of the most portable ideas in the Damodaran ecosystem. It feeds directly into investing, corporate finance, valuation, and strategy because every serious decision is ultimately a decision about which risks are being taken and what compensation those risks require.",
        },
    ],
    "valuation-starts-by-understanding-what-kind-of-claim-you-own": [
        {
            "title": "Different Claims, Different Logic",
            "body": "The course does not treat valuation as one universal formula. Bonds, equity, and options differ because the structure of the claim changes the structure of the payoff.",
        },
        {
            "title": "Why Claim Structure Comes First",
            "body": "A bond holder is promised contractual cash flows. An equity owner gets what is left over. An option holder benefits only in specific states of the world. If the analyst misses that hierarchy, every later valuation step becomes confused.",
        },
        {
            "title": "What This Enables Later",
            "body": "Once claim structure is clear, more advanced Damodaran courses can build naturally into intrinsic valuation, pricing, private-company issues, optionality, and control. This theme is the compact origin point for that later complexity.",
        },
    ],
    "macro-forces-inflation-rates-and-currencies-shape-every-financial-decision": [
        {
            "title": "The Environment Around Every Valuation",
            "body": "Inflation, interest rates, and currencies are not side topics. They define the nominal environment in which every cash flow and discount rate is measured.",
        },
        {
            "title": "What Damodaran Is Simplifying",
            "body": "The course reduces macro complexity to a usable operating logic. Inflation erodes real value. Interest rates combine real growth and inflation expectations. Currencies become comparable when the analyst stays consistent about the nominal unit being used.",
        },
        {
            "title": "Why This Matters For Real Work",
            "body": "This theme matters whenever someone compares companies across countries, shifts models between currencies, or talks about real versus nominal performance. It trains the reader to defend consistency, not just compute outputs.",
        },
    ],
}


COURSE_THESIS_SECTIONS: list[dict[str, str]] = [
    {
        "title": "The Course Thesis",
        "body": "Foundations of Finance is a first-principles bridge course. It builds the conceptual architecture required to understand how businesses create value, how claims on that value differ, and how time, risk, inflation, and currency shape every financial judgment.",
    },
    {
        "title": "Why This Course Matters In The Larger Damodaran System",
        "body": "In the broader Damodaran corpus, this course acts like the basement layer. Investment philosophy, valuation, and corporate finance all assume the reader already understands cash flows, risk, claim structure, discounting, and nominal consistency. Foundations of Finance makes those assumptions explicit.",
    },
    {
        "title": "What A Reader Should Carry Forward",
        "body": "A reader should leave with a handful of durable habits: ask what claim is being valued, ask whose risk matters, separate nominal from real thinking, treat growth as valuable only when it creates value, and keep the whole analysis internally consistent.",
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value))


def session_label(session_index: int, sessions: dict[int, dict[str, Any]]) -> str:
    record = sessions.get(session_index)
    if not record:
        return f"Session {session_index}"
    return f"Session {session_index}: {record['title']}"


def top_nav(nav_key: str, in_concepts: bool) -> str:
    if in_concepts:
        items = [
            ("Overview", "../index.html", "overview"),
            ("Course Thesis", "../course-thesis.html", "thesis"),
            ("Concept Atlas", "index.html", "concepts"),
        ]
    else:
        items = [
            ("Overview", "index.html", "overview"),
            ("Course Thesis", "course-thesis.html", "thesis"),
            ("Concept Atlas", "concepts/index.html", "concepts"),
        ]
    return "".join(
        f'<a class="{"active" if key == nav_key else ""}" href="{href}">{label}</a>'
        for label, href, key in items
    )


def base_page(title: str, body: str, nav_key: str, *, in_concepts: bool = False) -> str:
    back_href = "../../../site/index.html" if in_concepts else "../../site/index.html"
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{esc(title)}</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f4f1ea;
        --panel: #fffdf8;
        --panel-alt: #f8f4ed;
        --ink: #1f1f1b;
        --muted: #605b52;
        --line: #d7d0c4;
        --accent: #0b6b6f;
        --accent-soft: #d8ecec;
        --accent-2: #8e4b15;
        --shadow: 0 16px 40px rgba(32, 26, 16, 0.08);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--ink);
        line-height: 1.58;
      }}
      a {{ color: inherit; }}
      .page {{
        width: min(1180px, calc(100% - 32px));
        margin: 0 auto;
        padding: 24px 0 64px;
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
      .hero, .card, .essay {{
        background: var(--panel);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 8px;
      }}
      .hero {{
        display: grid;
        grid-template-columns: 1.45fr 1fr;
        gap: 24px;
        padding: 28px;
      }}
      .eyebrow {{
        display: inline-block;
        padding: 6px 10px;
        background: var(--accent-soft);
        color: var(--accent);
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
      }}
      h1, h2, h3 {{ margin: 0; font-weight: 700; }}
      h1 {{ margin-top: 12px; font-size: clamp(2.2rem, 4vw, 3.4rem); line-height: 1.04; }}
      h2 {{ font-size: 1.4rem; margin-bottom: 10px; }}
      h3 {{ font-size: 1.02rem; margin-bottom: 8px; }}
      p {{ margin: 0; color: var(--muted); }}
      .lead {{ color: var(--ink); font-size: 1.05rem; max-width: 70ch; }}
      nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
      }}
      nav a {{
        display: inline-flex;
        align-items: center;
        min-height: 34px;
        padding: 0 12px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: var(--panel-alt);
        color: var(--muted);
        text-decoration: none;
      }}
      nav a.active {{
        background: var(--accent-soft);
        color: var(--accent);
        border-color: rgba(11, 107, 111, 0.25);
      }}
      .meta, .chips {{
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
      .hero-aside {{
        display: grid;
        gap: 16px;
      }}
      .aside-card {{
        padding: 18px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: linear-gradient(180deg, #fffdf8 0%, #f6f0e6 100%);
      }}
      .section {{ margin-top: 24px; }}
      .section-head {{ margin-bottom: 14px; }}
      .grid-2, .grid-3 {{
        display: grid;
        gap: 16px;
      }}
      .grid-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .card, .essay {{ padding: 20px; }}
      .card a, .essay a {{
        color: var(--accent);
        font-weight: 700;
        text-decoration: none;
      }}
      .essay p + p {{ margin-top: 12px; }}
      ul {{
        margin: 10px 0 0;
        padding-left: 18px;
        color: var(--muted);
      }}
      li + li {{ margin-top: 8px; }}
      .stats {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin-top: 14px;
      }}
      .stat {{
        padding: 14px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--panel-alt);
      }}
      .stat .label {{
        font-size: 0.76rem;
        text-transform: uppercase;
        font-weight: 700;
        color: var(--muted);
      }}
      .stat .value {{
        margin-top: 6px;
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--ink);
      }}
      .list {{
        display: grid;
        gap: 12px;
      }}
      .list-item {{
        padding: 14px 16px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--panel-alt);
      }}
      .kicker {{
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: 700;
        color: var(--accent-2);
        margin-bottom: 6px;
      }}
      @media (max-width: 980px) {{
        .hero, .grid-2, .grid-3 {{ grid-template-columns: 1fr; }}
      }}
      @media (max-width: 720px) {{
        .page {{ width: min(100% - 20px, 1180px); padding-top: 14px; }}
        .hero, .card, .essay {{ padding: 16px; }}
        .stats {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main class="page">
      <a class="back" href="{back_href}">Back to root research index</a>
{body}
    </main>
  </body>
</html>
"""


def render_hero(summary: dict[str, Any], coverage_note: str, thesis: str, nav_key: str, *, in_concepts: bool = False) -> str:
    return f"""
      <section class="hero">
        <div>
          <span class="eyebrow">Foundations Course Research</span>
          <h1>Foundations of Finance</h1>
          <p class="lead">{esc(thesis)}</p>
          <div class="meta">
            <span class="chip">Updated: August 9, 2026</span>
            <span class="chip">{summary['videos']} playlist videos</span>
            <span class="chip">{summary['available_transcripts']} transcript-backed sessions</span>
            <span class="chip">{summary['total_words']:,} words</span>
          </div>
          <nav>{top_nav(nav_key, in_concepts)}</nav>
        </div>
        <div class="hero-aside">
          <div class="aside-card">
            <h2>What This Course Adds</h2>
            <p>This workspace now has a reader-facing layer for Damodaran's first-principles finance course, making the introductory material usable alongside the richer investment, valuation, and corporate-finance workspaces.</p>
          </div>
          <div class="aside-card">
            <h2>Coverage Note</h2>
            <p>{esc(coverage_note)}</p>
          </div>
        </div>
      </section>
"""


def build_overview(summary: dict[str, Any], themes: list[dict[str, Any]], sessions: dict[int, dict[str, Any]], coverage_note: str) -> str:
    hero = render_hero(
        summary,
        coverage_note,
        "A concise Damodaran bridge course that explains how business structure, cash flows, risk, claim design, and nominal consistency fit together before the heavier valuation and investing material begins.",
        "overview",
    )
    theme_cards = "\n".join(
        f"""
          <article class="card">
            <div class="kicker">Theme {index}</div>
            <h3><a href="concepts/{esc(theme['id'])}.html">{esc(theme['name'])}</a></h3>
            <p>{esc(theme['summary'])}</p>
            <div class="chips">{''.join(f'<span class="chip">{esc(lens)}</span>' for lens in theme.get('lenses', []))}</div>
            <ul>
              <li>{len(theme.get('subthemes', []))} subthemes</li>
              <li>{', '.join(session_label(session_index, sessions) for session_index in theme.get('evidence_sessions', []))}</li>
            </ul>
          </article>
        """
        for index, theme in enumerate(themes, start=1)
    )
    session_items = "\n".join(
        f"""
          <div class="list-item">
            <div class="kicker">Session {record['index']}</div>
            <h3>{esc(record['title'])}</h3>
            <p>{esc(record['summary'])}</p>
          </div>
        """
        for record in [sessions[index] for index in sorted(sessions)]
    )
    body = hero + f"""
      <section class="section">
        <div class="section-head">
          <h2>Course Shape</h2>
          <p>A short course with a broad remit: teach the financial grammar needed to understand later work on valuation, investing, capital allocation, and market claims.</p>
        </div>
        <div class="grid-3">
          <article class="card">
            <h3>Business First</h3>
            <p>The opening sessions define finance as a way of reading businesses, not merely a computational toolkit.</p>
          </article>
          <article class="card">
            <h3>Claims Next</h3>
            <p>The middle of the course shows how bonds, equity, and options differ because each holder owns a different claim on future outcomes.</p>
          </article>
          <article class="card">
            <h3>Consistency Always</h3>
            <p>The macro sessions enforce a habit that later courses depend on: separate real from nominal thinking and keep currencies, inflation, and discount rates internally consistent.</p>
          </article>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Major Themes</h2>
          <p>These pages distill the transcript-backed conceptual structure visible in the currently captured sessions.</p>
        </div>
        <div class="grid-2">
{theme_cards}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>What A Reader Can Use This For</h2>
        </div>
        <div class="grid-2">
          <article class="card">
            <h3>As A Primer</h3>
            <p>This course is the cleanest entry point for readers who need to understand Damodaran's later work without jumping straight into full valuation or corporate-finance complexity.</p>
          </article>
          <article class="card">
            <h3>As A Framework Check</h3>
            <p>It is also useful for experienced readers who want to go back to first principles and test whether their models still line up with cash flows, claim structure, risk logic, and nominal consistency.</p>
          </article>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Transcript-Backed Session Ladder</h2>
          <p>The currently available sessions move from first principles to asset claims to macro context.</p>
        </div>
        <div class="list">
{session_items}
        </div>
      </section>
"""
    return base_page("Foundations of Finance - Course Research Overview", body, "overview")


def build_thesis(summary: dict[str, Any], coverage_note: str) -> str:
    hero = render_hero(
        summary,
        coverage_note,
        "The course teaches the conceptual floor beneath Damodaran's broader system: how to think about value claims before building more advanced valuation, financing, and investing judgments.",
        "thesis",
    )
    sections = "\n".join(
        f"""
          <article class="essay">
            <h2>{esc(section['title'])}</h2>
            <p>{esc(section['body'])}</p>
          </article>
        """
        for section in COURSE_THESIS_SECTIONS
    )
    body = hero + f"""
      <section class="section">
        <div class="section-head">
          <h2>Long-Form Reading</h2>
          <p>A simple way to read the course is as an argument about how financial claims become legible.</p>
        </div>
{sections}
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Three Durable Takeaways</h2>
        </div>
        <div class="grid-3">
          <article class="card">
            <h3>Value Starts With Business Reality</h3>
            <p>Every later spreadsheet is downstream of a view about what the business owns, how it grows, and who gets paid first.</p>
          </article>
          <article class="card">
            <h3>Risk And Discounting Are Interpretive</h3>
            <p>Required return is an argument about uncertainty and ownership, not just a plug variable.</p>
          </article>
          <article class="card">
            <h3>Consistency Is A Habit</h3>
            <p>Real versus nominal logic, inflation assumptions, and currency choice have to fit together before the final number can mean anything.</p>
          </article>
        </div>
      </section>
"""
    return base_page("Foundations of Finance - Course Thesis", body, "thesis")


def build_concepts_index(summary: dict[str, Any], themes: list[dict[str, Any]], coverage_note: str) -> str:
    hero = render_hero(
        summary,
        coverage_note,
        "Each major theme is treated here as a reusable concept page, so the course can function as a compact concept atlas rather than only as a session list.",
        "concepts",
        in_concepts=True,
    )
    cards = "\n".join(
        f"""
          <article class="card">
            <div class="kicker">Concept</div>
            <h3><a href="{esc(theme['id'])}.html">{esc(theme['name'])}</a></h3>
            <p>{esc(theme['summary'])}</p>
            <ul>
              <li>{len(theme.get('subthemes', []))} subthemes</li>
              <li>{len(theme.get('evidence_sessions', []))} evidence sessions</li>
            </ul>
          </article>
        """
        for theme in themes
    )
    body = hero + f"""
      <section class="section">
        <div class="section-head">
          <h2>Concept Pages</h2>
          <p>These pages are written for reuse in later cross-course synthesis, teaching notes, and future normalized concept work.</p>
        </div>
        <div class="grid-2">
{cards}
        </div>
      </section>
"""
    return base_page("Foundations of Finance - Concept Atlas", body, "concepts", in_concepts=True)


def build_theme_page(summary: dict[str, Any], theme: dict[str, Any], sessions: dict[int, dict[str, Any]], coverage_note: str) -> str:
    hero = render_hero(summary, coverage_note, theme["summary"], "concepts", in_concepts=True)
    sections = "\n".join(
        f"""
          <article class="essay">
            <h2>{esc(section['title'])}</h2>
            <p>{esc(section['body'])}</p>
          </article>
        """
        for section in THEME_SECTIONS.get(theme["id"], [])
    )
    subtheme_items = "\n".join(
        f"""
          <div class="list-item">
            <div class="kicker">Subtheme</div>
            <h3>{esc(subtheme['name'])}</h3>
            <p>{esc(subtheme['summary'])}</p>
            <ul>
              <li>{', '.join(session_label(session_index, sessions) for session_index in subtheme.get('evidence_sessions', []))}</li>
            </ul>
          </div>
        """
        for subtheme in theme.get("subthemes", [])
    )
    evidence_items = "\n".join(
        f"""
          <article class="card">
            <div class="kicker">Evidence Session</div>
            <h3>{esc(sessions[session_index]['title'])}</h3>
            <p>{esc(sessions[session_index]['summary'])}</p>
          </article>
        """
        for session_index in theme.get("evidence_sessions", [])
        if session_index in sessions
    )
    body = hero + f"""
      <section class="section">
        <div class="section-head">
          <h2>{esc(theme['name'])}</h2>
          <p>{esc(theme['summary'])}</p>
        </div>
{sections}
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Subthemes</h2>
        </div>
        <div class="list">
{subtheme_items}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Evidence Sessions</h2>
        </div>
        <div class="grid-2">
{evidence_items}
        </div>
      </section>
"""
    return base_page(f"{theme['name']} - Foundations of Finance", body, "concepts", in_concepts=True)


def build(course_root: Path) -> None:
    course_root = course_root.resolve()
    summary = load_json(course_root / "raw-material/youtube/summary.json")
    transcript_index = load_json(course_root / "raw-material/youtube/transcript-index.json")
    theme_map = load_json(course_root / "analysis/themes-and-subthemes.json")

    site_dir = course_root / "site"
    concepts_dir = site_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    sessions = {
        int(record["index"]): {
            "index": int(record["index"]),
            "title": record["title"],
            "summary": (
                f"{record.get('word_count', 0):,} words across {record.get('cue_count', 0):,} transcript cues."
                if record.get("word_count", 0)
                else "Transcript unavailable in the current corpus."
            ),
        }
        for record in transcript_index
    }
    coverage_note = theme_map["course"]["coverage_note"]
    themes = theme_map["themes"]

    write_text(site_dir / "index.html", build_overview(summary, themes, sessions, coverage_note))
    write_text(site_dir / "course-thesis.html", build_thesis(summary, coverage_note))
    write_text(concepts_dir / "index.html", build_concepts_index(summary, themes, coverage_note))

    for theme in themes:
        write_text(concepts_dir / f"{theme['id']}.html", build_theme_page(summary, theme, sessions, coverage_note))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Foundations of Finance reader-facing course pages.")
    parser.add_argument(
        "--course-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "foundations-of-finance",
        help="Path to the Foundations of Finance course root.",
    )
    args = parser.parse_args()
    build(args.course_root)


if __name__ == "__main__":
    main()
