# Visuals

Each script reads only from `data/clean/` and writes a 1200 × 1500 PNG (LinkedIn portrait) next to itself.
`style.py` holds the shared colors, fonts and footer.

| Folder | Script | Reads |
|--------|--------|-------|
| `market_expectations/` | `senate_seats_heatmap.py` | `pm_senate_seats.csv` |
| `senate_money_flow/` | `money_flow.py` | `senate_money_flow.csv` |
| `money_per_vote/` | `money_per_vote.py` | `senate_races.csv` |
| `vote_circles/` | `vote_circles.py` | `county_map_2026.csv` (+ raw 2024 results and Census county centers) |
