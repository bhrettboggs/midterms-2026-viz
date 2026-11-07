# Early-Vote Tracker Methods: Bias & Checks

Reference tables on how early-vote trackers are built: county-lean estimates understated Democratic margins by a median 16 points, and bellwether counties barely exist in midterms.

Published by [Carmena’s Overton & Electoral Research](https://carmenaresearch.com/), an independent, non-partisan US election research firm. These are the public tables behind our charts. Party means voter registration, not vote choice, unless a column says otherwise. Figures are compared at the same number of days before Election Day in each year.

## Files
- **chart-county-bias.csv** (8 rows): How far the county method understated the Democratic early-vote margin. Columns: `state` State; `bias` Bias of county method (points). Source page: https://carmenaresearch.com/data/#chart-county-bias
- **chart-bellwethers.csv** (2 rows): Share of counties that moved with the nation, within 4 points. Columns: `midterms` Midterms; `low` Low (%); `high` High (%). Source page: https://carmenaresearch.com/data/#chart-bellwethers
- **chart-voterfile-access.csv** (7 rows): Where voter files are free, with no account or form. Columns: `place` Place; `access` Access. Source page: https://carmenaresearch.com/data/#chart-voterfile-access
- **chart-oh-agree.csv** (3 rows): Ohio early voters: state file against the tracker. Columns: `party` Party; `stateFile` State file; `tracker` Tracker. Source page: https://carmenaresearch.com/data/#chart-oh-agree
- **chart-tx-records.csv** (3 rows): Texas early voters: state records against the tracker. Columns: `party` Party; `stateRecords` State records; `tracker` Tracker. Source page: https://carmenaresearch.com/data/#chart-tx-records
- **chart-tx-new-voters.csv** (3 rows): Texas 2026 early voters by vote history and party. Columns: `history` Vote history; `democrats` Democrats (%); `republicans` Republicans (%). Source page: https://carmenaresearch.com/data/#chart-tx-new-voters
- **chart-new-voters-swing.csv** (5 rows): Correlation of county new-voter share with the presidential swing. Columns: `group` Group; `year` Year; `r` Correlation (r). Source page: https://carmenaresearch.com/data/#chart-new-voters-swing

## Provenance and method
Carmena’s Overton compiles cumulative early-ballot counts from state and county election records and joins them to voter registration and vote history. Calculations are ours; the method is described on our [methodology page](https://carmenaresearch.com/methodology/). Last updated 2026-10-23. Updated as our tracking runs, typically weekly during the early-voting period.

## Caveats
- Tested only in the 8 states where party is known from records.
- A perfect past record adds 0–4 points of predictive edge.
- Cheapest paid files: Pennsylvania about $20, Alaska about $21.
- The two sources agree on the margin and disagree on independents.
- Adding 2022 and 2024 primaries in 4 counties (25% of votes) moved the margin about 0.6 pt. The tracker read D 49, R 42, Other 9 (D+7) on Oct 22.
- Nationally, 80% of early voters voted in both 2022 and 2024. “New” = voted in neither 2022 nor 2024.
- Correlation across counties, not a measure of individual voters. In 2024 the correlation was about zero.

## Also on
- Kaggle: [Early-Vote Tracker Methods: Bias & Checks](https://www.kaggle.com/datasets/carmenaresearch/early-vote-tracker-methods)
- Our data page: [carmenaresearch.com/data](https://carmenaresearch.com/data/)

## Licence and citation
CC BY 4.0. Credit “Carmena’s Overton & Electoral Research” and link to the file or page you used. Citation: Carmena’s Overton & Electoral Research. “Early-Vote Tracker Methods: Bias & Checks” (CSV). Last updated 2026-10-23. https://carmenaresearch.com/data/. Licensed CC BY 4.0.

More public data, with JSON copies and a changelog, is on our [data page](https://carmenaresearch.com/data/). In-depth data and custom research are available for commercial use on request. New analysis goes out by email first: [subscribe](https://carmenaresearch.com/#newsletter).
