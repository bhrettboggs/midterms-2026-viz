# Pipeline checks

Generated 2026-11-07 13:30 by `pipeline/run_all.py`. Results are unofficial until states certify; re-run after certification.

- results: one reporting level per state; dropped duplicate levels County (40), House District (320), Overseas (8), Town (7702), Township (2982)
- results: 0 places could not be matched to a county code (0.000% of votes); see unmatched_places.csv
- results: county sums vs statewide rows: 2 races checked, 0 off by more than 1%
- results: 71 races, 2815 counties, 168,433,993 votes across all Senate + governor races
- map: 2815 counties in 45 states; 28 have no 2024 baseline match
- map: states with no Senate or governor race in the data: DC, IN, MO, ND, UT, WA
- map: states under 95% reporting (median county): AK 66%, CA 70%, WV 74%, PA 79%, AZ 80%, SD 80%, OK 81%, NJ 83%, KY 84%, GA 84%, TN 84%, MT 85%, AR 85%, RI 86%, WY 87%, MD 87%, HI 87%, NM 87%, NV 87%, WI 88%, DE 89%, KS 89%, FL 90%, NY 90%, IL 91%, CO 92%, TX 92%, OR 92%, NH 92%, MA 92%, NC 93%, OH 93%, ID 93%, VT 93%, ME 94%, AL 94%, MI 95%
- outside money: 51,186 rows / $42.8B raw -> 41,670 rows / $3.67B clean (15 junk rows over $100M dropped, totalling $37.5B)
- senate: 71 of 72 candidates with >=5% of the vote matched to an FEC ID; unmatched: Natalie M Fleming (ID)
- senate: 35 races; money per vote ranges $1.77-$625.20 (campaign spending is cycle-to-date, includes primaries)
- polymarket 'Balance of Power': 474 days, 5 outcomes; 0% of days summed more than 5 points away from 100% before rescaling
- polymarket 'Republican Senate seats': 320 days, 11 outcomes; 37% of days summed more than 5 points away from 100% before rescaling
- polymarket: biggest one-day swings in any balance-of-power outcome: 2026-11-04 (12%), 2025-11-06 (8%), 2026-11-03 (6%), 2025-12-04 (5%), 2025-11-11 (5%) — confirm what happened on these dates before labeling them
- turnout: 2026 national estimate 49.1% (UF v0.2, initial); 26 earlier midterms were higher
- turnout: 51 states with both years; 34 up from 2022, 17 down
- cross-check: 33 state races appear in both civicAPI and pushbuild; 3 differ by more than 2%: CA GOV (+2.7%), CO SEN (+24.1%), VT GOV (-50.0%)
