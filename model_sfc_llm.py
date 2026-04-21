"""
SFC Model with LLM Household Decisions (Gemini Flash)
======================================================
Subclasses HouseholdBehaviour from model_sfc.py and replaces
the fixed-rule decide() method with a Gemini Flash call.

Each simulated year, each of 6 household types receives a structured
prompt describing their personal financial situation and the macro
environment. Gemini returns a JSON spending/saving decision.

Setup
-----
    pip install google-genai

    export GEMINI_API_KEY=your_key_here
    python model_sfc_llm.py

Cost estimate
-------------
~6 types × 35 years = 210 LLM calls per full scenario run.
Gemini Flash pricing is negligible at this scale.

Model string
------------
Set GEMINI_MODEL below. Typical values:
    "gemini-2.0-flash"
    "gemini-2.5-flash"   (if available in your project)
"""

import os
import json
import time
import hashlib
from pathlib import Path

from model_sfc import (
    Params, SFCModel, HouseholdBehaviour,
    SCENARIOS_SFC, plot_sfc,
)

# ── Config ───────────────────────────────────────────────────────────────────

GEMINI_MODEL  = "gemini-2.5-flash"    # ← change to your available model
CACHE_DIR     = Path(".llm_cache")    # cache responses to avoid re-calling
VERBOSE       = True                  # print LLM reasoning each step
MEMORY_WINDOW = 3                     # years of prior decisions fed back into prompt

# ── Household personas ────────────────────────────────────────────────────────

PERSONAS = {
    0: {
        "name": "Concentrated capital owner",
        "description": (
            "You are a wealthy individual or institutional investor. Most of your "
            "income comes from dividends, capital gains, and returns on AI/robotic "
            "capital you own. You have high financial literacy, a long time horizon, "
            "and advisors who help you optimise tax and investment strategy. "
            "You tend to save and reinvest rather than spend, and you are sensitive "
            "to asset price changes and policy risk."
        ),
    },
    1: {
        "name": "Yeomen enterprise operator",
        "description": (
            "You run a small AI-augmented business — perhaps a design studio, "
            "logistics coordinator, legal drafting service, or agricultural operation "
            "using robotics. Your income is business revenue minus costs (AI compute, "
            "equipment loans). You think like a business owner: reinvest when confident, "
            "cut costs when uncertain, and borrow to grow if the opportunity is clear. "
            "You are aware that big platforms could undercut you if they choose to."
        ),
    },
    2: {
        "name": "DAO / commons contributor",
        "description": (
            "You contribute to a commons-governed AI model, open-source project, "
            "or physical cooperative (energy, agriculture, equipment pool). "
            "Your income comes from the commons DAO revenue share. You value "
            "community, tend to spend on experiences and human services, and "
            "reinvest some income back into commons projects. You are moderately "
            "financially secure but not wealthy."
        ),
    },
    3: {
        "name": "Displaced worker on UBI",
        "description": (
            "You recently lost your job to automation. You receive a Universal "
            "Basic Income from the government plus a small compute dividend if "
            "the public AI pool is active. Your savings are limited. You are "
            "anxious about the future, trying to retrain, and cutting non-essential "
            "spending. You prioritise food, housing, utilities, and healthcare. "
            "If income is very low you may need to borrow for essentials."
        ),
    },
    4: {
        "name": "Compute dividend recipient",
        "description": (
            "You receive a per-adult dividend from the public AI infrastructure pool. "
            "This may be your primary income if you are not working. The dividend "
            "feels like a small windfall — unconditional and regular. You tend to "
            "spend most of it, perhaps on experiences, small luxuries, or paying "
            "down debt. You are cautiously optimistic about the future."
        ),
    },
    5: {
        "name": "Human economy worker",
        "description": (
            "You work in a sector that remains irreducibly human: care work, "
            "skilled trades, teaching, performance, therapy, bespoke crafts. "
            "Your wage has held up because AI cannot fully substitute for you, "
            "but your cost of living (especially housing) has risen. You spend "
            "most of your income, save a small amount, and are cautious about debt."
        ),
    },
}


# ── LLM client (lazy init) ────────────────────────────────────────────────────

_client = None

def get_client():
    global _client
    if _client is None:
        try:
            from google import genai
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY environment variable not set.\n"
                    "Export it: export GEMINI_API_KEY=your_key_here"
                )
            _client = genai.Client(api_key=api_key)
        except ImportError:
            raise ImportError(
                "google-genai not installed.\n"
                "Run: pip install google-genai"
            )
    return _client


# ── Response cache ────────────────────────────────────────────────────────────

def _cache_key(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()

def _load_cache(key: str) -> dict | None:
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None

def _save_cache(key: str, data: dict):
    CACHE_DIR.mkdir(exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(data, indent=2))


# ── LLM household behaviour ───────────────────────────────────────────────────

class GeminiHouseholdBehaviour(HouseholdBehaviour):
    """
    Replaces fixed-rule decide() with a Gemini Flash call.
    Falls back to fixed rules if the API call fails.
    """

    def __init__(self, params: Params, use_cache: bool = True):
        super().__init__(params)
        self.use_cache = use_cache
        self.memory: dict[int, list[dict]] = {}  # hh_idx -> list of annual records

    def decide(
        self,
        hh_idx: int,
        income_k: float,
        wealth_k: float,
        debt_k: float,
        interest_burden_k: float,
        unemployment: bool,
        economic_context: dict,
        t: int,
    ) -> dict:

        persona  = PERSONAS[hh_idx]
        year     = economic_context.get("year", 2025)
        know_pct = economic_context.get("know_auto_pct", 0.0)
        phys_pct = economic_context.get("phys_auto_pct", 0.0)
        ubi_k    = economic_context.get("ubi_k", 0.0)
        div_k    = economic_context.get("compute_div_k", 0.0)
        disp_m   = economic_context.get("total_displaced_m", 0.0)

        net_worth_k    = wealth_k - debt_k
        debt_burden_pct= (interest_burden_k / max(income_k, 1)) * 100

        # Retrieve recent memory for this household (up to MEMORY_WINDOW years)
        prior_records = self.memory.get(hh_idx, [])
        recent_memory = prior_records[-MEMORY_WINDOW:]

        # Build memory section for prompt (only if prior history exists)
        if recent_memory:
            memory_lines = ["YOUR RECENT DECISIONS AND OUTCOMES:"]
            for rec in recent_memory:
                borrow_desc = (f"borrowed ${rec['borrow_k']:.0f}k"
                               if rec["borrow"] else "did not borrow")
                memory_lines.append(
                    f"[Year {rec['year']}]: Income ${rec['income_k']:.0f}k, "
                    f"Net wealth ${rec['net_worth_k']:.0f}k, Debt ${rec['debt_k']:.0f}k"
                )
                memory_lines.append(
                    f"  → You chose: consume {rec['consume_fraction']*100:.0f}% of income, "
                    f"{borrow_desc}"
                )
                if rec.get("reasoning"):
                    memory_lines.append(f"  → Reasoning: \"{rec['reasoning']}\"")
            memory_lines.append(
                "\nNote how your financial position has changed. "
                "Your current situation is shown below."
            )
            memory_section = "\n".join(memory_lines) + "\n\n"
        else:
            memory_section = ""

        prompt = f"""You are making financial decisions as a {persona['name']} in {year}.

PERSONA:
{persona['description']}

{memory_section}YOUR CURRENT FINANCIAL SITUATION:
- Annual income: ${income_k:.0f}k/yr
- Net wealth: ${net_worth_k:.0f}k (wealth ${wealth_k:.0f}k, debt ${debt_k:.0f}k)
- Annual interest payments on debt: ${interest_burden_k:.1f}k ({debt_burden_pct:.0f}% of income)
- Currently unemployed or primarily on transfers: {unemployment}

ECONOMIC ENVIRONMENT ({year}):
- Knowledge work automated: {know_pct:.0f}%
- Physical work automated: {phys_pct:.0f}%
- Workers displaced and without income: {disp_m:.0f} million
- Government UBI payment (if applicable): ${ubi_k:.1f}k/yr per person
- Citizen compute dividend (if public AI pool active): ${div_k:.1f}k/yr per person

TASK:
Decide how you will allocate your income this year. Think carefully about:
- Your income security and whether it might fall further
- Whether you need to save more (precautionary) or can afford to spend
- How much of your spending goes to human services (care, crafts, education,
  experiences, therapy, bespoke goods) vs cheap automated goods and services
- Whether you would borrow to maintain living standards if income is low
- Any changes in your behaviour compared to a normal year

Respond ONLY with a JSON object in exactly this format:
{{
  "consume_fraction": 0.82,
  "human_svc_share": 0.15,
  "borrow": false,
  "borrow_k": 0,
  "reasoning": "One or two sentences explaining your decision."
}}

Rules:
- consume_fraction: fraction of income consumed (0.0 to 1.20; can exceed 1 if drawing on savings)
- human_svc_share: fraction of consumption on human/irreplaceable services (0.0 to 0.60)
- borrow: true if you take on new debt this period
- borrow_k: additional debt in $k (0 if borrow=false)
- reasoning: brief plain-English explanation
"""

        # Cache key is based on full prompt (includes memory), so cache is
        # memory-aware: same situation + same history → cache hit; novel → miss
        cache_key = _cache_key(prompt)
        if self.use_cache:
            cached = _load_cache(cache_key)
            if cached:
                # Append to memory on cache hit as well
                self.memory.setdefault(hh_idx, []).append({
                    "year":             year,
                    "income_k":         income_k,
                    "net_worth_k":      net_worth_k,
                    "debt_k":           debt_k,
                    "consume_fraction": cached["consume_k"] / max(income_k, 1),
                    "borrow":           cached.get("borrow", False),
                    "borrow_k":         cached.get("borrow_k", 0.0),
                    "reasoning":        str(cached.get("reasoning", ""))[:120],
                })
                return cached

        # Call Gemini
        try:
            client = get_client()
            from google.genai import types
            response = client.models.generate_content(
                model   = GEMINI_MODEL,
                contents= prompt,
                config  = types.GenerateContentConfig(
                    temperature      = 0.7,
                    response_mime_type = "application/json",
                ),
            )
            raw = response.text.strip()
            data = json.loads(raw)

            # Validate and clamp
            consume_fraction = float(data.get("consume_fraction", 0.80))
            decision = {
                "consume_k":       consume_fraction * income_k,
                "human_svc_share": float(max(0.0, min(0.60, data.get("human_svc_share", 0.12)))),
                "auto_goods_share":1.0 - float(data.get("human_svc_share", 0.12)),
                "borrow":          bool(data.get("borrow", False)),
                "borrow_k":        float(data.get("borrow_k", 0.0)),
                "reasoning":       str(data.get("reasoning", "")),
            }
            decision["consume_k"] = max(0.0, decision["consume_k"])

            if VERBOSE:
                print(f"    [{year}] {persona['name'][:30]:30s} "
                      f"consume={data.get('consume_fraction', 0):.2f} "
                      f"human_svc={data.get('human_svc_share', 0):.2f} "
                      f"| {data.get('reasoning', '')[:80]}")

            if self.use_cache:
                _save_cache(cache_key, decision)

            # Append to memory
            self.memory.setdefault(hh_idx, []).append({
                "year":             year,
                "income_k":         income_k,
                "net_worth_k":      net_worth_k,
                "debt_k":           debt_k,
                "consume_fraction": consume_fraction,
                "borrow":           decision["borrow"],
                "borrow_k":         decision["borrow_k"],
                "reasoning":        str(data.get("reasoning", ""))[:120],
            })

            return decision

        except Exception as e:
            print(f"    [LLM ERROR] {persona['name']}: {e} — using fixed rules")
            # Fall back to parent fixed-rule behaviour
            fallback = super().decide(
                hh_idx=hh_idx, income_k=income_k, wealth_k=wealth_k,
                debt_k=debt_k, interest_burden_k=interest_burden_k,
                unemployment=unemployment, economic_context=economic_context, t=t,
            )
            # Append fallback decision to memory so history is continuous
            self.memory.setdefault(hh_idx, []).append({
                "year":             year,
                "income_k":         income_k,
                "net_worth_k":      net_worth_k,
                "debt_k":           debt_k,
                "consume_fraction": fallback["consume_k"] / max(income_k, 1),
                "borrow":           fallback.get("borrow", False),
                "borrow_k":         fallback.get("borrow_k", 0.0),
                "reasoning":        str(fallback.get("reasoning", ""))[:120],
            })
            return fallback


# ── Run ───────────────────────────────────────────────────────────────────────

def run_llm_scenario(scenario_name: str, scenario_params: dict) -> "pd.DataFrame":
    import pandas as pd

    params_dict = {k: v for k, v in scenario_params.items()
                   if k in Params.__dataclass_fields__}
    p  = Params(**params_dict)
    bh = GeminiHouseholdBehaviour(p, use_cache=True)
    model = SFCModel(p, behaviour=bh)

    print(f"\n{'─'*60}")
    print(f"  LLM Scenario: {scenario_name}")
    print(f"  Model: {GEMINI_MODEL}")
    print(f"{'─'*60}")

    df = model.run()
    return df


def run_comparison(scenario_name: str = "Fast / High yeomen / High tax"):
    """
    Run one scenario with fixed rules and one with LLM decisions, compare.
    """
    from model_sfc import SFCModel, Params, plot_sfc
    import pandas as pd

    params_dict = {k: v for k, v in SCENARIOS_SFC[scenario_name].items()
                   if k in Params.__dataclass_fields__}
    p = Params(**params_dict)

    # Fixed rules
    print("Running with fixed rules...")
    df_fixed = SFCModel(p).run()

    # LLM decisions
    print("Running with Gemini household decisions...")
    df_llm = run_llm_scenario(scenario_name, SCENARIOS_SFC[scenario_name])

    results = {
        f"{scenario_name} [fixed rules]": df_fixed,
        f"{scenario_name} [Gemini LLM]":  df_llm,
    }

    plot_sfc(results, outfile="ai_economy_sfc_llm.png")

    # Summary comparison
    print(f"\n{'Metric':<35} {'Fixed rules':>15} {'Gemini LLM':>15}")
    print("-" * 65)
    metrics = [
        ("gini_proxy",          "Gini t+10",            "{:.3f}"),
        ("effective_welfare_k", "Welfare t+10 ($k)",    "${:.0f}k"),
        ("gdp_nom_bn",          "Nominal GDP t+10 ($T)",lambda v: f"${v/1000:.1f}T"),
        ("cons_human_svcs_bn",  "Human economy t+10",   lambda v: f"${v/1000:.1f}T"),
        ("debt_gdp_ratio",      "Debt/GDP t+10",        "{:.2f}x"),
    ]
    for col, label, fmt in metrics:
        v_fixed = df_fixed[df_fixed.t == 10][col].values[0]
        v_llm   = df_llm  [df_llm.t   == 10][col].values[0]
        if callable(fmt):
            print(f"{label:<35} {fmt(v_fixed):>15} {fmt(v_llm):>15}")
        else:
            print(f"{label:<35} {fmt.format(v_fixed):>15} {fmt.format(v_llm):>15}")

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        scenario = " ".join(sys.argv[1:])
    else:
        scenario = "Fast / High yeomen / High tax"

    if scenario not in SCENARIOS_SFC:
        print(f"Unknown scenario. Available:\n" +
              "\n".join(f"  {k}" for k in SCENARIOS_SFC))
        sys.exit(1)

    run_comparison(scenario)
