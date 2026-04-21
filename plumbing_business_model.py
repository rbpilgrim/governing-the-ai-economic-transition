"""
Yeoman plumbing business: concrete unit economics.

A robot plumber yeoman owns 1-3 humanoid robots, operates them via AI agent,
dispatches to residential/commercial jobs. Models job economics, annual P&L,
and market price scenarios as robot plumbing commoditises over time.
"""

print("=" * 72)
print("  YEOMAN PLUMBING BUSINESS")
print("  Concrete unit economics: jobs, pricing, P&L")
print("=" * 72)

# ── The job ────────────────────────────────────────────────────────────────
print("""
  A TYPICAL PLUMBING JOB MIX (residential/light commercial)
  ──────────────────────────────────────────────────────────
  Job type            Share   Labour hrs   Materials   Current price
  ─────────────────────────────────────────────────────────────────
  Service call/repair   40%      1.5 hr      $40         $280
  Fixture install       25%      2.0 hr      $150        $450
  Drain/blockage        15%      1.0 hr      $20         $200
  Leak investigation    10%      2.5 hr      $60         $380
  Minor remodel         10%      6.0 hr      $300        $950
  ─────────────────────────────────────────────────────────────────
  Weighted average:              2.0 hr      $93         $390/job
""")

AVG_LABOUR_HRS  = 2.0
AVG_MATERIALS   = 93
AVG_PRICE_NOW   = 390
AVG_TRAVEL_HRS  = 0.5    # travel + setup per job
HRS_PER_JOB     = AVG_LABOUR_HRS + AVG_TRAVEL_HRS   # 2.5 hrs total per job slot

# ── Robot capacity ─────────────────────────────────────────────────────────
WORK_HRS_DAY    = 10     # dispatched 10 hrs/day
WORK_DAYS_YR    = 300    # allowing for maintenance windows, slow periods
JOBS_PER_DAY    = WORK_HRS_DAY / HRS_PER_JOB   # 4 jobs/day
JOBS_PER_YR     = JOBS_PER_DAY * WORK_DAYS_YR  # 1,200 jobs/yr per robot

print(f"  ROBOT CAPACITY (per robot)")
print(f"  {'Work hours/day:':30} {WORK_HRS_DAY} hrs")
print(f"  {'Work days/year:':30} {WORK_DAYS_YR} days")
print(f"  {'Hours per job (incl travel):':30} {HRS_PER_JOB} hrs")
print(f"  {'Jobs per day:':30} {JOBS_PER_DAY:.1f}")
print(f"  {'Jobs per year:':30} {JOBS_PER_YR:,.0f}")

# ── Cost structure per robot ───────────────────────────────────────────────
ROBOT_COST      = 150_000
ROBOT_LIFE      = 7
VAN_COST        = 35_000     # robot needs transport
VAN_LIFE        = 5
VAN_RUNNING_YR  = 8_000      # fuel, insurance, maintenance
ROBOT_ENERGY_YR = 3_500      # charging
ROBOT_MAINT_YR  = 4_000      # servicing, parts
TOOLS_YR        = 2_000      # plumbing tools, consumables
LIABILITY_INS   = 5_000      # per robot — higher than generic, licensed work
LICENSING_YR    = 1_500      # plumbing licence, certifications
ORCHESTRATION   = 3_000      # AI agent software, dispatch platform, registry fees
ACCOUNTING_YR   = 2_000      # once across whole business

robot_fixed = (ROBOT_COST / ROBOT_LIFE) + (VAN_COST / VAN_LIFE)
robot_variable = ROBOT_ENERGY_YR + ROBOT_MAINT_YR + VAN_RUNNING_YR + TOOLS_YR + LIABILITY_INS + LICENSING_YR + ORCHESTRATION
total_per_robot = robot_fixed + robot_variable
cost_per_job = total_per_robot / JOBS_PER_YR

print(f"""
  ANNUAL COST PER ROBOT
  ─────────────────────────────────────────────────────────────────
  Robot amortisation  (${ROBOT_COST:,} / {ROBOT_LIFE}yr):   ${ROBOT_COST/ROBOT_LIFE:>10,.0f}
  Van amortisation    (${VAN_COST:,}  / {VAN_LIFE}yr):   ${VAN_COST/VAN_LIFE:>10,.0f}
  Van running costs:                              ${VAN_RUNNING_YR:>10,}
  Robot energy (charging):                        ${ROBOT_ENERGY_YR:>10,}
  Robot maintenance/servicing:                    ${ROBOT_MAINT_YR:>10,}
  Tools and consumables:                          ${TOOLS_YR:>10,}
  Liability insurance:                            ${LIABILITY_INS:>10,}
  Licensing and certifications:                   ${LICENSING_YR:>10,}
  AI orchestration / dispatch / registry:         ${ORCHESTRATION:>10,}
  ─────────────────────────────────────────────────────────────────
  Total fixed + variable per robot/yr:            ${total_per_robot:>10,}
  Plus: materials (pass-through at cost):         ${AVG_MATERIALS*JOBS_PER_YR:>10,}  (${AVG_MATERIALS}/job × {JOBS_PER_YR:.0f} jobs)
  
  Cost per job (excl materials):  ${cost_per_job:.2f}
  Cost per job (incl materials):  ${cost_per_job + AVG_MATERIALS:.2f}
""")

# Add accounting once
ACCOUNTING_ONE_OFF = ACCOUNTING_YR

# ── P&L at different price points — 1 robot ───────────────────────────────
print("─" * 72)
print("  P&L: 1-ROBOT BUSINESS at different market prices")
print("─" * 72)
print(f"  {JOBS_PER_YR:.0f} jobs/yr  |  materials passed through at cost  "
      f"|  22% income tax on profit")
print()
print(f"  {'Price/job':>10}  {'Revenue':>10}  {'COGS':>10}  "
      f"{'Gross profit':>13}  {'Net income':>11}  {'vs $75k':>10}")
print(f"  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*13}  {'-'*11}  {'-'*10}")

cogs_excl_materials = total_per_robot + ACCOUNTING_ONE_OFF
for price in [150, 200, 250, 300, 350, 390, 450, 500]:
    revenue = price * JOBS_PER_YR
    materials_total = AVG_MATERIALS * JOBS_PER_YR
    cogs_total = cogs_excl_materials + materials_total
    gross = revenue - cogs_total
    net = gross * (1 - 0.22) if gross > 0 else gross
    vs_target = f"+${net-75000:,.0f}" if net >= 75000 else f"-${75000-net:,.0f}"
    marker = " ← today" if price == AVG_PRICE_NOW else ""
    print(f"  ${price:>8}  ${revenue:>9,.0f}  ${cogs_total:>9,.0f}  "
          f"  ${gross:>10,.0f}  ${net:>10,.0f}  {vs_target:>10}{marker}")

breakeven_price = (cogs_excl_materials + AVG_MATERIALS * JOBS_PER_YR) / JOBS_PER_YR
target_price_1r = (cogs_excl_materials + AVG_MATERIALS * JOBS_PER_YR + 75000/0.78) / JOBS_PER_YR
print(f"""
  Breakeven price (1 robot):       ${breakeven_price:.0f}/job
  Price for $75k net (1 robot):    ${target_price_1r:.0f}/job
  Current market price:            ${AVG_PRICE_NOW}/job  ✓ well above both
""")

# ── P&L: 2 robots ─────────────────────────────────────────────────────────
print("─" * 72)
print("  P&L: 2-ROBOT BUSINESS — shared accounting, separate vans")
print("─" * 72)

n = 2
cogs_2r = (total_per_robot * n) + ACCOUNTING_ONE_OFF
jobs_2r = JOBS_PER_YR * n
print(f"  {jobs_2r:.0f} jobs/yr  |  shared accounting overhead")
print()
print(f"  {'Price/job':>10}  {'Revenue':>10}  {'COGS':>10}  "
      f"{'Gross profit':>13}  {'Net income':>11}  {'vs $75k':>10}")
print(f"  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*13}  {'-'*11}  {'-'*10}")

for price in [100, 150, 200, 250, 300, 350, 390]:
    revenue = price * jobs_2r
    materials_total = AVG_MATERIALS * jobs_2r
    cogs_total = cogs_2r + materials_total
    gross = revenue - cogs_total
    net = gross * (1 - 0.22) if gross > 0 else gross
    vs_target = f"+${net-75000:,.0f}" if net >= 75000 else f"-${75000-net:,.0f}"
    marker = " ← today" if price == AVG_PRICE_NOW else ""
    print(f"  ${price:>8}  ${revenue:>9,.0f}  ${cogs_total:>9,.0f}  "
          f"  ${gross:>10,.0f}  ${net:>10,.0f}  {vs_target:>10}{marker}")

target_price_2r = (cogs_2r + AVG_MATERIALS * jobs_2r + 75000/0.78) / jobs_2r
print(f"\n  Price for $75k net (2 robots): ${target_price_2r:.0f}/job")

# ── Price compression over time ────────────────────────────────────────────
print()
print("─" * 72)
print("  PRICE COMPRESSION OVER TIME (2-robot business)")
print("─" * 72)
print(f"""
  As robot plumbers proliferate, market price falls toward COGS + normal return.
  Robot cost deflating ~15%/yr. But plumbing has structural price floor:
    • Liability and insurance (licensed work — not just robot-hours)  
    • Materials are pass-through (don't deflate with robot cost)
    • Emergency/same-day premium (inelastic demand)
    • Non-standard jobs requiring judgement (long tail)
  
  Assumed price trajectory (2-robot business):
""")

print(f"  {'Year':>6}  {'Mkt price/job':>14}  {'Revenue':>10}  {'Net income':>11}  "
      f"{'Robot cost':>11}  {'Status':>12}")
print(f"  {'-'*6}  {'-'*14}  {'-'*10}  {'-'*11}  {'-'*11}  {'-'*12}")

price_trajectory = {
    2025: 390, 2027: 340, 2029: 280, 2031: 220,
    2033: 170, 2035: 140, 2037: 120, 2040: 100
}
robot_cost_trajectory = {yr: ROBOT_COST * (0.85 ** (yr - 2025)) for yr in price_trajectory}

for yr, price in price_trajectory.items():
    rc = robot_cost_trajectory[yr]
    # Recalculate with deflated robot cost
    robot_amort = rc / ROBOT_LIFE
    van_amort = VAN_COST / VAN_LIFE   # van cost stable
    cogs_robot_yr = robot_amort + van_amort + ROBOT_ENERGY_YR + ROBOT_MAINT_YR + VAN_RUNNING_YR + TOOLS_YR + LIABILITY_INS + LICENSING_YR + ORCHESTRATION
    cogs_n = cogs_robot_yr * 2 + ACCOUNTING_ONE_OFF
    jobs_n = jobs_2r
    materials = AVG_MATERIALS * jobs_n
    revenue = price * jobs_n
    gross = revenue - cogs_n - materials
    net = gross * 0.78 if gross > 0 else gross
    status = "✓ above target" if net >= 75000 else ("✓ viable" if net >= 50000 else "✗ below target")
    print(f"  {yr:>6}  ${price:>12}  ${revenue:>9,.0f}  ${net:>10,.0f}  ${rc:>10,.0f}  {status:>12}")

print(f"""
  Key observation: robot cost deflation broadly tracks price compression.
  As market price falls, so does your capital cost — the margin is stickier
  than it looks because both sides of the P&L deflate together.
  
  The floor is set by non-deflating costs: materials, van, insurance, licensing.
  These keep a plumbing job from ever becoming a pure token-cost commodity.
""")

# ── The surtax question revisited ─────────────────────────────────────────
print("─" * 72)
print("  THE SURTAX QUESTION: when does it become necessary?")
print("─" * 72)
print(f"""
  At current prices ($390/job): yeomen earn well above $75k. No surtax needed.
  
  Surtax only becomes necessary when prices compress to the point where
  a 2-robot business can't clear $75k net. From the table above: ~$170/job (2035).
  
  At that point, what surtax keeps a 2-robot yeoman at $75k?
""")

yr = 2035
price_2035 = 140
rc_2035 = robot_cost_trajectory[2035]
robot_amort = rc_2035 / ROBOT_LIFE
cogs_robot_yr = robot_amort + VAN_COST/VAN_LIFE + ROBOT_ENERGY_YR + ROBOT_MAINT_YR + VAN_RUNNING_YR + TOOLS_YR + LIABILITY_INS + LICENSING_YR + ORCHESTRATION
cogs_2r_2035 = cogs_robot_yr * 2 + ACCOUNTING_ONE_OFF
materials_2r = AVG_MATERIALS * jobs_2r

# Corp floor in 2035
corp_rc_2035 = rc_2035 * 0.80  # corp volume discount
corp_amort_2035 = corp_rc_2035 / ROBOT_LIFE
corp_cogs_hr_2035 = (corp_amort_2035 + VAN_COST/VAN_LIFE/(8760*0.90) + 
                     (ROBOT_ENERGY_YR + ROBOT_MAINT_YR + VAN_RUNNING_YR)/(8760*0.90) + 1.50)
corp_floor_2035 = corp_cogs_hr_2035 * (1 + 0.25) * HRS_PER_JOB

yeoman_price_needed = (cogs_2r_2035 + materials_2r + 75000/0.78) / jobs_2r
surtax_2035 = max(0, 1 - corp_floor_2035 / yeoman_price_needed)

print(f"  2035 scenario:")
print(f"    Market price without surtax: ${corp_floor_2035:.0f}/job")
print(f"    Yeoman needs (2 robots):     ${yeoman_price_needed:.0f}/job")
print(f"    Surtax required:             {surtax_2035*100:.0f}%")
print(f"    Corp floor with surtax:      ${corp_floor_2035/(1-surtax_2035):.0f}/job")
print()
print(f"""  A ~{surtax_2035*100:.0f}% surtax on corporate robot plumbing income in 2035 
  keeps a 2-robot yeoman business at the $75k target.
  
  This is modest — similar to existing self-employment tax differentials —
  and only kicks in after a decade of price compression, by which time
  robot financing is largely paid off and capital costs are much lower.
""")

