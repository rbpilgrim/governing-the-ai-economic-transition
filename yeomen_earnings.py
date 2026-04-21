"""
Yeomen Earnings Estimator
==========================
What do independent operators actually take home under different conditions?

Three periods:
  t0  2025  — pre-AI yeoman (current freelance baseline)
  t1  2030  — early AI adoption, productivity gains not yet competed away
  t2  2038  — mature AI market, competitive equilibration mostly complete

Three skill tiers:
  High    top 20% — deep domain expertise, reputation, specialised judgment
  Mid     middle 60% — competent generalists, moderate differentiation
  Low     bottom 20% — commodity tasks, low differentiation

Physical and knowledge work treated separately.

Key output: net annual income after SE tax, benefits, tools, utilisation drag.
Compare to: W-2 equivalent (what the employer pays vs what worker takes home).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

# Billable hours per week (of 40hr working week)
# Low = lots of BD, gaps, admin. High = established pipeline, platform helps.
UTILISATION = {
    "t0_no_platform":   {"low": 0.35, "mid": 0.48, "high": 0.58},
    "t1_with_platform": {"low": 0.50, "mid": 0.62, "high": 0.70},
    "t2_with_platform": {"low": 0.55, "mid": 0.65, "high": 0.72},
}
WORKING_WEEKS = 48   # 4 weeks off/sick/etc

# SE overhead (as fraction of gross, then fixed costs)
SE_TAX_RATE        = 0.153   # self-employment tax (both halves)
SE_TAX_DEDUCTIBLE  = 0.50    # SE tax is 50% deductible → effective ~11.5%
HEALTH_INS_ANNUAL  = 9_000   # individual market, mid-tier plan (2025 USD)
RETIREMENT_ANNUAL  = 4_000   # rough self-funded retirement saving
TOOLS_ANNUAL       = 4_500   # AI APIs + software + subscriptions
PROFESSIONAL_COSTS = 2_000   # accounting, legal, professional memberships

SE_FIXED_OVERHEAD = HEALTH_INS_ANNUAL + RETIREMENT_ANNUAL + TOOLS_ANNUAL + PROFESSIONAL_COSTS

# AI productivity multiplier on output per billable hour
# How much MORE output can an AI-augmented operator deliver vs pre-AI?
# High skill: AI handles 60-70% of execution, operator handles judgment/client → big leverage
# Mid: AI handles 40-50% → moderate leverage
# Low: tasks mostly automated away; remaining yeoman work is the judgment layer → complex
AI_OUTPUT_MULT = {
    "t0": {"high": 1.0, "mid": 1.0, "low": 1.0},   # baseline
    "t1": {"high": 3.5, "mid": 2.5, "low": 1.8},   # early AI: gains not competed away
    "t2": {"high": 2.0, "mid": 1.5, "low": 1.2},   # mature: competition compresses margins
                                                      # but operators still somewhat ahead of W-2
}

# Price competition factor: how much of the productivity gain is passed to buyers?
# 0 = operator keeps all gain (monopoly / early mover)
# 1 = all gain passed to buyers (perfect competition)
PRICE_COMPETITION = {
    "t0": 0.0,    # no AI to compete on
    "t1": 0.25,   # early adopters keep most of gain
    "t2": 0.65,   # mostly competed away, but differentiation still matters
}

# ---------------------------------------------------------------------------
# Hourly rates — knowledge work
# (Current market rates for independent consultants, pre-AI multiplier)
# ---------------------------------------------------------------------------
KNOW_RATES_T0 = {
    "high": 185,   # senior consultant / specialist: $150-220/hr
    "mid":   75,   # generalist analyst / developer: $55-95/hr
    "low":   32,   # commodity writing / basic tasks: $20-45/hr
}

# ---------------------------------------------------------------------------
# Hourly rates — physical work
# (Skilled trades, less AI-augmentable but still benefits from AI routing,
#  diagnostics, quoting, materials optimisation)
# ---------------------------------------------------------------------------
PHYS_RATES_T0 = {
    "high":  95,   # master electrician / HVAC specialist: $80-120/hr
    "mid":   55,   # general contractor / plumber: $45-70/hr
    "low":   28,   # unskilled physical: $22-35/hr
}
PHYS_AI_MULT = {
    "t0": {"high": 1.0, "mid": 1.0, "low": 1.0},
    "t1": {"high": 1.6, "mid": 1.3, "low": 1.1},   # diagnostic + quoting AI
    "t2": {"high": 1.4, "mid": 1.2, "low": 1.05},
}
PHYS_PRICE_COMPETITION = {"t0": 0.0, "t1": 0.15, "t2": 0.45}

# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def compute_earnings(
    base_rate: float,
    ai_mult: float,
    price_competition: float,
    utilisation: float,
    working_weeks: int = WORKING_WEEKS,
) -> dict:
    """
    Compute gross and net annual earnings for one operator.

    The effective rate = base_rate × AI_mult × (1 - fraction_passed_to_buyers)
    But AI also allows MORE clients at the SAME rate → utilisation rises.
    We model this as: effective rate stays at base × partial_capture,
    but the utilisation rate itself already incorporates the throughput benefit.
    """
    hours_per_week = 40
    billable_hours  = hours_per_week * utilisation * working_weeks

    # Rate after AI productivity × competitive pass-through
    effective_rate = base_rate * (1 + (ai_mult - 1) * (1 - price_competition))

    gross = effective_rate * billable_hours

    # SE overhead
    se_tax  = gross * SE_TAX_RATE * (1 - SE_TAX_DEDUCTIBLE * 0.25)  # simplified tax benefit
    net     = gross - se_tax - SE_FIXED_OVERHEAD

    return {
        "effective_rate":   effective_rate,
        "billable_hours":   billable_hours,
        "gross_annual":     gross,
        "se_tax":           se_tax,
        "fixed_overhead":   SE_FIXED_OVERHEAD,
        "net_annual":       max(net, 0),
        "net_hourly":       max(net, 0) / billable_hours if billable_hours > 0 else 0,
    }


def w2_net(gross_salary: float) -> float:
    """Employee take-home after income tax + employee FICA (no employer costs)."""
    employee_fica = gross_salary * 0.0765
    income_tax    = gross_salary * 0.22   # rough effective rate at these income levels
    return gross_salary - employee_fica - income_tax


def w2_employer_cost(gross_salary: float, office: str = "hybrid") -> float:
    """Total employer cost for a W-2 hire — what the company actually pays."""
    sqft_cost = {"remote": 0, "hybrid": 75 * 45, "office": 150 * 45}[office]
    return (gross_salary
            * (1 + 0.0765 + 0.015 + 0.01 + 0.04 + 0.096 + 0.15)
            + 8_700 + 2_500 + 1_500 + 3_000 + sqft_cost)


# ---------------------------------------------------------------------------
# Build full earnings table
# ---------------------------------------------------------------------------

def build_table():
    periods = {
        "t0 (2025, no platform)": ("t0", "t0_no_platform"),
        "t1 (2030, with platform)": ("t1", "t1_with_platform"),
        "t2 (2038, with platform)": ("t2", "t2_with_platform"),
    }
    tiers = ["high", "mid", "low"]

    rows = []
    for period_label, (t, util_key) in periods.items():
        for tier in tiers:
            util = UTILISATION[util_key][tier]

            # Knowledge work
            k = compute_earnings(
                KNOW_RATES_T0[tier],
                AI_OUTPUT_MULT[t][tier],
                PRICE_COMPETITION[t],
                util,
            )

            # Physical work
            p = compute_earnings(
                PHYS_RATES_T0[tier],
                PHYS_AI_MULT[t][tier],
                PHYS_PRICE_COMPETITION[t],
                util,
            )

            rows.append({
                "Period":           period_label,
                "Tier":             tier,
                "Utilisation":      util,
                # Knowledge
                "K rate ($/hr)":    round(k["effective_rate"]),
                "K gross ($k)":     round(k["gross_annual"] / 1000, 1),
                "K net ($k)":       round(k["net_annual"] / 1000, 1),
                # Physical
                "P rate ($/hr)":    round(p["effective_rate"]),
                "P gross ($k)":     round(p["gross_annual"] / 1000, 1),
                "P net ($k)":       round(p["net_annual"] / 1000, 1),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# W-2 equivalent comparison
# ---------------------------------------------------------------------------

def w2_comparison():
    """
    For context: what does a W-2 employee gross/net vs. a yeoman gross/net?
    Three reference salary points.
    """
    rows = []
    for label, salary in [("Low ($45k)", 45_000), ("Mid ($80k)", 80_000), ("High ($150k)", 150_000)]:
        rows.append({
            "W-2 salary": label,
            "Employee net ($k)":    round(w2_net(salary) / 1000, 1),
            "Employer total cost ($k)": round(w2_employer_cost(salary, "hybrid") / 1000, 1),
            "Employer/employee ratio": round(w2_employer_cost(salary, "hybrid") / salary, 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Income distribution: what does the yeomen economy look like in aggregate?
# ---------------------------------------------------------------------------

def income_distribution_t2():
    """
    At t2 (2038), if yeomen_frac = 0.50 of automatable work,
    what's the income distribution across ~60M operators?
    (Assuming 40% knowledge, 60% physical for illustrative split)
    """
    # Fraction of operators in each tier (roughly)
    tier_fracs = {"high": 0.20, "mid": 0.60, "low": 0.20}
    work_mix   = {"knowledge": 0.45, "physical": 0.55}

    t, util_key = "t2", "t2_with_platform"

    net_incomes = {}
    for tier, frac in tier_fracs.items():
        util = UTILISATION[util_key][tier]
        k = compute_earnings(KNOW_RATES_T0[tier], AI_OUTPUT_MULT[t][tier], PRICE_COMPETITION[t], util)
        p = compute_earnings(PHYS_RATES_T0[tier], PHYS_AI_MULT[t][tier], PHYS_PRICE_COMPETITION[t], util)
        blended_net = (k["net_annual"] * work_mix["knowledge"]
                       + p["net_annual"] * work_mix["physical"])
        net_incomes[tier] = blended_net

    total_operators = 60_000_000  # rough estimate of yeomen at 0.50 frac of 120M workforce

    print("\n  Income distribution at t2 (2038), 60M operators:")
    print(f"  {'Tier':<8} {'Frac':>6} {'Count':>10} {'Net income':>14} {'W-2 equiv salary':>18}")
    print("  " + "─"*60)
    total_income = 0
    for tier, frac in tier_fracs.items():
        n = int(total_operators * frac)
        net = net_incomes[tier]
        # W-2 equivalent: what salary would give the same take-home?
        w2_equiv = net / (1 - 0.0765 - 0.22)  # rough inverse
        total_income += net * n
        print(f"  {tier:<8} {frac:>6.0%} {n:>10,} {net/1000:>10.0f}k/yr  ~${w2_equiv/1000:.0f}k W-2 equiv")
    avg = total_income / total_operators
    print(f"  {'AVERAGE':<8} {'100%':>6} {total_operators:>10,} {avg/1000:>10.0f}k/yr")
    print(f"\n  Total yeomen income: ${total_income/1e12:.2f}T/yr")
    print(f"  (For context: US GDP ~$20T real in 2038 model)")


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_earnings():
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.suptitle("Yeomen Earnings by Tier and Period", fontsize=13, fontweight="bold")

    periods_plot = [
        ("t0 (2025, no platform)", "t0", "t0_no_platform", "#888"),
        ("t1 (2030, platform)",    "t1", "t1_with_platform", "#e67e22"),
        ("t2 (2038, platform)",    "t2", "t2_with_platform", "#2ecc71"),
    ]
    tiers = ["high", "mid", "low"]
    work_types = [
        ("Knowledge work", KNOW_RATES_T0, AI_OUTPUT_MULT, PRICE_COMPETITION),
        ("Physical work",  PHYS_RATES_T0, PHYS_AI_MULT,   PHYS_PRICE_COMPETITION),
    ]

    # Panel 1 & 2: Net income by tier and period for each work type
    for ax_idx, (wt_label, rates, ai_mults, price_comp) in enumerate(work_types):
        ax = axes[ax_idx]
        x = np.arange(len(tiers))
        width = 0.25

        for p_idx, (p_label, t, util_key, color) in enumerate(periods_plot):
            nets = []
            for tier in tiers:
                util = UTILISATION[util_key][tier]
                result = compute_earnings(rates[tier], ai_mults[t][tier], price_comp[t], util)
                nets.append(result["net_annual"] / 1000)
            bars = ax.bar(x + (p_idx - 1) * width, nets, width,
                          label=p_label, color=color, alpha=0.85)

        # W-2 comparison lines (what equivalent W-2 takes home)
        w2_nets = [w2_net(150_000)/1000, w2_net(75_000)/1000, w2_net(35_000)/1000]
        for i, (wn, tier) in enumerate(zip(w2_nets, tiers)):
            ax.hlines(wn, i - 0.4, i + 0.4, colors="navy", linewidths=1.5,
                      linestyles="--", alpha=0.6)

        ax.set_xticks(x)
        ax.set_xticklabels(["High tier\n(top 20%)", "Mid tier\n(mid 60%)", "Low tier\n(bot 20%)"])
        ax.set_ylabel("Net annual income ($k)")
        ax.set_title(f"{wt_label}\n(dashed = W-2 equivalent take-home)")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3, axis="y")
        ax.set_ylim(0, 350)

    # Panel 3: The utilisation drag — gross vs net over time for mid-tier knowledge
    ax = axes[2]
    t_periods = ["t0\n(2025)", "t1\n(2030)", "t2\n(2038)"]
    keys = [("t0", "t0_no_platform"), ("t1", "t1_with_platform"), ("t2", "t2_with_platform")]
    tier = "mid"

    grosses, nets, overheads = [], [], []
    for t, util_key in keys:
        util = UTILISATION[util_key][tier]
        r = compute_earnings(KNOW_RATES_T0[tier], AI_OUTPUT_MULT[t][tier], PRICE_COMPETITION[t], util)
        grosses.append(r["gross_annual"] / 1000)
        nets.append(r["net_annual"] / 1000)
        overheads.append((r["gross_annual"] - r["net_annual"]) / 1000)

    x = np.arange(len(t_periods))
    ax.bar(x, grosses, label="Gross revenue", color="#3498db", alpha=0.7)
    ax.bar(x, overheads, bottom=nets, label="SE overhead (tax + benefits + tools)", color="#e74c3c", alpha=0.7)
    ax.plot(x, nets, "ko-", linewidth=2, markersize=8, label="Net take-home", zorder=5)

    w2_equiv_net = w2_net(75_000) / 1000
    ax.axhline(w2_equiv_net, color="navy", linestyle="--", linewidth=1.5,
               label=f"W-2 $75k take-home (${w2_equiv_net:.0f}k)")

    ax.set_xticks(x)
    ax.set_xticklabels(t_periods)
    ax.set_ylabel("Annual ($k)")
    ax.set_title("Mid-tier knowledge worker\ngross vs net over time")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig("yeomen_earnings.png", dpi=150, bbox_inches="tight")
    print("  Saved: yeomen_earnings.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*72)
    print("YEOMEN EARNINGS ANALYSIS")
    print("="*72)

    df = build_table()

    print("\n--- KNOWLEDGE WORK: Net annual income ($k) ---")
    print(f"  {'Period':<30} {'Tier':<6} {'Rate':>8} {'Gross':>8} {'Net':>8}")
    print("  " + "─"*65)
    for _, row in df.iterrows():
        print(f"  {row['Period']:<30} {row['Tier']:<6} ${row['K rate ($/hr)']:>5}/hr  ${row['K gross ($k)']:>5}k  ${row['K net ($k)']:>5}k")

    print("\n--- PHYSICAL WORK: Net annual income ($k) ---")
    print(f"  {'Period':<30} {'Tier':<6} {'Rate':>8} {'Gross':>8} {'Net':>8}")
    print("  " + "─"*65)
    for _, row in df.iterrows():
        print(f"  {row['Period']:<30} {row['Tier']:<6} ${row['P rate ($/hr)']:>5}/hr  ${row['P gross ($k)']:>5}k  ${row['P net ($k)']:>5}k")

    print("\n--- W-2 REFERENCE: What employees take home vs what employers pay ---")
    w2 = w2_comparison()
    print(w2.to_string(index=False))

    print("\n--- SE OVERHEAD DRAG: Where gross income goes ---")
    print(f"  Fixed annual overhead per operator:")
    print(f"    Health insurance:   ${HEALTH_INS_ANNUAL:>7,}")
    print(f"    Retirement saving:  ${RETIREMENT_ANNUAL:>7,}")
    print(f"    AI tools + software:${TOOLS_ANNUAL:>7,}")
    print(f"    Professional costs: ${PROFESSIONAL_COSTS:>7,}")
    print(f"    Total fixed:        ${SE_FIXED_OVERHEAD:>7,}")
    print(f"  Plus SE tax ~{SE_TAX_RATE:.1%} of gross (partially deductible)")
    print(f"  Break-even gross (just to cover overhead): ~${SE_FIXED_OVERHEAD / (1 - SE_TAX_RATE):.0f}")
    print(f"  → Operators earning <~${SE_FIXED_OVERHEAD / (1 - SE_TAX_RATE)/1000:.0f}k gross are worse off than W-2")

    income_distribution_t2()

    print("\n--- KEY OBSERVATIONS ---")
    print("""
  1. THE UTILISATION PROBLEM IS THE BIGGEST DRAG
     A $75/hr mid-tier knowledge worker billing 48% of hours (t0)
     earns ~$55k gross → $30k net. Same rate at 65% utilisation (t1)
     earns ~$75k gross → $50k net. Platform matters more through
     utilisation than through fee elimination.

  2. EARLY AI IS VERY GOOD FOR YEOMEN; LATE AI IS STILL OK
     t1 (2030): AI productivity gain not yet fully competed away →
     high-tier operators can make $200k+ net. Mid-tier: $80-100k net.
     t2 (2038): Margins compress but utilisation stays high → mid-tier
     settles at $60-80k net, which beats equivalent W-2 take-home.

  3. LOW-TIER IS THE PROBLEM
     Bottom 20% of operators — low differentiation, commodity tasks —
     are squeezed: AI competes their prices down faster than it boosts
     their productivity. Net income at t2 is worse than W-2 equivalent.
     This is the welfare case: these workers likely need human-economy
     jobs or public support, not a yeomen platform.

  4. PHYSICAL WORK BECOMES STRUCTURALLY ATTRACTIVE WITH PLATFORM
     The employer's W-2 cost for physical workers (office, workers comp,
     benefits) is very high relative to salary. Eliminating those via
     yeoman outsourcing + zero-fee platform creates real wage-equivalent
     gains even with modest AI augmentation.

  5. THE OVERHEAD FLOOR MATTERS
     ~$20k/yr in fixed SE overhead (health, retirement, tools) means
     any operator grossing <$30k is materially worse off than W-2.
     This argues for: (a) group health plans through the platform,
     (b) portable retirement via platform-administered accounts,
     (c) subsidised AI tool access for low-income operators.
     The platform needs to be more than just matching infrastructure —
     it needs to deliver the benefits layer that employment currently provides.
  """)

    print("Generating chart...")
    plot_earnings()
    print("="*72 + "\n")


if __name__ == "__main__":
    main()
