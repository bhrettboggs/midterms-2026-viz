# North Carolina Early Vote 2026 by Party

North Carolina’s registered voters moved toward Republicans while its early voters moved 10 points toward Democrats, D+7 in 2022 to D+17 in 2026 at the same point.

Published by [Carmena’s Overton & Electoral Research](https://carmenaresearch.com/), an independent, non-partisan US election research firm. These are the public tables behind our charts. Party means voter registration, not vote choice, unless a column says otherwise. Figures are compared at the same number of days before Election Day in each year.

## Files
- **chart-nc-reg-vs-early.csv** (2 rows): Registered voters moved toward Republicans. Early voters moved 10 points toward Democrats. Columns: `label` Group; `margin2022` 2022; `margin2026` 2026. Source page: https://carmenaresearch.com/data/#chart-nc-reg-vs-early
- **chart-nc-party-rates.csv** (3 rows): About 25% of registered Democrats have voted early, against 15% of Republicans. Columns: `label` Party; `v2022` 2022 (%); `v2026` 2026 (%). Source page: https://carmenaresearch.com/data/#chart-nc-party-rates
- **chart-nc-unaffiliated.csv** (2 rows): North Carolina unaffiliated early voters by last primary ballot. Columns: `lastPrimaryBallot` Last primary ballot; `votersThousands` Early voters (thousands); `share` Share (%). Source page: https://carmenaresearch.com/data/#chart-nc-unaffiliated
- **chart-nc-county-shift.csv** (9 rows): Every large county moved toward Democrats, and several suburban and exurban counties switched sides. Columns: `label` County; `group` Group; `margin2022` 2022; `margin2026` 2026; `ballots2026` 2026 early ballots. Source page: https://carmenaresearch.com/data/#chart-nc-county-shift
- **chart-nc-early-mix.csv** (4 rows): North Carolina’s early voters are younger and less white than in 2022. Columns: `label` Group; `v2022` 2022 (%); `v2026` 2026 (%). Source page: https://carmenaresearch.com/data/#chart-nc-early-mix
- **chart-nc-voter-history.csv** (5 rows): Voters who cast ballots in all four recent general elections are 67% of the early vote, and they lean further toward Democrats than in 2022. Columns: `label` Voted in previous four generals; `margin2022` 2022; `margin2026` 2026; `share2022` 2022 share (%); `share2026` 2026 share (%). Source page: https://carmenaresearch.com/data/#chart-nc-voter-history
- **chart-primary-proxy.csv** (2 rows): North Carolina: party of last primary against registration. Columns: `measure` Measure; `lastPrimary` Party of last primary; `registration` Registration (truth). Source page: https://carmenaresearch.com/data/#chart-primary-proxy
- **chart-unaffiliated-split.csv** (2 rows): North Carolina 2024: unaffiliated voters for President and for Governor. Columns: `race` Race; `demTwoPartyShare` Democratic two-party share, about (%). Source page: https://carmenaresearch.com/data/#chart-unaffiliated-split
- **chart-habit-nc-groups.csv** (5 rows): North Carolina’s most consistent Democrats have accelerated the most since 2022. Columns: `label` Voted in previous four generals; `v2022` 2022 (%); `v2026` 2026 (%). Source page: https://carmenaresearch.com/data/#chart-habit-nc-groups
- **chart-habit-nc-unit.csv** (2 rows): Of every 100 North Carolina Democratic four-time voters, 55 have already voted. Columns: `label` Year; `value` Voted early (%); `early` Early ballots; `registered` Registered four-time Democrats. Source page: https://carmenaresearch.com/data/#chart-habit-nc-unit

## Provenance and method
Carmena’s Overton compiles cumulative early-ballot counts from state and county election records and joins them to voter registration and vote history. Calculations are ours; the method is described on our [methodology page](https://carmenaresearch.com/methodology/). Last updated 2026-10-26. Updated as our tracking runs, typically weekly during the early-voting period.

## Caveats
- Registered party of early voters and of all registered voters, 11 days before Election Day in each year. Margins are Democrats minus Republicans as a share of all voters, including unaffiliated.
- Early mail and in-person ballots divided by registered voters of the same party, 11 days before Election Day.
- Only unaffiliated early voters who have voted in a primary are counted.
- Registered party of early voters, same day in both years.
- Shares of early mail and in-person voters, 9 days before Election Day in each year; race and age shares are calculated separately.
- Prior elections: 2014–2020 for 2022, 2018–2024 for 2026, from each cycle’s matched voter file.
- The proxy moves unaffiliated primary voters into a party, and partisans who skip primaries into Other.
- Estimated from totals, assuming partisans voted for their own party.
- 8 days before Election Day in each year. Prior elections: 2014–2020 for 2022, 2018–2024 for 2026.
- 8 days before Election Day in each year.

## Credits
Our licences for some inputs require these credits. Keep them when you reuse the file.
- `chart-nc-reg-vs-early.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-nc-party-rates.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-nc-county-shift.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-nc-voter-history.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-habit-nc-groups.csv`: Source: Carmena’s Overton; early votes via ColdSpark.
- `chart-habit-nc-unit.csv`: Source: Carmena’s Overton; early votes via ColdSpark.

## Also on
- Kaggle: [North Carolina Early Vote 2026 by Party](https://www.kaggle.com/datasets/carmenaresearch/north-carolina-early-vote-2026)
- Our data page: [carmenaresearch.com/data](https://carmenaresearch.com/data/)

## Licence and citation
CC BY 4.0. Credit “Carmena’s Overton & Electoral Research” and link to the file or page you used. Citation: Carmena’s Overton & Electoral Research. “North Carolina Early Vote 2026 by Party” (CSV). Last updated 2026-10-26. https://carmenaresearch.com/data/. Licensed CC BY 4.0.

More public data, with JSON copies and a changelog, is on our [data page](https://carmenaresearch.com/data/). In-depth data and custom research are available for commercial use on request. New analysis goes out by email first: [subscribe](https://carmenaresearch.com/#newsletter).
