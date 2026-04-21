"""
Agent-Based Model — AI Economic Transition (2026-2030)
=======================================================
Monthly timestep ABM with individual consumer and enterprise agents.

Primary question: Are the SFC model's parametric assumptions (MPC, yeomen
share, automation speed) realistic when built from individual agent behaviour?

Secondary question: Is the assumed yeomen capital share sustainable under
competitive pressure from platforms?

Architecture:
  - Imports Params, s_curve from model_sfc.py for consistency
  - Consumer agents: individual state + monthly decide()
  - Enterprise agents: individual state + monthly decide()
  - GoodsMarket: matches consumer demand to enterprise supply by sector
  - LabourMarket: matches enterprise hiring to consumer job-seeking
  - Monthly loop with SFC accounting check at aggregate level

Cost estimate (Gemini Flash):
  ~3,000 agents × 60 months × 15% fresh LLM calls ≈ 27k calls ≈ $0.80-1.50/run
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
import json
import hashlib
import os
from pathlib import Path

from model_sfc import Params, s_curve
from archetypes import (
    CONSUMER_ARCHETYPES, ENTERPRISE_ARCHETYPES,
    US_ADULTS_M, US_GDP_2025_BN,
)


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ABMConfig:
    """ABM-specific parameters (on top of SFC Params)."""
    # Time
    start_year: int = 2026
    n_months: int = 60           # 5 years (2026-2030)

    # Agent instantiation
    agents_per_consumer_archetype: int = 25   # stochastic instances per template
    agents_per_enterprise_archetype: int = 10

    # LLM
    use_llm: bool = False         # False = fixed rules; True = Gemini decide()
    llm_call_rate: float = 0.15   # fraction of agent-steps that get fresh LLM calls
    cache_dir: str = ".abm_cache"

    # Market dynamics
    price_adjustment_speed: float = 0.05    # monthly price adjustment rate
    wage_adjustment_speed: float = 0.03     # monthly wage adjustment rate
    market_share_inertia: float = 0.90      # fraction of market share retained per month

    # Yeomen-specific
    yeomen_compute_premium: float = 3.3     # yeomen pay 3.3× platform compute cost
    yeomen_cac_premium: float = 5.0         # customer acquisition cost multiple vs platform
    platform_predatory_threshold: float = 0.3  # platforms can run at this margin to kill yeomen

    # Financial
    interest_rate_yeomen: float = 0.12      # annual borrowing rate for yeomen
    interest_rate_platform: float = 0.04    # annual borrowing rate for platforms
    bankruptcy_threshold: float = -50.0     # $k net worth → firm exits

    # Retraining
    retraining_subsidy_k: float = 0.0       # $k/yr government retraining subsidy


# ─────────────────────────────────────────────────────────────────────────────
# CONSUMER AGENT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ConsumerAgent:
    """Individual consumer agent with monthly state."""
    agent_id: int
    archetype: str        # name from CONSUMER_ARCHETYPES
    category: str

    # State ($k)
    income_k: float       # annual income (current)
    wealth_k: float       # net financial wealth
    debt_k: float         # outstanding debt
    monthly_income_k: float = 0.0

    # Employment
    employed: bool = True
    employer_id: int = -1        # which enterprise agent employs them
    occupation: str = ""
    months_unemployed: int = 0
    retraining_months_left: int = 0

    # Behavioural parameters (drawn stochastically from archetype)
    auto_exposure: float = 0.5
    auto_type: str = "knowledge"
    human_svc_share: float = 0.12
    retraining_years: float = 2.0

    # Consumption tracking (monthly, $k)
    monthly_consumption_k: float = 0.0
    monthly_human_svc_k: float = 0.0
    monthly_auto_goods_k: float = 0.0
    monthly_saving_k: float = 0.0

    # Pop weight: how many real people this agent represents
    pop_weight: float = 1.0      # = archetype pop_weight × US_ADULTS_M / n_agents

    # Persona for LLM
    description: str = ""

    def mpc(self) -> float:
        """Emergent MPC based on financial situation."""
        # Wealth-to-income ratio determines precautionary saving
        if self.income_k <= 0:
            return 0.95  # spend almost everything (transfer income)
        wir = self.wealth_k / max(self.income_k, 1)
        if wir < 0.5:
            return 0.92   # liquidity constrained
        elif wir < 2.0:
            return 0.82   # moderate buffer
        elif wir < 10.0:
            return 0.65   # comfortable
        else:
            return 0.30   # wealthy, save most

    def decide_monthly(self, price_index: float, unemployment_rate: float,
                       automation_pct: float) -> dict:
        """
        Monthly consumption/saving decision (fixed rules).
        Override with LLM in LLM mode.
        """
        monthly_income = self.income_k / 12.0
        interest_monthly = self.debt_k * 0.06 / 12.0  # rough avg rate

        disposable = max(monthly_income - interest_monthly, 0)

        # MPC adjusted for uncertainty
        base_mpc = self.mpc()
        # Precautionary saving increases with automation exposure and unemployment
        uncertainty_adj = self.auto_exposure * automation_pct * 0.1
        unemployment_adj = unemployment_rate * 0.05
        adj_mpc = max(base_mpc - uncertainty_adj - unemployment_adj, 0.15)

        if not self.employed:
            # Unemployed: draw down savings, high MPC on what you have
            adj_mpc = min(0.95, adj_mpc + 0.15)

        consume = disposable * adj_mpc

        # Wealth effect: small fraction of wealth consumed
        if self.wealth_k > 0:
            consume += self.wealth_k * 0.003 / 1.0  # 0.3% monthly

        consume = max(consume, 0)

        # Split between human services and automated goods
        # As prices of automated goods fall, shift toward them (price elasticity)
        eff_human_share = self.human_svc_share
        if price_index < 0.9:
            # Automated goods are cheaper → buy more of them
            eff_human_share *= (price_index / 0.9) ** 0.5  # elasticity ~0.5

        human_svc = consume * eff_human_share
        auto_goods = consume * (1 - eff_human_share)
        saving = disposable - consume

        self.monthly_consumption_k = consume
        self.monthly_human_svc_k = human_svc
        self.monthly_auto_goods_k = auto_goods
        self.monthly_saving_k = saving

        return {
            "consume_k": consume,
            "human_svc_k": human_svc,
            "auto_goods_k": auto_goods,
            "saving_k": saving,
        }

    def update_balance_sheet(self):
        """Update wealth and debt from monthly flows."""
        self.wealth_k += self.monthly_saving_k
        if self.wealth_k < 0 and self.debt_k < 200:
            # Borrow to cover shortfall (up to limit)
            shortfall = -self.wealth_k
            self.debt_k += shortfall
            self.wealth_k = 0
        # Small debt repayment if wealth allows
        if self.wealth_k > 10 and self.debt_k > 0:
            repay = min(self.debt_k * 0.02, self.wealth_k * 0.05)
            self.debt_k -= repay
            self.wealth_k -= repay


# ─────────────────────────────────────────────────────────────────────────────
# ENTERPRISE AGENT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EnterpriseAgent:
    """Individual enterprise agent with monthly state."""
    agent_id: int
    archetype: str
    category: str
    sector: str
    output_category: str    # knowledge_services, physical_goods, human_services, physical_services

    # Financials ($bn for large firms, but stored as $k for consistency)
    revenue_k: float        # annual revenue ($k)
    capital_k: float        # capital stock ($k)
    cash_k: float = 0.0     # cash on hand ($k)
    debt_k: float = 0.0     # outstanding debt ($k)

    # Workforce
    headcount: int = 0
    target_headcount: int = 0
    employee_ids: list = field(default_factory=list)
    labour_categories: list = field(default_factory=list)
    wage_k: float = 50.0    # average annual wage ($k)

    # AI adoption
    ai_adoption: float = 0.0        # 0-1 current level
    ai_adoption_target: float = 0.5  # where heading
    compute_cost_idx: float = 1.0   # relative compute cost (platforms < yeomen)
    market_power: float = 0.0       # pricing power

    # Market position
    market_share: float = 0.0       # within sector
    price_idx: float = 1.0          # relative to sector average
    quality_idx: float = 1.0        # perceived quality

    # Firm count: how many real firms this agent represents
    firm_weight: float = 1.0

    # Status
    alive: bool = True
    months_negative_cash: int = 0

    # Persona for LLM
    description: str = ""

    def unit_cost(self, automation_level: float) -> float:
        """Unit cost as function of AI adoption and compute costs."""
        # Labour cost (decreases with automation)
        labour_cost = (1 - self.ai_adoption * automation_level) * self.wage_k * self.headcount / max(self.revenue_k, 1)
        # Compute cost (increases with AI adoption, modulated by compute_cost_idx)
        compute_cost = self.ai_adoption * self.compute_cost_idx * 0.15
        # Capital/overhead
        overhead = 0.15
        return labour_cost + compute_cost + overhead

    def decide_monthly(self, sector_demand_k: float, automation_level: float,
                       competitor_prices: list, month: int) -> dict:
        """
        Monthly enterprise decision: pricing, hiring, AI investment.
        """
        # Revenue based on market share × sector demand
        monthly_revenue = (self.market_share * sector_demand_k) / 12.0

        # Cost structure
        uc = self.unit_cost(automation_level)
        monthly_cost = monthly_revenue * uc

        # Profit
        monthly_profit = monthly_revenue - monthly_cost

        # Pricing decision: undercut if losing share, raise if winning
        avg_competitor_price = np.mean(competitor_prices) if competitor_prices else 1.0
        if self.market_power > 0.5:
            # Dominant firm: price at premium
            target_price = avg_competitor_price * (1 + self.market_power * 0.2)
        else:
            # Competitive firm: try to match or undercut
            target_price = avg_competitor_price * (1 - (1 - self.market_power) * 0.05)

        # Predatory pricing: platforms can go below cost temporarily
        if self.category == "big_tech" and self.cash_k > monthly_cost * 12:
            # Can sustain losses to gain share
            target_price = min(target_price, uc * 0.8)

        self.price_idx += (target_price - self.price_idx) * 0.1  # gradual adjustment

        # Hiring/firing decision
        revenue_per_worker = monthly_revenue / max(self.headcount, 1) * 12
        if revenue_per_worker > self.wage_k * 1.3:
            # Profitable per worker → consider hiring
            self.target_headcount = min(self.headcount + max(1, self.headcount // 20),
                                         int(self.headcount * 1.5))
        elif revenue_per_worker < self.wage_k * 0.8:
            # Losing money per worker → reduce headcount
            self.target_headcount = max(1, int(self.headcount * 0.95))

        # AI adoption: gradually move toward target
        if self.ai_adoption < self.ai_adoption_target:
            invest_rate = 0.02 if self.category in ["big_tech", "finance"] else 0.01
            self.ai_adoption = min(self.ai_adoption + invest_rate, self.ai_adoption_target)

        # Cash update
        self.cash_k += monthly_profit * 1000  # convert to $k

        # Bankruptcy check
        if self.cash_k < self.capital_k * -0.2:
            self.months_negative_cash += 1
        else:
            self.months_negative_cash = 0

        if self.months_negative_cash > 6:
            self.alive = False

        return {
            "monthly_revenue_k": monthly_revenue * 1000,
            "monthly_profit_k": monthly_profit * 1000,
            "target_price": target_price,
            "target_headcount": self.target_headcount,
            "ai_adoption": self.ai_adoption,
        }


# ─────────────────────────────────────────────────────────────────────────────
# MARKETS
# ─────────────────────────────────────────────────────────────────────────────

class GoodsMarket:
    """
    Matches consumer demand to enterprise supply by sector/category.
    Computes market shares based on price and quality.
    """

    def __init__(self):
        self.sector_demand = defaultdict(float)   # sector → total demand ($k/month)
        self.sector_supply = defaultdict(list)     # sector → list of enterprise agents

    def clear(self):
        self.sector_demand.clear()
        self.sector_supply.clear()

    def register_demand(self, sector: str, amount_k: float):
        self.sector_demand[sector] += amount_k

    def register_supply(self, enterprise: EnterpriseAgent):
        self.sector_supply[enterprise.sector].append(enterprise)

    def compute_market_shares(self):
        """
        Compute market shares within each sector based on price and quality.
        Lower price + higher quality → more share.
        """
        for sector, enterprises in self.sector_supply.items():
            alive = [e for e in enterprises if e.alive]
            if not alive:
                continue

            # Score = quality / price (higher is better)
            scores = []
            for e in alive:
                score = (e.quality_idx / max(e.price_idx, 0.01)) * (1 + e.market_power * 0.5)
                # Weight by firm size (larger firms have brand/scale advantage)
                score *= (e.firm_weight ** 0.3)
                scores.append(max(score, 0.001))

            total_score = sum(scores)
            for e, score in zip(alive, scores):
                new_share = score / total_score
                # Inertia: market share changes slowly
                e.market_share = e.market_share * 0.9 + new_share * 0.1


class LabourMarket:
    """
    Matches enterprise hiring needs to consumer job-seeking.
    """

    def __init__(self):
        self.job_openings: list[tuple[EnterpriseAgent, str, float]] = []  # (firm, occupation, wage)
        self.job_seekers: list[ConsumerAgent] = []

    def clear(self):
        self.job_openings.clear()
        self.job_seekers.clear()

    def register_opening(self, enterprise: EnterpriseAgent, occupation: str, wage_k: float):
        self.job_openings.append((enterprise, occupation, wage_k))

    def register_seeker(self, consumer: ConsumerAgent):
        self.job_seekers.append(consumer)

    def match(self):
        """
        Match seekers to openings. Matching works in two passes:
        1. Exact occupation match
        2. Category-compatible match (any seeker can take adjacent jobs)
        Priority by months unemployed (longer wait → higher priority).
        """
        seekers = sorted(self.job_seekers, key=lambda c: -c.months_unemployed)

        # Group openings by occupation
        openings_by_occ = defaultdict(list)
        for firm, occ, wage in self.job_openings:
            openings_by_occ[occ].append((firm, wage))

        # All remaining openings (for pass 2)
        all_openings = list(self.job_openings)

        matches = []
        matched_seekers = set()

        # Pass 1: exact occupation match
        for seeker in seekers:
            occ = seeker.occupation
            if occ in openings_by_occ and openings_by_occ[occ]:
                firm, wage = openings_by_occ[occ].pop(0)
                matches.append((seeker, firm, wage))
                matched_seekers.add(seeker.agent_id)

        # Pass 2: any remaining seeker takes any remaining opening
        remaining_openings = []
        for firm, occ, wage in all_openings:
            # Check if this opening was consumed in pass 1
            if openings_by_occ[occ]:  # still has openings
                remaining_openings.append((firm, occ, wage))
        # Deduplicate: use openings that weren't matched
        remaining_openings = []
        for occ, pairs in openings_by_occ.items():
            for firm, wage in pairs:
                remaining_openings.append((firm, occ, wage))

        for seeker in seekers:
            if seeker.agent_id in matched_seekers:
                continue
            if not remaining_openings:
                break
            # Take any opening (retraining complete = flexible)
            if seeker.retraining_months_left == 0:
                firm, occ, wage = remaining_openings.pop(0)
                matches.append((seeker, firm, wage))
                matched_seekers.add(seeker.agent_id)

        # Apply matches
        for consumer, firm, wage in matches:
            consumer.employed = True
            consumer.employer_id = firm.agent_id
            consumer.income_k = wage
            consumer.months_unemployed = 0
            firm.employee_ids.append(consumer.agent_id)
            firm.headcount = len(firm.employee_ids)

        return len(matches)


# ─────────────────────────────────────────────────────────────────────────────
# ABM MODEL
# ─────────────────────────────────────────────────────────────────────────────

class ABMModel:
    """
    Main ABM simulation.

    Monthly loop:
      1. Compute automation levels (from SFC s_curve)
      2. Enterprise decisions (pricing, hiring/firing, AI adoption)
      3. Labour market matching (displaced workers seek new jobs)
      4. Consumer decisions (consumption, saving)
      5. Goods market clearing (demand → enterprise revenue)
      6. Balance sheet updates
      7. Record aggregates for reconciliation
    """

    def __init__(self, sfc_params: Params, config: ABMConfig):
        self.p = sfc_params
        self.cfg = config
        self.consumers: list[ConsumerAgent] = []
        self.enterprises: list[EnterpriseAgent] = []
        self.goods_market = GoodsMarket()
        self.labour_market = LabourMarket()
        self.history: list[dict] = []

        self._init_agents()

    def _init_agents(self):
        """Instantiate agents from archetypes with stochastic variation."""
        rng = np.random.default_rng(42)
        agent_id = 0

        # Consumer agents
        for arch in CONSUMER_ARCHETYPES:
            n = self.cfg.agents_per_consumer_archetype
            pop_weight = arch["pop_weight"] * US_ADULTS_M / n  # M people per agent

            for i in range(n):
                # Stochastic variation
                income = max(5, rng.normal(arch["income_mean_k"], arch["income_sigma_k"]))
                wealth = max(0, rng.lognormal(
                    np.log(max(arch["wealth_mean_k"], 1)),
                    0.8  # lognormal spread
                ))
                debt = max(0, rng.normal(arch["debt_mean_k"], arch["debt_mean_k"] * 0.3))

                agent = ConsumerAgent(
                    agent_id=agent_id,
                    archetype=arch["name"],
                    category=arch["category"],
                    income_k=income,
                    wealth_k=wealth,
                    debt_k=debt,
                    employed=(arch["category"] not in ("transitional",) or arch["name"] == "recent_graduate"),
                    occupation=arch["name"],
                    auto_exposure=arch["auto_exposure"] * rng.uniform(0.8, 1.2),
                    auto_type=arch["auto_type"],
                    human_svc_share=arch["human_svc_share"] * rng.uniform(0.7, 1.3),
                    retraining_years=arch["retraining_years"],
                    pop_weight=pop_weight,
                    description=arch["description"],
                )
                self.consumers.append(agent)
                agent_id += 1

        # Enterprise agents
        for arch in ENTERPRISE_ARCHETYPES:
            n = self.cfg.agents_per_enterprise_archetype
            firm_weight = arch["firm_count"] / n

            for i in range(n):
                revenue = max(0.001, rng.lognormal(
                    np.log(max(arch["revenue_mean_bn"] * 1e6, 1)),  # convert $bn to $k
                    0.5
                ))
                capital = max(0.001, arch["capital_stock_bn"] * 1e6 * rng.uniform(0.5, 1.5))

                agent = EnterpriseAgent(
                    agent_id=agent_id,
                    archetype=arch["name"],
                    category=arch["category"],
                    sector=arch["sector"],
                    output_category=arch["output_category"],
                    revenue_k=revenue,
                    capital_k=capital,
                    cash_k=revenue * 0.1,  # 10% of revenue as initial cash
                    headcount=max(1, int(arch["headcount_mean"] * rng.uniform(0.5, 1.5))),
                    labour_categories=arch.get("labour_categories", []),
                    wage_k=50.0,  # will be calibrated from consumer incomes
                    ai_adoption=arch["ai_adoption"] * rng.uniform(0.7, 1.0),
                    ai_adoption_target=min(arch["ai_adoption"] * 1.3, 0.98),
                    compute_cost_idx=arch["compute_cost_idx"],
                    market_power=arch["market_power"],
                    firm_weight=firm_weight,
                    description=arch["description"],
                )
                # Initial market share proportional to revenue × firm_weight
                sector_total_rev = sum(
                    a["firm_count"] * a["revenue_mean_bn"]
                    for a in ENTERPRISE_ARCHETYPES if a["sector"] == arch["sector"]
                )
                agent.market_share = (firm_weight * arch["revenue_mean_bn"]) / max(sector_total_rev, 0.001)
                self.enterprises.append(agent)
                agent_id += 1

        print(f"Initialized {len(self.consumers)} consumer agents, "
              f"{len(self.enterprises)} enterprise agents")

    def _automation_level(self, month: int) -> tuple[float, float]:
        """Current knowledge and physical automation levels."""
        t = month / 12.0  # convert to years from 2026
        # Offset: model starts at 2026, SFC starts at 2025, so add 1 year
        t_sfc = t + 1.0
        ka = s_curve(t_sfc, self.p.know_ceiling, 0.50, self.p.auto_mid)
        pa = s_curve(t_sfc, self.p.phys_ceiling, 0.28, self.p.auto_mid + self.p.phys_lag)
        return ka, pa

    def _displace_workers(self, know_auto: float, phys_auto: float, rng):
        """
        Probabilistically displace workers based on automation exposure.
        """
        for c in self.consumers:
            if not c.employed:
                continue
            # Displacement probability based on automation level and exposure
            if c.auto_type == "knowledge":
                auto_level = know_auto
            elif c.auto_type == "physical":
                auto_level = phys_auto
            else:
                auto_level = (know_auto + phys_auto) / 2

            # Monthly displacement probability
            # exposure × automation_level gives cumulative risk
            # Convert to monthly: p_monthly ≈ 1 - (1-p_annual)^(1/12)
            p_annual = c.auto_exposure * auto_level
            p_monthly = 1 - (1 - p_annual) ** (1/12)

            # Already employed agents have lower displacement (incumbency advantage)
            p_monthly *= 0.3  # only 30% of theoretical displacement materialises per month

            if rng.random() < p_monthly:
                c.employed = False
                c.employer_id = -1
                c.months_unemployed = 0
                c.retraining_months_left = int(c.retraining_years * 12)
                # Income drops to UBI-like floor
                c.income_k = max(c.income_k * 0.3, 15.0)

    def _update_unemployed(self):
        """Update unemployment counters and retraining status."""
        for c in self.consumers:
            if not c.employed:
                c.months_unemployed += 1
                if c.retraining_months_left > 0:
                    c.retraining_months_left -= 1

    def _compute_aggregates(self, month: int, know_auto: float,
                            phys_auto: float) -> dict:
        """Compute aggregate statistics for this month."""
        total_pop = sum(c.pop_weight for c in self.consumers)
        employed_pop = sum(c.pop_weight for c in self.consumers if c.employed)
        unemployed_pop = total_pop - employed_pop

        total_income = sum(c.income_k * c.pop_weight for c in self.consumers)
        total_consumption = sum(c.monthly_consumption_k * 12 * c.pop_weight
                                for c in self.consumers)
        total_human_svc = sum(c.monthly_human_svc_k * 12 * c.pop_weight
                              for c in self.consumers)
        total_auto_goods = sum(c.monthly_auto_goods_k * 12 * c.pop_weight
                               for c in self.consumers)
        total_wealth = sum(c.wealth_k * c.pop_weight for c in self.consumers)
        total_debt = sum(c.debt_k * c.pop_weight for c in self.consumers)

        # Emergent MPC
        agg_mpc = total_consumption / max(total_income, 1)

        # MPC by category
        mpc_by_cat = {}
        for cat in set(c.category for c in self.consumers):
            cat_income = sum(c.income_k * c.pop_weight
                             for c in self.consumers if c.category == cat)
            cat_consumption = sum(c.monthly_consumption_k * 12 * c.pop_weight
                                  for c in self.consumers if c.category == cat)
            mpc_by_cat[cat] = cat_consumption / max(cat_income, 1)

        # Enterprise aggregates
        alive_enterprises = [e for e in self.enterprises if e.alive]
        total_enterprise_revenue = sum(e.revenue_k * e.firm_weight / 1e6
                                       for e in alive_enterprises)  # $bn

        # Yeomen vs platform market share
        yeomen_revenue = sum(e.revenue_k * e.firm_weight / 1e6
                             for e in alive_enterprises
                             if e.category == "yeoman_dao")
        platform_revenue = sum(e.revenue_k * e.firm_weight / 1e6
                               for e in alive_enterprises
                               if e.category == "big_tech")
        services_revenue = sum(e.revenue_k * e.firm_weight / 1e6
                               for e in alive_enterprises
                               if e.output_category == "knowledge_services")

        yeomen_share = yeomen_revenue / max(services_revenue, 0.001)
        platform_share = platform_revenue / max(services_revenue, 0.001)

        # Firm deaths/births
        dead_firms = sum(e.firm_weight for e in self.enterprises if not e.alive)
        alive_firms = sum(e.firm_weight for e in alive_enterprises)

        # Yeomen alive
        yeomen_alive = sum(e.firm_weight for e in alive_enterprises
                           if e.category == "yeoman_dao")
        yeomen_total = sum(e.firm_weight for e in self.enterprises
                           if e.category == "yeoman_dao")

        # Gini proxy (from income distribution)
        incomes = sorted([c.income_k for c in self.consumers for _ in range(max(1, int(c.pop_weight)))])
        n = len(incomes)
        if n > 0 and sum(incomes) > 0:
            cumulative = np.cumsum(incomes)
            gini = 1 - 2 * sum(cumulative) / (n * cumulative[-1]) + 1/n
        else:
            gini = 0.5

        # Unemployment rate
        unemployment_rate = unemployed_pop / max(total_pop, 1)

        # Human services share of consumption
        human_svc_share = total_human_svc / max(total_consumption, 1)

        year_frac = self.cfg.start_year + month / 12.0

        return {
            "month": month,
            "year": year_frac,
            "know_auto_pct": know_auto * 100,
            "phys_auto_pct": phys_auto * 100,
            "unemployment_rate": unemployment_rate,
            "total_pop_m": total_pop,
            "employed_m": employed_pop,
            "unemployed_m": unemployed_pop,
            "total_income_bn": total_income / 1e3,    # $k × M = $bn
            "total_consumption_bn": total_consumption / 1e3,
            "total_human_svc_bn": total_human_svc / 1e3,
            "total_auto_goods_bn": total_auto_goods / 1e3,
            "total_wealth_bn": total_wealth / 1e3,
            "total_debt_bn": total_debt / 1e3,
            "aggregate_mpc": agg_mpc,
            "human_svc_share": human_svc_share,
            "gini": gini,
            "enterprise_revenue_bn": total_enterprise_revenue,
            "yeomen_share": yeomen_share,
            "platform_share": platform_share,
            "yeomen_alive_pct": yeomen_alive / max(yeomen_total, 1) * 100,
            "firms_alive": alive_firms,
            "firms_dead": dead_firms,
            **{f"mpc_{cat}": v for cat, v in mpc_by_cat.items()},
        }

    def run(self) -> pd.DataFrame:
        """Run the full ABM simulation."""
        rng = np.random.default_rng(42)

        print(f"\nRunning ABM: {self.cfg.start_year} to "
              f"{self.cfg.start_year + self.cfg.n_months // 12}")
        print(f"  {len(self.consumers)} consumers × {len(self.enterprises)} enterprises")
        print(f"  {self.cfg.n_months} monthly steps")
        print()

        for month in range(self.cfg.n_months):
            # 1. Automation levels
            know_auto, phys_auto = self._automation_level(month)

            # 2. Displace workers
            self._displace_workers(know_auto, phys_auto, rng)
            self._update_unemployed()

            # Unemployment rate for consumer decisions
            total_pop = sum(c.pop_weight for c in self.consumers)
            employed_pop = sum(c.pop_weight for c in self.consumers if c.employed)
            unemp_rate = 1 - employed_pop / max(total_pop, 1)

            # Price index (automated goods get cheaper)
            auto_price_idx = (1 - self.p.deflation_know * (1 - self.p.monopoly_rent)) ** (month / 12.0)
            composite_price = 0.7 * auto_price_idx + 0.3 * 1.0  # 30% human services at stable prices

            # 3. Consumer decisions
            for c in self.consumers:
                c.decide_monthly(composite_price, unemp_rate,
                                 (know_auto + phys_auto) / 2)

            # 4. Goods market: aggregate demand by sector mapping
            self.goods_market.clear()
            # Simple mapping: human_svc → healthcare, hospitality, education
            # auto_goods → retail, manufacturing, tech
            total_human_demand = sum(c.monthly_human_svc_k * c.pop_weight
                                     for c in self.consumers)
            total_auto_demand = sum(c.monthly_auto_goods_k * c.pop_weight
                                    for c in self.consumers)

            # Distribute to sectors (rough mapping)
            sector_demand = {
                "healthcare": total_human_demand * 0.30,
                "hospitality": total_human_demand * 0.25,
                "education": total_human_demand * 0.20,
                "retail": total_auto_demand * 0.35,
                "manufacturing": total_auto_demand * 0.25,
                "tech": total_auto_demand * 0.20,
                "financial_services": total_auto_demand * 0.10,
                "logistics": total_auto_demand * 0.10,
                "professional_services": total_human_demand * 0.15,
                "media": total_auto_demand * 0.05 + total_human_demand * 0.05,
                "agriculture": total_auto_demand * 0.05,
                "energy": total_auto_demand * 0.03,
                "government": total_human_demand * 0.05,
            }

            # 5. Enterprise decisions
            for e in self.enterprises:
                if not e.alive:
                    continue
                demand = sector_demand.get(e.sector, 0) * 12  # annualise
                competitors = [x.price_idx for x in self.enterprises
                               if x.sector == e.sector and x.alive and x.agent_id != e.agent_id]
                e.decide_monthly(demand, (know_auto + phys_auto) / 2,
                                 competitors, month)

            # 6. Market share computation
            for sector in set(e.sector for e in self.enterprises):
                sector_ents = [e for e in self.enterprises
                               if e.sector == sector and e.alive]
                if not sector_ents:
                    continue
                scores = []
                for e in sector_ents:
                    score = (e.quality_idx / max(e.price_idx, 0.01)) * (1 + e.market_power * 0.5)
                    score *= (e.firm_weight ** 0.2)
                    scores.append(max(score, 0.001))
                total_score = sum(scores)
                for e, score in zip(sector_ents, scores):
                    new_share = score / total_score
                    e.market_share = e.market_share * 0.92 + new_share * 0.08

            # 7. Labour market
            self.labour_market.clear()
            for e in self.enterprises:
                if not e.alive:
                    continue
                if e.headcount < e.target_headcount:
                    openings_needed = e.target_headcount - e.headcount
                    cats = e.labour_categories if e.labour_categories else ["general"]
                    for i in range(min(openings_needed, 5)):  # cap at 5 openings/month
                        occ = cats[i % len(cats)]
                        self.labour_market.register_opening(e, occ, e.wage_k)
            for c in self.consumers:
                if not c.employed and c.retraining_months_left == 0:
                    self.labour_market.register_seeker(c)
            matches = self.labour_market.match()

            # 8. Update balance sheets
            for c in self.consumers:
                c.update_balance_sheet()

            # 9. Record aggregates
            agg = self._compute_aggregates(month, know_auto, phys_auto)
            self.history.append(agg)

            # Progress
            if month % 12 == 0:
                yr = self.cfg.start_year + month // 12
                print(f"  Year {yr}: unemp={agg['unemployment_rate']:.1%}, "
                      f"MPC={agg['aggregate_mpc']:.3f}, "
                      f"yeomen_share={agg['yeomen_share']:.3f}, "
                      f"gini={agg['gini']:.3f}, "
                      f"matched={matches}")

        return pd.DataFrame(self.history)


# ─────────────────────────────────────────────────────────────────────────────
# RECONCILIATION — compare ABM emergent aggregates to SFC assumptions
# ─────────────────────────────────────────────────────────────────────────────

def reconcile(abm_df: pd.DataFrame, sfc_params: Params) -> pd.DataFrame:
    """
    Produce reconciliation table: SFC assumed vs ABM emergent.
    This is the primary output — validates whether SFC parametric
    assumptions hold when built from individual agent behaviour.
    """
    # Get ABM values at key timepoints
    month_12 = abm_df[abm_df.month == 11].iloc[0] if len(abm_df) > 11 else abm_df.iloc[-1]
    month_36 = abm_df[abm_df.month == 35].iloc[0] if len(abm_df) > 35 else abm_df.iloc[-1]
    month_60 = abm_df[abm_df.month == 59].iloc[0] if len(abm_df) > 59 else abm_df.iloc[-1]

    rows = [
        {
            "parameter": "Aggregate MPC (all HH)",
            "sfc_assumed": 0.72,
            "abm_year1": month_12["aggregate_mpc"],
            "abm_year3": month_36["aggregate_mpc"],
            "abm_year5": month_60["aggregate_mpc"],
        },
        {
            "parameter": "Human services share of consumption",
            "sfc_assumed": sfc_params.human_svc_h6,
            "abm_year1": month_12["human_svc_share"],
            "abm_year3": month_36["human_svc_share"],
            "abm_year5": month_60["human_svc_share"],
        },
        {
            "parameter": "Yeomen share of knowledge services",
            "sfc_assumed": sfc_params.yeomen_target,
            "abm_year1": month_12["yeomen_share"],
            "abm_year3": month_36["yeomen_share"],
            "abm_year5": month_60["yeomen_share"],
        },
        {
            "parameter": "Unemployment rate",
            "sfc_assumed": 0.04,  # baseline
            "abm_year1": month_12["unemployment_rate"],
            "abm_year3": month_36["unemployment_rate"],
            "abm_year5": month_60["unemployment_rate"],
        },
        {
            "parameter": "Gini coefficient",
            "sfc_assumed": 0.40,
            "abm_year1": month_12["gini"],
            "abm_year3": month_36["gini"],
            "abm_year5": month_60["gini"],
        },
        {
            "parameter": "Yeomen firms alive (%)",
            "sfc_assumed": 100.0,
            "abm_year1": month_12["yeomen_alive_pct"],
            "abm_year3": month_36["yeomen_alive_pct"],
            "abm_year5": month_60["yeomen_alive_pct"],
        },
    ]

    # Add MPC by category if available
    for cat_key in ["mpc_knowledge_high_exposure", "mpc_physical_high_exposure",
                    "mpc_care_low_exposure", "mpc_non_labour"]:
        if cat_key in month_12:
            sfc_map = {
                "mpc_knowledge_high_exposure": sfc_params.mpc_h1,  # rough mapping
                "mpc_physical_high_exposure": sfc_params.mpc_h4,
                "mpc_care_low_exposure": sfc_params.mpc_h6,
                "mpc_non_labour": sfc_params.mpc_h1,
            }
            rows.append({
                "parameter": f"MPC ({cat_key.replace('mpc_', '')})",
                "sfc_assumed": sfc_map.get(cat_key, 0.7),
                "abm_year1": month_12[cat_key],
                "abm_year3": month_36[cat_key],
                "abm_year5": month_60[cat_key],
            })

    recon_df = pd.DataFrame(rows)

    # Add delta columns
    for col in ["abm_year1", "abm_year3", "abm_year5"]:
        recon_df[f"delta_{col}"] = (
            (recon_df[col] - recon_df["sfc_assumed"]) / recon_df["sfc_assumed"].replace(0, 1) * 100
        )

    return recon_df


def print_reconciliation(recon_df: pd.DataFrame):
    """Pretty-print the reconciliation table."""
    print(f"\n{'='*90}")
    print(f"RECONCILIATION: SFC Assumptions vs ABM Emergent Aggregates")
    print(f"{'='*90}")
    print(f"{'Parameter':<40} {'SFC':>8} {'Y1':>8} {'Y3':>8} {'Y5':>8} {'Δ Y5':>8}")
    print(f"{'-'*90}")
    for _, row in recon_df.iterrows():
        delta = row.get("delta_abm_year5", 0)
        flag = " ←" if abs(delta) > 20 else ""
        print(f"{row['parameter']:<40} "
              f"{row['sfc_assumed']:>8.3f} "
              f"{row['abm_year1']:>8.3f} "
              f"{row['abm_year3']:>8.3f} "
              f"{row['abm_year5']:>8.3f} "
              f"{delta:>+7.0f}%{flag}")


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING
# ─────────────────────────────────────────────────────────────────────────────

def plot_abm(df: pd.DataFrame, outfile="ai_economy_abm.png"):
    """Plot key ABM outputs."""
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(18, 14))
    fig.suptitle(
        "Agent-Based Model — AI Economic Transition (2026-2030)\n"
        "Monthly timestep, ~3,000 agents",
        fontsize=13, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

    x = df["year"]

    panels = [
        (gs[0, 0], "unemployment_rate", "Unemployment Rate", "%", 100),
        (gs[0, 1], "aggregate_mpc", "Aggregate MPC", "MPC", 1),
        (gs[0, 2], "gini", "Gini Coefficient", "Gini", 1),
        (gs[1, 0], "yeomen_share", "Yeomen Share (Knowledge Svcs)", "share", 1),
        (gs[1, 1], "platform_share", "Platform Share (Knowledge Svcs)", "share", 1),
        (gs[1, 2], "yeomen_alive_pct", "Yeomen Firms Alive", "%", 1),
        (gs[2, 0], "human_svc_share", "Human Services Share of Consumption", "share", 1),
        (gs[2, 1], "know_auto_pct", "Knowledge Automation", "%", 1),
        (gs[2, 2], "total_consumption_bn", "Total Consumption", "$bn", 1),
    ]

    for loc, col, title, ylabel, scale in panels:
        ax = fig.add_subplot(loc)
        if col in df.columns:
            ax.plot(x, df[col] * scale, color="#2ca02c", lw=2)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xlabel("Year", fontsize=9)
        ax.grid(True, alpha=0.25)

    plt.savefig(outfile, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nChart saved → {outfile}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    # Use SFC params for the "Fast / High yeomen / High tax" scenario
    p = Params(
        auto_mid=5.0,
        yeomen_target=0.35,
        tax_k=0.35,
        enforcement=1.0,
        monopoly_rent=0.00,
    )

    cfg = ABMConfig(
        start_year=2026,
        n_months=60,
        agents_per_consumer_archetype=25,
        agents_per_enterprise_archetype=10,
        use_llm=False,
    )

    model = ABMModel(p, cfg)
    df = model.run()

    # Save time series
    df.to_csv("abm_timeseries.csv", index=False)
    print(f"\nTime series saved → abm_timeseries.csv")

    # Reconciliation
    recon = reconcile(df, p)
    print_reconciliation(recon)

    # Plot
    plot_abm(df)
