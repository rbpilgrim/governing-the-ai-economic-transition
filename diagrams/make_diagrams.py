import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os

OUT = "/Users/rorypilgrim/claude/future_of_economy/diagrams"

# Colour palette
BLUE   = "#2D6FA3"
GREEN  = "#2E8B57"
ORANGE = "#E07B1A"
RED    = "#C0392B"
GREY   = "#F0F0F0"
DARK   = "#222222"
WHITE  = "#FFFFFF"
LIGHT_BLUE = "#D6E8F7"
LIGHT_GREEN = "#D4EDDA"
LIGHT_ORANGE = "#FAE3C0"
LIGHT_RED = "#FADBD8"

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f"Saved: {path}")


# ─────────────────────────────────────────────
# Diagram 1: The Basic Loop
# ─────────────────────────────────────────────
def diagram_01():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)

    ax.set_title("The Basic Loop", fontsize=22, fontweight='bold', color=DARK, pad=16)

    # Box helper
    def box(cx, cy, w, h, text, color, facecolor, fontsize=13):
        rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                               boxstyle="round,pad=0.12", linewidth=2,
                               edgecolor=color, facecolor=facecolor, zorder=3)
        ax.add_patch(rect)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color=DARK, zorder=4, wrap=True,
                multialignment='center')

    # Four corners
    box(2.0, 6.2, 2.6, 1.1, "HOUSEHOLDS", BLUE, LIGHT_BLUE, 14)
    box(8.0, 6.2, 2.6, 1.1, "FIRMS", BLUE, LIGHT_BLUE, 14)
    box(2.0, 1.8, 2.6, 1.1, "HOUSEHOLDS", BLUE, LIGHT_BLUE, 14)
    box(8.0, 1.8, 2.6, 1.1, "FIRMS", BLUE, LIGHT_BLUE, 14)

    # Edge labels
    ax.text(5.0, 7.0, "SPEND MONEY", ha='center', va='center', fontsize=13,
            fontweight='bold', color=ORANGE)
    ax.text(5.0, 1.0, "PAY WAGES", ha='center', va='center', fontsize=13,
            fontweight='bold', color=GREEN)
    ax.text(0.9, 4.0, "RECEIVE\nWAGES", ha='center', va='center', fontsize=11,
            color=GREEN, fontstyle='italic')
    ax.text(9.1, 4.0, "EARN\nREVENUE", ha='center', va='center', fontsize=11,
            color=ORANGE, fontstyle='italic')

    # Arrows — top (households → firms)
    ax.annotate("", xy=(6.6, 6.2), xytext=(3.3, 6.2),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2.5))
    # bottom (firms → households)
    ax.annotate("", xy=(3.3, 1.8), xytext=(6.6, 1.8),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.5))
    # left down
    ax.annotate("", xy=(2.0, 2.4), xytext=(2.0, 5.65),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.5))
    # right up
    ax.annotate("", xy=(8.0, 5.65), xytext=(8.0, 2.4),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.5))

    # Government centre box
    gov_rect = FancyBboxPatch((3.7, 3.2), 2.6, 1.6,
                               boxstyle="round,pad=0.12", linewidth=2.5,
                               edgecolor=RED, facecolor="#FDECEA", zorder=3)
    ax.add_patch(gov_rect)
    ax.text(5.0, 4.1, "GOVERNMENT", ha='center', va='center', fontsize=13,
            fontweight='bold', color=RED, zorder=4)
    ax.text(5.0, 3.6, "takes tax · gives UBI", ha='center', va='center',
            fontsize=10, color=DARK, zorder=4)

    # Gov arrows
    ax.annotate("", xy=(3.7, 4.0), xytext=(3.1, 5.8),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8,
                                connectionstyle="arc3,rad=0.2"))
    ax.annotate("", xy=(3.1, 2.2), xytext=(3.7, 3.2),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8,
                                connectionstyle="arc3,rad=-0.2"))

    # Caption
    ax.text(5.0, 0.2, "\"Every dollar spent becomes someone else's income\"",
            ha='center', va='center', fontsize=12, fontstyle='italic', color=DARK)

    save(fig, "diagram_01_basic_loop.png")


# ─────────────────────────────────────────────
# Diagram 2: Who Are the Households?
# ─────────────────────────────────────────────
def diagram_02():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)

    ax.set_title("Six Types of Households", fontsize=22, fontweight='bold',
                 color=DARK, pad=16)

    households = [
        ("[H1]", "Concentrated Capital Owner", "Owns AI/robot capital", "Spends 25¢ of every $1", BLUE, LIGHT_BLUE),
        ("[H2]", "Yeomen Operator",            "Runs AI-augmented small business", "Spends 78¢ of every $1", GREEN, LIGHT_GREEN),
        ("[H3]", "DAO Contributor",            "Works in commons/cooperative", "Spends 78¢ of every $1", GREEN, LIGHT_GREEN),
        ("[H4]", "Displaced Worker",           "Lost job to automation, on UBI", "Spends 92¢ of every $1", RED, LIGHT_RED),
        ("[H5]", "Compute Dividend Recipient", "Receives public AI dividend", "Spends 85¢ of every $1", ORANGE, LIGHT_ORANGE),
        ("[H6]", "Human Economy Worker",       "Care, trades, teaching", "Spends 82¢ of every $1", BLUE, LIGHT_BLUE),
    ]

    cols = [2.0, 8.0]
    rows = [7.8, 4.9, 2.0]

    for i, (emoji, name, desc, mpc, color, facecolor) in enumerate(households):
        col = i % 2
        row = i // 2
        cx = cols[col]
        cy = rows[row]
        w, h = 5.5, 2.4

        rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                               boxstyle="round,pad=0.15", linewidth=2.5,
                               edgecolor=color, facecolor=facecolor, zorder=3)
        ax.add_patch(rect)

        # badge label
        badge = FancyBboxPatch((cx - w/2 + 0.15, cy - 0.38), 0.72, 0.76,
                                boxstyle="round,pad=0.06", linewidth=1.5,
                                edgecolor=color, facecolor=color, zorder=4)
        ax.add_patch(badge)
        ax.text(cx - w/2 + 0.51, cy, emoji, ha='center', va='center',
                fontsize=11, fontweight='bold', color=WHITE, zorder=5)
        # name
        ax.text(cx - w/2 + 1.05, cy + 0.52, name, fontsize=12, fontweight='bold',
                color=DARK, va='center', zorder=4)
        # description
        ax.text(cx - w/2 + 1.05, cy + 0.04, desc, fontsize=11, color="#444444",
                va='center', zorder=4)
        # MPC
        ax.text(cx - w/2 + 1.05, cy - 0.52, mpc, fontsize=12, fontweight='bold',
                color=color, va='center', zorder=4)

    ax.text(6.0, 0.4,
            "The key number is how much of each $1 earned gets spent back into the economy",
            ha='center', va='center', fontsize=12, fontstyle='italic', color=DARK)

    save(fig, "diagram_02_households.png")


# ─────────────────────────────────────────────
# Diagram 3: How an LLM Agent Decides
# ─────────────────────────────────────────────
def diagram_03():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)

    ax.set_title("How Each Household Decides (Every Year)", fontsize=21,
                 fontweight='bold', color=DARK, pad=14)

    # Box 1 — blue
    r1 = FancyBboxPatch((0.3, 1.2), 3.6, 4.4,
                         boxstyle="round,pad=0.15", linewidth=2.5,
                         edgecolor=BLUE, facecolor=LIGHT_BLUE, zorder=3)
    ax.add_patch(r1)
    ax.text(2.1, 5.2, "WHAT THE\nAGENT KNOWS", ha='center', va='center',
            fontsize=14, fontweight='bold', color=BLUE, zorder=4)
    items1 = [
        "• Their finances",
        "  (income, savings, debt)",
        "• The economy",
        "  (automation %, UBI level,",
        "   displaced workers)",
        "• Last 3 years of decisions",
        "  (memory)",
    ]
    for j, line in enumerate(items1):
        ax.text(0.55, 4.55 - j*0.44, line, fontsize=10.5, color=DARK, va='center', zorder=4)

    # Arrow 1
    ax.annotate("", xy=(5.4, 3.4), xytext=(3.95, 3.4),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.5))
    ax.text(4.65, 3.85, "sent as a\nprompt to", ha='center', fontsize=10,
            color=BLUE, fontstyle='italic')
    ax.text(4.65, 3.1, "Gemini", ha='center', fontsize=11, fontweight='bold', color=BLUE)

    # Box 2 — green (larger, centre)
    r2 = FancyBboxPatch((5.4, 0.6), 4.2, 5.0,
                         boxstyle="round,pad=0.15", linewidth=3.0,
                         edgecolor=GREEN, facecolor=LIGHT_GREEN, zorder=3)
    ax.add_patch(r2)
    ax.text(7.5, 5.25, "GEMINI\nREASONS", ha='center', va='center',
            fontsize=14, fontweight='bold', color=GREEN, zorder=4)

    # Inner reasoning box
    reason_rect = FancyBboxPatch((5.65, 1.0), 3.7, 3.6,
                                  boxstyle="round,pad=0.1", linewidth=1.0,
                                  edgecolor="#AAAAAA", facecolor="#F7F7F7", zorder=4)
    ax.add_patch(reason_rect)
    reasoning = (
        "\"I am a displaced worker.\n"
        "My UBI fell again this year\n"
        "($5k). I have $8k debt.\n"
        "Last year I borrowed to\n"
        "cover essentials. This year\n"
        "I must cut spending further\n"
        "to avoid a debt spiral...\""
    )
    ax.text(7.5, 2.8, reasoning, ha='center', va='center', fontsize=9.5,
            color="#333333", zorder=5, linespacing=1.5)

    # Arrow 2
    ax.annotate("", xy=(10.05, 3.4), xytext=(9.6, 3.4),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.5))
    ax.text(9.83, 3.85, "returns a\nJSON", ha='center', fontsize=10,
            color=GREEN, fontstyle='italic')
    ax.text(9.83, 3.1, "decision", ha='center', fontsize=11, fontweight='bold', color=GREEN)

    # Box 3 — orange
    r3 = FancyBboxPatch((10.05, 1.2), 3.6, 4.4,
                          boxstyle="round,pad=0.15", linewidth=2.5,
                          edgecolor=ORANGE, facecolor=LIGHT_ORANGE, zorder=3)
    ax.add_patch(r3)
    ax.text(11.85, 5.2, "WHAT THEY\nDECIDE", ha='center', va='center',
            fontsize=14, fontweight='bold', color=ORANGE, zorder=4)
    items3 = [
        "• Spend X% of income",
        "",
        "• Borrow: yes / no",
        "",
        "• Spend Y% on",
        "  human services",
    ]
    for j, line in enumerate(items3):
        ax.text(10.25, 4.55 - j*0.44, line, fontsize=11, color=DARK, va='center', zorder=4)

    # Caption
    ax.text(7.0, 0.2,
            "Unlike fixed rules, the agent reasons about its situation — and remembers what happened before",
            ha='center', va='center', fontsize=12, fontstyle='italic', color=DARK)

    save(fig, "diagram_03_llm_decision.png")


# ─────────────────────────────────────────────
# Diagram 4: The Governance Loop
# ─────────────────────────────────────────────
def diagram_04():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)

    ax.set_title("Why Concentrated Ownership Is Self-Reinforcing", fontsize=20,
                 fontweight='bold', color=DARK, pad=14)

    # 6 nodes clockwise starting top-left-ish
    angles = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, 7)[:-1]  # 6 evenly spaced
    cx_c, cy_c = 5.5, 5.1
    r = 3.0

    node_texts = [
        "Wealth concentrates\nin few hands",
        "Capital owners spend on\nlobbying & tax avoidance",
        "Enforcement\nweakens",
        "Less tax\ncollected",
        "Less UBI —\nmore poverty",
        "Inequality\nrises further",
    ]
    node_colors = [RED, RED, ORANGE, ORANGE, ORANGE, RED]
    node_faces  = [LIGHT_RED, LIGHT_RED, LIGHT_ORANGE, LIGHT_ORANGE, LIGHT_ORANGE, LIGHT_RED]

    positions = []
    for ang in angles:
        nx = cx_c + r * np.cos(ang)
        ny = cy_c + r * np.sin(ang)
        positions.append((nx, ny))

    w_box, h_box = 2.8, 1.1

    for i, (px, py) in enumerate(positions):
        rect = FancyBboxPatch((px - w_box/2, py - h_box/2), w_box, h_box,
                               boxstyle="round,pad=0.1", linewidth=2.2,
                               edgecolor=node_colors[i], facecolor=node_faces[i], zorder=3)
        ax.add_patch(rect)
        ax.text(px, py, node_texts[i], ha='center', va='center', fontsize=10.5,
                fontweight='bold', color=DARK, zorder=4, multialignment='center')

    # Clockwise arrows between nodes
    for i in range(6):
        p1 = np.array(positions[i])
        p2 = np.array(positions[(i+1) % 6])
        mid = (p1 + p2) / 2
        # offset midpoint outward slightly to curve
        direction = mid - np.array([cx_c, cy_c])
        norm = direction / np.linalg.norm(direction)
        ctrl = mid + norm * 0.6
        ax.annotate("", xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.2,
                                    connectionstyle=f"arc3,rad=0.25"),
                    zorder=2)

    # Centre label
    ax.text(cx_c, cy_c, "DOOM\nLOOP", ha='center', va='center', fontsize=22,
            fontweight='bold', color=RED, zorder=5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=RED, linewidth=2))

    # Break-out arrow and green box
    escape_x, escape_y = 10.5, 2.0
    # Arrow from node 6 (bottom right area) outward
    last_node = positions[5]
    ax.annotate("", xy=(escape_x - 1.8, escape_y + 0.3), xytext=(last_node[0] + 0.4, last_node[1] - 0.3),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.5,
                                connectionstyle="arc3,rad=-0.3"))
    ax.text(last_node[0] + 0.7, last_node[1] - 0.55, "BREAK\nOUT", fontsize=9,
            color=GREEN, fontweight='bold', ha='center')

    green_rect = FancyBboxPatch((escape_x - 1.8, escape_y - 0.9), 3.1, 1.6,
                                 boxstyle="round,pad=0.12", linewidth=2.5,
                                 edgecolor=GREEN, facecolor=LIGHT_GREEN, zorder=3)
    ax.add_patch(green_rect)
    ax.text(escape_x - 0.25, escape_y + 0.15,
            "Distributed ownership\n(yeomen / DAO)\nkeeps inequality low\nenough to avoid the loop",
            ha='center', va='center', fontsize=9.5, color=DARK, zorder=4,
            multialignment='center')

    save(fig, "diagram_04_governance.png")


# ─────────────────────────────────────────────
# Diagram 5: What the Simulation Does Each Year
# ─────────────────────────────────────────────
def diagram_05():
    fig, ax = plt.subplots(figsize=(8, 14))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 14)
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)

    ax.set_title("One Year in the Simulation", fontsize=21, fontweight='bold',
                 color=DARK, pad=14)

    steps = [
        ("1", "INCOME", "Calculate incomes",
         "SFC model works out what each\nhousehold earns from last year's state",
         BLUE, LIGHT_BLUE),
        ("2", "LLM x6", "Ask each household agent",
         "6 LLM calls: each agent reads their\nsituation + memory, decides how to spend",
         GREEN, LIGHT_GREEN),
        ("3", "GOV", "Ask the government agent",
         "1 LLM call: government sees lobbying\npressure + fiscal stress, decides enforcement",
         GREEN, LIGHT_GREEN),
        ("4", "G(t)", "Update governance",
         "Enforcement effort becomes this year's\ninstitutional quality score G(t)",
         ORANGE, LIGHT_ORANGE),
        ("5", "FLOW", "Run the flow matrix",
         "Spending flows through the economy:\nconsumption -> firm revenue -> wages -> taxes",
         BLUE, LIGHT_BLUE),
        ("6", "MEM", "Update memory",
         "Each agent remembers what they\ndecided and what happened",
         ORANGE, LIGHT_ORANGE),
        ("7", "NEXT", "Save state, advance year",
         "New wealth, debt, governance stocks saved;\nmove to next year",
         BLUE, LIGHT_BLUE),
    ]

    top_y = 12.8
    step_h = 1.55
    box_w = 7.0
    box_h = 1.3

    for i, (num, emoji, title, desc, color, facecolor) in enumerate(steps):
        cy = top_y - i * step_h

        rect = FancyBboxPatch((0.5, cy - box_h/2), box_w, box_h,
                               boxstyle="round,pad=0.12", linewidth=2.2,
                               edgecolor=color, facecolor=facecolor, zorder=3)
        ax.add_patch(rect)

        # Step number circle
        circ = plt.Circle((1.05, cy), 0.32, color=color, zorder=4)
        ax.add_patch(circ)
        ax.text(1.05, cy, num, ha='center', va='center', fontsize=13,
                fontweight='bold', color=WHITE, zorder=5)

        # icon badge
        ibadge = FancyBboxPatch((1.42, cy - 0.28), 0.95, 0.56,
                                  boxstyle="round,pad=0.06", linewidth=1.5,
                                  edgecolor=color, facecolor=color, zorder=4)
        ax.add_patch(ibadge)
        ax.text(1.895, cy, emoji, ha='center', va='center', fontsize=8,
                fontweight='bold', color=WHITE, zorder=5)

        # title
        ax.text(2.3, cy + 0.2, title, fontsize=13, fontweight='bold',
                color=DARK, va='center', zorder=4)
        # description
        ax.text(2.3, cy - 0.27, desc, fontsize=10, color="#444444",
                va='center', zorder=4)

        # downward arrow (not after last)
        if i < len(steps) - 1:
            arrow_y_top = cy - box_h/2 - 0.02
            ax.annotate("", xy=(4.0, arrow_y_top - 0.18),
                        xytext=(4.0, arrow_y_top),
                        arrowprops=dict(arrowstyle="-|>", color="#888888", lw=2.0))

    ax.text(4.0, 0.35,
            "Repeat 35 times (2025–2059)",
            ha='center', va='center', fontsize=12, fontstyle='italic', color=DARK)

    save(fig, "diagram_05_one_year.png")


if __name__ == "__main__":
    diagram_01()
    diagram_02()
    diagram_03()
    diagram_04()
    diagram_05()
    print("All diagrams saved.")
