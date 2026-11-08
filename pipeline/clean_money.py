"""FEC campaign money + outside spending, matched to 2026 Senate general-election results.

Inputs
  data/raw/fec/weball26.txt                     candidate summary (principal campaign committees)
  data/raw/fec/independent_expenditure_2026.csv outside spending (super PACs, parties, groups)
  data/raw/civicapi/races.csv                   statewide race results (for Senate vote totals)

Outputs (data/clean/)
  ie_clean.csv               outside spending after the cleaning rules below
  senate_candidates.csv      one row per Senate general candidate: votes, campaign money, outside money
  senate_races.csv           one row per Senate race: total money, total votes, money per vote, margin
  senate_money_flow.csv      source -> party -> use edges for a Sankey diagram
"""
import unicodedata

import pandas as pd

from common import CLEAN, RAW, STATES, ie_side, note, party_bucket

WEBALL_COLS = [
    "cand_id", "cand_name", "cand_ici", "pty_cd", "party", "receipts", "trans_from_auth",
    "disbursements", "trans_to_auth", "coh_start", "coh_end", "cand_contrib", "cand_loans",
    "other_loans", "cand_loan_repay", "other_loan_repay", "debts", "indiv_contrib", "state",
    "district", "spec_election", "prim_election", "run_election", "gen_election",
    "gen_election_pct", "pac_contrib", "party_contrib", "coverage_end", "indiv_refunds", "cmte_refunds",
]

# No single real independent expenditure comes near this; the 2026 file has a handful of
# junk filings at $1B-$9B each. Anything above the cap is dropped and logged.
IE_CAP = 100_000_000


def name_tokens(name: str) -> set[str]:
    """Upper-case name words with accents stripped ("Luján" -> "LUJAN"), punctuation removed."""
    n = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().upper()
    return {t for t in n.replace(",", " ").replace(".", " ").split() if len(t) > 2}


def match_fec(ballot: pd.DataFrame, fec: pd.DataFrame) -> pd.Series:
    """FEC candidate ID for each ballot row: same state, and the ballot surname appears anywhere
    in the FEC name (handles "Fetty Anderson", "Arenholz, Ashley Hinson").

    Among several same-surname filers, the one sharing the most name words with the ballot name
    wins (so "Darline Graham" -> GRAHAM, DARLINE and not GRAHAM, LINDSEY O.); money breaks ties.
    If two ballot candidates in one race still land on the same ID (Alaska's "Daniel J. Sullivan Jr."
    and Sen. Dan Sullivan), only the one with more votes keeps it, so no committee is counted twice."""
    fec = fec.assign(tokens=fec.cand_name.map(name_tokens)).sort_values("receipts", ascending=False)
    out = {}
    for i, row in ballot.iterrows():
        last = next(iter(name_tokens(row["last"])), None)
        full = name_tokens(row["candidate"])
        pool = fec[fec.state == row["state"]]
        hit = pool[pool.tokens.map(lambda t: last in t)] if last else pool.iloc[0:0]
        if len(hit):
            overlap = hit.tokens.map(lambda t: len(t & full))
            hit = hit[overlap == overlap.max()]  # already sorted by receipts, so [0] is the richest
        out[i] = hit.cand_id.iloc[0] if len(hit) else None
    ids = pd.Series(out)
    ranked = ballot.assign(cand_id=ids).sort_values("votes", ascending=False)
    dup = ranked.cand_id.notna() & ranked.duplicated(["race_id", "cand_id"], keep="first")
    if dup.any():
        note("senate: same FEC ID matched twice in one race, kept for the bigger vote-getter only: "
             + ", ".join(f"{r.candidate} ({r.state})" for r in ranked[dup].itertuples()))
    ids[ranked.index[dup]] = None
    return ids


def load_weball() -> pd.DataFrame:
    w = pd.read_csv(RAW / "fec" / "weball26.txt", sep="|", header=None, names=WEBALL_COLS, dtype={"cand_id": str})
    w["office"] = w.cand_id.str[0]
    w["last"] = w.cand_name.str.split(",").str[0].str.strip().str.upper()
    w["bucket"] = w.party.map({"DEM": "D", "DFL": "D", "REP": "R"}).fillna("O")
    return w


def clean_ie() -> pd.DataFrame:
    ie = pd.read_csv(RAW / "fec" / "independent_expenditure_2026.csv", low_memory=False, dtype={"cand_id": str})
    n0, d0 = len(ie), ie.exp_amo.sum()

    # 1. Keep only the latest amendment of each transaction.
    ie = ie.sort_values("file_num").drop_duplicates(["spe_id", "tran_id"], keep="last")
    # 2. Drop impossible amounts (logged so they can be reviewed).
    junk = ie[ie.exp_amo > IE_CAP]
    junk[["cand_name", "spe_nam", "exp_amo", "pur", "receipt_dat"]].to_csv(CLEAN / "ie_dropped_junk.csv", index=False)
    ie = ie[(ie.exp_amo > 0) & (ie.exp_amo <= IE_CAP)]
    # 3. The same spend often appears in a 24/48-hour report and again in a later periodic report.
    #    Rows with the same spender, candidate, amount and distribution date are kept only from the
    #    earliest filing they appear in. Identical rows inside ONE filing are kept: those are separate
    #    buys (e.g. two $1.25M ad buys on the same day), not re-reports.
    key = ["spe_id", "cand_id", "exp_amo", "dissem_dt"]
    n_before, d_before = len(ie), ie.exp_amo.sum()
    first_filing = ie.groupby(key, dropna=False).file_num.transform("min")
    ie = ie[ie.file_num == first_filing]
    note(f"outside money: {n_before - len(ie):,} rows / ${(d_before - ie.exp_amo.sum())/1e6:,.0f}M dropped as "
         "re-reports of the same expenditure in a later filing")

    note(f"outside money: {n0:,} rows / ${d0/1e9:,.1f}B raw -> {len(ie):,} rows / ${ie.exp_amo.sum()/1e9:,.2f}B clean "
         f"({len(junk)} junk rows over ${IE_CAP/1e6:.0f}M dropped, totalling ${junk.exp_amo.sum()/1e9:,.1f}B)")
    ie.to_csv(CLEAN / "ie_clean.csv", index=False)
    return ie


def senate_general_ie(ie: pd.DataFrame) -> pd.DataFrame:
    """Outside spending in 2026 Senate general-election races, with the side it helped and a parsed
    distribution date. Every chart that shows Senate outside money reads this one table."""
    g = ie[(ie.can_office == "S") & (ie.ele_type == "G")].copy()
    g["side"] = [ie_side(p, s) for p, s in zip(g.cand_pty_aff, g.sup_opp)]
    g["date"] = pd.to_datetime(g.dissem_dt, format="%d-%b-%y", errors="coerce")
    g = g[["cand_id", "cand_name", "cand_pty_aff", "can_office_state", "spe_id", "spe_nam", "sup_opp", "side",
           "exp_amo", "date", "dissem_dt", "pur", "file_num"]].rename(columns={"can_office_state": "state"})
    g.to_csv(CLEAN / "ie_senate_general.csv", index=False)
    by = g.groupby("side").exp_amo.sum() / 1e6
    undated = g[g.date.isna()].exp_amo.sum() / g.exp_amo.sum()
    note(f"outside money, Senate general elections: ${g.exp_amo.sum()/1e6:,.0f}M in {len(g):,} rows; "
         f"helping D ${by.get('D', 0):,.0f}M, helping R ${by.get('R', 0):,.0f}M, independents/other ${by.get('O', 0):,.0f}M; "
         f"{undated:.1%} of dollars have no distribution date")
    return g


def senate_ballot() -> pd.DataFrame:
    """Statewide 2026 Senate general-election candidates and votes from civicAPI."""
    r = pd.read_csv(RAW / "civicapi" / "races.csv", low_memory=False)
    r = r[(r.type == "US Senate") & r.election_type.isin(["Statewide", "General", "Special Election"])
          & r.state.isin(STATES)]
    r = r[~r.election_name.str.contains("Primary|Runoff", case=False)]
    ascii_name = r.candidate.map(lambda n: unicodedata.normalize("NFKD", str(n)).encode("ascii", "ignore").decode())
    r["last"] = ascii_name.str.split().str[-1].str.upper().str.replace(r"[^A-Z\-']", "", regex=True)
    # Suffixes like "Jr." leave the real surname one word earlier.
    suffix = r["last"].isin(["JR", "SR", "II", "III", "IV"])
    r.loc[suffix, "last"] = ascii_name[suffix].str.split().str[-2].str.upper().str.replace(r"[^A-Z\-']", "", regex=True)
    r["bucket"] = r.party.map(party_bucket)
    races_per_state = r.groupby("state").race_id.nunique()
    if (races_per_state > 1).any():
        note(f"senate: more than one Senate race in {', '.join(races_per_state[races_per_state > 1].index)}")
    return r


def main() -> None:
    w = load_weball()
    ie = clean_ie()
    g = senate_general_ie(ie)
    ballot = senate_ballot()

    # Match ballot candidates to FEC IDs by state + surname (see match_fec for tie-breaking).
    fec_s = w[w.office == "S"]
    ballot["cand_id"] = match_fec(ballot, fec_s)
    cand = ballot.merge(fec_s[["cand_id", "receipts", "disbursements", "coh_start", "coh_end", "indiv_contrib",
                               "pac_contrib", "party_contrib", "cand_contrib", "cand_loans", "trans_from_auth",
                               "coverage_end"]], on="cand_id", how="left")

    by_cand = g.pivot_table(index="cand_id", columns="sup_opp", values="exp_amo", aggfunc="sum", fill_value=0)
    by_cand = by_cand.rename(columns={"S": "outside_support", "O": "outside_oppose"})
    cand = cand.merge(by_cand, left_on="cand_id", right_index=True, how="left")
    cand[["outside_support", "outside_oppose"]] = cand[["outside_support", "outside_oppose"]].fillna(0)

    major = cand[cand.votes >= cand.groupby("race_id").votes.transform("sum") * 0.05]
    note(f"senate: {major.cand_id.notna().sum()} of {len(major)} candidates with >=5% of the vote matched to an FEC ID; "
         f"unmatched: {', '.join(major[major.cand_id.isna()].candidate + ' (' + major[major.cand_id.isna()].state + ')') or 'none'}")
    cand.to_csv(CLEAN / "senate_candidates.csv", index=False)

    # Race level. Outside money counts every general-election IE in that state's Senate race,
    # including spending aimed at minor candidates who aren't matched above.
    race_ie = g.groupby("state").exp_amo.sum()
    races = cand.groupby(["race_id", "election_name", "state"]).agg(
        total_votes=("votes", "sum"), campaign_spending=("disbursements", "sum"),
        pct_reporting=("percent_reporting", "max")).reset_index()
    races["outside_spending"] = races.state.map(race_ie).fillna(0)
    races["total_money"] = races.campaign_spending + races.outside_spending
    races["money_per_vote"] = races.total_money / races.total_votes
    top2 = cand.sort_values("votes", ascending=False).groupby("race_id").head(2)
    margin = top2.groupby("race_id").apply(lambda d: (d.votes.max() - d.votes.min()) / cand[cand.race_id == d.name].votes.sum(),
                                           include_groups=False)
    races["top_two_margin"] = races.race_id.map(margin)
    races.sort_values("money_per_vote", ascending=False).to_csv(CLEAN / "senate_races.csv", index=False)
    note(f"senate: {len(races)} races; money per vote ranges ${races.money_per_vote.min():.2f}"
         f"-${races.money_per_vote.max():.2f} (campaign spending is cycle-to-date, includes primaries)")

    # Sankey edges: where general-election candidates' campaign money came from and went.
    m = cand.dropna(subset=["cand_id"]).drop_duplicates("cand_id")
    m = m.assign(self_funding=m.cand_contrib + m.cand_loans)
    named = ["indiv_contrib", "pac_contrib", "party_contrib", "self_funding", "trans_from_auth"]
    m["other_receipts"] = (m.receipts - m[named].sum(axis=1)).clip(lower=0)
    label = {"indiv_contrib": "Individual donors", "pac_contrib": "PACs", "party_contrib": "Party committees",
             "self_funding": "Self-funding", "trans_from_auth": "Joint fundraising transfers",
             "other_receipts": "Other"}
    side = m.bucket.map({"D": "Democratic campaigns", "R": "Republican campaigns"}).fillna("Other campaigns")
    edges = []
    for col, name in label.items():
        for s, v in m.groupby(side)[col].sum().items():
            edges.append((name, s, v))
    for s, v in m.groupby(side).coh_start.sum().items():
        edges.append(("Cash on hand before 2025", s, v))
    for s, d in m.groupby(side):
        edges.append((s, "Spent", d.disbursements.sum()))
        edges.append((s, "Cash left (mid-Oct)", d.coh_end.sum()))
    # Outside money never passes through a campaign: draw it as its own band. Same universe and
    # side definition as the timing and per-state charts (every Senate general-election IE).
    for b, v in g.groupby("side").exp_amo.sum().items():
        edges.append(("Outside groups", {"D": "Helping Democrats", "R": "Helping Republicans"}.get(b, "Independents and others"), v))
    pd.DataFrame(edges, columns=["source", "target", "value"]).to_csv(CLEAN / "senate_money_flow.csv", index=False)


if __name__ == "__main__":
    main()
