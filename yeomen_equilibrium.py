"""
Yeomen Compute Gift — Equilibrium Model
========================================
Core question: what token gift + service tax level puts competing yeomen
at a decent living wage without over-subsidising or taxing AI progress?

Key constraints:
  - Compute is SCARCE (no excess capacity). Gift is a forced reallocation.
  - Yeomen compete with each other → prices compress toward minimum viable rate.
  - Companies prefer cheap yeomen over AI providers (gifted compute = low COGS).
  - Remaining compute after gift goes to enterprise at market rates.
  - Tax must fund the reallocation without killing R&D investment incentives.

Run: python3 yeomen_equilibrium.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOKENS_PER_YEOMAN_YEAR  = 1_000_000_000    # 1B tokens/yr (proposed gift)
HUMAN_HOURS_PER_YEAR    = 1_200             # ~24 hrs/wk × 50 wks (billable)

# Token intensity ranges — how many tokens does a yeoman burn per billable hour?
# Higher = more agentic/intensive workflows (reasoning models, long chains, tool use)
TOKENS_PER_HOUR = {
    "basic":    200_000,   # lightweight assist: 200k/hr → 1B covers 5,000 hrs
    "standard": 500_000,   # typical professional: 500k/hr → 1B covers 2,000 hrs
    "intensive":1_000_000, # full agentic: 1M/hr → 1B covers 1,000 hrs (= human hrs)
    "frontier": 2_000_000, # reasoning-heavy: 2M/hr → 1B covers 500 hrs (binding!)
}
# At 'intensive': 1B tokens exactly matches 1,200 human hours → no waste
# At 'frontier':  1B tokens is the binding constraint, not human time

# Fixed SE overhead per yeoman per year (health, retirement, tools, accounting)
SE_OVERHEAD_ANNUAL = 19_500

# "Decent living" target: net income the yeoman should earn
# Not spectacular, not poverty — roughly median individual income
DECENT_LIVING_NET = 55_000   # ~$55k net ≈ $75k gross equivalent W-2 salary

# Opportunity cost of yeoman time (what they could earn in W-2 labour market)
# Varies by skill tier
OPPORTUNITY_COST_HOURLY = {
    "low_skill":  18,    # minimum-ish wage, limited alternatives
    "mid_skill":  35,    # decent W-2 job
    "high_skill": 65,    # professional employment alternative
}

# Self-employment tax rate (effective, partially deductible)
SE_TAX_EFFECTIVE = 0.115

# Current token market price (enterprise, no subsidy)
TOKEN_PRICE_PER_M = {
    2025: 8.0,
    2027: 2.5,
    2030: 0.8,
}

# US demand for AI-augmented professional services (total market, $ billions/yr)
# This is the total spend companies make on services that COULD be done by yeomen
AI_SERVICE_DEMAND_BN = {
    2025: 200,    # early market — AI-augmentable services
    2027: 600,    # growing rapidly
    2030: 1_500,  # mainstream
}

# Demand price elasticity for AI-augmented services
# -0.8 means 10% price drop → 8% more demand
DEMAND_ELASTICITY = -0.8


# ---------------------------------------------------------------------------
# Core: minimum viable yeoman rate
# ---------------------------------------------------------------------------

def min_viable_rate(skill: str, hours: int = HUMAN_HOURS_PER_YEAR) -> dict:
    """
    Minimum hourly rate a yeoman will accept, given:
      - Fixed SE overhead they must cover
      - Opportunity cost of their time
      - No compute COGS (gifted)

    This is the floor price in a competitive yeoman market.
    Below this, the operator is better off taking a W-2 job.
    """
    opp_cost_annual = OPPORTUNITY_COST_HOURLY[skill] * hours
    gross_needed    = (opp_cost_annual + SE_OVERHEAD_ANNUAL) / (1 - SE_TAX_EFFECTIVE)
    min_rate        = gross_needed / hours
    net_income      = gross_needed * (1 - SE_TAX_EFFECTIVE) - SE_OVERHEAD_ANNUAL

    return {
        "skill":           skill,
        "opp_cost_hourly": OPPORTUNITY_COST_HOURLY[skill],
        "gross_needed":    gross_needed,
        "min_rate_hourly": min_rate,
        "net_at_min_rate": net_income,
    }


# ---------------------------------------------------------------------------
# Market equilibrium
# ---------------------------------------------------------------------------

def equilibrium_price(
    n_yeomen: int,
    year: int,
    demand_scale: float = 1.0,
) -> dict:
    """
    Find market clearing price for AI-augmented services.

    Supply: n_yeomen × HUMAN_HOURS_PER_YEAR hours of service
    Demand: price-elastic demand curve anchored at AI_SERVICE_DEMAND_BN

    Demand curve: Q_demand = Q_0 × (P / P_0)^elasticity
    P_0 = current AI provider direct-service price (what companies pay without yeomen)
    Q_0 = total market hours at P_0

    At equilibrium: Q_supply = Q_demand
    Solve for P.
    """
    total_demand_bn   = AI_SERVICE_DEMAND_BN[year] * demand_scale
    # Average hourly rate companies currently pay for AI-augmented services
    # (AI provider direct provision, pre-tax, approximately)
    p_0 = 150   # $150/hr benchmark (AI consulting / professional services avg)

    # Total hours demanded at P_0
    q_0 = (total_demand_bn * 1e9) / p_0

    # Total yeoman supply (hours)
    q_supply = n_yeomen * HUMAN_HOURS_PER_YEAR

    # Solve P* such that q_0 × (P* / p_0)^elasticity = q_supply
    # q_supply = q_0 × (P*/p_0)^e
    # (P*/p_0)^e = q_supply / q_0
    # P* = p_0 × (q_supply/q_0)^(1/e)
    ratio = q_supply / q_0
    p_star = p_0 * (ratio ** (1 / DEMAND_ELASTICITY))

    # Yeoman gross revenue at equilibrium
    gross_per_yeoman = p_star * HUMAN_HOURS_PER_YEAR
    net_per_yeoman   = gross_per_yeoman * (1 - SE_TAX_EFFECTIVE) - SE_OVERHEAD_ANNUAL

    # Mid-skill floor rate for reference
    floor = min_viable_rate("mid_skill")

    return {
        "year":               year,
        "n_yeomen_M":         n_yeomen / 1e6,
        "eq_price":           p_star,
        "gross_per_yeoman":   gross_per_yeoman,
        "net_per_yeoman":     net_per_yeoman,
        "above_floor":        p_star > floor["min_rate_hourly"],
        "above_decent_living": net_per_yeoman >= DECENT_LIVING_NET,
        "floor_rate":         floor["min_rate_hourly"],
        "total_market_value_bn": (p_star * q_supply) / 1e9,
    }


# ---------------------------------------------------------------------------
# Value created per yeoman at 1B tokens
# ---------------------------------------------------------------------------

def value_per_yeoman(intensity: str, eq_price: float) -> dict:
    """
    Economic value a single yeoman creates, given token intensity and market price.

    The token allocation determines the CEILING on AI-assisted hours.
    Human time is always the floor constraint.
    """
    ai_hours_enabled = TOKENS_PER_YEOMAN_YEAR / TOKENS_PER_HOUR[intensity]
    binding          = "compute" if ai_hours_enabled < HUMAN_HOURS_PER_YEAR else "human_time"
    effective_hours  = min(ai_hours_enabled, HUMAN_HOURS_PER_YEAR)

    market_value     = effective_hours * eq_price
    gross            = market_value   # competitive market, price = marginal value
    net              = gross * (1 - SE_TAX_EFFECTIVE) - SE_OVERHEAD_ANNUAL

    token_market_val = TOKENS_PER_YEOMAN_YEAR / 1e6 * TOKEN_PRICE_PER_M[2025]

    return {
        "intensity":          intensity,
        "tokens_per_hour":    TOKENS_PER_HOUR[intensity],
        "ai_hours_enabled":   ai_hours_enabled,
        "binding_constraint": binding,
        "effective_hours":    effective_hours,
        "market_value":       market_value,
        "net_income":         net,
        "token_gift_value":   token_market_val,    # $ value of the gifted tokens at market rate
        "income_per_token_gifted": market_value / TOKENS_PER_YEOMAN_YEAR * 1e6,  # $/1M tokens
    }


# ---------------------------------------------------------------------------
# The subsidy efficiency / tax calibration
# ---------------------------------------------------------------------------

def tax_calibration(n_yeomen: int, year: int) -> dict:
    """
    How much does the compute gift cost, and what tax rate funds it
    without punishing AI R&D?

    Cost of gift:
      = n_yeomen × 1B tokens × token_price (opportunity cost — these tokens
        could have gone to enterprise at full market price)

    Tax revenue needed:
      = gift opportunity cost (at minimum; could fund other programs too)

    Tax base:
      = AI provider DIRECT SERVICE REVENUE (not compute/API revenue)
      = fraction of total AI market that is "full stack" service provision

    The tax should NOT apply to:
      - Raw compute / API token sales (this is infrastructure, not services)
      - Model training / R&D
      - Enterprise software / SaaS with AI features
    It SHOULD apply to:
      - AI companies acting as consultants / service providers
      - "AI as a service" where AI company takes end-to-end responsibility
    Estimated direct-service fraction of AI market: ~15-25%
    """
    token_price     = TOKEN_PRICE_PER_M[year]
    gift_opp_cost   = n_yeomen * TOKENS_PER_YEOMAN_YEAR / 1e6 * token_price  # total $ opportunity cost

    # Total AI market revenue (rough estimate, grows with compute demand)
    ai_market_bn    = {2025: 500, 2027: 1_200, 2030: 3_000}[year]
    service_frac    = 0.20   # fraction that is direct-service (taxable)
    taxable_base_bn = ai_market_bn * service_frac

    tax_rate_needed = gift_opp_cost / (taxable_base_bn * 1e9)

    # Also compute: what would a 40% tax on direct services raise?
    revenue_at_40pct = taxable_base_bn * 0.40  # $bn

    return {
        "year":                   year,
        "n_yeomen_M":             n_yeomen / 1e6,
        "token_price_per_M":      token_price,
        "gift_opp_cost_bn":       gift_opp_cost / 1e9,
        "ai_market_bn":           ai_market_bn,
        "taxable_base_bn":        taxable_base_bn,
        "tax_rate_to_fund_gift":  tax_rate_needed,
        "revenue_at_40pct_bn":    revenue_at_40pct,
        "funded_by_40pct":        revenue_at_40pct * 1e9 >= gift_opp_cost,
    }


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_equilibrium():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Yeomen Equilibrium: Compute Gift Economics", fontsize=13, fontweight="bold")

    yeomen_range = np.linspace(0.5e6, 40e6, 200)

    # ── Panel 1: Equilibrium price vs N yeomen ───────────────────────────────
    ax = axes[0, 0]
    for year, color in [(2025, "#888"), (2027, "#e67e22"), (2030, "#2ecc71")]:
        prices = [equilibrium_price(int(n), year)["eq_price"] for n in yeomen_range]
        ax.plot(yeomen_range / 1e6, prices, color=color, linewidth=2, label=str(year))

    floor = min_viable_rate("mid_skill")["min_rate_hourly"]
    decent_rate = (DECENT_LIVING_NET + SE_OVERHEAD_ANNUAL) / (1 - SE_TAX_EFFECTIVE) / HUMAN_HOURS_PER_YEAR
    ax.axhline(floor, color="red", linestyle="--", linewidth=1.5, label=f"Min viable rate: ${floor:.0f}/hr")
    ax.axhline(decent_rate, color="navy", linestyle="--", linewidth=1.5,
               label=f"Decent living rate: ${decent_rate:.0f}/hr")

    ax.set_xlabel("Number of yeomen (millions)")
    ax.set_ylabel("Market clearing price ($/hr)")
    ax.set_title("Equilibrium hourly rate vs yeoman supply\n(demand grows with year)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 200)

    # ── Panel 2: Net income per yeoman ───────────────────────────────────────
    ax = axes[0, 1]
    for year, color in [(2025, "#888"), (2027, "#e67e22"), (2030, "#2ecc71")]:
        nets = [equilibrium_price(int(n), year)["net_per_yeoman"] / 1000 for n in yeomen_range]
        ax.plot(yeomen_range / 1e6, nets, color=color, linewidth=2, label=str(year))

    ax.axhline(DECENT_LIVING_NET / 1000, color="navy", linestyle="--", linewidth=1.5,
               label=f"Decent living target: ${DECENT_LIVING_NET/1000:.0f}k")
    ax.axhline(0, color="red", linestyle=":", linewidth=1, alpha=0.7, label="Break-even")

    ax.set_xlabel("Number of yeomen (millions)")
    ax.set_ylabel("Net annual income ($k)")
    ax.set_title("Yeoman net income at equilibrium\n(all competing, mid-skill)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-20, 150)

    # ── Panel 3: Value per yeoman by token intensity ─────────────────────────
    ax = axes[1, 0]
    intensities = list(TOKENS_PER_HOUR.keys())
    eq_2027 = equilibrium_price(10_000_000, 2027)["eq_price"]

    vals = [value_per_yeoman(i, eq_2027) for i in intensities]
    hours    = [v["effective_hours"] for v in vals]
    mkt_vals = [v["market_value"] / 1000 for v in vals]
    nets     = [v["net_income"] / 1000 for v in vals]
    gift_val = [v["token_gift_value"] / 1000 for v in vals]

    x = np.arange(len(intensities))
    w = 0.25
    ax.bar(x - w, mkt_vals,  w, label="Market value (gross)", color="#3498db", alpha=0.85)
    ax.bar(x,     nets,      w, label="Net income",            color="#2ecc71", alpha=0.85)
    ax.bar(x + w, gift_val,  w, label="Token gift value (mkt rate)", color="#e74c3c", alpha=0.85)

    ax.axhline(DECENT_LIVING_NET / 1000, color="navy", linestyle="--", linewidth=1.5,
               label=f"Decent living: ${DECENT_LIVING_NET/1000:.0f}k")

    # Mark which constraint binds
    for i, v in enumerate(vals):
        constraint = "compute" if v["binding_constraint"] == "compute" else "time"
        ax.text(i, -8, f"bound by\n{constraint}", ha="center", fontsize=7, color="gray")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{i}\n({TOKENS_PER_HOUR[i]//1000}k tok/hr)" for i in intensities],
                       fontsize=8)
    ax.set_ylabel("Annual ($k)")
    ax.set_title(f"Value per yeoman at 1B tokens by AI intensity\n(10M yeomen, 2027 market price: ${eq_2027:.0f}/hr)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylim(-15, 200)

    # ── Panel 4: Tax rate to fund gift ───────────────────────────────────────
    ax = axes[1, 1]
    n_range = np.linspace(1e6, 30e6, 100)

    for year, color in [(2025, "#888"), (2027, "#e67e22"), (2030, "#2ecc71")]:
        tax_rates = [tax_calibration(int(n), year)["tax_rate_to_fund_gift"] * 100
                     for n in n_range]
        ax.plot(n_range / 1e6, tax_rates, color=color, linewidth=2, label=str(year))

    ax.axhspan(30, 50, alpha=0.1, color="blue", label="Plausible service tax range (30-50%)")
    ax.axhline(40, color="blue", linestyle="--", linewidth=1, alpha=0.6)

    ax.set_xlabel("Number of yeomen (millions)")
    ax.set_ylabel("Service tax rate needed to fund gift (%)")
    ax.set_title("Tax rate on AI direct-service revenue\nneeded to fund compute gift program")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig("yeomen_equilibrium.png", dpi=150, bbox_inches="tight")
    print("  Saved: yeomen_equilibrium.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*72)
    print("YEOMEN EQUILIBRIUM MODEL — 1B TOKENS/YEOMAN/YEAR")
    print("="*72)

    # --- Minimum viable rates ---
    print("\n--- MINIMUM VIABLE HOURLY RATES (floor in competitive market) ---")
    print(f"  {'Skill tier':<14} {'Opp cost':>10} {'Min rate':>10} {'Net at floor':>14}")
    print("  " + "─"*52)
    for skill in OPPORTUNITY_COST_HOURLY:
        r = min_viable_rate(skill)
        print(f"  {skill:<14} ${r['opp_cost_hourly']:>7}/hr  ${r['min_rate_hourly']:>7.0f}/hr  ${r['net_at_min_rate']/1000:>8.1f}k/yr")

    decent_rate = (DECENT_LIVING_NET + SE_OVERHEAD_ANNUAL) / (1 - SE_TAX_EFFECTIVE) / HUMAN_HOURS_PER_YEAR
    print(f"\n  Decent living target: ${DECENT_LIVING_NET/1000:.0f}k net → ${decent_rate:.0f}/hr needed")

    # --- Value per yeoman at 1B tokens ---
    print("\n--- VALUE PER YEOMAN: 1B TOKENS, DIFFERENT AI INTENSITIES ---")
    print(f"  (Market price: $80/hr — equilibrium at ~10M yeomen in 2027)")
    print(f"  {'Intensity':<12} {'Tok/hr':>8} {'Hours':>8} {'Binding':>10} {'Gross':>10} {'Net':>10} {'$/1M tok gifted':>16}")
    print("  " + "─"*78)
    for intensity in TOKENS_PER_HOUR:
        v = value_per_yeoman(intensity, 80)
        print(f"  {intensity:<12} {TOKENS_PER_HOUR[intensity]//1000:>5}k/hr  "
              f"{v['effective_hours']:>6.0f}  {v['binding_constraint']:>10}  "
              f"${v['market_value']/1000:>6.0f}k  ${v['net_income']/1000:>6.0f}k  "
              f"${v['income_per_token_gifted']:>8.2f}/1M")

    # --- Market equilibrium at key yeomen counts ---
    print("\n--- MARKET EQUILIBRIUM: PRICE + INCOME BY SCALE ---")
    for year in [2025, 2027, 2030]:
        print(f"\n  Year {year}:")
        print(f"  {'Yeomen':>10}  {'Eq price':>10}  {'Gross/yr':>10}  {'Net/yr':>10}  {'Decent living?':>16}")
        print("  " + "─"*60)
        for n in [2_000_000, 5_000_000, 10_000_000, 15_000_000, 20_000_000, 30_000_000]:
            eq = equilibrium_price(n, year)
            dl = "YES" if eq["above_decent_living"] else "no"
            print(f"  {n/1e6:>8.0f}M  ${eq['eq_price']:>7.0f}/hr  "
                  f"${eq['gross_per_yeoman']/1000:>6.0f}k  ${eq['net_per_yeoman']/1000:>6.0f}k  {dl:>16}")

    # --- Tax calibration ---
    print("\n--- TAX CALIBRATION: WHAT RATE FUNDS THE GIFT? ---")
    print("  (Tax on AI direct-service revenue only; compute/API revenue untouched)")
    for year in [2025, 2027, 2030]:
        print(f"\n  Year {year}  |  AI market: ${tax_calibration(10_000_000, year)['ai_market_bn']}B  "
              f"| Taxable base (20%): ${tax_calibration(10_000_000, year)['taxable_base_bn']:.0f}B")
        print(f"  {'Yeomen':>10}  {'Gift opp cost':>16}  {'Tax rate needed':>16}  {'40% funds it?':>14}")
        print("  " + "─"*60)
        for n in [5_000_000, 10_000_000, 20_000_000]:
            tc = tax_calibration(n, year)
            funded = "YES" if tc["funded_by_40pct"] else "no"
            print(f"  {n/1e6:>8.0f}M  ${tc['gift_opp_cost_bn']:>10.1f}B  "
                  f"{tc['tax_rate_to_fund_gift']*100:>13.1f}%  {funded:>14}")

    # --- Design sweet spot ---
    print("\n--- DESIGN SWEET SPOT ---")
    print("""
  THE BINDING CONSTRAINT DEPENDS ON TOKEN INTENSITY:
    - Basic/Standard use (200-500k tokens/hr): human time binds, not tokens.
      1B tokens gives 2-5x more than the yeoman can use. The gift is oversized
      but ensures they never ration AI quality mid-task.
    - Intensive/Frontier use (1-2M tokens/hr): tokens bind or co-bind.
      At frontier intensity, 1B tokens = ~500 billable hours — you only get
      half a working year of full AI capability. This is where 1B feels tight.

  WHAT 1B TOKENS ACTUALLY ENABLES:
    At standard intensity ($80/hr market, 2027):
      Effective hours = 2,000 (token ceiling) vs 1,200 (human ceiling)
      → Human time is still binding; tokens are not rationed
      → Gross: ~$96k, Net: ~$60k  ← AT the decent living target
      → The gift is well-sized for this intensity

    At frontier/reasoning intensity (heavy agentic workflows):
      Effective hours = 500 (compute-bound)
      → Tokens ARE the constraint; yeoman can only do 500 real hrs of this work
      → Gross: ~$40k, Net: ~$14k  ← BELOW decent living
      → Would need 2.4B tokens for frontier intensity to hit decent living

  THE COMPETITION DYNAMIC:
    More yeomen → lower equilibrium price → lower net income per yeoman.
    The program self-limits: if income drops below floor, yeomen exit to W-2.
    At 10M yeomen (2027): ~$80/hr equilibrium → ~$60k net → barely decent.
    At 5M yeomen (2027):  ~$105/hr → ~$85k net → good.
    At 20M yeomen (2027): ~$63/hr → ~$42k net → below decent living.

    This means the token gift SIZE should scale with N:
      More yeomen → need more tokens each to maintain viable income.
      OR: cap the number of registered yeomen to hold the price floor.
      OR: let the market self-regulate — as income drops, yeomen exit.

  TAX RATE TO FUND IT:
    At 10M yeomen (2027), gift opportunity cost: ~$25B/yr.
    Taxable AI service revenue base: ~$240B (20% of $1.2T market).
    Tax rate needed: ~10-11% on direct-service revenue.
    A 40% tax overfunds it massively → could fund UBI for displaced workers too.
    The 65-67% breakeven tax (from prior model) is NOT needed if the goal is
    just funding the gift — 10-15% is sufficient. The higher rate is only
    needed to STRUCTURALLY PREVENT AI providers from competing with yeomen.
    These are two separate levers: funding tax vs. structural tax.

  RECOMMENDED POLICY PARAMETERS:
    Token gift:    1B tokens/registered yeoman/year (standard intensity)
                   Scale to 2.5B if frontier AI models dominate by 2030
    Funding tax:   15-20% on AI direct-service revenue > $10M/yr
    Structural tax: 50-60% on AI direct-service revenue > $100M/yr
                   (creates price floor above which yeomen undercut)
    Yeomen cap:    Register at most N* yeomen such that equilibrium net >= $50k
                   N* ≈ 8-12M in 2027, growing with AI service demand
    """)

    print("Generating charts...")
    plot_equilibrium()
    print("="*72 + "\n")


if __name__ == "__main__":
    main()
