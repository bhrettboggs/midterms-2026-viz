"""County-level 2026 Senate and governor results, joined to the 2024 presidential baseline.

Inputs
  data/raw/civicapi/sen_gov_county.csv   votes per candidate per county (civicAPI)
  data/raw/census/2024_Gaz_counties_*    county codes and center points
  data/raw/tonmcg/2024_US_County_Level_Presidential_Results.csv

Outputs (data/clean/)
  county_results_2026.csv   one row per race x county: D, R, other and total votes
  county_map_2026.csv       one race per state (Senate if there is one, else governor),
                            with 2024 baseline, shift and county center point
"""
import pandas as pd

from common import CLEAN, RAW, STATES, gazetteer, norm_place, note, party_bucket

# civicAPI reports some states at two levels at once (New England: counties AND towns;
# Alaska: boroughs AND house districts; Connecticut: old counties AND planning regions).
# Adding them up double-counts, so each state uses exactly one level:
#   Connecticut -> planning regions (what the Census and the 2024 baseline use now)
#   everyone else -> county-equivalents (counties, parishes, boroughs, independent cities)
COUNTY_TYPES = {"County", "Parish", "Borough", "City"}


def load_civic() -> pd.DataFrame:
    c = pd.read_csv(RAW / "civicapi" / "sen_gov_county.csv", dtype={"fips": str}, low_memory=False)
    c = c[c.state.isin(STATES)]  # drops national roll-ups and territories
    c["office"] = c.election_name.str.contains("Senate").map({True: "SEN", False: "GOV"})
    c["special"] = c.election_name.str.contains("Special")
    c["bucket"] = c.party.map(party_bucket)
    return c


def keep_one_level(c: pd.DataFrame) -> pd.DataFrame:
    ct = c.state.eq("CT")
    keep = (ct & c.region_type.eq("Planning Region")) | (~ct & c.region_type.isin(COUNTY_TYPES))
    dropped = c[~keep & ~c.region_type.isin(["State"])]
    note("results: one reporting level per state; dropped duplicate levels "
         + ", ".join(f"{k} ({v})" for k, v in dropped.groupby("region_type").size().items()))
    return c[keep].copy()


def attach_fips(c: pd.DataFrame) -> pd.DataFrame:
    """Every row gets a 5-digit county FIPS; rows without one are matched by name."""
    counties = gazetteer("counties")
    counties["key"] = counties.NAME.map(norm_place)
    lookup = counties.set_index(["USPS", "key"]).GEOID.sort_index()

    c["county_fips"] = c.fips.where(c.fips.str.len() == 5)
    miss = c.county_fips.isna()
    keys = list(zip(c.loc[miss, "state"], c.loc[miss, "region_name"].map(norm_place)))
    c.loc[miss, "county_fips"] = [lookup.get(k) for k in keys]

    unmatched = c[c.county_fips.isna()]
    total = c.votes.sum()
    note(f"results: {unmatched.drop_duplicates(['state','region_name']).shape[0]} places could not be "
         f"matched to a county code ({unmatched.votes.sum() / total:.3%} of votes); see unmatched_places.csv")
    (unmatched.drop_duplicates(["state", "region_type", "region_name"])
     [["state", "region_type", "region_name"]].to_csv(CLEAN / "unmatched_places.csv", index=False))
    return c[c.county_fips.notna()]


def check_against_state_totals(raw: pd.DataFrame, t: pd.DataFrame) -> None:
    """Where civicAPI gives a statewide row, our county sum should match it."""
    st = raw[raw.region_type.eq("State") & raw.state.isin(STATES)].groupby("race_id").votes.sum()
    ours = t.groupby("race_id").total_votes.sum()
    both = pd.concat([st.rename("state_row"), ours.rename("county_sum")], axis=1).dropna()
    both["ratio"] = both.county_sum / both.state_row
    bad = both[(both.ratio - 1).abs() > 0.01]
    note(f"results: county sums vs statewide rows: {len(both)} races checked, {len(bad)} off by more than 1%")


def d_vs_r_races(c: pd.DataFrame) -> set:
    """Races whose two leading candidates statewide are one Democrat and one Republican.
    Anything else (no Democrat on the ballot, or an independent as the main challenger, as in
    Montana's Senate race) can't be compared with a D-vs-R presidential baseline."""
    tot = c.groupby(["race_id", "candidate", "bucket"], as_index=False).votes.sum()
    top2 = tot.sort_values("votes", ascending=False).groupby("race_id").head(2)
    ok = top2.groupby("race_id").bucket.apply(lambda b: set(b) == {"D", "R"})
    skipped = c[~c.race_id.isin(ok[ok].index)].drop_duplicates("race_id")
    note("results: races not Democrat-vs-Republican at the top (left out of shift comparisons): "
         + (", ".join(sorted(skipped.election_name)) or "none"))
    return set(ok[ok].index)


def county_table(c: pd.DataFrame) -> pd.DataFrame:
    """Sum votes to race x county x party bucket."""
    idx = ["race_id", "election_name", "state", "office", "special", "county_fips"]
    pr = c.groupby(idx).agg(pct_reporting=("region_pct_reporting", "median"))
    v = (c.pivot_table(index=idx, columns="bucket", values="votes", aggfunc="sum", fill_value=0)
         .reindex(columns=["D", "R", "O"], fill_value=0))
    out = v.join(pr).reset_index().rename(columns={"D": "dem_votes", "R": "rep_votes", "O": "other_votes"})
    out["total_votes"] = out[["dem_votes", "rep_votes", "other_votes"]].sum(axis=1)
    out["margin_2026"] = (out.dem_votes - out.rep_votes) / out.total_votes  # + = D lead
    out["d_vs_r_race"] = out.race_id.isin(d_vs_r_races(c))
    return out


def pick_one_race_per_state(t: pd.DataFrame) -> pd.DataFrame:
    """Senate (regular before special) if the state has one, otherwise governor."""
    order = t.assign(rank=t.office.map({"SEN": 0, "GOV": 1}) * 2 + t.special.astype(int))
    best = order.sort_values("rank").drop_duplicates("state")[["state", "race_id"]]
    return t.merge(best, on=["state", "race_id"])


def main() -> None:
    raw = load_civic()
    c = attach_fips(keep_one_level(raw))
    t = county_table(c)
    check_against_state_totals(raw, t)
    t.to_csv(CLEAN / "county_results_2026.csv", index=False)
    note(f"results: {t.race_id.nunique()} races, {t.county_fips.nunique()} counties, "
         f"{int(t.total_votes.sum()):,} votes across all Senate + governor races")

    m = pick_one_race_per_state(t)
    base = pd.read_csv(RAW / "tonmcg" / "2024_US_County_Level_Presidential_Results.csv", dtype={"county_fips": str})
    base = base.assign(margin_2024=(base.votes_dem - base.votes_gop) / base.total_votes,
                       total_votes_2024=base.total_votes)[["county_fips", "margin_2024", "total_votes_2024"]]
    geo = gazetteer("counties").rename(columns={"GEOID": "county_fips", "NAME": "county_name",
                                                "INTPTLAT": "lat", "INTPTLONG": "lon"})
    m = (m.merge(base, on="county_fips", how="left")
          .merge(geo[["county_fips", "county_name", "lat", "lon", "ALAND_SQMI"]], on="county_fips", how="left"))
    m["shift_vs_2024"] = m.margin_2026 - m.margin_2024  # + = moved toward D since 2024
    m["turnout_vs_2024"] = m.total_votes / m.total_votes_2024
    m.to_csv(CLEAN / "county_map_2026.csv", index=False)

    no_base = m.margin_2024.isna().sum()
    note(f"map: {len(m)} counties in {m.state.nunique()} states; {no_base} have no 2024 baseline match")
    missing_states = sorted(STATES - set(m.state))
    note(f"map: states with no Senate or governor race in the data: {', '.join(missing_states) or 'none'}")
    low = m.groupby("state").pct_reporting.median()
    note("map: states under 95% reporting (median county): "
         + ", ".join(f"{s} {v:.0f}%" for s, v in low[low < 95].sort_values().items()))


if __name__ == "__main__":
    main()
