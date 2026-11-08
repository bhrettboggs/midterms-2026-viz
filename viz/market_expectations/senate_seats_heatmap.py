"""What the prediction market expected: Republican Senate seats after the 2026 midterms.

Reads  data/clean/pm_senate_seats.csv  (daily probability per seat range, sums to 1)
       data/raw/civicapi/races.csv       (race calls, for the result note)
Writes viz/market_expectations/senate_seats_heatmap.png  (1200 x 1500, LinkedIn portrait)

Top panel: monthly average probability per seat range, printed in each cell.
Bottom panel: the daily chance the market gave the range the result landed in.
Both stop on Election Day (Nov 3): the Nov 4 price reflects results coming in, not expectations.
"""
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
CLEAN = HERE.parents[1] / "data" / "clean"
RAW = HERE.parents[1] / "data" / "raw"

# 53 Republican seats before the election minus the 22 Republican-held seats on the ballot
# (20 regular + the Ohio and Florida specials) = 31 Republican seats not up in 2026.
R_HELD_OVER = 31
ELECTION = "2026-11-03"
RESULT_RANGE = "≤47"  # 44-46 Republican seats either way the two uncalled races go


def result_note() -> str:
    """Republican seats called so far, from civicAPI's winner flags, plus the uncalled races."""
    r = pd.read_csv(RAW / "civicapi" / "races.csv", low_memory=False)
    r = r[(r.type == "US Senate") & ~r.election_name.str.contains("Primary|Runoff", case=False) & (r.state != "US")]
    won = r[r.winner == True]  # noqa: E712
    r_called = R_HELD_OVER + won.party.str.contains("Republican").sum()
    uncalled = r.race_id.nunique() - won.race_id.nunique()
    return (f"Result: {r_called} Republican seats called, {uncalled} races still counting → "
            f"final count {r_called}–{r_called + uncalled}")

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
BLUE = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
ACCENT = "#0d366b"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 15, "text.color": INK,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2,
    "xtick.color": INK_2, "ytick.color": INK_2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
})


ROWS = [  # (label, columns summed) - 54+ merged: each of those counts sat near 0% all year
    ("54 or more", ["54", "55", "56", "57+"]), ("53", ["53"]), ("52", ["52"]), ("51", ["51"]),
    ("50", ["50"]), ("49", ["49"]), ("48", ["48"]), ("47 or fewer", ["≤47"]),
]


def main() -> None:
    s = pd.read_csv(CLEAN / "pm_senate_seats.csv", parse_dates=["date"], index_col="date")
    # Drop the market's first two weeks (near-flat placeholder prices at launch) and everything
    # after Election Day.
    s = s.loc["2026-01-01":ELECTION]
    p_result = s[RESULT_RANGE]
    led_since = (s.idxmax(axis=1) != RESULT_RANGE)[::-1].idxmax() + pd.Timedelta(days=1)
    over_half = s.index[p_result > 0.5].min()

    # Monthly averages, one row per seat range (top = most Republican seats).
    grouped = pd.DataFrame({label: s[cols].sum(axis=1) for label, cols in ROWS})
    monthly = grouped.resample("MS").mean()
    col_labels = [f"{d:%b}" for d in monthly.index]
    col_labels[-1] = f"Nov\n1–{s.index[-1].day}"  # Nov 1-3: Election Day is the last day shown
    grid = monthly.T.values  # rows x months

    fig = plt.figure(figsize=(12, 15), dpi=100)
    gs = fig.add_gridspec(2, 1, height_ratios=[2.6, 1], left=0.16, right=0.86, top=0.80, bottom=0.115, hspace=0.22)
    ax = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # --- monthly grid ---------------------------------------------------------------
    cmap = LinearSegmentedColormap.from_list("seq_blue", BLUE)
    nrow, ncol = grid.shape
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=0.6, aspect="auto")
    for i in range(nrow):
        for j in range(ncol):
            v = grid[i, j]
            ax.text(j, i, f"{v:.0%}" if v >= 0.005 else "<1%", ha="center", va="center", fontsize=15,
                    color=SURFACE if v >= 0.33 else (INK if v >= 0.08 else MUTED),
                    weight="semibold" if i == nrow - 1 else "normal")
    # White gaps between cells.
    for i in range(nrow + 1):
        ax.axhline(i - 0.5, color=SURFACE, lw=3)
    for j in range(ncol + 1):
        ax.axvline(j - 0.5, color=SURFACE, lw=3)
    ax.set_xticks(range(ncol))
    ax.set_xticklabels(col_labels, fontsize=15)
    ax.xaxis.tick_top()
    ax.set_yticks(range(nrow))
    ax.set_yticklabels([label for label, _ in ROWS], fontsize=15)
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_ylabel("Republican Senate seats", labelpad=14, fontsize=15)
    # Majority line between 50 and 51.
    y_major = [label for label, _ in ROWS].index("51") + 0.5
    ax.axhline(y_major, color=INK, lw=2)
    ax.text(ncol - 0.35, y_major, "↑ 51+ seats:\nRepublican\nmajority", ha="left", va="center",
            fontsize=12.5, color=INK, linespacing=1.3)
    # Outline the result row.
    ax.add_patch(plt.Rectangle((-0.5, nrow - 1.5), ncol, 1, fill=False, ec=ACCENT, lw=3, zorder=4))
    ax.text(-0.5, nrow - 0.38, "↑ where the result landed", ha="left", va="top", fontsize=12.5,
            color=ACCENT, weight="semibold", transform=ax.transData)

    # --- daily chance of the eventual answer ----------------------------------------
    ax2.fill_between(s.index, p_result, color="#cde2fb", lw=0)
    ax2.plot(s.index, p_result, color=ACCENT, lw=2.5)
    ax2.axhline(0.5, color=MUTED, lw=1, ls=(0, (4, 3)))
    ax2.text(s.index[2], 0.52, "50%", color=INK_2, fontsize=13, va="bottom")
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0, 0.5, 1])
    ax2.set_yticklabels(["0%", "50%", "100%"])
    ax2.grid(axis="y", color=GRID, lw=1)
    ax2.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax2.spines[side].set_visible(False)
    ax2.tick_params(length=0, labelsize=14)
    ax2.set_title("Daily chance the market gave “47 or fewer”", loc="left", fontsize=16, weight="semibold", pad=12)
    last = s.index[-1]
    ax2.annotate(f"{p_result.iloc[-1]:.0%} on Election Day", (last, p_result.iloc[-1]), xytext=(-12, 0),
                 textcoords="offset points", ha="right", va="center", fontsize=13.5, color=INK, weight="semibold")
    ax2.axvline(led_since, color=MUTED, lw=1)
    ax2.annotate(f"Became the market's top pick\non {led_since:%b %-d}", (led_since, 0.92),
                 xytext=(8, 0), textcoords="offset points", fontsize=13.5, color=INK_2, va="top")
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # --- titles and footer ----------------------------------------------------------
    fig.text(0.04, 0.955, "The market's top pick from March was right —", fontsize=30, weight="bold")
    fig.text(0.04, 0.925, "but it stayed under 50% until Election Day", fontsize=30, weight="bold")
    fig.text(0.04, 0.89, "Polymarket's average monthly probability for how many Senate seats Republicans would hold\n"
                         "after the 2026 midterms. Darker = more likely.", fontsize=16, color=INK_2, va="top",
             linespacing=1.4)
    fig.text(0.04, 0.076, result_note() + f". “47 or fewer” first topped 50% on {over_half:%b %-d} (Election Day).",
             fontsize=12.5, color=INK_2)
    fig.text(0.04, 0.058, "Prices run through Election Day only; the next day, as results came in, the range jumped to 70%.",
             fontsize=12.5, color=INK_2)
    fig.text(0.04, 0.040, "Note: “47 or fewer” is open-ended, so it covers more outcomes than the single-seat rows.",
             fontsize=12.5, color=INK_2)
    fig.text(0.04, 0.020, "Data: Polymarket public API (daily prices, rescaled to sum to 100%); race calls via civicAPI. "
                          "Chart: Bhrett Boggs", fontsize=12.5, color=MUTED)

    out = HERE / "senate_seats_heatmap.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  (led since {led_since:%Y-%m-%d}, over 50% from {over_half:%Y-%m-%d})")


if __name__ == "__main__":
    main()
