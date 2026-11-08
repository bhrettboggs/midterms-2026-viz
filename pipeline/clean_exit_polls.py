"""National exit polls by demographic group, 1996-2026, harmonized to groups that exist every year.

Inputs
  data/raw/exit_polls/roper_how_groups_voted_1996_2024.csv   presidential vote (Roper Center "How Groups Voted")
  data/raw/exit_polls/wikipedia_house_exit_polls_2006_2026.csv midterm U.S. House vote (network exit polls,
                                                               as compiled on Wikipedia)
Output
  data/clean/exit_poll_groups.csv   year, election (President / House midterm), dimension, group,
                                    dem %, rep %, share of voters %, margin (D minus R, points)

Harmonizing: exit polls change their brackets over time, so
  age     -> 18-29 and 65+ (sub-brackets like 18-24 + 25-29 are combined, weighted by share of voters)
  income  -> under $50K and $100K+ (nominal dollars; brackets that straddle a cut-off are left out)
  race    -> White, Black, Hispanic/Latino, Asian
"""
import re

import numpy as np
import pandas as pd

from common import CLEAN, RAW, note


def money(s: str) -> float:
    s = s.replace(",", "")
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", s)]
    # Roper writes "$15-29,999": the first number is in thousands.
    return [n * 1000 if n < 1000 else n for n in nums]


def income_bucket(label: str) -> str | None:
    s = label.lower()
    nums = money(label)
    if not nums:
        return None
    if any(k in s for k in ("under", "less than", "<")):
        lo, hi = 0, nums[0]
    elif any(k in s for k in ("over", "more", "& over", "+")):
        lo, hi = nums[0], np.inf
    elif len(nums) >= 2:
        lo, hi = nums[0], nums[1]
    else:
        return None
    if hi <= 50_000:
        return "Under $50K"
    if lo >= 100_000:
        return "$100K+"
    return None


def age_bucket(label: str) -> str | None:
    s = label.replace("–", "-")
    nums = [int(n) for n in re.findall(r"\d+", s)]
    if not nums:
        return None
    if any(k in s.lower() for k in ("over", "older", "+")):
        return "65+" if nums[0] >= 60 else None
    if len(nums) >= 2 and nums[0] >= 18 and nums[1] <= 29:
        return "18-29"
    return None


RACE = {"white": "White", "african-american": "Black", "black": "Black", "hispanic": "Hispanic/Latino",
        "latino": "Hispanic/Latino", "hispanic (of any race)": "Hispanic/Latino", "asian": "Asian"}


def classify(dim: str, group: str) -> tuple[str, str] | None:
    d, g = dim.lower(), group.strip()
    if d in ("sex", "gender"):
        return ("Gender", g.title()) if g.lower() in ("men", "women") else None
    if d.startswith("race"):
        return ("Race", RACE[g.lower()]) if g.lower() in RACE else None
    if d == "age":
        b = age_bucket(g)
        return ("Age", b) if b else None
    if "income" in d and "by" not in d:
        b = income_bucket(g)
        return ("Income", b) if b else None
    return None


def tidy(df: pd.DataFrame, election: str) -> pd.DataFrame:
    rows = []
    for r in df.itertuples():
        c = classify(str(r.dim), str(r.group))
        if c and pd.notna(r.dem) and pd.notna(r.gop):
            rows.append(dict(year=r.year, election=election, dimension=c[0], group=c[1], dem=float(r.dem),
                             rep=float(r.gop), share=float(r.share) if pd.notna(r.share) else np.nan))
    t = pd.DataFrame(rows)
    # Combine sub-brackets (e.g. 18-24 + 25-29) weighted by their share of voters.
    def combine(g: pd.DataFrame) -> pd.Series:
        w = g.share.fillna(1)
        return pd.Series({"dem": np.average(g.dem, weights=w), "rep": np.average(g.rep, weights=w),
                          "share": g.share.sum(min_count=1), "pieces": len(g)})
    return t.groupby(["year", "election", "dimension", "group"]).apply(combine, include_groups=False).reset_index()


def main() -> None:
    roper = pd.read_csv(RAW / "exit_polls" / "roper_how_groups_voted_1996_2024.csv")
    roper = roper.rename(columns={"type": "dim", "col1": "dem", "col2": "gop"})
    for c in ("dem", "gop", "share"):
        roper[c] = pd.to_numeric(roper[c], errors="coerce")
    pres = tidy(roper, "President")

    wiki = pd.read_csv(RAW / "exit_polls" / "wikipedia_house_exit_polls_2006_2026.csv").rename(columns={"section": "dim"})
    for c in ("dem", "gop", "share"):
        wiki[c] = pd.to_numeric(wiki[c].astype(str).str.replace("%", ""), errors="coerce")
    house = tidy(wiki.dropna(subset=["dim"]), "House midterm")

    out = pd.concat([pres, house], ignore_index=True)
    out["margin"] = out.dem - out.rep
    out = out.sort_values(["dimension", "group", "year"])
    out.to_csv(CLEAN / "exit_poll_groups.csv", index=False)

    cover = out.groupby(["dimension", "group"]).year.apply(lambda y: f"{len(y)} elections").to_dict()
    note("exit polls: " + "; ".join(f"{k[0]}/{k[1]}: {v}" for k, v in cover.items()))
    if (out[(out.dimension == "Age") & (out.group == "65+") & (out.year == 2006)].shape[0]):
        note("exit polls: 2006 has no 65+ bracket; its '60 and older' row is used for 65+")


if __name__ == "__main__":
    main()
