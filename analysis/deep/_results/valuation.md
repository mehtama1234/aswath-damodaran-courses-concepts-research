# Damodaran valuation — verified measured results (a real DCF engine, one worked company)

Every number below is COMPUTED by a discounted-cash-flow (DCF) engine we actually ran on one
self-consistent example company, "Northwind". The inputs are stated assumptions (valuation always
rests on a story); the engine computes the consequences honestly. The same method applies to any
real firm by plugging in its financials. Script: scripts/experiments/valuation_run.py. Cite verbatim.

Northwind base assumptions: $10,000M revenue last year; revenue grows 15% for 5 years then fades to
2.5% by year 10; 25% operating margin; 25% tax; return on new investment (ROIC) 20%; cost of capital
(discount rate) 9%; perpetual growth after year 10 = 2.5%; 1,000M shares.

## EXP1 — intrinsic value = present value of future cash flows (concept: intrinsic-value-dcf)
- Discounted near-term cash flows (years 1-10): $9,931M. Plus discounted terminal value: $33,296M.
- Enterprise value $43,227M -> intrinsic value **$43.23 per share**.
- Insight: a business is worth the cash it will hand its owners over its life, each future dollar
  pulled back to today at a rate that reflects its risk. That is the whole idea of intrinsic value.

## EXP2 — most of the value is the terminal value, and it's fragile (concept: terminal-value)
- The terminal value (everything beyond year 10, collapsed into one number) is **77%** of the total.
- Sensitivity of value/share to the perpetual growth rate: 1.5% -> $40.14; 2.0% -> $41.58;
  2.5% -> $43.23; 3.0% -> $45.14; 3.5% -> $47.39.
- A 2-point change in that one hard-to-know number swings the value ~18% ($40 -> $47).
- Insight: the bulk of "today's worth" is a guess about a distant, steady future — so the terminal
  value assumptions deserve the most scrutiny, and the perpetual growth rate can't exceed the economy's.

## EXP3 — the discount rate is risk turned into a number (concept: cost-of-capital)
- Sweeping the cost of capital (higher risk -> higher rate -> lower value): 7% -> $69.20;
  8% -> $53.75; 9% -> $43.23; 10% -> $35.66; 12% -> $25.60.
- Insight: identical future cash flows are worth far less when discounted at a higher, riskier rate.
  The cost of capital is where risk enters a valuation — it is not a footnote, it is a lever that
  more than halves the value across a plausible range.

## EXP4 — reverse DCF: what is the market price already assuming? (concept: reverse-dcf)
- Suppose Northwind trades at **$95** (well above our $43.23 estimate). Solving for the near-term
  revenue growth the price requires: **32.4% per year for 5 years** (versus our assumed 15%).
- Insight: instead of arguing about the "right" value, invert the price — it turns any market price
  into the growth story it is quietly assuming, which you can then judge as plausible or not.

## EXP5 — growth is not free; it only adds value above the cost of capital (concept: growth-and-reinvestment)
- Same 15% growth, three different returns on the money reinvested to fund it (ROIC):
  ROIC 6% -> **$14.41** (destroys value, below the 9% cost of capital); ROIC 9% -> **$22.60**
  (adds nothing, exactly equal to the cost of capital); ROIC 20% -> **$43.23** (creates value).
- Insight: value comes from the SPREAD between the return on invested capital and the cost of that
  capital, not from growth itself. Growth funded at a break-even return is worth nothing.

## EXP6 — the story drives the number (concept: narrative-and-numbers)
- Same company, same spreadsheet, three stories: "category winner" (22% growth, 30% margins)
  -> **$70.12**; base story -> **$43.23**; "niche player" (8% growth, 18% margins, ROIC 12%)
  -> **$18.99**.
- Insight: a valuation is a story told in numbers. The spreadsheet doesn't create the value — the
  narrative you believe about the business does, and the numbers just make that story explicit and
  checkable.

## EXP7 — a value is a distribution, not a point; margin of safety (concept: margin-of-safety)
- Running the DCF 20,000 times over plausible ranges for growth, margin, cost of capital, and ROIC
  gives a value RANGE: 10th percentile **$27.58**, median **$41.91**, 90th percentile **$64.66**.
- At the $95 market price, only **1%** of scenarios value the company above the price.
- Insight: because every input is uncertain, the honest output is a spread. "Margin of safety" means
  buying far enough below the median that even an unlucky combination of assumptions still works out.

## EXP8 — a multiple is a DCF in disguise (concept: relative-valuation-multiples)
- The base DCF value implies a fair price-to-earnings multiple of **20.0x** current earnings; the
  "category winner" story implies **32.5x** on the SAME current earnings.
- Insight: a price-to-earnings (or similar) multiple is just a compressed valuation. Two companies at
  the same multiple are not equally cheap — the multiple each deserves is set by growth, the return on
  that growth, and risk, which is exactly what the full DCF spells out.
