"""Where 2026 Senate campaign money came from and went, plus the outside money around it.

Reads  data/clean/senate_money_flow.csv
Writes viz/senate_money_flow/money_flow.png

One alluvial (Sankey) diagram drawn in real dollars, so every height is comparable:
  top    sources -> campaigns by party -> spent / cash left
  bottom outside groups -> who their spending helped (it never passes through a campaign)
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import (CLEAN, DEM, DEM_LIGHT, FIGSIZE, INK, INK_2, OTHER, REP, REP_LIGHT, SURFACE, footer,  # noqa: E402
                   money, setup, titles)

HERE = Path(__file__).resolve().parent
MERGE = {"Party committees": "Self-funding, party & other", "Other": "Self-funding, party & other",
         "Self-funding": "Self-funding, party & other"}
SOURCES = ["Individual donors", "Joint fundraising transfers", "Cash on hand before 2025", "PACs",
           "Self-funding, party & other"]
CAMPAIGNS = ["Democratic campaigns", "Republican campaigns", "Other campaigns"]
USES = ["Spent", "Cash left (mid-Oct)"]
HELPS = ["Helping Democrats", "Helping Republicans", "Independents and others"]
NODE = {"Democratic campaigns": DEM, "Republican campaigns": REP, "Other campaigns": OTHER,
        "Helping Democrats": DEM, "Helping Republicans": REP, "Independents and others": OTHER}
BAND = {"Democratic campaigns": DEM_LIGHT, "Republican campaigns": REP_LIGHT, "Other campaigns": "#e4e3df",
        "Helping Democrats": DEM_LIGHT, "Helping Republicans": REP_LIGHT, "Independents and others": "#e4e3df"}

X = [0.30, 0.56, 0.80]   # column positions (axes fraction)
W = 0.016                # node width
GAP = 28                 # $M between stacked nodes


def band(ax, x0, top0, x1, top1, h, color):
    """A smooth band of height h ($M) from (x0, top0) to (x1, top1); y grows downward."""
    xm = (x0 + x1) / 2
    v = [(x0, top0), (xm, top0), (xm, top1), (x1, top1), (x1, top1 + h), (xm, top1 + h), (xm, top0 + h),
         (x0, top0 + h), (x0, top0)]
    c = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO, MPath.CURVE4, MPath.CURVE4,
         MPath.CURVE4, MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(v, c), fc=color, ec=SURFACE, lw=0.8))


def stack(names, totals, top):
    """Top y of each node in a column, stacked downward with gaps."""
    out, y = {}, top
    for n in names:
        out[n] = y
        y += totals[n] + GAP
    return out


def label(ax, x, top, h, text, value, side, box=False):
    tx, ha = (x - 0.012, "right") if side == "left" else (x + W + 0.012, "left")
    ax.text(tx, top + h / 2, f"{text}  {money(value * 1e6)}" if h < 100 else f"{text}\n{money(value * 1e6)}",
            ha=ha, va="center", fontsize=14, color=INK, linespacing=1.25,
            bbox=dict(fc=SURFACE, ec="none", alpha=0.85, pad=1.5) if box else None)


def main() -> None:
    setup()
    f = pd.read_csv(CLEAN / "senate_money_flow.csv")
    f["value"] = f.value / 1e6
    f["source"] = f.source.replace(MERGE)
    f = f.groupby(["source", "target"], as_index=False).value.sum()
    flows = {(r.source, r.target): r.value for r in f.itertuples()}

    src_tot = f[f.target.isin(CAMPAIGNS)].groupby("source").value.sum()
    camp_tot = f[f.target.isin(CAMPAIGNS)].groupby("target").value.sum()
    use_tot = f[f.source.isin(CAMPAIGNS)].groupby("target").value.sum()
    help_tot = f[f.source == "Outside groups"].set_index("target").value

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.03, 0.11, 0.94, 0.72])
    ax.axis("off")
    ax.set_xlim(0, 1)

    # --- campaigns' own money -----------------------------------------------------
    top_a = 60
    s_top, c_top, u_top = stack(SOURCES, src_tot, top_a), stack(CAMPAIGNS, camp_tot, top_a), stack(USES, use_tot, top_a)
    s_off, c_in = dict(s_top), dict(c_top)
    for c in CAMPAIGNS:
        for s in SOURCES:
            v = flows.get((s, c), 0)
            if v > 0:
                band(ax, X[0] + W, s_off[s], X[1], c_in[c], v, BAND[c])
                s_off[s] += v
                c_in[c] += v
    c_out, u_in = dict(c_top), dict(u_top)
    for c in CAMPAIGNS:
        for u in USES:
            v = flows.get((c, u), 0)
            if v > 0:
                band(ax, X[1] + W, c_out[c], X[2], u_in[u], v, BAND[c])
                c_out[c] += v
                u_in[u] += v
    for s in SOURCES:
        ax.add_patch(Rectangle((X[0], s_top[s]), W, src_tot[s], fc=INK_2, ec="none"))
        label(ax, X[0], s_top[s], src_tot[s], s, src_tot[s], "left")
    for c in CAMPAIGNS:
        ax.add_patch(Rectangle((X[1], c_top[c]), W, camp_tot[c], fc=NODE[c], ec="none"))
        label(ax, X[1], c_top[c], camp_tot[c], c, camp_tot[c], "right", box=True)
    for u in USES:
        ax.add_patch(Rectangle((X[2], u_top[u]), W, use_tot[u], fc=INK_2, ec="none"))
        label(ax, X[2], u_top[u], use_tot[u], u, use_tot[u], "right")
    ax.text(0.0, top_a - 25, "SENATE CAMPAIGNS' OWN MONEY", fontsize=13, color=INK_2, weight="semibold")
    bottom_a = top_a + src_tot.sum() + GAP * (len(SOURCES) - 1)

    # --- outside groups, same dollar scale ----------------------------------------
    top_b = bottom_a + 170
    ax.text(0.0, top_b - 25, "OUTSIDE GROUPS' SPENDING  (super PACs, party committees, other groups)",
            fontsize=13, color=INK_2, weight="semibold")
    o_tot = help_tot.sum()
    ax.add_patch(Rectangle((X[0], top_b), W, o_tot, fc=INK_2, ec="none"))
    label(ax, X[0], top_b, o_tot, "Outside groups", o_tot, "left")
    h_top = stack(HELPS, help_tot, top_b)
    off = top_b
    for h in HELPS:
        band(ax, X[0] + W, off, X[1], h_top[h], help_tot[h], BAND[h])
        off += help_tot[h]
        ax.add_patch(Rectangle((X[1], h_top[h]), W, help_tot[h], fc=NODE[h], ec="none"))
        label(ax, X[1], h_top[h], help_tot[h], h, help_tot[h], "right", box=True)
    bottom_b = top_b + o_tot + GAP * (len(HELPS) - 1)

    # "Raised" = receipts this cycle, so cash carried in from before 2025 is left out of the ratio.
    raised = f[f.target.isin(CAMPAIGNS) & (f.source != "Cash on hand before 2025")].groupby("target").value.sum()
    ratio = raised["Democratic campaigns"] / raised["Republican campaigns"]
    ax.text(X[2] - 0.01, top_b + 40,
            f"Campaigns:\n{ratio:.1f}× more raised\non the Democratic side\n\n"
            f"Outside groups:\n{money(help_tot['Helping Democrats'] * 1e6)} vs "
            f"{money(help_tot['Helping Republicans'] * 1e6)},\nnearly even",
            fontsize=15, color=INK, va="top", linespacing=1.35)

    ax.set_ylim(bottom_b + 20, 0)

    titles(fig, f"Democratic Senate campaigns raised {ratio:.1f}× more —",
           "outside groups spent almost evenly",
           "Money in 2026 U.S. Senate general-election races. Top: what the candidates' own campaigns\n"
           "raised and spent. Bottom: outside spending. Heights are in dollars, on one scale.")
    footer(fig, [
        "Campaign money is cycle-to-date through each campaign's pre-general FEC report (mid-October) and includes primaries.",
        "“Helping” = spending to support that party's candidate or to oppose the opponent; general-election spending only.",
    ], "FEC candidate summaries and independent expenditures (junk filings and duplicate reports removed)")

    out = HERE / "money_flow.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
