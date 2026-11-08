# Sources

All files in `data/raw/` were downloaded on November 7, 2026.

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
| `carmena/` | 2026 early-vote data (not used yet) | [carmenaresearch/election-data](https://github.com/carmenaresearch/election-data) | CC BY 4.0 |
