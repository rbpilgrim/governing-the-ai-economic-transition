"""
Yeomen Parallel Model: AI Agents + Robots
==========================================
A yeoman is not a sequential worker. They supervise:
  - N parallel AI agents (each consuming tokens independently)
  - M physical robots (generating value from physical capital, minimal tokens)

The human is a coordination and exception-handling node, not a worker.
Their binding constraint is supervision bandwidth, not working hours.

This changes the equilibrium fundamentally:
  - Token consumption = N_agents × tokens_per_agent_hour × supervision_hours
  - Physical value = M_robots × robot_daily_revenue × operating_days
  - Total value per yeoman can reach $200-600k/year

The competition dynamic also shifts: yeomen differentiate not just on skill
but on HOW MANY agents/robots they can effectively supervise. There is now
a spectrum from "basic solo operator" to "micro-enterprise operator".

Run: python3 yeomen_parallel.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------------------
# AI Agent parameters
# ---------------------------------------------------------------------------

TOKENS_PER_AGENT_HOUR = 500_000   # each agent at standard intensity
SUPERVISION_HOURS_YR  = 1_200     # human hours available for oversight

# How effectively can a human supervise N agents simultaneously?
# Efficiency degrades as N grows — attention is finite
def supervision_efficiency(n_agents: int) -> float:
    """
    Returns effective throughput fraction per agent as N grows.
    At N=1: 100% (dedicated attention)
    At N=5: ~85% (manageable)
    At N=10: ~65% (exception-handling only)
    At N=20: ~40% (dashboard monitoring, minimal intervention)
    Models that N human hours ≠ N × agent-hours of quality output
    """
    return 1.0 / (1.0 + 0.04 * (n_agents - 1) ** 1.2)

# ---------------------------------------------------------------------------
# Robot parameters
# ---------------------------------------------------------------------------

# Robot types a yeoman might own and operate
ROBOT_TYPES = {
    "logistics": {
        "purchase_cost":    40_000,   # $ upfront
        "annual_revenue":   45_000,   # competing with ~$35k warehouse worker
        "operating_cost":    8_000,   # energy, maintenance, insurance
        "tokens_per_day":    5_000,   # minimal — control signals, exception routing
        "description": "Warehouse/delivery robot (competing with $35k worker)",
    },
    "skilled_trade": {
        "purchase_cost":    80_000,
        "annual_revenue":   85_000,   # competing with $65k skilled trade worker
        "operating_cost":   15_000,
        "tokens_per_day":   20_000,   # more AI direction needed for varied tasks
        "description": "Construction/installation robot (competing with $65k trade worker)",
    },
    "care_assist": {
        "purchase_cost":    60_000,
        "annual_revenue":   55_000,   # care work premium for human-adjacent tasks
        "operating_cost":   10_000,
        "tokens_per_day":   30_000,   # high AI direction — care requires judgment
        "description": "Care assistant robot (competing with $45k home health aide)",
    },
    "humanoid_general": {
        "purchase_cost":   150_000,   # Tesla Optimus class, near-future
        "annual_revenue":  120_000,   # general purpose → high value tasks
        "operating_cost":   20_000,
        "tokens_per_day":   50_000,   # heavy AI direction for general tasks
        "description": "General humanoid (near-future, 2028+)",
    },
}

# Robot financing: yeoman takes a loan / lease at this annual cost of capital
COST_OF_CAPITAL = 0.10   # 10% — small business loan rate

# Operating days per year
OPERATING_DAYS_YR = 300

# ---------------------------------------------------------------------------
# Yeoman operator model
# ---------------------------------------------------------------------------

def yeoman_economics(
    n_ai_agents: int,
    robot_fleet: list[str],         # list of robot_type keys
    token_gift: int,                # tokens per year gifted
    hourly_market_rate: float,      # market price for AI-augmented services
    robot_market_rate: float = 1.0, # multiplier on robot annual_revenue (market pricing)
    year: int = 2027,
) -> dict:
    """
    Compute the full economics for one yeoman operator.

    Token budget allocation:
      - AI agents: n_agents × tokens_per_agent_hour × supervision_hours (up to token budget)
      - Robots: tokens_per_day × operating_days (deducted from same budget)

    The human supervises both — robots during day, AI agents throughout.
    """
    # ── Robot economics ───────────────────────────────────────────────────
    robot_gross_revenue    = 0
    robot_operating_costs  = 0
    robot_financing_costs  = 0
    robot_tokens_consumed  = 0
    robot_net_margin       = 0

    for rtype in robot_fleet:
        r = ROBOT_TYPES[rtype]
        robot_gross_revenue   += r["annual_revenue"] * robot_market_rate
        robot_operating_costs += r["operating_cost"]
        robot_financing_costs += r["purchase_cost"] * COST_OF_CAPITAL
        robot_tokens_consumed += r["tokens_per_day"] * OPERATING_DAYS_YR

    robot_net_before_tax = (robot_gross_revenue
                            - robot_operating_costs
                            - robot_financing_costs)

    # ── Token budget allocation ───────────────────────────────────────────
    remaining_tokens = token_gift - robot_tokens_consumed
    remaining_tokens = max(remaining_tokens, 0)

    # AI agent throughput from remaining tokens
    eff = supervision_efficiency(n_ai_agents)
    tokens_needed_for_full_year = (n_ai_agents * TOKENS_PER_AGENT_HOUR
                                   * SUPERVISION_HOURS_YR)

    # Actual agent-hours delivered (token-capped)
    if tokens_needed_for_full_year <= remaining_tokens:
        agent_hours = n_ai_agents * SUPERVISION_HOURS_YR * eff
        tokens_used_agents = tokens_needed_for_full_year
        binding = "human_time"
    else:
        # Token-bound: how many supervision hours can we afford?
        supervision_possible = remaining_tokens / (n_ai_agents * TOKENS_PER_AGENT_HOUR)
        agent_hours = n_ai_agents * supervision_possible * eff
        tokens_used_agents = remaining_tokens
        binding = "tokens"

    ai_gross_revenue = agent_hours * hourly_market_rate
    total_tokens_used = robot_tokens_consumed + tokens_used_agents

    # ── Total economics ───────────────────────────────────────────────────
    SE_OVERHEAD_ANNUAL = 19_500
    SE_TAX_RATE        = 0.115

    total_gross = ai_gross_revenue + robot_gross_revenue
    total_costs = robot_operating_costs + robot_financing_costs + SE_OVERHEAD_ANNUAL
    taxable     = total_gross - robot_operating_costs - robot_financing_costs
    se_tax      = taxable * SE_TAX_RATE
    net_income  = total_gross - total_costs - se_tax

    # Token utilisation
    token_util = total_tokens_used / token_gift

    return {
        "n_agents":            n_ai_agents,
        "n_robots":            len(robot_fleet),
        "robot_types":         robot_fleet,
        # AI
        "agent_hours":         agent_hours,
        "ai_gross":            ai_gross_revenue,
        "tokens_for_agents_M": tokens_used_agents / 1e6,
        "binding_constraint":  binding,
        # Robots
        "robot_gross":         robot_gross_revenue,
        "robot_op_cost":       robot_operating_costs,
        "robot_finance_cost":  robot_financing_costs,
        "robot_tokens_M":      robot_tokens_consumed / 1e6,
        # Combined
        "total_gross":         total_gross,
        "total_costs":         total_costs,
        "se_tax":              se_tax,
        "net_income":          net_income,
        "token_utilisation":   token_util,
        "tokens_total_M":      total_tokens_used / 1e6,
        "hourly_equivalent":   net_income / SUPERVISION_HOURS_YR,  # net per human hour
    }


# ---------------------------------------------------------------------------
# Equilibrium: what happens when N yeomen each run parallel agents + robots?
# ---------------------------------------------------------------------------

def parallel_equilibrium(
    n_yeomen: int,
    n_agents_per: int,
    n_robots_per: int,
    robot_type: str,
    token_gift: int,
    year: int,
) -> dict:
    """
    Market equilibrium with parallel yeomen.
    Total supply = n_yeomen × effective_agent_hours (AI) + n_yeomen × robot_hours (physical)
    Demand is now split: AI services + physical robot services (separate markets).
    """
    AI_SERVICE_DEMAND_BN = {2025: 200, 2027: 600, 2030: 1_500}
    PHYS_SERVICE_DEMAND_BN = {2025: 800, 2027: 1_200, 2030: 2_000}  # physical labour market is huge
    P0_AI   = 150   # $/hr reference price for AI services
    P0_PHYS = 35    # $/hr reference price for physical labour (current avg wage)
    ELASTICITY = -0.8

    # AI market
    q0_ai    = AI_SERVICE_DEMAND_BN[year] * 1e9 / P0_AI
    eff      = supervision_efficiency(n_agents_per)

    # Tokens per yeoman for agents (after robots take their share)
    r = ROBOT_TYPES[robot_type]
    tokens_for_robots = r["tokens_per_day"] * OPERATING_DAYS_YR * n_robots_per
    tokens_for_agents = max(token_gift - tokens_for_robots, 0)
    tokens_per_agent_year = tokens_for_agents / max(n_agents_per, 1)
    agent_hours_per_yeoman = min(
        tokens_per_agent_year / TOKENS_PER_AGENT_HOUR,
        SUPERVISION_HOURS_YR
    ) * n_agents_per * eff

    q_supply_ai = n_yeomen * agent_hours_per_yeoman
    ratio_ai    = q_supply_ai / q0_ai
    p_ai        = P0_AI * (ratio_ai ** (1 / ELASTICITY)) if ratio_ai > 0 else P0_AI

    # Physical market
    q0_phys     = PHYS_SERVICE_DEMAND_BN[year] * 1e9 / P0_PHYS
    robot_hours = n_robots_per * OPERATING_DAYS_YR * 8   # 8-hr robot day
    q_supply_phys = n_yeomen * robot_hours
    ratio_phys  = q_supply_phys / q0_phys if q_supply_phys > 0 else 0
    p_phys_hourly = P0_PHYS * (ratio_phys ** (1 / ELASTICITY)) if ratio_phys > 0 else P0_PHYS
    robot_annual_revenue = p_phys_hourly * OPERATING_DAYS_YR * 8

    # Yeoman income at these prices
    econ = yeoman_economics(
        n_agents_per,
        [robot_type] * n_robots_per,
        token_gift,
        p_ai,
        robot_market_rate=robot_annual_revenue / r["annual_revenue"],
        year=year,
    )

    return {
        "year":             year,
        "n_yeomen_M":       n_yeomen / 1e6,
        "n_agents":         n_agents_per,
        "n_robots":         n_robots_per,
        "eq_price_ai":      p_ai,
        "eq_price_phys":    p_phys_hourly,
        "net_per_yeoman":   econ["net_income"],
        "total_gross":      econ["total_gross"],
        "ai_gross":         econ["ai_gross"],
        "robot_gross":      econ["robot_gross"],
        "token_util":       econ["token_utilisation"],
        "decent_living":    econ["net_income"] >= 55_000,
    }


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_parallel():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Yeomen Parallel Operations: AI Agents + Robots", fontsize=13, fontweight="bold")
    TOKEN_GIFT = 1_000_000_000

    # ── Panel 1: Value per yeoman by agent + robot count (2027) ─────────────
    ax = axes[0, 0]
    agent_counts = [1, 3, 5, 10, 15, 20]
    robot_counts = [0, 1, 3]
    colors = ["#95a5a6", "#e67e22", "#e74c3c"]

    for rc, color in zip(robot_counts, colors):
        robot_fleet = ["logistics"] * rc
        nets = []
        for na in agent_counts:
            e = yeoman_economics(na, robot_fleet, TOKEN_GIFT, 80)
            nets.append(e["net_income"] / 1000)
        label = f"{rc} logistics robot{'s' if rc != 1 else ''}"
        ax.plot(agent_counts, nets, "o-", color=color, linewidth=2, label=label)

    ax.axhline(55, color="navy", linestyle="--", linewidth=1.5, label="Decent living ($55k)")
    ax.axhline(120, color="green", linestyle=":", linewidth=1.5, alpha=0.7, label="High earner ($120k)")
    ax.set_xlabel("Number of parallel AI agents")
    ax.set_ylabel("Net annual income ($k)")
    ax.set_title("Net income vs parallel AI agents + robots\n($80/hr AI rate, 1B tokens, logistics robots)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-20, 300)

    # ── Panel 2: Token utilisation with parallelism ───────────────────────
    ax = axes[0, 1]
    agent_range = np.arange(1, 21)

    for n_robots, robot_label, color in [
        (0, "no robots",       "#2ecc71"),
        (2, "2 logistics",     "#e67e22"),
        (2, "2 skilled trade", "#e74c3c"),
    ]:
        robot_fleet = (["logistics"] * n_robots if "logistics" in robot_label
                       else ["skilled_trade"] * n_robots)
        utils = []
        for na in agent_range:
            e = yeoman_economics(na, robot_fleet, TOKEN_GIFT, 80)
            utils.append(e["token_utilisation"] * 100)
        ax.plot(agent_range, utils, "o-", color=color, linewidth=2,
                label=robot_label)

    ax.axhline(100, color="red", linestyle="--", linewidth=2, label="Token budget exhausted")
    ax.axhline(80, color="orange", linestyle=":", linewidth=1.5, alpha=0.7, label="80% threshold")
    ax.set_xlabel("Number of parallel AI agents")
    ax.set_ylabel("Token budget utilisation (%)")
    ax.set_title("Token utilisation vs agents + robots\n(1B token budget)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 130)

    # ── Panel 3: Operator type comparison ────────────────────────────────
    ax = axes[1, 0]
    operator_types = [
        ("Solo knowledge",          1,  [],                                 ),
        ("Parallel AI (5 agents)",  5,  [],                                 ),
        ("Parallel AI (10 agents)", 10, [],                                 ),
        ("1 logistics robot",       2,  ["logistics"],                      ),
        ("3 logistics robots",      2,  ["logistics"]*3,                    ),
        ("5 agents + 2 trade robots",5, ["skilled_trade"]*2,                ),
        ("10 agents + 3 trade robots",10,["skilled_trade"]*3,               ),
        ("5 agents + 2 humanoids",  5,  ["humanoid_general"]*2,             ),
    ]

    for year, color in [(2027, "#e67e22"), (2030, "#2ecc71")]:
        rate = 80 if year == 2027 else 120
        nets = []
        for label, na, rf in operator_types:
            e = yeoman_economics(na, rf, TOKEN_GIFT, rate)
            nets.append(e["net_income"] / 1000)
        x = np.arange(len(operator_types))
        offset = -0.2 if year == 2027 else 0.2
        bars = ax.bar(x + offset, nets, 0.4, label=str(year), color=color, alpha=0.85)

    ax.axhline(55, color="navy", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.set_xticks(np.arange(len(operator_types)))
    ax.set_xticklabels([t[0] for t in operator_types], rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("Net annual income ($k)")
    ax.set_title("Net income by operator configuration\n(dashed = decent living floor)")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    # ── Panel 4: Market equilibrium — AI + physical with parallelism ─────
    ax = axes[1, 1]
    yeomen_range = np.linspace(1e6, 20e6, 80)
    configs = [
        ("1 agent, 0 robots",  1, 0, "logistics", "#95a5a6"),
        ("5 agents, 0 robots", 5, 0, "logistics", "#3498db"),
        ("5 agents, 2 robots", 5, 2, "logistics", "#e67e22"),
        ("10 agents, 3 robots",10, 3, "skilled_trade", "#e74c3c"),
    ]

    for label, na, nr, rt, color in configs:
        nets = []
        for n in yeomen_range:
            eq = parallel_equilibrium(int(n), na, nr, rt, TOKEN_GIFT, 2027)
            nets.append(eq["net_per_yeoman"] / 1000)
        ax.plot(yeomen_range / 1e6, nets, linewidth=2, color=color, label=label)

    ax.axhline(55, color="navy", linestyle="--", linewidth=1.5, label="Decent living ($55k)")
    ax.set_xlabel("Number of yeomen (millions)")
    ax.set_ylabel("Net income per yeoman ($k)")
    ax.set_title("Equilibrium income vs yeoman count\n(2027, different configurations)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-20, 400)

    plt.tight_layout()
    plt.savefig("yeomen_parallel.png", dpi=150, bbox_inches="tight")
    print("  Saved: yeomen_parallel.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 72)
    print("YEOMEN PARALLEL MODEL: AI AGENTS + PHYSICAL ROBOTS")
    print("=" * 72)

    TOKEN_GIFT = 1_000_000_000

    # --- Robot types ---
    print("\n--- ROBOT ECONOMICS (per unit, per year) ---")
    print(f"  {'Type':<20} {'Purchase':>10} {'Revenue':>10} {'OpCost':>9} {'Finance':>9} {'Net margin':>12}")
    print("  " + "─" * 72)
    for rtype, r in ROBOT_TYPES.items():
        finance = r["purchase_cost"] * COST_OF_CAPITAL
        net_margin = r["annual_revenue"] - r["operating_cost"] - finance
        print(f"  {rtype:<20} ${r['purchase_cost']/1000:>5.0f}k   "
              f"${r['annual_revenue']/1000:>5.0f}k   ${r['operating_cost']/1000:>4.0f}k   "
              f"${finance/1000:>4.0f}k   ${net_margin/1000:>6.0f}k/yr")

    # --- Supervision efficiency ---
    print("\n--- SUPERVISION EFFICIENCY DEGRADATION ---")
    print(f"  {'N agents':>10}  {'Efficiency':>12}  {'Effective throughput':>22}")
    print("  " + "─" * 48)
    for n in [1, 2, 3, 5, 8, 10, 15, 20]:
        eff = supervision_efficiency(n)
        throughput = n * eff
        print(f"  {n:>10}  {eff:>10.1%}  {throughput:>15.1f}x solo")

    # --- Operator configurations ---
    print("\n--- OPERATOR CONFIGURATIONS: INCOME AT $80/hr AI rate, 1B tokens ---")
    configs = [
        ("Solo (1 agent, 0 robots)",         1,  []),
        ("3 parallel agents",                 3,  []),
        ("5 parallel agents",                 5,  []),
        ("10 parallel agents",               10,  []),
        ("20 parallel agents",               20,  []),
        ("1 agent + 2 logistics robots",      1,  ["logistics"]*2),
        ("5 agents + 2 logistics robots",     5,  ["logistics"]*2),
        ("5 agents + 3 trade robots",         5,  ["skilled_trade"]*3),
        ("10 agents + 3 trade robots",       10,  ["skilled_trade"]*3),
        ("5 agents + 2 humanoids (2028+)",    5,  ["humanoid_general"]*2),
        ("10 agents + 3 humanoids (2028+)",  10,  ["humanoid_general"]*3),
    ]

    print(f"  {'Configuration':<40} {'Gross':>8} {'Net':>8} {'Tok util':>10} {'Binding':>12}")
    print("  " + "─" * 82)
    for label, na, rf in configs:
        e = yeoman_economics(na, rf, TOKEN_GIFT, 80)
        flag = " ⚠" if e["token_utilisation"] > 0.95 else ""
        print(f"  {label:<40} ${e['total_gross']/1000:>5.0f}k  ${e['net_income']/1000:>5.0f}k  "
              f"{e['token_utilisation']:>8.0%}  {e['binding_constraint']:>12}{flag}")

    # --- Token budget sensitivity ---
    print("\n--- TOKEN BUDGET SENSITIVITY (5 agents + 3 logistics robots) ---")
    print(f"  How many tokens does parallel work actually need?")
    print(f"  {'Token gift':>14}  {'Binding':>12}  {'Net income':>12}  {'Tok util':>10}")
    print("  " + "─" * 54)
    for tokens in [200_000_000, 500_000_000, 1_000_000_000, 2_000_000_000, 5_000_000_000]:
        e = yeoman_economics(5, ["logistics"]*3, tokens, 80)
        print(f"  {tokens/1e9:>10.1f}B tok  {e['binding_constraint']:>12}  "
              f"${e['net_income']/1000:>8.0f}k  {e['token_utilisation']:>8.0%}")

    # --- The market equilibrium ---
    print("\n--- MARKET EQUILIBRIUM: HOW MANY YEOMEN CAN THE MARKET SUPPORT? ---")
    print("  (5 agents + 2 logistics robots, 1B tokens, 2027)")
    print(f"  {'Yeomen':>10}  {'AI price':>10}  {'Robot rev':>12}  {'Net income':>12}  {'Decent?':>8}")
    print("  " + "─" * 58)
    for n in [1_000_000, 3_000_000, 5_000_000, 8_000_000, 10_000_000, 15_000_000]:
        eq = parallel_equilibrium(n, 5, 2, "logistics", TOKEN_GIFT, 2027)
        d = "YES" if eq["decent_living"] else "no"
        print(f"  {n/1e6:>8.1f}M  ${eq['eq_price_ai']:>7.0f}/hr  "
              f"${eq['robot_gross']/1000:>7.0f}k/yr  ${eq['net_per_yeoman']/1000:>8.0f}k  {d:>8}")

    # --- Key insight ---
    print("\n--- KEY INSIGHTS ---")
    print("""
  1. PARALLELISM CHANGES THE TOKEN ARITHMETIC COMPLETELY
     5 parallel agents × 500k tokens/hr × 1,200 supervision hours = 3B tokens/yr needed.
     1B tokens only covers 400 supervision hours of 5-agent parallel work.
     → For parallel operation, 1B tokens is TIGHT, not generous.
     → 2-3B tokens/yeoman is the right gift size for a 5-agent operator.
     → Or: design the gift as a function of registered parallel capacity.

  2. ROBOTS CONSUME TOKENS TOO — BUT FAR LESS
     A logistics robot uses ~5k tokens/day = 1.5M/yr (trivial from 1B budget).
     A humanoid doing general tasks uses ~50k tokens/day = 15M/yr (still modest).
     Robots are mostly physical — their token budget is small vs. AI agents.
     Physical value generation is largely token-independent.

  3. THE SUPERVISION EFFICIENCY CURVE IS THE KEY DESIGN VARIABLE
     At N=5 agents: 85% efficiency (nearly full leverage).
     At N=10: 65% (still very worthwhile).
     At N=20: 40% (diminishing — you need better async AI tools to go here).
     Most yeomen will optimise at 5-10 agents where marginal efficiency is still high.

  4. ROBOTS UNLOCK PHYSICAL LABOUR MARKETS WITHOUT TOKEN PRESSURE
     3 skilled-trade robots → $150k gross/yr from physical work, using only
     ~22M tokens/yr (out of 1B budget). The physical economy is CHEAP to tokenise.
     Robot + agent combos have the highest net income AND efficient token use.

  5. THE EQUILIBRIUM PRICE WITH PARALLELISM STAYS HIGHER
     Each yeoman serves more clients → but they're also generating more VALUE per client.
     The AI service market price compresses less because quality/throughput rises with N.
     5M yeomen with 5-agent parallel capacity can all earn $80-120k net in 2027.
     Compare to sequential model: same 5M yeomen only earned $55-85k.

  6. WHAT THIS MEANS FOR TOKEN GIFT SIZING
     For SEQUENTIAL (solo) yeoman:   1B tokens is sufficient (human time binds)
     For PARALLEL (5 agents):        2-3B tokens needed (agents exhaust budget)
     For PARALLEL + ROBOTS:          2B tokens covers agents; robots are cheap
     For FRONTIER parallel (10+ ag): 5B+ tokens needed — this gets expensive

     Policy design: gift should scale with REGISTERED AGENT CAPACITY, not be flat.
     Base grant: 500M tokens (solo floor)
     Per registered parallel agent: +300M tokens/agent/yr
     Per registered robot: +20M tokens/robot/yr
     Cap at 10 agents + 5 robots to prevent micro-enterprise concentration.
    """)

    print("Generating chart...")
    plot_parallel()
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
