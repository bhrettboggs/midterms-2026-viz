"""When outside money hit 2026 Senate general-election races, week by week.

Reads  data/clean/ie_clean.csv
Writes viz/outside_money_timing/outside_money_timing.png

Mirror bars: spending that helped Democrats above the line, spending that helped Republicans below.
"Helped" = supported that party's candidate or opposed the opponent. Dated by when the ad or mail went out.
"""
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import CLEAN, DEM, FIGSIZE, GRID, INK, INK_2, REP, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
START, ELECTION = "2026-06-01", "2026-11-03"


def helps(party: str, sup_opp: str) -> str:
    p = str(party).upper()
    side = "D" if "DEMOCRAT" in p else ("R" if "REPUBLICAN" in p else "O")
    if sup_opp == "O":
        side = {"D": "R", "R": "D"}.get(side, "O")
    return side


def main() -> None:
    setup()
    ie = pd.read_csv(CLEAN / "ie_clean.csv", low_memory=False)
    g = ie[(ie.can_office == "S") & (ie.ele_type == "G")].copy()
    g["date"] = pd.to_datetime(g.dissem_dt, format="%d-%b-%y", errors="coerce")
    undated = g.date.isna().mean()
    g = g[g.date.between("2026-01-01", ELECTION)]
    g["side"] = [helps(p, s) for p, s in zip(g.cand_pty_aff, g.sup_opp)]
    last30 = g[g.date >= pd.Timestamp(ELECTION) - pd.Timedelta(days=30)].exp_amo.sum() / g.exp_amo.sum()

    w = (g[g.date >= START].set_index("date").groupby("side").exp_amo.resample("W-SUN").sum()
         .unstack(0).fillna(0) / 1e6)
    for col in ("D", "R"):
        if col not in w:
            w[col] = 0

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.10, 0.14, 0.85, 0.65])
    width = 5.2
    ax.bar(w.index - pd.Timedelta(days=3), w.D, width=width, color=DEM, zorder=3)
    ax.bar(w.index - pd.Timedelta(days=3), -w.R, width=width, color=REP, zorder=3)
    ax.axhline(0, color=INK, lw=1, zorder=4)
    top = max(w.D.max(), w.R.max()) * 1.15
    ax.set_ylim(-top, top)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${abs(v):.0f}M"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, labelsize=14)
    ax.set_ylabel("Outside spending per week", labelpad=12)
    ax.text(pd.Timestamp("2026-06-05"), top * 0.85, "Helping Democrats ↑", fontsize=15, color=DEM, weight="semibold")
    ax.text(pd.Timestamp("2026-06-05"), -top * 0.85, "Helping Republicans ↓", fontsize=15, color=REP,
            weight="semibold", va="top")

    cut = pd.Timestamp(ELECTION) - pd.Timedelta(days=30)
    ax.axvspan(cut, pd.Timestamp(ELECTION), color="#f0efec", zorder=0)
    ax.text(cut + pd.Timedelta(days=15), top * 0.97, f"Final 30 days:\n{last30:.0%} of the money",
            ha="center", va="top", fontsize=14, color=INK, weight="semibold")
    ax.axvline(pd.Timestamp(ELECTION), color=INK_2, lw=1, ls=(0, (3, 2)))
    ax.text(pd.Timestamp(ELECTION) + pd.Timedelta(days=1.5), -top * 0.97, "Election\nDay", fontsize=12, color=INK_2,
            va="bottom")
    ax.set_xlim(pd.Timestamp(START) - pd.Timedelta(days=4), pd.Timestamp(ELECTION) + pd.Timedelta(days=10))

    d_tot, r_tot = g[g.side == "D"].exp_amo.sum(), g[g.side == "R"].exp_amo.sum()
    titles(fig, f"{last30:.0%} of outside Senate money landed",
           "in the last 30 days",
           f"Weekly spending by super PACs, parties and other outside groups in 2026 Senate general-election\n"
           f"races. Both sides surged late: ${d_tot / 1e6:,.0f}M helping Democrats, ${r_tot / 1e6:,.0f}M helping "
           f"Republicans (dated spending only).")
    footer(fig, [
        "Dated by when ads or mail went out. “Helping” = supporting that party's candidate or opposing the opponent.",
        f"{undated:.0%} of spending rows have no distribution date and are left out; totals here are lower than the full $1.6B.",
    ], "FEC independent expenditures (junk filings and duplicate reports removed)")

    out = HERE / "outside_money_timing.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  last30 {last30:.3f}, undated {undated:.3f}, D {d_tot/1e6:.0f} R {r_tot/1e6:.0f}")


if __name__ == "__main__":
    main()
