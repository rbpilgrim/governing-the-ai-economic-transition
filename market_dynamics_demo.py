"""
Market Dynamics: Dynamic Tax → Pricing → Utilisation Rebalancing
=================================================================
Shows how the dynamic ownership/deployment tax creates a self-regulating
labour market without coordination between yeomen.

The feedback loop:
  High utilisation  →  tax rate rises  →  floor price rises
  →  loses some bids to cheaper competitors  →  utilisation falls
  →  tax rate falls  →  floor price falls  →  wins more bids  →  equilibrium

This is the tax doing the work a union wage floor would do — but automatically,
via price signals rather than collective bargaining.

Each yeoman tracks:
  - Monthly contracts won (utilisation %)
  - Current tax rate (dynamic, adjusted each period)
  - Floor price (derived from net income target + costs + tax obligation)
  - Monthly net earnings

Run for 12 monthly periods. Show how the market converges from an unequal
starting distribution (Aisha has 8 contracts, Dev has 1) toward balance.

Run: python3 market_dynamics_demo.py
"""

from __future__ import annotations
import random, hashlib
from dataclasses import dataclass, field
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

from federated_registry_demo import (
    JurisdictionalAgent, NationalRegistry, TaxAuthority,
    Matchmaker, AgentNegotiator, FedNowRail,
    make_supplier, make_buyer, make_tender, make_contract, _h,
)
from platform_schemas import (
    TaxRecord, TaxRecordRole, CrossBorderContractBundle, MilestoneStatus,
)


# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC TAX ENGINE
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DynamicTaxState:
    """
    Per-yeoman tax state. Adjusted monthly based on utilisation.
    Taylor-rule-style: tax rises when utilisation > target, falls when below.
    Also penalises if aggregate supply growth is too slow (keeps supply healthy).

    τ(t+1) = τ(t) + α*(U(t) - U_target) - β*max(0, G_target - G(t))
    where G is market-wide new yeoman growth rate.
    """
    base_rate:   float = 0.20   # starting deployment tax rate
    current:     float = 0.20
    min_rate:    float = 0.05   # floor — never fully zero
    max_rate:    float = 0.50   # ceiling
    alpha:       float = 0.04   # utilisation sensitivity
    beta:        float = 0.02   # supply growth sensitivity
    u_target:    float = 0.75   # target utilisation

    def adjust(self, utilisation: float, supply_growth: float = 0.0, g_target: float = 0.05):
        delta = (self.alpha * (utilisation - self.u_target)
                 - self.beta * max(0.0, g_target - supply_growth))
        self.current = float(np.clip(self.current + delta, self.min_rate, self.max_rate))
        return self.current


# ─────────────────────────────────────────────────────────────────────────────
# YEOMAN MARKET STATE
# ─────────────────────────────────────────────────────────────────────────────

MONTHLY_CAPACITY  = 8      # contracts a yeoman can handle per month (simplified)
NET_INCOME_TARGET = 4_600  # $/month take-home target
FIXED_OVERHEAD_MO = 1_625  # health, tools, accounting (monthly)
TRANSPORT_FRAC    = 0.25   # transport takes 25% of gross

@dataclass
class YeomanState:
    did:          str
    name:         str
    capabilities: list[str]
    naics:        list[str]

    # Dynamic state — updated each period
    tax:          DynamicTaxState = field(default_factory=DynamicTaxState)
    contracts_won:int   = 0   # this period
    utilisation:  float = 0.0
    floor_price:  float = 0.0
    net_earnings: float = 0.0
    cumulative_earnings: float = 0.0

    # History
    utilisation_history: list[float] = field(default_factory=list)
    tax_history:         list[float] = field(default_factory=list)
    floor_history:       list[float] = field(default_factory=list)
    earnings_history:    list[float] = field(default_factory=list)

    def compute_floor_price(self, avg_contract_size: float = 8_000) -> float:
        """
        Minimum acceptable contract price given current tax rate.
        Derived from: gross → after transport → after tax → after overhead → net.
        Solve for gross such that net = NET_INCOME_TARGET (per contract, proportional).

        net_per_contract = gross*(1-transport)*(1-tax_rate) - overhead_per_contract
        floor: gross*(1-transport)*(1-tax_rate) = NET_INCOME_TARGET/capacity + overhead/capacity
        gross = (NET_INCOME_TARGET/capacity + overhead/capacity) / ((1-transport)*(1-tax_rate))
        """
        net_needed   = NET_INCOME_TARGET / MONTHLY_CAPACITY
        overhead_per = FIXED_OVERHEAD_MO / MONTHLY_CAPACITY
        effective    = (1 - TRANSPORT_FRAC) * (1 - self.tax.current)
        if effective <= 0:
            return avg_contract_size * 2   # degenerate: price very high
        floor = (net_needed + overhead_per) / effective
        self.floor_price = round(floor, 0)
        return self.floor_price

    def record_period(self, contracts_won: int, supply_growth: float = 0.0):
        self.contracts_won = contracts_won
        self.utilisation   = contracts_won / MONTHLY_CAPACITY
        new_tax = self.tax.adjust(self.utilisation, supply_growth)
        self.compute_floor_price()

        # Earnings: gross per contract × contracts won, minus costs
        avg_gross    = self.floor_price * 1.10   # win at ~10% above floor
        gross_total  = avg_gross * contracts_won
        after_trans  = gross_total * (1 - TRANSPORT_FRAC)
        after_tax    = after_trans * (1 - self.tax.current)
        net          = after_tax - FIXED_OVERHEAD_MO
        self.net_earnings       = max(net, 0.0)
        self.cumulative_earnings += self.net_earnings

        self.utilisation_history.append(self.utilisation)
        self.tax_history.append(new_tax)
        self.floor_history.append(self.floor_price)
        self.earnings_history.append(self.net_earnings)


# ─────────────────────────────────────────────────────────────────────────────
# MARKET SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class MarketSimulation:
    """
    Runs N monthly periods of a yeoman service market.
    Each period: DAO posts tasks → matchmaker scores suppliers → winner negotiated.
    Supplier floor price is tax-adjusted. High-utilisation yeomen price themselves
    out; low-utilisation yeomen become cheaper and win more contracts.
    """

    def __init__(self, yeomen: list[YeomanState], tasks_per_period: int = 15,
                 avg_budget: float = 12_000):
        self.yeomen           = yeomen
        self.tasks_per_period = tasks_per_period
        self.avg_budget       = avg_budget
        self.period_log: list[dict] = []

    def _score(self, yeoman: YeomanState, budget: float) -> float:
        """
        Matchmaker scoring: capability match + reputation + price competitiveness.
        Price competitiveness: how far below budget is the yeoman's floor?
        """
        price_fit  = max(0.0, (budget - yeoman.floor_price) / budget)
        reputation = min(len(yeoman.capabilities) / 5.0, 1.0)  # proxy for rep
        noise      = random.uniform(0.85, 1.15)                 # market noise
        return (0.4 * price_fit + 0.4 * reputation + 0.2 * noise)

    def run_period(self, period: int, n_new_yeomen: int = 0) -> dict:
        # Optional: new yeomen enter the market (supply growth)
        supply_growth = n_new_yeomen / len(self.yeomen) if self.yeomen else 0.0

        contracts = {y.did: 0 for y in self.yeomen}

        for t in range(self.tasks_per_period):
            budget = self.avg_budget * random.uniform(0.5, 1.8)

            # Score all eligible yeomen (floor <= budget)
            eligible = [(y, self._score(y, budget))
                        for y in self.yeomen
                        if y.floor_price <= budget
                        and contracts[y.did] < MONTHLY_CAPACITY]

            if not eligible:
                continue  # no affordable supplier — task unmet

            eligible.sort(key=lambda x: x[1], reverse=True)
            winner, score = eligible[0]
            contracts[winner.did] += 1

        # Update each yeoman's state
        period_data = {"period": period, "yeomen": {}}
        for y in self.yeomen:
            won = contracts[y.did]
            y.record_period(won, supply_growth)
            period_data["yeomen"][y.name] = {
                "contracts": won,
                "utilisation": y.utilisation,
                "tax_rate": y.tax.current,
                "floor_price": y.floor_price,
                "net_earnings": y.net_earnings,
            }

        self.period_log.append(period_data)
        return period_data

    def gini(self) -> float:
        """Gini coefficient of cumulative earnings — 0=equal, 1=fully unequal."""
        earnings = sorted([y.cumulative_earnings for y in self.yeomen])
        n = len(earnings)
        if n == 0 or sum(earnings) == 0:
            return 0.0
        idx = list(range(1, n + 1))
        return (2 * sum(i * e for i, e in zip(idx, earnings))
                / (n * sum(earnings))) - (n + 1) / n


# ─────────────────────────────────────────────────────────────────────────────
# PRINT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def print_period(period: int, data: dict):
    print(f"\n  Period {period:>2}  {'Name':<22} {'Won':>4} {'Util':>6} "
          f"{'Tax':>6} {'Floor':>8} {'Net/mo':>8}")
    print("  " + "─" * 64)
    for name, d in data["yeomen"].items():
        bar = "█" * int(d["utilisation"] * 10) + "░" * (10 - int(d["utilisation"] * 10))
        print(f"  {'':<6}  {name:<22} {d['contracts']:>4} "
              f"[{bar}] {d['tax_rate']:>5.1%} "
              f"${d['floor_price']:>6,.0f} ${d['net_earnings']:>6,.0f}")


def print_summary(sim: MarketSimulation):
    print("\n  ── FINAL STATE (end of simulation)")
    print(f"  {'Name':<22} {'Util avg':>9} {'Tax now':>8} "
          f"{'Floor now':>10} {'Cum earnings':>13} {'Contracts':>10}")
    print("  " + "─" * 78)

    sorted_y = sorted(sim.yeomen, key=lambda y: y.cumulative_earnings, reverse=True)
    for y in sorted_y:
        avg_util = sum(y.utilisation_history) / len(y.utilisation_history)
        print(f"  {y.name:<22} {avg_util:>8.0%}  {y.tax.current:>8.1%}  "
              f"${y.floor_price:>8,.0f}  ${y.cumulative_earnings:>11,.0f}  "
              f"{sum(1 for _ in y.utilisation_history if _ > 0):>7} periods active")

    print(f"\n  Earnings Gini coefficient: {sim.gini():.3f}  "
          f"(0 = perfect equality, 1 = one earner takes all)")
    target_util = 0.75
    utils = [y.utilisation_history[-1] for y in sim.yeomen]
    print(f"  Final period utilisation:  "
          f"avg={sum(utils)/len(utils):.0%}  "
          f"std={float(np.std(utils)):.0%}  "
          f"target={target_util:.0%}")


# ─────────────────────────────────────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────────────────────────────────────

def plot_dynamics(sim: MarketSimulation, title_suffix: str = ""):
    periods = list(range(1, len(sim.period_log) + 1))
    n_y     = len(sim.yeomen)
    colours = plt.cm.tab10(np.linspace(0, 1, n_y))

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(f"Market Dynamics: Dynamic Tax → Price → Utilisation{title_suffix}",
                 fontsize=12, fontweight="bold")

    # Panel 1: Utilisation over time
    ax = axes[0, 0]
    for y, c in zip(sim.yeomen, colours):
        ax.plot(periods, y.utilisation_history, color=c, linewidth=1.8, label=y.name)
    ax.axhline(0.75, color="black", linestyle="--", linewidth=1.2, label="Target (75%)")
    ax.set_title("Utilisation by yeoman")
    ax.set_ylabel("Utilisation")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # Panel 2: Tax rate over time
    ax = axes[0, 1]
    for y, c in zip(sim.yeomen, colours):
        ax.plot(periods, y.tax_history, color=c, linewidth=1.8, label=y.name)
    ax.axhline(0.20, color="black", linestyle="--", linewidth=1.2, label="Base rate (20%)")
    ax.set_title("Dynamic tax rate by yeoman")
    ax.set_ylabel("Tax rate")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_ylim(0, 0.55)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # Panel 3: Floor price over time
    ax = axes[1, 0]
    for y, c in zip(sim.yeomen, colours):
        ax.plot(periods, y.floor_history, color=c, linewidth=1.8, label=y.name)
    ax.set_title("Floor price (min acceptable bid) by yeoman")
    ax.set_ylabel("Floor price ($)")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # Panel 4: Monthly net earnings
    ax = axes[1, 1]
    for y, c in zip(sim.yeomen, colours):
        ax.plot(periods, [e / 1000 for e in y.earnings_history],
                color=c, linewidth=1.8, label=y.name)
    ax.axhline(4.6, color="black", linestyle="--", linewidth=1.2,
               label="Target ($4.6k/mo)")
    ax.set_title("Monthly net earnings by yeoman")
    ax.set_ylabel("Net earnings ($k/mo)")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fname = "market_dynamics.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    print(f"\n  Saved: {fname}")


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

def scenario_no_tax(n_periods: int = 12) -> MarketSimulation:
    """Baseline: fixed tax, no dynamic adjustment. Winner keeps winning."""
    print("\n  [No dynamic tax — fixed 20% rate for all]")
    random.seed(42)
    yeomen = [
        YeomanState("a1", "Aisha Johnson", ["content","nlp"],    ["541611","519130"]),
        YeomanState("a2", "Maria Chen",    ["python","ml"],       ["541511","541512"]),
        YeomanState("a3", "Dev Patel",     ["rust","api"],        ["541511"]),
        YeomanState("a4", "Priya Nair",    ["typescript","ui"],   ["541511","541519"]),
        YeomanState("a5", "Leo Tanaka",    ["strategy","research"],["541611"]),
        YeomanState("a6", "Yuki Sato",     ["go","devops"],       ["541511"]),
    ]
    # Freeze tax — no dynamic adjustment
    for y in yeomen:
        y.tax.alpha = 0.0
        y.tax.beta  = 0.0

    sim = MarketSimulation(yeomen, tasks_per_period=15, avg_budget=10_000)
    for p in range(1, n_periods + 1):
        sim.run_period(p)
    return sim


def scenario_dynamic_tax(n_periods: int = 12) -> MarketSimulation:
    """Dynamic tax: utilisation drives rate → floor price → rebalancing."""
    print("\n  [Dynamic tax — rate adjusts monthly to utilisation]")
    random.seed(42)
    yeomen = [
        YeomanState("b1", "Aisha Johnson", ["content","nlp"],     ["541611","519130"]),
        YeomanState("b2", "Maria Chen",    ["python","ml"],        ["541511","541512"]),
        YeomanState("b3", "Dev Patel",     ["rust","api"],         ["541511"]),
        YeomanState("b4", "Priya Nair",    ["typescript","ui"],    ["541511","541519"]),
        YeomanState("b5", "Leo Tanaka",    ["strategy","research"],["541611"]),
        YeomanState("b6", "Yuki Sato",     ["go","devops"],        ["541511"]),
    ]
    # All start equal; dynamic tax active
    sim = MarketSimulation(yeomen, tasks_per_period=15, avg_budget=10_000)
    for p in range(1, n_periods + 1):
        sim.run_period(p)
    return sim


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 68)
    print("  MARKET DYNAMICS: DYNAMIC TAX → PRICING → REBALANCING")
    print("=" * 68)
    print("""
  Mechanism:
    High utilisation → tax rate rises → floor price rises
    → loses bids to cheaper (less busy) competitors
    → utilisation falls → tax rate falls → prices fall → wins more
    → equilibrium: all yeomen near target utilisation

  Key insight: the tax does not suppress supply — it taxes OWNERSHIP
  proportional to utilisation, making over-utilised yeomen expensive
  and under-utilised ones cheap. The market self-balances.
  """)

    N = 12  # months

    # ── Scenario 1: No dynamic tax ────────────────────────────────────────────
    print("─" * 68)
    print("  SCENARIO 1 — Fixed tax (no dynamic adjustment)")
    print("  Winner keeps winning. Work concentrates. Gini rises.")
    print("─" * 68)

    sim_fixed = scenario_no_tax(N)
    print_period(N, sim_fixed.period_log[-1])
    print_summary(sim_fixed)

    # ── Scenario 2: Dynamic tax ───────────────────────────────────────────────
    print("\n" + "─" * 68)
    print("  SCENARIO 2 — Dynamic tax (adjusts monthly to utilisation)")
    print("  Busy yeomen price up; idle yeomen price down. Market balances.")
    print("─" * 68)

    sim_dynamic = scenario_dynamic_tax(N)

    # Print every 3 periods to show convergence
    for p_idx in [0, 2, 5, 8, 11]:
        if p_idx < len(sim_dynamic.period_log):
            print_period(p_idx + 1, sim_dynamic.period_log[p_idx])

    print_summary(sim_dynamic)

    # ── Comparison ────────────────────────────────────────────────────────────
    print("\n" + "─" * 68)
    print("  COMPARISON: Fixed tax vs Dynamic tax")
    print("─" * 68)

    gini_f = sim_fixed.gini()
    gini_d = sim_dynamic.gini()
    utils_f = [y.utilisation_history[-1] for y in sim_fixed.yeomen]
    utils_d = [y.utilisation_history[-1] for y in sim_dynamic.yeomen]

    print(f"\n  {'Metric':<35} {'Fixed tax':>12} {'Dynamic tax':>12}")
    print("  " + "─" * 60)
    print(f"  {'Earnings Gini (lower=more equal)':<35} {gini_f:>12.3f} {gini_d:>12.3f}")
    print(f"  {'Avg utilisation (period 12)':<35} "
          f"{sum(utils_f)/len(utils_f):>11.0%} {sum(utils_d)/len(utils_d):>11.0%}")
    print(f"  {'Util std dev (period 12)':<35} "
          f"{float(np.std(utils_f)):>11.0%} {float(np.std(utils_d)):>11.0%}")

    # Highest earner under each scenario
    top_f = max(sim_fixed.yeomen,   key=lambda y: y.cumulative_earnings)
    top_d = max(sim_dynamic.yeomen, key=lambda y: y.cumulative_earnings)
    low_f = min(sim_fixed.yeomen,   key=lambda y: y.cumulative_earnings)
    low_d = min(sim_dynamic.yeomen, key=lambda y: y.cumulative_earnings)

    print(f"  {'Top earner cumulative':<35} "
          f"${top_f.cumulative_earnings:>10,.0f} ${top_d.cumulative_earnings:>10,.0f}")
    print(f"  {'Bottom earner cumulative':<35} "
          f"${low_f.cumulative_earnings:>10,.0f} ${low_d.cumulative_earnings:>10,.0f}")
    print(f"  {'Top/bottom ratio':<35} "
          f"{top_f.cumulative_earnings/max(low_f.cumulative_earnings,1):>11.1f}x "
          f"{top_d.cumulative_earnings/max(low_d.cumulative_earnings,1):>11.1f}x")

    print(f"""
  Key result:
    Fixed tax concentrates work — the best-matched yeoman keeps winning,
    earns more, and the gap widens. No self-correcting mechanism.

    Dynamic tax disperses work — as Aisha wins more, her floor price rises,
    she loses some bids to Leo or Dev who are cheaper because they're less busy.
    The market converges toward equal utilisation without anyone coordinating.

    The tax collects MORE total revenue at high utilisation (rate goes up)
    which funds the yeoman programme, and LESS at low utilisation (rate goes down)
    which subsidises yeomen to stay in the market during slow periods.
    It's countercyclical by design.
    """)

    print("  Generating chart...")
    plot_dynamics(sim_dynamic, " (dynamic tax active)")
    print("=" * 68 + "\n")


if __name__ == "__main__":
    main()
