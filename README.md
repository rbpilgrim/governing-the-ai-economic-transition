# AI Economic Transition Model

A parametric economic model of the transition from a human-labour economy to one
dominated by AI and robotics. The goal is not to tell a story but to make
assumptions explicit and show what the numbers imply across a range of plausible
futures.

**Base economy:** US-like ($28T nominal GDP, 160M workers, 2025 baseline)
**Horizon:** 2025–2060 (35 years)
**Language:** Python 3.11+

---

## What It Models

The model tracks eight interconnected things through time:

1. **Output** — real vs. nominal GDP as automation displaces labour and deflates prices
2. **Labour displacement** — how many workers lose income, and how fast
3. **Income distribution** — the shifting split between labour, yeomen, and concentrated capital income
4. **Government finances** — tax revenue, existing obligations, and the surplus available for redistribution
5. **Effective welfare** — UBI per displaced person *plus* the subsistence buffer from home production
6. **Human economy wages** — income for workers in irreducibly human occupations (derived from consumption flows)
7. **Capital returns** — by asset class: AI/compute, yeomen tools, land, energy infrastructure, blended market
8. **Inequality** — Gini proxy tracking the labour/capital income shift over time

---

## Quick Start

```bash
pip install numpy pandas matplotlib
python3 model.py
```

Outputs:
- `ai_economy.png` — 12-panel chart across all scenarios
- `scenario_*.csv` — annual time series for each scenario

---

## Model Structure

### Four Economic Sectors

| Sector | Initial GDP share | Automatable? | Price trend |
|---|---|---|---|
| Knowledge work | 40% | Yes (ceiling: 88%) | −10%/yr nominal |
| Physical/manual work | 30% | Yes (ceiling: 68%, lagged 7yr) | −6%/yr nominal |
| Human economy | 7% | No (by definition) | +4%/yr (Baumol) |
| Government & public services | 23% | Partially | +2%/yr |

### The Nominal GDP Problem

A central finding of the model — and a deliberate design choice — is that
**nominal GDP may decline even as real output grows substantially**. This is
because competition passes AI productivity gains to consumers as lower prices.
The real economy (in quantity terms) becomes enormously more productive, but
the *nominal* economy — which is what the tax base tracks — shrinks in
automatable sectors.

This creates the core fiscal tension: governments must fund redistribution from
a potentially contracting nominal tax base.

### Automation S-Curves

Automation displacement follows a logistic (S-curve) function, consistent with
how all major technology adoptions have diffused historically. The three
parameters that matter:

- **Ceiling** — the maximum fraction of jobs that can be automated (fixed at
  88% for knowledge work, 68% for physical)
- **Speed** — steepness of the S-curve (fixed)
- **Midpoint** — the year at which 50% of the ceiling is reached (the main
  scenario variable: slow=14yr, medium=9yr, fast=5yr)

Physical work automation lags knowledge work by 7 years at the midpoint,
reflecting the harder engineering problem of unstructured physical environments.

### Capital Returns

Returns are modelled by asset class rather than as a single rate:

- **AI/compute capital**: Starts at 28% (oligopoly rents from early movers),
  decays toward 7% (competitive rate) with an 11-year half-life. The assumption
  is that open-source models and commoditising inference hardware progressively
  erode monopoly returns.
- **Land**: Stable 3.5% yield + 3.5% price appreciation = 7% total return.
  Land is the canonical rivalrous asset — it cannot be replicated.
- **Energy infrastructure**: Starts at 7%, rises 1.2%/yr as AI and robotics
  dramatically increase energy demand. Capped at 18%.
- **Blended market return**: Weighted average across asset classes, with AI
  capital weight declining over time as it commoditises. Falls from ~13% to
  ~7% over the horizon.

---

## The Three Scenario Parameters

All scenarios are combinations of these three levers:

| Parameter | Values | What it controls |
|---|---|---|
| `mid` (automation midpoint, years) | 5 / 9 / 14 | Speed of labour displacement |
| `yeomen` (fraction of capital income through owner-operators) | 0.0 / 0.35 / 0.60 | How distributed AI/robot ownership is |
| `tax_k` (effective tax rate on concentrated capital income) | 0.20 / 0.35 / 0.50 | Government's ability to redistribute |

### Human Economy Is Derived, Not Assumed

The human economy size is not a free parameter — it is computed from consumption
flows each period:

```
human_economy_demand =
    concentrated_capital_income × MPC_concentrated × human_service_share (30%)
  + yeomen_income               × MPC_yeomen       × human_service_share (10%)
  + labour_income               × 0.90             × human_service_share (10%)
  + UBI_spending                                   × human_service_share (15%)
```

This produces a human economy of roughly 5–8% of nominal GDP initially, falling
toward 2–4% as nominal GDP contracts and capital concentrates. The only forces
that grow the human economy are: more redistribution (UBI → discretionary
spending), more yeomen income (high MPC), and land-access households whose
subsistence buffer frees up UBI for discretionary consumption.

### The Yeomen Parameter

`yeomen` represents the fraction of automatable-sector capital income that flows
to small owner-operators rather than to large firms. This matters because:

- Yeomen income has labour-like MPC (~78%), vs. ~25% for concentrated capital
- It circulates demand more broadly, supporting the human economy
- It directly reduces inequality without requiring government redistribution
- It does not require high tax rates to achieve — it is a structural property
  of how production is organised

The yeomen scenario is grounded in two observations:

**1. Transaction cost collapse (Coase).** Firms internalise functions because
contracting is costly: search, specification, monitoring, enforcement. AI
reduces all of these toward zero simultaneously. When a manufacturing company
can contract out its IT, legal, accounting, marketing, logistics management, and
R&D to AI-augmented solo operators at near-zero coordination cost, those
functions fragment into yeomen enterprises. Only the physical production core —
the fab, the chemical plant, the assembly line — stays inside the firm. That
core is often 40–60% of manufacturing GDP; the services shell around it
(currently 30–40% of manufacturing employment) becomes yeomen-amenable.

**2. Sector amenability.** Sectors divide roughly as follows:

| High yeomen (>60%) | Medium (30–60%) | Low (<30%) |
|---|---|---|
| Construction & trades | Agriculture (commodity) | Semiconductor fabs |
| Professional services | Retail | Automotive assembly |
| Healthcare delivery | Transportation | Chemical plants |
| Food service | Vertical farming | Digital platforms |
| Personal services | Education | Core finance/insurance |
| Creative/media | Real estate services | Pharma R&D |

High-yeomen sectors share: low fixed costs, bespoke output, relationship-based
trust, no network effects on the production side. Low-yeomen sectors share:
high minimum efficient scale, network effects, physical infrastructure with
natural monopoly characteristics, or safety/regulatory requirements demanding
institutional scale. Roughly 35–55% of private-sector GDP is amenable to
yeomen organisation once the services shell around concentrated industries
is included.

---

## Key Assumptions and Rationale

### 1. TFP growth and price deflation roughly cancel in nominal terms

In competitive markets, productivity gains pass to consumers as lower prices.
A firm that can produce twice as much with the same inputs will be undercut by
competitors until prices halve. This means nominal revenue in automatable
sectors stays roughly flat even as real output soars.

Evidence: This is what happened in manufacturing (especially electronics) over
the past 40 years. Semiconductor performance has improved ~1,000,000× since
1970; the nominal revenue of the semiconductor industry has grown modestly.

### 2. Knowledge work automation ceiling: 88%

Not all knowledge work is automatable. Residual human roles include legal
liability bearing, fiduciary responsibility, political representation,
high-stakes negotiation, and work whose value is specifically that a human did
it. 88% leaves roughly 1-in-8 knowledge jobs as structurally human.

### 3. Physical work automation ceiling: 68%, lagged 7 years

Physical automation faces harder engineering problems: unstructured
environments, weather, safety regulations, and the high per-unit capital cost
of physical robots (unlike software, physical robots cannot be infinitely copied
at zero marginal cost). The ceiling is lower and the timeline longer.

Construction costs in particular are dominated by materials (~40–50%) and
permitting/regulatory processes — neither of which is automated by robots —
so cost deflation in physical sectors is slower than in knowledge sectors.

### 4. Baumol cost disease in the human economy (+4%/yr)

Services that cannot be automated become relatively more expensive over time
as overall productivity rises. This is Baumol's cost disease: a string quartet
requires the same four musicians it did in 1800, so its relative cost rises
as the rest of the economy gets more productive.

In a world where AI goods approach zero marginal cost, human-delivered services
will command an extreme Baumol premium. The 4%/yr figure is conservative
relative to what the full model implies structurally.

### 5. Existing government spending: 27% of GDP

US federal + state + local spending is roughly 35–37% of GDP today, but
approximately 7–10 percentage points of that is transfer payments (Social
Security, Medicare, welfare) which are themselves a form of redistribution
already. The 27% figure represents the non-transfer baseline: defence,
infrastructure, public health, education, and the administrative machinery
of government. These are largely fixed obligations that do not shrink easily.

### 6. Capital income tax rate: 20–50%

The US effective corporate tax rate after deductions is approximately 18–22%.
The high-tax scenario (50%) represents aggressive reform including higher
headline rates, elimination of offshoring vehicles, and possibly a robot/AI
transaction tax. The practical ceiling is contested; the model treats it as
a free parameter rather than making a political prediction.

### 7. Home production as subsistence buffer

The model includes a subsistence buffer from home production — food growing,
basic home services, household energy generation — that partially offsets the
loss of wage income for households with land access.

The analogy is residential solar panels. It is more efficient to buy electricity
from the grid than to generate your own; but if you have no currency to pay the
bill, generating your own power is strictly preferable to going without. The
same logic applies to food and basic services when wage income dries up: the
opportunity cost of time approaches zero, cheap energy (solar) reduces input
costs, and AI-assisted tools lower the skill threshold for small-scale
production.

Parameters:
- `LAND_ACCESS_FRAC = 0.40` — 40% of displaced workers have land access
  (homeowners with outdoor space; urban renters cannot participate)
- `HOME_PROD_VALUE_K = 6.0` — $6k/yr of effective home production value
  (covers ~25–35% of food needs plus basic home services)

**The demand circulation effect.** When home production covers part of
subsistence, a larger fraction of any cash UBI is discretionary rather than
survival spending. Discretionary spending has a higher fraction going to the
human economy (people choose human-delivered experiences) vs. automatable goods
(which they buy at rock-bottom prices regardless). This means:

```
same UBI budget → more goes to human services → more human economy demand
                → more tax base → more UBI → positive feedback
```

The model captures this through a slightly higher human-service spending share
for land-access UBI recipients (`HOME_PROD_UBI_UPLIFT = 0.08`). The aggregate
effect on nominal GDP is modest (~1–3%) but meaningful for welfare: effective
welfare = UBI + $2.4k average home production contribution.

**The land bifurcation.** This mechanism creates a two-tier outcome among
displaced workers. Those with land access achieve effective welfare materially
above their cash UBI. Urban renters are fully dependent on cash transfers. Land
policy — community gardens, allotment access, urban farming infrastructure,
land value taxation to discourage vacancy — is therefore a welfare policy, not
just a planning question.

### 8. Capital ownership distribution and MPC

The model uses a single blended marginal propensity to consume (MPC) from
capital income of approximately 20–35%. The true figure depends on who owns
the capital:

| Owner type | Capital share | MPC |
|---|---|---|
| Top 1% (active investors) | ~38% | ~12% |
| Next 9% (wealthy households) | ~51% | ~30% |
| 401k/pension holders | ~10% | ~65% |
| Bottom 50% | ~1% | ~90% |

Weighted average: ~25–30%. This is substantially higher than a pure
oligarch-concentration model (which would imply ~12%) but much lower than
the ~90% MPC of labour income. The demand gap between a labour economy and
a capital economy is real but not as extreme as the simplest version of the
displacement story suggests.

Passive dividend income from index funds and 401k plans partially closes this
gap, particularly as the population ages and more people consume from
retirement savings rather than wages.

---

## Known Limitations

**No debt dynamics.** The model does not include debt deflation feedback. In a
deflationary scenario, the real burden of existing nominal debt increases,
which can trigger defaults, credit contraction, and further deflation — a
spiral described by Irving Fisher (1933). This is a significant omission for
near-term (5–15 year) dynamics.

**No international dimension.** The model is US-centric. Capital flight to
lower-tax jurisdictions, global AI diffusion, and geopolitical competition
(especially US–China on semiconductor and model access) are not modelled.

**Capital returns are stylised.** The asset return functions are constructed
from plausible economic arguments but are not estimated from data. They are
best understood as directional claims (AI returns fall, energy rises, land
holds) rather than point forecasts.

**Political economy is absent.** The tax rates and redistribution mechanisms
are assumed to be achievable. In practice, the political feasibility of
high capital taxation depends on whether displaced workers can organise faster
than capital owners capture regulatory institutions — arguably the central
political question of the coming decades.

---

## Policy Extension: Commons DAOs as Yeomen Infrastructure

The `yeomen` parameter represents distributed capital ownership, but it raises
a practical question: what institutional mechanisms actually produce it? One
promising structure is the **commons DAO** — a decentralised autonomous
organisation that governs a shared productive asset and distributes income to
contributors.

### The Software DAO Model

The simplest implementation is open source software:

1. **The DAO owns a software commons** — not just the code repository, but the
   ongoing service bundle that enterprises actually pay for:
   - Security audit certification and CVE response SLA
   - Legal indemnification for licence compliance
   - Long-term API/ABI compatibility certification
   - Managed upgrade paths and dependency resolution

2. **Enterprises pay licence fees** for the service bundle, not the code. The
   code remains freely forkable; the services are not. This is fork-resistant
   because a company cannot replicate the institutional trust (audit history,
   legal standing, SLA track record) by copying the repository. A fork starts
   with zero certification history.

3. **Fees flow into a contract auction pool.** Maintenance tasks —
   specification writing, security audits, documentation, compatibility
   testing, CVE triage — are posted as bounties and auctioned to contributors.
   AI-augmented individuals can bid on tasks that previously required a team.

4. **Governance is dual-track:**
   - *Licensees* vote on product roadmap and service levels (they pay, so they
     have legitimate standing to set direction)
   - *Contributors* vote on internal governance: token allocation, audit
     standards, dispute resolution
   - Tokens are time-weighted (early contribution rewarded) with a
     decay function to prevent permanent lock-in by founding cohorts

### Why This Matters for the Model

A software commons DAO is effectively a mechanism for converting concentrated
platform rents into distributed yeomen income. Without it, the economic surplus
from a widely-used open source project flows mostly to: (a) the handful of
companies whose employees maintain it (GitHub, Google, Red Hat), or (b) the
large firms that deploy it without contributing. With a commons DAO, surplus is
redistributed to anyone who contributes certified work — including displaced
knowledge workers who, with AI assistance, can now complete tasks that
previously required specialised expertise.

In model terms, this raises the effective `yeomen_frac` for the knowledge
economy sector without requiring government redistribution. It is a structural
property of how production is organised, not a tax-and-transfer mechanism.

### Extensions Beyond Software

Software is the easiest case because the marginal cost of digital goods is
already near zero. The same structure applies wherever:

- The commons is a shared digital asset with high fixed costs and near-zero
  marginal reproduction cost
- There is a service bundle around the asset that generates ongoing fees
- Contribution can be verified and rewarded programmatically

Candidate commons:

| Domain | Commons asset | Service bundle |
|---|---|---|
| Software | Code, specifications | Security cert, SLA, compatibility |
| AI models | Weights, training data | Audit cert, safety eval, fine-tune support |
| Medical protocols | Clinical guidelines | Liability indemnification, update SLA |
| Legal templates | Contract library | Jurisdiction compliance, update tracking |
| Scientific data | Research datasets | Provenance certification, curation |
| Urban planning | Model libraries | Localisation support, regulatory mapping |

Each domain follows the same logic: the code/protocol/dataset is free; the
institutional trust wrapper is not.

### Government as Anchor Client

The US federal government spends approximately $100bn/year on IT procurement.
A policy requiring that publicly-funded software be governed through public
DAOs — analogous to open access mandates for publicly-funded research — would:

- Create a large, stable revenue base for commons DAOs immediately
- Establish certified governance standards others could adopt
- Reduce vendor lock-in in critical infrastructure
- Provide income to a distributed contributor base including geographically
  dispersed workers who currently have no path into knowledge-economy income

This is not a radical departure from existing procurement policy — it is
an extension of the open-source preference clauses already in the Federal
Acquisition Regulation — but it would be materially redistributive.

### Connection to Ostrom's Commons Governance

The governance design above maps directly onto Elinor Ostrom's seven principles
for sustainable commons management (Ostrom, 1990):

1. **Clearly defined membership** — token holders with verified contributions
2. **Proportional distribution** — fees distributed to contributors by stake
3. **Collective choice** — dual-track governance with voice for affected parties
4. **Monitoring** — on-chain audit trails; all contributions and disbursements
   are transparent
5. **Graduated sanctions** — slashing of tokens for certified work that is later
   found fraudulent
6. **Conflict resolution** — binding arbitration mechanism in the governance charter
7. **Recognition of rights** — legal entity (LLC or co-operative) wrapper that
   gives the DAO standing in contract and IP law

Ostrom showed these principles were sufficient to sustain commons over
centuries in pre-digital contexts (irrigation systems, fishing grounds,
Alpine meadows). The blockchain/smart-contract stack makes them cheap to
implement at global scale, for the first time removing the coordination
cost barrier that previously limited commons to geographically proximate
communities.

---

## Intellectual Background

This model was built against the backdrop of a debate in early 2026 between two
competing macro views of AI's economic consequences:

**The doom loop view** (Citrini Research, "The 2028 Global Intelligence Crisis"):
AI displaces white-collar workers → incomes fall → consumer spending softens →
companies cut more with AI → private credit built on stable income assumptions
collapses → financial cascade. The scarce input (intelligence) became abundant,
dissolving the income assumptions underlying the entire financial system.

**The sceptic view** (Citadel Securities, "The 2026 Global Intelligence Crisis"):
Technology diffusion follows S-curves, not exponentials. Compute costs, regulatory
barriers, and organisational inertia constrain deployment. National accounting
identities mean productivity gains must show up as demand somewhere. Historical
precedent (electrification, computing) shows technology creates more jobs than
it destroys.

This model attempts to be agnostic between them by making the key parameters
explicit — automation speed, human economy size, tax regime — and showing what
each combination implies rather than asserting which is correct.

---

## Key References

**Primary sources that motivated this model:**

- Citrini Research. "The 2028 Global Intelligence Crisis." February 2026.
  https://www.citriniresearch.com/p/2028gic

- Citadel Securities. "The 2026 Global Intelligence Crisis." February 2026.
  https://www.citadelsecurities.com/news-and-insights/2026-global-intelligence-crisis/

**Economic concepts drawn on:**

- Baumol, W.J. and Bowen, W.G. (1966). *Performing Arts: The Economic Dilemma*.
  Twentieth Century Fund. [Origin of Baumol's cost disease — the structural
  reason human services inflate relative to automated goods.]

- Fisher, I. (1933). "The Debt-Deflation Theory of Great Depressions."
  *Econometrica*, 1(4), 337–357. [Mechanism by which deflation causes debt
  defaults which cause further deflation — a known risk in the transition period
  not captured by this model.]

- Keynes, J.M. (1930). "Economic Possibilities for our Grandchildren." In
  *Essays in Persuasion* (1931). [Predicted 15-hour workweeks from productivity
  growth; was right about productivity, wrong about leisure vs. consumption
  expansion. The cautionary precedent for all labour displacement predictions.]

- Piketty, T. (2014). *Capital in the Twenty-First Century*. Harvard University
  Press. [Framework for thinking about r > g, capital share dynamics, and
  long-run inequality when returns on capital exceed economic growth.]

- Rogers, E.M. (1962). *Diffusion of Innovations*. Free Press. [S-curve model
  of technology adoption used for the automation displacement functions.]

- Acemoglu, D. and Restrepo, P. (2018). "The Race between Man and Machine."
  *American Economic Review*, 108(6), 1488–1542. [Formal model of automation
  and labour displacement; distinguishes task-replacement from productivity-
  enhancing automation.]

**On capital ownership distribution:**

- Wolff, E.N. (2021). "Wealth Inequality in the United States, 1983–2019."
  NBER Working Paper 28715. [Source for the ~90% equity concentration in the
  top 10% of households used in the MPC calculation.]

- Board of Governors of the Federal Reserve System. *Distributional Financial
  Accounts*. https://www.federalreserve.gov/releases/z1/dataviz/dfa/
  [Quarterly data on wealth distribution by income percentile used to
  calibrate ownership concentration assumptions.]

**On industrial policy and distributed ownership models:**

- Simon, H. (1992). "What is an Explanation of Behavior?" *Psychological
  Science*. [Background on firm structure and coordination costs.]

- Herrigel, G. (1996). *Industrial Constructions: The Sources of German
  Industrial Power*. Cambridge University Press. [Historical analysis of the
  German Mittelstand model — the main empirical precedent for the distributed
  ownership / micro-firm scenario.]

**On commons governance and DAO structures:**

- Ostrom, E. (1990). *Governing the Commons: The Evolution of Institutions for
  Collective Action*. Cambridge University Press. [Nobel Prize-winning analysis
  of how communities sustainably manage shared resources without privatisation
  or state control. The seven design principles for viable commons governance
  are the structural template for the commons DAO policy extension.]

- Coase, R.H. (1937). "The Nature of the Firm." *Economica*, 4(16), 386–405.
  [Transaction cost theory of why firms exist — and therefore why declining
  transaction costs (via AI) shrink the boundary of the firm toward yeomen
  enterprises and commons structures.]
