"""
Capital return model: can owning a robot or compute allocation generate subsistence income?

Core framing (user):
  - All task prices → opportunity cost of the underlying resource (robot-hours or tokens)
  - Physical tasks price toward robot opportunity cost, NOT displaced human labor rate
  - Knowledge tasks price toward token cost
  - Ignored: differential compute costs by task complexity (acknowledged, set aside)
  - Question: does owning the capital generate a return above its own cost?

In competitive equilibrium:
  market_rental_rate = capital_amortization + operating_cost
  → yeoman income = 0 (they cover costs, earn nothing above)

Margin only exists from:
  1. Capital scarcity rent (limited supply → price above amortization)
  2. Utilisation advantage (yeoman utilises better than market average)
  3. Policy floor (minimum service price, like minimum wage for capital)
  4. Geographic thin-market premium (only robot available locally)
"""

# ── Ignored (acknowledged) ────────────────────────────────────────────────
# Differential compute costs: a complex task requires more tokens than a simple one.
# This creates a cost-of-goods hierarchy but not a margin — buyers pay proportionally
# more WTP for more complex tasks. The margin (price - COGS) as a fraction of price
# is roughly constant across complexity levels in a competitive market.
# We ignore this and treat compute as a uniform per-unit cost.

SUBSISTENCE_ANNUAL = 55_000   # USD gross, US target

print("=" * 72)
print("  CAPITAL RETURN MODEL")
print("  Can owning a robot/compute earn subsistence in competitive equilibrium?")
print("=" * 72)

print("""
  Ignored (acknowledged): differential compute costs by task complexity.
  In competitive markets, price scales with cost — margin fraction is flat.
  We treat compute as a uniform per-unit cost throughout.
""")

# ── Robot capital ─────────────────────────────────────────────────────────
print("─" * 72)
print("  PART 1: Robot capital return in competitive equilibrium")
print("─" * 72)

print("""
  In competitive equilibrium:
    rental_rate_per_hr = amortization_per_hr + operating_cost_per_hr
    yeoman_annual_income = (rental_rate - operating_cost) × hours - amortization
                        = 0   ← by definition of equilibrium

  So the question is not "does the robot earn income?" but:
    "Is the competitive RETURN ON CAPITAL above the yeoman's cost of capital?"
    
  If yes: the robot is a good investment (like a bond or ETF).
  If no:  the robot is a liability and yeomen exit.
  But in either case: the yeoman earns the RETURN ON CAPITAL, not a labor wage.
""")

# Robot economics
robot_prices = [50_000, 100_000, 150_000, 300_000]
robot_life_yr = 7
utilisation   = 0.70   # fraction of 8760 hrs/yr
operating_cost_hr = 1.50   # energy + maintenance + tokens for control

hours_active = 8760 * utilisation

print(f"  Robot life: {robot_life_yr}yr  |  Utilisation: {utilisation*100:.0f}%  "
      f"|  Operating cost: ${operating_cost_hr:.2f}/hr  |  Hours active: {hours_active:,.0f}/yr")
print()
print(f"  {'Robot cost':>12}  {'Amort/hr':>10}  {'Op cost/hr':>11}  {'Break-even rate':>16}  "
      f"{'Annual revenue':>15}  {'Net income':>12}  {'ROC':>8}")
print(f"  {'-'*12}  {'-'*10}  {'-'*11}  {'-'*16}  {'-'*15}  {'-'*12}  {'-'*8}")

for robot_cost in robot_prices:
    amort_per_hr = (robot_cost / robot_life_yr) / hours_active
    breakeven_rate = amort_per_hr + operating_cost_hr
    annual_revenue = breakeven_rate * hours_active
    net_income = annual_revenue - operating_cost_hr * hours_active - robot_cost / robot_life_yr
    roc = net_income / robot_cost * 100  # should be ~0 at breakeven
    print(f"  ${robot_cost:>10,}  ${amort_per_hr:>8.2f}  ${operating_cost_hr:>9.2f}  "
          f"  ${breakeven_rate:>13.2f}  ${annual_revenue:>13,.0f}  ${net_income:>10,.0f}  {roc:>7.1f}%")

print("""
  At breakeven rental rate: net income = $0. The robot covers its own costs exactly.
  Yeoman earns 0% return on capital. This is competitive equilibrium.
  
  Above-equilibrium return requires scarcity (price > breakeven).
  That scarcity comes from: limited robot supply, geographic isolation, or policy floor.
""")

# ── Scarcity rent ─────────────────────────────────────────────────────────
print("─" * 72)
print("  PART 2: Scarcity premium — what rental rate above breakeven funds subsistence?")
print("─" * 72)

robot_cost = 150_000
amort_per_hr = (robot_cost / robot_life_yr) / hours_active
breakeven_rate = amort_per_hr + operating_cost_hr

gross_needed = SUBSISTENCE_ANNUAL
per_hr_surplus_needed = gross_needed / hours_active
required_rate = breakeven_rate + per_hr_surplus_needed
scarcity_premium = per_hr_surplus_needed
premium_pct = scarcity_premium / breakeven_rate * 100

print(f"""
  Robot cost: $150k  |  Breakeven rate: ${breakeven_rate:.2f}/hr  |  Hours active: {hours_active:,.0f}/yr

  To earn ${SUBSISTENCE_ANNUAL:,}/yr above cost:
    Required surplus per hour:  ${per_hr_surplus_needed:.2f}/hr
    Required rental rate:       ${required_rate:.2f}/hr  ({premium_pct:.0f}% above breakeven)
    
  The market must price robot-hours at {premium_pct:.0f}% above marginal cost
  for yeoman ownership to generate subsistence income.
  
  When is this plausible?
    • Robot supply constrained (early deployment, slow manufacturing scale-up)
    • Geographic monopoly (1 robot per 50 sq miles in rural area)
    • Regulatory licensing (only certified robots can do medical/food tasks)
    • Policy price floor (analogous to minimum wage — but for robot services)
""")

# ── The compute equivalent ─────────────────────────────────────────────────
print("─" * 72)
print("  PART 3: Compute — same logic, much faster commoditisation")
print("─" * 72)

# Compute: token costs falling ~30-40%/yr (Moore's law for inference)
# Robot: price falling ~15%/yr, capability rising
TOKEN_COST_NOW       = 0.35   # $/1000-token task
TOKEN_COST_DEFLATION = 0.35   # 35%/yr price decline
ROBOT_PRICE_DEFLATION= 0.15   # 15%/yr

print(f"""
  Token cost deflation: ~{TOKEN_COST_DEFLATION*100:.0f}%/yr (inference efficiency + competition)
  Robot price deflation: ~{ROBOT_PRICE_DEFLATION*100:.0f}%/yr
  
  Breakeven rental rate tracks capital cost. As capital price falls, breakeven falls.
  The scarcity premium (in $) that funds subsistence stays constant in real terms.
  But as a % of task price it RISES — making it harder for buyers to justify.
""")

print(f"  {'Year':>6}  {'Token cost':>11}  {'Robot breakeven':>16}  "
      f"{'Subsist premium %':>18}  {'Is premium sustainable?':>25}")
print(f"  {'-'*6}  {'-'*11}  {'-'*16}  {'-'*18}  {'-'*25}")

for yr in [0, 3, 5, 7, 10]:
    tc = TOKEN_COST_NOW * (1 - TOKEN_COST_DEFLATION) ** yr
    rc = robot_cost * (1 - ROBOT_PRICE_DEFLATION) ** yr
    robot_be = (rc / robot_life_yr) / hours_active + operating_cost_hr
    sub_prem_pct_robot = (per_hr_surplus_needed / robot_be) * 100
    sub_prem_pct_token = (SUBSISTENCE_ANNUAL / (tc * 800 * 12) - 1) * 100   # 800 tasks/mo
    sustainable = "possible" if sub_prem_pct_robot < 30 else ("hard" if sub_prem_pct_robot < 80 else "implausible")
    print(f"  {yr:>6}  ${tc:>9.3f}  ${robot_be:>14.2f}  "
          f"{sub_prem_pct_robot:>17.0f}%  {sustainable:>25}")

print("""
  As capital costs fall, the scarcity premium required as a % of price grows.
  Eventually the premium required exceeds any plausible market scarcity rent.
  At that point: owning capital earns 0% above cost in competitive markets.
  The yeoman earns nothing above their cost of capital.
""")

# ── The equilibrium conclusion ─────────────────────────────────────────────
print("=" * 72)
print("  EQUILIBRIUM CONCLUSION")
print("=" * 72)
print(f"""
  In a fully competitive market where robots do all physical tasks and
  agents do all knowledge tasks:

    ALL task prices → opportunity cost of capital (robot-hours or tokens)
    Yeoman income   → return on capital, not a labor wage
    Return on capital → risk-free rate + risk premium (not subsistence income)

  The risk-free rate (US Treasuries, ~4-5%) on $150k robot = $6-7.5k/yr.
  Subsistence target: $55k/yr.
  Gap: ~$47k/yr.

  This gap is structural. It cannot be closed by:
    ✗ Tax credits on buyer contracts (WTP = opportunity cost, credit just shifts who pays)
    ✗ Subsidised compute (lowers floor and WTP equally — gap unchanged)
    ✗ More tasks (all at opportunity cost price — more volume, same 0 margin)

  It CAN be closed by:
    ✓ Policy price floor above opportunity cost (robot minimum wage equivalent)
        → buyer's WTP must exceed floor or task goes undone
        → only works if floor < buyer's actual value (otherwise buyers self-provision)
    ✓ Capital concentration limit + distribution
        → if each yeoman owns more capital (bigger robot fleet, more compute),
           the 4-5% return on $1M of capital = $40-50k/yr → near subsistence
           → this is the "more capital per yeoman" solution, not "higher margin per task"
    ✓ Direct transfer funded by AI productivity gains (UBI / dividend)
        → decouple subsistence from capital returns entirely
        → fund from levy on AI-generated revenue (4% on $3T = $120B/yr)

  The cleanest frame:
    Owning $1M of productive AI capital at 5% return = $50k/yr subsistence.
    The policy question is: HOW does a yeoman accumulate $1M of capital?
    Answer: government-subsidised robot financing + mandatory reinvestment
    of earnings into additional capital until the portfolio self-sustains.
""")

