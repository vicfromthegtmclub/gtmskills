#!/usr/bin/env python3
"""
Parse a raw guest-list dump (pasted text, page text from a browser, or a transcription of
screenshots) into a clean CSV with one row per guest.

Usage:
    python3 parse_guest_list.py raw_guests.txt --platform partiful --event "Event name" --out guests_parsed.csv

Input format: one guest per line. Optional extra info on the same line separated by " | ",
for example "Jane Doe | VP Marketing at Acme". Luma-style dumps where the bio is on the
following line are handled with --platform luma.

Output columns:
    guest_id, full_name, first_name, last_name, partial_name, rsvp_status, plus_ones, raw_bio, raw_line
"""

import argparse
import csv
import re
import sys
import unicodedata

STATUS_HEADERS = {
    "going": "going",
    "going!": "going",
    "maybe": "maybe",
    "can't go": "declined",
    "cant go": "declined",
    "not going": "declined",
    "interested": "interested",
    "waitlist": "waitlist",
    "waitlisted": "waitlist",
    "hosts": "host",
    "attendees": "going",
    "guests": "going",
    "speakers": "speaker",
}

NOISE_PATTERNS = [
    r"^\+\d+$",                       # "+3"
    r"^\d+ (guests?|on the list|going|attendees?|members?)$",
    r"^(view all|see all|show more|load more|see more)$",
    r"^(guest list|guests list|attendee list|who's going|who is going|people going)$",
    r"^\d+ events? attended$",
    r"^(organi[sz]er|event host|co-host)$",
    r"^(you|me)$",
    r"^(rsvp|register|get on the list|join)$",
    r"^\W+$",                          # emoji-only or punctuation-only lines
]

BADGES = {"host": "host", "co-host": "host", "cohost": "host", "organizer": "host",
          "organiser": "host", "event host": "host", "speaker": "speaker"}


def strip_emoji(s: str) -> str:
    return "".join(ch for ch in s if unicodedata.category(ch) not in {"So", "Sk", "Cs", "Co"}).strip()


def is_noise(line: str) -> bool:
    low = line.lower().strip()
    return any(re.match(p, low) for p in NOISE_PATTERNS)


def looks_like_name(line: str) -> bool:
    """Heuristic: 1-4 tokens, mostly alphabetic, no sentence punctuation, not too long."""
    s = strip_emoji(line)
    if not s or len(s) > 60:
        return False
    if re.search(r"[.!?;:]{1}\s|\bat\b|\b@\b|http", s.lower()) and not re.match(r"^[A-Z][a-z]+ [A-Z]\.$", s):
        return False
    tokens = s.replace("-", " ").split()
    if not 1 <= len(tokens) <= 4:
        return False
    alpha = sum(1 for t in tokens if re.match(r"^[A-Za-zÀ-ÿ'’.]+$", t))
    return alpha >= max(1, len(tokens) - 1)


def split_name(full: str):
    full = strip_emoji(full)
    full = re.sub(r"\s+", " ", full).strip(" ,")
    partial = False
    tokens = full.split(" ")
    if len(tokens) == 1:
        return full, tokens[0], "", True
    last = " ".join(tokens[1:])
    if re.match(r"^[A-Za-zÀ-ÿ]\.?$", last.strip()):
        partial = True
    return full, tokens[0], last, partial


def parse(lines, platform):
    guests = []
    status = "going"
    pending = None  # for luma: name waiting for a bio line

    def flush():
        nonlocal pending
        if pending:
            guests.append(pending)
            pending = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        low = strip_emoji(line).lower().strip(" :")

        # status headers like "Going (12)" or "Maybe"
        m = re.match(r"^([a-z' ]+?)\s*\(?\d*\)?$", low)
        if m and m.group(1).strip() in STATUS_HEADERS:
            flush()
            status = STATUS_HEADERS[m.group(1).strip()]
            continue

        if is_noise(line):
            # "+2" on its own line applies to the previous guest
            pm = re.match(r"^\+(\d+)$", line)
            if pm and (pending or guests):
                target = pending or guests[-1]
                target["plus_ones"] = pm.group(1)
            continue

        # badge lines
        if low in BADGES:
            target = pending or (guests[-1] if guests else None)
            if target:
                target["rsvp_status"] = BADGES[low]
            continue

        name_part, bio_part = line, ""
        if " | " in line:
            name_part, bio_part = [p.strip() for p in line.split(" | ", 1)]

        # trailing "+N" or badge inside the line
        pm = re.search(r"\s\+(\d+)$", name_part)
        plus = pm.group(1) if pm else ""
        if pm:
            name_part = name_part[: pm.start()]
        badge = ""
        for b, s in BADGES.items():
            if re.search(rf"\b{re.escape(b)}\b$", name_part.lower()):
                badge = s
                name_part = re.sub(rf"\s*\b{re.escape(b)}\b$", "", name_part, flags=re.I)

        if platform == "luma" and pending and not looks_like_name(line):
            pending["raw_bio"] = (pending["raw_bio"] + " " + line).strip()
            continue

        if not looks_like_name(name_part):
            # attach to previous as bio if plausible, else skip
            target = pending or (guests[-1] if guests else None)
            if target and len(line) < 160:
                target["raw_bio"] = (target["raw_bio"] + " " + line).strip()
            continue

        flush()
        full, first, last, partial = split_name(name_part)
        pending = {
            "full_name": full,
            "first_name": first,
            "last_name": last,
            "partial_name": "yes" if partial else "no",
            "rsvp_status": badge or status,
            "plus_ones": plus,
            "raw_bio": bio_part,
            "raw_line": raw.strip(),
        }
    flush()

    # dedupe on normalised full name
    seen, out = set(), []
    for g in guests:
        key = g["full_name"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(g)
    for i, g in enumerate(out, 1):
        g["guest_id"] = f"g_{i:03d}"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--platform", default="generic",
                    choices=["partiful", "luma", "eventbrite", "meetup", "conference", "generic"])
    ap.add_argument("--event", default="")
    ap.add_argument("--out", default="guests_parsed.csv")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        lines = f.readlines()
    guests = parse(lines, args.platform)

    cols = ["guest_id", "full_name", "first_name", "last_name", "partial_name",
            "rsvp_status", "plus_ones", "raw_bio", "raw_line"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for g in guests:
            w.writerow({c: g.get(c, "") for c in cols})

    partial = sum(1 for g in guests if g["partial_name"] == "yes")
    print(f"{len(guests)} guests parsed ({partial} with partial names) -> {args.out}")
    if not guests:
        print("No names recognised. Check the raw file has one guest per line.", file=sys.stderr)


if __name__ == "__main__":
    main()
