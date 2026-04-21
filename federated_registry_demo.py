"""
Federated Agent Commerce Registry — Prototype
=============================================
Demonstrates the L0–L5 layered architecture for AI agent commerce infrastructure.

  L0  International Standard  — shared schemas (platform_schemas.py + extensions)
  L1  National Registry       — per-country identity, credentials, tax reporting
  L2  Matchmaker              — private competitive operator, reports to L1
  L3  Agent Negotiation       — A2A proposal / counter-proposal loop
  L4  Settlement              — FedNow (domestic) or x402 stablecoin (cross-border)
  L5  Tax Reporting           — automatic at contract execution, forwarded to tax authority

Five demos:
  1. Domestic US flow          — single registry, single matchmaker, baseline
  2. Cross-border flow         — US yeoman × EU DAO, dual registry reporting
  3. Competing matchmakers     — same tender, two matchmakers, winner takes contract
  4. Reputation portability    — yeoman switches matchmaker; reputation follows from registry
  5. Machine-speed batch       — 20 micro-contracts in one loop, all reported

Run: python3 federated_registry_demo.py
"""

from __future__ import annotations
import hashlib, random, uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from platform_schemas import (
    SupplierAgentCard, BuyerAgentCard, Tender, TenderRequirements,
    Bid, Contract, Milestone, MilestoneStatus, EngagementType, TenderStatus,
    ContractStatus, STANDARD_MODULES,
    TaxRecord, TaxRecordRole, AgentNegotiationMessage, NegotiationMessageType,
    MatchmakerLicense, CrossBorderContractBundle, SettlementEvent, PaymentRail,
)


# ─────────────────────────────────────────────────────────────────────────────
# L0 EXTENSION: Jurisdiction-aware agent card
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class JurisdictionalAgent:
    """
    Wraps any agent card with jurisdiction metadata added by L1 at registration.
    The sub-DID format allows an operator to run multiple specialised agents:
      operator DID  →  did:nat:us:maria-chen
      agent sub-DID →  did:nat:us:maria-chen/agent:data-analyst-v2
    """
    base_card: SupplierAgentCard | BuyerAgentCard
    home_jurisdiction: str        # ISO 3166-1: "US", "DE", "UK"
    registry_did: str             # DID of the L1 registry that issued identity
    registry_attestation_hash: str
    agent_did: str                # sub-DID

    @property
    def did(self) -> str:
        return self.base_card.did

    @property
    def display_name(self) -> str:
        return self.base_card.display_name

    @property
    def naics_codes(self) -> list[str]:
        return getattr(self.base_card, "naics_codes", [])

    @property
    def credential_hashes(self) -> list[str]:
        return getattr(self.base_card, "credential_hashes", [])

    @property
    def is_supplier(self) -> bool:
        return isinstance(self.base_card, SupplierAgentCard)


# ─────────────────────────────────────────────────────────────────────────────
# L1: NATIONAL REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

class NationalRegistry:
    """
    Government-chartered nonprofit. One per jurisdiction. Analogous to ccTLD registry.

    Responsibilities
    ─────────────────
    • Agent identity — DID issuance and verification
    • Reputation storage — attestation hashes only (not credential content)
    • Contract report intake from licensed matchmakers
    • Tax record forwarding to TaxAuthority
    • Matchmaker licensing (like ICANN accrediting registrars)

    What it does NOT do
    ─────────────────────
    • Run matching algorithms
    • Hold credential content (privacy: hashes only)
    • Set contract terms
    """

    def __init__(self, country_code: str, name: str, tax_authority: TaxAuthority):
        self.country_code = country_code
        self.registry_did = f"did:nat:{country_code.lower()}:registry"
        self.name = name
        self.tax_authority = tax_authority

        self.agents:               dict[str, JurisdictionalAgent] = {}
        self.reputation_db:        dict[str, list[str]]           = {}  # did → attestation hashes
        self.licensed_matchmakers: dict[str, MatchmakerLicense]   = {}
        self._seen_bundles:        set[str]                       = set()  # deduplication
        self.contracts_reported:   int                            = 0

    # ── Registration ──────────────────────────────────────────────────────────

    def register_agent(self, card: SupplierAgentCard | BuyerAgentCard) -> JurisdictionalAgent:
        slug = card.display_name.lower().replace(" ", "-")
        agent_did = f"{card.did}/agent:{slug}"
        att_body  = f"{self.registry_did}:{card.did}:{datetime.now(timezone.utc).isoformat()}"
        att_hash  = hashlib.sha256(att_body.encode()).hexdigest()[:16]

        ja = JurisdictionalAgent(
            base_card=card,
            home_jurisdiction=self.country_code,
            registry_did=self.registry_did,
            registry_attestation_hash=att_hash,
            agent_did=agent_did,
        )
        self.agents[card.did] = ja
        self.reputation_db[card.did] = list(getattr(card, "credential_hashes", []))
        return ja

    def license_matchmaker(self, matchmaker_id: str, name: str) -> MatchmakerLicense:
        lic = MatchmakerLicense(
            matchmaker_id=matchmaker_id,
            matchmaker_name=name,
            licensed_by=[self.registry_did],
        )
        self.licensed_matchmakers[matchmaker_id] = lic
        return lic

    # ── Reputation (portable: queried by any matchmaker, not owned by any) ───

    def get_reputation(self, did: str) -> list[str]:
        return self.reputation_db.get(did, [])

    def add_attestation(self, did: str, attestation_hash: str):
        self.reputation_db.setdefault(did, []).append(attestation_hash)

    def get_agent(self, did: str) -> Optional[JurisdictionalAgent]:
        return self.agents.get(did)

    # ── Contract reporting ────────────────────────────────────────────────────

    def receive_contract_report(
        self,
        bundle: CrossBorderContractBundle,
        party_role: TaxRecordRole,
        party_did: str,
    ) -> Optional[TaxRecord]:
        """
        Called by matchmaker after contract execution.
        Deduplicates, verifies matchmaker license, creates tax record.
        """
        dedup_key = f"{bundle.bundle_id}:{self.country_code}:{party_role.value}"
        if dedup_key in self._seen_bundles:
            return None
        self._seen_bundles.add(dedup_key)

        if bundle.executed_by_matchmaker not in self.licensed_matchmakers:
            raise PermissionError(
                f"Matchmaker '{bundle.executed_by_matchmaker}' is not licensed in {self.country_code}"
            )

        agent = self.agents.get(party_did)
        tax_id_hash = getattr(agent.base_card, "tax_id_hash", "unknown") if agent else "unknown"

        record = TaxRecord(
            jurisdiction=self.tax_authority.jurisdiction,
            contract_bundle_id=bundle.bundle_id,
            party_role=party_role,
            party_tax_id_hash=tax_id_hash,
            contract_value_usd=bundle.contract.total_value_usd,
            currency="USD",
            reporting_matchmaker=bundle.executed_by_matchmaker,
        )
        self.tax_authority.receive(record)
        self.contracts_reported += 1
        return record

    def summary(self) -> str:
        return (
            f"Registry [{self.country_code}] '{self.name}'  "
            f"agents={len(self.agents)}  "
            f"matchmakers={len(self.licensed_matchmakers)}  "
            f"contracts_reported={self.contracts_reported}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# L1 COMPANION: TAX AUTHORITY
# ─────────────────────────────────────────────────────────────────────────────

class TaxAuthority:
    """Append-only ledger. Receives L0-format TaxRecords from NationalRegistry."""

    def __init__(self, jurisdiction: str):
        self.jurisdiction = jurisdiction
        self.ledger: list[TaxRecord] = []

    def receive(self, record: TaxRecord):
        self.ledger.append(record)

    def total_declared(self) -> float:
        return sum(r.contract_value_usd for r in self.ledger)

    def print_summary(self):
        supplier = [r for r in self.ledger if r.party_role == TaxRecordRole.SUPPLIER]
        buyer    = [r for r in self.ledger if r.party_role == TaxRecordRole.BUYER]
        print(f"\n  [{self.jurisdiction}]  records={len(self.ledger)}  "
              f"(supplier={len(supplier)}, buyer={len(buyer)})  "
              f"total_declared=${self.total_declared():,.0f}")
        for r in self.ledger[:4]:
            role = r.party_role.value
            bid  = r.contract_bundle_id[:18]
            print(f"    {role:>8}  {bid}...  ${r.contract_value_usd:>8,.0f}  "
                  f"via {r.reporting_matchmaker}")
        if len(self.ledger) > 4:
            print(f"    ... and {len(self.ledger) - 4} more")


# ─────────────────────────────────────────────────────────────────────────────
# L2: MATCHMAKER
# ─────────────────────────────────────────────────────────────────────────────

class Matchmaker:
    """
    Private competitive operator. Licensed by ≥1 NationalRegistry.
    Competitive differentiator: matching algorithm.
    Mandatory obligations: report all contracts, allow reputation portability.

    What it does NOT own:
    • Agent reputation data (lives in NationalRegistry, queried via API)
    • Agent credentials (hashes in registry; content in agent wallet)
    • Contract terms (governed by L0 standard modules)
    """

    def __init__(self, matchmaker_id: str, name: str, algorithm: str = "score"):
        self.matchmaker_id    = matchmaker_id
        self.name             = name
        self.algorithm        = algorithm   # "score" | "reputation" | "price"
        self.licenses:  dict[str, MatchmakerLicense] = {}
        self.contracts_executed = 0

    def register_with(self, registry: NationalRegistry) -> MatchmakerLicense:
        lic = registry.license_matchmaker(self.matchmaker_id, self.name)
        self.licenses[registry.country_code] = lic
        return lic

    def is_licensed_in(self, country_code: str) -> bool:
        return country_code in self.licenses

    # ── L2 core function: matching ────────────────────────────────────────────

    def find_matches(
        self,
        tender: Tender,
        registries: list[NationalRegistry],
        top_n: int = 3,
    ) -> list[tuple[JurisdictionalAgent, float]]:
        """
        Query multiple registries. Returns scored (agent, score) pairs.
        Reputation queried from registry — matchmaker has no local copy.
        """
        candidates = []
        req = tender.requirements

        for registry in registries:
            for did, agent in registry.agents.items():
                if not agent.is_supplier:
                    continue

                naics_match = (
                    not req or not req.required_naics
                    or any(n in agent.naics_codes for n in req.required_naics)
                )
                rep_count = len(registry.get_reputation(did))

                if self.algorithm == "score":
                    score = (0.5 * float(naics_match)
                             + 0.3 * min(rep_count / 10.0, 1.0)
                             + 0.2 * random.uniform(0.6, 1.0))
                elif self.algorithm == "reputation":
                    score = min(rep_count / 10.0, 1.0) + 0.1 * float(naics_match)
                else:  # price-first
                    score = random.uniform(0.4, 0.9) * float(naics_match or True)

                if naics_match:
                    candidates.append((agent, round(score, 3)))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_n]

    # ── L2 → L1: mandatory contract reporting ────────────────────────────────

    def build_bundle(
        self,
        contract: Contract,
        supplier_jurisdiction: str,
        buyer_jurisdiction: str,
    ) -> CrossBorderContractBundle:
        bundle = CrossBorderContractBundle(
            contract=contract,
            supplier_jurisdiction=supplier_jurisdiction,
            buyer_jurisdiction=buyer_jurisdiction,
            executed_by_matchmaker=self.matchmaker_id,
            cross_border=(supplier_jurisdiction != buyer_jurisdiction),
        )
        self.contracts_executed += 1
        return bundle

    def report_contract(
        self,
        bundle: CrossBorderContractBundle,
        supplier_did: str, supplier_registry: NationalRegistry,
        buyer_did: str,    buyer_registry: NationalRegistry,
    ) -> list[TaxRecord]:
        """Mandatory. Called immediately after contract execution."""
        records = []
        r = supplier_registry.receive_contract_report(bundle, TaxRecordRole.SUPPLIER, supplier_did)
        if r:
            records.append(r)
        r = buyer_registry.receive_contract_report(bundle, TaxRecordRole.BUYER, buyer_did)
        if r:
            records.append(r)
        return records


# ─────────────────────────────────────────────────────────────────────────────
# L3: AGENT NEGOTIATION (A2A proposal / counter / accept)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NegotiationResult:
    success:            bool
    final_price:        float
    final_timeline:     int
    rounds:             int
    supplier_did:       str
    buyer_did:          str
    session_id:         str
    log:                list[str] = field(default_factory=list)


class AgentNegotiator:
    """
    Simulates A2A machine-speed negotiation.
    Neither buyer nor seller agent waits for a human between rounds.
    Max 3 rounds; both sides have simple strategy parameters.
    """
    MAX_ROUNDS = 3

    def negotiate(
        self,
        tender: Tender,
        supplier: JurisdictionalAgent,
        buyer: JurisdictionalAgent,
        supplier_floor: float,
    ) -> NegotiationResult:
        session_id    = f"neg:{uuid.uuid4().hex[:10]}"
        budget_cap    = tender.budget_max_usd or supplier_floor * 1.5
        ask           = supplier_floor * 1.15   # supplier opens 15% above floor
        timeline      = tender.estimated_duration_days
        log           = []

        for rnd in range(1, self.MAX_ROUNDS + 1):
            log.append(f"  Round {rnd}: supplier asks ${ask:,.0f}")

            if ask <= budget_cap:
                log.append(f"  Round {rnd}: buyer ACCEPTS ${ask:,.0f}")
                return NegotiationResult(True, ask, timeline, rnd,
                                         supplier.did, buyer.did, session_id, log)

            if ask <= budget_cap * 1.25 and rnd < self.MAX_ROUNDS:
                counter = (ask + budget_cap) / 2
                log.append(f"  Round {rnd}: buyer counters ${counter:,.0f}")
                if counter >= supplier_floor:
                    ask = counter       # supplier accepts counter, re-proposes
                    log.append(f"  Round {rnd}: supplier accepts counter")
                    return NegotiationResult(True, ask, timeline, rnd,
                                             supplier.did, buyer.did, session_id, log)
                else:
                    log.append(f"  Round {rnd}: counter below floor — supplier walks")
                    break
            else:
                log.append(f"  Round {rnd}: buyer REJECTS (over budget)")
                break

        return NegotiationResult(False, 0.0, 0, rnd,
                                 supplier.did, buyer.did, session_id, log)


# ─────────────────────────────────────────────────────────────────────────────
# L4: SETTLEMENT RAILS
# ─────────────────────────────────────────────────────────────────────────────

class FedNowRail:
    """US domestic. <1 second. USD only."""
    def settle(self, bundle: CrossBorderContractBundle, milestone: Milestone) -> SettlementEvent:
        return SettlementEvent(
            contract_bundle_id=bundle.bundle_id,
            milestone_id=milestone.id,
            amount=milestone.amount_usd,
            currency="USD",
            rail=PaymentRail.FEDNOW,
            status="released",
        )

class X402Rail:
    """Cross-border. HTTP-native USDC. <500ms."""
    def settle(self, bundle: CrossBorderContractBundle, milestone: Milestone) -> SettlementEvent:
        return SettlementEvent(
            contract_bundle_id=bundle.bundle_id,
            milestone_id=milestone.id,
            amount=milestone.amount_usd,
            currency="USDC",
            rail=PaymentRail.X402,
            status="released",
        )


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _h(s: str, n: int = 16) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:n]

def make_supplier(name: str, naics: list[str], caps: list[str], n_creds: int = 3) -> SupplierAgentCard:
    slug = name.lower().replace(" ", "-")
    return SupplierAgentCard(
        did=f"did:nat:agent:{slug}",
        display_name=name,
        entity_type="sole_operator",
        tax_id_hash=_h(f"tax:{slug}"),
        capabilities=caps,
        naics_codes=naics,
        credential_hashes=[_h(f"cred:{slug}:{i}") for i in range(n_creds)],
        service_endpoint=f"https://agents.yeomen.net/{slug}",
        auth_scheme="oauth2",
        set_aside_eligibility=[],
    )

def make_buyer(name: str, entity_type: str = "private_company") -> BuyerAgentCard:
    slug = name.lower().replace(" ", "-")
    return BuyerAgentCard(
        did=f"did:nat:buyer:{slug}",
        display_name=name,
        entity_type=entity_type,
        tax_id_hash=_h(f"tax:{slug}"),
        service_endpoint=f"https://buyers.yeomen.net/{slug}",
        auth_scheme="oauth2",
        set_aside_preferences=[],
    )

def make_tender(buyer_did: str, title: str, naics: list[str],
                budget: float, duration: int) -> Tender:
    return Tender(
        buyer_did=buyer_did,
        title=title,
        description_plain=f"Automated tender: {title}",
        requirements=TenderRequirements(
            required_naics=naics,
            required_credentials=[],
            min_past_performance_count=0,
            set_aside=None,
            geographic_constraint=None,
        ),
        engagement_type=EngagementType.FIXED_PRICE,
        budget_max_usd=budget,
        estimated_duration_days=duration,
    )

def make_contract(tender: Tender, neg: NegotiationResult) -> Contract:
    ms = Milestone(
        description="Full delivery",
        amount_usd=neg.final_price,
        status=MilestoneStatus.PENDING,
    )
    c = Contract(
        tender_id=tender.id,
        buyer_did=neg.buyer_did,
        supplier_did=neg.supplier_did,
        total_value_usd=neg.final_price,
        milestones=[ms],
        modules=[STANDARD_MODULES["fixed_price_engagement"],
                 STANDARD_MODULES["ai_use_standard"]],
    )
    c.execute(neg.buyer_did, neg.supplier_did)
    return c

def sep(title: str = ""):
    print("\n" + "─" * 70)
    if title:
        print(f"  {title}")
        print("─" * 70)


# ─────────────────────────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────────────────────────

def setup_world():
    """Instantiate the full federated stack."""

    # L1 Tax Authorities
    irs  = TaxAuthority("US-IRS")
    eu   = TaxAuthority("EU-VAT:MULTI")
    hmrc = TaxAuthority("UK-HMRC")

    # L1 National Registries
    us_reg = NationalRegistry("US", "US Yeoman Agent Registry", irs)
    eu_reg = NationalRegistry("EU", "EU Agent Commerce Registry", eu)
    uk_reg = NationalRegistry("UK", "UK Agent Registry", hmrc)

    # L2 Matchmakers — competing private operators
    alpha = Matchmaker("mm-alpha", "AlphaMatch", algorithm="score")
    beta  = Matchmaker("mm-beta",  "BetaMatch",  algorithm="reputation")
    cross = Matchmaker("mm-cross", "CrossBorder", algorithm="score")

    # License matchmakers with registries
    alpha.register_with(us_reg)
    beta.register_with(us_reg)
    cross.register_with(us_reg)
    cross.register_with(eu_reg)
    cross.register_with(uk_reg)

    # L3 Negotiator and L4 Rails
    neg      = AgentNegotiator()
    fednow   = FedNowRail()
    x402     = X402Rail()

    return {
        "registries": {"US": us_reg, "EU": eu_reg, "UK": uk_reg},
        "tax":        {"US": irs, "EU": eu, "UK": hmrc},
        "matchmakers": {"alpha": alpha, "beta": beta, "cross": cross},
        "negotiator": neg,
        "rails":      {"fednow": fednow, "x402": x402},
    }


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 1 — Domestic US
# ─────────────────────────────────────────────────────────────────────────────

def demo_domestic_us(world: dict):
    sep("DEMO 1 — Domestic US flow")
    print("  US yeoman × US company × AlphaMatch (licensed US only)\n")

    us_reg = world["registries"]["US"]
    alpha  = world["matchmakers"]["alpha"]
    neg    = world["negotiator"]
    fednow = world["rails"]["fednow"]

    # Agents
    maria  = us_reg.register_agent(
        make_supplier("Maria Chen", ["541511", "541512"], ["python", "llm", "data-analysis"], n_creds=5))
    acme   = us_reg.register_agent(
        make_buyer("Acme Corp"))

    tender = make_tender(acme.did, "Data pipeline build", ["541511"], 18_000, 30)
    print(f"  Tender: '{tender.title}'  budget=${tender.budget_max_usd:,}")

    # L2 matching
    matches = alpha.find_matches(tender, [us_reg])
    print(f"  AlphaMatch found {len(matches)} candidate(s)")
    top_supplier, score = matches[0]
    print(f"  Top match: {top_supplier.display_name}  score={score}")

    # L3 negotiation
    result = neg.negotiate(tender, top_supplier, acme, supplier_floor=15_000)
    for line in result.log:
        print(f"  {line}")
    print(f"  Negotiation: {'SUCCESS' if result.success else 'FAILED'}  "
          f"price=${result.final_price:,.0f}  rounds={result.rounds}")

    if not result.success:
        return

    # Execute contract + bundle
    contract = make_contract(tender, result)
    bundle   = alpha.build_bundle(contract, "US", "US")

    # L4 settlement
    settlement = fednow.settle(bundle, contract.milestones[0])
    print(f"  Settlement: {settlement.rail.value.upper()}  "
          f"${settlement.amount:,.0f}  status={settlement.status}")

    # L2 → L1 mandatory reporting
    records = alpha.report_contract(bundle, maria.did, us_reg, acme.did, us_reg)
    print(f"  Tax records filed: {len(records)}")
    for r in records:
        print(f"    [{r.jurisdiction}] {r.party_role.value:>8}  ${r.contract_value_usd:,.0f}")

    print(f"\n  {us_reg.summary()}")


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 2 — Cross-border: US yeoman × EU DAO
# ─────────────────────────────────────────────────────────────────────────────

def demo_cross_border(world: dict):
    sep("DEMO 2 — Cross-border: US yeoman × EU DAO")
    print("  CrossBorder matchmaker licensed in both US + EU registries\n")

    us_reg = world["registries"]["US"]
    eu_reg = world["registries"]["EU"]
    cross  = world["matchmakers"]["cross"]
    neg    = world["negotiator"]
    x402   = world["rails"]["x402"]

    # US yeoman already registered in demo 1; add a new one here
    dev = us_reg.register_agent(
        make_supplier("Dev Patel", ["541511", "519130"], ["rust", "distributed-systems"], n_creds=4))

    # EU DAO — registered in EU registry
    dao = eu_reg.register_agent(
        make_buyer("Sustainability Commons DAO", entity_type="cooperative"))

    tender = make_tender(dao.did, "Carbon ledger smart contracts", ["541511"], 32_000, 45)
    print(f"  Tender (EU DAO): '{tender.title}'  budget=${tender.budget_max_usd:,}")

    # L2 matching across both registries
    matches = cross.find_matches(tender, [us_reg, eu_reg])
    print(f"  CrossBorder matchmaker queried US + EU registries  → {len(matches)} candidate(s)")
    top, score = matches[0]
    print(f"  Top match: {top.display_name} [{top.home_jurisdiction}]  score={score}")

    # L3 negotiation
    result = neg.negotiate(tender, top, dao, supplier_floor=26_000)
    for line in result.log:
        print(f"  {line}")
    print(f"  Negotiation: {'SUCCESS' if result.success else 'FAILED'}  "
          f"price=${result.final_price:,.0f}")

    if not result.success:
        return

    # Bundle — cross-border flag set automatically
    contract = make_contract(tender, result)
    bundle   = cross.build_bundle(contract, "US", "EU")
    print(f"\n  Bundle ID: {bundle.bundle_id[:28]}...")
    print(f"  cross_border={bundle.cross_border}  "
          f"supplier_jurisdiction={bundle.supplier_jurisdiction}  "
          f"buyer_jurisdiction={bundle.buyer_jurisdiction}")

    # L4 x402 stablecoin (cross-border)
    settlement = x402.settle(bundle, contract.milestones[0])
    print(f"  Settlement: {settlement.rail.value.upper()}  "
          f"{settlement.amount:,.0f} {settlement.currency}  status={settlement.status}")

    # L2 → L1 dual reporting: same bundle_id appears in BOTH registries
    records = cross.report_contract(bundle, dev.did, us_reg, dao.did, eu_reg)
    print(f"\n  Tax records filed to {len(records)} jurisdictions:")
    for r in records:
        print(f"    [{r.jurisdiction:<12}] {r.party_role.value:>8}  "
              f"${r.contract_value_usd:,.0f}  bundle={r.contract_bundle_id[:20]}...")

    print(f"\n  {us_reg.summary()}")
    print(f"  {eu_reg.summary()}")


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 3 — Competing matchmakers: same tender, race to match
# ─────────────────────────────────────────────────────────────────────────────

def demo_competing_matchmakers(world: dict):
    sep("DEMO 3 — Competing matchmakers: same tender, two operators race")
    print("  AlphaMatch (score algorithm) vs BetaMatch (reputation algorithm)\n")

    us_reg = world["registries"]["US"]
    alpha  = world["matchmakers"]["alpha"]
    beta   = world["matchmakers"]["beta"]
    neg    = world["negotiator"]
    fednow = world["rails"]["fednow"]

    # Add more suppliers so both matchmakers have candidates
    for i, (name, naics) in enumerate([
        ("Sam Rivera",   ["541511"]),
        ("Priya Nair",   ["541511", "541512"]),
        ("Leo Tanaka",   ["541511"]),
    ]):
        us_reg.register_agent(make_supplier(name, naics, ["python"], n_creds=i+2))

    buyer  = us_reg.register_agent(make_buyer("FutureWorks Inc"))
    tender = make_tender(buyer.did, "ML inference API", ["541511"], 22_000, 20)
    print(f"  Tender: '{tender.title}'  budget=${tender.budget_max_usd:,}")

    # Both matchmakers run independently
    alpha_matches = alpha.find_matches(tender, [us_reg])
    beta_matches  = beta.find_matches(tender, [us_reg])

    print(f"\n  AlphaMatch top pick: {alpha_matches[0][0].display_name}  "
          f"score={alpha_matches[0][1]}")
    print(f"  BetaMatch  top pick: {beta_matches[0][0].display_name}  "
          f"score={beta_matches[0][1]}")

    # Alpha wins the race (first to complete negotiation)
    winner_supplier = alpha_matches[0][0]
    result = neg.negotiate(tender, winner_supplier, buyer, supplier_floor=18_000)
    for line in result.log:
        print(f"  {line}")

    if result.success:
        contract = make_contract(tender, result)
        bundle   = alpha.build_bundle(contract, "US", "US")
        records  = alpha.report_contract(bundle, winner_supplier.did, us_reg, buyer.did, us_reg)

        print(f"\n  AlphaMatch won the race — contract executed")
        print(f"  BetaMatch's proposal is superseded (tender now AWARDED)")
        print(f"  Tax records filed by winner: {len(records)}")
        print(f"  Registry records the winning matchmaker: "
              f"'{records[0].reporting_matchmaker}' (not BetaMatch)")

    print(f"\n  AlphaMatch contracts executed: {alpha.contracts_executed}")
    print(f"  BetaMatch  contracts executed: {beta.contracts_executed} (lost this race)")


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 4 — Reputation portability
# ─────────────────────────────────────────────────────────────────────────────

def demo_reputation_portability(world: dict):
    sep("DEMO 4 — Reputation portability: yeoman switches matchmaker")
    print("  Reputation lives in L1 registry — any matchmaker can read it\n")

    us_reg = world["registries"]["US"]
    alpha  = world["matchmakers"]["alpha"]
    beta   = world["matchmakers"]["beta"]
    neg    = world["negotiator"]
    fednow = world["rails"]["fednow"]

    # New yeoman starts with AlphaMatch
    ana = us_reg.register_agent(
        make_supplier("Ana Souza", ["519130", "541511"], ["nlp", "python"], n_creds=1))

    print(f"  Ana registers with registry. Initial reputation: "
          f"{len(us_reg.get_reputation(ana.did))} attestation(s)")

    # Complete 3 contracts via AlphaMatch — each adds a reputation attestation
    buyer1 = us_reg.register_agent(make_buyer("Buyer One"))
    buyer2 = us_reg.register_agent(make_buyer("Buyer Two"))
    buyer3 = us_reg.register_agent(make_buyer("Buyer Three"))

    for i, (buyer, budget) in enumerate([(buyer1, 5_000), (buyer2, 7_000), (buyer3, 6_500)], 1):
        tender  = make_tender(buyer.did, f"NLP task {i}", ["519130"], budget, 10)
        matches = alpha.find_matches(tender, [us_reg])
        if not matches:
            continue
        result  = neg.negotiate(tender, ana, buyer, supplier_floor=budget * 0.8)
        if result.success:
            contract = make_contract(tender, result)
            bundle   = alpha.build_bundle(contract, "US", "US")
            alpha.report_contract(bundle, ana.did, us_reg, buyer.did, us_reg)
            # Add reputation attestation to registry (matchmaker attests, registry stores)
            att = _h(f"perf:{ana.did}:{bundle.bundle_id}")
            us_reg.add_attestation(ana.did, att)
            print(f"  Contract {i} via AlphaMatch — attestation added to US registry")

    print(f"\n  Ana's reputation in US registry: "
          f"{len(us_reg.get_reputation(ana.did))} attestation(s)  "
          f"(stored in registry, not in AlphaMatch)")

    # Ana switches to BetaMatch — BetaMatch queries registry directly
    print(f"\n  Ana switches to BetaMatch...")
    buyer4 = us_reg.register_agent(make_buyer("Buyer Four"))
    tender = make_tender(buyer4.did, "NLP task 4", ["519130"], 8_000, 10)

    beta_matches = beta.find_matches(tender, [us_reg])
    # Verify BetaMatch can see Ana's full reputation
    ana_rep_via_beta = us_reg.get_reputation(ana.did)
    print(f"  BetaMatch queries registry for Ana → sees "
          f"{len(ana_rep_via_beta)} attestation(s)")
    print(f"  (AlphaMatch cooperation not required — data is in the registry)")

    result = neg.negotiate(tender, ana, buyer4, supplier_floor=6_500)
    if result.success:
        contract = make_contract(tender, result)
        bundle   = beta.build_bundle(contract, "US", "US")
        beta.report_contract(bundle, ana.did, us_reg, buyer4.did, us_reg)
        print(f"  Contract 4 via BetaMatch — price=${result.final_price:,.0f}")
        print(f"  Portability confirmed: yeoman switched matchmakers without losing reputation")


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 5 — Machine speed: 20 micro-contracts in one loop
# ─────────────────────────────────────────────────────────────────────────────

def demo_machine_speed(world: dict):
    sep("DEMO 5 — Machine-speed batch: 20 micro-contracts")
    print("  Simulates AI agents transacting autonomously at scale\n")

    us_reg = world["registries"]["US"]
    eu_reg = world["registries"]["EU"]
    cross  = world["matchmakers"]["cross"]
    neg    = world["negotiator"]

    # Pool of suppliers and buyers (mix of US and EU)
    suppliers = [
        us_reg.register_agent(make_supplier(f"Agent-{i}", ["541511"], ["python"], n_creds=2))
        for i in range(5)
    ]
    eu_buyers = [
        eu_reg.register_agent(make_buyer(f"EU-Buyer-{i}", "private_company"))
        for i in range(4)
    ]
    us_buyers = [
        us_reg.register_agent(make_buyer(f"US-Buyer-{i}"))
        for i in range(3)
    ]

    n_contracts  = 0
    n_cross      = 0
    total_value  = 0.0
    start        = datetime.now(timezone.utc)

    for i in range(20):
        supplier = random.choice(suppliers)
        is_cross = random.random() > 0.4
        buyer    = random.choice(eu_buyers) if is_cross else random.choice(us_buyers)
        b_reg    = eu_reg if is_cross else us_reg
        budget   = random.randint(500, 5_000)

        tender  = make_tender(buyer.did, f"Micro task {i}", ["541511"], budget, 3)
        result  = neg.negotiate(tender, supplier, buyer, supplier_floor=budget * 0.75)

        if result.success:
            contract = make_contract(tender, result)
            s_jur = supplier.home_jurisdiction
            b_jur = buyer.home_jurisdiction
            bundle = cross.build_bundle(contract, s_jur, b_jur)
            cross.report_contract(bundle, supplier.did, us_reg, buyer.did, b_reg)
            n_contracts += 1
            n_cross     += int(is_cross)
            total_value += result.final_price

    elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
    print(f"  Attempted: 20  |  Completed: {n_contracts}  |  Cross-border: {n_cross}")
    print(f"  Total value: ${total_value:,.0f}")
    print(f"  Wall-clock time: {elapsed_ms:.1f}ms  "
          f"(in production: <500ms/contract on async rails)")
    print(f"  All {n_contracts} contracts reported to registries synchronously")
    print(f"  Tax overhead per contract: 0 marginal cost (same execution path)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    random.seed(42)

    print("\n" + "=" * 70)
    print("  FEDERATED AGENT COMMERCE REGISTRY — PROTOTYPE")
    print("  L0–L5 Stack: International Standard → National Registry →")
    print("               Matchmaker → Negotiation → Settlement → Tax")
    print("=" * 70)

    world = setup_world()

    print("\n  Infrastructure initialised:")
    for code, reg in world["registries"].items():
        print(f"    {reg.summary()}")
    print(f"    Matchmakers: "
          + ", ".join(f"{mm.name} ({mm.matchmaker_id})" for mm in world["matchmakers"].values()))

    demo_domestic_us(world)
    demo_cross_border(world)
    demo_competing_matchmakers(world)
    demo_reputation_portability(world)
    demo_machine_speed(world)

    sep("TAX AUTHORITY LEDGERS — end state")
    print()
    for code, ta in world["tax"].items():
        ta.print_summary()

    sep("REGISTRY SUMMARIES — end state")
    print()
    for code, reg in world["registries"].items():
        print(f"  {reg.summary()}")

    sep("MATCHMAKER ACTIVITY")
    print()
    for key, mm in world["matchmakers"].items():
        licensed_in = ", ".join(mm.licenses.keys()) or "none"
        print(f"  {mm.name:<15} contracts_executed={mm.contracts_executed:<4} "
              f"licensed_in=[{licensed_in}]")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
