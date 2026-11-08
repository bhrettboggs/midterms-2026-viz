"""Betting odds vs outside money in the months before the 2026 election.

Reads  data/raw/polymarket/daily.csv      ("Which party will win the Senate in 2026?")
       data/clean/ie_senate_general.csv   outside spending in Senate general-election races, by side
Writes viz/money_vs_odds/money_vs_odds.png

Top: Polymarket's daily chance that Democrats win the Senate. Bottom: weekly outside spending by side.
Two panels on one time axis (no second y-axis). Both stop on Election Day: the Nov 4 price reflects
results coming in, not expectations.
"""
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import CLEAN, DEM, FIGSIZE, GRID, INK, INK_2, MUTED, REP, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"
START, END = "2026-06-01", "2026-11-03"


def main() -> None:
    setup()
    p = pd.read_csv(RAW / "polymarket" / "daily.csv")
    s = p[p.event.str.startswith("Which party will win the Senate")].pivot_table(
        index="date", columns="outcome_label", values="price", aggfunc="last")
    s.index = pd.to_datetime(s.index)
    s = s.asfreq("D").ffill()
    odds = (s.div(s.sum(axis=1), axis=0)["Democratic Party"] * 100).loc[START:END]

    g = pd.read_csv(CLEAN / "ie_senate_general.csv", parse_dates=["date"])
    g = g[g.date.between(START, END)]
    w = g.set_index("date").groupby("side").exp_amo.resample("W-SUN").sum().unstack(0).fillna(0) / 1e6
    w = w.reindex(columns=["D", "R"], fill_value=0)
    w = w[w.index <= pd.Timestamp(END)]  # drop the partial week (Nov 1-3 only)
    d_ahead = w[(w.D > w.R) & (w.index >= "2026-09-01")].index.min()
    # The day the odds went above 50% for good (they had also been above 50% briefly in spring).
    crossed = odds[odds <= 50].index.max() + pd.Timedelta(days=1)
    weekly_odds = odds.resample("W-SUN").mean().reindex(w.index)
    share = w.D / (w.D + w.R)
    rho = spearmanr(share[w.D + w.R > 5], weekly_odds[w.D + w.R > 5]).statistic

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax1 = fig.add_axes([0.10, 0.51, 0.85, 0.25])
    ax2 = fig.add_axes([0.10, 0.14, 0.85, 0.30], sharex=ax1)

    ax1.plot(odds.index, odds, color=INK, lw=2.5)
    ax1.axhline(50, color=MUTED, lw=1, ls=(0, (4, 3)))
    ax1.set_ylim(30, 100)
    ax1.set_yticks([30, 50, 70, 90])
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax1.set_title("Market's chance Democrats win the Senate", loc="left", fontsize=16, weight="semibold", pad=10)
    ax1.annotate(f"{odds.iloc[0]:.0f}% on {odds.index[0]:%b %-d}", (odds.index[0], odds.iloc[0]), xytext=(0, -28),
                 textcoords="offset points", fontsize=13, color=INK_2)
    ax1.annotate(f"{odds.iloc[-1]:.0f}% on Election Day\n(before results)", (odds.index[-1], odds.iloc[-1]),
                 xytext=(-8, 6), textcoords="offset points", ha="right", fontsize=13.5, weight="semibold", color=INK)
    ax1.annotate(f"Above 50% for good\nfrom {crossed:%b %-d}", (crossed, 50), xytext=(-20, 32), textcoords="offset points",
                 fontsize=13, color=INK, ha="right", arrowprops=dict(arrowstyle="-", color=INK_2, lw=1))

    ax2.bar(w.index - pd.Timedelta(days=3), w.D, width=5.2, color=DEM, zorder=3)
    ax2.bar(w.index - pd.Timedelta(days=3), -w.R, width=5.2, color=REP, zorder=3)
    ax2.axhline(0, color=INK, lw=1, zorder=4)
    top = max(w.D.max(), w.R.max()) * 1.2
    ax2.set_ylim(-top, top)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${abs(v):.0f}M"))
    ax2.set_title("Outside spending per week in Senate races", loc="left", fontsize=16, weight="semibold", pad=10)
    ax2.text(pd.Timestamp("2026-06-04"), top * 0.8, "Helping Democrats ↑", fontsize=13.5, color=DEM, weight="semibold")
    ax2.text(pd.Timestamp("2026-06-04"), -top * 0.8, "Helping Republicans ↓", fontsize=13.5, color=REP,
             weight="semibold", va="top")
    ax2.annotate(f"Democratic-side money first\nout-spends Republican side:\nweek of {d_ahead - pd.Timedelta(days=6):%b %-d}",
                 (d_ahead - pd.Timedelta(days=3), w.loc[d_ahead, "D"]), xytext=(-150, 20), textcoords="offset points",
                 fontsize=13, color=INK, arrowprops=dict(arrowstyle="-", color=INK_2, lw=1))

    for ax in (ax1, ax2):
        ax.axvline(crossed, color=GRID, lw=1.5, zorder=1)
        ax.axvline(d_ahead - pd.Timedelta(days=3), color=GRID, lw=1.5, zorder=1)
        ax.grid(axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(length=0, labelsize=13.5)
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax2.set_xlim(pd.Timestamp(START) - pd.Timedelta(days=4), pd.Timestamp(END) + pd.Timedelta(days=4))

    lag = (d_ahead - pd.Timedelta(days=6) - crossed).days
    titles(fig, "The odds moved first.",
           "Democratic-side money caught up later.",
           f"Polymarket's odds of a Democratic Senate stayed above 50% from {crossed:%b %-d} on. Outside money helping\n"
           f"Democrats didn't out-spend the Republican side in a week until {abs(lag)} days {'later' if lag > 0 else 'earlier'}. Week to week the two\n"
           f"move together only loosely (rank correlation {rho:.2f}): this is timing, not proof that either caused the other.")
    footer(fig, [
        "Odds: daily price of the Democratic outcome, rescaled with the other outcomes to sum to 100%, through Election Day",
        "(the market jumped to 90% on Nov 4 as results came in). Money: FEC independent expenditures in Senate general-election",
        "races, dated by distribution; the partial week of Nov 1–3 and the 0.8% of dollars with no date are left out.",
    ], "Polymarket public API, FEC")

    out = HERE / "money_vs_odds.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  crossed {crossed:%Y-%m-%d}, D ahead week ending {d_ahead:%Y-%m-%d}, lag {lag}, rho {rho:.2f}")


if __name__ == "__main__":
    main()
