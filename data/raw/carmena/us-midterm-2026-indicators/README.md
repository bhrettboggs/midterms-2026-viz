# US Midterm 2026 Indicators: Early Vote, Ballot

Eleven days before the 2026 midterm, the national generic ballot, early-ballot counts and the party split of early voters, lined up against the same point in 2018, 2022 and 2024.

Published by [Carmena’s Overton & Electoral Research](https://carmenaresearch.com/), an independent, non-partisan US election research firm. These are the public tables behind our charts. Party means voter registration, not vote choice, unless a column says otherwise. Figures are compared at the same number of days before Election Day in each year.

## Files
- **midterm-indicators.csv** (10 rows): 2026 midterm indicators, 11 days out. Columns: `indicator` What is measured; `cycle` Election year; `value` Value; negative D−R values are Republican leads; `unit` Unit of the value; `as_of` Date of the figure (same point before Election Day); `source` Source of the figure. Source page: https://carmenaresearch.com/data/#midterm-indicators
- **generic-ballot.csv** (3 rows): Generic ballot 11 days out and the final House vote. Columns: `cycle` Election year; `average_11_days_out` Average 11 days before Election Day, D−R points; `average_election_day` Average on Election Day, D−R points; `house_popular_vote` National House popular vote, D−R points. Source page: https://carmenaresearch.com/data/#generic-ballot
- **early-voters-by-party.csv** (3 rows): Early voters by party, national, 11 days out. Columns: `cycle` Election year; `as_of` Date of the reading; `dem_pct` Democratic share of early voters, %; `rep_pct` Republican share, %; `other_pct` Other share, %; `dem_minus_rep` Democratic minus Republican share, points. Source page: https://carmenaresearch.com/data/#early-voters-by-party
- **chart-generic-ballot.csv** (3 rows): Generic ballot 11 days out, against the final House vote. Columns: `year` Year; `average11DaysOut` Average, 11 days out; `finalHouseVote` Final House vote. Source page: https://carmenaresearch.com/data/#chart-generic-ballot
- **chart-banked-share.csv** (3 rows): 21.7M early ballots so far, against 2024 at the same point. Columns: `measure` Measure; `value2026` 2026; `value2024` 2024, same point. Source page: https://carmenaresearch.com/data/#chart-banked-share
- **chart-early-mix.csv** (3 rows): Early voters are D+15 this year. At the same point in 2024 they were D+2. Columns: `party` Party; `share2026` 2026; `share2024` 2024, same point. Source page: https://carmenaresearch.com/data/#chart-early-mix
- **chart-modelled-share.csv** (2 rows): Where the tracker’s party split is a model. Columns: `group` Group; `states` States; `shareOfEarlyVotes` Share of 2026 early votes (%). Source page: https://carmenaresearch.com/data/#chart-modelled-share
- **chart-early-vs-2022-total.csv** (15 rows): Thirteen states have already cast more early ballots than in their entire 2022 early vote. Columns: `state` State; `group` Group; `early2026` Early ballots, 2026 (Oct 29); `early2022` Early ballots, all of 2022; `pct` 2026 so far, % of all 2022. Source page: https://carmenaresearch.com/data/#chart-early-vs-2022-total

## Provenance and method
Carmena’s Overton compiles cumulative early-ballot counts from state and county election records and joins them to voter registration and vote history. Calculations are ours; the method is described on our [methodology page](https://carmenaresearch.com/methodology/). Last updated 2026-10-29. Updated as our tracking runs, typically weekly during the early-voting period.

## Caveats
- Party is not vote choice. TargetSmart models party in 21 states holding 48% of 2026 early votes (Oct 23, 2026).
- 2022 polls understated Republicans: R+0.6 in the average at this point, R+2.7 in the House vote.
- The early-ballot share uses 2022 total turnout (109,979,856) and 2024 total turnout (156,766,239) as denominators.
- 2026 uses the Silver Bulletin average; 2018 and 2022 use 538’s average. The methods differ.
- 2022 polls understated Republicans by about 2 points from this point.
- Party is not vote choice.
- Democrats have voted early in larger numbers since 2020.
- TargetSmart models party in 21 states; on Oct 23, 2026 they held 48% of early votes.
- NBC publishes whole percentages, so each share is precise to about half a point.
- 2022 polls understated Republicans: R+0.6 in the average, R+2.7 in the House vote.
- The 2026 share is of 2022’s total turnout; the 2024 share is of 2024’s. Raw ballots are at 61% of 2024’s pace, a presidential year.
- TargetSmart models party in 21 states, and party is not vote choice. Democrats have voted early in larger numbers since 2020.
- “Not marked as modelled” is NBC’s labelling, not a check we ran.
- 2024’s early vote was larger than 2026’s so far in every state shown except New Jersey (110% of 2024).

## Third-party figures
- Generic ballot averages belong to Silver Bulletin and 538; early-vote counts and party splits come from the NBC News / TargetSmart tracker. Credit those sources when reusing their figures.
- Averages belong to Silver Bulletin (2026) and 538 (2018, 2022). House vote: Cook Political Report (2018) and published 2022 results.
- These shares are NBC News / TargetSmart figures. Our licence covers our compilation; credit NBC News / TargetSmart as the source.

## Also on
- Kaggle: [US Midterm 2026 Indicators: Early Vote, Ballot](https://www.kaggle.com/datasets/carmenaresearch/us-midterm-2026-indicators)
- Our data page: [carmenaresearch.com/data](https://carmenaresearch.com/data/)

## Licence and citation
CC BY 4.0. Credit “Carmena’s Overton & Electoral Research” and link to the file or page you used. Citation: Carmena’s Overton & Electoral Research. “US Midterm 2026 Indicators: Early Vote, Ballot” (CSV). Last updated 2026-10-29. https://carmenaresearch.com/data/. Licensed CC BY 4.0.

More public data, with JSON copies and a changelog, is on our [data page](https://carmenaresearch.com/data/). In-depth data and custom research are available for commercial use on request. New analysis goes out by email first: [subscribe](https://carmenaresearch.com/#newsletter).
