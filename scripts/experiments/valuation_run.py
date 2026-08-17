"""Real valuation runs: a discounted-cash-flow (DCF) engine, run on ONE self-consistent
example company so every number ties out. Inputs are ASSUMPTIONS (that is the whole point of
valuation); the engine computes the consequences honestly. No external data — the method
applies to any real firm by plugging in its financials. numpy only."""
import numpy as np

# ---- the example company: "Northwind" (all figures are stated assumptions) ----
BASE = dict(
    revenue0=10_000.0,      # $M revenue last year
    g_high=0.15,            # revenue growth, years 1-5
    g_fade_to=0.025,        # growth fades to this by year 10 (the stable rate)
    op_margin=0.25,         # target operating (EBIT) margin
    tax=0.25,
    roic=0.20,             # return on invested capital on new investment
    wacc=0.09,             # cost of capital (discount rate)
    g_term=0.025,          # perpetual growth after year 10 (must be <= risk-free ~ 0.04)
    shares=1000.0,         # millions of shares
    N=10,
)

def dcf(p, verbose=False):
    R=p['revenue0']; gs=np.concatenate([np.full(5,p['g_high']),
        np.linspace(p['g_high'], p['g_fade_to'], 5)])   # growth fades years 6-10
    revs=[]; r=R
    for g in gs: r=r*(1+g); revs.append(r)
    revs=np.array(revs)
    ebit=revs*p['op_margin']; nopat=ebit*(1-p['tax'])
    # reinvestment to fund growth: reinvest = growth / ROIC  of NOPAT
    reinv_rate=np.clip(gs/p['roic'],0,1.5)
    fcff=nopat*(1-reinv_rate)
    disc=1/(1+p['wacc'])**np.arange(1,p['N']+1)
    pv_fcff=fcff*disc
    # terminal value at year N: stable growth, reinvest = g_term/roic
    term_reinv=p['g_term']/p['roic']
    fcff_term=nopat[-1]*(1+p['g_term'])*(1-term_reinv)
    tv=fcff_term/(p['wacc']-p['g_term'])
    pv_tv=tv*disc[-1]
    ev=pv_fcff.sum()+pv_tv
    per_share=ev/p['shares']
    if verbose:
        return dict(revs=revs,fcff=fcff,pv_fcff=pv_fcff,pv_tv=pv_tv,ev=ev,per_share=per_share,tv=tv)
    return per_share

base_val=dcf(BASE,verbose=True)
print("=== EXP1: intrinsic value = present value of future cash flows (DCF) ===")
print(f"  Northwind: $10,000M revenue, 15% growth fading to 2.5%, 25% margins, 9% cost of capital.")
print(f"  sum of discounted near-term cash flows: ${base_val['pv_fcff'].sum():,.0f}M")
print(f"  plus discounted terminal value:         ${base_val['pv_tv']:,.0f}M")
print(f"  = enterprise value ${base_val['ev']:,.0f}M  ->  intrinsic value per share ${base_val['per_share']:.2f}")

print("\n=== EXP2: most of the value lives in the terminal value (and it's fragile) ===")
frac=base_val['pv_tv']/base_val['ev']*100
print(f"  the terminal value is {frac:.0f}% of the total — most of 'today's worth' is beyond year 10.")
print("  sensitivity of value/share to the perpetual growth rate g:")
for g in [0.015,0.02,0.025,0.03,0.035]:
    v=dcf({**BASE,'g_term':g})
    print(f"    g_term = {g*100:.1f}%  ->  ${v:.2f} per share")
print("  => a 2-point change in one hard-to-know perpetual-growth number swings the value ~18% ($40 to $47),")
print("     and it sits inside the 77% of value that is already the fragile terminal piece.")

print("\n=== EXP3: the discount rate (cost of capital) is risk priced as a number ===")
print("  sweep the cost of capital (higher risk -> higher rate -> lower value):")
for w in [0.07,0.08,0.09,0.10,0.12]:
    v=dcf({**BASE,'wacc':w})
    print(f"    cost of capital {w*100:.0f}%  ->  ${v:.2f} per share")
print("  => the same cash flows are worth far less when discounted at a higher risk-based rate.")

print("\n=== EXP4: reverse DCF — what growth is the market price assuming? ===")
price=95.0   # assume Northwind trades at $95 (a stated market price)
lo,hi=0.0,0.60
for _ in range(60):
    mid=(lo+hi)/2
    if dcf({**BASE,'g_high':mid}) < price: lo=mid
    else: hi=mid
print(f"  suppose the market price is ${price:.0f} (well above our ${base_val['per_share']:.2f} estimate).")
print(f"  solving for the near-term growth the price requires: {mid*100:.1f}% per year for 5 years")
print(f"  (vs our assumed 15%). Reverse-DCF turns a price into the STORY it is quietly assuming.")

print("\n=== EXP5: growth is not free — it only adds value when ROIC beats the cost of capital ===")
print("  same 15% growth, three different returns on the money reinvested to get it:")
for roic in [0.06,0.09,0.20]:
    v=dcf({**BASE,'roic':roic})
    tag="destroys value (ROIC<WACC)" if roic<BASE['wacc'] else ("adds nothing (ROIC=WACC)" if abs(roic-BASE['wacc'])<1e-9 else "creates value (ROIC>WACC)")
    print(f"    ROIC {roic*100:.0f}%  ->  ${v:.2f} per share   {tag}")
print("  => growth funded at a return equal to the cost of capital is worth nothing; the value")
print("     comes from the SPREAD between the return and the cost, not from growth itself.")

print("\n=== EXP6: the story drives the number — two narratives, two valuations ===")
bull={**BASE,'g_high':0.22,'op_margin':0.30}          # 'category winner'
bear={**BASE,'g_high':0.08,'op_margin':0.18,'roic':0.12}  # 'niche, competed-away'
print(f"  'category winner' story (22% growth, 30% margins): ${dcf(bull):.2f} per share")
print(f"  'niche player' story (8% growth, 18% margins):      ${dcf(bear):.2f} per share")
print(f"  base story:                                          ${base_val['per_share']:.2f} per share")
print("  => same company, same spreadsheet — the value swings with the STORY you believe.")

print("\n=== EXP7: margin of safety — a value is a distribution, not a point ===")
rng=np.random.default_rng(0); vals=[]
for _ in range(20000):
    v=dcf({**BASE,
        'g_high':rng.normal(0.15,0.04),
        'op_margin':np.clip(rng.normal(0.25,0.04),0.05,0.6),
        'wacc':np.clip(rng.normal(0.09,0.01),0.05,0.15),
        'roic':np.clip(rng.normal(0.20,0.04),0.05,0.5)})
    vals.append(v)
vals=np.array(vals); p10,p50,p90=np.percentile(vals,[10,50,90])
below=(vals>price).mean()*100
print(f"  running the DCF 20,000 times over plausible assumption ranges gives a value RANGE:")
print(f"    10th pct ${p10:.2f}  |  median ${p50:.2f}  |  90th pct ${p90:.2f}")
print(f"  at the ${price:.0f} market price, only {below:.0f}% of scenarios value it above the price")
print(f"  => 'margin of safety' means buying far enough below the median that even a bad draw is OK.")

print("\n=== EXP8: a multiple is a DCF in disguise (relative valuation) ===")
# implied fair P/E from the base DCF: price/earnings where earnings = year-1 NOPAT/share
eps1=base_val['revs'][0]*BASE['op_margin']*(1-BASE['tax'])/BASE['shares']
pe_base=base_val['per_share']/eps1
pe_bull=dcf(bull)/eps1
print(f"  our base value implies a fair price-to-earnings multiple of {pe_base:.1f}x")
print(f"  the 'category winner' story implies {pe_bull:.1f}x on the SAME current earnings")
print("  => two firms at the same P/E are NOT equally cheap: the multiple you deserve is set by")
print("     growth, the return on that growth, and risk — the very things the DCF spells out.")
