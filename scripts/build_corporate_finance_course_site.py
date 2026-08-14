#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from concept_enrichment import enrichment_html, load_enrichment


@dataclass(frozen=True)
class ThemeRule:
    slug: str
    name: str
    thesis: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class ConceptRule:
    slug: str
    name: str
    theme_slug: str
    meaning: str
    importance: str
    development: str
    mistakes: tuple[str, ...]
    connections: tuple[str, ...]
    keywords: tuple[str, ...]


THEMES: tuple[ThemeRule, ...] = (
    ThemeRule(
        "objective-function",
        "The Objective Function",
        "Corporate finance starts by asking what a business should maximize, who gets to decide, and what happens when the objective is bent toward other stakeholder claims.",
        ("objective", "stockholder", "shareholder", "stakeholder", "esg", "governance", "end game", "sustainability"),
    ),
    ThemeRule(
        "risk-and-hurdle-rates",
        "Risk and Hurdle Rates",
        "The cost of capital is built from riskfree rates, equity risk premiums, betas, default spreads, and financing costs rather than taken as a spreadsheet input.",
        ("riskfree", "risk free", "equity risk premium", "premium", "beta", "cost of equity", "cost of debt", "hurdle", "default spread", "rating"),
    ),
    ThemeRule(
        "investment-decision",
        "Investment Decision",
        "Good projects are judged on incremental cash flows, time-weighted returns, side costs, side benefits, real options, and post-mortems rather than accounting earnings alone.",
        ("investment", "incremental", "cash flow", "return", "npv", "project", "side cost", "side benefit", "real option", "post-mortem", "celsius"),
    ),
    ThemeRule(
        "financing-mix",
        "Financing Mix",
        "Debt is useful only up to the point where tax benefits, default risk, agency costs, flexibility, and business risk stop improving firm value.",
        ("debt", "equity", "financing", "tradeoff", "cost of capital", "apv", "peer group", "debt mix", "tax benefit", "bankruptcy"),
    ),
    ThemeRule(
        "debt-design",
        "Debt Design",
        "The right debt instrument should match the business: currency, maturity, fixed versus floating rate, and commodity exposure should reflect operating cash flows.",
        ("debt design", "duration", "maturity", "currency", "fixed", "floating", "convertible", "bond", "loan", "cash flow matching"),
    ),
    ThemeRule(
        "dividends-and-cash-return",
        "Dividends and Cash Return",
        "Cash return policy is a discipline problem: compare cash generated, reinvestment needs, trust in management, taxes, buybacks, and dividends.",
        ("dividend", "cash return", "buyback", "payout", "cash", "stock buyback", "special dividend", "return cash"),
    ),
    ThemeRule(
        "valuation-closure",
        "Valuation as the Final Integration",
        "The course closes by tying objective, risk, investment quality, capital structure, and payout into valuation.",
        ("valuation", "value", "terminal", "growth", "discount", "final frontier", "dcf", "free cash flow"),
    ),
)


SUBTHEME_RULES: dict[str, tuple[tuple[str, str, tuple[str, ...]], ...]] = {
    "objective-function": (
        ("corporate-governance", "Corporate governance and control", ("governance", "board", "ceo", "power", "control", "activist")),
        ("stakeholders-and-esg", "Stakeholders, sustainability, and ESG", ("stakeholder", "esg", "sustainability", "social", "environment")),
        ("business-end-game", "The end game in business", ("end game", "objective", "maximize", "business")),
    ),
    "risk-and-hurdle-rates": (
        ("riskfree-rates", "Riskfree rates", ("riskfree", "risk free", "default free", "currency")),
        ("equity-risk-premiums", "Equity risk premiums", ("equity risk premium", "erp", "premium", "country risk")),
        ("bottom-up-betas", "Bottom-up betas", ("bottom up", "beta", "regression", "private company", "unlevered")),
        ("cost-of-debt", "Cost of debt", ("cost of debt", "default spread", "rating", "interest coverage")),
    ),
    "investment-decision": (
        ("incremental-cash-flows", "Incremental cash flows", ("incremental", "cash flow", "sunk cost", "working capital")),
        ("return-measures", "Return measures", ("return", "time weighted", "accounting", "irr", "roic")),
        ("side-costs-benefits", "Side costs and benefits", ("side cost", "side benefit", "cannibalization", "synergy")),
        ("real-options", "Real options and post-mortems", ("real option", "option", "post-mortem", "celsius")),
    ),
    "financing-mix": (
        ("debt-equity-tradeoff", "Debt-equity tradeoff", ("debt equity", "tradeoff", "tax benefit", "bankruptcy")),
        ("cost-of-capital-optimization", "Cost of capital optimization", ("optimize", "cost of capital", "debt ratio", "firm value")),
        ("apv-peer-group", "APV and peer group approaches", ("apv", "adjusted present value", "peer group", "comparable")),
    ),
    "debt-design": (
        ("cash-flow-matching", "Cash-flow matching", ("match", "cash flow", "duration", "maturity")),
        ("debt-terms", "Debt terms and structure", ("fixed", "floating", "currency", "convertible", "commodity")),
    ),
    "dividends-and-cash-return": (
        ("dividend-tradeoffs", "Dividend tradeoffs", ("dividend trade", "tax", "clientele", "signaling")),
        ("cash-return-discipline", "Assessing cash return policy", ("cash return", "buyback", "payout", "trust", "management")),
    ),
    "valuation-closure": (
        ("valuation-synthesis", "Valuation synthesis", ("valuation", "discount", "growth", "cash flow", "terminal")),
        ("course-end-game", "Course end game", ("end game", "closure", "final", "wrap")),
    ),
}


CONCEPTS: tuple[ConceptRule, ...] = (
    ConceptRule(
        "objective-function",
        "Objective function",
        "objective-function",
        "The operating target for corporate finance: make decisions that increase the value of the business, while being explicit about whose claim is being maximized.",
        "Without an objective function, investment, financing, and payout decisions become political preferences with numbers attached.",
        "Damodaran opens the course by forcing the end-game question before any spreadsheet mechanics: managers need a target before they can judge tradeoffs.",
        ("Treating value maximization as a slogan instead of a discipline.", "Changing the objective when the answer becomes uncomfortable."),
        ("corporate-governance", "stakeholders-sustainability-and-esg", "valuation-closure"),
        ("objective", "maximize", "maximization", "end game", "business", "stockholder", "shareholder", "value"),
    ),
    ConceptRule(
        "corporate-governance",
        "Corporate governance",
        "objective-function",
        "The system that determines whether managers act for owners, themselves, or other power centers around the firm.",
        "Governance is the enforcement mechanism behind the objective function; weak governance lets value-destroying choices persist.",
        "The early governance sessions turn abstract value maximization into a control problem: who has power, how is it checked, and what happens when nobody is watching?",
        ("Assuming boards automatically protect shareholders.", "Ignoring how dispersed ownership weakens discipline."),
        ("objective-function", "debt-equity-tradeoff", "cash-return-policy"),
        ("governance", "board", "ceo", "manager", "management", "power", "control", "stockholder", "shareholder"),
    ),
    ConceptRule(
        "stakeholders-sustainability-and-esg",
        "Stakeholders, sustainability, and ESG",
        "objective-function",
        "The claim that firms should consider employees, customers, society, sustainability, and ESG goals alongside or inside value creation.",
        "These claims matter because they can either discipline long-term thinking or become vague cover for unaccountable management choices.",
        "Damodaran treats stakeholder language as a test of clarity: what exactly is being optimized, who measures it, and who pays when goals conflict?",
        ("Using ESG as an unmeasured virtue label.", "Pretending stakeholder tradeoffs have no cost."),
        ("objective-function", "corporate-governance", "valuation-closure"),
        ("stakeholder", "stakeholders", "sustainability", "sustainable", "esg", "social", "environment", "purpose"),
    ),
    ConceptRule(
        "riskfree-rates",
        "Riskfree rates",
        "risk-and-hurdle-rates",
        "The base rate for discounting cash flows in a currency, stripped of default risk and matched to the currency of the cash flows.",
        "Every hurdle rate starts here; a wrong riskfree rate contaminates valuation, project analysis, and capital structure choices.",
        "The risk block begins by separating currency, inflation, default risk, and maturity so the discount rate has a defensible anchor.",
        ("Using the government bond yield mechanically even when default risk exists.", "Mixing a dollar riskfree rate with non-dollar cash flows."),
        ("equity-risk-premiums", "cost-of-equity", "valuation-closure"),
        ("riskfree", "risk free", "default free", "currency", "treasury", "government bond", "inflation"),
    ),
    ConceptRule(
        "equity-risk-premiums",
        "Equity risk premiums",
        "risk-and-hurdle-rates",
        "The extra return investors demand for holding equities instead of a riskfree asset.",
        "The ERP is one of the largest moving parts in cost of equity, and small changes can swing investment and valuation conclusions.",
        "Damodaran develops the premium as a market price of risk rather than a fixed historical constant, with country risk and forward-looking estimates entering the discussion.",
        ("Blindly using long historical averages.", "Ignoring country risk or current market pricing."),
        ("riskfree-rates", "cost-of-equity", "bottom-up-betas"),
        ("equity risk premium", "erp", "premium", "country risk", "implied premium", "market risk"),
    ),
    ConceptRule(
        "bottom-up-betas",
        "Bottom-up betas",
        "risk-and-hurdle-rates",
        "A beta estimated from the business or businesses a firm operates in, adjusted for operating and financial leverage.",
        "Bottom-up betas are Damodaran's answer to noisy regressions, private companies, changing business mixes, and thin trading.",
        "The beta sessions move from market regressions toward business-risk estimation, using comparable firms and leverage adjustments.",
        ("Trusting a single regression beta without asking what business it measures.", "Forgetting to unlever and relever betas when financial leverage changes."),
        ("cost-of-equity", "hurdle-rates", "debt-equity-tradeoff"),
        ("bottom up", "bottom-up", "beta", "betas", "regression", "unlevered", "levered", "private company"),
    ),
    ConceptRule(
        "cost-of-equity",
        "Cost of equity",
        "risk-and-hurdle-rates",
        "The return equity investors require for bearing the risk of the firm's residual cash flows.",
        "It is the equity hurdle rate for projects and the equity discount rate in valuation.",
        "The course builds cost of equity from riskfree rates, premiums, and betas, turning risk into an explicit required return.",
        ("Treating cost of equity as what the company wants to earn.", "Using one corporate cost of equity for projects with different risk."),
        ("riskfree-rates", "equity-risk-premiums", "bottom-up-betas", "hurdle-rates"),
        ("cost of equity", "expected return", "required return", "capm", "beta", "premium"),
    ),
    ConceptRule(
        "cost-of-debt",
        "Cost of debt",
        "risk-and-hurdle-rates",
        "The current market cost of borrowing, driven by default risk, tax effects, maturity, and currency.",
        "Debt is not cheap just because coupon rates are low; the relevant cost is the current pre-tax and after-tax cost of borrowing.",
        "Damodaran connects ratings, default spreads, interest coverage, and taxes to make debt cost a live financing input.",
        ("Using book interest expense divided by book debt.", "Ignoring default risk or tax shields."),
        ("hurdle-rates", "debt-equity-tradeoff", "cost-of-capital-optimization"),
        ("cost of debt", "default spread", "rating", "ratings", "interest coverage", "tax rate", "after-tax"),
    ),
    ConceptRule(
        "hurdle-rates",
        "Hurdle rates",
        "risk-and-hurdle-rates",
        "The minimum required return for an investment, matched to its risk, currency, and financing mix.",
        "Hurdle rates decide what the firm says yes or no to; they translate risk into capital allocation discipline.",
        "The course treats hurdle rates as built objects: riskfree rate, risk premium, beta, debt cost, and capital mix must all be internally consistent.",
        ("Using the same hurdle rate for every project.", "Confusing accounting return targets with risk-adjusted required returns."),
        ("cost-of-equity", "cost-of-debt", "incremental-cash-flows", "project-returns"),
        ("hurdle", "hurdle rate", "cost of capital", "required return", "discount rate", "project risk"),
    ),
    ConceptRule(
        "incremental-cash-flows",
        "Incremental cash flows",
        "investment-decision",
        "The cash flows that change because the project is taken, including working capital, taxes, side effects, and opportunity costs.",
        "Project analysis lives or dies on incrementality; accounting categories and sunk costs can make bad projects look good or good projects look bad.",
        "The investment section shifts attention from reported earnings to actual cash-flow consequences of a decision.",
        ("Counting sunk costs.", "Ignoring opportunity costs, working capital, or cannibalization."),
        ("project-returns", "side-costs-and-side-benefits", "valuation-closure"),
        ("incremental", "cash flow", "cash flows", "sunk cost", "opportunity cost", "working capital", "tax"),
    ),
    ConceptRule(
        "project-returns",
        "Project returns",
        "investment-decision",
        "Measures used to judge whether projects clear their hurdle rates and create value.",
        "Return measures are useful only when they are cash-flow based, time-consistent, and compared to the right risk-adjusted hurdle rate.",
        "Damodaran uses the project-return sessions to separate investment quality from accounting appearance.",
        ("Comparing accounting returns to market hurdle rates.", "Using IRR mechanically when scale or timing distorts the answer."),
        ("hurdle-rates", "incremental-cash-flows", "real-options"),
        ("return", "returns", "irr", "npv", "roic", "accounting return", "time weighted", "project"),
    ),
    ConceptRule(
        "side-costs-and-side-benefits",
        "Side costs and side benefits",
        "investment-decision",
        "The indirect effects a project imposes on the rest of the business, including cannibalization, synergies, brand effects, and strategic spillovers.",
        "They are where project analysis stops being isolated spreadsheet work and becomes firm-level capital allocation.",
        "The course explicitly asks students to bring side consequences into project choice instead of pretending each investment stands alone.",
        ("Treating synergy as a free add-on.", "Ignoring cannibalization because it is politically inconvenient."),
        ("incremental-cash-flows", "project-returns", "real-options"),
        ("side cost", "side costs", "side benefit", "side benefits", "cannibalization", "synergy", "spillover"),
    ),
    ConceptRule(
        "real-options",
        "Real options",
        "investment-decision",
        "Managerial flexibility embedded in projects: the option to expand, abandon, delay, or adapt as uncertainty resolves.",
        "Real options matter when static NPV misses the value of learning and future choice.",
        "The Celsius and post-mortem material uses real options to show when uncertainty can create value rather than merely risk.",
        ("Calling every uncertain project an option.", "Double-counting option value already embedded in cash-flow forecasts."),
        ("project-returns", "side-costs-and-side-benefits", "valuation-closure"),
        ("real option", "real options", "option", "abandon", "delay", "expand", "uncertainty", "celsius", "post-mortem"),
    ),
    ConceptRule(
        "debt-equity-tradeoff",
        "Debt-equity tradeoff",
        "financing-mix",
        "The balance between the benefits of debt, especially tax shields and discipline, and its costs, especially distress, agency conflicts, and lost flexibility.",
        "Capital structure is not about liking debt or equity; it is about finding where financing choices increase firm value.",
        "The financing block begins with the tradeoff and then tests it through cost-of-capital, APV, peer-group, and design lenses.",
        ("Assuming more debt is always cheaper.", "Ignoring business risk and flexibility needs."),
        ("cost-of-capital-optimization", "apv-and-peer-group-financing", "debt-design"),
        ("debt equity", "debt-equity", "tradeoff", "tax benefit", "bankruptcy", "distress", "agency", "flexibility"),
    ),
    ConceptRule(
        "cost-of-capital-optimization",
        "Cost of capital optimization",
        "financing-mix",
        "Estimating the debt ratio that minimizes the weighted average cost of capital and maximizes firm value.",
        "It gives the financing decision an explicit value test instead of relying on peer imitation or managerial instinct.",
        "Damodaran walks through changing debt ratios, ratings, debt costs, equity costs, and firm value to locate a financing mix.",
        ("Optimizing WACC without updating default risk.", "Treating the current debt ratio as automatically optimal."),
        ("cost-of-debt", "debt-equity-tradeoff", "apv-and-peer-group-financing"),
        ("cost of capital", "optimize", "optimization", "debt ratio", "wacc", "firm value", "rating"),
    ),
    ConceptRule(
        "apv-and-peer-group-financing",
        "APV and peer group financing approaches",
        "financing-mix",
        "Alternative ways to assess financing mix: APV values tax benefits and distress costs directly, while peer analysis uses comparable-company behavior as evidence.",
        "They check the cost-of-capital approach from different angles and reveal when market practice or model assumptions deserve skepticism.",
        "The course uses APV and peer groups after WACC optimization to show that financing decisions can be triangulated rather than dictated by one model.",
        ("Using peers as proof instead of evidence.", "Forgetting that APV still requires judgments about debt benefits and costs."),
        ("debt-equity-tradeoff", "cost-of-capital-optimization", "debt-design"),
        ("apv", "adjusted present value", "peer group", "comparable", "financing mix", "tax benefit"),
    ),
    ConceptRule(
        "debt-design",
        "Debt design",
        "debt-design",
        "Choosing the currency, maturity, rate structure, and covenants of debt so financing matches the firm's asset cash flows.",
        "Even the right amount of debt can be dangerous if it is the wrong kind of debt.",
        "After optimizing debt levels, Damodaran turns to debt design: match financing to how the business earns cash.",
        ("Stopping at the debt ratio.", "Borrowing in a currency or maturity that does not match operating cash flows."),
        ("debt-equity-tradeoff", "apv-and-peer-group-financing", "cash-return-policy"),
        ("debt design", "duration", "maturity", "currency", "fixed", "floating", "bond", "loan", "cash flow matching"),
    ),
    ConceptRule(
        "dividends-and-buybacks",
        "Dividends and buybacks",
        "dividends-and-cash-return",
        "The two main ways firms return cash to shareholders, each carrying different tax, signaling, flexibility, and trust implications.",
        "Payout policy is where excess cash, reinvestment discipline, and shareholder trust become visible.",
        "The payout block starts with dividends and buybacks as tools, then asks when returning cash is the best use of corporate resources.",
        ("Treating dividends as automatically good.", "Treating buybacks as automatically manipulative or automatically value creating."),
        ("cash-return-policy", "corporate-governance", "valuation-closure"),
        ("dividend", "dividends", "buyback", "buybacks", "stock buyback", "payout", "cash return"),
    ),
    ConceptRule(
        "cash-return-policy",
        "Cash return policy",
        "dividends-and-cash-return",
        "The broader discipline of deciding how much cash to retain, reinvest, or return to owners.",
        "Cash return policy tests whether managers can be trusted to reinvest well or should be forced to give capital back.",
        "Damodaran frames payout as a consequence of investment opportunity, financing needs, taxes, and governance trust.",
        ("Letting cash accumulate without a reinvestment case.", "Using payout policy to hide weak investment discipline."),
        ("dividends-and-buybacks", "corporate-governance", "objective-function"),
        ("cash return", "return cash", "payout", "dividend", "buyback", "reinvestment", "cash", "trust"),
    ),
    ConceptRule(
        "valuation-closure",
        "Valuation closure",
        "valuation-closure",
        "The integration point where objective function, risk, investment quality, financing mix, and payout policy are converted into value.",
        "Valuation is the final audit: every corporate finance choice should eventually show up in expected cash flows, growth, risk, or terminal value.",
        "The closing sessions make valuation the course's synthesis rather than a separate topic bolted on at the end.",
        ("Treating valuation as only a modeling exercise.", "Ignoring how earlier corporate finance choices feed cash flows, risk, and growth."),
        ("objective-function", "hurdle-rates", "incremental-cash-flows", "debt-equity-tradeoff", "cash-return-policy"),
        ("valuation", "value", "dcf", "discount", "growth", "terminal", "free cash flow", "final frontier"),
    ),
)


STOPWORDS = {
    "about", "after", "again", "also", "because", "before", "being", "class", "could", "course", "does", "going",
    "have", "here", "just", "like", "look", "more", "much", "need", "right", "session", "should", "take", "than",
    "that", "their", "them", "then", "there", "these", "thing", "think", "this", "those", "through", "time", "today",
    "want", "what", "when", "where", "which", "will", "with", "would", "your",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return value.strip("-") or "item"


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z\-']{2,}", text.lower()) if w not in STOPWORDS]


def first_sentence(text: str, limit: int = 260) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return "Transcript text is not available for this session."
    sentence = compact[:limit]
    for index, char in enumerate(compact[:limit], 1):
        if index >= 80 and char in ".!?":
            sentence = compact[:index]
            break
    return sentence[:limit].rstrip()


def keyword_score(text: str, keywords: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(lowered.count(keyword) for keyword in keywords)


def clip_words(text: str, limit: int = 34) -> str:
    words = re.sub(r"\s+", " ", text).strip().split()
    if len(words) <= limit:
        return " ".join(words)
    return " ".join(words[:limit]).rstrip(" ,;:") + "..."


def classify_theme(text: str) -> ThemeRule:
    scored = sorted(((keyword_score(text, rule.keywords), rule) for rule in THEMES), key=lambda item: item[0], reverse=True)
    return scored[0][1] if scored and scored[0][0] > 0 else THEMES[0]


def classify_subtheme(theme_slug: str, text: str) -> tuple[str, str]:
    candidates = SUBTHEME_RULES.get(theme_slug, ())
    if not candidates:
        return f"{theme_slug}-general", "General discussion"
    scored = sorted(((keyword_score(text, keywords), slug, name) for slug, name, keywords in candidates), reverse=True)
    _, slug, name = scored[0]
    return slug, name


def load_cue_excerpt(course_root: Path, session: dict[str, Any], keywords: tuple[str, ...]) -> dict[str, Any]:
    cue_ref = session.get("cue_json")
    cue_path = course_root / cue_ref if cue_ref else None
    if not cue_path or not cue_path.is_file():
        return {"excerpt": session.get("summary", ""), "start_seconds": None, "end_seconds": None}
    cues = load_json(cue_path)
    best = None
    for cue in cues:
        score = keyword_score(cue.get("text", ""), keywords)
        if best is None or score > best[0]:
            best = (score, cue)
    if best and best[0] > 0:
        cue = best[1]
        return {
            "excerpt": clip_words(cue.get("text", ""), 42),
            "start_seconds": cue.get("start_seconds"),
            "end_seconds": cue.get("end_seconds"),
        }
    return {"excerpt": session.get("summary", ""), "start_seconds": None, "end_seconds": None}


def build_concepts(course_root: Path, sessions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _enrichment = load_enrichment(course_root)
    concepts: list[dict[str, Any]] = []
    evidence_map: dict[str, Any] = {"concepts": {}}
    session_texts: dict[int, str] = {}
    for session in sessions:
        text_ref = session.get("clean_txt")
        text_path = course_root / text_ref if text_ref else None
        text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path and text_path.is_file() else ""
        session_texts[int(session["index"])] = f"{session.get('title', '')}\n{text}"

    for rule in CONCEPTS:
        scored = []
        for session in sessions:
            text = session_texts[int(session["index"])]
            score = keyword_score(text, rule.keywords)
            if score > 0:
                scored.append((score, session))
        scored.sort(key=lambda item: item[0], reverse=True)
        evidence = []
        for score, session in scored[:5]:
            excerpt = load_cue_excerpt(course_root, session, rule.keywords)
            evidence.append(
                {
                    "session": session["index"],
                    "title": session["title"],
                    "url": session["url"],
                    "score": score,
                    **excerpt,
                }
            )
        concept = {
            "slug": rule.slug,
            "name": rule.name,
            "theme_slug": rule.theme_slug,
            "meaning": rule.meaning,
            "importance": rule.importance,
            "development": rule.development,
            "common_mistakes": list(rule.mistakes),
            "connections": list(rule.connections),
            "keywords": list(rule.keywords),
            "strongest_sessions": [item["session"] for item in evidence],
            "evidence": evidence,
            "worked_example": _enrichment.get(rule.slug, {}).get("worked_example", ""),
            "failure_boundary": _enrichment.get(rule.slug, {}).get("failure_boundary", ""),
        }
        concepts.append(concept)
        evidence_map["concepts"][rule.slug] = evidence
    return concepts, evidence_map


def html_page(title: str, body: str, current: str = "", *, asset_prefix: str = "") -> str:
    nav = [
        ("index.html", "Overview"),
        ("course-thesis.html", "Thesis"),
        ("themes.html", "Themes"),
        ("subthemes.html", "Subthemes"),
        ("concepts/index.html", "Concepts"),
        ("evidence.html", "Evidence"),
        ("discussions.html", "Discussions"),
        ("sessions.html", "Sessions"),
    ]
    links = "\n".join(
        f'<a class="{"active" if label == current else ""}" href="{asset_prefix}{href}">{label}</a>' for href, label in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{asset_prefix}assets/styles.css">
</head>
<body>
  <header class="top">
    <div>
      <p class="eyebrow">Aswath Damodaran course atlas</p>
      <h1>{html.escape(title)}</h1>
    </div>
    <nav>{links}</nav>
  </header>
  <main>
{body}
  </main>
</body>
</html>
"""


def esc(value: Any) -> str:
    return html.escape(str(value))


def session_card(record: dict[str, Any]) -> str:
    return f"""
    <article class="card">
      <div class="meta">Session {record["index"]:02d} · {record.get("word_count", 0):,} words</div>
      <h3>{esc(record["title"])}</h3>
      <p>{esc(record["summary"])}</p>
      <div class="tags"><span>{esc(record["theme_name"])}</span><span>{esc(record["subtheme_name"])}</span></div>
      <a href="{esc(record["url"])}">YouTube</a>
    </article>"""


def build(course_root: Path) -> None:
    manifest = load_json(course_root / "raw-material/youtube/course-manifest.json")
    transcript_index = load_json(course_root / "raw-material/youtube/transcript-index.json")
    analysis_dir = course_root / "analysis"
    site_dir = course_root / "site"
    (site_dir / "assets").mkdir(parents=True, exist_ok=True)

    enriched: list[dict[str, Any]] = []
    for record in transcript_index:
        text_ref = record.get("clean_txt")
        text_path = course_root / text_ref if text_ref else None
        text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path and text_path.is_file() else ""
        combined = f"{record.get('title', '')}\n{text}"
        theme = classify_theme(combined)
        subtheme_slug, subtheme_name = classify_subtheme(theme.slug, combined)
        terms = Counter(tokenize(combined)).most_common(10)
        enriched.append(
            {
                **record,
                "theme_slug": theme.slug,
                "theme_name": theme.name,
                "subtheme_slug": subtheme_slug,
                "subtheme_name": subtheme_name,
                "summary": first_sentence(text),
                "top_terms": [term for term, _ in terms],
            }
        )

    themes = []
    for rule in THEMES:
        sessions = [item for item in enriched if item["theme_slug"] == rule.slug]
        if not sessions:
            continue
        themes.append(
            {
                "slug": rule.slug,
                "name": rule.name,
                "thesis": rule.thesis,
                "session_indexes": [item["index"] for item in sessions],
                "session_titles": [item["title"] for item in sessions],
                "evidence_terms": Counter(term for item in sessions for term in item["top_terms"]).most_common(12),
            }
        )

    subthemes = []
    for slug, grouped in sorted(group_by(enriched, "subtheme_slug").items()):
        subthemes.append(
            {
                "slug": slug,
                "name": grouped[0]["subtheme_name"],
                "theme": grouped[0]["theme_name"],
                "session_indexes": [item["index"] for item in grouped],
                "session_titles": [item["title"] for item in grouped],
            }
        )

    discussions = [
        {
            "session": item["index"],
            "title": item["title"],
            "theme": item["theme_name"],
            "subtheme": item["subtheme_name"],
            "discussion": discussion_for(item),
            "url": item["url"],
        }
        for item in enriched
    ]
    concepts, evidence_map = build_concepts(course_root, enriched)

    write_json(analysis_dir / "sessions.json", enriched)
    write_json(analysis_dir / "themes.json", themes)
    write_json(analysis_dir / "subthemes.json", subthemes)
    write_json(analysis_dir / "discussions.json", discussions)
    write_json(analysis_dir / "themes-and-subthemes.json", {"themes": themes, "subthemes": subthemes})
    write_json(analysis_dir / "concepts.json", concepts)
    write_json(analysis_dir / "evidence-map.json", evidence_map)
    write_text(analysis_dir / "course-thesis.md", course_thesis_markdown(enriched, themes, concepts))
    write_text(analysis_dir / "session-briefs.md", session_briefs_markdown(enriched))

    write_site(site_dir, manifest, enriched, themes, subthemes, discussions, concepts, evidence_map)
    print(
        f"built {len(enriched)} sessions, {len(themes)} themes, "
        f"{len(subthemes)} subthemes, {len(concepts)} concepts"
    )


def group_by(items: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        groups.setdefault(item[key], []).append(item)
    return groups


def discussion_for(item: dict[str, Any]) -> str:
    terms = ", ".join(item["top_terms"][:5])
    return (
        f"This session sits inside '{item['theme_name']}' and narrows the course conversation toward "
        f"'{item['subtheme_name']}'. The transcript vocabulary clusters around {terms}, which makes it useful "
        "as evidence for how Damodaran moves from first financial principles into operating choices managers can make."
    )


def course_thesis_markdown(
    sessions: list[dict[str, Any]],
    themes: list[dict[str, Any]],
    concepts: list[dict[str, Any]],
) -> str:
    total_words = sum(item.get("word_count", 0) for item in sessions)
    lines = [
        "# Course Thesis",
        "",
        "Damodaran's Corporate Finance Spring 2025 course is a single argument about capital allocation under constraints. The course starts with the objective function because corporate finance needs a target before it can judge any decision. It then builds the machinery that lets managers act on that target: risk-adjusted hurdle rates, cash-flow based investment tests, financing choices that trade off tax benefits against distress and flexibility costs, debt design that matches the business, payout discipline, and finally valuation as the integration layer.",
        "",
        "The course is not a sequence of disconnected finance formulas. It is a decision architecture. Every major topic asks the same question in a new setting: does this choice increase the value of the business after accounting for risk, timing, side effects, financing consequences, and managerial discipline?",
        "",
        f"This atlas is grounded in {len(sessions)} playlist records, {sum(1 for item in sessions if item.get('transcript_status') == 'available')} transcript-backed sessions, and {total_words:,} transcript words.",
        "",
        "## Argument Spine",
        "",
        "1. Define the end game before choosing tools.",
        "2. Convert risk into hurdle rates that match currency, business risk, and financing mix.",
        "3. Judge projects by incremental cash flows and risk-adjusted returns.",
        "4. Choose a financing mix by comparing debt's benefits with distress, agency, and flexibility costs.",
        "5. Design debt to fit operating cash flows rather than stopping at a target debt ratio.",
        "6. Return cash when managers cannot reinvest it well.",
        "7. Use valuation as the final audit of every corporate finance choice.",
        "",
        "## Themes",
        "",
    ]
    for theme in themes:
        lines.extend(
            [
                f"### {theme['name']}",
                "",
                theme["thesis"],
                "",
                f"Sessions: {', '.join(str(i) for i in theme['session_indexes'])}",
                "",
            ]
        )
    lines.extend(["## Concept Layer", ""])
    for concept in concepts:
        lines.extend(
            [
                f"- **{concept['name']}**: {concept['meaning']}",
            ]
        )
    return "\n".join(lines)


def session_briefs_markdown(sessions: list[dict[str, Any]]) -> str:
    groups = group_by(sessions, "theme_name")
    lines = [
        "# Session Briefs",
        "",
        "Plain-English course map for `Corporate Finance Spring 2025`, generated from the transcript index and organized by the dominant theme assigned to each session.",
        "",
    ]
    for theme_name, grouped in groups.items():
        lines.extend([f"## {theme_name}", ""])
        for item in grouped:
            lines.extend(
                [
                    f"`{item['index']:03d}` {item['title']}  ",
                    session_brief_for(item),
                    "",
                ]
            )
    lines.extend(
        [
            "## High-level course arc",
            "",
            "1. Establish the objective function and governance constraints.",
            "2. Build risk and hurdle-rate inputs.",
            "3. Evaluate investments through incremental cash flows and project returns.",
            "4. Optimize financing mix and debt design.",
            "5. Decide how much cash to return.",
            "6. Close by tying corporate finance choices back to valuation.",
        ]
    )
    return "\n".join(lines)


def session_brief_for(item: dict[str, Any]) -> str:
    title = item["title"].lower()
    if "preview" in title:
        return "A short course preview without an available caption track; it is kept in the playlist index but excluded from transcript-backed evidence."
    if item["theme_slug"] == "objective-function":
        return "This session sets up the course's end-game logic: managers need a clear objective and governance system before investment, financing, and payout tools can be judged."
    if item["theme_slug"] == "risk-and-hurdle-rates":
        return "This session builds the risk-to-return machinery behind hurdle rates, connecting rates, premiums, betas, debt costs, and business risk."
    if item["theme_slug"] == "investment-decision":
        return "This session asks whether projects create value after accounting for incremental cash flows, timing, uncertainty, side effects, and managerial flexibility."
    if item["theme_slug"] == "financing-mix":
        return "This session studies how much debt a firm should use by weighing tax benefits and discipline against distress, agency, and flexibility costs."
    if item["theme_slug"] == "debt-design":
        return "This session moves from how much debt to what kind of debt, matching financing terms to the cash-flow structure of the business."
    if item["theme_slug"] == "dividends-and-cash-return":
        return "This session treats payout as a capital allocation and governance question: keep cash only when managers can reinvest it well."
    if item["theme_slug"] == "valuation-closure":
        return "This session ties the course back to valuation, showing how objective, risk, investment, financing, and payout choices flow into value."
    return item.get("summary", "Transcript-backed session brief unavailable.")


def write_site(
    site_dir: Path,
    manifest: dict[str, Any],
    sessions: list[dict[str, Any]],
    themes: list[dict[str, Any]],
    subthemes: list[dict[str, Any]],
    discussions: list[dict[str, Any]],
    concepts: list[dict[str, Any]],
    evidence_map: dict[str, Any],
) -> None:
    css = """
:root {
  color-scheme: light;
  --ink: #17211c;
  --muted: #5d6a62;
  --line: #d9ded7;
  --paper: #f7f6ef;
  --panel: #ffffff;
  --accent: #176f6b;
  --accent-2: #9b3d2e;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Georgia, 'Times New Roman', serif; color: var(--ink); background: linear-gradient(135deg, #fbfaf4 0%, #eef4ef 58%, #f7eee9 100%); }
.top { display: flex; justify-content: space-between; gap: 24px; align-items: end; padding: 40px min(6vw, 72px) 24px; border-bottom: 1px solid var(--line); }
.eyebrow { margin: 0 0 8px; color: var(--accent-2); text-transform: uppercase; letter-spacing: .08em; font: 700 12px/1.2 ui-sans-serif, system-ui, sans-serif; }
h1 { margin: 0; font-size: clamp(34px, 5vw, 68px); line-height: .95; max-width: 880px; }
h2 { font-size: 30px; margin: 0 0 16px; }
h3 { margin: 8px 0 10px; font-size: 21px; }
p { line-height: 1.6; }
nav { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
nav a, .button { color: var(--ink); text-decoration: none; border: 1px solid var(--line); background: rgba(255,255,255,.72); padding: 8px 11px; border-radius: 4px; font: 700 13px/1 ui-sans-serif, system-ui, sans-serif; }
nav a.active, nav a:hover, .button:hover { background: var(--accent); color: white; border-color: var(--accent); }
main { padding: 34px min(6vw, 72px) 64px; }
.hero { max-width: 920px; font-size: 20px; color: var(--muted); }
.thesis { max-width: 980px; display: grid; gap: 18px; }
.essay { background: rgba(255,255,255,.78); border: 1px solid var(--line); border-radius: 6px; padding: 22px; }
.essay p { margin: 0 0 14px; }
.kicker { font: 700 14px/1.4 ui-sans-serif, system-ui, sans-serif; color: var(--accent); }
.split { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(260px, .8fr); gap: 18px; align-items: start; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 16px; margin-top: 24px; }
.card { background: rgba(255,255,255,.78); border: 1px solid var(--line); border-radius: 6px; padding: 18px; box-shadow: 0 18px 40px rgba(23,33,28,.06); }
.meta { color: var(--accent-2); font: 700 12px/1.4 ui-sans-serif, system-ui, sans-serif; text-transform: uppercase; letter-spacing: .05em; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
.tags span { background: #e8f1ee; color: #14524f; border: 1px solid #cfe2dd; padding: 5px 8px; border-radius: 999px; font: 700 12px/1 ui-sans-serif, system-ui, sans-serif; }
.list { display: grid; gap: 12px; }
.row { background: rgba(255,255,255,.7); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; }
.row strong { display: block; margin-bottom: 6px; }
.evidence { border-left: 4px solid var(--accent); }
.concept-links { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.concept-links a { color: var(--accent); background: #eef6f3; border: 1px solid #cfe2dd; border-radius: 999px; padding: 6px 9px; text-decoration: none; font: 700 12px/1 ui-sans-serif, system-ui, sans-serif; }
ol.arc { padding-left: 22px; line-height: 1.7; }
@media (max-width: 760px) { .top { display: block; } nav { justify-content: flex-start; margin-top: 20px; } .split { grid-template-columns: 1fr; } }
"""
    (site_dir / "assets/styles.css").write_text(css.strip() + "\n", encoding="utf-8")

    total_words = sum(item.get("word_count", 0) for item in sessions)
    home_body = f"""
    <section class="hero">
      <p>{esc(manifest["title"])} is organized as a transcript-backed atlas of Damodaran's spring 2025 corporate finance course: objective function, risk and hurdle rates, investment returns, financing mix, debt design, cash return, and valuation closure.</p>
      <p>{len(sessions)} videos indexed · {total_words:,} transcript words · {len(themes)} themes · {len(subthemes)} subthemes · {len(concepts)} concepts.</p>
      <p><a class="button" href="course-thesis.html">Read the thesis</a> <a class="button" href="concepts/index.html">Browse concepts</a> <a class="button" href="sessions.html">Browse sessions</a></p>
    </section>
    <section class="essay" style="margin-top:24px">
      <p class="kicker">Course argument</p>
      <p>Corporate Finance Spring 2025 is a decision architecture: define the objective, price risk, choose investments by incremental cash flows, pick financing by value impact, design debt to fit the business, return cash when reinvestment is weak, and use valuation as the final audit.</p>
    </section>
    <section class="grid">
      {''.join(f'<article class="card"><div class="meta">{len(t["session_indexes"])} sessions</div><h3>{esc(t["name"])}</h3><p>{esc(t["thesis"])}</p></article>' for t in themes)}
    </section>
"""
    (site_dir / "index.html").write_text(html_page(manifest["title"], home_body, "Overview"), encoding="utf-8")

    thesis_body = f"""
    <section class="thesis">
      <article class="essay">
        <p class="kicker">Long-form synthesis</p>
        <h2>The real thesis of Corporate Finance Spring 2025</h2>
        <p>Damodaran's course is not mainly a tour of corporate finance formulas. It is a sustained argument about how managers should make value-relevant decisions when risk, agency problems, taxes, side effects, financing constraints, and reinvestment limits all collide.</p>
        <p>The course starts with the objective function because the rest of corporate finance has no meaning without a target. It then builds the machinery required to act on that target: hurdle rates, project cash flows, capital structure, debt design, payout policy, and valuation.</p>
      </article>
      <article class="essay">
        <h2>Argument spine</h2>
        <ol class="arc">
          <li>Define the end game before choosing tools.</li>
          <li>Convert risk into hurdle rates matched to currency, business risk, and financing mix.</li>
          <li>Judge investments by incremental cash flows and risk-adjusted returns.</li>
          <li>Use debt only when its benefits exceed distress, agency, and flexibility costs.</li>
          <li>Design debt to fit operating cash flows.</li>
          <li>Return cash when managers cannot reinvest it well.</li>
          <li>Use valuation as the final integration of every corporate finance choice.</li>
        </ol>
      </article>
      <section class="grid">
        {''.join(f'<article class="card"><div class="meta">{len(t["session_indexes"])} sessions</div><h3>{esc(t["name"])}</h3><p>{esc(t["thesis"])}</p></article>' for t in themes)}
      </section>
    </section>
"""
    (site_dir / "course-thesis.html").write_text(
        html_page("Corporate Finance Course Thesis", thesis_body, "Thesis"), encoding="utf-8"
    )

    theme_body = "<section class=\"grid\">" + "".join(
        f"""<article class="card">
      <div class="meta">{len(theme["session_indexes"])} sessions · {', '.join(str(i) for i in theme["session_indexes"])}</div>
      <h3>{esc(theme["name"])}</h3>
      <p>{esc(theme["thesis"])}</p>
      <div class="tags">{''.join(f'<span>{esc(term)}</span>' for term, _ in theme["evidence_terms"][:6])}</div>
    </article>"""
        for theme in themes
    ) + "</section>"
    (site_dir / "themes.html").write_text(html_page("Corporate Finance Themes", theme_body, "Themes"), encoding="utf-8")

    subtheme_body = "<section class=\"list\">" + "".join(
        f"""<div class="row">
      <div class="meta">{esc(subtheme["theme"])} · sessions {', '.join(str(i) for i in subtheme["session_indexes"])}</div>
      <strong>{esc(subtheme["name"])}</strong>
      <span>{esc('; '.join(subtheme["session_titles"]))}</span>
    </div>"""
        for subtheme in subthemes
    ) + "</section>"
    (site_dir / "subthemes.html").write_text(html_page("Corporate Finance Subthemes", subtheme_body, "Subthemes"), encoding="utf-8")

    concepts_dir = site_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    concept_index_body = "<section class=\"hero\"><p>Each concept page explains the idea, why it matters, how Damodaran develops it, common mistakes, related concepts, and the strongest transcript-backed sessions.</p></section>"
    concept_index_body += "<section class=\"grid\">" + "".join(
        f"""<article class="card">
      <div class="meta">{esc(concept["theme_slug"].replace("-", " "))}</div>
      <h3><a href="{esc(concept["slug"])}.html">{esc(concept["name"])}</a></h3>
      <p>{esc(concept["meaning"])}</p>
      <div class="tags">{''.join(f'<span>Session {session}</span>' for session in concept["strongest_sessions"][:3])}</div>
    </article>"""
        for concept in concepts
    ) + "</section>"
    (concepts_dir / "index.html").write_text(
        html_page("Corporate Finance Concepts", concept_index_body, "Concepts", asset_prefix="../"), encoding="utf-8"
    )

    concept_by_slug = {concept["slug"]: concept for concept in concepts}
    for concept in concepts:
        evidence = concept.get("evidence", [])
        evidence_html = "".join(
            f"""<article class="row evidence">
        <div class="meta">Session {item["session"]:02d} · score {item["score"]}</div>
        <strong>{esc(item["title"])}</strong>
        <p>{esc(item["excerpt"])}</p>
        <a href="{esc(item["url"])}">YouTube</a>
      </article>"""
            for item in evidence
        )
        connection_html = "".join(
            f'<a href="{esc(slug)}.html">{esc(concept_by_slug.get(slug, {"name": slug})["name"])}</a>'
            for slug in concept.get("connections", [])
        )
        mistakes_html = "".join(f"<li>{esc(item)}</li>" for item in concept.get("common_mistakes", []))
        body = f"""
    <section class="split">
      <article class="essay">
        <p class="kicker">Concept</p>
        <h2>{esc(concept["name"])}</h2>
        <p><strong>Meaning.</strong> {esc(concept["meaning"])}</p>
        <p><strong>Why it matters.</strong> {esc(concept["importance"])}</p>
        <p><strong>How Damodaran develops it.</strong> {esc(concept["development"])}</p>
        <h3>Common mistakes</h3>
        <ul>{mistakes_html}</ul>
        {enrichment_html(esc, concept)}
      </article>
      <aside class="card">
        <div class="meta">Connected concepts</div>
        <div class="concept-links">{connection_html}</div>
      </aside>
    </section>
    <section class="list" style="margin-top:22px">
      <h2>Strongest transcript evidence</h2>
      {evidence_html}
    </section>
"""
        (concepts_dir / f"{concept['slug']}.html").write_text(
            html_page(concept["name"], body, "Concepts", asset_prefix="../"), encoding="utf-8"
        )

    evidence_body = "<section class=\"hero\"><p>Evidence links each concept to the sessions and cue excerpts where the course language most strongly matches that idea.</p></section><section class=\"list\">"
    for concept in concepts:
        evidence_body += f'<article class="row"><strong><a href="concepts/{esc(concept["slug"])}.html">{esc(concept["name"])}</a></strong>'
        evidence_body += "<p>" + "; ".join(
            f'Session {item["session"]:02d}: {esc(item["title"])}' for item in concept.get("evidence", [])[:4]
        ) + "</p></article>"
    evidence_body += "</section>"
    (site_dir / "evidence.html").write_text(html_page("Corporate Finance Evidence Map", evidence_body, "Evidence"), encoding="utf-8")

    discussion_body = "<section class=\"list\">" + "".join(
        f"""<article class="row">
      <div class="meta">Session {item["session"]:02d} · {esc(item["theme"])} · {esc(item["subtheme"])}</div>
      <strong>{esc(item["title"])}</strong>
      <p>{esc(item["discussion"])}</p>
      <a href="{esc(item["url"])}">YouTube</a>
    </article>"""
        for item in discussions
    ) + "</section>"
    (site_dir / "discussions.html").write_text(html_page("Course Discussions", discussion_body, "Discussions"), encoding="utf-8")

    session_body = "<section class=\"grid\">" + "".join(session_card(item) for item in sessions) + "</section>"
    (site_dir / "sessions.html").write_text(html_page("Course Sessions", session_body, "Sessions"), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-root", default=".")
    args = parser.parse_args()
    build(Path(args.course_root).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
