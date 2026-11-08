# 2026 Midterms, Visualized

Unusual views of the November 3, 2026 U.S. midterm elections, built from public data. Every chart is a
standalone 1200 × 1500 image with its sources on it; every number comes from `data/clean/`, which
`pipeline/run_all.py` rebuilds from the raw files.

## The swing, like for like

These compare the same office in the same counties four years apart (2022 midterm → 2026 midterm), using
MIT Election Lab's 2022 precinct returns. Unlike a presidential baseline, this holds the office and the
kind of electorate constant.

| Visual | Finding |
|--------|---------|
| [Same office, same counties, four years apart](viz/gov_swing_2022_2026/gov_swing_2022_2026.png) | Governor races moved 12 points toward Democrats from 2022 to 2026 (vote-weighted, 2,002 counties in 31 states); 81% of counties moved that way. Vermont (+40), Alabama, Ohio (+32) and Iowa (+29) moved most, Kansas (−3) and Massachusetts (−2) moved the other way. |
| [Two yardsticks, one swing](viz/two_yardsticks/two_yardsticks.png) | The median state's governor swing is +11 against 2022's governor race and +12 against the 2024 presidential vote, so the national story doesn't depend on the baseline. Individual states do: Vermont is +40 by one yardstick and −38 by the other, Kansas −2 vs +17, Oklahoma +8 vs +28. Those gaps are candidates, not voters. |
| [Rural, suburban, urban](viz/density_swing/density_swing.png) | Within states, the sparsest counties moved 3–4 points less than the rest of their state, suburban-density counties 1 point more; votes cast rose 7% in urban counties and fell 2% in the sparsest. |

## Senate and governor races

| Visual | Finding |
|--------|---------|
| [Counties as circles sized by votes](viz/vote_circles/vote_circles.png) | 97% of counties moved toward Democrats compared with the 2024 presidential vote (different offices, so candidate effects are included). |
| [Ticket splitting, county by county](viz/split_counties/split_counties.png) | 97% of counties backed the same party for senator and governor (correlation 0.97, typical gap 5 points); the 56 that didn't cluster in a few states (New Hampshire, Maine, Iowa, South Carolina). |
| [Ticket splitting, state by state](viz/ticket_splitting/ticket_splitting.png) | Of 21 states with a Democrat-vs-Republican Senate race and governor race, South Carolina and New Hampshire have different parties leading each. |
| [Every Senate race at a glance](viz/senate_states_glance/senate_states_glance.png) | Which side outspent didn't track the swing (rank correlation +0.07); lower-turnout states swung more (−0.57), and so did redder states (−0.40). |
| [Turnout and the swing, county by county](viz/turnout_vs_shift/turnout_vs_shift.png) | Within each state, counties where turnout fell off most moved only ~1.3 points more than counties where it held up, against a ~15-point swing. This rules out a county-to-county turnout story, not a uniform one. |
| [Age, turnout and shift](viz/age_turnout_shift/age_turnout_shift.png) | Within states, the oldest fifth of counties turned out 5 points above average but moved 3 points less toward Democrats; the youngest fifth did the reverse. |

## Money

| Visual | Finding |
|--------|---------|
| [Where the Senate money went](viz/senate_money_flow/money_flow.png) | Democratic Senate campaigns raised 2.6× more than Republican ones ($713M vs $275M); outside groups spent almost evenly ($772M vs $777M). |
| [Money per vote](viz/money_per_vote/money_per_vote.png) | Races decided by under 7 points drew a median $78 per vote, against $7 in races decided by 15+. |
| [When outside money arrived](viz/outside_money_timing/outside_money_timing.png) | 60% of dated outside spending in Senate races landed in the final 30 days, on both sides. |
| [Odds vs money](viz/money_vs_odds/money_vs_odds.png) | Polymarket's Democratic Senate odds stayed above 50% from Aug 31; Democratic-side outside money first out-spent the Republican side 35 days later. |

## Turnout, markets, surveys, the ballot

| Visual | Finding |
|--------|---------|
| [236 years of midterm turnout](viz/turnout_history/turnout_history.png) | The 2026 early estimate (49.1%) is the second-highest midterm turnout in more than a century: only 2018 (50.0%) was higher among midterms after 1914. |
| [Turnout change by state](viz/turnout_change/turnout_change.png) | Compared with 2022, turnout rose in 34 states and fell in 17 (early estimates). |
| [What the market expected](viz/market_expectations/senate_seats_heatmap.png) | Polymarket's top pick for Republican Senate seats from March onward was the range the result landed in, but it stayed under 50% until Election Day (prices shown through Nov 3 only). |
| [30 years of how groups vote](viz/demographic_trends/demographic_trends.png) | The income gap has nearly closed: voters earning $100K+ leaned Republican through 2020 and now lean Democratic (D+12), a little less than voters under $50K (D+16). |
| [Which groups moved in 2026](viz/demographic_shift_2026/demographic_shift_2026.png) | Every group in the election-day surveys moved toward Democrats vs. the 2022 midterm; Asian voters (+25), young voters and $100K+ earners (+20 each) moved most. 2026 is The Voter Poll by SSRS, not the Edison exit poll, so part of the change may be method. |
| [How many House votes were cast in a real contest?](viz/house_competition/house_competition.png) | Only 17% of House votes were cast in a district decided by under 5 points; 47% were in districts decided by 20 or more. |
| [Close House races](viz/house_close_races/house_close_races.png) | 25 U.S. House races are within 2 points, 12 within 1, with counting still going (417 contested districts shown). |
| [Congress was ~1% of the ballot](viz/ballot_length/ballot_length.png) | Of 39,430 races tracked on Nov 3, 470 were for Congress; city, town and township races were 40%. |

## Gallery

![Same office, same counties, four years apart](viz/gov_swing_2022_2026/gov_swing_2022_2026.png)
![Two yardsticks, one swing](viz/two_yardsticks/two_yardsticks.png)
![Rural, suburban, urban](viz/density_swing/density_swing.png)
![Counties as circles sized by votes](viz/vote_circles/vote_circles.png)
![Ticket splitting, county by county](viz/split_counties/split_counties.png)
![Ticket splitting, state by state](viz/ticket_splitting/ticket_splitting.png)
![Every Senate race at a glance](viz/senate_states_glance/senate_states_glance.png)
![Turnout and the swing, county by county](viz/turnout_vs_shift/turnout_vs_shift.png)
![Age, turnout and shift](viz/age_turnout_shift/age_turnout_shift.png)
![Where the Senate money went](viz/senate_money_flow/money_flow.png)
![Money per vote](viz/money_per_vote/money_per_vote.png)
![When outside money arrived](viz/outside_money_timing/outside_money_timing.png)
![Odds vs money](viz/money_vs_odds/money_vs_odds.png)
![236 years of midterm turnout](viz/turnout_history/turnout_history.png)
![Turnout change by state](viz/turnout_change/turnout_change.png)
![What the market expected](viz/market_expectations/senate_seats_heatmap.png)
![30 years of how groups vote](viz/demographic_trends/demographic_trends.png)
![Which groups moved in 2026](viz/demographic_shift_2026/demographic_shift_2026.png)
![How many House votes were cast in a real contest?](viz/house_competition/house_competition.png)
![Close House races](viz/house_close_races/house_close_races.png)
![Congress was ~1% of the ballot](viz/ballot_length/ballot_length.png)

## Repo layout

```
data/raw/      source files as downloaded (see SOURCES.md); data/raw/medsl/ is a small county-level
               aggregate built from MIT Election Lab's 2 GB of 2022 precinct files by pipeline/aggregate_medsl_2022.py
data/clean/    tidy tables the visuals read from, plus CHECKS.md
pipeline/      cleaning scripts; run_all.py runs everything
viz/           one folder per visual; style.py holds the shared look
REVIEW.md      the November 8 review: what was checked, what was wrong, what changed
IDEAS.md       twenty chart ideas, scored, and which were built
```

## Rebuild everything

```bash
pip install -r requirements.txt
python pipeline/run_all.py
for f in viz/*/*.py; do python "$f"; done
```

The charts use the Inter font. If it isn't installed, matplotlib falls back to its default font.

`run_all.py` writes every table in `data/clean/` and a `CHECKS.md` report: match rates, rows dropped and why, and cross-checks between sources. To rebuild the 2022 baseline from scratch, clone [MEDSL/2022-elections-official](https://github.com/MEDSL/2022-elections-official) and run `python pipeline/aggregate_medsl_2022.py <path>/individual_states`.

## What the cleaning handles

- **Junk FEC filings.** The FEC outside-spending file includes 15 nonsense entries of $1 billion to $9 billion each ($37.5 billion in total). Single expenditures over $100 million are dropped and logged in `ie_dropped_junk.csv`. Each transaction keeps only its latest amendment, and an expenditure repeated in a later filing (a 24-hour report that reappears in a periodic report) is kept once. Result: $42.8 billion raw becomes $3.71 billion. One table, `ie_senate_general.csv`, holds every Senate general-election expenditure with the side it helped, so all the money charts agree.
- **Double-reported votes.** civicAPI reports some states at two levels at once: counties and towns (New England), boroughs and house districts (Alaska), and old counties and planning regions (Connecticut). Each state uses exactly one level so no vote is counted twice.
- **Candidate matching.** Ballot names are matched to FEC IDs by state and surname, ignoring accents. That catches "Luján" and two-word surnames like "Fetty Anderson". When several filers share a surname, the one sharing the most name words wins (Darline Graham, not Lindsey Graham, in South Carolina), and no committee can be matched to two candidates in one race. 71 of the 72 Senate candidates with at least 5% of the vote are matched; the one gap never filed with the FEC.
- **Thin prediction markets.** Polymarket outcomes are put on a full daily calendar. Gaps are filled from the last real price, and each day is rescaled so the outcomes sum to 100%.
- **2022 precinct returns.** MIT Election Lab reports some states by vote mode and some with a TOTAL row; within each precinct only TOTAL rows are used when present. Tally rows that aren't candidates (ballots cast, undervotes) and county-aggregate rows that duplicate precincts (Idaho) are dropped; fusion lines (New York) are credited to the candidate's major party. Every statewide total was checked against the official 2022 result.

## Known limits

- Results are **unofficial** until states certify (late November to mid-December 2026). Re-run the pipeline then.
- Campaign money runs through each candidate's pre-general FEC report (mid-October) and includes primary spending.
- Alaska has no 2024 county-level presidential baseline, so it has no "shift since 2024", and its results are first-choice votes: both statewide races go to ranked-choice tabulation on Nov 18.
- Cross-check against pushbuild (the official state feeds): 44 Senate and governor races appear in both sources. Every D-minus-R margin agrees within 0.6 points. Four differ in total votes by more than 2%:
  - Colorado: pushbuild's snapshot is about 20% behind civicAPI's count.
  - Vermont governor: the pushbuild total is exactly double the county sum, which points to a duplicated statewide row.
  - California: counting is still ongoing.
- Shifts are only computed for races whose top two candidates were a Democrat and a Republican. Montana's Senate race (independent runner-up), Rhode Island's and Wyoming's governor races, and the Idaho, Nebraska and South Dakota Senate races are left out of those comparisons.
- The 2022 baseline has no Alaska (no county units), Tennessee (the 2022 file lacks the governor race), Connecticut (2022 counties vs 2026 planning regions) or full Indiana (57 counties missing in 2022).
- The 2026 demographic figures come from The Voter Poll by SSRS, which replaced the Edison exit poll this cycle; comparisons with earlier exit polls mix two methods.
- Prediction-market prices show what traders expected. They are not polls, and one election can't show whether markets are "accurate".

## Review

[REVIEW.md](REVIEW.md) records a full second pass over the data and charts (November 8, 2026): what was checked, what was wrong, and what changed. [IDEAS.md](IDEAS.md) lists the chart ideas that were weighed and which were built.

## Sources

See [SOURCES.md](SOURCES.md). Election results by [civicAPI](https://civicapi.org) and [pushbuild](https://github.com/pushbuild/us-2026-election-results); 2022 returns from the [MIT Election Data and Science Lab](https://github.com/MEDSL/2022-elections-official); turnout by Michael McDonald, [UF Election Lab](https://election.lab.ufl.edu); campaign finance from the [FEC](https://www.fec.gov/data/browse-data/?tab=bulk-data).
