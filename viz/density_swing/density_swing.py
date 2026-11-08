"""Rural, suburban, urban: where the like-for-like 2022 -> 2026 swing was biggest, and where turnout grew.

Reads  data/clean/county_shift_2022_2026.csv          2022 -> 2026 governor-race county results
       data/raw/census/cc-est2024-agesex-all.csv       county population (July 2024), for density
Writes viz/density_swing/density_swing.png

Counties are grouped by people per square mile. Top: each group's vote-weighted shift relative to its
own state's shift (so Vermont's or Ohio's candidates don't set the rural number). Bottom: 2026 governor
votes as a share of 2022 governor votes in the same counties.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"
MIN_REPORTING = 60
BINS = [0, 10, 50, 200, 1000, 5000, np.inf]
LABELS = ["under 10", "10–50", "50–200", "200–1,000", "1,000–5,000", "5,000+"]
KIND = ["frontier", "rural", "small-town", "suburban", "urban", "dense core"]


def load() -> pd.DataFrame:
    m = pd.read_csv(CLEAN / "county_shift_2022_2026.csv", dtype={"county_fips": str})
    g = m[(m.office == "GOV") & (m.pct_reporting_2026 >= MIN_REPORTING)].copy()
    a = pd.read_csv(RAW / "census" / "cc-est2024-agesex-all.csv", encoding="latin-1")
    a = a[a.YEAR == 6].assign(county_fips=lambda d: d.STATE.astype(str).str.zfill(2) + d.COUNTY.astype(str).str.zfill(3))
    g = g.merge(a[["county_fips", "POPESTIMATE"]], on="county_fips", how="inner")
    g["density"] = g.POPESTIMATE / g.ALAND_SQMI
    g["sh"] = g.shift_2022_2026 * 100
    state_w = g.groupby("state").apply(lambda d: (d.sh * d.votes_2026).sum() / d.votes_2026.sum(), include_groups=False)
    g["rel"] = g.sh - g.state.map(state_w)
    g["bin"] = pd.cut(g.density, BINS, labels=LABELS)
    return g


def main() -> None:
    setup()
    g = load()
    res = g.groupby("bin", observed=True).apply(lambda d: pd.Series({
        "n": len(d), "votes": d.votes_2026.sum(),
        "rel": (d.rel * d.votes_2026).sum() / d.votes_2026.sum(),
        "raw": (d.sh * d.votes_2026).sum() / d.votes_2026.sum(),
        "turnout": d.votes_2026.sum() / d.votes_2022.sum() * 100 - 100}), include_groups=False)
    x = np.arange(len(res))

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax1 = fig.add_axes([0.10, 0.50, 0.86, 0.26])
    ax2 = fig.add_axes([0.10, 0.125, 0.86, 0.19])

    def bars(ax, vals, fmt, color_pos, color_neg, pad, ylim=None):
        ax.bar(x, vals, width=0.64, color=[color_pos if v >= 0 else color_neg for v in vals], zorder=3)
        for xi, v in zip(x, vals):
            ax.text(xi, v + (pad if v >= 0 else -pad), fmt(v), ha="center", va="bottom" if v >= 0 else "top",
                    fontsize=15, weight="semibold", color=INK)
        ax.axhline(0, color=INK, lw=1, zorder=4)
        lim = max(abs(vals).max() * 1.45, 1)
        ax.set_ylim(*(ylim or (-lim, lim)))
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_xlim(-0.6, len(vals) - 0.4)
        for sp in ax.spines.values():
            sp.set_visible(False)

    def signed(v, nd):
        return "0" if round(v, nd) == 0 else f"{v:+.{nd}f}".replace("-", "−")

    bars(ax1, res.rel.values, lambda v: signed(v, 1), ACCENT, "#a3a29c", 0.12)
    tv = res.turnout.values
    bars(ax2, tv, lambda v: signed(v, 0) + "%", ACCENT, "#a3a29c", 0.25, ylim=(min(tv.min() * 1.8, -1.5), tv.max() * 1.4))
    ax1.set_title("Shift toward Democrats, 2022 → 2026 governor race, compared with the rest of the state (points)",
                  loc="left", fontsize=15.5, weight="semibold", pad=12)
    ax2.set_title("Change in votes cast, 2022 → 2026 governor race", loc="left", fontsize=15.5, weight="semibold", pad=12)
    ax1.text(-0.6, ax1.get_ylim()[1] * 0.98, "moved more than\nits state ↑", fontsize=11.5, color=INK_2, va="top",
             linespacing=1.2)
    ax1.text(-0.6, ax1.get_ylim()[0] * 0.98, "moved less ↓", fontsize=11.5, color=INK_2, va="bottom")

    # Shared category labels between the panels, with how much of the vote each group holds.
    share = res.votes / res.votes.sum()
    for xi, (lab, kind, n, sh) in enumerate(zip(LABELS, KIND, res.n, share)):
        fig.text(0.10 + 0.86 * (xi + 0.5) / len(res), 0.445, f"{lab}", ha="center", fontsize=14, color=INK,
                 weight="semibold")
        fig.text(0.10 + 0.86 * (xi + 0.5) / len(res), 0.425, f"{kind}", ha="center", fontsize=12.5, color=INK_2)
        fig.text(0.10 + 0.86 * (xi + 0.5) / len(res), 0.405, f"{int(n):,} counties\n{sh:.0%} of votes", ha="center",
                 va="top", fontsize=11.5, color=MUTED, linespacing=1.25)
    fig.text(0.10, 0.468, "People per square mile (2024)", fontsize=12.5, color=INK_2)

    rural = res.rel.iloc[:2].min()
    sub = res.rel.loc["200–1,000"]
    titles(fig, "Rural counties lagged their states' swing.",
           "Suburban counties led it. Turnout grew with density.",
           f"Counties grouped by population density: {len(g):,} counties in {g.state.nunique()} states with a governor race in\n"
           f"both 2022 and 2026. The sparsest counties moved about {abs(rural):.0f} points less than the rest of their state,\n"
           f"suburban-density counties {sub:+.0f} point more. Votes cast rose {res.turnout.iloc[-2]:.0f}% in urban counties, "
           f"fell {abs(res.turnout.iloc[0]):.0f}% in the sparsest.")
    footer(fig, [
        "Like-for-like: the same office (governor) and the same counties, four years apart, so no presidential baseline is involved.",
        "Within-state comparison removes candidate effects (Vermont, Ohio); across all states the raw shift still rises from "
        f"{res.raw.iloc[0]:+.0f} in the sparsest",
        f"counties to {res.raw.loc['200–1,000']:+.0f} in suburban ones. Unofficial 2026 counts; counties under {MIN_REPORTING}% counted "
        "left out. Density = people ÷ land area.",
    ], "MIT Election Data and Science Lab (2022), civicAPI (2026), Census Bureau (population, land area)")

    out = HERE / "density_swing.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}\n{res.round(2)}")


if __name__ == "__main__":
    main()
