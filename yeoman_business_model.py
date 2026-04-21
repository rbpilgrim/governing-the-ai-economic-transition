"""
Yeoman business model: what fleet size and surtax achieves $75k net income?

Key questions:
  1. What gross revenue does a yeoman need to net $75k after all expenses and tax?
  2. What fleet size (number of robots) achieves that at competitive market prices?
  3. What corporate robot income surtax raises the market floor to that price?
  4. What is the efficiency cost of that surtax?

Ignored: differential compute costs by task complexity (acknowledged — 
higher-complexity tasks cost more tokens; margin fraction roughly constant).
"""

# ── Parameters ─────────────────────────────────────────────────────────────
NET_TARGET        = 75_000    # after all expenses and income tax
YEOMAN_TAX_RATE   = 0.22     # effective income tax on yeoman business profit
CORP_RETURN_TARGET= 0.25     # corps need 25% return on COGS to invest

# Robot unit economics
ROBOT_COST        = 150_000
ROBOT_LIFE_YR     = 7
UTIL_YEOMAN       = 0.70
UTIL_CORP         = 0.90     # corps utilise more efficiently
HOURS_YR          = 8_760

HOURS_YEOMAN      = HOURS_YR * UTIL_YEOMAN   # 6,132
HOURS_CORP        = HOURS_YR * UTIL_CORP      # 7,884

# Yeoman per-robot annual costs
ROBOT_AMORT_YR    = ROBOT_COST / ROBOT_LIFE_YR              # $21,429
ENERGY_MAINT_HR   = 1.50     # energy + maintenance + control tokens
INSURANCE_YR      = 3_000
YEOMAN_COGS_ROBOT = ROBOT_AMORT_YR + ENERGY_MAINT_HR * HOURS_YEOMAN + INSURANCE_YR
# = 21,429 + 9,198 + 3,000 = $33,627/yr per robot

# Corp per-robot annual costs (scale advantages)
CORP_ROBOT_COST   = 120_000  # 20% volume discount
CORP_AMORT_YR     = CORP_ROBOT_COST / ROBOT_LIFE_YR         # $17,143
CORP_ENERGY_HR    = 1.00     # bulk energy + tokens
CORP_OVERHEAD_HR  = 1.50     # management, software, admin allocation
CORP_COGS_ROBOT   = CORP_AMORT_YR + (CORP_ENERGY_HR + CORP_OVERHEAD_HR) * HOURS_CORP
# = 17,143 + 19,710 = $36,853/yr per robot
CORP_COGS_HR      = CORP_COGS_ROBOT / HOURS_CORP             # $/hr

print("=" * 72)
print("  YEOMAN BUSINESS MODEL")
print("  What fleet size + surtax achieves $75k net income?")
print("=" * 72)
print(f"""
  Target net income:          ${NET_TARGET:,}/yr (after expenses and income tax)
  Yeoman income tax rate:     {YEOMAN_TAX_RATE*100:.0f}%  (self-employment + income tax)
  Corp return requirement:    {CORP_RETURN_TARGET*100:.0f}%  (minimum to justify investment)

  Per-robot annual costs:
    Yeoman (70% util):  ${YEOMAN_COGS_ROBOT:,.0f}/yr  (${YEOMAN_COGS_ROBOT/HOURS_YEOMAN:.2f}/hr)
    Corp   (90% util):  ${CORP_COGS_ROBOT:,.0f}/yr  (${CORP_COGS_HR:.2f}/hr)
  
  Corp scale advantage: lower capital cost + higher utilisation + bulk energy
  
  Ignored: differential compute costs by task complexity.
""")

# ── Part 1: Revenue needed for $75k net ───────────────────────────────────
print("─" * 72)
print("  PART 1: Revenue needed to net $75k after expenses and tax")
print("─" * 72)

gross_profit_needed = NET_TARGET / (1 - YEOMAN_TAX_RATE)   # $96,154

print(f"""
  Net target:              ${NET_TARGET:,}
  Gross profit needed:     ${gross_profit_needed:,.0f}  (= net / (1 - {YEOMAN_TAX_RATE*100:.0f}%))
  
  Total revenue = gross profit needed + all COGS
""")

print(f"  {'Robots':>6}  {'Total COGS':>12}  {'Revenue needed':>15}  "
      f"{'Hours/yr':>10}  {'Price/hr needed':>16}")
print(f"  {'-'*6}  {'-'*12}  {'-'*15}  {'-'*10}  {'-'*16}")

fleet_data = {}
for n in [1, 2, 3, 5, 8, 10]:
    cogs = YEOMAN_COGS_ROBOT * n
    revenue = gross_profit_needed + cogs
    hours = HOURS_YEOMAN * n
    price_hr = revenue / hours
    fleet_data[n] = {'cogs': cogs, 'revenue': revenue, 'hours': hours, 'price_hr': price_hr}
    print(f"  {n:>6}  ${cogs:>10,.0f}  ${revenue:>13,.0f}  {hours:>10,.0f}  ${price_hr:>14.2f}")

# ── Part 2: What market price does the corp set? ──────────────────────────
print()
print("─" * 72)
print("  PART 2: Market price set by corporate competition")
print("─" * 72)

corp_floor_no_surtax = CORP_COGS_HR * (1 + CORP_RETURN_TARGET)

print(f"""
  Corp COGS/hr:       ${CORP_COGS_HR:.2f}
  Corp return req:    {CORP_RETURN_TARGET*100:.0f}%
  Market floor price: ${corp_floor_no_surtax:.2f}/hr  (no surtax)
  
  At ${corp_floor_no_surtax:.2f}/hr, which yeoman fleet is viable without surtax?
""")

for n, d in fleet_data.items():
    viable = "viable" if corp_floor_no_surtax >= d['price_hr'] else f"gap: ${d['price_hr'] - corp_floor_no_surtax:.2f}/hr short"
    print(f"    {n} robot{'s' if n>1 else ' '}: needs ${d['price_hr']:.2f}/hr  →  {viable}")

# ── Part 3: Surtax needed by fleet size ───────────────────────────────────
print()
print("─" * 72)
print("  PART 3: Corporate surtax needed to raise market floor to yeoman's required price")
print("─" * 72)
print(f"""
  With surtax T: corp minimum price = COGS × (1 + return) / (1 - T)
  Solve for T: T = 1 - corp_floor_no_surtax / target_price
""")
print(f"  {'Robots':>6}  {'Price needed':>13}  {'Surtax needed':>14}  "
      f"{'Corp price w/surtax':>20}  {'Efficiency cost':>16}")
print(f"  {'-'*6}  {'-'*13}  {'-'*14}  {'-'*20}  {'-'*16}")

for n, d in fleet_data.items():
    target = d['price_hr']
    if target <= corp_floor_no_surtax:
        surtax = 0.0
        corp_price = corp_floor_no_surtax
        eff_cost = "none needed"
    else:
        surtax = 1 - corp_floor_no_surtax / target
        corp_price = CORP_COGS_HR * (1 + CORP_RETURN_TARGET) / (1 - surtax)
        # Efficiency cost: price inflation reduces demand
        # Assume demand elasticity -0.5 (inelastic — physical services)
        price_increase_pct = (corp_price / corp_floor_no_surtax - 1) * 100
        demand_reduction = price_increase_pct * 0.5
        eff_cost = f"-{demand_reduction:.0f}% demand"
    print(f"  {n:>6}  ${target:>11.2f}  {surtax*100:>13.1f}%  ${corp_price:>18.2f}  {eff_cost:>16}")

# ── Part 4: The practical sweet spot ─────────────────────────────────────
print()
print("─" * 72)
print("  PART 4: The practical design")
print("─" * 72)

# Target: surtax of 20-30% (acceptable distortion)
# Find what net income that delivers at different fleet sizes
print(f"  Corp floor without surtax: ${corp_floor_no_surtax:.2f}/hr")
print()
print(f"  {'Surtax':>8}  {'Market price':>13}  {'1-robot net':>12}  "
      f"{'3-robot net':>12}  {'5-robot net':>12}  {'10-robot net':>13}")
print(f"  {'-'*8}  {'-'*13}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*13}")

for surtax in [0.0, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]:
    market_price = corp_floor_no_surtax / (1 - surtax)
    row = f"  {surtax*100:>7.0f}%  ${market_price:>11.2f}  "
    for n in [1, 3, 5, 10]:
        cogs = YEOMAN_COGS_ROBOT * n
        hours = HOURS_YEOMAN * n
        revenue = market_price * hours
        gross_profit = revenue - cogs
        net = gross_profit * (1 - YEOMAN_TAX_RATE)
        row += f"  ${net:>9,.0f}"
    print(row)

# ── Part 5: What fleet makes sense? ──────────────────────────────────────
print()
print("─" * 72)
print("  PART 5: What does a viable yeoman business look like?")
print("─" * 72)

SURTAX = 0.25
market_price = corp_floor_no_surtax / (1 - SURTAX)

print(f"""
  Assume: 25% corporate robot income surtax
  Market price rises from ${corp_floor_no_surtax:.2f}/hr → ${market_price:.2f}/hr

  Yeoman with subsidised financing (0% interest vs market 8%):
    Capital cost reduction: ~${ROBOT_COST * 0.08:,.0f}/yr per robot
    Effective COGS/robot/yr: ${YEOMAN_COGS_ROBOT - ROBOT_COST * 0.08:,.0f}  
      (vs unsubsidised ${YEOMAN_COGS_ROBOT:,.0f})
""")

SUBSIDY_SAVING = ROBOT_COST * 0.08   # interest saving from 0% vs 8% loan

for n in [1, 2, 3, 5]:
    cogs_subsidised = (YEOMAN_COGS_ROBOT - SUBSIDY_SAVING) * n
    hours = HOURS_YEOMAN * n
    revenue = market_price * hours
    gross_profit = revenue - cogs_subsidised
    net = gross_profit * (1 - YEOMAN_TAX_RATE)
    robot_equiv = ROBOT_COST * n
    print(f"  {n} robot fleet  (${robot_equiv:,} capital, subsidised financing):")
    print(f"    Revenue:      ${revenue:>10,.0f}/yr  (${market_price:.2f}/hr × {hours:,.0f} hr)")
    print(f"    COGS:         ${cogs_subsidised:>10,.0f}/yr")
    print(f"    Gross profit: ${gross_profit:>10,.0f}/yr")
    print(f"    Net income:   ${net:>10,.0f}/yr  {'✓ above $75k target' if net >= 75000 else f'✗ ${75000-net:,.0f} below target'}")
    print()

print("─" * 72)
print("  EFFICIENCY COST SUMMARY")
print("─" * 72)
price_increase = (market_price / corp_floor_no_surtax - 1) * 100
demand_reduction = price_increase * 0.5
print(f"""
  25% surtax raises market price by {price_increase:.0f}%
  With demand elasticity -0.5: roughly {demand_reduction:.0f}% less robot-hours purchased
  
  Trade-off: {demand_reduction:.0f}% lower volume of robot services consumed
             in exchange for viable yeoman class at 3-5 robot fleet scale
  
  Mitigant: surtax revenue funds robot financing programme
    → lowers yeoman COGS → lowers required market price → reduces required surtax
    → self-reinforcing: small initial surtax → more yeomen → more tax revenue
       → cheaper financing → more yeomen viable → equilibrium at lower surtax

  The 25% surtax is not permanent policy — it's the entry ramp.
  As yeomen build capital and utilisation improves, required surtax falls.
""")

