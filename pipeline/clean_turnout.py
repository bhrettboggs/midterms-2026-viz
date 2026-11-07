"""Turnout: the long national midterm series plus state-level 2022 vs 2026.

Inputs (UF Election Lab, Michael McDonald)
  data/raw/uf/US_VEP_Turnout_Rates_v1.4.csv   national turnout, 1789-2024
  data/raw/uf/Turnout_1980_2022_v1.2.csv      state turnout, 1980-2022
  data/raw/uf/Turnout_2026G_v0.2.csv          2026 initial estimate

Outputs (data/clean/)
  turnout_national_midterms.csv   year, turnout rate (share of eligible voters), is_estimate
  turnout_states_2022_2026.csv    state, 2022 rate, 2026 rate, change in points
"""
import pandas as pd

from common import CLEAN, RAW, note


def pct(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.rstrip("%").str.replace(",", ""), errors="coerce") / 100


def main() -> None:
    nat = pd.read_csv(RAW / "uf" / "US_VEP_Turnout_Rates_v1.4.csv")
    mid = nat[["YEAR", "TURNOUT_RATE_MIDTERM"]].dropna().rename(columns={"YEAR": "year", "TURNOUT_RATE_MIDTERM": "turnout"})
    # The file records 0 for a few early years with no data; those aren't real zeros.
    mid = mid[mid.turnout > 0].assign(is_estimate=False)

    t26 = pd.read_csv(RAW / "uf" / "Turnout_2026G_v0.2.csv")
    us26 = pct(t26.loc[t26.STATE_ABV == "US", "VEP_TURNOUT_RATE"]).iloc[0]
    mid = pd.concat([mid, pd.DataFrame([{"year": 2026, "turnout": us26, "is_estimate": True}])])
    mid.to_csv(CLEAN / "turnout_national_midterms.csv", index=False)
    rank = (mid.turnout > us26).sum()
    note(f"turnout: 2026 national estimate {us26:.1%} (UF v0.2, initial); {rank} earlier midterms were higher")

    st = pd.read_csv(RAW / "uf" / "Turnout_1980_2022_v1.2.csv")
    s22 = st[(st.YEAR == 2022) & (st.STATE_ABV.str.len() == 2)][["STATE_ABV", "VEP_TURNOUT_RATE"]]
    s22 = s22.assign(turnout_2022=pct(s22.VEP_TURNOUT_RATE))[["STATE_ABV", "turnout_2022"]]
    s26 = t26[t26.STATE_ABV != "US"].assign(turnout_2026=lambda d: pct(d.VEP_TURNOUT_RATE))[["STATE_ABV", "turnout_2026"]]
    both = s22.merge(s26, on="STATE_ABV", how="outer").rename(columns={"STATE_ABV": "state"})
    both["change_pts"] = (both.turnout_2026 - both.turnout_2022) * 100
    both.sort_values("change_pts", ascending=False).to_csv(CLEAN / "turnout_states_2022_2026.csv", index=False)
    note(f"turnout: {both.change_pts.notna().sum()} states with both years; "
         f"{(both.change_pts > 0).sum()} up from 2022, {(both.change_pts < 0).sum()} down")


if __name__ == "__main__":
    main()
