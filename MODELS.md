# Economic Model Families
## Reference Document for AI Transition Modelling

This document describes the four main model families considered for simulating
the AI economic transition, their strengths, limitations, and implementation
references. The current implementation uses an SFC base with an LLM household
decision layer.

---

## 1. Stock-Flow Consistent (SFC) Models ← **Current approach**

### What it is
Developed by Wynne Godley and Marc Lavoie (*Monetary Economics*, 2007).
Every financial flow appears twice in a transaction matrix — as a payment by
one sector and income for another. Every row and column sums to zero. This
enforces full accounting consistency: nothing is created or destroyed, only
transferred.

### Core structure
Three matrices:
- **Transaction flow matrix**: who pays whom each period (wages, taxes,
  dividends, interest, consumption, investment)
- **Balance sheet matrix**: stocks at end of each period (deposits, loans,
  equity, government bonds, capital)
- **Revaluation matrix**: capital gains/losses that change stock values
  without appearing as flows

### Sectors in our implementation
| Sector | Assets | Liabilities |
|---|---|---|
| Households (6 types) | Deposits, equity, housing | Bank loans, mortgages |
| AI-sector firms | Capital stock | Bank loans, equity |
| Human-economy firms | Capital stock | Bank loans, equity |
| Government | — | Bonds outstanding |
| Banks | Loans, reserves, bonds | Deposits |

### Second and third order effects captured
- **Endogenous money**: banks create credit when households borrow to consume;
  spending can exceed income → demand amplification
- **Debt dynamics**: falling labour income → debt service burden rises →
  forced saving → demand contraction (Fisher debt-deflation endogenous)
- **Wealth effects**: asset price changes affect consumption even without
  income change (capital owners cut spending when equity values fall)
- **Circular flow**: consumption → firm revenue → wages → consumption
  (multiplier effect fully tracked)
- **Government automatic stabilisers**: tax revenue falls as income falls;
  UBI spending rises as displacement rises; deficit/surplus endogenous

### Key references
- Godley, W. & Lavoie, M. (2007). *Monetary Economics: An Integrated Approach
  to Credit, Money, Income, Production and Wealth*. Palgrave Macmillan.
- Godley, W. (1999). "Seven Unsustainable Processes." Levy Economics Institute.
- Nikiforos, M. & Zezza, G. (2017). "Stock-flow Consistent Macroeconomic
  Models: A Survey." *Journal of Economic Surveys*, 31(5), 1204-1239.

### Python implementations
- `pysolve` — SFC equation solver
- Custom numpy/pandas implementation (our approach — most flexible)
- `sfcr` (R package) — best documented, good for learning structure

---

## 2. Heterogeneous Agent New Keynesian (HANK)

### What it is
Extension of standard DSGE models (Kaplan, Moll & Violante, 2018). Keeps
the New Keynesian macro structure (sticky prices, monetary policy) but
replaces the representative household with a distribution of households
differing in wealth, income, and liquidity constraints.

### Key insight
Aggregate MPC is not a constant — it depends on the *distribution* of income
and wealth. A fiscal transfer going to liquidity-constrained low-wealth
households has a much larger multiplier than the same transfer going to
wealthy households. This is the core of our ownership-structure finding,
but in HANK it is derived from optimisation rather than assumed.

### Second and third order effects captured
- MPC is endogenous to wealth distribution (not a parameter)
- Monetary policy transmission differs radically by income decile
- Fiscal multipliers depend on who receives the transfer
- Precautionary savings dynamics: households save more when future income
  is uncertain (directly relevant to AI displacement scenarios)

### Limitations
- Requires equilibrium assumption — no demand deficiency spirals possible
- Computationally expensive (requires solving household optimisation over
  wealth distribution)
- Monetary policy is central; less suited to supply-side productivity shocks

### Key references
- Kaplan, G., Moll, B. & Violante, G.L. (2018). "Monetary Policy According
  to HANK." *American Economic Review*, 108(3), 697-743.
- Auclert, A. et al. (2021). "Using the Sequence-Space Jacobian to Solve and
  Estimate Heterogeneous-Agent Models." *Econometrica*, 89(5), 2375-2408.

### Python implementations
- `sequence-jacobian` (Auclert et al.) — canonical HANK solver
- `quantecon` — includes heterogeneous agent building blocks

---

## 3. Agent-Based Models (ABM)

### What it is
Simulate thousands of individual agents (households, firms, banks) each
following simple behavioural rules. No equilibrium assumption. Macro
behaviour emerges from micro interactions. Particularly good at capturing
non-linear dynamics, tipping points, and persistent unemployment.

### Key models
**Mark-0 / Mark-I / Mark-II** (Bouchaud, Gualdi, Marsili, Fagilo et al.):
- Firms hire/fire based on demand and profit signals
- Workers search for jobs with finite probability of finding one
- Unemployment can persist indefinitely without market clearing
- Shows how economies can tip from high- to low-employment equilibria
- Directly applicable to automation displacement scenarios

**EURACE** (Dawid et al.):
- Full-scale macro ABM with financial sector
- Household consumption depends on income AND wealth expectations
- Firms make investment decisions based on capacity utilisation
- Used by European Central Bank for policy analysis

### Second and third order effects captured
- Demand deficiency spirals (no equilibrating mechanism forces recovery)
- Unemployment hysteresis (long-term unemployed lose skills, exit labour force)
- Financial accelerator (asset price falls → collateral falls → lending falls →
  investment falls → asset prices fall further)
- Innovation diffusion (adoption spreads through networks, not uniformly)
- Firm entry/exit dynamics

### Limitations
- Results depend heavily on agent rules (garbage in, garbage out)
- Hard to validate — many free parameters
- Computationally expensive at scale
- Aggregation is not analytically tractable

### Key references
- Fagiolo, G. & Roventini, A. (2017). "Macroeconomic Policy in DSGE and
  Agent-Based Models Redux." *Journal of Artificial Societies and Social
  Simulation*, 20(1).
- Bouchaud, J.P. et al. (2018). "Optimal Inflation Target: Insights from an
  Agent-Based Model." *Journal of Economic Interaction and Coordination*.
- Dawid, H. et al. (2019). "Agent-Based Macroeconomic Modeling and Policy
  Analysis: The EURACE@Unibi Model." in *Handbook of Computational Economics*.

### Python implementations
- `mesa` — general ABM framework
- `agentpy` — cleaner API, good for economic models
- Mark-0 implementations on GitHub (multiple)

---

## 4. LLM-Augmented SFC (Current Implementation)

### What it is
SFC accounting shell with LLM (Gemini Flash) replacing fixed household
behavioural equations. Each period, each household type receives a structured
prompt describing their current financial situation and the economic
environment. The LLM returns a spending/saving decision in JSON, which feeds
back into the SFC flow matrix.

### Why this is interesting
- Behavioural equations in SFC/HANK are always somewhat arbitrary (why MPC
  = 0.78 rather than 0.75?). LLMs encode implicit models of human behaviour
  from training on vast economic and social text.
- Households can exhibit loss aversion, anchoring, social comparison, and
  adaptive expectations without these being explicitly programmed.
- The `reasoning` field in LLM output provides qualitative explanation of
  *why* spending patterns shift — a form of interpretable AI.
- Scenarios can be given narrative framing ("there are news reports of mass
  layoffs") and households respond to that framing, not just numbers.

### Design
- 6 representative household types (not thousands of agents)
- Each type has a persistent memory of past decisions and economic conditions
- LLM called once per type per simulated year
- Structured JSON output (consume_fraction, human_services_share,
  borrow, invest_in_yeomen_enterprise, ...)
- SFC accounting enforces consistency regardless of LLM output

### Limitations
- LLM behaviour may not be stable across runs (stochasticity)
- Representative household approach misses within-type heterogeneity
- LLM "reasoning" is not ground truth — it reflects training data biases
- Slower and more expensive than fixed equations

### Key references (LLM agents in economics)
- Horton, J.J. (2023). "Large Language Models as Simulated Economic Agents:
  What Can We Learn from Homo Silicus?" NBER Working Paper 31122.
- Argyle, L. et al. (2023). "Out of One, Many: Using Language Models to
  Simulate Human Samples." *Political Analysis*, 31(3), 337-351.
- Manning, R. et al. (2024). "Automated Social Science: Language Models as
  Scientist and Subjects." NBER Working Paper 32381.

---

## Comparison Summary

| Model | Equilibrium | Heterogeneity | 2nd/3rd order | Complexity | LLM-ready |
|---|---|---|---|---|---|
| Parametric (current) | Implicit | Fixed tiers | Partial | Low | No |
| SFC | No | Sector-level | Full flow accounting | Medium | Yes |
| HANK | Yes | Continuous distribution | Full, optimised | High | Partial |
| ABM | No | Individual agents | Full emergence | High | Yes |
| SFC + LLM | No | LLM-behavioural | Full + adaptive | Medium | Native |

---

## Unmodelled Scenarios Worth Noting

### Space Capital / Techno-Utopian Scenario
Capital owners reinvest all returns into space colonisation and AI/robotics R&D rather than consuming or paying taxes. Two effects: (1) accelerated technology deflation — faster investment drives steeper cost reduction curves, compute going from -10%/yr to -20%/yr; (2) a voluntary "residual dividend" — as compute becomes trivially cheap, even a small share of capital income buys substantial real living standards for everyone.

This is the implicit worldview of much Silicon Valley thinking. It produces potentially high absolute welfare alongside Gini approaching 1.0 — distributional structure and welfare floor completely decouple. Key tensions: no enforcement mechanism (residual depends on capital owner benevolence), democratic dependency (people live well at pleasure of owners not by right), single point of failure (if space fails or owners stop sharing, floor collapses), and accelerated governance decay (less need for public institutions).

Interesting comparison point: same technology trajectory as public AI, completely different political economy. Aaron Bastani's Fully Automated Luxury Communism assumes public ownership of deflated technology; this assumes private ownership with voluntary residual.

Model parameters needed if built: `space_frac` (H1 reinvestment rate), `space_deflation_boost` (multiplier on deflation rates), `residual_dividend_frac` (voluntary transfer rate, decays with governance quality).

---

## Possible Future Extensions

1. **SFC + ABM hybrid**: Use SFC accounting for macro consistency but simulate
   hundreds of agents within each sector using Mesa. LLM used for firm
   investment decisions, not just households.

2. **HANK calibration**: Use LLM-SFC outputs to calibrate MPC distributions
   for a HANK model, giving you both behavioural realism and analytical
   tractability.

3. **Multi-country SFC**: Extend with a foreign sector to model the enforcement
   gap and capital flight explicitly as balance-of-payments dynamics.

4. **Network effects**: Add an inter-firm transaction network (Leontief-style)
   inside the production sector to capture supply chain second-order effects
   of automation.
