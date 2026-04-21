# Yeomen Procurement Platform
## A Design Primer for Government-Owned Work Discovery Infrastructure

**Status**: Early-stage design document — for discussion and development
**Context**: This document emerges from a broader research project on AI economic transition policy. The core argument: a yeomen economy (distributed AI-augmented small operators) requires market infrastructure that private platforms won't build because it eliminates the rents they depend on. Government-owned procurement infrastructure is the concrete institutional form of that policy agenda.

---

## The Problem

Professional services work discovery currently flows through private platforms (Upwork, Fiverr, LinkedIn, industry-specific marketplaces) that extract 25–35% effective margin through commissions, algorithmic manipulation, and reputation lock-in. This margin is not payment for genuine coordination value — it is rent extracted from a captive network.

The consequences for a yeomen economy are structural:

- A sole operator with $150k gross revenue keeps ~$105k after platform fees — less than a W-2 employee at equivalent productivity, with no benefits
- Reputation built on a platform is non-portable — switching platforms means starting over
- Buyers and suppliers cannot form direct relationships without paying a "buyout fee"
- Tax compliance is patchy — platforms in low-tax jurisdictions don't share data; thresholds create reporting gaps
- Government procurement ($100B+/yr in federal IT alone) is structurally inaccessible to small operators due to compliance overhead

The result: the Coasian fragmentation of firms into small AI-augmented operators — which AI economics makes structurally natural — gets captured back into platform dependency. Operators are technically independent but economically sharecroppers.

---

## The Proposed Solution

A **government-owned, open-standard procurement platform** that:

1. Charges no transaction margin — coordination is a public good
2. Makes every transaction visible for tax purposes — replacing enforcement with automatic reporting
3. Holds credentials portably — suppliers own their reputation, not the platform
4. Uses open standards — any software can implement the protocol, no lock-in
5. Minimises friction — tender to accepted contract in hours, not weeks

The closest analogy is **DNS**: government-overseen, technically delegated, no profit motive, anyone can build on top. The platform owns the standard and the identity layer; it does not own the market.

---

## Design Principles

### 1. Zero extraction
No commission, no take rate, no subscription fee for core functions. Funded by government as public infrastructure, justified by tax visibility gains alone. The economic case: if the platform recovers even 5% of currently unreported self-employment income, it pays for itself many times over.

### 2. Tax by design
Every accepted tender is a recorded transaction linked to verified identities on both sides. Payment flows through government-visible rails (FedNow or equivalent). Automatic 1099 generation. No thresholds — all transactions reported at the point of contract acceptance, not payment. The platform is the withholding mechanism without withholding tax — it makes income declare itself.

This is enforcement-immune taxation applied to labour income: the transaction is visible because work is being procured, not because a payment cleared a reporting threshold.

### 3. Privacy-preserving credentials
The platform verifies supplier qualifications without storing the underlying relationship data. Key mechanism: **W3C Verifiable Credentials** — cryptographically signed attestations held by the supplier, verified by the platform without the platform needing to see the source data.

Example: "This supplier has been attested to by 12 past clients with high satisfaction ratings" — the attestation is signed by each client and held by the supplier. The platform verifies the signature; it never stores the underlying work details.

Zero-knowledge proofs for sensitive qualifications: "This supplier meets the security clearance requirement" without revealing clearance level, granting authority, or specific clearance holder.

Privacy risks of government ownership are real and must be designed against:
- Supplier capability profiles are sensitive business intelligence
- Bid amounts reveal pricing strategies
- Relationship graphs reveal competitive intelligence

Mitigations: federated architecture (government sets standard, matching can run locally), credential portability (supplier controls what they share), minimum-necessary data retention, FOIA exemptions for commercial procurement data.

### 4. Open standard, not a walled garden
The protocol for tender posting, credential verification, and contract execution is an open standard — any government, cooperative, or private entity can implement it. Multiple compatible platforms can exist. Suppliers register once; credentials work everywhere that implements the standard.

This is the ActivityPub model for procurement: federated, interoperable, no single entity controls the network.

---

## Architecture: Five Layers

### Layer 1: Identity and Credential Infrastructure

**What it does**: Gives every supplier a portable professional identity that travels with them across platforms and across time.

**Components**:
- Government-issued professional DID (Decentralised Identifier) linked to tax ID and relevant licences
- Credential issuance by trusted third parties: professional associations (bar, accounting, design guilds), past clients (signed work attestations), certification bodies, state licensing boards
- Open verification API: any buyer or platform can query credential status without asking the supplier to resubmit documents

**Key design decisions**:
- Supplier holds credentials, not the platform — credentials stored in supplier's own wallet (software or hardware)
- Revocation is possible (for disciplinary actions) without destroying the full credential history
- Credentials are composable — a supplier can share a subset relevant to a specific tender

**Standards**: W3C Verifiable Credentials Data Model 2.0, W3C DID 1.0, Open Badges 3.0

**Institutional anchors needed**: Professional associations must adopt VC issuance. This is the primary adoption bottleneck — not technology, but institutional willingness. Government mandate (e.g., "federal contractors must use portable credential standard by [date]") would accelerate adoption.

---

### Layer 2: Discovery and Matching

**What it does**: Connects buyers with qualified suppliers at near-zero search cost, without algorithmic manipulation.

**For buyers**:
- Post a tender in plain English — AI maps to relevant credential requirements and NAICS codes automatically
- Set qualification thresholds (required credentials, minimum past performance level, geographic constraints)
- System pushes tender to all credentialled suppliers who match — no supplier pays for visibility

**For suppliers**:
- Register capability profile once — described in plain English plus structured credential tags
- Relevant tenders arrive as notifications — no manual monitoring of procurement portals
- AI-assisted proposal drafting that respects format requirements (FAR for federal, equivalent for state/commercial)

**Key design decision — no ranking algorithm**:
Ranking algorithms are where platform capture happens. Instead: buyers see all qualified suppliers who have responded, sorted by credential match score (objective) not by "platform score" (manipulable). Buyers choose. No black box.

**Government procurement integration**:
- Full two-way sync with SAM.gov / beta.SAM.gov
- Automated SAM registration assistance and maintenance for small operators
- Proactive matching to set-aside vehicles (8(a), WOSB, HUBZone, SBIR) based on supplier profile
- Plain-English translation of solicitation requirements

**Privacy consideration**: Tender details visible only to credentialled, matched suppliers — not publicly searchable. Prevents competitive intelligence harvesting by incumbents monitoring what their clients are procuring.

---

### Layer 3: Contract Standards

**What it does**: Reduces the cost of going from "accepted" to "working" from days/weeks to hours.

**Open contract module library**:
Standard terms for every common procurement type, combinable like building blocks:

| Module | Covers |
|---|---|
| Engagement type | Fixed price / time-and-materials / retainer / outcome-based |
| IP ownership | Work-for-hire / licensed / shared / supplier-retained |
| AI use disclosure | AI tools used, human review requirements, training data exclusions |
| Confidentiality | NDA terms, carve-outs, duration |
| Dispute resolution | Binding arbitration by default, venue, governing law |
| Termination | Notice period, kill fee, deliverables on termination |

Buyer selects modules. Supplier confirms or counter-proposes. Both sign digitally. Contract is executed — linked to payment escrow, milestone schedule, and tax reporting.

**Machine-readable format**: SPDX-style structured JSON so contracts can be parsed by payment systems, audit tools, and compliance checkers without human review.

**AI use disclosure as standard**: All contracts include a standard AI-use addendum — what tools were used, what human review occurred, what training data exclusions apply. This becomes the industry norm through procurement infrastructure rather than requiring separate regulation.

**Legislative opportunity**: Federal small business contracting vehicles (SBIR, 8(a)) could mandate this standard contract library, making it the default for all federal small-business work. State equivalents would follow.

---

### Layer 4: Payment and Escrow

**What it does**: Gets money from buyer to supplier fast, automatically, and with full tax reporting.

**Design**:
- Milestone-triggered escrow: buyer deposits at contract acceptance; funds release automatically when milestone conditions are met
- Dispute resolution built in: if supplier claims milestone complete and buyer disputes, neutral arbitration (not platform-decided) with defined SLA
- Real-time payment via FedNow (already live in US) — settlement in seconds, not days
- Automatic 1099-K generation for every transaction, linked to supplier's tax ID
- Lien/retainer mechanics for ongoing engagements

**No float extraction**: Platform holds funds in escrow only for the duration of active dispute. No revenue from interest on held funds. Escrow held in government-backed account, not platform's operating account.

**Cross-border work**: ISO 20022 standard for payment messaging enables interoperability with international payment systems. Cross-border transactions reported to both jurisdictions' tax authorities at time of contract acceptance — not when payment clears.

**Privacy**: Payment amounts are reported to tax authority but not publicly visible. Buyer and supplier see each other's payment details; platform sees aggregate flows but not content.

---

### Layer 5: Governance and Standards Body

**What it does**: Ensures the platform remains neutral, the standard evolves appropriately, and disputes are resolved fairly.

**Not a government agency running the platform day-to-day**. Instead: government sets and enforces the standard; operation is delegated (like ICANN for DNS).

**Governance structure — tripartite**:
- One-third: worker/supplier representatives (professional associations, cooperative federations)
- One-third: buyer representatives (small business associations, government procurement officials, enterprise buyer groups)
- One-third: public interest (government representatives, academic, consumer advocates)

**Responsibilities**:
- Maintain open standard and protocol specifications
- Certify compatible platform implementations
- Adjudicate standard disputes
- Set minimum privacy and security requirements for all implementations
- Publish transparency reports on platform usage (anonymised aggregate data)

**Dispute resolution**:
- Contract disputes: binding arbitration with published precedent database
- Credential disputes: appeals process to issuing body with independent review
- Platform behaviour disputes: complaints to standards body, not to platform operator

---

## The Tax Case in Detail

This deserves its own section because it is both the strongest economic justification and the most underappreciated aspect of the design.

**Current state of self-employment tax compliance**:
- IRS estimates the tax gap (taxes owed but not collected) at ~$600B/yr, with self-employment income a major component
- Platform 1099-K threshold games: until 2022, the threshold was $20,000 AND 200 transactions; the $600 threshold adopted in 2022 (implementation delayed) would capture far more but still only at payment receipt
- International platforms: no obligation to report to IRS; suppliers can structure payments to avoid US tax entirely

**How platform-as-tax-infrastructure changes this**:

Every tender accepted on the platform creates a tax record at the point of contract — before any work is done, before any payment. The buyer's identity (and tax ID) is verified. The supplier's identity (and tax ID) is verified. The contract amount is recorded.

This shifts the tax reporting point from payment (which can be structured, delayed, or routed) to **commitment** (which is the economically meaningful moment when income is earned).

The government doesn't need to audit anyone. The transaction declares itself.

**The enforcement arithmetic**:
- US self-employment income: approximately $1.2T/yr (BLS/IRS estimates)
- Estimated unreported fraction: 25-40% (IRS compliance studies)
- Unreported self-employment income: ~$300-500B/yr
- Marginal tax rate on recovered income: ~25% blended
- Potential additional tax revenue: $75-125B/yr

Platform operating cost (government IT infrastructure at scale): ~$500M-1B/yr.

The platform pays for itself 75-125x over in tax recovery alone, before counting friction reduction, welfare effects for operators, or improved government procurement efficiency.

---

## What This Means for the Yeomen Economy Model

The procurement platform directly affects three parameters in the economic model:

**1. Effective yeomen fraction**: Platform capture currently suppresses the achievable yeomen fraction. At 30% platform take, the effective yeomen ceiling may be 10-15% even if nominal fragmentation is higher. Remove platform extraction and the ceiling rises to 35-60% as modelled.

**2. MPC of yeomen income**: The model assumes yeomen MPC ~78% (labour-like, because it is earned income). If 25-35% of gross income is extracted by platforms, the effective MPC on net income is the same but the absolute income base is smaller — reducing the demand multiplier effect. Remove platform extraction and the full $78 of every $100 earned flows into consumption.

**3. Tax enforcement**: The platform is the enforcement mechanism. Yeomen income becomes as tax-visible as wage income. The enforcement gap that afflicts capital income taxation does not apply — every transaction is recorded at commitment.

**Combined effect**: The procurement platform doesn't just reduce friction. It materially changes the distributional outcomes of the yeomen scenario, potentially closing half the gap between yeomen and public AI scenarios in the model.

---

## Comparison to Existing Systems

| | SAM.gov | Upwork | Proposed Platform |
|---|---|---|---|
| **Ownership** | Government | Private (VC-backed) | Government / standards body |
| **Take rate** | 0% | 10-35% effective | 0% |
| **Accessible to small operators** | No (compliance overhead) | Yes | Yes (by design) |
| **Portable reputation** | No | No (locked in) | Yes (W3C VC) |
| **Tax reporting** | Partial | Partial | Full, automatic |
| **Standard contracts** | No | Platform ToS | Open modular library |
| **Payment speed** | Net-60 to net-90 | 5-10 days | Real-time (FedNow) |
| **Privacy** | Low (FOIA exposed) | Low (platform data) | High (ZK credentials) |
| **Open standard** | No | No | Yes |
| **International** | US only | Global but extractive | Open standard, multi-jurisdiction |

---

## Nearest Existing Analogues

**DNS / ICANN**: Government-overseen root; delegated operation; open protocol; anyone can build on top; no extraction from each lookup. The procurement platform should be designed to this model exactly.

**FedNow**: Government-owned real-time payment rail. No private intermediary extracting float. Available to all financial institutions. The payment layer of the procurement platform should run on FedNow.

**SWIFT (what to avoid)**: Centralised, government-adjacent but privately controlled, has become a geopolitical instrument. Shows the risks of insufficient governance architecture.

**Lloyd's of London**: Historically, separated the information infrastructure (Lloyd's Register, the ship-quality publication) from the transactional marketplace (Lloyd's of London, the insurance market). This separation — commons information layer, competitive transaction layer — is the right architectural model.

**Open Badges / W3C VC**: Already-existing open credential standards. The identity layer of the procurement platform should implement these, not create a proprietary alternative.

---

## Open Questions for Further Development

1. **Adoption strategy**: How do you get critical mass on both sides? Government mandating use for federal small-business contracts would bootstrap supply. But buyer adoption in private markets requires either mandate or demonstrated superiority.

2. **International coordination**: Should this be a US government platform or an open standard that multiple governments implement? Open standard is more robust but requires international coordination. G7/G20 digital economy working groups are the institutional home for this conversation.

3. **Relationship to existing platforms**: Coexistence or displacement? Portability mandates (EU DMA-style, requiring platforms to export reputation data) would allow existing platforms to continue operating while removing the lock-in that makes them extractive.

4. **Security clearance and sensitive procurement**: How does the platform handle classified procurement where even the existence of the tender is sensitive? Likely a parallel system with different privacy architecture rather than integration.

5. **Dispute resolution at scale**: Binding arbitration works for individual disputes but who funds and staffs the arbitration body? This needs an institutional design answer.

6. **AI-assisted proposal quality**: If the platform helps small operators write better proposals, does this advantage incumbents who can game AI tools? Or does it level the playing field? Probably the latter — large contractors already have proposal writing teams.

7. **Credential bootstrap problem**: W3C VCs are only valuable if trusted issuers adopt them. What's the minimum viable institutional set to make the credential layer work from day one? Hypothesis: federal contractor registration (already mandatory via SAM/UEI) + one major professional association per domain would be sufficient.

---

## Suggested Next Steps

**For a Claude Code instance picking this up:**

1. **Spec the data model**: What does a tender look like as structured data? What does a credential look like? What does a contract look like? Start with JSON schemas for each.

2. **Prototype the credential layer**: Implement W3C VC issuance and verification in Python. A small demo where a "professional association" issues a credential, a "supplier" holds it, and a "buyer" verifies it — end to end.

3. **Map the federal procurement integration**: What APIs does SAM.gov expose? What data can be pulled programmatically today? What's the gap between current state and "AI-assisted matching to relevant tenders"?

4. **Design the contract module library**: Draft 5-10 standard contract modules in both plain English and machine-readable JSON-LD. Start with the simplest case: fixed-price project with defined deliverable, standard IP terms, arbitration clause.

5. **Model the economic effects**: In the SFC model (`model_sfc.py`), add a `platform_capture` parameter (0.0 = no platform, 1.0 = full platform extraction at 30%). Show how removing platform capture affects effective yeomen income, MPC, and the distributional outcomes at t+10.

---

*This document is part of a broader project on AI economic transition policy. See `policy_brief.md` for the macroeconomic model context and `MODELS.md` for the modelling framework. The procurement platform is the institutional complement to the yeomen scenario in the policy brief — the market infrastructure without which distributed AI-augmented work remains platform-dependent.*
