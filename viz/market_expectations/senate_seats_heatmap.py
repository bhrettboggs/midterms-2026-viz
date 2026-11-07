"""What the prediction market expected: Republican Senate seats after the 2026 midterms.

Reads  data/clean/pm_senate_seats.csv  (daily probability per seat range, sums to 1)
Writes viz/market_expectations/senate_seats_heatmap.png  (1200 x 1500, LinkedIn portrait)

Top panel: one row per seat range, one column per day, darker = more likely.
Bottom panel: the chance the market gave the range the result landed in.
"""
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
CLEAN = HERE.parents[1] / "data" / "clean"

# Result (as of Nov 7, 2026): 44 Republican seats called, 2 races uncalled,
# so the final count is 44-46 -> the "47 or fewer" range either way.
RESULT_RANGE = "≤47"
RESULT_NOTE = "Result: 44 Republican seats called, 2 races still counting → final count 44–46"

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


def main() -> None:
    s = pd.read_csv(CLEAN / "pm_senate_seats.csv", parse_dates=["date"], index_col="date")
    # The first two weeks are the market opening at near-flat placeholder prices.
    s = s.loc["2026-01-01":]
    p_result = s[RESULT_RANGE]
    # Heatmap shows a 7-day average to calm thin-market noise; the line and the dates use raw daily prices.
    smooth = s.rolling(7, min_periods=1).mean()
    led_since = (s.idxmax(axis=1) != RESULT_RANGE)[::-1].idxmax() + pd.Timedelta(days=1)
    over_half = s.index[p_result > 0.5].min()

    fig = plt.figure(figsize=(12, 15), dpi=100)
    gs = fig.add_gridspec(2, 2, height_ratios=[3.1, 1], width_ratios=[40, 1],
                          left=0.14, right=0.9, top=0.80, bottom=0.10, hspace=0.18, wspace=0.03)
    ax = fig.add_subplot(gs[0, 0])
    cax = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax)

    # --- heatmap -----------------------------------------------------------------
    cmap = LinearSegmentedColormap.from_list("seq_blue", BLUE)
    x = mdates.date2num(s.index.to_pydatetime())
    edges_x = list(x - 0.5) + [x[-1] + 0.5]
    rows = list(s.columns)  # ≤47 ... 57+, bottom to top
    mesh = ax.pcolormesh(edges_x, range(len(rows) + 1), smooth.T.values, cmap=cmap, vmin=0, vmax=0.6,
                         shading="flat", rasterized=True)
    ax.set_yticks([i + 0.5 for i in range(len(rows))])
    ax.set_yticklabels(["47 or fewer" if r == "≤47" else ("57 or more" if r == "57+" else r) for r in rows])
    ax.set_ylabel("Republican Senate seats", labelpad=12)
    ax.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    # 50 seats: the line between majority and minority (VP breaks a 50-50 tie).
    y50 = rows.index("50") + 1
    ax.axhline(y50, color=SURFACE, lw=2)
    ax.text(x[3], y50 + 0.12, "51+ = Republican majority", color=SURFACE, fontsize=13, va="bottom", weight="medium")
    # Outline the row the result landed in.
    ax.add_patch(plt.Rectangle((edges_x[0], 0.04), edges_x[-1] - edges_x[0], 0.92, fill=False,
                               ec=ACCENT, lw=2.5, zorder=3))

    cb = fig.colorbar(mesh, cax=cax, ticks=[0, 0.2, 0.4, 0.6])
    cb.ax.set_yticklabels(["0%", "20%", "40%", "60%+"])
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=13)
    cb.set_label("Market probability", color=INK_2, labelpad=10)

    # --- probability of the eventual answer ---------------------------------------
    ax2.fill_between(s.index, p_result, color="#cde2fb", lw=0)
    ax2.plot(s.index, p_result, color=ACCENT, lw=2)
    ax2.axhline(0.5, color=MUTED, lw=1, ls=(0, (4, 3)))
    ax2.text(s.index[3], 0.52, "50%", color=INK_2, fontsize=13, va="bottom")
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax2.set_yticklabels(["0%", "", "50%", "", "100%"])
    ax2.grid(axis="y", color=GRID, lw=1)
    ax2.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax2.spines[side].set_visible(False)
    ax2.tick_params(length=0)
    ax2.set_ylabel("Chance of 47\nor fewer", labelpad=12)
    last = s.index[-1]
    ax2.annotate(f"{p_result.iloc[-1]:.0%} on\n{last:%b %-d}", (last, p_result.iloc[-1]), xytext=(-16, -6),
                 textcoords="offset points", ha="right", va="top", fontsize=13, color=INK, weight="medium")
    ax2.axvline(led_since, color=MUTED, lw=1)
    ax2.annotate(f"Became the single most likely\noutcome on {led_since:%b %-d}", (led_since, 0.9),
                 xytext=(8, 0), textcoords="offset points", fontsize=13, color=INK_2, va="top")
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    plt.setp(ax.get_xticklabels(), visible=False)

    # --- titles and footer --------------------------------------------------------
    fig.text(0.04, 0.955, "The eventual result led the market from March —", fontsize=30, weight="bold")
    fig.text(0.04, 0.925, "but didn't give it even odds until Election Day", fontsize=30, weight="bold")
    fig.text(0.04, 0.885, "Polymarket's daily probability for each Republican Senate seat count after the 2026\n"
                          "midterms (7-day average). The outlined row is where the result landed.", fontsize=16, color=INK_2,
             va="top", linespacing=1.4)
    fig.text(0.04, 0.045, RESULT_NOTE + f". 47 or fewer first topped 50% on {over_half:%b %-d}.",
             fontsize=12.5, color=INK_2)
    fig.text(0.04, 0.025, "Data: Polymarket public API (daily prices, rescaled to sum to 100%); race calls via civicAPI. "
                          "Chart: Bhrett Boggs", fontsize=12.5, color=MUTED)

    out = HERE / "senate_seats_heatmap.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  (led since {led_since:%Y-%m-%d}, over 50% from {over_half:%Y-%m-%d})")


if __name__ == "__main__":
    main()
