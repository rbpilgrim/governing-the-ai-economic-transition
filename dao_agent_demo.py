"""
DAO Procurement Agent — Collective AI Buying at Scale
======================================================
Shows how a DAO's AI agent manages procurement autonomously within
governance-set constraints, across many concurrent vendor relationships.

A DAO buyer is structurally different from a company buyer:
  • Collective treasury — funds belong to token holders, not a principal
  • Governance thresholds — spending authority tiers require votes
  • Transparency mandate — all spending visible to token holders
  • Vendor portfolio — manages relationships across many yeomen simultaneously
  • Concentration risk — governance limits exposure to any single vendor

Spending authority tiers:
  < $10k   →  Agent acts autonomously (routine, repeating needs)
  $10k–50k →  Council vote required (3 of 5 multisig council members)
  > $50k   →  Full token holder vote (simulated; 48h window, quorum 10%)

Demos:
  1. Autonomous procurement  — agent handles routine tasks within limit
  2. Council escalation      — mid-size contract triggers council vote
  3. Token holder vote       — large contract goes to full governance
  4. Portfolio management    — 30-day procurement cycle, many vendors
  5. Spending report         — transparent summary for token holders

Run: python3 dao_agent_demo.py
"""

from __future__ import annotations
import hashlib, random, uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict

from platform_schemas import (
    SupplierAgentCard, BuyerAgentCard, Contract, Milestone,
    MilestoneStatus, EngagementType, STANDARD_MODULES,
    TaxRecord, TaxRecordRole, CrossBorderContractBundle,
    SettlementEvent, PaymentRail,
)
from federated_registry_demo import (
    JurisdictionalAgent, NationalRegistry, TaxAuthority,
    Matchmaker, AgentNegotiator, FedNowRail, X402Rail,
    make_supplier, make_buyer, make_tender, make_contract, _h,
)


# ─────────────────────────────────────────────────────────────────────────────
# DAO STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CategoryBudget:
    name:           str
    monthly_limit:  float
    spent_mtd:      float  = 0.0
    naics_codes:    list   = field(default_factory=list)

    @property
    def remaining(self) -> float:
        return max(self.monthly_limit - self.spent_mtd, 0.0)

    @property
    def utilisation(self) -> float:
        return self.spent_mtd / self.monthly_limit if self.monthly_limit else 0.0


@dataclass
class GovernanceParams:
    """Spending authority tiers set by DAO governance."""
    autonomous_limit:   float = 10_000   # agent acts alone below this
    council_limit:      float = 50_000   # council vote required above this
    council_size:       int   = 5
    council_threshold:  int   = 3        # votes needed for approval
    token_quorum_pct:   float = 0.10     # 10% token holder participation needed
    vote_window_hours:  int   = 48
    max_vendor_share:   float = 0.30     # no single vendor >30% of total spend


@dataclass
class VendorRecord:
    """DAO's view of a supplier — built from registry attestations + own history."""
    did:             str
    name:            str
    contracts_count: int   = 0
    total_paid:      float = 0.0
    avg_score:       float = 1.0
    last_revision:   bool  = False   # did last delivery need revision?
    categories:      list  = field(default_factory=list)


@dataclass
class ProcurementDecision:
    task_title:      str
    category:        str
    amount:          float
    supplier_did:    str
    supplier_name:   str
    approval_path:   str    # "autonomous" | "council" | "token_vote"
    approved:        bool
    contract_id:     str    = ""
    notes:           str    = ""


@dataclass
class GovernanceVote:
    vote_id:      str  = field(default_factory=lambda: f"vote:{uuid.uuid4().hex[:8]}")
    proposal:     str  = ""
    amount:       float = 0.0
    tier:         str  = ""       # "council" | "token_vote"
    result:       str  = ""       # "approved" | "rejected" | "no_quorum"
    votes_for:    int  = 0
    votes_against:int  = 0
    quorum_met:   bool = False


# ─────────────────────────────────────────────────────────────────────────────
# DAO TREASURY
# ─────────────────────────────────────────────────────────────────────────────

class DAOTreasury:
    def __init__(self, total_usd: float, categories: list[CategoryBudget]):
        self.total_usd        = total_usd
        self.categories       = {c.name: c for c in categories}
        self.total_committed  = 0.0
        self.total_paid       = 0.0
        self.tx_log: list[dict] = []

    def can_spend(self, category: str, amount: float) -> tuple[bool, str]:
        if category not in self.categories:
            return False, f"Unknown category: {category}"
        cat = self.categories[category]
        if amount > cat.remaining:
            return False, f"Exceeds category budget (${cat.remaining:,.0f} remaining)"
        if self.total_committed + amount > self.total_usd:
            return False, "Exceeds total treasury"
        return True, "ok"

    def commit(self, category: str, amount: float, contract_id: str):
        self.categories[category].spent_mtd += amount
        self.total_committed += amount
        self.tx_log.append({
            "type": "commit", "category": category,
            "amount": amount, "contract_id": contract_id,
        })

    def pay(self, amount: float, contract_id: str):
        self.total_paid += amount
        self.tx_log.append({"type": "pay", "amount": amount, "contract_id": contract_id})

    def vendor_share(self, vendor_did: str, vendor_records: dict) -> float:
        vr = vendor_records.get(vendor_did)
        if not vr or self.total_committed == 0:
            return 0.0
        return vr.total_paid / self.total_committed


# ─────────────────────────────────────────────────────────────────────────────
# GOVERNANCE SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class GovernanceSimulator:
    """
    Simulates DAO governance votes.
    Council votes: semi-informed (members review brief); higher approval rate.
    Token votes: large population, noisy; lower approval rate, quorum risk.
    """

    def __init__(self, params: GovernanceParams, token_holders: int = 5_000):
        self.params        = params
        self.token_holders = token_holders

    def council_vote(self, proposal: str, amount: float) -> GovernanceVote:
        p = self.params
        # Council approval probability: base 80%, lower for larger amounts
        approval_prob = max(0.50, 0.90 - (amount / p.council_limit) * 0.25)
        votes_for     = sum(1 for _ in range(p.council_size) if random.random() < approval_prob)
        votes_against = p.council_size - votes_for
        approved      = votes_for >= p.council_threshold

        vote = GovernanceVote(
            proposal=proposal, amount=amount, tier="council",
            votes_for=votes_for, votes_against=votes_against,
            quorum_met=True,
            result="approved" if approved else "rejected",
        )
        return vote

    def token_vote(self, proposal: str, amount: float) -> GovernanceVote:
        p = self.params
        # Participation rate: base 12–18%, higher for larger/controversial proposals
        participation = random.uniform(0.08, 0.20)
        quorum_met    = participation >= p.token_quorum_pct
        if not quorum_met:
            return GovernanceVote(
                proposal=proposal, amount=amount, tier="token_vote",
                quorum_met=False, result="no_quorum",
            )
        votes_total    = int(self.token_holders * participation)
        approval_prob  = max(0.45, 0.75 - (amount / 500_000) * 0.20)
        votes_for      = int(votes_total * approval_prob * random.uniform(0.90, 1.10))
        votes_against  = votes_total - votes_for
        approved       = votes_for > votes_against

        return GovernanceVote(
            proposal=proposal, amount=amount, tier="token_vote",
            votes_for=votes_for, votes_against=votes_against,
            quorum_met=True,
            result="approved" if approved else "rejected",
        )


# ─────────────────────────────────────────────────────────────────────────────
# DAO PROCUREMENT AGENT
# ─────────────────────────────────────────────────────────────────────────────

class DAOProcurementAgent:
    """
    Autonomous agent managing procurement for a DAO.
    Operates within governance-set constraints; escalates when needed.
    Tracks vendor portfolio, manages concentration risk, reports to token holders.
    """

    def __init__(
        self,
        dao_name:    str,
        card:        JurisdictionalAgent,
        treasury:    DAOTreasury,
        governance:  GovernanceParams,
        gov_sim:     GovernanceSimulator,
        registry:    NationalRegistry,
        matchmakers: list[Matchmaker],
        negotiator:  AgentNegotiator,
        rail:        FedNowRail | X402Rail,
    ):
        self.dao_name    = dao_name
        self.card        = card
        self.treasury    = treasury
        self.governance  = governance
        self.gov_sim     = gov_sim
        self.registry    = registry
        self.matchmakers = matchmakers
        self.negotiator  = negotiator
        self.rail        = rail

        self.vendor_records:   dict[str, VendorRecord] = {}
        self.active_contracts: list[Contract]          = []
        self.decisions:        list[ProcurementDecision] = []
        self.votes:            list[GovernanceVote]    = []

    # ── Approval routing ─────────────────────────────────────────────────────

    def _route_approval(self, task: str, amount: float) -> tuple[str, bool, GovernanceVote | None]:
        g = self.governance
        if amount < g.autonomous_limit:
            return "autonomous", True, None
        elif amount < g.council_limit:
            vote = self.gov_sim.council_vote(task, amount)
            self.votes.append(vote)
            return "council", vote.result == "approved", vote
        else:
            vote = self.gov_sim.token_vote(task, amount)
            self.votes.append(vote)
            approved = vote.result == "approved"
            # If no quorum: try re-vote once (common in DAOs)
            if vote.result == "no_quorum":
                log(f"    No quorum ({vote.votes_for + vote.votes_against} voters). "
                    f"Scheduling re-vote...")
                vote2 = self.gov_sim.token_vote(task + " [re-vote]", amount)
                self.votes.append(vote2)
                approved = vote2.result == "approved"
                vote = vote2
            return "token_vote", approved, vote

    # ── Vendor concentration check ────────────────────────────────────────────

    def _check_concentration(self, supplier_did: str) -> tuple[bool, str]:
        share = self.treasury.vendor_share(supplier_did, self.vendor_records)
        if share >= self.governance.max_vendor_share:
            vr = self.vendor_records.get(supplier_did)
            name = vr.name if vr else supplier_did[:20]
            return False, (f"Vendor concentration limit: {name} already at "
                           f"{share:.0%} of total spend (limit {self.governance.max_vendor_share:.0%})")
        return True, "ok"

    # ── Core procurement flow ─────────────────────────────────────────────────

    def procure(
        self,
        task_title:  str,
        category:    str,
        budget:      float,
        naics:       list[str],
        duration:    int = 14,
        verbose:     bool = True,
    ) -> ProcurementDecision:

        def vlog(msg):
            if verbose:
                log(msg)

        # Budget check
        ok, reason = self.treasury.can_spend(category, budget)
        if not ok:
            vlog(f"  ✗ Budget check failed: {reason}")
            return ProcurementDecision(task_title, category, budget, "", "", "n/a", False, notes=reason)

        # Approval routing
        approval_path, approved, vote = self._route_approval(task_title, budget)
        vlog(f"  Approval path: {approval_path}", )
        if vote:
            vlog(f"    Vote result: {vote.result}  "
                 f"({vote.votes_for} for / {vote.votes_against} against)")
        if not approved:
            note = f"Governance rejected: {vote.result if vote else 'n/a'}"
            return ProcurementDecision(task_title, category, budget, "", "", approval_path, False, notes=note)

        # Find candidates across matchmakers
        tender = make_tender(self.card.did, task_title, naics, budget, duration)
        candidates = []
        for mm in self.matchmakers:
            candidates.extend(mm.find_matches(tender, [self.registry], top_n=5))
        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = candidates[:5]  # de-dup top 5 overall

        if not candidates:
            return ProcurementDecision(task_title, category, budget, "", "", approval_path, False,
                                       notes="No candidates found")

        # Select vendor: top score, but check concentration
        chosen_agent, score = None, 0.0
        for agent, s in candidates:
            ok, reason = self._check_concentration(agent.did)
            if ok:
                chosen_agent, score = agent, s
                break
        if not chosen_agent:
            vlog("  All top candidates at concentration limit — selecting next available")
            chosen_agent, score = candidates[-1]

        # Negotiate
        floor  = budget * 0.78
        result = self.negotiator.negotiate(tender, chosen_agent, self.card, supplier_floor=floor)
        if not result.success:
            return ProcurementDecision(task_title, category, budget, chosen_agent.did,
                                       chosen_agent.display_name, approval_path, False,
                                       notes="Negotiation failed")

        # Execute contract
        contract = make_contract(tender, result)
        self.active_contracts.append(contract)

        # Report to registry
        mm = self.matchmakers[0]
        bundle = mm.build_bundle(contract, chosen_agent.home_jurisdiction,
                                 self.card.home_jurisdiction)
        mm.report_contract(bundle, chosen_agent.did, self.registry,
                           self.card.did, self.registry)

        # Treasury commit
        self.treasury.commit(category, result.final_price, contract.id)

        # Update vendor record
        vr = self.vendor_records.setdefault(
            chosen_agent.did,
            VendorRecord(did=chosen_agent.did, name=chosen_agent.display_name,
                         categories=[category])
        )
        vr.contracts_count += 1

        decision = ProcurementDecision(
            task_title=task_title, category=category, amount=result.final_price,
            supplier_did=chosen_agent.did, supplier_name=chosen_agent.display_name,
            approval_path=approval_path, approved=True, contract_id=contract.id,
        )
        self.decisions.append(decision)
        return decision

    def complete_contract(self, contract_id: str, score: float):
        """Simulate contract completion — update vendor record, write attestation."""
        decision = next((d for d in self.decisions if d.contract_id == contract_id), None)
        if not decision:
            return
        vr = self.vendor_records.get(decision.supplier_did)
        if vr:
            vr.total_paid += decision.amount
            vr.avg_score   = (vr.avg_score * (vr.contracts_count - 1) + score) / vr.contracts_count
        self.treasury.pay(decision.amount, contract_id)
        att = _h(f"dao-perf:{decision.supplier_did}:{contract_id}:{score:.2f}")
        self.registry.add_attestation(decision.supplier_did, att)

    # ── Reporting ─────────────────────────────────────────────────────────────

    def spending_report(self):
        print(f"\n  {'─'*60}")
        print(f"  {self.dao_name} — Monthly Procurement Report")
        print(f"  {'─'*60}")
        print(f"  Treasury committed: ${self.treasury.total_committed:>10,.0f}")
        print(f"  Treasury paid:      ${self.treasury.total_paid:>10,.0f}")
        print(f"  Active contracts:   {len(self.active_contracts)}")
        print(f"  Total decisions:    {len(self.decisions)}")
        approved = [d for d in self.decisions if d.approved]
        rejected = [d for d in self.decisions if not d.approved]
        print(f"  Approved:           {len(approved)}  |  Rejected: {len(rejected)}")

        print(f"\n  Category spend:")
        for name, cat in self.treasury.categories.items():
            bar_len = int(cat.utilisation * 20)
            bar     = "█" * bar_len + "░" * (20 - bar_len)
            print(f"    {name:<18} [{bar}] {cat.utilisation:>4.0%}  "
                  f"${cat.spent_mtd:>8,.0f} / ${cat.monthly_limit:>8,.0f}")

        print(f"\n  Vendor portfolio ({len(self.vendor_records)} vendors):")
        sorted_vendors = sorted(self.vendor_records.values(),
                                key=lambda v: v.total_paid, reverse=True)
        total_paid = self.treasury.total_paid or 1
        for vr in sorted_vendors[:8]:
            share = vr.total_paid / total_paid if total_paid else 0
            flag  = " ⚠ near limit" if share > self.governance.max_vendor_share * 0.85 else ""
            print(f"    {vr.name:<25} contracts={vr.contracts_count}  "
                  f"paid=${vr.total_paid:>7,.0f}  share={share:>4.0%}  "
                  f"score={vr.avg_score:.2f}{flag}")

        print(f"\n  Governance votes this period: {len(self.votes)}")
        for v in self.votes:
            status = {"approved": "✓", "rejected": "✗", "no_quorum": "?"}.get(v.result, "?")
            print(f"    {status} [{v.tier:<12}] ${v.amount:>8,.0f}  "
                  f"for={v.votes_for} against={v.votes_against}  → {v.result}")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def log(msg: str):
    print(msg)

def section(title: str):
    print("\n" + "─" * 68)
    print(f"  {title}")
    print("─" * 68)

def step(title: str):
    print(f"\n  ── {title}")


def build_world():
    irs    = TaxAuthority("US-IRS")
    us_reg = NationalRegistry("US", "US Yeoman Agent Registry", irs)

    # Supplier pool — diverse capabilities
    suppliers = [
        ("Maria Chen",       ["541511", "541512"], ["python", "ml", "data-analysis"],   6),
        ("Dev Patel",        ["541511"],            ["rust", "api-design", "backend"],   4),
        ("Ana Souza",        ["519130", "541511"],  ["nlp", "python", "rag"],            3),
        ("Sam Rivera",       ["561720"],            ["commercial-cleaning", "robot-ops"],4),
        ("Priya Nair",       ["541511", "541519"],  ["typescript", "react", "ui"],       5),
        ("Leo Tanaka",       ["541611"],            ["strategy", "market-research"],     3),
        ("Yuki Sato",        ["541511"],            ["go", "devops", "k8s"],             4),
        ("Carlos Mendez",    ["541430"],            ["graphic-design", "branding"],      3),
        ("Aisha Johnson",    ["541611", "519130"],  ["content", "copywriting"],          4),
        ("Tom Walsh",        ["541511", "541512"],  ["python", "data-engineering"],      5),
    ]
    for name, naics, caps, n in suppliers:
        us_reg.register_agent(make_supplier(name, naics, caps, n_creds=n))

    alpha = Matchmaker("mm-alpha", "AlphaMatch", algorithm="score")
    beta  = Matchmaker("mm-beta",  "BetaMatch",  algorithm="reputation")
    alpha.register_with(us_reg)
    beta.register_with(us_reg)

    return us_reg, irs, [alpha, beta], AgentNegotiator(), FedNowRail()


def build_dao(us_reg, matchmakers, negotiator, rail) -> DAOProcurementAgent:
    dao_card = us_reg.register_agent(
        make_buyer("Sustainability Commons DAO", entity_type="cooperative"))

    treasury = DAOTreasury(
        total_usd=500_000,
        categories=[
            CategoryBudget("engineering",   200_000, naics_codes=["541511", "541512", "541519"]),
            CategoryBudget("data_and_ai",   100_000, naics_codes=["519130", "541511"]),
            CategoryBudget("operations",     80_000, naics_codes=["541611", "561720"]),
            CategoryBudget("design",         60_000, naics_codes=["541430"]),
            CategoryBudget("content",        60_000, naics_codes=["541611", "519130"]),
        ]
    )
    governance = GovernanceParams(
        autonomous_limit=10_000,
        council_limit=50_000,
        council_size=5,
        council_threshold=3,
        token_quorum_pct=0.10,
        max_vendor_share=0.30,
    )
    gov_sim = GovernanceSimulator(governance, token_holders=8_000)

    return DAOProcurementAgent(
        dao_name="Sustainability Commons DAO",
        card=dao_card,
        treasury=treasury,
        governance=governance,
        gov_sim=gov_sim,
        registry=us_reg,
        matchmakers=matchmakers,
        negotiator=negotiator,
        rail=rail,
    )


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 1 — Autonomous procurement (routine, small)
# ─────────────────────────────────────────────────────────────────────────────

def demo_autonomous(dao: DAOProcurementAgent):
    section("DEMO 1 — Autonomous procurement  (< $10k, no vote needed)")
    log("  Agent acts immediately within autonomous spending limit.\n")

    tasks = [
        ("Carbon data pipeline v2",   "data_and_ai",  8_500, ["519130", "541511"], 7),
        ("Landing page redesign",     "design",        6_000, ["541430"],           5),
        ("Blog content — Q1 series",  "content",       4_500, ["541611", "519130"], 3),
    ]
    for title, cat, budget, naics, dur in tasks:
        log(f"  Task: '{title}'  category={cat}  budget=${budget:,}")
        d = dao.procure(title, cat, budget, naics, dur, verbose=True)
        icon = "✓" if d.approved else "✗"
        log(f"  {icon} {d.approval_path}  →  {d.supplier_name}  ${d.amount:,.0f}\n")
        if d.approved:
            dao.complete_contract(d.contract_id, score=random.uniform(0.85, 1.0))


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 2 — Council escalation ($10k–$50k)
# ─────────────────────────────────────────────────────────────────────────────

def demo_council(dao: DAOProcurementAgent):
    section("DEMO 2 — Council escalation  ($10k–$50k, 3 of 5 council vote)")
    log("  Agent pauses, submits proposal to council, resumes if approved.\n")

    tasks = [
        ("Smart contract audit — v3 protocol",  "engineering", 28_000, ["541511"], 21),
        ("Market research: carbon credit buyers","operations",  15_000, ["541611"], 14),
        ("ML model fine-tuning — emissions",    "data_and_ai", 42_000, ["541511", "519130"], 30),
    ]
    for title, cat, budget, naics, dur in tasks:
        log(f"  Task: '{title}'  budget=${budget:,}")
        d = dao.procure(title, cat, budget, naics, dur, verbose=True)
        icon = "✓" if d.approved else "✗"
        log(f"  {icon} {d.approval_path}  →  "
            f"{'APPROVED → ' + d.supplier_name + ' $' + f'{d.amount:,.0f}' if d.approved else 'REJECTED'}\n")
        if d.approved:
            dao.complete_contract(d.contract_id, score=random.uniform(0.80, 0.95))


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 3 — Token holder vote (> $50k)
# ─────────────────────────────────────────────────────────────────────────────

def demo_token_vote(dao: DAOProcurementAgent):
    section("DEMO 3 — Token holder vote  (> $50k, 48h window, 10% quorum)")
    log("  Agent submits full proposal to token holders. Quorum risk is real.\n")

    tasks = [
        ("Core protocol engineering — Q2",  "engineering", 120_000, ["541511", "541512"], 60),
        ("Data infrastructure rebuild",     "data_and_ai",  75_000, ["519130", "541511"], 45),
    ]
    for title, cat, budget, naics, dur in tasks:
        log(f"  Task: '{title}'  budget=${budget:,}")
        d = dao.procure(title, cat, budget, naics, dur, verbose=True)
        icon = "✓" if d.approved else "✗"
        result_str = (f"APPROVED → {d.supplier_name} ${d.amount:,.0f}"
                      if d.approved else f"FAILED ({d.notes})")
        log(f"  {icon} {d.approval_path}  →  {result_str}\n")
        if d.approved:
            dao.complete_contract(d.contract_id, score=random.uniform(0.88, 0.98))


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 4 — Full 30-day procurement cycle
# ─────────────────────────────────────────────────────────────────────────────

MONTHLY_TASKS = [
    # (title, category, budget, naics, duration_days)
    ("API gateway maintenance",         "engineering", 4_200,  ["541511"],           7),
    ("UX audit — mobile app",           "design",      7_800,  ["541430"],           10),
    ("Newsletter content — April",      "content",     2_400,  ["541611"],           3),
    ("Emissions data ETL pipeline",     "data_and_ai", 9_500,  ["519130", "541511"], 14),
    ("Ops playbook documentation",      "operations",  3_800,  ["541611"],           5),
    ("Token analytics dashboard",       "engineering", 18_500, ["541511", "541519"], 21),
    ("Brand identity refresh",          "design",      22_000, ["541430"],           28),
    ("AI model evaluation framework",   "data_and_ai", 31_000, ["519130", "541511"], 21),
    ("Community growth strategy",       "operations",  14_500, ["541611"],           14),
    ("Smart contract security review",  "engineering", 45_000, ["541511"],           30),
    ("Podcast production — 8 episodes", "content",     11_000, ["541611", "519130"], 30),
    ("Infrastructure cost optimisation","engineering",  8_200, ["541511"],           10),
    ("Carbon methodology research",     "data_and_ai", 27_500, ["519130"],           21),
    ("Governance tooling v2",           "engineering", 68_000, ["541511", "541512"], 45),
    ("Social media management — Q2",    "content",      5_600, ["541611"],           30),
]

def demo_30day_cycle(dao: DAOProcurementAgent):
    section("DEMO 4 — 30-day procurement cycle (15 tasks, full portfolio)")
    log("  Simulates a realistic monthly procurement cycle.\n")

    approved_count  = 0
    rejected_count  = 0
    autonomous_n    = 0
    council_n       = 0
    token_vote_n    = 0

    for title, cat, budget, naics, dur in MONTHLY_TASKS:
        d = dao.procure(title, cat, budget, naics, dur, verbose=False)
        icon = "✓" if d.approved else "✗"
        path_tag = {"autonomous": "AUTO", "council": "CNCL",
                    "token_vote": "VOTE", "n/a": "    "}.get(d.approval_path, "    ")
        vendor   = d.supplier_name[:20] if d.approved else f"— {d.notes[:30]}"
        log(f"  {icon} [{path_tag}] ${budget:>7,}  {title[:40]:<40}  → {vendor}")

        if d.approved:
            approved_count += 1
            dao.complete_contract(d.contract_id, score=random.uniform(0.78, 0.98))
            if d.approval_path == "autonomous":  autonomous_n += 1
            elif d.approval_path == "council":   council_n    += 1
            else:                                token_vote_n  += 1
        else:
            rejected_count += 1

    log(f"\n  Summary: {approved_count} approved  {rejected_count} rejected")
    log(f"  By path: autonomous={autonomous_n}  council={council_n}  token_vote={token_vote_n}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    random.seed(99)

    print("\n" + "=" * 68)
    print("  DAO PROCUREMENT AGENT — COLLECTIVE AI BUYING AT SCALE")
    print("=" * 68)

    us_reg, irs, matchmakers, neg, rail = build_world()
    dao = build_dao(us_reg, matchmakers, neg, rail)

    log(f"\n  DAO:       {dao.dao_name}")
    log(f"  Treasury:  ${dao.treasury.total_usd:,.0f}")
    log(f"  Suppliers: {len([a for a in us_reg.agents.values() if a.is_supplier])} registered in registry")
    log(f"  Governance: autonomous < ${dao.governance.autonomous_limit:,.0f}  |  "
        f"council < ${dao.governance.council_limit:,.0f}  |  "
        f"token vote above")

    demo_autonomous(dao)
    demo_council(dao)
    demo_token_vote(dao)
    demo_30day_cycle(dao)

    dao.spending_report()

    print("\n" + "─" * 68)
    print("  REGISTRY & TAX STATE")
    print("─" * 68)
    irs.print_summary()
    print(f"  {us_reg.summary()}")
    print("\n" + "=" * 68 + "\n")


if __name__ == "__main__":
    main()
