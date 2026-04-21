"""
Yeomen Procurement Platform — Core Data Schemas
================================================
Modelled on A2A (Agent-to-Agent) protocol primitives:
  - AgentCard  →  SupplierAgent / BuyerAgent
  - Task       →  Tender
  - Message    →  Bid (with credential Parts)
  - Artifact   →  SignedContract

Wire format: JSON-LD compatible dicts (machine-readable, FOIA-safe)
Credential format: W3C Verifiable Credentials Data Model 2.0 (simplified, no real crypto)

Design notes on the hard policy questions are in comments throughout.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import hashlib
import json
import uuid


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EngagementType(str, Enum):
    FIXED_PRICE    = "fixed_price"
    TIME_AND_MATERIALS = "time_and_materials"
    RETAINER       = "retainer"
    OUTCOME_BASED  = "outcome_based"

class IPTerms(str, Enum):
    WORK_FOR_HIRE  = "work_for_hire"
    LICENSED       = "licensed"
    SHARED         = "shared"
    SUPPLIER_RETAINED = "supplier_retained"

class TenderStatus(str, Enum):
    OPEN      = "open"
    MATCHED   = "matched"   # platform has pushed to qualified suppliers
    IN_REVIEW = "in_review" # buyer reviewing bids
    AWARDED   = "awarded"
    CANCELLED = "cancelled"

class ContractStatus(str, Enum):
    DRAFT     = "draft"
    EXECUTED  = "executed"
    ACTIVE    = "active"
    COMPLETED = "completed"
    DISPUTED  = "disputed"

class MilestoneStatus(str, Enum):
    PENDING   = "pending"
    CLAIMED   = "claimed"   # supplier says done
    APPROVED  = "approved"
    DISPUTED  = "disputed"
    RELEASED  = "released"  # funds released via FedNow


# ---------------------------------------------------------------------------
# Layer 1 — Identity & Credentials
#
# Privacy design:
#   - The platform holds HASHES of credentials, not content.
#   - Actual credential JSON is held by the supplier (in their wallet).
#   - Verification = supplier presents VC → platform checks signature hash.
#   - Off-platform: supplier's tax_id is the anchor; all on-platform
#     transactions are 1099-linked at contract acceptance (not payment).
# ---------------------------------------------------------------------------

@dataclass
class VerifiableCredential:
    """
    W3C VC Data Model 2.0 (simplified — no real crypto, just the shape).

    In production: issuer signs with Ed25519; proof.jws is a real JWS.
    Here: proof.jws is a SHA-256 hash of the credential body (toy only).

    Privacy note: The supplier presents this to the platform. The platform
    stores only credential_hash and issuer_did. The full VC stays in the
    supplier's wallet. This means the platform cannot be compelled (FOIA)
    to reveal the underlying work details.
    """
    id: str                          # did:example:cred:<uuid>
    type: list[str]                  # ["VerifiableCredential", "PastPerformanceCredential"]
    issuer_did: str                  # did:example:org:<issuer-id>
    issuer_name: str                 # human-readable for display
    subject_did: str                 # supplier's DID
    issued_at: str                   # ISO8601
    expiry: str | None               # ISO8601 or None
    claims: dict[str, Any]           # credential-specific payload
    proof_jws: str = ""              # toy: SHA-256 of body; real: JWS

    def __post_init__(self):
        if not self.proof_jws:
            body = json.dumps({
                "id": self.id, "issuer": self.issuer_did,
                "subject": self.subject_did, "claims": self.claims
            }, sort_keys=True)
            self.proof_jws = hashlib.sha256(body.encode()).hexdigest()

    @property
    def credential_hash(self) -> str:
        return hashlib.sha256(self.proof_jws.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SupplierAgentCard:
    """
    A2A AgentCard for a supplier agent.

    Privacy note: capability_tags and credential_hashes are what the
    platform stores. Actual credential content lives with the supplier.
    tax_id is stored encrypted; the platform decrypts only at contract
    acceptance for 1099 generation.

    Off-market problem: tax_id linkage means any payment from a verified
    buyer to this supplier — even outside the platform — can be flagged
    if the 1099 doesn't match platform records. The platform becomes the
    baseline expectation.
    """
    did: str                         # did:gov:tax:<hashed-EIN-or-SSN>
    display_name: str                # public name
    entity_type: str                 # "sole_operator" | "llc" | "cooperative"
    tax_id_hash: str                 # SHA-256(tax_id) — stored; tax_id encrypted separately
    capabilities: list[str]          # plain-English tags: ["python", "data-analysis", "llm-fine-tuning"]
    naics_codes: list[str]           # NAICS codes for procurement matching
    credential_hashes: list[str]     # hashes of held VCs (not VC content)
    service_endpoint: str            # A2A endpoint URL for this supplier's agent
    auth_scheme: str                 # "oauth2" | "api_key"
    set_aside_eligibility: list[str] # ["8a", "wosb", "hubzone", "sdvosb"]
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_sam_registered: bool = False  # synced from SAM.gov

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BuyerAgentCard:
    """A2A AgentCard for a buyer. Symmetric to supplier."""
    did: str
    display_name: str
    entity_type: str                 # "federal_agency" | "state_agency" | "private_company" | "individual"
    tax_id_hash: str
    service_endpoint: str
    auth_scheme: str
    set_aside_preferences: list[str] # preferred set-aside vehicles
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Layer 2 — Tender (A2A Task)
#
# Off-market problem (addressed here):
#   The platform cannot prevent off-market transactions — no system can.
#   The design instead makes on-platform transactions so clearly superior
#   that off-market becomes the irrational choice:
#     1. Zero fee vs 30% on private platforms
#     2. Tax-safe harbour: on-platform = 1099 auto-generated, no audit risk
#     3. Reputation non-portable off-platform (attestations are on-platform)
#     4. FedNow instant payment only via platform escrow
#     5. For federal work: mandate (can't go off-platform)
#   The regulatory minimum: a 'platform-verified' flag on 1099s, making
#   unverified transactions more likely to trigger audit — not a ban, just
#   a signal. This is analogous to how card payments replaced cash in B2B.
# ---------------------------------------------------------------------------

@dataclass
class TenderRequirements:
    """Structured qualification requirements for a tender."""
    required_naics: list[str]        # must match at least one
    required_credentials: list[str]  # credential type tags supplier must hold
    min_past_performance_count: int  # minimum verified prior engagements
    set_aside: str | None            # "8a" | "wosb" | None (open)
    geographic_constraint: str | None # "US_only" | "state:CA" | None
    clearance_required: bool = False  # triggers separate classified flow


@dataclass
class Tender:
    """
    A2A Task adapted for procurement.

    Matching is push-based and private:
      - Platform evaluates all registered SupplierAgentCards against requirements
      - Sends tender only to matching suppliers (they don't know who else received it)
      - No public listing → prevents incumbent intelligence harvesting
      - Bid amounts encrypted in transit; only buyer + platform (for tax) see them
    """
    id: str = field(default_factory=lambda: f"tender:{uuid.uuid4().hex[:12]}")
    buyer_did: str = ""
    title: str = ""
    description_plain: str = ""      # human-readable
    requirements: TenderRequirements | None = None
    engagement_type: EngagementType = EngagementType.FIXED_PRICE
    budget_min_usd: float | None = None
    budget_max_usd: float | None = None
    response_deadline: str = ""      # ISO8601
    start_date: str = ""
    estimated_duration_days: int = 0
    milestones: list[dict] = field(default_factory=list)
    status: TenderStatus = TenderStatus.OPEN
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Tax infrastructure fields (set at creation, immutable)
    tax_record_id: str = field(default_factory=lambda: f"txrec:{uuid.uuid4().hex}")
    reporting_jurisdiction: str = "US-IRS"

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.requirements:
            d["requirements"] = asdict(self.requirements)
        return d


# ---------------------------------------------------------------------------
# Layer 3 — Bid (A2A Message with credential Parts)
#
# Privacy: bid_amount_usd visible to buyer + platform only (not public).
# Credentials presented as hashes + ZK-style claims (toy implementation).
# ---------------------------------------------------------------------------

@dataclass
class CredentialPresentation:
    """
    Supplier presents a subset of credentials relevant to this tender.
    ZK-style: platform verifies the hash matches a known VC without
    seeing the full VC content. In production: real ZK proof or selective
    disclosure (SD-JWT).
    """
    credential_hash: str             # matches hash in SupplierAgentCard
    credential_type: str             # e.g. "PastPerformanceCredential"
    issuer_did: str
    disclosed_claims: dict[str, Any] # what the supplier chooses to reveal
    # e.g. {"past_project_count": 14, "avg_rating": 4.8, "domain": "data-analysis"}
    # NOT revealed: client names, project details, exact amounts


@dataclass
class Bid:
    """A2A Message representing a supplier's response to a tender."""
    id: str = field(default_factory=lambda: f"bid:{uuid.uuid4().hex[:12]}")
    tender_id: str = ""
    supplier_did: str = ""
    bid_amount_usd: float = 0.0
    proposed_timeline_days: int = 0
    approach_summary: str = ""       # plain English
    credential_presentations: list[CredentialPresentation] = field(default_factory=list)
    ai_tools_used: list[str] = field(default_factory=list)  # AI disclosure (standard)
    submitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        d = asdict(self)
        d["credential_presentations"] = [asdict(cp) for cp in self.credential_presentations]
        return d


# ---------------------------------------------------------------------------
# Layer 3 — Contract (A2A Artifact, machine-readable)
#
# Machine-readable + plain-English. SPDX-style modular structure.
# AI use disclosure is a standard field, not an optional addendum.
# Tax record created at contract ACCEPTANCE (not payment) — this is the
# key design choice that makes the platform enforcement-immune to payment
# routing games.
# ---------------------------------------------------------------------------

@dataclass
class ContractModule:
    """One standard module from the open contract library."""
    module_type: str                 # "engagement" | "ip" | "ai_disclosure" | "confidentiality" | "dispute" | "termination"
    version: str                     # "1.0"
    terms: dict[str, Any]            # structured terms
    plain_english_summary: str       # human-readable


@dataclass
class Milestone:
    id: str = field(default_factory=lambda: f"ms:{uuid.uuid4().hex[:8]}")
    description: str = ""
    due_date: str = ""
    amount_usd: float = 0.0
    status: MilestoneStatus = MilestoneStatus.PENDING
    escrow_account: str = ""         # FedNow escrow account ref
    completion_criteria: str = ""    # plain English


@dataclass
class Contract:
    """
    A2A Artifact. Executed at contract acceptance.
    Tax record (irs_record_id) is created HERE — before any payment.
    This is the enforcement mechanism: the income is declared at commitment.

    Private sector imposition concern:
      The contract standard is OPEN — private platforms can implement it.
      The requirement is only that federal contracts use this format.
      Private sector adopts because: portable reputation is more valuable
      than lock-in for suppliers, and standard contracts reduce buyer
      legal costs. The mandate is soft: "federal work requires this format"
      not "all private contracts require this format". Uptake follows from
      network effects, not regulation.
    """
    id: str = field(default_factory=lambda: f"contract:{uuid.uuid4().hex[:12]}")
    tender_id: str = ""
    bid_id: str = ""
    buyer_did: str = ""
    supplier_did: str = ""
    total_value_usd: float = 0.0
    milestones: list[Milestone] = field(default_factory=list)
    modules: list[ContractModule] = field(default_factory=list)
    status: ContractStatus = ContractStatus.DRAFT

    # Tax infrastructure — created at acceptance, immutable
    irs_record_id: str = field(default_factory=lambda: f"irs:{uuid.uuid4().hex}")
    tax_year: int = field(default_factory=lambda: datetime.now(timezone.utc).year)
    reporting_jurisdiction: str = "US-IRS"
    auto_1099_scheduled: bool = True

    # Signatures (toy: hashes; real: Ed25519 digital signatures)
    buyer_signature: str = ""
    supplier_signature: str = ""
    platform_attestation: str = ""   # platform certifies both parties verified
    executed_at: str = ""

    def execute(self, buyer_did: str, supplier_did: str):
        """Sign and execute the contract. Creates the tax record."""
        now = datetime.now(timezone.utc).isoformat()
        self.buyer_signature = hashlib.sha256(f"{buyer_did}:{self.id}:{now}".encode()).hexdigest()
        self.supplier_signature = hashlib.sha256(f"{supplier_did}:{self.id}:{now}".encode()).hexdigest()
        self.platform_attestation = hashlib.sha256(
            f"PLATFORM_VERIFIED:{self.id}:{now}".encode()
        ).hexdigest()
        self.executed_at = now
        self.status = ContractStatus.EXECUTED
        return self

    def to_dict(self) -> dict:
        d = asdict(self)
        d["milestones"] = [asdict(m) for m in self.milestones]
        d["modules"] = [asdict(m) for m in self.modules]
        return d


# ---------------------------------------------------------------------------
# Standard Contract Module Library (open, versioned)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Federated Registry Extensions — L0 International Standard additions
# ---------------------------------------------------------------------------

class PaymentRail(str, Enum):
    FEDNOW         = "fednow"
    X402           = "x402"            # HTTP-native stablecoin (Coinbase)
    SWIFT_ISO20022 = "swift_iso20022"

class NegotiationMessageType(str, Enum):
    PROPOSAL = "proposal"
    COUNTER  = "counter"
    ACCEPT   = "accept"
    REJECT   = "reject"

class TaxRecordRole(str, Enum):
    SUPPLIER = "supplier"
    BUYER    = "buyer"


@dataclass
class TaxRecord:
    """
    L0-standardised tax record. Created at contract execution, not payment.
    Submitted by the matchmaker to each relevant national registry.
    Each registry forwards to its domestic tax authority.
    schema_version pins the L0 standard version for forward-compatibility.
    """
    record_id: str              = field(default_factory=lambda: f"taxrec:{uuid.uuid4().hex[:12]}")
    jurisdiction: str           = ""          # "US-IRS", "EU-VAT:DE", "UK-HMRC"
    contract_bundle_id: str     = ""          # globally unique — same ID in both registries
    party_role: TaxRecordRole   = TaxRecordRole.SUPPLIER
    party_tax_id_hash: str      = ""
    contract_value_usd: float   = 0.0
    currency: str               = "USD"
    declared_at: str            = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reporting_matchmaker: str   = ""
    schema_version: str         = "L0-v1.0"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AgentNegotiationMessage:
    """
    L3 A2A negotiation message. Proposal → Counter → Accept/Reject.
    Both sides are AI agents; human is not in the loop per message.
    """
    message_id: str                       = field(default_factory=lambda: f"msg:{uuid.uuid4().hex[:10]}")
    negotiation_session_id: str           = ""
    sender_did: str                       = ""
    receiver_did: str                     = ""
    message_type: NegotiationMessageType  = NegotiationMessageType.PROPOSAL
    proposed_terms: dict                  = field(default_factory=dict)
    timestamp: str                        = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    round_number: int                     = 1

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MatchmakerLicense:
    """
    Issued by a NationalRegistry to a private matchmaker.
    Conditions: implement L0 schema, report contracts, allow portability.
    Analogous to ICANN accredited registrar license.
    """
    matchmaker_id: str      = ""
    matchmaker_name: str    = ""
    licensed_by: list[str]  = field(default_factory=list)   # list of registry DIDs
    license_issued_at: str  = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    license_conditions: list[str] = field(default_factory=lambda: [
        "report_contracts_within_60s",
        "portability_of_reputation_data",
        "implement_l0_schema_v1",
        "no_retention_of_credential_content",
    ])

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CrossBorderContractBundle:
    """
    L0 wrapper that routes a Contract to the correct national registries.
    bundle_id is globally unique — referenced by BOTH registries.
    This is the artifact that makes cross-border tax reporting automatic.
    """
    bundle_id: str              = field(default_factory=lambda: f"bundle:{uuid.uuid4().hex}")
    contract: Any               = None          # Contract instance
    supplier_jurisdiction: str  = ""            # ISO 3166-1 alpha-2
    buyer_jurisdiction: str     = ""
    reporting_registries: list  = field(default_factory=list)  # registry DIDs
    executed_by_matchmaker: str = ""
    cross_border: bool          = False
    schema_version: str         = "L0-v1.0"


@dataclass
class SettlementEvent:
    """L4 settlement record. One per milestone released."""
    event_id: str               = field(default_factory=lambda: f"settle:{uuid.uuid4().hex[:10]}")
    contract_bundle_id: str     = ""
    milestone_id: str           = ""
    amount: float               = 0.0
    currency: str               = "USD"
    rail: PaymentRail           = PaymentRail.FEDNOW
    status: str                 = "released"    # "escrowed" | "released" | "disputed"
    timestamp: str              = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


STANDARD_MODULES = {
    "fixed_price_engagement": ContractModule(
        module_type="engagement",
        version="1.0",
        terms={
            "type": "fixed_price",
            "payment_on": "milestone_approval",
            "change_order_threshold_pct": 10,
            "change_order_process": "written_amendment_required"
        },
        plain_english_summary=(
            "Fixed price. Payment releases when buyer approves each milestone. "
            "Changes over 10% of contract value require a written amendment."
        )
    ),
    "work_for_hire_ip": ContractModule(
        module_type="ip",
        version="1.0",
        terms={
            "ownership": "buyer",
            "transfer_on": "final_payment",
            "supplier_portfolio_rights": True,   # supplier can show work in portfolio
            "training_data_exclusion": True       # buyer's data cannot be used for AI training
        },
        plain_english_summary=(
            "Buyer owns all deliverables on final payment. "
            "Supplier may reference the engagement in their portfolio. "
            "Buyer's data is excluded from AI training datasets."
        )
    ),
    "ai_use_standard": ContractModule(
        module_type="ai_disclosure",
        version="1.0",
        terms={
            "declaration_required": True,
            "human_review_required": True,
            "tools_disclosed_at": "bid_submission",  # supplier lists tools in bid
            "prohibited_uses": ["training_on_client_data", "retention_beyond_project"]
        },
        plain_english_summary=(
            "Supplier must declare all AI tools used in the bid. "
            "All AI-generated deliverables must have human review. "
            "Client data may not be used to train AI models."
        )
    ),
    "standard_arbitration": ContractModule(
        module_type="dispute",
        version="1.0",
        terms={
            "mechanism": "binding_arbitration",
            "body": "platform_arbitration_panel",
            "sla_days": 21,
            "governing_law": "US_federal",
            "precedent_published": True   # anonymised decisions are public
        },
        plain_english_summary=(
            "Disputes go to binding arbitration within 21 days. "
            "Decisions are published (anonymised) to build public precedent."
        )
    ),
    "standard_termination": ContractModule(
        module_type="termination",
        version="1.0",
        terms={
            "notice_days": 7,
            "kill_fee_pct": 20,           # of remaining contract value
            "deliverables_on_termination": "completed_work_to_date",
            "escrow_release_on": "termination_confirmed"
        },
        plain_english_summary=(
            "Either party may terminate with 7 days notice. "
            "Buyer pays a 20% kill fee on remaining value. "
            "Supplier delivers all completed work; escrow releases accordingly."
        )
    ),
}
