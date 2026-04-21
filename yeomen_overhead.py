"""
Yeomen Outsourcing Overhead Estimator
======================================
Estimates the transaction costs that companies face when outsourcing
knowledge/physical work to yeomen (AI-augmented sole operators) versus
keeping W-2 employees — and how those costs change with the procurement
platform.

Three regimes compared:
  A. W-2 employee (baseline)
  B. Yeoman via private platform (current state: Upwork / Fiverr / etc.)
  C. Yeoman via government procurement platform (proposed)

Key findings fed back into the macro model:
  - effective_yeomen_suppression: how much transaction overhead reduces
    the achievable yeoman fraction below the structural maximum
  - duration_threshold: engagement length at which outsourcing breaks even
    vs. employment
  - platform_overhead_factor: residual friction even with ideal platform

Run: python3 yeomen_overhead.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------------------
# Constants — W-2 overhead components
# ---------------------------------------------------------------------------

# Employer-side costs as fraction of base salary (US 2025)
W2_FICA           = 0.0765   # Social Security 6.2% + Medicare 1.45%
W2_WORKERS_COMP   = 0.015    # varies by industry; ~1.5% for office/knowledge work
W2_UNEMP_INS      = 0.010    # federal + state unemployment insurance
W2_401K_MATCH     = 0.040    # typical 3-4% match
W2_HEALTH_ANNUAL  = 8_000    # employer share, single coverage (KFF 2024: ~$8k)
W2_DENTAL_VIS     = 700      # employer share
W2_PTO_FRAC       = 0.096    # 25 days PTO+holiday / 261 working days = ~9.6% of salary paid non-productive
W2_HR_ADMIN       = 3_000    # HR/admin overhead per employee per year
W2_EQUIP_IT       = 2_500    # laptop + software + IT support per year
W2_TRAINING       = 1_500    # training & development per year
W2_OFFICE_SQFT    = 150      # sqft per knowledge worker (remote=0, hybrid=75, in-office=150)
W2_OFFICE_COST    = 45       # $/sqft/yr (Class B office, US average)
W2_MGMT_OVERHEAD  = 0.15     # fraction of direct manager's time per employee (at manager's loaded rate)

# ---------------------------------------------------------------------------
# Constants — Yeoman overhead components (per engagement)
# ---------------------------------------------------------------------------

# CURRENT (private platform)
YEO_DISCOVERY_MIN   = 500     # $ — time to post, review, shortlist (min)
YEO_DISCOVERY_MAX   = 3_000   # $ — extensive search for specialist
YEO_CONTRACT_MIN    = 500     # $ — template review, NDA, IP terms
YEO_CONTRACT_MAX    = 4_000   # $ — legal review for complex/high-value
YEO_ONBOARD_MIN     = 2_000   # $ — knowledge transfer, context, tools setup
YEO_ONBOARD_MAX     = 15_000  # $ — for deeply embedded domain knowledge
YEO_PLATFORM_TAKE   = 0.275   # 27.5% average effective take (Upwork ~20% listed + buyer fees + algorithmic tax)
YEO_QA_OVERHEAD     = 0.08    # 8% of engagement value — reviewing deliverables
YEO_COORD_PREMIUM   = 0.20    # 20% more management time than W-2 equivalent
YEO_MISCLASS_RISK   = 0.025   # 2.5% of contract value as expected cost of misclassification exposure
                               # (probability × penalty; ABC test states, IRS scrutiny)

# Supplier rate premium (supplier must charge more to cover own benefits + SE tax + platform take)
# W-2 employee at $X base → employer fully-loaded cost ~1.38X
# Yeoman to net equivalent after-tax: must gross ~1.40X on top of platform fee
# Platform take 27.5% → buyer gross rate = yeoman_gross / (1 - 0.275)
# Approximate: buyer pays ~1.65-1.90x W-2 base for equivalent output
YEO_CURRENT_RATE_PREMIUM_KNOW = 1.72   # knowledge work (includes platform take in gross rate)
YEO_CURRENT_RATE_PREMIUM_PHYS = 1.45   # physical work (lower because fewer displaced fixed costs)

# PLATFORM (government open-standard platform)
YEO_PLT_DISCOVERY  = 100      # $ — automated matching, nearly zero
YEO_PLT_CONTRACT   = 50       # $ — standard modules, no legal review needed
YEO_PLT_ONBOARD    = 3_000    # $ — average (can't eliminate knowledge transfer; assume mid-range)
YEO_PLT_PLATFORM_TAKE = 0.00  # 0% — funded as public infrastructure
YEO_PLT_QA         = 0.05     # 5% — milestone-based, slightly lower than open-ended
YEO_PLT_COORD      = 0.12     # 12% — better tooling (standard milestones, A2A agent handoffs)
YEO_PLT_MISCLASS   = 0.002    # 0.2% — platform creates clear 1099 record, dramatically lower
YEO_PLT_RATE_PREMIUM_KNOW = 1.35  # supplier charges less — no platform fee, more competition
YEO_PLT_RATE_PREMIUM_PHYS = 1.25

# ---------------------------------------------------------------------------
# Helper: compute total annual cost per worker for each regime
# ---------------------------------------------------------------------------

def w2_fully_loaded(base_salary: float, office_mode: str = "hybrid") -> dict:
    """
    Total employer cost to have a W-2 employee for 1 year.
    office_mode: "remote" | "hybrid" | "office"
    """
    office_sqft = {"remote": 0, "hybrid": 75, "office": 150}[office_mode]
    office_cost  = office_sqft * W2_OFFICE_COST

    components = {
        "base_salary":       base_salary,
        "fica":              base_salary * W2_FICA,
        "workers_comp":      base_salary * W2_WORKERS_COMP,
        "unemp_ins":         base_salary * W2_UNEMP_INS,
        "401k_match":        base_salary * W2_401K_MATCH,
        "health_dental_vis": W2_HEALTH_ANNUAL + W2_DENTAL_VIS,
        "pto_nonprod":       base_salary * W2_PTO_FRAC,
        "hr_admin":          W2_HR_ADMIN,
        "equip_it":          W2_EQUIP_IT,
        "training":          W2_TRAINING,
        "office":            office_cost,
        "mgmt_overhead":     base_salary * W2_MGMT_OVERHEAD,
    }
    components["total"] = sum(components.values())
    return components


def yeoman_cost_current(
    base_salary: float,
    engagement_months: float,
    work_type: str = "knowledge",
    onboard_complexity: str = "medium",  # "low" | "medium" | "high"
) -> dict:
    """
    Total buyer cost to hire a yeoman via private platform for N months
    worth of equivalent W-2 output.

    base_salary: the W-2 equivalent annual salary (to normalise comparison).
    """
    rate_premium = YEO_CURRENT_RATE_PREMIUM_KNOW if work_type == "knowledge" else YEO_CURRENT_RATE_PREMIUM_PHYS
    annual_equiv  = base_salary * rate_premium   # what buyer pays before per-engagement costs
    engagement_val = annual_equiv * (engagement_months / 12)

    onboard_cost = {
        "low":    YEO_ONBOARD_MIN,
        "medium": (YEO_ONBOARD_MIN + YEO_ONBOARD_MAX) / 2,
        "high":   YEO_ONBOARD_MAX,
    }[onboard_complexity]

    discovery = (YEO_DISCOVERY_MIN + YEO_DISCOVERY_MAX) / 2
    contract  = (YEO_CONTRACT_MIN  + YEO_CONTRACT_MAX)  / 2

    components = {
        "engagement_rate_inc_platform_take": engagement_val,
        "discovery_search":                  discovery,
        "contracting_legal":                 contract,
        "onboarding_knowledge_transfer":     onboard_cost,
        "qa_review_overhead":                engagement_val * YEO_QA_OVERHEAD,
        "coordination_premium":              base_salary * (engagement_months/12) * YEO_COORD_PREMIUM,
        "misclassification_risk":            engagement_val * YEO_MISCLASS_RISK,
    }
    components["total"] = sum(components.values())
    return components


def yeoman_cost_platform(
    base_salary: float,
    engagement_months: float,
    work_type: str = "knowledge",
    onboard_complexity: str = "medium",
) -> dict:
    """Total buyer cost via government platform."""
    rate_premium = YEO_PLT_RATE_PREMIUM_KNOW if work_type == "knowledge" else YEO_PLT_RATE_PREMIUM_PHYS
    annual_equiv  = base_salary * rate_premium
    engagement_val = annual_equiv * (engagement_months / 12)

    components = {
        "engagement_rate_no_platform_take": engagement_val,
        "discovery_search":                 YEO_PLT_DISCOVERY,
        "contracting_standard_modules":     YEO_PLT_CONTRACT,
        "onboarding_knowledge_transfer":    YEO_PLT_ONBOARD,
        "qa_review_overhead":               engagement_val * YEO_PLT_QA,
        "coordination_premium":             base_salary * (engagement_months/12) * YEO_PLT_COORD,
        "misclassification_risk":           engagement_val * YEO_PLT_MISCLASS,
    }
    components["total"] = sum(components.values())
    return components


# ---------------------------------------------------------------------------
# Analysis 1: Cost comparison by engagement duration
# ---------------------------------------------------------------------------

def cost_vs_duration(base_salary: float = 120_000, work_type: str = "knowledge",
                      onboard: str = "medium", office: str = "hybrid"):
    months = np.arange(1, 37)

    w2 = w2_fully_loaded(base_salary, office)
    w2_monthly = w2["total"] / 12

    current_totals  = [yeoman_cost_current(base_salary, m, work_type, onboard)["total"]  for m in months]
    platform_totals = [yeoman_cost_platform(base_salary, m, work_type, onboard)["total"] for m in months]
    w2_totals       = [w2_monthly * m for m in months]

    # Find break-even months
    def breakeven(yeoman_costs, w2_costs):
        for i, (y, w) in enumerate(zip(yeoman_costs, w2_costs)):
            if y > w:
                return months[i]
        return None

    be_current  = breakeven(current_totals, w2_totals)
    be_platform = breakeven(platform_totals, w2_totals)

    return months, w2_totals, current_totals, platform_totals, be_current, be_platform


# ---------------------------------------------------------------------------
# Analysis 2: Overhead component breakdown (annualised, 12-month engagement)
# ---------------------------------------------------------------------------

def overhead_breakdown(base_salary: float = 120_000):
    w2 = w2_fully_loaded(base_salary, "hybrid")
    cur = yeoman_cost_current(base_salary, 12, "knowledge", "medium")
    plt_ = yeoman_cost_platform(base_salary, 12, "knowledge", "medium")
    return w2, cur, plt_


# ---------------------------------------------------------------------------
# Analysis 3: Effective yeomen fraction suppression
# ---------------------------------------------------------------------------

def effective_yeomen_suppression():
    """
    Estimates the gap between structural yeomen potential (what AI makes
    technically possible) and effective yeomen fraction (what actually
    happens given transaction costs).

    The model has yeomen_frac as target parameter (e.g. 0.60 in the
    high-yeomen scenario). But friction means the achieved fraction is lower.

    This function estimates:
      - structural_max: what fraction of currently W-2 work is technically
        outsourceable as discrete, verifiable tasks
      - current_effective: structural_max × (1 - friction_suppression)
      - platform_effective: structural_max × (1 - residual_friction)

    Friction suppression logic:
      A task is worth outsourcing if the expected cost difference
      (yeoman - w2) < 0. Friction shifts this threshold: tasks that would
      be worth outsourcing become not worth it because per-engagement costs
      exceed the rate savings at short durations.
    """

    # What fraction of total W-2 work is STRUCTURALLY discrete enough to outsource?
    # (can be spec'd, delivered, and verified as a bounded task)
    # Knowledge work: ~60-70% structurally fungible (the rest is continuous, embedded)
    # Physical work: ~40-50% structurally fungible (rest is ongoing operations)
    structural_max_know = 0.65
    structural_max_phys = 0.45

    # At each engagement duration, what fraction of structurally fungible work
    # actually BECOMES worth outsourcing (cost saves exceed overhead)?
    durations  = np.array([1, 2, 3, 6, 9, 12, 18, 24])   # months
    base_salary = 120_000

    fracs_current  = []
    fracs_platform = []

    for d in durations:
        w2_cost = w2_fully_loaded(base_salary, "hybrid")["total"] * (d/12)
        cur = yeoman_cost_current(base_salary, d, "knowledge", "medium")["total"]
        plt_ = yeoman_cost_platform(base_salary, d, "knowledge", "medium")["total"]

        # Fraction of fungible tasks worth outsourcing at this duration
        # If yeoman cost < w2, all fungible tasks get outsourced
        # If yeoman cost > w2, assume linear reduction (0 at 2x w2 cost)
        def worth_frac(yeoman_cost, w2_cost):
            ratio = yeoman_cost / w2_cost
            if ratio <= 1.0:
                return 1.0
            elif ratio >= 2.0:
                return 0.0
            else:
                return 1.0 - (ratio - 1.0)  # linear between 1x and 2x

        fracs_current.append(worth_frac(cur, w2_cost))
        fracs_platform.append(worth_frac(plt_, w2_cost))

    # Weighted average: assume work is evenly distributed across engagement durations
    # (simplification — in reality most is long-duration, so this is conservative)
    weights = np.array([0.05, 0.08, 0.10, 0.20, 0.20, 0.20, 0.10, 0.07])
    weights = weights / weights.sum()

    avg_frac_current  = np.dot(weights, fracs_current)
    avg_frac_platform = np.dot(weights, fracs_platform)

    # Effective yeomen fractions
    # These are fractions of TOTAL automatable-sector income — so scale down
    # by the structural maximum (not all work is fungible)
    eff_current_know  = structural_max_know * avg_frac_current
    eff_platform_know = structural_max_know * avg_frac_platform

    results = {
        "structural_max_knowledge":      structural_max_know,
        "structural_max_physical":       structural_max_phys,
        "avg_fraction_worth_outsourcing_current":  avg_frac_current,
        "avg_fraction_worth_outsourcing_platform": avg_frac_platform,
        "effective_yeomen_knowledge_current":      eff_current_know,
        "effective_yeomen_knowledge_platform":     eff_platform_know,
        "platform_uplift_vs_current":              (eff_platform_know - eff_current_know) / eff_current_know,
        "suppression_vs_structural_current":       1 - (eff_current_know / structural_max_know),
        "suppression_vs_structural_platform":      1 - (eff_platform_know / structural_max_know),
    }

    return results, durations, fracs_current, fracs_platform


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_all():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Yeomen Outsourcing Overhead Analysis", fontsize=14, fontweight="bold")

    salary = 120_000

    # ── Panel 1: Cost vs engagement duration (knowledge work) ────────────────
    ax = axes[0, 0]
    months, w2, cur, plt_, be_cur, be_plt = cost_vs_duration(salary, "knowledge", "medium", "hybrid")
    ax.plot(months, [x/1000 for x in w2],  "k-",  linewidth=2, label="W-2 employee")
    ax.plot(months, [x/1000 for x in cur], "r-",  linewidth=2, label="Yeoman / private platform (current)")
    ax.plot(months, [x/1000 for x in plt_],"g-",  linewidth=2, label="Yeoman / govt platform (proposed)")
    if be_cur:
        ax.axvline(be_cur,  color="r", linestyle="--", alpha=0.5, label=f"Break-even current: {be_cur}mo")
    if be_plt:
        ax.axvline(be_plt,  color="g", linestyle="--", alpha=0.5, label=f"Break-even platform: {be_plt}mo")
    ax.set_xlabel("Engagement duration (months)")
    ax.set_ylabel("Total buyer cost ($k)")
    ax.set_title(f"Knowledge work — $120k equivalent salary\n(hybrid office, medium onboarding complexity)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── Panel 2: Cost vs engagement duration (physical work) ─────────────────
    ax = axes[0, 1]
    months, w2p, cur_p, plt_p, be_cur_p, be_plt_p = cost_vs_duration(60_000, "physical", "low", "office")
    ax.plot(months, [x/1000 for x in w2p],   "k-",  linewidth=2, label="W-2 employee")
    ax.plot(months, [x/1000 for x in cur_p], "r-",  linewidth=2, label="Yeoman / private platform")
    ax.plot(months, [x/1000 for x in plt_p], "g-",  linewidth=2, label="Yeoman / govt platform")
    if be_cur_p:
        ax.axvline(be_cur_p, color="r", linestyle="--", alpha=0.5, label=f"Break-even current: {be_cur_p}mo")
    if be_plt_p:
        ax.axvline(be_plt_p, color="g", linestyle="--", alpha=0.5, label=f"Break-even platform: {be_plt_p}mo")
    ax.set_xlabel("Engagement duration (months)")
    ax.set_ylabel("Total buyer cost ($k)")
    ax.set_title("Physical work — $60k equivalent salary\n(in-office, low onboarding complexity)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── Panel 3: Overhead component breakdown (12-month engagement) ──────────
    ax = axes[1, 0]
    w2_bd, cur_bd, plt_bd = overhead_breakdown(salary)

    # Map to comparable categories
    categories = ["Rate\n(inc. platform take)", "Per-engagement\nfixed costs", "QA +\ncoordination", "Risk\n(misclass)"]

    w2_vals = [
        w2_bd["base_salary"] + w2_bd["fica"] + w2_bd["workers_comp"] + w2_bd["unemp_ins"] +
        w2_bd["401k_match"] + w2_bd["health_dental_vis"] + w2_bd["pto_nonprod"],
        w2_bd["hr_admin"] + w2_bd["equip_it"] + w2_bd["training"] + w2_bd["office"],
        w2_bd["mgmt_overhead"],
        0,
    ]
    cur_vals = [
        cur_bd["engagement_rate_inc_platform_take"],
        cur_bd["discovery_search"] + cur_bd["contracting_legal"] + cur_bd["onboarding_knowledge_transfer"],
        cur_bd["qa_review_overhead"] + cur_bd["coordination_premium"],
        cur_bd["misclassification_risk"],
    ]
    plt_vals = [
        plt_bd["engagement_rate_no_platform_take"],
        plt_bd["discovery_search"] + plt_bd["contracting_standard_modules"] + plt_bd["onboarding_knowledge_transfer"],
        plt_bd["qa_review_overhead"] + plt_bd["coordination_premium"],
        plt_bd["misclassification_risk"],
    ]

    x = np.arange(len(categories))
    width = 0.25
    bars_w2  = ax.bar(x - width, [v/1000 for v in w2_vals],  width, label="W-2",             color="steelblue")
    bars_cur = ax.bar(x,         [v/1000 for v in cur_vals],  width, label="Yeoman (current)", color="tomato")
    bars_plt = ax.bar(x + width, [v/1000 for v in plt_vals],  width, label="Yeoman (platform)", color="seagreen")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel("Annual cost ($k, 12-month engagement)")
    ax.set_title("Cost component breakdown\n$120k knowledge worker equivalent")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # Totals above bars
    for bars, vals in [(bars_w2, w2_vals), (bars_cur, cur_vals), (bars_plt, plt_vals)]:
        pass  # totals added in table below

    # Add total annotations
    for regime, total, color in [
        ("W-2 total", sum(w2_vals)/1000, "steelblue"),
        ("Yeoman current", sum(cur_vals)/1000, "tomato"),
        ("Yeoman platform", sum(plt_vals)/1000, "seagreen"),
    ]:
        ax.annotate(f"{regime}: ${total:.0f}k", xy=(0.02, 0.97 - [0.06, 0.12, 0.18][["W-2 total","Yeoman current","Yeoman platform"].index(regime)]),
                    xycoords="axes fraction", fontsize=8, color=color, fontweight="bold")

    # ── Panel 4: Effective yeomen fraction suppression ───────────────────────
    ax = axes[1, 1]
    results, durations, fracs_cur, fracs_plt = effective_yeomen_suppression()

    ax.plot(durations, fracs_cur, "ro-", linewidth=2, label="Current (private platform)")
    ax.plot(durations, fracs_plt, "go-", linewidth=2, label="Govt platform")
    ax.axhline(results["structural_max_knowledge"], color="k", linestyle="--",
               alpha=0.5, label=f"Structural max ({results['structural_max_knowledge']:.0%})")
    ax.fill_between(durations, fracs_cur, fracs_plt, alpha=0.15, color="green",
                    label="Platform benefit")

    ax.set_xlabel("Engagement duration (months)")
    ax.set_ylabel("Fraction of fungible work worth outsourcing")
    ax.set_title("Effective outsourcing rate by engagement length\n(fraction of structurally fungible tasks)")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig("yeomen_overhead.png", dpi=150, bbox_inches="tight")
    print("  Saved: yeomen_overhead.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*72)
    print("YEOMEN OUTSOURCING OVERHEAD ANALYSIS")
    print("="*72)

    salary_k = 120_000
    salary_p = 60_000

    # --- Knowledge work ---
    months, w2, cur, plt_, be_cur, be_plt = cost_vs_duration(salary_k, "knowledge", "medium", "hybrid")
    print(f"\n{'─'*50}")
    print(f"KNOWLEDGE WORK  |  $120k W-2 equivalent  |  hybrid office  |  medium onboarding")
    print(f"{'─'*50}")
    for label, regime, be in [("Current (private platform)", cur, be_cur), ("Govt platform", plt_, be_plt)]:
        print(f"\n  {label}:")
        for m in [1, 3, 6, 12, 24]:
            idx = m - 1
            w2_cost = w2[idx]
            y_cost  = regime[idx]
            delta_pct = (y_cost - w2_cost) / w2_cost * 100
            symbol = "↑" if delta_pct > 0 else "↓"
            print(f"    {m:2d}mo  →  yeoman ${y_cost/1000:6.1f}k  vs  W-2 ${w2_cost/1000:6.1f}k  ({symbol}{abs(delta_pct):.0f}%)")
        if be:
            print(f"  Break-even (yeoman becomes more expensive): {be} months")
        else:
            print("  Yeoman is cheaper at all durations tested")

    # --- Physical work ---
    months_p, w2p, cur_p, plt_p, be_cur_p, be_plt_p = cost_vs_duration(salary_p, "physical", "low", "office")
    print(f"\n{'─'*50}")
    print(f"PHYSICAL WORK  |  $60k W-2 equivalent  |  in-office  |  low onboarding")
    print(f"{'─'*50}")
    for label, regime, be in [("Current (private platform)", cur_p, be_cur_p), ("Govt platform", plt_p, be_plt_p)]:
        print(f"\n  {label}:")
        for m in [1, 3, 6, 12, 24]:
            idx = m - 1
            w2_cost = w2p[idx]
            y_cost  = regime[idx]
            delta_pct = (y_cost - w2_cost) / w2_cost * 100
            symbol = "↑" if delta_pct > 0 else "↓"
            print(f"    {m:2d}mo  →  yeoman ${y_cost/1000:6.1f}k  vs  W-2 ${w2_cost/1000:6.1f}k  ({symbol}{abs(delta_pct):.0f}%)")
        if be:
            print(f"  Break-even: {be} months")
        else:
            print("  Yeoman cheaper at all durations")

    # --- Overhead breakdown ---
    print(f"\n{'─'*50}")
    print("COMPONENT BREAKDOWN  |  $120k  |  12-month engagement")
    print(f"{'─'*50}")
    w2_bd, cur_bd, plt_bd = overhead_breakdown(salary_k)
    headers = ["Component", "W-2", "Yeoman (current)", "Yeoman (platform)"]
    rows = []
    for label, key_w2, key_cur, key_plt in [
        ("Base rate + benefits",    "base_salary",                        "engagement_rate_inc_platform_take",  "engagement_rate_no_platform_take"),
        ("Fixed engagement costs",  None,                                  None,                                  None),
        ("QA + coordination",       "mgmt_overhead",                       None,                                  None),
        ("Misclassification risk",  None,                                  "misclassification_risk",              "misclassification_risk"),
    ]:
        pass  # detailed table printed below

    fmt = "{:<32} {:>10} {:>18} {:>18}"
    print(fmt.format(*headers))
    print("─" * 80)

    def row(label, w2v, curv, pltv):
        print(fmt.format(label, f"${w2v/1000:.1f}k", f"${curv/1000:.1f}k", f"${pltv/1000:.1f}k"))

    row("Base rate (incl. platform take)",
        w2_bd["base_salary"] + w2_bd["fica"] + w2_bd["workers_comp"] +
        w2_bd["unemp_ins"] + w2_bd["401k_match"] + w2_bd["health_dental_vis"] + w2_bd["pto_nonprod"],
        cur_bd["engagement_rate_inc_platform_take"],
        plt_bd["engagement_rate_no_platform_take"])

    row("Fixed per-engagement costs",
        w2_bd["hr_admin"] + w2_bd["equip_it"] + w2_bd["training"] + w2_bd["office"],
        cur_bd["discovery_search"] + cur_bd["contracting_legal"] + cur_bd["onboarding_knowledge_transfer"],
        plt_bd["discovery_search"] + plt_bd["contracting_standard_modules"] + plt_bd["onboarding_knowledge_transfer"])

    row("QA + coordination overhead",
        w2_bd["mgmt_overhead"],
        cur_bd["qa_review_overhead"] + cur_bd["coordination_premium"],
        plt_bd["qa_review_overhead"] + plt_bd["coordination_premium"])

    row("Misclassification risk",
        0,
        cur_bd["misclassification_risk"],
        plt_bd["misclassification_risk"])

    print("─" * 80)
    row("TOTAL (12 months)",
        w2_bd["total"],
        cur_bd["total"],
        plt_bd["total"])

    cur_vs_w2  = (cur_bd["total"] - w2_bd["total"]) / w2_bd["total"] * 100
    plt_vs_w2  = (plt_bd["total"] - w2_bd["total"]) / w2_bd["total"] * 100
    print(f"\n  Current platform overhead vs W-2:   {cur_vs_w2:+.0f}%")
    print(f"  Govt platform overhead vs W-2:      {plt_vs_w2:+.0f}%")

    # --- Effective yeomen fraction ---
    print(f"\n{'─'*50}")
    print("EFFECTIVE YEOMEN FRACTION (macro model implications)")
    print(f"{'─'*50}")
    results, dur, fc, fp = effective_yeomen_suppression()
    print(f"""
  Structural maximum (tech-feasible fungible work):
    Knowledge work:   {results['structural_max_knowledge']:.0%}
    Physical work:    {results['structural_max_physical']:.0%}

  Avg fraction worth outsourcing (weighted by duration distribution):
    Current platform:  {results['avg_fraction_worth_outsourcing_current']:.0%}
    Govt platform:     {results['avg_fraction_worth_outsourcing_platform']:.0%}

  Effective yeomen fraction (knowledge work):
    Current platform:  {results['effective_yeomen_knowledge_current']:.0%}
    Govt platform:     {results['effective_yeomen_knowledge_platform']:.0%}
    Structural max:    {results['structural_max_knowledge']:.0%}

  Transaction cost suppression vs structural max:
    Current: {results['suppression_vs_structural_current']:.0%} below structural max
    Platform: {results['suppression_vs_structural_platform']:.0%} below structural max

  Implication for model:
    The model's 'Fast / High yeomen' scenario targets yeomen_frac = 0.60.
    Without platform, transaction costs mean the achievable effective rate
    is ~{results['effective_yeomen_knowledge_current']:.0%} of what's structurally possible —
    suppressing yeomen_frac by ~{results['suppression_vs_structural_current']:.0%}.
    Platform reduces suppression to ~{results['suppression_vs_structural_platform']:.0%}.
    Platform effectively enables ~{results['platform_uplift_vs_current']:.0%} more effective
    outsourcing vs current state — a significant distributional change.
    """)

    print("Generating charts...")
    plot_all()
    print("="*72 + "\n")


if __name__ == "__main__":
    main()
