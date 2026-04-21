"""
Yeomen Procurement Platform — End-to-End Demo
==============================================
Toy prototype showing the full flow:

  1. Professional association issues a VerifiableCredential to a supplier
  2. Supplier registers as an A2A agent (SupplierAgentCard)
  3. Buyer posts a Tender (A2A Task)
  4. Platform matches + pushes tender to qualified suppliers (private, push-based)
  5. Supplier submits a Bid with credential presentations
  6. Buyer selects winning bid
  7. Contract is assembled from standard modules, signed, tax record created
  8. Milestones tracked; FedNow escrow simulated

Run: python3 platform_demo.py
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from platform_schemas import (
    VerifiableCredential, SupplierAgentCard, BuyerAgentCard,
    Tender, TenderRequirements, Bid, CredentialPresentation,
    Contract, Milestone, ContractModule,
    EngagementType, TenderStatus, ContractStatus, MilestoneStatus,
    STANDARD_MODULES
)


# ---------------------------------------------------------------------------
# Toy Platform: in-memory registry + matching engine
# ---------------------------------------------------------------------------

class PlatformRegistry:
    """
    In-memory stand-in for the government platform's registry.

    In production: federated — each jurisdiction runs its own node,
    synced via the open standard protocol (like ActivityPub federation).
    The platform holds no VC content, only hashes and capability tags.
    """
    def __init__(self):
        self.suppliers: dict[str, SupplierAgentCard] = {}
        self.buyers: dict[str, BuyerAgentCard] = {}
        self.tenders: dict[str, Tender] = {}
        self.bids: dict[str, list[Bid]] = {}        # tender_id → [Bid]
        self.contracts: dict[str, Contract] = {}
        self.tax_ledger: list[dict] = []            # append-only IRS records

    def register_supplier(self, agent: SupplierAgentCard):
        self.suppliers[agent.did] = agent
        print(f"  [REGISTRY] Supplier registered: {agent.display_name} ({agent.did})")

    def register_buyer(self, agent: BuyerAgentCard):
        self.buyers[agent.did] = agent
        print(f"  [REGISTRY] Buyer registered: {agent.display_name} ({agent.did})")

    def post_tender(self, tender: Tender) -> list[str]:
        """
        Buyer posts a tender. Platform matches and returns list of matched
        supplier DIDs. Suppliers are notified (not the tender posted publicly).

        Off-market consideration: matched supplier DIDs are not revealed to
        the buyer until bids are submitted. This prevents buyer from taking
        the shortlist and transacting off-platform — they don't know who else
        was contacted.
        """
        self.tenders[tender.id] = tender
        matched = self._match_suppliers(tender)
        tender.status = TenderStatus.MATCHED
        print(f"  [PLATFORM] Tender '{tender.title}' matched to {len(matched)} suppliers (private push)")
        # In production: platform sends A2A task/send to each matched supplier's service_endpoint
        return matched

    def _match_suppliers(self, tender: Tender) -> list[str]:
        """
        Objective matching: credential tags + NAICS codes.
        No ranking algorithm — all qualified suppliers get the tender.
        Buyer sees all responses; black box eliminated.
        """
        req = tender.requirements
        if not req:
            return list(self.suppliers.keys())

        matched = []
        for did, supplier in self.suppliers.items():
            # NAICS match
            if req.required_naics and not any(n in supplier.naics_codes for n in req.required_naics):
                continue
            # Set-aside eligibility
            if req.set_aside and req.set_aside not in supplier.set_aside_eligibility:
                continue
            matched.append(did)
        return matched

    def submit_bid(self, bid: Bid):
        if bid.tender_id not in self.bids:
            self.bids[bid.tender_id] = []
        self.bids[bid.tender_id].append(bid)
        print(f"  [PLATFORM] Bid received from {bid.supplier_did}: ${bid.bid_amount_usd:,.0f}")

    def verify_credentials(self, bid: Bid, supplier: SupplierAgentCard) -> bool:
        """
        Platform verifies credential presentations against supplier's registered hashes.
        ZK-style: we check the hash matches; we don't store or examine VC content.

        Privacy: the platform learns ONLY that the credential is valid.
        It does not learn client names, project details, or payment amounts.
        """
        registered_hashes = set(supplier.credential_hashes)
        for pres in bid.credential_presentations:
            if pres.credential_hash not in registered_hashes:
                print(f"  [VERIFY] FAILED: credential hash {pres.credential_hash} not in registry")
                return False
        print(f"  [VERIFY] All {len(bid.credential_presentations)} credentials verified for {supplier.display_name}")
        return True

    def award_contract(self, tender_id: str, winning_bid_id: str, buyer_did: str) -> Contract:
        """
        Buyer selects winning bid. Contract assembled from standard modules.
        TAX RECORD CREATED HERE — at contract acceptance, before any payment.
        This is the enforcement moment: income declared at commitment, not receipt.
        """
        tender = self.tenders[tender_id]
        winning_bid = next(b for b in self.bids[tender_id] if b.id == winning_bid_id)

        # Build milestones from tender spec
        milestones = []
        if tender.milestones:
            for ms_spec in tender.milestones:
                milestones.append(Milestone(
                    description=ms_spec["description"],
                    due_date=ms_spec["due_date"],
                    amount_usd=ms_spec["amount_usd"],
                    escrow_account=f"fednow:escrow:{uuid.uuid4().hex[:8]}"
                ))
        else:
            # Single milestone for simple fixed-price
            milestones.append(Milestone(
                description="Project completion",
                due_date=(datetime.now(timezone.utc) + timedelta(days=winning_bid.proposed_timeline_days)).isoformat(),
                amount_usd=winning_bid.bid_amount_usd,
                escrow_account=f"fednow:escrow:{uuid.uuid4().hex[:8]}"
            ))

        # Assemble standard modules
        modules = [
            STANDARD_MODULES["fixed_price_engagement"] if tender.engagement_type == EngagementType.FIXED_PRICE
            else STANDARD_MODULES["fixed_price_engagement"],  # extend for other types
            STANDARD_MODULES["work_for_hire_ip"],
            STANDARD_MODULES["ai_use_standard"],
            STANDARD_MODULES["standard_arbitration"],
            STANDARD_MODULES["standard_termination"],
        ]

        contract = Contract(
            tender_id=tender_id,
            bid_id=winning_bid.id,
            buyer_did=buyer_did,
            supplier_did=winning_bid.supplier_did,
            total_value_usd=winning_bid.bid_amount_usd,
            milestones=milestones,
            modules=modules,
        )

        contract.execute(buyer_did, winning_bid.supplier_did)
        self.contracts[contract.id] = contract
        tender.status = TenderStatus.AWARDED

        # Append-only tax record — IRS gets this at execution, not payment
        tax_record = {
            "irs_record_id": contract.irs_record_id,
            "tax_year": contract.tax_year,
            "reporting_jurisdiction": contract.reporting_jurisdiction,
            "buyer_tax_id_hash": self.buyers[buyer_did].tax_id_hash,
            "supplier_tax_id_hash": self.suppliers[winning_bid.supplier_did].tax_id_hash,
            "contract_value_usd": contract.total_value_usd,
            "declared_at": contract.executed_at,
            "auto_1099_scheduled": True,
        }
        self.tax_ledger.append(tax_record)
        print(f"  [TAX]      IRS record created: {contract.irs_record_id} — ${contract.total_value_usd:,.0f} declared")

        return contract

    def release_milestone(self, contract_id: str, milestone_id: str):
        """Simulate FedNow instant payment release on milestone approval."""
        contract = self.contracts[contract_id]
        ms = next(m for m in contract.milestones if m.id == milestone_id)
        ms.status = MilestoneStatus.RELEASED
        print(f"  [FEDNOW]   ${ms.amount_usd:,.0f} released via FedNow escrow {ms.escrow_account}")


# ---------------------------------------------------------------------------
# Demo flow
# ---------------------------------------------------------------------------

def run_demo():
    print("\n" + "="*70)
    print("YEOMEN PROCUREMENT PLATFORM — TOY PROTOTYPE")
    print("="*70)

    platform = PlatformRegistry()

    # ------------------------------------------------------------------
    # Step 1: Professional association issues VCs to a supplier
    # ------------------------------------------------------------------
    print("\n--- Step 1: Credential Issuance ---")
    print("  American Institute of Data Professionals issues VC to Maria Chen")

    vc_past_performance = VerifiableCredential(
        id=f"did:example:cred:{uuid.uuid4().hex[:8]}",
        type=["VerifiableCredential", "PastPerformanceCredential"],
        issuer_did="did:example:org:aidp",
        issuer_name="American Institute of Data Professionals",
        subject_did="did:gov:tax:supplier-maria-chen",
        issued_at=datetime.now(timezone.utc).isoformat(),
        expiry=None,
        claims={
            "completed_projects": 23,
            "avg_client_rating": 4.9,
            "domain_tags": ["data-analysis", "python", "llm-fine-tuning"],
            "total_contract_value_tier": "100k-500k",  # range, not exact — privacy
        }
    )

    vc_naics_cert = VerifiableCredential(
        id=f"did:example:cred:{uuid.uuid4().hex[:8]}",
        type=["VerifiableCredential", "NAICSCertification"],
        issuer_did="did:example:org:sba",
        issuer_name="Small Business Administration",
        subject_did="did:gov:tax:supplier-maria-chen",
        issued_at=datetime.now(timezone.utc).isoformat(),
        expiry=None,
        claims={"naics_codes": ["541511", "541512"], "wosb_eligible": True}
    )

    print(f"  VC 1 hash: {vc_past_performance.credential_hash}")
    print(f"  VC 2 hash: {vc_naics_cert.credential_hash}")
    print("  [Maria holds these VCs in her wallet — platform stores only hashes]")

    # ------------------------------------------------------------------
    # Step 2: Supplier registers AgentCard
    # ------------------------------------------------------------------
    print("\n--- Step 2: Supplier Registration ---")

    maria = SupplierAgentCard(
        did="did:gov:tax:supplier-maria-chen",
        display_name="Maria Chen Data Services LLC",
        entity_type="llc",
        tax_id_hash="sha256:abc123...encrypted",  # real: SHA-256(EIN), stored encrypted
        capabilities=["python", "data-analysis", "llm-fine-tuning", "sql", "tableau"],
        naics_codes=["541511", "541512"],
        credential_hashes=[vc_past_performance.credential_hash, vc_naics_cert.credential_hash],
        service_endpoint="https://maria-agent.example.com/a2a",
        auth_scheme="oauth2",
        set_aside_eligibility=["wosb"],
        is_sam_registered=True,
    )
    platform.register_supplier(maria)

    # Second supplier for contrast
    bob = SupplierAgentCard(
        did="did:gov:tax:supplier-bob-patel",
        display_name="Bob Patel Analytics",
        entity_type="sole_operator",
        tax_id_hash="sha256:def456...encrypted",
        capabilities=["python", "data-analysis", "statistics"],
        naics_codes=["541512"],
        credential_hashes=["fakehash001", "fakehash002"],
        service_endpoint="https://bob-agent.example.com/a2a",
        auth_scheme="oauth2",
        set_aside_eligibility=[],
    )
    platform.register_supplier(bob)

    # ------------------------------------------------------------------
    # Step 3: Buyer registers and posts a Tender
    # ------------------------------------------------------------------
    print("\n--- Step 3: Buyer Posts Tender ---")

    doe_agency = BuyerAgentCard(
        did="did:gov:agency:doe-office-of-science",
        display_name="DOE Office of Science",
        entity_type="federal_agency",
        tax_id_hash="sha256:gov:doe:oos",
        service_endpoint="https://doe-procurement.gov/a2a",
        auth_scheme="oauth2",
        set_aside_preferences=["wosb", "sdvosb"],
    )
    platform.register_buyer(doe_agency)

    tender = Tender(
        buyer_did=doe_agency.did,
        title="AI-assisted analysis of energy grid sensor data",
        description_plain=(
            "We need a data analyst to clean, analyse, and summarise 18 months "
            "of smart grid sensor readings. Output: cleaned dataset + 10-page "
            "summary report with visualisations. AI tools permitted with disclosure."
        ),
        requirements=TenderRequirements(
            required_naics=["541511", "541512"],
            required_credentials=["PastPerformanceCredential"],
            min_past_performance_count=5,
            set_aside="wosb",
            geographic_constraint="US_only",
        ),
        engagement_type=EngagementType.FIXED_PRICE,
        budget_min_usd=15_000,
        budget_max_usd=35_000,
        response_deadline=(datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        start_date=(datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
        estimated_duration_days=30,
        milestones=[
            {"description": "Cleaned dataset delivered", "due_date": (datetime.now(timezone.utc) + timedelta(days=21)).isoformat(), "amount_usd": 12_000},
            {"description": "Final report delivered", "due_date": (datetime.now(timezone.utc) + timedelta(days=44)).isoformat(), "amount_usd": 13_000},
        ]
    )

    matched_dids = platform.post_tender(tender)
    print(f"  Matched suppliers: {matched_dids}")
    print("  [Only matched suppliers see this tender — no public listing]")

    # ------------------------------------------------------------------
    # Step 4: Supplier submits Bid with credential presentations
    # ------------------------------------------------------------------
    print("\n--- Step 4: Supplier Submits Bid ---")

    # Maria presents a subset of her credentials (selective disclosure)
    credential_pres = CredentialPresentation(
        credential_hash=vc_past_performance.credential_hash,
        credential_type="PastPerformanceCredential",
        issuer_did="did:example:org:aidp",
        disclosed_claims={
            # She chooses what to reveal — not the full VC
            "completed_projects": 23,
            "avg_client_rating": 4.9,
            "domain_tags": ["data-analysis", "python"],
            # She does NOT disclose: client names, contract amounts, project details
        }
    )

    maria_bid = Bid(
        tender_id=tender.id,
        supplier_did=maria.did,
        bid_amount_usd=24_500,
        proposed_timeline_days=28,
        approach_summary=(
            "I will use Python (pandas, matplotlib) with Claude API for anomaly "
            "detection. All AI outputs will be human-reviewed. Deliverables include "
            "cleaned Parquet dataset + Jupyter notebook + PDF report."
        ),
        credential_presentations=[credential_pres],
        ai_tools_used=["Claude claude-sonnet-4-6", "pandas-ai"],
    )
    platform.submit_bid(maria_bid)

    # Verify credentials before presenting to buyer
    verified = platform.verify_credentials(maria_bid, maria)

    # ------------------------------------------------------------------
    # Step 5: Buyer awards contract
    # ------------------------------------------------------------------
    print("\n--- Step 5: Contract Award ---")

    contract = platform.award_contract(
        tender_id=tender.id,
        winning_bid_id=maria_bid.id,
        buyer_did=doe_agency.did,
    )

    print(f"  Contract ID:    {contract.id}")
    print(f"  Value:          ${contract.total_value_usd:,.0f}")
    print(f"  Status:         {contract.status}")
    print(f"  IRS Record:     {contract.irs_record_id} [created NOW, before any payment]")
    print(f"  Modules:        {[m.module_type for m in contract.modules]}")

    # ------------------------------------------------------------------
    # Step 6: Milestone completion + FedNow payment
    # ------------------------------------------------------------------
    print("\n--- Step 6: Milestone Completion ---")

    ms1 = contract.milestones[0]
    ms1.status = MilestoneStatus.APPROVED
    print(f"  Buyer approved: '{ms1.description}'")
    platform.release_milestone(contract.id, ms1.id)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n--- Tax Ledger (IRS view) ---")
    for rec in platform.tax_ledger:
        print(f"  {json.dumps(rec, indent=4)}")

    print("\n--- Platform Economics ---")
    print(f"  Platform take rate:         0%  (vs ~30% Upwork)")
    print(f"  Maria's gross:              ${contract.total_value_usd:,.0f}")
    print(f"  Maria's net (after platform): ${contract.total_value_usd:,.0f}  (same — no extraction)")
    print(f"  Upwork equivalent net:      ${contract.total_value_usd * 0.70:,.0f}  (-30%)")
    print(f"  Extra income to yeomen:     ${contract.total_value_usd * 0.30:,.0f}")

    print("\n--- Design Question Responses (embedded in architecture) ---")
    print("""
  OFF-MARKET PREVENTION:
    This platform cannot ban off-market transactions — no system can.
    The design makes on-platform irrational to avoid:
      • Zero fee (vs 30% private platform)
      • Tax safe harbour: on-platform = auto-1099, no audit exposure
      • Reputation non-portable off-platform (attestations are on-platform)
      • FedNow instant payment only via platform escrow
      • Federal mandate for government work (SAM.gov precedent)
    Regulatory lever: "platform-verified" flag on 1099s — off-platform
    income is not illegal, but it's more likely to trigger audit.
    Analogy: card payments didn't ban cash in B2B, they just made
    cash irrational for any party that cares about auditability.

  PRIVACY:
    • Platform stores credential HASHES only — not VC content
    • Bid amounts visible to buyer + platform (tax) only
    • Matched supplier list hidden from buyer until bids arrive
    • Federated architecture: matching can run locally (no central store)
    • FOIA exemption needed for commercial procurement data
    • ZK proofs for clearance/sensitive qualifications

  PRIVATE SECTOR IMPOSITION:
    The mandate is minimal and limited to:
      1. Federal contracts: must use open contract format (like SAM/UEI today)
      2. Platforms above threshold: must export reputation data on request
         (EU DMA-style portability, not a ban on operating)
    Everything else is opt-in. Private platforms can implement the open
    standard — they lose lock-in but gain interoperability. Upwork could
    become a UI layer on top of this rail, competing on UX not network effects.
    The DNS analogy: DNS doesn't prevent private intranets. It just makes
    the public internet work without a single private gatekeeper.
    """)

    print("="*70)
    print("Demo complete.")
    print("="*70 + "\n")

    return platform, contract


if __name__ == "__main__":
    platform, contract = run_demo()
