"""
AI Economic Transition Model
=============================
Parametric model of the transition from human-labour to AI/robot economy.

Key outputs:
  - Real & nominal GDP path
  - Labor vs capital income (inequality)
  - Government tax revenue & redistributable surplus
  - UBI capacity (excess for non-laboring population)
  - Human economy wages (derived from consumption flows, not assumed)
  - Return on capital by asset class (AI/concentrated, yeomen, land, energy)
  - Implied asset valuations

Base economy: US-like (~$28T nominal GDP, 160M workers, 2025 baseline)
Horizon: 2025-2060 (35 years)

Human economy size is DERIVED from:
  (1) Capital owner consumption × fraction on human services
  (2) UBI income × fraction on human services
  Both consumption terms use MPC that adjusts upward as labour income falls.

Capital income is split into:
  - Concentrated: large firms, oligopoly rents, low MPC (~20%)
  - Yeomen: small owner-operators, competitive returns, high MPC (~75%)
  - DAO: commons-governed knowledge-work income, high MPC (~78%)

Enforcement/tax-leakage dimension:
  - enforcement: fraction of statutory capital tax that government can collect
  - 1.0 = large bloc (US/EU) with full consumer-market leverage
  - 0.65 = medium nation with some leverage
  - 0.30 = small open economy, high capital mobility / profit-shifting
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# FIXED CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

GDP_0       = 28_000   # $bn nominal GDP, 2025
BASE_NOMINAL_GDP = GDP_0     # alias used in sector init
LABOR_FORCE = 160.0    # millions of workers

# ── Sector GDP shares (2025 nominal baseline)
KNOW_GDP_SHARE      = 0.33   # knowledge work: software, finance, legal, media
AI_SVC_GDP_SHARE    = 0.15   # AI-delivered services: healthcare, education (NEW)
PHYS_GDP_SHARE      = 0.22   # physical goods manufacturing
ENERGY_GDP_SHARE    = 0.04   # energy sector (NEW)
SCARCITY_GDP_SHARE  = 0.05   # provably-human, artisanal, scarce experiences (NEW)
GOVT_GDP_SHARE      = 0.21   # government services (largely unchanged)

# ── Sector worker shares (2025)
KNOW_WORKER_SHARE    = 0.28
AI_SVC_WORKER_SHARE  = 0.18   # healthcare + education workers (NEW)
PHYS_WORKER_SHARE    = 0.32
ENERGY_WORKER_SHARE  = 0.02   # NEW
# remaining workers in govt/human economy

# ── Automation ceilings (max fraction of sector automatable)
KNOW_AUTO_CEILING    = 0.93   # was 0.88
AI_SVC_AUTO_CEILING  = 0.95   # healthcare/ed fully AI-deliverable (NEW)
PHYS_AUTO_CEILING    = 0.82   # was 0.68
PHYS_LAG_YEARS       = 7      # physical lags knowledge by this many years (kept for s_curve speed)

# ── Price dynamics
PRICE_DEFLATION_KNOW    = 0.08   # -8%/yr when fully automated
PRICE_DEFLATION_AI_SVC  = 0.08   # same for AI services
PRICE_DEFLATION_PHYS    = 0.05   # partially deflating (labour component only)
# Physical goods — empirically calibrated cost structure (Oliver Wyman 2025, NAHB)
PHYS_AUTOMATABLE_SHARE  = 0.25   # labour ~10% + design ~5% + logistics ~10%
PHYS_MATERIAL_SHARE     = 0.57   # purchased parts + raw materials
PHYS_ENERGY_SHARE       = 0.08   # embedded energy
PHYS_OTHER_SHARE        = 0.10   # non-automatable overhead
MATERIAL_PRICE_GROWTH   = 0.030  # +3%/yr (IEA: copper +50% by 2040, supply deficits)
PHYS_DEMAND_ELASTICITY  = 1.0    # unit elastic → Jevons: nominal physical GDP roughly flat

# Energy sector — two-phase model (tied to automation speed via mid parameter)
#
# Phase 1: Grid infrastructure buildout
#   Retail electricity prices RISE despite cheap solar modules because transmission
#   upgrades, storage integration, and grid hardening costs dominate. Data-centre
#   demand boom and EV ramp drive strong volume growth.
#   Price: +1.5%/yr  ·  Demand: +5%/yr  →  nominal ≈ +6.6%/yr
#
# Phase 2: Robotics-accelerated solar + Jevons backfire
#   Robotics cuts solar installation labour (15-40% of installed cost) — the
#   component of LCOE that resisted the module learning curve. Solar+storage
#   reaches dominance. Electricity price collapses toward marginal cost of sunlight.
#   Cheap energy unlocks: green hydrogen (replaces coal in steel, jet fuel, fertiliser),
#   desalination at scale, direct air capture, always-on robotic manufacturing, AI
#   compute without electricity as binding constraint.
#   Price: -5%/yr  ·  Demand: +9%/yr  →  nominal ≈ +3.6%/yr (Jevons backfire confirmed)
#
# Transition timing: Phase 1 → Phase 2 at year ≈ mid × ENERGY_ROBOTICS_TRANSITION_MULT
#   Fast automation (mid=5)  → transition ~year 7-8
#   Medium automation (mid=9) → transition ~year 13-14
#   Slow automation (mid=14)  → transition ~year 20-21
#
ENERGY_PHASE1_PRICE_GROWTH  = 0.015  # +1.5%/yr: grid capex > solar module savings
ENERGY_PHASE1_DEMAND_GROWTH = 0.050  # +5.0%/yr: data centres + EVs
ENERGY_PHASE2_PRICE_DEFL    = 0.050  # -5.0%/yr: robotics solar collapse
ENERGY_PHASE2_DEMAND_GROWTH = 0.090  # +9.0%/yr: H2, DAC, desalination, manufacturing
ENERGY_ROBOTICS_TRANSITION_MULT = 1.5  # transition year = mid × this

# Scarcity goods — appreciate with income inequality
SCARCITY_PRICE_GROWTH   = 0.06   # +6%/yr: artisanal, provably-human premium

# ── Yeomen fiscal parameters
YEOMEN_TAX_FRICTION_BASE  = 0.18  # double FICA + healthcare + compliance ~18% income discount
FIRM_REBATE_YEOMEN_EFFECT = 0.20  # fraction of friction eliminated by firm rebate policy

HUMAN_PRICE_INFL     = 0.04   # 4%/yr Baumol inflation in human economy

# Government
# Split government spending into two components:
#   (1) Discretionary/mandatory programmes: proportional to nominal GDP
#   (2) Debt service: fixed nominal obligation — does NOT deflate with GDP
# This separation captures the "nominal GDP paradox" for public finance:
# as nominal GDP halves, interest payments remain constant, rising as a
# share of tax revenue and crowding out redistributable surplus.
EXISTING_GOVT_BASE_PCT = 0.215  # non-interest govt spending as % of nominal GDP
DEBT_INITIAL_BN        = 34_000 # US federal debt, 2025 (~$34T)
DEBT_INTEREST_RATE     = 0.045  # effective avg interest rate on outstanding debt
# Note: at t=0, interest = 34000 × 4.5% = $1,530bn = 5.5% of GDP
# Total: 21.5% + 5.5% = 27.0% ← matches prior EXISTING_GOVT_PCT calibration

TAX_LABOR_RATE    = 0.25   # income tax rate on labour income
TAX_VAT_RATE      = 0.12   # VAT on ~65% of nominal GDP

# Capital stock
CAPITAL_GDP_RATIO_0 = 3.5
CAPITAL_ACCUM_RATE  = 0.04   # 4%/yr real capital accumulation

# Capital ownership distribution (shares of total equity/capital)
# Source: Wolff (2021), Federal Reserve DFA
CAP_SHARE_TOP1     = 0.38   # top 1% own 38%
CAP_SHARE_NEXT9    = 0.51   # next 9% own 51%
CAP_SHARE_PENSION  = 0.10   # 401k/pension holders own 10%
CAP_SHARE_BOT50    = 0.01   # bottom 50% own 1%

# BASE marginal propensity to consume from capital income, by ownership tier
# These rise dynamically as labour income falls (see mpc_adjusted() below)
MPC_BASE_TOP1     = 0.12
MPC_BASE_NEXT9    = 0.30
MPC_BASE_PENSION  = 0.72   # already higher — retirees, limited other income
MPC_BASE_BOT50    = 0.90

# Fraction of personal consumption that goes to human services
# (vs. automatable goods which approach zero marginal cost)
HUMAN_SVC_SHARE_CAPITAL = 0.30   # capital-owner consumption on human services
HUMAN_SVC_SHARE_UBI     = 0.15   # UBI recipients spend less on premium human services
HUMAN_SVC_SHARE_LABOR   = 0.10   # workers still employed spend some on human svcs

# Yeomen enterprise: owner-operators who own their AI/robots
# Their "capital income" is really hybrid labor+capital; MPC is labour-like
MPC_YEOMEN = 0.78

# DAO / commons enterprise: knowledge-work income flowing through commons DAOs
# Contributors are individuals earning from open source, AI models, data commons
# MPC is labour-like (earned income, not passive capital); human service share
# slightly higher than labour (knowledge workers value human experiences)
MPC_DAO              = 0.78
HUMAN_SVC_SHARE_DAO  = 0.12

# Jurisdiction enforcement leverage presets
# Represents the fraction of statutory capital tax rate actually collectible,
# after profit-shifting, transfer pricing, and capital mobility.
JURISDICTION_LEVERAGE = {
    "large_bloc":    1.00,   # US/EU — strong consumer-market enforcement
    "medium_nation": 0.65,   # mid-size country with some leverage
    "small_nation":  0.30,   # small open economy, high capital mobility
}

# ── 2025 US baseline values (common t=0 anchor for all scenarios) ────────────
# All scenario parameters ramp from these real-world 2025 values to their
# target over POLICY_RAMP_YEARS. This ensures every scenario starts from
# the same point on all charts regardless of its target parameters.
YEOMEN_BASE        = 0.08   # ~8%: current self-employment + small-business share
TAX_K_BASE         = 0.21   # ~21%: current effective US capital/corporate rate
DAO_BASE           = 0.00   # commons DAOs essentially non-existent in 2025
POLICY_RAMP_YEARS  = 10     # years to fully reach scenario target parameters

# Home production / subsistence buffer
# Analogy: rooftop solar — inefficient vs. grid at market prices, but rational
# when you have no currency income, cheap energy, and land access.
# Effect: reduces required cash income for survival → more of UBI is
# discretionary → higher MPC into market economy → more human economy demand.
#
# Land access is unequally distributed (homeowners w/ outdoor space).
# Urban renters cannot participate → bifurcates welfare outcomes.
LAND_ACCESS_FRAC   = 0.40   # fraction of displaced workers with land access
HOME_PROD_VALUE_K  = 6.0    # $k/yr value of home production (food + basic svcs)
                             # covers ~25-35% of food needs + some home services
SUBSISTENCE_COST_K = 16.0   # approximate annual subsistence cost ($k/yr)

# When home production covers part of subsistence, the UBI fraction that is
# "discretionary" (spent freely in market) rises, slightly increasing the
# share going to human services vs. cheap automatable goods.
HOME_PROD_UBI_UPLIFT = 0.08  # extra fraction of UBI going to human services
                              # for land-access households (base is 0.15)

# Base asset returns
R_AI_INITIAL    = 0.28   # oligopoly return on concentrated AI capital
R_AI_TERMINAL   = 0.07   # long-run competitive return
R_AI_HALFLIFE   = 11     # years for premium to halve
R_YEOMEN        = 0.08   # yeomen earn competitive tool return (skill premium
                          # is captured in their hybrid income, not capital return)
R_LAND_YIELD    = 0.035
R_LAND_APPREC   = 0.035
R_ENERGY_0      = 0.07
R_ENERGY_GROW   = 0.012  # rises with AI energy demand, capped at 18%

# Government daoification: acquisition cost as fraction of acquired income stream
# Government pays ~30 cents per dollar of asset value (distressed acquisition);
# amortised over ~2 years of earnings → annual cost ≈ 15% of acquired income
DAOGOV_ACQUISITION_COST = 0.15

# Public AI infrastructure: how compute pool revenue is distributed
# State owns fraction of AI/robot capital; rents it via usage-fee market;
# revenue split between citizen compute dividend and priority-use subsidies.
COMPUTE_DIVIDEND_FRAC  = 0.70   # fraction of pool revenue paid as citizen dividend
COMPUTE_SUBSIDY_FRAC   = 0.20   # fraction subsidising essential/priority uses
COMPUTE_OVERHEAD_FRAC  = 0.10   # maintenance, administration
ADULT_POPULATION       = 260.0  # M — US adult population (dividend recipients)
PUBLIC_AI_BASE         = 0.00   # current public ownership of AI capital (near zero)


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO DEFINITIONS
# Five dimensions:
#   automation speed × yeomen fraction × DAO fraction × capital tax rate × enforcement
# ─────────────────────────────────────────────────────────────────────────────

# mid:          years until 50% of knowledge-work ceiling is automated
#               slow=14, medium=9, fast=5
#
# yeomen:       fraction of ALL automatable-sector capital income to owner-operators
#               none=0.0, moderate=0.35, high=0.60
#
# dao_frac:     fraction of KNOWLEDGE-WORK non-yeomen capital income through DAOs
#               none=0.0, moderate=0.25
#
# tax_k:        effective statutory tax rate on concentrated capital income
#               low=0.20, medium=0.35, high=0.50
#
# enforcement:  fraction of tax_k actually collectible (jurisdiction leverage)
#               large_bloc=1.0, medium=0.65, small=0.30
#
# public_ai_frac: fraction of AI/robot capital owned publicly as infrastructure.
#               Usage-fee market allocates scarce compute/robot time; revenue
#               distributed as citizen compute dividend (70%) + priority-use
#               subsidies (20%) + overhead (10%). Allocation remains market-based
#               (no central planning) — the state captures rent, not output.
#               0.0 = fully private; 0.5 = half public; 0.9 = near-full public pool.
#
# levy_prog:    compute levy progressivity (0=flat tax, 1=highly progressive)
#               Two effects:
#               (1) Revenue: effective rate on concentrated capital scaled up by
#                   (1 + 0.5*levy_prog), capturing tiered levy on heavy users
#               (2) Behaviour: firms facing escalating rates contract work out
#                   to yeomen operators below threshold → endogenous yeomen uplift
#                   of up to +25pp at full progressivity
#
# dao_govt_rate: annual fraction of displacement-driven concentrated capital
#               income the government acquires and daoifies. Scales with
#               automation level (more displacement → more failing assets).
#               Acquired assets produce commons income (MPC ~0.78).
#               Government pays acquisition cost (DAOGOV_ACQUISITION_COST × income).

SCENARIOS = {
    # Baseline comparisons (large-bloc enforcement assumed)
    "Fast / No yeomen / Low tax":           dict(mid=5,  yeomen=0.00, dao_frac=0.00, tax_k=0.20, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    "Fast / No yeomen / High tax":          dict(mid=5,  yeomen=0.00, dao_frac=0.00, tax_k=0.50, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    "Fast / Moderate yeomen / Med tax":     dict(mid=5,  yeomen=0.35, dao_frac=0.00, tax_k=0.35, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    "Fast / High yeomen / High tax":        dict(mid=5,  yeomen=0.60, dao_frac=0.00, tax_k=0.50, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    "Medium / Moderate yeomen / Med tax":   dict(mid=9,  yeomen=0.35, dao_frac=0.00, tax_k=0.35, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    "Slow / Moderate yeomen / Med tax":     dict(mid=14, yeomen=0.35, dao_frac=0.00, tax_k=0.35, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    "Slow / No yeomen / Low tax":           dict(mid=14, yeomen=0.00, dao_frac=0.00, tax_k=0.20, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    # DAO / commons scenarios
    "Fast / Yeomen + DAO / High tax":       dict(mid=5,  yeomen=0.35, dao_frac=0.25, tax_k=0.50, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00),
    # Progressive compute levy (no other structural changes) — shows levy alone
    "Fast / Progressive levy / High tax":   dict(mid=5,  yeomen=0.00, dao_frac=0.00, tax_k=0.50, enforcement=1.00, levy_prog=0.8, dao_govt_rate=0.00, public_ai_frac=0.00),
    # Govt daoification (no levy) — shows daoification alone
    "Fast / Govt daoify / High tax":        dict(mid=5,  yeomen=0.00, dao_frac=0.00, tax_k=0.50, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.20, public_ai_frac=0.00),
    # Full private-ownership stack: levy + daoification + yeomen + DAO
    "Fast / Full stack":                    dict(mid=5,  yeomen=0.35, dao_frac=0.20, tax_k=0.50, enforcement=1.00, levy_prog=0.8, dao_govt_rate=0.20, public_ai_frac=0.00),
    # Public AI infrastructure scenarios
    "Fast / Public AI 50%":                 dict(mid=5,  yeomen=0.10, dao_frac=0.00, tax_k=0.25, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00, public_ai_frac=0.50),
    "Fast / Public AI 90%":                 dict(mid=5,  yeomen=0.10, dao_frac=0.00, tax_k=0.20, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00, public_ai_frac=0.90),
    "Fast / Public AI + full stack":        dict(mid=5,  yeomen=0.20, dao_frac=0.10, tax_k=0.25, enforcement=1.00, levy_prog=0.3, dao_govt_rate=0.10, public_ai_frac=0.70),
    # Small-nation enforcement scenarios
    "Fast / High yeomen / High tax / Small nation": dict(mid=5, yeomen=0.60, dao_frac=0.00, tax_k=0.50, enforcement=0.30, levy_prog=0.0, dao_govt_rate=0.00, public_ai_frac=0.00),
    "Fast / No yeomen / High tax / Small nation":   dict(mid=5, yeomen=0.00, dao_frac=0.00, tax_k=0.50, enforcement=0.30, levy_prog=0.0, dao_govt_rate=0.00, public_ai_frac=0.00),
    # Stress test: Public AI alone vs. platform centralization
    # Tests Gemini's critique: if yeomen fails (platform capture / closed models),
    # can public AI infrastructure alone prevent Gini collapse?
    "Fast / Public AI 90% / No yeomen":             dict(mid=5, yeomen=0.00, dao_frac=0.00, tax_k=0.20, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00, public_ai_frac=0.90),
    # Yeomen tax friction scenarios
    "Fast / High yeomen / Tax reform":              dict(mid=5, yeomen=0.60, dao_frac=0.10, tax_k=0.50, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00, yeomen_tax_friction=0.0,  firm_yeomen_rebate=0.15),
    "Fast / High yeomen / No tax reform":           dict(mid=5, yeomen=0.60, dao_frac=0.00, tax_k=0.50, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00, yeomen_tax_friction=0.18, firm_yeomen_rebate=0.0),
    "Fast / High yeomen / Firm rebate":             dict(mid=5, yeomen=0.40, dao_frac=0.00, tax_k=0.40, enforcement=1.00, levy_prog=0.0, dao_govt_rate=0.00, yeomen_tax_friction=0.18, firm_yeomen_rebate=0.15),
}

COLORS = [
    "#d62728", "#ff7f0e", "#2ca02c", "#1f77b4",
    "#9467bd", "#8c564b", "#e377c2", "#17becf",
    "#bcbd22", "#aec7e8", "#f7b6d2", "#c5b0d5",
    "#c49c94", "#dbdb8d", "#9edae5", "#393b79",
]

HIGHLIGHT = [
    "Fast / No yeomen / Low tax",
    "Fast / No yeomen / High tax",
    "Fast / High yeomen / High tax",
    "Fast / Full stack",
    "Fast / Public AI 90%",
    "Fast / Public AI + full stack",
    "Fast / Public AI 90% / No yeomen",
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def s_curve(t, ceiling, speed, midpoint):
    """
    Logistic S-curve normalized so that t=0 always returns 0.
    All scenarios start from the same baseline in 2025; the midpoint
    parameter controls when the curve inflects, not where it starts.
    """
    raw  = ceiling / (1.0 + np.exp(-speed * (t - midpoint)))
    init = ceiling / (1.0 + np.exp(-speed * (0 - midpoint)))
    # Shift to zero at t=0, rescale so ceiling is still reached
    result = (raw - init) * (ceiling / (ceiling - init))
    return np.clip(result, 0.0, ceiling)


def mpc_adjusted(base_mpc, labour_income_decline_frac, sensitivity=0.5):
    """
    Adjust MPC upward as labour income declines.
    When workers lose wages and must live on capital/dividend income,
    their marginal propensity to consume from that income rises toward ~0.90.
    sensitivity: how strongly MPC adjusts (0=no adjustment, 1=full adjustment)
    """
    target = 0.90
    adjustment = (target - base_mpc) * labour_income_decline_frac * sensitivity
    return np.minimum(base_mpc + adjustment, target)


# ─────────────────────────────────────────────────────────────────────────────
# CORE MODEL
# ─────────────────────────────────────────────────────────────────────────────

def run(mid: float, yeomen: float, tax_k: float,
        dao_frac: float = 0.0, enforcement: float = 1.0,
        levy_prog: float = 0.0, dao_govt_rate: float = 0.0,
        public_ai_frac: float = 0.0,
        yeomen_tax_friction: float = 0.18, firm_yeomen_rebate: float = 0.0,
        n_years: int = 35, base_year: int = 2025) -> pd.DataFrame:
    """
    Parameters
    ----------
    mid           : midpoint year for knowledge-work automation S-curve
    yeomen        : fraction of ALL automatable-sector capital income going to
                    small owner-operators (yeomen enterprises)
    tax_k         : statutory tax rate on concentrated capital income
    dao_frac      : fraction of non-yeomen KNOWLEDGE-WORK capital income flowing
                    through commons DAOs (high MPC, like yeomen, knowledge-specific)
    enforcement   : fraction of tax_k actually collectable given jurisdiction size
                    and capital mobility (large_bloc=1.0, medium=0.65, small=0.30)
    levy_prog     : compute levy progressivity (0=flat tax, 1=highly progressive)
                    Raises effective rate on heavy compute users; endogenously
                    increases yeomen_t as firms contract out to avoid the levy.
    dao_govt_rate : annual fraction of displacement-driven concentrated capital
                    income acquired by government and daoified. Scales with
                    automation level. Acquired assets produce commons income.
    """
    t    = np.arange(n_years, dtype=float)
    year = base_year + t

    # ── Policy ramp-in ────────────────────────────────────────────────────────
    # Parameters ramp from real 2025 US baseline to scenario targets over
    # POLICY_RAMP_YEARS. All scenarios are therefore identical at t=0.
    ramp           = np.minimum(t / POLICY_RAMP_YEARS, 1.0)
    yeomen_t       = YEOMEN_BASE    + (yeomen        - YEOMEN_BASE)    * ramp
    dao_frac_t     = DAO_BASE       + (dao_frac      - DAO_BASE)       * ramp
    tax_k_t        = TAX_K_BASE     + (tax_k         - TAX_K_BASE)     * ramp
    public_ai_t    = PUBLIC_AI_BASE + (public_ai_frac - PUBLIC_AI_BASE) * ramp

    # ── Automation displacement ───────────────────────────────────────────────
    # know_auto = knowledge sector automation fraction
    # auto_phys = physical sector automation fraction (lags knowledge by 30%)
    # auto_ai_svc = AI services sector (slightly faster than knowledge)
    know_auto   = s_curve(t, KNOW_AUTO_CEILING,   0.50, mid)
    auto_phys   = s_curve(t, PHYS_AUTO_CEILING,   0.28, mid * 1.3)
    auto_ai_svc = s_curve(t, AI_SVC_AUTO_CEILING, 0.55, mid * 0.9)
    # Keep phys_auto as alias for backward-compat (used in displacement + income)
    phys_auto = auto_phys

    know_workers_0    = LABOR_FORCE * KNOW_WORKER_SHARE    # ~45M
    phys_workers_0    = LABOR_FORCE * PHYS_WORKER_SHARE    # ~51M
    ai_svc_workers_0  = LABOR_FORCE * AI_SVC_WORKER_SHARE  # ~29M
    energy_workers_0  = LABOR_FORCE * ENERGY_WORKER_SHARE  # ~3M

    know_displaced    = know_workers_0   * know_auto
    phys_displaced    = phys_workers_0   * auto_phys
    ai_svc_displaced  = ai_svc_workers_0 * auto_ai_svc
    total_displaced   = know_displaced + phys_displaced + ai_svc_displaced

    # ── Nominal GDP — 6-sector structure ─────────────────────────────────────
    # Knowledge sector: deflation proportional to incremental automation each year
    # Physical goods: Jevons dynamics — only automatable share deflates, material
    #   share appreciates; demand response offsets price savings
    # AI services: like knowledge, strong deflation as AI takes over delivery
    # Energy: nominal grows (demand overwhelms price deflation)
    # Scarcity: appreciates with inequality
    # Government: slight nominal shrinkage

    # Per-year sector nominal outputs (initialise at t=0 values)
    know_nom_arr    = np.zeros(n_years)
    ai_svc_nom_arr  = np.zeros(n_years)
    phys_nom_arr    = np.zeros(n_years)
    energy_nom_arr  = np.zeros(n_years)
    scarcity_nom_arr= np.zeros(n_years)
    govt_nom_arr    = np.zeros(n_years)

    # Seed t=0 levels
    _know_nom    = BASE_NOMINAL_GDP * KNOW_GDP_SHARE
    _ai_svc_nom  = BASE_NOMINAL_GDP * AI_SVC_GDP_SHARE
    _phys_nom    = BASE_NOMINAL_GDP * PHYS_GDP_SHARE
    _energy_nom  = BASE_NOMINAL_GDP * ENERGY_GDP_SHARE
    _scarcity_nom= BASE_NOMINAL_GDP * SCARCITY_GDP_SHARE
    _govt_nom    = BASE_NOMINAL_GDP * GOVT_GDP_SHARE

    for _i in range(n_years):
        know_nom_arr[_i]     = _know_nom
        ai_svc_nom_arr[_i]   = _ai_svc_nom
        phys_nom_arr[_i]     = _phys_nom
        energy_nom_arr[_i]   = _energy_nom
        scarcity_nom_arr[_i] = _scarcity_nom
        govt_nom_arr[_i]     = _govt_nom
        if _i < n_years - 1:
            # Knowledge: incremental deflation proportional to new automation
            auto_k_cur  = know_auto[_i]
            auto_k_next = know_auto[_i + 1]
            incr_know_defl = PRICE_DEFLATION_KNOW * max(auto_k_next - auto_k_cur, 0)
            _know_nom = _know_nom * (1 - incr_know_defl) * (1 + 0.02)

            # AI services: same structure
            auto_ai_cur  = auto_ai_svc[_i]
            auto_ai_next = auto_ai_svc[_i + 1]
            incr_ai_defl = PRICE_DEFLATION_AI_SVC * max(auto_ai_next - auto_ai_cur, 0)
            _ai_svc_nom = _ai_svc_nom * (1 - incr_ai_defl) * (1 + 0.02)

            # Physical goods: Jevons — only automatable share deflates
            auto_p_cur  = auto_phys[_i]
            auto_p_next = auto_phys[_i + 1]
            labour_cost_defl    = PRICE_DEFLATION_PHYS * max(auto_p_next - auto_p_cur, 0) * PHYS_AUTOMATABLE_SHARE
            material_cost_chg   = MATERIAL_PRICE_GROWTH * PHYS_MATERIAL_SHARE
            net_phys_price_chg  = -labour_cost_defl + material_cost_chg
            demand_response     = PHYS_DEMAND_ELASTICITY * labour_cost_defl
            _phys_nom = _phys_nom * (1 + net_phys_price_chg + demand_response + 0.01)

            # Energy: two-phase model
            # Phase 1 = infrastructure buildout (prices rising, data-centre demand)
            # Phase 2 = robotics-accelerated solar + Jevons backfire
            _energy_transition_yr = mid * ENERGY_ROBOTICS_TRANSITION_MULT
            if _i < _energy_transition_yr:
                _e_price_chg   = ENERGY_PHASE1_PRICE_GROWTH
                _e_demand_chg  = ENERGY_PHASE1_DEMAND_GROWTH
            else:
                _e_price_chg   = -ENERGY_PHASE2_PRICE_DEFL
                _e_demand_chg   = ENERGY_PHASE2_DEMAND_GROWTH
            _energy_nom = _energy_nom * (1 + _e_price_chg) * (1 + _e_demand_chg)

            # Scarcity: appreciates
            _scarcity_nom = _scarcity_nom * (1 + SCARCITY_PRICE_GROWTH)

            # Government: slight shrinkage
            _govt_nom = _govt_nom * (1 - 0.005)

    know_nom = know_nom_arr
    ai_svc_nom = ai_svc_nom_arr
    phys_nom = phys_nom_arr
    energy_nom = energy_nom_arr
    scarcity_nom = scarcity_nom_arr
    govt_nom = govt_nom_arr

    # ── Income from automatable sectors ──────────────────────────────────────
    # Labour income: fraction of nominal revenue × (1 - displaced)
    know_labor    = know_nom   * (1 - know_auto)   * 0.60
    phys_labor    = phys_nom   * (1 - auto_phys)   * 0.58
    ai_svc_labor  = ai_svc_nom * (1 - auto_ai_svc) * 0.55
    auto_labor_income = know_labor + phys_labor + ai_svc_labor

    # Gross capital income (everything not going to labour)
    know_gross_cap   = know_nom   * (know_auto   * 0.60 + 0.40)
    phys_gross_cap   = phys_nom   * (auto_phys   * 0.58 + 0.42)
    ai_svc_gross_cap = ai_svc_nom * (auto_ai_svc * 0.55 + 0.45)
    # Energy and scarcity: capital-intensive, high capital share
    energy_gross_cap   = energy_nom   * 0.70
    scarcity_gross_cap = scarcity_nom * 0.50
    gross_capital_income = (know_gross_cap + phys_gross_cap + ai_svc_gross_cap +
                            energy_gross_cap + scarcity_gross_cap)

    # Split capital income into three streams:
    #   1. Yeomen: small owner-operators across all automated sectors (high MPC)
    #   2. DAO: commons-governed knowledge-work income (high MPC, knowledge-specific)
    #   3. Concentrated: large firms, oligopoly rents (low MPC)
    #
    # DAO income is carved from the non-yeomen portion of knowledge work only
    # (DAOs are primarily a knowledge-economy structure; physical automation
    # consolidates in capital-intensive firms)
    # ── Public AI infrastructure: carve out compute pool ─────────────────────
    # State owns public_ai_t fraction of AI/robot capital. Usage-fee market
    # still allocates scarce compute/robot time (no central planning);
    # the state captures the rent rather than private owners.
    compute_pool_income   = gross_capital_income * public_ai_t
    private_cap_income    = gross_capital_income * (1 - public_ai_t)

    # Compute pool revenue distribution
    compute_dividend_total  = compute_pool_income * COMPUTE_DIVIDEND_FRAC   # → citizens
    compute_subsidy_total   = compute_pool_income * COMPUTE_SUBSIDY_FRAC    # → priority users
    compute_overhead        = compute_pool_income * COMPUTE_OVERHEAD_FRAC   # → maintenance
    # Per-adult citizen dividend
    compute_dividend_k      = compute_dividend_total / ADULT_POPULATION     # $k/yr

    # ── Progressive compute levy: behavioural effect ─────────────────────────
    levy_yeomen_bonus = levy_prog * 0.25 * ramp
    yeomen_effective  = np.minimum(yeomen_t + levy_yeomen_bonus, 0.85)

    yeomen_income   = private_cap_income * yeomen_effective
    # DAO income carved from non-yeomen knowledge + AI services (knowledge-economy structures)
    knowledge_ai_cap_private = (know_gross_cap + ai_svc_gross_cap) * (1 - public_ai_t)
    dao_income      = knowledge_ai_cap_private * (1 - yeomen_effective) * dao_frac_t
    conc_cap_income = (know_gross_cap * (1 - public_ai_t) * (1 - yeomen_effective) * (1 - dao_frac_t) +
                       ai_svc_gross_cap * (1 - public_ai_t) * (1 - yeomen_effective) * (1 - dao_frac_t) +
                       phys_gross_cap * (1 - public_ai_t) * (1 - yeomen_effective) +
                       energy_gross_cap * (1 - public_ai_t) * (1 - yeomen_effective) +
                       scarcity_gross_cap * (1 - public_ai_t) * (1 - yeomen_effective))

    # ── Yeomen tax friction ───────────────────────────────────────────────────
    # Double FICA, healthcare, compliance costs reduce effective yeomen income
    # Firm rebate policy (firm_yeomen_rebate) can partially eliminate this burden
    effective_friction = max(0.0, yeomen_tax_friction - firm_yeomen_rebate * FIRM_REBATE_YEOMEN_EFFECT)
    yeomen_friction_cost = yeomen_income * effective_friction
    yeomen_net_income    = yeomen_income * (1 - effective_friction)
    # Use net income for MPC/consumption; gross income for tax base
    yeomen_income_for_mpc = yeomen_net_income

    # ── Government daoification ───────────────────────────────────────────────
    # Government acquires underutilised/failing assets at distressed prices
    # and converts to commons DAOs. Rate scales with displacement: more
    # automation → more businesses under demand pressure → more acquisition
    # opportunities.
    # Acquired income is removed from concentrated capital and redistributed
    # to commons contributors (high MPC, work-conditioned).
    displacement_frac = (know_auto + phys_auto) / 2.0
    govt_dao_income   = dao_govt_rate * conc_cap_income * displacement_frac
    # Acquisition cost: government pays distressed-price premium each year
    # (amortised acquisition cost ≈ DAOGOV_ACQUISITION_COST × acquired income)
    govt_dao_cost     = DAOGOV_ACQUISITION_COST * govt_dao_income
    # Remove from private concentrated capital
    conc_cap_income   = conc_cap_income - govt_dao_income

    # ── Consumption and derived human economy ────────────────────────────────
    # How much labour income has fallen (fraction of initial)
    labor_income_0    = GDP_0 * (KNOW_GDP_SHARE * 0.60 + PHYS_GDP_SHARE * 0.58 + AI_SVC_GDP_SHARE * 0.55)
    labour_decline    = np.clip((labor_income_0 - auto_labor_income) / labor_income_0, 0, 1)

    # Adjusted MPC for each capital-owning tier (rises as labour income falls)
    mpc_top1    = mpc_adjusted(MPC_BASE_TOP1,    labour_decline, sensitivity=0.30)
    mpc_next9   = mpc_adjusted(MPC_BASE_NEXT9,   labour_decline, sensitivity=0.55)
    mpc_pension = mpc_adjusted(MPC_BASE_PENSION, labour_decline, sensitivity=0.20)
    mpc_bot50   = mpc_adjusted(MPC_BASE_BOT50,   labour_decline, sensitivity=0.05)

    # Weighted average MPC on concentrated capital income
    mpc_conc = (CAP_SHARE_TOP1    * mpc_top1 +
                CAP_SHARE_NEXT9   * mpc_next9 +
                CAP_SHARE_PENSION * mpc_pension +
                CAP_SHARE_BOT50   * mpc_bot50)

    # Total consumption from each income source (before redistribution)
    conc_consumption      = conc_cap_income        * mpc_conc
    yeomen_conc           = yeomen_income_for_mpc  * MPC_YEOMEN
    dao_consumption       = dao_income             * MPC_DAO
    govt_dao_consumption  = govt_dao_income        * MPC_DAO
    # Compute dividend: citizens spend with high MPC (it's cash income)
    compute_div_consumption = compute_dividend_total * 0.85
    labour_conc           = auto_labor_income      * 0.90

    # ── Government finances (first pass, before human economy) ───────────────
    wealth_tax_rate = 0.01 if tax_k >= 0.40 else 0.005
    K = GDP_0 * CAPITAL_GDP_RATIO_0 * (1 + CAPITAL_ACCUM_RATE) ** t

    # Fixed nominal interest obligation — the debt-deflation squeeze:
    # as nominal GDP shrinks, this constant burden rises as a % of GDP and
    # as a % of tax revenue, directly crowding out redistributable surplus.
    interest_burden_bn = np.full(n_years, DEBT_INITIAL_BN * DEBT_INTEREST_RATE)

    # Effective capital tax = ramped statutory rate × enforcement leverage
    # tax_k_t ramps from TAX_K_BASE to scenario target; enforcement is structural
    tax_k_effective = tax_k_t * enforcement

    # Progressive compute levy: revenue effect
    # Heavy compute users pay a premium above the baseline rate.
    # levy_prog=0: levy_multiplier=1.0 (flat, same as tax_k_effective)
    # levy_prog=1: levy_multiplier=1.5 (50% higher effective rate on concentrated capital)
    levy_multiplier = 1.0 + levy_prog * 0.50
    tax_conc_rate   = tax_k_effective * levy_multiplier

    # DAO and yeomen income taxed as labour (owner-operators, earned income)
    tax_conc   = tax_conc_rate * conc_cap_income
    tax_yeomen = TAX_LABOR_RATE  * yeomen_income
    tax_dao    = TAX_LABOR_RATE  * dao_income
    tax_labor  = TAX_LABOR_RATE  * auto_labor_income
    tax_wealth = wealth_tax_rate * K

    # VAT computed on total nominal GDP — iterate once to include human economy
    # First pass: use all 6 sectors (excl. human economy, added in second pass)
    gdp_auto_govt = know_nom + ai_svc_nom + phys_nom + energy_nom + scarcity_nom + govt_nom
    tax_vat_pass1 = TAX_VAT_RATE * gdp_auto_govt * 0.65

    # Compute pool overhead is a government operating cost; dividend and subsidy
    # flow directly to citizens/users (not via government budget)
    tax_total_pass1   = tax_conc + tax_yeomen + tax_dao + tax_labor + tax_wealth + tax_vat_pass1
    existing_spending = (EXISTING_GOVT_BASE_PCT * gdp_auto_govt + interest_burden_bn +
                         govt_dao_cost + compute_overhead)
    redistributable_pass1 = np.maximum(tax_total_pass1 - existing_spending, 0.0)

    # Displaced workers who get UBI (approximation — iterate once)
    net_displaced_pass1 = total_displaced
    ubi_pass1 = np.where(net_displaced_pass1 > 0.5,
                         redistributable_pass1 / net_displaced_pass1, 0.0)

    # Consumption from UBI
    ubi_total_spending   = ubi_pass1 * net_displaced_pass1 * 0.85  # $bn (85% spent)

    # ── Derived human economy ─────────────────────────────────────────────────
    # Demand for human services comes from four sources:
    #   1. Concentrated capital owners: consumption × human_svc_share
    #   2. Yeomen: consumption × human_svc_share (similar to labour)
    #   3. DAO contributors: consumption × human_svc_share (slightly higher)
    #   4. UBI recipients: spend smaller fraction on premium human services
    #   5. Remaining workers: spend some fraction on human services

    human_demand = (
        conc_consumption        * HUMAN_SVC_SHARE_CAPITAL +
        yeomen_conc             * HUMAN_SVC_SHARE_LABOR   +
        dao_consumption         * HUMAN_SVC_SHARE_DAO     +
        govt_dao_consumption    * HUMAN_SVC_SHARE_DAO     +
        compute_div_consumption * HUMAN_SVC_SHARE_UBI     +  # dividend recipients like UBI
        compute_subsidy_total   * HUMAN_SVC_SHARE_LABOR   +  # subsidised priority use
        labour_conc             * HUMAN_SVC_SHARE_LABOR   +
        ubi_total_spending      * HUMAN_SVC_SHARE_UBI
    )  # $bn

    # Human economy GDP ≈ demand (it's demand-constrained)
    human_nom = human_demand

    # Human economy workers: sector is ~82% labour
    # Wage is endogenous: wage = human_labour_income / workers employed
    human_labor_income = human_nom * 0.82
    human_wage_floor   = 60    # $k/yr floor (minimum someone accepts for human economy work)
    human_workers_max  = human_labor_income / human_wage_floor   # M workers
    human_workers = np.minimum(human_workers_max, total_displaced * 0.50)
    human_workers = np.maximum(human_workers, 0.1)
    human_wage_k = human_labor_income / human_workers   # $k/yr

    # Net workers without any income after human economy absorbs some
    net_without_income = np.maximum(total_displaced - human_workers, 0.0)

    # ── Full nominal GDP — 6 sectors + human economy ─────────────────────────
    gdp_nom = know_nom + ai_svc_nom + phys_nom + energy_nom + scarcity_nom + govt_nom + human_nom

    # ── Refined government finances (with human economy) ─────────────────────
    tax_vat    = TAX_VAT_RATE * gdp_nom * 0.65
    tax_total  = tax_conc + tax_yeomen + tax_dao + tax_labor + tax_wealth + tax_vat
    existing_spending = (EXISTING_GOVT_BASE_PCT * gdp_nom + interest_burden_bn +
                         govt_dao_cost + compute_overhead)
    redistributable   = np.maximum(tax_total - existing_spending, 0.0)

    ubi_per_person = np.where(
        net_without_income > 0.5,
        redistributable / net_without_income,   # $k/yr (bn/M = k)
        0.0
    )

    # ── Home production / subsistence buffer ─────────────────────────────────
    home_prod_avg   = HOME_PROD_VALUE_K * LAND_ACCESS_FRAC
    # Welfare floor = UBI + compute dividend (both are unconditional cash) + home production
    effective_welfare_k = ubi_per_person + compute_dividend_k + home_prod_avg

    ubi_land_access   = ubi_per_person * net_without_income * LAND_ACCESS_FRAC
    extra_human_demand = ubi_land_access * HOME_PROD_UBI_UPLIFT

    human_nom        = human_nom + extra_human_demand
    human_labor_income = human_nom * 0.82
    human_workers_max = human_labor_income / human_wage_floor
    human_workers     = np.minimum(human_workers_max, total_displaced * 0.50)
    human_workers     = np.maximum(human_workers, 0.1)
    human_wage_k      = human_labor_income / human_workers

    net_without_income = np.maximum(total_displaced - human_workers, 0.0)

    # ── Labour share & inequality ─────────────────────────────────────────────
    # DAO and yeomen income are distributed like labour (high MPC, earned income)
    total_labor_income   = auto_labor_income + human_labor_income + yeomen_income + dao_income + govt_dao_income
    total_capital_income = conc_cap_income
    # Compute dividend is equally distributed across all adults → Gini ≈ 0 on that component
    total_income         = total_labor_income + total_capital_income + compute_dividend_total

    labor_share_pct = total_labor_income / total_income * 100

    # Gini proxy: capital concentration × capital share
    capital_share_frac = total_capital_income / total_income
    gini_proxy = 0.35 * (1 - capital_share_frac) + 0.90 * capital_share_frac * (1 - yeomen_t)
    gini_proxy += 0.45 * capital_share_frac * yeomen_t
    # Compute dividend is equally distributed (Gini=0) → pulls overall Gini down
    # proportional to its share of total income
    dividend_income_share = compute_dividend_total / np.maximum(total_income, 1)
    gini_proxy = gini_proxy * (1 - dividend_income_share)

    # ── Real GDP index ────────────────────────────────────────────────────────
    w_a = KNOW_GDP_SHARE + AI_SVC_GDP_SHARE + PHYS_GDP_SHARE
    w_h = 0.05
    know_price    = (1 - PRICE_DEFLATION_KNOW)   ** t
    ai_svc_price  = (1 - PRICE_DEFLATION_AI_SVC) ** t
    phys_price    = (1 - PRICE_DEFLATION_PHYS)   ** t
    # Energy price index: Phase 1 rises, Phase 2 falls
    _e_trans = mid * ENERGY_ROBOTICS_TRANSITION_MULT
    energy_price = np.where(
        t <= _e_trans,
        (1 + ENERGY_PHASE1_PRICE_GROWTH) ** t,
        (1 + ENERGY_PHASE1_PRICE_GROWTH) ** _e_trans *
        (1 - ENERGY_PHASE2_PRICE_DEFL)   ** (t - _e_trans)
    )
    scarcity_price= (1 + SCARCITY_PRICE_GROWTH)  ** t
    human_price   = (1 + HUMAN_PRICE_INFL) ** t
    composite_price = (KNOW_GDP_SHARE    * know_price   +
                       AI_SVC_GDP_SHARE  * ai_svc_price +
                       PHYS_GDP_SHARE    * phys_price   +
                       ENERGY_GDP_SHARE  * energy_price +
                       SCARCITY_GDP_SHARE * scarcity_price +
                       w_h * human_price) / (w_a + w_h)
    gdp_real_idx = (gdp_nom / composite_price) / GDP_0 * 100

    # ── Capital returns ───────────────────────────────────────────────────────
    # Concentrated AI capital: starts high (oligopoly), decays toward competitive
    r_ai = (R_AI_INITIAL - R_AI_TERMINAL) * 2**(-t / R_AI_HALFLIFE) + R_AI_TERMINAL

    r_yeomen = R_YEOMEN * np.ones(n_years)
    r_land   = (R_LAND_YIELD + R_LAND_APPREC) * np.ones(n_years)
    r_energy = np.minimum(R_ENERGY_0 + R_ENERGY_GROW * t, 0.18)

    # Blended market return — weight shifts as AI commoditises and yeomen/DAO grow
    distributed_frac = yeomen_t + (1 - yeomen_t) * dao_frac_t
    w_ai     = (1 - distributed_frac) * 0.50 * 2**(-t / 10)
    w_yeomen = distributed_frac        * 0.50 * (1 - 0.3 * 2**(-t / 10))
    w_land   = 0.25
    w_energy = 0.15
    w_other  = np.maximum(1 - w_ai - w_yeomen - w_land - w_energy, 0.05)
    total_w  = w_ai + w_yeomen + w_land + w_energy + w_other

    r_blended = (w_ai     * r_ai     +
                 w_yeomen * r_yeomen +
                 w_land   * r_land   +
                 w_energy * r_energy +
                 w_other  * 0.04) / total_w

    # ── Asset valuations ──────────────────────────────────────────────────────
    implied_pe       = 1.0 / np.maximum(r_blended, 0.01)
    land_price_idx   = (1 + R_LAND_APPREC) ** t * 100
    energy_price_idx = (r_energy / R_ENERGY_0) * 100

    # ── Aggregate MPC (for output/diagnostics) ────────────────────────────────
    mpc_aggregate = (conc_cap_income * mpc_conc +
                     yeomen_income   * MPC_YEOMEN +
                     dao_income      * MPC_DAO +
                     auto_labor_income * 0.90) / np.maximum(total_income, 1)

    # ── Tax leakage diagnostic ────────────────────────────────────────────────
    # How much tax revenue is lost to enforcement gap vs. statutory rate
    tax_lost_to_leakage = tax_k * (1 - enforcement) * conc_cap_income

    # ── Sovereign debt dynamics ───────────────────────────────────────────────
    # Debt stock held constant at 2025 initial value (static debt analysis).
    # Real squeeze comes from nominal GDP contraction: interest stays fixed
    # while the economy it is measured against shrinks.
    # interest_pct_revenue: fraction of tax revenue consumed by debt service.
    # In worst case this rises from ~15% to 35-45%, directly crowding out UBI.
    debt_gdp_ratio       = DEBT_INITIAL_BN / gdp_nom
    interest_pct_revenue = interest_burden_bn / np.maximum(tax_total, 1) * 100
    fiscal_space_bn      = tax_total - existing_spending  # before UBI; can go negative

    return pd.DataFrame({
        "year":                  year,
        "t":                     t,

        # GDP
        "gdp_nom_bn":            gdp_nom,
        "gdp_real_idx":          gdp_real_idx,
        "human_nom_bn":          human_nom,
        "human_pct_gdp":         human_nom / gdp_nom * 100,

        # Labour
        "total_displaced_m":     total_displaced,
        "human_workers_m":       human_workers,
        "net_without_income_m":  net_without_income,
        "know_auto_pct":         know_auto * 100,
        "phys_auto_pct":         phys_auto * 100,

        # Income
        "labor_income_bn":       total_labor_income,
        "capital_income_bn":     total_capital_income,
        "yeomen_income_bn":      yeomen_income,
        "dao_income_bn":         dao_income,
        "govt_dao_income_bn":    govt_dao_income,
        "govt_dao_cost_bn":      govt_dao_cost,
        "compute_pool_bn":       compute_pool_income,
        "compute_dividend_k":    compute_dividend_k,
        "yeomen_effective":      yeomen_effective,
        "levy_multiplier":       np.full(n_years, 1.0) if levy_prog == 0 else levy_multiplier,
        "labor_share_pct":       labor_share_pct,
        "gini_proxy":            gini_proxy,
        "mpc_aggregate":         mpc_aggregate * 100,

        # Government
        "tax_total_bn":          tax_total,
        "tax_k_effective":       tax_k_effective,
        "tax_lost_leakage_bn":   tax_lost_to_leakage,
        "redistributable_bn":    redistributable,
        "ubi_per_person_k":      ubi_per_person,
        "existing_spending_bn":  existing_spending,
        "interest_burden_bn":    interest_burden_bn,

        # Sovereign debt dynamics
        "debt_gdp_ratio":        debt_gdp_ratio,
        "interest_pct_revenue":  interest_pct_revenue,
        "fiscal_space_bn":       fiscal_space_bn,

        # Welfare (UBI + home production buffer)
        "effective_welfare_k":   effective_welfare_k,
        "home_prod_avg_k":       np.full(n_years, home_prod_avg),

        # Human economy
        "human_wage_k":          human_wage_k,

        # Capital returns (%)
        "r_ai_pct":              r_ai     * 100,
        "r_yeomen_pct":          r_yeomen * 100,
        "r_land_pct":            r_land   * 100,
        "r_energy_pct":          r_energy * 100,
        "r_blended_pct":         r_blended * 100,

        # Valuations
        "implied_pe":            implied_pe,
        "land_price_idx":        land_price_idx,
        "energy_price_idx":      energy_price_idx,

        # 6-sector nominal GDP breakdown (new)
        "nom_gdp_bn":            gdp_nom,
        "nom_know_bn":           know_nom,
        "nom_ai_svc_bn":         ai_svc_nom,
        "nom_phys_bn":           phys_nom,
        "nom_energy_bn":         energy_nom,
        "energy_phase":          np.where(
                                     np.arange(n_years) < mid * ENERGY_ROBOTICS_TRANSITION_MULT,
                                     1, 2),
        "nom_scarcity_bn":       scarcity_nom,
        "yeomen_friction_cost_bn": yeomen_friction_cost,

        # AI services automation
        "ai_svc_auto_pct":       auto_ai_svc * 100,
    })


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING
# ─────────────────────────────────────────────────────────────────────────────

def plot(results: dict, outfile: str = "ai_economy.png"):
    fig = plt.figure(figsize=(22, 35))
    fig.suptitle(
        "AI Economic Transition Model  |  2025–2060\n"
        "Automation speed  ×  Yeomen/DAO ownership  ×  Capital tax rate  ×  Enforcement",
        fontsize=13, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(5, 3, figure=fig, hspace=0.50, wspace=0.35)

    panels = [
        # Row 0: GDP and displacement
        (gs[0, 0], "gdp_nom_bn",           "$T",       "Nominal GDP",                    1/1000),
        (gs[0, 1], "gdp_real_idx",         "Index",    "Real GDP (2025=100)",             1),
        (gs[0, 2], "net_without_income_m", "Millions", "Workers w/o Income",              1),

        # Row 1: Inequality and welfare
        (gs[1, 0], "labor_share_pct",      "%",        "Labour Share of Income",          1),
        (gs[1, 1], "gini_proxy",           "Gini",     "Inequality (Gini proxy)",         1),
        (gs[1, 2], "effective_welfare_k",   "$k/yr",    "Effective Welfare (UBI+Home)",   1),

        # Row 2: Government finances
        (gs[2, 0], "tax_total_bn",         "$T",       "Total Tax Revenue",               1/1000),
        (gs[2, 1], "redistributable_bn",   "$T",       "Redistributable Surplus",         1/1000),
        (gs[2, 2], "human_wage_k",         "$k/yr",    "Human Economy Wage",              1),

        # Row 3: Capital and enforcement
        (gs[3, 0], "r_blended_pct",        "% return", "Blended Capital Return",          1),
        (gs[3, 1], "tax_lost_leakage_bn",  "$T",       "Tax Lost to Enforcement Gap",     1/1000),
        (gs[3, 2], "human_pct_gdp",        "% of GDP", "Human Economy % of GDP",         1),

        # Row 4: Sovereign debt dynamics (new)
        (gs[4, 0], "debt_gdp_ratio",       "ratio",    "Debt / Nominal GDP",              1),
        (gs[4, 1], "interest_pct_revenue", "%",        "Interest as % of Tax Revenue",    1),
        (gs[4, 2], "fiscal_space_bn",      "$T",       "Fiscal Space (before UBI)",       1/1000),
    ]

    axes = [fig.add_subplot(loc) for loc, *_ in panels]

    for i, (name, df) in enumerate(results.items()):
        color = COLORS[i % len(COLORS)]
        hl    = name in HIGHLIGHT
        x     = df["year"]
        for ax, (_, col, unit, title, scale) in zip(axes, panels):
            ax.plot(x, df[col] * scale, color=color,
                    alpha=1.0 if hl else 0.22,
                    linewidth=2.0 if hl else 0.8,
                    label=name if hl else "_nolegend_")

    for ax, (_, col, unit, title, scale) in zip(axes, panels):
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel(unit, fontsize=9)
        ax.set_xlabel("Year", fontsize=9)
        ax.grid(True, alpha=0.25)
        ax.set_xlim(2025, 2059)
        ax.legend(fontsize=6, loc="best", framealpha=0.7)

    # Add row separator annotation above debt row
    fig.text(0.5, 0.21, "── Sovereign Debt Dynamics ──",
             ha="center", va="center", fontsize=10, color="#555555",
             fontweight="bold")

    # Dedicated capital returns panel: replace human_pct_gdp (gs[3,2])
    ax_ret = axes[11]   # gs[3, 2]
    ax_ret.clear()
    mid_df = results.get("Medium / Moderate yeomen / Med tax",
                         list(results.values())[0])
    x = mid_df["year"]
    ax_ret.plot(x, mid_df["r_ai_pct"],      label="Concentrated AI capital", lw=2, color="#d62728")
    ax_ret.plot(x, mid_df["r_yeomen_pct"],  label="Yeomen (competitive)",    lw=2, color="#2ca02c")
    ax_ret.plot(x, mid_df["r_land_pct"],    label="Land",                    lw=2, color="#ff7f0e")
    ax_ret.plot(x, mid_df["r_energy_pct"],  label="Energy infrastructure",   lw=2, color="#9467bd")
    ax_ret.plot(x, mid_df["r_blended_pct"], label="Blended market",          lw=2, color="#1f77b4",
                linestyle="--")
    ax_ret.set_title("Capital Returns by Asset Class", fontsize=10, fontweight="bold")
    ax_ret.set_ylabel("% annual return", fontsize=9)
    ax_ret.set_xlabel("Year", fontsize=9)
    ax_ret.legend(fontsize=7)
    ax_ret.grid(True, alpha=0.25)
    ax_ret.set_xlim(2025, 2059)

    plt.savefig(outfile, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Chart saved → {outfile}")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY TABLE
# ─────────────────────────────────────────────────────────────────────────────

CHECKPOINTS = [5, 10, 20, 30]

METRICS = [
    ("gdp_nom_bn",          "Nominal GDP ($T)",                  lambda v: f"${v/1000:.1f}T"),
    ("gdp_real_idx",        "Real GDP index (2025=100)",         lambda v: f"{v:.0f}"),
    ("know_auto_pct",       "Knowledge work automated (%)",      lambda v: f"{v:.0f}%"),
    ("phys_auto_pct",       "Physical work automated (%)",       lambda v: f"{v:.0f}%"),
    ("net_without_income_m","Workers w/o income (M)",            lambda v: f"{v:.0f}M"),
    ("human_pct_gdp",       "Human economy % of GDP (derived)",  lambda v: f"{v:.1f}%"),
    ("human_wage_k",        "Human economy wage ($k/yr)",        lambda v: f"${v:.0f}k"),
    ("labor_share_pct",     "Labour share of income (%)",        lambda v: f"{v:.0f}%"),
    ("gini_proxy",          "Gini proxy",                        lambda v: f"{v:.3f}"),
    ("mpc_aggregate",       "Aggregate MPC on income (%)",       lambda v: f"{v:.0f}%"),
    ("tax_total_bn",        "Tax revenue ($T)",                  lambda v: f"${v/1000:.1f}T"),
    ("tax_k_effective",     "Effective capital tax rate",        lambda v: f"{v:.0%}"),
    ("tax_lost_leakage_bn", "Tax lost to enforcement gap ($T)",  lambda v: f"${v/1000:.1f}T"),
    ("redistributable_bn",  "Redistributable surplus ($T)",      lambda v: f"${v/1000:.1f}T"),
    ("ubi_per_person_k",    "Max UBI per person ($k/yr)",        lambda v: f"${v:.0f}k"),
    ("effective_welfare_k", "Effective welfare (UBI+home) $k/yr",lambda v: f"${v:.0f}k"),
    ("dao_income_bn",       "DAO commons income ($T)",           lambda v: f"${v/1000:.2f}T"),
    ("govt_dao_income_bn",  "Govt daoified income ($T)",         lambda v: f"${v/1000:.2f}T"),
    ("compute_pool_bn",     "Public AI pool revenue ($T)",       lambda v: f"${v/1000:.2f}T"),
    ("compute_dividend_k",  "Citizen compute dividend ($k/yr)",  lambda v: f"${v:.1f}k"),
    ("yeomen_effective",    "Effective yeomen frac (w/ levy)",   lambda v: f"{v:.2f}"),
    ("r_ai_pct",            "Return: concentrated AI (%)",       lambda v: f"{v:.1f}%"),
    ("r_yeomen_pct",        "Return: yeomen tools (%)",          lambda v: f"{v:.1f}%"),
    ("r_land_pct",          "Return: land (%)",                  lambda v: f"{v:.1f}%"),
    ("r_energy_pct",        "Return: energy infra (%)",          lambda v: f"{v:.1f}%"),
    ("r_blended_pct",       "Return: blended market (%)",        lambda v: f"{v:.1f}%"),
    ("implied_pe",          "Implied equity P/E",                lambda v: f"{v:.1f}x"),
    ("land_price_idx",      "Land price index (2025=100)",       lambda v: f"{v:.0f}"),
    # Sovereign debt
    ("debt_gdp_ratio",      "Debt / nominal GDP",                lambda v: f"{v:.2f}x"),
    ("interest_pct_revenue","Interest as % of tax revenue",      lambda v: f"{v:.0f}%"),
    ("fiscal_space_bn",     "Fiscal space before UBI ($T)",      lambda v: f"${v/1000:.1f}T"),
]


def print_summary(results: dict):
    col_w = 15
    header_right = "".join(f"{'t+'+str(y)+'yr':>{col_w}}" for y in CHECKPOINTS)
    for name, df in results.items():
        print("\n" + "═" * 88)
        print(f"  {name}")
        print("═" * 88)
        print(f"{'Metric':<44}" + header_right)
        print("─" * 88)
        for col, label, fmt in METRICS:
            row = f"{label:<44}"
            for y in CHECKPOINTS:
                v = df[df["t"] == y][col]
                row += f"{fmt(v.values[0]):>{col_w}}" if len(v) else f"{'—':>{col_w}}"
            print(row)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    results = {}
    for name, params in SCENARIOS.items():
        results[name] = run(**params)
        print(f"  ✓  {name}")

    plot(results)
    print_summary(results)

    for name, df in results.items():
        slug = name.replace(" ", "_").replace("/", "-").lower()[:60]
        df.to_csv(f"scenario_{slug}.csv", index=False)
    print("\nCSVs saved.")


if __name__ == "__main__":
    main()
