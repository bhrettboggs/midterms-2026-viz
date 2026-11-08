"""Ticket splitting: in states that elected a senator AND a governor in 2026, how far apart the two races landed.

Reads  data/clean/county_results_2026.csv
Writes viz/ticket_splitting/ticket_splitting.png

One row per state. Filled dot = Senate margin, ring = governor margin, both statewide (summed from counties).
Rows are sorted by the gap. Highlighted rows: different parties lead the two races.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
NAMES = {"AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "CO": "Colorado", "GA": "Georgia", "IA": "Iowa",
         "IL": "Illinois", "KS": "Kansas", "MA": "Massachusetts", "ME": "Maine", "MI": "Michigan",
         "MN": "Minnesota", "NH": "New Hampshire", "NM": "New Mexico", "OK": "Oklahoma", "OR": "Oregon",
         "RI": "Rhode Island", "SC": "South Carolina", "TN": "Tennessee", "TX": "Texas", "WY": "Wyoming",
         "ID": "Idaho", "NE": "Nebraska", "SD": "South Dakota", "OH": "Ohio", "FL": "Florida"}
CLIP = 58  # points; margins beyond this are pinned to the edge


def fmt(m: float) -> str:
    return "even" if abs(m) < 0.05 else (f"D+{m:.0f}" if m > 0 else f"R+{-m:.0f}")


def main() -> None:
    setup()
    c = pd.read_csv(CLEAN / "county_results_2026.csv", dtype={"county_fips": str})
    # Statewide totals per race; drop races without both a Democrat and a Republican.
    races = (c[c.d_vs_r_race].groupby(["state", "office", "special"])
             [["dem_votes", "rep_votes", "total_votes"]].sum().reset_index())
    races["margin"] = (races.dem_votes - races.rep_votes) / races.total_votes * 100
    # Where a state has a regular and a special Senate race, use the regular one.
    races = races.sort_values("special").drop_duplicates(["state", "office"])
    w = races.pivot(index="state", columns="office", values="margin").dropna()
    w["gap"] = w.SEN - w.GOV
    w["split"] = (w.SEN > 0) != (w.GOV > 0)
    w = w.assign(abs_gap=w.gap.abs()).sort_values("abs_gap")  # biggest gap at the top
    dropped = sorted(set(c.state[~c.d_vs_r_race]))

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.20, 0.13, 0.74, 0.66])
    for i, (st, r) in enumerate(w.iterrows()):
        if r.split:
            ax.axhspan(i - 0.45, i + 0.45, color="#fbf0d9", zorder=0)
        s, g = max(-CLIP, min(CLIP, r.SEN)), max(-CLIP, min(CLIP, r.GOV))
        ax.plot([s, g], [i, i], color=MUTED, lw=2, zorder=1, solid_capstyle="round")
        ax.scatter([g], [i], s=95, facecolor=SURFACE, edgecolor=ACCENT, lw=2, zorder=3)
        ax.scatter([s], [i], s=95, color=ACCENT, zorder=4)
        ax.text(CLIP + 2, i, f"{abs(r.gap):.0f} pt" + ("" if round(abs(r.gap)) == 1 else "s"), va="center", fontsize=12, color=INK_2)
    ax.set_yticks(range(len(w)))
    ax.set_yticklabels([NAMES.get(s, s) for s in w.index], fontsize=13)
    for lab, (_, r) in zip(ax.get_yticklabels(), w.iterrows()):
        if r.split:
            lab.set_fontweight("bold")
            lab.set_color(INK)
    ax.axvline(0, color=INK_2, lw=1.2, zorder=1)
    ax.set_xlim(-CLIP - 2, CLIP + 12)
    ax.set_ylim(-0.7, len(w) - 0.3)
    ticks = [-50, -25, 0, 25, 50]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["R+50", "R+25", "even", "D+25", "D+50"])
    ax.xaxis.tick_top()
    ax.grid(axis="x", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, labelsize=13)
    ax.text(CLIP + 2, len(w) - 0.2, "gap", fontsize=12, color=INK_2)

    # Key.
    fig.text(0.20, 0.835, "●", color=ACCENT, fontsize=16, va="center")
    fig.text(0.222, 0.835, "Senate", fontsize=13.5, color=INK, va="center")
    fig.text(0.31, 0.835, "○", color=ACCENT, fontsize=18, va="center", weight="bold")
    fig.text(0.332, 0.835, "Governor", fontsize=13.5, color=INK, va="center")
    fig.text(0.44, 0.835, "■", color="#f3dca8", fontsize=16, va="center")
    fig.text(0.462, 0.835, "Different parties lead the two races", fontsize=13.5, color=INK, va="center")

    n_split = int(w.split.sum())
    split_names = " and ".join(NAMES[s] for s in w.index[w.split])
    big = w.gap.abs().sort_values(ascending=False)
    titles(fig, f"{len(w)} states chose a senator and a governor —",
           f"in {n_split}, different parties lead the two races",
           f"Statewide margin in each 2026 race, for states with both on the ballot, sorted by how far apart\n"
           f"they landed. {split_names} have different parties ahead. Median gap: {big.median():.0f} points.")
    footer(fig, [
        "Unofficial, still-counting results summed from county returns.",
        f"Not shown: {', '.join(NAMES.get(s, s) for s in dropped)} (no Democrat-vs-Republican Senate race).",
        "A gap reflects candidates as much as voters: popular incumbents and weak nominees both widen it.",
    ], "civicAPI (2026 county results)")

    out = HERE / "ticket_splitting.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  states {len(w)}, split {list(w.index[w.split])}")


if __name__ == "__main__":
    main()
