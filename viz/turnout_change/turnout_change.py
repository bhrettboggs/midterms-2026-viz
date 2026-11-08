"""Turnout change from the 2022 midterm to 2026, state by state.

Reads  data/clean/turnout_states_2022_2026.csv
Writes viz/turnout_change/turnout_change.png

One row per state: ring = 2022 turnout, dot = 2026 early estimate, sorted by change.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
DOWN = "#b04a3d"


def main() -> None:
    setup()
    t = pd.read_csv(CLEAN / "turnout_states_2022_2026.csv").dropna().sort_values("change_pts")
    up, down = (t.change_pts > 0).sum(), (t.change_pts < 0).sum()
    top, bot = t.iloc[-1], t.iloc[0]

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.08, 0.10, 0.84, 0.685])
    for i, r in enumerate(t.itertuples()):
        a, b = r.turnout_2022 * 100, r.turnout_2026 * 100
        col = ACCENT if b >= a else DOWN
        ax.annotate("", (b, i), (a, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, mutation_scale=11,
                                                        shrinkA=4, shrinkB=2))
        ax.scatter([a], [i], s=28, facecolor=SURFACE, edgecolor=MUTED, lw=1.2, zorder=3)
        ax.text(max(a, b) + 0.8, i, f"{r.change_pts:+.1f}".replace("-0.0", "0.0").replace("+0.0", "0.0"), va="center", fontsize=10.5,
                color=col if abs(r.change_pts) >= 5 else INK_2, weight="semibold" if abs(r.change_pts) >= 5 else None)
    ax.set_yticks(range(len(t)))
    ax.set_yticklabels(t.state, fontsize=10.5)
    ax.set_ylim(-0.8, len(t) - 0.2)
    ax.set_xlim(28, 72)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.xaxis.tick_top()
    ax.grid(axis="x", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, labelsize=12.5)

    fig.text(0.08, 0.835, "○", color=MUTED, fontsize=15, va="center", weight="bold")
    fig.text(0.10, 0.835, "2022", fontsize=13, color=INK, va="center")
    fig.text(0.16, 0.835, "→", color=ACCENT, fontsize=16, va="center", weight="bold")
    fig.text(0.185, 0.835, "2026, up", fontsize=13, color=INK, va="center")
    fig.text(0.28, 0.835, "→", color=DOWN, fontsize=16, va="center", weight="bold")
    fig.text(0.305, 0.835, "2026, down", fontsize=13, color=INK, va="center")
    fig.text(0.43, 0.835, "share of eligible voters who voted; number = change in points", fontsize=12, color=MUTED,
             va="center")

    titles(fig, f"Turnout rose in {up} states and fell in {down}",
           f"compared with the 2022 midterm",
           f"{top.state} gained the most ({top.change_pts:+.0f} points), {bot.state} lost the most "
           f"({bot.change_pts:+.0f}). What's on the ballot matters: Mississippi had no\nSenate or governor race in 2022, "
           "and a Senate race within 1 point this year.")
    footer(fig, [
        "2026 figures are initial estimates (UF v0.2) and will be revised as counting finishes.",
    ], "Michael McDonald, UF Election Lab (VEP turnout, 2022 v1.2 and 2026 v0.2)")

    out = HERE / "turnout_change.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  up {up} down {down}")


if __name__ == "__main__":
    main()
