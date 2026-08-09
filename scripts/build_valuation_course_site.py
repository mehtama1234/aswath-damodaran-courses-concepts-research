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


STOPWORDS = {
    "about", "after", "again", "against", "also", "and", "because", "been", "before",
    "being", "between", "business", "can", "class", "course", "damodaran", "does",
    "doing", "dont", "every", "from", "going", "have", "into", "just", "know",
    "like", "look", "make", "more", "much", "need", "only", "really", "right",
    "said", "same", "session", "should", "some", "than", "that", "the", "their",
    "then", "there", "these", "they", "this", "through", "time", "value",
    "valuation", "valuing", "want", "what", "when", "where", "which", "with",
    "would", "your",
}


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
        "valuation-discipline",
        "Valuation As A Discipline",
        "The course frames valuation as translated judgment: a business story has to become explicit assumptions, and those assumptions have to survive economic scrutiny.",
        ("story", "stories", "narrative", "discipline", "uncertainty", "intrinsic value", "bermuda triangle", "value", "pricing"),
    ),
    ThemeRule(
        "dcf-architecture",
        "DCF Architecture And Consistency",
        "Discounted cash flow valuation is built as an internally consistent architecture of cash flows, discount rates, currency, inflation, growth, reinvestment, and terminal value.",
        ("dcf", "cash flow", "cash flows", "discount", "riskfree", "risk free", "currency", "inflation", "terminal", "reinvestment"),
    ),
    ThemeRule(
        "risk-discount-rates",
        "Risk And Discount Rates",
        "Risk enters valuation through riskfree rates, equity risk premiums, country risk, betas, costs of debt, and costs of capital that must match the cash flows being valued.",
        ("riskfree", "risk free", "equity risk premium", "premium", "country risk", "beta", "cost of capital", "cost of equity", "cost of debt"),
    ),
    ThemeRule(
        "growth-cash-flows",
        "Growth, Cash Flows, And Operating Reality",
        "Growth creates value only when the operating story supports margins, taxes, reinvestment, capital intensity, and ownership of future cash flows.",
        ("growth", "margin", "margins", "reinvestment", "sales to capital", "stock based compensation", "cash flow", "terminal value", "life cycle"),
    ),
    ThemeRule(
        "pricing-language",
        "Pricing As A Different Market Language",
        "Pricing is treated as a relative and social market language built from multiples, comparables, peer groups, and market mood rather than a shortcut version of intrinsic value.",
        ("pricing", "multiple", "multiples", "comparable", "peer group", "pe ratio", "market pe", "revenues", "ebitda"),
    ),
    ThemeRule(
        "special-situations",
        "Special Situations And Ownership Frictions",
        "Private companies, IPOs, asset-based cases, distressed firms, and acquisitions reveal where public-market valuation habits need new anchors.",
        ("private", "liquidity", "illiquidity", "ipo", "asset based", "distress", "distressed", "acquisition", "synergy"),
    ),
    ThemeRule(
        "optionality-control",
        "Optionality, Control, And Decision Rights",
        "Late-course material shows when uncertainty can create option value and when control creates value by changing decisions rather than merely changing ownership labels.",
        ("option", "options", "patent", "natural resource", "distressed equity", "control", "premium", "decision", "acquisition"),
    ),
)


SUBTHEME_RULES: dict[str, tuple[tuple[str, str, tuple[str, ...]], ...]] = {
    "valuation-discipline": (
        ("story-to-numbers", "Stories translated into numbers", ("story", "stories", "narrative", "numbers", "assumptions")),
        ("intrinsic-vs-pricing", "Intrinsic value versus pricing", ("intrinsic", "pricing", "price", "value")),
        ("valuation-mindset", "Valuation mindset and process", ("valuation", "uncertainty", "discipline", "bermuda triangle")),
    ),
    "dcf-architecture": (
        ("cash-flow-consistency", "Cash-flow consistency", ("cash flow", "cash flows", "consistency", "currency")),
        ("riskfree-and-currency", "Riskfree rates, currency, and inflation", ("riskfree", "risk free", "currency", "inflation")),
        ("terminal-value-discipline", "Terminal value discipline", ("terminal", "stable growth", "reinvestment", "forever")),
    ),
    "risk-discount-rates": (
        ("equity-risk-premiums", "Equity risk premiums and country risk", ("equity risk premium", "premium", "country risk", "implied")),
        ("relative-risk", "Relative risk and betas", ("beta", "betas", "relative risk", "regression", "bottom up")),
        ("cost-of-capital", "Cost of capital construction", ("cost of capital", "cost of equity", "cost of debt", "debt")),
    ),
    "growth-cash-flows": (
        ("free-cash-flow", "Free cash flow construction", ("cash flow", "free cash flow", "working capital", "tax")),
        ("growth-and-reinvestment", "Growth and reinvestment economics", ("growth", "reinvestment", "sales to capital", "return on capital")),
        ("life-cycle-and-loose-ends", "Life cycle and loose ends", ("life cycle", "stock based compensation", "loose ends", "young", "mature")),
    ),
    "pricing-language": (
        ("pricing-101", "Pricing 101 and multiples", ("pricing", "multiple", "multiples", "revenue", "earnings")),
        ("market-pe", "Market PE ratios and macro pricing", ("market pe", "pe ratio", "tariff", "index")),
        ("peer-groups", "Peer groups and pricing analytics", ("peer group", "comparable", "regression", "pricing analytics")),
    ),
    "special-situations": (
        ("asset-based", "Asset-based valuation and pricing", ("asset based", "asset", "book value", "liquidation")),
        ("private-companies", "Private companies, liquidity, and owner risk", ("private", "liquidity", "illiquidity", "undiversified")),
        ("ipos-and-acquisitions", "IPOs, acquisitions, and market process", ("ipo", "acquisition", "takeover", "synergy")),
    ),
    "optionality-control": (
        ("real-options", "Real options with guardrails", ("real option", "option", "exclusive", "volatility")),
        ("patents-resources-distress", "Patents, natural resources, and distressed equity", ("patent", "natural resource", "distressed equity", "distress")),
        ("control-value", "Control value and decision rights", ("control", "premium", "management", "decision")),
    ),
}


CONCEPT_SPECS = [
    ("valuation-as-translated-judgment", "Valuation as translated judgment", "valuation-discipline", "Valuation is a disciplined translation of a business story into explicit assumptions about growth, margins, reinvestment, risk, and time.", "This is the course's deepest habit: a model is useful only when its numbers expose the story rather than hiding it.", "The opening and closing sessions keep returning to valuation as a craft of judgment under uncertainty, not spreadsheet completion.", ("Building a model before knowing the story.", "Treating precision in cells as proof of analytical precision."), ("stories-into-inputs", "intrinsic-value-vs-pricing", "terminal-value"), ("story", "stories", "narrative", "assumptions", "judgment", "uncertainty", "valuation")),
    ("bermuda-triangle-of-valuation", "Bermuda Triangle of valuation", "valuation-discipline", "The analyst can get lost between story, numbers, and bias unless the valuation process keeps each leg visible and testable.", "It gives the course a practical warning: valuation errors are often failures of process rather than failures of arithmetic.", "Early sessions use this frame to separate disciplined valuation from confirmation bias, spreadsheet theater, and market storytelling.", ("Letting bias choose the assumptions.", "Using complexity to disguise weak economics."), ("valuation-as-translated-judgment", "stories-into-inputs", "intrinsic-value-vs-pricing"), ("bermuda triangle", "bias", "story", "numbers", "process", "valuation")),
    ("stories-into-inputs", "Stories into inputs", "valuation-discipline", "Stories matter only when they become model inputs: market size, revenue growth, margins, reinvestment, risk, and terminal economics.", "This is how the course turns strategy talk into something that can be tested, debated, and revised.", "The narrative sessions and first valuation exercises force every qualitative claim to show up somewhere in the model.", ("Letting a persuasive story float above the spreadsheet.", "Changing inputs without changing the underlying story."), ("valuation-as-translated-judgment", "growth-estimation", "life-cycle-valuation"), ("story", "stories", "narrative", "inputs", "numbers", "market size", "margins")),
    ("intrinsic-value-vs-pricing", "Intrinsic value versus pricing", "valuation-discipline", "Intrinsic valuation asks what an asset is worth from its own cash flows, while pricing asks what similar assets trade for.", "The distinction prevents a common analytical category error: using market mood as if it were business value.", "The course first introduces the distinction philosophically, then revisits it in the pricing block with multiples and peer groups.", ("Calling a multiple-based price an intrinsic value.", "Using comparables without admitting the claim is relative."), ("pricing-101", "multiples-hide-assumptions", "peer-group-selection"), ("intrinsic", "pricing", "price", "value", "cash flows", "multiple", "market")),
    ("dcf-big-picture", "DCF big picture", "dcf-architecture", "A DCF values an asset by forecasting expected cash flows and discounting them at rates that reflect timing, risk, and currency.", "It is the central architecture for intrinsic value and the reference point for understanding why shortcuts can mislead.", "Damodaran builds DCF from first principles before adding the hard inputs: riskfree rates, premiums, cash flows, growth, and terminal value.", ("Treating DCF as a template.", "Mixing cash-flow definitions and discount-rate definitions."), ("cash-flow-consistency", "discount-rate-consistency", "terminal-value"), ("dcf", "discounted cash flow", "cash flow", "discount rate", "present value", "intrinsic value")),
    ("cash-flow-consistency", "Cash-flow consistency", "dcf-architecture", "Cash flows have to match the claim being valued, the currency chosen, the inflation assumption, and the discount rate.", "Most wrong valuations are not wrong because the math fails; they are wrong because the model combines incompatible assumptions.", "The early DCF sessions make consistency the hidden law that governs currency, nominal versus real inputs, taxes, debt, and equity claims.", ("Discounting equity cash flows at a cost of capital.", "Mixing real cash flows with nominal discount rates."), ("dcf-big-picture", "riskfree-rates", "free-cash-flow-to-firm"), ("cash flow", "cash flows", "consistency", "currency", "nominal", "real", "equity", "firm")),
    ("discount-rate-consistency", "Discount-rate consistency", "dcf-architecture", "The discount rate must be built in the same currency, inflation terms, claim definition, and risk frame as the cash flows.", "It is the guardrail that keeps DCF from becoming a collection of copied market inputs.", "Riskfree-rate, ERP, country-risk, beta, and cost-of-capital sessions all return to this matching principle.", ("Mixing currencies.", "Applying a firm discount rate to equity cash flows."), ("riskfree-rates", "cost-of-capital", "cash-flow-consistency"), ("discount rate", "discount rates", "currency", "nominal", "real", "cost of capital", "cost of equity")),
    ("riskfree-rates", "Riskfree rates", "dcf-architecture", "The riskfree rate is the base rate in the currency of the cash flows, free of default risk and internally consistent with inflation.", "It anchors every discount rate. If this base is wrong, the valuation is contaminated before risk premiums or betas enter.", "Sessions on riskfree rates separate currency choice, sovereign default risk, real versus nominal rates, and maturity matching.", ("Using a government bond yield mechanically when default risk exists.", "Using a dollar riskfree rate for non-dollar cash flows."), ("discount-rate-consistency", "equity-risk-premiums", "country-risk"), ("riskfree", "risk free", "default free", "government bond", "currency", "inflation", "treasury")),
    ("equity-risk-premiums", "Equity risk premiums", "risk-discount-rates", "The equity risk premium is the market price of bearing equity risk over a riskfree asset.", "It is one of the biggest levers in valuation and should reflect current market pricing, not just inherited historical averages.", "Damodaran develops historical, implied, and country-adjusted premiums as competing ways to estimate the market price of risk.", ("Using a stale historical premium without checking current market levels.", "Ignoring country risk in global businesses."), ("riskfree-rates", "country-risk", "cost-of-equity"), ("equity risk premium", "erp", "premium", "implied premium", "historical premium", "market risk")),
    ("country-risk", "Country risk", "risk-discount-rates", "Country risk captures exposure to macro, political, currency, and default risk beyond mature-market baseline risk.", "Global companies are exposed to risk where they operate, not merely where they are incorporated or listed.", "The country-risk sessions connect sovereign spreads, revenue exposure, and implied premiums to the cost of equity.", ("Assigning country risk by headquarters only.", "Double-counting country risk in both cash flows and discount rates."), ("equity-risk-premiums", "cost-of-equity", "discount-rate-consistency"), ("country risk", "sovereign", "default spread", "emerging market", "revenue exposure", "premium")),
    ("relative-risk-and-betas", "Relative risk and betas", "risk-discount-rates", "Beta is a measure of relative risk, but useful beta estimation has to reflect business mix and leverage rather than blindly trust regressions.", "The course uses beta to discipline risk measurement while warning against false precision from noisy market data.", "Damodaran moves from regression betas to bottom-up thinking and alternatives when firms are private, changing, or thinly traded.", ("Taking a regression beta as truth.", "Forgetting that financial leverage changes equity beta."), ("cost-of-equity", "cost-of-capital", "private-company-valuation"), ("beta", "betas", "relative risk", "regression", "bottom up", "unlevered", "levered")),
    ("cost-of-equity", "Cost of equity", "risk-discount-rates", "The cost of equity is the return required by equity investors for bearing the risk of residual cash flows.", "It is the equity discount rate and a central input in both firm and equity valuation.", "The course builds it from riskfree rates, equity risk premiums, country risk, and relative risk measures.", ("Treating cost of equity as what managers hope to earn.", "Using the same cost of equity for businesses with different risk."), ("riskfree-rates", "equity-risk-premiums", "relative-risk-and-betas"), ("cost of equity", "required return", "expected return", "capm", "beta", "premium")),
    ("cost-of-capital", "Cost of capital", "risk-discount-rates", "The cost of capital combines the costs of debt and equity in proportions that match the business and the cash flows being discounted.", "It is the firm-wide discount rate for operating cash flows, but only when it is constructed consistently.", "The transition from risk inputs to cash-flow valuation closes with cost of capital before the course turns to cash flows.", ("Using book-value weights by default.", "Applying one corporate cost of capital to every asset or geography."), ("cost-of-equity", "free-cash-flow-to-firm", "discount-rate-consistency"), ("cost of capital", "wacc", "cost of debt", "cost of equity", "debt", "equity")),
    ("free-cash-flow-to-firm", "Free cash flow to firm", "growth-cash-flows", "FCFF is operating cash flow available to all capital providers after taxes and reinvestment needed to sustain growth.", "It is the cash-flow engine for firm valuation and forces the analyst to separate accounting earnings from owner-relevant cash flows.", "The cash-flow sessions clean up operating income, taxes, reinvestment, working capital, and accounting adjustments.", ("Using net income as if it were free cash flow.", "Forgetting working capital or capital expenditures."), ("cash-flow-consistency", "reinvestment", "terminal-value"), ("free cash flow", "cash flow to firm", "fcff", "operating income", "tax", "working capital", "capex")),
    ("growth-estimation", "Growth estimation", "growth-cash-flows", "Growth has to be estimated from fundamentals, analyst judgment, past performance, and the operating story rather than assumed as an isolated input.", "Growth is often the most seductive valuation input, and the course makes it earn its way into the model.", "The growth block links revenue growth, margins, reinvestment, return on capital, and life-cycle stage.", ("Projecting high growth without asking how it is funded.", "Extrapolating history when the business is changing."), ("reinvestment", "growth-quality", "life-cycle-valuation"), ("growth", "expected growth", "revenue growth", "earnings growth", "return on capital", "fundamental growth")),
    ("reinvestment", "Reinvestment", "growth-cash-flows", "Reinvestment is the capital required to generate and sustain growth, including capex, working capital, acquisitions, and other growth investments.", "It is the cost side of the growth story. Growth without reinvestment discipline is usually fantasy.", "Damodaran ties growth to sales-to-capital ratios, return on capital, and reinvestment needs through the middle sessions.", ("Assuming growth is free.", "Using high terminal growth without matching reinvestment."), ("growth-estimation", "free-cash-flow-to-firm", "terminal-value"), ("reinvestment", "sales to capital", "capital invested", "working capital", "capex", "return on capital")),
    ("growth-quality", "Growth quality", "growth-cash-flows", "Growth is high quality only when it earns more than it costs, can be funded realistically, and does not destroy margins or returns.", "The course refuses to treat growth as automatically good; growth can destroy value when reinvestment economics are weak.", "Growth, cash-flow, and terminal-value sessions repeatedly connect growth to returns on capital and reinvestment intensity.", ("Rewarding revenue growth without checking returns.", "Assuming scale automatically improves economics."), ("growth-estimation", "reinvestment", "terminal-value"), ("growth", "quality", "return on capital", "reinvestment", "margins", "value creating")),
    ("terminal-value", "Terminal value", "dcf-architecture", "Terminal value captures cash flows beyond the explicit forecast period under stable-growth assumptions.", "It is often the largest part of a DCF, so small inconsistencies in mature growth, reinvestment, or risk can dominate the answer.", "The course treats terminal value as a consistency test: stable growth must fit the economy, the firm, and the reinvestment economics.", ("Using terminal growth higher than the economy forever.", "Letting terminal value rescue an implausible story."), ("dcf-big-picture", "reinvestment", "life-cycle-valuation"), ("terminal value", "stable growth", "forever", "terminal growth", "reinvestment", "mature")),
    ("stock-based-compensation", "Stock-based compensation", "growth-cash-flows", "Stock-based compensation is a real claim on future equity value, not a harmless non-cash expense to ignore.", "It matters because valuation is about who owns the future cash flows, not just what operating income looks like today.", "Loose-end sessions use SBC to show how accounting adjustments can shift value between current and future owners.", ("Adding back SBC without accounting for dilution.", "Treating employee equity as free compensation."), ("free-cash-flow-to-firm", "cash-flow-consistency", "life-cycle-valuation"), ("stock based compensation", "sbc", "options", "dilution", "employee options", "shares")),
    ("life-cycle-valuation", "Life-cycle valuation", "growth-cash-flows", "A company should be valued differently depending on whether it is young, scaling, mature, declining, private, distressed, or being acquired.", "The same template cannot carry every firm; the stage of the business changes the plausible story and the right inputs.", "The course explicitly pauses to value companies across the life cycle after building the core DCF machinery.", ("Using mature-company margins for startups.", "Using startup growth stories for declining firms."), ("growth-estimation", "terminal-value", "private-company-valuation"), ("life cycle", "young", "startup", "mature", "declining", "growth", "profitability")),
    ("pricing-101", "Pricing 101", "pricing-language", "Pricing estimates what an asset should trade for by looking at similar assets and the market's current pricing language.", "It is powerful because markets often transact on relative pricing, but it should not be confused with intrinsic value.", "The pricing block starts by separating pricing from valuation before moving into multiples and peer groups.", ("Calling pricing valuation.", "Choosing comparables to justify a desired price."), ("intrinsic-value-vs-pricing", "multiples-hide-assumptions", "peer-group-selection"), ("pricing", "price", "market", "comparables", "multiple", "relative valuation")),
    ("multiples-hide-assumptions", "Multiples hide assumptions", "pricing-language", "A multiple compresses assumptions about growth, risk, margins, capital intensity, and cash-flow quality into one market ratio.", "Multiples feel simple because assumptions are hidden; the analyst's job is to make those assumptions visible again.", "Damodaran repeatedly decomposes PE, EV/EBITDA, revenue multiples, and other ratios into their fundamental drivers.", ("Using a multiple without defining it consistently.", "Ignoring growth and risk differences across comparable firms."), ("pricing-101", "peer-group-selection", "market-pe-ratios"), ("multiple", "multiples", "pe ratio", "ev ebitda", "revenue multiple", "drivers")),
    ("peer-group-selection", "Peer group selection", "pricing-language", "A peer group is an analytical choice about which firms are similar enough for relative pricing.", "Peer choice is where pricing becomes both useful and dangerous: the answer can move with the comparable set.", "Pricing analytics sessions use peer groups and regressions to make relative pricing more disciplined.", ("Assuming peers are naturally given.", "Picking peers because they support the target price."), ("pricing-101", "multiples-hide-assumptions", "pricing-analytics"), ("peer group", "peers", "comparable", "comparables", "similar", "pricing analytics", "regression")),
    ("pricing-analytics", "Pricing analytics", "pricing-language", "Pricing analytics uses regressions, screens, and diagnostics to make relative pricing less arbitrary.", "It is the course's bridge between informal comparable-company work and a more disciplined market-pricing process.", "The peer-group session shows how to test whether differences in multiples are driven by fundamentals or by market noise.", ("Letting regression output replace judgment.", "Ignoring variable definitions and outliers."), ("peer-group-selection", "multiples-hide-assumptions", "market-pe-ratios"), ("pricing analytics", "regression", "peer group", "multiple", "outlier", "fundamentals")),
    ("market-pe-ratios", "Market PE ratios", "pricing-language", "Market PE ratios price entire markets by relating index prices to earnings and macro expectations.", "The concept shows that pricing logic applies at the market level too, where rates, growth, risk premiums, and mood collide.", "The tariff and market PE session applies pricing language to market-wide multiples and macro narratives.", ("Reading market PE without considering rates and growth.", "Treating macro narratives as if they bypass valuation math."), ("multiples-hide-assumptions", "equity-risk-premiums", "pricing-101"), ("market pe", "pe ratio", "index", "tariff", "market", "earnings yield")),
    ("asset-based-valuation-pricing", "Asset-based valuation and pricing", "special-situations", "Asset-based approaches anchor value or price in what the underlying assets are worth, especially when going-concern cash-flow logic is weak.", "They matter in liquidation, holding-company, commodity, financial, and distressed settings where operating forecasts are less reliable.", "The pricing closure introduces asset-based valuation and pricing as a different anchor after multiples.", ("Using book value as market value without adjustment.", "Applying asset-based logic to businesses whose value is mainly intangible growth."), ("private-company-valuation", "distressed-equity", "pricing-101"), ("asset based", "asset-based", "book value", "liquidation", "replacement cost", "assets")),
    ("private-company-valuation", "Private company valuation", "special-situations", "Private-company valuation changes when the marginal owner, diversification, control, illiquidity, and information quality differ from public markets.", "It forces the analyst to stop pretending the public-market template always applies.", "The private-business session brings owner-specific risk, liquidity discounts, and control into the valuation problem.", ("Using public-company betas without adjusting for owner risk.", "Treating illiquidity as a generic arbitrary discount."), ("relative-risk-and-betas", "liquidity-and-ownership", "control-value"), ("private company", "private business", "liquidity", "illiquidity", "undiversified", "owner")),
    ("liquidity-and-ownership", "Liquidity and ownership", "special-situations", "Liquidity, diversification, and control rights affect value when the owner cannot freely trade or diversify the asset.", "This shifts valuation from a clean security-market problem to a problem of who owns the asset and under what constraints.", "Private-company and control sessions make ownership frictions explicit rather than treating them as footnotes.", ("Applying the same discount for every private firm.", "Ignoring whether the buyer is diversified or has control."), ("private-company-valuation", "control-value", "asset-based-valuation-pricing"), ("liquidity", "illiquidity", "ownership", "owner", "control", "diversified", "undiversified")),
    ("ipo-valuation-and-pricing", "IPO valuation and pricing", "special-situations", "IPOs combine intrinsic valuation, pricing, market timing, narrative momentum, underwriter incentives, and investor demand.", "They expose the tension between what a business is worth and what the market can be persuaded to pay at issuance.", "The IPO session closes pricing and opens real options, showing how market process can dominate clean valuation logic.", ("Treating IPO price as proof of value.", "Ignoring how supply, demand, and narrative shape offering prices."), ("pricing-101", "peer-group-selection", "life-cycle-valuation"), ("ipo", "initial public offering", "offering", "underwriter", "pricing", "shares")),
    ("real-options", "Real options", "optionality-control", "A real option is the value of managerial flexibility under uncertainty when the firm owns a scarce right to wait, expand, abandon, or change course.", "It changes the role of uncertainty: uncertainty can increase value when downside is limited and upside remains open.", "Real options are introduced after IPOs and then applied to patents, natural resources, distressed equity, and strategic rights.", ("Using option language for any uncertain growth story.", "Ignoring the need for exclusivity and genuine flexibility."), ("patents-as-options", "natural-resources-as-options", "distressed-equity"), ("real option", "option", "options", "flexibility", "exclusive", "volatility", "right to wait")),
    ("patents-as-options", "Patents as options", "optionality-control", "A patent can be valued as an option when it gives exclusive rights to commercialize a product if future economics become attractive.", "It is a disciplined way to value rights that may be worthless under current cash flows but valuable under future states.", "The patents session applies option logic to technology and drug-development style claims.", ("Valuing every idea like a patent.", "Ignoring development cost, expiration, or probability of commercial success."), ("real-options", "natural-resources-as-options", "terminal-value"), ("patent", "patents", "drug", "exclusive", "expiration", "option", "commercialize")),
    ("natural-resources-as-options", "Natural resources as options", "optionality-control", "A natural-resource reserve can behave like an option because the owner can choose when to extract as commodity prices and costs change.", "It shows how option logic applies outside technology when the asset has a right to wait and uncertain payoff.", "The natural-resource session uses reserves, commodity prices, extraction cost, and time to develop the option frame.", ("Ignoring extraction cost and reserve life.", "Treating all commodity exposure as option value."), ("real-options", "patents-as-options", "asset-based-valuation-pricing"), ("natural resource", "oil", "reserve", "commodity", "extraction", "option", "price")),
    ("distressed-equity", "Distressed equity", "optionality-control", "Equity in a deeply distressed firm can resemble an option on the firm's assets after debt claims are considered.", "It explains why equity can retain value even when conventional DCF equity value looks close to zero.", "The distressed-equity session uses option logic to value residual claims when debt creates asymmetric payoffs.", ("Treating distressed equity like normal equity.", "Ignoring debt maturity, asset volatility, and claim priority."), ("real-options", "acquisition-valuation", "asset-based-valuation-pricing"), ("distressed equity", "distress", "debt", "option", "asset value", "bankruptcy", "equity")),
    ("acquisition-valuation", "Acquisition valuation", "special-situations", "Acquisition valuation asks what a target is worth to a buyer, including standalone value, synergy, control changes, and deal process constraints.", "It separates value creation from value transfer: paying more only makes sense if the buyer can create or capture incremental value.", "Late sessions connect distressed equity, acquisition pricing, synergy, and value enhancement before the final control discussion.", ("Paying for synergy without specifying who creates it.", "Confusing strategic desire with incremental value."), ("control-value", "synergy", "value-enhancement"), ("acquisition", "takeover", "target", "synergy", "control", "premium", "deal")),
    ("synergy", "Synergy", "special-situations", "Synergy is incremental value created by combining businesses through higher cash flows, lower risk, better reinvestment, or financing improvements.", "It is often used to justify acquisition premiums, so the course forces it into measurable operating or financial claims.", "The acquisition sessions treat synergy as something to value separately and assign to the party that can actually create it.", ("Using synergy as a vague acquisition slogan.", "Letting the seller capture all synergy through the purchase price."), ("acquisition-valuation", "control-value", "value-enhancement"), ("synergy", "synergies", "merger", "acquisition", "cost savings", "growth", "premium")),
    ("value-enhancement", "Value enhancement", "optionality-control", "Value enhancement identifies actions that increase firm value by changing cash flows, growth, risk, reinvestment, financing, or asset use.", "It turns valuation from a passive estimate into an active diagnostic of what management can improve.", "The penultimate session uses value enhancement to connect acquisition closure with the operating levers behind control value.", ("Calling any restructuring value enhancing without quantifying the lever.", "Improving accounting optics without improving value."), ("control-value", "acquisition-valuation", "terminal-value"), ("value enhancement", "enhance value", "improve value", "restructure", "cash flows", "cost of capital", "growth")),
    ("control-value", "Control value", "optionality-control", "Control value is the incremental value from changing who makes decisions and what decisions get made.", "A control premium is justified only if new control can improve operations, financing, payout, investment, or strategy.", "The final session closes the course by returning valuation to governance, decision rights, and the power to change outcomes.", ("Paying a control premium for voting rights alone.", "Assuming every acquirer can run the target better."), ("acquisition-valuation", "value-enhancement", "liquidity-and-ownership"), ("control", "control premium", "premium", "management", "decision", "governance", "acquisition")),
]


CONCEPTS: tuple[ConceptRule, ...] = tuple(ConceptRule(*spec) for spec in CONCEPT_SPECS)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z\-']{2,}", text.lower()) if w not in STOPWORDS]


def keyword_score(text: str, keywords: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(lowered.count(keyword) for keyword in keywords)


def first_sentence(text: str, limit: int = 280) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return "Transcript text is not available for this session."
    sentence = compact[:limit]
    for index, char in enumerate(compact[:limit], 1):
        if index >= 80 and char in ".!?":
            sentence = compact[:index]
            break
    return sentence[:limit].rstrip()


def clip_words(text: str, limit: int = 42) -> str:
    words = re.sub(r"\s+", " ", text).strip().split()
    if len(words) <= limit:
        return " ".join(words)
    return " ".join(words[:limit]).rstrip(" ,;:") + "..."


def esc(value: Any) -> str:
    return html.escape(str(value))


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


def group_by(items: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        groups.setdefault(item[key], []).append(item)
    return groups


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
            "excerpt": clip_words(cue.get("text", ""), 46),
            "start_seconds": cue.get("start_seconds"),
            "end_seconds": cue.get("end_seconds"),
        }
    return {"excerpt": session.get("summary", ""), "start_seconds": None, "end_seconds": None}


def build_concepts(course_root: Path, sessions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    session_texts: dict[int, str] = {}
    for session in sessions:
        text_ref = session.get("clean_txt")
        text_path = course_root / text_ref if text_ref else None
        text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path and text_path.is_file() else ""
        session_texts[int(session["index"])] = f"{session.get('title', '')}\n{text}"

    concepts: list[dict[str, Any]] = []
    evidence_map: dict[str, Any] = {"concepts": {}}
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
            evidence.append(
                {
                    "session": session["index"],
                    "title": session["title"],
                    "url": session["url"],
                    "score": score,
                    **load_cue_excerpt(course_root, session, rule.keywords),
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
        }
        concepts.append(concept)
        evidence_map["concepts"][rule.slug] = evidence
    return concepts, evidence_map


def discussion_for(item: dict[str, Any]) -> str:
    terms = ", ".join(item["top_terms"][:5])
    return (
        f"This session sits inside '{item['theme_name']}' and sharpens the course around '{item['subtheme_name']}'. "
        f"The transcript vocabulary clusters around {terms}, so the class is doing more than covering a topic list: "
        "it is pushing one specific valuation bottleneck into the open and showing how Damodaran wants it disciplined. "
        "In the broader course arc, this is where story, pricing, risk, growth, optionality, or control gets translated "
        "into a narrower operating rule the analyst can actually use."
    )


def session_brief_for(item: dict[str, Any]) -> str:
    title = item["title"].lower()
    if "preview" in title:
        return "A short preview that frames valuation as a broad discipline before the formal MBA sequence begins."
    if item["theme_slug"] == "valuation-discipline":
        return "This session frames valuation as a disciplined process for converting stories, uncertainty, and market behavior into testable estimates of value."
    if item["theme_slug"] == "dcf-architecture":
        return "This session builds the intrinsic valuation architecture: cash flows, discount rates, currency, inflation, and terminal value must all be internally consistent."
    if item["theme_slug"] == "risk-discount-rates":
        return "This session turns risk into discount-rate inputs: riskfree rates, equity risk premiums, country risk, betas, debt costs, and costs of capital."
    if item["theme_slug"] == "growth-cash-flows":
        return "This session connects growth stories to cash-flow reality, margins, reinvestment, stock-based compensation, life-cycle stage, and terminal assumptions."
    if item["theme_slug"] == "pricing-language":
        return "This session separates pricing from valuation and shows how multiples, comparables, peer groups, and market-level ratios work as a different language."
    if item["theme_slug"] == "special-situations":
        return "This session adapts valuation to special settings such as private firms, IPOs, asset-based cases, distressed businesses, and acquisitions."
    if item["theme_slug"] == "optionality-control":
        return "This session studies real options, distressed claims, patents, natural resources, value enhancement, acquisitions, and the value of control."
    return item.get("summary", "Transcript-backed session brief unavailable.")


def course_thesis_markdown(sessions: list[dict[str, Any]], themes: list[dict[str, Any]], concepts: list[dict[str, Any]]) -> str:
    total_words = sum(item.get("word_count", 0) for item in sessions)
    lines = [
        "# Course Thesis",
        "",
        "Damodaran's Valuation MBA Spring 2025 course is a sustained argument that valuation is translated judgment. The analyst starts with a story about a business, turns that story into explicit assumptions, keeps those assumptions internally consistent, and then separates intrinsic value from the market's pricing language.",
        "",
        "The course is not a DCF template. It is an operating system for thinking about value across public companies, private businesses, IPOs, distressed claims, acquisitions, patents, natural resources, and control situations.",
        "",
        f"This atlas is grounded in {len(sessions)} playlist records, {sum(1 for item in sessions if item.get('transcript_status') == 'available')} transcript-backed sessions, and {total_words:,} transcript words.",
        "",
        "## Argument Spine",
        "",
        "1. Start with a story, but force the story into numbers.",
        "2. Separate intrinsic value from pricing before choosing tools.",
        "3. Build DCF inputs so cash flows, discount rates, currency, inflation, and claim definitions match.",
        "4. Estimate risk through riskfree rates, equity risk premiums, country risk, betas, and costs of capital.",
        "5. Treat growth as valuable only when margins and reinvestment economics support it.",
        "6. Use pricing consciously as a relative market language, not as hidden intrinsic valuation.",
        "7. Adapt valuation to private firms, IPOs, asset-based cases, distressed firms, acquisitions, options, and control.",
        "",
        "## Themes",
        "",
    ]
    for theme in themes:
        lines.extend([f"### {theme['name']}", "", theme["thesis"], "", f"Sessions: {', '.join(str(i) for i in theme['session_indexes'])}", ""])
    lines.extend(["## Concept Layer", ""])
    for concept in concepts:
        lines.append(f"- **{concept['name']}**: {concept['meaning']}")
    return "\n".join(lines)


def session_briefs_markdown(sessions: list[dict[str, Any]]) -> str:
    lines = [
        "# Session Briefs",
        "",
        "Plain-English course map for `Valuation MBA Spring 2025`, generated from the transcript index and organized by each session's dominant theme.",
        "",
    ]
    for theme_name, grouped in group_by(sessions, "theme_name").items():
        lines.extend([f"## {theme_name}", ""])
        for item in grouped:
            lines.extend([f"`{item['index']:03d}` {item['title']}  ", session_brief_for(item), ""])
    lines.extend(
        [
            "## High-level course arc",
            "",
            "1. Establish valuation philosophy and the value-versus-price distinction.",
            "2. Build intrinsic valuation from cash-flow and discount-rate consistency.",
            "3. Estimate risk and growth without importing incoherent assumptions.",
            "4. Translate stories into revenue, margin, reinvestment, and terminal-value inputs.",
            "5. Shift to pricing through multiples, peer groups, and market ratios.",
            "6. Extend the framework to private firms, IPOs, options, distressed equity, acquisitions, value enhancement, and control.",
        ]
    )
    return "\n".join(lines)


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
  <main>
{body}
  </main>
</body>
</html>
"""


def session_card(record: dict[str, Any]) -> str:
    return f"""
    <article class="card">
      <div class="meta">Session {record["index"]:02d} · {record.get("word_count", 0):,} words</div>
      <h3>{esc(record["title"])}</h3>
      <p>{esc(record["summary"])}</p>
      <div class="tags"><span>{esc(record["theme_name"])}</span><span>{esc(record["subtheme_name"])}</span></div>
      <a href="{esc(record["url"])}">YouTube</a>
    </article>"""


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
  --ink: #191713;
  --muted: #675f52;
  --line: #d8cdbb;
  --paper: #f4efe4;
  --panel: rgba(255,255,255,.82);
  --accent: #0b6f73;
  --accent-2: #9a4b18;
  --wash: #e9f3f1;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Georgia, 'Times New Roman', serif; color: var(--ink); background: radial-gradient(circle at 10% 0%, #f9e8cf 0, transparent 34%), linear-gradient(135deg, #fbf8ef 0%, #edf4f1 54%, #f5eadf 100%); }
.top { display: flex; justify-content: space-between; gap: 24px; align-items: end; padding: 40px min(6vw, 72px) 24px; border-bottom: 1px solid var(--line); }
.eyebrow { margin: 0 0 8px; color: var(--accent-2); text-transform: uppercase; letter-spacing: .08em; font: 700 12px/1.2 ui-sans-serif, system-ui, sans-serif; }
h1 { margin: 0; font-size: clamp(34px, 5vw, 68px); line-height: .95; max-width: 920px; }
h2 { font-size: 30px; margin: 0 0 16px; }
h3 { margin: 8px 0 10px; font-size: 21px; }
p { line-height: 1.6; }
nav { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
nav a, .button { color: var(--ink); text-decoration: none; border: 1px solid var(--line); background: rgba(255,255,255,.72); padding: 8px 11px; border-radius: 4px; font: 700 13px/1 ui-sans-serif, system-ui, sans-serif; }
nav a.active, nav a:hover, .button:hover { background: var(--accent); color: white; border-color: var(--accent); }
main { padding: 34px min(6vw, 72px) 64px; }
.hero { max-width: 980px; font-size: 20px; color: var(--muted); }
.thesis { max-width: 1020px; display: grid; gap: 18px; }
.essay { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 22px; box-shadow: 0 18px 40px rgba(25,23,19,.05); }
.essay p { margin: 0 0 14px; }
.kicker { font: 700 14px/1.4 ui-sans-serif, system-ui, sans-serif; color: var(--accent); text-transform: uppercase; letter-spacing: .05em; }
.split { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(260px, .8fr); gap: 18px; align-items: start; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 16px; margin-top: 24px; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 18px; box-shadow: 0 18px 40px rgba(25,23,19,.06); }
.meta { color: var(--accent-2); font: 700 12px/1.4 ui-sans-serif, system-ui, sans-serif; text-transform: uppercase; letter-spacing: .05em; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
.tags span { background: var(--wash); color: #145255; border: 1px solid #cfe2dd; padding: 5px 8px; border-radius: 999px; font: 700 12px/1 ui-sans-serif, system-ui, sans-serif; }
.list { display: grid; gap: 12px; }
.row { background: rgba(255,255,255,.76); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; }
.row strong { display: block; margin-bottom: 6px; }
.evidence { border-left: 4px solid var(--accent); }
.concept-links { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.concept-links a { color: var(--accent); background: #eef6f3; border: 1px solid #cfe2dd; border-radius: 999px; padding: 6px 9px; text-decoration: none; font: 700 12px/1 ui-sans-serif, system-ui, sans-serif; }
ol.arc { padding-left: 22px; line-height: 1.7; }
@media (max-width: 760px) { .top { display: block; } nav { justify-content: flex-start; margin-top: 20px; } .split { grid-template-columns: 1fr; } }
"""
    (site_dir / "assets").mkdir(parents=True, exist_ok=True)
    write_text(site_dir / "assets/styles.css", css)

    total_words = sum(item.get("word_count", 0) for item in sessions)
    home_body = f"""
    <section class="hero">
      <p>{esc(manifest["title"])} is organized as a transcript-backed atlas of Damodaran's valuation course: story-to-number discipline, DCF architecture, discount-rate construction, cash-flow and growth economics, pricing, special situations, optionality, acquisitions, and control.</p>
      <p>{len(sessions)} videos indexed · {total_words:,} transcript words · {len(themes)} themes · {len(subthemes)} subthemes · {len(concepts)} concepts.</p>
      <p><a class="button" href="course-thesis.html">Read the thesis</a> <a class="button" href="concepts/index.html">Browse concepts</a> <a class="button" href="sessions.html">Browse sessions</a></p>
    </section>
    <section class="essay" style="margin-top:24px">
      <p class="kicker">Course argument</p>
      <p>Valuation MBA Spring 2025 is a course about disciplined translation: stories become inputs, inputs obey consistency, intrinsic value stays separate from pricing, and special situations reveal where ownership, optionality, and control change the answer.</p>
    </section>
    <section class="grid">
      {''.join(f'<article class="card"><div class="meta">{len(t["session_indexes"])} sessions</div><h3>{esc(t["name"])}</h3><p>{esc(t["thesis"])}</p></article>' for t in themes)}
    </section>
"""
    write_text(site_dir / "index.html", html_page(manifest["title"], home_body, "Overview"))

    thesis_body = f"""
    <section class="thesis">
      <article class="essay">
        <p class="kicker">Long-form synthesis</p>
        <h2>The real thesis of Valuation MBA Spring 2025</h2>
        <p>Damodaran's valuation course is not mainly about producing DCF files. It is a sustained discipline for making a business story explicit, converting it into numbers, checking the internal consistency of those numbers, and deciding whether the resulting value is different from the price the market is willing to pay.</p>
        <p>The full arc matters because valuation breaks at the boundaries: early-stage firms have stories before earnings, mature firms hide value in reinvestment and terminal assumptions, private firms add owner and liquidity frictions, IPOs mix value with selling process, distressed equity behaves like an option, and acquisitions add control and synergy claims.</p>
      </article>
      <article class="essay">
        <h2>Argument spine</h2>
        <ol class="arc">
          <li>Start with a story, but force the story into numbers.</li>
          <li>Separate intrinsic value from pricing before choosing tools.</li>
          <li>Keep cash flows, discount rates, currency, inflation, and claim definitions consistent.</li>
          <li>Build discount rates from riskfree rates, premiums, country risk, betas, and capital costs.</li>
          <li>Make growth pay for itself through margins and reinvestment economics.</li>
          <li>Use multiples and peer groups as pricing tools, not disguised valuation truth.</li>
          <li>Extend the framework to private firms, IPOs, real options, distressed equity, acquisitions, value enhancement, and control.</li>
        </ol>
      </article>
      <section class="grid">
        {''.join(f'<article class="card"><div class="meta">{len(t["session_indexes"])} sessions</div><h3>{esc(t["name"])}</h3><p>{esc(t["thesis"])}</p></article>' for t in themes)}
      </section>
    </section>
"""
    write_text(site_dir / "course-thesis.html", html_page("Valuation Course Thesis", thesis_body, "Thesis"))

    theme_body = "<section class=\"grid\">" + "".join(
        f"""<article class="card">
      <div class="meta">{len(theme["session_indexes"])} sessions · {', '.join(str(i) for i in theme["session_indexes"])}</div>
      <h3>{esc(theme["name"])}</h3>
      <p>{esc(theme["thesis"])}</p>
      <div class="tags">{''.join(f'<span>{esc(term)}</span>' for term, _ in theme["evidence_terms"][:6])}</div>
    </article>"""
        for theme in themes
    ) + "</section>"
    write_text(site_dir / "themes.html", html_page("Valuation Themes", theme_body, "Themes"))

    subtheme_body = "<section class=\"list\">" + "".join(
        f"""<div class="row">
      <div class="meta">{esc(subtheme["theme"])} · sessions {', '.join(str(i) for i in subtheme["session_indexes"])}</div>
      <strong>{esc(subtheme["name"])}</strong>
      <span>{esc('; '.join(subtheme["session_titles"]))}</span>
    </div>"""
        for subtheme in subthemes
    ) + "</section>"
    write_text(site_dir / "subthemes.html", html_page("Valuation Subthemes", subtheme_body, "Subthemes"))

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
    write_text(concepts_dir / "index.html", html_page("Valuation Concepts", concept_index_body, "Concepts", asset_prefix="../"))

    concept_by_slug = {concept["slug"]: concept for concept in concepts}
    for concept in concepts:
        evidence_html = "".join(
            f"""<article class="row evidence">
        <div class="meta">Session {item["session"]:02d} · score {item["score"]}</div>
        <strong>{esc(item["title"])}</strong>
        <p>{esc(item["excerpt"])}</p>
        <a href="{esc(item["url"])}">YouTube</a>
      </article>"""
            for item in concept.get("evidence", [])
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
        write_text(concepts_dir / f"{concept['slug']}.html", html_page(concept["name"], body, "Concepts", asset_prefix="../"))

    evidence_body = "<section class=\"hero\"><p>Evidence links each concept to the sessions and cue excerpts where the course language most strongly matches that idea.</p></section><section class=\"list\">"
    for concept in concepts:
        evidence_body += f'<article class="row"><strong><a href="concepts/{esc(concept["slug"])}.html">{esc(concept["name"])}</a></strong>'
        evidence_body += "<p>" + "; ".join(
            f'Session {item["session"]:02d}: {esc(item["title"])}' for item in concept.get("evidence", [])[:4]
        ) + "</p></article>"
    evidence_body += "</section>"
    write_text(site_dir / "evidence.html", html_page("Valuation Evidence Map", evidence_body, "Evidence"))

    discussion_body = "<section class=\"list\">" + "".join(
        f"""<article class="row">
      <div class="meta">Session {item["session"]:02d} · {esc(item["theme"])} · {esc(item["subtheme"])}</div>
      <strong>{esc(item["title"])}</strong>
      <p>{esc(item["discussion"])}</p>
      <a href="{esc(item["url"])}">YouTube</a>
    </article>"""
        for item in discussions
    ) + "</section>"
    write_text(site_dir / "discussions.html", html_page("Course Discussions", discussion_body, "Discussions"))

    session_body = "<section class=\"grid\">" + "".join(session_card(item) for item in sessions) + "</section>"
    write_text(site_dir / "sessions.html", html_page("Course Sessions", session_body, "Sessions"))


def build(course_root: Path) -> None:
    manifest = load_json(course_root / "raw-material/youtube/course-manifest.json")
    transcript_index = load_json(course_root / "raw-material/youtube/transcript-index.json")
    analysis_dir = course_root / "analysis"
    site_dir = course_root / "site"

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
    print(f"built {len(enriched)} sessions, {len(themes)} themes, {len(subthemes)} subthemes, {len(concepts)} concepts")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-root", default=".")
    args = parser.parse_args()
    build(Path(args.course_root).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
