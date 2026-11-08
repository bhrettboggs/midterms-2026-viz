"""How many House votes were cast in a real contest? Every 2026 district by its margin, and the votes behind them.

Reads  data/raw/civicapi/races.csv
Writes viz/house_competition/house_competition.png

Top: all votes cast in U.S. House races, split by how close the district ended up. Bottom: every district
as one bar, sorted from the biggest Democratic margin to the biggest Republican one, colored by the same bands.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from common import party_bucket  # noqa: E402
from style import CLEAN, FIGSIZE, GRID, INK, INK_2, MUTED, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"
BANDS = ["under 5", "5–10", "10–20", "20 or more", "no D-vs-R contest"]
COLOR = {"under 5": "#0d366b", "5–10": "#2a78d6", "10–20": "#6da7ec", "20 or more": "#cde2fb",
         "no D-vs-R contest": "#d9d8d3"}
TEXT_ON = {"under 5": SURFACE, "5–10": SURFACE, "10–20": INK, "20 or more": INK, "no D-vs-R contest": INK}


def load() -> pd.DataFrame:
    c = pd.read_csv(RAW / "civicapi" / "races.csv", low_memory=False)
    h = c[(c.type == "House of Representatives") & (c.state != "US")
          & ~c.election_type.str.contains("Primary|Runoff", case=False, na=False)].copy()
    h["b"] = h.party.map(party_bucket)
    p = h.pivot_table(index="race_id", columns="b", values="votes", aggfunc="sum", fill_value=0)
    meta = h.groupby("race_id").agg(name=("election_name", "first"), pr=("percent_reporting", "max"))
    d = p.join(meta)
    d["tot"] = d[["D", "R", "O"]].sum(axis=1)
    contested = (d.D > 0) & (d.R > 0)
    d["margin"] = np.where(contested, (d.D - d.R) / d.tot.replace(0, np.nan) * 100, np.nan)
    d["band"] = pd.cut(d.margin.abs(), [-0.1, 5, 10, 20, 100], labels=BANDS[:4]).astype(object)
    d["band"] = d.band.fillna(BANDS[4])
    return d


def main() -> None:
    setup()
    d = load()
    res = d.groupby("band").agg(districts=("tot", "size"), votes=("tot", "sum")).reindex(BANDS)
    res["share"] = res.votes / res.votes.sum()
    con = d.dropna(subset=["margin"]).sort_values("margin", ascending=False)
    # Vote-weighted median of |margin|: half of all votes in D-vs-R districts were cast where the margin was this or wider.
    order = con.margin.abs().sort_values()
    cum = con.loc[order.index, "tot"].cumsum() / con.tot.sum()
    weighted_median = order[cum >= 0.5].iloc[0]

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    # --- stacked bar of votes ------------------------------------------------------------
    ax1 = fig.add_axes([0.04, 0.60, 0.92, 0.13])
    left = 0
    for band, r in res.iterrows():
        ax1.barh(0, r.share, left=left, height=0.9, color=COLOR[band], ec=SURFACE, lw=2)
        if r.share > 0.06:
            ax1.text(left + r.share / 2, 0.2, f"{r.share:.0%}", ha="center", va="center", fontsize=21, weight="bold",
                     color=TEXT_ON[band])
            ax1.text(left + r.share / 2, -0.07, f"{band} points", ha="center", va="center", fontsize=12.5,
                     color=TEXT_ON[band])
            ax1.text(left + r.share / 2, -0.29, f"{int(r.districts)} districts", ha="center", va="center", fontsize=12,
                     color=TEXT_ON[band])
        else:
            ax1.annotate(f"{r.share:.0%}: {band}\n({int(r.districts)} districts)", (left + r.share / 2, 0.45),
                         xytext=(left + r.share / 2 - 0.02, 0.85), textcoords="data", fontsize=12, color=INK_2,
                         ha="right", va="center", arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.9), linespacing=1.2)
        left += r.share
    ax1.set_xlim(0, 1)
    ax1.set_ylim(-0.5, 1.1)
    ax1.axis("off")
    fig.text(0.04, 0.755, "Share of all House votes, by the margin in the voter's district", fontsize=16, weight="semibold")

    # --- every district as a bar ----------------------------------------------------------
    ax2 = fig.add_axes([0.07, 0.125, 0.89, 0.42])
    x = np.arange(len(con))
    ax2.bar(x, con.margin, width=1.0, color=[COLOR[b] for b in con.band], lw=0)
    ax2.axhline(0, color=INK, lw=1)
    close = con[con.band == "under 5"]
    i0, i1 = x[con.band.values == "under 5"].min(), x[con.band.values == "under 5"].max()
    ax2.axvspan(i0 - 0.5, i1 + 0.5, color="#fbf0d9", zorder=0)
    ax2.annotate(f"{len(close)} districts within 5 points", ((i0 + i1) / 2, 7), xytext=(0, 70), textcoords="offset points",
                 ha="center", fontsize=13.5, weight="semibold", color=INK,
                 arrowprops=dict(arrowstyle="-", color=INK_2, lw=1))
    ax2.set_xlim(-2, len(con) + 1)
    ax2.set_ylim(-60, 92)
    ax2.set_xticks([])
    ax2.set_yticks([-50, -25, 0, 25, 50, 75])
    ax2.set_yticklabels(["R+50", "R+25", "even", "D+25", "D+50", "D+75"])
    ax2.grid(axis="y", color=GRID, lw=1)
    ax2.set_axisbelow(True)
    for sp in ax2.spines.values():
        sp.set_visible(False)
    ax2.tick_params(length=0, labelsize=13)
    ax2.text(2, 88, f"Every district with a Democrat and a Republican ({len(con)}), sorted by margin", fontsize=16,
             weight="semibold", va="top")
    ax2.text(2, 60, "Democrat ahead ↑", fontsize=12.5, color=INK_2)
    ax2.text(len(con) - 2, -45, "Republican ahead ↓", fontsize=12.5, color=INK_2, ha="right")
    n_d, n_r = (con.margin > 0).sum(), (con.margin < 0).sum()
    ax2.text(2, -55, f"{n_d} districts lean Democratic, {n_r} Republican in the count so far", fontsize=12.5, color=INK_2)

    under5 = res.loc["under 5"]
    big = res.loc["20 or more"]
    titles(fig, f"Only {under5.share:.0%} of House votes were cast in a district",
           "decided by fewer than 5 points",
           f"All 435 U.S. House races on November 3, 2026, grouped by each district's Democrat-vs-Republican margin.\n"
           f"Nearly half of all votes ({big.share:.0%}) were cast in districts decided by 20 points or more. Half of the votes in\n"
           f"two-party districts came from places where the margin was at least {weighted_median:.0f} points.")
    footer(fig, [
        "Unofficial, still-counting results as of Nov 7; districts near a band's edge can move. “No D-vs-R contest” = unopposed or two",
        "candidates of the same party (California's top-two primaries, Massachusetts), plus one Florida district with no count posted yet.",
    ], "civicAPI (2026 U.S. House results)")

    out = HERE / "house_competition.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}\n{res.round(3)}\nvote-weighted median |margin| {weighted_median:.1f}")


if __name__ == "__main__":
    main()
