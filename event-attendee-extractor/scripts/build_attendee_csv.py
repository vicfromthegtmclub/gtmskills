#!/usr/bin/env python3
"""
Merge the parsed guest list with enrichment results into the final attendee CSV.

Usage:
    python3 build_attendee_csv.py guests_parsed.csv enrichment.json \
        --event "Event name" --date "2026-10-06" --url "https://..." --platform partiful \
        --out /mnt/user-data/outputs/event-attendees.csv

enrichment.json: { "<guest_id>": { "job_title": "", "company": "", "linkedin_url": "",
                   "other_social_url": "", "confidence": "high|medium|low|none",
                   "match_evidence": "", "notes": "" }, ... }
Guests missing from the JSON get confidence "none".
"""

import argparse
import csv
import json
from collections import Counter

FINAL_COLS = [
    "guest_id", "full_name", "first_name", "last_name", "partial_name", "rsvp_status",
    "job_title", "company", "linkedin_url", "other_social_url", "confidence", "match_evidence",
    "event_name", "event_date", "event_url", "source_platform", "notes",
]
VALID_CONF = {"high", "medium", "low", "none"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parsed_csv")
    ap.add_argument("enrichment_json")
    ap.add_argument("--event", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--platform", default="")
    ap.add_argument("--out", default="attendees.csv")
    args = ap.parse_args()

    with open(args.parsed_csv, newline="", encoding="utf-8") as f:
        guests = list(csv.DictReader(f))
    with open(args.enrichment_json, encoding="utf-8") as f:
        enrich = json.load(f)

    rows, conf_count = [], Counter()
    for g in guests:
        e = enrich.get(g["guest_id"], {})
        conf = (e.get("confidence") or "none").lower()
        if conf not in VALID_CONF:
            conf = "low"
        # a partial name can never be more than medium, whatever the enrichment says
        if g.get("partial_name") == "yes" and conf == "high":
            conf = "medium"
        notes = e.get("notes", "")
        if g.get("raw_bio") and g["raw_bio"] not in notes:
            notes = (notes + " | bio on page: " + g["raw_bio"]).strip(" |")
        if g.get("plus_ones"):
            notes = (notes + f" | brings +{g['plus_ones']}").strip(" |")
        rows.append({
            "guest_id": g["guest_id"],
            "full_name": g["full_name"],
            "first_name": g["first_name"],
            "last_name": g["last_name"],
            "partial_name": g.get("partial_name", ""),
            "rsvp_status": g.get("rsvp_status", ""),
            "job_title": e.get("job_title", "") if conf != "none" else "",
            "company": e.get("company", "") if conf != "none" else "",
            "linkedin_url": e.get("linkedin_url", "") if conf != "none" else "",
            "other_social_url": e.get("other_social_url", ""),
            "confidence": conf,
            "match_evidence": e.get("match_evidence", ""),
            "event_name": args.event,
            "event_date": args.date,
            "event_url": args.url,
            "source_platform": args.platform,
            "notes": notes,
        })
        conf_count[conf] += 1

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FINAL_COLS)
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} attendees -> {args.out}")
    print("confidence:", ", ".join(f"{k}={conf_count[k]}" for k in ["high", "medium", "low", "none"]))


if __name__ == "__main__":
    main()
