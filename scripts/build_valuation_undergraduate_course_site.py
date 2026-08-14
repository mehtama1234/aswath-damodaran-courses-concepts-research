#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from concept_enrichment import enrichment_html, load_enrichment


CONCEPT_SPECS = [
    {
        "slug": "valuation-as-sequenced-craft",
        "name": "Valuation as sequenced craft",
        "theme_id": "valuation-is-taught-as-a-sequenced-craft-not-a-mystery",
        "meaning": "Valuation is taught as a learnable sequence of choices rather than a mysterious expert ritual.",
        "importance": "This is the pedagogical spine of the undergraduate course and the reason the material feels executable rather than ornamental.",
        "development": "The early sessions keep breaking valuation into ordered steps, then the later sessions return to that sequence when the class reaches pricing, options, and acquisitions.",
        "common_mistakes": ["Treating valuation as a spreadsheet inherited from someone else.", "Jumping into outputs before defining the sequence of inputs."],
        "connections": ["bermuda-triangle-of-valuation", "dcf-big-picture", "valuation-as-a-doable-project"],
        "keywords": ["valuation", "process", "sequence", "steps", "dcf", "class", "company"],
    },
    {
        "slug": "bermuda-triangle-of-valuation",
        "name": "Bermuda Triangle of valuation",
        "theme_id": "valuation-is-taught-as-a-sequenced-craft-not-a-mystery",
        "meaning": "Students get lost when they confuse value, price, and narrative or let bias control the path between them.",
        "importance": "It gives the course a durable warning about category mistakes that recur in investing, company analysis, and market talk.",
        "development": "The second session names the concept directly, and later storytelling and pricing sessions keep reworking the same distinction.",
        "common_mistakes": ["Treating market price as proof of intrinsic value.", "Letting the story justify the answer you wanted in advance."],
        "connections": ["valuation-as-sequenced-craft", "intrinsic-value-versus-pricing", "storytelling-into-inputs"],
        "keywords": ["bermuda triangle", "value", "price", "story", "bias", "valuation"],
    },
    {
        "slug": "dcf-big-picture",
        "name": "DCF big picture",
        "theme_id": "valuation-is-taught-as-a-sequenced-craft-not-a-mystery",
        "meaning": "A DCF is the course's organizing architecture for intrinsic value: expected cash flows discounted at rates that match risk, currency, and claim definition.",
        "importance": "It turns valuation from a loose idea into an operating framework that can be built and checked piece by piece.",
        "development": "The course introduces DCF early, then spends most of the semester unpacking the assumptions hidden inside it.",
        "common_mistakes": ["Using DCF as a blank template without understanding the claim being valued.", "Letting terminal value hide a weak operating story."],
        "connections": ["riskfree-rates", "cash-flow-construction", "terminal-value-discipline"],
        "keywords": ["dcf", "discounted cash flow", "intrinsic value", "cash flow", "discount rate", "present value"],
    },
    {
        "slug": "riskfree-rates",
        "name": "Riskfree rates",
        "theme_id": "discount-rates-are-built-from-economic-logic",
        "meaning": "The riskfree rate is chosen to match the currency and inflation setting of the valuation, not copied blindly from a default reference bond.",
        "importance": "It anchors every later discount-rate choice, so a bad starting rate contaminates the whole model.",
        "development": "The early rate sessions repeatedly tie the riskfree rate back to currency, sovereign default risk, and inflation logic.",
        "common_mistakes": ["Using a US Treasury by habit for non-dollar cash flows.", "Ignoring sovereign default risk in the base rate."],
        "connections": ["equity-risk-premiums", "betas-and-relative-risk", "cost-of-capital"],
        "keywords": ["riskfree", "risk free", "currency", "inflation", "treasury", "default"],
    },
    {
        "slug": "equity-risk-premiums",
        "name": "Equity risk premiums",
        "theme_id": "discount-rates-are-built-from-economic-logic",
        "meaning": "The equity risk premium is the market's current price of bearing equity risk over the riskfree alternative.",
        "importance": "It is one of the largest levers in any valuation and a direct bridge from market pricing into intrinsic-value inputs.",
        "development": "The course moves from standard premium intuition into implied premiums and country-sensitive adjustments.",
        "common_mistakes": ["Memorizing one historical premium and using it everywhere.", "Ignoring how market conditions shift the premium investors demand."],
        "connections": ["riskfree-rates", "betas-and-relative-risk", "cost-of-capital"],
        "keywords": ["equity risk premium", "premium", "implied", "market", "risk"],
    },
    {
        "slug": "betas-and-relative-risk",
        "name": "Betas and relative risk",
        "theme_id": "discount-rates-are-built-from-economic-logic",
        "meaning": "Beta is used as a way to connect company risk back to market risk, but only after thinking through business mix and leverage.",
        "importance": "It prevents discount rates from becoming abstract finance formulas detached from the business being valued.",
        "development": "The beta sessions push students toward relative-risk reasoning before debt costs and cost of capital are finalized.",
        "common_mistakes": ["Treating a regression beta as final truth.", "Forgetting that leverage changes equity risk."],
        "connections": ["equity-risk-premiums", "cost-of-capital", "private-company-valuation"],
        "keywords": ["beta", "betas", "relative risk", "levered", "unlevered", "debt"],
    },
    {
        "slug": "cost-of-capital",
        "name": "Cost of capital",
        "theme_id": "discount-rates-are-built-from-economic-logic",
        "meaning": "The cost of capital combines debt and equity costs into a rate that matches operating cash flows.",
        "importance": "It is where the logic of rates, risk, and claims has to come together consistently.",
        "development": "The course closes the discount-rate block by building the cost of capital before moving to cash-flow definition.",
        "common_mistakes": ["Discounting equity cash flows with a firm-wide rate.", "Using weights or debt costs with no link to the business being valued."],
        "connections": ["betas-and-relative-risk", "cash-flow-construction", "intrinsic-value-versus-pricing"],
        "keywords": ["cost of capital", "wacc", "cost of debt", "cost of equity", "capital structure"],
    },
    {
        "slug": "cash-flow-construction",
        "name": "Cash-flow construction",
        "theme_id": "cash-flows-growth-and-terminal-value-form-the-operating-core",
        "meaning": "Valuation cash flows are built by translating accounting statements into operating claims after taxes, capex, and working-capital needs.",
        "importance": "This is where the course forces students to stop confusing reported earnings with distributable economic cash flow.",
        "development": "The middle sessions walk through taxes, capex, working capital, and FCFE closure in sequence.",
        "common_mistakes": ["Using net income as if it were free cash flow.", "Ignoring reinvestment and working-capital demands."],
        "connections": ["growth-and-reinvestment", "terminal-value-discipline", "cost-of-capital"],
        "keywords": ["cash flow", "working capital", "capex", "fcfe", "tax", "reinvestment"],
    },
    {
        "slug": "growth-and-reinvestment",
        "name": "Growth and reinvestment",
        "theme_id": "cash-flows-growth-and-terminal-value-form-the-operating-core",
        "meaning": "Growth creates value only when the business can fund it through credible reinvestment economics.",
        "importance": "It stops students from treating growth as free upside and ties the valuation back to operating reality.",
        "development": "Growth sessions keep connecting expansion to reinvestment needs, margins, and return logic.",
        "common_mistakes": ["Projecting high growth without funding it.", "Assuming any growth is automatically value-creating."],
        "connections": ["cash-flow-construction", "terminal-value-discipline", "storytelling-into-inputs"],
        "keywords": ["growth", "reinvestment", "sales to capital", "margin", "return on capital"],
    },
    {
        "slug": "terminal-value-discipline",
        "name": "Terminal value discipline",
        "theme_id": "cash-flows-growth-and-terminal-value-form-the-operating-core",
        "meaning": "Terminal value is the mature-state closure of the valuation and therefore a test of whether the whole story is internally consistent.",
        "importance": "Because terminal value can dominate the result, small mistakes here can overwhelm the rest of the model.",
        "development": "The terminal-value sessions isolate the idea and show how stable growth, reinvestment, and risk have to fit together.",
        "common_mistakes": ["Using forever growth that outpaces the economy.", "Letting terminal value rescue implausible near-term assumptions."],
        "connections": ["growth-and-reinvestment", "dcf-big-picture", "life-cycle-valuation"],
        "keywords": ["terminal value", "stable growth", "terminal growth", "forever", "mature"],
    },
    {
        "slug": "storytelling-into-inputs",
        "name": "Storytelling into inputs",
        "theme_id": "storytelling-is-allowed-but-it-must-change-the-numbers",
        "meaning": "Narrative is allowed only when it changes concrete assumptions about growth, margins, reinvestment, risk, and life-cycle path.",
        "importance": "This is how the course allows strategic thinking without letting storytelling float free of economics.",
        "development": "The storytelling block makes students rewrite qualitative views as model inputs and then defend them.",
        "common_mistakes": ["Keeping the story in prose but not in the spreadsheet.", "Changing numbers without changing the business story."],
        "connections": ["bermuda-triangle-of-valuation", "life-cycle-valuation", "growth-and-reinvestment"],
        "keywords": ["story", "storytelling", "narrative", "margins", "growth", "assumptions"],
    },
    {
        "slug": "life-cycle-valuation",
        "name": "Life-cycle valuation",
        "theme_id": "storytelling-is-allowed-but-it-must-change-the-numbers",
        "meaning": "Firms should be valued differently depending on whether they are young, mature, declining, emerging-market, or financial-service businesses.",
        "importance": "It is where the course stops pretending one template can serve every company equally well.",
        "development": "The life-cycle and special-company sessions test whether the story and assumptions actually fit the business type.",
        "common_mistakes": ["Using mature-company assumptions for young firms.", "Ignoring structural differences in business models and environments."],
        "connections": ["storytelling-into-inputs", "private-company-valuation", "terminal-value-discipline"],
        "keywords": ["life cycle", "young", "mature", "declining", "emerging market", "financial service"],
    },
    {
        "slug": "intrinsic-value-versus-pricing",
        "name": "Intrinsic value versus pricing",
        "theme_id": "pricing-is-a-different-language-from-intrinsic-value",
        "meaning": "Intrinsic value asks what the asset is worth from its own cash flows, while pricing asks what similar assets trade for in a market.",
        "importance": "This separation is one of the course's most durable intellectual distinctions and a major protection against analytical confusion.",
        "development": "The transition into pricing is explicit: Damodaran treats it as a different language, not a lighter version of DCF.",
        "common_mistakes": ["Calling a multiple-based answer intrinsic value.", "Treating market price as a substitute for analysis."],
        "connections": ["pricing-multiples", "peer-groups-and-comparables", "asset-based-valuation"],
        "keywords": ["intrinsic value", "pricing", "price", "market", "multiple", "comparables"],
    },
    {
        "slug": "pricing-multiples",
        "name": "Pricing multiples",
        "theme_id": "pricing-is-a-different-language-from-intrinsic-value",
        "meaning": "Multiples compress assumptions about growth, risk, and profitability into a market ratio that looks simple only because the assumptions are hidden.",
        "importance": "It helps students see why comparables are powerful in markets but still require disciplined interpretation.",
        "development": "The pricing sessions unpack the hidden drivers inside common multiples rather than treating them as plug-and-play facts.",
        "common_mistakes": ["Using multiples without matching the underlying definitions.", "Ignoring how risk and growth differences move the multiple."],
        "connections": ["intrinsic-value-versus-pricing", "peer-groups-and-comparables", "market-level-pricing"],
        "keywords": ["multiple", "multiples", "pe", "ebitda", "revenue", "pricing"],
    },
    {
        "slug": "peer-groups-and-comparables",
        "name": "Peer groups and comparables",
        "theme_id": "pricing-is-a-different-language-from-intrinsic-value",
        "meaning": "Relative pricing depends on which firms are judged similar enough to act as comparables and how those similarities are defined.",
        "importance": "This is where pricing becomes either disciplined or manipulable depending on peer-group judgment.",
        "development": "The peer-group analytics session makes the comparable set itself part of the analysis rather than a background assumption.",
        "common_mistakes": ["Choosing peers because they support the answer you want.", "Pretending there is one natural comparable set."],
        "connections": ["pricing-multiples", "intrinsic-value-versus-pricing", "market-level-pricing"],
        "keywords": ["peer group", "comparable", "comparables", "pricing analytics", "regression"],
    },
    {
        "slug": "market-level-pricing",
        "name": "Market-level pricing",
        "theme_id": "pricing-is-a-different-language-from-intrinsic-value",
        "meaning": "Pricing logic also applies to whole markets, where rates, macro narratives, tariffs, and mood shape the multiples investors will pay.",
        "importance": "It widens the course from company-specific analysis into broader consumer, policy, and market context.",
        "development": "The tariff and market-pricing discussion shows how valuation ideas interact with public narratives and macro repricing.",
        "common_mistakes": ["Reading market multiples without considering rates and risk appetite.", "Assuming macro narratives suspend valuation logic."],
        "connections": ["pricing-multiples", "equity-risk-premiums", "intrinsic-value-versus-pricing"],
        "keywords": ["market", "tariff", "pe", "pricing", "macro", "index"],
    },
    {
        "slug": "private-company-valuation",
        "name": "Private-company valuation",
        "theme_id": "special-cases-show-where-default-models-stop-working",
        "meaning": "Private-company valuation changes when the owners are undiversified, liquidity is limited, and control rights are structured differently from public markets.",
        "importance": "It forces the class to confront who owns the asset and under what constraints rather than assuming a public-market marginal investor.",
        "development": "The private-company session turns owner type, control, and illiquidity into central valuation variables.",
        "common_mistakes": ["Using public-market assumptions unchanged for private assets.", "Treating illiquidity as a generic arbitrary haircut."],
        "connections": ["asset-based-valuation", "acquisition-and-value-enhancement", "betas-and-relative-risk"],
        "keywords": ["private company", "illiquidity", "control", "owner", "liquidity", "private"],
    },
    {
        "slug": "asset-based-valuation",
        "name": "Asset-based valuation and pricing",
        "theme_id": "special-cases-show-where-default-models-stop-working",
        "meaning": "Asset-based approaches anchor value in underlying assets when operating cash-flow or comparable-company methods become less reliable.",
        "importance": "It gives the course a fallback anchor for settings where the default public-company mindset stops working.",
        "development": "The pricing closure sessions introduce asset-based approaches right where relative pricing reaches its limits.",
        "common_mistakes": ["Using book value as if it were already economic value.", "Applying asset-based logic where intangible growth dominates."],
        "connections": ["intrinsic-value-versus-pricing", "private-company-valuation", "distressed-equity-as-option"],
        "keywords": ["asset based", "asset-based", "book value", "liquidation", "assets"],
    },
    {
        "slug": "real-options",
        "name": "Real options",
        "theme_id": "uncertainty-can-create-optionality-not-just-a-higher-discount-rate",
        "meaning": "Real options treat uncertainty as a potential source of value when a firm controls a scarce right to wait, expand, or change course.",
        "importance": "It is the course's clearest break from the idea that uncertainty only belongs in a higher discount rate.",
        "development": "The IPO-to-options transition and the patents/resources block show when optionality is real and when it is being abused rhetorically.",
        "common_mistakes": ["Calling every uncertain project an option.", "Ignoring the need for exclusivity and decision flexibility."],
        "connections": ["patents-and-resource-options", "distressed-equity-as-option", "intrinsic-value-versus-pricing"],
        "keywords": ["real option", "option", "options", "wait", "exclusive", "uncertainty"],
    },
    {
        "slug": "patents-and-resource-options",
        "name": "Patents and resource options",
        "theme_id": "uncertainty-can-create-optionality-not-just-a-higher-discount-rate",
        "meaning": "Patents and natural resources make option logic visible because the owner controls timing over an uncertain but exclusive economic right.",
        "importance": "These cases make contingent upside easier to reason about than standard operating-company examples do.",
        "development": "The course uses patents and resource rights as the cleanest teaching cases for real-options intuition.",
        "common_mistakes": ["Using option language without a real exclusive right.", "Ignoring development cost, timing, or resource economics."],
        "connections": ["real-options", "distressed-equity-as-option", "asset-based-valuation"],
        "keywords": ["patent", "natural resource", "oil", "reserve", "option", "exclusive"],
    },
    {
        "slug": "distressed-equity-as-option",
        "name": "Distressed equity as option",
        "theme_id": "uncertainty-can-create-optionality-not-just-a-higher-discount-rate",
        "meaning": "In distress, equity can behave like a contingent claim on recovery rather than a normal residual ownership interest.",
        "importance": "It shows how capital structure and downside asymmetry can preserve equity value even when conventional valuation looks bleak.",
        "development": "The distressed-equity session broadens option logic beyond technology and natural-resource cases.",
        "common_mistakes": ["Valuing distressed equity like ordinary equity.", "Ignoring debt priority and volatility in recovery."],
        "connections": ["real-options", "asset-based-valuation", "acquisition-and-value-enhancement"],
        "keywords": ["distressed equity", "distress", "option", "debt", "recovery", "bankruptcy"],
    },
    {
        "slug": "acquisition-and-value-enhancement",
        "name": "Acquisition and value enhancement",
        "theme_id": "special-cases-show-where-default-models-stop-working",
        "meaning": "Acquisition value depends on who can change decisions, create synergies, and improve the business after control changes hands.",
        "importance": "It turns valuation from passive measurement into a framework for governance, operating change, and strategic intervention.",
        "development": "The course ends by linking acquisition cases to value enhancement and decision rights rather than stopping at stand-alone valuation.",
        "common_mistakes": ["Paying for vague synergy without specifying the operating change.", "Assuming control is valuable without showing what better decisions look like."],
        "connections": ["private-company-valuation", "distressed-equity-as-option", "valuation-as-a-doable-project"],
        "keywords": ["acquisition", "synergy", "value enhancement", "control", "premium", "decision"],
    },
    {
        "slug": "valuation-as-a-doable-project",
        "name": "Valuation as a doable project",
        "theme_id": "the-undergraduate-course-treats-valuation-as-a-doable-project",
        "meaning": "The course treats valuation as something students must actually finish: pick a company, build the model, revise it, and make a recommendation.",
        "importance": "It is the bridge between theory and practice and one of the clearest differences between this course and a purely conceptual finance sequence.",
        "development": "From class logistics through live project reminders, the course keeps dragging abstract valuation back into execution discipline.",
        "common_mistakes": ["Waiting for perfect certainty before starting.", "Stopping at a number instead of making a recommendation."],
        "connections": ["valuation-as-sequenced-craft", "storytelling-into-inputs", "acquisition-and-value-enhancement"],
        "keywords": ["project", "company", "valuation", "feedback", "quiz", "recommendation"],
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value))


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def clip_words(text: str, limit: int = 46) -> str:
    words = re.sub(r"\s+", " ", text).strip().split()
    if len(words) <= limit:
        return " ".join(words)
    return " ".join(words[:limit]).rstrip(" ,;:") + "..."


def keyword_score(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(keyword) for keyword in keywords)


def html_page(title: str, body: str, current: str) -> str:
    nav = [
        ("index.html", "Overview"),
        ("course-thesis.html", "Thesis"),
        ("themes.html", "Themes"),
        ("concepts/index.html", "Concepts"),
        ("evidence.html", "Evidence"),
        ("sessions.html", "Sessions"),
    ]
    links = "\n".join(
        f'<a class="{"active" if label == current else ""}" href="{href}">{label}</a>'
        for href, label in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <header class="top">
    <div>
      <p class="eyebrow">Aswath Damodaran course atlas</p>
      <h1>{esc(title)}</h1>
    </div>
    <nav>{links}</nav>
  </header>
  <main>
{body}
  </main>
</body>
</html>
"""


def build_css() -> str:
    return """
:root {
  color-scheme: light;
  --ink: #181713;
  --muted: #5c574c;
  --line: #d8cfc2;
  --paper: #f6f2ea;
  --panel: #fffdf9;
  --panel-alt: #f1ece2;
  --accent: #0d6d71;
  --accent-soft: #deefef;
  --accent-2: #975423;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background: linear-gradient(180deg, #faf6ef 0%, #f3efe7 100%);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.6;
}
.top {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: end;
  padding: 36px min(5vw, 64px) 20px;
  border-bottom: 1px solid var(--line);
}
.eyebrow {
  margin: 0 0 8px;
  color: var(--accent-2);
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .06em;
}
h1, h2, h3 { margin: 0; }
h1 { font-size: clamp(34px, 5vw, 62px); line-height: 1; max-width: 900px; }
h2 { font-size: 30px; margin-bottom: 14px; }
h3 { font-size: 22px; margin-bottom: 10px; }
p { margin: 0 0 14px; color: var(--muted); }
a { color: var(--accent); }
nav { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
nav a {
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 8px 11px;
  color: var(--ink);
  background: var(--panel);
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
}
nav a.active, nav a:hover { background: var(--accent); border-color: var(--accent); color: white; }
main { padding: 30px min(5vw, 64px) 60px; }
.hero, .essay, .card, .row {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
}
.hero { padding: 24px; max-width: 1080px; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  background: var(--panel-alt);
  border: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}
.section { margin-top: 24px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
.card, .essay { padding: 20px; }
.card p:last-child, .essay p:last-child { margin-bottom: 0; }
.kicker {
  margin-bottom: 10px;
  color: var(--accent);
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .06em;
}
.row { padding: 16px 18px; }
.row + .row { margin-top: 12px; }
.row .minor {
  margin-bottom: 6px;
  color: var(--accent-2);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .05em;
}
.minor {
  margin-bottom: 6px;
  color: var(--accent-2);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .05em;
}
.session-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.session-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
  background: var(--panel);
}
.session-card .topline {
  color: var(--accent-2);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .05em;
}
.session-card .theme {
  display: inline-block;
  margin-top: 12px;
  padding: 5px 8px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}
.concept-links { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.concept-links a {
  color: var(--accent);
  background: var(--accent-soft);
  border: 1px solid #cfe2dd;
  border-radius: 999px;
  padding: 6px 9px;
  text-decoration: none;
  font-size: 12px;
  font-weight: 700;
}
ol { margin: 0; padding-left: 22px; color: var(--muted); }
li + li { margin-top: 8px; }
ul { margin: 0; padding-left: 18px; color: var(--muted); }
@media (max-width: 760px) {
  .top { display: block; }
  nav { justify-content: flex-start; margin-top: 18px; }
  main { padding-top: 20px; }
}
"""


def build_course_thesis(course_title: str, transcript_count: int, total_words: int) -> str:
    return "\n".join(
        [
            "# Course Thesis",
            "",
            f"{course_title} is a practical course in valuation as ordered judgment. It teaches students to move in sequence: define the valuation problem, separate value from price, build discount rates from economic logic, convert accounting statements into cash flows, connect growth to reinvestment, and only then widen into pricing, private-company frictions, optionality, acquisitions, and value enhancement.",
            "",
            "The undergraduate framing matters. Damodaran is not assuming that students already think like professional appraisers or buy-side analysts. He keeps converting valuation into a doable project with deadlines, company choices, model inputs, and recommendation-making. The intellectual work is still rigorous, but the pedagogy is deliberately executable.",
            "",
            "The course also carries wider market and institutional themes. It treats public markets as social pricing systems, not as truth machines; it shows that owner type and liquidity conditions matter in private assets; it distinguishes operational value from issuance mood in IPOs; and it reframes uncertainty as potential optionality when firms control scarce rights or contingent claims.",
            "",
            f"This synthesis is grounded in {transcript_count} transcript-backed sessions and {total_words:,} transcript words.",
            "",
            "## Argument Spine",
            "",
            "1. Teach valuation as an ordered craft rather than a mystery.",
            "2. Build discount rates from currency, inflation, riskfree rates, risk premiums, betas, and debt costs.",
            "3. Translate accounting numbers into economic cash flows, reinvestment needs, and terminal assumptions.",
            "4. Allow narrative, but only when it changes the numbers in a disciplined way.",
            "5. Separate intrinsic value from pricing and comparables.",
            "6. Extend the framework to private firms, IPOs, real options, distressed equity, acquisitions, and value enhancement.",
            "7. Treat the final output as a recommendation under uncertainty, not just a spreadsheet result.",
        ]
    )


def infer_theme_for_session(index: int) -> str:
    if index <= 4:
        return "Valuation as sequenced craft"
    if index <= 8:
        return "Discount rates from economic logic"
    if index <= 13:
        return "Cash flows, growth, and terminal value"
    if index <= 18:
        return "Storytelling into assumptions"
    if index <= 22:
        return "Pricing as a different language"
    if index in {23, 27}:
        return "Special cases and governance"
    if index in {24, 25, 26}:
        return "Optionality and contingent claims"
    return "Course framing"


def session_summary(index: int, title: str) -> str:
    summaries = {
        1: "Introduces the course structure, the semester valuation project, and the expectation that students commit early to a company and work through the valuation in public.",
        2: "Defines the Bermuda Triangle of valuation and starts separating story, intrinsic value, and market price so students stop treating them as the same thing.",
        3: "Continues the valuation-method comparison and begins the move into intrinsic-value logic and the DCF framework.",
        4: "Lays out the big-picture DCF architecture and starts the first serious work on riskfree rates and discount-rate consistency.",
        5: "Finishes the riskfree-rate discussion and moves into the logic of equity risk premiums across currencies and markets.",
        6: "Shows how implied equity risk premiums are estimated and why market-implied risk can matter more than memorized historical averages.",
        7: "Builds relative risk through betas and starts connecting business risk to borrowing costs and capital structure.",
        8: "Closes the cost-of-capital block and opens the cash-flow side of valuation by defining what has to be measured and matched.",
        9: "Works through tax rates, capital expenditures, and working capital so accounting statements can be translated into economic cash-flow inputs.",
        10: "Closes FCFE issues and begins the growth discussion by linking expansion to valuation rather than treating growth as a free assumption.",
        11: "Pushes further on growth and opens terminal value, showing how mature-state assumptions can dominate an entire model.",
        12: "Focuses tightly on terminal value and the discipline required to make stable-growth assumptions believable.",
        13: "Cleans up loose ends in the valuation framework and gets the class ready for the transition from mechanics into storytelling.",
        14: "Introduces storytelling as a valuation discipline, showing that narrative matters only when it changes concrete assumptions.",
        15: "Extends the storytelling framework into first company valuations and demonstrates how qualitative views become model inputs.",
        16: "Uses market and life-cycle valuation cases to show how assumptions should change across young, mature, and shifting businesses.",
        17: "Applies the framework to declining firms, emerging-market firms, and financial-service companies where standard assumptions need adjustment.",
        18: "Closes the intrinsic-value block and opens pricing, making the distinction between value and relative market language explicit.",
        19: "Continues pricing through multiples and comparables, showing how markets embed assumptions in seemingly simple ratios.",
        20: "Uses a market-level pricing discussion to connect valuation logic with macro narratives, tariffs, and broader market mood.",
        21: "Deepens pricing analytics by working through peer groups and comparability, making relative valuation more systematic.",
        22: "Closes pricing and introduces asset-based anchors for cases where market multiples or DCF logic are not enough on their own.",
        23: "Shows how private-company valuation changes once ownership concentration, illiquidity, and owner-specific constraints matter.",
        24: "Closes the IPO discussion and opens real options, linking issuance context to contingent upside and the value of waiting.",
        25: "Uses patents and natural resources to make real-options logic concrete in settings with exclusivity, timing choice, and uncertain payoffs.",
        26: "Treats distressed equity as an option-like claim and connects contingent-claim thinking back to acquisition valuation.",
        27: "Closes acquisitions and value enhancement by showing that governance and decision change, not just measurement, can create value.",
        28: "A short preview that frames valuation as a broad practical discipline before the full course sequence begins.",
    }
    return summaries.get(index, f"Transcript-backed session on {title.lower()}.")


def find_theme(themes: list[dict[str, Any]], theme_id: str) -> dict[str, Any]:
    for theme in themes:
        if theme["id"] == theme_id:
            return theme
    raise KeyError(theme_id)


def load_cue_excerpt(course_root: Path, record: dict[str, Any], keywords: list[str]) -> dict[str, Any]:
    cue_path = course_root / record["cue_json"]
    if not cue_path.is_file():
        return {"excerpt": session_summary(int(record["index"]), record["title"]), "start_seconds": None, "end_seconds": None}
    cues = load_json(cue_path)
    best_score = -1
    best_cue: dict[str, Any] | None = None
    for cue in cues:
        text = cue.get("text", "")
        score = keyword_score(text, keywords)
        if score > best_score:
            best_score = score
            best_cue = cue
    if best_cue and best_score > 0:
        return {
            "excerpt": clip_words(best_cue.get("text", "")),
            "start_seconds": best_cue.get("start_seconds"),
            "end_seconds": best_cue.get("end_seconds"),
        }
    return {"excerpt": session_summary(int(record["index"]), record["title"]), "start_seconds": None, "end_seconds": None}


def build_concepts(course_root: Path, transcript_index: list[dict[str, Any]], themes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _enrichment = load_enrichment(course_root)
    session_texts: dict[int, str] = {}
    for record in transcript_index:
        text_path = course_root / record["clean_txt"]
        session_texts[int(record["index"])] = (
            f"{record['title']}\n{text_path.read_text(encoding='utf-8', errors='ignore')}" if text_path.is_file() else record["title"]
        )

    concepts: list[dict[str, Any]] = []
    evidence_map: dict[str, Any] = {"concepts": {}}
    for spec in CONCEPT_SPECS:
        theme = find_theme(themes, spec["theme_id"])
        scored: list[tuple[int, dict[str, Any]]] = []
        for record in transcript_index:
            session_index = int(record["index"])
            score = keyword_score(session_texts[session_index], spec["keywords"])
            if session_index in theme["evidence_sessions"]:
                score += 8
            if score > 0:
                scored.append((score, record))
        scored.sort(key=lambda item: item[0], reverse=True)
        evidence = []
        for score, record in scored[:5]:
            evidence.append(
                {
                    "session": record["index"],
                    "title": record["title"],
                    "url": record["url"],
                    "score": score,
                    **load_cue_excerpt(course_root, record, spec["keywords"]),
                }
            )
        concept = {
            "slug": spec["slug"],
            "name": spec["name"],
            "theme_id": spec["theme_id"],
            "theme_name": theme["name"],
            "meaning": spec["meaning"],
            "importance": spec["importance"],
            "development": spec["development"],
            "common_mistakes": spec["common_mistakes"],
            "connections": spec["connections"],
            "keywords": spec["keywords"],
            "strongest_sessions": [item["session"] for item in evidence],
            "evidence": evidence,
            "worked_example": _enrichment.get(spec["slug"], {}).get("worked_example", ""),
            "failure_boundary": _enrichment.get(spec["slug"], {}).get("failure_boundary", ""),
        }
        concepts.append(concept)
        evidence_map["concepts"][spec["slug"]] = evidence
    return concepts, evidence_map


def build(course_root: Path) -> None:
    load_json(course_root / "raw-material/youtube/course-manifest.json")
    transcript_index = load_json(course_root / "raw-material/youtube/transcript-index.json")
    theme_map = load_json(course_root / "analysis/themes-and-subthemes.json")
    site_dir = course_root / "site"
    analysis_dir = course_root / "analysis"

    course = theme_map["course"]
    themes = theme_map["themes"]
    concepts, evidence_map = build_concepts(course_root, transcript_index, themes)

    write_text(site_dir / "assets/styles.css", build_css())

    overview_body = f"""
    <section class="hero">
      <p>{esc(course["title"])} is a transcript-backed undergraduate valuation atlas built from the full Spring 2025 teaching sequence. The course moves from valuation framing, to discount-rate construction, to cash-flow and growth mechanics, then into narrative discipline, pricing, special-case valuation, optionality, acquisitions, and value enhancement.</p>
      <p>What makes this course distinctive is its teaching style: Damodaran treats valuation as a structured student project that can be executed step by step, not as a black-box practice reserved for experts.</p>
      <div class="meta">
        <span class="chip">{course["transcript_count"]} transcript-backed sessions</span>
        <span class="chip">{course["total_words"]:,} transcript words</span>
        <span class="chip">{len(themes)} major themes</span>
        <span class="chip">{len(concepts)} concepts</span>
        <span class="chip">Undergraduate teaching order normalized</span>
      </div>
    </section>
    <section class="section grid">
      <article class="card">
        <p class="kicker">Course claim</p>
        <h3>Valuation is taught here as disciplined execution</h3>
        <p>The course turns valuation into a series of linked decisions: what is being valued, whose cash flows matter, what risk belongs in the rate, what growth costs to sustain, and whether the market is pricing the asset differently from intrinsic value.</p>
      </article>
      <article class="card">
        <p class="kicker">Institutional angle</p>
        <h3>Markets, owners, and deal settings change the answer</h3>
        <p>Private ownership, IPO process, distressed claims, acquisition context, and control rights are treated as real structural differences rather than edge-case noise.</p>
      </article>
      <article class="card">
        <p class="kicker">Reader use</p>
        <h3>This atlas is for learning and comparison</h3>
        <p>It gives a plain-language route into the course while also making it easier to compare the undergraduate sequence against the MBA valuation course and other Damodaran playlists.</p>
      </article>
    </section>
    <section class="section">
      <div class="essay">
        <p class="kicker">Theme structure</p>
        <h2>How the course is organized</h2>
        <p>The sequence is cumulative. Early sessions build the conceptual frame, middle sessions build the operating mechanics, and later sessions test the framework against real market frictions, contingent claims, and decision rights.</p>
      </div>
      <div class="grid" style="margin-top:16px">
        {"".join(f'<article class="card"><div class="minor">{", ".join(str(i) for i in theme["evidence_sessions"])}</div><h3>{esc(theme["name"])}</h3><p>{esc(theme["summary"])}</p></article>' for theme in themes)}
      </div>
    </section>
"""
    write_text(site_dir / "index.html", html_page(course["title"], overview_body, "Overview"))

    thesis_body = f"""
    <section class="essay">
      <p class="kicker">Long-form synthesis</p>
      <h2>The real thesis of {esc(course["title"])}</h2>
      <p>Damodaran's undergraduate valuation course is built around an unusually clear promise: valuation can be taught as an ordered craft. Students do not begin with advanced edge cases or heroic spreadsheet complexity. They begin by learning what problem they are solving, what intrinsic value is, why pricing is different, and how a valuation becomes credible only when its assumptions are economically consistent.</p>
      <p>That makes the course especially useful as a map of first principles. Discount rates are not decorative finance jargon. They are built from currency choice, inflation logic, riskfree rates, market risk premiums, company risk, and debt costs. Cash flows are not accounting leftovers. They are reconstructed from taxes, reinvestment, working capital, and the claims that belong to debt holders versus equity holders. Growth is not free upside. It must be paid for through operating economics and capital intensity.</p>
      <p>The social and institutional layer appears later but matters just as much. Pricing is shown as a market language shaped by peer groups, multiples, and mood. Private-company valuation forces attention onto ownership structure and illiquidity. IPOs show the gap between business value and issuance process. Real options show that uncertainty can create upside when rights are scarce. Acquisitions and value enhancement bring the course back to governance and the power to change decisions.</p>
    </section>
    <section class="essay section">
      <h2>Argument spine</h2>
      <ol>
        <li>Teach students to stop confusing value, price, and narrative.</li>
        <li>Make the DCF framework feel buildable through disciplined inputs.</li>
        <li>Show that discount rates come from economic choices, not templates.</li>
        <li>Translate accounting statements into cash flows, growth, and terminal assumptions.</li>
        <li>Allow storytelling only when it changes margins, reinvestment, growth, and risk.</li>
        <li>Separate intrinsic value from market pricing and comparables.</li>
        <li>Use special cases to reveal where ownership, liquidity, optionality, and control change valuation.</li>
      </ol>
    </section>
    <section class="section grid">
      {"".join(f'<article class="card"><div class="minor">{len(theme["subthemes"])} subthemes</div><h3>{esc(theme["name"])}</h3><p>{esc(theme["summary"])}</p></article>' for theme in themes)}
    </section>
"""
    write_text(site_dir / "course-thesis.html", html_page("Valuation Undergraduate Course Thesis", thesis_body, "Thesis"))

    themes_body = "<section class=\"section\">"
    for theme in themes:
        subtheme_items = "".join(
            f"<li><strong>{esc(item['name'])}.</strong> {esc(item['summary'])}</li>"
            for item in theme["subthemes"]
        )
        themes_body += f"""
      <article class="row">
        <div class="minor">Sessions {", ".join(str(i) for i in theme["evidence_sessions"])}</div>
        <h3>{esc(theme["name"])}</h3>
        <p>{esc(theme["summary"])}</p>
        <ul>{subtheme_items}</ul>
      </article>
"""
    themes_body += "</section>"
    write_text(site_dir / "themes.html", html_page("Valuation Undergraduate Themes", themes_body, "Themes"))

    concepts_dir = site_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    concept_index_body = f"""
    <section class="hero">
      <p>The concept layer pulls durable ideas out of the course so they can be compared across Damodaran's valuation teaching at different audience levels.</p>
      <div class="meta">
        <span class="chip">{len(concepts)} concepts</span>
        <span class="chip">{sum(len(c['evidence']) for c in concepts)} evidence links</span>
      </div>
    </section>
    <section class="section grid">
      {"".join(f'<article class="card"><div class="minor">{esc(c["theme_name"])}</div><h3><a href="{esc(c["slug"])}.html">{esc(c["name"])}</a></h3><p>{esc(c["meaning"])}</p></article>' for c in concepts)}
    </section>
"""
    write_text(concepts_dir / "index.html", html_page("Valuation Undergraduate Concepts", concept_index_body, "Concepts").replace('href="index.html"', 'href="../index.html"').replace('href="course-thesis.html"', 'href="../course-thesis.html"').replace('href="themes.html"', 'href="../themes.html"').replace('href="concepts/index.html"', 'href="index.html"').replace('href="evidence.html"', 'href="../evidence.html"').replace('href="sessions.html"', 'href="../sessions.html"').replace('href="assets/styles.css"', 'href="../assets/styles.css"'))

    concept_lookup = {concept["slug"]: concept for concept in concepts}
    for concept in concepts:
        evidence_html = "".join(
            f"""<article class="row">
      <div class="minor">Session {item["session"]:02d} · score {item["score"]}</div>
      <h3>{esc(item["title"])}</h3>
      <p>{esc(item["excerpt"])}</p>
      <p><a href="{esc(item["url"])}">YouTube session link</a></p>
    </article>"""
            for item in concept["evidence"]
        )
        connection_html = "".join(
            f'<a href="{esc(slug)}.html">{esc(concept_lookup[slug]["name"])}</a>'
            for slug in concept["connections"]
            if slug in concept_lookup
        )
        mistakes_html = "".join(f"<li>{esc(item)}</li>" for item in concept["common_mistakes"])
        body = f"""
    <section class="essay">
      <p class="kicker">Concept</p>
      <h2>{esc(concept["name"])}</h2>
      <p><strong>Meaning.</strong> {esc(concept["meaning"])}</p>
      <p><strong>Why it matters.</strong> {esc(concept["importance"])}</p>
      <p><strong>How the course develops it.</strong> {esc(concept["development"])}</p>
      {enrichment_html(esc, concept)}
      <div class="concept-links">{connection_html}</div>
    </section>
    <section class="section grid">
      <article class="card">
        <div class="minor">Theme</div>
        <h3>{esc(concept["theme_name"])}</h3>
        <p>Strongest sessions: {", ".join(str(s) for s in concept["strongest_sessions"])}</p>
      </article>
      <article class="card">
        <div class="minor">Common mistakes</div>
        <ul>{mistakes_html}</ul>
      </article>
    </section>
    <section class="section">
      {evidence_html}
    </section>
"""
        page = html_page(concept["name"], body, "Concepts")
        page = page.replace('href="index.html"', 'href="../index.html"').replace('href="course-thesis.html"', 'href="../course-thesis.html"').replace('href="themes.html"', 'href="../themes.html"').replace('href="concepts/index.html"', 'href="index.html"').replace('href="evidence.html"', 'href="../evidence.html"').replace('href="sessions.html"', 'href="../sessions.html"').replace('href="assets/styles.css"', 'href="../assets/styles.css"')
        write_text(concepts_dir / f"{concept['slug']}.html", page)

    evidence_body = f"""
    <section class="hero">
      <p>This evidence map links each undergraduate valuation concept to the sessions where the transcript language most strongly supports it.</p>
    </section>
    <section class="section">
      {"".join(f'<article class="row"><div class="minor">{esc(c["theme_name"])}</div><h3><a href="concepts/{esc(c["slug"])}.html">{esc(c["name"])}</a></h3><p>' + "; ".join(f'Session {e['session']:02d}: {esc(e['title'])}' for e in c['evidence'][:4]) + '</p></article>' for c in concepts)}
    </section>
"""
    write_text(site_dir / "evidence.html", html_page("Valuation Undergraduate Evidence", evidence_body, "Evidence"))

    session_cards = []
    for record in transcript_index:
        summary = session_summary(int(record["index"]), record["title"])
        session_cards.append(
            f"""
      <article class="session-card">
        <div class="topline">Session {record["index"]:02d} · {record["word_count"]:,} words · {record["cue_count"]:,} cues</div>
        <h3>{esc(record["title"])}</h3>
        <p>{esc(summary)}</p>
        <div class="theme">{esc(infer_theme_for_session(int(record["index"])))}</div>
        <p style="margin-top:12px"><a href="{esc(record['url'])}">YouTube session link</a></p>
      </article>
"""
        )
    sessions_body = f"""
    <section class="hero">
      <p>The session layer keeps the course in teaching order so readers can see how Damodaran sequences the work: frame the problem, build the inputs, stress-test the logic, separate pricing from value, and then extend valuation into harder ownership and market settings.</p>
    </section>
    <section class="section session-grid">
      {''.join(session_cards)}
    </section>
"""
    write_text(site_dir / "sessions.html", html_page("Valuation Undergraduate Sessions", sessions_body, "Sessions"))

    write_text(analysis_dir / "concepts.json", json.dumps(concepts, indent=2, ensure_ascii=False))
    write_text(analysis_dir / "evidence-map.json", json.dumps(evidence_map, indent=2, ensure_ascii=False))
    write_text(
        analysis_dir / "course-thesis.md",
        build_course_thesis(course["title"], int(course["transcript_count"]), int(course["total_words"])),
    )

    print(f"built undergraduate valuation site with {len(themes)} themes, {len(concepts)} concepts, and {len(transcript_index)} sessions")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-root", default=".")
    args = parser.parse_args()
    build(Path(args.course_root).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
