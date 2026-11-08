# Sources

All files in `data/raw/` were downloaded on November 7, 2026 (exit-poll tables on November 8). Results are a snapshot from before certification; see REVIEW.md for what was and wasn't newer as of November 8.

| Folder | What | Source | Terms |
|--------|------|--------|-------|
| `civicapi/races.csv` | Every 2026 U.S. race: candidates, party, votes, percent reporting | [civicAPI](https://civicapi.org/api-documentation/) `/api/v2/race/search` | Free; attribution required for non-personal projects |
| `civicapi/sen_gov_county.csv` | County results for every Senate and governor race | civicAPI `/api/v2/race/{id}` | Same as above |
| `pushbuild/*.csv` | Unofficial results by state and county from each state's official feed, as of Nov 6, 2026 11:32 PM ET | [pushbuild/us-2026-election-results](https://github.com/pushbuild/us-2026-election-results) | CC0 |
| `fec/weball26.txt` | Candidate financial summary, 2025–2026 | [FEC bulk data](https://www.fec.gov/data/browse-data/?tab=bulk-data) | Public domain |
| `fec/cn.txt`, `fec/ccl.txt` | Candidate master file; candidate–committee links | FEC bulk data | Public domain |
| `fec/independent_expenditure_2026.csv` | Outside spending for and against candidates | FEC bulk data | Public domain |
| `uf/` | National turnout 1789–2024; state turnout 1980–2022; 2026 initial estimate (v0.2) | Michael McDonald, [UF Election Lab](https://election.lab.ufl.edu/data-archive/national/) | Cite Michael McDonald, UF Election Lab |
| `polymarket/daily.csv` | Daily prices for House control, Senate control, balance of power, and Republican Senate seat brackets | [Polymarket](https://polymarket.com) public Gamma and CLOB APIs | Public API; check Polymarket's terms before redistributing |
| `tonmcg/` | 2020 and 2024 county presidential results | [tonmcg/US_County_Level_Election_Results_08-24](https://github.com/tonmcg/US_County_Level_Election_Results_08-24) | MIT |
| `census/` | 2024 Gazetteer county and county-subdivision files: codes, land area, center points | [U.S. Census Bureau](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/) | Public domain |
| `census/cc-est2024-agesex-all.csv` | County population estimates by age group, July 2024 | [U.S. Census Bureau](https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/asrh/) | Public domain |
| `exit_polls/roper_how_groups_voted_1996_2024.csv` | Presidential exit polls by group, 1996–2024 | [Roper Center, How Groups Voted](https://ropercenter.cornell.edu/how-groups-voted) | Cite the Roper Center; national exit poll consortium data |
| `exit_polls/wikipedia_house_exit_polls_2006_2026.csv` | National House vote by group, midterms 2006–2026, transcribed from Wikipedia's tables. 2006–2022: Edison Research exit polls for the National Election Pool. 2026: [The Voter Poll by SSRS](https://ssrs.com/ssrs-solutions/voter-poll/), the networks' and AP's replacement for the exit poll (a large pre-election survey plus in-person interviews in 15 states); every 2026 figure was checked against [ABC News's tables](https://abcnews.com/Elections/polls-2026-us-house-election-results-analysis) | Wikipedia election articles; Edison/NEP; SSRS | CC BY-SA 4.0 (Wikipedia tables); cite the pollsters |
| `carmena/` | 2026 early-vote data (not used yet) | [carmenaresearch/election-data](https://github.com/carmenaresearch/election-data) | CC BY 4.0 |
| `medsl/county_sen_gov_2022.csv` | 2022 general-election Senate and governor votes by county (D / R / other), aggregated by `pipeline/aggregate_medsl_2022.py` from MIT Election Lab's precinct-level files (one zip per state, ~2 GB unzipped, downloaded November 8, 2026). Not in the file: Alaska (no county units), Tennessee's governor race (absent from the source), 57 Indiana counties (no precinct data). New Mexico's party labels and Wyoming's Democratic nominee are filled in by hand (see the script). | [MEDSL/2022-elections-official](https://github.com/MEDSL/2022-elections-official), MIT Election Data and Science Lab | Cite the dataset: MIT Election Data and Science Lab, "2022 Precinct-Level Returns" |
