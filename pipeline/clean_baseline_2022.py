"""Like-for-like baseline: 2022 midterm county results joined to the same office in 2026.

Every "shift since 2024" in this repo compares a Senate or governor race with a presidential race.
That mixes two things: how voters moved, and how a midterm electorate differs from a presidential
one. This step adds the clean comparison: the same office in the same county, four years apart.

Inputs
  data/raw/medsl/county_sen_gov_2022.csv   2022 county Senate/governor votes (built by aggregate_medsl_2022.py)
  data/clean/county_results_2026.csv       2026 county Senate/governor votes (built by clean_results.py)
  data/raw/census/2024_Gaz_counties_*       county names, land area, center points

Output (data/clean/)
  county_shift_2022_2026.csv   one row per county x office where both years had a Democrat-vs-Republican
                               race: 2022 and 2026 margins, shift, 2026 votes as a share of 2022 votes

Rules
  * A race counts only if in BOTH years a Democrat and a Republican were the top two (2026: from the
    pipeline's d_vs_r_race flag; 2022: D and R each out-polled all other candidates combined).
  * Governor races are the main comparison (34 states had one in both years with usable data).
    Senate races are kept where the same state voted for the Senate in both years (Georgia, Ohio,
    Florida, Oklahoma, South Carolina, Alabama, Iowa, Kansas ...).
  * Not available: Alaska (MEDSL reports no counties), Tennessee (MEDSL's 2022 file lacks the governor
    race), Connecticut (2022 counties vs 2026 planning regions), Indiana (57 counties missing in 2022).
"""
import pandas as pd

from common import CLEAN, RAW, gazetteer, note


def main() -> None:
    b = pd.read_csv(RAW / "medsl" / "county_sen_gov_2022.csv", dtype={"county_fips": str})
    b = b[b.county_fips != "unassigned"]
    # A 2022 race is D-vs-R if each major party out-polled everyone else combined, statewide.
    st = b.groupby(["state", "office", "special"])[["dem_votes", "rep_votes", "other_votes"]].sum()
    ok22 = st[(st.dem_votes > st.other_votes) & (st.rep_votes > st.other_votes)].reset_index()
    skipped = st[~st.index.isin(ok22.set_index(["state", "office", "special"]).index)].reset_index()
    note("baseline 2022: races not Democrat-vs-Republican at the top in 2022 (skipped): "
         + (", ".join(f"{r.state} {r.office}" for r in skipped.itertuples()) or "none"))
    # Where a state had a regular and a special Senate race in 2022 (Oklahoma), keep the regular one.
    ok22 = ok22.sort_values("special").drop_duplicates(["state", "office"])
    b = b.merge(ok22[["state", "office", "special"]], on=["state", "office", "special"])
    b = b.rename(columns={"dem_votes": "dem_2022", "rep_votes": "rep_2022", "total_votes": "votes_2022"})
    b["margin_2022"] = (b.dem_2022 - b.rep_2022) / b.votes_2022

    c = pd.read_csv(CLEAN / "county_results_2026.csv", dtype={"county_fips": str})
    c = c[c.d_vs_r_race].sort_values("special").drop_duplicates(["state", "office", "county_fips"])
    c = c.rename(columns={"dem_votes": "dem_2026", "rep_votes": "rep_2026", "total_votes": "votes_2026",
                          "pct_reporting": "pct_reporting_2026"})

    m = b.merge(c[["state", "office", "county_fips", "dem_2026", "rep_2026", "votes_2026", "margin_2026",
                   "pct_reporting_2026", "election_name"]], on=["state", "office", "county_fips"], how="inner")
    m = m[(m.votes_2022 > 0) & (m.votes_2026 > 0)]
    m["shift_2022_2026"] = m.margin_2026 - m.margin_2022   # + = moved toward Democrats
    m["votes_vs_2022"] = m.votes_2026 / m.votes_2022
    geo = gazetteer("counties").rename(columns={"GEOID": "county_fips", "NAME": "county_name_census",
                                                "INTPTLAT": "lat", "INTPTLONG": "lon"})
    m = m.merge(geo[["county_fips", "county_name_census", "lat", "lon", "ALAND_SQMI"]], on="county_fips", how="left")
    m["county_name"] = m.county_name_census.fillna(m.county_name)
    cols = ["state", "office", "election_name", "county_fips", "county_name", "lat", "lon", "ALAND_SQMI",
            "dem_2022", "rep_2022", "votes_2022", "margin_2022", "dem_2026", "rep_2026", "votes_2026", "margin_2026",
            "shift_2022_2026", "votes_vs_2022", "pct_reporting_2026"]
    m[cols].sort_values(["office", "state", "county_fips"]).to_csv(CLEAN / "county_shift_2022_2026.csv", index=False)

    # Coverage and sanity checks.
    gov = m[m.office == "GOV"]
    sen = m[m.office == "SEN"]
    note(f"baseline 2022: governor-vs-governor in {gov.state.nunique()} states ({len(gov):,} counties); "
         f"Senate-vs-Senate in {sen.state.nunique()} states ({len(sen):,} counties)")
    # States with a 2026 race of that office but no 2022 match, and why.
    have26 = set(zip(c.state, c.office))
    have22 = set(zip(b.state, b.office))
    missing = sorted(have26 - have22)
    note("baseline 2022: 2026 races with no 2022 same-office baseline: "
         + ", ".join(f"{s} {o}" for s, o in missing))
    # County coverage inside matched states: 2022 counties that found no 2026 partner.
    for off, grp in b.groupby("office"):
        paired = m[m.office == off]
        lost = grp[grp.state.isin(paired.state.unique()) & ~grp.county_fips.isin(paired.county_fips)]
        if len(lost):
            note(f"baseline 2022 {off}: {len(lost)} 2022 counties in matched states had no 2026 county match "
                 f"({lost.votes_2022.sum() / grp[grp.state.isin(paired.state.unique())].votes_2022.sum():.2%} of their votes)"
                 + (f"; e.g. {', '.join(lost.state + ' ' + lost.county_name.fillna(lost.county_fips))}" if len(lost) <= 8 else ""))
    swing = m.groupby("office").apply(lambda d: pd.Series({
        "vote_weighted_shift": (d.shift_2022_2026 * d.votes_2026).sum() / d.votes_2026.sum(),
        "share_moved_D": (d.shift_2022_2026 > 0).mean()}), include_groups=False)
    for off, r in swing.iterrows():
        note(f"baseline 2022 {off}: vote-weighted county shift since 2022 {r.vote_weighted_shift * 100:+.1f} points; "
             f"{r.share_moved_D:.0%} of counties moved toward Democrats")


if __name__ == "__main__":
    main()
