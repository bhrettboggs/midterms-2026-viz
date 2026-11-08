"""Every 2026 Senate race at a glance: shift, turnout, age and money per vote for each side.

Reads  data/clean/senate_candidates.csv, data/clean/ie_senate_general.csv, data/clean/turnout_states_2022_2026.csv
       data/raw/tonmcg/2024_..._Results.csv, data/raw/census/cc-est2024-agesex-all.csv, Gazetteer
Writes viz/senate_states_glance/senate_states_glance.png  (+ senate_states_glance.csv next to it)

One row per Senate race with both a Democrat and a Republican, sorted by shift since 2024.
Money per side = that party's campaign spending + outside spending that helped it, per vote cast.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import ACCENT, CLEAN, DEM, FIGSIZE, GRID, INK, INK_2, MUTED, REP, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"


def build() -> pd.DataFrame:
    geo = pd.read_csv(RAW / "census" / "2024_Gaz_counties_national.txt", sep="\t", dtype={"GEOID": str})
    geo.columns = geo.columns.str.strip()
    usps = {g[:2]: u for g, u in zip(geo.GEOID, geo.USPS)}

    b = pd.read_csv(RAW / "tonmcg" / "2024_US_County_Level_Presidential_Results.csv", dtype={"county_fips": str})
    b["state"] = b.county_fips.str[:2].map(usps)
    p24 = b.groupby("state")[["votes_dem", "votes_gop", "total_votes"]].sum()
    p24 = ((p24.votes_dem - p24.votes_gop) / p24.total_votes * 100).rename("m24")

    c = pd.read_csv(CLEAN / "senate_candidates.csv")
    v = c.pivot_table(index=["race_id", "state"], columns="bucket", values="votes", aggfunc="sum", fill_value=0)
    v = v.reindex(columns=["D", "R", "O"], fill_value=0).reset_index()
    v["votes"] = v[["D", "R", "O"]].sum(axis=1)
    # Only races whose top two are a Democrat and a Republican (drops ID, MT, NE, SD).
    top2 = (c.sort_values("votes", ascending=False).groupby("race_id").head(2)
            .groupby("race_id").bucket.apply(lambda b: set(b) == {"D", "R"}))
    v = v[v.race_id.isin(top2[top2].index)]
    v["m26"] = (v.D - v.R) / v.votes * 100
    camp = c.pivot_table(index="race_id", columns="bucket", values="disbursements", aggfunc="sum", fill_value=0)
    camp = camp.reindex(columns=["D", "R"], fill_value=0).add_prefix("camp_")

    g = pd.read_csv(CLEAN / "ie_senate_general.csv")
    out = g.pivot_table(index="state", columns="side", values="exp_amo", aggfunc="sum", fill_value=0)
    out = out.reindex(columns=["D", "R"], fill_value=0).add_prefix("out_")

    a = pd.read_csv(RAW / "census" / "cc-est2024-agesex-all.csv", encoding="latin-1")
    a = a[a.YEAR == 6].assign(state=lambda d: d.STATE.astype(str).str.zfill(2).map(usps))
    age = a.groupby("state")[["AGE65PLUS_TOT", "AGE18PLUS_TOT"]].sum()
    age = (age.AGE65PLUS_TOT / age.AGE18PLUS_TOT * 100).rename("old")
    t = pd.read_csv(CLEAN / "turnout_states_2022_2026.csv").set_index("state").turnout_2026 * 100

    d = (v.merge(camp, left_on="race_id", right_index=True, how="left")
          .merge(out, left_on="state", right_index=True, how="left").fillna(0))
    d = d.join(p24, on="state").join(age, on="state").join(t.rename("turnout"), on="state")
    d["shift"] = d.m26 - d.m24
    d["d_pv"] = (d.camp_D + d.out_D) / d.votes
    d["r_pv"] = (d.camp_R + d.out_R) / d.votes
    d["d_share"] = (d.camp_D + d.out_D) / (d.camp_D + d.out_D + d.camp_R + d.out_R)
    return d.sort_values("shift")


def main() -> None:
    setup()
    d = build()
    d.to_csv(HERE / "senate_states_glance.csv", index=False)
    rho = {k: spearmanr(d[k], d["shift"]).statistic for k in ("d_share", "turnout", "old", "d_pv", "r_pv", "m24")}
    # Redder states also swung more, so check that turnout's link isn't just that: partial rank
    # correlation after taking the 2024 margin out of both turnout and shift.
    resid = lambda y, x: y - np.polyval(np.polyfit(x, y, 1), x)
    rho_partial = spearmanr(resid(d.turnout, d.m24), resid(d["shift"], d.m24)).statistic

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    left, top, h = 0.09, 0.755, 0.615
    widths = [0.23, 0.15, 0.14, 0.27]
    gaps = 0.035
    axes, x = [], left
    for w in widths:
        axes.append(fig.add_axes([x, top - h, w, h]))
        x += w + gaps
    y = np.arange(len(d))

    def frame(ax, title, xlim, ticks, fmt):
        ax.set_ylim(-0.7, len(d) - 0.3)
        ax.set_xlim(*xlim)
        ax.set_xticks(ticks)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(fmt))
        ax.xaxis.tick_top()
        ax.grid(axis="x", color=GRID, lw=1)
        for i in range(0, len(d), 2):
            ax.axhspan(i - 0.5, i + 0.5, color="#f5f4f1", zorder=0)
        ax.set_axisbelow(True)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0, labelsize=11.5)
        ax.set_title(title, fontsize=13.5, weight="semibold", pad=26, loc="left")

    a0, a1, a2, a3 = axes
    frame(a0, "Shift since 2024", (-20, 30), [-15, 0, 15, 30], lambda v, _: "0" if v == 0 else f"{'D' if v > 0 else 'R'}+{abs(v):.0f}")
    a0.barh(y, d["shift"], color=[ACCENT if s > 0 else MUTED for s in d["shift"]], height=0.62, zorder=3)
    a0.axvline(0, color=INK_2, lw=1)
    a0.set_yticks(y)
    a0.set_yticklabels(d.state, fontsize=11.5)

    frame(a1, "Turnout", (35, 70), [40, 50, 60], lambda v, _: f"{v:.0f}%")
    a1.scatter(d.turnout, y, s=34, color=INK_2, zorder=3)
    a1.set_yticks([])

    frame(a2, "Adults 65+", (16, 30), [20, 25], lambda v, _: f"{v:.0f}%")
    a2.scatter(d.old, y, s=34, color=INK_2, zorder=3)
    a2.set_yticks([])

    frame(a3, "Money per vote", (0.05, 800), [0.1, 1, 10, 100], lambda v, _: f"${v:g}")
    a3.set_xscale("log")
    a3.set_xticks([0.1, 1, 10, 100])
    a3.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:g}"))
    for i, (dv, rv) in enumerate(zip(d.d_pv, d.r_pv)):
        lo, hi = max(min(dv, rv), 0.06), max(dv, rv, 0.06)
        a3.plot([lo, hi], [i, i], color=GRID, lw=2, zorder=2)
    a3.scatter(d.d_pv.clip(lower=0.06), y, s=36, color=DEM, zorder=3, label="Helping Democrats")
    a3.scatter(d.r_pv.clip(lower=0.06), y, s=36, color=REP, zorder=3, label="Helping Republicans")
    a3.set_yticks([])
    a3.text(0.0, -0.035, "●", color=DEM, fontsize=12, transform=a3.transAxes)
    a3.text(0.05, -0.035, "Helping D", fontsize=11.5, color=INK_2, transform=a3.transAxes)
    a3.text(0.52, -0.035, "●", color=REP, fontsize=12, transform=a3.transAxes)
    a3.text(0.57, -0.035, "Helping R", fontsize=11.5, color=INK_2, transform=a3.transAxes)

    titles(fig, "Money didn't track the swing.",
           "Lower-turnout states swung more.",
           f"{len(d)} Senate races with a Democrat and a Republican, sorted by how far each state moved from the 2024\n"
           f"presidential vote. Rank correlation with the shift: Democrats' share of the money {rho['d_share']:+.2f}, "
           f"turnout {rho['turnout']:+.2f},\nadults 65+ {rho['old']:+.2f}. With {len(d)} races, anything under ±0.35 "
           "is indistinguishable from no pattern.")
    footer(fig, [
        "Money per vote = that side's campaign spending + outside spending supporting it or opposing its opponent, ÷ votes cast.",
        f"Redder states (2024 margin) also swung more ({rho['m24']:+.2f}); turnout's link holds after adjusting for that ({rho_partial:+.2f}).",
        "Campaign money through mid-Oct. Turnout: UF early estimate. Age: Census July 2024. Shift and results are unofficial.",
    ], "FEC, civicAPI, tonmcg, Census Bureau, UF Election Lab")

    out = HERE / "senate_states_glance.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  n={len(d)}  " + ", ".join(f"{k} {v:+.2f}" for k, v in rho.items()))


if __name__ == "__main__":
    main()
