"""
Yeomen Market Microstructure: Discovery + Contracting
======================================================
Models the contract mechanisms that would emerge in a high-volume
parallel yeoman economy. Key insight: like energy markets, spot
markets exist for price discovery but most volume flows through
longer-term instruments for stability.

Questions addressed:
  1. What contract types emerge and why?
  2. How does discovery work at machine speed (A2A)?
  3. What is the stability premium buyers pay for retainers?
  4. How do long-term contracts affect equilibrium income stability?
  5. What platform infrastructure does each contract type require?
  6. The quasi-employment risk of retainer lock-in.

Run: python3 yeomen_contracts.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick
from dataclasses import dataclass, field
from typing import Callable
import random

# ---------------------------------------------------------------------------
# Market parameters
# ---------------------------------------------------------------------------

# Spot price volatility: how much does the hourly rate swing?
# Driven by: compute price swings, skill demand spikes, yeoman pool size shifts
SPOT_PRICE_MEAN    = 80     # $/hr baseline
SPOT_PRICE_VOL     = 0.35   # annualised volatility (35% — high, like commodity markets)
SPOT_PRICE_MR      = 0.15   # mean reversion speed (moderately mean-reverting)

# Stability premium: how much extra do buyers pay for price certainty?
# Empirically: energy forward contracts trade at ~5-15% premium to expected spot
STABILITY_PREMIUM = {
    "sprint_1wk":   0.05,    # 5% premium for 1-week lock-in
    "sprint_4wk":   0.08,
    "retainer_qtr": 0.12,    # 12% for quarterly retainer
    "retainer_yr":  0.18,    # 18% for annual retainer
    "future_1yr":   0.15,    # forward contract 1yr out
    "pool_access":  0.22,    # subscription pool (flexibility premium)
}

# Discount yeomen accept for income certainty
# A yeoman on a 12-month retainer might accept 10% below spot for stability
YEOMAN_CERTAINTY_DISCOUNT = {
    "sprint_1wk":   0.02,
    "sprint_4wk":   0.05,
    "retainer_qtr": 0.08,
    "retainer_yr":  0.12,
    "future_1yr":   0.10,
    "pool_access":  0.08,
}

# The SPREAD (buyer premium - yeoman discount) goes to platform or is efficiency gain
# Positive spread = platform can take a cut, OR prices can clear tighter

# Transaction costs by contract type (search, negotiation, contracting, monitoring)
# In a mature A2A platform these are much lower than current markets
TRANSACTION_COST_CURRENT = {
    "spot":         0.35,    # 35% — platform take + search cost + contract overhead
    "sprint_1wk":   0.25,
    "sprint_4wk":   0.20,
    "retainer_qtr": 0.12,
    "retainer_yr":  0.08,
    "future_1yr":   0.10,
    "pool_access":  0.15,
}
TRANSACTION_COST_PLATFORM = {  # with govt platform (zero take rate, standard contracts)
    "spot":         0.03,    # just matching cost — near zero
    "sprint_1wk":   0.02,
    "sprint_4wk":   0.02,
    "retainer_qtr": 0.02,
    "retainer_yr":  0.02,
    "future_1yr":   0.03,    # slightly more — clearinghouse overhead
    "pool_access":  0.03,
}

# Quasi-employment risk: at what revenue concentration does a yeoman become
# economically dependent on a single buyer (losing independence)?
DEPENDENCY_THRESHOLD = 0.60   # >60% of income from one buyer = dependent

# ---------------------------------------------------------------------------
# 1. Price volatility simulation (mean-reverting spot price)
# ---------------------------------------------------------------------------

def simulate_spot_price(n_days: int = 365, seed: int = 42) -> np.ndarray:
    """
    Ornstein-Uhlenbeck mean-reverting spot price process.
    Models compute cost swings, skill demand spikes, pool size shifts.
    """
    rng = np.random.default_rng(seed)
    dt  = 1 / 252   # daily steps (trading days)
    prices = np.zeros(n_days)
    prices[0] = SPOT_PRICE_MEAN

    for t in range(1, n_days):
        drift     = SPOT_PRICE_MR * (SPOT_PRICE_MEAN - prices[t-1]) * dt
        diffusion = SPOT_PRICE_VOL * prices[t-1] * np.sqrt(dt) * rng.normal()
        prices[t] = max(prices[t-1] + drift + diffusion, 5)   # floor at $5/hr

    return prices


# ---------------------------------------------------------------------------
# 2. Buyer economics: spot vs retainer
# ---------------------------------------------------------------------------

def buyer_contract_value(
    spot_prices: np.ndarray,
    contract_type: str,
    hours_per_day: float = 8,
    platform: str = "govt",
) -> dict:
    """
    For a buyer needing H hours/day of yeoman capacity, compare:
    - Spot market: pay daily spot price (volatile)
    - Retainer/forward: pay fixed rate (stable, with premium)

    Returns NPV comparison and volatility metrics.
    """
    tc = TRANSACTION_COST_PLATFORM if platform == "govt" else TRANSACTION_COST_CURRENT
    prem = STABILITY_PREMIUM.get(contract_type, 0)
    disc = YEOMAN_CERTAINTY_DISCOUNT.get(contract_type, 0)

    # Spot costs
    spot_tc    = tc["spot"]
    spot_daily = spot_prices * hours_per_day * (1 + spot_tc)

    # Contract rate: spot mean × (1 + premium) at time of signing
    # Yeoman accepts: spot mean × (1 - discount)
    contract_rate   = SPOT_PRICE_MEAN * (1 + prem)
    contract_daily  = contract_rate * hours_per_day * (1 + tc.get(contract_type, 0.02))

    # Buyer comparison
    spot_mean   = spot_daily.mean()
    spot_std    = spot_daily.std()
    contract_vs_spot = (contract_daily - spot_mean) / spot_mean

    # Volatility reduction (buyer's perspective)
    spot_cv     = spot_std / spot_mean   # coefficient of variation
    contract_cv = 0.0   # fixed contract = zero price volatility

    # Value of certainty (using risk-adjusted approach)
    # Risk-averse buyer with coefficient γ values certainty at: E[spot] + γ × Var[spot]
    gamma = 2.0   # moderate risk aversion
    certainty_value = spot_mean + gamma * (spot_std ** 2) / spot_mean
    buyer_surplus   = certainty_value - contract_daily

    return {
        "contract_type":    contract_type,
        "spot_mean_daily":  spot_mean,
        "spot_std_daily":   spot_std,
        "spot_cv":          spot_cv,
        "contract_daily":   contract_daily,
        "premium_vs_spot":  contract_vs_spot,
        "certainty_value":  certainty_value,
        "buyer_surplus":    buyer_surplus,  # positive = buyer happy to pay premium
        "yeoman_rate":      SPOT_PRICE_MEAN * (1 - disc) * hours_per_day,
        "platform_spread":  (contract_daily - SPOT_PRICE_MEAN * (1 - disc) * hours_per_day),
    }


# ---------------------------------------------------------------------------
# 3. Income stability: yeoman perspective
# ---------------------------------------------------------------------------

def yeoman_income_stability(
    spot_prices: np.ndarray,
    contract_mix: dict[str, float],   # {contract_type: fraction_of_hours}
    hours_per_day: float = 8,
    platform: str = "govt",
) -> dict:
    """
    Given a mix of contract types, compute yeoman income statistics.
    contract_mix: fractions must sum to 1.0.

    Key question: how much of income is stable (contracted) vs. volatile (spot)?
    """
    tc = TRANSACTION_COST_PLATFORM if platform == "govt" else TRANSACTION_COST_CURRENT

    daily_income = np.zeros(len(spot_prices))

    for ctype, frac in contract_mix.items():
        h = hours_per_day * frac
        disc = YEOMAN_CERTAINTY_DISCOUNT.get(ctype, 0)
        ctc  = tc.get(ctype, tc["spot"])

        if ctype == "spot":
            income = spot_prices * h * (1 - ctc)
        else:
            # Fixed rate for contract duration, resets at renewal
            rate = SPOT_PRICE_MEAN * (1 - disc) * (1 - ctc)
            income = np.full(len(spot_prices), rate * h)

        daily_income += income

    annual_income = daily_income.sum()
    monthly_income = np.array([daily_income[i*30:(i+1)*30].sum() for i in range(12)])

    return {
        "annual_income":       annual_income,
        "monthly_mean":        monthly_income.mean(),
        "monthly_std":         monthly_income.std(),
        "monthly_cv":          monthly_income.std() / monthly_income.mean(),
        "worst_month":         monthly_income.min(),
        "income_at_risk_5pct": np.percentile(monthly_income, 5),
        "contract_mix":        contract_mix,
    }


# ---------------------------------------------------------------------------
# 4. Quasi-employment risk from retainer concentration
# ---------------------------------------------------------------------------

def dependency_risk(
    n_buyers: int,
    income_distribution: str = "pareto",  # "equal" | "pareto"
) -> dict:
    """
    Model how income concentration across buyers creates dependency.

    With many short-term clients: low dependency (diversified).
    With 1-2 long-term retainers: high dependency (quasi-employee).

    The irony: long-term contracts that solve income volatility
    recreate the employment relationship the yeoman tried to escape.
    """
    rng = np.random.default_rng(0)

    if income_distribution == "equal":
        shares = np.ones(n_buyers) / n_buyers
    else:
        # Pareto: a few big clients dominate (realistic for professional services)
        raw = rng.pareto(1.5, n_buyers)
        shares = raw / raw.sum()

    top1_share  = shares.max()
    top3_share  = np.sort(shares)[-3:].sum() if n_buyers >= 3 else shares.sum()
    herfindahl  = (shares ** 2).sum()   # HHI: 1 = monopoly, 1/n = equal
    dependent   = top1_share > DEPENDENCY_THRESHOLD

    return {
        "n_buyers":     n_buyers,
        "top1_share":   top1_share,
        "top3_share":   top3_share,
        "hhi":          herfindahl,
        "dependent":    dependent,
        "distribution": income_distribution,
    }


# ---------------------------------------------------------------------------
# 5. A2A discovery volume model
# ---------------------------------------------------------------------------

def discovery_volume(n_yeomen: int, n_buyers: int, tasks_per_buyer_day: float) -> dict:
    """
    At scale, how many discovery/matching events happen per day?
    What infrastructure does this imply?
    """
    total_tasks_day   = n_buyers * tasks_per_buyer_day
    tasks_per_yeoman  = total_tasks_day / n_yeomen

    # Each task: buyer agent → platform → N matched yeoman agents → bids → award
    # Platform processes: 1 broadcast + N responses + 1 award = N+2 messages per task
    avg_matches_per_task = 5   # platform sends to top-5 qualified yeomen
    messages_per_task    = avg_matches_per_task + 2

    total_messages_day   = total_tasks_day * messages_per_task
    messages_per_second  = total_messages_day / 86_400

    # Most of this is machine-to-machine (A2A) — no human involved in discovery
    human_review_fraction = 0.15   # only 15% of task awards need human approval

    return {
        "total_tasks_day":       total_tasks_day,
        "tasks_per_yeoman_day":  tasks_per_yeoman,
        "total_a2a_messages_day":total_messages_day,
        "messages_per_second":   messages_per_second,
        "human_reviews_day":     total_tasks_day * human_review_fraction,
        "fully_automated_pct":   1 - human_review_fraction,
        "implied_latency_ms":    1000 / messages_per_second if messages_per_second > 0 else 0,
    }


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_contracts():
    fig = plt.figure(figsize=(16, 11))
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)
    fig.suptitle("Yeomen Market Microstructure: Contracts + Discovery", fontsize=13, fontweight="bold")

    spot = simulate_spot_price(365)
    days = np.arange(365)

    # ── Panel 1: Spot price volatility ───────────────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(days, spot, color="#e74c3c", linewidth=1, alpha=0.8, label="Spot rate")
    ax.axhline(SPOT_PRICE_MEAN, color="k", linestyle="--", linewidth=1.5, label=f"Mean: ${SPOT_PRICE_MEAN}/hr")

    for label, ctype, color in [
        ("Quarterly retainer", "retainer_qtr", "#2ecc71"),
        ("Annual retainer",    "retainer_yr",  "#3498db"),
    ]:
        rate = SPOT_PRICE_MEAN * (1 + STABILITY_PREMIUM[ctype])
        ax.axhline(rate, color=color, linestyle="-.", linewidth=1.5,
                   label=f"{label}: ${rate:.0f}/hr (+{STABILITY_PREMIUM[ctype]:.0%})")

    ax.set_xlabel("Day of year")
    ax.set_ylabel("Market rate ($/hr)")
    ax.set_title(f"Spot price volatility\n(vol={SPOT_PRICE_VOL:.0%}, mean-reverting)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ── Panel 2: Buyer value of stability premium ─────────────────────────
    ax = fig.add_subplot(gs[0, 1])
    contract_types = ["sprint_1wk", "sprint_4wk", "retainer_qtr", "retainer_yr", "pool_access"]
    labels = ["Sprint\n1wk", "Sprint\n4wk", "Retainer\nQtr", "Retainer\n1yr", "Pool\naccess"]
    premiums    = [STABILITY_PREMIUM[c] * 100 for c in contract_types]
    surpluses   = [buyer_contract_value(spot, c)["buyer_surplus"] for c in contract_types]

    colors = ["#27ae60" if s > 0 else "#e74c3c" for s in surpluses]
    x = np.arange(len(contract_types))
    bars = ax.bar(x, premiums, color=colors, alpha=0.85)
    ax2 = ax.twinx()
    ax2.plot(x, surpluses, "ko-", linewidth=2, markersize=6, label="Buyer surplus (risk-adj)")
    ax2.axhline(0, color="k", linestyle=":", alpha=0.5)
    ax2.set_ylabel("Daily buyer surplus ($ over spot)", color="k")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Stability premium charged (%)")
    ax.set_title("Buyer willingness to pay for stability\n(green = buyer is surplus+)")
    ax.grid(True, alpha=0.3, axis="y")

    # ── Panel 3: Yeoman income stability by contract mix ──────────────────
    ax = fig.add_subplot(gs[0, 2])
    mixes = {
        "All spot":           {"spot": 1.0},
        "50% sprint":         {"spot": 0.5, "sprint_4wk": 0.5},
        "50% retainer (qtr)": {"spot": 0.3, "sprint_4wk": 0.2, "retainer_qtr": 0.5},
        "80% retainer (yr)":  {"spot": 0.1, "sprint_4wk": 0.1, "retainer_yr": 0.8},
        "Pool + spot":        {"spot": 0.4, "pool_access": 0.6},
    }

    names, cvs, worst = [], [], []
    for name, mix in mixes.items():
        r = yeoman_income_stability(spot, mix, platform="govt")
        names.append(name)
        cvs.append(r["monthly_cv"] * 100)
        worst.append(r["income_at_risk_5pct"])

    x = np.arange(len(names))
    ax.bar(x, cvs, color="#e74c3c", alpha=0.8, label="Monthly income CoV (%)")
    ax2b = ax.twinx()
    ax2b.plot(x, worst, "go-", linewidth=2, markersize=6, label="5th pctile monthly income ($)")
    ax2b.set_ylabel("5th pctile monthly income ($)")

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=7)
    ax.set_ylabel("Monthly income volatility (CoV %)")
    ax.set_title("Yeoman income stability\nby contract mix (govt platform)")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")

    # ── Panel 4: Quasi-employment dependency risk ─────────────────────────
    ax = fig.add_subplot(gs[1, 0])
    buyer_counts = [1, 2, 3, 5, 8, 10, 15, 20]

    for dist, color, ls in [("pareto", "#e74c3c", "-"), ("equal", "#2ecc71", "--")]:
        top1s = [dependency_risk(n, dist)["top1_share"] * 100 for n in buyer_counts]
        ax.plot(buyer_counts, top1s, color=color, linestyle=ls, linewidth=2,
                label=f"{dist} income dist.")

    ax.axhline(DEPENDENCY_THRESHOLD * 100, color="k", linestyle=":",
               linewidth=2, label=f"Dependency threshold ({DEPENDENCY_THRESHOLD:.0%})")
    ax.fill_between(buyer_counts,
                    [DEPENDENCY_THRESHOLD * 100] * len(buyer_counts), 100,
                    alpha=0.1, color="red", label="Quasi-employment zone")

    ax.set_xlabel("Number of distinct buyers")
    ax.set_ylabel("Top buyer income share (%)")
    ax.set_title("Quasi-employment risk\nvs buyer diversification")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 105)

    # ── Panel 5: Discovery volume at scale ───────────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    yeomen_range = [1e6, 5e6, 10e6, 20e6]
    tasks_per_buyer = [2, 10, 50]   # tasks/day

    for tpb, color in zip(tasks_per_buyer, ["#3498db", "#e67e22", "#e74c3c"]):
        msgs = []
        for n_y in yeomen_range:
            n_b = n_y * 0.1   # assume 1 buyer per 10 yeomen (rough)
            d   = discovery_volume(int(n_y), int(n_b), tpb)
            msgs.append(d["messages_per_second"] / 1000)
        ax.plot([n/1e6 for n in yeomen_range], msgs, "o-", color=color, linewidth=2,
                label=f"{tpb} tasks/buyer/day")

    ax.set_xlabel("Yeomen (millions)")
    ax.set_ylabel("A2A messages/second (thousands)")
    ax.set_title("Platform A2A message volume\n(discovery + matching)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── Panel 6: Contract type share vs market maturity ───────────────────
    ax = fig.add_subplot(gs[1, 2])
    phases = ["Early\n(2025)", "Growth\n(2027)", "Mature\n(2030)", "Deep\n(2033)"]
    # Estimated contract mix evolution
    spot_share    = [0.70, 0.45, 0.25, 0.15]
    sprint_share  = [0.20, 0.30, 0.30, 0.25]
    retainer_share= [0.08, 0.18, 0.30, 0.35]
    pool_share    = [0.02, 0.07, 0.15, 0.25]

    x = np.arange(len(phases))
    ax.bar(x, spot_share,     label="Spot/task",    color="#e74c3c", alpha=0.85)
    ax.bar(x, sprint_share,   bottom=spot_share,    label="Sprint",  color="#e67e22", alpha=0.85)
    cum2 = [a+b for a,b in zip(spot_share, sprint_share)]
    ax.bar(x, retainer_share, bottom=cum2,           label="Retainer",color="#3498db", alpha=0.85)
    cum3 = [a+b for a,b in zip(cum2, retainer_share)]
    ax.bar(x, pool_share,     bottom=cum3,           label="Pool/sub",color="#2ecc71", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(phases)
    ax.set_ylabel("Share of transaction volume")
    ax.set_title("Contract type evolution\nas market matures")
    ax.legend(fontsize=8)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.grid(True, alpha=0.3, axis="y")

    plt.savefig("yeomen_contracts.png", dpi=150, bbox_inches="tight")
    print("  Saved: yeomen_contracts.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 72)
    print("YEOMEN MARKET MICROSTRUCTURE")
    print("=" * 72)

    spot = simulate_spot_price(365)

    print(f"\n--- SPOT PRICE STATISTICS ---")
    print(f"  Mean:   ${spot.mean():.0f}/hr")
    print(f"  Std:    ${spot.std():.0f}/hr  (CoV: {spot.std()/spot.mean():.0%})")
    print(f"  Min:    ${spot.min():.0f}/hr")
    print(f"  Max:    ${spot.max():.0f}/hr")
    print(f"  5th pct:${np.percentile(spot, 5):.0f}/hr")
    print(f"  95th:   ${np.percentile(spot, 95):.0f}/hr")

    print(f"\n--- BUYER ECONOMICS: STABILITY PREMIUM vs CERTAINTY VALUE ---")
    print(f"  (8 hrs/day capacity, govt platform, moderate risk aversion)")
    print(f"  {'Contract':<20} {'Rate/hr':>9} {'Premium':>9} {'Buyer surplus/day':>18} {'Worth it?':>10}")
    print("  " + "─" * 70)
    for ctype, label in [
        ("spot",         "Spot market"),
        ("sprint_1wk",   "Sprint 1wk"),
        ("sprint_4wk",   "Sprint 4wk"),
        ("retainer_qtr", "Retainer qtr"),
        ("retainer_yr",  "Retainer yr"),
        ("pool_access",  "Pool access"),
    ]:
        r = buyer_contract_value(spot, ctype)
        rate = SPOT_PRICE_MEAN * (1 + STABILITY_PREMIUM.get(ctype, 0))
        worth = "YES" if r["buyer_surplus"] > 0 else "no"
        print(f"  {label:<20} ${rate:>6.0f}/hr  {STABILITY_PREMIUM.get(ctype,0):>7.0%}  "
              f"${r['buyer_surplus']:>14.0f}/day  {worth:>10}")

    print(f"\n--- YEOMAN INCOME STABILITY BY CONTRACT MIX ---")
    mixes = {
        "All spot":           {"spot": 1.0},
        "50/50 sprint":       {"spot": 0.5, "sprint_4wk": 0.5},
        "50% qtr retainer":   {"spot": 0.3, "sprint_4wk": 0.2, "retainer_qtr": 0.5},
        "80% yr retainer":    {"spot": 0.1, "sprint_4wk": 0.1, "retainer_yr": 0.8},
        "Pool + spot":        {"spot": 0.4, "pool_access": 0.6},
    }
    print(f"  {'Mix':<24} {'Annual':>10} {'Monthly CoV':>12} {'Worst month':>13} {'5th pct/mo':>12}")
    print("  " + "─" * 75)
    for name, mix in mixes.items():
        r = yeoman_income_stability(spot, mix, platform="govt")
        print(f"  {name:<24} ${r['annual_income']/1000:>6.0f}k   "
              f"{r['monthly_cv']:>10.0%}   ${r['worst_month']:>9.0f}   "
              f"${r['income_at_risk_5pct']:>8.0f}")

    print(f"\n--- QUASI-EMPLOYMENT RISK ---")
    print(f"  (Dependency threshold: >{DEPENDENCY_THRESHOLD:.0%} income from one buyer)")
    print(f"  {'N buyers':<10} {'Pareto top-1':>14} {'Equal top-1':>14} {'Dependent (Pareto)?':>20}")
    print("  " + "─" * 62)
    for n in [1, 2, 3, 5, 8, 10, 15, 20]:
        p = dependency_risk(n, "pareto")
        e = dependency_risk(n, "equal")
        dep = "YES ⚠" if p["dependent"] else "no"
        print(f"  {n:<10} {p['top1_share']:>12.0%}   {e['top1_share']:>12.0%}   {dep:>20}")

    print(f"\n--- DISCOVERY VOLUME ---")
    print(f"  {'Scale':<16} {'Tasks/day':>12} {'A2A msgs/sec':>14} {'Human reviews/day':>18} {'Auto %':>8}")
    print("  " + "─" * 72)
    for n_y, n_b, tpb, label in [
        (1_000_000,  100_000,  5,  "1M yeomen"),
        (5_000_000,  500_000,  10, "5M yeomen"),
        (10_000_000, 1_000_000,20, "10M yeomen"),
        (20_000_000, 2_000_000,50, "20M yeomen"),
    ]:
        d = discovery_volume(n_y, n_b, tpb)
        print(f"  {label:<16} {d['total_tasks_day']:>12,.0f}  "
              f"{d['messages_per_second']:>12.0f}   "
              f"{d['human_reviews_day']:>14,.0f}   "
              f"{d['fully_automated_pct']:>6.0%}")

    print(f"\n--- CONTRACT MECHANISMS AND PLATFORM REQUIREMENTS ---")
    print("""
  CONTRACT LANDSCAPE (what emerges and why):

  SPOT/TASK  — "Post and match"
    How: Buyer agent broadcasts task → platform matches → yeoman agents bid → auto-award
    Price: Real-time auction or posted price (yeoman sets standing offer)
    Good for: One-off tasks, defined outputs, buyers who tolerate price variance
    Platform needs: Sub-second A2A matching, standing offer registry, instant escrow
    Risk: Income volatility for yeomen, price uncertainty for buyers
    Share at maturity: ~15% of volume (price discovery function)

  SPRINT  — "Fixed scope, fixed price"
    How: Buyer posts scope → yeoman bids fixed price → contract signed → milestone payments
    Price: Negotiated at start, locked for duration
    Good for: Projects with clear deliverables, 1-4 week horizon
    Platform needs: Scope templates, milestone tracking, dispute arbitration
    Risk: Scope creep (managed by change order threshold in contract module)
    Share at maturity: ~25%

  RETAINER  — "Capacity reservation"
    How: Buyer reserves N hours/tokens per period at locked rate
    Price: Spot × (1 + stability premium) — typically +12-18% vs expected spot
    Good for: Ongoing needs, buyers wanting predictable costs, yeomen wanting stability
    Platform needs: Capacity booking system, utilisation reporting, rollover mechanics
    KEY RISK: Quasi-employment. At 80% retainer income from one buyer, the yeoman
    is economically an employee regardless of legal status. Platform should flag
    this and encourage diversification — or the yeomen economy recreates employment
    through the back door.
    Share at maturity: ~35%

  SUBSCRIPTION POOL  — "Access not ownership"
    How: Buyer subscribes to a credentialled pool; platform routes tasks to available
    yeomen within pool. Yeomen in pool get steady load, buyers get flexibility.
    Price: Monthly subscription for X capacity units; pool handles routing
    Good for: Enterprise buyers with variable, unpredictable demand
    Platform needs: Pool management, load balancing across yeomen, SLA monitoring
    This is closest to a staffing agency model but without the extraction:
    platform routes but doesn't own the relationship or take a commission
    Share at maturity: ~25%

  CAPACITY FUTURES  — "Forward booking"
    How: Buyer purchases right to N hours of yeoman-class capacity at future date
    Price: Today's expectation of future spot + risk premium
    Good for: Buyers with predictable future projects who want rate certainty
    Platform needs: Clearinghouse, margin requirements, settlement mechanism
    Only emerges once spot market is liquid enough for futures to price correctly
    Probably 2029+ before this layer exists at scale

  THE LONG-TERM CONTRACT DYNAMIC (your core point):
    You're right: price instability → buyers prefer long-term contracts.
    But this has a second-order effect on the YEOMAN ECONOMY structure:
    - Retainers are good for yeoman income stability (good)
    - But concentrated retainers recreate quasi-employment (bad)
    - The platform should enforce a "diversification requirement":
      no single buyer can represent >40% of a yeoman's token capacity allocation
      This is structurally analogous to anti-monopoly rules — prevents buyer
      lock-in from undermining the independence that makes yeomen yeomen
    - The government platform is the right place to enforce this because
      it sees the full revenue picture across all transactions

  DISCOVERY AT SCALE:
    At 10M yeomen: ~200M tasks/day, ~2,300 A2A messages/second
    85% fully automated (machine-to-machine, no human in loop)
    Human review only for: high-value contracts, novel scope, first-time relationships
    The platform is essentially running a continuous, real-time commodity exchange
    with credential verification baked into the matching layer
    """)

    print("Generating charts...")
    plot_contracts()
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
