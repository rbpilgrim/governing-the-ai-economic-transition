# Governing the AI Economic Transition
## A Scenario Exercise on Distributional Outcomes Under Rapid Automation

**Working Paper — April 2026**

*Model source code available at the project repository. All assumptions are explicit and adjustable.*

---

## Abstract

This paper is a thought experiment, not a forecast. We ask a conditional question: *if* artificial intelligence and robotics displace a large share of current jobs within a decade or two, what kind of economy emerges, and which policy responses produce which kinds of outcomes? To answer it concretely enough to discuss, we build a parametric macroeconomic model of a US-like economy ($28 trillion, 160 million workers, 2026 baseline), project it forward 35 years, and run ten policy dimensions across a wide range of assumptions about ownership structure, tax instruments, and institutional capacity. We do not claim to know whether rapid automation will occur, how fast, or how the system will react. We deliberately stress the model with a wide sensitivity analysis precisely because the system's reactions are impossible to anticipate; we acknowledge this irreducible uncertainty rather than write past it.

Within the conditional frame, the pattern that keeps reappearing across scenario configurations is that **distributional outcomes depend primarily on who owns the AI capital — and the policy instruments that perform well are different from the ones we would reach for by default.**

The central distributional choice is between two ownership archetypes. In the **concentrated** model, AI and robotic capital is held by a small number of large operators; income accrues to capital owners with low marginal propensity to spend, demand contracts, and the tax base — designed for wage income — erodes. In the **yeomen** model, the same capital is held by many independent owner-operators — think the small business owner who owns their robot fleet or AI agents outright, earns the full return, and bears professional accountability for the output, in contrast to the operator who rents compute from a platform and accumulates no capital of their own. Yeomen earn income with high marginal propensity to spend, sustaining demand and the tax base through the transition.

Seven structural findings follow from the scenario analysis.

**1. The economy pivots in composition, not size.** Nominal GDP grows — from ~$30T in 2026 to ~$33T by 2036 and ~$42T by 2046 — because AI-driven deflation in knowledge work is offset by Jevons demand expansion in physical goods, real estate appreciation as automation unlocks previously marginal land, and rising premiums on irreducibly human services. The distributional problem is not economic contraction; it is that the income from growth accrues to capital owners.

**2. The fiscal problem is instrument mismatch, not insolvency.** The tax base shifts from labour income (high-enforcement, withholding-based) to capital income (mobile, leakage-prone). A government relying on payroll taxes faces structural revenue erosion even as nominal GDP grows.

**3. Ownership outperforms redistribution by roughly 2-to-1.** In this model, distributing AI capital ownership to independent operators reduces inequality approximately twice as effectively as taxing concentrated capital income and redistributing the proceeds — driven by the marginal propensity to consume differential (~25% for concentrated capital, ~78% for earned income). This result is robust to wide parameter variation but depends on a supported yeoman equilibrium, not spontaneous market fragmentation.

**4. The yeoman model has a fiscal prerequisite that does not exist today.** The current US tax code imposes an ~18% effective income discount on self-employed operators (double FICA, non-deductible health insurance, administrative overhead) relative to equivalent corporate-employed workers — roughly $2.4 trillion per year in foregone income at full yeoman deployment. This is not a market outcome; it is a tax code distortion that systematically subsidises large firm employment over independent contracting.

**5. Instrument design beats statutory rate.** Enforcement-immune instruments — land value taxes (immobile, near-complete enforcement), energy levies (physical metering, known location), and value-added taxes (collected at point of consumption) — outperform capital income taxes at any statutory rate for jurisdictions where capital is mobile. For small open economies, the instrument choice is more consequential than the rate.

The paper's central recommendation follows from these findings: **build the ownership structure and the infrastructure before the displacement arrives, not after.** The fiscal window for public investment is open now (AI capital returns at 22–28%, concentrated in 2026–2036) and closes as returns compress and governance erodes under concentrated ownership. A federated open marketplace — making agent-to-agent contracting, automatic tax reporting, and aggregate foreign-ownership tracking available at near-zero cost — is the prerequisite for both the yeoman economy and for the regulatory legibility that small nations need to defend against machine-speed capital accumulation and knowledge-work offshoring. This infrastructure does not yet exist. Building it is the highest-leverage near-term action.

---

## 1. Introduction

### 1.1 What this paper is, and what it is not

This paper is a structured thought experiment. We do not claim to predict whether rapid automation will occur, how fast it will happen, or how labour markets, capital markets, governments, and households will actually respond. Each of those questions is genuinely open, and most attempts to answer them have aged poorly. What we do claim is that *if* rapid automation arrives — within the range of possibilities seriously discussed by AI researchers, policymakers, and frontier labs as of 2026 — then certain structural relationships between ownership, taxation, and distribution will dominate the outcome, and these relationships are largely invisible in the policy frameworks designed for previous economic transitions. The paper exists to make those relationships concrete enough to argue about.

The model we build is almost certainly wrong in its specifics. Macroeconomic models of structural transitions always are. We chose to build one anyway, rather than reason in prose, for two reasons. First, a model forces every assumption to be explicit and every claim to be reproducible — readers who disagree with a parameter can change it and see the result. Second, distributional outcomes under rapid automation are emergent: they arise from interactions between productivity, demand, taxation, enforcement, and institutional decay that prose arguments routinely fail to track. A model is the smallest tool that keeps these in view simultaneously.

We compensate for the model's unreliability by running an unusually wide sensitivity analysis: ten independently varying policy dimensions, automation speeds from 5 to 14 years to midpoint, statutory capital tax rates from 20% to 50%, enforcement levels from 30% to 100%, and ownership structures spanning concentrated, distributed-yeomen (independent owner-operators — defined in §2), commons-DAO, and public-infrastructure models. Across that full range, the same structural relationships keep appearing and the same instruments keep working or failing for the same reasons. The conversation starter we are offering is that pattern, not the numbers attached to any specific run. Limitations and known sensitivities are addressed in §7.

### 1.2 Why the question matters now

Previous automation waves substituted capital for labour in specific tasks while complementing human labour in others, and net employment effects were ambiguous. The current wave has structural features that may produce a categorically different outcome. Large language models and associated AI systems substitute for the *cognitive* component of white-collar work — the component that previously commanded a wage premium and anchored middle-class income distribution. The marginal cost of deploying additional intelligence approaches zero once training costs are sunk. Deployment is software-first, diffusing through API access rather than physical installation, removing the friction that slowed earlier automation. And the same robotic systems that automate warehouses and factories are approaching the dexterity threshold required for unstructured physical environments.

If this transition is fast enough — and we make no claim about whether it will be — the distributional question becomes structural rather than cyclical. When compute and robotics are the primary factors of production, income accrues to the owners of those factors. Labour income, which today sustains consumer demand, the tax base, and household debt serviceability, falls. What replaces it, who receives it, and how it is taxed determine what kind of economy emerges on the other side. The window in which institutions can be designed to shape this outcome is narrowest precisely when the political pressure to act is lowest: before displacement is severe enough to be obviously unignorable. That asymmetry is the policy-relevant motivation for thinking about the question now, in the conditional, rather than waiting for empirical confirmation.

---

## 2. Theoretical Framework

**Factor substitution and income distribution.** When AI and robotics reduce the marginal cost of capital-provided cognitive and physical services toward zero, the equilibrium capital share of income in automatable sectors rises toward 100% of output. The distributional question concerns who owns the capital.

**Baumol cost disease** (Baumol and Bowen, 1966). When productivity growth concentrates in capital-intensive sectors, labour-intensive sectors experience persistent relative cost growth. The model applies this to the residual human economy — irreducibly human services (bespoke professional work, live performance, care relationships) — but explicitly *excludes* mass-market healthcare and education, which are modelled as AI-delivered services subject to software-like price deflation, not Baumol dynamics.

**Scarcity goods** are a distinct sector in the model: goods and services that require irreducible human presence or labour, cannot be substituted by AI or robotics without destroying the product itself, and are therefore shielded from productivity-driven deflation. The defining property is that the buyer's willingness to pay is anchored to the human component, not to the underlying capital cost. Live performance, bespoke craft work, direct relational care, and certified professional accountability where a human must be legally and personally responsible are representative examples. As AI-provided alternatives become cheap and abundant, the residual human-provided category becomes scarcer and more valuable — Baumol dynamics apply and the premium rises with income inequality.

**Fisher debt-deflation** (Fisher, 1933). Fixed nominal debt obligations become more or less burdensome as the nominal economy evolves. In the revised model, nominal GDP grows, so the Fisher mechanism runs in the benign direction — real debt burden falls. The fiscal tension that remains is instrument-structural: the tax base is shifting from labour income (high-enforcement, withholding-based) to capital income (mobile, harder to collect).

**Coase theory of the firm** (Coase, 1937). Firm boundaries are set by transaction costs. AI reduces search, specification, monitoring, and enforcement costs toward zero simultaneously, shifting the Coasian equilibrium toward smaller firm sizes. Tasks previously internalised within large firms — because external contracting overhead was high — fragment to independent operators. This is the economic foundation of the **yeomen** fragmentation dynamic: not AI making small firms more productive per se, but AI making the coordination overhead that justified large firms disappear.

*The term "yeomen" throughout this paper refers to independent owner-operators who deploy their own AI and robotic capital — analogous to the historical yeoman farmer who owned the land they worked, as distinct from the tenant farmer who rented it. In the AI context, a yeoman is a sole operator or small cooperative who owns their AI agents, robot fleet, or compute capacity outright, earns the full return on that capital, and is legally and professionally accountable for the output. The contrast class is the "sharecropper" model: an operator who deploys AI tools owned by a platform, pays a per-transaction fee, accumulates no capital, and cannot exit without losing their accumulated reputation and client relationships. The yeoman/sharecropper distinction is the central distributional question of the paper.*

**Ostrom commons governance** (Ostrom, 1990). Commons DAOs in the model are designed around Ostrom's conditions for sustainable commons: clearly defined boundaries, collective choice arrangements, monitoring, graduated sanctions, and conflict resolution. The model treats commons income as high-MPC earned income from contributions to a managed asset, rather than passive capital income. Appendix D applies these conditions to both collective commons ownership and the thin-core asset entity model, in which a tightly-governed DAO systematically routes operational spending to independent operators through the agentic marketplace.

**Political economy of institutions** (Acemoglu and Robinson, 2012; Zucman, 2015). The governance decay mechanism draws on the documented relationship between concentrated economic power and institutional erosion, operating through reduced tax authority budgets, deliberate weakening of enforcement agencies, and lobbying against regulatory capacity. US IRS audit rates for the top 0.1% fell from ~10% in 2010 to ~2% by 2018. South Africa's SARS was deliberately weakened during the state capture period 2014–2018.

---

## 3. Model in Brief

The model is a parametric scenario tool, not an econometric forecast. It tracks a US-like economy across six sectors (knowledge work, AI-delivered services, physical goods, energy, scarcity goods, government) plus a derived human-services residual. Automation proceeds along logistic S-curves with sector-specific ceilings. Income flows are split into concentrated capital, yeomen, commons/DAO, and labour streams — each with distinct tax treatment and marginal propensity to consume. The human economy is derived endogenously from consumption flows rather than fixed exogenously. Government finances are tracked under multiple tax instruments with explicit enforcement parameters. Ten policy dimensions vary across scenarios: automation speed, four ownership structures, two tax instruments, enforcement, two yeomen-fiscal-friction parameters, and a governance decay mechanism.

Full model construction, baseline calibration, sector price dynamics, MPC tables, scenario parameter ranges, and the governance decay specification are documented in **Appendix B**. Readers interested primarily in results and policy implications can proceed directly to §4.

---

## 4. Results

### 4.1 The economy pivots in composition, not in size

Real output grows strongly while nominal GDP also grows — from $30T in 2026 to $37T by 2036 and $47T by 2046. This result reflects three offsetting mechanisms against knowledge-sector deflation:

| Sector | 2026 | 2036 | 2046 |
|---|---|---|---|
| Nominal GDP (total) | $30T | $37T | $47T |
| Real GDP index (2026=100) | 100 | 173 | 230 |
| Knowledge sector | $9.2T | $10.5T | $12.7T |
| Physical goods | $6.2T | $8.0T | $10.5T |
| Energy sector | $1.1T | $2.0T | $2.8T |
| Scarcity goods | $1.4T | $2.5T | $4.5T |

*Fast automation, concentrated ownership, low tax scenario.*

Knowledge sector nominal output grows only modestly despite 85% automation by 2035, because price deflation (−8%/yr) partially offsets real productivity gains. Physical goods nominal output grows as Jevons demand surges offset deflation in the automatable 25% of cost, with the material floor preventing collapse. Energy grows through Phase 1 infrastructure investment, then transitions to Phase 2 cheap-energy-enabled Jevons backfire. Scarcity goods appreciate as the premium on provably-human output rises with inequality.

The structural tension is compositional: sectors generating labour income deflate in per-unit price even as real output grows, while low-labour sectors (energy, scarcity goods) capture a rising share of nominal GDP. This is a distribution problem, not a macroeconomic collapse. The fiscal corollary: the tax base does not shrink, but its composition shifts from labour income (high-enforcement, withholding-based) toward capital income (mobile, harder to collect). A government relying on payroll taxes faces structural revenue erosion even as total nominal GDP grows.

### 4.2 Fiscal capacity depends on tax base design, not nominal GDP

Because nominal GDP grows, sovereign debt dynamics are manageable relative to earlier projections. Debt/GDP falls from ~1.2x in 2026 to ~0.9x by 2036 as the nominal economy expands. Interest payments at $1.53T/yr consume 9–17% of tax revenue by 2035 depending on scenario — a declining burden, not a spiralling one.

| Scenario | Debt/GDP t+10 | Interest % revenue t+10 | Fiscal space t+10 |
|---|---|---|---|
| No yeomen / Low tax | 0.93x | 17% | **−$0.5T** |
| No yeomen / High tax | 0.90x | 9% | +$6.9T |
| High yeomen / High tax | 0.91x | 12% | +$3.7T |
| Public AI 90% | 0.93x | 32% | −$6.5T* |

*\*Public AI negative fiscal space is not a crisis — the compute dividend of $55k/yr per adult bypasses the government budget entirely. Citizens are funded through a different channel.*

The concentrated low-tax scenario produces modestly negative fiscal space (−$0.5T) not because nominal GDP fell, but because a 20% effective capital tax rate on an economy where labour income is collapsing generates insufficient revenue. Conversely, the high-tax concentrated scenario generates +$6.9T surplus — adequate for large UBI transfers — but at the cost of highly concentrated market income (Gini 0.770) and without addressing the structural MPC problem that suppresses demand.

The practical finding: tax *instrument* design matters as much as tax *rate*. Land value taxes are enforcement-immune — land cannot be registered in the Cayman Islands. Data-centre energy levies are enforcement-immune — physical metering at a known location. VAT on AI-delivered services follows the consumer. Corporate income taxes on AI capital are not enforcement-immune — profit-shifting is already the primary avoidance mechanism, and AI makes it easier by making value more location-agnostic.

### 4.3 Ownership structure outperforms redistribution

The pattern that appears most consistently across scenario configurations: how AI capital is owned tends to matter more than how its income is subsequently taxed and redistributed. One caveat is important before reading the results: the high-yeoman scenarios are not purely emergent market outcomes. In a mature market with large corporate operators enjoying scale advantages in compute, energy procurement, and cost of capital, the natural Coasian equilibrium without policy intervention may still tilt toward concentration. The yeoman scenarios assume a supported equilibrium — subsidised capital access, fiscal code reform, and a conditional surtax backstop — as described in §6.3. The distributional superiority of the yeoman model is real, but it is the outcome of a coherent policy package, not spontaneous market fragmentation.

| Scenario | Gini t+10 | Gini t+30 | Welfare t+10 |
|---|---|---|---|
| No yeomen / Low tax | 0.784 | 0.815 | $2k/yr |
| No yeomen / High tax | 0.770 | 0.798 | $151k/yr* |
| High yeomen / High tax | 0.439 | 0.446 | $73k/yr |
| High yeomen / Tax reform | 0.433 | ~0.44 | $72k/yr |
| Public AI 90% | 0.140 | 0.117 | $57k/yr† |

*\*Market income Gini. The high-tax concentrated scenario redistributes large surpluses but market income remains highly concentrated; Gini reflects pre-transfer income structure.*
*†Includes $55k/yr citizen compute dividend.*
*Today's US Gini is approximately 0.41. All concentrated scenarios represent severe deterioration.*

The mechanism is the MPC differential. For every $1 trillion shifted from concentrated capital to distributed income, approximately $530–600 billion of additional annual consumption is generated, sustaining demand, the human economy, and the VAT tax base. Under high-MPC distributed income, the economic system becomes self-reinforcing: more consumption → larger human economy → more labour demand → higher wages → more tax revenue → more redistribution. Under low-MPC concentrated income, the system does the opposite.

#### The yeomen mechanism: Coase in reverse

The economic logic for distributed ownership through yeomen enterprises follows Coasian transaction cost theory. When AI reduces search, specification, monitoring, and enforcement costs toward zero, the boundary of the firm contracts — functions previously internalised because external contracting was expensive fragment to independent operators who now face near-zero coordination costs. The AI tools, domain knowledge, and client relationship sit with the individual operator. This fragmentation is happening through market logic without requiring policy construction; roughly 35–55% of private-sector employment is amenable to it under modelled assumptions.

The same logic applies to asset-owning entities. A DAO governing a productive asset — a solar farm, a shared dataset, a piece of infrastructure — can operate with minimal direct employment by contracting most of its operational needs to yeomen through the agentic marketplace. The tax efficiency of doing so, combined with the near-zero transaction cost of the marketplace layer, makes this the rational organisational form for any asset whose core function can be narrowly defined. DAOs of this type are therefore a structural source of recurring demand for yeoman services, not just another supply-side ownership form. The governance design principles are developed in Appendix D.

Policy's role is not to construct this dynamic but to defend it against platform capture (§4.3.3) and to remove the fiscal barriers that currently penalise it (§4.3.2).

One clarification matters for the political economy argument. The yeoman fraction grows at the margin — through new business formation, career transitions, and firms outsourcing to independent operators rather than hiring — not through redistribution or expropriation of existing corporate capital. Large firms retain the functions where scale genuinely lowers cost; independent operators take the fragmented, variable-demand, specialist work where scale provides no structural advantage. This is a combination of competitive pressure from small businesses and targeted incentives that level the fiscal playing field, not a programme to dismantle existing enterprise. The model's yeoman fraction parameter captures the long-run equilibrium share, not a point-in-time redistribution.

Capital utilisation economics determines where this boundary falls. A large corporate robot fleet needs sustained high utilisation — typically 70–80% — to justify its capital cost and meet investor return requirements. Corporate fleets therefore concentrate in high-volume, standardised, geographically dense markets where demand is predictable. Yeomen face a structurally lower utilisation threshold: their capital cost is partly or fully amortised, idle capacity has near-zero opportunity cost, and their cost structure does not carry a corporate return-on-equity requirement. This means the market self-selects yeomen into variable-demand, thin-market, and geographically dispersed niches — not as a policy design but as an emergent property of the cost structure. The plumber serving a rural county, the technician covering off-peak maintenance windows, and the specialist handling infrequent non-standard problems all represent natural yeoman territory. This is not a fragile assumption; it follows directly from the economics of utilisation.

#### Agency and democratic legitimacy

Beyond distributional mechanics, the yeomen model has a property welfare metrics cannot capture: people earn what they receive. Economic agency — the sense of being a contributor rather than a recipient — and the democratic legitimacy that comes from owning one's means of production are not captured in a Gini coefficient. Concentrated economic power, whether in private monopoly or state enterprise, produces subjects rather than citizens. The yeomen model is not only distributionally competitive; it is more consistent with the conditions for democratic self-governance.

#### 4.3.1 Deployment speed and tax design

A concern with capital taxation of AI is that it reduces deployment incentives, slowing the real output gains that benefit all consumers. The model captures this through a `tax_drag` parameter that shifts the automation S-curve rightward with effective tax burden. At 35% statutory rate, a blunt capital tax slows deployment by ~2.6%. A rent tax — applying only to returns above the threshold required to justify investment — reduces deployment drag by ~70% for the same statutory rate, because the marginal investment incentive is preserved.

Yeomen ownership eliminates the tradeoff entirely: an owner-operator has full incentive to deploy AI as fast as possible because they capture the return directly.

#### 4.3.2 The fiscal prerequisite for yeomen: tax code reform

The yeomen scenarios assume independent operators receive the same effective income as equivalent corporate-employed workers. This is not true under the current US tax code.

| Cost component | Annual burden | Corporate employee equivalent |
|---|---|---|
| Double FICA (employer + employee share) | ~7.65% of income | Employer pays; invisible to employee |
| Own health insurance (no employer subsidy) | ~6–8% of income | Employer-subsidised; pre-tax |
| Tax compliance and administration | ~2–3% of income | Employer-handled |
| **Effective income discount** | **~18%** | ~0% |

At the scale of full yeomen deployment — 60% of capital income to millions of independent operators — this represents approximately **$2.4 trillion per year in foregone effective income by 2035 under the modelled assumptions**. Without fiscal reform, the yeomen equilibrium requires workers to accept substantially lower effective compensation to participate, reducing the achievable yeomen fraction from the modelled ceiling.

Two policy mechanisms reduce this friction. **Tax code reform** (FICA parity for self-employed, full health deductibility) eliminates the friction directly. **Firm rebate for external contracting** — a demand-side tax credit for firms that contract work to independent operators rather than employing staff — creates the incentive on the demand side. At a 15% rebate rate, yeomen friction cost falls from $2.4T to ~$1.4T per year at t+10; a $1T/yr improvement at modest revenue cost.

#### 4.3.3 Platform capture risk

The yeomen mechanism has a critical dependency: access to competitive frontier AI capability at market rates. If frontier models remain proprietary closed systems, the economics of small-operator independence invert. The operator rents compute and models from a platform at rates set by the platform; their output is locked into the platform ecosystem. These are not independent yeomen — they are high-tech sharecroppers, capturing less value than their labour warrants and accumulating no capital.

The scenarios should be read as: *if* a competitive AI capability layer exists, yeomen fractions of 35–60% are achievable; *if* proprietary platforms maintain durable capability monopoly, the effective ceiling is substantially lower. The assumption is not that open-weight models must win outright — it is that competition among frontier providers is sufficient to prevent durable monopoly pricing. A market with three or four capable closed-weight competitors at commodity prices satisfies the condition; a single provider with no credible alternatives does not. Defending both the open-weight ecosystem and competitive market structure among closed providers are therefore structural prerequisites for the yeomen scenario.

The required regulatory intervention is **use-and-deployment non-discrimination**: platforms above a scale threshold cannot favour their own AI-powered products over third-party operators using equivalent models; vertical integration between model development, cloud infrastructure, and dominant application layers is limited; users own their data and can move it. This is net-neutrality logic applied to intelligence — precedented in telecoms, payments, and financial infrastructure.

### 4.4 The public AI infrastructure model

The public AI model treats AI compute and robots as public utilities. The state owns the capital layer and rents it via usage-fee markets — no central planning of what to produce. Firms and individuals compete freely using rented compute and robot time. The state captures the economic rent and distributes it as a citizen compute dividend.

At 90% public AI, the model produces the best distributional outcome (Gini 0.14 at t+10) and a compute dividend of $55k/yr per adult. Negative fiscal space (−$6.5T) requires explanation. Fiscal space in this model is defined as conventional tax revenue minus existing government obligations (programme spending plus $1.53T debt service). In the public AI scenario, compute usage fees — the state's primary revenue from owning the capital — are treated as flowing directly to citizens as dividend rather than through the government account. This is an intentional design choice, not a fiscal failure: it mirrors the Alaska Permanent Fund model, where resource revenue goes to citizens rather than to the state budget. The government continues to fund its operations through conventional taxes on the remaining private economy. The −$6.5T figure means the government's conventional tax base alone cannot cover existing obligations — it does not mean citizens are poor. A full implementation would allocate some fraction of usage fee revenue to government operations and distribute the remainder as dividend; the split is a policy parameter the model does not optimise.

The public AI model has a structural enforcement advantage: rent from state-owned infrastructure cannot be shifted offshore. It has a corresponding institutional risk that deserves equal treatment to the failure modes of other scenarios.

The model produces attractive public AI outcomes by holding governance quality constant and assuming the infrastructure is built on schedule, priced efficiently, and insulated from political interference. These are demanding assumptions. The governance decay analysis (§4.6) partially addresses this: public AI scenarios with decay enabled show G settling around 0.79–0.82 — better than concentrated private ownership (0.39) but below distributed yeomen (0.89). The source of that drag is different in kind: not oligarchic lobbying but bureaucratic capture, below-cost political pricing, and reduced incentives for frontier capability investment. Public enterprises in network industries have historically underinvested in capacity when pricing is set by political rather than economic logic — the result is infrastructure that distributes existing rent well but does not generate the next generation of it.

The compute dividend arithmetic — $45–93k/yr per adult by t+10–30 — only works if the infrastructure earns a return. A state compute monopoly facing sustained political pressure to lower usage fees, prioritise politically salient users, or cross-subsidise legacy industries faces the same pressures that degraded the performance of state telecoms, railways, and energy utilities before privatisation. The model does not capture this because it holds the revenue flow constant; reality would not.

The public ownership case is strongest where private regulatory capture is demonstrably worse — where incumbents have already corrupted the alternative — and weakest where the state itself is the primary capture risk. A privately owned AI infrastructure operator subject to mandated universal access and cost-based pricing enforced by an independent regulator could achieve comparable welfare outcomes; whether that regulatory independence is achievable is the genuine empirical question the model cannot answer.

### 4.5 The enforcement gap

A 50% statutory capital tax rate with 30% enforcement — representative of a small open economy — generates no redistributable surplus and in some configurations produces less revenue than a 20% rate at full enforcement.

| Scenario | Statutory rate | Enforcement | Fiscal space t+10 |
|---|---|---|---|
| Large bloc / High tax | 50% | 100% | +$5.9T |
| Small nation / High tax | 50% | 30% | −$0.2T |
| Small nation / High yeomen | 50% | 30% | +$0.8T |

Tax instruments divide sharply by enforcement robustness:

| Instrument | Enforcement | Notes |
|---|---|---|
| Land value tax | Very high | Land cannot be registered elsewhere |
| Data-centre energy levy | High | Physical metering at location |
| VAT on AI-delivered services | High | Consumption at consumer location |
| Corporate income tax on AI capital | Low | Profit-shifting is primary avoidance mechanism |
| Wealth tax on financial assets | Very low | Capital mobility requires global coordination |

Yeomen and public AI models are enforcement-immune by construction: yeomen income is earned income with low international mobility; public AI infrastructure cannot be registered offshore because the physical assets are in-country. For small and medium nations, this structural enforcement advantage of distributed ownership is not a secondary benefit — it may be the primary reason to prefer these models over high statutory tax rates. The enforcement problem, however, has a second dimension that applies even to countries that successfully distribute domestic ownership: the threat of foreign capital accumulation and knowledge-work offshoring at machine speed. This is addressed in §6.5.

### 4.6 Concentrated ownership erodes its own institutional constraints

The static model treats enforcement as a fixed policy parameter. A more realistic treatment models governance quality G(t) as a stock that decays endogenously when inequality is high and concentrated wealth has incentive and means to undermine institutions.

Under concentrated-ownership scenarios, the model produces a self-reinforcing dynamic — directionally consistent with political-economy literature on institutional capture, though not offered as a precise forecasting law:

**concentrated ownership → high inequality → governance decay → lower effective enforcement → less redistribution → higher inequality → faster decay**

By t+20 under concentrated low-tax scenarios, G(t) has fallen to approximately 0.3 in the model — losing around 70% of enforcement capacity under the modelled decay parameters. A statutory 50% rate effectively collects 15%. By t+30, G(t) approaches the model floor of 0.10.

| Scenario | G t+10 | G t+20 | G t+30 |
|---|---|---|---|
| No yeomen / Low tax | 0.665 | 0.482 | 0.390 |
| No yeomen / High tax | 0.665 | 0.482 | 0.390 |
| High yeomen / High tax | 0.847 | 0.869 | 0.886 |
| Full stack (yeomen + DAO + public AI) | 0.812 | 0.774 | 0.745 |
| Public AI 90% | 0.823 | 0.806 | 0.793 |

The concentrated scenarios are identical regardless of statutory tax rate — decay responds to ownership structure, not the rate. The high-yeomen scenario dips during the ramp-in period then recovers — G rises from 0.847 at t+10 to 0.886 at t+30 as distributed ownership actively strengthens institutions. Public AI 90% holds around 0.79–0.82: the private concentrated share is nearly eliminated (reducing oligarchic pressure), but a separate institutional drag from operating state infrastructure — political pricing interference, bureaucratic capture, underinvestment incentives — prevents full recovery to 1.0. The model distinguishes two failure modes: oligarchic erosion (fast, self-reinforcing, G → 0.39) and bureaucratic capture (slow, partially correctable, G → 0.79).

**The practical implication: static scenario comparisons understate the advantage of distributed ownership.** The high-tax concentrated scenario that appears fiscally adequate in static analysis (Finding 4.2) depends on institutional capacity that concentrated ownership, over time, removes. The 2035 snapshot looks manageable; the 2050 snapshot does not.

### 4.7 The redistribution window is narrow

AI capital returns begin at 22–28% (early oligopoly rents) and decay toward 7–10% — the model uses an approximately 11-year half-life calibrated to observed platform-era return compression, though the specific timeline is illustrative — as competition and open-source alternatives erode the premium. The fiscal surplus available from taxing AI capital is concentrated in 2026–2036.

Simultaneously, institutional capacity has not yet been eroded. Open-weight AI models already exist. The Coasian fragmentation toward yeomen structures is already beginning. The political salience of the problem is at its weakest because displacement is not yet severe.

This is the adverse timing problem: the window for effective action is open precisely when political pressure to act is lowest, and closes before displacement peaks. Each year of delay narrows the fiscal window, advances governance decay, and allows concentrated owners more time to convert economic position into political power.

The practical implication for instrument design: the more likely political economy is that a displacement crisis — not foresight — creates the political window. A proposal that requires a year of legislative drafting after the crisis arrives will not be implemented before the window closes. Pre-designing the instruments, establishing enabling authority in legislation, and piloting the infrastructure while it is still politically low-salience is itself a form of policy response. The near-term actions in §6.4 are designed with this in mind: each is executable within existing authority or with modest legislation, so that the harder instruments can be deployed rapidly when the political conditions finally arrive.

---

## 5. Scenario Comparison

| Scenario | Gini t+10 | Welfare t+10 | Fiscal space t+10 | Debt/GDP t+10 | Interest % rev t+10 |
|---|---|---|---|---|---|
| No yeomen / Low tax | 0.701 | $2k/yr | −$0.1T | 1.06x | 19% |
| No yeomen / High tax | 0.699 | $62k/yr* | +$5.9T | 0.21x | 11% |
| Moderate yeomen / Med tax | 0.512 | $62k/yr | +$2.0T | 0.80x | 15% |
| High yeomen / High tax | 0.421 | $62k/yr | +$3.3T | 0.45x | 13% |
| Public AI 90% | 0.197 | $45k/yr† | −$4.8T | 1.74x | 31% |
| High yeomen / Small nation | 0.421 | $62k/yr | +$0.8T | 1.09x | 17% |
| High tax / Small nation | 0.701 | $2k/yr | −$0.2T | 1.23x | 19% |

*\*The $5.9T annual fiscal surplus divided across displaced workers yields a capped UBI of $62k/yr — the model applies a $60k ceiling. Market income Gini remains 0.699 (essentially the same as low-tax concentrated); redistribution covers welfare needs on paper but does not address structural demand suppression, the MPC feedback loop, or the governance decay that erodes the institutional capacity to keep collecting it.*
*†Public AI 90% welfare of $45k/yr reflects the citizen compute dividend only; negative fiscal space (−$4.8T) means the state is funding the capital acquisition deficit. The model holds this constant; in practice the public infrastructure investment is front-loaded and the fiscal position improves as the asset generates returns.*

**Three structural observations:**

(1) High-tax concentrated and high-yeomen scenarios produce identical welfare at t+10 ($62k/yr) but through entirely different mechanisms. High-tax concentrated achieves this through fiscal redistribution ($5.9T surplus redistributed to displaced workers); high-yeomen achieves it through market income structure. The high-tax route is vulnerable to governance decay; the yeomen route is not. By t+20 the gap widens as concentrated-ownership governance erodes and the effective tax rate falls.

(2) The small-nation high-yeomen scenario has nearly identical market Gini (0.421) to the large-bloc equivalent and positive fiscal space (+$0.8T) — a better outcome than small-nation high-tax (Gini 0.701, −$0.2T fiscal space). Distributed ownership is viable for small nations without large-bloc enforcement leverage; high capital tax rates are not. The enforcement gap finding is not symmetric across ownership structures.

(3) The public AI scenario achieves the lowest Gini (0.197) but at persistent negative fiscal space (−$4.8T) and a debt/GDP trajectory that reaches 3.1x by t+30 under static assumptions. Under governance decay the institutional drag is real but manageable (G=0.79); the fiscal trajectory is the harder constraint.

### Robustness

**Robust across parameter ranges:**
- Enforcement gap disadvantages small open economies under any calibration of capital mobility
- Ownership structure outperforms ex-post redistribution across MPC spread variations of ±10 percentage points
- Governance decay worsens concentrated-ownership scenarios regardless of specific decay coefficients
- Tax instrument design matters more than rate for small open economies
- Yeomen tax friction reduces achievable welfare gains proportional to friction magnitude

**Fragile — highly assumption-sensitive:**
- Specific nominal GDP trajectory: sensitive to Jevons demand elasticities and material price growth assumptions
- Achievable yeomen fraction: conditional on competitive open-weight AI availability
- Energy sector Phase 2 timing: sensitive to robotics deployment speed and grid storage costs
- Quantitative welfare figures: sensitive to automation speed, MPC calibration, and sector price dynamics. Qualitative orderings are more robust than point estimates.

---

## 6. Policy Implications

### 6.1 Framework

The following is ordered by enforcement robustness and implementation feasibility.

**Layer 1 — Enforcement-robust taxes (all jurisdictions)**

- **Land value tax**: enforcement-immune, captures appreciation (land values triple by t+30 across all scenarios), discourages speculative vacancy. The land value appreciation in all scenarios represents a large, entirely unearned gain to existing landowners — the strongest case for public capture of any instrument in the model.
- **Data-centre energy levy**: physical metering, cannot be offshored. Scales naturally with AI deployment. Establishes the administrative pathway for compute taxation at near-zero friction cost.
- **Digital services VAT extension**: consumption occurs where the consumer resides; extending VAT to AI-delivered services follows the EU Digital Services Tax model and captures revenue regardless of provider location.

**Layer 2 — Yeomen fiscal prerequisites (all jurisdictions)**

Without fiscal code reform, the yeomen equilibrium is structurally disadvantaged. Two complementary instruments:
- **FICA parity and full health deductibility for self-employed**: eliminates the ~18% effective income discount on sole operators. This is not a subsidy for small business — it is removing a tax code distortion that currently subsidises large firm employment over independent contracting.
- **Firm rebate for external contracting**: a demand-side tax credit creates the incentive on the employer side, accelerating Coasian fragmentation and reducing yeomen friction cost by ~$1T/yr at modest revenue cost.

**Layer 3 — Cooperative capital access (all jurisdictions)**

- Accelerated depreciation for AI/robot capital owned by sole proprietors and cooperatives, phased out for large firms
- Cooperative lending programs for small-business AI/robot deployment
- Public compute access at cost for small operators (rural electrification model)

**Layer 4 — Commons governance infrastructure (all jurisdictions)**

- Government procurement preference for commons-governed software and AI systems (US federal IT procurement is ~$100B/yr — routing a defined share through open-credential standards bootstraps the supply side)
- Legal entity frameworks giving commons DAOs standing in contract and IP law
- Government acquisition and daoification of underutilised assets from failing businesses

**Layer 5 — Progressive compute levy (large blocs)**

Tax AI compute consumption with escalating rates above a threshold, subsidising access below it:

| Compute spend per year | Levy rate |
|---|---|
| Below $100k | Exempt |
| $100k – $1M | 10% |
| $1M – $10M | 25% |
| Above $10M | 40% |

The tax base is compute spend (API fees, cloud GPU rental, imputed value of owned hardware), not revenue — this captures internal automation that never shows up in revenue and creates a direct financial incentive to contract work to operators below the threshold.

**Layer 6 — Defend the open-weight ecosystem (large blocs, regulatory authority)**

- Challenge acquisitions of open-source AI projects by dominant platform operators under existing competition authority
- Prohibit platforms above a scale threshold from favouring their own AI-powered products over third-party operators using equivalent models
- Mandate data portability — users own their data and can move it, interrupting the data flywheel that entrenches incumbents regardless of model quality
- Prohibit exclusive dealing between hyperscaler compute providers and frontier model API providers

**Layer 7 — Public AI infrastructure and energy investment (large blocs and resource-rich nations)**

- Public compute infrastructure funded from energy taxes, land value taxes, and capital taxes during the high-rent window (2026–2036)
- Usage-fee markets for compute access with tiered social priority
- Citizen compute dividend distributed per adult
- Accelerated public investment in grid infrastructure to bring forward the Phase 2 energy transition — every year of delay is a year of unnecessarily high electricity prices

**Layer 8 — Small and medium nation strategy**

- Regional bloc coordination before unilateral capital tax measures: harmonise digital tax policy within regional blocs (AU, ASEAN, Mercosur)
- Mineral resource leverage: nations controlling AI input materials (cobalt, lithium, rare earths, copper) should require value-added processing before export
- Commons and cooperative structures as primary strategy — locally-anchored, enforcement-immune, not dependent on capital mobility constraints

### 6.2 Agentic marketplace infrastructure: transaction costs and price discovery

The yeomen scenario depends structurally on transaction costs approaching zero. Current contracting infrastructure imposes costs at every stage: search (finding counterparties), specification (agreeing terms), monitoring (verifying delivery), enforcement (resolving disputes), and tax reporting. AI-mediated agent-to-agent contracting eliminates most of these at the execution layer — but only if the underlying infrastructure is open and federated rather than private and extractive. A private platform that mediates agent commerce reintroduces the same rent extraction and lock-in that characterised the web-platform transition; the yeomen become high-tech sharecroppers paying per-transaction fees in perpetuity.

The required infrastructure has six layers, each with a distinct governance model and technical role:

```
L5  Tax Reporting     National tax authorities receive structured records automatically
L4  Settlement        FedNow (domestic) or x402 stablecoin (cross-border)
L3  Agent Negotiation A2A protocol: machine-speed proposal / counter / accept
L2  Matchmakers       Private competitive operators licensed by L1
L1  National Registry Per-country identity, reputation, contract reporting — public nonprofit
L0  International Std ITU/ISO treaty body — shared schemas, wire format
```

**What makes this different from a platform.** In a platform model, reputation data, pricing history, and buyer relationships are held by the operator and not portable. A yeoman who builds a track record on Platform A cannot take it to Platform B; the platform extracts this switching cost as a permanent rent. The federated architecture inverts this: reputation attestations are stored as hashes in the national registry (L1), with credential content held by the agent. Any licensed matchmaker (L2) can query them via open API. This is the equivalent of phone number portability — a structural guarantee against lock-in, not dependent on platform goodwill.

**Transaction cost targets.** For a yeoman running a plumbing business at $200/job, a 10% platform take-rate is material. The federated design achieves near-zero marginal transaction cost through structural means: discovery is free at L1 (any matchmaker can query the registry without per-query fees); negotiation is peer-to-peer at L3 (A2A protocol, matchmaker facilitates but does not price); settlement approaches zero (FedNow domestic, x402 stablecoin cross-border at <$0.001/transaction); tax reporting is automatic in the contract execution path at no marginal cost to the yeoman. Licensed matchmakers can charge for premium matching features — faster response, better ranking for niche skills — but not for basic access or portability. Competition among matchmakers drives rates toward marginal cost. Target: total transaction overhead below 1% of contract value.

**Price discovery.** Agent-to-agent markets have a structural price discovery problem: if buyers and sellers both use AI agents, prices can converge without any human ever observing them. This creates two failure modes — algorithmic collusion (agents coordinating tacitly on supracompetitive prices, documented in LLM-agent literature) and race-to-the-bottom compression (agents undercutting each other below the viable floor). The registry's aggregate price data is the corrective: L1 registries hold all executed contract values by category, geography, and time period. This data must be publicly available in aggregate — analogous to published wage surveys — while individual contract terms remain private. Competition authorities query the same data for collusion monitoring; the dynamic surtax mechanism (§6.3) draws on it to calibrate rate adjustments. A circuit-breaker at L3 prevents the flash-crash dynamic: if prices in a category move beyond a threshold in a short window, the registry signals matchmakers to queue rather than execute.

**Productive capital deployment.** For a yeoman to deploy their capital efficiently — robots, specialised equipment, compute — the matchmaker layer must handle physical geography, availability signalling, and idle-capacity routing. Physical tasks have location constraints that pure knowledge work does not: a robot in one city cannot serve an emergency job in another. Agent cards at L0 carry geographic service radius as a first-class field. Availability state (available now, booked until Thursday) is published continuously so buyers match against real capacity. Opportunistic bidding — a yeoman's robot is available at a discount during a slow period — is supported natively, allowing the market to absorb idle capital without requiring the yeoman to actively manage pricing. The policy does not prescribe what tasks a registered robot performs. The yeoman deploys their capital however market signals indicate; task switching is handled by the AI agent layer, not by administrative rules. Specialisation emerges from competitive dynamics, not from programme design.

**Tax reporting as a feature, not a burden.** The L5 tax reporting layer declares income at contract commitment, not at payment. This eliminates payment-routing games (routing transactions through jurisdictions with no reporting obligation) and creates a complete audit trail without any action by the yeoman. The same contract data that goes to the matchmaker goes to the tax authority. For the yeoman, this is a reduction in compliance cost. For the tax authority, it is continuous visibility into a tax base that would otherwise be entirely opaque at machine speed. The self-employment tax gap is already $300–500B/yr in the US under human-speed transactions; agent-speed commerce without this infrastructure would multiply that gap. Cross-border transactions use a shared bundle identifier that appears in both national registries simultaneously — no bilateral treaty required per country pair.

### 6.3 Yeoman viability: capital access and tax structure

Two types of yeomen emerge from this analysis, with different economics and different policy needs. **Type A yeomen** deploy physical capital — robots, specialised equipment, vehicles — and are the primary target of the robot financing programme. Their COGS includes non-deflating components (materials, insurance, licensing) that create a durable price floor. **Type B yeomen** deploy knowledge capital: AI agents, curated prompting harnesses, evaluation workflows, and professional credentials and legal accountability. Fine-tuning proprietary models is not assumed — the differentiation is in workflow quality, domain-specific evaluation pipelines, and verified professional accountability, not in bespoke model weights. Type B yeomen can often be self-financed (initial capital costs are lower than physical robots), but face faster margin compression as commodity AI access lowers the barrier to equivalent capability. The distinction matters for programme design: subsidised financing is most effective for Type A; credential infrastructure and professional licensing reform are the levers for Type B.

**The competitive dynamics of a fully automated economy.** When robots perform physical tasks and AI agents perform knowledge tasks, all task prices converge toward the opportunity cost of the underlying productive capital — robot-hours or compute tokens. The buyer's willingness to pay is anchored by what it would cost them to deploy equivalent capital directly. In competitive equilibrium among large corporate operators with scale advantages (volume purchasing, higher utilisation, lower cost of capital), the market-clearing price settles at:

```
market_price = corporate_COGS × (1 + target_return)
```

where corporate COGS already reflects economies of scale. A yeoman whose own costs exceed this floor cannot survive on price competition alone. The question is whether a combination of structural advantages and policy instruments makes the yeoman's effective floor competitive without requiring permanent operating subsidy — which would constitute a distortion to resource allocation that reduces overall productivity.

**Two structural advantages of small operators.** Yeomen have natural cost advantages that partially offset their scale disadvantage and do not require ongoing policy support to maintain.

*Idle capital opportunity cost.* A corporate operator must charge full capital amortisation on every robot-hour to justify its return on investment. A yeoman whose robot would otherwise be idle faces a marginal cost on the next job of near zero — only energy, materials, and tokens. In markets with variable or lumpy demand, this allows yeomen to undercut corporate floor pricing at the margin without destroying their overall economics. The corporate fleet faces utilisation pressure that the single-robot yeoman does not.

*Subsidised financing.* A government loan at 2% versus a corporate cost of capital at 8–10% reduces annual capital cost by approximately $12,000 per year per $150,000 robot. This is a direct and permanent cost advantage that persists for the loan term and does not create ongoing operating distortions — it is a one-time capital allocation, not a per-transaction subsidy. The redistribution happens at the capital acquisition stage; the market then operates without further policy intervention.

**The concrete viability case.** Modelling a 2-robot plumbing business (residential and light commercial, 2,400 jobs per year, $93 average materials per job) with subsidised financing reveals the following trajectory:

| Year | Market price/job | Yeoman net income | Status |
|------|-----------------|-------------------|--------|
| 2026 | $390 | ~$468k | Windfall — strong entry incentive |
| 2029 | $280 | ~$278k | Well above target |
| 2031 | $220 | ~$171k | Comfortable |
| 2033 | $170 | ~$80k | Just above $75k target |
| 2035 | $140 | ~$27k | Below target — surtax activates |

Several structural properties of this trajectory deserve attention. First, robot cost deflation broadly tracks price compression — as market prices fall, so does the cost of the next robot purchase, making the margin stickier than a static analysis suggests. Second, non-deflating costs — materials, vehicle, insurance, licensing — create a structural price floor around $100–120 per job. Physical service markets cannot compress to pure token-cost commodities because the non-computational inputs do not follow the same deflation curve as hardware. Third, the early years generate windfall income that, if reinvested in additional capital, builds the portfolio that sustains the yeoman through the compressed-price phase. The financing programme functions best as a capital accumulation mechanism, not a permanent income supplement.

**Exhibit: 2-robot plumbing business P&L under price compression**

*Assumptions: $150k robot × 2, subsidised financing at 2% (saving ~$12k/yr/robot vs market rate), 300 working days/yr, 4 jobs/day/robot, $93 average materials per job passed through at cost, 22% effective income tax on profit.*

| Year | Market price/job | Annual revenue | Total COGS | Net income | Status |
|------|-----------------|---------------|-----------|-----------|--------|
| 2026 | $390 | $936k | $336k | ~$468k | Windfall |
| 2029 | $280 | $672k | $336k | ~$278k | Well above target |
| 2031 | $220 | $528k | $336k | ~$171k | Comfortable |
| 2033 | $170 | $408k | $320k* | ~$80k | Just above $75k |
| 2035 | $140 | $336k | $305k* | ~$27k | Surtax activates |

*\*COGS falls modestly as robot amortisation declines with hardware price deflation.*

Price for $75k net income with 2 robots and subsidised financing: **~$180/job**. Current market price is more than double this threshold, providing a decade of margin before the surtax backstop is needed.

**The self-service boundary.** As general-purpose robots become widely owned, buyers will handle routine tasks themselves — basic maintenance, simple repairs, cleaning — rather than contracting out. This does not eliminate the yeoman market; it concentrates it. What remains is work requiring specialised equipment the buyer does not own, licensed professional accountability, liability insurance, or specialist AI training for non-standard problems. These categories share a structural property: the buyer's willingness to pay is anchored to the value of the outcome (avoiding water damage, passing a building inspection) rather than to the cost of the robot's time. This anchoring protects margins even as hardware prices fall. The plumber who builds a business around emergency response and non-standard diagnosis is competing on a different price curve than the one set by corporate robot-hours.

**The knowledge work caveat.** Pure knowledge tasks — AI agents executing commodity research, analysis, or code review — commoditise faster than physical work because there is no capital moat. A buyer can run equivalent agents at token cost, and as buyer AI improves the coordination and quality-verification overhead that currently justifies a premium above token cost approaches zero. Knowledge-only yeomen are viable over the long term only if they hold a non-replicable position: a professional licence creating legal accountability, a well-curated domain workflow or evaluation harness that consistently outperforms commodity prompting, or verified reputation that materially reduces buyer risk. (Fine-tuning proprietary models is not assumed as a durable moat — training costs are high relative to expected returns for most small operators, and the capability gap between fine-tuned and well-prompted frontier models narrows with each model generation.) Without one of these, commodity knowledge work should not be the primary target of the robot financing programme. The programme should prioritise general-purpose physical capital — robots that can be redeployed across task categories as market conditions shift.

**Progressive robot income surtax — design and timing.** When price compression eventually reaches the point where a small operator cannot earn $75k net from a 2–3 robot business (modelled around 2034), a progressive robot income surtax on large operators raises their market floor, creating headroom for yeomen. The mechanism: with surtax T on large operators, their minimum viable price rises to COGS × (1 + return) / (1 − T). Yeomen, taxed at a lower rate or zero, earn the spread between the corporate-set market price and their own lower floor.

The key design principle is that this surtax is computed from registry aggregate data — the same data that enables price discovery — rather than set as a fixed statutory rate. High yeoman utilisation and rising prices signal the market is healthy; the surtax can be reduced. Falling utilisation and compressed margins signal the floor is under pressure; the surtax rises. The instrument is therefore countercyclical by design and does not require legislative action to adjust.

The anti-avoidance mechanism is the Yeoman Entity: a legal structure in which a single natural person is the beneficial owner, robot fleet value is below a capital threshold (suggested $500k), and all entities with the same principal are aggregated for tax purposes. A large corporation cannot claim preferential rates by fragmenting its fleet into single-robot LLCs because common ownership is attributed regardless of structure. Registry registration and Yeoman Entity status are the same act — the entity's DID, productive capital, reputation, and tax treatment are unified in the public infrastructure.

**Assessment of sufficiency.** The combination of public robot financing, the federated marketplace infrastructure, and a conditional progressive surtax is likely sufficient to maintain a viable yeoman class across most physical task categories, for the following reasons. Early windfall income (2026–2034) funds capital accumulation before compression arrives. Non-deflating costs maintain a structural price floor even in fully commoditised markets. The market self-selects yeomen into specialist, licensed, liability-bearing work where margin anchoring to outcome value is strongest. The surtax activates from observable data, adjusts dynamically, and is self-funding through the mechanism that its revenue reduces yeoman capital costs, which in turn reduces the surtax required at equilibrium. The alternative — doing nothing — replicates concentrated ownership of productive capital at larger scale and higher speed than previous transitions. The productivity gains of automation accrue entirely to whoever owns the robots first. The proposed instruments are, individually, modest. Their combination is structurally robust precisely because each addresses a different part of the competitive gap: financing reduces the capital cost disadvantage; the marketplace reduces transaction cost disadvantage; the surtax, if needed, addresses the residual scale advantage. No single instrument needs to close the entire gap.

### 6.4 Near-term actions (2026–2027)

The redistribution window is open now. The following are achievable within existing authority or with modest legislative change.

**Tax base transition (executive authority or simple legislation):**
- IRS: implement the $600 1099-K threshold — delayed three times since 2022; recovers $8–12B/yr of unreported self-employment income at no cost
- EPA/Treasury: pilot a compute energy levy — data centres already report energy consumption to EPA; a joint agency pilot establishes the administrative pathway
- Treasury/BEA: separate AI capital income in national accounts — currently embedded in corporate income; a reporting requirement creates fiscal visibility before the transition accelerates

**Yeomen fiscal reform (legislation, moderate political difficulty):**
- Extend full FICA parity to self-employed on first $200k of income
- Make health insurance fully deductible from self-employment income (currently only from income tax, not SE tax)
- Create a firm rebate at 10–15% for verified external contracting to sole operators

**Commons and yeomen infrastructure (appropriations and procurement):**
- Federal IT procurement pilot: route a defined share of SBIR/STTR Phase II contracts through open-credential-standard procurement
- SBA compute credit: extend SBA 7(a) loan eligibility to AI compute expenditure for small operators
- Commons legal entity pilot: three to five states create "Digital Commons Cooperative" entity frameworks under cooperative statute amendments

**Fiscal visibility (analytical, minimal political cost):**
- CBO mandate: expand baseline to include annual AI transition projections — displacement rates, nominal GDP trajectory, fiscal capacity under current policy
- OMB/Treasury: commission a 10-year AI transition fiscal stress test

### 6.5 The small open economy problem: automation arbitrage and foreign accumulation

The model's small-nation scenarios (§4.5) capture domestic enforcement weakness — capital flight and tax leakage. They do not capture a second and distinct vulnerability: a large country that runs concentrated-ownership automation at the cost of domestic welfare accumulates an enormous capital pool. When domestic returns compress under diminishing returns, that capital seeks external assets. Small open economies — Switzerland, Belgium, Singapore, the Netherlands — are natural targets. Their assets are high-quality, their capital accounts are open, and their regulatory frameworks were designed for a world in which large foreign capital pools moved slowly.

This section describes the attack mechanism and the policy response. There are two distinct vectors.

#### 6.5.1 Asset accumulation: death by a thousand cuts

The standard defense against foreign asset accumulation is investment screening — CFIUS in the US, the EU FDI Regulation of 2019, Switzerland's ORIA. These are designed to catch large transactions in strategically sensitive sectors. They are the wrong instrument for AI-era accumulation.

Distributed domestic ownership — the yeoman model — reduces the concentration of *domestic* capital but creates a new vulnerability to *foreign* piecemeal acquisition. If productive capital is held by 200,000 small operators, each holding $50k–$500k of registered assets, a foreign sovereign wealth fund or state-backed vehicle can acquire 1–2% of each position without triggering any single review threshold. No individual transaction is large enough to attract regulatory attention. The aggregate effect — foreign control of 15–20% of the domestic productive capital base — is achieved without a single reviewable event.

The existing legal architecture has no answer to this. Deal-size thresholds, sector-by-sector review, and country-of-origin prohibitions all require a visible, large, discrete transaction. The required instrument is different in kind: **aggregate beneficial ownership tracking** at the registry level.

The federated registry (§6.2) already records the DID and beneficial ownership of every registered productive-capital entity. The extension required is an automatic computation of aggregate foreign-held fractions by sector, updated in real time, with threshold-triggered review at the sector level rather than the deal level. A country sets: "when foreign beneficial ownership across all registered entities in the [energy / AI infrastructure / real estate / manufacturing] sector crosses 10%, the next acquisition in that sector triggers review regardless of individual transaction size." This is new — it does not exist in any jurisdiction today — but it is technically straightforward given the registry architecture. Without the registry, it is administratively impossible. With it, it requires one additional query.

**Land value tax as automatic defense.** For real estate specifically, investment screening is not the right instrument even at the aggregate level. Foreign buyers acquire real estate for capital preservation and appreciation, not strategic control. The correct defense is a land value tax (LVT) — it is enforcement-immune, applies identically to domestic and foreign owners, and reduces the attractiveness of real estate as a pure capital store by converting expected appreciation into an annual tax obligation. An LVT does not restrict foreign ownership; it simply removes the primary economic motive for holding land as a speculative asset. Jurisdictions with LVT do not need separate foreign-ownership caps because the instrument already internalises the scarcity rent that drives accumulation. This is not incidental — it is the design property that makes LVT the correct instrument for this specific threat vector.

**Reciprocity as a default rule.** For non-real-estate assets, the cleanest defense that survives WTO scrutiny is reciprocity: a foreign entity may acquire domestic productive capital on the same terms that domestic entities may acquire equivalent assets in the foreign jurisdiction. If Country A's capital account is closed to inbound investment from Country B's citizens, Country B applies equivalent restrictions to Country A's capital. This is non-discriminatory in the WTO sense (it applies the same rule regardless of which foreign country), directly addresses the asymmetry that creates the vulnerability, and does not require naming China or any other country explicitly. The EU and UK are both moving toward reciprocity frameworks for strategic sectors; small open economies should push for their formalisation.

#### 6.5.2 Knowledge work offshoring at machine speed

The asset accumulation problem is visible — it involves transfers of ownership title. The knowledge-work offshoring problem is invisible and potentially larger.

In a world of agent-to-agent commerce, a Belgian law firm, consulting practice, or engineering company can procure AI agent services through the federated marketplace from the cheapest provider globally. A Chinese datacenter running at $0.001 per 1,000 tokens — a cost achievable when labour costs are low, energy is subsidised, and compute is scaled to national policy priority — can consistently underbid every domestically-operated AI agent for every knowledge-work contract. The specification of the task and the consumption of the output remain in Belgium. The computation — and therefore the value-added, the employment, the margin — is offshore.

This is offshoring, but it is categorically different from the offshoring that previous policy responses were designed for. Previous offshoring moved functions over months, involved language friction, time-zone friction, quality variance, IP exposure, and management overhead that created natural limits. AI offshoring has near-zero friction: switching a workload from a Brussels datacenter to a Beijing one requires changing an API endpoint. A company can shift its entire knowledge-work compute overnight. There is no equivalent of factory relocation costs to create a natural brake on the speed of transition.

The accounting problem this creates is not yet resolved in any jurisdiction. Current GDP accounting attributes value-added to where production occurs. If the computation producing a Belgian company's legal research, financial analysis, or engineering output occurs in a foreign datacenter, the value-added is foreign regardless of where the output is consumed or what professional signs off on it. The Belgian company's contribution to domestic GDP, for that function, approaches zero. At scale — if most knowledge work in small open economies migrates to cheapest-compute providers — the domestic GDP contribution from the knowledge sector falls not because the work stops happening but because the computation leaves.

The fiscal corollary is direct: the income that previously paid Belgian knowledge workers and generated income tax, social contributions, and VAT is replaced by a subscription fee to a foreign AI provider. If that provider is incorporated in a zero-corporate-tax jurisdiction (a reasonable assumption for a Chinese state-backed competitor), the tax base loss is total.

**A new accounting framework is needed.** Three principles should govern it:

*Value attribution at point of accountability, not compute.* A Belgian lawyer who specifies the task, reviews the output, and bears professional liability for the advice has contributed Belgian value-added regardless of where the tokens were generated. The professional credential — the licensed accountability layer — is the locus of value creation and should be the locus of taxation. This is not a novel principle; it is already how professional services are taxed when junior associates do the drafting. The extension to AI is a reclassification, not a new instrument. It requires tax authorities to define "accountable output" as distinct from "compute" and to tax the former at the location of the accountable professional.

*AI service imports as taxable imports.* API calls to foreign AI infrastructure are currently invisible to trade statistics and largely invisible to VAT systems (digital services taxes apply to platforms, not to compute providers selling to businesses). They should be treated as service imports subject to VAT at point of consumption, with the same enforcement mechanisms as other digital service imports. The EU VAT system already captures this in principle for B2C transactions; the extension to B2B AI compute procurement is a classification decision, not a structural change.

*Compute sovereignty floors for strategic sectors.* For sectors where the accountability argument is insufficient — national security, critical infrastructure, classified research — a minimum domestic compute floor is warranted. A defined percentage of AI compute for specified categories must run on infrastructure under domestic or allied-jurisdiction control. This is analogous to domestic content requirements in manufacturing and is already implicit in frameworks like France's SecNumCloud qualification and the EU AI Act's requirements for high-risk AI systems. Formalising it as a cross-sector compute-origin requirement for strategic categories — and defining "allied jurisdiction" explicitly — is the coherent extension.

#### 6.5.3 The registry as the accounting mechanism

Both problems share a structural property: they are invisible without the federated registry infrastructure and manageable with it.

Without the registry, piecemeal foreign asset accumulation cannot be tracked in aggregate. With it, beneficial ownership across all registered entities is a query. Without the registry, AI agent-to-agent contracts are opaque — there is no systematic record of which computation happened where, who paid whom, and what value was attributed where. With it, every executed contract carries the agent's registration jurisdiction, the compute location, the contract value, and the tax record — all in L0 format, all in the same ledger that feeds the tax authority.

The federated registry was motivated in this paper primarily as a domestic instrument: reducing transaction costs, enabling automatic tax reporting, preventing platform capture of the agent commerce layer. Its strategic value for small open economies adds a second and independent justification: it is the infrastructure that makes foreign accumulation and offshoring-at-scale legible, and legibility is the precondition for any regulatory response.

**The EU dimension for Belgium.** Belgium's leverage on both problems runs through Brussels, not solely through its domestic legislature. The EU FDI Regulation needs an extension to handle aggregate piecemeal accumulation. The EU VAT system needs a B2B AI compute classification. The EU AI Act's compute sovereignty requirements need operationalisation. Belgium, as a member state with Brussels as a regulatory hub, has standing and incentive to push all three. Its interests here align with France and Germany — both of which are also vulnerable to the knowledge-work offshoring mechanism — creating a natural coalition.

**The Swiss position is harder.** Switzerland is outside the EU and has a deeply embedded open-capital-market culture. Its bilateral agreements with the EU do not give it access to EU-level investment screening. Its FDI framework (ORIA) covers critical infrastructure but not AI capital or knowledge-work compute. The Swiss response must rely more heavily on: the LVT instrument for real estate; unilateral reciprocity requirements for AI-sector acquisitions; and a domestic compute sovereignty requirement for the Swiss financial sector — which is already heavily regulated and would accept a compute-origin rule as an extension of existing data residency requirements. Switzerland's position in the global financial system also gives it leverage it has not yet used: Swiss banks and clearing infrastructure are a chokepoint for cross-border capital flows, including the capital flows that would fund foreign acquisition of Swiss assets. Conditional access to that infrastructure for jurisdictions that do not reciprocate on investment screening is a credible instrument that does not require EU coordination.

---



### 7.1 Irreducible uncertainty

The model cannot anticipate how the system will react to a change of this magnitude. Structural transitions reorganise not just quantities but the categories through which those quantities are understood: new firm types, new contracting forms, new household arrangements, new political coalitions, new institutions built for circumstances that have no direct precedent. None of this is in the model. None of it could be. We chose to build a parametric scenario tool and run wide sensitivity analysis rather than attempt a detailed prediction precisely because the latter would misrepresent what is knowable.

The sensitivity range we ran is deliberately broad: ten policy dimensions, automation speeds spanning a 3x ratio, capital tax rates from 20% to 50%, enforcement from 30% to 100%, and four distinct ownership archetypes (concentrated, distributed-yeomen, commons-DAO, public infrastructure), in combination. Across that range, the same structural relationships reappear: the MPC differential between concentrated and distributed income dominates distributional outcomes; instrument design dominates enforcement-weighted revenue; ownership structure dominates inequality more than tax rate does; governance decay compounds in the same direction wherever concentration persists. These are the directional relationships we think survive most reasonable disagreements with the model's specifics. The point-estimate trajectories — nominal GDP in 2035, specific Gini values, welfare levels — should be treated as illustrative scenario outputs, not forecasts.

### 7.2 What we deliberately chose not to predict

**Automation timing and depth.** We do not know whether rapid AI takeoff will occur within our modelled window, or at all. We run scenarios across a range of speeds (5, 9, 14 years to knowledge-work automation midpoint) because the range of expert opinion is at least that wide, and narrowing it would falsely imply we know more than we do. Our policy recommendations are framed as conditional on rapid automation occurring, not as claims that it will.

**Labour market adaptation and complementarity.** We do not model the reallocation of displaced workers into new occupations that do not yet exist, the creation of entirely new categories of employment, or the household-level decisions that would shape labour supply in a world where most current jobs are automatable. These are exactly the dynamics previous automation waves turned on. We cannot reason credibly about their post-AI form. More fundamentally, the scenario presented here is deliberately focused on a world where automation is fast and broad enough that the standard adjustment channels — occupational churn, new task creation, wage bargaining, gradual diffusion — are insufficient to absorb displacement within a policy-relevant timeframe. If automation is slower, more complementary with human labour, or concentrated in narrower task categories than modelled, the distributional pressures are proportionally reduced and the urgency of the policy instruments described here is lower. The exercise does not argue that this complementarity-dominant outcome is unlikely; it argues that the instruments needed if it fails to materialise should be designed now, when they can be. Readers who believe AI-human complementarity will dominate should take the scenario as a contingency plan rather than a prediction.

**Political response.** We do not model the political coalitions that would form, the parties that would rise or collapse, the tax reforms that would pass or fail, or the populist movements that would emerge in response to visible displacement. Our policy recommendations describe what *would work* if implemented; they are silent on whether implementation is politically feasible.

**Frontier capability advancement.** We treat AI capability gain as exogenous to ownership structure. In reality, a geopolitical race in which concentrated private models reach a higher capability frontier faster is possible and would change the comparative analysis between private-concentrated and public AI scenarios in ways we cannot quantify.

**Institutional innovation.** We do not model the new institutions that would be built — cooperative ownership vehicles, data dividends, commons DAOs, public compute utilities — because the specific forms they would take depend on political, legal, and cultural decisions we cannot anticipate. The model treats these as parameters because the alternative is pretending to know something we do not.

### 7.3 Known sensitivities within the modelled frame

**Scenario bundling.** Each ownership regime in the model bundles several variables simultaneously — ownership structure, market openness, platform regulation, tax enforcement capacity, and institutional quality all co-vary across the scenario archetypes. This makes the scenarios narratively coherent but analytically less clean than a controlled comparison. A reader should not conclude that ownership structure alone drives the distributional differences; in practice, ownership, market structure, and institutional capacity co-evolve and are hard to separate. The exercise compares plausible political-economic packages, not clean single-variable treatments.

**Nominal GDP trajectory.** The finding that nominal GDP grows depends on Jevons demand elasticities (~1.0 for physical goods), material price growth (+3%/yr; see Appendix A), and the two-phase energy sector timing. Inelastic demand, faster material price appreciation, or delayed Phase 2 transition would shift the trajectory. The qualitative finding — that the economy pivots in composition rather than shrinks — is more robust than any specific GDP figure.

**Yeomen platform dependency.** Whether yeomen are genuinely independent or become high-tech sharecroppers depends on the open/closed dynamics of frontier AI model markets. Scenarios with yeomen fractions above 30% are conditional on continued open-weight availability. This dependency is structural but external to the model.

**Energy Phase 2 timing.** The transition from infrastructure-buildout to cheap-energy phase depends on robotics maturity, grid storage costs, and the policy environment for solar deployment. Our coupling to automation speed (`mid × 1.5`) captures the mechanism but may over- or under-estimate the lag.

**Public AI and commons failure modes are understated.** The model treats public AI infrastructure as a well-functioning utility and commons DAOs as effective self-governing entities. Both face institutional challenges not modelled: public compute risks thin usage-fee markets, lobbying for subsidies, and reduced investment incentives; commons governance faces de facto control by active minorities and free-riding.

**Governance decay is smooth.** Empirical institutional collapse is lumpy and event-driven — specific appointments, budget decisions, legislative changes — not smooth decay. The doom loop structure is directionally correct; the timeline is not empirically grounded.

**Welfare measures are nominal.** The model measures welfare as nominal cash transfers. Scenarios with aggressive AI deployment may produce high real living standards alongside low nominal welfare and high Gini. Cross-scenario comparisons should be read as nominal, not real.

### 7.4 What the reader should take from the model

Take the relationships, not the numbers. The model is a structured way to make an argument about *which* policy instruments are robust to *what kind* of structural change, and *why*. Every specific figure in this paper would be improved by a better model, better data, and more time. The structural claims — that ownership dominates redistribution, that instrument design dominates rate, that governance decay compounds, that distributed-ownership equilibria have fiscal prerequisites — are the part we think survives most reasonable disagreements with our assumptions. That is the conversation starter. If the reader disagrees with a parameter, the model is open source; they can change it and run it. The framework for thinking about the problem is the contribution.

---

## 8. Conclusion

Three conclusions emerge from the scenario exercise.

**In this model, the distributional problem is not about economic size — it is about economic composition.** Real output nearly doubles in a decade under fast automation. The nominal economy grows. The problem is that the income from that growth accrues to owners of AI and robotic capital, which the existing tax code was designed to collect from workers. Redistribution from concentrated capital income can cover welfare needs — the high-tax concentrated scenario shows this — but it does not address the structural suppression of demand, the MPC-driven feedback loop that shrinks the human economy, or the governance decay that erodes the institutions required to keep collecting. Ownership structure addresses all three simultaneously.

**Build the institutional window before it closes.** The fiscal capacity to fund structural change — public compute infrastructure, cooperative capital pools, yeomen fiscal reform, commons governance frameworks — is greatest before 2035. Institutional capacity has not yet been eroded. Open-weight models exist. Coasian fragmentation toward independent operators is already beginning through market forces. Each year of delay simultaneously narrows the fiscal window, advances governance decay, and allows concentrated owners more time to convert economic position into political power. The political salience of the problem is weakest in precisely the period when action is most effective.

**Match instrument to jurisdiction.** Large blocs with consumer market leverage can enforce capital income taxes and fund public AI infrastructure. Small and medium nations should prioritise enforcement-immune instruments — land value taxes, energy levies, commons governance, mineral resource leverage, and regional coordination — over high statutory capital tax rates that cannot be collected and may accelerate capital flight. For all jurisdictions, the progression is: first get capital into small operators' hands through subsidised financing; let market dynamics run for a decade; activate a progressive robot income surtax on large operators only when price compression has eroded small-operator margins below a viable floor. The surtax is computed from registry data — the same infrastructure that enables open contracting — so no separate monitoring apparatus is needed. The instruments reinforce each other: open marketplace generates the price data that calibrates the surtax; the surtax funds the financing programme that lowers yeoman capital costs; lower capital costs reduce the surtax required at equilibrium. Asset-owning DAOs governed to keep a narrow core reinforce this further on the demand side — by routing operational spending through the marketplace to independent operators, they generate the recurring contract flows that sustain yeoman income between individual consumer engagements.

**The choice between yeomen and public AI is not primarily economic.** The model shows public AI achieving the best distributional outcomes on paper — Gini 0.20 at t+10, compute dividend of $45k/yr — but these numbers are conditional on a set of institutional assumptions the model holds constant and history gives us reason to question. The governance decay extension shows public AI settling around G=0.79–0.82: real institutional friction, not the oligarchic doom loop, but a persistent drag from political pricing and bureaucratic capture. The yeomen model achieves comparable distributional outcomes conditional on a narrower and more defensible commitment: defending the open-weight AI ecosystem that already exists and enforcing non-discrimination rules against platform capture. Their failure modes differ in kind. Public AI fails expensively and potentially irreversibly if the state monopoly is captured — the infrastructure is there but it serves political rather than economic ends. Yeomen policy fails gradually and visibly as platform capture extends, with more opportunity for course correction. The asymmetry in reversibility, not the headline Gini, is the stronger argument for the yeomen approach.

There is also a dimension the model cannot measure. Public AI produces better-distributed material outcomes; the yeomen model produces people who *earned* what they have. Economic agency, social dignity, and the democratic legitimacy that comes from owning one's means of production are not captured in a Gini coefficient. The choice is ultimately a values question. It should be stated plainly rather than dissolved into welfare metrics.

The worst outcomes are not inevitable. They require a specific conjunction: fast automation, concentrated ownership, and fiscal failure simultaneously. Each is independently addressable. Addressing any one substantially improves outcomes. Addressing all three produces distributional outcomes better than today's baseline.

---

## Appendix A: Physical Goods Material Constraints — A First-Principles Assessment

The physical goods model assumes material prices appreciate at ~3%/yr near-term. This appendix examines whether that assumption is grounded in actual reserve data and demand trajectories, with particular attention to materials without ready substitutes.

The core finding mirrors the energy analysis: **supply constraints are predominantly temporal, not geological.** Physical reserves are generally adequate over a 35-year horizon. The binding constraint is the mismatch between demand acceleration (non-linear, faster than straight-line forecasts suggest) and supply response lead times (17–29 years for new mines). This crunch window — roughly 2026–2042 — is the period of most severe price pressure, and it coincides with the most capital-intensive phase of the AI/robotics buildout. Robotics then resolves most constraints by lowering the economic grade threshold for extraction.

**The demand forecasting problem.** Standard industry projections model demand growth as a roughly linear function of policy targets or announced EV sales. This understates the actual trajectory for two structural reasons. First, AI and robotics deployment accelerates across sectors simultaneously rather than sector-by-sector, generating correlated demand spikes across multiple materials at once. Second, each technological enablement unlocks the next: cheap solar enables green hydrogen; green hydrogen enables green steel; green steel enables lower-cost infrastructure; lower-cost infrastructure enables more renewable deployment. These cascades mean demand for copper, rare earths, and lithium grows faster than naive extrapolation from any single sector implies. The 2040 demand figures below should be treated as conservative floors, not central estimates.

---

### Copper — Temporal Crunch, Not Geological Scarcity

**Reserves and resources.** USGS 2023 data: 890 million tonnes (MT) identified reserves; 2.1 billion tonnes (BT) identified resources; ~6.3 BT estimated total including undiscovered. At 42 MT/yr demand by 2040, even the conservative reserve figure gives 21 years, the total potential >150 years at elevated rates.

**The supply crunch.** Current mine production: ~22 MT/yr. Recycled: ~8.7 MT (32% of demand). IEA projected demand 2040: ~42 MT — a 50% increase driven by EVs (+6.3 MT), data centres (+2.5 MT), grid expansion (+1.0 MT), and on-premise robotics (unquantified but additive). Average new mine lead time: 17–18 years globally; 29 years in the US permitting environment. Mines announced today cannot begin significant production before 2040. Even at peak mine production, a ~10 MT/yr supply deficit is plausible by 2040.

**Why this resolves.** Copper is not rare — it is merely expensive to extract at today's economic grade thresholds (~0.2% ore grade). The ~700 MT of copper already in global building and infrastructure stock is infinitely recyclable; recycling currently captures 32% of demand and rising. Robotics lowers extraction cost non-linearly: sub-economic deposits become viable when extraction labour is automated, shifting the grade threshold from ~0.2% to ~0.08–0.10%. Deep-sea polymetallic nodules in the Clarion-Clipperton Zone contain an estimated 250 MT of copper at average grades comparable to today's mines — available to whoever resolves the environmental permitting problem. None of these sources come online during the supply crunch window.

**Price trajectory.** Near-term (2026–2040): +4–5%/yr as demand outpaces supply response, consistent with USGS and Wood Mackenzie projections. Medium-term (2040–2050): price appreciation flattens as robotics mining scales and secondary supply deepens. Long-term (2050+): mild deflation as extraction costs fall and above-ground stock recirculates efficiently. The model's +3%/yr flat assumption is slightly conservative on near-term price pressure but reasonable on the 35-year average.

---

### Rare Earth Elements — Geopolitical Concentration, Not Geological Scarcity

REEs are misnamed: neodymium, praseodymium, dysprosium, and terbium — the four most relevant for AI/robotics applications (permanent magnets in motors and generators) — are moderately abundant in the earth's crust. The constraint is not geological.

**What's actually scarce: processing concentration.** China accounts for 94% of sintered permanent magnet production and is the leading refiner for 19 of 20 critical minerals (average market share ~70%). This is a processing and refining concentration, not a reserves concentration. Western nations hold significant REE deposits (Mountain Pass in the US, Bayan Obo in Mongolia, MP Materials capacity) but lack the full processing chain to convert ore to finished magnets at competitive cost.

**Demand-supply mismatch.** Neodymium demand is projected to grow 48% by 2050. Under current supply trajectories, demand could exceed available non-Chinese supply by 250% by 2030. This is an extreme estimate conditional on no Western supply chain buildout, but the directional concern is real: a single country controlling 94% of a critical input for industrial motors is a concentration risk of a different character than a geological reserve limit.

**Substitution pathways.** Induction motors, which require no rare earth magnets, are technically viable for most EV and industrial applications at a 10–15% efficiency penalty — significant but not prohibitive. Switched reluctance motors eliminate REEs entirely. Direct-drive wind turbines can be redesigned with gearbox architectures that reduce or eliminate permanent magnet requirements. These design alternatives have lead times of 5–10 years to deploy at scale through product redesign cycles.

**Assessment.** REE supply is a near-term geopolitical vulnerability — observable already in China's export controls on gallium, germanium, and antimony — rather than a geological scarcity. It warrants policy response (supply chain diversification, downstream processing investment, motor technology redesign incentives) but does not fundamentally constrain the physical goods or energy sector nominal trajectory modelled here.

---

### Cobalt — Rapidly Being Engineered Around

Cobalt presents a different picture: the constraint is real but diminishing as battery chemistry evolves.

**Reserves.** Global cobalt reserves: ~10 MT identified, 150+ year supply at current rates on land, and an estimated 725-year equivalent in ocean floor polymetallic nodules. The DRC holds 48% of reserves and produces 68% of global mine supply. The concentration risk is political/supply chain, not geological.

**The substitution trajectory.** This is the most material development. LFP (lithium iron phosphate) batteries, which contain zero cobalt, overtook cobalt-containing NCM chemistries for the first time in 2023 (45% vs 43% global EV battery market share). CATL began mass production of sodium-ion batteries in late 2025, which require neither cobalt nor lithium, using sodium carbonate (soda ash) — effectively unlimited in supply. The trajectory is clear: cobalt demand is likely to *peak and decline* within the model window as chemistry innovation accelerates. DRC export restrictions announced in 2025 will accelerate this transition by raising cobalt prices, making the switch to LFP and sodium-ion more economically compelling.

**Assessment.** Cobalt is not a long-term material constraint. It is a transitional exposure whose timeline for resolution is measured in years, not decades. It does not require significant modelling attention beyond noting that the DRC concentration creates short-term supply chain risk.

---

### Lithium — Abundant Geology, Copper-Like Timing Problem

Lithium reserves are very large (USGS 2023: 28 MT identified reserves, ~98 MT resources globally), but supply faces the same lead-time mismatch as copper. Demand is projected to grow 5x by 2040 under IEA STEPS — and, per the demand forecasting caveat above, faster if AI/robotics deployment is non-linear.

The specific lithium supply constraint differs from copper: hard rock lithium mines take 7–10 years to develop (faster than copper), but lithium brine operations in South America's Lithium Triangle require 3–5 years of evaporation pond buildup plus political negotiation with Chile, Argentina, and Bolivia. The geological abundance is not in question; the timing mismatch is shorter but still relevant for the 2028–2037 window.

Sodium-ion chemistry, if it scales as CATL projects, reduces lithium demand growth for batteries substantially, relieving this constraint before it becomes binding.

---

### Synthesis: A Hierarchy of Material Constraints

| Material | Constraint Type | Peak Pressure | Self-Resolving? | Main Mechanism |
|---|---|---|---|---|
| Copper | Temporal / mine lead-time | 2028–2042 | Yes, ~2045 | Robotics mining + recycling scale |
| Rare earths | Geopolitical / processing | Now–2035 | Partially | Western processing buildout + motor redesign |
| Lithium | Temporal / mine lead-time | 2028–2037 | Yes, ~2040 | Sodium-ion substitution + brine expansion |
| Cobalt | Chemistry-specific | Now–2030 | Yes, ~2030 | LFP + sodium-ion transition |
| Nickel | Manageable | 2028–2035 | Yes | Indonesia expansion + LFP shift reduces demand |
| Silicon (chips) | Fabrication capacity | Near-term | Yes, 3–4 yr | Fab construction faster than mines |

**The policy-relevant implication is timing, not magnitude.** None of these materials represent a fundamental ceiling on the AI/robotics transition over a 35-year horizon. They do represent a concentration of price pressure in the 2026–2042 window that: (a) raises the cost floor in the physical goods sector; (b) creates inflation that partially offsets demand growth, supporting nominal sector size; and (c) makes the energy Phase 2 transition marginally more expensive because the copper and rare earths required for solar installations and transmission are more expensive in that period.

Nations controlling critical mineral deposits — cobalt (DRC), lithium (Chile, Argentina), REEs (China, Vietnam, Brazil), copper (Chile, Peru) — hold structural leverage during this window. The policy recommendation to require domestic value-added processing before export, and to use mineral rents to fund commons/cooperative ownership structures, is strongest in precisely this period.

---

## Appendix B: Model Construction

This appendix documents the baseline calibration, automation dynamics, sector price mechanisms, MPC assumptions, fiscal structure, scenario parameters, and governance decay mechanism referenced in §3. Full source code is available at the project repository; every parameter below can be varied.

### B.1 Baseline economy (2026)

| Parameter | Value | Basis |
|---|---|---|
| Nominal GDP | $28 trillion | BEA 2024 |
| Labour force | 160 million workers | BLS 2024 |
| Knowledge-work GDP share | 28% | Finance/insurance, professional services, information, education (BEA GDP by Industry 2024) |
| Automatable services share | 11% | Retail trade, accommodation/food, personal services (BEA 2024) |
| Physical-goods GDP share | 25% | Manufacturing, construction, transport, wholesale, mining/utilities/ag (BEA 2024) |
| Government GDP share | 11% | Government VALUE-ADDED only — not total outlays (BEA 2024: 11.3%); total outlays ≈21.5% of GDP |
| Real estate GDP share | 13% | Mostly imputed rent — treated as capital income, not automatable production (BEA 2024) |
| Human economy | ~12% baseline + demand | Residual from GDP accounting; grows via redistribution spillover and worker pivot (§B.5) |
| Federal debt outstanding | $34 trillion | US Treasury 2024 |
| Effective average interest rate | 4.5% | Weighted average of existing maturities |
| Annual interest obligation | $1.53 trillion | Fixed nominal |
| Knowledge workers | 35M (22% of labour force) | BLS Employment by Major Industry 2024 |
| Automatable services workers | 35M (22%) | Retail, food service, accommodation, personal services |
| Physical workers | 38M (24%) | Manufacturing, construction, transport, wholesale, mining/ag |

### B.2 Automation dynamics

Automation proceeds via logistic S-curves, separately parameterised for each sector. All scenarios start from 0% automation in 2026, ensuring a common baseline anchor.

**Knowledge work:** ceiling 93% (7% reserved for judgment, accountability, interpersonal trust). S-curve speed 0.8/yr.

**AI-delivered services (healthcare, education):** ceiling 95%. Modelled as AI-delivered, not as Baumol human services — mass-market diagnosis, surgery, adaptive tutoring, and care protocols will be AI-provided. The irreducibly-human remainder is a small premium fraction captured in the scarcity goods sector.

**Physical work:** ceiling 82% (18% reserved for unstructured environments, safety oversight, fine dexterity). Physical automation lags knowledge by ~30% in pace (hardware deployment friction vs software-first AI).

Automation ceilings reflect task-based theory (Acemoglu and Restrepo, 2018): not all tasks within an occupation are automatable. These are illustrative upper bounds, not econometric estimates.

### B.3 Sector price dynamics

| Sector | Price dynamic | Mechanism |
|---|---|---|
| Knowledge work | −8%/yr → −2%/yr | Asymptotic: near-zero marginal cost, competitive diffusion; Jevons demand expansion partially offsets |
| Automatable services | −4%/yr → −1%/yr | Asymptotic: high labour content → steep drop when automated |
| Physical goods | Net ~flat | See below |
| Real estate | +2.5%/yr baseline + automation uplift | See below |
| Scarcity goods | +6%/yr | Provably-human premium rises with income inequality |
| Human economy | +4%/yr Baumol | Residual labour-intensive sector |
| Government | −0.5%/yr | Modest efficiency gains |
| Debt service | Fixed $1.53T/yr | Nominally fixed; real burden falls as GDP grows |

**Real estate — automation-amplified appreciation.** Real estate in this model grows faster than a naive "population + housing inflation" baseline for a structural reason: automation expands the effective supply of *valuable* land. Precision construction robotics reduces the cost of building in difficult terrain; logistics automation (autonomous vehicles, drone delivery) collapses the transport-cost premium that makes rural land cheap; smart-grid and energy infrastructure, when rolled out by robotic workforces, makes previously marginal land viable for habitation and industry. The traditional Ricardian scarcity mechanism concentrates value at the centre; the AI-era mechanism is that the frontier of "prime" land expands. The model captures this as a baseline appreciation rate of 2.5%/yr (population + nominal housing inflation) plus an automation-proportional uplift of up to 2.5%/yr as `avg_auto` rises toward 1.0 — reaching roughly 5%/yr at full automation. This is conservative relative to the last decade's observed land appreciation in AI-adjacent corridors.

**Physical goods cost structure.** Labour and automatable logistics represent only ~25% of physical goods cost; raw materials and purchased parts ~57%; embedded energy ~8%; non-automatable overhead ~10% (calibrated from Oliver Wyman 2025, NAHB, Counterpoint Research). AI and robotics automation reduces the 25% automatable share, creating a hard cost floor at the material component. Material prices appreciate ~3%/yr as electrification demand (copper, lithium, rare earths) outpaces supply. Demand responds at approximately unit elasticity: cheaper goods → more units demanded, roughly offsetting per-unit deflation. Net: nominal physical goods GDP remains broadly stable or grows modestly, not a deflationary casualty.

**Energy sector — two-phase model.** The energy sector trajectory is modelled with a phase transition whose timing is endogenous to the automation speed parameter, because robotics is the primary mechanism that will collapse the cost of solar installation.

*Phase 1 — Grid infrastructure buildout* (duration ≈ `mid × 1.5` years): Retail electricity prices rise ~+1.5%/yr despite cheap solar *modules*, because grid transmission upgrades, storage integration, and grid hardening dominate delivered cost. Solar module cost is ~30% of utility-scale LCOE; balance of system, land, financing, and transmission components do not follow the same learning curve and have been rising with infrastructure investment. Data-centre electricity demand grows ~15%/yr from a 4–5% base, with EVs and industrial electrification adding further volume. Net nominal energy sector growth: **+6.5%/yr**.

*Phase 2 — Robotics-accelerated solar collapse + Jevons backfire* (remainder): Solar installation labour is 15–40% of installed cost — exactly the kind of structured, repetitive physical work that humanoid and specialised construction robots will perform. Automation of this component is equivalent to one additional capacity doubling under the module learning curve, a ~12% step-change in total LCOE. Solar+storage reaches grid dominance; electricity prices fall ~5%/yr toward the marginal cost of sunlight. Cheap electricity then unlocks new demand at a scale that produces full Jevons backfire: green hydrogen becomes competitive below ~$20/MWh (enabling green steel, synthetic aviation fuel, ammonia-based fertiliser), desalination becomes viable globally, direct air capture crosses the economic threshold, and always-on robotic manufacturing no longer has electricity as its binding constraint. Demand grows ~9%/yr. Net nominal: **+3.5%/yr**. The transition date is endogenous to `mid`: fast automation (mid=5) triggers Phase 2 around 2032; medium (mid=9) around 2038; slow (mid=14) around 2046.

A counterintuitive implication: faster automation produces a smaller nominal energy sector by 2055 ($4T vs $5.8T for slow automation), because energy companies capture high Phase 1 prices for fewer years. The welfare gain from fast automation shows up in the broader economy through cheap electricity, not in energy sector revenue.

### B.4 Income distribution and MPC calibration

| Income stream | MPC | Tax treatment | Description |
|---|---|---|---|
| Concentrated capital | 0.25 | `tax_k × enforcement` | Large AI/robot owners; high saving rate |
| Yeomen income | 0.78 | Labour tax rate | Small owner-operators; earned income character |
| DAO commons income | 0.78 | Labour tax rate | Commons contributors; earned-income character |
| Labour income | 0.82 | Labour tax rate | Declining with displacement; MPC rises as income falls |
| Citizen compute dividend | 0.85 | Labour tax rate | Per-adult dividend; high MPC as marginal income |

The MPC differential is the primary mechanism behind the ownership finding. Concentrated capital MPC of 25% is calibrated from documented saving behaviour of the top wealth decile (Dynan, Skinner and Zeldes, 2004; Carroll, 2000). Yeomen and commons MPC of 78% reflects average household MPC for earned income. Compute dividend MPC of 85% reflects evidence that households treat unexpected income with higher MPC than expected earned income (Jappelli and Pistaferri, 2010).

Labour income MPC adjusts upward as labour income declines — liquidity-constrained households have higher MPC from any income source (Kaplan, Moll and Violante, 2018).

### B.5 Human economy (derived)

Unlike models that fix the human economy exogenously, this model derives it from consumption flows each period. Human-economy output equals the sum of consumption from each income stream multiplied by the fraction each directs toward irreducibly-human services. Capital owner consumption directs ~15% toward human services (revised down from 30% after real estate income was added to the capital pool — the incremental consumption from imputed rent flows more heavily toward goods and financial assets than bespoke services); yeomen and labour income direct ~10%; UBI recipients direct ~6% (income-constrained households prioritise necessities; premium human services are discretionary). DAO commons income directs ~12%, reflecting the collaborative and experiential orientation of commons-sector participants.

Human-economy wages clear this derived demand against labour supply. Concentrated-ownership scenarios produce smaller human economies because concentrated capital income has low MPC and low human-services share — the feedback loop between income distribution and economic activity is endogenous.

### B.6 Government finances

| Tax instrument | Rate | Enforcement | Notes |
|---|---|---|---|
| Labour income tax | 28% effective | ~100% | Withholding; declines as labour income falls |
| Capital income tax | `tax_k` (scenario) | `enforcement` (scenario) | Mobile; profit-shifting reduces effective rate |
| Land value tax | 1.2% of value | ~95% | Immobile; near-complete enforcement |
| VAT / consumption | 8% effective | ~90% | Consumption at consumer location |

Fiscal space is defined as tax revenue minus existing obligations (programme spending proportional to GDP + fixed debt service of $1.53T/yr), before any UBI. Negative fiscal space means existing obligations cannot be covered without new borrowing.

### B.7 Scenario dimensions

| Parameter | Description | Range modelled |
|---|---|---|
| `mid` | Years to 50% knowledge-work automation | 5 (fast) / 9 (medium) / 14 (slow) |
| `yeomen` | Fraction of capital income to small owner-operators | 0% – 60% |
| `dao_frac` | Fraction through commons DAO governance | 0% – 25% |
| `public_ai_frac` | Fraction of AI/robot capital as public infrastructure | 0% – 90% |
| `tax_k` | Statutory capital income tax rate | 20% – 50% |
| `enforcement` | Fraction of `tax_k` collectible given capital mobility | 30% – 100% |
| `levy_prog` | Progressive compute levy progressivity | 0 – 1.0 |
| `dao_govt_rate` | Annual rate of government → commons asset conversion | 0% – 20% |
| `yeomen_tax_friction` | Income discount from current tax code on sole operators | 0% (reformed) – 18% (current) |
| `firm_yeomen_rebate` | Demand-side tax credit for firms contracting to independent operators | 0% – 25% |

### B.8 Governance decay mechanism

In the static model, `enforcement` is a fixed policy choice. An extended version treats governance quality G(t) as a stock that evolves endogenously each period according to:

```
G(t+1) = G(t) + recovery(t) - β · G(t) · pressure(t)

where:
  pressure(t)  = (1 - yeomen_frac(t)) · (1 - dao_frac(t)) · 0.7
               ≈ concentrated ownership share (ranges 0 → 0.7)

  recovery(t)  = α · max(G_target - G(t), 0)   [mean reversion when below target]
               + γ · (1 - pressure(t)) · G(t)   [active strengthening when conditions are favourable]

  α  = 0.02/yr   (slow mean reversion toward 1.0)
  β  = 0.08/yr   (decay under concentrated pressure)
  γ  = 0.03/yr   (active strengthening under distributed ownership)
  G_floor = 0.10                 (institutions do not fully collapse)
  G_target = 1.0                 (full enforcement capacity)
```

Effective enforcement each period = `enforcement_statutory × G(t)`.

The three-term structure is important. The γ coefficient (0.03) is calibrated so that at maximum distributed ownership (yeomen=0.60), the recovery term approximately matches the decay term at G=1.0 — keeping governance stable rather than slowly drifting down. The logic: `γ × (1 - pressure) ≥ β × pressure` at stability; solving gives `γ ≥ β × pressure / (1 - pressure) = 0.08 × 0.28 / 0.72 ≈ 0.031`. Under concentrated ownership (pressure=0.70), decay still overwhelms recovery by a factor of 4. Under high-yeomen ownership (pressure=0.28), G stabilises near 1.0 and, if Gini is falling during the policy ramp-in, G recovers back toward 1.0 after the initial dip. This matches the empirical pattern that low-inequality societies maintain stronger institutions over time (Acemoglu and Robinson, 2012), while high-inequality societies erode them even when the initial statutory framework is strong.

The decay function is logistic in character: decay is fastest when G(t) is near 1.0 and `pressure(t)` is high (a well-functioning institution under sustained attack), and slows as G(t) approaches the floor. Recovery is linear when `G(t) < G_target` and `pressure(t)` is low.

The coefficients α = 0.02 and β = 0.08 are calibrated to produce an institutional half-life of approximately 25–30 years under concentrated-ownership scenarios, consistent with documented regulatory capture timelines (IRS top-0.1% audit rates fell from ~10% to ~2% over 8 years; SARS South Africa lost significant capacity within a single political term). The specific coefficients are illustrative rather than empirically estimated — the model is open source and readers can adjust them.

---

## References

Acemoglu, D. and Restrepo, P. (2018). "The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment." *American Economic Review*, 108(6), 1488–1542.

Acemoglu, D. and Robinson, J.A. (2012). *Why Nations Fail: The Origins of Power, Prosperity and Poverty*. Crown Publishers.

Baumol, W.J. (1967). "Macroeconomics of Unbalanced Growth: The Anatomy of Urban Crisis." *American Economic Review*, 57(3), 415–426.

Baumol, W.J. and Bowen, W.G. (1966). *Performing Arts: The Economic Dilemma*. Twentieth Century Fund.

Carroll, C.D. (2000). "Why Do the Rich Save So Much?" in Joel B. Slemrod, ed., *Does Atlas Shrug? The Economic Consequences of Taxing the Rich*. Harvard University Press.

Clausing, K.A. (2020). "Profit Shifting Before and After the Tax Cuts and Jobs Act." *National Tax Journal*, 73(4), 1233–1266.

Coase, R.H. (1937). "The Nature of the Firm." *Economica*, 4(16), 386–405.

Dynan, K., Skinner, J. and Zeldes, S. (2004). "Do the Rich Save More?" *Journal of Political Economy*, 112(2), 397–444.

Fisher, I. (1933). "The Debt-Deflation Theory of Great Depressions." *Econometrica*, 1(4), 337–357.

Jappelli, T. and Pistaferri, L. (2010). "The Consumption Response to Income Changes." *Annual Review of Economics*, 2, 479–506.

Kaplan, G., Moll, B. and Violante, G.L. (2018). "Monetary Policy According to HANK." *American Economic Review*, 108(3), 697–743.

Krier, J. (2025). "Bargaining at Scale: AI and the Future of Labor Contracting." *Yale Law Journal* (forthcoming).

Ostrom, E. (1990). *Governing the Commons: The Evolution of Institutions for Collective Action*. Cambridge University Press.

Zucman, G. (2015). *The Hidden Wealth of Nations: The Scourge of Tax Havens*. University of Chicago Press.

---

*This paper is generated from an open parametric model. All scenario parameters are explicit, all code is available, and all results are reproducible.*

---

## Appendix C: Building the Agentic Marketplace — Technical Architecture

This appendix describes the concrete technical architecture required for the federated agent commerce infrastructure introduced in §6.2. The working prototype (`federated_registry_demo.py`) implements all five key flows in memory; this appendix describes the production architecture.

### C.1 Design principles

Three principles constrain every design choice.

**Reputation portability over platform convenience.** Any decision that makes reputation data more convenient for a single matchmaker at the cost of portability is wrong. Reputation is the yeoman's primary capital; it must be portable.

**Tax reporting in the execution path.** Tax declaration happens at contract commitment, in the same atomic operation as execution. It cannot be a separate step the matchmaker might skip or defer. This eliminates the payment-routing games that plague current self-employment taxation.

**Open protocol, competitive operators.** The standard (L0) is public and royalty-free. The registries (L1) are government-chartered nonprofits. The matchmakers (L2) are private and competitive. Anyone can implement the standard; no one can own it.

### C.2 Layer-by-layer summary

The full technical specification is maintained in the companion technical document (`PROPOSAL.md`). This section summarises the governance and functional logic of each layer; readers interested in wire formats, schema definitions, or implementation status should refer to the technical document.

**L0 — International Standard.** Defines wire format for all cross-layer communication — analogous to TCP/IP. Core schemas cover agent capability declarations, tender specifications, contract bundles, tax records, and negotiation messages. Governance follows IETF rough-consensus: standards published freely, patent-free licensing required from contributors, persistent objections documented and addressed. No single operator owns or controls the standard.

**L1 — National Registry.** One per jurisdiction; government-chartered nonprofit. Issues and verifies decentralised identifiers, stores reputation attestation hashes (credential content stays with the agent), licenses matchmakers, receives contract reports within 60 seconds of execution, and forwards structured tax records to the domestic tax authority. Publishes aggregate price data; individual contract records are exempt from public disclosure. Distributed operation — no single node can unilaterally alter the registry.

**L2 — Matchmakers.** Private, competitive, low barrier to entry. License conditions are the floor: implement L0 schema exactly, report contracts promptly, allow reputation portability, hold no credential content. Competitive differentiation is on matching quality, speed, and vertical specialisation — not on data lock-in. Anyone can register; the barrier is compliance, not approval.

**L3 — Agent Negotiation.** AI agents on both sides; neither principal is in the loop per negotiation round. Built on A2A protocol (Linux Foundation v0.3) with a structured `proposed_terms` extension — free-text negotiation is explicitly excluded because it produces agreements that cannot be reported to tax authorities in structured form. Circuit breaker prevents AI-speed flash crashes: the registry can signal matchmakers to queue if prices in a category move beyond a threshold in a short window.

**L4 — Settlement.** Domestic: FedNow (sub-second, USD). Cross-border: x402 HTTP-native stablecoin payment (Coinbase open standard, <$0.001/transaction). Milestone-based contracts use escrow with atomic release on deliverable hash verification. The matchmaker selects the rail based on jurisdiction; the L0 payment trigger schema is rail-agnostic.

**L5 — Tax Reporting.** Not a separate system — a mandatory step in the L2 matchmaker's contract execution function. Tax records are pushed to relevant registries at contract commitment (not payment), eliminating payment-routing games. The same operation that executes the contract also files the tax record. For the yeoman, this is a compliance cost reduction; for the tax authority, it is continuous real-time visibility into a base that would otherwise be entirely opaque at machine speed.

### C.3 Cross-border flow walkthrough

A US yeoman accepts a contract from an EU buyer via a matchmaker licensed in both jurisdictions:

```
1. EU buyer's agent posts tender to CrossBorder matchmaker (L2)
2. Matchmaker queries US-L1 and EU-L1 in parallel for matching suppliers (L1 API)
3. US yeoman's agent selected; A2A negotiation begins (L3)
4. Agreement reached → ContractBundle executed (L0 format)
5. Matchmaker wraps in CrossBorderContractBundle with unique bundle_id
6. Payment released via x402 stablecoin (L4)
7. Matchmaker reports to US-L1 → US-IRS receives supplier TaxRecord (L5)
8. Matchmaker reports to EU-L1 → EU tax authority receives buyer TaxRecord (L5)

Same bundle_id in both records.
No bilateral agreement required between jurisdictions.
Each tax authority applies its own domestic rules.
```

The `bundle_id` is the linchpin of cross-border tax reconciliation. If the US and EU sign a tax treaty covering agent commerce, both authorities can match records by `bundle_id` without any additional data exchange infrastructure. If no treaty exists, each authority independently applies domestic rules to its slice. The protocol is treaty-agnostic.

### C.4 Anti-collusion and market integrity

LLM-based agents converge on supracompetitive prices without explicit coordination — documented in laboratory settings and consistent with theoretical predictions from multi-agent reinforcement learning. The registry's aggregate price data is the primary monitoring tool: competition authorities receive read access to price series by category and geography, with statistical anomaly flagging when prices move in correlated ways across multiple matchmakers simultaneously.

The circuit breaker at L3 addresses short-term spikes; competition authority monitoring addresses long-term convergence. A third mechanism is mandatory price disclosure on agent cards: suppliers must publish their floor price as a field on their registered agent card. This does not require them to accept below-floor offers, but it makes the floor visible to buyers and to the price-monitoring system, making coordinated above-floor pricing harder to sustain invisibly.

### C.5 Prototype

A working prototype (`federated_registry_demo.py`) demonstrates five flows in memory: domestic single-registry contracting, cross-border dual-registry reporting with shared bundle identifier, competing matchmakers racing on the same tender, reputation portability across matchmaker switches, and machine-speed throughput (20 micro-contracts reported synchronously). Schema definitions in `platform_schemas.py` are production-shaped; the prototype uses in-memory structures and SHA-256 hashes in place of distributed databases and real signatures. Full implementation and phased deployment roadmap are documented in `PROPOSAL.md`.

---

## Appendix D: Commons DAOs — Governance Model and Economic Properties

### D.1 What this appendix is not about

The word "DAO" has been substantially contaminated by association with speculative DeFi governance tokens, anonymous pseudonymous voting, and projects whose primary product was the token itself. None of that is the model here. The commons DAO in this paper is an Ostrom-style managed commons — a legal structure for collective ownership and governance of a productive asset — that happens to use programmable governance infrastructure where that reduces cost and increases transparency. The governance token, if any, is a governance instrument, not a speculative asset; it has no secondary market value independent of the underlying commons.

The frame is: cooperative ownership of AI or robot capital, governed by contributors rather than capital holders, distributing income as earned contributions rather than passive dividends. DAOs create demand for yeoman services by design — the tax efficiency of contracting out through the agentic marketplace, combined with governance rules that keep the core asset narrow, makes independent operators the natural counterparty for most of what a DAO needs done.

### D.2 Two distinct DAO functions

DAOs in this framework serve two distinct economic functions that are worth separating before discussing either in detail.

**Function 1 — Thin-core asset entity.** A DAO owns a single narrowly-defined productive asset — a solar farm, a dataset, a software service, a piece of infrastructure — and operates with minimal direct employment, contracting the vast majority of its operational needs to yeomen via the agentic marketplace. The DAO's AI agents handle most contracting, quality verification, payment, and tax reporting autonomously. It may employ a small number of people for governance oversight or functions that genuinely require an ongoing employment relationship, but its defining characteristic is very high leverage: large output relative to headcount, with operational spending routed through the marketplace rather than through payroll.

This is the Coasian minimum viable firm: with transaction costs approaching zero at the marketplace layer, the boundary of the organisation collapses toward just the asset and the governance contract. A conventional corporation internalises maintenance, legal, accounting, marketing, and operations because managing those relationships externally was expensive. A thin-core DAO contracts most of them to yeomen because the agentic marketplace makes external contracting cheaper than internalisation for all but the most sensitive or continuous functions.

The policy significance is on the **demand side**: thin-core DAOs create structural, recurring demand for yeoman services. A solar farm DAO needs maintenance yeomen, monitoring yeomen, grid-compliance yeomen, legal yeomen, accounting yeomen. It sources most of them through the marketplace, generating stable contract flows that anchor yeoman income in ways that individual consumer hiring does not. The DAO is not a worker collective — its members may be investors, community members, or former employees of a converted business — but it systematically routes its operational spending to independent operators rather than to internal headcount or large corporate contractors.

**Function 2 — Collective ownership of shared infrastructure.** A group of yeomen jointly own a productive asset that is too expensive, underutilised, or network-effect-dependent for individual ownership. A GPU cluster, a shared evaluation dataset, a regional logistics network. The governance challenge is ensuring distributions are proportional to contribution, not capital stake.

The remainder of this appendix addresses both functions, noting where their design requirements differ.

### D.3 What assets suit the thin-core model

The thin-core DAO model is most applicable where:

- The core asset generates predictable revenue without requiring ongoing human judgment (a solar farm, a data centre, a royalty-generating IP portfolio, a toll infrastructure)
- Non-core services are well-specified enough for the agentic marketplace to handle contracting without principal supervision
- Governance is stable enough that the DAO's AI agents can execute procurement within pre-approved parameters for extended periods

This covers a surprisingly wide range of assets. Real estate managed by a thin-core DAO contracts maintenance, compliance, and tenant communication to yeomen. A media archive DAO contracts curation, transcription, and licensing negotiations. A cooperative utility DAO contracts installation, repair, and customer service. In each case, the DAO's AI agents post tenders to the marketplace, evaluate bids against reputation and price, execute contracts, verify deliverables, and file the tax records — all without human intervention per transaction.

The boundary of what counts as "core" is a governance question, not a technical one. A solar farm DAO might define core as: the physical panels, the grid interconnect agreement, and the revenue distribution contract. Everything else is a contracted service. Keeping this definition tight prevents scope creep that would convert the DAO back into a vertically integrated firm over time — the natural tendency of any organisation is to internalise functions that generate recurring value, and the governance structure must explicitly resist this.

### D.4 What problem collective commons DAOs solve

Collective commons DAOs address assets that are most productive when shared and where the coordination overhead of individual ownership would be prohibitive.

Three categories suit this model well:

**Shared compute infrastructure.** A GPU cluster serving fifty specialist operators is more efficiently managed as a commons than as fifty individual purchases — utilisation is higher, maintenance is pooled, and the cost per unit of compute is lower. The individual operators contribute to governance and receive compute credits; they remain independent businesses, but their capital access is collective.

**Training and evaluation datasets.** A curated, domain-specific evaluation harness for medical coding, legal document review, or structural engineering takes years of expert contribution to build. It is non-rival (one operator using it doesn't reduce another's access) but requires ongoing contribution to remain current. A commons DAO with clear contribution rules and income-sharing proportional to contribution solves the free-rider problem while keeping the asset open to all contributors.

**Reputation and certification infrastructure.** A shared reputation system — credential verification, peer attestation, dispute resolution — has network effects that make it more valuable when broader. A single yeoman cannot build this alone; a platform that builds it will extract rent from it. A commons DAO owned by the operators it serves can maintain it as a shared asset without rent extraction.

### D.3 Why commons income is treated as earned income in the model

In the model, commons DAO income carries yeoman-like MPC (0.78) and is taxed at labour rates rather than capital rates. This is not an assumption of convenience — it reflects a substantive claim about the income's character.

Commons income in this framework is proportional to contribution, not to capital stake. A member who contributes more evaluation data, more compute time, or more governance participation receives a larger share. This makes commons income economically equivalent to earned income: it is the return on active productive participation, not passive ownership. The analogy is a worker cooperative's profit distribution, which is legally and economically distinct from a dividend: it is compensation for contribution, subject to labour taxation, and characterised by high MPC because recipients are active participants rather than passive wealth holders.

The legal structure must reflect this to receive the tax treatment: charter provisions must tie distributions to contribution metrics, prohibit pure-capital voting rights, and establish that no member can receive distributions without active participation above a minimum threshold.

### D.4 Governance structure — Ostrom conditions applied

Elinor Ostrom's conditions for sustainable commons governance translate directly to the digital commons context:

| Ostrom Condition | Commons DAO Implementation |
|---|---|
| Clearly defined boundaries | Membership requires contribution above minimum threshold; free-riders are excluded from distributions |
| Collective choice arrangements | Governance votes weighted by contribution history, not capital stake; one-member-one-vote for constitutional questions |
| Monitoring | On-chain contribution ledger; all distributions are auditable and public |
| Graduated sanctions | Warning → reduced distribution share → suspension → expulsion; no single-step exclusion |
| Conflict resolution | Arbitration clause; escalating tiers (peer mediation → elected committee → external arbiter) |
| Recognition of rights | Legal entity status gives the commons standing in contract, IP, and employment law |
| Nested governance | Local working groups handle day-to-day; full membership votes on constitutional changes |

The critical governance design choice is the voting weight mechanism. Capital-weighted voting replicates the dynamics the commons is meant to avoid — large early contributors eventually dominate governance, effectively converting the commons into a concentrated-ownership structure. Contribution-weighted voting with decay (recent contributions weighted more than historical ones) maintains ongoing engagement as a prerequisite for governance power.

### D.5 Legal prerequisites

Commons DAOs currently exist in a legal grey area. A working cooperative statute provides some of what is needed but was not designed for digital commons assets or programmable governance. The gaps:

**Legal personhood for the commons asset.** The GPU cluster or dataset needs to be owned by a legal entity that can hold IP, enter contracts, and be taxed. A cooperative statute provides this; a standard LLC or C-corp does not carry the governance constraints required.

**IP ownership and licensing.** Contributions of training data, evaluation harnesses, and model fine-tunes need a clear IP contribution agreement that vests ownership in the commons while granting perpetual use rights to contributors. Existing open-source licences (MIT, Apache, Creative Commons) cover some use cases but not the contribution-with-income-sharing model.

**Tax treatment of distributions.** The IRS currently has no clear ruling on whether contribution-proportional distributions from a commons DAO are labour income or capital income. The cooperative model (patronage dividends) is the closest existing treatment and should be the default, but enabling legislation that explicitly extends this treatment to digital commons DAOs would eliminate the uncertainty that currently deters formation.

**Three to five state pilots** creating a "Digital Commons Cooperative" entity class under cooperative statute amendments would establish the legal precedent. Federal tax guidance can follow once the entity form is established.

### D.6 The daoification mechanism

The policy layer in §6.1 includes government acquisition and "daoification" of underutilised assets. This warrants elaboration.

When a business that owns productive AI or robot capital fails, those assets are typically acquired by larger operators — concentrating ownership further — or liquidated at distressed prices. An alternative disposition path: the government acquires the assets through an existing economic development mechanism (SBA, state development finance authorities) and transfers them to a newly chartered commons DAO whose initial members are the displaced workers from the failed business, the suppliers and contractors who depended on it, and any other eligible contributors in the affected community.

This is not nationalisation. The government holds no ongoing stake. The transfer is at acquisition cost, repaid over time through commons revenue — a loan, not a grant. The government's role ends when the loan is repaid. The resulting commons DAO is owned and governed by its contributors, not by the state.

The mechanism is most tractable in three situations: rural communities where a single large employer's failure would otherwise cause persistent economic damage; sector transitions where an entire industry's capital base is being replaced (coal-to-solar, internal combustion to electric); and cases where the asset's value depends on network effects that no single buyer would sustain (a regional logistics network, a shared inspection certification system).

### D.7 Failure modes

The model treats commons DAOs as well-functioning. The following failure modes are real and not modelled:

**De facto control by active minorities.** In practice, most members of any commons do not participate actively in governance. The small minority who do effectively control the institution. This replicates plutocracy through the back door if active participants have correlated interests — e.g., they are all early adopters with large historical contribution shares. Contribution decay and mandatory rotation of governance positions partially address this; no design fully eliminates it.

**Free-rider equilibria.** If contribution verification is costly, members will under-contribute and over-extract. On-chain contribution ledgers reduce verification cost for digital assets; physical contributions (care work, community service) remain difficult to verify without surveillance that members would reasonably reject.

**Regulatory capture of the certification function.** If a commons DAO becomes the dominant certification body for a professional category, it faces the same regulatory capture dynamics as any other standard-setting body. The Ostrom conditions provide structural resistance but not immunity.

**Capital starvation.** Commons DAOs without access to capital markets grow slowly. Cooperative lending programmes and public compute credits (§6.1, Layer 3) address this, but the structural disadvantage versus private-equity-backed competitors remains significant in capital-intensive sectors.

These failure modes are reasons to design commons institutions carefully and to maintain a diverse ecosystem — yeomen, commons DAOs, and public infrastructure — rather than to avoid the model. The yeoman model's failure modes (platform capture, margin compression) are equally real; neither structure dominates on all dimensions.
