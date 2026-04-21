# The AI Economy: What the Numbers Say
## A Summary of Findings for Policymakers

**March 2026** · *Based on a parametric model of the AI economic transition, calibrated to a US-like economy. Full paper and model code available on request.*

---

## The core problem

AI and robotics are making the economy vastly more productive. But productivity gains and shared prosperity are not the same thing — and who owns the machines determines which one you get.

The model projects a US-like economy over 35 years under different assumptions about how AI capital is owned, taxed, and governed. The central finding: **real output nearly doubles within a decade, but who benefits depends almost entirely on ownership structure, not on how hard governments try to redistribute afterwards.**

---

## Five things that might surprise you

### 1. The economy doesn't shrink — it pivots

An earlier version of this model projected nominal GDP halving as AI deflated prices. The revised model, which accounts for Jevons-paradox dynamics in physical goods, surging energy demand, and scarcity goods appreciation, shows a different outcome: nominal GDP grows from $30 trillion in 2025 to roughly **$37 trillion by 2035 and $47 trillion by 2045**.

But the growth is compositional. Sectors that employ most workers — knowledge work, professional services — deflate in per-unit price as AI commoditises their output. Sectors with few workers — energy infrastructure, artisanal and provably-human goods — grow rapidly. The economy isn't shrinking. The problem is that the growth is going to people and sectors that don't employ many workers.

> *What's growing: physical goods (Jevons demand surge), energy (two-phase: infrastructure boom then robotics-enabled solar collapse + Jevons backfire), scarcity goods (+6%/yr). What's deflating: knowledge work, mass-market healthcare, education. Net result: GDP grows, but labour income doesn't.*

Physical goods are an important case. Labour is only about **25% of the cost of making something** — the rest is raw materials (57%), embedded energy (8%), and overhead. When AI automates the 25%, prices fall modestly. But demand surges. And rising material costs (copper is projected to be 50% more expensive by 2040 as electrification demand outstrips supply) create a hard floor. So manufacturing stays roughly flat in nominal terms, not a casualty of deflation.

Energy is the most interesting sector. In the near term, retail electricity prices actually *rise* — not because solar modules are expensive (they're not) but because grid transmission, storage, and infrastructure hardening dominate delivered cost. Then robotics changes the equation: solar installation labour is 15–40% of installed cost, and it is exactly the kind of structured repetitive work robots will automate. This unlocks cheap electricity, which in turn enables green hydrogen (making green steel, synthetic fuels, and fertiliser viable), desalination at scale, and always-on robotic manufacturing. Demand grows faster than prices fall — Jevons backfire, the same dynamic that made the computing sector grow even as the cost of computation fell by 10 orders of magnitude. The model captures this as a phase transition whose timing depends on how fast automation proceeds.

---

### 2. The fiscal problem is about tax instruments, not tax rates

Because nominal GDP grows, the debt crisis narrative is less severe than earlier projections suggested. Debt-to-GDP falls from ~1.2x in 2025 to ~0.9x by 2035 across scenarios. Interest payments consume 9–17% of tax revenue by 2035, not the 39–55% previously projected.

But there is a real fiscal problem — it's just different. **The tax base is shifting from labour income (easy to collect via withholding) to capital income (mobile, harder to collect)**. A government that collects 28% of $10 trillion in labour wages collects $2.8T. A government that collects 20% of $12 trillion in capital income collects $2.4T — with more leakage. As workers are displaced and capital income rises, a government relying on payroll taxes sees revenue erode even as the nominal economy expands.

The practical implication: **instrument design matters more than rate**. A 50% capital tax rate at 30% enforcement (small open economy) collects less than a 20% land value tax at 95% enforcement. Land value taxes, energy levies on data centres, and VAT on AI-delivered services are enforcement-immune. Corporate income taxes on AI capital are not.

---

### 3. Who owns the machines matters more than tax rates

This is the finding that most challenges conventional redistributive policy thinking. Under baseline assumptions, **distributed ownership of AI capital reduces inequality roughly twice as effectively as equivalent fiscal redistribution**.

| Ownership structure | Gini at 2035 | Effective welfare (2035) |
|---|---|---|
| Concentrated / Low tax | 0.78 | $2k/yr |
| Concentrated / High tax | 0.77 | $151k/yr* |
| Distributed (yeomen 60%) | 0.44 | $73k/yr |
| Public AI infrastructure (90%) | 0.14 | $57k/yr† |

*\*High welfare per displaced worker reflects large tax revenues from 50% capital tax on $37T economy, divided across 46M displaced workers. Market income distribution remains highly concentrated.*
*†Includes $55k/yr citizen compute dividend.*

*Today's US Gini is approximately 0.41. The concentrated scenarios represent severe deterioration; the distributed scenarios represent improvement on today's baseline.*

The mechanism is the marginal propensity to consume (MPC) differential. Concentrated capital income has an MPC of around 25% — most of it is saved or reinvested. Distributed (yeomen/commons) income has an MPC of around 78% — labour-like, because it is earned income. Every $1 trillion shifted from concentrated to distributed ownership generates approximately $530–600 billion of additional annual consumption, sustaining demand, the human economy, and the VAT base.

---

### 4. Yeomen require the right tax code to work

The yeomen model depends on a mechanism that doesn't currently exist: **equal tax treatment for independent operators vs corporate employees**.

Under the current US tax code, an independent operator faces approximately an 18% effective income discount compared to a corporate employee earning the same gross amount:
- Double FICA (employer + employee share): ~8%
- Own health insurance (no employer subsidy): ~7%
- Compliance overhead: ~3%

At the scale of the yeomen transition modelled — 60% of capital income flowing to millions of independent operators — this represents approximately **$2.4 trillion per year in foregone effective income by 2035**. Without fiscal reform, the yeomen equilibrium requires workers to accept substantially lower effective compensation to participate.

Two policy levers reduce this friction:

**Tax code reform** (extend employee-equivalent FICA treatment, full health deductibility): Eliminates ~$2.4T/yr friction at full deployment.

**Firm rebate for contracting to external operators**: A tax credit for firms that hire independent contractors rather than employees creates a demand-side incentive for the Coasian fragmentation. At 15% rebate rate, friction costs fall from $2.4T to ~$1.4T/yr — a $1T/yr improvement at modest revenue cost.

---

### 5. Concentrated ownership erodes the institutions needed to fix it

The static scenarios assume enforcement capacity is a policy choice. A more realistic model treats it as a stock that decays when concentrated wealth has both the incentive and the means to weaken it.

International evidence supports the directional claim. The US IRS audit rate for the top 0.1% fell from ~10% in 2010 to ~2% by 2018 — driven by budget cuts financed partly through political donations with an interest in reduced scrutiny. South Africa's revenue authority was deliberately weakened during the state capture period (2014–2018) to protect elite non-compliance.

The model captures this as a doom loop: concentrated ownership → high inequality → governance decay → lower effective tax collection → less redistribution → higher inequality → faster decay.

**The practical implication: concentrated-ownership scenarios are worse than the static analysis implies.** The high-tax response that appears to work assumes institutional capacity that concentrated ownership, over time, removes.

---

## What to do — ordered by who can do it

**Any jurisdiction, immediately:**
- Shift to enforcement-immune taxes: land value tax (land triples in value by 2055 across all scenarios), data centre energy levy, digital services VAT
- Reform the yeomen tax code: extend FICA parity and health deductibility to independent operators; create firm rebate for external contracting
- Give small operators capital access: accelerated depreciation for AI tools owned by sole operators and cooperatives, cooperative lending programs, public compute access at cost

**Large blocs (US, EU, major economies):**
- Progressive compute levy: exempt small users, escalating rates for large commercial users
- Defend the open-weight AI ecosystem: prevent vertical integration that forecloses small-operator independence; portability mandates; interoperability requirements
- Public AI infrastructure investment: state-owned compute rented via usage-fee markets, citizen dividend from rental income

**Small and medium nations:**
- Regional bloc coordination before unilateral capital tax measures
- Mineral resource leverage where available (cobalt, lithium, rare earths)
- Commons and cooperative structures as primary strategy — locally anchored, enforcement-immune

---

## The window is now

AI capital rents are highest in the first decade of the transition. Institutional capacity has not yet been eroded. Open-weight AI models already exist and provide the foundation for a distributed-ownership equilibrium without requiring it to be built from scratch.

The political salience is lowest in the same period — displacement is not yet severe, pressure to act is weakest. This is the adverse timing problem.

Each year of delay simultaneously narrows the fiscal window and advances the governance decay that makes later action harder to implement. The case for acting now is not that the problem is already severe. It is that **acting before it becomes severe is the only path that uses the available tools while they still work**.

---

## The deeper question

The model shows public AI infrastructure achieving the best distributional outcomes. It also shows that getting there requires the state to successfully build, govern, and operate frontier infrastructure across election cycles and against sustained incumbent opposition — a significant institutional ask.

The yeomen model achieves nearly comparable outcomes with a narrower commitment: defending the open-weight AI ecosystem that already exists and enforcing net-neutrality-style non-discrimination rules. Its failure mode — platform capture — is gradual and visible, with more opportunity for correction than the public AI failure mode.

But the model cannot capture what the numbers miss. Public AI produces better-distributed material outcomes; the yeomen model produces people who *earned* what they have. Economic agency, the sense of being a contributor rather than a recipient, and the democratic legitimacy that comes from owning one's means of production are not captured in a Gini coefficient. The choice between them is ultimately a values question. It should be stated plainly rather than dissolved into welfare metrics.

---

*Full methodology, all scenario parameters, model code, and references available in the accompanying technical paper.*
