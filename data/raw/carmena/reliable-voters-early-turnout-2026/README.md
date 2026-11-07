# Reliable Voters’ Early Turnout by Party 2026

Democrats are front-loading their most reliable voters: in North Carolina 55% of Democratic four-time voters had voted early eight days out in 2026, against 34% of Republicans.

Published by [Carmena’s Overton & Electoral Research](https://carmenaresearch.com/), an independent, non-partisan US election research firm. These are the public tables behind our charts, from the article [Democrats are front-loading their reliable voters](https://carmenaresearch.com/blog/reliable-democrats-are-voting-early/). Party means voter registration, not vote choice, unless a column says otherwise. Figures are compared at the same number of days before Election Day in each year.

## Files
- **chart-habit-party-rates.csv** (6 rows): Democrats have used more of their reliable-voter pool, and the gap has widened since 2022. Columns: `group` State; `label` Party; `v2022` 2022 (%); `v2026` 2026 (%); `early2026` 2026 early ballots; `registered2026` 2026 registered. Source page: https://carmenaresearch.com/data/#chart-habit-party-rates
- **chart-habit-overall-margins.csv** (9 rows): Early voters lean further toward Democrats than at the same point in 2022 and 2024. Columns: `label` State; `year` Year; `margin` Party margin; `days` Days before Election Day; `counties` Matched counties; `democrats` democrats; `republicans` republicans; `other` other. Source page: https://carmenaresearch.com/data/#chart-habit-overall-margins
- **chart-habit-gap-change.csv** (7 rows): The gap between the parties’ four-time voters widened most in North Carolina. Columns: `label` State; `change` Change (points); `gap2022` 2022 gap; `gap2026` 2026 gap. Source page: https://carmenaresearch.com/data/#chart-habit-gap-change
- **chart-habit-gap-states.csv** (7 rows): Among four-time voters, Democrats’ lead in early-turnout rate grew in all seven states. Columns: `label` State; `group` Party basis; `margin2022` 2022 gap (points); `margin2026` 2026 gap (points); `days` Days before Election Day. Source page: https://carmenaresearch.com/data/#chart-habit-gap-states
- **chart-habit-lead-share.csv** (7 rows): Changes in four-time voters’ turnout account for about half or more of the turnout-driven gain in Democrats’ early lead. Columns: `label` State; `group` Party basis; `part` From four-time voters (%); `gainFromTurnout` Turnout-driven gain (ballots); `fromFourTime` From four-time voters (ballots); `lead2026` 2026 Democratic early lead (ballots); `leadIfFourTimeAt2022` Lead if four-time voters were at their 2022 pace. Source page: https://carmenaresearch.com/data/#chart-habit-lead-share

## Provenance and method
Carmena’s Overton compiles cumulative early-ballot counts from state and county election records and joins them to voter registration and vote history. Calculations are ours; the method is described on our [methodology page](https://carmenaresearch.com/methodology/). Last updated 2026-10-27. Updated as our tracking runs, typically weekly during the early-voting period.

## Caveats
- Days before Election Day: North Carolina 8, Kansas 7, Florida 8. Four-time voters voted in 2014–2020 for the 2022 comparison and 2018–2024 for 2026. These are changing cohorts, not a panel of the same people.
- Margins are (Democratic minus Republican ballots) / all early ballots, including other parties. Coverage: North Carolina 100 counties, Florida 67, Kansas 103 matched counties. The statewide-total and voting-history extracts are separate source slices and do not exactly reconcile; no decomposition of the statewide margin is inferred here. 2024 is a presidential-election comparison; 2022 is the preceding midterm.
- Days before Election Day: North Carolina 8, Kansas 7, Florida 8, Iowa 8, Ohio 8, Georgia 8, Texas 8.
- Days before Election Day: North Carolina 8, Kansas 7, Florida 8, Iowa 8, Ohio 8, Georgia 8, Texas 8. Prior elections: 2014–2020 for 2022, 2018–2024 for 2026. Registered party, not vote choice.
- Four-time voters’ part: the 2026 lead minus the lead with only four-time voters returned to their 2022 rates. Same day in both years; days before Election Day: North Carolina 8, Kansas 7, Florida 8, Iowa 8, Ohio 8, Georgia 8, Texas 8.

## Credits
Our licences for some inputs require these credits. Keep them when you reuse the file.
- `chart-habit-party-rates.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-habit-overall-margins.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-habit-gap-change.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-habit-gap-states.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-habit-lead-share.csv`: Source: Carmena’s Overton; early votes via ColdSpark.

## Also on
- Kaggle: [Reliable Voters’ Early Turnout by Party 2026](https://www.kaggle.com/datasets/carmenaresearch/reliable-voters-early-turnout-2026)
- Our data page: [carmenaresearch.com/data](https://carmenaresearch.com/data/)

## Licence and citation
CC BY 4.0. Credit “Carmena’s Overton & Electoral Research” and link to the file or page you used. Citation: Carmena’s Overton & Electoral Research. “Reliable Voters’ Early Turnout by Party 2026” (CSV). Last updated 2026-10-27. https://carmenaresearch.com/data/. Licensed CC BY 4.0.

More public data, with JSON copies and a changelog, is on our [data page](https://carmenaresearch.com/data/). In-depth data and custom research are available for commercial use on request. New analysis goes out by email first: [subscribe](https://carmenaresearch.com/#newsletter).
