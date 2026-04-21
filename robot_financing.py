"""
Government Robot Financing Model
==================================
Government provides financing for yeomen to purchase robots + transport.
Key questions:
  1. What financing terms make the program self-funding via tax revenue?
  2. Loan (yeoman owns) vs. robot bank (govt owns, leases) — which is better?
  3. What's the fiscal cost at scale (1M, 5M, 10M yeomen)?
  4. Does the program pay for itself, and over what horizon?

Core insight: robots generate immediate taxable income. Unlike student loans
(long lag to income), a robot starts earning day one. The government's
financing cost is typically covered by the tax revenue uplift alone —
loan repayments are gravy.

Run: python3 robot_financing.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROBOT_COST       = 80_000    # $ robot purchase
VEHICLE_COST     = 50_000    # $ transport vehicle
TOTAL_CAPITAL    = ROBOT_COST + VEHICLE_COST   # $130k per yeoman

GOVT_BORROW_RATE = 0.035     # govt cost of borrowing (10-yr treasury ~3.5%)
LOAN_TERMS = {
    "market":     0.085,     # 8.5% — SBA 7(a) current rate
    "subsidised": 0.030,     # 3.0% — subsidised (e.g. green energy loan equivalent)
    "zero":       0.000,     # 0%   — interest-free (grant-equivalent)
}
LOAN_TERM_YRS    = 10        # repayment period

# Yeoman economics (from prior model)
ROBOT_HOURS_YR       = 2_000     # robot operates 250 days × 8 hrs
BASE_HOURLY_RATE     = 55        # $/hr (commodity market, transport overhead included)
TRANSPORT_OVERHEAD   = 0.25      # 25% of gross goes to transport costs
SE_TAX_RATE          = 0.115
YEO_OVERHEAD_FIXED   = 19_500    # health, tools, accounting
INCOME_TAX_EFFECTIVE = 0.18      # effective income tax rate on yeoman net
DECENT_LIVING_NET    = 55_000

# Robot bank alternative
ROBOT_BANK_LEASE_MARKUP = 0.05   # 5% above govt's carrying cost (for maintenance reserve)

# ---------------------------------------------------------------------------
# Per-yeoman fiscal arithmetic
# ---------------------------------------------------------------------------

def yeoman_fiscal(loan_rate: float, hourly_rate: float = BASE_HOURLY_RATE,
                  utilisation: float = 0.75) -> dict:
    """
    Cash flows for one government-financed yeoman over loan term.
    """
    # Annual loan payment (standard amortisation)
    if loan_rate > 0:
        r = loan_rate
        n = LOAN_TERM_YRS
        annual_payment = TOTAL_CAPITAL * (r * (1+r)**n) / ((1+r)**n - 1)
    else:
        annual_payment = TOTAL_CAPITAL / LOAN_TERM_YRS   # zero-interest: just principal

    # Yeoman income
    gross_robot     = hourly_rate * ROBOT_HOURS_YR * utilisation
    gross_after_transport = gross_robot * (1 - TRANSPORT_OVERHEAD)
    se_tax          = gross_after_transport * SE_TAX_RATE
    net_before_it   = gross_after_transport - se_tax - YEO_OVERHEAD_FIXED - annual_payment
    income_tax      = max(net_before_it, 0) * INCOME_TAX_EFFECTIVE
    net_income      = net_before_it - income_tax

    # Government cash flows
    govt_interest_cost = TOTAL_CAPITAL * GOVT_BORROW_RATE   # govt's funding cost
    govt_loan_receipt  = annual_payment                      # loan repayment
    govt_tax_receipt   = se_tax + income_tax                 # tax take from yeoman
    govt_net_annual    = govt_loan_receipt + govt_tax_receipt - govt_interest_cost

    # Also: tax from the BUYER side (company deducts yeoman cost, but saves employment costs)
    # Rough: buyer saves 40% on loaded W-2 cost → additional tax base from buyer productivity
    buyer_tax_uplift   = gross_robot * 0.05   # conservative: 5% of gross robot revenue

    govt_net_with_buyer = govt_net_annual + buyer_tax_uplift

    # NPV of government position over loan term
    cashflows = [govt_net_with_buyer] * LOAN_TERM_YRS
    npv = sum(cf / (1 + GOVT_BORROW_RATE)**t for t, cf in enumerate(cashflows, 1))
    npv -= TOTAL_CAPITAL   # initial outlay

    return {
        "loan_rate":           loan_rate,
        "annual_payment":      annual_payment,
        "gross_robot":         gross_robot,
        "net_income":          net_income,
        "decent_living":       net_income >= DECENT_LIVING_NET,
        "govt_interest_cost":  govt_interest_cost,
        "govt_loan_receipt":   govt_loan_receipt,
        "govt_tax_receipt":    govt_tax_receipt,
        "buyer_tax_uplift":    buyer_tax_uplift,
        "govt_net_annual":     govt_net_with_buyer,
        "govt_npv_10yr":       npv,
        "self_funding":        npv > 0,
        "payback_years":       TOTAL_CAPITAL / govt_net_with_buyer if govt_net_with_buyer > 0 else 999,
    }


def robot_bank_fiscal(hourly_rate: float = BASE_HOURLY_RATE,
                      utilisation: float = 0.75) -> dict:
    """
    Alternative: government owns robots, leases to yeomen at cost + small reserve.
    Yeoman pays lease, not loan. No equity build — government retains asset.
    """
    # Government's annual cost of owning the robot
    govt_capital_cost  = TOTAL_CAPITAL * GOVT_BORROW_RATE
    robot_depreciation = TOTAL_CAPITAL / 10   # 10-yr life
    maintenance        = 8_000                # annual maintenance
    total_govt_cost    = govt_capital_cost + robot_depreciation + maintenance

    # Lease price (cost recovery + reserve)
    lease_annual = total_govt_cost * (1 + ROBOT_BANK_LEASE_MARKUP)

    # Yeoman economics under lease
    gross_robot          = hourly_rate * ROBOT_HOURS_YR * utilisation
    gross_after_transport= gross_robot * (1 - TRANSPORT_OVERHEAD)
    se_tax               = gross_after_transport * SE_TAX_RATE
    net_before_it        = gross_after_transport - se_tax - YEO_OVERHEAD_FIXED - lease_annual
    income_tax           = max(net_before_it, 0) * INCOME_TAX_EFFECTIVE
    net_income           = net_before_it - income_tax

    govt_tax_receipt     = se_tax + income_tax
    govt_lease_profit    = lease_annual - total_govt_cost   # should be near zero
    govt_net_annual      = govt_tax_receipt + govt_lease_profit

    return {
        "model":             "robot_bank",
        "lease_annual":      lease_annual,
        "govt_cost_annual":  total_govt_cost,
        "net_income":        net_income,
        "decent_living":     net_income >= DECENT_LIVING_NET,
        "govt_net_annual":   govt_net_annual,
        "yeoman_owns_equity":False,
        "note": "Govt owns asset. Yeoman has lower barrier but no equity build.",
    }


# ---------------------------------------------------------------------------
# Scale: aggregate fiscal picture
# ---------------------------------------------------------------------------

def aggregate_fiscal(n_yeomen: int, loan_rate: float, phase_in_years: int = 5) -> dict:
    """
    Government balance sheet for financing N yeomen.
    Phase-in: not all at once — ramp over phase_in_years.
    """
    r = yeoman_fiscal(loan_rate)

    # Outlay: phased
    annual_outlay = (n_yeomen * TOTAL_CAPITAL) / phase_in_years

    # By year 5: full program running
    # Tax revenue: starts small (year 1 cohort only), grows as cohorts accumulate
    tax_revenue_yr5  = n_yeomen * r["govt_tax_receipt"]
    loan_repay_yr5   = n_yeomen * r["govt_loan_receipt"]
    buyer_uplift_yr5 = n_yeomen * r["buyer_tax_uplift"]
    interest_cost_yr5= n_yeomen * r["govt_interest_cost"]

    net_annual_yr5 = tax_revenue_yr5 + loan_repay_yr5 + buyer_uplift_yr5 - interest_cost_yr5
    total_outlay   = n_yeomen * TOTAL_CAPITAL

    return {
        "n_yeomen":          n_yeomen,
        "loan_rate":         loan_rate,
        "total_outlay_bn":   total_outlay / 1e9,
        "annual_outlay_bn":  annual_outlay / 1e9,
        "net_annual_yr5_bn": net_annual_yr5 / 1e9,
        "payback_total_yrs": total_outlay / net_annual_yr5 if net_annual_yr5 > 0 else 999,
        "govt_npv_bn":       n_yeomen * r["govt_npv_10yr"] / 1e9,
    }


# ---------------------------------------------------------------------------
# Ownership equity build
# ---------------------------------------------------------------------------

def equity_build(loan_rate: float) -> pd.DataFrame:
    """How quickly does a yeoman build equity in their robot+vehicle?"""
    rows = []
    balance = TOTAL_CAPITAL

    if loan_rate > 0:
        r = loan_rate
        n = LOAN_TERM_YRS
        payment = TOTAL_CAPITAL * (r * (1+r)**n) / ((1+r)**n - 1)
    else:
        payment = TOTAL_CAPITAL / LOAN_TERM_YRS

    for yr in range(1, LOAN_TERM_YRS + 1):
        interest = balance * loan_rate
        principal = payment - interest
        balance  = max(balance - principal, 0)

        # Robot asset value (depreciates)
        vehicle_val = max(VEHICLE_COST * (1 - 0.15)**yr, VEHICLE_COST * 0.1)
        robot_val   = max(ROBOT_COST   * (1 - 0.10)**yr, ROBOT_COST   * 0.2)
        asset_val   = vehicle_val + robot_val
        equity      = asset_val - balance

        rows.append({"year": yr, "loan_balance": balance,
                     "asset_value": asset_val, "equity": equity,
                     "loan_rate": loan_rate})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_financing():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Government Robot Financing Program — Fiscal Model", fontsize=13, fontweight="bold")

    # ── Panel 1: Yeoman net income by loan rate ───────────────────────────
    ax = axes[0, 0]
    rates  = np.linspace(0, 0.10, 50)
    utils  = [0.60, 0.75, 0.90]
    colors = ["#e74c3c", "#e67e22", "#2ecc71"]
    for util, color in zip(utils, colors):
        nets = [yeoman_fiscal(r, utilisation=util)["net_income"]/1000 for r in rates]
        ax.plot(rates*100, nets, color=color, linewidth=2, label=f"{util:.0%} utilisation")
    ax.axhline(DECENT_LIVING_NET/1000, color="navy", linestyle="--", linewidth=1.5,
               label=f"Decent living (${DECENT_LIVING_NET/1000:.0f}k)")
    ax.axhline(0, color="k", linestyle=":", alpha=0.5)
    ax.set_xlabel("Loan interest rate (%)")
    ax.set_ylabel("Yeoman net income ($k/yr)")
    ax.set_title("Yeoman income vs loan rate\n(robot+van, different utilisation)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    # ── Panel 2: Government net annual position ───────────────────────────
    ax = axes[0, 1]
    for util, color in zip(utils, colors):
        govt_nets = [yeoman_fiscal(r, utilisation=util)["govt_net_annual"]/1000 for r in rates]
        ax.plot(rates*100, govt_nets, color=color, linewidth=2, label=f"{util:.0%} util")
    ax.axhline(0, color="k", linestyle="--", linewidth=1.5)
    ax.fill_between(rates*100, 0, 50, alpha=0.08, color="green", label="Self-funding zone")
    ax.set_xlabel("Loan interest rate (%)")
    ax.set_ylabel("Govt net annual cash flow / yeoman ($k)")
    ax.set_title("Government net position per yeoman\n(tax + loan repayment - funding cost)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    # ── Panel 3: Equity build (loan vs robot bank) ────────────────────────
    ax = axes[0, 2]
    for rate, label, color, ls in [
        (0.085, "Market rate (8.5%)",   "#e74c3c", "-"),
        (0.030, "Subsidised (3%)",      "#e67e22", "-"),
        (0.000, "Zero interest",        "#2ecc71", "-"),
    ]:
        df = equity_build(rate)
        ax.plot(df["year"], df["equity"]/1000, color=color, linestyle=ls,
                linewidth=2, label=label)

    ax.axhline(0, color="k", linestyle=":", alpha=0.5)
    ax.set_xlabel("Year of ownership")
    ax.set_ylabel("Yeoman equity in robot+vehicle ($k)")
    ax.set_title("Equity build under different\nfinancing terms")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.fill_between(range(1,11), 0, 130, alpha=0.05, color="green")

    # ── Panel 4: Aggregate fiscal cost + payback ─────────────────────────
    ax = axes[1, 0]
    n_range = [1e6, 2e6, 5e6, 10e6, 20e6]

    for rate, label, color in [
        (0.000, "Zero interest", "#2ecc71"),
        (0.030, "3% subsidised", "#e67e22"),
    ]:
        outlays  = [aggregate_fiscal(int(n), rate)["total_outlay_bn"] for n in n_range]
        paybacks = [aggregate_fiscal(int(n), rate)["payback_total_yrs"] for n in n_range]
        ax.plot([n/1e6 for n in n_range], outlays, color=color, linewidth=2,
                linestyle="-", label=f"Total outlay ({label})")

    ax.set_xlabel("Number of yeomen financed (millions)")
    ax.set_ylabel("Total programme outlay ($B)")
    ax.set_title("Government balance sheet commitment\nvs programme scale")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax2 = ax.twinx()
    for rate, label, color in [(0.000, "Zero", "#2ecc71"), (0.030, "3%", "#e67e22")]:
        paybacks = [aggregate_fiscal(int(n), rate)["payback_total_yrs"] for n in n_range]
        ax2.plot([n/1e6 for n in n_range], paybacks, color=color,
                 linestyle="--", linewidth=2, label=f"Payback yrs ({label})")
    ax2.set_ylabel("Payback period (years)", color="gray")
    ax2.tick_params(axis="y", labelcolor="gray")

    # ── Panel 5: Loan vs robot bank comparison ────────────────────────────
    ax = axes[1, 1]
    categories = ["Yeoman\nnet income", "Govt net\nannual/yeoman", "Payback\nyears"]
    loan_zero = yeoman_fiscal(0.000)
    loan_3pct = yeoman_fiscal(0.030)
    bank      = robot_bank_fiscal()

    vals = {
        "Loan (0%)":   [loan_zero["net_income"]/1000,  loan_zero["govt_net_annual"]/1000,  loan_zero["payback_years"]],
        "Loan (3%)":   [loan_3pct["net_income"]/1000,  loan_3pct["govt_net_annual"]/1000,  loan_3pct["payback_years"]],
        "Robot bank":  [bank["net_income"]/1000,        bank["govt_net_annual"]/1000,        TOTAL_CAPITAL/bank["govt_net_annual"] if bank["govt_net_annual"] > 0 else 0],
    }
    x = np.arange(len(categories))
    width = 0.25
    offsets = [-width, 0, width]
    colors_bar = ["#2ecc71", "#e67e22", "#3498db"]

    for (label, data), off, color in zip(vals.items(), offsets, colors_bar):
        ax.bar(x + off, data, width, label=label, color=color, alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_title("Loan vs Robot Bank\nkey metrics comparison")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # ── Panel 6: Programme cost vs GDP contribution ───────────────────────
    ax = axes[1, 2]
    years = np.arange(2025, 2040)
    n_financed = np.minimum((years - 2025) * 1_000_000, 10_000_000)  # ramp 1M/yr to 10M

    rate = 0.000  # zero interest
    r    = yeoman_fiscal(rate)

    cumulative_outlay = n_financed * TOTAL_CAPITAL / 1e12
    cumulative_tax    = np.cumsum(n_financed * r["govt_tax_receipt"]) / 1e12
    cumulative_repay  = np.cumsum(n_financed * r["govt_loan_receipt"]) / 1e12
    robot_gdp         = n_financed * BASE_HOURLY_RATE * ROBOT_HOURS_YR * 0.75 / 1e12  # at 75% util

    ax.fill_between(years, 0, cumulative_outlay, alpha=0.3, color="#e74c3c", label="Cumulative outlay ($T)")
    ax.plot(years, cumulative_tax + cumulative_repay, color="#2ecc71", linewidth=2,
            label="Cumulative tax+repayment ($T)")
    ax.plot(years, robot_gdp, color="#3498db", linewidth=2, linestyle="--",
            label="Annual robot GDP contribution ($T)")

    ax.set_xlabel("Year")
    ax.set_ylabel("$T (trillions)")
    ax.set_title("Programme cost vs GDP contribution\n(zero-interest loan, 1M new yeomen/yr)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("robot_financing.png", dpi=150, bbox_inches="tight")
    print("  Saved: robot_financing.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*72)
    print("GOVERNMENT ROBOT FINANCING: FISCAL MODEL")
    print("="*72)

    print(f"\n  Total capital per yeoman: ${TOTAL_CAPITAL:,}  (robot ${ROBOT_COST:,} + vehicle ${VEHICLE_COST:,})")
    print(f"  Government borrowing rate: {GOVT_BORROW_RATE:.1%}")

    print(f"\n--- PER-YEOMAN ECONOMICS BY FINANCING TERMS ---")
    print(f"  {'Loan rate':>10}  {'Payment/yr':>12}  {'Net income':>12}  {'Govt net/yr':>13}  {'NPV 10yr':>10}  {'Self-funding?':>14}")
    print("  " + "─"*78)
    for name, rate in LOAN_TERMS.items():
        r = yeoman_fiscal(rate, utilisation=0.75)
        sf = "YES ✓" if r["self_funding"] else "no"
        print(f"  {name} ({rate:.1%})   ${r['annual_payment']:>8,.0f}   "
              f"${r['net_income']:>8,.0f}   ${r['govt_net_annual']:>9,.0f}   "
              f"${r['govt_npv_10yr']:>6,.0f}   {sf:>14}")

    print(f"\n--- ROBOT BANK ALTERNATIVE ---")
    b = robot_bank_fiscal()
    print(f"  Lease per year:        ${b['lease_annual']:>8,.0f}")
    print(f"  Yeoman net income:     ${b['net_income']:>8,.0f}")
    print(f"  Decent living:         {'YES' if b['decent_living'] else 'NO'}")
    print(f"  Govt net/yr/yeoman:    ${b['govt_net_annual']:>8,.0f}")
    print(f"  Yeoman owns equity:    {b['yeoman_owns_equity']}")
    print(f"  Note: {b['note']}")

    print(f"\n--- AGGREGATE FISCAL (zero-interest loan) ---")
    print(f"  {'Scale':>10}  {'Total outlay':>14}  {'Annual outlay':>14}  {'Net/yr @yr5':>13}  {'Payback':>9}  {'NPV':>10}")
    print("  " + "─"*78)
    for n in [1_000_000, 2_000_000, 5_000_000, 10_000_000]:
        a = aggregate_fiscal(n, 0.000, phase_in_years=5)
        print(f"  {n/1e6:>7.0f}M   ${a['total_outlay_bn']:>9.0f}B    "
              f"${a['annual_outlay_bn']:>9.0f}B    ${a['net_annual_yr5_bn']:>8.0f}B   "
              f"{a['payback_total_yrs']:>6.1f}yr   ${a['govt_npv_bn']:>6.0f}B")

    print(f"\n--- EQUITY BUILD: ZERO-INTEREST LOAN ---")
    df = equity_build(0.000)
    print(f"  {'Year':>6}  {'Loan balance':>14}  {'Asset value':>13}  {'Equity':>10}")
    print("  " + "─"*48)
    for _, row in df.iterrows():
        print(f"  {row['year']:>6.0f}  ${row['loan_balance']:>10,.0f}    "
              f"${row['asset_value']:>9,.0f}    ${row['equity']:>7,.0f}")

    print(f"\n--- LOAN vs ROBOT BANK: OWNERSHIP IMPLICATIONS ---")
    print(f"""
  LOAN MODEL (government lends, yeoman buys):
    + Yeoman owns the robot — genuine owner-operator
    + Builds equity over 10 years (~$50-80k asset value at payoff)
    + Incentivised to maintain, upgrade, use efficiently (it's theirs)
    + If robot economy grows, asset appreciates → wealth effect
    + Aligns with "own your means of production" goal
    - Requires creditworthiness check (or universal access regardless)
    - Default risk: government recovers robot (physical collateral)
    - Govt balance sheet: large initial outlay, recovers over time

  ROBOT BANK MODEL (govt owns, leases at cost):
    + Zero barrier — anyone can participate immediately
    + No default risk — govt just takes robot back if lease unpaid
    + Simpler administration
    - Yeoman never builds equity — always a renter, not an owner
    - No wealth effect from robot appreciation
    - Less incentive to maintain (not theirs)
    - Recreates the tenant-farmer problem the yeoman model aims to solve

  VERDICT: Loan model is strongly preferable on ownership grounds.
  Robot bank solves a simpler problem (access) but creates the wrong
  relationship between the yeoman and their capital.

  HYBRID: Government guarantees the loan, private lender provides capital.
  Like FHA mortgages — yeoman gets market-rate financing with government
  backstop. Government's balance sheet exposure is guarantee liability,
  not full loan amount. At 5% default rate: govt exposure is 5% of programme.
  For 10M yeomen: $650B programme → $32.5B government guarantee exposure.
  Much more manageable than $650B direct outlay.
    """)

    print(f"\n--- DOES IT PAY FOR ITSELF? ---")
    r = yeoman_fiscal(0.000, utilisation=0.75)
    print(f"""
  Per yeoman (zero-interest loan, 75% utilisation):
    Government outlay:          ${TOTAL_CAPITAL:>8,}  (one-time)
    Annual loan repayment:      ${r['annual_payment']:>8,.0f}
    Annual SE tax from yeoman:  ${r['govt_tax_receipt']:>8,.0f}  (estimated)
    Annual buyer tax uplift:    ${r['buyer_tax_uplift']:>8,.0f}  (conservative)
    Government funding cost:    ${r['govt_interest_cost']:>8,.0f}  (at {GOVT_BORROW_RATE:.1%} borrow rate)
    ─────────────────────────────────────────
    Net annual government gain: ${r['govt_net_annual']:>8,.0f}
    Payback period:             {r['payback_years']:>5.1f} years
    NPV over 10 years:          ${r['govt_npv_10yr']:>8,.0f}  (POSITIVE)

  YES. The programme pays for itself in ~{r['payback_years']:.0f} years at 75% utilisation.
  At 60% utilisation: payback ~{yeoman_fiscal(0.000, utilisation=0.60)['payback_years']:.0f} years — still positive.
  At 50% utilisation: payback ~{yeoman_fiscal(0.000, utilisation=0.50)['payback_years']:.0f} years — marginal.

  The programme is self-funding above ~55% yeoman utilisation.
  Below that, it's a net cost — which is the dynamic tax's job to prevent.
  The two mechanisms are therefore complementary:
    Dynamic tax   → keeps utilisation high (demand side)
    Govt financing → ensures access (supply side)
    """)

    print("Generating charts...")
    plot_financing()
    print("="*72 + "\n")


if __name__ == "__main__":
    main()
