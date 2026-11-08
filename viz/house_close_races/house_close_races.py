"""Every contested 2026 U.S. House race as a dot, placed by its current margin.

Reads  data/raw/civicapi/races.csv
Writes viz/house_close_races/house_close_races.png

A beeswarm: dots are stacked so they don't overlap; y = margin (D+ up, R+ down).
Races without both a Democrat and a Republican (uncontested, or two candidates of one party) are left out.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from common import party_bucket  # noqa: E402
from style import ACCENT, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"
CLOSE = 2.0   # points


def swarm(x: np.ndarray, d: float) -> np.ndarray:
    """1-D beeswarm: for each point (in x order) take the nearest free slot above or below the axis."""
    y = np.zeros_like(x)
    placed: list[tuple[float, float]] = []
    for i in np.argsort(x):
        k = 0
        while True:
            cand = 0.0 if k == 0 else ((k + 1) // 2) * d * (1 if k % 2 else -1)
            if all((x[i] - px) ** 2 + (cand - py) ** 2 >= (d * 0.98) ** 2 for px, py in placed if abs(x[i] - px) < d):
                y[i] = cand
                placed.append((x[i], cand))
                break
            k += 1
    return y


def main() -> None:
    setup()
    c = pd.read_csv(RAW / "civicapi" / "races.csv", low_memory=False)
    h = c[(c.type == "House of Representatives") & ~c.election_type.str.contains("Primary|Runoff", case=False, na=False)]
    h = h.assign(b=h.party.map(party_bucket))
    p = h.pivot_table(index="race_id", columns="b", values="votes", aggfunc="sum", fill_value=0)
    meta = h.groupby("race_id").agg(name=("election_name", "first"), pr=("percent_reporting", "max"))
    d = p.join(meta)
    d["tot"] = d[["D", "R", "O"]].sum(axis=1)
    d = d[(d.D > 0) & (d.R > 0)].copy()
    d["margin"] = (d.D - d.R) / d.tot * 100
    n_out = 435 - len(d)
    close = d[d.margin.abs() < CLOSE]
    within1 = (d.margin.abs() < 1).sum()

    m = d.margin.values
    dot = 1.75  # dot diameter in margin points
    x = swarm(m, dot)  # sideways offsets; margin runs up the page

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.07, 0.10, 0.50, 0.70])
    ax.axhspan(-CLOSE, CLOSE, color="#fbf0d9", zorder=0)
    is_close = np.abs(m) < CLOSE
    ax.scatter(x[~is_close], m[~is_close], s=52, color="#9ec5f4", ec=SURFACE, lw=0.5, zorder=2)
    ax.scatter(x[is_close], m[is_close], s=56, color=ACCENT, ec=SURFACE, lw=0.5, zorder=3)
    ax.axhline(0, color=INK_2, lw=1, zorder=1)
    ax.set_aspect("equal")
    half = np.abs(x).max() + 2
    ax.set_xlim(-half, half)
    ax.set_ylim(m.min() - 3, m.max() + 3)
    ax.set_xticks([])
    ticks = [-50, -25, 0, 25, 50, 75]
    ax.set_yticks(ticks)
    ax.set_yticklabels(["R+50", "R+25", "even", "D+25", "D+50", "D+75"])
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, labelsize=13)
    ax.text(half, m.max(), "Democrat\nahead ↑", fontsize=13, color=INK_2, ha="right", va="top")
    ax.text(half, m.min(), "Republican\nahead ↓", fontsize=13, color=INK_2, ha="right", va="bottom")

    # Right panel: the races within 1 point, closest first.
    tight = d[d.margin.abs() < 1].assign(a=lambda t: t.margin.abs()).sort_values("a")
    fig.text(0.60, 0.565, f"{len(close)} races within {CLOSE:.0f} points", fontsize=17, weight="semibold", color=INK)
    fig.text(0.60, 0.540, f"The {within1} closest, within 1 point:", fontsize=13.5, color=INK_2)
    for j, (n, mg, pr) in enumerate(zip(tight.name, tight.margin, tight.pr)):
        yy = 0.510 - j * 0.0235
        fig.text(0.60, yy, n.replace(" US House ", " "), fontsize=13, color=INK)
        fig.text(0.86, yy, f"{'D' if mg > 0 else 'R'}+{abs(mg):.1f}", fontsize=13, color=INK, ha="right",
                 weight="semibold")
        fig.text(0.965, yy, f"{pr:.0f}% in", fontsize=12, color=INK_2, ha="right")

    titles(fig, f"{len(close)} House races are within {CLOSE:.0f} points",
           "with votes still being counted",
           f"Every contested 2026 U.S. House race, placed by its current margin. Each dot is one district.\n"
           f"{len(d)} races shown; {n_out} without both a Democrat and a Republican are left out.")
    footer(fig, [
        "Unofficial: many districts are under 95% counted, so close margins can still flip. ",
    ], "civicAPI (2026 U.S. House results)")

    out = HERE / "house_close_races.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  shown {len(d)}, close {len(close)}, within1 {within1}")


if __name__ == "__main__":
    main()
