"""Run every cleaning step, cross-check the outputs, and write data/clean/CHECKS.md."""
import glob
from datetime import datetime

import pandas as pd

import clean_exit_polls
import clean_money
import clean_polymarket
import clean_results
import clean_turnout
from common import CLEAN, NOTES, RAW, note


def cross_check_pushbuild() -> None:
    """Compare civicAPI-based totals with pushbuild's copy of the official state feeds."""
    pb = pd.concat(pd.read_csv(f, low_memory=False) for f in glob.glob(str(RAW / "pushbuild" / "*.csv")))
    pb = pb[pb.level == "state"]
    pb["office"] = None
    pb.loc[pb.contest.str.contains(r"(?:U\.?S\.?|United States) Senat", case=False, na=False), "office"] = "SEN"
    pb.loc[pb.contest.str.fullmatch(r"(?i)governor(?: and lieutenant governor)?", na=False), "office"] = "GOV"
    pb = pb.dropna(subset=["office"]).groupby(["state", "office"]).votes.sum().rename("pushbuild")

    ours = pd.read_csv(CLEAN / "county_results_2026.csv").groupby(["state", "office"]).total_votes.sum().rename("ours")
    both = pd.concat([pb, ours], axis=1).dropna()
    both["diff"] = both.ours / both.pushbuild - 1
    off = both[both["diff"].abs() > 0.02]
    note(f"cross-check: {len(both)} state races appear in both civicAPI and pushbuild; "
         f"{len(off)} differ by more than 2%"
         + (": " + ", ".join(f"{s} {o} ({d:+.1%})" for (s, o), d in off["diff"].items()) if len(off) else ""))
    both.to_csv(CLEAN / "crosscheck_pushbuild.csv")


def main() -> None:
    for step in (clean_results, clean_money, clean_polymarket, clean_turnout, clean_exit_polls):
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
