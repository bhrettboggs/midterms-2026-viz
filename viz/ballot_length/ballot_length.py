"""What was on the November 3, 2026 ballot besides Congress: every tracked race as a square.

Reads  data/raw/civicapi/races.csv
Writes viz/ballot_length/ballot_length.png

One square = 25 races, grouped by level of government from the top of the ballot down.
civicAPI tracks more local races in some states than others, so local counts are a floor:
the share for Congress is an upper bound.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import FIGSIZE, INK, INK_2, SURFACE, footer, setup, titles  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data" / "raw"
STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY "
             "NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
PER_SQUARE = 25
COLS = 32

# Ballot order, reference categorical palette in slot order (+ a neutral for the catch-all).
LEVELS = [
    ("Congress", "#2a78d6"), ("Statewide offices", "#eb6834"), ("State legislature", "#1baf7a"),
    ("Judges", "#eda100"), ("County offices", "#e87ba4"), ("City, town & township", "#008300"),
    ("School boards", "#6250d6"), ("Ballot measures", "#e34948"), ("Special districts & other", "#a3a29c"),
]


def level(race_type: str, election_type: str, name: str) -> str:
    t, n = str(race_type).lower(), str(name).lower()
    if t in ("us senate", "house of representatives"):
        return "Congress"
    if t in ("state house", "state senate"):
        return "State legislature"
    if t == "referendum":
        return "Ballot measures"
    if "school" in t or "school" in n:
        return "School boards"
    if any(k in t or k in n for k in ("judic", "judge", "magistrate", "justice of the peace", "court")):
        return "Judges"
    if election_type == "Statewide":
        return "Statewide offices"
    if any(k in n for k in ("town", "township", "city", "mayor", "council", "village", "alderman")) or any(
            k in t for k in ("city", "mayor", "township", "alderman", "neighborhood", "village", "local")):
        return "City, town & township"
    if any(k in t or k in n for k in ("county", "sheriff", "coroner", "assessor", "auditor", "district attorney",
                                      "clerk", "treasurer", "constable", "recorder")):
        return "County offices"
    return "Special districts & other"


def main() -> None:
    setup()
    r = pd.read_csv(RAW / "civicapi" / "races.csv", low_memory=False).drop_duplicates("race_id")
    r = r[r.state.isin(STATES) & ~r.election_type.str.contains("Primary|Runoff", case=False, na=False)]
    r["level"] = [level(t, e, n) for t, e, n in zip(r.type, r.election_type, r.election_name)]
    counts = r.level.value_counts().reindex([n for n, _ in LEVELS]).fillna(0).astype(int)
    total = counts.sum()
    congress_share = counts["Congress"] / total

    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    ax = fig.add_axes([0.05, 0.11, 0.92, 0.70])
    ax.set_aspect("equal")
    ax.axis("off")

    # Each level starts on a fresh row, with one empty row between levels; its label sits beside it.
    row = 0
    for name, color in LEVELS:
        n = int(round(counts[name] / PER_SQUARE)) or 1
        for k in range(n):
            rr, cc = divmod(k, COLS)
            ax.add_patch(plt.Rectangle((cc, -(row + rr)), 0.82, 0.82, fc=color, ec="none"))
        block_rows = (n - 1) // COLS + 1
        mid = -(row + (block_rows - 1) / 2) + 0.41
        c = counts[name]
        ax.text(COLS + 1.2, mid, name, fontsize=14, color=INK, va="center", weight="semibold")
        ax.text(COLS + 25, mid, f"{c:,}  ·  {c / total:.1%}", fontsize=13.5, color=INK_2, va="center",
                ha="right")
        row += block_rows + 1
    ax.set_xlim(-0.3, COLS + 25.3)
    ax.set_ylim(-row + 0.6, 1.2)

    titles(fig, f"Congress was only about {congress_share:.0%} of the",
           "races on the 2026 ballot",
           f"Every race tracked on the November 3, 2026 general-election ballot — {total:,} in all —\n"
           f"grouped by level of government. One square = {PER_SQUARE} races.")
    footer(fig, [
        "civicAPI tracks local races fully in some states and partly in others, so local counts are a floor and",
        f"Congress's {congress_share:.1%} is an upper bound. Each race appears only on the ballots of the voters it covers.",
    ], "civicAPI (Nov 3, 2026 general election; primaries and runoffs removed)")

    out = HERE / "ballot_length.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}  total {total:,}; " + ", ".join(f"{k} {v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
