#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


STOPWORDS = {
    "about", "after", "again", "against", "also", "and", "because", "been", "being", "course",
    "damodaran", "does", "from", "have", "into", "just", "like", "more", "only", "other",
    "session", "should", "some", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "through", "very", "what", "when", "where", "which", "with",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value))


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z\-']{2,}", text.lower()) if w not in STOPWORDS]


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def render_inline(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def first_sentence(text: str, limit: int = 280) -> str:
    text = compact(text)
    if not text:
        return "Transcript text is not available for this session."
    sentence = text[:limit]
    for index, char in enumerate(text[:limit], 1):
        if index >= 80 and char in ".!?":
            sentence = text[:index]
            break
    return sentence[:limit].rstrip()


def keyword_score(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(term) for term in terms)


def theme_terms(theme: dict[str, Any]) -> list[str]:
    terms = [theme["name"], theme.get("summary", "")]
    terms.extend(theme.get("lenses", []))
    for sub in theme.get("subthemes", []):
        terms.append(sub["name"])
        terms.append(sub.get("summary", ""))
    bag = []
    for item in terms:
        bag.extend(tokenize(item))
    return sorted(set([t for t in bag if len(t) > 3]))


def subtheme_terms(subtheme: dict[str, Any]) -> list[str]:
    bag = tokenize(subtheme["name"]) + tokenize(subtheme.get("summary", ""))
    return sorted(set([t for t in bag if len(t) > 3]))


def classify(record: dict[str, Any], full_text: str, themes: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    seeded_theme = next((theme for theme in themes if record["index"] in theme.get("evidence_sessions", [])), None)
    if seeded_theme is None:
        scored = []
        for theme in themes:
            score = keyword_score(full_text, theme_terms(theme))
            scored.append((score, theme))
        scored.sort(key=lambda item: item[0], reverse=True)
        seeded_theme = scored[0][1]
    seeded_subtheme = next((sub for sub in seeded_theme.get("subthemes", []) if record["index"] in sub.get("evidence_sessions", [])), None)
    if seeded_subtheme is None and seeded_theme.get("subthemes"):
        scored_sub = []
        for sub in seeded_theme["subthemes"]:
            score = keyword_score(full_text, subtheme_terms(sub))
            scored_sub.append((score, sub))
        scored_sub.sort(key=lambda item: item[0], reverse=True)
        seeded_subtheme = scored_sub[0][1]
    return seeded_theme, seeded_subtheme or {"name": "General discussion", "summary": seeded_theme.get("summary", "")}


def html_page(
    title: str,
    body: str,
    current: str,
    *,
    with_subthemes: bool = True,
    with_concepts: bool = False,
    nav_prefix: str = "",
    asset_prefix: str = "",
) -> str:
    nav = [
        (f"{nav_prefix}index.html", "Overview"),
        (f"{nav_prefix}course-thesis.html", "Thesis"),
        (f"{nav_prefix}themes.html", "Themes"),
        (f"{nav_prefix}subthemes.html", "Subthemes"),
        (f"{nav_prefix}discussions.html", "Discussions"),
        (f"{nav_prefix}sessions.html", "Sessions"),
    ]
    if with_concepts:
        nav.insert(3, (f"{nav_prefix}concepts/index.html", "Concepts"))
    if not with_subthemes:
        nav = [item for item in nav if item[1] != "Subthemes"]
    links = "".join(f'<a class="{"active" if label == current else ""}" href="{href}">{label}</a>' for href, label in nav)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{asset_prefix}assets/styles.css">
</head>
<body>
  <header class="top">
    <div>
      <p class="eyebrow">Aswath Damodaran course atlas</p>
      <h1>{esc(title)}</h1>
    </div>
    <nav>{links}</nav>
  </header>
  <main>{body}</main>
</body>
</html>
"""


def write_styles(site_dir: Path) -> None:
    css = """
:root {
  color-scheme: light;
  --ink: #171818;
  --muted: #616567;
  --line: #d8dbd7;
  --panel: rgba(255,255,255,.84);
  --accent: #0c6f74;
  --accent-2: #8c4d1f;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Georgia, 'Times New Roman', serif; color: var(--ink); background: linear-gradient(135deg, #f8f4ec 0%, #edf5f2 58%, #f6ebe3 100%); }
.top { display:flex; justify-content:space-between; gap:24px; align-items:end; padding:40px min(6vw,72px) 24px; border-bottom:1px solid var(--line); }
.eyebrow { margin:0 0 8px; color:var(--accent-2); text-transform:uppercase; letter-spacing:.08em; font:700 12px/1.2 ui-sans-serif,system-ui,sans-serif; }
h1 { margin:0; font-size:clamp(34px,5vw,64px); line-height:.95; max-width:860px; }
h2 { font-size:30px; margin:0 0 14px; }
h3 { margin:8px 0 10px; font-size:21px; }
p { line-height:1.6; }
nav { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
nav a, .button { color:var(--ink); text-decoration:none; border:1px solid var(--line); background:rgba(255,255,255,.72); padding:8px 11px; border-radius:4px; font:700 13px/1 ui-sans-serif,system-ui,sans-serif; }
nav a.active, nav a:hover, .button:hover { background:var(--accent); color:white; border-color:var(--accent); }
main { padding:34px min(6vw,72px) 64px; }
.hero { max-width:980px; font-size:20px; color:var(--muted); }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:16px; margin-top:24px; }
.card, .row, .essay { background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:18px; box-shadow:0 18px 40px rgba(20,22,19,.05); }
.meta { color:var(--accent-2); font:700 12px/1.4 ui-sans-serif,system-ui,sans-serif; text-transform:uppercase; letter-spacing:.05em; }
.tags { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; }
.tags span { background:#e8f1ee; color:#145255; border:1px solid #cfe2dd; padding:5px 8px; border-radius:999px; font:700 12px/1 ui-sans-serif,system-ui,sans-serif; }
.list { display:grid; gap:12px; }
.row strong { display:block; margin-bottom:6px; }
.essay { max-width:1020px; }
@media (max-width:760px) { .top { display:block; } nav { justify-content:flex-start; margin-top:20px; } }
"""
    write_text(site_dir / "assets/styles.css", css)


def discussion_text(item: dict[str, Any]) -> str:
    terms = ", ".join(item["top_terms"][:4])
    return (
        f"{item['title']} sits inside '{item['theme_name']}' and sharpens the course around '{item['subtheme_name']}'. "
        f"The transcript concentrates on {terms}, so the session works best as evidence for how Damodaran moves from the course thesis into a narrower applied question. "
        f"In the larger course arc, this is where the abstract frame becomes a more usable rule, distinction, or investing/finance habit."
    )


def session_briefs_markdown(title: str, sessions: list[dict[str, Any]]) -> str:
    lines = ["# Session Briefs", "", f"Plain-English course map for `{title}`.", ""]
    grouped = {}
    for item in sessions:
        grouped.setdefault(item["theme_name"], []).append(item)
    for theme_name, items in grouped.items():
        lines.extend([f"## {theme_name}", ""])
        for item in items:
            lines.extend([f"`{item['index']:03d}` {item['title']}  ", item["brief"], ""])
    return "\n".join(lines)


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


def render_markdown_lines(lines: list[str]) -> str:
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
        match = ordered_prefix.match(stripped)
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


def thesis_body_from_markdown(path: Path, summary: dict[str, Any], themes: list[dict[str, Any]], has_concepts: bool) -> str:
    sections = load_markdown_sections(path)
    lead = ""
    argument_spine = ""
    section_html: list[str] = []
    for title, lines in sections:
        rendered = render_markdown_lines(lines)
        if title == "The Real Thesis Of Investment Philosophies 2026":
            lead = rendered
            continue
        if title == "Argument Spine":
            argument_spine = rendered
            continue
        section_html.append(
            f"""<section class="essay">
      <h2>{esc(title)}</h2>
      {rendered}
    </section>"""
        )
    theme_cards = "".join(
        f"""<article class="card">
      <div class="meta">{len(theme.get('evidence_sessions', []))} sessions</div>
      <h3>{esc(theme['name'])}</h3>
      <p>{esc(theme['summary'])}</p>
    </article>"""
        for theme in themes
    )
    concept_chip = "<span>Concept atlas linked</span>" if has_concepts else ""
    return f"""
    <section class="hero">
      <p class="meta">Long-form synthesis</p>
      <h2>The Real Thesis Of Investment Philosophies 2026</h2>
      {lead}
      <div class="tags">
        <span>{summary['available_transcripts']} transcript-backed sessions</span>
        <span>{summary['total_words']:,} words indexed</span>
        <span>{len(themes)} themes</span>
        {concept_chip}
      </div>
    </section>
    <section class="essay">
      <h2>Argument Spine</h2>
      {argument_spine}
    </section>
    <section class="grid">
      {theme_cards}
    </section>
    {''.join(section_html)}
"""


def concept_index_body(concepts: list[dict[str, Any]]) -> str:
    cards = []
    for concept in concepts:
        session_label = ", ".join(str(x) for x in concept.get("primary_sessions", concept.get("strongest_sessions", [])))
        fallback_slug = concept.get("slug", concept.get("id", "concept"))
        href = Path(concept["site_page"]).name if concept.get("site_page") else f"{fallback_slug}.html"
        title = concept.get("title") or concept.get("name") or fallback_slug
        summary = concept.get("summary", concept.get("meaning", ""))
        why_it_matters = concept.get("why_it_matters", concept.get("importance", ""))
        tags = concept.get("lenses", concept.get("connections", []))
        cards.append(
            f"""<article class="card">
      <div class="meta">Sessions {esc(session_label)}</div>
      <h3><a href="{esc(href)}">{esc(title)}</a></h3>
      <p>{esc(summary)}</p>
      <div class="tags">{''.join(f'<span>{esc(item)}</span>' for item in tags[:5])}</div>
      <p><strong>Why it matters:</strong> {esc(why_it_matters)}</p>
    </article>"""
        )
    return (
        '<section class="hero">'
        '<p>This concept atlas turns the course into a reusable idea system. Each concept page keeps the big picture visible: investing style, market behavior, timing, crowding, trust, alternatives, and portfolio fit.</p>'
        f'<p>{len(concepts)} concept pages tied to transcript-backed course themes and sessions.</p>'
        "</section>"
        + '<section class="grid">'
        + "".join(cards)
        + "</section>"
    )


def concept_page_body(concept: dict[str, Any]) -> str:
    session_label = ", ".join(str(x) for x in concept.get("primary_sessions", concept.get("strongest_sessions", [])))
    frames = concept.get("analytical_frames", [])
    subthemes = concept.get("subtheme_refs", [])
    broader_patterns = concept.get("broader_patterns", [])
    applied_uses = concept.get("applied_uses", [])
    fallback_slug = concept.get("slug", concept.get("id", "concept"))
    title = concept.get("title") or concept.get("name") or fallback_slug
    summary = concept.get("summary", concept.get("meaning", ""))
    core_idea = concept.get("core_idea", concept.get("meaning", summary))
    why_it_matters = concept.get("why_it_matters", concept.get("importance", ""))
    if not frames:
        frames = [
            {"title": "Meaning", "text": concept.get("meaning", summary)},
            {"title": "Development", "text": concept.get("development", why_it_matters)},
        ]
    if not broader_patterns:
        broader_patterns = concept.get("common_mistakes", [])
    if not applied_uses:
        applied_uses = concept.get("connections", [])
    return f"""
    <section class="hero">
      <p class="meta">Concept Page</p>
      <h2>{esc(title)}</h2>
      <p>{esc(summary)}</p>
      <div class="tags">
        <span>Primary sessions: {esc(session_label)}</span>
        {''.join(f'<span>{esc(item)}</span>' for item in concept.get('lenses', concept.get('connections', [])[:4]))}
      </div>
    </section>
    <section class="essay">
      <h2>Core Idea</h2>
      <p>{esc(core_idea)}</p>
    </section>
    <section class="grid">
      {''.join(f'<article class="card"><h3>{esc(frame["title"])}</h3><p>{esc(frame["text"])}</p></article>' for frame in frames)}
    </section>
    <section class="essay">
      <h2>Why It Matters</h2>
      <p>{esc(why_it_matters)}</p>
    </section>
    <section class="grid">
      <article class="card">
        <div class="meta">Linked Subthemes</div>
        <ul>{''.join(f'<li>{esc(item)}</li>' for item in subthemes)}</ul>
      </article>
      <article class="card">
        <div class="meta">Broader Patterns</div>
        <ul>{''.join(f'<li>{esc(item)}</li>' for item in broader_patterns)}</ul>
      </article>
    </section>
    <section class="essay">
      <h2>Applied Uses</h2>
      <ul>{''.join(f'<li>{esc(item)}</li>' for item in applied_uses)}</ul>
    </section>
"""


def build(course_root: Path) -> None:
    manifest = load_json(course_root / "raw-material/youtube/course-manifest.json")
    summary = load_json(course_root / "raw-material/youtube/summary.json")
    transcript_index = load_json(course_root / "raw-material/youtube/transcript-index.json")
    theme_map = load_json(course_root / "analysis/themes-and-subthemes.json")
    themes = theme_map["themes"]
    concepts_path = course_root / "analysis/concepts.json"
    if concepts_path.exists():
        concept_data = load_json(concepts_path)
        concepts = concept_data.get("concepts", []) if isinstance(concept_data, dict) else concept_data
    else:
        concepts = []
    has_concepts = bool(concepts)
    thesis_markdown_path = course_root / "analysis/course-thesis.md"

    sessions = []
    for record in transcript_index:
        text_ref = record.get("clean_txt")
        text_path = course_root / text_ref if text_ref else None
        text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path and text_path.is_file() else ""
        combined = f"{record.get('title', '')}\n{text}"
        theme, subtheme = classify(record, combined, themes)
        top_terms = [term for term, _ in Counter(tokenize(combined)).most_common(10)]
        summary_line = first_sentence(text)
        brief = (
            f"This session sits inside {theme['name']} and is best read through {subtheme['name']}. "
            f"It focuses on {', '.join(top_terms[:4]) or 'the core course vocabulary'} and pushes the course one step further from framing into application."
            if record.get("transcript_status") == "available"
            else f"This playlist entry currently has no transcript, so it is carried as a structural part of {theme['name']} rather than a transcript-backed discussion surface."
        )
        sessions.append(
            {
                **record,
                "theme_id": theme["id"],
                "theme_name": theme["name"],
                "subtheme_name": subtheme["name"],
                "summary": summary_line,
                "brief": brief,
                "discussion": "",
                "top_terms": top_terms,
            }
        )

    for item in sessions:
        item["discussion"] = discussion_text(item)

    analysis_dir = course_root / "analysis"
    site_dir = course_root / "site"
    site_dir.mkdir(parents=True, exist_ok=True)
    write_styles(site_dir)
    write_json(analysis_dir / "sessions.json", sessions)
    write_json(
        analysis_dir / "discussions.json",
        [
            {
                "session": item["index"],
                "title": item["title"],
                "theme": item["theme_name"],
                "subtheme": item["subtheme_name"],
                "discussion": item["discussion"],
                "url": item["url"],
            }
            for item in sessions
        ],
    )
    write_text(analysis_dir / "session-briefs.md", session_briefs_markdown(manifest["title"], sessions))

    home = f"""
    <section class="hero">
      <p>{esc(manifest['title'])} now has a transcript-backed session, theme, subtheme, and discussion layer wrapped around the existing course overview, thesis, and concept work.</p>
      <p>{summary['videos']} videos indexed · {summary['available_transcripts']} transcripts · {summary['total_words']:,} words · {len(themes)} themes.</p>
      <p><a class="button" href="themes.html">Browse themes</a>{' <a class="button" href="concepts/index.html">Browse concepts</a>' if has_concepts else ''} <a class="button" href="discussions.html">Read discussions</a> <a class="button" href="sessions.html">Browse sessions</a></p>
    </section>
    <section class="grid">{''.join(f'<article class="card"><div class="meta">{len(t.get("evidence_sessions", []))} anchor sessions</div><h3>{esc(t["name"])}</h3><p>{esc(t["summary"])}</p></article>' for t in themes)}</section>
"""
    write_text(site_dir / "index.html", html_page(f"{manifest['title']} - Course Research Overview", home, "Overview", with_concepts=has_concepts))

    thesis_path = site_dir / "course-thesis.html"
    thesis_body = (
        thesis_body_from_markdown(thesis_markdown_path, summary, themes, has_concepts)
        if thesis_markdown_path.exists()
        else f'<section class="essay"><h2>Course Thesis</h2><p>{esc("This course has not yet been given a richer thesis page, but it now has transcript-backed session, theme, and discussion navigation.")}</p></section>'
    )
    write_text(
        thesis_path,
        html_page(
            f"{manifest['title']} - Course Thesis",
            thesis_body,
            "Thesis",
            with_concepts=has_concepts,
        ),
    )

    theme_body = "<section class=\"grid\">" + "".join(
        f"""<article class="card">
      <div class="meta">{', '.join(str(x) for x in theme.get('evidence_sessions', []))}</div>
      <h3>{esc(theme['name'])}</h3>
      <p>{esc(theme['summary'])}</p>
      <div class="tags">{''.join(f'<span>{esc(l)}</span>' for l in theme.get('lenses', []))}</div>
    </article>"""
        for theme in themes
    ) + "</section>"
    write_text(site_dir / "themes.html", html_page(f"{manifest['title']} - Themes", theme_body, "Themes", with_concepts=has_concepts))

    subtheme_rows = []
    for theme in themes:
        for sub in theme.get("subthemes", []):
            subtheme_rows.append(
                f"""<article class="row">
      <div class="meta">{esc(theme['name'])} · sessions {', '.join(str(x) for x in sub.get('evidence_sessions', []))}</div>
      <strong>{esc(sub['name'])}</strong>
      <p>{esc(sub['summary'])}</p>
    </article>"""
            )
    write_text(site_dir / "subthemes.html", html_page(f"{manifest['title']} - Subthemes", "<section class=\"list\">" + "".join(subtheme_rows) + "</section>", "Subthemes", with_concepts=has_concepts))

    discussions_body = "<section class=\"list\">" + "".join(
        f"""<article class="row">
      <div class="meta">Session {item['index']:02d} · {esc(item['theme_name'])} · {esc(item['subtheme_name'])}</div>
      <strong>{esc(item['title'])}</strong>
      <p>{esc(item['discussion'])}</p>
      <a href="{esc(item['url'])}">YouTube</a>
    </article>"""
        for item in sessions
    ) + "</section>"
    write_text(site_dir / "discussions.html", html_page(f"{manifest['title']} - Discussions", discussions_body, "Discussions", with_concepts=has_concepts))

    session_body = "<section class=\"grid\">" + "".join(
        f"""<article class="card">
      <div class="meta">Session {item['index']:02d} · {item.get('word_count', 0):,} words</div>
      <h3>{esc(item['title'])}</h3>
      <p>{esc(item['summary'])}</p>
      <div class="tags"><span>{esc(item['theme_name'])}</span><span>{esc(item['subtheme_name'])}</span></div>
      <a href="{esc(item['url'])}">YouTube</a>
    </article>"""
        for item in sessions
    ) + "</section>"
    write_text(site_dir / "sessions.html", html_page(f"{manifest['title']} - Sessions", session_body, "Sessions", with_concepts=has_concepts))

    if has_concepts:
        concepts_dir = site_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            concepts_dir / "index.html",
            html_page(
                f"{manifest['title']} - Concepts",
                concept_index_body(concepts),
                "Concepts",
                with_concepts=True,
                nav_prefix="../",
                asset_prefix="../",
            ),
        )
        for concept in concepts:
            concept_slug = concept.get("slug") or concept.get("id") or "concept"
            concept_title = concept.get("title") or concept.get("name") or concept_slug
            concept_filename = Path(concept["site_page"]).name if concept.get("site_page") else f"{concept_slug}.html"
            write_text(
                concepts_dir / concept_filename,
                html_page(
                    f"{manifest['title']} - {concept_title}",
                    concept_page_body(concept),
                    "Concepts",
                    with_concepts=True,
                    nav_prefix="../",
                    asset_prefix="../",
                ),
            )

    print(f"built atlas extensions for {manifest['title']}: {len(sessions)} sessions, {len(themes)} themes")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build transcript-backed session, theme, and discussion extensions for an existing course atlas.")
    parser.add_argument("--course-root", required=True, type=Path)
    args = parser.parse_args()
    build(args.course_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
