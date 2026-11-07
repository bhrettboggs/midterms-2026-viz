# 2026 Midterms, Visualized

Unusual views of the November 3, 2026 U.S. midterm elections, built from public data:

| # | Visual | Question | Status |
|---|--------|----------|--------|
| 1 | **What the market expected** | How did prediction-market odds for House and Senate control move over 15 months, and where did they end up relative to the result? | data ready |
| 2 | **Where the Senate money went** | Where did Senate campaign money come from, where did it go, and how much outside money flowed around the campaigns? | data ready |
| 3 | **Money per vote** | How much was spent around each Senate race for every vote cast? | data ready |
| 4 | **Counties as circles sized by votes** | Which way did each county move since 2024, sized by how many people actually voted? | data ready |

## Repo layout

```
data/raw/      source files exactly as downloaded (see SOURCES.md)
data/clean/    tidy tables the visuals read from, plus CHECKS.md
pipeline/      cleaning scripts; run_all.py runs everything
viz/           one folder per visual
```

## Rebuild the clean data

```bash
pip install -r requirements.txt
cd pipeline
python run_all.py
```

`run_all.py` writes every table in `data/clean/` and a `CHECKS.md` report: match rates, rows dropped and why, and cross-checks between sources.

## What the cleaning handles

- **Junk FEC filings.** The FEC outside-spending file includes 15 nonsense entries of $1 billion to $9 billion each ($37.5 billion in total). Single expenditures over $100 million are dropped and logged in `ie_dropped_junk.csv`. Each transaction keeps only its latest amendment, and rows repeated between 24-hour and quarterly reports are collapsed. Result: $42.8 billion raw becomes $3.67 billion.
- **Double-reported votes.** civicAPI reports some states at two levels at once: counties and towns (New England), boroughs and house districts (Alaska), and old counties and planning regions (Connecticut). Each state uses exactly one level so no vote is counted twice.
- **Candidate matching.** Ballot names are matched to FEC IDs by state and surname, ignoring accents. That catches "Luján" and two-word surnames like "Fetty Anderson". 71 of the 72 Senate candidates with at least 5% of the vote are matched; the one gap never filed with the FEC.
- **Thin prediction markets.** Polymarket outcomes are put on a full daily calendar. Gaps are filled from the last real price, and each day is rescaled so the outcomes sum to 100%.

## Known limits

- Results are **unofficial** until states certify (late November to mid-December 2026). Re-run the pipeline then.
- Campaign money runs through each candidate's pre-general FEC report (mid-October) and includes primary spending.
- Alaska has no 2024 county-level presidential baseline, so it has no "shift since 2024".
- Cross-check against pushbuild: three of 33 state races differ by more than 2%.
  - Colorado: pushbuild's snapshot had only about 22% reporting.
  - Vermont governor: the pushbuild total is exactly double the county sum, which points to a duplicated statewide row.
  - California: counting is still ongoing.
- Prediction-market prices show what traders expected. They are not polls, and one election can't show whether markets are "accurate".

## Sources

See [SOURCES.md](SOURCES.md). Election results by [civicAPI](https://civicapi.org) and [pushbuild](https://github.com/pushbuild/us-2026-election-results); turnout by Michael McDonald, [UF Election Lab](https://election.lab.ufl.edu); campaign finance from the [FEC](https://www.fec.gov/data/browse-data/?tab=bulk-data).
