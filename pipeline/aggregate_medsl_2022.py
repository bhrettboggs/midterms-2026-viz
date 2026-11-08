"""Build the 2022 county-level Senate and governor baseline from MEDSL's precinct returns.

The MIT Election Data and Science Lab publishes precinct-level 2022 general-election returns for
every state (github.com/MEDSL/2022-elections-official, one zip per state, ~2 GB unzipped). This
script boils them down to one small file the pipeline can keep in the repo:

  data/raw/medsl/county_sen_gov_2022.csv   state, office, county_fips, county_name, D/R/other/total votes

Usage
  git clone --depth 1 https://github.com/MEDSL/2022-elections-official
  python pipeline/aggregate_medsl_2022.py 2022-elections-official/individual_states

Rules (see MEDSL's README warnings about modes and tally rows)
  * Only US SENATE and GOVERNOR, general-election stage (GEN); Georgia's Senate runoff is left out.
  * Vote modes: within each precinct, if a TOTAL mode is reported only TOTAL rows are used; otherwise
    the separate modes (ABSENTEE, ELECTION DAY, ...) are summed once.
  * Tally rows that are not candidates (BALLOTS CAST, PUBLIC COUNTER, UNDERVOTES, BLANK VOTES ...)
    are dropped. Write-ins and scattering count as "other".
  * "Precincts" that are really county aggregates (Idaho's COUNTY TOTAL rows duplicate every precinct)
    are dropped when the county's other rows add up to the same votes (within 2%); otherwise kept,
    since a lone county-level row is the only data for that county.
  * Party is assigned per candidate, not per ballot line, so fusion votes (Hochul on the Working
    Families line, Zeldin on the Conservative line) go to the candidate's major party. Any party
    label containing DEM (DEMOCRAT, DFL, DEMOCRATIC-NPL, DEM/PROG) is D; REPUBLICAN is R.
  * New Mexico's file has no party labels; its governor candidates are assigned from the ballot. Wyoming's
    file labels the Democratic nominee for governor (Theresa Livingston) Libertarian; corrected by hand.
  * Rows aggregated above the county level (no county code, or a FLOATING county) are kept in an
    "unassigned" row per race so nothing is silently dropped.
"""
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

OFFICES = {"US SENATE", "GOVERNOR"}
COLS = ["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips",
        "candidate", "state_po", "stage", "special"]
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "medsl" / "county_sen_gov_2022.csv"
TALLY = re.compile(r"BALLOTS CAST|CAST VOTES|^TOTAL$|PUBLIC COUNTER|UNDER ?VOTES?|OVER ?VOTES?|BLANK|NOT QUALIFIED|"
                   r"^ABSENTEE|^AFFIDAVIT|REGISTERED|TIMES COUNTED|VOID|^UNASSIGNED|UNRESOLVED|^NONE OF", re.I)
HAND_PARTY = {("NM", "GOVERNOR", "MICHELLE LUJAN GRISHAM"): "D", ("NM", "GOVERNOR", "MARK V RONCHETTI"): "R",
              ("WY", "GOVERNOR", "THERESA A LIVINGSTON"): "D"}


def load_state(path: Path) -> pd.DataFrame:
    """Read one state's zip (or csv) and keep Senate + governor general-election rows."""
    def read(fh):
        parts = []
        for chunk in pd.read_csv(fh, usecols=COLS, dtype=str, chunksize=500_000, low_memory=False):
            parts.append(chunk[chunk.office.isin(OFFICES) & chunk.stage.str.upper().eq("GEN")])
        return pd.concat(parts, ignore_index=True)

    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv") and not n.startswith("__MACOSX")]
            frames = [read(z.open(n)) for n in names]
        return pd.concat(frames, ignore_index=True)
    return read(path)


def party_of(detailed, simplified) -> str:
    p = f"{detailed} {simplified}".upper()
    if "DEM" in p:
        return "D"
    if "REPUBLICAN" in p:
        return "R"
    return "O"


def aggregate(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["votes"] = pd.to_numeric(d.votes, errors="coerce").fillna(0)
    d["mode"] = d["mode"].fillna("TOTAL").str.upper()
    d["candidate"] = d.candidate.fillna("").str.upper().str.strip()
    d = d[~d.candidate.str.contains(TALLY)]
    d["office"] = d.office.map({"US SENATE": "SEN", "GOVERNOR": "GOV"})
    d["special"] = d.special.astype(str).str.upper().eq("TRUE")
    d["county_fips"] = d.county_fips.astype(str).str.zfill(5)
    d.loc[~d.county_fips.str.fullmatch(r"\d{5}") | d.county_name.str.contains("FLOATING", na=False), "county_fips"] = "unassigned"
    d["precinct"] = d.precinct.fillna("")

    # County-aggregate rows masquerading as precincts: drop when redundant with the real precincts.
    agg_like = d.precinct.str.upper().str.contains(r"TOTAL|CUMULATIVE|ALL PRECINCTS|^SUMMARY", regex=True)
    cty = ["state_po", "office", "special", "county_fips"]
    agg_sum = d[agg_like].groupby(cty).votes.sum()
    rest_sum = d[~agg_like].groupby(cty).votes.sum()
    both = pd.concat([agg_sum.rename("agg_votes"), rest_sum.rename("rest_votes")], axis=1).dropna()
    redundant = both[(both.agg_votes - both.rest_votes).abs() <= 0.02 * both.rest_votes].index
    drop = agg_like & d.set_index(cty).index.isin(redundant)
    if drop.any():
        print(f"   dropped {int(drop.sum()):,} county-aggregate rows ({int(d[drop].votes.sum()):,} votes) that duplicated precincts")
    d = d[~drop]

    # Party per candidate (so every ballot line of a fusion candidate counts for their major party).
    line_party = [party_of(a, b) for a, b in zip(d.party_detailed, d.party_simplified)]
    d["bucket"] = line_party
    key = ["state_po", "office", "candidate"]
    for b in ("D", "R"):
        who = d[d.bucket == b][key].drop_duplicates()
        d.loc[d.set_index(key).index.isin(who.set_index(key).index), "bucket"] = b
    for (st, off, cand), b in HAND_PARTY.items():
        d.loc[(d.state_po == st) & (d.office == {"GOVERNOR": "GOV", "US SENATE": "SEN"}[off]) & (d.candidate == cand), "bucket"] = b

    # Within each precinct, TOTAL rows win over split modes.
    grp = ["state_po", "office", "special", "county_fips", "precinct"]
    has_total = d.assign(t=d["mode"].eq("TOTAL")).groupby(grp).t.transform("any")
    d = d[(d["mode"] == "TOTAL") == has_total]

    piv = (d.pivot_table(index=["state_po", "office", "special", "county_fips"], columns="bucket", values="votes",
                         aggfunc="sum", fill_value=0).reindex(columns=["D", "R", "O"], fill_value=0))
    names = d.groupby(["state_po", "office", "special", "county_fips"]).county_name.first()
    modes = d.groupby(["state_po", "office", "special", "county_fips"])["mode"].apply(lambda m: ";".join(sorted(set(m))))
    res = piv.join(names).join(modes).reset_index().rename(
        columns={"state_po": "state", "D": "dem_votes", "R": "rep_votes", "O": "other_votes", "mode": "modes"})
    res["total_votes"] = res[["dem_votes", "rep_votes", "other_votes"]].sum(axis=1)
    return res[["state", "office", "special", "county_fips", "county_name", "dem_votes", "rep_votes", "other_votes",
                "total_votes", "modes"]]


def main(folder: str) -> None:
    files = sorted(p for p in Path(folder).iterdir() if p.suffix in (".zip", ".csv"))
    frames = []
    for p in files:
        d = load_state(p)
        print(f"{p.name}: {len(d):,} Senate/governor precinct rows")
        if len(d):
            frames.append(aggregate(d))
    res = pd.concat(frames, ignore_index=True)
    res = res[res.total_votes > 0]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT, index=False)
    print(f"wrote {OUT}: {len(res):,} county rows, {res.state.nunique()} states, "
          f"{int(res.total_votes.sum()):,} votes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2022-elections-official/individual_states")
