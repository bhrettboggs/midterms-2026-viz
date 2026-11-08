"""Ticket splitting, county by county: every county's 2026 Senate margin against its governor margin.

Reads  data/clean/county_results_2026.csv
Writes viz/split_counties/split_counties.png

States that elected both a senator and a governor in 2026, keeping only races where a Democrat and a
Republican finished top two. One dot per county (area = votes in the Senate race). On the diagonal, the
county gave both candidates the same margin; above it, the Senate candidate ran ahead of the governor
candidate on the Democratic side. Counties that picked different parties for the two offices are orange.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
SPLIT = "#e08a1e"
NAMES = {"NH": "New Hampshire", "NM": "New Mexico", "OR": "Oregon", "SC": "South Carolina", "GA": "Georgia",
         "TN": "Tennessee", "OK": "Oklahoma", "ME": "Maine", "IA": "Iowa", "KS": "Kansas", "TX": "Texas",
         "AK": "Alaska", "MA": "Massachusetts", "IL": "Illinois", "MI": "Michigan", "OH": "Ohio", "AL": "Alabama",
         "AR": "Arkansas", "CO": "Colorado", "FL": "Florida", "MN": "Minnesota"}
# States whose counties sit farthest off the diagonal, with where to put each label (in open space).
LABEL = {"NH": (-48, 34), "ME": (30, -14), "IA": (34, -30), "OK": (-8, -62), "TN": (14, -50), "OR": (-62, 8),
         "GA": (-62, -10)}


def main() -> None:
    setup()
    c = pd.read_csv(CLEAN / "county_results_2026.csv", dtype={"county_fips": str})
    c = c[c.d_vs_r_race].sort_values("special").drop_duplicates(["state", "office", "county_fips"])
    margins = c.pivot_table(index=["state", "county_fips"], columns="office", values="margin_2026") * 100
    votes = c.pivot_table(index=["state", "county_fips"], columns="office", values="total_votes")
    d = margins.dropna().join(votes.add_prefix("v_")).reset_index()
    d["split"] = np.sign(d.SEN) != np.sign(d.GOV)
    d["gap"] = d.SEN - d.GOV
    corr = np.corrcoef(d.SEN, d.GOV)[0, 1]
    same = 1 - d.split.mean()
    med_gap = d.gap.abs().median()

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.11, 0.135, 0.84, 0.64])
    lim = 85
    ax.fill_between([-lim, 0], [0, 0], [lim, lim], color="#fbf0d9", zorder=0)
    ax.fill_between([0, lim], [-lim, -lim], [0, 0], color="#fbf0d9", zorder=0)
    ax.plot([-lim, lim], [-lim, lim], color=INK_2, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.axhline(0, color=INK_2, lw=1, zorder=1)
    ax.axvline(0, color=INK_2, lw=1, zorder=1)
    size = d.v_SEN / d.v_SEN.max() * 1500 + 8
    reg = d[~d.split]
    ax.scatter(reg.GOV, reg.SEN, s=size[~d.split], color="#9ec5f4", ec=ACCENT, lw=0.5, alpha=0.65, zorder=3)
    sp = d[d.split]
    ax.scatter(sp.GOV, sp.SEN, s=size[d.split], color=SPLIT, ec=SURFACE, lw=0.8, alpha=0.9, zorder=4)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ticks = [-80, -60, -40, -20, 0, 20, 40, 60, 80]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    fmt = plt.FuncFormatter(lambda v, _: "even" if v == 0 else (f"D+{v:.0f}" if v > 0 else f"R+{-v:.0f}"))
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    ax.grid(color=GRID, lw=1)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, labelsize=13)
    ax.set_xlabel("Governor race margin in the county", labelpad=10)
    ax.set_ylabel("Senate race margin in the county", labelpad=10)
    ax.text(-82, 80, "Governor Republican,\nsenator Democratic", fontsize=12.5, color=INK_2, va="top", linespacing=1.25)
    ax.text(82, -5, "Governor Democratic,\nsenator Republican", fontsize=12.5, color=INK_2, va="top", ha="right",
            linespacing=1.25)
    ax.text(60, 70, "same margin\nfor both ↗", fontsize=12, color=INK_2, ha="center", rotation=0)

    # State labels, each pointing at the state's median county, placed in open space.
    med = d.groupby("state")[["GOV", "SEN"]].median()
    for st, (tx, ty) in LABEL.items():
        x, y = med.loc[st]
        ax.annotate(NAMES[st], (x, y), xytext=(tx, ty), fontsize=12, color=INK, weight="semibold", ha="center",
                    va="center", arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.9, shrinkB=3), zorder=6)

    # Size key and the orange key, in the empty lower-right quadrant.
    for i, v in enumerate((10_000, 100_000, 1_000_000)):
        xk, yk = 38 + i * 16, -48
        ax.scatter([xk], [yk], s=v / d.v_SEN.max() * 1500 + 8, color="#9ec5f4", ec=ACCENT, lw=0.5)
        ax.text(xk, -60, f"{v // 1000:,}K" if v < 1e6 else "1M", ha="center", fontsize=11.5, color=INK_2)
    ax.text(31, -36, "Votes cast in the Senate race", fontsize=12, color=INK_2)
    ax.scatter([34], [-73], s=90, color=SPLIT, ec=SURFACE, lw=0.8)
    ax.text(39, -73, f"different parties won the two races\n({int(d.split.sum())} counties, {d[d.split].v_SEN.sum() / d.v_SEN.sum():.0%} of votes)",
            fontsize=12, color=INK_2, va="center", linespacing=1.2)

    titles(fig, f"{same:.0%} of counties backed the same party for",
           "senator and governor. The exceptions cluster by state.",
           f"Each dot is a county in one of the {d.state.nunique()} states that elected both in 2026 ({len(d):,} counties). "
           f"The two margins\ntrack each other closely (correlation {corr:.2f}; typical gap {med_gap:.0f} points), and where "
           f"they don't, whole states\nmove together (New Hampshire, Oklahoma, Tennessee, Maine): the candidates differ, "
           "not the voters.")
    footer(fig, [
        "Unofficial, still-counting results. Only races where a Democrat and a Republican finished top two (drops Idaho, Nebraska,",
        "South Dakota, Rhode Island, Wyoming). Alaska: first-choice votes; both races go to ranked-choice rounds. Margins are",
        "Democratic minus Republican share of all votes in the county.",
    ], "civicAPI (2026 county results)")

    out = HERE / "split_counties.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  n={len(d)}, split {int(d.split.sum())}, corr {corr:.3f}, median gap {med_gap:.2f}")


if __name__ == "__main__":
    main()
