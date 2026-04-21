# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Model

```bash
pip install numpy pandas matplotlib
python3 model.py
```

Produces:
- `ai_economy.png` — 12-panel chart comparing all scenarios
- `scenario_*.csv` — Annual time-series data per scenario (2025–2060)
- Console summary tables at t+5, t+10, t+20, t+30 years

No build, lint, or test infrastructure exists. Validation is done by inspecting the generated chart and CSVs for plausible trajectories.

## Architecture

Single-file model (`model.py`, ~700 lines). Dependencies: `numpy`, `pandas`, `matplotlib` only.

**What it models:** A parametric macroeconomic simulation of AI/automation's impact on a US-like economy from 2025–2060. Central finding: real output may grow 63%+ while nominal GDP halves due to deflationary productivity gains — with large structural implications for income distribution and fiscal capacity.

**Code layout:**

| Section | Lines | Purpose |
|---------|-------|---------|
| Constants | 43–160 | Economy parameters, price dynamics, capital ownership tiers, MPC by tier |
| Scenario definitions | 167–197 | 10 preset scenarios across 5 dimensions |
| Helper functions | 217–241 | `s_curve()` (logistic automation adoption), `mpc_adjusted()` |
| `run()` | 247–551 | Core simulation — takes scenario params, returns 35-column annual DataFrame |
| `plot()` | 557–625 | 12-panel matplotlib comparison across all scenarios |
| `print_summary()` | 662–676 | Console tables at checkpoint years |
| Main | 683–699 | Runs all scenarios, writes outputs |

**Five scenario dimensions:**
1. `automation_mid` — speed of automation (fast/medium/slow: 5/9/14 years to midpoint)
2. `yeomen_frac` — fraction of capital income flowing to owner-operators (0.0–0.60)
3. `dao_frac` — fraction going to commons/DAO governance structures
4. `tax_k` — capital tax rate (0.20–0.50)
5. `enforcement` — tax enforcement leverage multiplier

**Key model mechanics in `run()`:**
- All scenarios ramp in from a shared 2025 baseline (no discontinuities)
- Income split into: concentrated capital, yeomen, DAO, and labour — each with distinct tax treatment and MPC
- Human-economy wages are _derived_ from consumption flows, not assumed
- Home production buffer reduces cash welfare requirement
- `tax_lost_leakage_bn` column tracks enforcement gap diagnostics

## SFC + LLM Model

```bash
pip install numpy pandas matplotlib google-genai
export GEMINI_API_KEY=AIzaSyDDN8W_1VhSUJhNuu3VmD1XYB5JIJSFoAM
python3 model_sfc_llm.py "Fast / High yeomen / High tax"
```

- `model_sfc.py` — Stock-Flow Consistent base model (6 household types, balance sheet tracking, `monopoly_rent` param)
- `model_sfc_llm.py` — Gemini Flash LLM layer; overrides household `decide()` with structured JSON prompt; caches responses in `.llm_cache/`
- Current model: `gemini-2.5-flash` (gemini-2.0-flash deprecated)
- `MODELS.md` — Documents alternative model families (HANK, ABM, LLM-SFC) with references
