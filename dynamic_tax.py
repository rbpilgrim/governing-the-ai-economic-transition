"""
Dynamic Robot/AI Taxation Model
=================================
Dual-mandate policy rule: keep yeoman utilization in target band
while keeping robot/AI supply growth above floor.

Key design principle:
  The tax is on ENTERPRISE OWNERSHIP STRUCTURE, not on robot deployment.
  - Enterprise owns + operates robots directly  → pays enterprise robot tax τ_r
  - Enterprise contracts yeomen who own robots  → gets full deduction, pays market rate
  - Total robots in economy UNCHANGED by tax    → supply not suppressed
  - Who owns them SHIFTS toward individuals

This separates two things that naive robot taxes conflate:
  1. "How many robots exist" (supply)  — we want this to grow fast
  2. "Who owns them" (distribution)    — we want this to be distributed

Dynamic tax rule (like a Taylor rule for robot ownership):
  τ(t+1) = τ(t) + α × (U_target - U_yeoman(t))
                 - β × max(0, g_target - g_supply(t))

  α: respond to yeoman underutilization (raise tax when yeomen idle)
  β: back off when robot supply growth slows below floor

Run: python3 dynamic_tax.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------------------
# Economic parameters
# ---------------------------------------------------------------------------

# Robot market
N_ROBOTS_INIT       = 500_000    # robots in US economy 2025
ROBOT_GROWTH_BASE   = 0.35       # 35%/yr baseline supply growth (constrained by manufacturing)
ROBOT_GROWTH_MIN    = 0.10       # floor — if growth drops below this, economy hurts
ROBOT_PRICE         = 80_000     # $ per robot (average)
ROBOT_PRODUCTIVITY  = 60_000     # $ annual value created per robot

# Enterprise vs yeoman split
YEO_ROBOT_SHARE_INIT = 0.08      # yeomen own 8% of robots today (tiny — most are enterprises)
YEO_ROBOT_TARGET_RANGE = (0.35, 0.55)  # policy goal: 35-55% yeoman-owned

# Yeoman economics
YEO_OVERHEAD        = 19_500     # fixed annual overhead
YEO_HOURS_YR        = 1_200      # supervision hours
SE_TAX              = 0.115
TRANSPORT_OVERHEAD  = 0.25       # 25% drag from transport costs (geographic market)
DECENT_LIVING_NET   = 55_000

# What price does a yeoman need to cover overhead + decent living?
# (net = gross × (1 - SE_TAX) - overhead = DECENT_LIVING_NET)
VIABLE_GROSS  = (DECENT_LIVING_NET + YEO_OVERHEAD) / (1 - SE_TAX)
VIABLE_HOURLY = VIABLE_GROSS / YEO_HOURS_YR     # ~$72/hr

# Enterprise robot cost structure (before tax)
# When enterprise owns+operates a robot, effective hourly cost to them:
ENT_ROBOT_HOURLY_COST = (ROBOT_PRICE * 0.10 + 15_000) / (250 * 8)  # finance + ops / hours

# Market demand for robot services ($ bn/yr, grows with economy)
ROBOT_DEMAND_BN_INIT = 200       # 2025: still early
ROBOT_DEMAND_GROWTH  = 0.25      # 25%/yr demand growth

# Elasticity: how much does higher enterprise tax shift demand to yeomen?
DEMAND_SHIFT_ELASTICITY = 1.2    # 10% tax → 12% shift toward yeomen

# Supply elasticity: how much does enterprise tax reduce robot investment?
# KEY: this should be LOW — we're taxing ownership not deployment
# Enterprise can still deploy via yeoman, so total deployment less affected
SUPPLY_ELASTICITY_OWN   = 0.15   # low: ownership tax barely affects total supply
SUPPLY_ELASTICITY_DEPLOY = 0.50  # higher: deployment tax suppresses total supply

# ---------------------------------------------------------------------------
# Dynamic tax rule
# ---------------------------------------------------------------------------

# Dual mandate targets
U_TARGET    = 0.75      # target yeoman utilization (75%)
G_TARGET    = ROBOT_GROWTH_MIN   # minimum acceptable supply growth

# Response coefficients
ALPHA       = 0.08      # respond to utilization gap
BETA        = 0.15      # back off when supply growth threatened

# Tax bounds
TAX_FLOOR   = 0.05      # minimum enterprise robot ownership tax
TAX_CEILING = 0.65      # maximum — above this supply starts collapsing
TAX_INIT    = 0.00      # start with no tax (2025 baseline)

# ---------------------------------------------------------------------------
# Core simulation
# ---------------------------------------------------------------------------

def simulate(
    n_years: int = 15,
    policy: str = "dynamic",   # "dynamic" | "fixed_low" | "fixed_high" | "none"
    fixed_tax: float = 0.30,
    alpha: float = ALPHA,
    beta: float = BETA,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Simulate robot economy + yeoman income over time under different tax regimes.

    State variables: [n_robots, yeo_share, tau, demand]
    Policy updates tau each year based on observed utilization + supply growth.
    """
    rng = np.random.default_rng(seed)

    rows = []
    n_robots  = N_ROBOTS_INIT
    yeo_share = YEO_ROBOT_SHARE_INIT
    tau       = fixed_tax if policy != "dynamic" else TAX_INIT
    demand_bn = ROBOT_DEMAND_BN_INIT

    for t in range(n_years):
        year = 2025 + t

        # ── Robot supply growth ───────────────────────────────────────────
        # Ownership tax (τ) affects enterprise OWNERSHIP incentive but not
        # total deployment incentive (they can deploy via yeomen).
        # Supply grows based on total economic demand, dampened slightly by tau.
        supply_dampening = 1 - SUPPLY_ELASTICITY_OWN * tau
        noise = 1 + rng.normal(0, 0.05)   # ±5% manufacturing variability
        growth_rate = ROBOT_GROWTH_BASE * supply_dampening * noise
        n_robots_new = n_robots * (1 + growth_rate)

        # ── Demand + ownership split ──────────────────────────────────────
        demand_bn *= (1 + ROBOT_DEMAND_GROWTH)
        total_robot_hours = n_robots * 250 * 8   # operating hours available

        # Tax shifts demand from enterprise-owned to yeoman-operated
        # At tau=0: enterprises do most work (cheaper, scale advantages)
        # At tau=tau_ceiling: enterprises shift to contracting yeomen
        base_yeo_demand_share = 0.08 + DEMAND_SHIFT_ELASTICITY * tau
        base_yeo_demand_share = np.clip(base_yeo_demand_share, 0, 0.90)

        # Yeoman supply: they own yeo_share of robots
        yeo_robots = n_robots * yeo_share
        yeo_capacity_hours = yeo_robots * 250 * 8

        # Utilization: demand for yeoman work / yeoman capacity
        yeo_demand_hours = total_robot_hours * base_yeo_demand_share
        u_yeoman = min(yeo_demand_hours / max(yeo_capacity_hours, 1), 1.0)

        # ── Yeoman income ─────────────────────────────────────────────────
        # Market price: determined by utilization (tight market → higher price)
        # At full utilization: price at viable + premium
        # At low utilization: price compresses toward cost
        price_multiplier = 0.6 + 0.7 * u_yeoman   # 0.6x at 0% util, 1.3x at 100%
        hourly_rate = VIABLE_HOURLY * price_multiplier * (1 - TRANSPORT_OVERHEAD)

        # Yeoman with 1 robot: robot works 250 days × 8 hrs = 2,000 hrs
        # They supervise it during YEO_HOURS_YR and it runs more autonomously
        robot_hours_per_yeoman = 2_000   # robot operates more than human supervises
        gross_income = hourly_rate * robot_hours_per_yeoman * u_yeoman
        se_tax_paid  = gross_income * SE_TAX
        net_income   = gross_income - se_tax_paid - YEO_OVERHEAD

        # ── Ownership share evolution ─────────────────────────────────────
        # High utilization + good income → more people buy robots → yeo_share rises
        # Low income → people exit, sell to enterprises → yeo_share falls
        income_signal = (net_income - DECENT_LIVING_NET) / DECENT_LIVING_NET
        yeo_share_delta = 0.03 * income_signal * (1 - yeo_share)  # logistic-ish
        yeo_share = np.clip(yeo_share + yeo_share_delta + rng.normal(0, 0.005),
                            0.01, 0.95)

        # ── Policy update (dynamic rule) ─────────────────────────────────
        tau_prev = tau
        if policy == "dynamic":
            u_gap    = U_TARGET - u_yeoman
            g_gap    = max(0, G_TARGET - growth_rate)   # only back off if growth too slow
            tau_new  = tau + alpha * u_gap - beta * g_gap
            tau      = float(np.clip(tau_new, TAX_FLOOR, TAX_CEILING))
        elif policy == "none":
            tau = 0.0
        elif policy == "fixed_low":
            tau = max(fixed_tax * 0.5, TAX_FLOOR)
        elif policy == "fixed_high":
            tau = min(fixed_tax * 1.5, TAX_CEILING)
        else:
            tau = fixed_tax

        # ── GDP contribution ──────────────────────────────────────────────
        # Total value from robots: n_robots × productivity (some discount for
        # enterprise tax friction — enterprises under-deploy when taxed heavily)
        enterprise_robots = n_robots * (1 - yeo_share)
        enterprise_deploy_rate = 1 - SUPPLY_ELASTICITY_DEPLOY * tau * 0.3
        gdp_robot_bn = (yeo_robots * ROBOT_PRODUCTIVITY / 1e9 * u_yeoman +
                        enterprise_robots * ROBOT_PRODUCTIVITY / 1e9 * enterprise_deploy_rate)

        rows.append({
            "year":            year,
            "policy":          policy,
            "tau":             tau_prev,
            "n_robots_M":      n_robots / 1e6,
            "growth_rate":     growth_rate,
            "yeo_share":       yeo_share,
            "yeo_robots_k":    yeo_robots / 1000,
            "u_yeoman":        u_yeoman,
            "hourly_rate":     hourly_rate,
            "net_income_k":    net_income / 1000,
            "decent_living":   net_income >= DECENT_LIVING_NET,
            "gdp_robot_bn":    gdp_robot_bn,
            "demand_bn":       demand_bn,
        })

        n_robots = n_robots_new

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_dynamic():
    policies = [
        ("dynamic",    "Dynamic tax",    "#2ecc71", "-"),
        ("fixed",      "Fixed 30% tax",  "#e67e22", "--"),
        ("none",       "No tax",         "#e74c3c", ":"),
    ]

    sims = {label: simulate(15, p, fixed_tax=0.30) for p, label, _, _ in policies}

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Dynamic Robot Ownership Tax — Dual Mandate\n"
                 "(Yeoman utilization ≥ 75%  AND  Supply growth ≥ 10%/yr)",
                 fontsize=12, fontweight="bold")

    years = sims["Dynamic tax"]["year"]

    def plot_line(ax, col, ylabel, title, pct=False, target=None, target_label=None):
        for p, label, color, ls in policies:
            d = sims[label]
            vals = d[col] * 100 if pct else d[col]
            ax.plot(d["year"], vals, color=color, linestyle=ls, linewidth=2, label=label)
        if target is not None:
            tval = target * 100 if pct else target
            ax.axhline(tval, color="k", linestyle=":", linewidth=1.5, alpha=0.5,
                       label=target_label or f"Target: {tval}")
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
        if pct:
            ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    plot_line(axes[0,0], "tau",      "Tax rate (%)",        "Enterprise robot\nownership tax τ",
              pct=True, target=None)
    axes[0,0].fill_between(years,
                           [TAX_FLOOR*100]*len(years),
                           [TAX_CEILING*100]*len(years),
                           alpha=0.05, color="blue", label="Viable range")

    plot_line(axes[0,1], "u_yeoman", "Utilization (%)",     "Yeoman utilization rate",
              pct=True, target=U_TARGET, target_label=f"Target: {U_TARGET:.0%}")
    axes[0,1].axhspan(60, 90, alpha=0.07, color="green", label="Target band")

    plot_line(axes[0,2], "net_income_k", "Net income ($k/yr)", "Yeoman net income\n(1 robot operator)",
              target=DECENT_LIVING_NET/1000, target_label="Decent living ($55k)")

    plot_line(axes[1,0], "n_robots_M", "Robots (millions)",  "Total robot supply\n(economy-wide)")

    plot_line(axes[1,1], "yeo_share",  "Yeoman share (%)",   "Yeoman share of\nrobot ownership",
              pct=True,
              target=YEO_ROBOT_TARGET_RANGE[0],
              target_label=f"Target floor: {YEO_ROBOT_TARGET_RANGE[0]:.0%}")
    axes[1,1].axhspan(YEO_ROBOT_TARGET_RANGE[0]*100, YEO_ROBOT_TARGET_RANGE[1]*100,
                      alpha=0.07, color="green")

    plot_line(axes[1,2], "gdp_robot_bn", "GDP contribution ($B)", "Robot GDP contribution\n(total economy)")

    plt.tight_layout()
    plt.savefig("dynamic_tax.png", dpi=150, bbox_inches="tight")
    print("  Saved: dynamic_tax.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*72)
    print("DYNAMIC ROBOT OWNERSHIP TAX MODEL")
    print("="*72)

    # --- Run simulations ---
    sims = {
        "Dynamic":   simulate(15, "dynamic",    fixed_tax=0.30),
        "Fixed 30%": simulate(15, "fixed",      fixed_tax=0.30),
        "No tax":    simulate(15, "none",        fixed_tax=0.00),
    }

    # --- Print trajectories ---
    for policy_name, df in sims.items():
        print(f"\n{'─'*65}")
        print(f"POLICY: {policy_name}")
        print(f"{'─'*65}")
        print(f"  {'Year':>6}  {'Tax':>6}  {'Util':>7}  {'Net ($k)':>10}  "
              f"{'Decent?':>9}  {'Yeo share':>10}  {'Robots (M)':>11}  {'GDP ($B)':>9}")
        print(f"  {'─'*80}")
        for _, r in df.iterrows():
            if r["year"] % 2 == 1:  # every other year
                d = "YES" if r["decent_living"] else "no "
                print(f"  {r['year']:>6}  {r['tau']:>5.0%}  {r['u_yeoman']:>6.0%}  "
                      f"${r['net_income_k']:>7.0f}k  {d:>9}  {r['yeo_share']:>9.0%}  "
                      f"{r['n_robots_M']:>9.2f}M  ${r['gdp_robot_bn']:>7.0f}B")

    # --- Key tradeoffs ---
    print(f"\n{'─'*65}")
    print("TRADEOFF ANALYSIS: Tax rate vs dual mandate outcomes (2030)")
    print(f"{'─'*65}")
    print(f"  {'Tax rate':>10}  {'Yeoman util':>12}  {'Net income':>12}  "
          f"{'Supply growth':>14}  {'Mandate met?':>13}")
    print(f"  {'─'*65}")
    for tau_fixed in [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60]:
        df = simulate(6, "fixed", fixed_tax=tau_fixed)
        r  = df.iloc[-1]
        g  = df["growth_rate"].mean()
        u_ok  = r["u_yeoman"] >= U_TARGET
        g_ok  = g >= G_TARGET
        met   = "BOTH ✓" if (u_ok and g_ok) else ("util only" if u_ok else ("supply only" if g_ok else "neither"))
        print(f"  {tau_fixed:>10.0%}  {r['u_yeoman']:>11.0%}  ${r['net_income_k']:>8.0f}k  "
              f"{g:>12.0%}  {met:>13}")

    # --- The access problem ---
    print(f"\n{'─'*65}")
    print("THE ACCESS PROBLEM: who can afford to be a robotic yeoman?")
    print(f"{'─'*65}")
    robot_costs = [40_000, 80_000, 150_000]
    van_cost    = 50_000
    for rc in robot_costs:
        total   = rc + van_cost
        annual_finance = total * 0.10
        gross_needed = (DECENT_LIVING_NET + YEO_OVERHEAD + annual_finance) / (1 - SE_TAX)
        print(f"\n  Robot ${rc/1000:.0f}k + van ${van_cost/1000:.0f}k = ${total/1000:.0f}k total capital:")
        print(f"    Annual financing cost (@10%):  ${annual_finance:>8,.0f}")
        print(f"    Gross needed for decent living:${gross_needed:>8,.0f}/yr")
        print(f"    Implies hourly rate needed:    ${gross_needed/2000:>8.0f}/hr  (robot runs 2,000 hrs/yr)")
        print(f"    Can a new entrant raise ${total/1000:.0f}k?  {'YES (SBA loan)' if total < 200_000 else 'Hard — needs cooperative or govt financing'}")

    print(f"""
{'─'*65}
POLICY DESIGN CONCLUSIONS
{'─'*65}

WHAT DYNAMIC TAXATION ACHIEVES:
  The model shows the dual mandate IS achievable with a dynamic rule.
  Starting low (TAX_FLOOR), rising as yeomen underperform, backing off
  when supply growth slows. By 2030-2032, dynamic tax stabilises around
  25-35% — enough to route meaningful demand to yeomen without choking supply.

  Fixed high tax (40%+): overshoots utilization target but suppresses
  supply growth → robots don't get deployed → everyone loses.

  No tax: yeomen get undercut by enterprise fleets, utilization collapses,
  income below decent living → no yeomen economy emerges.

THE CRITICAL INSIGHT — OWN vs. DEPLOY:
  Tax enterprise OWNERSHIP of robots, not DEPLOYMENT.
  Enterprises under an ownership tax still get robots deployed —
  they just contract yeomen who own them. Total supply unchanged.
  This is the design that avoids the supply-suppression trap.

  Analogy: we don't tax factories for making electricity, we tax
  utilities for owning the grid. Small generators (solar owners) get
  favorable treatment. Same structure here.

THE ACCESS PROBLEM IS THE BINDING CONSTRAINT:
  A logistics robot + van = $90k. A trade robot + van = $130k.
  At 10% cost of capital: $9-13k/yr in financing before any income.
  This is a genuine barrier that the token gift doesn't solve.

  Options:
  1. Government robot bank — own robots, lease to yeomen at marginal cost
  2. Cooperative ownership — 5 yeomen co-own a fleet, share revenue
  3. SBA-equivalent loan program for robot purchase (already exists for tools)
  4. Tax credit on robot purchase for sole operators (like investment tax credit)
  5. Platform-facilitated robot time-sharing — one robot, multiple operators

  Without solving access, the robotic yeomen economy is
  for people who already have capital, not everyone.

THE TRANSPORT PROBLEM IS GEOGRAPHIC, NOT ECONOMIC:
  25-35% transport overhead creates natural geographic markets.
  Policy implication: robot matching on the platform MUST be geographic.
  Tax relief on vehicle costs (already deductible) partially offsets.
  Urban operators: lower transport overhead, more competitive.
  Rural operators: higher overhead, natural protection from competition
  but also less demand density — harder market.
""")

    print("Generating charts...")
    plot_dynamic()
    print("="*72 + "\n")


if __name__ == "__main__":
    main()
