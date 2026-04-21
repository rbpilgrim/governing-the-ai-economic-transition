"""
Stock-Flow Consistent (SFC) Model — AI Economic Transition
===========================================================
Godley-Lavoie style SFC with 6 household types, 2 firm sectors,
government, and banking sector.

Every financial flow appears in the transaction matrix as both a
payment and an income — the fundamental SFC accounting identity.
Row and column sums = 0 every period.

Household behavioural equations are implemented as fixed rules here
but are designed to be swapped out for LLM decisions in model_sfc_llm.py.

Sectors
-------
Households (6 types):
  H1  Concentrated capital owners   (top 1-10%, low MPC)
  H2  Yeomen enterprise operators   (small AI-augmented firms)
  H3  DAO / commons contributors    (knowledge commons income)
  H4  Displaced workers on UBI      (no market income)
  H5  Compute dividend recipients   (public AI pool dividend)
  H6  Human economy workers         (care, craft, services)

Firms (2 sectors):
  FA  Automated sector  (AI/robot-driven production, low labour)
  FH  Human economy     (demand-determined, labour-intensive)

Government (G):  taxes, transfers, bond issuance
Banks (B):       deposit-taking, lending, reserve management

Stocks tracked
--------------
Each household type: deposits, equity holdings, mortgage/consumer debt
Firms: capital stock, bank loans
Government: bonds outstanding (= debt)
Banks: loans (asset), deposits (liability), reserves, bonds held
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Params:
    # ── Economy baseline ─────────────────────────────────────────────────────
    gdp_0: float         = 28_000.0   # $bn nominal GDP 2025
    n_workers: float     = 160.0      # M workers
    n_adults: float      = 260.0      # M adults (dividend recipients)
    base_year: int       = 2025
    n_years: int         = 35

    # ── Household population shares ───────────────────────────────────────────
    # Fraction of adult population in each type (sum to 1)
    pop_h1: float = 0.10   # concentrated capital owners (top 10%)
    pop_h2: float = 0.08   # yeomen operators
    pop_h3: float = 0.02   # DAO contributors
    pop_h4: float = 0.35   # displaced workers (grows with automation)
    pop_h5: float = 0.00   # compute dividend only (set by public_ai_frac)
    pop_h6: float = 0.45   # human economy workers (residual)

    # ── Initial income shares ─────────────────────────────────────────────────
    labour_share_0: float  = 0.64    # labour share of GDP 2025
    capital_share_0: float = 0.36

    # ── Automation (S-curve parameters) ──────────────────────────────────────
    know_ceiling: float    = 0.88    # max fraction of knowledge work automated
    phys_ceiling: float    = 0.68    # max fraction of physical work automated
    phys_lag: int          = 7       # physical lags knowledge by N years
    auto_mid: float        = 5.0     # years to 50% knowledge automation

    # ── Tax-drag parameters ───────────────────────────────────────────────────
    tax_drag: float        = 0.0     # fraction by which automation rate slows per unit of
                                      # capital tax burden. 0.0 = no effect, 0.3 = aggressive drag.
    rent_fraction: float   = 1.0     # fraction of AI capital returns that are pure rent.
                                      # 1.0 = all returns are rent (full drag applies).
                                      # 0.3 = only 30% is rent; drag reduced proportionally.

    # ── Price dynamics ────────────────────────────────────────────────────────
    deflation_know: float  = 0.10    # nominal price deflation in knowledge sector
    deflation_phys: float  = 0.06    # nominal price deflation in physical sector
    baumol_rate: float     = 0.04    # Baumol inflation in human services
    monopoly_rent: float   = 0.00    # fraction of productivity NOT passed through
                                      # 0 = full competition, 0.5 = half monopoly
                                      # Reduces nominal deflation under concentration

    # ── Policy scenario ───────────────────────────────────────────────────────
    yeomen_target: float   = 0.35    # target fraction of capital income to yeomen
    dao_frac: float        = 0.10    # fraction of knowledge capital to DAOs
    public_ai_frac: float  = 0.00    # fraction of AI capital as public infrastructure
    tax_k: float           = 0.35    # statutory capital tax rate
    tax_labour: float      = 0.25    # labour income tax rate
    tax_vat: float         = 0.12    # VAT rate
    enforcement: float     = 1.00    # fraction of tax_k collectible
    levy_prog: float       = 0.00    # compute levy progressivity
    dao_govt_rate: float   = 0.00    # govt daoification rate
    policy_ramp: int       = 10      # years to ramp to target policy

    # ── Household balance sheets (2025 baseline, $k per person) ──────────────
    wealth_h1_0: float  = 1_200.0   # concentrated capital: high wealth
    wealth_h2_0: float  =   180.0   # yeomen: moderate business equity
    wealth_h3_0: float  =    40.0   # DAO contributors: modest
    wealth_h4_0: float  =    15.0   # displaced workers: low savings
    wealth_h5_0: float  =    15.0   # compute dividend only
    wealth_h6_0: float  =    60.0   # human economy workers

    debt_h1_0: float    =    80.0   # mortgage + consumer debt $k/person
    debt_h2_0: float    =   120.0   # business debt
    debt_h4_0: float    =    25.0   # consumer debt (highest burden relative to income)
    debt_h6_0: float    =    40.0   # mortgage

    # ── Financial sector ──────────────────────────────────────────────────────
    interest_rate_loan: float   = 0.055   # bank lending rate
    interest_rate_deposit: float= 0.025   # deposit rate
    interest_rate_bond: float   = 0.045   # government bond rate
    debt_initial_bn: float      = 34_000  # federal debt outstanding

    # ── Fixed MPC rules (replaced by LLM in model_sfc_llm.py) ───────────────
    # These are the baseline behavioural equations.
    # MPC = fraction of disposable income consumed each period.
    mpc_h1: float = 0.20    # capital owners: low MPC (save / reinvest)
    mpc_h2: float = 0.75    # yeomen: labour-like MPC
    mpc_h3: float = 0.78    # DAO contributors
    mpc_h4: float = 0.92    # displaced workers: high MPC (liquidity constrained)
    mpc_h5: float = 0.85    # compute dividend recipients
    mpc_h6: float = 0.88    # human economy workers

    # Fraction of consumption going to human services vs automated goods
    human_svc_h1: float = 0.30
    human_svc_h2: float = 0.12
    human_svc_h3: float = 0.14
    human_svc_h4: float = 0.10
    human_svc_h5: float = 0.12
    human_svc_h6: float = 0.10

    # ── Home production buffer ────────────────────────────────────────────────
    home_prod_k: float    = 6.0     # $k/yr value for land-access households
    land_access_frac: float = 0.40  # fraction of displaced with land access

    # ── Government ────────────────────────────────────────────────────────────
    govt_base_pct: float  = 0.215   # non-interest spending as % of nominal GDP


# ─────────────────────────────────────────────────────────────────────────────
# STATE — stocks at each point in time
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class State:
    """All stock variables. Updated each period from flows."""
    year: int = 2025

    # Household wealth ($bn total for each type)
    wealth: np.ndarray = field(default_factory=lambda: np.zeros(6))
    debt:   np.ndarray = field(default_factory=lambda: np.zeros(6))

    # Firm capital stocks ($bn)
    capital_auto: float   = 0.0
    capital_human: float  = 0.0

    # Government debt ($bn)
    govt_debt: float = 34_000.0

    # Bank balance sheet ($bn)
    bank_loans:    float = 0.0
    bank_deposits: float = 0.0
    bank_bonds:    float = 0.0

    # Automation level (0-1)
    know_auto: float = 0.0
    phys_auto: float = 0.0

    # Population in each household type (millions)
    pop: np.ndarray = field(default_factory=lambda: np.zeros(6))

    # Governance quality (0.1 to 1.0); starts at 1.0, decays with inequality
    governance: float = 1.0


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def s_curve(t: float, ceiling: float, speed: float, midpoint: float) -> float:
    """Logistic S-curve normalised to 0 at t=0."""
    raw  = ceiling / (1.0 + np.exp(-speed * (t - midpoint)))
    init = ceiling / (1.0 + np.exp(-speed * (0 - midpoint)))
    return float(np.clip((raw - init) * (ceiling / (ceiling - init)), 0.0, ceiling))


def ramp(t: int, ramp_years: int) -> float:
    return min(t / ramp_years, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTION FLOW MATRIX
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Flows:
    """
    All flows in one period ($bn).
    Sign convention: positive = inflow to that sector.
    The transaction matrix enforces: sum of all flows = 0.
    """
    # Income flows
    wages_auto:    float = 0.0   # wages from automated sector
    wages_human:   float = 0.0   # wages from human economy
    dividends:     float = 0.0   # concentrated capital dividends
    yeomen_income: float = 0.0   # yeomen enterprise net income
    dao_income:    float = 0.0   # commons DAO income
    compute_div:   float = 0.0   # public AI pool dividend (total $bn)
    ubi:           float = 0.0   # government UBI transfers ($bn total)

    # Consumption flows ($bn)
    cons_auto_goods:   float = 0.0   # spending on automated goods
    cons_human_svcs:   float = 0.0   # spending on human services

    # Government
    tax_labour:    float = 0.0
    tax_capital:   float = 0.0
    tax_vat:       float = 0.0
    govt_spending: float = 0.0   # non-transfer spending
    interest_govt: float = 0.0   # interest on government debt

    # Financial
    new_loans:     float = 0.0   # new bank lending to households
    loan_repay:    float = 0.0   # loan repayments
    interest_paid: float = 0.0   # interest paid by households to banks
    interest_recv: float = 0.0   # interest received by households on deposits

    # By household type ($bn)
    income_by_hh:  np.ndarray = field(default_factory=lambda: np.zeros(6))
    cons_by_hh:    np.ndarray = field(default_factory=lambda: np.zeros(6))
    saving_by_hh:  np.ndarray = field(default_factory=lambda: np.zeros(6))

    # Diagnostics
    gdp_nom:       float = 0.0
    gdp_real_idx:  float = 100.0
    gini_proxy:    float = 0.0
    welfare_k:     float = 0.0   # effective welfare floor $k/yr
    tax_leakage:   float = 0.0
    debt_gdp:      float = 0.0
    interest_pct_rev: float = 0.0
    fiscal_space:  float = 0.0
    ubi_per_person: float = 0.0
    compute_div_k: float = 0.0
    know_auto_pct: float = 0.0
    phys_auto_pct: float = 0.0
    labour_share:  float = 0.0
    governance:    float = 1.0
    effective_auto_mid: float = 0.0  # actual S-curve midpoint after tax drag


# ─────────────────────────────────────────────────────────────────────────────
# HOUSEHOLD BEHAVIOUR  (override this class in model_sfc_llm.py)
# ─────────────────────────────────────────────────────────────────────────────

class HouseholdBehaviour:
    """
    Fixed-rule household behavioural equations.
    In model_sfc_llm.py this class is subclassed and decide() is
    replaced with LLM calls.
    """

    def __init__(self, params: Params):
        self.p = params
        self.mpcs = np.array([
            params.mpc_h1, params.mpc_h2, params.mpc_h3,
            params.mpc_h4, params.mpc_h5, params.mpc_h6,
        ])
        self.human_svcs = np.array([
            params.human_svc_h1, params.human_svc_h2, params.human_svc_h3,
            params.human_svc_h4, params.human_svc_h5, params.human_svc_h6,
        ])

    def decide(
        self,
        hh_idx: int,
        income_k: float,          # disposable income $k/yr
        wealth_k: float,          # net wealth $k
        debt_k: float,            # outstanding debt $k
        interest_burden_k: float, # annual interest payments $k
        unemployment: bool,       # is this HH type primarily unemployed?
        economic_context: dict,   # macro conditions (passed to LLM)
        t: int,                   # year index
    ) -> dict:
        """
        Returns spending decision for one household type.

        Override this method in LLM subclass.
        Fixed rules here implement standard post-Keynesian consumption function:
          C = alpha1 * YD + alpha2 * W
        where YD = disposable income, W = wealth (Godley-Lavoie SIM model).
        """
        p = self.p

        # Wealth effect: consume small fraction of wealth (portfolio rebalancing)
        wealth_effect = 0.04 * wealth_k   # 4% of wealth per year

        # Income consumption
        mpc = self.mpcs[hh_idx]

        # Liquidity constraint: if income fell sharply, constrained households
        # try to maintain consumption by drawing on savings or borrowing
        if unemployment and income_k < 20.0 and wealth_k > 0:
            # Draw down savings to smooth consumption
            mpc = min(mpc + 0.10, 0.98)

        # Debt service reduces disposable income
        disposable_k = max(income_k - interest_burden_k, 0)

        consume_k = mpc * disposable_k + wealth_effect * 0.5
        consume_k = max(consume_k, 0)

        human_svc_share = self.human_svcs[hh_idx]

        # Adaptive: as income falls, shift more toward cheap automated goods
        if income_k < 15.0:
            human_svc_share = human_svc_share * 0.7  # less premium human services

        return {
            "consume_k":          consume_k,
            "human_svc_share":    human_svc_share,
            "auto_goods_share":   1.0 - human_svc_share,
            "borrow":             debt_k < 30.0 and income_k < 15.0,
            "borrow_k":           5.0 if (debt_k < 30.0 and income_k < 15.0) else 0.0,
            "reasoning":          "fixed-rule: Godley-Lavoie SIM consumption function",
        }


# ─────────────────────────────────────────────────────────────────────────────
# CORE SFC MODEL
# ─────────────────────────────────────────────────────────────────────────────

class SFCModel:

    def __init__(self, params: Params, behaviour: Optional[HouseholdBehaviour] = None):
        self.p = params
        self.behaviour = behaviour or HouseholdBehaviour(params)
        self.state = self._init_state()
        self.history: list[dict] = []

    def _init_state(self) -> State:
        p = self.p
        pop = np.array([p.pop_h1, p.pop_h2, p.pop_h3,
                        p.pop_h4, p.pop_h5, p.pop_h6]) * p.n_adults  # millions

        wealth_0_k = np.array([p.wealth_h1_0, p.wealth_h2_0, p.wealth_h3_0,
                                p.wealth_h4_0, p.wealth_h5_0, p.wealth_h6_0])
        debt_0_k   = np.array([p.debt_h1_0,   p.debt_h2_0,   0.0,
                                p.debt_h4_0,   0.0,           p.debt_h6_0])

        # Convert $k/person to $bn (pop in millions, k × M = bn)
        wealth_bn = wealth_0_k * pop / 1000.0
        debt_bn   = debt_0_k   * pop / 1000.0

        capital_gdp = 3.5
        auto_share  = 0.70   # fraction of capital in automated sector

        return State(
            year         = p.base_year,
            wealth       = wealth_bn,
            debt         = debt_bn,
            capital_auto = p.gdp_0 * capital_gdp * auto_share,
            capital_human= p.gdp_0 * capital_gdp * (1 - auto_share),
            govt_debt    = p.debt_initial_bn,
            bank_loans   = debt_bn.sum(),
            bank_deposits= wealth_bn.sum() * 0.30,  # ~30% of wealth held as deposits
            bank_bonds   = p.debt_initial_bn * 0.20, # banks hold ~20% of govt bonds
            pop          = pop,
        )

    # ── Production and income ─────────────────────────────────────────────────

    def _automation(self, t: int) -> tuple[float, float, float]:
        p = self.p
        # Tax drag: higher tax burden on capital slows automation adoption.
        # Only the rent portion of capital returns is subject to drag;
        # required returns (1 - rent_fraction) are unaffected.
        effective_tax_burden = p.tax_k * p.enforcement * self.state.governance * p.rent_fraction
        effective_auto_mid = p.auto_mid * (1.0 + effective_tax_burden * p.tax_drag)
        ka = s_curve(t, p.know_ceiling, 0.50, effective_auto_mid)
        pa = s_curve(t, p.phys_ceiling, 0.28, effective_auto_mid + p.phys_lag)
        return ka, pa, effective_auto_mid

    def _nominal_output(self, t: int, know_auto: float, phys_auto: float) -> tuple[float, float]:
        """Nominal output of automated sectors. Monopoly rent reduces deflation."""
        p = self.p
        # Effective deflation rate: reduced by monopoly rent (firms keep productivity gains)
        eff_deflation_know = p.deflation_know * (1.0 - p.monopoly_rent)
        eff_deflation_phys = p.deflation_phys * (1.0 - p.monopoly_rent)
        know_nom = p.gdp_0 * 0.40 * (1 - eff_deflation_know) ** t
        phys_nom = p.gdp_0 * 0.30 * (1 - eff_deflation_phys) ** t
        return know_nom, phys_nom

    def _split_income(
        self, t: int, know_nom: float, phys_nom: float,
        know_auto: float, phys_auto: float,
    ) -> dict:
        """Split sectoral output into labour, capital, and ownership tiers."""
        p = self.p
        r = ramp(t, p.policy_ramp)

        yeomen_t    = 0.08 + (p.yeomen_target - 0.08) * r
        dao_frac_t  = 0.00 + (p.dao_frac      - 0.00) * r
        pub_ai_t    = 0.00 + (p.public_ai_frac - 0.00) * r
        tax_k_t     = 0.21 + (p.tax_k          - 0.21) * r

        # Progressive levy endogenous yeomen uplift
        levy_bonus  = p.levy_prog * 0.25 * r
        yeomen_eff  = min(yeomen_t + levy_bonus, 0.85)

        # Labour income (remaining workers)
        know_labor = know_nom * (1 - know_auto) * 0.60
        phys_labor = phys_nom * (1 - phys_auto) * 0.58

        # Gross capital income
        know_cap = know_nom * (know_auto * 0.60 + 0.40)
        phys_cap = phys_nom * (phys_auto * 0.58 + 0.42)
        gross_cap = know_cap + phys_cap

        # Public AI pool
        compute_pool   = gross_cap * pub_ai_t
        private_cap    = gross_cap * (1 - pub_ai_t)
        compute_div    = compute_pool * 0.70
        compute_subsidy= compute_pool * 0.20
        compute_overhead= compute_pool * 0.10

        # Split private capital
        yeomen_inc  = private_cap * yeomen_eff
        dao_inc     = know_cap * (1 - pub_ai_t) * (1 - yeomen_eff) * dao_frac_t
        conc_cap    = (know_cap * (1 - pub_ai_t) * (1 - yeomen_eff) * (1 - dao_frac_t) +
                       phys_cap * (1 - pub_ai_t) * (1 - yeomen_eff))

        # Government daoification
        disp_frac   = (know_auto + phys_auto) / 2.0
        govt_dao_inc= p.dao_govt_rate * conc_cap * disp_frac
        conc_cap   -= govt_dao_inc

        # Monopoly rent: if concentrated, less passes through → higher nominal income
        # captured by concentrated owners as rent (already in conc_cap via lower deflation)

        return {
            "know_labor": know_labor, "phys_labor": phys_labor,
            "yeomen_inc": yeomen_inc, "dao_inc": dao_inc,
            "conc_cap": conc_cap, "govt_dao_inc": govt_dao_inc,
            "compute_div": compute_div, "compute_subsidy": compute_subsidy,
            "compute_overhead": compute_overhead,
            "compute_div_k": compute_div / p.n_adults,
            "yeomen_eff": yeomen_eff, "pub_ai_t": pub_ai_t,
            "tax_k_t": tax_k_t,
        }

    # ── Government finances ───────────────────────────────────────────────────

    def _taxes(self, inc: dict, auto_labor: float, gdp_nom_pass1: float,
               tax_k_t: float) -> dict:
        p    = self.p
        # Effective enforcement is scaled by governance quality
        eff_enforcement = p.enforcement * self.state.governance
        levy_mult = 1.0 + p.levy_prog * 0.50
        eff_rate  = tax_k_t * eff_enforcement * levy_mult

        tax_conc   = eff_rate * inc["conc_cap"]
        tax_yeomen = p.tax_labour * inc["yeomen_inc"]
        tax_dao    = p.tax_labour * inc["dao_inc"]
        tax_labor  = p.tax_labour * auto_labor
        tax_vat    = p.tax_vat * gdp_nom_pass1 * 0.65
        tax_wealth = 0.01 * self.state.capital_auto  # wealth tax on AI capital

        total = tax_conc + tax_yeomen + tax_dao + tax_labor + tax_vat + tax_wealth
        leakage = p.tax_k * (1 - eff_enforcement) * inc["conc_cap"]

        return {
            "tax_conc": tax_conc, "tax_yeomen": tax_yeomen, "tax_dao": tax_dao,
            "tax_labor": tax_labor, "tax_vat": tax_vat, "total": total,
            "leakage": leakage,
        }

    # ── Main step ─────────────────────────────────────────────────────────────

    def step(self, t: int) -> Flows:
        p   = self.p
        s   = self.state
        f   = Flows()

        # 1. Automation levels
        know_auto, phys_auto, eff_auto_mid = self._automation(t)
        f.know_auto_pct = know_auto * 100
        f.phys_auto_pct = phys_auto * 100
        f.effective_auto_mid = eff_auto_mid

        # 2. Nominal output
        know_nom, phys_nom = self._nominal_output(t, know_auto, phys_auto)
        govt_nom = p.gdp_0 * 0.23 * (1.02 ** t)

        # 3. Income split
        inc = self._split_income(t, know_nom, phys_nom, know_auto, phys_auto)
        auto_labor = inc["know_labor"] + inc["phys_labor"]

        # 4. First-pass government (before human economy sized)
        interest_bn = s.govt_debt * p.interest_rate_bond
        taxes_p1 = self._taxes(inc, auto_labor,
                                know_nom + phys_nom + govt_nom, inc["tax_k_t"])
        existing_spend_p1 = (p.govt_base_pct * (know_nom + phys_nom + govt_nom)
                             + interest_bn + inc["compute_overhead"])
        redistributable_p1 = max(taxes_p1["total"] - existing_spend_p1, 0.0)

        # Displacement
        know_disp = p.n_workers * 0.45 * know_auto
        phys_disp = p.n_workers * 0.40 * phys_auto
        total_disp = know_disp + phys_disp

        # UBI (first pass)
        ubi_p1 = redistributable_p1 / max(total_disp, 0.5) if total_disp > 0.5 else 0.0

        # 5. Household income (per person, $k/yr)
        # Assign income to household types
        # H1: concentrated capital dividends
        # H2: yeomen income
        # H3: DAO income
        # H4: UBI (displaced workers)
        # H5: compute dividend
        # H6: human economy wages (derived below)
        income_k = np.array([
            inc["conc_cap"] / (s.pop[0] + 0.001),          # H1: $bn / M = $k/person
            inc["yeomen_inc"] / (s.pop[1] + 0.001),         # H2
            inc["dao_inc"] / (s.pop[2] + 0.001),            # H3
            ubi_p1 + inc["compute_div_k"],                   # H4: UBI + dividend
            inc["compute_div_k"],                            # H5: dividend only
            0.0,                                             # H6: set after human economy
        ])

        # 6. Household consumption decisions
        wealth_k = s.wealth / (s.pop / 1000.0 + 0.001)   # $bn / M = $k/person
        debt_k   = s.debt   / (s.pop / 1000.0 + 0.001)

        cons_by_hh    = np.zeros(6)
        human_svc_frac= np.zeros(6)
        new_debt      = np.zeros(6)

        economic_context = {
            "year":          p.base_year + t,
            "know_auto_pct": f.know_auto_pct,
            "phys_auto_pct": f.phys_auto_pct,
            "ubi_k":         ubi_p1,
            "compute_div_k": inc["compute_div_k"],
            "total_displaced_m": total_disp,
        }

        for i in range(5):   # H1-H5; H6 set after human economy
            interest_k = debt_k[i] * p.interest_rate_loan
            decision = self.behaviour.decide(
                hh_idx           = i,
                income_k         = float(income_k[i]),
                wealth_k         = float(wealth_k[i]),
                debt_k           = float(debt_k[i]),
                interest_burden_k= float(interest_k),
                unemployment     = (i == 3),   # H4 = displaced workers
                economic_context = economic_context,
                t                = t,
            )
            cons_by_hh[i]    = decision["consume_k"]
            human_svc_frac[i]= decision["human_svc_share"]
            if decision.get("borrow", False):
                new_debt[i] = decision.get("borrow_k", 0.0)

        # 7. Derive human economy from demand
        # Human services demand ($bn) = sum over HH types of:
        #   (consumption × human_svc_share × population)
        pop_m = s.pop  # millions
        human_demand_bn = sum(
            cons_by_hh[i] * human_svc_frac[i] * pop_m[i] / 1000.0
            for i in range(5)
        )
        # Also: government spending on human services (~15% of govt_nom)
        human_demand_bn += govt_nom * 0.15

        # Human economy wages (82% of revenue goes to labour)
        human_nom          = human_demand_bn
        human_labor_bn     = human_nom * 0.82
        human_wage_floor_k = 60.0   # $k/yr minimum acceptable wage
        human_workers_max  = human_labor_bn / human_wage_floor_k  # M
        human_workers      = min(human_workers_max, total_disp * 0.50)
        human_workers      = max(human_workers, 0.1)
        human_wage_k       = human_labor_bn / human_workers

        # H6 income = human economy wage
        income_k[5] = human_wage_k
        s.pop[5]    = human_workers  # actual workers, not fixed

        # H6 consumption decision
        interest_k6 = debt_k[5] * p.interest_rate_loan
        dec6 = self.behaviour.decide(
            hh_idx=5, income_k=float(human_wage_k),
            wealth_k=float(wealth_k[5]), debt_k=float(debt_k[5]),
            interest_burden_k=float(interest_k6),
            unemployment=False, economic_context=economic_context, t=t,
        )
        cons_by_hh[5]    = dec6["consume_k"]
        human_svc_frac[5]= dec6["human_svc_share"]

        # Net displaced with no income
        net_no_income = max(total_disp - human_workers, 0.0)

        # 8. Full GDP
        total_consumption_bn = sum(
            cons_by_hh[i] * pop_m[i] / 1000.0 for i in range(6)
        )
        gdp_nom = know_nom + phys_nom + human_nom + govt_nom

        # 9. Final government finances
        taxes = self._taxes(inc, auto_labor, gdp_nom, inc["tax_k_t"])
        existing_spend = (p.govt_base_pct * gdp_nom + interest_bn
                         + inc["compute_overhead"]
                         + 0.15 * inc["govt_dao_inc"])  # daoification cost
        redistributable = max(taxes["total"] - existing_spend, 0.0)
        ubi_per_person  = redistributable / max(net_no_income, 0.5) if net_no_income > 0.5 else 0.0

        # Home production buffer
        home_prod = p.home_prod_k * p.land_access_frac
        effective_welfare = ubi_per_person + inc["compute_div_k"] + home_prod

        # Update H4 income with final UBI
        income_k[3] = ubi_per_person + inc["compute_div_k"]

        # 10. Stock updates (SFC balance sheet accounting)
        # Household savings = income - consumption - interest
        for i in range(6):
            income_bn     = income_k[i] * pop_m[i] / 1000.0
            consume_bn    = cons_by_hh[i] * pop_m[i] / 1000.0
            interest_out  = debt_k[i] * p.interest_rate_loan * pop_m[i] / 1000.0
            interest_in   = wealth_k[i] * p.interest_rate_deposit * 0.30 * pop_m[i] / 1000.0
            saving_bn     = income_bn - consume_bn - interest_out + interest_in

            s.wealth[i] = max(s.wealth[i] + saving_bn + new_debt[i] * pop_m[i] / 1000.0, 0.0)
            s.debt[i]   = max(s.debt[i]   + new_debt[i] * pop_m[i] / 1000.0
                              - 0.05 * s.debt[i], 0.0)   # 5% annual repayment

        # Government debt: deficit adds to stock
        govt_balance = taxes["total"] - existing_spend - redistributable
        s.govt_debt += max(-govt_balance, 0.0)   # grows if deficit

        # Capital accumulation
        s.capital_auto  *= (1 + 0.08)   # AI capital grows 8%/yr
        s.capital_human *= (1 + 0.02)   # human economy capital grows 2%/yr

        # 11. Inequality proxy
        total_labor_inc = auto_labor + human_labor_bn + inc["yeomen_inc"] + inc["dao_inc"]
        total_cap_inc   = inc["conc_cap"]
        total_inc       = total_labor_inc + total_cap_inc + inc["compute_div"]
        labor_share     = total_labor_inc / max(total_inc, 1)
        cap_share       = total_cap_inc   / max(total_inc, 1)
        div_share       = inc["compute_div"] / max(total_inc, 1)

        yeomen_t_now    = inc["yeomen_eff"]
        gini = 0.35 * (1 - cap_share) + 0.90 * cap_share * (1 - yeomen_t_now)
        gini += 0.45 * cap_share * yeomen_t_now
        gini *= (1 - div_share)

        # 11b. Governance quality update
        capital_share_wealth = s.wealth[0] / max(sum(s.wealth), 1.0)  # H1 share of total wealth

        decay_rate = 0.0
        if gini > 0.50:
            decay_rate += (gini - 0.50) * 0.04   # up to ~1.5%/yr at Gini=0.88
        if capital_share_wealth > 0.40:
            decay_rate += (capital_share_wealth - 0.40) * 0.06  # up to ~3.6%/yr at 100% concentration

        recovery_rate = 0.0
        if gini < 0.35:
            recovery_rate = (0.35 - gini) * 0.02  # up to ~0.7%/yr at Gini=0

        s.governance = min(1.0, max(0.1, s.governance + recovery_rate - decay_rate))

        # Real GDP index
        know_price  = (1 - p.deflation_know * (1 - p.monopoly_rent)) ** t
        phys_price  = (1 - p.deflation_phys * (1 - p.monopoly_rent)) ** t
        human_price = (1 + p.baumol_rate) ** t
        w_a, w_h = 0.70, 0.05
        composite_price = (0.40 * know_price + 0.30 * phys_price + w_h * human_price) / (w_a + w_h)
        gdp_real_idx = (gdp_nom / composite_price) / p.gdp_0 * 100

        # 12. Fill Flows record
        f.wages_auto       = auto_labor
        f.wages_human      = human_labor_bn
        f.dividends        = inc["conc_cap"]
        f.yeomen_income    = inc["yeomen_inc"]
        f.dao_income       = inc["dao_inc"]
        f.compute_div      = inc["compute_div"]
        f.ubi              = redistributable
        f.cons_human_svcs  = human_nom
        f.cons_auto_goods  = total_consumption_bn - human_nom
        f.tax_labour       = taxes["tax_labor"] + taxes["tax_yeomen"] + taxes["tax_dao"]
        f.tax_capital      = taxes["tax_conc"]
        f.tax_vat          = taxes["tax_vat"]
        f.govt_spending    = existing_spend
        f.interest_govt    = interest_bn
        f.income_by_hh     = income_k
        f.cons_by_hh       = cons_by_hh
        f.gdp_nom          = gdp_nom
        f.gdp_real_idx     = gdp_real_idx
        f.gini_proxy       = gini
        f.welfare_k        = effective_welfare
        f.tax_leakage      = taxes["leakage"]
        f.debt_gdp         = s.govt_debt / max(gdp_nom, 1)
        f.interest_pct_rev = interest_bn / max(taxes["total"], 1) * 100
        f.fiscal_space     = taxes["total"] - existing_spend
        f.ubi_per_person   = ubi_per_person
        f.compute_div_k    = inc["compute_div_k"]
        f.labour_share     = labor_share * 100
        f.governance       = s.governance

        s.year += 1
        return f

    # ── Run full simulation ───────────────────────────────────────────────────

    def run(self) -> pd.DataFrame:
        records = []
        for t in range(self.p.n_years):
            f = self.step(t)
            records.append({
                "year":             self.p.base_year + t,
                "t":                t,
                "gdp_nom_bn":       f.gdp_nom,
                "gdp_real_idx":     f.gdp_real_idx,
                "know_auto_pct":    f.know_auto_pct,
                "phys_auto_pct":    f.phys_auto_pct,
                "labour_share":     f.labour_share,
                "gini_proxy":       f.gini_proxy,
                "effective_welfare_k": f.welfare_k,
                "ubi_per_person_k": f.ubi_per_person,
                "compute_div_k":    f.compute_div_k,
                "tax_total_bn":     f.tax_labour + f.tax_capital + f.tax_vat,
                "redistributable_bn": f.ubi,
                "debt_gdp_ratio":   f.debt_gdp,
                "interest_pct_rev": f.interest_pct_rev,
                "fiscal_space_bn":  f.fiscal_space,
                "tax_leakage_bn":   f.tax_leakage,
                "cons_human_svcs_bn": f.cons_human_svcs,
                "cons_auto_goods_bn": f.cons_auto_goods,
                "govt_debt_bn":     self.state.govt_debt,
                # Income by household type ($k/person/yr)
                "income_h1_k": f.income_by_hh[0],
                "income_h2_k": f.income_by_hh[1],
                "income_h3_k": f.income_by_hh[2],
                "income_h4_k": f.income_by_hh[3],
                "income_h5_k": f.income_by_hh[4],
                "income_h6_k": f.income_by_hh[5],
                # Consumption decisions ($k/person/yr)
                "cons_h1_k":   f.cons_by_hh[0],
                "cons_h2_k":   f.cons_by_hh[1],
                "cons_h3_k":   f.cons_by_hh[2],
                "cons_h4_k":   f.cons_by_hh[3],
                "cons_h5_k":   f.cons_by_hh[4],
                "cons_h6_k":   f.cons_by_hh[5],
                # Governance
                "governance":  f.governance,
                # Tax drag diagnostics
                "effective_auto_mid": f.effective_auto_mid,
            })
        return pd.DataFrame(records)


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIOS + QUICK RUN
# ─────────────────────────────────────────────────────────────────────────────

SCENARIOS_SFC = {
    "Fast / No yeomen / Low tax": dict(
        auto_mid=5, yeomen_target=0.00, tax_k=0.20, dao_frac=0.00,
        public_ai_frac=0.00, levy_prog=0.0, enforcement=1.0, dao_govt_rate=0.0,
        monopoly_rent=0.00,
    ),
    "Fast / No yeomen / Monopoly": dict(
        auto_mid=5, yeomen_target=0.00, tax_k=0.20, dao_frac=0.00,
        public_ai_frac=0.00, levy_prog=0.0, enforcement=1.0, dao_govt_rate=0.0,
        monopoly_rent=0.50,   # ← key: AI firms keep half productivity as rent
    ),
    "Fast / High yeomen / High tax": dict(
        auto_mid=5, yeomen_target=0.60, tax_k=0.50, dao_frac=0.10,
        public_ai_frac=0.00, levy_prog=0.0, enforcement=1.0, dao_govt_rate=0.0,
        monopoly_rent=0.00,
    ),
    "Fast / Public AI 70%": dict(
        auto_mid=5, yeomen_target=0.10, tax_k=0.20, dao_frac=0.00,
        public_ai_frac=0.70, levy_prog=0.0, enforcement=1.0, dao_govt_rate=0.0,
        monopoly_rent=0.00,
    ),
    "Fast / Full stack": dict(
        auto_mid=5, yeomen_target=0.35, tax_k=0.50, dao_frac=0.20,
        public_ai_frac=0.00, levy_prog=0.8, enforcement=1.0, dao_govt_rate=0.20,
        monopoly_rent=0.00,
    ),
    "Fast / No yeomen / Monopoly / Decay": dict(
        auto_mid=5.0, yeomen_target=0.0, monopoly_rent=0.50,
        tax_k=0.35, enforcement=1.0, public_ai_frac=0.0,
        dao_frac=0.00, levy_prog=0.0, dao_govt_rate=0.0,
        # starts at full enforcement but governance decays endogenously
    ),
    # ── Tax-drag tradeoff scenarios ────────────────────────────────────────────
    "Fast / High yeomen / High tax / No drag": dict(
        auto_mid=5.0, yeomen_target=0.35, tax_k=0.35,
        enforcement=1.0, tax_drag=0.0, rent_fraction=1.0,
    ),
    "Fast / High yeomen / High tax / Low drag": dict(
        auto_mid=5.0, yeomen_target=0.35, tax_k=0.35,
        enforcement=1.0, tax_drag=0.15, rent_fraction=1.0,
    ),
    "Fast / High yeomen / High tax / Rent tax": dict(
        # Same statutory rate but only rents taxed — lower effective drag
        auto_mid=5.0, yeomen_target=0.35, tax_k=0.35,
        enforcement=1.0, tax_drag=0.15, rent_fraction=0.35,
    ),
    "Fast / No yeomen / Low tax / No drag": dict(
        # Baseline comparison: no tax, no drag, concentrated ownership
        auto_mid=5.0, yeomen_target=0.0, tax_k=0.10,
        enforcement=1.0, tax_drag=0.0, rent_fraction=1.0,
    ),
}


def run_scenarios(scenarios=None) -> dict[str, pd.DataFrame]:
    results = {}
    for name, overrides in (scenarios or SCENARIOS_SFC).items():
        p = Params(**{k: v for k, v in overrides.items()
                      if hasattr(Params, k) or k in Params.__dataclass_fields__})
        # Map scenario keys to Params fields
        field_map = {
            "auto_mid":      "auto_mid",
            "yeomen_target": "yeomen_target",
            "monopoly_rent": "monopoly_rent",
        }
        # Rebuild with correct field names
        params_dict = {}
        for k, v in overrides.items():
            if k == "auto_mid":
                params_dict["auto_mid"] = v
            else:
                params_dict[k] = v
        p = Params(**{k: v for k, v in params_dict.items()
                      if k in Params.__dataclass_fields__})
        model = SFCModel(p)
        df    = model.run()
        results[name] = df
        print(f"  ✓  {name}")
    return results


def plot_sfc(results: dict, outfile="ai_economy_sfc.png"):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(20, 30))
    fig.suptitle(
        "SFC Model — AI Economic Transition\n"
        "Stock-Flow Consistent with Household Balance Sheets",
        fontsize=13, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(5, 3, figure=fig, hspace=0.50, wspace=0.35)

    COLORS = ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd", "#8c564b"]

    panels = [
        (gs[0, 0], "gdp_nom_bn",           "$T",      "Nominal GDP",              1/1000),
        (gs[0, 1], "gdp_real_idx",         "idx",     "Real GDP (2025=100)",      1),
        (gs[0, 2], "gini_proxy",           "Gini",    "Inequality (Gini proxy)",  1),
        (gs[1, 0], "effective_welfare_k",  "$k/yr",   "Effective Welfare",        1),
        (gs[1, 1], "tax_total_bn",         "$T",      "Tax Revenue",              1/1000),
        (gs[1, 2], "fiscal_space_bn",      "$T",      "Fiscal Space (pre-UBI)",   1/1000),
        (gs[2, 0], "debt_gdp_ratio",       "ratio",   "Debt / Nominal GDP",       1),
        (gs[2, 1], "interest_pct_rev",     "%",       "Interest % of Revenue",    1),
        (gs[2, 2], "cons_human_svcs_bn",   "$T",      "Human Economy Demand",     1/1000),
        (gs[3, 0], "income_h1_k",          "$k/yr",   "Capital Owner Income",     1),
        (gs[3, 1], "income_h4_k",          "$k/yr",   "Displaced Worker Income",  1),
        (gs[3, 2], "income_h6_k",          "$k/yr",   "Human Economy Wage",       1),
        (gs[4, 0], "governance",           "G(t)",    "Governance Quality G(t)",  1),
    ]

    axes = [fig.add_subplot(loc) for loc, *_ in panels]

    for i, (name, df) in enumerate(results.items()):
        color = COLORS[i % len(COLORS)]
        x = df["year"]
        for ax, (_, col, unit, title, scale) in zip(axes, panels):
            ax.plot(x, df[col] * scale, color=color, lw=2, label=name)

    for ax, (_, col, unit, title, scale) in zip(axes, panels):
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel(unit, fontsize=9)
        ax.set_xlabel("Year", fontsize=9)
        ax.grid(True, alpha=0.25)
        ax.set_xlim(2025, 2059)
        ax.legend(fontsize=7, loc="best", framealpha=0.7)

    # Governance panel: add reference line at 1.0 and floor at 0.1
    gov_ax = axes[-1]
    gov_ax.axhline(1.0, color="gray", lw=1, ls="--", alpha=0.5, label="_baseline")
    gov_ax.axhline(0.1, color="gray", lw=1, ls=":",  alpha=0.5, label="_floor")
    gov_ax.set_ylim(0.0, 1.05)

    plt.savefig(outfile, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Chart saved → {outfile}")


if __name__ == "__main__":
    print("Running SFC scenarios...")
    results = run_scenarios()
    plot_sfc(results)

    # Quick summary (all scenarios)
    print(f"\n{'Scenario':<40} {'Gini t+10':>10} {'Welfare t+10':>12} {'Debt/GDP t+10':>14} {'Nominal GDP t+10':>16}")
    print("-" * 95)
    for name, df in results.items():
        row = df[df.t == 10].iloc[0]
        print(f"{name:<40} {row.gini_proxy:>10.3f} "
              f"${row.effective_welfare_k:>10.0f}k "
              f"{row.debt_gdp_ratio:>13.2f}x "
              f"${row.gdp_nom_bn/1000:>14.1f}T")

    # ── Tax-drag tradeoff table ────────────────────────────────────────────────
    drag_scenarios = [
        "Fast / High yeomen / High tax",          # existing baseline
        "Fast / High yeomen / High tax / No drag",
        "Fast / High yeomen / High tax / Low drag",
        "Fast / High yeomen / High tax / Rent tax",
        "Fast / No yeomen / Low tax / No drag",
    ]

    HDR = (f"\n{'Scenario':<45} {'Gini':>6} {'Welfare$k':>10} "
           f"{'NomGDP$T':>9} {'eff_mid':>8} {'G(t)':>7}")
    SEP = "-" * 90

    for label, t_yr in [("t+10", 10), ("t+20", 20)]:
        print(f"\n── Tax-drag tradeoff comparison at {label} ──")
        print(HDR)
        print(SEP)
        for name in drag_scenarios:
            if name not in results:
                continue
            df  = results[name]
            row = df[df.t == t_yr].iloc[0]
            print(
                f"{name:<45} {row.gini_proxy:>6.3f} "
                f"${row.effective_welfare_k:>8.1f}k "
                f"${row.gdp_nom_bn/1000:>7.1f}T "
                f"{row.effective_auto_mid:>8.2f} "
                f"{row.governance:>7.3f}"
            )
