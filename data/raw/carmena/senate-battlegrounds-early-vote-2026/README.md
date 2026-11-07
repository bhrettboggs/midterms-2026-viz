# Senate Battlegrounds Early Vote Pace 2026

Ten Senate battlegrounds were voting early at 50% to 98% of their 2024 pace eleven days out in 2026; against 2022, nine of the ten were ahead.

Published by [Carmena’s Overton & Electoral Research](https://carmenaresearch.com/), an independent, non-partisan US election research firm. These are the public tables behind our charts. Party means voter registration, not vote choice, unless a column says otherwise. Figures are compared at the same number of days before Election Day in each year.

## Files
- **senate-battlegrounds.csv** (10 rows): Early voting in ten Senate battlegrounds. Columns: `st` State abbreviation; `state` State; `early_2026` 2026 early ballots, Oct 23, 2026; `early_2024_same_point` 2024 early ballots at the same point (NBC News tracker); `early_2022_same_point` 2022 early ballots at the same point (NBC News tracker); `pace_vs_2024_pct` 2026 as % of 2024 at the same point, one decimal (the site shows whole numbers); `pace_vs_2022_pct` 2026 as % of 2022 at the same point; `dem_pct` Democratic share of early voters, %; `rep_pct` Republican share, %; `other_pct` Other share, %; `dem_minus_rep` D−R points; negative = Republican lead; `source_tag` reg. = state registration; primary = party of last primary from state records; model = vendor estimate (TargetSmart, via NBC); `party_source` Where the party mix comes from; `party_as_of` Date of the party figures; `note` State-specific caveat. Source page: https://carmenaresearch.com/data/#senate-battlegrounds
- **chart-battleground-pace.csv** (10 rows): Early voting in ten Senate battlegrounds: 50% to 98% of 2024’s pace. Columns: `state` State; `pace` Early ballots, % of 2024 at the same point; `dr` D−R of early voters (points); `drSource` Party source. Source page: https://carmenaresearch.com/data/#chart-battleground-pace

## Provenance and method
Carmena’s Overton compiles cumulative early-ballot counts from state and county election records and joins them to voter registration and vote history. Calculations are ours; the method is described on our [methodology page](https://carmenaresearch.com/methodology/). Last updated 2026-10-23. Updated as our tracking runs, typically weekly during the early-voting period.

## Caveats
- Registered party is not vote choice.
- Michigan, Minnesota and South Carolina party figures are TargetSmart’s model.
- Ohio (Oct 22) and Texas (through Oct 21) party figures come from state files not refreshed on Oct 23; Maine’s from the state file of Oct 20.
- Compiled by Carmena’s Overton from state and county early-vote records and voter registration; calculations are ours.
- 2024 was a presidential year, so every state is below its 2024 count. Party mix is not vote choice.

## Third-party figures
- Counts for 2022 and 2024, and party figures tagged model or from NBC, come from NBC News / TargetSmart. Credit those sources when reusing their figures.

## Also on
- Kaggle: [Senate Battlegrounds Early Vote Pace 2026](https://www.kaggle.com/datasets/carmenaresearch/senate-battlegrounds-early-vote-2026)
- Our data page: [carmenaresearch.com/data](https://carmenaresearch.com/data/)

## Licence and citation
CC BY 4.0. Credit “Carmena’s Overton & Electoral Research” and link to the file or page you used. Citation: Carmena’s Overton & Electoral Research. “Senate Battlegrounds Early Vote Pace 2026” (CSV). Last updated 2026-10-23. https://carmenaresearch.com/data/. Licensed CC BY 4.0.

More public data, with JSON copies and a changelog, is on our [data page](https://carmenaresearch.com/data/). In-depth data and custom research are available for commercial use on request. New analysis goes out by email first: [subscribe](https://carmenaresearch.com/#newsletter).
