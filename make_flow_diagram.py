"""
Flow diagram: LLM-Augmented SFC Model — One Simulation Year
Saves to simulation_flow.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ── colour palette ────────────────────────────────────────────────────────────
C_SFC    = "#2B6CB0"   # blue  – SFC model
C_SFC_LT = "#BEE3F8"
C_LLM    = "#276749"   # green – LLM agents
C_LLM_LT = "#C6F6D5"
C_MEM    = "#C05621"   # orange – memory
C_MEM_LT = "#FEEBC8"
C_CACHE  = "#4A5568"   # grey  – cache
C_CACHE_LT = "#E2E8F0"
C_ARROW  = "#2D3748"
C_STEP   = "#744210"   # step label colour

FIG_W, FIG_H = 22, 15

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")
fig.patch.set_facecolor("#F7FAFC")

# ── helpers ───────────────────────────────────────────────────────────────────

def box(ax, x, y, w, h, label, sublabel=None,
        fc="#FFFFFF", ec="#2D3748", lw=1.4,
        fontsize=8, bold=False, radius=0.25):
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0.05,rounding_size={radius}",
                           facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3)
    ax.add_patch(patch)
    weight = "bold" if bold else "normal"
    ax.text(x + w/2, y + h/2 + (0.12 if sublabel else 0),
            label, ha="center", va="center",
            fontsize=fontsize, fontweight=weight,
            color="#1A202C", zorder=4, wrap=True)
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.22,
                sublabel, ha="center", va="center",
                fontsize=6.2, color="#4A5568", zorder=4,
                style="italic")


def arrow(ax, x0, y0, x1, y1, label="", color=C_ARROW,
          lw=1.3, connectionstyle="arc3,rad=0.0",
          label_offset=(0, 0.13), fontsize=6.0):
    arw = FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle="->,head_length=0.22,head_width=0.13",
        color=color, linewidth=lw,
        connectionstyle=connectionstyle,
        zorder=5
    )
    ax.add_patch(arw)
    if label:
        mx = (x0 + x1) / 2 + label_offset[0]
        my = (y0 + y1) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="bottom",
                fontsize=fontsize, color=color, zorder=6,
                bbox=dict(fc="white", ec="none", pad=1.0, alpha=0.75))


def section_label(ax, x, y, text, color):
    ax.text(x, y, text, fontsize=9.5, fontweight="bold",
            color=color, va="bottom", ha="left", zorder=4)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – SFC MODEL CORE  (left column, x: 0.3 – 4.4)
# ══════════════════════════════════════════════════════════════════════════════
SFC_X = 0.3
SFC_W = 4.1

section_label(ax, SFC_X, 14.55, "① SFC MODEL CORE", C_SFC)

# State stocks box
box(ax, SFC_X, 12.5, SFC_W, 1.85,
    "STATE STOCKS  (t−1 → t)",
    sublabel="Wealth[6]  Debt[6]  Capital_auto  Capital_human\n"
             "Govt_debt  Governance G(t)",
    fc=C_SFC_LT, ec=C_SFC, lw=1.8, fontsize=8.2, bold=True)

# Flows computed box
box(ax, SFC_X, 10.3, SFC_W, 1.85,
    "FLOWS COMPUTED EACH STEP",
    sublabel="Income split  ·  Tax revenue  ·  UBI\n"
             "Compute dividend  ·  Human-economy wages",
    fc=C_SFC_LT, ec=C_SFC, lw=1.8, fontsize=8.2, bold=True)

# Arrow: stocks → flows
arrow(ax, SFC_X + SFC_W/2, 12.5, SFC_X + SFC_W/2, 12.15,
      label="last-year state", color=C_SFC, fontsize=6)

# Economic context assembled
box(ax, SFC_X, 8.3, SFC_W, 1.65,
    "ECONOMIC CONTEXT  (assembled)",
    sublabel="automation %  ·  UBI level  ·  displaced workers\n"
             "compute dividend  ·  fiscal position",
    fc="#EBF8FF", ec=C_SFC, lw=1.4, fontsize=7.8, bold=False)

arrow(ax, SFC_X + SFC_W/2, 10.3, SFC_X + SFC_W/2, 9.95,
      label="income / UBI / wages", color=C_SFC, fontsize=6)

# Step label ①
ax.text(SFC_X + SFC_W + 0.1, 13.35, "step 1", fontsize=6.5,
        color=C_STEP, va="center", style="italic")
ax.text(SFC_X + SFC_W + 0.1, 11.2, "step 2", fontsize=6.5,
        color=C_STEP, va="center", style="italic")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – LLM AGENTS  (centre column, x: 5.5 – 14.0)
# ══════════════════════════════════════════════════════════════════════════════
LLM_X = 5.5
LLM_W = 8.6

section_label(ax, LLM_X, 14.55, "② LLM AGENTS", C_LLM)

# ── Household agents H1-H6 ────────────────────────────────────────────────────
HH_ROWS = [
    ("H1", "Concentrated capital owner",  "consume_fraction · human_svc_share · lobbying_spend_k"),
    ("H2", "Yeomen operator",             "consume_fraction · invest_fraction"),
    ("H3", "DAO contributor",             "consume_fraction · reinvest_fraction"),
    ("H4", "Displaced worker on UBI",     "consume_fraction · borrow"),
    ("H5", "Compute dividend recipient",  "consume_fraction"),
    ("H6", "Human economy worker",        "consume_fraction"),
]

HH_H   = 0.82
HH_GAP = 0.18
HH_TOP = 13.80
HH_W   = LLM_W - 0.15

for i, (hid, role, outputs) in enumerate(HH_ROWS):
    y0 = HH_TOP - i * (HH_H + HH_GAP)
    fc = C_LLM_LT
    ec = C_LLM
    lw = 1.6 if hid == "H1" else 1.3
    label = f"{hid}: {role}"
    box(ax, LLM_X, y0, HH_W, HH_H,
        label, sublabel=f"→ {outputs}",
        fc=fc, ec=ec, lw=lw, fontsize=7.5, bold=(hid == "H1"))

# Gov + lobbying agents (below household rows)
GOV_Y = HH_TOP - 6 * (HH_H + HH_GAP) - 0.15
box(ax, LLM_X, GOV_Y, HH_W, 1.05,
    "AGENT 7: Government / Regulator",
    sublabel="inputs: fiscal position · H1 lobbying pressure · displacement rate\n"
             "output: enforcement_effort (0–1)",
    fc="#FEFCBF", ec="#D69E2E", lw=1.8, fontsize=7.5, bold=True)

# Step labels
ax.text(LLM_X - 0.45, HH_TOP + HH_H/2, "step 3", fontsize=6.5,
        color=C_STEP, va="center", style="italic")
ax.text(LLM_X - 0.45, HH_TOP - 0 * (HH_H + HH_GAP) + HH_H/2, "step 4",
        fontsize=6.5, color=C_STEP, va="center", style="italic")
ax.text(LLM_X - 0.45, GOV_Y + 0.52, "step 5", fontsize=6.5,
        color=C_STEP, va="center", style="italic")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – MEMORY  (right column, x: 15.0 – 19.0)
# ══════════════════════════════════════════════════════════════════════════════
MEM_X = 15.0
MEM_W = 3.8

section_label(ax, MEM_X, 14.55, "③ MEMORY", C_MEM)

MEM_AGENTS = [
    ("H1 memory", "consume · invest · lobby\n(last 3 yrs + outcomes)"),
    ("H2 memory", "consume · invest\n(last 3 yrs)"),
    ("H3 memory", "consume · reinvest\n(last 3 yrs)"),
    ("H4 memory", "consume · borrow\n(last 3 yrs)"),
    ("H5 memory", "consume\n(last 3 yrs)"),
    ("H6 memory", "consume\n(last 3 yrs)"),
    ("Gov memory", "enforcement · fiscal\n(last 3 yrs)"),
]

# MEM_TOP must align with HH_TOP so memory rows line up with agent rows
MEM_H   = HH_H       # match household box height
MEM_GAP = HH_GAP     # match household gap
MEM_TOP = HH_TOP     # start at same Y as H1

for i, (mlabel, msub) in enumerate(MEM_AGENTS):
    y0 = MEM_TOP - i * (MEM_H + MEM_GAP)
    box(ax, MEM_X, y0, MEM_W, MEM_H,
        mlabel, sublabel=msub,
        fc=C_MEM_LT, ec=C_MEM, lw=1.3, fontsize=7.2)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – CACHE  (far right, x: 19.2 – 21.5)
# ══════════════════════════════════════════════════════════════════════════════
CACHE_X = 19.2
CACHE_W = 2.5

section_label(ax, CACHE_X, 14.55, "④ CACHE", C_CACHE)

box(ax, CACHE_X, 12.1, CACHE_W, 1.5,
    "MD5 CACHE",
    sublabel="prompt hash\n→ cached JSON\nresponse",
    fc=C_CACHE_LT, ec=C_CACHE, lw=1.3, fontsize=7.5, bold=True)

box(ax, CACHE_X, 10.0, CACHE_W, 1.5,
    ".llm_cache/",
    sublabel="disk-backed\nkey-value store\nper scenario",
    fc=C_CACHE_LT, ec=C_CACHE, lw=1.3, fontsize=7.5)

arrow(ax, CACHE_X + CACHE_W/2, 11.6, CACHE_X + CACHE_W/2, 11.5,
      color=C_CACHE, fontsize=6)

# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM ROW – SFC FLOW MATRIX  +  OUTPUT STOCKS
# ══════════════════════════════════════════════════════════════════════════════
FLOW_Y  = 4.2
FLOW_H  = 1.55

# SFC flow matrix
box(ax, 0.3, FLOW_Y, 6.5, FLOW_H,
    "SFC FLOW MATRIX  (step 8)",
    sublabel="consumption → firm revenue → wages → tax revenue\n"
             "All household decisions aggregated",
    fc=C_SFC_LT, ec=C_SFC, lw=1.8, fontsize=8.0, bold=True)

# Enforcement / governance
box(ax, 7.2, FLOW_Y, 5.5, FLOW_H,
    "EFFECTIVE TAX ENFORCEMENT  (steps 6–7)",
    sublabel="G(t) updated by enforcement_effort\n"
             "effective_enforcement = p.enforcement × G(t)",
    fc="#FFF5F5", ec="#C53030", lw=1.8, fontsize=7.8, bold=True)

# Tax → UBI feedback
box(ax, 13.1, FLOW_Y, 5.0, FLOW_H,
    "TAX COLLECTION → UBI  (step 9)",
    sublabel="tax_revenue × effective_enforcement\n"
             "→ actual taxes → UBI disbursed to H4 / H5",
    fc="#F0FFF4", ec=C_LLM, lw=1.8, fontsize=7.8, bold=True)

# New state stocks
box(ax, 0.3, 2.3, 6.5, 1.55,
    "NEW STATE STOCKS  (step 10)",
    sublabel="Wealth[6]  Debt[6]  Capital_auto  Capital_human\n"
             "Govt_debt  Governance G(t)  — written to DataFrame row",
    fc=C_SFC_LT, ec=C_SFC, lw=1.8, fontsize=7.8, bold=True)

# Memory update
box(ax, 7.2, 2.3, 5.5, 1.55,
    "MEMORY UPDATE  (step 11)",
    sublabel="Agent decisions appended to memory stores\n"
             "oldest entry dropped when len > 3",
    fc=C_MEM_LT, ec=C_MEM, lw=1.8, fontsize=7.8, bold=True)

# Cache + record
box(ax, 13.1, 2.3, 5.0, 1.55,
    "CACHE + RECORD  (step 12)",
    sublabel="Results cached  ·  DataFrame row appended\n"
             "Advance t → t+1",
    fc=C_CACHE_LT, ec=C_CACHE, lw=1.8, fontsize=7.8, bold=True)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS – context to agents
# ══════════════════════════════════════════════════════════════════════════════

# SFC econ context → H1..H6 (bundle arrow)
arrow(ax, SFC_X + SFC_W, 8.9, LLM_X, 11.0,
      label="persona + financials\n+ econ context",
      color=C_SFC, fontsize=6.0,
      connectionstyle="arc3,rad=-0.18",
      label_offset=(0, 0.12))

# SFC econ context → Gov agent
arrow(ax, SFC_X + SFC_W, 8.6, LLM_X, GOV_Y + 0.52,
      label="fiscal position +\ndisplacement rate",
      color=C_SFC, fontsize=5.8,
      connectionstyle="arc3,rad=0.15",
      label_offset=(0.2, 0.1))

# Memory → H1-H6 (shown as one bundle)
MEM_MID_Y = MEM_TOP - 2.5 * (MEM_H + MEM_GAP)
for i in range(6):
    y_agent = HH_TOP - i * (HH_H + HH_GAP) + HH_H/2
    arrow(ax, MEM_X, MEM_TOP - i * (MEM_H + MEM_GAP) + MEM_H/2,
          LLM_X + HH_W, y_agent,
          color=C_MEM, lw=0.9, fontsize=5.5,
          connectionstyle="arc3,rad=0.0")

# Memory → Gov agent
arrow(ax, MEM_X, MEM_TOP - 6 * (MEM_H + MEM_GAP) + MEM_H/2,
      LLM_X + HH_W, GOV_Y + 0.52,
      color=C_MEM, lw=0.9,
      connectionstyle="arc3,rad=0.0")

# Memory label (once, on bundle)
ax.text(MEM_X - 0.15, HH_TOP - 2*(MEM_H+MEM_GAP) + MEM_H/2 + 0.2,
        "last 3 yrs\n+ outcomes", fontsize=5.5, color=C_MEM,
        ha="right", va="center")

# H1 lobbying → Gov agent
H1_Y = HH_TOP + HH_H/2
GOV_MID_Y = GOV_Y + 0.52
# Draw a dashed arrow inside LLM column
ax.annotate("",
            xy=(LLM_X + HH_W * 0.5, GOV_MID_Y + 1.05),
            xytext=(LLM_X + HH_W * 0.85, H1_Y),
            arrowprops=dict(arrowstyle="->,head_length=0.22,head_width=0.13",
                            color="#D69E2E", lw=1.4,
                            connectionstyle="arc3,rad=0.35"),
            zorder=6)
ax.text(LLM_X + HH_W * 0.73, (H1_Y + GOV_MID_Y)/2 + 0.3,
        "lobbying_spend_k\n(step 4)", fontsize=5.8,
        color="#D69E2E", ha="center", va="bottom",
        bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.8))

# ── Agents → SFC flow matrix (step 8) ────────────────────────────────────────
arrow(ax, LLM_X + HH_W/2, GOV_Y,
      3.55, FLOW_Y + FLOW_H,
      label="all consume_fraction\ndecisions",
      color=C_LLM, fontsize=6.0,
      connectionstyle="arc3,rad=0.1",
      label_offset=(0.3, 0.1))

# Gov → enforcement box (step 6)
arrow(ax, LLM_X + HH_W/2, GOV_Y,
      9.95, FLOW_Y + FLOW_H,
      label="enforcement_effort",
      color="#D69E2E", fontsize=6.0,
      connectionstyle="arc3,rad=0.05",
      label_offset=(0.2, 0.1))

# Enforcement → Tax→UBI
arrow(ax, 12.7, FLOW_Y + FLOW_H/2,
      13.1, FLOW_Y + FLOW_H/2,
      label="effective\nenforcement",
      color="#C53030", fontsize=5.8,
      label_offset=(0, 0.15))

# Flow matrix → new stocks
arrow(ax, 3.55, FLOW_Y,
      3.55, 2.3 + 1.55,
      label="aggregated\nflows",
      color=C_SFC, fontsize=6.0,
      label_offset=(0.35, 0.05))

# Tax→UBI → H4/H5 (feedback loop — goes back up to agent column)
arrow(ax, 15.6, FLOW_Y + FLOW_H,
      LLM_X + HH_W * 0.55,
      HH_TOP - 3 * (HH_H + HH_GAP) + HH_H/2,  # H4
      label="UBI → H4/H5\nnext context",
      color=C_LLM, fontsize=5.8,
      connectionstyle="arc3,rad=-0.35",
      label_offset=(0.5, 0.15))

# New stocks → State stocks (cycle arrow — back to top)
ax.annotate("",
            xy=(SFC_X + 0.3, 12.5),
            xytext=(SFC_X + 0.3, 2.3 + 1.55),
            arrowprops=dict(arrowstyle="->,head_length=0.22,head_width=0.13",
                            color=C_SFC, lw=1.5,
                            connectionstyle="arc3,rad=0.5"),
            zorder=6)
ax.text(SFC_X - 0.9, 7.5, "t+1\ncycle", fontsize=6.5, color=C_SFC,
        ha="center", va="center", fontweight="bold")

# Memory update → memory stores (step 11)
arrow(ax, 9.95, 2.3 + 1.55,
      MEM_X + MEM_W/2, MEM_TOP - 6*(MEM_H+MEM_GAP),
      label="append decisions\n+ outcomes",
      color=C_MEM, fontsize=5.8,
      connectionstyle="arc3,rad=-0.2",
      label_offset=(0.3, 0.1))

# Cache → .llm_cache (already done above)
# LLM agents → cache (check / write)
arrow(ax, LLM_X + HH_W, HH_TOP - 2*(HH_H + HH_GAP) + HH_H/2,
      CACHE_X, 12.1 + 0.75,
      label="prompt hash\n→ check/write",
      color=C_CACHE, fontsize=5.8,
      connectionstyle="arc3,rad=-0.05",
      label_offset=(0.2, 0.12))

# Flow matrix → memory update arrow
arrow(ax, 6.8, 2.3 + 0.77,
      7.2, 2.3 + 0.77,
      color=C_SFC, lw=1.0, fontsize=5.5)

# Tax→UBI row → cache+record arrow
arrow(ax, 18.1, 2.3 + 0.77,
      19.2 - 0.05, 2.3 + 0.77,  # not beyond fig
      color=C_CACHE, lw=1.0, fontsize=5.5)

# ══════════════════════════════════════════════════════════════════════════════
# LEGEND
# ══════════════════════════════════════════════════════════════════════════════
leg_x, leg_y = 0.3, 1.55
items = [
    (C_SFC_LT,   C_SFC,   "SFC Model components"),
    (C_LLM_LT,   C_LLM,   "LLM Agents (Gemini 2.5 Flash)"),
    (C_MEM_LT,   C_MEM,   "Agent memory stores"),
    (C_CACHE_LT, C_CACHE, "Prompt cache (.llm_cache/)"),
]
for k, (fc, ec, label) in enumerate(items):
    bx = leg_x + k * 4.8
    ax.add_patch(FancyBboxPatch((bx, leg_y), 0.45, 0.38,
                                boxstyle="round,pad=0.03",
                                facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=3))
    ax.text(bx + 0.6, leg_y + 0.19, label,
            fontsize=7.5, va="center", color="#1A202C")

# ══════════════════════════════════════════════════════════════════════════════
# TITLE + SUBTITLE
# ══════════════════════════════════════════════════════════════════════════════
ax.text(FIG_W/2, 14.82,
        "LLM-Augmented SFC Model: One Simulation Year",
        ha="center", va="center",
        fontsize=15, fontweight="bold", color="#1A202C")

ax.text(FIG_W/2, 14.45,
        "Stock-Flow Consistent macro model  ×  Gemini 2.5 Flash agent decisions  ×  Per-agent memory",
        ha="center", va="center",
        fontsize=8.5, color="#4A5568")

# thin horizontal rule under title
ax.axhline(14.3, color="#CBD5E0", linewidth=0.8)

# ── save ──────────────────────────────────────────────────────────────────────
OUT = "/Users/rorypilgrim/claude/future_of_economy/simulation_flow.png"
plt.tight_layout(pad=0.3)
plt.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved → {OUT}")
