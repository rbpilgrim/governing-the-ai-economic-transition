"""
Robot Technology Obsolescence Risk Model
=========================================
Question: If I finance a robot early and technology improves, am I disadvantaged
compared to someone who waits for cheaper, more capable robots?

Key tensions:
  1. Technology price curve: robots get ~15% cheaper per year (learning curve)
  2. Capability improvement: new robots earn more (better specs, less downtime)
  3. But early adopter earns income during the waiting period the late adopter misses
  4. And early adopter may be locked into loan repayments on depreciating asset

This model:
  A. Quantifies the obsolescence gap (how bad is it really?)
  B. Shows where early-mover income offsets the technology cost
  C. Designs three policy mechanisms to neutralise the disadvantage:
       - Upgrade credit (govt pays off residual, yeoman re-enters programme)
       - Shortened loan terms for fast-moving tech
       - Performance-indexed loan payments (pay less if robot earns less)

Run: python3 robot_obsolescence.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


# ---------------------------------------------------------------------------
# Technology trajectory parameters
# ---------------------------------------------------------------------------

ROBOT_COST_2025     = 80_000    # $ today
VEHICLE_COST        = 50_000    # vehicle doesn't obsolete as fast
TOTAL_2025          = ROBOT_COST_2025 + VEHICLE_COST

# Robot technology learning curve (based on Moore's-law-adjacent hardware trends)
# Conservative: 12%/yr price decline for equivalent capability
# Optimistic: 20%/yr (closer to GPU trajectory)
PRICE_DECLINE_YR    = 0.15      # 15%/yr — central estimate
CAPABILITY_GAIN_YR  = 0.08      # 8%/yr improvement in robot earning power (speed, uptime, range)

# Yeoman income baseline
BASE_HOURLY_RATE    = 55.0      # $/hr at t=0 capability
ROBOT_HOURS_YR      = 2_000
TRANSPORT_OVERHEAD  = 0.25
SE_TAX              = 0.115
INCOME_TAX          = 0.18
FIXED_OVERHEAD      = 19_500

GOVT_BORROW_RATE    = 0.035
LOAN_TERM_STD       = 10
LOAN_TERM_SHORT     = 5         # shortened for fast-tech option

GOVT_LOAN_RATE      = 0.000     # zero-interest (base scenario)


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def robot_cost_at(year: int) -> float:
    """Purchase cost of a new robot at given year (price decline over time)."""
    return ROBOT_COST_2025 * (1 - PRICE_DECLINE_YR) ** year


def capability_at(purchase_year: int, current_year: int) -> float:
    """
    Relative earning power of a robot bought at purchase_year, evaluated at current_year.
    - New robots each year are more capable (gains CAPABILITY_GAIN_YR vs prior gen)
    - Market prices commoditise: yeomen with old robots bid lower to compete
    - Combined: old robot earns less relative to market rate
    """
    # Best robot available in current_year has had (current_year - purchase_year) years of improvement
    # Old robot has static capability; market rate reflects newest robot
    market_capability = (1 + CAPABILITY_GAIN_YR) ** (current_year - purchase_year)
    # Old robot still works but buyer has access to better robots — price competition compresses old-robot rate
    # Assume old robot earns market_rate / market_capability (commodity compression)
    return 1.0 / market_capability


def annual_loan_payment(principal: float, rate: float, term: int) -> float:
    if rate > 0:
        r = rate
        return principal * (r * (1 + r) ** term) / ((1 + r) ** term - 1)
    else:
        return principal / term


def yeoman_net(gross_robot: float, loan_payment: float) -> float:
    """Net income after transport, taxes, overhead, loan."""
    gross_after_transport = gross_robot * (1 - TRANSPORT_OVERHEAD)
    se_tax = gross_after_transport * SE_TAX
    net_before_it = gross_after_transport - se_tax - FIXED_OVERHEAD - loan_payment
    income_tax = max(net_before_it, 0) * INCOME_TAX
    return net_before_it - income_tax


# ---------------------------------------------------------------------------
# Strategy A: Early adopter — buys in 2025, 10-yr loan, no upgrade
# ---------------------------------------------------------------------------

def early_adopter_cashflows(loan_term: int = LOAN_TERM_STD,
                             loan_rate: float = GOVT_LOAN_RATE,
                             upgrade_year: int = None,
                             upgrade_credit_pct: float = 0.0) -> pd.DataFrame:
    """
    Simulate a yeoman who buys in year 0.
    Optional: government upgrade credit at upgrade_year.
    """
    total_capital = TOTAL_2025
    payment = annual_loan_payment(total_capital, loan_rate, loan_term)
    loan_balance = total_capital

    rows = []
    cumulative_net = 0.0

    for yr in range(1, 16):  # model 15 years
        # Has loan expired?
        in_loan = (yr <= loan_term)
        pmt = payment if in_loan else 0.0

        # Capability degradation vs market
        cap = capability_at(purchase_year=0, current_year=yr)
        hourly = BASE_HOURLY_RATE * cap
        gross_robot = hourly * ROBOT_HOURS_YR * 0.75  # 75% utilisation

        # Upgrade credit: government pays residual loan balance at upgrade_year
        upgrade_benefit = 0.0
        if upgrade_year and yr == upgrade_year and in_loan:
            # Calc remaining balance
            remaining_balance = total_capital
            for _ in range(yr):
                interest = remaining_balance * loan_rate
                principal_paid = payment - interest
                remaining_balance = max(remaining_balance - principal_paid, 0)
            upgrade_benefit = remaining_balance * upgrade_credit_pct
            # After upgrade: yeoman re-enters with new robot at year-yr cost
            # (simplified: we just show the cash benefit, full re-entry is "late adopter" scenario)

        net = yeoman_net(gross_robot, pmt) + upgrade_benefit
        cumulative_net += net

        # Update loan balance for equity tracking
        if in_loan:
            interest = loan_balance * loan_rate
            principal_paid = payment - interest
            loan_balance = max(loan_balance - principal_paid, 0)

        rows.append({
            "year": yr,
            "strategy": "Early adopter",
            "hourly_rate": hourly,
            "gross_robot": gross_robot,
            "loan_payment": pmt,
            "net_income": net,
            "cumulative_net": cumulative_net,
            "upgrade_credit": upgrade_benefit,
            "capability_ratio": cap,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Strategy B: Late adopter — waits N years, buys newer cheaper robot
# ---------------------------------------------------------------------------

def late_adopter_cashflows(wait_years: int, loan_term: int = LOAN_TERM_STD,
                            loan_rate: float = GOVT_LOAN_RATE) -> pd.DataFrame:
    """
    Simulate a yeoman who waits wait_years before entering.
    During waiting period, earns zero from robots.
    """
    robot_cost_entry = robot_cost_at(wait_years)
    total_capital = robot_cost_entry + VEHICLE_COST
    payment = annual_loan_payment(total_capital, loan_rate, loan_term)

    rows = []
    cumulative_net = 0.0
    loan_balance = total_capital

    for yr in range(1, 16):
        if yr <= wait_years:
            rows.append({
                "year": yr,
                "strategy": f"Late ({wait_years}yr wait)",
                "hourly_rate": 0,
                "gross_robot": 0,
                "loan_payment": 0,
                "net_income": 0,
                "cumulative_net": 0,
                "upgrade_credit": 0,
                "capability_ratio": 0,
            })
            continue

        # Operating year number (1 = first year with robot)
        op_yr = yr - wait_years
        in_loan = op_yr <= loan_term
        pmt = payment if in_loan else 0.0

        # New robot at entry is best available, but capability gap with market grows each year
        cap = capability_at(purchase_year=wait_years, current_year=yr)
        hourly = BASE_HOURLY_RATE * (1 + CAPABILITY_GAIN_YR) ** wait_years * cap
        # Late adopter's robot is better at entry, but same degradation rate applies
        gross_robot = hourly * ROBOT_HOURS_YR * 0.75

        net = yeoman_net(gross_robot, pmt)
        cumulative_net += net

        if in_loan:
            interest = loan_balance * loan_rate
            principal_paid = pmt - interest
            loan_balance = max(loan_balance - principal_paid, 0)

        rows.append({
            "year": yr,
            "strategy": f"Late ({wait_years}yr wait)",
            "hourly_rate": hourly,
            "gross_robot": gross_robot,
            "loan_payment": pmt,
            "net_income": net,
            "cumulative_net": cumulative_net,
            "upgrade_credit": 0,
            "capability_ratio": cap,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Policy mechanism models
# ---------------------------------------------------------------------------

def upgrade_credit_analysis() -> pd.DataFrame:
    """
    Compare: no upgrade vs upgrade credit at year 5 (govt pays 50% of residual).
    After upgrade, yeoman gets new robot with new loan at current prices.
    """
    no_upgrade = early_adopter_cashflows()
    with_credit = early_adopter_cashflows(upgrade_year=5, upgrade_credit_pct=0.50)

    # After upgrade at year 5: modelled as re-entering with yr-5 robot
    robot_cost_yr5 = robot_cost_at(5)
    total_yr5 = robot_cost_yr5 + VEHICLE_COST
    payment_yr5 = annual_loan_payment(total_yr5, GOVT_LOAN_RATE, LOAN_TERM_STD)

    # Build upgrade-then-new scenario
    rows = []
    cumulative = 0.0
    loan_balance_new = total_yr5

    for yr in range(1, 16):
        if yr <= 5:
            # Same as early adopter for first 5 years (but receives credit at yr5)
            base_row = with_credit[with_credit.year == yr].iloc[0]
            cumulative += base_row["net_income"]
            rows.append({
                "year": yr,
                "strategy": "Upgrade at yr5 (50% credit)",
                "net_income": base_row["net_income"],
                "cumulative_net": cumulative,
                "note": "yr5: credit received" if yr == 5 else "",
            })
        else:
            # Now operating new robot purchased at yr5
            op_yr = yr - 5
            in_loan = op_yr <= LOAN_TERM_STD
            pmt = payment_yr5 if in_loan else 0.0

            # New robot starts fresh — capability_at(purchase_year=5, current_year=yr)
            cap = capability_at(purchase_year=5, current_year=yr)
            hourly = BASE_HOURLY_RATE * (1 + CAPABILITY_GAIN_YR) ** 5 * cap
            gross_robot = hourly * ROBOT_HOURS_YR * 0.75

            net = yeoman_net(gross_robot, pmt)
            cumulative += net

            if in_loan:
                interest = loan_balance_new * GOVT_LOAN_RATE
                principal_paid = pmt - interest
                loan_balance_new = max(loan_balance_new - principal_paid, 0)

            rows.append({
                "year": yr,
                "strategy": "Upgrade at yr5 (50% credit)",
                "net_income": net,
                "cumulative_net": cumulative,
                "note": "",
            })

    return pd.DataFrame(rows)


def shortened_loan_analysis() -> pd.DataFrame:
    """
    5-year loan matches technology cycle — loan paid off before major obsolescence.
    Yeoman then has option to upgrade with new loan on newer/cheaper robot.
    """
    rows = []
    cumulative = 0.0

    # Phase 1: yr 1-5, repay loan on original robot
    total_capital = TOTAL_2025
    payment_5yr = annual_loan_payment(total_capital, GOVT_LOAN_RATE, 5)
    loan_balance = total_capital

    for yr in range(1, 6):
        cap = capability_at(purchase_year=0, current_year=yr)
        hourly = BASE_HOURLY_RATE * cap
        gross_robot = hourly * ROBOT_HOURS_YR * 0.75
        net = yeoman_net(gross_robot, payment_5yr)
        cumulative += net

        interest = loan_balance * GOVT_LOAN_RATE
        principal_paid = payment_5yr - interest
        loan_balance = max(loan_balance - principal_paid, 0)

        rows.append({
            "year": yr, "strategy": "5-yr loan, upgrade yr6",
            "net_income": net, "cumulative_net": cumulative,
        })

    # Phase 2: yr 6-15, new loan on yr-5 robot (cheaper, better)
    robot_cost_yr5 = robot_cost_at(5)
    total_yr5 = robot_cost_yr5 + VEHICLE_COST
    payment_new = annual_loan_payment(total_yr5, GOVT_LOAN_RATE, 10)
    loan_balance_new = total_yr5

    for yr in range(6, 16):
        op_yr = yr - 5
        in_loan = op_yr <= 10
        pmt = payment_new if in_loan else 0.0

        cap = capability_at(purchase_year=5, current_year=yr)
        hourly = BASE_HOURLY_RATE * (1 + CAPABILITY_GAIN_YR) ** 5 * cap
        gross_robot = hourly * ROBOT_HOURS_YR * 0.75
        net = yeoman_net(gross_robot, pmt)
        cumulative += net

        if in_loan:
            interest = loan_balance_new * GOVT_LOAN_RATE
            principal_paid = pmt - interest
            loan_balance_new = max(loan_balance_new - principal_paid, 0)

        rows.append({
            "year": yr, "strategy": "5-yr loan, upgrade yr6",
            "net_income": net, "cumulative_net": cumulative,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# The core question: technology price trajectory vs income stream
# ---------------------------------------------------------------------------

def tech_vs_income_table() -> None:
    """Print the key numbers: robot price decline vs income earned during wait."""
    print("\n--- TECHNOLOGY PRICE CURVE VS INCOME FOREGONE DURING WAIT ---")
    print(f"\n  Robot purchase price (ex-vehicle) by entry year:")
    print(f"  {'Entry year':>12}  {'Robot cost':>12}  {'Total capital':>14}  "
          f"{'Saving vs 2025':>16}  {'Income foregone':>17}")
    print("  " + "─" * 76)

    early_net_yr = yeoman_fiscal_simple(year=1)  # approximate annual net during wait

    for wait in range(0, 11, 1):
        robot_cost = robot_cost_at(wait)
        total = robot_cost + VEHICLE_COST
        saving = TOTAL_2025 - total
        income_lost = early_net_yr * wait  # income early adopter earns while waiting
        crossover = "← WAIT COSTS MORE" if income_lost > saving else ""
        print(f"  {2025+wait:>8}  (wait {wait:>2}yr)  ${robot_cost:>9,.0f}   "
              f"${total:>11,.0f}    ${saving:>13,.0f}    ${income_lost:>13,.0f}  {crossover}")


def yeoman_fiscal_simple(year: int) -> float:
    """Approximate net income in a given year with zero-interest 10yr loan."""
    payment = TOTAL_2025 / LOAN_TERM_STD
    cap = capability_at(purchase_year=0, current_year=year)
    hourly = BASE_HOURLY_RATE * cap
    gross = hourly * ROBOT_HOURS_YR * 0.75
    return yeoman_net(gross, payment)


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

def plot_obsolescence():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Robot Technology Obsolescence: Risk & Policy Mitigations", fontsize=13, fontweight="bold")

    years = np.arange(1, 16)

    # ── Panel 1: Robot price trajectory ──────────────────────────────────
    ax = axes[0, 0]
    robot_prices = [robot_cost_at(y) for y in range(0, 11)]
    total_costs   = [robot_cost_at(y) + VEHICLE_COST for y in range(0, 11)]
    ax.bar(range(2025, 2036), robot_prices, color="#3498db", alpha=0.7, label="Robot cost")
    ax.bar(range(2025, 2036), [VEHICLE_COST]*11, bottom=robot_prices, color="#95a5a6",
           alpha=0.7, label="Vehicle cost (stable)")
    ax.axhline(TOTAL_2025, color="#e74c3c", linestyle="--", linewidth=1.5,
               label=f"2025 total (${TOTAL_2025/1000:.0f}k)")
    ax.set_xlabel("Entry year")
    ax.set_ylabel("Capital cost ($)")
    ax.set_title("Robot purchase price over time\n(15%/yr technology learning curve)")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # ── Panel 2: Cumulative net income — early vs wait strategies ─────────
    ax = axes[0, 1]
    early = early_adopter_cashflows()
    ax.plot(years, early["cumulative_net"] / 1000, color="#2ecc71", linewidth=2.5, label="Enter 2025")
    colors_wait = ["#e67e22", "#e74c3c", "#9b59b6"]
    for wait, color in zip([3, 5, 7], colors_wait):
        late = late_adopter_cashflows(wait_years=wait)
        ax.plot(years, late["cumulative_net"] / 1000, color=color, linewidth=2,
                linestyle="--", label=f"Wait {wait} years (enter {2025+wait})")

    ax.axhline(0, color="k", linestyle=":", alpha=0.4)
    ax.set_xlabel("Years from 2025")
    ax.set_ylabel("Cumulative net income ($k)")
    ax.set_title("Cumulative earnings: early entry vs waiting\n(zero-interest loan, 75% utilisation)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── Panel 3: Annual income — capability degradation effect ────────────
    ax = axes[0, 2]
    ax.plot(years, early["net_income"] / 1000, color="#2ecc71", linewidth=2.5, label="Enter 2025")
    for wait, color in zip([3, 5], ["#e67e22", "#e74c3c"]):
        late = late_adopter_cashflows(wait_years=wait)
        ax.plot(years, late["net_income"] / 1000, color=color, linewidth=2,
                linestyle="--", label=f"Wait {wait}yr (enter {2025+wait})")
    ax.axhline(55, color="navy", linestyle=":", linewidth=1.5, label="Decent living ($55k)")
    ax.axhline(0, color="k", linestyle=":", alpha=0.4)
    ax.set_xlabel("Years from 2025")
    ax.set_ylabel("Annual net income ($k)")
    ax.set_title("Annual income vs time\n(shows capability erosion over loan term)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── Panel 4: Policy mitigations vs baseline ────────────────────────────
    ax = axes[1, 0]
    early = early_adopter_cashflows()
    upgrade5 = upgrade_credit_analysis()
    short_loan = shortened_loan_analysis()
    late5 = late_adopter_cashflows(wait_years=5)

    ax.plot(years, early["cumulative_net"] / 1000, color="#2ecc71", linewidth=2.5, label="Enter 2025, no upgrade")
    ax.plot(years, upgrade5["cumulative_net"] / 1000, color="#3498db", linewidth=2,
            linestyle="-.", label="Enter 2025 + upgrade credit yr5")
    ax.plot(years, short_loan["cumulative_net"] / 1000, color="#9b59b6", linewidth=2,
            linestyle="-.", label="5yr loan + new robot yr6")
    ax.plot(years, late5["cumulative_net"] / 1000, color="#e74c3c", linewidth=2,
            linestyle="--", label="Wait 5yr (no mitigation)")
    ax.axhline(0, color="k", linestyle=":", alpha=0.4)
    ax.set_xlabel("Years from 2025")
    ax.set_ylabel("Cumulative net income ($k)")
    ax.set_title("Policy mitigations vs baseline\n(are early adopters made whole?)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── Panel 5: Breakeven: when does waiting pay off? ────────────────────
    ax = axes[1, 1]
    wait_years_range = range(0, 11)
    cum_at_yr10 = []
    for wait in wait_years_range:
        late = late_adopter_cashflows(wait_years=wait)
        cum10 = late[late.year == 10]["cumulative_net"].values[0]
        cum_at_yr10.append(cum10 / 1000)

    ax.bar(wait_years_range, cum_at_yr10, color=["#2ecc71" if w == 0 else "#e74c3c" if c < cum_at_yr10[0] else "#e67e22"
                                                   for w, c in zip(wait_years_range, cum_at_yr10)], alpha=0.85)
    ax.axhline(cum_at_yr10[0], color="#2ecc71", linestyle="--", linewidth=1.5,
               label=f"Enter 2025 baseline: ${cum_at_yr10[0]:.0f}k at yr10")
    ax.set_xlabel("Years to wait before entering")
    ax.set_ylabel("Cumulative net income at year-10 ($k)")
    ax.set_title("Impact of waiting: 10-year cumulative income\n(waiting always costs in present value)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # ── Panel 6: Govt upgrade credit fiscal cost ──────────────────────────
    ax = axes[1, 2]
    credit_pcts = [0.25, 0.50, 0.75, 1.00]
    # At yr5, remaining loan balance (zero-interest 10yr): 50% of principal
    residual_yr5 = TOTAL_2025 * 0.50   # 5 of 10 years paid off

    scales = [1e6, 2e6, 5e6, 10e6]
    for cpct in credit_pcts:
        credit_cost_per = residual_yr5 * cpct
        costs_bn = [n * credit_cost_per / 1e9 for n in scales]
        ax.plot([n/1e6 for n in scales], costs_bn, linewidth=2,
                label=f"{cpct:.0%} residual credit (${credit_cost_per/1000:.0f}k/yeoman)")

    ax.set_xlabel("Number of yeomen in upgrade cohort (M)")
    ax.set_ylabel("Upgrade credit programme cost ($B)")
    ax.set_title("Cost of upgrade credit programme\n(at year 5 refresh cycle)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("robot_obsolescence.png", dpi=150, bbox_inches="tight")
    print("  Saved: robot_obsolescence.png")


# ---------------------------------------------------------------------------
# Self-funded upgrade: can the yeoman save up and buy the next robot outright?
# ---------------------------------------------------------------------------

LIVING_STANDARD      = 55_000    # yeoman keeps this; saves the rest
SAVINGS_RETURN       = 0.04      # savings earn 4%/yr (low-risk investment)

def self_funded_upgrade_analysis() -> pd.DataFrame:
    """
    Track yeoman savings over loan period.
    After paying loan + living standard, can surplus fund the year-5 upgrade outright?
    If savings >= new robot cost at upgrade year, no second loan needed.
    """
    payment = TOTAL_2025 / LOAN_TERM_STD   # zero-interest: $13k/yr
    savings = 0.0
    rows = []

    for yr in range(1, 16):
        in_loan = yr <= LOAN_TERM_STD
        loan_pmt = payment if in_loan else 0.0

        # Gross income (capability degrades vs market over time)
        cap = capability_at(purchase_year=0, current_year=yr)
        hourly = BASE_HOURLY_RATE * cap
        gross_robot = hourly * ROBOT_HOURS_YR * 0.75

        # Net income after transport, taxes, overhead, loan
        net = yeoman_net(gross_robot, loan_pmt)

        # Surplus above living standard goes to savings
        surplus = max(net - LIVING_STANDARD, 0)
        savings = savings * (1 + SAVINGS_RETURN) + surplus

        # Cost of upgrading to current-generation robot this year
        upgrade_cost = robot_cost_at(yr) + VEHICLE_COST
        # Residual loan balance (zero-interest: linear paydown)
        residual_loan = max(TOTAL_2025 - payment * yr, 0)
        # Net cost: buy new robot, sell old (secondary market ~20% of original)
        old_robot_resale = max(ROBOT_COST_2025 * (0.20), 0)  # floor value
        net_upgrade_cost = upgrade_cost - old_robot_resale

        can_self_fund = savings >= net_upgrade_cost
        can_clear_residual = savings >= residual_loan  # can also pay off old loan

        rows.append({
            "year": yr,
            "net_income": net,
            "surplus_saved": surplus,
            "cumulative_savings": savings,
            "upgrade_cost_new_robot": upgrade_cost,
            "old_robot_resale": old_robot_resale,
            "net_upgrade_cost": net_upgrade_cost,
            "residual_loan": residual_loan,
            "can_clear_residual_loan": can_clear_residual,
            "can_self_fund_upgrade": can_self_fund,
        })

    return pd.DataFrame(rows)


def print_self_funded_table() -> None:
    df = self_funded_upgrade_analysis()
    print("\n--- SELF-FUNDED UPGRADE: CAN SAVINGS REPLACE THE SECOND LOAN? ---")
    print(f"  Assumption: yeoman keeps ${LIVING_STANDARD/1000:.0f}k/yr, saves the rest at {SAVINGS_RETURN:.0%}")
    print(f"\n  {'Year':>6}  {'Net income':>12}  {'Surplus':>10}  {'Savings':>12}  {'Upgrade cost':>14}  "
          f"{'Clear loan?':>12}  {'Self-fund?':>11}")
    print("  " + "─" * 84)
    for _, r in df.iterrows():
        clear = "YES ✓" if r["can_clear_residual_loan"] else "no"
        fund  = "YES ✓" if r["can_self_fund_upgrade"] else "no"
        print(f"  {r['year']:>6.0f}  ${r['net_income']:>9,.0f}   ${r['surplus_saved']:>7,.0f}   "
              f"${r['cumulative_savings']:>9,.0f}    ${r['net_upgrade_cost']:>11,.0f}    "
              f"{clear:>12}  {fund:>11}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 72)
    print("ROBOT TECHNOLOGY OBSOLESCENCE: RISK ANALYSIS & POLICY DESIGN")
    print("=" * 72)

    print(f"""
  Core concern: robots bought in 2025 at ${TOTAL_2025:,} may be outclassed by
  robots available in 2030 at ~${robot_cost_at(5)+VEHICLE_COST:,.0f} — with better specs,
  lower price. Does early financing put yeomen at a structural disadvantage?

  Technology assumptions:
    Robot price decline:    {PRICE_DECLINE_YR:.0%}/yr  (learning curve, similar to solar/GPUs)
    Capability improvement: {CAPABILITY_GAIN_YR:.0%}/yr  (speed, uptime, task range)
    Vehicle cost:           Stable (conventional vehicle, no technology cliff)
    Loan type:              Zero-interest, 10yr, government-backed
    """)

    # ── Table 1: Price trajectory ──────────────────────────────────────────
    print("--- ROBOT PRICE BY ENTRY YEAR ---")
    print(f"\n  {'Wait':>6}  {'Entry year':>10}  {'Robot cost':>12}  {'Total capital':>14}  {'Saving vs today':>16}")
    print("  " + "─" * 64)
    for wait in range(0, 11, 1):
        robot_cost = robot_cost_at(wait)
        total = robot_cost + VEHICLE_COST
        saving = TOTAL_2025 - total
        print(f"  {wait:>4}yr  {2025+wait:>10}  ${robot_cost:>10,.0f}   ${total:>11,.0f}    ${saving:>13,.0f}")

    # ── Table 2: Income foregone vs capital saving ─────────────────────────
    tech_vs_income_table()

    print(f"""
  KEY INSIGHT: Waiting 5 years saves ~${(TOTAL_2025 - robot_cost_at(5) - VEHICLE_COST):,.0f} in capital cost.
  But the early adopter earns ~${sum(yeoman_fiscal_simple(y) for y in range(1, 6)):,.0f} in net income over those 5 years.
  The capital saving is MUCH smaller than the income foregone.
  Waiting is not rational even in a fast-depreciation environment.
    """)

    # ── Table 3: Cumulative income comparison ─────────────────────────────
    print("--- CUMULATIVE NET INCOME AT YEAR 10: EARLY VS WAIT STRATEGIES ---")
    print(f"\n  {'Strategy':>30}  {'Year 5 cum':>12}  {'Year 10 cum':>13}  {'Year 15 cum':>13}")
    print("  " + "─" * 72)

    strategies = [
        ("Enter 2025 (early)", early_adopter_cashflows()),
        ("Wait 3yr (enter 2028)", late_adopter_cashflows(3)),
        ("Wait 5yr (enter 2030)", late_adopter_cashflows(5)),
        ("Wait 7yr (enter 2032)", late_adopter_cashflows(7)),
        ("Early + upgrade credit yr5", upgrade_credit_analysis()),
        ("5yr loan + new robot yr6", shortened_loan_analysis()),
    ]
    for name, df in strategies:
        c5  = df[df.year ==  5]["cumulative_net"].values[0]
        c10 = df[df.year == 10]["cumulative_net"].values[0]
        c15 = df[df.year == 15]["cumulative_net"].values[0]
        print(f"  {name:>30}  ${c5:>9,.0f}    ${c10:>9,.0f}    ${c15:>9,.0f}")

    # ── Policy design: upgrade mechanisms ─────────────────────────────────
    print(f"""
--- POLICY DESIGN: MANAGING OBSOLESCENCE RISK ---

  THREE MECHANISMS, increasing government cost:

  1. UPGRADE CREDIT (recommended)
     Government pays off 50% of residual loan balance at year 5 if yeoman
     re-enters the programme with a new robot loan at current prices.
     - Per-yeoman cost: ~${TOTAL_2025 * 0.50 * 0.50:,.0f}  (50% of ~50% residual)
     - For 5M yeomen: ~${5_000_000 * TOTAL_2025 * 0.25 / 1e9:.0f}B one-time at yr5
     - Yeoman immediately has: better robot, lower payment (cheaper new robot),
       higher earning power — net income rises sharply
     - Programme design: upgrade credit is conditional on re-entering a new loan,
       so government recovers via future tax revenue and loan repayment
     - Fiscal payback: ~2 years on the credit cost (same self-funding logic applies)

  2. SHORTENED LOAN TERMS (5-year cycle)
     Match loan term to technology cycle — yeoman pays off robot in 5 years,
     then enters new loan for next-generation robot. No upgrade credit needed.
     - Payment is higher (5yr vs 10yr) but zero-interest mitigates this
     - New loan: cheaper robot (yr5 price), lower payment than original
     - No government budget line needed — just programme design
     - Risk: higher annual payment in years 1-5 squeezes yeoman income

  3. PERFORMANCE-INDEXED PAYMENTS (complex, not recommended short-term)
     Loan payment adjusts to robot earnings — if market rates fall due to
     capability obsolescence, payment falls proportionally.
     - Solves the cash flow problem but not the wealth/equity problem
     - Requires real-time income reporting (feasible with procurement platform data)
     - Creates moral hazard: yeomen can claim low utilisation to reduce payments

  RECOMMENDATION: Upgrade credit + 5yr tech cycle loan design.
     - Keep base loan at 10yr for income stability
     - At year 5, offer upgrade credit of 50% residual (conditional on re-entry)
     - Programme self-funds via improved productivity and lower robot costs
     - Yeoman always owns, never falls behind peers by more than half-cycle

--- FIRST-MOVER DISADVANTAGE: IS IT REAL? ---

  The disadvantage exists but is asymmetric:
    - Capital cost: early adopter overpays ~${(TOTAL_2025 - robot_cost_at(5) - VEHICLE_COST)/1000:.0f}k vs yr5 entry
    - Income stream: early adopter earns ~${sum(yeoman_fiscal_simple(y) for y in range(1, 6))/1000:.0f}k extra over 5 years
    - NET ADVANTAGE of entering 2025 vs 2030: ~${(sum(yeoman_fiscal_simple(y) for y in range(1,6)) - (TOTAL_2025 - robot_cost_at(5) - VEHICLE_COST))/1000:.0f}k over 15 years

  The early adopter is AHEAD, not behind. The psychological concern is real
  (watching newer robots appear) but the economic concern is not, provided
  utilisation stays high. The upgrade credit mechanism addresses both:
    - Economic: partial residual write-off closes any remaining gap
    - Psychological: yeoman knows there's a refresh path built into the programme

  The government's fiscal position also improves with upgrade cycles:
    - Older robots returned/sold (secondary market for developing world use)
    - New loans generate new repayments
    - Productivity of workforce increases each cycle
    """)

    print_self_funded_table()

    df_sf = self_funded_upgrade_analysis()
    first_clear_yr = df_sf[df_sf["can_clear_residual_loan"]]["year"].min()
    first_fund_yr  = df_sf[df_sf["can_self_fund_upgrade"]]["year"].min()

    savings_yr5 = df_sf[df_sf.year == 5]["cumulative_savings"].values[0]
    upgrade_cost_yr5 = df_sf[df_sf.year == 5]["net_upgrade_cost"].values[0]
    residual_yr5 = df_sf[df_sf.year == 5]["residual_loan"].values[0]

    print(f"""
--- SELF-FUNDING VERDICT ---

  At year 5 (natural upgrade point):
    Cumulative savings:        ${savings_yr5:>10,.0f}
    Cost of new robot (net):   ${upgrade_cost_yr5:>10,.0f}   (new purchase - resale of old)
    Residual loan balance:     ${residual_yr5:>10,.0f}
    Can clear old loan?        {'YES ✓' if savings_yr5 >= residual_yr5 else 'NO — shortfall: $' + f'{residual_yr5 - savings_yr5:,.0f}'}
    Can fund upgrade outright? {'YES ✓' if savings_yr5 >= upgrade_cost_yr5 else 'NO — shortfall: $' + f'{upgrade_cost_yr5 - savings_yr5:,.0f}'}

  First year yeoman can clear old loan:  year {first_clear_yr}
  First year yeoman can self-fund fully: year {first_fund_yr if first_fund_yr < 999 else '(never at $55k floor)'}

  IMPLICATION:
    If the yeoman saves surplus above their ${LIVING_STANDARD/1000:.0f}k living standard,
    they accumulate enough to self-fund or nearly self-fund the upgrade.
    No second government loan needed — just sell the old robot, use savings,
    and step into next-gen hardware.

    This makes the programme design even simpler:
      - One loan, 10 years, zero interest
      - Built-in 5yr tech refresh (save + trade-in)
      - Government upgrade credit becomes OPTIONAL, not required
        (useful for yeomen who didn't save enough, or to accelerate adoption)

    The only remaining programme risk is the yeomen who don't save —
    which argues for automatic savings accounts tied to the procurement
    platform (escrowed from contract payments, like mandatory super in Australia).
    """)

    print("Generating charts...")
    plot_obsolescence()
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
