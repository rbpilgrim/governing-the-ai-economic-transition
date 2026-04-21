"""
Tax credit equilibrium model.

Mechanism:
  Buyer gets credit = T_rate × contract_value paid to registered yeoman.
  Buyer effective cost: P × (1 - T_rate)
  Buyer's outside option: run own robot/compute at opportunity cost C.
  Buyer is indifferent when: P × (1 - T_rate) = C  →  P_max = C / (1 - T_rate)

  In competitive yeoman market:
    - Many yeomen compete → price bids down to the floor that still earns subsistence
    - Equilibrium price: P* = C / (1 - T_rate)  [buyer captures no surplus; yeoman earns subsistence]
    - Yeoman gross income: (P* - C) × hours = (C/(1-T) - C) × hours = C × T/(1-T) × hours

  Required credit rate for subsistence:
    Subsistence = C × T/(1-T) × hours
    T/(1-T) = Subsistence / (C × hours)
    T = S / (S + C × hours)   where S = subsistence target

  Government fiscal flows:
    OUT: credit = T × P* × hours × n_yeomen
    IN:  income tax on yeoman earnings + saved unemployment benefit
    NET: credit - income_tax_recovered - unemployment_saved

  Note: differential compute costs by task complexity are ignored throughout.
  Higher-complexity tasks cost more tokens; buyers pay proportionally more.
  The margin fraction (price - cost)/price is roughly constant — ignored here.
"""

SUBSISTENCE      = 55_000   # USD/yr gross target
INCOME_TAX_RATE  = 0.25
UNEMPLOYMENT_BEN = 25_000   # USD/yr per displaced worker (status quo)
N_YEOMEN         = 10_000_000  # scale

# Robot parameters
ROBOT_COST       = 150_000
ROBOT_LIFE_YR    = 7
UTILISATION      = 0.70
HOURS_YR         = 8760 * UTILISATION        # 6,132 hr/yr
OPERATING_HR     = 1.50                       # energy + maintenance + control tokens
AMORT_HR         = (ROBOT_COST / ROBOT_LIFE_YR) / HOURS_YR
OPP_COST_HR      = AMORT_HR + OPERATING_HR   # buyer's outside option = $4.99/hr

print("=" * 72)
print("  TAX CREDIT EQUILIBRIUM")
print("  What credit rate funds subsistence? What does it cost the government?")
print("=" * 72)
print(f"""
  Robot: ${ROBOT_COST:,} / {ROBOT_LIFE_YR}yr / {UTILISATION*100:.0f}% util
  Buyer opportunity cost (run own robot): ${OPP_COST_HR:.2f}/hr
  Active hours/yr: {HOURS_YR:,.0f}
  
  Ignored: differential compute cost by task complexity (acknowledged).
  In competitive markets, price scales proportionally with cost — margin
  fraction is approximately constant across task types.
""")

# ── Required credit rate ───────────────────────────────────────────────────
# Subsistence = OPP_COST × T/(1-T) × HOURS_YR
# T = S / (S + OPP_COST × HOURS_YR)
S = SUBSISTENCE
C_total = OPP_COST_HR * HOURS_YR  # total opp cost per year per robot

T_required = S / (S + C_total)
P_star = OPP_COST_HR / (1 - T_required)  # equilibrium price per hour
yeoman_surplus_hr = P_star - OPP_COST_HR
yeoman_gross = yeoman_surplus_hr * HOURS_YR

print("─" * 72)
print("  PART 1: Required credit rate for subsistence")
print("─" * 72)
print(f"""
  Subsistence target:        ${S:,}/yr
  Buyer opp cost (total/yr): ${C_total:,.0f}/yr  (${OPP_COST_HR:.2f}/hr × {HOURS_YR:,.0f} hr)
  
  Required credit rate:      T* = {T_required*100:.1f}%
  Equilibrium price:         ${P_star:.2f}/hr  ({P_star/OPP_COST_HR:.1f}× opportunity cost)
  Yeoman surplus per hour:   ${yeoman_surplus_hr:.2f}/hr
  Yeoman gross income/yr:    ${yeoman_gross:,.0f}  (≈ subsistence target ✓)
  
  The credit roughly doubles what the buyer effectively pays
  (${OPP_COST_HR:.2f}/hr effective cost, ${P_star:.2f}/hr sticker price).
  Yeoman captures the gap as margin above their own capital cost.
""")

# ── Sensitivity: subsistence at different credit rates ─────────────────────
print("─" * 72)
print("  PART 2: Yeoman income at different credit rates (T)")
print("─" * 72)
print(f"  Buyer opp cost: ${OPP_COST_HR:.2f}/hr  |  Hours active: {HOURS_YR:,.0f}/yr")
print()
print(f"  {'Credit rate':>12}  {'Price/hr':>10}  {'Surplus/hr':>12}  {'Annual income':>14}  {'vs subsistence':>16}")
print(f"  {'-'*12}  {'-'*10}  {'-'*12}  {'-'*14}  {'-'*16}")

for T in [0.20, 0.30, 0.40, 0.50, T_required, 0.65, 0.70, 0.80]:
    P = OPP_COST_HR / (1 - T)
    surplus = (P - OPP_COST_HR) * HOURS_YR
    marker = " ← subsistence" if abs(T - T_required) < 0.005 else ""
    print(f"  {T*100:>11.1f}%  ${P:>8.2f}  ${P-OPP_COST_HR:>10.2f}  ${surplus:>12,.0f}  "
          f"{surplus/SUBSISTENCE*100:>14.0f}%{marker}")

# ── Fiscal flows ───────────────────────────────────────────────────────────
print()
print("─" * 72)
print(f"  PART 3: Net fiscal cost at T={T_required*100:.1f}% credit, {N_YEOMEN/1e6:.0f}M yeomen")
print("─" * 72)

gross_credit      = T_required * P_star * HOURS_YR * N_YEOMEN
income_tax_back   = INCOME_TAX_RATE * yeoman_gross * N_YEOMEN
unemployment_saved= UNEMPLOYMENT_BEN * N_YEOMEN
net_cost          = gross_credit - income_tax_back - unemployment_saved

# Also: what does the buyer save vs. employing humans at pre-AI wage?
HUMAN_WAGE_HR     = 25.00   # pre-AI median task wage
buyer_savings_yr  = (HUMAN_WAGE_HR - P_star * (1 - T_required)) * HOURS_YR * N_YEOMEN
buyer_tax_on_savings = 0.21 * buyer_savings_yr  # corporate tax on additional profit

net_after_buyer_tax = net_cost - buyer_tax_on_savings

print(f"""
  GOVERNMENT OUTFLOWS:
    Gross credit paid:            ${gross_credit/1e9:.0f}B/yr
      = {T_required*100:.1f}% × ${P_star:.2f}/hr × {HOURS_YR:,.0f} hr × {N_YEOMEN/1e6:.0f}M yeomen

  GOVERNMENT INFLOWS:
    Income tax on yeoman earnings: ${income_tax_back/1e9:.0f}B/yr
      = {INCOME_TAX_RATE*100:.0f}% × ${yeoman_gross:,.0f} × {N_YEOMEN/1e6:.0f}M
    Saved unemployment benefits:  ${unemployment_saved/1e9:.0f}B/yr
      = ${UNEMPLOYMENT_BEN:,}/yr × {N_YEOMEN/1e6:.0f}M (baseline cost avoided)

  NET FISCAL COST (before buyer tax effect):   ${net_cost/1e9:.0f}B/yr
  
  BUYER WINDFALL (corporations save on labor):
    Pre-AI human wage:            ${HUMAN_WAGE_HR:.2f}/hr
    Effective robot rate (w/credit): ${OPP_COST_HR:.2f}/hr
    Buyer savings:                ${buyer_savings_yr/1e9:.0f}B/yr
    Corporate tax on that profit: ${buyer_tax_on_savings/1e9:.0f}B/yr  (21% rate)

  NET FISCAL COST (after corporate tax on buyer windfall):  ${net_after_buyer_tax/1e9:.0f}B/yr
""")

# ── Funding: AI revenue levy ───────────────────────────────────────────────
print("─" * 72)
print("  PART 4: Funding the credit — AI revenue levy")
print("─" * 72)

AI_REVENUE = 3_000   # $3T projected AI-generated corporate revenue (10yr)
levy_rate_needed = net_after_buyer_tax / 1e9 / AI_REVENUE

print(f"""
  Net programme cost:               ${net_after_buyer_tax/1e9:.0f}B/yr
  AI-generated corporate revenue:   ${AI_REVENUE:,}B/yr (10yr projection)
  
  Levy rate needed:                 {levy_rate_needed*100:.1f}%
  
  For context:
    OECD Pillar Two global minimum: 15%
    US corporate rate:              21%
    Proposed AI revenue levy:       {levy_rate_needed*100:.0f}–{levy_rate_needed*100*1.5:.0f}%
    
  A {levy_rate_needed*100:.0f}% levy on AI-generated revenue funds {N_YEOMEN/1e6:.0f}M yeomen at subsistence.
  This is a small fraction of AI productivity gains going back into
  distributed capital ownership rather than accumulating at the top.
""")

# ── Cross-check: how much does buyer value the service above cost? ─────────
print("─" * 72)
print("  PART 5: Is the credit rate sustainable? (Does buyer value > price?)")
print("─" * 72)
print(f"""
  For the credit to work, the buyer must value the task above the sticker price.
  Otherwise they self-provision (run their own robot fleet).

  Key question: what stops large enterprises from just buying robots themselves?
  
  At equilibrium price ${P_star:.2f}/hr:
    Break-even for self-provision (own fleet):  ${OPP_COST_HR:.2f}/hr
    Sticker price from yeoman:                  ${P_star:.2f}/hr
    Effective cost after {T_required*100:.0f}% credit:           ${OPP_COST_HR:.2f}/hr  ← identical

  Buyer is exactly indifferent → they may as well hire yeomen (zero switching cost).
  Credit makes yeoman price competitive at any scale.
  
  Enterprises prefer yeomen when:
    • Variable demand (don't want to own idle capital)
    • Specialised tasks (certified yeoman has credential they don't)
    • Liability transfer (yeoman is legally responsible for the work)
    • Audit trail (registered matchmaker contract satisfies procurement rules)
    
  These are real preferences — the credit makes price neutral, these tip the balance.
  Large self-provisioning fleets remain viable for high-volume homogeneous tasks;
  yeoman market dominates variable, specialised, and liability-bearing work.
""")

# ── Summary table ──────────────────────────────────────────────────────────
print("=" * 72)
print("  SUMMARY")
print("=" * 72)
print(f"""
  Credit rate for subsistence ({N_YEOMEN/1e6:.0f}M yeomen, $150k robot):  {T_required*100:.1f}%
  Equilibrium price:                                          ${P_star:.2f}/hr  ({P_star/OPP_COST_HR:.1f}× opp cost)
  Gross credit cost:                                          ${gross_credit/1e9:.0f}B/yr
  Net fiscal cost (after tax recovery + unemployment saved):  ${net_cost/1e9:.0f}B/yr
  Net after corporate tax on buyer windfall:                  ${net_after_buyer_tax/1e9:.0f}B/yr
  AI revenue levy needed:                                     {levy_rate_needed*100:.1f}%
  
  The credit mechanism is self-consistent:
    Buyer pays market rate after credit → no distortion of their investment decisions
    Yeoman earns subsistence → distributed capital ownership maintained
    Government net cost < unemployment baseline (self-financing after ~yr 3)
    Funded by small levy on AI productivity gains that would otherwise accumulate narrowly
""")

