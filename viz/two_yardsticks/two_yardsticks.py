"""Two yardsticks for one swing: each governor race's shift measured against 2022's governor race,
and against the 2024 presidential vote, in the same counties.

Reads  data/clean/county_shift_2022_2026.csv                 2022 -> 2026 same-office county results
       data/raw/tonmcg/2024_US_County_Level_Presidential_Results.csv
Writes viz/two_yardsticks/two_yardsticks.png

Every "shift since 2024" in this project compares a governor or Senate race with a presidential race.
This chart shows what that choice does: statewide, the two baselines agree on the size of the national
swing but disagree, sometimes wildly, on individual states — the gap is candidates and offices, not voters.
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
NAMES = {"AL": "Alabama", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "FL": "Florida",
         "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IA": "Iowa", "KS": "Kansas", "ME": "Maine",
         "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "NE": "Nebraska", "NV": "Nevada",
         "NH": "New Hampshire", "NM": "New Mexico", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
         "PA": "Pennsylvania", "SC": "South Carolina", "SD": "South Dakota", "TX": "Texas", "VT": "Vermont",
         "WI": "Wisconsin"}
CLIP = 42


def build() -> pd.DataFrame:
    m = pd.read_csv(CLEAN / "county_shift_2022_2026.csv", dtype={"county_fips": str})
    m = m[m.office == "GOV"]
    b = pd.read_csv(RAW / "tonmcg" / "2024_US_County_Level_Presidential_Results.csv", dtype={"county_fips": str})
    m = m.merge(b[["county_fips", "votes_dem", "votes_gop", "total_votes"]], on="county_fips", how="inner")
    s = m.groupby("state")[["dem_2022", "rep_2022", "votes_2022", "dem_2026", "rep_2026", "votes_2026",
                            "votes_dem", "votes_gop", "total_votes"]].sum()
    s["m22"] = (s.dem_2022 - s.rep_2022) / s.votes_2022 * 100
    s["m24"] = (s.votes_dem - s.votes_gop) / s.total_votes * 100
    s["m26"] = (s.dem_2026 - s.rep_2026) / s.votes_2026 * 100
    s["vs22"] = s.m26 - s.m22
    s["vs24"] = s.m26 - s.m24
    return s.sort_values("vs22")


def fmt(v: float) -> str:
    return "0" if round(v) == 0 else f"{v:+.0f}".replace("-", "−")


def main() -> None:
    setup()
    s = build()
    med22, med24 = s.vs22.median(), s.vs24.median()
    s["gap"] = (s.vs22 - s.vs24).abs()

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.17, 0.12, 0.70, 0.645])
    y = np.arange(len(s))
    for i in range(0, len(s), 2):
        ax.axhspan(i - 0.5, i + 0.5, color="#f5f4f1", zorder=0)
    ax.axvline(0, color=INK_2, lw=1.2, zorder=2)
    for yi, (st, r) in zip(y, s.iterrows()):
        a, b = np.clip(r.vs22, -CLIP, CLIP), np.clip(r.vs24, -CLIP, CLIP)
        ax.plot([a, b], [yi, yi], color="#c9c8c3" if r.gap < 8 else "#e3a94a", lw=2.5 if r.gap >= 8 else 2, zorder=2,
                solid_capstyle="round")
        ax.scatter([b], [yi], s=78, facecolor=SURFACE, edgecolor=INK_2, lw=1.8, zorder=3)
        ax.scatter([a], [yi], s=86, color=ACCENT, zorder=4)
        ax.text(CLIP + 5.5, yi, fmt(r.vs22), va="center", ha="right", fontsize=12.5, color=INK, weight="semibold")
        ax.text(CLIP + 13.5, yi, fmt(r.vs24), va="center", ha="right", fontsize=12.5, color=INK_2)
        if r.vs22 < -CLIP or r.vs22 > CLIP or r.vs24 < -CLIP or r.vs24 > CLIP:
            ax.text(np.sign(r.vs24) * (CLIP + 0.8), yi, "→" if r.vs24 > 0 else "←", va="center",
                    ha="left" if r.vs24 > 0 else "right", fontsize=11, color=INK_2)
    ax.set_yticks(y)
    ax.set_yticklabels([NAMES.get(st, st) for st in s.index], fontsize=12.5)
    ax.set_ylim(-0.7, len(s) + 1.5)
    ax.set_xlim(-CLIP - 2, CLIP + 14)
    ax.set_xticks([-40, -30, -20, -10, 0, 10, 20, 30, 40])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: "no change" if v == 0 else f"{v:+.0f}".replace("-", "−")))
    ax.grid(axis="x", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, labelsize=12)
    ax.text(CLIP + 5.5, len(s) + 1.45, "vs 2022\ngov.", ha="right", va="top", fontsize=11, color=INK, weight="semibold",
            linespacing=1.15)
    ax.text(CLIP + 13.5, len(s) + 1.45, "vs 2024\npres.", ha="right", va="top", fontsize=11, color=INK_2, linespacing=1.15)
    ax.text(-1.2, len(s) + 1.0, "← toward Republicans", fontsize=12, color=INK_2, va="top", ha="right")
    ax.text(1.2, len(s) + 1.0, "toward Democrats →", fontsize=12, color=INK_2, va="top", ha="left")

    # Key.
    fig.text(0.17, 0.80, "●", color=ACCENT, fontsize=15, va="center")
    fig.text(0.19, 0.80, "shift vs. the 2022 governor race (same office)", fontsize=13, color=INK, va="center")
    fig.text(0.57, 0.80, "○", color=INK_2, fontsize=16, va="center", weight="bold")
    fig.text(0.59, 0.80, "shift vs. the 2024 presidential vote", fontsize=13, color=INK, va="center")
    fig.text(0.17, 0.778, "■", color="#e3a94a", fontsize=13, va="center")
    fig.text(0.19, 0.778, "the two yardsticks disagree by 8 points or more", fontsize=12.5, color=INK_2, va="center")

    big = s.sort_values("gap", ascending=False).head(3)
    names = ", ".join(NAMES[i] for i in big.index)
    titles(fig, "Two yardsticks, one swing: the national story holds,",
           "the state stories depend on what you compare",
           f"Each state's 2026 governor margin against its 2022 governor margin (same office, same kind of electorate)\n"
           f"and against the 2024 presidential margin, in the same counties. Median state: {med22:+.0f} points by the first\n"
           f"yardstick, {med24:+.0f} by the second. The biggest gaps ({names}) are candidate effects.")
    footer(fig, [
        f"{len(s)} states with a Democrat-vs-Republican governor race in both 2022 and 2026. Unofficial 2026 counts. "
        "Vermont's 2022 race (a popular",
        "Republican winning by 47 in a Harris+32 state) is the extreme case of a candidate effect: +40 by one yardstick, −38 by the other.",
        "The same comparison for Senate races in the 16 states that also voted for the Senate in 2022 gives medians of +15 and +18.",
    ], "MIT Election Data and Science Lab (2022), civicAPI (2026), tonmcg (2024 county presidential results)")

    out = HERE / "two_yardsticks.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  medians vs22 {med22:.1f} vs24 {med24:.1f}; biggest gaps {big.gap.round(1).to_dict()}")


if __name__ == "__main__":
    main()
