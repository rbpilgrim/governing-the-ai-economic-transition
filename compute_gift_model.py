"""
Compute Gift + Service Tax Model
==================================
Estimates the policy parameters needed to make AI providers rationally
gift compute to yeomen rather than self-provide AI services.

Core mechanism:
  - Government mandates AI providers allocate X tokens/yr to registered yeomen
  - High tax τ on AI providers selling 'intelligence as a service' directly
  - Yeomen have near-zero COGS (gifted compute) → can undercut AI providers
  - AI providers find gifting + stepping back from services better than self-provision

Three questions:
  1. How much compute does a yeoman actually need? (token budget)
  2. What tax rate τ makes self-provision irrational for AI providers?
  3. What's the aggregate compute requirement across N yeomen, and is it feasible?

Run: python3 compute_gift_model.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------------------
# Compute demand: how many tokens does a yeoman need per year?
# ---------------------------------------------------------------------------

# Billable hours per year (mid-tier yeoman, with platform)
BILLABLE_HOURS_YR = 1_000   # ~20 hrs/week × 50 weeks

# AI interactions per billable hour (prompts + completions)
# Varies a lot by task type — estimate ranges
INTERACTIONS_PER_HOUR = {
    "light":    10,   # mostly human judgment, occasional AI assist (writing review, research)
    "moderate": 35,   # typical knowledge work (coding, analysis, drafting)
    "heavy":    100,  # AI-intensive (data pipeline, code generation, content factory)
}

# Tokens per interaction (input + output combined)
TOKENS_PER_INTERACTION = {
    "light":    3_000,
    "moderate": 6_000,
    "heavy":    12_000,
}

# Token pricing (current 2025, projected 2030)
# GPT-4o class model
PRICE_PER_1M_TOKENS = {
    2025: 8.0,    # ~$5 input + $15 output blended ≈ $8/1M
    2028: 1.5,    # 5x reduction (historical trend: ~10x per 2 yrs, slowing)
    2032: 0.3,    # another 5x
}

def compute_per_yeoman(intensity: str) -> dict:
    interactions = INTERACTIONS_PER_HOUR[intensity]
    tokens_per   = TOKENS_PER_INTERACTION[intensity]
    annual_tokens = BILLABLE_HOURS_YR * interactions * tokens_per

    results = {"intensity": intensity, "annual_tokens_M": annual_tokens / 1e6}
    for year, price in PRICE_PER_1M_TOKENS.items():
        results[f"cost_{year}_usd"] = annual_tokens / 1e6 * price
    return results


# ---------------------------------------------------------------------------
# AI provider decision model
#
# Provider chooses between:
#   A) Self-provide: sell AI service directly to end buyers
#   B) Gift compute: allocate compute to yeomen, stay out of services
#
# The comparison is on NET PRESENT VALUE per unit of market (one yeoman's worth)
# ---------------------------------------------------------------------------

def provider_payoff(
    service_market_value: float,   # what buyers pay for full AI-augmented service / yeoman / yr
    ai_provider_margin: float,     # provider's gross margin if self-providing (incl. model + ops)
    compute_cost_actual: float,    # provider's true marginal cost of compute for one yeoman / yr
    compute_gift_fmv: float,       # fair market value of the gifted compute
    corp_tax_rate: float = 0.21,   # provider's corporate tax rate (for deduction calc)
    service_tax_rate: float = 0.0, # τ: tax on direct AI service provision revenue
) -> dict:
    """
    Compare provider economics under self-provision vs. compute gift.

    Key assumption: the service tax is on REVENUE from full-stack AI service
    delivery, not on raw compute/API sales. This creates a structural
    disincentive to vertically integrate into services.

    The gift is treated as a business expense (marketing / infrastructure
    contribution), fully deductible at corporate rate.
    """
    # Option A: Self-provide full AI service
    gross_profit_a  = service_market_value * ai_provider_margin
    service_tax_a   = service_market_value * service_tax_rate
    net_profit_a    = gross_profit_a - service_tax_a

    # Option B: Gift compute, step out of direct service provision
    # Cost = actual compute cost - tax deduction on gift at fair market value
    # (Provider deducts compute gift at FMV, even though their cost is lower)
    gift_deduction  = compute_gift_fmv * corp_tax_rate
    net_gift_cost   = compute_cost_actual - gift_deduction
    net_profit_b    = -net_gift_cost   # negative cost = positive when gift deduction > actual cost

    return {
        "service_market_value":   service_market_value,
        "service_tax_rate":       service_tax_rate,
        "option_a_gross_profit":  gross_profit_a,
        "option_a_service_tax":   service_tax_a,
        "option_a_net_profit":    net_profit_a,
        "option_b_compute_cost":  compute_cost_actual,
        "option_b_gift_deduction":gift_deduction,
        "option_b_net_profit":    net_profit_b,
        "gift_preferred":         net_profit_b > net_profit_a,
        "margin_difference":      net_profit_b - net_profit_a,
    }


def breakeven_tax(
    service_market_value: float,
    ai_provider_margin: float,
    compute_cost_actual: float,
    compute_gift_fmv: float,
    corp_tax_rate: float = 0.21,
) -> float:
    """
    Solve for τ* such that provider is indifferent between self-provision and gifting.

    Option A net profit = Option B net profit:
    service_market_value × margin - service_market_value × τ = -(compute_cost - gift × corp_tax)
    τ = margin + (compute_cost - gift × corp_tax) / service_market_value
    """
    gift_deduction = compute_gift_fmv * corp_tax_rate
    net_gift_cost  = compute_cost_actual - gift_deduction
    τ_star = ai_provider_margin + net_gift_cost / service_market_value
    return τ_star


# ---------------------------------------------------------------------------
# Aggregate compute supply feasibility
# ---------------------------------------------------------------------------

# Major AI provider compute capacity (very rough estimates, 2025)
# Based on disclosed capex, cluster sizes, and analyst estimates
PROVIDER_COMPUTE = {
    # (name, estimated GPU-hours/day available for inference, source notes)
    "OpenAI":    {"gpu_hours_day": 50_000_000,  "note": "~500k A100-equiv, ~65% util"},
    "Google":    {"gpu_hours_day": 200_000_000, "note": "TPU pods + A100s, rough estimate"},
    "Anthropic": {"gpu_hours_day": 10_000_000,  "note": "AWS partnership, conservative"},
    "Meta":      {"gpu_hours_day": 150_000_000, "note": "open weights, internal infra"},
    "Microsoft": {"gpu_hours_day": 100_000_000, "note": "Azure AI, partner capacity"},
}

# A100 GPU-hours to tokens (approximate, model-size dependent)
# GPT-4 class at ~1750 tokens/sec on A100 for output
TOKENS_PER_GPU_HOUR = 1_750 * 3600   # ~6.3M tokens/GPU-hour (output)
# But including input processing and batching overhead, effective:
EFFECTIVE_TOKENS_PER_GPU_HOUR = 3_000_000   # 3M tokens/GPU-hour blended

def aggregate_feasibility(n_yeomen: int, intensity: str = "moderate") -> dict:
    """
    Given N yeomen at a given intensity, estimate:
    - Total tokens required per year
    - Total GPU-hours required per year
    - As a % of estimated current industry capacity
    - How many tokens each major provider would need to allocate per yeoman
    """
    tokens_per_yeoman = (BILLABLE_HOURS_YR
                         * INTERACTIONS_PER_HOUR[intensity]
                         * TOKENS_PER_INTERACTION[intensity])
    total_tokens_yr   = n_yeomen * tokens_per_yeoman
    total_gpu_hours_yr = total_tokens_yr / EFFECTIVE_TOKENS_PER_GPU_HOUR

    total_industry_gpu_hours_day = sum(p["gpu_hours_day"] for p in PROVIDER_COMPUTE.values())
    total_industry_gpu_hours_yr  = total_industry_gpu_hours_day * 365

    pct_of_industry = total_gpu_hours_yr / total_industry_gpu_hours_yr * 100

    # Per-provider allocation (proportional to their capacity)
    provider_alloc = {}
    for name, data in PROVIDER_COMPUTE.items():
        provider_frac  = data["gpu_hours_day"] / total_industry_gpu_hours_day
        alloc_tokens   = total_tokens_yr * provider_frac
        alloc_per_yeoman = alloc_tokens / n_yeomen / 1e6  # M tokens per yeoman
        provider_alloc[name] = {
            "total_tokens_M": alloc_tokens / 1e6,
            "tokens_per_yeoman_M": alloc_per_yeoman,
        }

    return {
        "n_yeomen": n_yeomen,
        "tokens_per_yeoman_M": tokens_per_yeoman / 1e6,
        "total_tokens_B": total_tokens_yr / 1e9,
        "total_gpu_hours_M": total_gpu_hours_yr / 1e6,
        "industry_capacity_gpu_hours_M": total_industry_gpu_hours_yr / 1e6,
        "pct_of_industry_capacity": pct_of_industry,
        "provider_alloc": provider_alloc,
    }


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_model():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Compute Gift + Service Tax Model", fontsize=13, fontweight="bold")

    # ── Panel 1: Breakeven tax rate vs service market value ─────────────────
    ax = axes[0, 0]
    service_values = np.linspace(20_000, 200_000, 100)

    for label, compute_cost, gift_fmv, color in [
        ("Low compute ($500/yr)",    500,   500,   "#2ecc71"),
        ("Mid compute ($2k/yr)",    2000,  2000,   "#e67e22"),
        ("High compute ($8k/yr)",   8000,  8000,   "#e74c3c"),
    ]:
        taus = [breakeven_tax(sv, 0.65, cc, gf)
                for sv, cc, gf in zip(service_values,
                                       [compute_cost]*len(service_values),
                                       [gift_fmv]*len(service_values))]
        ax.plot(service_values / 1000, [t * 100 for t in taus],
                label=label, color=color, linewidth=2)

    ax.axhspan(40, 60, alpha=0.1, color="blue", label="Plausible policy range (40-60%)")
    ax.set_xlabel("Service market value per yeoman / yr ($k)")
    ax.set_ylabel("Breakeven service tax rate (%)")
    ax.set_title("Tax rate needed to make AI providers\nprefer gifting over self-provision")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    # ── Panel 2: Provider net profit at different tax rates ──────────────────
    ax = axes[0, 1]
    tax_rates = np.linspace(0, 1, 100)
    service_mv = 100_000
    margin     = 0.65
    comp_cost  = 2_000

    profit_a = [service_mv * margin - service_mv * τ for τ in tax_rates]
    profit_b = [-(comp_cost - comp_cost * 0.21)] * len(tax_rates)

    ax.plot(tax_rates * 100, [p/1000 for p in profit_a], "r-", linewidth=2,
            label="Self-provide (taxed)")
    ax.axhline(profit_b[0]/1000, color="g", linewidth=2, linestyle="--",
               label="Gift compute (fixed cost)")

    tau_star = breakeven_tax(service_mv, margin, comp_cost, comp_cost)
    ax.axvline(tau_star * 100, color="k", linestyle=":", linewidth=1.5,
               label=f"Breakeven τ* = {tau_star:.0%}")
    ax.fill_betweenx([-5, 70], tau_star*100, 100, alpha=0.1, color="green",
                     label="Gift preferred zone")

    ax.set_xlabel("Service tax rate τ (%)")
    ax.set_ylabel("Provider net profit per yeoman / yr ($k)")
    ax.set_title(f"Provider economics\n(100k service, 65% margin, 2k compute cost)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-5, 70)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    # ── Panel 3: Aggregate compute demand vs N yeomen ────────────────────────
    ax = axes[1, 0]
    yeomen_range = np.array([1e6, 5e6, 10e6, 20e6, 30e6, 50e6])

    for intensity, color, ls in [
        ("light",    "#2ecc71", "-"),
        ("moderate", "#e67e22", "-"),
        ("heavy",    "#e74c3c", "-"),
    ]:
        pcts = [aggregate_feasibility(int(n), intensity)["pct_of_industry_capacity"]
                for n in yeomen_range]
        ax.plot(yeomen_range / 1e6, pcts, color=color, linestyle=ls, linewidth=2,
                label=f"{intensity} intensity")

    ax.axhline(10, color="k", linestyle="--", alpha=0.5, label="10% of industry capacity")
    ax.axhline(25, color="k", linestyle=":",  alpha=0.5, label="25% of industry capacity")
    ax.set_xlabel("Number of yeomen (millions)")
    ax.set_ylabel("% of estimated industry GPU capacity")
    ax.set_title("Total compute demand as % of industry capacity\n(2025 capacity estimate)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    # ── Panel 4: Tokens per yeoman vs cost over time ─────────────────────────
    ax = axes[1, 1]
    intensities = ["light", "moderate", "heavy"]
    years = list(PRICE_PER_1M_TOKENS.keys())
    x = np.arange(len(years))
    width = 0.25

    for i, intensity in enumerate(intensities):
        d = compute_per_yeoman(intensity)
        costs = [d[f"cost_{yr}_usd"] for yr in years]
        ax.bar(x + (i-1)*width, costs, width, label=f"{intensity} ({d['annual_tokens_M']:.0f}M tok/yr)",
               alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_ylabel("Annual compute cost per yeoman (USD)")
    ax.set_title("Compute cost per yeoman by intensity & year\n(token price reduction trend)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    ax.axhline(500, color="navy", linestyle="--", alpha=0.6, label="$500 threshold")

    plt.tight_layout()
    plt.savefig("compute_gift_model.png", dpi=150, bbox_inches="tight")
    print("  Saved: compute_gift_model.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*72)
    print("COMPUTE GIFT + SERVICE TAX MODEL")
    print("="*72)

    # --- Compute demand per yeoman ---
    print("\n--- COMPUTE DEMAND PER YEOMAN / YEAR ---")
    print(f"  (Based on {BILLABLE_HOURS_YR} billable hours/year)")
    print(f"  {'Intensity':<12} {'Tokens/yr':>12} {'Cost 2025':>12} {'Cost 2028':>12} {'Cost 2032':>12}")
    print("  " + "─"*62)
    for intensity in ["light", "moderate", "heavy"]:
        d = compute_per_yeoman(intensity)
        print(f"  {d['intensity']:<12} {d['annual_tokens_M']:>9.0f}M  "
              f"${d['cost_2025_usd']:>9,.0f}  ${d['cost_2028_usd']:>9,.0f}  ${d['cost_2032_usd']:>9,.0f}")

    # --- Breakeven tax rates ---
    print("\n--- BREAKEVEN SERVICE TAX RATES ---")
    print("  (Tax rate at which AI providers prefer gifting compute over self-provision)")
    print(f"\n  {'Service value/yr':<20} {'Compute cost':<16} {'Margin':<10} {'Breakeven τ':>12}")
    print("  " + "─"*62)
    scenarios = [
        ("$50k/yr service",   50_000,  0.65, 500,   "light intensity"),
        ("$100k/yr service",  100_000, 0.65, 2_000, "moderate intensity"),
        ("$100k/yr service",  100_000, 0.65, 8_000, "heavy intensity"),
        ("$150k/yr service",  150_000, 0.70, 2_000, "high-tier operator"),
        ("$200k/yr service",  200_000, 0.75, 2_000, "top-tier specialist"),
    ]
    for label, smv, margin, comp, note in scenarios:
        tau = breakeven_tax(smv, margin, comp, comp)
        flag = " ← plausible" if 0.35 <= tau <= 0.65 else (" ← very high" if tau > 0.65 else " ← low")
        print(f"  {label:<20} ${comp:>6,}/yr ({note:<22}) {tau:>10.1%}{flag}")

    # --- Provider payoff at key tax rates ---
    print("\n--- PROVIDER PAYOFF: $100k service, 65% margin, $2k compute ---")
    print(f"  {'Tax rate':>10}  {'Self-provide profit':>22}  {'Gift cost':>12}  {'Gift preferred?':>16}")
    print("  " + "─"*65)
    for τ in [0.20, 0.35, 0.50, 0.65, 0.67, 0.70, 0.80]:
        r = provider_payoff(100_000, 0.65, 2_000, 2_000, service_tax_rate=τ)
        pref = "YES ✓" if r["gift_preferred"] else "no"
        print(f"  {τ:>10.0%}  ${r['option_a_net_profit']:>18,.0f}    ${abs(r['option_b_net_profit']):>8,.0f}    {pref:>16}")

    # --- Aggregate feasibility ---
    print("\n--- AGGREGATE COMPUTE FEASIBILITY ---")
    print("  (Moderate intensity, current 2025 industry capacity)")
    print(f"  {'Yeomen':>12}  {'Total tokens':>16}  {'GPU-hours':>14}  {'% of industry':>14}")
    print("  " + "─"*62)
    for n in [1_000_000, 5_000_000, 10_000_000, 20_000_000, 30_000_000]:
        f = aggregate_feasibility(n, "moderate")
        flag = ""
        if f["pct_of_industry_capacity"] > 30:
            flag = " ← strained"
        elif f["pct_of_industry_capacity"] > 10:
            flag = " ← significant"
        print(f"  {n/1e6:>8.0f}M  {f['total_tokens_B']:>12.0f}B tok  "
              f"{f['total_gpu_hours_M']:>10.0f}M hrs  {f['pct_of_industry_capacity']:>10.1f}%{flag}")

    # --- Per-provider allocation at 10M yeomen ---
    print("\n--- PROVIDER ALLOCATION AT 10M YEOMEN (moderate intensity) ---")
    f = aggregate_feasibility(10_000_000, "moderate")
    print(f"  Total tokens needed: {f['total_tokens_B']:.0f}B/yr  "
          f"({f['pct_of_industry_capacity']:.1f}% of current industry capacity)")
    print(f"  {'Provider':<14} {'Share of alloc':>16}  {'Tokens/yeoman':>16}")
    print("  " + "─"*50)
    for name, alloc in f["provider_alloc"].items():
        print(f"  {name:<14} {alloc['total_tokens_M']:>12,.0f}M tok  {alloc['tokens_per_yeoman_M']:>12.1f}M tok/yr")

    # --- Policy summary ---
    print("\n--- POLICY DESIGN SUMMARY ---")
    print("""
  COMPUTE GIFT SIZE:
    Moderate-intensity yeoman needs ~210M tokens/year (2025 prices: ~$1,700/yr)
    By 2028 at projected price declines: same tokens cost ~$315/yr
    The gift is cheap in dollar terms and getting cheaper fast.
    In regulation: mandate N tokens/year per registered yeoman,
    not a dollar value — quantity is what matters, price will fall.

    Recommended mandate: 200-250M tokens/year per yeoman
    (equivalent to ~35 meaningful AI interactions per billable hour)

  SERVICE TAX RATE:
    At $100k service value (mid-tier), breakeven τ ≈ 65-67%
    This is high — comparable to Nordic income tax on top bracket.
    Key insight: this tax is NOT on compute revenue (API tokens).
    It's specifically on DIRECT SERVICE PROVISION — AI companies
    acting as consultants/service providers, not as infrastructure.
    The distinction matters: Google Search isn't taxed here.
    OpenAI offering "AI consulting" to enterprises is.

    The tax creates a structural barrier to vertical integration
    from infrastructure into services — which is where concentration
    risk actually lives.

    Practical range: 50-70% on direct AI service revenue above
    a threshold (say >$10M/yr in direct service contracts).

  AGGREGATE FEASIBILITY:
    10M yeomen at moderate intensity = ~7% of current industry capacity.
    20M yeomen = ~14% — significant but not infeasible given 2x annual
    capacity growth trend.
    30M yeomen would be ~21% — this requires capacity growth over 2-3 yrs.
    The mandate should phase in with capacity: start with 5M yeomen,
    scale as industry capacity expands.

  THE DYNAMIC:
    AI providers spend $200B+ on capex (2025-2026).
    Much of this becomes excess capacity as efficiency improves.
    Gifting tokens to yeomen is a way to monetise excess capacity
    at near-zero marginal cost while getting a tax deduction.
    By 2028, gifting 200M tokens costs an AI provider ~$60-80 in
    marginal compute — trivial against the regulatory goodwill and
    tax benefit.
    """)

    print("Generating charts...")
    plot_model()
    print("="*72 + "\n")


if __name__ == "__main__":
    main()
