"""Same office, same counties, four years apart: every county's 2022 -> 2026 governor-race swing.

Reads  data/clean/county_shift_2022_2026.csv   (2022 MEDSL county returns joined to 2026 civicAPI returns)
Writes viz/gov_swing_2022_2026/gov_swing_2022_2026.png

One row per state with a governor race in both 2022 and 2026; one dot per county (area = 2026 votes),
x = change in the Democratic-minus-Republican margin. The bar is the state's vote-weighted shift.
This is the like-for-like comparison the presidential-baseline charts can't give: midterm vs midterm,
governor vs governor.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
MIN_REPORTING = 60  # counties below this are left undrawn (a 24%-counted county showed a fake +64)
NAMES = {"AL": "Alabama", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "FL": "Florida",
         "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IA": "Iowa", "KS": "Kansas", "ME": "Maine",
         "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "NE": "Nebraska", "NV": "Nevada",
         "NH": "New Hampshire", "NM": "New Mexico", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
         "PA": "Pennsylvania", "SC": "South Carolina", "SD": "South Dakota", "TX": "Texas", "VT": "Vermont",
         "WI": "Wisconsin"}


def main() -> None:
    setup()
    m = pd.read_csv(CLEAN / "county_shift_2022_2026.csv", dtype={"county_fips": str})
    g = m[m.office == "GOV"].copy()
    g["sh"] = g.shift_2022_2026 * 100
    n_all = len(g)
    drawn = g[g.pct_reporting_2026 >= MIN_REPORTING].copy()
    state = (drawn.groupby("state").apply(lambda d: (d.sh * d.votes_2026).sum() / d.votes_2026.sum(), include_groups=False)
             .sort_values())
    national = (drawn.sh * drawn.votes_2026).sum() / drawn.votes_2026.sum()
    share_up = (drawn.sh > 0).mean()

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.17, 0.125, 0.74, 0.66])
    order = {s: i for i, s in enumerate(state.index)}
    rng = np.random.default_rng(7)
    drawn["y"] = drawn.state.map(order) + rng.uniform(-0.3, 0.3, len(drawn))
    size = drawn.votes_2026 / drawn.votes_2026.max() * 900 + 6
    for i in range(0, len(state), 2):
        ax.axhspan(i - 0.5, i + 0.5, color="#f5f4f1", zorder=0)
    ax.axvline(0, color=INK_2, lw=1.2, zorder=2)
    ax.axvline(national, color=MUTED, lw=1.2, ls=(0, (4, 3)), zorder=2)
    ax.scatter(drawn.sh, drawn.y, s=size, color="#9ec5f4", ec=ACCENT, lw=0.4, alpha=0.55, zorder=3)
    for s, v in state.items():
        ax.plot([v, v], [order[s] - 0.42, order[s] + 0.42], color=INK, lw=3, zorder=5, solid_capstyle="butt")
        label = "0" if round(v) == 0 else f"{v:+.0f}".replace("-", "−")
        ax.text(52, order[s], label, va="center", ha="right", fontsize=12.5, color=INK, weight="semibold")
    ax.set_yticks(range(len(state)))
    ax.set_yticklabels([NAMES.get(s, s) for s in state.index], fontsize=12.5)
    ax.set_ylim(-1.1, len(state) + 1.0)
    ax.set_xlim(-27, 53)
    ax.set_xticks([-20, -10, 0, 10, 20, 30, 40])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: "no change" if v == 0 else f"{v:+.0f}".replace("-", "−")))
    ax.grid(axis="x", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, labelsize=12.5)
    ax.text(52, len(state) + 0.95, "state shift\n(vote-weighted)", ha="right", va="top", fontsize=11.5, color=INK_2,
            linespacing=1.2)
    ax.text(national + 0.8, -1.05, f"all {len(state)} states: {national:+.0f}", fontsize=12, color=INK_2, va="bottom")
    ax.text(-1.2, len(state) + 0.75, "← moved toward Republicans", fontsize=12, color=INK_2, va="top", ha="right")
    ax.text(1.2, len(state) + 0.75, "moved toward Democrats →", fontsize=12, color=INK_2, va="top", ha="left")

    # Size key, in the empty top-left corner (the top rows have no county left of zero).
    ky = len(state) - 3
    for i, v in enumerate((10_000, 100_000, 1_000_000)):
        xk = -24 + i * 5.5
        ax.scatter([xk], [ky], s=v / drawn.votes_2026.max() * 900 + 6, color="#9ec5f4", ec=ACCENT, lw=0.4)
        ax.text(xk, ky - 1.0, f"{v // 1000:,}K" if v < 1e6 else "1M", ha="center", va="top", fontsize=11, color=INK_2)
    ax.text(-26, ky + 1.3, "2026 votes", fontsize=11.5, color=INK_2, ha="left")

    titles(fig, "Same office, same counties, four years apart:",
           f"governor races moved {national:.0f} points toward Democrats",
           f"Each dot is a county's change in Democratic-minus-Republican margin from its 2022 governor race to its\n"
           f"2026 governor race ({len(drawn):,} counties in {len(state)} states), sized by 2026 votes. {share_up:.0%} of counties "
           f"moved toward\nDemocrats. Midterm against midterm, governor against governor — not a presidential baseline.")
    footer(fig, [
        f"Unofficial 2026 counts; {n_all - len(drawn)} counties under {MIN_REPORTING}% counted are not drawn. Candidates still matter: open seats",
        "and term-limited incumbents move margins too. Only races where a Democrat and a Republican finished top two in both years.",
        "No like-for-like pair for Alaska (no county data), Connecticut (new county units), Tennessee (2022 file incomplete), RI, WY.",
    ], "MIT Election Data and Science Lab (2022 precinct returns), civicAPI (2026 county results)")

    out = HERE / "gov_swing_2022_2026.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  national {national:.2f}, share up {share_up:.3f}, drawn {len(drawn)} of {n_all}")


if __name__ == "__main__":
    main()
