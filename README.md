# 2026 Midterms, Visualized

Unusual views of the November 3, 2026 U.S. midterm elections, built from public data:

| Visual | Finding |
|--------|---------|
| [What the market expected](viz/market_expectations/senate_seats_heatmap.png) | Polymarket's top pick for Republican Senate seats from March onward was the range the result landed in, but it stayed under 50% until Election Day. |
| [Where the Senate money went](viz/senate_money_flow/money_flow.png) | Democratic Senate campaigns raised 2.3× more than Republican ones; outside groups spent almost evenly ($748M vs $760M). |
| [Money per vote](viz/money_per_vote/money_per_vote.png) | Races decided by under 7 points drew a median $78 per vote, against $7 in races decided by 15+. |
| [Counties as circles sized by votes](viz/vote_circles/vote_circles.png) | 95% of counties moved toward Democrats compared with the 2024 presidential vote (different offices, so candidate effects are included). |

| [Congress was ~1% of the ballot](viz/ballot_length/ballot_length.png) | Of 39,430 races tracked on Nov 3, 470 were for Congress; city, town and township races were 40%. |
| [236 years of midterm turnout](viz/turnout_history/turnout_history.png) | The 2026 early estimate (49.1%) is the second-highest midterm turnout since 1914, behind only 2018. |
| [Ticket splitting](viz/ticket_splitting/ticket_splitting.png) | Of 23 states with both a Senate and a governor race, South Carolina and New Hampshire have different parties leading each. |
| [When outside money arrived](viz/outside_money_timing/outside_money_timing.png) | 60% of dated outside spending in Senate races landed in the final 30 days, on both sides. |
| [Turnout change by state](viz/turnout_change/turnout_change.png) | Compared with 2022, turnout rose in 34 states and fell in 17 (early estimates). |
| [Close House races](viz/house_close_races/house_close_races.png) | 25 U.S. House races are within 2 points, 12 within 1, with counting still going. |
| [Did turnout decide the swing?](viz/turnout_vs_shift/turnout_vs_shift.png) | Within each state, counties where turnout fell off most moved only ~1.3 points more than counties where it held up, against a ~15-point swing. |

![What the market expected](viz/market_expectations/senate_seats_heatmap.png)
![Where the Senate money went](viz/senate_money_flow/money_flow.png)
![Money per vote](viz/money_per_vote/money_per_vote.png)
![Counties as circles sized by votes](viz/vote_circles/vote_circles.png)
![Congress was ~1% of the ballot](viz/ballot_length/ballot_length.png)
![236 years of midterm turnout](viz/turnout_history/turnout_history.png)
![Ticket splitting](viz/ticket_splitting/ticket_splitting.png)
![When outside money arrived](viz/outside_money_timing/outside_money_timing.png)
![Turnout change by state](viz/turnout_change/turnout_change.png)
![Close House races](viz/house_close_races/house_close_races.png)
![Did turnout decide the swing?](viz/turnout_vs_shift/turnout_vs_shift.png)

## Repo layout

```
data/raw/      source files exactly as downloaded (see SOURCES.md)
data/clean/    tidy tables the visuals read from, plus CHECKS.md
pipeline/      cleaning scripts; run_all.py runs everything
viz/           one folder per visual
```

## Rebuild everything

```bash
pip install -r requirements.txt
cd pipeline && python run_all.py && cd ..
python viz/market_expectations/senate_seats_heatmap.py
python viz/senate_money_flow/money_flow.py
python viz/money_per_vote/money_per_vote.py
python viz/vote_circles/vote_circles.py
python viz/ballot_length/ballot_length.py
python viz/turnout_history/turnout_history.py
python viz/ticket_splitting/ticket_splitting.py
python viz/outside_money_timing/outside_money_timing.py
python viz/turnout_change/turnout_change.py
python viz/house_close_races/house_close_races.py
python viz/turnout_vs_shift/turnout_vs_shift.py
```

The charts use the Inter font. If it isn't installed, matplotlib falls back to its default font.

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
