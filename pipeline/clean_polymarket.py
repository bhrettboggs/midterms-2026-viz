"""Polymarket daily prices -> clean probability series.

Input
  data/raw/polymarket/daily.csv   one row per market outcome per day (price of the "Yes" share)

Outputs (data/clean/)
  pm_balance_of_power.csv   daily probability of each House/Senate control combination (sums to 1)
  pm_senate_seats.csv       daily probability of each Republican Senate seat bracket (sums to 1)
  pm_uncertainty.csv        daily entropy of both series (0 = market certain, higher = unsure)

Cleaning: thin markets skip days and quote prices that don't add up to 100%, so each series
is put on a full daily calendar, gaps are carried forward from the last real price, and
each day is rescaled so the outcomes sum to exactly 1.
"""
import numpy as np
import pandas as pd

from common import CLEAN, RAW, note

SEAT_ORDER = ["≤47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57+"]


def tidy(p: pd.DataFrame, event_prefix: str, order: list[str] | None = None) -> pd.DataFrame:
    d = p[p.event.str.startswith(event_prefix)]
    wide = d.pivot_table(index="date", columns="outcome_label", values="price", aggfunc="last")
    wide.index = pd.to_datetime(wide.index)
    wide = wide.reindex(pd.date_range(wide.index.min(), wide.index.max(), freq="D")).ffill()
    if order:
        wide = wide[[c for c in order if c in wide.columns]]
    raw_sum = wide.sum(axis=1)
    off = ((raw_sum - 1).abs() > 0.05).mean()
    note(f"polymarket '{event_prefix}': {len(wide)} days, {wide.shape[1]} outcomes; "
         f"{off:.0%} of days summed more than 5 points away from 100% before rescaling")
    return wide.div(raw_sum, axis=0).rename_axis("date")


def entropy(wide: pd.DataFrame) -> pd.Series:
    p = wide.clip(lower=1e-9)
    return -(p * np.log2(p)).sum(axis=1)


def main() -> None:
    p = pd.read_csv(RAW / "polymarket" / "daily.csv")
    bop = tidy(p, "Balance of Power")
    seats = tidy(p, "Republican Senate seats", SEAT_ORDER)
    bop.to_csv(CLEAN / "pm_balance_of_power.csv")
    seats.to_csv(CLEAN / "pm_senate_seats.csv")
    pd.DataFrame({"balance_of_power_bits": entropy(bop), "senate_seats_bits": entropy(seats)}).to_csv(
        CLEAN / "pm_uncertainty.csv", index_label="date")

    moves = bop.diff().abs().max(axis=1).nlargest(5)
    note("polymarket: biggest one-day swings in any balance-of-power outcome: "
         + ", ".join(f"{d:%Y-%m-%d} ({v:.0%})" for d, v in moves.items())
         + " — confirm what happened on these dates before labeling them")


if __name__ == "__main__":
    main()
