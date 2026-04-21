"""
Yeoman margin model: what does a yeoman need to earn above token cost
to achieve subsistence, and what policy interventions close the gap?

Core question: as AI-driven buyers compress prices toward token cost,
can yeomen earn a living? What does the margin arithmetic look like?
"""

import numpy as np

# ── Subsistence parameters ─────────────────────────────────────────────────
SUBSISTENCE_ANNUAL   = 55_000   # USD/yr gross (US median household ~$75k; yeoman target lower)
SUBSISTENCE_MONTHLY  = SUBSISTENCE_ANNUAL / 12   # $4,583
INCOME_TAX_RATE      = 0.25     # effective rate after deductions
NET_TARGET_MONTHLY   = SUBSISTENCE_MONTHLY * (1 - INCOME_TAX_RATE)  # $3,438

# ── Task economics ─────────────────────────────────────────────────────────
# Token cost for a "standard knowledge task" (research report, code review, data analysis)
# Claude Sonnet class: ~$3/M input + $15/M output. Complex task: 50k in + 5k out ≈ $0.23
# GPT-4o: $5/$15/M → similar. Call it a range.
TOKEN_COST_PER_TASK   = 0.25    # USD — inference only
INFRA_COST_PER_TASK   = 0.10    # hosting, orchestration, storage
COGS_PER_TASK         = TOKEN_COST_PER_TASK + INFRA_COST_PER_TASK   # $0.35

# How many tasks can one agent handle per month?
# Assume async, ~4 min avg wall-clock per task → ~10,800 tasks/month theoretical
# But quality tasks need human-readable output review loop: practical ~500-2000/mo
TASKS_PER_MONTH_LOW   = 200
TASKS_PER_MONTH_MID   = 800
TASKS_PER_MONTH_HIGH  = 3_000

# ── What buyers will pay ────────────────────────────────────────────────────
# Buyer's AI benchmarks tasks. They know token cost. They pay:
#   token_cost * (1 + coordination_premium) + reputation_premium
# As buyer AI gets better, coordination_premium → 0
COORD_PREMIUM_NOW    = 2.0    # buyer pays 3x token cost today (search, trust, coordination)
COORD_PREMIUM_5YR    = 0.5    # buyer pays 1.5x token cost in 5 years
COORD_PREMIUM_10YR   = 0.1    # buyer pays 1.1x in 10 years — approaching token cost

def buyer_wtp(cogs, coord_premium, reputation_premium=0.0):
    """What a fully-automated buyer will pay per task."""
    return cogs * (1 + coord_premium) + reputation_premium

def yeoman_floor_price(fixed_overhead_monthly, tasks_per_month, cogs_per_task, tax_rate=0.25):
    """Minimum price to cover subsistence + overhead + COGS."""
    gross_needed = SUBSISTENCE_MONTHLY / (1 - tax_rate)
    per_task_overhead = (gross_needed + fixed_overhead_monthly) / tasks_per_month
    return cogs_per_task + per_task_overhead

# ── Scenarios ─────────────────────────────────────────────────────────────
FIXED_OVERHEAD = 500   # monthly: software subscriptions, connectivity, accounting

print("=" * 72)
print("  YEOMAN MARGIN MODEL: TOKEN COST COMPRESSION")
print("=" * 72)

print("""
  The structural problem:
    Buyer's AI knows token cost. As buyer AI handles coordination and QC,
    willingness-to-pay → token cost. But yeoman needs margin above token
    cost to fund subsistence. That margin must come from somewhere.
""")

# ── Table 1: floor price vs task volume ───────────────────────────────────
print("─" * 72)
print("  TABLE 1: Yeoman floor price vs task volume (25% income tax, $500/mo overhead)")
print("─" * 72)
print(f"  {'Tasks/mo':>10}  {'COGS/task':>10}  {'Overhead/task':>14}  {'Floor price':>12}  {'Markup over COGS':>18}")
print(f"  {'-'*10}  {'-'*10}  {'-'*14}  {'-'*12}  {'-'*18}")

for tasks in [100, 200, 500, 1_000, 2_000, 5_000]:
    floor = yeoman_floor_price(FIXED_OVERHEAD, tasks, COGS_PER_TASK)
    markup_pct = (floor - COGS_PER_TASK) / COGS_PER_TASK * 100
    print(f"  {tasks:>10,}  ${COGS_PER_TASK:>8.2f}  ${FIXED_OVERHEAD/tasks:>12.2f}  ${floor:>11.2f}  {markup_pct:>16.0f}%")

# ── Table 2: buyer WTP vs time ─────────────────────────────────────────────
print()
print("─" * 72)
print("  TABLE 2: Buyer WTP compression over time (token cost = $0.35/task)")
print("─" * 72)
print(f"  {'Scenario':>15}  {'Coord premium':>14}  {'Buyer WTP':>10}  {'Viable at N tasks/mo':>22}")

for label, premium in [("Today", COORD_PREMIUM_NOW), ("5 years", COORD_PREMIUM_5YR), ("10 years", COORD_PREMIUM_10YR)]:
    wtp = buyer_wtp(COGS_PER_TASK, premium)
    margin_per_task = wtp - COGS_PER_TASK
    if margin_per_task > 0:
        # tasks needed: (gross_needed + overhead) / margin_per_task
        gross_needed = SUBSISTENCE_MONTHLY / (1 - INCOME_TAX_RATE)
        tasks_needed = (gross_needed + FIXED_OVERHEAD) / margin_per_task
        viable = f"{tasks_needed:,.0f} tasks/mo"
    else:
        viable = "not viable"
    print(f"  {label:>15}  {premium:>13.1f}x  ${wtp:>8.2f}  {viable:>22}")

# ── Table 3: the gap ───────────────────────────────────────────────────────
print()
print("─" * 72)
print("  TABLE 3: The gap — floor price vs buyer WTP at 800 tasks/mo")
print("─" * 72)

tasks = 800
floor = yeoman_floor_price(FIXED_OVERHEAD, tasks, COGS_PER_TASK)
print(f"  Yeoman floor price (800 tasks/mo):  ${floor:.2f}/task")
print()
for label, premium in [("Today", COORD_PREMIUM_NOW), ("5 years", COORD_PREMIUM_5YR), ("10 years", COORD_PREMIUM_10YR)]:
    wtp = buyer_wtp(COGS_PER_TASK, premium)
    gap = wtp - floor
    viable = "VIABLE" if gap >= 0 else "GAP — requires subsidy"
    monthly_surplus = gap * tasks
    print(f"  {label}: WTP=${wtp:.2f}  floor=${floor:.2f}  gap=${gap:+.2f}/task  "
          f"monthly surplus=${monthly_surplus:+,.0f}  → {viable}")

# ── What closes the gap? ───────────────────────────────────────────────────
print()
print("─" * 72)
print("  TABLE 4: Policy levers to close the 10-year gap")
print("─" * 72)

# At 10yr, WTP = $0.385, floor = ~$6.39 at 800 tasks. Gap = -$6.00/task.
wtp_10yr = buyer_wtp(COGS_PER_TASK, COORD_PREMIUM_10YR)
floor_800 = yeoman_floor_price(FIXED_OVERHEAD, 800, COGS_PER_TASK)
gap_per_task = wtp_10yr - floor_800
monthly_gap = gap_per_task * 800

print(f"""
  Baseline gap (10yr, 800 tasks/mo): ${gap_per_task:.2f}/task = ${monthly_gap:,.0f}/mo to close

  Lever A — Subsidised compute (government buys tokens at cost, resells to yeomen):
    Eliminates COGS_per_task from floor. New floor = overhead/tasks only.
    Floor drops from ${floor_800:.2f} → ${FIXED_OVERHEAD/800 + SUBSISTENCE_MONTHLY/(1-INCOME_TAX_RATE)/800:.2f}/task
    Still above WTP (${wtp_10yr:.2f}). Compute subsidy alone is not enough.

  Lever B — UBI/basic income supplement (separate from yeoman earnings):
    Reduces subsistence the yeoman must earn from contracts.
    If UBI covers $2,000/mo, gross needed from contracts = ${(SUBSISTENCE_MONTHLY - 2000)/(1-INCOME_TAX_RATE):.0f}/mo
    New floor = ${yeoman_floor_price(FIXED_OVERHEAD, 800, COGS_PER_TASK, 0.25) - 2000/(800*(1-0.25)):.2f}/task
    Viable if WTP ≥ floor.

  Lever C — Fewer, higher-value tasks (specialisation):
    Instead of 800 commodity tasks at $0.38, do 20 premium tasks at ?
    Gross needed: ${SUBSISTENCE_MONTHLY/(1-INCOME_TAX_RATE) + FIXED_OVERHEAD:,.0f}/mo
    Required price per task (20/mo): ${(SUBSISTENCE_MONTHLY/(1-INCOME_TAX_RATE) + FIXED_OVERHEAD + COGS_PER_TASK*20)/20:,.0f}/task
    Premium tasks: certified medical coding, legal drafts, engineering sign-off — 
    where yeoman provides licensed accountability, not just inference.

  Lever D — Physical world tasks (robots):
    Buyer cannot replicate with tokens alone. They need the robot.
    Price floor includes capital amortization, not just compute.
    At $150k robot / 5yr / 80% utilisation → $3.57/hr capital cost
    4hr physical task (cleaning, delivery, inspection) → $14 capital + $0.35 compute = $14.35 floor
    Buyer WTP = labor market rate they're replacing ($20-$80/hr) = $80-320/task
    Margin: $65-$305/task — STRONGLY VIABLE even at 10yr compression
""")

# ── Physical vs knowledge task comparison ─────────────────────────────────
print("─" * 72)
print("  TABLE 5: Physical vs knowledge tasks — margin comparison")
print("─" * 72)

ROBOT_COST        = 150_000
ROBOT_LIFE_YR     = 5
ROBOT_UTIL        = 0.80
HOURS_PER_YR      = 8760 * ROBOT_UTIL
CAPITAL_COST_HR   = ROBOT_COST / (ROBOT_LIFE_YR * HOURS_PER_YR)

print(f"  Robot: ${ROBOT_COST:,} / {ROBOT_LIFE_YR}yr / {ROBOT_UTIL*100:.0f}% utilisation → "
      f"${CAPITAL_COST_HR:.2f}/hr capital cost")
print()
print(f"  {'Task type':>25}  {'Hours':>6}  {'Capital':>8}  {'Compute':>8}  "
      f"{'Floor':>8}  {'Buyer WTP':>10}  {'Margin/task':>12}")
print(f"  {'-'*25}  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*12}")

physical_tasks = [
    ("Office cleaning",          4,   15.00,  7,   "$40-60/hr"),
    ("Package delivery",         0.5,  3.00,  12,  "$20-25/hr"),
    ("Building inspection",      2,    5.00,  45,  "$60-80/hr"),
    ("Elder care assist",        6,   10.00,  25,  "$30-40/hr"),
    ("Construction assist",      8,   15.00,  60,  "$40-60/hr"),
]

for name, hours, compute_cost, wtp_low, wtp_range in physical_tasks:
    capital = CAPITAL_COST_HR * hours
    # Overhead allocation: $500/mo / 200 physical tasks
    overhead = 500 / 200
    floor = capital + compute_cost + overhead
    margin = wtp_low - floor
    print(f"  {name:>25}  {hours:>6.1f}  ${capital:>6.2f}  ${compute_cost:>6.2f}  "
          f"  ${floor:>6.2f}  {wtp_range:>10}  ${margin:>+10.2f}")

print()
knowledge_tasks = [
    ("Commodity research",       0,   0.35,   0.39, "→$0.39 WTP (10yr)"),
    ("Data analysis report",     0,   2.50,   5.00, "→$5/task WTP"),
    ("Code review",              0,   1.00,   2.00, "→$2/task WTP"),
    ("Licensed medical code",    0,   0.35,  15.00, "→$15 (liability moat)"),
    ("Legal brief (licensed)",   0,   1.50,  50.00, "→$50 (bar license)"),
]

for name, hours, compute_cost, wtp_low, note in knowledge_tasks:
    floor_k = COGS_PER_TASK + FIXED_OVERHEAD/800
    margin = wtp_low - floor_k
    print(f"  {name:>25}  {'AI':>6}  {'  —':>7}  ${compute_cost:>6.2f}  "
          f"  ${floor_k:>6.2f}  {note:<20}  ${margin:>+8.2f}")

# ── Conclusion ─────────────────────────────────────────────────────────────
print()
print("=" * 72)
print("  STRUCTURAL CONCLUSION")
print("=" * 72)
print("""
  Knowledge tasks: margin collapses toward zero as buyer AI improves.
  Viable only if the yeoman holds a non-replicable moat:
    • Regulated accountability (licensed professional signs off)
    • Proprietary data/fine-tuning the buyer cannot access
    • Verified trust/reputation that reduces buyer's risk premium
  Without a moat, commodity knowledge tasks → token cost + ε.

  Physical tasks: margin is structurally protected.
    The buyer's WTP is the labor market rate they're replacing.
    The yeoman's cost floor is capital amortization + compute — 
    NOT just compute. Capital creates the moat. Market cannot compress
    physical task price below asset return requirement.

  Policy implication:
    1. Robot financing program is the correct lever — it creates the
       physical-world margin that knowledge work cannot sustain alone.
    2. Knowledge-only yeomen will need UBI supplement or licensed moats.
    3. Subsidised compute helps at the margin but doesn't close the gap
       if all buyer coordination is also AI (the gap isn't in compute cost).
    4. The yeoman programme must be designed around PHYSICAL CAPITAL DEPLOYMENT
       not just "run your own agents" — because agents alone commoditise instantly.
""")



# ═══════════════════════════════════════════════════════════════════════════
# TAX CREDIT MECHANISM
# ═══════════════════════════════════════════════════════════════════════════
# Buyer gets a tax credit for contracting with registered yeomen.
# Buyer is indifferent between:
#   (a) running their own agents at token cost C
#   (b) paying yeoman price P and receiving credit T_rate * P
# Indifference: P * (1 - T_rate) = C  →  P = C / (1 - T_rate)
# The yeoman needs P ≥ floor. So: floor ≤ C / (1 - T_rate)
# Solving for T_rate: T_rate ≥ 1 - C / floor

print()
print("=" * 72)
print("  TAX CREDIT MECHANISM: what rate makes yeomen viable?")
print("=" * 72)
print("""
  Mechanism:
    Government offers buyers a tax credit = T_rate × contract_value
    Buyer is indifferent when: P × (1-T_rate) = token_cost
    → Yeoman can charge P = token_cost / (1-T_rate) and buyer still chooses them
    → Required credit rate: T_rate = 1 - token_cost / floor_price
    
  Government cost = T_rate × P × contracts_per_yeoman × n_yeomen
  Compare to: unemployment benefit = $25k/yr per displaced worker
""")

print("─" * 72)
print("  Required credit rate by task type and volume")
print("─" * 72)
print(f"  {'Task type':>28}  {'Floor/task':>10}  {'WTP (mkt)':>10}  {'Credit rate':>12}  {'Viable?':>8}")
print(f"  {'-'*28}  {'-'*10}  {'-'*10}  {'-'*12}  {'-'*8}")

scenarios = [
    # (name, floor_price, market_wtp_10yr)
    ("Knowledge: commodity (800/mo)", floor_800,       0.39),
    ("Knowledge: data analysis (200/mo)", yeoman_floor_price(FIXED_OVERHEAD, 200, COGS_PER_TASK), 5.00),
    ("Knowledge: licensed medical (50/mo)", yeoman_floor_price(FIXED_OVERHEAD, 50, COGS_PER_TASK), 15.00),
    ("Knowledge: legal brief (20/mo)",     yeoman_floor_price(FIXED_OVERHEAD, 20, COGS_PER_TASK), 50.00),
    ("Physical: package delivery",        7.64,         10.00),
    ("Physical: building inspection",     16.06,        60.00),
]

for name, floor, wtp_nat in scenarios:
    # credit rate needed so buyer pays floor but effective cost = token-equivalent WTP
    # buyer effective cost target: wtp_nat (what they'd pay without credit)
    credit_rate = max(0, 1 - wtp_nat / floor)
    if credit_rate >= 1.0:
        viable = "not viable"
        credit_str = ">100%"
    elif credit_rate > 0.5:
        viable = "high subsidy"
        credit_str = f"{credit_rate*100:.0f}%"
    elif credit_rate > 0.2:
        viable = "moderate"
        credit_str = f"{credit_rate*100:.0f}%"
    elif credit_rate > 0:
        viable = "low"
        credit_str = f"{credit_rate*100:.0f}%"
    else:
        viable = "no credit needed"
        credit_str = "0%"
    print(f"  {name:>28}  ${floor:>8.2f}  ${wtp_nat:>8.2f}  {credit_str:>12}  {viable:>8}")

# ── Fiscal cost at scale ───────────────────────────────────────────────────
print()
print("─" * 72)
print("  Fiscal cost of credit at national scale (US, 10 years out)")
print("─" * 72)

N_YEOMEN = 10_000_000   # 10M displaced workers enrolled in yeoman programme
# Realistic mix: most physical (viable without credit), minority knowledge with moat

scenarios_fiscal = [
    ("Commodity knowledge (no moat)", 0.30, 0.39, 800, 0.0, 0.5),   # 50% of cohort, no credit → UBI
    ("Licensed knowledge (moat)",     0.30, 15.0, 50,  0.0, 0.1),   # 10% — lawyers, doctors
    ("Physical (robot tasks)",        7.64, 15.0, 200, 0.0, 0.4),   # 40% — physical
]

print(f"""
  Assumptions: {N_YEOMEN/1e6:.0f}M yeomen, mix of task types
  Credit is on contract value paid to registered yeoman
  Alternative cost: $25,000/yr unemployment benefit per displaced worker
  Alternative cost total: ${N_YEOMEN * 25_000 / 1e9:.0f}B/yr
""")
print(f"  {'Segment':>30}  {'Share':>6}  {'Yeomen':>10}  {'Credit rate':>12}  {'Annual cost':>12}")
print(f"  {'-'*30}  {'-'*6}  {'-'*10}  {'-'*12}  {'-'*12}")

total_credit_cost = 0
for name, floor, price, tasks_mo, credit_rate_override, share in scenarios_fiscal:
    n = N_YEOMEN * share
    credit_rate = max(0, 1 - price / floor) if credit_rate_override == 0 else credit_rate_override
    annual_contract_value = price * tasks_mo * 12 * n
    annual_credit_cost = credit_rate * annual_contract_value
    total_credit_cost += annual_credit_cost
    print(f"  {name:>30}  {share*100:.0f}%  {n/1e6:.1f}M      "
          f"{credit_rate*100:.0f}%          ${annual_credit_cost/1e9:.0f}B/yr")

print(f"""
  Total credit cost:    ${total_credit_cost/1e9:.0f}B/yr
  Alt (unemployment):   ${N_YEOMEN * 25_000 / 1e9:.0f}B/yr
  
  Note: commodity knowledge yeomen (50% of cohort) receive $0 credit above —
  they're NOT viable through credit alone. They need either:
    a) UBI supplement (~$2k/mo → adds ${N_YEOMEN * 0.5 * 24_000 / 1e9:.0f}B/yr)
    b) Physical capital (robot) to move into viable task categories
    c) Licensed moat (professional credential + AI)

  The physical robot programme is cheaper at scale than either UBI or
  unlimited compute credits, because it creates real productive capital
  that generates positive-margin tasks.
""")

# ── What tax rate on AI-generated revenue funds this? ──────────────────────
print("─" * 72)
print("  What AI revenue tax funds the credit programme?")
print("─" * 72)

# US GDP ~ $28T. AI-generated value added growing fast.
# By 10yr, plausible AI share of productivity = 20-30% of GDP = $5.6-8.4T
# Corresponding AI revenue (corporate, not GDP): ~$2-4T

AI_REVENUE_10YR = 3_000   # $3T — AI-generated corporate revenue at 10yr
PROGRAMME_COST  = total_credit_cost / 1e9 + N_YEOMEN * 0.5 * 24_000 / 1e9  # credits + UBI for unviable segment

tax_rate_needed = PROGRAMME_COST / AI_REVENUE_10YR
print(f"""
  Estimated AI-generated corporate revenue (10yr):  ${AI_REVENUE_10YR:,}B/yr
  Yeoman credit programme cost:                     ${total_credit_cost/1e9:.0f}B/yr
  UBI for unviable knowledge segment:               ${N_YEOMEN * 0.5 * 24_000 / 1e9:.0f}B/yr
  Total programme cost:                             ${PROGRAMME_COST:.0f}B/yr
  
  Implied AI revenue tax rate to fund programme:    {tax_rate_needed*100:.1f}%
  
  For comparison:
    US corporate tax rate:  21%
    Biden proposed minimum: 15%
    OECD global minimum:    15%
    
  A {tax_rate_needed*100:.0f}-{tax_rate_needed*100*1.5:.0f}% levy on AI-generated revenue (not all corporate revenue)
  funds the entire yeoman programme. This is fiscally feasible if
  AI revenue grows as projected and the levy is internationally coordinated
  (OECD Pillar Two extension to AI-derived income).
""")

