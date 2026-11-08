"""An 8-page LinkedIn carousel that tells one story: why did the 2026 midterms swing toward Democrats?

Each page tests one idea; a clue tracker at the bottom fills in as you swipe.
Written for about a 6th-grade reading level.

Reads  data/clean/county_map_2026.csv, turnout_national_midterms.csv, exit_poll_groups.csv,
       plus the Senate race table built by viz/senate_states_glance.
Writes viz/linkedin_story/page_1.png ... page_8.png and midterms_2026_story.pdf (upload the PDF to LinkedIn).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

VIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VIZ))
sys.path.insert(0, str(VIZ / "senate_states_glance"))
from senate_states_glance import build as senate_table  # noqa: E402
from style import ACCENT, CLEAN, DEM, GRID, INK, INK_2, MUTED, NEUTRAL, REP, SURFACE, setup  # noqa: E402

HERE = Path(__file__).resolve().parent
W, H = 10.8, 13.5  # 1080 x 1350 px: LinkedIn's portrait document size
TOTAL = 8
QUESTION = "Why did the 2026 midterms swing toward Democrats?"
REPO = "github.com/bhrettboggs/midterms-2026-viz"
L = 0.07  # left margin
YES, NO, OPEN = "#0d366b", "#8a8984", "#d9d8d3"

# Clue tracker states, page by page: (verdict, short word)
IDEAS = ["More people voting", "More money", "Voters changed"]


# ---------- shared page parts ----------

def page(n: int):
    fig = plt.figure(figsize=(W, H), dpi=100)
    fig.text(L, 0.955, QUESTION, fontsize=15, color=MUTED, weight="semibold")
    fig.text(1 - L, 0.955, f"{n} / {TOTAL}", fontsize=15, color=MUTED, ha="right", weight="semibold")
    # progress bar
    fig.add_artist(Rectangle((L, 0.94), 1 - 2 * L, 0.004, color=GRID, transform=fig.transFigure))
    fig.add_artist(Rectangle((L, 0.94), (1 - 2 * L) * n / TOTAL, 0.004, color=ACCENT, transform=fig.transFigure))
    return fig


def headline(fig, text: str, body: str = "", y: float = 0.905) -> None:
    fig.text(L, y, text, fontsize=38, weight="bold", va="top", linespacing=1.12)
    if body:
        lines = text.count("\n") + 1
        fig.text(L, y - 0.052 * lines - 0.012, body, fontsize=20, color=INK_2, va="top", linespacing=1.45)


def tracker(fig, verdicts: dict, current: str | None = None, y: float = 0.085) -> None:
    """Three cards along the bottom. verdicts: idea -> (status, word); status in yes/no/open."""
    fig.text(L, y + 0.088, "CLUE TRACKER", fontsize=13, color=MUTED, weight="bold")
    gap = 0.02
    w = (1 - 2 * L - 2 * gap) / 3
    for i, idea in enumerate(IDEAS):
        x = L + i * (w + gap)
        status, word = verdicts.get(idea, ("open", "Not tested yet"))
        face = {"yes": YES, "no": SURFACE, "open": SURFACE}[status]
        edge = {"yes": YES, "no": NO, "open": OPEN}[status]
        lw = 3 if idea == current else 1.5
        if idea == current and status == "open":
            edge = ACCENT
        fig.add_artist(FancyBboxPatch((x, y), w, 0.075, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, fc=face, ec=edge, lw=lw))
        ink = SURFACE if status == "yes" else (INK if status == "no" else INK_2)
        mark = {"yes": "✓", "no": "✗", "open": "?"}[status]
        fig.text(x + 0.018, y + 0.051, f"{mark}  {idea}", fontsize=14.5, weight="bold", color=ink, va="center")
        fig.text(x + 0.018, y + 0.022, word, fontsize=13.5, color=ink, va="center")


def source(fig, text: str) -> None:
    fig.text(L, 0.035, text, fontsize=11.5, color=MUTED, va="top", linespacing=1.4)


def clean_axes(ax) -> None:
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)


# ---------- data ----------

def county_numbers():
    m = pd.read_csv(CLEAN / "county_map_2026.csv")
    m = m[m.d_vs_r_race & m.margin_2024.notna()]
    return len(m), (m.shift_vs_2024 > 0).mean(), m.state.nunique()


def turnout_test(min_reporting: float = 95):
    """Same method as viz/turnout_vs_shift: compare counties inside the same state."""
    m = pd.read_csv(CLEAN / "county_map_2026.csv")
    m = m[m.d_vs_r_race & m.margin_2024.notna() & (m.total_votes_2024 > 0) & (m.pct_reporting >= min_reporting)].copy()
    m["held"] = m.total_votes / m.total_votes_2024 * 100
    m = m[m.held.between(20, 150)]
    m["shift"] = m.shift_vs_2024 * 100
    m["held_dm"] = m.held - m.groupby("state").held.transform("mean")
    m["shift_dm"] = m["shift"] - m.groupby("state")["shift"].transform("mean")
    lo = m[m.held_dm <= m.held_dm.quantile(0.2)]
    hi = m[m.held_dm >= m.held_dm.quantile(0.8)]
    return np.average(m["shift"], weights=m.total_votes), lo.shift_dm.mean() - hi.shift_dm.mean(), len(m)


# ---------- pages ----------

def p1():
    fig = page(1)
    fig.text(L, 0.86, "The 2026 midterms\nswung toward\nDemocrats.", fontsize=58, weight="bold", va="top",
             linespacing=1.08)
    fig.text(L, 0.56, "Why?", fontsize=58, weight="bold", color=ACCENT, va="top")
    fig.text(L, 0.44, "People have lots of ideas. I tested three of them\nwith public data. "
                      "Each page checks one clue.", fontsize=22, color=INK_2, va="top", linespacing=1.45)
    fig.text(L, 0.31, "Swipe to follow along  →", fontsize=22, weight="bold", color=ACCENT, va="top")
    tracker(fig, {})
    source(fig, "By Bhrett Boggs. Results are unofficial, as of Nov. 6, 2026.")
    return fig


def p2():
    n, share, states = county_numbers()
    blue = round(share * 100)
    fig = page(2)
    headline(fig, f"First, what happened?\n{blue} of every 100 counties\nmoved toward Democrats.",
             "Compared with how the same county voted\nfor president in 2024.")
    ax = fig.add_axes([0.20, 0.25, 0.60, 0.36])
    for k in range(100):
        r, c = divmod(k, 10)
        ax.add_patch(Rectangle((c, 9 - r), 0.86, 0.86, color=DEM if k < blue else REP))
    ax.set_xlim(-0.1, 10)
    ax.set_ylim(-0.1, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(0.20, 0.225, "■", color=DEM, fontsize=20, va="center")
    fig.text(0.235, 0.225, f"{blue} moved toward Democrats", fontsize=17, va="center")
    fig.text(0.60, 0.225, "■", color=REP, fontsize=20, va="center")
    fig.text(0.635, 0.225, f"{100 - blue} toward Republicans", fontsize=17, va="center")
    fig.text(0.5, 0.185, "That is a lot. So what caused it? Let's test three ideas.", fontsize=18,
             weight="semibold", ha="center", color=ACCENT)
    source(fig, f"{n:,} counties in {states} states with a Senate or governor race between a Democrat and a Republican.\n"
                "The 2026 races are for Senate or governor, not president, so some of the move is just different races.\n"
                "Data: civicAPI (2026), tonmcg county results (2024).")
    return fig


def p3():
    t = pd.read_csv(CLEAN / "turnout_national_midterms.csv")
    t = t[t.year >= 1950]
    fig = page(3)
    headline(fig, "Idea 1: More people voted.",
             "49 out of every 100 eligible people voted.\nThat's the 2nd most for a midterm in over 100 years.")
    ax = fig.add_axes([0.10, 0.34, 0.83, 0.38])
    colors = [ACCENT if y == 2026 else ("#9ec5f4" if y == 2018 else "#cfcec9") for y in t.year]
    ax.bar(t.year, t.turnout * 100, width=3, color=colors, zorder=3)
    for yr, lab in ((2018, "2018: 50"), (2026, "2026: 49")):
        v = t.loc[t.year == yr, "turnout"].iloc[0] * 100
        ax.text(yr, v + (5.5 if yr == 2018 else 1.2), lab, ha="center", fontsize=15, weight="bold", color=ACCENT if yr == 2026 else INK_2)
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_ylabel("Out of every 100 eligible people", fontsize=15)
    ax.set_xticks([1950, 1970, 1990, 2010, 2026])
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    clean_axes(ax)
    ax.tick_params(labelsize=15)
    fig.text(L, 0.275, "High turnout is a common guess for a big swing.\nBut did it actually cause it? Next page.",
             fontsize=18, weight="semibold", color=ACCENT, va="top", linespacing=1.4)
    tracker(fig, {}, current=IDEAS[0])
    source(fig, "Midterm turnout of eligible citizens. 2026 is an early estimate.\n"
                "Data: Michael McDonald, UF Election Lab.")
    return fig


def p4():
    swing, part, n = turnout_test()
    fig = page(4)
    headline(fig, "Turnout test:\nonly a small part.",
             "I compared counties inside the same state.\nWhere fewer people showed up, the swing was only\n"
             f"about {part:.0f} point bigger. The total swing was about {swing:.0f}.")
    ax = fig.add_axes([0.36, 0.33, 0.55, 0.20])
    ax.barh([1, 0], [swing, part], color=[ACCENT, MUTED], height=0.55, zorder=3)
    ax.text(swing + 0.3, 1, f"{swing:.0f} points", va="center", fontsize=20, weight="bold", color=ACCENT)
    ax.text(part + 0.3, 0, f"about {part:.0f}", va="center", fontsize=20, weight="bold", color=INK_2)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["Average swing\ntoward Democrats", "Extra swing where\nturnout dropped most"], fontsize=16)
    ax.set_xlim(0, 21)
    ax.set_xticks([])
    clean_axes(ax)
    fig.text(L, 0.27, "What's a point? If one side wins 55 to 45, they lead by 10 points.\n"
                      "A swing of 15 means the lead moved 15 points toward Democrats.",
             fontsize=16, color=INK_2, va="top", linespacing=1.45)
    tracker(fig, {IDEAS[0]: ("no", "Only a small part")}, current=IDEAS[0])
    source(fig, f"{n} counties at 95%+ counted. \"Turnout dropped most\" = the fifth of counties in each state with the\n"
                "biggest drop in votes since 2024, compared with the fifth with the smallest drop. Association, not cause.")
    return fig


def p5():
    d = senate_table()
    d["dmore"] = d.d_share > 0.5
    g = d.groupby("dmore")["shift"].agg(["mean", "size"])
    fig = page(5)
    headline(fig, "Idea 2: The side that\nspent more won more.",
             "I checked every Senate race. Did Democrats swing\nmore in states where they spent more?")
    ax = fig.add_axes([0.14, 0.35, 0.76, 0.28])
    vals = [g.loc[True, "mean"], g.loc[False, "mean"]]
    ax.bar([0, 1], vals, color=[DEM, REP], width=0.55, zorder=3)
    for x, v in enumerate(vals):
        ax.text(x, v + 0.5, f"{v:.0f} points", ha="center", fontsize=24, weight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels([f"Democrats spent more\n({g.loc[True, 'size']} races)",
                        f"Republicans spent more\n({g.loc[False, 'size']} races)"], fontsize=16)
    ax.set_ylim(0, 20)
    ax.set_yticks([])
    ax.set_title("Average swing toward Democrats", fontsize=16, color=INK_2, loc="left", pad=18)
    clean_axes(ax)
    fig.text(L, 0.255, "Same swing either way. Spending more didn't seem to matter.", fontsize=18,
             weight="semibold", color=ACCENT, va="top")
    tracker(fig, {IDEAS[0]: ("no", "Only a small part"), IDEAS[1]: ("no", "No clear link")}, current=IDEAS[1])
    source(fig, f"{len(d)} Senate races with a Democrat and a Republican. Spending = campaigns + outside groups.\n"
                f"Exact averages: {vals[0]:.1f} vs. {vals[1]:.1f}. Data: FEC, civicAPI, tonmcg (2024).")
    return fig


def p6():
    d = pd.read_csv(CLEAN / "exit_poll_groups.csv")
    w = d.pivot_table(index="group", columns="year", values="margin")
    order = [("18-29", "Ages 18–29"), ("65+", "Ages 65+"), ("Women", "Women"), ("Men", "Men"),
             ("Black", "Black"), ("Hispanic/Latino", "Latino"), ("Asian", "Asian"), ("White", "White"),
             ("Under $50K", "Earn under $50K"), ("$100K+", "Earn $100K+")]
    fig = page(6)
    headline(fig, "Idea 3: Voters changed.\nEvery group moved.",
             "Compared with the last midterm in 2022, every group\nbelow voted more for Democrats in 2026.")
    ax = fig.add_axes([0.27, 0.215, 0.58, 0.43])
    ys = np.arange(len(order))[::-1]
    for y, (g, lab) in zip(ys, order):
        a, b = w.loc[g, 2022], w.loc[g, 2026]
        ax.annotate("", (b, y), (a, y), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.2, mutation_scale=16,
                                                         shrinkA=7, shrinkB=5))
        ax.scatter([a], [y], s=90, fc=SURFACE, ec=ACCENT, lw=2.2, zorder=4)
        ax.scatter([b], [y], s=100, color=ACCENT, zorder=5)
        ax.text(98, y, f"+{b - a:.0f}", va="center", ha="right", fontsize=17, weight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([lab for _, lab in order], fontsize=16)
    ax.axvline(0, color=INK_2, lw=1.2)
    ax.set_xlim(-25, 100)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_xticks([-20, 0, 20, 40, 60])
    ax.set_xticklabels(["R+20", "Tied", "D+20", "D+40", "D+60"], fontsize=14)
    ax.xaxis.tick_top()
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    clean_axes(ax)
    fig.text(0.841, 0.655, "Moved", fontsize=14, color=INK_2, ha="right")
    fig.text(L, 0.695, "○ 2022   ● 2026      D+20 = Democrats won that group by 20 points",
             fontsize=15, color=INK_2)
    tracker(fig, {IDEAS[0]: ("no", "Only a small part"), IDEAS[1]: ("no", "No clear link"),
                  IDEAS[2]: ("yes", "Biggest clue")}, current=IDEAS[2])
    source(fig, "National exit polls for the U.S. House. Exit polls are surveys, so each number can be off by a few points.\n"
                "2026 numbers are early. Data: network exit polls via Wikipedia; checked against ABC News.")
    return fig


def p7():
    d = pd.read_csv(CLEAN / "exit_poll_groups.csv")
    d = d[d.dimension == "Income"].pivot_table(index="year", columns="group", values="margin")
    gap96 = d.loc[1996, "Under $50K"] - d.loc[1996, "$100K+"]
    gap26 = d.loc[2026, "Under $50K"] - d.loc[2026, "$100K+"]
    fig = page(7)
    headline(fig, "One layer deeper:\nsome changes are older.",
             "For 30 years, richer voters leaned Republican and\npoorer voters leaned Democratic. "
             "Now they vote\nalmost the same.")
    ax = fig.add_axes([0.10, 0.31, 0.70, 0.35])
    ax.axhspan(0, 30, color="#eef4fc", zorder=0)
    ax.axhspan(-25, 0, color="#fcefee", zorder=0)
    ax.text(1997, 27, "Leaned Democratic", fontsize=14, color=DEM, weight="bold", va="top")
    ax.text(1997, -22, "Leaned Republican", fontsize=14, color=REP, weight="bold", va="bottom")
    for g, col, lab in (("Under $50K", INK, "Earn under\n$50K"), ("$100K+", ACCENT, "Earn\n$100K+")):
        ax.plot(d.index, d[g], color=col, lw=3, marker="o", ms=6, zorder=3)
        ax.text(2027.3, d.loc[2026, g] + (4 if g == "Under $50K" else -4), lab, fontsize=15, weight="bold",
                color=col, va="center")
    ax.axhline(0, color=INK_2, lw=1)
    ax.set_xlim(1995, 2027)
    ax.set_ylim(-25, 30)
    ax.set_yticks([-20, -10, 0, 10, 20])
    ax.set_yticklabels(["R+20", "R+10", "Tied", "D+10", "D+20"], fontsize=14)
    ax.set_xticks([1996, 2006, 2016, 2026])
    ax.tick_params(labelsize=14)
    clean_axes(ax)
    fig.text(L, 0.27, f"The gap between them was {gap96:.0f} points in 1996.\nIn 2026 it was {gap26:.0f}.",
             fontsize=19, weight="semibold", color=ACCENT, va="top", linespacing=1.4)
    tracker(fig, {IDEAS[0]: ("no", "Only a small part"), IDEAS[1]: ("no", "No clear link"),
                  IDEAS[2]: ("yes", "Biggest clue")}, current=IDEAS[2])
    source(fig, "Exit polls for president (1996–2024) and U.S. House (midterms). Dollars are not adjusted for inflation.\n"
                "Data: Roper Center; network exit polls via Wikipedia.")
    return fig


def p8():
    fig = page(8)
    headline(fig, "What I found")
    rows = [("✗", "More people voting", "Turnout was high, but it explains only\nabout 1 point of a 15-point swing.", NO),
            ("✗", "More money", "States where Democrats spent more\nswung the same as states where they didn't.", NO),
            ("✓", "Voters changed", "Almost every place and every group\nmoved toward Democrats.", YES)]
    y = 0.80
    for mark, idea, why, col in rows:
        fig.text(L, y, mark, fontsize=34, weight="bold", color=col, va="top")
        fig.text(L + 0.07, y - 0.002, idea, fontsize=24, weight="bold", va="top")
        fig.text(L + 0.07, y - 0.045, why, fontsize=18, color=INK_2, va="top", linespacing=1.4)
        y -= 0.145
    fig.add_artist(Rectangle((L, 0.355), 1 - 2 * L, 0.0015, color=GRID, transform=fig.transFigure))
    fig.text(L, 0.33, "What the data can't tell us", fontsize=20, weight="bold", va="top")
    fig.text(L, 0.29, "Why people changed their minds. That needs other data,\nlike polls about the issues. "
                      "One thing to know: the party\nin the White House usually loses ground in midterms.",
             fontsize=17, color=INK_2, va="top", linespacing=1.45)
    fig.text(L, 0.135, "All code and data are free to check:", fontsize=17, va="top")
    fig.text(L, 0.10, REPO, fontsize=19, weight="bold", color=ACCENT, va="top")
    source(fig, "Results are unofficial and still being counted. Patterns here are links, not proof of cause.")
    return fig


def main() -> None:
    setup()
    pages = [p1, p2, p3, p4, p5, p6, p7, p8]
    with PdfPages(HERE / "midterms_2026_story.pdf") as pdf:
        for i, make in enumerate(pages, 1):
            fig = make()
            fig.savefig(HERE / f"page_{i}.png", facecolor=SURFACE)
            pdf.savefig(fig, facecolor=SURFACE)
            plt.close(fig)
    print("wrote", HERE)


if __name__ == "__main__":
    main()
