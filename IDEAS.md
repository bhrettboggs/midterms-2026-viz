# Visual ideas, scored

Twenty candidates for new standalone charts, scored 1–5 on five things and ranked by the total:

- **New**: is it an angle people haven't seen in the usual election coverage?
- **Insight**: does it answer a real question honestly, with the data we have?
- **Feasible**: can it be built from data already in the repo (or one well-documented addition)?
- **Visual**: will it stop a scroll at 1200×1500?
- **Robust**: does it survive the caveats (unofficial counts, candidate effects, survey methods)?

| # | Idea | New | Insight | Feasible | Visual | Robust | Total | Decision |
|---|------|----:|--------:|---------:|-------:|-------:|------:|----------|
| 1 | **Same office, four years apart.** Every county's 2022→2026 governor swing, one strip per state. Uses the new MEDSL 2022 baseline, so it is midterm-to-midterm and office-to-office, not Senate-vs-president. | 4 | 5 | 5 | 4 | 4 | **22** | Built: `gov_swing_2022_2026` |
| 2 | **Two yardsticks for one swing.** For each governor race, the shift measured against 2022's governor race next to the shift measured against the 2024 presidential vote. Shows how much of the repo's "shift since 2024" is electorate and candidate rather than movement. | 5 | 5 | 5 | 3 | 4 | **22** | Built: `two_yardsticks` |
| 3 | **Suburbs or countryside?** 2022→2026 governor swing by county density (votes per square mile), binned, same like-for-like baseline. | 4 | 5 | 5 | 4 | 4 | **22** | Built: `density_swing` |
| 4 | **Ticket splitting, county by county.** 2026 Senate margin vs governor margin for every county in states with both races; the diagonal is straight-ticket voting. | 4 | 4 | 5 | 4 | 4 | **21** | Built: `split_counties` |
| 5 | **How many House votes were cast in a real contest?** Share of all House votes by final margin band (uncontested, 20+, 10–20, 5–10, under 5), plus every district as a tick. | 3 | 4 | 5 | 4 | 4 | **20** | Built: `house_competition` |
| 6 | Turnout change vs swing, 2022→2026 (same office), county by county — an upgrade of the existing turnout chart. | 4 | 4 | 5 | 3 | 4 | 20 | Not built: overlaps the existing turnout chart; idea 3 covers the structural angle |
| 7 | Early-vote party margin (registration/model, 11 days out) vs the final Senate margin in 10 battlegrounds (Carmena data). | 4 | 4 | 5 | 3 | 2 | 18 | Not built: ten points from three different party sources |
| 8 | 2022 vs 2026 statewide governor margins as one scatter with the no-change diagonal. | 3 | 4 | 5 | 3 | 5 | 20 | Folded into idea 2 |
| 9 | Swing vs 2024 Trump margin by county: did the reddest places move most? | 4 | 4 | 5 | 3 | 3 | 19 | Not built: partly answered in the Senate-at-a-glance footer |
| 10 | House outside money per vote vs margin (FEC House IEs + civicAPI House results). | 3 | 3 | 5 | 3 | 3 | 17 | Not built: a repeat of the Senate chart |
| 11 | Where the Senate outside money went: a dollar-sized state treemap. | 2 | 3 | 5 | 3 | 4 | 17 | Not built |
| 12 | Generic ballot 11 days out vs House popular vote, 2018/2022/2026. | 2 | 3 | 5 | 2 | 3 | 15 | Not built: three data points |
| 13 | Age mix of the electorate across surveys (65+ share rose to 36% in 2026). | 3 | 3 | 5 | 3 | 1 | 15 | Not built: the 2026 survey changed method |
| 14 | Ballot measures: what passed, by topic. | 3 | 3 | 2 | 3 | 2 | 13 | Not built: 2,330 local measures, no topic labels |
| 15 | State legislative seat flips from civicAPI. | 3 | 4 | 2 | 3 | 2 | 14 | Not built: some states are aggregated, not by district |
| 16 | Cost of flipping: dollars in Senate seats that changed hands vs. held. | 3 | 3 | 5 | 3 | 2 | 16 | Not built: nine flips |
| 17 | Counties where Senate and governor winners differ (map). | 3 | 3 | 5 | 3 | 4 | 18 | Folded into idea 4 |
| 18 | The uncounted vote: reporting percentage vs UF's estimated total ballots by state on Nov 7. | 4 | 3 | 5 | 3 | 2 | 17 | Not built: "percent reporting" means different things by state |
| 19 | Class of 2020 → 2026: each Senate seat's 2020 margin and 2026 margin. | 3 | 4 | 2 | 3 | 4 | 16 | Not built: no 2020 Senate file in the repo |
| 20 | Alaska and Mississippi photo finishes, vote by vote. | 2 | 2 | 3 | 3 | 1 | 11 | Not built: changes daily |

The five built charts share one idea: use the like-for-like 2022 baseline where it exists, and show structure
(place, office, competitiveness) rather than another ranking of states.
