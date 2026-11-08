"""Every county as a circle sized by votes cast, colored by how far it moved since 2024.

Reads  data/clean/county_map_2026.csv           2026 Senate (or governor) results + 2024 baseline
       data/raw/tonmcg/2024_..._Results.csv     2024 votes, to size counties with no 2026 statewide race
       data/raw/census/2024_Gaz_counties_*.txt  county center points
Writes viz/vote_circles/vote_circles.png

Circles start at each county's center (Albers equal-area projection, lower 48), are sized by
votes cast (area proportional to votes), then nudged apart until none overlap (a Dorling cartogram).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.patches import Circle
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import CLEAN, FIGSIZE, INK, INK_2, MUTED, SHIFT_CMAP, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"
SKIP = {"AK", "HI"}           # not drawn: lower 48 only (Alaska also has no county baseline)
CLIP = 0.30                   # color scale saturates at a 30-point shift
NO_RACE_STATES = {"IN", "MO", "ND", "UT", "WA"}
LABELS = {"06037": "Los Angeles", "17031": "Cook (Chicago)", "48201": "Harris (Houston)",
          "04013": "Maricopa (Phoenix)", "12086": "Miami-Dade", "36047": "Brooklyn",
          "26163": "Wayne (Detroit)", "13121": "Fulton (Atlanta)", "45019": "Charleston"}


def albers(lon, lat, lat0=23.0, lon0=-96.0, p1=29.5, p2=45.5):
    """Albers equal-area conic projection (the standard lower-48 parameters), unit sphere."""
    lon, lat = np.radians(lon), np.radians(lat)
    lat0, lon0, p1, p2 = map(np.radians, (lat0, lon0, p1, p2))
    n = (np.sin(p1) + np.sin(p2)) / 2
    c = np.cos(p1) ** 2 + 2 * n * np.sin(p1)
    rho = np.sqrt(c - 2 * n * np.sin(lat)) / n
    rho0 = np.sqrt(c - 2 * n * np.sin(lat0)) / n
    theta = n * (lon - lon0)
    return rho * np.sin(theta), rho0 - rho * np.cos(theta)


def relax(xy: np.ndarray, r: np.ndarray, steps: int = 400) -> np.ndarray:
    """Push overlapping circles apart while a weak spring pulls each back to its true location."""
    home = xy.copy()
    p = xy.copy()
    for _ in range(steps):
        tree = cKDTree(p)
        pairs = tree.query_pairs(2 * r.max(), output_type="ndarray")
        if len(pairs):
            i, j = pairs[:, 0], pairs[:, 1]
            d = p[j] - p[i]
            dist = np.hypot(d[:, 0], d[:, 1]) + 1e-9
            overlap = r[i] + r[j] + 0.0004 - dist
            hit = overlap > 0
            i, j, d, dist, overlap = i[hit], j[hit], d[hit], dist[hit], overlap[hit]
            push = (d / dist[:, None]) * (overlap / 2)[:, None]
            # Big circles move less than small ones.
            wi = (r[j] ** 2 / (r[i] ** 2 + r[j] ** 2))[:, None]
            move = np.zeros_like(p)
            np.add.at(move, i, -push * wi * 2)
            np.add.at(move, j, push * (1 - wi) * 2)
            p += move * 0.5
        p += (home - p) * 0.01
    return p


def main() -> None:
    setup()
    m = pd.read_csv(CLEAN / "county_map_2026.csv", dtype={"county_fips": str})
    m = m[~m.state.isin(SKIP)]
    m["kind"] = np.where(~m.d_vs_r_race, "no_dr", np.where(m.margin_2024.isna(), "no_base", "shift"))

    # Counties in states with no Senate or governor race: draw hollow, sized by 2024 presidential votes.
    base = pd.read_csv(RAW / "tonmcg" / "2024_US_County_Level_Presidential_Results.csv", dtype={"county_fips": str})
    geo = pd.read_csv(RAW / "census" / "2024_Gaz_counties_national.txt", sep="\t", dtype={"GEOID": str})
    geo.columns = geo.columns.str.strip()
    nr = (base.merge(geo[["GEOID", "USPS", "INTPTLAT", "INTPTLONG"]], left_on="county_fips", right_on="GEOID")
          .query("USPS in @NO_RACE_STATES")
          .rename(columns={"USPS": "state", "INTPTLAT": "lat", "INTPTLONG": "lon"}))
    nr = nr.assign(kind="no_race")[["county_fips", "state", "lat", "lon", "total_votes", "kind"]]
    d = pd.concat([m[["county_fips", "state", "lat", "lon", "total_votes", "shift_vs_2024", "kind"]], nr],
                  ignore_index=True).dropna(subset=["lat", "lon"])
    d = d[d.total_votes > 0]

    x, y = albers(d.lon.values, d.lat.values)
    xy = np.column_stack([x, y])
    # Scale so the circles' total area is ~30% of the map's bounding box.
    box = (x.max() - x.min()) * (y.max() - y.min())
    k = np.sqrt(0.30 * box / (np.pi * d.total_votes.sum()))
    r = k * np.sqrt(d.total_votes.values)
    xy = relax(xy, r)

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.02, 0.24, 0.96, 0.62])
    ax.set_aspect("equal")
    ax.axis("off")
    norm = Normalize(-CLIP, CLIP)
    order = np.argsort(-r)  # draw big first so small ones stay visible
    for idx in order:
        row = d.iloc[idx]
        if row.kind == "shift":
            fc, ec, lw = SHIFT_CMAP(norm(np.clip(row.shift_vs_2024, -CLIP, CLIP))), SURFACE, 0.4
        elif row.kind == "no_race":
            fc, ec, lw = "none", "#b9b8b2", 0.6
        else:
            fc, ec, lw = "#d9d8d3", SURFACE, 0.4
        ax.add_patch(Circle(xy[idx], r[idx], fc=fc, ec=ec, lw=lw))
    pad = 0.01
    ax.set_xlim(xy[:, 0].min() - pad, xy[:, 0].max() + pad)
    ax.set_ylim(xy[:, 1].min() - pad, xy[:, 1].max() + pad)

    # Points per map unit, to place labels just below each circle.
    ext = ax.get_window_extent()
    ppu = ext.height * 72 / fig.dpi / (ax.get_ylim()[1] - ax.get_ylim()[0])
    for fips, name in LABELS.items():
        hit = np.where(d.county_fips.values == fips)[0]
        if len(hit):
            i = hit[0]
            ax.annotate(name, xy[i], xytext=(0, -r[i] * ppu - 4), textcoords="offset points", ha="center",
                        va="top", fontsize=11.5, color=INK, bbox=dict(fc=SURFACE, ec="none", alpha=0.75, pad=0.8))

    # --- legends ---------------------------------------------------------------------
    cax = fig.add_axes([0.08, 0.205, 0.52, 0.018])
    sm = plt.cm.ScalarMappable(norm=norm, cmap=SHIFT_CMAP)
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=[-0.3, -0.15, 0, 0.15, 0.3])
    cb.ax.set_xticklabels(["30+", "15", "0", "15", "30+"])
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=12.5, colors=INK_2)
    fig.text(0.08, 0.232, "← moved toward Republicans", fontsize=12.5, color=INK_2)
    fig.text(0.60, 0.232, "moved toward Democrats →", fontsize=12.5, color=INK_2, ha="right")
    fig.text(0.34, 0.172, "change in margin, points", fontsize=12, color=MUTED, ha="center")

    # Size key drawn in the map's own units, so the circles match the map exactly.
    lax = fig.add_axes([0.66, 0.155, 0.32, 0.10])
    lax.set_aspect("equal")
    lax.axis("off")
    unit = (ax.get_ylim()[1] - ax.get_ylim()[0]) / ext.height  # map units per pixel
    lax_h_px = lax.get_window_extent().height
    lax.set_ylim(0, lax_h_px * unit)
    lax.set_xlim(0, lax.get_window_extent().width * unit)
    xs, base_y = 0.0, 0.010
    for v, lab in ((10_000, "10K"), (100_000, "100K"), (1_000_000, "1M")):
        rr = k * np.sqrt(v)
        lax.add_patch(Circle((xs + rr, base_y + rr), rr, fc="none", ec=INK_2, lw=1))
        lax.text(xs + rr, base_y - 0.004, lab, ha="center", va="top", fontsize=11.5, color=INK_2)
        xs += 2 * rr + 0.018
    top = lax.get_ylim()[1]
    lax.text(0, top, "Votes cast", fontsize=12.5, color=INK_2, va="top")
    small = 0.006
    lax.add_patch(Circle((xs + small, base_y + 0.032), small, fc="none", ec="#b9b8b2", lw=1))
    lax.text(xs + 3 * small, base_y + 0.032, "no statewide race", va="center", fontsize=11.5, color=INK_2)
    lax.add_patch(Circle((xs + small, base_y + 0.008), small, fc="#d9d8d3", ec="none"))
    lax.text(xs + 3 * small, base_y + 0.008, "no D-vs-R race", va="center", fontsize=11.5, color=INK_2)

    s = d[d.kind == "shift"]
    share = (s.shift_vs_2024 > 0).mean()
    weighted = np.average(s.shift_vs_2024, weights=s.total_votes)
    # States drawn gray because their race wasn't Democrat-vs-Republican at the top (independent or
    # no Democrat as the main challenger), named from the data rather than hard-coded.
    NAMES = {"ID": "Idaho", "MT": "Montana", "NE": "Nebraska", "SD": "South Dakota", "RI": "Rhode Island",
             "WY": "Wyoming"}
    no_dr = ", ".join(NAMES.get(st, st) for st in sorted(m[~m.d_vs_r_race].state.unique()))
    titles(fig, f"{share:.0%} of counties moved toward Democrats",
           "compared with the 2024 presidential vote",
           f"Each circle is a county, sized by votes cast in 2026. Color is the change in margin from the 2024\n"
           f"presidential race to this year's Senate race (governor where there was no Senate race).\n"
           f"Vote-weighted, the average county moved {weighted * 100:.0f} points.")
    footer(fig, [
        "Compares different offices: a Senate or governor race vs. the presidential race, so candidate effects are included.",
        "Unofficial, still-counting results. Lower 48 only.",
        f"Gray: the race's top two weren't a Democrat and a Republican ({no_dr}): no D-vs-R shift to show.",
        "No statewide race in Indiana, Missouri, North Dakota, Utah, Washington (hollow circles, sized by 2024 votes).",
    ], "civicAPI (2026 county results), tonmcg (2024 county results), U.S. Census Gazetteer (county centers)")

    out = HERE / "vote_circles.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  share {share:.3f}, weighted {weighted:.3f}, n={len(s)}")


if __name__ == "__main__":
    main()
