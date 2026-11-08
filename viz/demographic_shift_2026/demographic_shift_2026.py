"""Which groups moved most in 2026? Each group's margin in the 2022 midterm, 2024 presidential and 2026 midterm.

Reads  data/clean/exit_poll_groups.csv
Writes viz/demographic_shift_2026/demographic_shift_2026.png

The arrow runs 2022 -> 2026 (midterm to midterm, the like-for-like comparison). The gray dot is 2024's presidential vote.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
ORDER = [("Age", "18-29"), ("Age", "65+"), ("Gender", "Women"), ("Gender", "Men"), ("Race", "Black"),
         ("Race", "Hispanic/Latino"), ("Race", "Asian"), ("Race", "White"), ("Income", "Under $50K"),
         ("Income", "$100K+")]
NOUN = {"Asian": "Asian voters", "18-29": "young voters", "White": "white voters", "Men": "men", "$100K+": "higher earners"}
LABEL = {"18-29": "Ages 18–29", "65+": "Ages 65+", "Hispanic/Latino": "Latino", "Under $50K": "Income under $50K",
         "$100K+": "Income $100K+"}


def fmt(v: float) -> str:
    return "Even" if round(v) == 0 else (f"D+{v:.0f}" if v > 0 else f"R+{-v:.0f}")


def main() -> None:
    setup()
    d = pd.read_csv(CLEAN / "exit_poll_groups.csv")
    w = d.pivot_table(index=["dimension", "group"], columns="year", values="margin")
    rows = [(dim, g, w.loc[(dim, g), 2022], w.loc[(dim, g), 2024], w.loc[(dim, g), 2026]) for dim, g in ORDER]
    t = pd.DataFrame(rows, columns=["dim", "group", "m22", "m24", "m26"])
    t["chg"] = t.m26 - t.m22
    top = t.sort_values("chg", ascending=False).iloc[0]

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.21, 0.10, 0.66, 0.68])
    y = list(range(len(t)))[::-1]
    prev = None
    for yi, r in zip(y, t.itertuples()):
        if r.dim != prev and prev is not None:
            ax.axhline(yi + 0.5, color=GRID, lw=1)
        prev = r.dim
        ax.annotate("", (r.m26, yi), (r.m22, yi), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2,
                                                                   mutation_scale=14, shrinkA=6, shrinkB=4))
        ax.scatter([r.m22], [yi], s=70, facecolor=SURFACE, edgecolor=ACCENT, lw=2, zorder=4)
        # 2024 sits just above the row so it stays visible when it equals 2022 or 2026 (Black, Women, 65+).
        ax.scatter([r.m24], [yi + 0.24], s=55, color=MUTED, zorder=3)
        ax.scatter([r.m26], [yi], s=80, color=ACCENT, zorder=5)
        ax.text(102, yi, f"{r.chg:+.0f}", va="center", ha="right", fontsize=14, weight="semibold", color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([LABEL.get(g, g) for g in t.group], fontsize=14)
    ax.axvline(0, color=INK_2, lw=1)
    ax.set_xlim(-30, 104)
    ax.set_ylim(-0.7, len(t) - 0.3)
    ax.set_xticks([-20, 0, 20, 40, 60, 80])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt(v)))
    ax.xaxis.tick_top()
    ax.grid(axis="x", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, labelsize=13)
    ax.text(102, len(t) - 0.15, "Change\nsince 2022", ha="right", va="bottom", fontsize=12, color=INK_2)

    fig.text(0.21, 0.815, "○", fontsize=15, color=ACCENT, va="center", weight="bold")
    fig.text(0.23, 0.815, "2022 midterm", fontsize=13, color=INK, va="center")
    fig.text(0.37, 0.815, "●", fontsize=13, color=MUTED, va="center")
    fig.text(0.39, 0.815, "2024 presidential (above the line)", fontsize=13, color=INK, va="center")
    fig.text(0.665, 0.815, "●", fontsize=13, color=ACCENT, va="center")
    fig.text(0.685, 0.815, "2026 midterm", fontsize=13, color=INK, va="center")

    titles(fig, "Every group moved toward Democrats",
           f"in 2026 — {NOUN.get(top.group, top.group)} the most",
           "Democratic-minus-Republican margin in national election-day surveys. Arrows compare the 2026\n"
           "midterm with the 2022 midterm (like for like); the gray dot is the 2024 presidential vote.")
    footer(fig, [
        "Surveys: subgroup margins carry several points of error (more for Asian voters), and 2026 will be re-weighted to final results.",
        "2026 is The Voter Poll by SSRS, which replaced the Edison exit poll used in 2022 and 2024, so some of the change is method.",
        "Income brackets are nominal dollars. Margins are for U.S. House (midterms) and president (2024).",
    ], "Edison/NEP exit poll via Wikipedia (2022); Roper Center (2024); The Voter Poll by SSRS via ABC News (2026)")

    out = HERE / "demographic_shift_2026.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}\n{t.round(0).to_string()}")


if __name__ == "__main__":
    main()
