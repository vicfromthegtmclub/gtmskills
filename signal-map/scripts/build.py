#!/usr/bin/env python3
"""Build a signal map page: validate a data JSON, inject it into the template.

Usage: python3 build.py data.json out.html
"""
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
TIERS = {"now", "next", "opp", "skip"}


def check(d):
    errs = []
    for k in ("company", "title", "eyebrow", "lede", "specs", "pains", "signals", "footer"):
        if k not in d:
            errs.append(f"missing top-level key: {k}")
    sigs = d.get("signals", [])
    if not 8 <= len(sigs) <= 15:
        errs.append(f"{len(sigs)} signals; aim for 10 to 12 (8 to 15 allowed)")
    for i, s in enumerate(sigs, 1):
        for k in ("n", "ty", "t", "ef", "eo", "why", "setup", "res"):
            if k not in s:
                errs.append(f"signal {i}: missing {k}")
        if s.get("t") not in TIERS:
            errs.append(f"signal {i}: tier must be one of {sorted(TIERS)}")
        for k in ("ef", "eo"):
            if not isinstance(s.get(k), int) or not 1 <= s[k] <= 5:
                errs.append(f"signal {i}: {k} must be an int 1..5")
    now = [s for s in sigs if s.get("t") == "now"]
    if not 3 <= len(now) <= 5:
        errs.append(f"{len(now)} 'now' signals; launch 3 to 5 this week")
    order = {"now": 0, "next": 1, "opp": 2, "skip": 3}
    ranks = [order.get(s.get("t"), 9) for s in sigs]
    if ranks != sorted(ranks):
        errs.append("signals must be ordered now > next > opp > skip")
    for i, m in enumerate(d.get("copy", {}).get("mails", []), 1):
        if not isinstance(m.get("sig"), int) or not 1 <= m["sig"] <= len(sigs):
            errs.append(f"mail {i}: sig must be a 1-based signal rank")
    raw = json.dumps(d, ensure_ascii=False)
    if "—" in raw:
        errs.append("em dash found; rewrite with a comma, colon or period")
    return errs


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    data = json.loads(Path(sys.argv[1]).read_text())
    errs = check(data)
    if errs:
        print("Fix before publishing:\n- " + "\n- ".join(errs))
        sys.exit(1)
    blob = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    title = data["title"].replace("&", "&amp;").replace("<", "&lt;")
    html = TEMPLATE.read_text().replace("__TITLE__", title).replace("__DATA__", blob)
    Path(sys.argv[2]).write_text(html)
    print(f"Built {sys.argv[2]}: {len(data['signals'])} signals, "
          f"{len(data.get('copy', {}).get('mails', []))} emails")


if __name__ == "__main__":
    main()
