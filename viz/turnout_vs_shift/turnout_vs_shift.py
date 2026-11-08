"""Did turnout drive the 2026 shift? County turnout (vs 2024) against how far each county moved.

Reads  data/clean/county_map_2026.csv
Writes viz/turnout_vs_shift/turnout_vs_shift.png

x = 2026 Senate/governor votes as a share of the county's 2024 presidential votes ("turnout held up")
y = change in margin from 2024 president to 2026 Senate/governor (+ = toward Democrats)
Only counties at least 95% counted, so partial counts don't fake a turnout drop.
This shows association, not cause.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
MIN_REPORTING = 95


def main() -> None:
    setup()
    m = pd.read_csv(CLEAN / "county_map_2026.csv", dtype={"county_fips": str})
    m = m[m.d_vs_r_race & m.margin_2024.notna() & (m.total_votes_2024 > 0) & (m.pct_reporting >= MIN_REPORTING)].copy()
    m["held"] = m.total_votes / m.total_votes_2024 * 100
    m = m[m.held.between(20, 150)]
    m["shift"] = m.shift_vs_2024 * 100

    # Within-state comparison: rank counties against others in the same state (same races, same candidates).
    m["held_dm"] = m.held - m.groupby("state").held.transform("mean")
    m["shift_dm"] = m["shift"] - m.groupby("state")["shift"].transform("mean")
    lo = m[m.held_dm <= m.held_dm.quantile(0.2)]
    hi = m[m.held_dm >= m.held_dm.quantile(0.8)]
    gap = lo.shift_dm.mean() - hi.shift_dm.mean()
    rho = spearmanr(m.held_dm, m.shift_dm).statistic
    avg = np.average(m["shift"], weights=m.total_votes)

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.10, 0.17, 0.85, 0.62])
    size = np.sqrt(m.total_votes) / np.sqrt(m.total_votes.max()) * 420 + 6
    ax.scatter(m.held_dm, m.shift_dm, s=size, color="#9ec5f4", ec=ACCENT, lw=0.5, alpha=0.75, zorder=3)

    # Binned medians: the typical county at each relative-turnout level.
    bins = np.arange(-15, 16, 3)
    m["bin"] = pd.cut(m.held_dm, bins)
    med = m.groupby("bin", observed=True).agg(x=("held_dm", "median"), y=("shift_dm", "median"), n=("shift_dm", "size"))
    med = med[med.n >= 15]
    ax.plot(med.x, med.y, color=INK, lw=2.5, marker="o", ms=7, mfc=SURFACE, mew=2, zorder=5)
    ax.annotate("Typical county at each turnout\nlevel (median): nearly flat", (med.x.iloc[-2], med.y.iloc[-2]),
                xytext=(10, 80), textcoords="offset points", fontsize=13.5, color=INK, weight="semibold",
                arrowprops=dict(arrowstyle="-", color=INK_2, lw=1))

    ax.axhline(0, color=INK_2, lw=1, zorder=1)
    ax.axvline(0, color=INK_2, lw=1, zorder=1)
    ax.set_xlim(-18, 18)
    ax.set_ylim(-20, 20)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:+.0f}".replace("-", "−") if v else "state avg"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: "state avg" if v == 0 else f"{v:+.0f}".replace("-", "−")))
    ax.grid(color=GRID, lw=1)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, labelsize=13.5)
    ax.set_xlabel("Turnout vs. the rest of its state (points)  ←  fell off more   |   held up better  →", labelpad=12)
    ax.set_ylabel("Shift since 2024 vs. the rest of its state (points)", labelpad=10)
    ax.text(-17.5, 19, "Moved more toward Democrats ↑", fontsize=12.5, color=INK_2, va="top")
    ax.text(-17.5, -19, "Moved more toward Republicans ↓", fontsize=12.5, color=INK_2, va="bottom")

    # Size key.
    for i, v in enumerate((10_000, 100_000, 1_000_000)):
        xx = 8 + i * 3.6
        ax.scatter([xx], [-15.5], s=np.sqrt(v) / np.sqrt(m.total_votes.max()) * 420 + 6, color="#9ec5f4", ec=ACCENT,
                   lw=0.5)
        ax.text(xx, -18.2, f"{v:,}", ha="center", fontsize=11, color=INK_2)
    ax.text(8, -12.3, "Votes cast", fontsize=12, color=INK_2)

    titles(fig, "Turnout didn't decide the swing",
           "Counties moved about the same either way",
           f"Each dot is a county at least {MIN_REPORTING}% counted ({len(m):,} counties, {m.state.nunique()} states), "
           "compared with other\ncounties in its own state, since every state had different races. Where turnout fell "
           f"off most,\ncounties moved just {gap:.1f} points more than where it held up, against a ~{avg:.0f}-point swing overall.")
    footer(fig, [
        "Shows association, not cause. Turnout = 2026 Senate/governor votes as a share of 2024 presidential votes. Shift = change in",
        "margin from the 2024 presidential race. Across states (not within), lower-turnout states did swing more, but those states also",
        f"had different races and candidates. Rank correlation within states: {rho:.2f}.",
    ], "civicAPI (2026 county results), tonmcg (2024 county results). Unofficial results")

    out = HERE / "turnout_vs_shift.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  n={len(m)}, avg {avg:.1f}, gap {gap:.2f}, rho {rho:.3f}")


if __name__ == "__main__":
    main()
