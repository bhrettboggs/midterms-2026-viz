# Review of the pipeline and charts (November 8, 2026)

A second pass over everything in the repo, done without trusting the first pass: the pipeline was
rebuilt from the raw files in a clean environment, every number in the README and on the charts was
recomputed, and the results data were checked against a second source. Each problem below gives the
evidence, how sure I am, and what changed. Everything marked **Fixed** is in the code now.

## What held up

- **The pipeline is reproducible.** `python pipeline/run_all.py` on a fresh machine regenerated every
  table in `data/clean/` byte-for-byte identical to the committed versions (pandas 3.0 and 2.3 both work).
- **The results are real and the margins are right.** civicAPI is a free aggregator, so I compared it
  against the official state feeds in `data/raw/pushbuild/` on *margins*, not just vote totals. 44
  Senate and governor races appear in both sources; every D-minus-R margin agrees within 0.6 points and
  40 of 44 agree within 0.1. AP race calls reported in the press (Talarico over Paxton in Texas,
  Andrews in South Carolina, Turek in Iowa, Hamilton in Kansas, the uncalled Alaska and Mississippi
  races) match the data. Confidence that the county-level results are trustworthy: 95%.
- **The 2026 survey numbers are accurate**, just mislabeled (see finding 3): every demographic figure
  matches ABC News's published tables for the national House vote.
- The outside-money junk filter is right: all 15 dropped rows are nonsense filings by one person
  ("Warren Buffet", "DJIA", $1B–$9B each).
- The Polymarket cleaning (daily calendar, forward-fill, rescale to 100%) is reasonable for a thin
  market, and the dates it reports (top pick from March 14, above 50% only on Election Day) reproduce.
- UF turnout v0.2 (Nov 3) is still the latest release; pushbuild has not updated since Nov 6, 11:32 PM ET.

## Problems found

### 1. The wrong Graham got $22 million — Fixed (confidence 95%)

**What:** South Carolina's Republican nominee was Darline Graham. The FEC matcher looked for any
same-state Senate filer with the surname and took the one with the most money, which is Lindsey
Graham (S0SC00149, $22.2M disbursed, lost in the primary). Darline Graham's own committee
(S6SC04437) disbursed $1.28M.

**Evidence:** `data/raw/fec/weball26.txt` has both; the old `senate_candidates.csv` carried
S0SC00149 for "Darline Graham". pushbuild's official SC feed also lists Darline Graham as the nominee.

**Effect:** South Carolina's money per vote fell from $42 to $32, Republican campaign totals in the
Sankey fell from $327M to $306M, and the "raised x times more" headline moved.

**Change:** `match_fec` now prefers the filer sharing the most name words with the ballot name
(so "Darline" beats "Lindsey"); money only breaks remaining ties.

### 2. Dan Sullivan counted twice in Alaska — Fixed (95%)

**What:** The minor candidate "Daniel J. Sullivan Jr." (1.7%) matched Sen. Dan Sullivan's FEC ID, so
Sullivan's $10.8M in spending was added to Alaska's race total twice ($625 per vote instead of $577).

**Change:** Same name-overlap rule now finds Sullivan Jr.'s own tiny committee (S6AK00326); and if two
ballot candidates in one race ever land on the same ID, only the bigger vote-getter keeps it (logged
in `CHECKS.md`; it caught a Texas write-in listed twice).

### 3. The 2026 "exit poll" is not an exit poll, and not Edison — Fixed (85%)

**What:** In 2026 the networks and the AP replaced the Edison/NEP exit poll and AP VoteCast with
*The Voter Poll by SSRS*, a large pre-election survey plus in-person interviews in 15 states. The raw
CSV labeled 2026 "(Edison)" and the two demographic charts called everything "network exit polls".
The numbers themselves match ABC News's tables; the label and the methodological caveat were missing.

**Evidence:** SSRS press release (Oct 28, 2025) and AP/ABC descriptions of The Voter Poll; ABC's 2026
page is titled "National Voter Poll" (its 2024 page is "National Exit Poll").

**Change:** Captions in the raw CSV, both chart footers, `SOURCES.md` and the README now name the
source and warn that part of the 2022→2026 change may be method.

### 4. Montana shows a Republican "shift" that is an artifact — Fixed (85%)

**What:** Montana's Senate race was Kurt Alme (R) 48% vs. Seth Bodnar, an independent, 38%; the
Democrat got 12%. "D minus R" there is not a two-party margin, so 56 Montana counties were painted
red on the county map and pulled the within-state correlations. The old rule only required a Democrat
and a Republican to have *some* votes.

**Change:** `d_vs_r_race` now requires the race's top two candidates statewide to be one Democrat and
one Republican. This drops Montana's Senate race, Rhode Island's governor race (an independent came
second) and Wyoming's governor race (a Constitution Party candidate came second) from the shift and
ticket-splitting comparisons; Idaho, Nebraska and South Dakota were already out. The county map's
headline moved from 95% to 97% of counties moving toward Democrats; ticket splitting now covers 21
states instead of 23 (still South Carolina and New Hampshire split).

### 5. "Second-highest midterm turnout since 1914" — Fixed (95%)

**What:** 1914's turnout (50.4%) was higher than 2026's early estimate (49.1%), so counting from
1914 makes 2026 third. The chart and README now say "in more than a century" and spell out that only
2018 (50.0%) was higher among midterms after 1914.

### 6. "The income gap flipped" — Fixed (85%)

**What:** The subtitle on the 30-year chart said higher earners now lean Democratic *because the
income gap flipped*. In 2026 voters under $50K (D+16) are still more Democratic than $100K+ voters
(D+12); the gap flipped only in 2024 and un-flipped in 2026. Reworded to "the income gap has nearly
closed".

### 7. Post-result trading in the prediction-market charts — Fixed (80%)

**What:** The daily Polymarket series runs through Nov 4, when results were already in (the "47 or
fewer" bracket jumped to 70%, Democratic Senate control to 90%). Those days were averaged into the
heatmap's "Nov 1–4" column and used as the endpoint of the odds chart, which overstates what the
market "expected". Both charts now stop on Election Day and say so.

**Caveat left open:** the raw file has dates only, with no time zone; a "Nov 3" price could be the last
trade before U.S. polls closed or a little after. Confidence that it is pre-results: 75%.

### 8. "Turnout didn't decide the swing" over-claimed — Fixed (75%)

**What:** The chart compares counties *within* states: counties whose turnout fell more swung only
1.3 points more. That rules out a county-to-county turnout story, but it cannot see a uniform one
(the same kind of 2024 voter staying home everywhere would leave the county pattern flat). The title
asserted the stronger claim. Retitled to what the data show, with the limitation in the footer.

### 9. National roll-up row counted as a House race — Fixed (95%)

civicAPI carries a "United States House of Representatives" row with state "US". The close-races
chart counted it as a contested district (418 shown, "17 without both parties"); the right numbers
are 417 and 18. The 25 within 2 points and 12 within 1 point were unaffected.

### 10. Three charts, three outside-money totals — Fixed (90%)

The Sankey used only money aimed at candidates it could match to the ballot ($1.57B, with the party
taken from the matched candidate), the timing chart used every Senate general-election expenditure
with the party from the FEC file ($1.63B), and the per-state chart used a third variant. The pipeline
now writes one table, `ie_senate_general.csv`, with one `side` column, and all three charts read it:
$1.64B total, $772M helping Democrats, $777M helping Republicans, $86M around independents.

### 11. "12% of spending rows have no date" — Fixed (95%)

True by row count, but those rows are small: 0.8% of dollars. The footer implied a much bigger gap.
The timing chart now states the share of dollars left out (1.0%, including the few rows dated outside
2026), and the partial final week (Nov 1–3, $3M) is no longer drawn as a bar that looked like a
spending collapse.

### 12. De-duplication removed real expenditures — Fixed (70%)

The old rule dropped any second row with the same spender, candidate, amount and date. That catches
24-hour reports repeated in periodic reports, but also removed distinct same-day buys inside a
single filing (e.g. two $1.25M LCV ad buys for El-Sayed on Oct 23 in one report). The rule now keeps
rows from the earliest filing and drops only later re-reports. Difference: +$45M overall (1.2%),
+$7M in Senate general elections. Neither rule is exact; the FEC file does not say which form a row
came from.

### 13. The pushbuild cross-check missed a quarter of the races and never compared margins — Fixed (95%)

Contest names vary by state ("U.S.  Senate" with two spaces, "Senator in Congress", "Governor / Lt.
Governor", "FOR GOVERNOR"), so the old regex matched 33 of 44 comparable races, and it compared only
vote totals. It now matches all 44 and compares margins too (see "What held up"). The README's note
that pushbuild's Colorado snapshot had "about 22% reporting" was also wrong: pushbuild's Colorado
total is about 20% *below* civicAPI's, i.e. a lagging snapshot, not a 22%-reported one.

### 14. Alaska's margins are first-choice votes only — Noted on the chart (90%)

Both Alaska races go to ranked-choice tabulation on Nov 18; the Senate race also has two Republicans
and a second "Sullivan". The ticket-splitting chart now says so. Alaska's money per vote ($577) is
also inflated by the slow count (74% reported) and will fall; that note was already there.

### 15. "Raised" included cash carried into the cycle — Fixed (85%)

The Sankey's "2.3× more" compared total inflows (receipts plus cash on hand at the start of 2025).
Receipts alone give 2.6× ($713M vs $275M). The headline now uses receipts.

### 16. Things to keep in mind that were not changed

- **Different offices.** Every "shift since 2024" compares a Senate or governor race with a
  presidential race, so candidate effects are baked in (Vermont's governor, for example, is a popular
  Republican in a Harris +32 state). The charts say so; there is no 2022 county baseline in the repo.
- **The 95%-counted filter** used by the within-state charts keeps 670 counties in 32 states, mostly
  fast-counting states with small counties. The results are about those counties, not the country.
- **Wikipedia as a source** for the 2006–2022 midterm exit polls is secondary. 2022 values were
  spot-checked against the published Edison tables and matched; earlier years were not re-checked.
- **"47 or fewer" is open-ended**, so its probability covers many outcomes; the chart notes it.
- **The early estimates** (UF v0.2 turnout, partial counts in CA, AZ, AK, WA) will move. Re-run after
  certification.

## Data refresh (what is and isn't newer than Nov 7)

- **civicAPI**: not reachable from this environment (blocked by the network allowlist), so results
  are still the Nov 7, 18:14 UTC snapshot. Re-download `races.csv` and `sen_gov_county.csv` from
  the same endpoints and re-run the pipeline; nothing else needs to change.
- **pushbuild**: last commit "Results as of November 6, 2026, 11:32 PM ET"; the repo says it will be
  refreshed after certification.
- **UF Election Lab**: v0.2 (Nov 3) is still the current 2026 release.
- **FEC**: independent expenditures keep arriving (24-hour reports) and post-general campaign
  reports are due Dec 3, 2026; the bulk files were not reachable from here.
- **Polymarket**: the markets closed Nov 4; the series in the repo is complete.
- **Press (Nov 5–8)**: Mississippi — Colom led Hyde-Smith by 1,138 votes with ~15,000 affidavit
  ballots and mail ballots arriving through Nov 10 to process; Mississippi has no automatic recount.
  Alaska — ranked-choice tabulation scheduled for Nov 18; an Alaska Beacon analysis of the cast-vote
  record found Heikes's voters' second choices favor Sullivan.

## Scope change

The 8-page LinkedIn carousel (`viz/linkedin_story/`) was dropped and removed from the repo; the
project now only makes standalone one-image charts.
