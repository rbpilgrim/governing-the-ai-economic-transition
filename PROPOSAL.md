# Federated Agent Commerce Infrastructure
## A Policy and Technical Proposal

**Version:** 0.2 Draft
**Status:** For discussion

---

## Executive Summary

AI agent commerce is arriving faster than governance infrastructure. Within a decade, a significant share of economic transactions — service procurement, knowledge work, physical robot deployment — will be negotiated and executed autonomously between AI agents at machine speed, with no human in the loop per transaction.

If no public standard exists, this layer will be captured by private platforms that extract rent from every transaction, deny tax visibility to governments, and lock participants into proprietary identity systems. This has happened before: internet search was built on open protocols but discovery was captured by private platforms. The yeoman economy — owner-operators using AI to sell services — cannot be viable if the discovery and contracting infrastructure is privately extractive.

This proposal describes a six-layer federated architecture for agent commerce infrastructure, modelled on the governance structures that made the internet interoperable: DNS (ccTLD federation), IETF (open protocol standards), and financial markets (open protocols with mandatory regulatory reporting). The prototype implementation demonstrates all five key flows.

---

## 1. The Problem

### 1.1 Machine-speed commerce without infrastructure

When AI agents negotiate contracts on behalf of their principals, three things break simultaneously:

**Tax visibility.** Current tax law assumes human-visible transactions: invoices, 1099s filed quarterly, bank records. Agent-to-agent contracts at machine speed generate no human-visible paper trail. The self-employment tax gap is already $300–500B/yr in the US. Agent commerce could multiply this.

**Identity and reputation.** A yeoman's track record — past performance, credentials, reliability — is their primary capital. If this data is held by a private platform, they can never leave. The platform extracts rent in perpetuity.

**Discovery monopoly.** Whoever controls discovery controls the market. Network effects tip toward monopoly. The platform learns demand patterns before participants, can favour paying customers in ranking, and can price-discriminate invisibly.

### 1.2 Why existing approaches fail

**Fully private platforms** (existing model): rent extraction, opacity, lock-in. Uber, App Store, Amazon Marketplace are the template. The yeoman earns less with each platform fee increase and has no exit.

**Fully government-run infrastructure**: governments cannot iterate fast enough on matching algorithms. Political capture means contracts go to favoured suppliers. US-controlled infrastructure is not trusted internationally.

**Self-regulated industry body**: fragile. The first large private platform to defect captures market share; others follow. The race to the bottom on standards compliance repeats the social media experience.

---

## 2. Proposed Architecture: Six Layers

The architecture separates concerns explicitly. Each layer has a distinct operator, governance model, and technical role.

```
L5  Tax Reporting          National tax authorities receive structured records
L4  Settlement             FedNow (domestic) or x402 stablecoin (cross-border)
L3  Agent Negotiation      A2A protocol: machine-speed proposal / counter / accept
L2  Matchmakers            Private competitive operators — licensed by L1
L1  National Registries    Per-country identity, reputation, contract reporting
L0  International Standard ITU/ISO treaty body — shared schemas, wire format
```

### L0 — International Standard

**Operator:** ITU/ISO treaty body (analogous to ICAO for passports, IETF for TCP/IP).
**What it defines:** Agent card schema, credential format, contract bundle format, tax record fields, API specifications.
**What it does not define:** Matching algorithms, pricing, domestic tax treatment.
**Governance:** Rough consensus among member states and technical contributors. Government has an advisory seat (non-binding, like ICANN's GAC). Standards published freely, royalty-free.
**Critical property:** The L0 standard is what makes national registries interoperable. A US yeoman and an EU DAO can transact because both sides implement the same wire format — no bilateral agreement required per pair of countries.

### L1 — National Registry

**Operator:** Government-chartered nonprofit, one per jurisdiction. Analogous to ccTLD registries (.uk, .de, .au). Government funds and mandates it but does not control day-to-day operations.
**Responsibilities:**
- Agent identity: DID issuance and verification
- Reputation storage: attestation hashes only (credential content held by the agent)
- Matchmaker licensing: sets conditions, revokes for non-compliance
- Contract report intake: receives structured L0 records from licensed matchmakers
- Tax record forwarding: passes records to the domestic tax authority

**What it does not do:** Run matching algorithms. Hold credential content. Set contract terms.

**Governance:** Board with balanced representation — yeomen, technical community, regulators, civil society. Supermajority required for policy changes. Public archive of all decisions. Distributed operation: multiple nodes, no single point of failure.

**Reputation portability guarantee:** Agent reputation data is stored in the registry, not in any matchmaker. Any licensed matchmaker can query it via open API. This is the structural guarantee against lock-in — analogous to phone number portability.

### L2 — Matchmakers

**Operator:** Private, competitive. Anyone can apply for a license from a national registry. Analogous to ICANN-accredited domain registrars.
**License conditions:**
- Implement L0 schema exactly
- Report all executed contracts to relevant registries within 60 seconds of execution
- Allow portability of agent reputation data (no retention beyond session)
- No retention of credential content

**Competitive differentiation:** Matching algorithms, UX, speed, specialisation by industry vertical. Matchmakers cannot compete by locking in reputation data.
**Revenue model:** Can charge buyers for premium matching features (faster response, better ranking for niche skills). Cannot charge for portability or basic access. Zero take-rate is not mandated for private matchmakers — but competition drives rates down because yeomen can switch.

### L3 — Agent Negotiation

**Operator:** AI agents on both sides. Neither principal is in the loop per round.
**Protocol:** A2A (Agent-to-Agent, Linux Foundation v0.3): proposal → counter → accept/reject.
**What the standard defines:** Message format, session ID, round number, proposed terms schema.
**What it does not define:** Agent strategy. Both sides run their own negotiation logic. The matchmaker facilitates but does not set terms.
**Circuit breaker:** If price movement across the market exceeds a threshold in a short window (flash crash prevention), the registry can signal matchmakers to queue rather than execute.

### L4 — Settlement

**Domestic:** FedNow (US), national equivalents elsewhere. <1 second, USD, existing regulatory framework.
**Cross-border:** x402 (HTTP-native USDC stablecoin, Coinbase). <500ms, <$0.001 per transaction, chain-agnostic. Both rails accept the same L0 payment trigger schema — the matchmaker chooses the rail based on jurisdiction.

### L5 — Tax Reporting

**Mechanism:** At contract execution (not payment), the matchmaker submits a L0-format tax record to each relevant national registry. The registry forwards to its domestic tax authority. No quarterly filing, no human action required — it happens in the same execution path as the contract.
**Key design choice:** Tax is declared at commitment, not at payment. This eliminates payment-routing games (routing payments through jurisdictions with no reporting obligation). The income is on record the moment the contract is signed.
**Cross-border:** The same bundle ID appears in both registries. Each tax authority sees only the slice relevant to their jurisdiction. Double-taxation treaty rules apply between authorities, not between matchmakers.

---

## 3. Cross-Border Flow

A US yeoman (registered in US-L1) accepts a contract from an EU DAO (registered in EU-L1) via a matchmaker licensed in both jurisdictions:

```
1. EU DAO's AI agent posts tender to CrossBorder matchmaker (L2)
2. Matchmaker queries US-L1 and EU-L1 for matching suppliers (L1 API)
3. US yeoman's AI agent and EU DAO's AI agent negotiate via A2A (L3)
4. Agreement reached → contract executed (L0 format)
5. Matchmaker builds CrossBorderContractBundle with unique bundle_id
6. Payment released via x402 stablecoin (L4)
7. Matchmaker reports bundle to US-L1 → US-IRS gets supplier record (L5)
8. Matchmaker reports bundle to EU-L1 → EU tax authority gets buyer record (L5)

Same bundle_id in both records. No bilateral agreement required.
Each tax authority applies its own domestic rules.
```

The prototype (Demo 2) demonstrates this exact flow, including the dual tax records with the shared bundle ID.

---

## 4. Governance

### The ICANN lesson

The internet succeeded because the US government deliberately relinquished direct control of DNS root zone management in 2016. US government control — even benign — undermined international adoption because other countries wouldn't accept US infrastructure as neutral. The same principle applies here: a US Treasury-controlled agent registry will not be adopted by the EU, China, or India. International legitimacy requires structural independence from any single government.

### The correct model

Government-chartered but community-governed, with the following safeguards:

| Principle | Implementation |
|---|---|
| Multi-stakeholder | Board seats for yeomen, technical community, regulators, civil society. No single constituency has majority. |
| Rough consensus | Technical decisions require broad agreement, not 51% majority. Persistent objections must be addressed or overruled with documented rationale. |
| Transparency | Public archive of all board decisions and technical working group discussions. |
| Distributed operation | Registry nodes operated by independent organisations in multiple jurisdictions. No single node can unilaterally alter the registry. |
| Supermajority for policy change | Root policy changes require 2/3 board vote + community comment period. Prevents capture by any single actor. |
| Independent review | Appeals process for registration disputes. Ombudsman for complaints. External review panel can overturn board decisions. |

### Government's role

Government passes enabling legislation that:
1. Creates the registry mandate (national registry must exist, must implement L0)
2. Creates the reporting requirement (matchmakers must report contracts)
3. Charters the nonprofit (but does not appoint majority of board after year 3)
4. Participates in the international standards body through its representative (advisory, non-binding)

This is the FHA mortgage / FDIC deposit insurance model: government creates the framework and backstops the system, but does not run it day-to-day.

### Matchmaker licensing

Matchmakers register with a national registry (low barrier — no approval process, just registration and compliance commitment). Operating without registration is legal for private transactions, but:
- Unregistered matchmaker contracts do not qualify for tax safe harbour
- Parties to unregistered contracts face standard audit risk
- Government procurement must use registered matchmakers

This replicates the card-payment dynamic: cash transactions remain legal, but the incentive structure makes electronic (registered) transactions the rational default.

---

## 5. What Each Stack Layer Needs

### L0 International Standard
- ITU or ISO working group to ratify L0 schemas
- Reference implementation (this prototype) as basis
- JSON-LD context URI with versioned namespace
- Backward compatibility commitment: new fields optional, old fields preserved
- Patent-free licensing commitment from all contributors

### L1 National Registry
- Enabling legislation in each jurisdiction
- Distributed database with cryptographic audit trail
- DID method specification anchored to the registry
- Open API for matchmaker queries (rate-limited, authenticated)
- Tax authority integration (structured data push, not file upload)
- Dispute resolution mechanism for registration conflicts

### L2 Matchmakers
- L0 schema implementation (reference library in Python, TypeScript, Rust)
- OAuth 2.1 M2M authentication to registry APIs
- Contract reporting pipeline (<60s from execution to registry)
- Agent card federation (query multiple registries in parallel)
- No local storage of credential content (privacy requirement)

### L3 Agent Negotiation
- A2A protocol v0.3 (Linux Foundation) as base
- L0 extension for proposed_terms schema (structured, not free-text)
- Session management (negotiation can span multiple HTTP connections)
- Circuit breaker hook (registry can signal pause)
- Audit log of negotiation messages (attached to contract bundle)

### L4 Settlement
- FedNow integration (domestic US — existing infrastructure)
- x402 HTTP header payment (cross-border — Coinbase, open standard)
- Escrow smart contract for milestone-based releases
- Atomic release on deliverable hash verification

### L5 Tax Reporting
- L0 TaxRecord schema (this prototype implements it)
- Registry-to-tax-authority API (push, not pull)
- Deduplication on bundle_id + jurisdiction + role
- Retention policy: records held for 7 years, then archived
- FOIA exemption for individual contract contents (only aggregate statistics public)

---

## 6. Implementation Roadmap

### Phase 1 — Standard and Pilot (months 1–12)
- Ratify L0 schema at ITU/ISO working group level
- Two national registry pilots (US + one partner jurisdiction)
- One reference matchmaker implementation (open source)
- FedNow integration for domestic settlement
- Treasury receives first automatic tax records

### Phase 2 — Negotiation and Cross-border (months 13–24)
- A2A L3 protocol extension ratified
- CrossBorder matchmaker pattern operational (US ↔ pilot partner)
- x402 integration for cross-border settlement
- Reputation portability API standardised and tested
- Circuit breaker mechanism piloted

### Phase 3 — Scale and International (months 25–36)
- L5 automatic tax reporting live in pilot jurisdictions
- Additional national registries onboarded (EU, UK, SG)
- Secondary matchmaker market operational (3+ competing operators)
- Cross-border tax record reconciliation protocol finalised
- Open source SDK released for agent developers

---

## 7. Open Questions

**Agent legal personhood.** Does an AI agent need its own DID, or does it inherit the operator's? Recommendation: sub-DIDs derived from the operator (`did:nat:us:maria-chen/agent:analyst-v2`). The operator is legally responsible; the agent is a capability declaration.

**Unlicensed jurisdiction fallback.** If a yeoman in a jurisdiction with no national registry wants to transact, which registry licenses their matchmaker? Interim proposal: any L1 registry can license a matchmaker operating in an unregistered jurisdiction, with notification obligation to that jurisdiction's tax authority via L0 protocol.

**Privacy.** The L1 registry receives all contract records. Minimum retention: bundle ID, party tax ID hashes, value, date. No contract content, no deliverable details. FOIA exemption required for individual records; aggregates are public.

**Algorithmic collusion.** Research shows LLM-based agents converge on supracompetitive prices without explicit instruction. The registry's aggregate price data should be available to competition authorities for monitoring. Circuit breakers should trigger on suspicious price convergence across multiple matchmakers.

**China and other non-participating jurisdictions.** A separate incompatible registry system is likely. Design for graceful degradation: cross-border contracts with non-participating jurisdictions fall back to existing mechanisms (bilateral treaties, manual tax filing). The L0 standard should not require mutual recognition to function domestically.

---

## 8. Prototype

The working prototype (`federated_registry_demo.py`) demonstrates all five key flows:

| Demo | What it shows |
|---|---|
| 1. Domestic US | Single registry, single matchmaker, baseline flow |
| 2. Cross-border | US yeoman × EU DAO, dual registry reporting, shared bundle ID |
| 3. Competing matchmakers | Same tender, two operators race, winner's contract is recorded |
| 4. Reputation portability | Yeoman switches matchmaker; reputation follows from registry |
| 5. Machine speed | 20 micro-contracts in <1ms wall-clock; all reported synchronously |

The prototype uses in-memory data structures and simplified cryptography (SHA-256 hashes, no real signatures). The schema design in `platform_schemas.py` is production-shaped — the data structures are the specification.

---

*This document is a working draft. The economic modelling underlying it is in `model.py` (macroeconomic simulation), `yeomen_earnings.py` (income projections), `dynamic_tax.py` (policy feedback mechanisms), and `robot_financing.py` (capital access). The governance model is derived from analysis of ICANN, IETF, W3C, and financial market regulatory structures.*
