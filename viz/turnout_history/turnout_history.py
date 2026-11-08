"""236 years of U.S. midterm turnout, with 2026 in context.

Reads  data/clean/turnout_national_midterms.csv     midterm turnout 1790-2022 + 2026 estimate
       data/raw/uf/US_VEP_Turnout_Rates_v1.4.csv     presidential turnout, for context
Writes viz/turnout_history/turnout_history.png

Turnout = ballots counted / voting-eligible population (Michael McDonald, UF Election Lab).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"

# Context marks: changes to who could vote, which move the denominator.
ERAS = [(1920, "Women's suffrage\n(19th Amendment)"), (1965, "1965–71: Voting Rights Act,\nvoting age lowered to 18")]


def main() -> None:
    setup()
    mid = pd.read_csv(CLEAN / "turnout_national_midterms.csv")
    pres = pd.read_csv(RAW / "uf" / "US_VEP_Turnout_Rates_v1.4.csv")[["YEAR", "TURNOUT_RATE_PRES"]].dropna()
    pres = pres[pres.TURNOUT_RATE_PRES > 0]
    est = mid[mid.is_estimate].iloc[0]
    hist = mid[~mid.is_estimate]
    # The most recent midterm before 2018 that beat 2026 (1914, at 50.4%). "Since" that year means
    # after it: among midterms from 1918 on, only 2018 was higher.
    last_higher = hist[(hist.turnout > est.turnout) & (hist.year < 2018)].year.max()
    higher_after = hist[(hist.year > last_higher) & (hist.turnout > est.turnout)]
    assert higher_after.year.tolist() == [2018], higher_after.year.tolist()
    first_since = last_higher + 4

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.09, 0.14, 0.86, 0.66])
    ax.plot(pres.YEAR, pres.TURNOUT_RATE_PRES * 100, color=MUTED, lw=1.5, alpha=0.7, zorder=2)
    ax.plot(hist.year, hist.turnout * 100, color=ACCENT, lw=2.5, zorder=3)
    ax.plot([hist.year.iloc[-1], est.year], [hist.turnout.iloc[-1] * 100, est.turnout * 100], color=ACCENT,
            lw=2.5, ls=(0, (2, 2)), zorder=3)
    ax.scatter([est.year], [est.turnout * 100], s=110, color=ACCENT, ec=SURFACE, lw=2, zorder=4)

    ax.annotate(f"2026: {est.turnout:.1%}\n(early estimate)", (est.year, est.turnout * 100), xytext=(12, 0),
                textcoords="offset points", ha="left", va="center", fontsize=15, weight="semibold", color=INK)
    r18 = hist[hist.year == 2018].iloc[0]
    ax.annotate(f"2018: {r18.turnout:.1%}", (2018, r18.turnout * 100), xytext=(-50, 40), textcoords="offset points",
                ha="center", fontsize=13.5, color=INK_2, arrowprops=dict(arrowstyle="-", color=INK_2, lw=1))
    low14 = hist[hist.year == 2014].iloc[0]
    r14 = hist[hist.year == last_higher].iloc[0]
    ax.annotate(f"2014: {low14.turnout:.1%}", (2014, low14.turnout * 100), xytext=(-40, -34), textcoords="offset points",
                ha="center", fontsize=13.5, color=INK_2, arrowprops=dict(arrowstyle="-", color=INK_2, lw=1))
    ax.annotate(f"{last_higher}: {r14.turnout:.1%}", (last_higher, r14.turnout * 100), xytext=(-62, 40),
                textcoords="offset points", ha="center", fontsize=13.5, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=INK_2, lw=1))
    ax.text(1935, 70, "Presidential years", fontsize=13.5, color=MUTED)
    ax.text(1793, 63, "Midterm years", fontsize=14, color=ACCENT, weight="semibold")

    for yr, lab in ERAS:
        ax.axvline(yr, color=GRID, lw=1.2, zorder=1)
        ax.text(yr + 1.5, 4, lab, fontsize=11.5, color=INK_2, va="bottom")

    ax.set_xlim(1786, 2062)
    ax.set_ylim(0, 90)
    ax.set_xticks([1800, 1850, 1900, 1950, 2000])
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, labelsize=14)
    ax.set_ylabel("Share of eligible voters who voted", labelpad=12)

    titles(fig, "2026 had the second-highest midterm",
           f"turnout in more than a century",
           f"Turnout in every U.S. midterm since 1790, as a share of eligible voters. The 2026 early estimate,\n"
           f"{est.turnout:.1%}, beats every midterm since {first_since} except 2018 ({r18.turnout:.1%}); "
           f"{last_higher} was the last one higher ({r14.turnout:.1%}).")
    footer(fig, [
        "2026 is an initial estimate (UF v0.2, Nov 2026) and will be revised as states finish counting.",
        "Eligible population changes over time (e.g. suffrage expansions), so very early figures cover far fewer people.",
    ], "Michael McDonald, UF Election Lab (national VEP turnout 1789–2024; 2026 estimate v0.2)")

    out = HERE / "turnout_history.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  2026 {est.turnout:.3f}; last midterm before 2018 that was higher: {last_higher}; "
          f"higher since then: {higher_after.year.tolist()}")


if __name__ == "__main__":
    main()
