#!/usr/bin/env python3
"""
Warm-intro path finder: deterministic pass over a LinkedIn Connections.csv.

Modes
-----
  --target "Acme"    Find who in the network can open a door at Acme.
  --reverse          Rank every company the network already reaches.
  --profile          Describe the network: employers, cohorts, coverage.

Emits JSON on stdout. The judgment pass (does this person plausibly know
the buyer?) happens after, in the model, on the shortlist only.
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime

import pandas as pd

# Companies that are not companies.
JUNK = {
    "freelance", "independant", "indepandant", "self employed", "selfemployed",
    "stealth startup", "stealth", "stealth mode", "unemployed", "retired",
    "none", "n a", "na", "various", "student", "etudiant",
    "looking for opportunities", "open to work", "consultant", "auto entrepreneur",
}

# Not commercial accounts.
NON_COMMERCIAL = re.compile(
    r"\b(?:universite|university|ecole|school|lycee|college|master|mba|"
    r"association|mairie|ministere|prefecture)\b"
)

LEGAL = r"\b(sas|sasu|sarl|inc|ltd|limited|llc|gmbh|bv|ab|corp|corporation|" \
        r"company|group|holding|international|france|french|uk|usa|us|europe|" \
        r"emea|the)\b"

SENIORITY = [
    ("founder", 5, r"founder|fondat|co-found|cofound|owner|propriétaire"),
    ("c_level", 5, r"\bceo\b|\bcto\b|\bcfo\b|\bcoo\b|\bcro\b|\bcmo\b|\bcpo\b|"
                   r"chief |président|president|managing director|directeur général|general manager"),
    ("vp", 4, r"\bvp\b|vice president|vice-président"),
    ("head", 4, r"\bhead of\b|\bhead,|directeur|director|responsable"),
    ("manager", 3, r"manager|lead\b|team lead|chef de|superviseur"),
    ("senior_ic", 2, r"senior|principal|staff|expert|consultant"),
    ("ic", 1, r".*"),
]


def normalize_company(raw) -> str:
    s = str(raw or "").lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"\(.*?\)", " ", s)            # drop "(ex-Beavr)", "(YC W24)"
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"[\u0080-\uffff]", " ", s)    # emoji, e.g. "trumpet 🎺"
    s = re.sub(LEGAL, " ", s)
    return re.sub(r"\s+", " ", s).strip()


def seniority(position) -> tuple:
    p = str(position or "").lower()
    for label, score, pattern in SENIORITY:
        if re.search(pattern, p):
            return label, score
    return "unknown", 1


def load(path: str) -> pd.DataFrame:
    """LinkedIn prefixes the real header with a 3-line privacy notice."""
    skip = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if line.startswith("First Name,"):
                skip = i
                break
            if i > 15:
                break

    df = pd.read_csv(path, skiprows=skip)
    df = df.dropna(subset=["Company"])
    df["company_norm"] = df["Company"].map(normalize_company)
    df = df[df["company_norm"].ne("") & ~df["company_norm"].isin(JUNK)]
    df = df[~df["company_norm"].str.contains(NON_COMMERCIAL, na=False)]
    df["connected_on"] = pd.to_datetime(
        df["Connected On"], format="%d %b %Y", errors="coerce"
    )
    df[["sen_label", "sen_score"]] = df["Position"].apply(
        lambda p: pd.Series(seniority(p))
    )
    df["has_email"] = df["Email Address"].notna()
    return df.reset_index(drop=True)


def infer_own_employers(df: pd.DataFrame, top: int = 3) -> list:
    """Your own employers surface as dense clusters of long-lived ties."""
    out = []
    for name, n in df["company_norm"].value_counts().head(12).items():
        sub = df[df["company_norm"] == name]
        span_years = (sub["connected_on"].max() - sub["connected_on"].min()).days / 365
        if n >= 10 and span_years >= 1.5:
            out.append({"company": name, "contacts": int(n),
                        "span_years": round(span_years, 1)})
    return out[:top]


def tie_strength(row, today: datetime) -> tuple:
    """
    0-100. Old ties beat new ones: a 2021 connection survived a job change
    or two and probably came from a real interaction. A 2026 connection is
    most likely an inbound follow off a LinkedIn post.
    """
    score, why = 0, []
    if pd.isna(row["connected_on"]):
        return 20, ["connection date unknown"]

    age_years = (today - row["connected_on"]).days / 365
    if age_years >= 4:
        score += 45; why.append(f"tie is {age_years:.0f}y old, predates the content era")
    elif age_years >= 2:
        score += 32; why.append(f"tie is {age_years:.0f}y old")
    elif age_years >= 1:
        score += 18; why.append("tie is about a year old")
    elif age_years >= 0.25:
        score += 8; why.append("recent tie, low context")
    else:
        score += 3; why.append("connected within the last 3 months, likely inbound")

    if row["has_email"]:
        score += 12; why.append("shared their email on export, open by default")

    if row["sen_score"] >= 5:
        score += 8; why.append("founder or C-level, can decide to make the intro alone")

    return min(score, 100), why


def path_relevance(row, cohort_size: int) -> tuple:
    """Would this person's intro actually land on the right desk?"""
    score, why = 0, []
    score += row["sen_score"] * 9
    why.append(f"{row['sen_label'].replace('_', ' ')} at the target")

    if cohort_size >= 8:
        score += 5; why.append(f"{cohort_size} contacts there, you know the building")
    elif cohort_size >= 3:
        score += 12; why.append(f"{cohort_size} contacts there, cross-checkable")
    else:
        score += 18; why.append("only route you have in")

    if row["sen_score"] <= 2 and cohort_size >= 8:
        score -= 15; why.append("junior at a company you already reach higher up")

    return max(min(score, 100), 0), why


def find_paths(df: pd.DataFrame, target: str, today: datetime) -> dict:
    tnorm = normalize_company(target)
    exact = df[df["company_norm"] == tnorm]
    fuzzy = df[df["company_norm"].str.contains(re.escape(tnorm), na=False)] \
        if tnorm else df.iloc[0:0]
    hits = exact if len(exact) else fuzzy

    paths = []
    for _, row in hits.iterrows():
        ts, tw = tie_strength(row, today)
        pr, pw = path_relevance(row, len(hits))
        paths.append({
            "name": f"{row['First Name']} {row['Last Name']}",
            "position": row["Position"],
            "company": row["Company"],
            "url": row["URL"],
            "connected_on": None if pd.isna(row["connected_on"])
                            else row["connected_on"].date().isoformat(),
            "tie_strength": ts,
            "path_relevance": pr,
            "tie_reasons": tw,
            "relevance_reasons": pw,
        })

    paths.sort(key=lambda p: (p["tie_strength"] + p["path_relevance"]), reverse=True)
    return {
        "target": target,
        "target_normalized": tnorm,
        "match_type": "exact" if len(exact) else ("fuzzy" if len(fuzzy) else "none"),
        "path_count": len(paths),
        "paths": paths[:15],
    }


def reverse(df: pd.DataFrame, today: datetime, min_score: int, limit: int) -> dict:
    """
    Different question, different scoring.

    Target mode asks "how do I get in?" and rewards scarcity: one route in
    is still a route. Reverse mode asks "is this account worth walking
    toward?", where scarcity is evidence of nothing. Reusing target-mode
    relevance here ranks solo founders of one-person shops at the top:
    maximum seniority, minimum contacts, zero commercial value.

    So: gate on plurality (a company you know one person at is not an
    account you have coverage of), then rank on tie quality and depth.
    Whether the account fits the ICP is not knowable from this file and
    is deliberately left to the judgment pass.
    """
    own = {e["company"] for e in infer_own_employers(df)}
    rows = []

    for name, sub in df.groupby("company_norm"):
        if name in own or len(sub) < 2:
            continue

        scored = []
        for _, r in sub.iterrows():
            ts, tw = tie_strength(r, today)
            scored.append((ts, r, tw))
        scored.sort(key=lambda x: (x[0], x[1]["sen_score"]), reverse=True)

        best_ts, best, best_why = scored[0]
        senior_count = int((sub["sen_score"] >= 4).sum())
        old_ties = int((sub["connected_on"] < today - pd.Timedelta(days=730)).sum())

        depth = min(len(sub) * 4, 24) + senior_count * 6 + old_ties * 5
        combined = best_ts + min(depth, 60)

        rows.append({
            "company": best["Company"],
            "contacts": len(sub),
            "senior_contacts": senior_count,
            "ties_over_2y": old_ties,
            "best_contact": f"{best['First Name']} {best['Last Name']}",
            "best_position": best["Position"],
            "best_connected_on": None if pd.isna(best["connected_on"])
                                 else best["connected_on"].date().isoformat(),
            "tie_strength": best_ts,
            "depth": min(depth, 60),
            "combined": combined,
            "why": best_why,
        })

    rows = [r for r in rows if r["combined"] >= min_score]
    rows.sort(key=lambda r: r["combined"], reverse=True)
    return {"reachable_companies": len(rows), "accounts": rows[:limit]}


def profile(df: pd.DataFrame, today: datetime) -> dict:
    by_year = df["connected_on"].dt.year.value_counts().sort_index()
    return {
        "total_usable_connections": len(df),
        "distinct_companies": int(df["company_norm"].nunique()),
        "with_email": int(df["has_email"].sum()),
        "likely_own_employers": infer_own_employers(df),
        "connections_by_year": {int(k): int(v) for k, v in by_year.items()},
        "ties_older_than_3y": int(
            (df["connected_on"] < today - pd.Timedelta(days=1095)).sum()
        ),
        "seniority_mix": df["sen_label"].value_counts().to_dict(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--target")
    ap.add_argument("--reverse", action="store_true")
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--min-score", type=int, default=60)
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    df = load(args.csv)
    today = datetime.now()

    if args.profile:
        out = profile(df, today)
    elif args.reverse:
        out = reverse(df, today, args.min_score, args.limit)
    elif args.target:
        out = find_paths(df, args.target, today)
    else:
        ap.error("pass --target, --reverse or --profile")

    json.dump(out, sys.stdout, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
