"""Older vs younger counties: who turned out, and who moved, in 2026.

Reads  data/clean/county_map_2026.csv
       data/raw/census/cc-est2024-agesex-all.csv   Census county population estimates by age (July 2024)
Writes viz/age_turnout_shift/age_turnout_shift.png

Counties (at least 95% counted) are split into five equal groups by their share of adults aged 65+,
measured against other counties in the same state. Top: turnout vs the state's average county.
Bottom: shift since 2024 vs the state's average county. County age profile, not individual voters' ages.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"
MIN_REPORTING = 95
LABELS = ["Youngest\nfifth", "", "Middle", "", "Oldest\nfifth"]


def load() -> pd.DataFrame:
    a = pd.read_csv(RAW / "census" / "cc-est2024-agesex-all.csv", encoding="latin-1")
    a = a[a.YEAR == 6]  # July 1, 2024 estimate
    a["county_fips"] = a.STATE.astype(str).str.zfill(2) + a.COUNTY.astype(str).str.zfill(3)
    a["adults"] = a.AGE18PLUS_TOT
    a["old"] = a.AGE65PLUS_TOT / a.adults * 100
    m = pd.read_csv(CLEAN / "county_map_2026.csv", dtype={"county_fips": str})
    m = m[m.d_vs_r_race & m.margin_2024.notna() & (m.pct_reporting >= MIN_REPORTING)]
    m = m.merge(a[["county_fips", "adults", "old"]], on="county_fips")
    m["turnout"] = m.total_votes / m.adults * 100
    m["shift"] = m.shift_vs_2024 * 100
    m = m[m.turnout.between(10, 100)]
    for c in ("old", "turnout", "shift"):
        m[c + "_dm"] = m[c] - m.groupby("state")[c].transform("mean")
    m["q"] = pd.qcut(m.old_dm, 5, labels=False)
    return m


def panel(ax, x, y, color, ylabel, fmt):
    ax.bar(x, y, width=0.62, color=[color if v >= 0 else "#a3a29c" for v in y], zorder=3)
    for xi, v in zip(x, y):
        ax.text(xi, v + (0.35 if v >= 0 else -0.35), fmt(v), ha="center", va="bottom" if v >= 0 else "top",
                fontsize=15, weight="semibold", color=INK)
    ax.axhline(0, color=INK, lw=1, zorder=4)
    lim = max(abs(y).max() * 1.35, 3)
    ax.set_ylim(-lim, lim)
    ax.set_yticks([])
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_ylabel(ylabel, labelpad=10, fontsize=14.5)


def main() -> None:
    setup()
    m = load()
    g = m.groupby("q").agg(old=("old", "median"), turnout=("turnout_dm", "mean"), shift=("shift_dm", "mean"))
    rho_t = spearmanr(m.old_dm, m.turnout_dm).statistic
    rho_s = spearmanr(m.old_dm, m.shift_dm).statistic
    x = np.arange(5)

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax1 = fig.add_axes([0.12, 0.50, 0.84, 0.27])
    ax2 = fig.add_axes([0.12, 0.17, 0.84, 0.27])
    panel(ax1, x, g.turnout.values, ACCENT, "Turnout vs. state\naverage (points)", lambda v: f"{v:+.1f}")
    panel(ax2, x, g["shift"].values, ACCENT, "Shift vs. state\naverage (points)",
          lambda v: f"{v:+.1f}")
    ax1.set_title("Who turned out", loc="left", fontsize=17, weight="semibold", pad=10)
    ax2.set_title("Who moved more (or less) toward Democrats than the rest of their state", loc="left", fontsize=17, weight="semibold", pad=10)
    for xi, lab in enumerate(["Youngest", "", "", "", "Oldest"]):
        ax1.text(xi, ax1.get_ylim()[0] - 0.2, lab, ha="center", va="top", fontsize=13, color=INK_2)
    for xi, (lab, old) in enumerate(zip(LABELS, g.old)):
        ax2.text(xi, ax2.get_ylim()[0] - 0.4, (lab + "\n" if lab else "\n\n") + f"{old:.0f}% are 65+",
                 ha="center", va="top", fontsize=13, color=INK_2)

    titles(fig, "Older counties voted more.",
           "Younger counties moved more.",
           f"{len(m):,} counties at least {MIN_REPORTING}% counted ({m.state.nunique()} states), split into fifths by "
           "their share of adults aged 65+,\neach compared with other counties in its own state. Nearly every county "
           "moved toward Democrats;\nthe bottom chart shows which moved more or less than their state's average.")
    footer(fig, [
        "This is each county's age profile, not the ages of the people who voted. Younger counties also tend to be college towns and",
        f"cities, so age overlaps with education and density. Rank correlation, 65+ share vs turnout: {rho_t:.2f}; vs shift: {rho_s:.2f}.",
    ], "Census Bureau county population estimates (July 2024), civicAPI, tonmcg. Unofficial results")

    out = HERE / "age_turnout_shift.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  n={len(m)}\n{g.round(2)}")


if __name__ == "__main__":
    main()
