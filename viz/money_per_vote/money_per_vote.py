"""How much was spent around each 2026 Senate race for every vote cast, against how close it was.

Reads  data/clean/senate_races.csv
Writes viz/money_per_vote/money_per_vote.png

One dot per race. x = final margin between the top two candidates, y = dollars per vote (log scale),
dot area = votes cast. One color for every race: this chart is about competitiveness, not party.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
STATE_NAME = {"AK": "Alaska", "ME": "Maine", "IA": "Iowa", "NH": "New Hampshire", "NE": "Nebraska",
              "KS": "Kansas", "OH": "Ohio", "MI": "Michigan", "TX": "Texas", "SC": "South Carolina",
              "MS": "Mississippi", "FL": "Florida", "GA": "Georgia", "NC": "North Carolina", "OR": "Oregon",
              "LA": "Louisiana", "IL": "Illinois", "WY": "Wyoming", "RI": "Rhode Island", "MA": "Massachusetts"}
LABEL = ["AK", "ME", "IA", "NH", "NE", "OH", "TX", "MI", "SC", "MS", "FL", "GA", "NC", "OR", "RI", "WY", "LA"]
CLOSE = 0.07  # "close race" cutoff for the headline comparison


def main() -> None:
    setup()
    r = pd.read_csv(CLEAN / "senate_races.csv")
    close = r[r.top_two_margin < CLOSE].money_per_vote.median()
    safe = r[r.top_two_margin >= 0.15].money_per_vote.median()
    rho = spearmanr(r.top_two_margin, r.money_per_vote).statistic

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.11, 0.18, 0.84, 0.64])
    x = r.top_two_margin * 100
    y = r.money_per_vote
    size = r.total_votes / r.total_votes.max() * 2600 + 40
    ax.scatter(x, y, s=size, color="#9ec5f4", ec=ACCENT, lw=1.2, alpha=0.85, zorder=3)

    ax.set_yscale("log")
    ax.set_ylim(1.2, 1000)
    ax.set_xlim(-1, 40)
    ax.yaxis.set_major_locator(FixedLocator([2, 5, 10, 20, 50, 100, 200, 500]))
    ax.yaxis.set_minor_locator(FixedLocator([]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} pts"))
    ax.grid(color=GRID, lw=1)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0, labelsize=14)
    ax.set_xlabel("Final margin between the top two candidates  →  less competitive", labelpad=12)
    ax.set_ylabel("Dollars spent per vote cast (log scale)", labelpad=12)

    # Shade the close-race zone.
    ax.axvspan(-1, CLOSE * 100, color="#f0efec", zorder=0)
    ax.text(CLOSE * 100 - 0.4, 1.4, f"Within {CLOSE * 100:.0f} pts", ha="right", fontsize=13, color=INK_2)

    # Labels sit just outside each bubble (marker size is an area in points^2).
    for i, row in r[r.state.isin(LABEL)].iterrows():
        gap = np.sqrt(size[i]) / 2 + 5
        left = row.state in ("RI", "WY", "MI")
        ax.annotate(f"{STATE_NAME.get(row.state, row.state)}  ${row.money_per_vote:,.0f}",
                    (row.top_two_margin * 100, row.money_per_vote), xytext=(-gap if left else gap, 0),
                    textcoords="offset points", fontsize=12.5, color=INK, va="center", ha="right" if left else "left",
                    bbox=dict(fc=SURFACE, ec="none", alpha=0.7, pad=0.5))

    # Size key.
    keys = [500_000, 3_000_000, 9_000_000]
    for i, v in enumerate(keys):
        xk = 27 + i * 4.3
        ax.scatter([xk], [600], s=v / r.total_votes.max() * 2600 + 40, color="#9ec5f4", ec=ACCENT, lw=1.2)
        ax.text(xk, 330, f"{v / 1e6:g}M", ha="center", fontsize=12, color=INK_2)
    ax.text(25, 900, "Votes cast", fontsize=12.5, color=INK_2, va="center")

    titles(fig, f"Close Senate races drew about {int(close / safe)}× more",
           "money for every vote cast",
           f"Campaign plus outside spending per vote in each 2026 Senate race. Races decided by under\n"
           f"{CLOSE * 100:.0f} points: median ${close:,.0f} per vote. Races decided by 15+ points: median ${safe:,.0f}.")
    footer(fig, [
        "Money follows races that looked close beforehand; the final margin is a stand-in for that, not the cause.",
        "Unofficial counts (Alaska ~74% reported, so its figure will fall). Campaign money includes primaries, through mid-Oct.",
        f"Rank correlation between margin and money per vote: {rho:.2f}.",
    ], "FEC (campaign + outside spending), civicAPI (votes)")

    out = HERE / "money_per_vote.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  close median {close:.1f}, safe median {safe:.1f}, rho {rho:.2f}")


if __name__ == "__main__":
    main()
