"""
Agent Archetypes — Consumer & Enterprise
=========================================
Calibrated to US 2024/2025 economy.

Sources:
  - BLS Occupational Employment & Wage Statistics (OES) May 2023
  - Census ACS 2022 (income distributions)
  - Fed Survey of Consumer Finances (SCF) 2022
  - BEA Industry Value-Added 2023
  - Census SUSB 2021 (firm size distributions)

Each archetype is a dict with:
  - name: human-readable label
  - category: grouping for analysis
  - pop_weight: fraction of 260M US adults in this archetype
  - income_mean_k: mean annual income ($k)
  - income_sigma_k: std dev for stochastic instantiation
  - wealth_mean_k: mean net wealth ($k)
  - wealth_sigma_k: std dev (lognormal draws)
  - debt_mean_k: mean outstanding debt ($k)
  - auto_exposure: 0-1 how much of this job is automatable by AI
  - auto_type: "knowledge" or "physical" or "mixed" — which S-curve hits
  - human_svc_share: fraction of consumption going to human services
  - sector_demand: which enterprise sectors this consumer buys from
  - retraining_years: expected time to retrain if displaced
  - description: persona description for LLM decide()

Pop weights across all consumer archetypes must sum to ~1.0 (some residual OK).
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONSUMER ARCHETYPES (~75)
# ─────────────────────────────────────────────────────────────────────────────

CONSUMER_ARCHETYPES = [

    # ── Knowledge work — HIGH automation exposure ────────────────────────────

    {
        "name": "junior_paralegal",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0012,   # ~310k paralegals, BLS 23-2011
        "income_mean_k": 62,
        "income_sigma_k": 18,
        "wealth_mean_k": 45,
        "wealth_sigma_k": 60,
        "debt_mean_k": 38,
        "auto_exposure": 0.85,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a junior paralegal at a mid-size law firm. Your work — document review, "
            "contract drafting, legal research — is increasingly done by AI. You have student "
            "loans, rent in a mid-cost city, and are worried about your job security. You spend "
            "carefully and are considering retraining."
        ),
    },
    {
        "name": "senior_litigator",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0035,   # ~900k lawyers, fraction doing litigation
        "income_mean_k": 185,
        "income_sigma_k": 80,
        "wealth_mean_k": 420,
        "wealth_sigma_k": 350,
        "debt_mean_k": 95,
        "auto_exposure": 0.55,
        "auto_type": "knowledge",
        "human_svc_share": 0.22,
        "sector_demand": ["luxury_retail", "hospitality", "healthcare", "financial_services"],
        "retraining_years": 3.0,
        "description": (
            "You are a senior litigator. AI handles research and brief drafting, but client "
            "relationships, courtroom presence, and strategic judgment remain yours. Your income "
            "is high but you're seeing junior associates replaced. You have a mortgage, kids in "
            "private school, and significant retirement savings."
        ),
    },
    {
        "name": "tax_accountant",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0052,   # ~1.35M accountants/auditors, BLS 13-2011
        "income_mean_k": 82,
        "income_sigma_k": 25,
        "wealth_mean_k": 180,
        "wealth_sigma_k": 150,
        "debt_mean_k": 55,
        "auto_exposure": 0.80,
        "auto_type": "knowledge",
        "human_svc_share": 0.14,
        "sector_demand": ["retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 2.5,
        "description": (
            "You are a tax accountant. AI now handles most returns and compliance work. "
            "Advisory and complex planning remain, but volume clients are disappearing. "
            "You have moderate savings and a mortgage. You're concerned about the next "
            "few years but not panicked."
        ),
    },
    {
        "name": "bookkeeper",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0045,   # ~1.17M, BLS 43-3031
        "income_mean_k": 47,
        "income_sigma_k": 12,
        "wealth_mean_k": 35,
        "wealth_sigma_k": 40,
        "debt_mean_k": 28,
        "auto_exposure": 0.92,
        "auto_type": "knowledge",
        "human_svc_share": 0.10,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You are a bookkeeper. AI handles invoicing, reconciliation, and payroll almost "
            "entirely. Your job is being eliminated. You have modest savings, possibly a "
            "working spouse, and are looking at retraining options."
        ),
    },
    {
        "name": "financial_analyst",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0028,   # ~730k, BLS 13-2051
        "income_mean_k": 105,
        "income_sigma_k": 40,
        "wealth_mean_k": 220,
        "wealth_sigma_k": 200,
        "debt_mean_k": 65,
        "auto_exposure": 0.75,
        "auto_type": "knowledge",
        "human_svc_share": 0.18,
        "sector_demand": ["retail", "hospitality", "financial_services", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a financial analyst. AI generates reports, models, and forecasts faster "
            "than you can. Senior relationship management and judgment calls persist but fewer "
            "analysts are needed. You have good savings and marketable quantitative skills."
        ),
    },
    {
        "name": "junior_software_engineer",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0055,   # ~1.4M software devs, junior fraction
        "income_mean_k": 95,
        "income_sigma_k": 30,
        "wealth_mean_k": 80,
        "wealth_sigma_k": 100,
        "debt_mean_k": 40,
        "auto_exposure": 0.70,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["retail", "hospitality", "tech_services", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You are a junior software engineer. AI writes most boilerplate code and can "
            "handle many feature implementations. You're being pushed toward architecture "
            "and system design roles but competition is fierce. Student debt is manageable, "
            "savings are growing."
        ),
    },
    {
        "name": "senior_staff_engineer",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0035,   # senior fraction of ~1.8M
        "income_mean_k": 210,
        "income_sigma_k": 70,
        "wealth_mean_k": 550,
        "wealth_sigma_k": 400,
        "debt_mean_k": 120,
        "auto_exposure": 0.45,
        "auto_type": "knowledge",
        "human_svc_share": 0.20,
        "sector_demand": ["luxury_retail", "hospitality", "tech_services", "healthcare"],
        "retraining_years": 2.0,
        "description": (
            "You are a senior/staff engineer. AI handles implementation but you design "
            "systems, make architectural decisions, and mentor. Your role is shrinking "
            "slowly as AI handles more complex tasks. High income, significant equity "
            "compensation, mortgage on an expensive home."
        ),
    },
    {
        "name": "ml_researcher",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0008,   # ~200k ML/AI researchers
        "income_mean_k": 180,
        "income_sigma_k": 60,
        "wealth_mean_k": 350,
        "wealth_sigma_k": 300,
        "debt_mean_k": 60,
        "auto_exposure": 0.40,
        "auto_type": "knowledge",
        "human_svc_share": 0.18,
        "sector_demand": ["tech_services", "hospitality", "healthcare"],
        "retraining_years": 3.0,
        "description": (
            "You are an ML researcher. Ironically, AI is automating AI research itself — "
            "automated experiment design, architecture search. The frontier moves fast. "
            "Your skills are in high demand now but the window may be closing. High income, "
            "substantial savings, equity in AI companies."
        ),
    },
    {
        "name": "graphic_designer",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0025,   # ~650k, BLS 27-1024
        "income_mean_k": 58,
        "income_sigma_k": 20,
        "wealth_mean_k": 40,
        "wealth_sigma_k": 50,
        "debt_mean_k": 30,
        "auto_exposure": 0.82,
        "auto_type": "knowledge",
        "human_svc_share": 0.14,
        "sector_demand": ["retail", "hospitality", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a graphic designer. AI image generation has decimated commodity "
            "design work. Brand identity and creative direction remain but at lower "
            "volumes. Freelance income is unstable. You have modest savings and are "
            "considering pivoting to UX or creative direction."
        ),
    },
    {
        "name": "copywriter",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0015,   # ~400k writers/authors, BLS 27-3043
        "income_mean_k": 52,
        "income_sigma_k": 22,
        "wealth_mean_k": 35,
        "wealth_sigma_k": 45,
        "debt_mean_k": 25,
        "auto_exposure": 0.88,
        "auto_type": "knowledge",
        "human_svc_share": 0.13,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a copywriter. AI writes marketing copy, product descriptions, "
            "and content at scale. Human voice and strategy still have value but "
            "the market has collapsed. Income is down 40% from peak. You're drawing "
            "on savings and considering other careers."
        ),
    },
    {
        "name": "translator_interpreter",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0008,   # ~210k, BLS 27-3091
        "income_mean_k": 55,
        "income_sigma_k": 18,
        "wealth_mean_k": 50,
        "wealth_sigma_k": 55,
        "debt_mean_k": 20,
        "auto_exposure": 0.90,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.5,
        "description": (
            "You are a translator. Machine translation has reached near-human quality "
            "for most language pairs. Only literary, legal, and diplomatic translation "
            "persist. Your income has dropped sharply and you're considering retraining."
        ),
    },
    {
        "name": "data_entry_clerk",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0012,   # ~310k, BLS 43-9021
        "income_mean_k": 38,
        "income_sigma_k": 10,
        "wealth_mean_k": 15,
        "wealth_sigma_k": 20,
        "debt_mean_k": 18,
        "auto_exposure": 0.95,
        "auto_type": "knowledge",
        "human_svc_share": 0.08,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a data entry clerk. Your job is almost entirely automated. "
            "You have very limited savings and are already looking for new work. "
            "Bills are tight."
        ),
    },
    {
        "name": "insurance_claims_adjuster",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0012,   # ~320k, BLS 13-1031
        "income_mean_k": 72,
        "income_sigma_k": 18,
        "wealth_mean_k": 90,
        "wealth_sigma_k": 80,
        "debt_mean_k": 45,
        "auto_exposure": 0.78,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["retail", "hospitality", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are an insurance claims adjuster. AI handles routine claims end-to-end. "
            "Complex and contested claims still need human judgment but volumes are falling. "
            "You have a family, a mortgage, and moderate savings."
        ),
    },
    {
        "name": "hr_generalist",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0025,   # ~650k HR specialists, BLS 13-1071
        "income_mean_k": 68,
        "income_sigma_k": 20,
        "wealth_mean_k": 75,
        "wealth_sigma_k": 70,
        "debt_mean_k": 40,
        "auto_exposure": 0.72,
        "auto_type": "knowledge",
        "human_svc_share": 0.14,
        "sector_demand": ["retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are an HR generalist. AI handles screening, onboarding paperwork, "
            "benefits admin, and basic employee queries. Culture, conflict resolution, "
            "and strategic workforce planning remain but fewer HR staff are needed."
        ),
    },
    {
        "name": "management_consultant",
        "category": "knowledge_high_exposure",
        "pop_weight": 0.0030,   # ~780k management analysts, BLS 13-1111
        "income_mean_k": 120,
        "income_sigma_k": 50,
        "wealth_mean_k": 200,
        "wealth_sigma_k": 180,
        "debt_mean_k": 55,
        "auto_exposure": 0.60,
        "auto_type": "knowledge",
        "human_svc_share": 0.18,
        "sector_demand": ["hospitality", "luxury_retail", "healthcare", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a management consultant. AI generates analyses and slide decks "
            "that used to take associates weeks. Client relationships and executive "
            "coaching persist but team sizes are shrinking. High income, high spending."
        ),
    },

    # ── Knowledge work — LOWER exposure ──────────────────────────────────────

    {
        "name": "psychotherapist",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0028,   # ~730k MH counselors + psychologists
        "income_mean_k": 65,
        "income_sigma_k": 20,
        "wealth_mean_k": 110,
        "wealth_sigma_k": 100,
        "debt_mean_k": 60,
        "auto_exposure": 0.15,
        "auto_type": "knowledge",
        "human_svc_share": 0.20,
        "sector_demand": ["grocery", "retail", "housing", "healthcare"],
        "retraining_years": 4.0,
        "description": (
            "You are a psychotherapist. Human connection is your product — AI chatbots "
            "handle some low-acuity support but clients with real needs want a human. "
            "Demand for your services is actually rising as automation-driven anxiety "
            "spreads. Student debt from grad school is significant."
        ),
    },
    {
        "name": "investigative_journalist",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0004,   # ~100k reporters, fraction doing investigative
        "income_mean_k": 55,
        "income_sigma_k": 20,
        "wealth_mean_k": 40,
        "wealth_sigma_k": 50,
        "debt_mean_k": 25,
        "auto_exposure": 0.30,
        "auto_type": "knowledge",
        "human_svc_share": 0.15,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are an investigative journalist. AI writes commodity news but deep "
            "investigation — sources, FOIA, fieldwork — remains human. Revenue models "
            "are precarious. You're modestly paid with limited savings."
        ),
    },
    {
        "name": "research_scientist",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0020,   # ~520k natural scientists + social scientists
        "income_mean_k": 95,
        "income_sigma_k": 30,
        "wealth_mean_k": 180,
        "wealth_sigma_k": 150,
        "debt_mean_k": 45,
        "auto_exposure": 0.35,
        "auto_type": "knowledge",
        "human_svc_share": 0.16,
        "sector_demand": ["retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 4.0,
        "description": (
            "You are a research scientist. AI accelerates your work enormously — literature "
            "review, experiment design, data analysis — but hypothesis generation and "
            "experimental creativity remain human. Funding is competitive but stable."
        ),
    },
    {
        "name": "judge",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0002,   # ~45k judges, BLS 23-1023
        "income_mean_k": 155,
        "income_sigma_k": 35,
        "wealth_mean_k": 450,
        "wealth_sigma_k": 300,
        "debt_mean_k": 80,
        "auto_exposure": 0.15,
        "auto_type": "knowledge",
        "human_svc_share": 0.22,
        "sector_demand": ["hospitality", "luxury_retail", "healthcare"],
        "retraining_years": 5.0,
        "description": (
            "You are a judge. AI assists with case research and precedent analysis "
            "but judicial authority, constitutional interpretation, and courtroom "
            "management cannot be automated. Your position is secure. High income, "
            "pension, strong financial position."
        ),
    },
    {
        "name": "senior_executive",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0030,   # ~780k chief executives, BLS 11-1011
        "income_mean_k": 250,
        "income_sigma_k": 150,
        "wealth_mean_k": 1200,
        "wealth_sigma_k": 1500,
        "debt_mean_k": 200,
        "auto_exposure": 0.20,
        "auto_type": "knowledge",
        "human_svc_share": 0.28,
        "sector_demand": ["luxury_retail", "hospitality", "financial_services", "healthcare"],
        "retraining_years": 3.0,
        "description": (
            "You are a senior executive (C-suite or VP). AI handles analytics and "
            "operational decisions but strategy, board management, and organizational "
            "leadership remain human. Very high income with significant equity. "
            "Low MPC — you save and invest most of your income."
        ),
    },
    {
        "name": "university_professor",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0045,   # ~1.17M postsecondary teachers
        "income_mean_k": 88,
        "income_sigma_k": 30,
        "wealth_mean_k": 250,
        "wealth_sigma_k": 200,
        "debt_mean_k": 55,
        "auto_exposure": 0.30,
        "auto_type": "knowledge",
        "human_svc_share": 0.18,
        "sector_demand": ["retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 4.0,
        "description": (
            "You are a university professor. AI tutoring threatens the teaching side "
            "but research, mentorship, and academic culture persist. Tenure provides "
            "security. Moderate income with decent retirement savings."
        ),
    },
    {
        "name": "physician",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0035,   # ~900k physicians/surgeons
        "income_mean_k": 280,
        "income_sigma_k": 100,
        "wealth_mean_k": 600,
        "wealth_sigma_k": 500,
        "debt_mean_k": 180,
        "auto_exposure": 0.25,
        "auto_type": "knowledge",
        "human_svc_share": 0.25,
        "sector_demand": ["luxury_retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 5.0,
        "description": (
            "You are a physician. AI handles diagnostics and treatment planning "
            "increasingly well but surgery, bedside manner, and complex cases remain "
            "human. Very high income but also very high student debt. Savings grow "
            "after loans are paid down."
        ),
    },
    {
        "name": "corporate_lawyer",
        "category": "knowledge_low_exposure",
        "pop_weight": 0.0020,   # fraction of ~800k lawyers doing transactional
        "income_mean_k": 195,
        "income_sigma_k": 85,
        "wealth_mean_k": 400,
        "wealth_sigma_k": 350,
        "debt_mean_k": 100,
        "auto_exposure": 0.50,
        "auto_type": "knowledge",
        "human_svc_share": 0.22,
        "sector_demand": ["luxury_retail", "hospitality", "financial_services"],
        "retraining_years": 3.0,
        "description": (
            "You are a corporate/transactional lawyer. AI handles due diligence, "
            "contract review, and regulatory filings. Client relationships and deal "
            "structuring remain but team sizes are shrinking significantly."
        ),
    },

    # ── Skilled physical — MEDIUM exposure ───────────────────────────────────

    {
        "name": "plumber",
        "category": "skilled_physical",
        "pop_weight": 0.0018,   # ~480k, BLS 47-2152
        "income_mean_k": 65,
        "income_sigma_k": 18,
        "wealth_mean_k": 95,
        "wealth_sigma_k": 80,
        "debt_mean_k": 35,
        "auto_exposure": 0.15,
        "auto_type": "physical",
        "human_svc_share": 0.10,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are a plumber. Robots can't navigate crawl spaces or diagnose "
            "old plumbing. AI helps with scheduling and quoting. Your income is "
            "stable and may rise as other trades get automated. You have a van, "
            "tools, and moderate savings."
        ),
    },
    {
        "name": "electrician",
        "category": "skilled_physical",
        "pop_weight": 0.0028,   # ~730k, BLS 47-2111
        "income_mean_k": 65,
        "income_sigma_k": 18,
        "wealth_mean_k": 90,
        "wealth_sigma_k": 75,
        "debt_mean_k": 30,
        "auto_exposure": 0.18,
        "auto_type": "physical",
        "human_svc_share": 0.10,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are an electrician. Wiring, panel upgrades, and troubleshooting "
            "remain highly manual. AI helps with code compliance and load calculations. "
            "Demand is strong from EV charger and solar installations."
        ),
    },
    {
        "name": "hvac_technician",
        "category": "skilled_physical",
        "pop_weight": 0.0015,   # ~394k, BLS 49-9021
        "income_mean_k": 58,
        "income_sigma_k": 15,
        "wealth_mean_k": 70,
        "wealth_sigma_k": 60,
        "debt_mean_k": 28,
        "auto_exposure": 0.20,
        "auto_type": "physical",
        "human_svc_share": 0.10,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.5,
        "description": (
            "You are an HVAC technician. Installation and repair remain hands-on. "
            "AI assists with diagnostics and predictive maintenance. Stable demand."
        ),
    },
    {
        "name": "carpenter",
        "category": "skilled_physical",
        "pop_weight": 0.0028,   # ~725k, BLS 47-2031
        "income_mean_k": 55,
        "income_sigma_k": 16,
        "wealth_mean_k": 65,
        "wealth_sigma_k": 55,
        "debt_mean_k": 25,
        "auto_exposure": 0.25,
        "auto_type": "physical",
        "human_svc_share": 0.10,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.5,
        "description": (
            "You are a carpenter. Prefab and CNC cut into some work but on-site "
            "framing, finishing, and renovation remain manual. Income is variable "
            "with construction cycles."
        ),
    },
    {
        "name": "welder",
        "category": "skilled_physical",
        "pop_weight": 0.0015,   # ~400k, BLS 51-4121
        "income_mean_k": 50,
        "income_sigma_k": 14,
        "wealth_mean_k": 55,
        "wealth_sigma_k": 50,
        "debt_mean_k": 22,
        "auto_exposure": 0.40,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a welder. Robotic welding handles production runs but field "
            "welding, repair, and custom fabrication remain human. Income is moderate."
        ),
    },
    {
        "name": "machinist",
        "category": "skilled_physical",
        "pop_weight": 0.0012,   # ~315k, BLS 51-4041
        "income_mean_k": 52,
        "income_sigma_k": 14,
        "wealth_mean_k": 60,
        "wealth_sigma_k": 55,
        "debt_mean_k": 20,
        "auto_exposure": 0.50,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a machinist. CNC does most production but setup, programming, "
            "and prototype work need you. The shift to AI-designed parts may change "
            "demand patterns."
        ),
    },
    {
        "name": "auto_mechanic",
        "category": "skilled_physical",
        "pop_weight": 0.0028,   # ~740k, BLS 49-3023
        "income_mean_k": 50,
        "income_sigma_k": 14,
        "wealth_mean_k": 55,
        "wealth_sigma_k": 50,
        "debt_mean_k": 22,
        "auto_exposure": 0.30,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are an auto mechanic. EV transition is changing your work — simpler "
            "drivetrains but more electronics. Diagnostics are AI-assisted. Demand "
            "remains as long as people drive."
        ),
    },
    {
        "name": "heavy_equipment_operator",
        "category": "skilled_physical",
        "pop_weight": 0.0018,   # ~475k, BLS 47-2073
        "income_mean_k": 55,
        "income_sigma_k": 15,
        "wealth_mean_k": 60,
        "wealth_sigma_k": 55,
        "debt_mean_k": 25,
        "auto_exposure": 0.45,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a heavy equipment operator. Autonomous dozers and excavators are "
            "coming but unstructured sites still need human operators. Union protection "
            "slows displacement."
        ),
    },
    {
        "name": "surgical_technician",
        "category": "skilled_physical",
        "pop_weight": 0.0005,   # ~120k, BLS 29-2055
        "income_mean_k": 58,
        "income_sigma_k": 12,
        "wealth_mean_k": 50,
        "wealth_sigma_k": 45,
        "debt_mean_k": 30,
        "auto_exposure": 0.25,
        "auto_type": "physical",
        "human_svc_share": 0.12,
        "sector_demand": ["retail", "grocery", "healthcare", "housing"],
        "retraining_years": 2.5,
        "description": (
            "You are a surgical technician. Robotic surgery is growing but you still "
            "prep, hand instruments, and assist. Demand tracks surgical volume."
        ),
    },
    {
        "name": "dental_hygienist",
        "category": "skilled_physical",
        "pop_weight": 0.0008,   # ~220k, BLS 29-1292
        "income_mean_k": 82,
        "income_sigma_k": 15,
        "wealth_mean_k": 120,
        "wealth_sigma_k": 100,
        "debt_mean_k": 40,
        "auto_exposure": 0.15,
        "auto_type": "physical",
        "human_svc_share": 0.14,
        "sector_demand": ["retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are a dental hygienist. Cleanings, X-rays, and patient education "
            "remain hands-on. AI helps with imaging analysis. Stable income."
        ),
    },
    {
        "name": "pharmacist",
        "category": "skilled_physical",
        "pop_weight": 0.0012,   # ~320k, BLS 29-1051
        "income_mean_k": 130,
        "income_sigma_k": 25,
        "wealth_mean_k": 250,
        "wealth_sigma_k": 200,
        "debt_mean_k": 100,
        "auto_exposure": 0.55,
        "auto_type": "mixed",
        "human_svc_share": 0.16,
        "sector_demand": ["retail", "hospitality", "healthcare", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are a pharmacist. Automated dispensing handles most fills. Clinical "
            "consultations and complex interactions remain. Retail pharmacy is shrinking "
            "but clinical roles grow. High student debt, good income."
        ),
    },
    {
        "name": "registered_nurse",
        "category": "skilled_physical",
        "pop_weight": 0.0115,   # ~3M, BLS 29-1141 — largest single occupation
        "income_mean_k": 82,
        "income_sigma_k": 18,
        "wealth_mean_k": 110,
        "wealth_sigma_k": 90,
        "debt_mean_k": 45,
        "auto_exposure": 0.15,
        "auto_type": "physical",
        "human_svc_share": 0.14,
        "sector_demand": ["retail", "grocery", "healthcare", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are a registered nurse. Patient care, assessment, medication "
            "administration, and emotional support are irreducibly human. AI helps "
            "with charting and monitoring. Demand is strong. Moderate income with "
            "steady growth."
        ),
    },

    # ── Physical — HIGH exposure ─────────────────────────────────────────────

    {
        "name": "warehouse_picker",
        "category": "physical_high_exposure",
        "pop_weight": 0.0060,   # ~1.56M laborers/freight/stock, BLS 53-7062
        "income_mean_k": 36,
        "income_sigma_k": 8,
        "wealth_mean_k": 10,
        "wealth_sigma_k": 15,
        "debt_mean_k": 12,
        "auto_exposure": 0.85,
        "auto_type": "physical",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You work in a warehouse picking and packing orders. Robots are replacing "
            "your job. You have very little savings, rent your home, and live paycheck "
            "to paycheck."
        ),
    },
    {
        "name": "long_haul_trucker",
        "category": "physical_high_exposure",
        "pop_weight": 0.0070,   # ~1.8M heavy truck drivers, BLS 53-3032
        "income_mean_k": 55,
        "income_sigma_k": 12,
        "wealth_mean_k": 45,
        "wealth_sigma_k": 50,
        "debt_mean_k": 30,
        "auto_exposure": 0.70,
        "auto_type": "physical",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You are a long-haul trucker. Autonomous trucks are handling highway segments. "
            "Last-mile and complex routes still need humans. You own or finance your rig. "
            "Savings are modest."
        ),
    },
    {
        "name": "delivery_driver",
        "category": "physical_high_exposure",
        "pop_weight": 0.0055,   # ~1.4M delivery drivers, BLS 53-3031
        "income_mean_k": 38,
        "income_sigma_k": 10,
        "wealth_mean_k": 12,
        "wealth_sigma_k": 18,
        "debt_mean_k": 15,
        "auto_exposure": 0.65,
        "auto_type": "physical",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a delivery driver (last-mile). Autonomous delivery is coming "
            "but urban environments are complex. Gig income, no benefits, minimal savings."
        ),
    },
    {
        "name": "taxi_rideshare_driver",
        "category": "physical_high_exposure",
        "pop_weight": 0.0030,   # ~780k taxi/rideshare
        "income_mean_k": 35,
        "income_sigma_k": 12,
        "wealth_mean_k": 15,
        "wealth_sigma_k": 20,
        "debt_mean_k": 18,
        "auto_exposure": 0.75,
        "auto_type": "physical",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You drive for a rideshare platform. Robotaxis are operational in some cities. "
            "Your income is already declining. Minimal savings, car payment."
        ),
    },
    {
        "name": "retail_cashier",
        "category": "physical_high_exposure",
        "pop_weight": 0.0120,   # ~3.1M cashiers, BLS 41-2011 — very large
        "income_mean_k": 30,
        "income_sigma_k": 6,
        "wealth_mean_k": 5,
        "wealth_sigma_k": 10,
        "debt_mean_k": 8,
        "auto_exposure": 0.88,
        "auto_type": "physical",
        "human_svc_share": 0.05,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a retail cashier. Self-checkout and automated stores are replacing "
            "you. Part-time, low wages, essentially no savings. You depend on every paycheck."
        ),
    },
    {
        "name": "fast_food_worker",
        "category": "physical_high_exposure",
        "pop_weight": 0.0130,   # ~3.4M food prep/serving, BLS 35-3023
        "income_mean_k": 28,
        "income_sigma_k": 6,
        "wealth_mean_k": 3,
        "wealth_sigma_k": 8,
        "debt_mean_k": 6,
        "auto_exposure": 0.72,
        "auto_type": "physical",
        "human_svc_share": 0.05,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You work in fast food. Robotic cooking and automated ordering are displacing "
            "your role. Very low income, zero savings, often working multiple jobs."
        ),
    },
    {
        "name": "factory_assembler",
        "category": "physical_high_exposure",
        "pop_weight": 0.0050,   # ~1.3M assemblers, BLS 51-2098
        "income_mean_k": 38,
        "income_sigma_k": 10,
        "wealth_mean_k": 20,
        "wealth_sigma_k": 25,
        "debt_mean_k": 15,
        "auto_exposure": 0.80,
        "auto_type": "physical",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You work on a factory assembly line. Robots handle most repetitive tasks. "
            "Quality checks and complex assembly still need humans but volumes are falling. "
            "Union provides some protection."
        ),
    },
    {
        "name": "call_centre_agent",
        "category": "physical_high_exposure",
        "pop_weight": 0.0055,   # ~1.4M customer service reps, BLS 43-4051
        "income_mean_k": 38,
        "income_sigma_k": 8,
        "wealth_mean_k": 12,
        "wealth_sigma_k": 18,
        "debt_mean_k": 12,
        "auto_exposure": 0.90,
        "auto_type": "knowledge",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a call centre agent. AI chatbots and voice agents handle 90% of "
            "queries. Only complex escalations remain. Your job is disappearing fast."
        ),
    },
    {
        "name": "security_guard",
        "category": "physical_high_exposure",
        "pop_weight": 0.0040,   # ~1.04M, BLS 33-9032
        "income_mean_k": 35,
        "income_sigma_k": 8,
        "wealth_mean_k": 10,
        "wealth_sigma_k": 15,
        "debt_mean_k": 10,
        "auto_exposure": 0.60,
        "auto_type": "physical",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a security guard. Camera AI and drones handle surveillance. "
            "Physical presence still needed for response but fewer guards required."
        ),
    },
    {
        "name": "janitor_cleaner",
        "category": "physical_high_exposure",
        "pop_weight": 0.0090,   # ~2.3M janitors/cleaners, BLS 37-2011
        "income_mean_k": 32,
        "income_sigma_k": 7,
        "wealth_mean_k": 5,
        "wealth_sigma_k": 10,
        "debt_mean_k": 8,
        "auto_exposure": 0.50,
        "auto_type": "physical",
        "human_svc_share": 0.05,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a janitor/cleaner. Robotic floor cleaners handle open areas but "
            "detailed cleaning (bathrooms, kitchens, offices) remains manual. Low wages, "
            "no savings, often immigrant."
        ),
    },

    # ── Care & human-contact — VERY LOW exposure ─────────────────────────────

    {
        "name": "nursing_aide",
        "category": "care_low_exposure",
        "pop_weight": 0.0055,   # ~1.4M nursing assistants, BLS 31-1131
        "income_mean_k": 35,
        "income_sigma_k": 7,
        "wealth_mean_k": 8,
        "wealth_sigma_k": 12,
        "debt_mean_k": 10,
        "auto_exposure": 0.10,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You are a nursing aide. Bathing, feeding, turning, comforting patients "
            "is irreducibly human. AI helps with scheduling. Low wages despite essential "
            "work. Almost no savings."
        ),
    },
    {
        "name": "elder_care_worker",
        "category": "care_low_exposure",
        "pop_weight": 0.0045,   # ~1.2M home health aides, BLS 31-1011
        "income_mean_k": 32,
        "income_sigma_k": 7,
        "wealth_mean_k": 6,
        "wealth_sigma_k": 10,
        "debt_mean_k": 8,
        "auto_exposure": 0.08,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You provide home care for elderly clients. Companionship, personal care, "
            "medication reminders — all require human presence. Growing demand as "
            "population ages. Very low wages."
        ),
    },
    {
        "name": "childcare_worker",
        "category": "care_low_exposure",
        "pop_weight": 0.0040,   # ~1.04M childcare workers, BLS 39-9011
        "income_mean_k": 30,
        "income_sigma_k": 7,
        "wealth_mean_k": 5,
        "wealth_sigma_k": 10,
        "debt_mean_k": 8,
        "auto_exposure": 0.05,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You work in childcare. Parents want humans with their children. "
            "Demand is stable. Pay is terrible. You may qualify for the programs "
            "your clients' children are in."
        ),
    },
    {
        "name": "primary_school_teacher",
        "category": "care_low_exposure",
        "pop_weight": 0.0055,   # ~1.4M elementary teachers, BLS 25-2021
        "income_mean_k": 62,
        "income_sigma_k": 12,
        "wealth_mean_k": 85,
        "wealth_sigma_k": 70,
        "debt_mean_k": 40,
        "auto_exposure": 0.15,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are a primary school teacher. AI tutoring supplements but young "
            "children need human teachers for socialisation, emotional development, "
            "and classroom management. Moderate income, pension, some student debt."
        ),
    },
    {
        "name": "secondary_school_teacher",
        "category": "care_low_exposure",
        "pop_weight": 0.0040,   # ~1.04M secondary teachers, BLS 25-2031
        "income_mean_k": 65,
        "income_sigma_k": 13,
        "wealth_mean_k": 90,
        "wealth_sigma_k": 75,
        "debt_mean_k": 38,
        "auto_exposure": 0.25,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are a high school teacher. AI handles content delivery and grading "
            "for some subjects. Lab work, coaching, mentorship, and classroom authority "
            "remain. More exposed than elementary but still protected."
        ),
    },
    {
        "name": "special_needs_teacher",
        "category": "care_low_exposure",
        "pop_weight": 0.0018,   # ~470k special ed teachers, BLS 25-2050
        "income_mean_k": 64,
        "income_sigma_k": 12,
        "wealth_mean_k": 80,
        "wealth_sigma_k": 65,
        "debt_mean_k": 35,
        "auto_exposure": 0.10,
        "auto_type": "knowledge",
        "human_svc_share": 0.14,
        "sector_demand": ["retail", "grocery", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You are a special education teacher. Individualised attention, behaviour "
            "management, and emotional support for students with disabilities cannot "
            "be automated. Strong job security."
        ),
    },
    {
        "name": "social_worker",
        "category": "care_low_exposure",
        "pop_weight": 0.0028,   # ~730k, BLS 21-1020
        "income_mean_k": 55,
        "income_sigma_k": 14,
        "wealth_mean_k": 50,
        "wealth_sigma_k": 50,
        "debt_mean_k": 35,
        "auto_exposure": 0.12,
        "auto_type": "knowledge",
        "human_svc_share": 0.14,
        "sector_demand": ["retail", "grocery", "housing", "healthcare"],
        "retraining_years": 3.0,
        "description": (
            "You are a social worker. Case management, crisis intervention, and "
            "client advocacy are deeply human. AI helps with documentation. Demand "
            "is rising with displacement. Moderate income, some student debt."
        ),
    },
    {
        "name": "hairdresser",
        "category": "care_low_exposure",
        "pop_weight": 0.0025,   # ~660k barbers/hairstylists, BLS 39-5012
        "income_mean_k": 35,
        "income_sigma_k": 12,
        "wealth_mean_k": 20,
        "wealth_sigma_k": 25,
        "debt_mean_k": 10,
        "auto_exposure": 0.05,
        "auto_type": "physical",
        "human_svc_share": 0.10,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You are a hairdresser. Cutting hair is irreducibly human and social. "
            "AI helps with booking. Variable income, tips matter. Modest savings."
        ),
    },
    {
        "name": "massage_therapist",
        "category": "care_low_exposure",
        "pop_weight": 0.0006,   # ~160k, BLS 31-9011
        "income_mean_k": 50,
        "income_sigma_k": 18,
        "wealth_mean_k": 35,
        "wealth_sigma_k": 40,
        "debt_mean_k": 15,
        "auto_exposure": 0.05,
        "auto_type": "physical",
        "human_svc_share": 0.12,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You are a massage therapist. Human touch is the product. Demand may "
            "increase as people seek stress relief from automation anxiety."
        ),
    },
    {
        "name": "personal_trainer",
        "category": "care_low_exposure",
        "pop_weight": 0.0012,   # ~310k fitness trainers, BLS 39-9031
        "income_mean_k": 45,
        "income_sigma_k": 18,
        "wealth_mean_k": 30,
        "wealth_sigma_k": 35,
        "debt_mean_k": 12,
        "auto_exposure": 0.15,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a personal trainer. AI generates workout plans but motivation, "
            "form correction, and accountability need a human. Variable income."
        ),
    },

    # ── Creative & craft ─────────────────────────────────────────────────────

    {
        "name": "live_musician",
        "category": "creative_craft",
        "pop_weight": 0.0008,   # ~200k musicians, BLS 27-2042, fraction live
        "income_mean_k": 40,
        "income_sigma_k": 25,
        "wealth_mean_k": 20,
        "wealth_sigma_k": 30,
        "debt_mean_k": 15,
        "auto_exposure": 0.10,
        "auto_type": "knowledge",
        "human_svc_share": 0.18,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a live musician. AI generates recorded music but live performance "
            "is irreplaceable. Income is volatile — gigs, sessions, teaching. Streaming "
            "revenue has collapsed but live demand may grow."
        ),
    },
    {
        "name": "fine_artist",
        "category": "creative_craft",
        "pop_weight": 0.0004,   # ~100k fine artists, BLS 27-1013
        "income_mean_k": 35,
        "income_sigma_k": 30,
        "wealth_mean_k": 25,
        "wealth_sigma_k": 40,
        "debt_mean_k": 12,
        "auto_exposure": 0.25,
        "auto_type": "knowledge",
        "human_svc_share": 0.16,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a fine artist. AI image generation floods the market with content "
            "but collectors still value human-made work. Income is extremely variable."
        ),
    },
    {
        "name": "ceramicist_potter",
        "category": "creative_craft",
        "pop_weight": 0.0002,   # ~50k craft artists, BLS 27-1012, fraction
        "income_mean_k": 32,
        "income_sigma_k": 15,
        "wealth_mean_k": 20,
        "wealth_sigma_k": 25,
        "debt_mean_k": 8,
        "auto_exposure": 0.05,
        "auto_type": "physical",
        "human_svc_share": 0.14,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a ceramicist. Handmade ceramics are valued for their uniqueness. "
            "AI can't throw a pot. Income is modest but stable within a niche."
        ),
    },
    {
        "name": "bespoke_tailor",
        "category": "creative_craft",
        "pop_weight": 0.0002,   # ~50k tailors/dressmakers, BLS 51-6052
        "income_mean_k": 38,
        "income_sigma_k": 15,
        "wealth_mean_k": 25,
        "wealth_sigma_k": 30,
        "debt_mean_k": 10,
        "auto_exposure": 0.10,
        "auto_type": "physical",
        "human_svc_share": 0.14,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a bespoke tailor. Mass-produced clothing is cheap but custom "
            "fitting and alterations remain human. Niche clientele, stable demand."
        ),
    },
    {
        "name": "chef_fine_dining",
        "category": "creative_craft",
        "pop_weight": 0.0006,   # ~160k chefs/head cooks, BLS 35-1011
        "income_mean_k": 58,
        "income_sigma_k": 25,
        "wealth_mean_k": 40,
        "wealth_sigma_k": 45,
        "debt_mean_k": 20,
        "auto_exposure": 0.10,
        "auto_type": "physical",
        "human_svc_share": 0.18,
        "sector_demand": ["grocery", "hospitality", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a fine dining chef. Creativity, palate, and kitchen leadership "
            "are human. Robotic cooking handles fast-food but not haute cuisine. "
            "Moderate income with high job satisfaction."
        ),
    },

    # ── Small business owner-operators ────────────────────────────────────────

    {
        "name": "local_restaurant_owner",
        "category": "small_business_owner",
        "pop_weight": 0.0030,   # ~780k restaurant owners
        "income_mean_k": 65,
        "income_sigma_k": 35,
        "wealth_mean_k": 150,
        "wealth_sigma_k": 150,
        "debt_mean_k": 120,
        "auto_exposure": 0.25,
        "auto_type": "mixed",
        "human_svc_share": 0.12,
        "sector_demand": ["grocery", "hospitality", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You own a local restaurant. AI helps with ordering, inventory, and "
            "marketing but the dining experience is human. Margins are thin. "
            "You have business debt and reinvest most profit."
        ),
    },
    {
        "name": "independent_retailer",
        "category": "small_business_owner",
        "pop_weight": 0.0020,   # ~520k non-franchise retail owners
        "income_mean_k": 55,
        "income_sigma_k": 30,
        "wealth_mean_k": 120,
        "wealth_sigma_k": 120,
        "debt_mean_k": 80,
        "auto_exposure": 0.45,
        "auto_type": "mixed",
        "human_svc_share": 0.10,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You own a small retail shop. E-commerce and AI-driven recommendation "
            "engines are killing foot traffic. You compete on curation and personal "
            "service. Business debt is significant."
        ),
    },
    {
        "name": "solo_consultant",
        "category": "small_business_owner",
        "pop_weight": 0.0025,   # ~650k independent consultants
        "income_mean_k": 95,
        "income_sigma_k": 45,
        "wealth_mean_k": 200,
        "wealth_sigma_k": 180,
        "debt_mean_k": 30,
        "auto_exposure": 0.50,
        "auto_type": "knowledge",
        "human_svc_share": 0.16,
        "sector_demand": ["hospitality", "retail", "healthcare", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are an independent consultant. AI handles analysis and deliverables "
            "but clients buy your judgment and relationships. Competition from AI-augmented "
            "juniors is growing. Good savings, no business debt."
        ),
    },
    {
        "name": "yeoman_design_studio_owner",
        "category": "small_business_owner",
        "pop_weight": 0.0008,   # emerging category
        "income_mean_k": 85,
        "income_sigma_k": 35,
        "wealth_mean_k": 100,
        "wealth_sigma_k": 100,
        "debt_mean_k": 50,
        "auto_exposure": 0.30,
        "auto_type": "knowledge",
        "human_svc_share": 0.14,
        "sector_demand": ["hospitality", "retail", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You run a small AI-augmented design studio — the yeoman model. You use AI "
            "as a tool to compete with larger firms. Margins are decent when clients value "
            "personal attention. Vulnerable to platform undercutting on price."
        ),
    },
    {
        "name": "smallholding_farmer",
        "category": "small_business_owner",
        "pop_weight": 0.0060,   # ~1.56M farm operators (most small)
        "income_mean_k": 40,
        "income_sigma_k": 25,
        "wealth_mean_k": 350,  # land value
        "wealth_sigma_k": 300,
        "debt_mean_k": 120,
        "auto_exposure": 0.35,
        "auto_type": "physical",
        "human_svc_share": 0.08,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 3.0,
        "description": (
            "You run a small farm. Precision agriculture and autonomous equipment help "
            "but you still do hands-on work. Land is your main asset. Income is volatile "
            "with commodity prices. Business debt for equipment and operating costs."
        ),
    },
    {
        "name": "etsy_maker",
        "category": "small_business_owner",
        "pop_weight": 0.0010,   # ~260k active Etsy-style sellers
        "income_mean_k": 25,
        "income_sigma_k": 20,
        "wealth_mean_k": 30,
        "wealth_sigma_k": 35,
        "debt_mean_k": 8,
        "auto_exposure": 0.20,
        "auto_type": "mixed",
        "human_svc_share": 0.12,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You sell handmade goods online. AI-generated products flood the market "
            "but authentic handmade has a premium. This is often a side income. "
            "Low overhead, low debt."
        ),
    },

    # ── Non-labour income ─────────────────────────────────────────────────────

    {
        "name": "retiree_state_pension_only",
        "category": "non_labour",
        "pop_weight": 0.0350,   # large — ~9.1M retirees on SS only
        "income_mean_k": 22,
        "income_sigma_k": 5,
        "wealth_mean_k": 30,
        "wealth_sigma_k": 40,
        "debt_mean_k": 8,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.18,
        "sector_demand": ["grocery", "healthcare", "housing"],
        "retraining_years": 0.0,
        "description": (
            "You are retired and live on Social Security only. Fixed income, "
            "sensitive to inflation and healthcare costs. Minimal savings. "
            "Deflation in goods prices actually helps you."
        ),
    },
    {
        "name": "retiree_pension_plus_savings",
        "category": "non_labour",
        "pop_weight": 0.0500,   # ~13M retirees with pension + some savings
        "income_mean_k": 45,
        "income_sigma_k": 15,
        "wealth_mean_k": 250,
        "wealth_sigma_k": 200,
        "debt_mean_k": 20,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.22,
        "sector_demand": ["grocery", "healthcare", "hospitality", "housing"],
        "retraining_years": 0.0,
        "description": (
            "You are retired with a pension and moderate savings (401k, home equity). "
            "Comfortable but watching healthcare costs. Spend on grandchildren, travel."
        ),
    },
    {
        "name": "retiree_wealthy",
        "category": "non_labour",
        "pop_weight": 0.0150,   # ~3.9M wealthy retirees
        "income_mean_k": 120,
        "income_sigma_k": 60,
        "wealth_mean_k": 1500,
        "wealth_sigma_k": 1200,
        "debt_mean_k": 50,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.30,
        "sector_demand": ["luxury_retail", "healthcare", "hospitality", "financial_services"],
        "retraining_years": 0.0,
        "description": (
            "You are a wealthy retiree living on investment income. Portfolio performance "
            "matters more than wage inflation. You spend on healthcare, travel, and "
            "human services (home care, personal chef, etc.)."
        ),
    },
    {
        "name": "landlord_small",
        "category": "non_labour",
        "pop_weight": 0.0060,   # ~1.56M individual landlords (1-4 units)
        "income_mean_k": 75,
        "income_sigma_k": 40,
        "wealth_mean_k": 500,
        "wealth_sigma_k": 400,
        "debt_mean_k": 250,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.16,
        "sector_demand": ["retail", "hospitality", "housing"],
        "retraining_years": 0.0,
        "description": (
            "You own 1-4 rental properties. Rental income is your main revenue. "
            "AI helps with tenant screening and property management. Significant "
            "mortgage debt but appreciating assets."
        ),
    },
    {
        "name": "rentier_dividend_income",
        "category": "non_labour",
        "pop_weight": 0.0080,   # ~2.1M living primarily on investment income
        "income_mean_k": 150,
        "income_sigma_k": 100,
        "wealth_mean_k": 2000,
        "wealth_sigma_k": 2500,
        "debt_mean_k": 100,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.25,
        "sector_demand": ["luxury_retail", "hospitality", "financial_services", "healthcare"],
        "retraining_years": 0.0,
        "description": (
            "You live on dividend and capital gains income. AI capital ownership "
            "benefits you directly. Low MPC — you reinvest most income. Very low "
            "sensitivity to labour market disruption."
        ),
    },
    {
        "name": "trust_fund_heir",
        "category": "non_labour",
        "pop_weight": 0.0015,   # ~390k living on inherited wealth
        "income_mean_k": 200,
        "income_sigma_k": 150,
        "wealth_mean_k": 5000,
        "wealth_sigma_k": 5000,
        "debt_mean_k": 50,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.30,
        "sector_demand": ["luxury_retail", "hospitality", "financial_services"],
        "retraining_years": 0.0,
        "description": (
            "You live on inherited wealth. You don't work. Very low MPC. "
            "AI capital appreciation benefits you enormously. No exposure to "
            "labour market disruption whatsoever."
        ),
    },
    {
        "name": "disability_benefits",
        "category": "non_labour",
        "pop_weight": 0.0320,   # ~8.3M SSDI recipients
        "income_mean_k": 18,
        "income_sigma_k": 4,
        "wealth_mean_k": 8,
        "wealth_sigma_k": 12,
        "debt_mean_k": 10,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.15,
        "sector_demand": ["grocery", "healthcare", "housing"],
        "retraining_years": 0.0,
        "description": (
            "You receive disability benefits. Fixed income, extremely sensitive to "
            "costs. AI price deflation helps with goods but healthcare costs may rise. "
            "No savings, some medical debt."
        ),
    },

    # ── Entry / transitional ──────────────────────────────────────────────────

    {
        "name": "university_student",
        "category": "transitional",
        "pop_weight": 0.0400,   # ~10.4M enrolled students (full + part time)
        "income_mean_k": 12,
        "income_sigma_k": 8,
        "wealth_mean_k": 2,
        "wealth_sigma_k": 5,
        "debt_mean_k": 20,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.10,
        "sector_demand": ["grocery", "housing", "retail"],
        "retraining_years": 0.0,
        "description": (
            "You are a university student. Living on loans, part-time work, or "
            "parental support. Accumulating debt. Uncertain about whether your "
            "degree will lead to a job. Very high MPC on necessities."
        ),
    },
    {
        "name": "bootcamp_reskiller",
        "category": "transitional",
        "pop_weight": 0.0015,   # ~390k in active retraining programs
        "income_mean_k": 15,
        "income_sigma_k": 8,
        "wealth_mean_k": 20,
        "wealth_sigma_k": 25,
        "debt_mean_k": 15,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.08,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 0.0,
        "description": (
            "You are retraining after job loss. Drawing on savings or government "
            "support. Anxious but hopeful. Living very lean."
        ),
    },
    {
        "name": "recent_graduate",
        "category": "transitional",
        "pop_weight": 0.0080,   # ~2.1M new graduates entering workforce
        "income_mean_k": 45,
        "income_sigma_k": 20,
        "wealth_mean_k": 5,
        "wealth_sigma_k": 10,
        "debt_mean_k": 35,
        "auto_exposure": 0.40,  # varies by field
        "auto_type": "knowledge",
        "human_svc_share": 0.10,
        "sector_demand": ["grocery", "retail", "hospitality", "housing"],
        "retraining_years": 1.0,
        "description": (
            "You are a recent graduate entering a job market transformed by AI. "
            "Entry-level knowledge work is disappearing. You have student debt "
            "and minimal savings. Competition for remaining roles is fierce."
        ),
    },
    {
        "name": "unemployed_jobseeker",
        "category": "transitional",
        "pop_weight": 0.0250,   # ~6.5M unemployed (varies with cycle)
        "income_mean_k": 18,
        "income_sigma_k": 8,
        "wealth_mean_k": 15,
        "wealth_sigma_k": 25,
        "debt_mean_k": 18,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.06,
        "sector_demand": ["grocery", "housing"],
        "retraining_years": 1.5,
        "description": (
            "You are actively seeking work. Unemployment benefits or savings fund "
            "your search. Every month costs you. You spend only on essentials."
        ),
    },
    {
        "name": "stay_at_home_parent",
        "category": "transitional",
        "pop_weight": 0.0200,   # ~5.2M SAH parents
        "income_mean_k": 10,
        "income_sigma_k": 8,
        "wealth_mean_k": 50,
        "wealth_sigma_k": 60,
        "debt_mean_k": 30,
        "auto_exposure": 0.0,
        "auto_type": "knowledge",
        "human_svc_share": 0.12,
        "sector_demand": ["grocery", "retail", "housing"],
        "retraining_years": 2.0,
        "description": (
            "You are a stay-at-home parent. Household depends on spouse's income. "
            "You produce home value (childcare, cooking, household management). "
            "Very sensitive to spouse's job security."
        ),
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# ENTERPRISE ARCHETYPES (~40)
# ─────────────────────────────────────────────────────────────────────────────

ENTERPRISE_ARCHETYPES = [

    # ── Big tech & AI platforms ──────────────────────────────────────────────

    {
        "name": "foundation_model_lab",
        "category": "big_tech",
        "firm_count": 8,           # OpenAI, Anthropic, Google DeepMind, Meta AI, etc.
        "revenue_mean_bn": 25.0,   # varies wildly, fast-growing
        "revenue_sigma_bn": 15.0,
        "headcount_mean": 3000,
        "capital_stock_bn": 50.0,
        "ai_adoption": 0.95,
        "compute_cost_idx": 0.3,   # 1.0 = retail; platforms get bulk discount
        "market_power": 0.85,      # 0 = perfect competition, 1 = monopoly
        "sector": "tech",
        "output_category": "knowledge_services",
        "labour_categories": ["ml_researcher", "senior_staff_engineer", "junior_software_engineer"],
        "description": (
            "You are a foundation model lab (like OpenAI or Anthropic). You have massive "
            "compute budgets, top-tier talent, and near-monopoly on frontier AI capability. "
            "Revenue is growing exponentially. You can undercut any yeoman on price."
        ),
    },
    {
        "name": "cloud_hyperscaler",
        "category": "big_tech",
        "firm_count": 4,           # AWS, Azure, GCP, Oracle
        "revenue_mean_bn": 80.0,
        "revenue_sigma_bn": 30.0,
        "headcount_mean": 60000,
        "capital_stock_bn": 200.0,
        "ai_adoption": 0.85,
        "compute_cost_idx": 0.2,
        "market_power": 0.80,
        "sector": "tech",
        "output_category": "knowledge_services",
        "labour_categories": ["senior_staff_engineer", "junior_software_engineer", "management_consultant"],
        "description": (
            "You are a cloud hyperscaler. You sell AI compute and services. Enormous "
            "scale economies in data centres. Pricing power through lock-in."
        ),
    },
    {
        "name": "vertical_ai_platform",
        "category": "big_tech",
        "firm_count": 30,          # legal-AI, med-AI, fin-AI specialists
        "revenue_mean_bn": 2.0,
        "revenue_sigma_bn": 1.5,
        "headcount_mean": 800,
        "capital_stock_bn": 3.0,
        "ai_adoption": 0.90,
        "compute_cost_idx": 0.5,
        "market_power": 0.60,
        "sector": "tech",
        "output_category": "knowledge_services",
        "labour_categories": ["junior_software_engineer", "senior_staff_engineer", "management_consultant"],
        "description": (
            "You are a vertical AI platform — specialised in legal, medical, or financial "
            "AI. You compete with both generic platforms and yeoman operators. Your advantage "
            "is domain expertise baked into fine-tuned models."
        ),
    },
    {
        "name": "ad_social_platform",
        "category": "big_tech",
        "firm_count": 6,           # Meta, Google (ads), TikTok, Snap, X, Pinterest
        "revenue_mean_bn": 50.0,
        "revenue_sigma_bn": 40.0,
        "headcount_mean": 30000,
        "capital_stock_bn": 80.0,
        "ai_adoption": 0.90,
        "compute_cost_idx": 0.3,
        "market_power": 0.75,
        "sector": "tech",
        "output_category": "knowledge_services",
        "labour_categories": ["junior_software_engineer", "senior_staff_engineer", "graphic_designer", "copywriter"],
        "description": (
            "You are a major ad-supported social platform. AI generates content, targets ads, "
            "and moderates. Network effects create strong moats. Labour needs are falling."
        ),
    },
    {
        "name": "robotics_oem",
        "category": "big_tech",
        "firm_count": 20,          # Boston Dynamics, Tesla Bot, FANUC, ABB, etc.
        "revenue_mean_bn": 5.0,
        "revenue_sigma_bn": 4.0,
        "headcount_mean": 5000,
        "capital_stock_bn": 15.0,
        "ai_adoption": 0.80,
        "compute_cost_idx": 0.5,
        "market_power": 0.55,
        "sector": "manufacturing",
        "output_category": "physical_goods",
        "labour_categories": ["senior_staff_engineer", "factory_assembler", "machinist"],
        "description": (
            "You manufacture robots and autonomous systems. Your products automate "
            "others' workforce. Massive capex, high R&D. Growing fast."
        ),
    },

    # ── Professional services ────────────────────────────────────────────────

    {
        "name": "white_shoe_law_firm",
        "category": "professional_services",
        "firm_count": 100,         # AmLaw 100
        "revenue_mean_bn": 3.5,
        "revenue_sigma_bn": 2.0,
        "headcount_mean": 3000,
        "capital_stock_bn": 0.5,
        "ai_adoption": 0.60,
        "compute_cost_idx": 0.8,
        "market_power": 0.65,
        "sector": "professional_services",
        "output_category": "knowledge_services",
        "labour_categories": ["senior_litigator", "corporate_lawyer", "junior_paralegal"],
        "description": (
            "You are a top-100 law firm. AI handles document review and research. "
            "Client relationships and complex litigation remain human. Reducing "
            "associate headcount while partner profits rise."
        ),
    },
    {
        "name": "midmarket_law_firm",
        "category": "professional_services",
        "firm_count": 5000,        # mid-size law firms
        "revenue_mean_bn": 0.05,
        "revenue_sigma_bn": 0.03,
        "headcount_mean": 50,
        "capital_stock_bn": 0.01,
        "ai_adoption": 0.45,
        "compute_cost_idx": 0.9,
        "market_power": 0.20,
        "sector": "professional_services",
        "output_category": "knowledge_services",
        "labour_categories": ["senior_litigator", "corporate_lawyer", "junior_paralegal"],
        "description": (
            "You are a mid-market law firm. Squeezed between AI-powered platforms above "
            "and solo AI-augmented lawyers below. Margins thinning. Some partners leaving "
            "to go yeoman."
        ),
    },
    {
        "name": "big4_accounting",
        "category": "professional_services",
        "firm_count": 4,           # Deloitte, PwC, EY, KPMG
        "revenue_mean_bn": 50.0,
        "revenue_sigma_bn": 10.0,
        "headcount_mean": 100000,
        "capital_stock_bn": 5.0,
        "ai_adoption": 0.65,
        "compute_cost_idx": 0.6,
        "market_power": 0.70,
        "sector": "professional_services",
        "output_category": "knowledge_services",
        "labour_categories": ["tax_accountant", "management_consultant", "financial_analyst"],
        "description": (
            "You are a Big-4 firm. AI automates audit, tax compliance, and advisory "
            "deliverables. Massive headcount reductions planned. Consulting arm pivoting "
            "to AI transformation services."
        ),
    },
    {
        "name": "boutique_accounting",
        "category": "professional_services",
        "firm_count": 40000,       # small CPA firms
        "revenue_mean_bn": 0.002,
        "revenue_sigma_bn": 0.001,
        "headcount_mean": 8,
        "capital_stock_bn": 0.0005,
        "ai_adoption": 0.35,
        "compute_cost_idx": 1.0,
        "market_power": 0.10,
        "sector": "professional_services",
        "output_category": "knowledge_services",
        "labour_categories": ["tax_accountant", "bookkeeper"],
        "description": (
            "You are a small CPA firm. AI handles most compliance work. You survive "
            "on client relationships and advisory. Many are closing or merging."
        ),
    },
    {
        "name": "strategy_consultancy",
        "category": "professional_services",
        "firm_count": 15,          # MBB + tier-2
        "revenue_mean_bn": 12.0,
        "revenue_sigma_bn": 8.0,
        "headcount_mean": 20000,
        "capital_stock_bn": 1.0,
        "ai_adoption": 0.55,
        "compute_cost_idx": 0.7,
        "market_power": 0.60,
        "sector": "professional_services",
        "output_category": "knowledge_services",
        "labour_categories": ["management_consultant", "financial_analyst"],
        "description": (
            "You are a top strategy consultancy (MBB-tier). AI generates analyses that "
            "used to require large teams. Selling judgment and relationships now, not "
            "slide decks. Reducing junior headcount."
        ),
    },
    {
        "name": "independent_consulting_firm",
        "category": "professional_services",
        "firm_count": 80000,       # small consultancies
        "revenue_mean_bn": 0.001,
        "revenue_sigma_bn": 0.001,
        "headcount_mean": 3,
        "capital_stock_bn": 0.0001,
        "ai_adoption": 0.50,
        "compute_cost_idx": 1.0,
        "market_power": 0.05,
        "sector": "professional_services",
        "output_category": "knowledge_services",
        "labour_categories": ["solo_consultant", "management_consultant"],
        "description": (
            "You are a small independent consultancy — essentially a yeoman. AI-augmented, "
            "competing on relationships and niche expertise. Low overhead, no scale economies."
        ),
    },

    # ── Finance ──────────────────────────────────────────────────────────────

    {
        "name": "investment_bank",
        "category": "finance",
        "firm_count": 15,          # bulge bracket + large banks
        "revenue_mean_bn": 35.0,
        "revenue_sigma_bn": 20.0,
        "headcount_mean": 50000,
        "capital_stock_bn": 100.0,
        "ai_adoption": 0.70,
        "compute_cost_idx": 0.5,
        "market_power": 0.75,
        "sector": "financial_services",
        "output_category": "knowledge_services",
        "labour_categories": ["financial_analyst", "senior_executive", "junior_software_engineer"],
        "description": (
            "You are a major investment bank. AI handles trading, risk models, and "
            "research. Relationship banking and deal origination remain human. "
            "Massive profits, shrinking headcount."
        ),
    },
    {
        "name": "regional_bank",
        "category": "finance",
        "firm_count": 4000,        # community + regional banks
        "revenue_mean_bn": 0.3,
        "revenue_sigma_bn": 0.2,
        "headcount_mean": 500,
        "capital_stock_bn": 2.0,
        "ai_adoption": 0.40,
        "compute_cost_idx": 0.9,
        "market_power": 0.20,
        "sector": "financial_services",
        "output_category": "knowledge_services",
        "labour_categories": ["financial_analyst", "bookkeeper"],
        "description": (
            "You are a regional/community bank. AI handles underwriting and fraud "
            "detection but local relationships matter. Squeezed by fintechs."
        ),
    },
    {
        "name": "hedge_fund",
        "category": "finance",
        "firm_count": 3500,
        "revenue_mean_bn": 0.15,
        "revenue_sigma_bn": 0.3,
        "headcount_mean": 30,
        "capital_stock_bn": 1.0,
        "ai_adoption": 0.85,
        "compute_cost_idx": 0.6,
        "market_power": 0.40,
        "sector": "financial_services",
        "output_category": "knowledge_services",
        "labour_categories": ["financial_analyst", "ml_researcher", "senior_staff_engineer"],
        "description": (
            "You are a hedge fund. AI drives most alpha generation now. "
            "Few employees, massive AUM. Extremely high income per head."
        ),
    },
    {
        "name": "insurance_carrier",
        "category": "finance",
        "firm_count": 6000,
        "revenue_mean_bn": 1.5,
        "revenue_sigma_bn": 3.0,
        "headcount_mean": 3000,
        "capital_stock_bn": 10.0,
        "ai_adoption": 0.55,
        "compute_cost_idx": 0.7,
        "market_power": 0.35,
        "sector": "financial_services",
        "output_category": "knowledge_services",
        "labour_categories": ["insurance_claims_adjuster", "financial_analyst", "bookkeeper"],
        "description": (
            "You are an insurance company. AI handles claims processing, underwriting, "
            "and fraud detection. Adjusters and agents are being reduced."
        ),
    },

    # ── Manufacturing ────────────────────────────────────────────────────────

    {
        "name": "automated_auto_plant",
        "category": "manufacturing",
        "firm_count": 50,          # major assembly plants
        "revenue_mean_bn": 8.0,
        "revenue_sigma_bn": 5.0,
        "headcount_mean": 3000,
        "capital_stock_bn": 5.0,
        "ai_adoption": 0.75,
        "compute_cost_idx": 0.5,
        "market_power": 0.50,
        "sector": "manufacturing",
        "output_category": "physical_goods",
        "labour_categories": ["factory_assembler", "welder", "machinist", "heavy_equipment_operator"],
        "description": (
            "You are a major auto manufacturer. Robots handle most assembly. "
            "Quality control, maintenance, and supervision still need humans. "
            "Transitioning to EV production."
        ),
    },
    {
        "name": "contract_electronics_mfg",
        "category": "manufacturing",
        "firm_count": 200,
        "revenue_mean_bn": 0.5,
        "revenue_sigma_bn": 0.8,
        "headcount_mean": 2000,
        "capital_stock_bn": 1.0,
        "ai_adoption": 0.70,
        "compute_cost_idx": 0.6,
        "market_power": 0.30,
        "sector": "manufacturing",
        "output_category": "physical_goods",
        "labour_categories": ["factory_assembler", "machinist"],
        "description": (
            "You are a contract electronics manufacturer. Highly automated production "
            "lines. Competing on cost and flexibility."
        ),
    },
    {
        "name": "small_specialty_fabricator",
        "category": "manufacturing",
        "firm_count": 50000,       # small machine shops, fabricators
        "revenue_mean_bn": 0.005,
        "revenue_sigma_bn": 0.004,
        "headcount_mean": 15,
        "capital_stock_bn": 0.002,
        "ai_adoption": 0.30,
        "compute_cost_idx": 1.0,
        "market_power": 0.08,
        "sector": "manufacturing",
        "output_category": "physical_goods",
        "labour_categories": ["machinist", "welder", "carpenter"],
        "description": (
            "You are a small fabrication shop. Custom work, prototypes, repair jobs. "
            "AI helps with quoting and CNC programming. Yeoman-scale."
        ),
    },
    {
        "name": "food_processor",
        "category": "manufacturing",
        "firm_count": 25000,
        "revenue_mean_bn": 0.08,
        "revenue_sigma_bn": 0.15,
        "headcount_mean": 100,
        "capital_stock_bn": 0.05,
        "ai_adoption": 0.45,
        "compute_cost_idx": 0.8,
        "market_power": 0.25,
        "sector": "manufacturing",
        "output_category": "physical_goods",
        "labour_categories": ["factory_assembler", "warehouse_picker"],
        "description": (
            "You are a food processing company. Automation handles sorting, packaging, "
            "and quality control. Some human labour remains for complex tasks."
        ),
    },
    {
        "name": "pharma_manufacturer",
        "category": "manufacturing",
        "firm_count": 800,
        "revenue_mean_bn": 3.0,
        "revenue_sigma_bn": 8.0,
        "headcount_mean": 5000,
        "capital_stock_bn": 10.0,
        "ai_adoption": 0.60,
        "compute_cost_idx": 0.5,
        "market_power": 0.65,
        "sector": "manufacturing",
        "output_category": "physical_goods",
        "labour_categories": ["research_scientist", "factory_assembler", "pharmacist"],
        "description": (
            "You are a pharmaceutical manufacturer. AI accelerates drug discovery "
            "enormously. Manufacturing is highly automated. Regulatory moats protect margins."
        ),
    },

    # ── Logistics & transport ────────────────────────────────────────────────

    {
        "name": "national_freight_network",
        "category": "logistics",
        "firm_count": 50,
        "revenue_mean_bn": 5.0,
        "revenue_sigma_bn": 4.0,
        "headcount_mean": 15000,
        "capital_stock_bn": 8.0,
        "ai_adoption": 0.55,
        "compute_cost_idx": 0.6,
        "market_power": 0.45,
        "sector": "logistics",
        "output_category": "physical_services",
        "labour_categories": ["long_haul_trucker", "warehouse_picker", "heavy_equipment_operator"],
        "description": (
            "You are a major freight company transitioning to autonomous trucks. "
            "Highway segments are automated. Urban and complex routes still need drivers."
        ),
    },
    {
        "name": "last_mile_delivery",
        "category": "logistics",
        "firm_count": 200,
        "revenue_mean_bn": 1.0,
        "revenue_sigma_bn": 2.0,
        "headcount_mean": 5000,
        "capital_stock_bn": 2.0,
        "ai_adoption": 0.50,
        "compute_cost_idx": 0.7,
        "market_power": 0.35,
        "sector": "logistics",
        "output_category": "physical_services",
        "labour_categories": ["delivery_driver", "warehouse_picker"],
        "description": (
            "You are a last-mile delivery company. Drones and autonomous vehicles "
            "handle some deliveries but urban complexity limits automation."
        ),
    },
    {
        "name": "rideshare_platform",
        "category": "logistics",
        "firm_count": 3,           # Uber, Lyft, Waymo
        "revenue_mean_bn": 15.0,
        "revenue_sigma_bn": 10.0,
        "headcount_mean": 10000,
        "capital_stock_bn": 15.0,
        "ai_adoption": 0.70,
        "compute_cost_idx": 0.4,
        "market_power": 0.80,
        "sector": "logistics",
        "output_category": "physical_services",
        "labour_categories": ["taxi_rideshare_driver", "junior_software_engineer"],
        "description": (
            "You are a rideshare/robotaxi platform. Transitioning from human drivers to "
            "autonomous vehicles. Network effects create strong moats. Drivers are contractors."
        ),
    },
    {
        "name": "owner_operator_trucker",
        "category": "logistics",
        "firm_count": 350000,      # independent truckers
        "revenue_mean_bn": 0.0003,
        "revenue_sigma_bn": 0.0001,
        "headcount_mean": 1,
        "capital_stock_bn": 0.00015,
        "ai_adoption": 0.15,
        "compute_cost_idx": 1.0,
        "market_power": 0.02,
        "sector": "logistics",
        "output_category": "physical_services",
        "labour_categories": ["long_haul_trucker"],
        "description": (
            "You are an owner-operator trucker. Your rig is your business. Autonomous "
            "trucks are your existential threat. No scale economies, no AI advantage."
        ),
    },

    # ── Retail & hospitality ─────────────────────────────────────────────────

    {
        "name": "big_box_retailer",
        "category": "retail_hospitality",
        "firm_count": 20,
        "revenue_mean_bn": 50.0,
        "revenue_sigma_bn": 40.0,
        "headcount_mean": 200000,
        "capital_stock_bn": 30.0,
        "ai_adoption": 0.60,
        "compute_cost_idx": 0.5,
        "market_power": 0.55,
        "sector": "retail",
        "output_category": "physical_goods",
        "labour_categories": ["retail_cashier", "warehouse_picker", "delivery_driver"],
        "description": (
            "You are a major retailer (Walmart, Target, Costco). Self-checkout, automated "
            "warehouses, and AI inventory management reduce headcount. Scale is your moat."
        ),
    },
    {
        "name": "ecommerce_pureplay",
        "category": "retail_hospitality",
        "firm_count": 10,
        "revenue_mean_bn": 30.0,
        "revenue_sigma_bn": 50.0,
        "headcount_mean": 50000,
        "capital_stock_bn": 40.0,
        "ai_adoption": 0.80,
        "compute_cost_idx": 0.4,
        "market_power": 0.70,
        "sector": "retail",
        "output_category": "physical_goods",
        "labour_categories": ["warehouse_picker", "delivery_driver", "junior_software_engineer"],
        "description": (
            "You are a major e-commerce platform. AI handles recommendations, logistics "
            "optimisation, and customer service. Warehouses are increasingly robotic."
        ),
    },
    {
        "name": "local_independent_store",
        "category": "retail_hospitality",
        "firm_count": 500000,
        "revenue_mean_bn": 0.001,
        "revenue_sigma_bn": 0.001,
        "headcount_mean": 5,
        "capital_stock_bn": 0.0003,
        "ai_adoption": 0.15,
        "compute_cost_idx": 1.0,
        "market_power": 0.03,
        "sector": "retail",
        "output_category": "physical_goods",
        "labour_categories": ["retail_cashier", "independent_retailer"],
        "description": (
            "You are a local independent shop. Competing on curation, personal service, "
            "and community connection. Amazon and AI-driven commerce are existential threats."
        ),
    },
    {
        "name": "chain_restaurant",
        "category": "retail_hospitality",
        "firm_count": 300,         # major chains (each with many locations)
        "revenue_mean_bn": 5.0,
        "revenue_sigma_bn": 4.0,
        "headcount_mean": 50000,
        "capital_stock_bn": 3.0,
        "ai_adoption": 0.45,
        "compute_cost_idx": 0.7,
        "market_power": 0.40,
        "sector": "hospitality",
        "output_category": "human_services",
        "labour_categories": ["fast_food_worker", "retail_cashier"],
        "description": (
            "You are a restaurant chain. Robotic cooking, automated ordering, "
            "and AI inventory management are reducing labour. Brand and convenience "
            "are your moats."
        ),
    },
    {
        "name": "local_restaurant",
        "category": "retail_hospitality",
        "firm_count": 600000,
        "revenue_mean_bn": 0.001,
        "revenue_sigma_bn": 0.0005,
        "headcount_mean": 12,
        "capital_stock_bn": 0.0003,
        "ai_adoption": 0.15,
        "compute_cost_idx": 1.0,
        "market_power": 0.03,
        "sector": "hospitality",
        "output_category": "human_services",
        "labour_categories": ["fast_food_worker", "chef_fine_dining", "local_restaurant_owner"],
        "description": (
            "You are a local restaurant. The dining experience is human. AI helps with "
            "reservations and ordering but kitchen and service remain labour-intensive."
        ),
    },

    # ── Healthcare ───────────────────────────────────────────────────────────

    {
        "name": "hospital_system",
        "category": "healthcare",
        "firm_count": 6000,
        "revenue_mean_bn": 0.8,
        "revenue_sigma_bn": 1.5,
        "headcount_mean": 3000,
        "capital_stock_bn": 1.0,
        "ai_adoption": 0.35,
        "compute_cost_idx": 0.7,
        "market_power": 0.50,
        "sector": "healthcare",
        "output_category": "human_services",
        "labour_categories": ["registered_nurse", "physician", "nursing_aide", "surgical_technician"],
        "description": (
            "You are a hospital system. AI assists with diagnostics, imaging, and "
            "administrative tasks. Clinical care remains labour-intensive. Chronic "
            "staffing shortages."
        ),
    },
    {
        "name": "independent_clinic",
        "category": "healthcare",
        "firm_count": 200000,
        "revenue_mean_bn": 0.002,
        "revenue_sigma_bn": 0.002,
        "headcount_mean": 8,
        "capital_stock_bn": 0.001,
        "ai_adoption": 0.30,
        "compute_cost_idx": 0.9,
        "market_power": 0.15,
        "sector": "healthcare",
        "output_category": "human_services",
        "labour_categories": ["physician", "registered_nurse", "dental_hygienist"],
        "description": (
            "You are a private medical/dental practice. AI helps with diagnostics and "
            "admin but patient relationships are your value. Squeezed by hospital systems."
        ),
    },
    {
        "name": "nursing_home_chain",
        "category": "healthcare",
        "firm_count": 15000,
        "revenue_mean_bn": 0.02,
        "revenue_sigma_bn": 0.03,
        "headcount_mean": 100,
        "capital_stock_bn": 0.01,
        "ai_adoption": 0.20,
        "compute_cost_idx": 0.9,
        "market_power": 0.15,
        "sector": "healthcare",
        "output_category": "human_services",
        "labour_categories": ["nursing_aide", "elder_care_worker", "registered_nurse"],
        "description": (
            "You are a nursing home/assisted living facility. Care is irreducibly human. "
            "Chronic labour shortage. AI helps with monitoring and scheduling."
        ),
    },
    {
        "name": "solo_medical_practitioner",
        "category": "healthcare",
        "firm_count": 150000,
        "revenue_mean_bn": 0.0005,
        "revenue_sigma_bn": 0.0003,
        "headcount_mean": 2,
        "capital_stock_bn": 0.0003,
        "ai_adoption": 0.25,
        "compute_cost_idx": 1.0,
        "market_power": 0.10,
        "sector": "healthcare",
        "output_category": "human_services",
        "labour_categories": ["physician", "psychotherapist"],
        "description": (
            "You are a solo practitioner (GP, psychiatrist, therapist). AI handles "
            "notes and insurance coding. Your human judgment and rapport are the product."
        ),
    },

    # ── Agriculture & energy ─────────────────────────────────────────────────

    {
        "name": "precision_ag_megafarm",
        "category": "agriculture_energy",
        "firm_count": 5000,
        "revenue_mean_bn": 0.05,
        "revenue_sigma_bn": 0.08,
        "headcount_mean": 50,
        "capital_stock_bn": 0.1,
        "ai_adoption": 0.55,
        "compute_cost_idx": 0.7,
        "market_power": 0.30,
        "sector": "agriculture",
        "output_category": "physical_goods",
        "labour_categories": ["heavy_equipment_operator", "smallholding_farmer"],
        "description": (
            "You are a large-scale farming operation. GPS-guided autonomous equipment, "
            "drone monitoring, AI-optimised inputs. Labour needs are low and falling."
        ),
    },
    {
        "name": "smallholding_cooperative",
        "category": "agriculture_energy",
        "firm_count": 20000,
        "revenue_mean_bn": 0.003,
        "revenue_sigma_bn": 0.003,
        "headcount_mean": 8,
        "capital_stock_bn": 0.005,
        "ai_adoption": 0.20,
        "compute_cost_idx": 1.0,
        "market_power": 0.05,
        "sector": "agriculture",
        "output_category": "physical_goods",
        "labour_categories": ["smallholding_farmer"],
        "description": (
            "You are a small farming cooperative. Shared equipment and marketing. "
            "Organic/local premium helps but scale economies work against you."
        ),
    },
    {
        "name": "utility_scale_energy",
        "category": "agriculture_energy",
        "firm_count": 200,
        "revenue_mean_bn": 5.0,
        "revenue_sigma_bn": 8.0,
        "headcount_mean": 5000,
        "capital_stock_bn": 30.0,
        "ai_adoption": 0.50,
        "compute_cost_idx": 0.6,
        "market_power": 0.55,
        "sector": "energy",
        "output_category": "physical_goods",
        "labour_categories": ["electrician", "heavy_equipment_operator"],
        "description": (
            "You are a major energy utility. AI optimises grid management and "
            "predictive maintenance. Renewable transition requires capital but "
            "reduces operating labour."
        ),
    },

    # ── Media & creative ─────────────────────────────────────────────────────

    {
        "name": "legacy_publisher",
        "category": "media_creative",
        "firm_count": 500,
        "revenue_mean_bn": 0.3,
        "revenue_sigma_bn": 0.5,
        "headcount_mean": 500,
        "capital_stock_bn": 0.2,
        "ai_adoption": 0.50,
        "compute_cost_idx": 0.8,
        "market_power": 0.25,
        "sector": "media",
        "output_category": "knowledge_services",
        "labour_categories": ["copywriter", "graphic_designer", "investigative_journalist"],
        "description": (
            "You are a legacy publisher (newspaper, magazine, book). AI generates "
            "commodity content. Investigative journalism and brand trust remain. "
            "Revenue models are strained."
        ),
    },
    {
        "name": "creator_economy_agency",
        "category": "media_creative",
        "firm_count": 5000,
        "revenue_mean_bn": 0.01,
        "revenue_sigma_bn": 0.02,
        "headcount_mean": 15,
        "capital_stock_bn": 0.002,
        "ai_adoption": 0.65,
        "compute_cost_idx": 0.8,
        "market_power": 0.15,
        "sector": "media",
        "output_category": "knowledge_services",
        "labour_categories": ["graphic_designer", "copywriter", "live_musician"],
        "description": (
            "You manage content creators. AI tools boost individual creator "
            "productivity but also flood the market. Talent curation is your value."
        ),
    },
    {
        "name": "indie_game_studio",
        "category": "media_creative",
        "firm_count": 10000,
        "revenue_mean_bn": 0.002,
        "revenue_sigma_bn": 0.005,
        "headcount_mean": 8,
        "capital_stock_bn": 0.001,
        "ai_adoption": 0.55,
        "compute_cost_idx": 0.9,
        "market_power": 0.05,
        "sector": "media",
        "output_category": "knowledge_services",
        "labour_categories": ["junior_software_engineer", "graphic_designer"],
        "description": (
            "You are a small game studio. AI generates assets, code, and even "
            "game design. Your edge is creative vision and community. Hit-driven, "
            "volatile revenue."
        ),
    },

    # ── Yeoman / DAO-native ──────────────────────────────────────────────────

    {
        "name": "yeoman_ai_design_studio",
        "category": "yeoman_dao",
        "firm_count": 50000,       # emerging — projected
        "revenue_mean_bn": 0.0005,
        "revenue_sigma_bn": 0.0004,
        "headcount_mean": 2,
        "capital_stock_bn": 0.0002,
        "ai_adoption": 0.85,
        "compute_cost_idx": 1.0,   # pays retail for compute
        "market_power": 0.05,
        "sector": "professional_services",
        "output_category": "knowledge_services",
        "labour_categories": ["yeoman_design_studio_owner", "graphic_designer"],
        "description": (
            "You are a yeoman AI-augmented design studio. One or two people using AI "
            "to compete with agencies. Personal attention is your differentiator. "
            "Vulnerable to platform undercutting on commodity work."
        ),
    },
    {
        "name": "logistics_worker_coop",
        "category": "yeoman_dao",
        "firm_count": 2000,        # emerging
        "revenue_mean_bn": 0.005,
        "revenue_sigma_bn": 0.004,
        "headcount_mean": 25,
        "capital_stock_bn": 0.003,
        "ai_adoption": 0.40,
        "compute_cost_idx": 0.9,
        "market_power": 0.08,
        "sector": "logistics",
        "output_category": "physical_services",
        "labour_categories": ["delivery_driver", "warehouse_picker"],
        "description": (
            "You are a worker-owned logistics cooperative. Competing with platforms "
            "on local service quality. Democratic governance, shared profits. "
            "Limited access to capital."
        ),
    },
    {
        "name": "open_source_maintainer_collective",
        "category": "yeoman_dao",
        "firm_count": 500,         # funded OSS projects
        "revenue_mean_bn": 0.005,
        "revenue_sigma_bn": 0.008,
        "headcount_mean": 10,
        "capital_stock_bn": 0.001,
        "ai_adoption": 0.75,
        "compute_cost_idx": 0.8,
        "market_power": 0.10,
        "sector": "tech",
        "output_category": "knowledge_services",
        "labour_categories": ["senior_staff_engineer", "junior_software_engineer"],
        "description": (
            "You are a funded open-source project / commons DAO. Revenue comes from "
            "sponsorships, grants, and service contracts. AI helps with code generation "
            "and review. Impact-driven, not profit-maximising."
        ),
    },
    {
        "name": "commons_ai_lab",
        "category": "yeoman_dao",
        "firm_count": 20,          # EleutherAI, LAION, etc.
        "revenue_mean_bn": 0.01,
        "revenue_sigma_bn": 0.015,
        "headcount_mean": 30,
        "capital_stock_bn": 0.05,
        "ai_adoption": 0.90,
        "compute_cost_idx": 0.6,   # donated/sponsored compute
        "market_power": 0.10,
        "sector": "tech",
        "output_category": "knowledge_services",
        "labour_categories": ["ml_researcher", "senior_staff_engineer"],
        "description": (
            "You are a commons AI research lab. Open-source models, public benefit. "
            "Funded by grants and donations. Competing with foundation model labs on "
            "openness, not scale."
        ),
    },

    # ── Public / non-profit ──────────────────────────────────────────────────

    {
        "name": "school_district",
        "category": "public_nonprofit",
        "firm_count": 13000,       # US school districts
        "revenue_mean_bn": 0.1,
        "revenue_sigma_bn": 0.15,
        "headcount_mean": 500,
        "capital_stock_bn": 0.2,
        "ai_adoption": 0.25,
        "compute_cost_idx": 0.9,
        "market_power": 0.0,       # not competing in market
        "sector": "education",
        "output_category": "human_services",
        "labour_categories": ["primary_school_teacher", "secondary_school_teacher", "special_needs_teacher"],
        "description": (
            "You are a school district. AI tutoring supplements but doesn't replace "
            "teachers. Budget-constrained, publicly funded. Largest employer in many "
            "communities."
        ),
    },
    {
        "name": "municipal_government",
        "category": "public_nonprofit",
        "firm_count": 20000,
        "revenue_mean_bn": 0.05,
        "revenue_sigma_bn": 0.1,
        "headcount_mean": 200,
        "capital_stock_bn": 0.5,
        "ai_adoption": 0.20,
        "compute_cost_idx": 1.0,
        "market_power": 0.0,
        "sector": "government",
        "output_category": "human_services",
        "labour_categories": ["social_worker", "security_guard", "bookkeeper"],
        "description": (
            "You are a local government. AI handles permitting, record-keeping, and "
            "some citizen services. Police, fire, parks, and social services remain "
            "labour-intensive."
        ),
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

US_ADULTS_M = 260.0        # million adults
US_GDP_2025_BN = 28_000.0  # $bn nominal GDP
US_LABOUR_SHARE = 0.64
US_TOTAL_EMPLOYMENT_M = 160.0
US_HH_NET_WORTH_TN = 140.0  # $T total household net worth

def validate_consumer_weights():
    """Check that consumer archetype weights sum to ~1.0 and print summary."""
    total_weight = sum(a["pop_weight"] for a in CONSUMER_ARCHETYPES)
    total_pop_m = total_weight * US_ADULTS_M

    total_income_bn = sum(
        a["pop_weight"] * US_ADULTS_M * a["income_mean_k"] / 1000.0
        for a in CONSUMER_ARCHETYPES
    )
    total_wealth_bn = sum(
        a["pop_weight"] * US_ADULTS_M * a["wealth_mean_k"] / 1000.0
        for a in CONSUMER_ARCHETYPES
    )

    print(f"\n{'='*60}")
    print(f"CONSUMER ARCHETYPE VALIDATION")
    print(f"{'='*60}")
    print(f"  Archetypes:           {len(CONSUMER_ARCHETYPES)}")
    print(f"  Total pop weight:     {total_weight:.4f}  (target: ~1.00)")
    print(f"  Total population:     {total_pop_m:.1f}M  (target: {US_ADULTS_M:.0f}M)")
    print(f"  Total income:         ${total_income_bn:.0f}bn  (target: ~${US_GDP_2025_BN * US_LABOUR_SHARE:.0f}bn labour)")
    print(f"  Total wealth:         ${total_wealth_bn/1000:.1f}T  (target: ~${US_HH_NET_WORTH_TN:.0f}T)")
    print()

    # By category
    from collections import defaultdict
    cats = defaultdict(lambda: {"count": 0, "weight": 0, "income_bn": 0, "pop_m": 0})
    for a in CONSUMER_ARCHETYPES:
        c = cats[a["category"]]
        c["count"] += 1
        c["weight"] += a["pop_weight"]
        c["pop_m"] += a["pop_weight"] * US_ADULTS_M
        c["income_bn"] += a["pop_weight"] * US_ADULTS_M * a["income_mean_k"] / 1000.0

    print(f"  {'Category':<30} {'#':>3} {'Pop M':>8} {'Income $bn':>12}")
    print(f"  {'-'*55}")
    for cat, d in sorted(cats.items()):
        print(f"  {cat:<30} {d['count']:>3} {d['pop_m']:>8.1f} {d['income_bn']:>12.0f}")

    return total_weight


def validate_enterprise_weights():
    """Check enterprise archetypes against BEA GDP."""
    total_revenue_bn = sum(
        a["firm_count"] * a["revenue_mean_bn"]
        for a in ENTERPRISE_ARCHETYPES
    )
    total_firms = sum(a["firm_count"] for a in ENTERPRISE_ARCHETYPES)
    total_employment = sum(
        a["firm_count"] * a["headcount_mean"]
        for a in ENTERPRISE_ARCHETYPES
    )

    print(f"\n{'='*60}")
    print(f"ENTERPRISE ARCHETYPE VALIDATION")
    print(f"{'='*60}")
    print(f"  Archetypes:           {len(ENTERPRISE_ARCHETYPES)}")
    print(f"  Total firms:          {total_firms:,.0f}  (target: ~6M US firms)")
    print(f"  Total revenue:        ${total_revenue_bn/1000:.1f}T  (target: ~${US_GDP_2025_BN/1000:.0f}T GDP)")
    print(f"  Total employment:     {total_employment/1e6:.1f}M  (target: ~{US_TOTAL_EMPLOYMENT_M:.0f}M)")
    print()

    from collections import defaultdict
    cats = defaultdict(lambda: {"count": 0, "firms": 0, "revenue_bn": 0, "employment": 0})
    for a in ENTERPRISE_ARCHETYPES:
        c = cats[a["category"]]
        c["count"] += 1
        c["firms"] += a["firm_count"]
        c["revenue_bn"] += a["firm_count"] * a["revenue_mean_bn"]
        c["employment"] += a["firm_count"] * a["headcount_mean"]

    print(f"  {'Category':<25} {'#':>3} {'Firms':>10} {'Rev $T':>8} {'Emp M':>8}")
    print(f"  {'-'*58}")
    for cat, d in sorted(cats.items()):
        print(f"  {cat:<25} {d['count']:>3} {d['firms']:>10,} {d['revenue_bn']/1000:>8.1f} {d['employment']/1e6:>8.1f}")


if __name__ == "__main__":
    validate_consumer_weights()
    validate_enterprise_weights()
