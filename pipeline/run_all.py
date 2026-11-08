"""Run every cleaning step, cross-check the outputs, and write data/clean/CHECKS.md."""
import glob
import re
from datetime import datetime

import pandas as pd

import clean_baseline_2022
import clean_exit_polls
import clean_money
import clean_polymarket
import clean_results
import clean_turnout
from common import CLEAN, NOTES, RAW, note


def state_party_code(party) -> str:
    """Pushbuild keeps each state's own party codes: 'D', 'Dem', 'DEM', 'DEMOCRATIC', 'DFL', 'DEM/PROG',
    'DEM/NON' (Alaska fusion labels), 'R', 'Rep', 'REPUBLICAN'... Any slash-separated piece that starts
    with 'dem' (or is 'd'/'dfl') counts as Democratic; 'rep' or 'r' as Republican."""
    parts = re.split(r"[/\s]+", str(party).strip().lower())
    if any(t.startswith("dem") or t in ("d", "dfl") for t in parts):
        return "D"
    if any(t.startswith("rep") or t == "r" for t in parts):
        return "R"
    return "O"


def cross_check_pushbuild() -> None:
    """Compare civicAPI-based totals AND margins with pushbuild's copy of the official state feeds.

    Contest names vary by state ("U.S.  Senate", "Senator in Congress", "Governor / Lt. Governor",
    "FOR GOVERNOR"), so the patterns are deliberately loose; the matched names are written to the
    cross-check table so they can be eyeballed."""
    pb = pd.concat(pd.read_csv(f, low_memory=False) for f in glob.glob(str(RAW / "pushbuild" / "*.csv")))
    pb = pb[pb.level == "state"].copy()
    name = pb.contest.astype(str)
    pb["office"] = None
    pb.loc[name.str.contains(r"u\.?\s*s\.?\s+senat|united states senat|senator in congress", case=False, regex=True),
           "office"] = "SEN"
    pb.loc[name.str.fullmatch(r"(?i)(?:for )?governor(?:\s*(?:/|and|&)\s*(?:lieutenant|lt\.?)\s*governor)?"), "office"] = "GOV"
    pb = pb.dropna(subset=["office"])
    pb["bucket"] = pb.party.map(state_party_code)
    agg = pb.groupby(["state", "office", "bucket"]).votes.sum().unstack("bucket").fillna(0)
    agg["pb_votes"] = agg.sum(axis=1)
    agg["pb_margin"] = (agg.get("D", 0) - agg.get("R", 0)) / agg.pb_votes * 100
    contests = pb.groupby(["state", "office"]).contest.first()

    ours = pd.read_csv(CLEAN / "county_results_2026.csv")
    ours = (ours.groupby(["state", "office", "special", "race_id"])[["dem_votes", "rep_votes", "total_votes"]].sum()
            .reset_index().sort_values("special").drop_duplicates(["state", "office"]).set_index(["state", "office"]))
    ours["our_margin"] = (ours.dem_votes - ours.rep_votes) / ours.total_votes * 100
    both = agg[["pb_votes", "pb_margin"]].join(ours[["total_votes", "our_margin"]], how="inner").join(contests)
    both["vote_ratio"] = both.total_votes / both.pb_votes
    both["margin_diff_pts"] = both.our_margin - both.pb_margin
    off_v = both[(both.vote_ratio - 1).abs() > 0.02]
    off_m = both[both.margin_diff_pts.abs() > 1]
    note(f"cross-check: {len(both)} state races appear in both civicAPI and pushbuild; "
         f"{len(off_v)} differ in total votes by more than 2%"
         + (": " + ", ".join(f"{s} {o} ({r - 1:+.1%})" for (s, o), r in off_v.vote_ratio.items()) if len(off_v) else "")
         + f"; {len(off_m)} differ in D-minus-R margin by more than 1 point"
         + (": " + ", ".join(f"{s} {o} ({d:+.1f})" for (s, o), d in off_m.margin_diff_pts.items()) if len(off_m) else ""))
    both.round(3).to_csv(CLEAN / "crosscheck_pushbuild.csv")


def main() -> None:
    for step in (clean_results, clean_baseline_2022, clean_money, clean_polymarket, clean_turnout, clean_exit_polls):
        print(f"\n== {step.__name__} ==")
        step.main()
    print("\n== cross-checks ==")
    cross_check_pushbuild()

    lines = ["# Pipeline checks", "",
             f"Generated {datetime.now():%Y-%m-%d %H:%M} by `pipeline/run_all.py`. "
             "Results are unofficial until states certify; re-run after certification.", ""]
    lines += [f"- {n}" for n in NOTES]
    (CLEAN / "CHECKS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {CLEAN / 'CHECKS.md'}")


if __name__ == "__main__":
    main()
