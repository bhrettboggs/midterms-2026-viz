# 2026 Midterms, Visualized

Unusual views of the November 3, 2026 U.S. midterm elections, built from public data:

| Visual | Finding |
|--------|---------|
| [What the market expected](viz/market_expectations/senate_seats_heatmap.png) | Polymarket's top pick for Republican Senate seats from March onward was the range the result landed in, but it stayed under 50% until Election Day (prices shown through Nov 3 only). |
| [Where the Senate money went](viz/senate_money_flow/money_flow.png) | Democratic Senate campaigns raised 2.6× more than Republican ones ($713M vs $275M); outside groups spent almost evenly ($772M vs $777M). |
| [Money per vote](viz/money_per_vote/money_per_vote.png) | Races decided by under 7 points drew a median $78 per vote, against $7 in races decided by 15+. |
| [Counties as circles sized by votes](viz/vote_circles/vote_circles.png) | 97% of counties moved toward Democrats compared with the 2024 presidential vote (different offices, so candidate effects are included). |
| [Congress was ~1% of the ballot](viz/ballot_length/ballot_length.png) | Of 39,430 races tracked on Nov 3, 470 were for Congress; city, town and township races were 40%. |
| [236 years of midterm turnout](viz/turnout_history/turnout_history.png) | The 2026 early estimate (49.1%) is the second-highest midterm turnout in more than a century: only 2018 (50.0%) was higher among midterms after 1914. |
| [Ticket splitting](viz/ticket_splitting/ticket_splitting.png) | Of 21 states with a Democrat-vs-Republican Senate race and governor race, South Carolina and New Hampshire have different parties leading each. |
| [When outside money arrived](viz/outside_money_timing/outside_money_timing.png) | 60% of dated outside spending in Senate races landed in the final 30 days, on both sides. |
| [Turnout change by state](viz/turnout_change/turnout_change.png) | Compared with 2022, turnout rose in 34 states and fell in 17 (early estimates). |
| [Close House races](viz/house_close_races/house_close_races.png) | 25 U.S. House races are within 2 points, 12 within 1, with counting still going (417 contested districts shown). |
| [Turnout and the swing, county by county](viz/turnout_vs_shift/turnout_vs_shift.png) | Within each state, counties where turnout fell off most moved only ~1.3 points more than counties where it held up, against a ~15-point swing. This rules out a county-to-county turnout story, not a uniform one. |
| [Age, turnout and shift](viz/age_turnout_shift/age_turnout_shift.png) | Within states, the oldest fifth of counties turned out 5 points above average but moved 3 points less toward Democrats; the youngest fifth did the reverse. |
| [Every Senate race at a glance](viz/senate_states_glance/senate_states_glance.png) | Which side outspent didn't track the swing (rank correlation +0.07); lower-turnout states swung more (−0.57), and so did redder states (−0.40). |
| [Odds vs money](viz/money_vs_odds/money_vs_odds.png) | Polymarket's Democratic Senate odds stayed above 50% from Aug 31; Democratic-side outside money first out-spent the Republican side 35 days later. |
| [30 years of how groups vote](viz/demographic_trends/demographic_trends.png) | The income gap has nearly closed: voters earning $100K+ leaned Republican through 2020 and now lean Democratic (D+12), a little less than voters under $50K (D+16). |
| [Which groups moved in 2026](viz/demographic_shift_2026/demographic_shift_2026.png) | Every group in the election-day surveys moved toward Democrats vs. the 2022 midterm; Asian voters (+25), young voters and $100K+ earners (+20 each) moved most. 2026 is The Voter Poll by SSRS, not the Edison exit poll, so part of the change may be method. |

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
![Age, turnout and shift](viz/age_turnout_shift/age_turnout_shift.png)
![Every Senate race at a glance](viz/senate_states_glance/senate_states_glance.png)
![Odds vs money](viz/money_vs_odds/money_vs_odds.png)
![30 years of how groups vote](viz/demographic_trends/demographic_trends.png)
![Which groups moved in 2026](viz/demographic_shift_2026/demographic_shift_2026.png)

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
python viz/age_turnout_shift/age_turnout_shift.py
python viz/senate_states_glance/senate_states_glance.py
python viz/money_vs_odds/money_vs_odds.py
```

The charts use the Inter font. If it isn't installed, matplotlib falls back to its default font.

`run_all.py` writes every table in `data/clean/` and a `CHECKS.md` report: match rates, rows dropped and why, and cross-checks between sources.

## What the cleaning handles

- **Junk FEC filings.** The FEC outside-spending file includes 15 nonsense entries of $1 billion to $9 billion each ($37.5 billion in total). Single expenditures over $100 million are dropped and logged in `ie_dropped_junk.csv`. Each transaction keeps only its latest amendment, and an expenditure repeated in a later filing (a 24-hour report that reappears in a periodic report) is kept once. Result: $42.8 billion raw becomes $3.71 billion. One table, `ie_senate_general.csv`, holds every Senate general-election expenditure with the side it helped, so all the money charts agree.
- **Double-reported votes.** civicAPI reports some states at two levels at once: counties and towns (New England), boroughs and house districts (Alaska), and old counties and planning regions (Connecticut). Each state uses exactly one level so no vote is counted twice.
- **Candidate matching.** Ballot names are matched to FEC IDs by state and surname, ignoring accents. That catches "Luján" and two-word surnames like "Fetty Anderson". When several filers share a surname, the one sharing the most name words wins (Darline Graham, not Lindsey Graham, in South Carolina), and no committee can be matched to two candidates in one race. 71 of the 72 Senate candidates with at least 5% of the vote are matched; the one gap never filed with the FEC.
- **Thin prediction markets.** Polymarket outcomes are put on a full daily calendar. Gaps are filled from the last real price, and each day is rescaled so the outcomes sum to 100%.

## Known limits

- Results are **unofficial** until states certify (late November to mid-December 2026). Re-run the pipeline then.
- Campaign money runs through each candidate's pre-general FEC report (mid-October) and includes primary spending.
- Alaska has no 2024 county-level presidential baseline, so it has no "shift since 2024".
- Cross-check against pushbuild (the official state feeds): 44 Senate and governor races appear in both sources. Every D-minus-R margin agrees within 0.6 points. Four differ in total votes by more than 2%:
  - Colorado: pushbuild's snapshot is about 20% behind civicAPI's count.
  - Vermont governor: the pushbuild total is exactly double the county sum, which points to a duplicated statewide row.
  - California: counting is still ongoing.
- "Shift since 2024" is only computed for races whose top two candidates were a Democrat and a Republican. Montana's Senate race (independent runner-up), Rhode Island's and Wyoming's governor races, and the Idaho, Nebraska and South Dakota Senate races are left out of those comparisons.
- Alaska's results are first-choice votes; both of its statewide races go to ranked-choice tabulation on Nov 18.
- The 2026 demographic figures come from The Voter Poll by SSRS, which replaced the Edison exit poll this cycle; comparisons with earlier exit polls mix two methods.
- Prediction-market prices show what traders expected. They are not polls, and one election can't show whether markets are "accurate".

## Review

[REVIEW.md](REVIEW.md) records a full second pass over the data and charts (November 8, 2026): what was checked, what was wrong, and what changed.

## Sources

See [SOURCES.md](SOURCES.md). Election results by [civicAPI](https://civicapi.org) and [pushbuild](https://github.com/pushbuild/us-2026-election-results); turnout by Michael McDonald, [UF Election Lab](https://election.lab.ufl.edu); campaign finance from the [FEC](https://www.fec.gov/data/browse-data/?tab=bulk-data).
