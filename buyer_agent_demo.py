"""
Buyer Agent — End-to-End Procurement Flow
==========================================
Shows the full lifecycle from the buyer agent's perspective:

  1. Task definition    — buyer agent knows what it needs and its constraints
  2. Tender posting     — structured requirements sent to matchmaker
  3. Candidate review   — matchmaker returns ranked suppliers with reputation
  4. Negotiation        — A2A proposal/counter loop with chosen supplier
  5. Contract signing   — both agents sign; tax record created immediately
  6. Work delivery      — supplier agent submits deliverable with content hash
  7. Validation         — buyer agent checks deliverable against acceptance criteria
  8. Payment release    — milestone funds released on pass; revision requested on fail
  9. Attestation        — performance record written to registry

Three scenarios:
  A. Clean pass     — deliverable accepted first time, payment released
  B. Revision cycle — first submission fails, revision requested, second passes
  C. Physical work  — robot task with IoT sensor attestation instead of content hash

Run: python3 buyer_agent_demo.py
"""

from __future__ import annotations
import hashlib, random, uuid, textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from platform_schemas import (
    SupplierAgentCard, BuyerAgentCard,
    Tender, TenderRequirements, Contract, Milestone, MilestoneStatus,
    EngagementType, ContractStatus, STANDARD_MODULES,
    TaxRecord, TaxRecordRole, CrossBorderContractBundle,
    SettlementEvent, PaymentRail,
)
from federated_registry_demo import (
    JurisdictionalAgent, NationalRegistry, TaxAuthority,
    Matchmaker, AgentNegotiator, NegotiationResult,
    FedNowRail, X402Rail,
    make_supplier, make_buyer, make_tender, make_contract,
    _h,
)


# ─────────────────────────────────────────────────────────────────────────────
# DELIVERABLE — what a supplier agent submits
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Deliverable:
    """
    Submitted by supplier agent on completion.
    content_hash: SHA-256 of the actual work artifact.
    In production: IPFS CID of deliverable stored off-chain.
    Smart contract verifies CID before releasing escrow.
    """
    deliverable_id:  str   = field(default_factory=lambda: f"del:{uuid.uuid4().hex[:10]}")
    contract_id:     str   = ""
    supplier_did:    str   = ""
    content_hash:    str   = ""       # SHA-256 of artifact
    content_summary: str   = ""       # human-readable description
    artifacts:       list  = field(default_factory=list)   # ["report.pdf", "pipeline.py"]
    submitted_at:    str   = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    revision:        int   = 1        # 1 = first attempt, 2 = after revision request


@dataclass
class ValidationCriterion:
    name:        str
    description: str
    required:    bool = True    # if True, failure = reject; if False, failure = flag only

@dataclass
class ValidationResult:
    passed:           bool
    score:            float          # 0.0–1.0
    criteria_results: dict           # criterion_name → {"passed": bool, "note": str}
    notes:            str
    action:           str            # "release_payment" | "request_revision" | "dispute"
    revision_notes:   str = ""       # what the supplier must fix


# ─────────────────────────────────────────────────────────────────────────────
# BUYER AGENT
# ─────────────────────────────────────────────────────────────────────────────

class BuyerAgent:
    """
    Autonomous agent acting on behalf of a buyer (company, DAO, government agency).
    Runs the full procurement lifecycle without human involvement per transaction.
    Human sets: budget, task requirements, acceptance criteria.
    Agent handles: discovery, negotiation, validation, payment, attestation.
    """

    def __init__(
        self,
        card: JurisdictionalAgent,
        budget_usd: float,
        task_title: str,
        task_description: str,
        acceptance_criteria: list[ValidationCriterion],
        naics_required: list[str],
        duration_days: int = 14,
    ):
        self.card                = card
        self.budget_usd          = budget_usd
        self.task_title          = task_title
        self.task_description    = task_description
        self.acceptance_criteria = acceptance_criteria
        self.naics_required      = naics_required
        self.duration_days       = duration_days

    def post_tender(self, matchmaker: Matchmaker) -> Tender:
        tender = Tender(
            buyer_did=self.card.did,
            title=self.task_title,
            description_plain=self.task_description,
            requirements=TenderRequirements(
                required_naics=self.naics_required,
                required_credentials=[],
                min_past_performance_count=0,
                set_aside=None,
                geographic_constraint=None,
            ),
            engagement_type=EngagementType.FIXED_PRICE,
            budget_max_usd=self.budget_usd,
            estimated_duration_days=self.duration_days,
        )
        log(f"Buyer agent posted tender: '{tender.title}'")
        log(f"  budget=${tender.budget_max_usd:,.0f}  "
            f"naics={self.naics_required}  duration={self.duration_days}d")
        return tender

    def review_candidates(
        self,
        candidates: list[tuple[JurisdictionalAgent, float]],
        registry: NationalRegistry,
    ) -> Optional[JurisdictionalAgent]:
        """
        Agent reviews ranked candidates. Applies its own selection policy.
        Here: take the top scorer but also inspect reputation depth.
        """
        log(f"\nBuyer agent reviewing {len(candidates)} candidate(s) from matchmaker:")
        for agent, score in candidates:
            rep = len(registry.get_reputation(agent.did))
            caps = getattr(agent.base_card, 'capabilities', [])
            log(f"  {agent.display_name:<22} score={score:.3f}  "
                f"rep={rep} attestations  caps={caps[:3]}")

        if not candidates:
            log("  No candidates found — widening search or reposting")
            return None

        chosen, score = candidates[0]
        log(f"\nBuyer agent selects: {chosen.display_name} (score={score:.3f})")
        return chosen

    def validate_deliverable(
        self,
        deliverable: Deliverable,
        contract: Contract,
    ) -> ValidationResult:
        """
        Buyer agent checks deliverable against acceptance criteria.
        In production: LLM-assisted review + deterministic checks.
        Here: simulated with rule-based scoring.
        """
        results = {}
        score_sum = 0.0
        n_required = 0
        required_failures = 0

        for criterion in self.acceptance_criteria:
            # Simulate: hash-based determinism so revisions can differ
            seed_val = int(
                hashlib.sha256(
                    f"{deliverable.content_hash}:{criterion.name}:{deliverable.revision}".encode()
                ).hexdigest()[:8], 16
            )
            # First revision: ~70% pass rate on required criteria
            # Second revision (after feedback): ~95% pass rate
            threshold = 0.30 if deliverable.revision == 1 else 0.05
            passed = (seed_val % 100) >= (threshold * 100)

            note = "✓ meets specification" if passed else "✗ does not meet specification"
            results[criterion.name] = {"passed": passed, "note": note, "required": criterion.required}

            score_sum += float(passed)
            if criterion.required:
                n_required += 1
                if not passed:
                    required_failures += 1

        overall_score = score_sum / len(self.acceptance_criteria) if self.acceptance_criteria else 1.0
        all_required_passed = (required_failures == 0)

        if all_required_passed and overall_score >= 0.75:
            action = "release_payment"
            notes  = "Deliverable meets all required criteria."
            rev    = ""
        elif not all_required_passed and deliverable.revision == 1:
            action = "request_revision"
            failed = [k for k, v in results.items() if not v["passed"] and v["required"]]
            notes  = f"Required criteria not met: {', '.join(failed)}."
            rev    = (f"Please address: " +
                      "; ".join(f"{k} — {results[k]['note']}" for k in failed))
        else:
            action = "dispute"
            notes  = "Deliverable fails acceptance criteria after revision."
            rev    = ""

        return ValidationResult(
            passed=all_required_passed and overall_score >= 0.75,
            score=round(overall_score, 2),
            criteria_results=results,
            notes=notes,
            action=action,
            revision_notes=rev,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIER AGENT
# ─────────────────────────────────────────────────────────────────────────────

class SupplierAgent:
    """
    Autonomous agent acting on behalf of a yeoman supplier.
    Receives contracts, executes work, submits deliverables.
    """

    def __init__(self, card: JurisdictionalAgent):
        self.card = card

    def acknowledge_contract(self, contract: Contract) -> str:
        ack = _h(f"ack:{self.card.did}:{contract.id}")
        log(f"Supplier agent [{self.card.display_name}] acknowledged contract {contract.id[:20]}...")
        return ack

    def submit_deliverable(
        self,
        contract: Contract,
        summary: str,
        artifacts: list[str],
        revision: int = 1,
    ) -> Deliverable:
        # In production: actual work product hashed and stored on IPFS
        content = f"{summary}:{artifacts}:{contract.id}:{revision}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        d = Deliverable(
            contract_id=contract.id,
            supplier_did=self.card.did,
            content_hash=content_hash,
            content_summary=summary,
            artifacts=artifacts,
            revision=revision,
        )
        log(f"Supplier agent [{self.card.display_name}] submitted deliverable "
            f"(revision {revision})")
        log(f"  artifacts: {artifacts}")
        log(f"  content_hash: {content_hash[:20]}...")
        return d

    def submit_revision(self, contract: Contract, original: Deliverable,
                        revision_notes: str) -> Deliverable:
        log(f"\nSupplier agent [{self.card.display_name}] received revision request:")
        log(f"  '{revision_notes[:80]}'")
        log(f"  Addressing feedback and resubmitting...")
        return self.submit_deliverable(
            contract,
            summary=original.content_summary + " [revised]",
            artifacts=[f"revised_{a}" for a in original.artifacts],
            revision=original.revision + 1,
        )


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_INDENT = "  "

def log(msg: str, indent: int = 0):
    prefix = _INDENT * indent
    print(prefix + msg)

def step(title: str):
    print(f"\n  ── {title}")

def section(title: str):
    print("\n" + "─" * 68)
    print(f"  {title}")
    print("─" * 68)

def print_validation(vr: ValidationResult):
    icon = "✓" if vr.passed else "✗"
    log(f"  Validation result: {icon}  score={vr.score:.0%}  action={vr.action}")
    for name, r in vr.criteria_results.items():
        req = "[required]" if r["required"] else "[optional]"
        icon = "✓" if r["passed"] else "✗"
        log(f"    {icon} {name:<35} {req}  {r['note']}")
    if vr.revision_notes:
        log(f"  Revision request: {vr.revision_notes[:80]}")


def run_full_procurement(
    buyer_agent: BuyerAgent,
    matchmaker: Matchmaker,
    registry: NationalRegistry,
    negotiator: AgentNegotiator,
    rail,
    allow_revision: bool = True,
) -> tuple[Optional[Contract], Optional[SettlementEvent]]:
    """Full lifecycle: tender → match → negotiate → contract → deliver → validate → pay."""

    random.seed(42)

    # ── Step 1: Post tender ──────────────────────────────────────────────────
    step("STEP 1 — Buyer agent posts tender")
    tender = buyer_agent.post_tender(matchmaker)

    # ── Step 2: Matchmaker finds candidates ──────────────────────────────────
    step("STEP 2 — Matchmaker finds and ranks candidates")
    candidates = matchmaker.find_matches(tender, [registry])
    if not candidates:
        log("  No candidates. Matchmaker widens search.")
        return None, None

    # ── Step 3: Buyer agent reviews ──────────────────────────────────────────
    step("STEP 3 — Buyer agent reviews candidates")
    chosen = buyer_agent.review_candidates(candidates, registry)
    if not chosen:
        return None, None

    # ── Step 4: Negotiation (A2A, no human in loop) ──────────────────────────
    step("STEP 4 — A2A negotiation (machine speed, no human in loop)")
    floor = tender.budget_max_usd * 0.78
    result = negotiator.negotiate(tender, chosen, buyer_agent.card, supplier_floor=floor)
    for line in result.log:
        log(line)

    if not result.success:
        log("  Negotiation failed — buyer agent widens budget or rejects")
        return None, None

    log(f"  Agreed: ${result.final_price:,.0f} over {result.final_timeline}d  "
        f"in {result.rounds} round(s)")

    # ── Step 5: Contract execution ───────────────────────────────────────────
    step("STEP 5 — Contract signed by both agents; tax record created immediately")
    contract = make_contract(tender, result)

    log(f"  Contract ID:  {contract.id}")
    log(f"  Buyer sig:    {contract.buyer_signature[:20]}...")
    log(f"  Supplier sig: {contract.supplier_signature[:20]}...")
    log(f"  Tax record:   {contract.irs_record_id}  "
        f"[declared at signing, not at payment]")

    # Matchmaker reports to registry (L2 → L1 mandatory)
    bundle = matchmaker.build_bundle(contract, chosen.home_jurisdiction, buyer_agent.card.home_jurisdiction)
    tax_records = matchmaker.report_contract(
        bundle, chosen.did, registry, buyer_agent.card.did, registry
    )
    log(f"  Tax records filed to registry: {len(tax_records)}")

    # ── Step 6: Supplier acknowledges and delivers ───────────────────────────
    step("STEP 6 — Supplier agent acknowledges contract and submits deliverable")
    supplier_agent = SupplierAgent(chosen)
    supplier_agent.acknowledge_contract(contract)

    deliverable = supplier_agent.submit_deliverable(
        contract,
        summary=f"Completed: {tender.title}",
        artifacts=[f"{tender.title.lower().replace(' ', '_')}.py",
                   f"{tender.title.lower().replace(' ', '_')}_report.md"],
    )

    # ── Step 7: Buyer agent validates ────────────────────────────────────────
    step("STEP 7 — Buyer agent validates deliverable against acceptance criteria")
    validation = buyer_agent.validate_deliverable(deliverable, contract)
    print_validation(validation)

    # ── Revision cycle if needed ─────────────────────────────────────────────
    if validation.action == "request_revision" and allow_revision:
        step("STEP 7b — Revision requested; supplier resubmits")
        deliverable = supplier_agent.submit_revision(
            contract, deliverable, validation.revision_notes
        )
        validation = buyer_agent.validate_deliverable(deliverable, contract)
        log("  Re-validation after revision:")
        print_validation(validation)

    if validation.action == "dispute":
        log("  ⚠ Escalating to dispute resolution (AI arbitration within 24h)")
        return contract, None

    # ── Step 8: Payment release ──────────────────────────────────────────────
    step("STEP 8 — Payment released via settlement rail")
    milestone = contract.milestones[0]
    milestone.status = MilestoneStatus.RELEASED
    settlement = rail.settle(bundle, milestone)
    log(f"  Rail:     {settlement.rail.value.upper()}")
    log(f"  Amount:   ${settlement.amount:,.0f} {settlement.currency}")
    log(f"  Status:   {settlement.status}")
    log(f"  Event ID: {settlement.event_id}")

    # ── Step 9: Performance attestation ─────────────────────────────────────
    step("STEP 9 — Buyer agent writes performance attestation to registry")
    score_str = f"{validation.score:.0%}"
    att_body  = (f"perf:{chosen.did}:{contract.id}:"
                 f"score={score_str}:revision={deliverable.revision}")
    att_hash  = _h(att_body)
    registry.add_attestation(chosen.did, att_hash)
    rep_total = len(registry.get_reputation(chosen.did))
    log(f"  Attestation hash: {att_hash}  written to registry")
    log(f"  {chosen.display_name} now has {rep_total} reputation attestation(s)")

    return contract, settlement


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO A — Clean pass
# ─────────────────────────────────────────────────────────────────────────────

def scenario_a(world: dict):
    section("SCENARIO A — Clean pass: deliverable accepted first time")

    irs    = world["tax"]["US"]
    us_reg = world["registries"]["US"]
    alpha  = world["matchmakers"]["alpha"]
    neg    = world["negotiator"]
    fednow = world["rails"]["fednow"]

    # Register supplier
    us_reg.register_agent(
        make_supplier("Maria Chen", ["541511", "541512"],
                      ["python", "data-analysis", "llm"], n_creds=5))

    # Buyer agent setup
    buyer_card = us_reg.register_agent(make_buyer("Acme Analytics"))
    buyer = BuyerAgent(
        card=buyer_card,
        budget_usd=20_000,
        task_title="Customer churn prediction pipeline",
        task_description=(
            "Build a Python ML pipeline that predicts customer churn "
            "from CRM data. Deliverables: trained model, evaluation report, "
            "inference API endpoint."
        ),
        acceptance_criteria=[
            ValidationCriterion("model_accuracy",    "AUC-ROC ≥ 0.80 on holdout set",  required=True),
            ValidationCriterion("inference_api",     "REST API with <200ms p99 latency", required=True),
            ValidationCriterion("evaluation_report", "Report with confusion matrix and feature importance", required=True),
            ValidationCriterion("code_tests",        "≥80% test coverage",               required=False),
            ValidationCriterion("documentation",     "README and inline docstrings",      required=False),
        ],
        naics_required=["541511", "541512"],
        duration_days=14,
    )

    run_full_procurement(buyer, alpha, us_reg, neg, fednow, allow_revision=False)


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO B — Revision cycle
# ─────────────────────────────────────────────────────────────────────────────

def scenario_b(world: dict):
    section("SCENARIO B — Revision cycle: first submission fails, revision passes")

    us_reg = world["registries"]["US"]
    alpha  = world["matchmakers"]["alpha"]
    neg    = world["negotiator"]
    fednow = world["rails"]["fednow"]

    random.seed(7)  # seed that causes first-attempt failure

    us_reg.register_agent(
        make_supplier("Dev Patel", ["541511"], ["rust", "api-design"], n_creds=3))

    buyer_card = us_reg.register_agent(make_buyer("FinanceDAO"))
    buyer = BuyerAgent(
        card=buyer_card,
        budget_usd=15_000,
        task_title="FX rate aggregation microservice",
        task_description=(
            "Rust microservice that aggregates FX rates from 3 public APIs, "
            "caches with 60s TTL, exposes gRPC and REST. "
            "Deliverables: source code, Docker image, load test results."
        ),
        acceptance_criteria=[
            ValidationCriterion("grpc_interface",   "gRPC service definition + implementation", required=True),
            ValidationCriterion("rest_fallback",     "REST endpoint at /rates/{pair}",           required=True),
            ValidationCriterion("caching",           "Redis-backed 60s TTL cache",               required=True),
            ValidationCriterion("load_test",         ">5000 req/s at p99 <10ms",                 required=True),
            ValidationCriterion("docker_image",      "Multi-stage Dockerfile, image <50MB",       required=False),
        ],
        naics_required=["541511"],
        duration_days=10,
    )

    run_full_procurement(buyer, alpha, us_reg, neg, fednow, allow_revision=True)


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO C — Physical robot task with IoT attestation
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class IoTAttestation:
    """Sensor data from the robot's onboard systems, signed by the robot's DID."""
    attestation_id: str  = field(default_factory=lambda: f"iot:{uuid.uuid4().hex[:10]}")
    robot_did:      str  = ""
    task_id:        str  = ""
    sensor_readings: dict = field(default_factory=dict)   # {"gps_verified": True, "sqft_cleaned": 4200, ...}
    signed_hash:    str  = ""
    timestamp:      str  = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def scenario_c(world: dict):
    section("SCENARIO C — Physical robot task: IoT sensor attestation")
    log("  (Cleaning robot hired for commercial property. Validation via onboard sensors.)\n")

    us_reg = world["registries"]["US"]
    cross  = world["matchmakers"]["cross"]
    neg    = world["negotiator"]
    fednow = world["rails"]["fednow"]

    # Robot-owning yeoman
    us_reg.register_agent(
        make_supplier("Sam Rivera Robotics", ["561720"],   # NAICS: janitorial services
                      ["commercial-cleaning", "robot-ops", "route-optimisation"], n_creds=4))

    buyer_card = us_reg.register_agent(make_buyer("PropCo Real Estate"))
    buyer = BuyerAgent(
        card=buyer_card,
        budget_usd=3_500,
        task_title="Deep clean — 12 Broad St, floors 3–5",
        task_description=(
            "Full deep clean of 3 office floors (~4,000 sqft each). "
            "Robot must complete within 8h window (06:00–14:00). "
            "Validation: GPS trail covers all zones, UV-C pass logged."
        ),
        acceptance_criteria=[
            ValidationCriterion("gps_coverage",    "GPS trail covers ≥95% of floor plan",   required=True),
            ValidationCriterion("uvc_pass",        "UV-C sanitisation logged for all zones", required=True),
            ValidationCriterion("duration",        "Completed within 8h window",             required=True),
            ValidationCriterion("photo_evidence",  "Before/after photos uploaded",           required=False),
        ],
        naics_required=["561720"],
        duration_days=1,
    )

    step("STEP 1 — Buyer agent posts tender")
    tender = buyer.post_tender(cross)

    step("STEP 2 — Matchmaker finds candidates")
    candidates = cross.find_matches(tender, [us_reg])
    chosen = buyer.review_candidates(candidates, us_reg)
    if not chosen:
        return

    step("STEP 3 — Negotiation")
    result = neg.negotiate(tender, chosen, buyer_card, supplier_floor=2_800)
    for line in result.log:
        log(line)
    if not result.success:
        return
    log(f"  Agreed: ${result.final_price:,.0f}")

    step("STEP 4 — Contract signed")
    contract = make_contract(tender, result)
    log(f"  Contract: {contract.id[:20]}...  tax record created at signing")
    bundle = cross.build_bundle(contract, chosen.home_jurisdiction, buyer_card.home_jurisdiction)
    cross.report_contract(bundle, chosen.did, us_reg, buyer_card.did, us_reg)

    step("STEP 5 — Robot dispatched; supplier agent monitors task")
    log(f"  Robot DID: {chosen.agent_did}")
    log(f"  Dispatching to 12 Broad St, floors 3–5...")
    log(f"  Estimated completion: 7h 40min")

    step("STEP 6 — Task complete; robot submits IoT attestation")
    # Simulate sensor data
    robot_did = chosen.agent_did
    sensor_data = {
        "gps_coverage_pct":    96.2,
        "uvc_zones_completed": 18,
        "uvc_zones_total":     18,
        "duration_minutes":    452,    # 7h 32min
        "sqft_cleaned":        12_340,
        "photo_count":         24,
    }
    att_body = f"{robot_did}:{contract.id}:{sensor_data}"
    iot = IoTAttestation(
        robot_did=robot_did,
        task_id=contract.id,
        sensor_readings=sensor_data,
        signed_hash=_h(att_body),
    )
    log(f"  IoT attestation: {iot.attestation_id}")
    for k, v in sensor_data.items():
        log(f"    {k:<28} {v}")

    step("STEP 7 — Buyer agent validates against acceptance criteria")
    # Deterministic validation from sensor data (not LLM — pure rules for physical work)
    criteria_map = {
        "gps_coverage":   sensor_data["gps_coverage_pct"] >= 95.0,
        "uvc_pass":       sensor_data["uvc_zones_completed"] == sensor_data["uvc_zones_total"],
        "duration":       sensor_data["duration_minutes"] <= 480,
        "photo_evidence": sensor_data["photo_count"] >= 10,
    }
    all_required = all(
        criteria_map[c.name] for c in buyer.acceptance_criteria if c.required
    )
    log(f"  Validation (rule-based, from IoT sensor data):")
    for c in buyer.acceptance_criteria:
        icon = "✓" if criteria_map[c.name] else "✗"
        req  = "[required]" if c.required else "[optional]"
        log(f"    {icon} {c.name:<28} {req}  {c.description}")
    log(f"\n  Result: {'PASS ✓' if all_required else 'FAIL ✗'}")

    step("STEP 8 — Payment released")
    milestone = contract.milestones[0]
    milestone.status = MilestoneStatus.RELEASED
    settlement = fednow.settle(bundle, milestone)
    log(f"  ${settlement.amount:,.0f} {settlement.currency} via {settlement.rail.value.upper()}")

    step("STEP 9 — IoT attestation written to registry (not just performance score)")
    att_hash = _h(f"iot-perf:{chosen.did}:{iot.attestation_id}:pass")
    us_reg.add_attestation(chosen.did, att_hash)
    log(f"  Attestation includes: GPS coverage, UV-C completion, duration, sqft")
    log(f"  Future buyers can query this yeoman's robot reliability record")
    log(f"  {chosen.display_name} now has {len(us_reg.get_reputation(chosen.did))} attestation(s)")


# ─────────────────────────────────────────────────────────────────────────────
# SETUP (minimal — just enough for the scenarios)
# ─────────────────────────────────────────────────────────────────────────────

def setup():
    irs    = TaxAuthority("US-IRS")
    eu_vat = TaxAuthority("EU-VAT:MULTI")
    us_reg = NationalRegistry("US", "US Yeoman Agent Registry", irs)
    eu_reg = NationalRegistry("EU", "EU Agent Commerce Registry", eu_vat)

    alpha = Matchmaker("mm-alpha", "AlphaMatch", algorithm="score")
    cross = Matchmaker("mm-cross", "CrossBorder", algorithm="score")
    alpha.register_with(us_reg)
    cross.register_with(us_reg)
    cross.register_with(eu_reg)

    return {
        "registries": {"US": us_reg, "EU": eu_reg},
        "tax":        {"US": irs, "EU": eu_vat},
        "matchmakers": {"alpha": alpha, "cross": cross},
        "negotiator": AgentNegotiator(),
        "rails":      {"fednow": FedNowRail(), "x402": X402Rail()},
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 68)
    print("  BUYER AGENT — END-TO-END PROCUREMENT FLOW")
    print("  From task definition to payment release and attestation")
    print("=" * 68)

    world = setup()

    scenario_a(world)   # Clean pass
    scenario_b(world)   # Revision cycle
    scenario_c(world)   # Physical robot / IoT attestation

    print("\n" + "─" * 68)
    print("  FINAL STATE")
    print("─" * 68)
    world["tax"]["US"].print_summary()
    for code, reg in world["registries"].items():
        print(f"  {reg.summary()}")

    print("\n" + "=" * 68 + "\n")


if __name__ == "__main__":
    main()
