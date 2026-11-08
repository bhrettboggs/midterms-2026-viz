"""How demographic groups have voted, 1996-2026: margin by group in every presidential and midterm election.

Reads  data/clean/exit_poll_groups.csv
Writes viz/demographic_trends/demographic_trends.png

Four panels (gender, race, age, income). Each line is one group's Democratic-minus-Republican margin.
Filled dots = presidential vote, hollow dots = midterm U.S. House vote.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
# Reference categorical palette, in slot order (identity only; the y-axis carries party direction).
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
PANELS = [("Gender", ["Women", "Men"]), ("Race", ["Black", "Hispanic/Latino", "Asian", "White"]),
          ("Age", ["18-29", "65+"]), ("Income", ["Under $50K", "$100K+"])]
LABEL = {"18-29": "Ages 18–29", "65+": "Ages 65+", "Hispanic/Latino": "Latino"}


def fmt(v: float) -> str:
    return "Even" if v == 0 else (f"D+{v:.0f}" if v > 0 else f"R+{-v:.0f}")


def main() -> None:
    setup()
    d = pd.read_csv(CLEAN / "exit_poll_groups.csv")
    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    boxes = [[0.09, 0.47, 0.39, 0.27], [0.59, 0.47, 0.39, 0.27],
             [0.09, 0.115, 0.39, 0.27], [0.59, 0.115, 0.39, 0.27]]
    for (dim, groups), box in zip(PANELS, boxes):
        ax = fig.add_axes(box)
        lims = {"Race": (-35, 100)}.get(dim, (-30, 55))
        for color, g in zip(SLOTS, groups):
            s = d[(d.dimension == dim) & (d.group == g)].sort_values("year")
            ax.plot(s.year, s.margin, color=color, lw=2, zorder=3)
            p, m = s[s.election == "President"], s[s.election != "President"]
            ax.scatter(p.year, p.margin, s=34, color=color, zorder=4)
            ax.scatter(m.year, m.margin, s=34, facecolor=SURFACE, edgecolor=color, lw=1.8, zorder=4)
        # Legend under the panel title: group name + its 2026 margin.
        x0 = 0.0
        for color, g in zip(SLOTS, groups):
            last = d[(d.dimension == dim) & (d.group == g)].sort_values("year").iloc[-1]
            txt = f"{LABEL.get(g, g)} {fmt(last.margin)}"
            ax.text(x0, 1.02, "●", color=color, fontsize=11, transform=ax.transAxes, va="bottom")
            ax.text(x0 + 0.04, 1.02, txt, color=INK, fontsize=11, transform=ax.transAxes, va="bottom")
            x0 += 0.06 + len(txt) * 0.021
        ax.axhline(0, color=INK_2, lw=1, zorder=2)
        ax.set_ylim(*lims)
        ax.set_xlim(1994.5, 2027.2)
        ax.set_xticks([1996, 2004, 2012, 2020, 2026])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt(v)))
        ax.grid(axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(length=0, labelsize=11.5)
        ax.set_title(dim, loc="left", fontsize=16, weight="semibold", pad=26)
        ax.axvspan(2025.4, 2027.2, color="#f5f4f1", zorder=0)

    # Marker key.
    fig.text(0.09, 0.80, "●", fontsize=13, color=INK_2, va="center")
    fig.text(0.107, 0.80, "Presidential vote", fontsize=12.5, color=INK, va="center")
    fig.text(0.26, 0.80, "○", fontsize=14, color=INK_2, va="center", weight="bold")
    fig.text(0.277, 0.80, "Midterm U.S. House vote", fontsize=12.5, color=INK, va="center")
    fig.text(0.49, 0.80, "Margin = Democratic % minus Republican %", fontsize=12, color=MUTED, va="center")

    titles(fig, "30 years of how groups vote",
           "1996–2026, presidential and midterm",
           "National exit polls across 14 elections. The income gap flipped: higher earners now lean Democratic.\n"
           "In 2026 every group shown moved toward Democrats vs. 2024 (a House vote vs. a presidential one).")
    footer(fig, [
        "Exit polls are surveys with sampling error (largest for small groups like Asian voters); 2026 will be re-weighted.",
        "Income is in nominal dollars: $100K in 1996 is worth far more than in 2026. Age 65+ in 2006 uses that poll's 60+ bracket.",
        "President: Roper Center “How Groups Voted”. Midterms: network exit polls via Wikipedia; 2026 checked against ABC News.",
    ], "Roper Center for Public Opinion Research; Wikipedia exit-poll tables")

    out = HERE / "demographic_trends.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
