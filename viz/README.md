# Visuals

Each script reads only from `data/clean/` and writes a 1200 × 1500 PNG (LinkedIn portrait) next to itself.
`style.py` holds the shared colors, fonts and footer.

| Folder | Script | Reads |
|--------|--------|-------|
| `market_expectations/` | `senate_seats_heatmap.py` | `pm_senate_seats.csv` |
| `senate_money_flow/` | `money_flow.py` | `senate_money_flow.csv` |
| `money_per_vote/` | `money_per_vote.py` | `senate_races.csv` |
| `vote_circles/` | `vote_circles.py` | `county_map_2026.csv` (+ raw 2024 results and Census county centers) |
| `ballot_length/` | `ballot_length.py` | raw `civicapi/races.csv` |
| `turnout_history/` | `turnout_history.py` | `turnout_national_midterms.csv` (+ raw UF presidential series) |
| `ticket_splitting/` | `ticket_splitting.py` | `county_results_2026.csv` |
| `outside_money_timing/` | `outside_money_timing.py` | `ie_clean.csv` |
| `turnout_change/` | `turnout_change.py` | `turnout_states_2022_2026.csv` |
| `house_close_races/` | `house_close_races.py` | raw `civicapi/races.csv` |
| `turnout_vs_shift/` | `turnout_vs_shift.py` | `county_map_2026.csv` |
| `age_turnout_shift/` | `age_turnout_shift.py` | `county_map_2026.csv` + raw Census age estimates |
| `senate_states_glance/` | `senate_states_glance.py` | senate, IE and turnout tables + raw 2024 results and Census age |
| `money_vs_odds/` | `money_vs_odds.py` | raw Polymarket daily + `ie_clean.csv` |
| `demographic_trends/` | `demographic_trends.py` | `exit_poll_groups.csv` |
| `demographic_shift_2026/` | `demographic_shift_2026.py` | `exit_poll_groups.csv` |
| `linkedin_story/` | `story.py` | county, turnout, Senate and exit-poll tables → 8 pages + `midterms_2026_story.pdf` (LinkedIn carousel) |
