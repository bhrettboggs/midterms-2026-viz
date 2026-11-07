"""Shared paths and helpers for the cleaning pipeline."""
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

# The 50 states + DC. Territories and the national roll-up rows are dropped.
STATES = set(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO "
    "MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
)

# Notes collected while cleaning; checks.py writes them to data/clean/CHECKS.md.
NOTES: list[str] = []


def note(msg: str) -> None:
    print(msg)
    NOTES.append(msg)


def party_bucket(party: str) -> str:
    """Collapse party labels to D / R / other. DFL counts as D."""
    p = str(party).lower()
    if "democrat" in p or "dfl" in p or "farmer-labor" in p:
        return "D"
    if "republican" in p:
        return "R"
    return "O"


def norm_place(name: str) -> str:
    """Normalize a town/county name so civicAPI and Census spellings line up."""
    n = str(name).lower()
    n = re.sub(r"\b(town city|city|town|township|plantation|county|parish|borough|census area|"
               r"planning region|municipality|unorganized territory|gore|grant|location|purchase)\b", "", n)
    n = n.replace("saint ", "st ").replace("st. ", "st ").replace(".", "")
    return re.sub(r"[^a-z]", "", n)


def gazetteer(kind: str) -> pd.DataFrame:
    """Census 2024 Gazetteer: kind = 'counties' or 'cousubs'."""
    df = pd.read_csv(RAW / "census" / f"2024_Gaz_{kind}_national.txt", sep="\t", dtype={"GEOID": str})
    df.columns = df.columns.str.strip()
    return df
