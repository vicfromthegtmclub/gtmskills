---
title: Warm intro finder
kind: Skill
description: Mines your LinkedIn connections to find a warm introduction or referral path into a target account, scores each path, and drafts the intro ask.
author: GTM Club
source: Member
updated: 2026-08-10
---


# Warm-intro and referral path finder

Cold is not the only way in. Given a target account, find the warm path
hiding in the network. Given the whole network, find which accounts are
already reachable.

## Before anything else

Ask for the LinkedIn export if it is not already provided:
Settings → Data privacy → Get a copy of your data → Connections.
The file arrives as `Connections.csv` with a 3-line privacy notice above
the real header. `scripts/match.py` handles that automatically.

## Workflow

### 1. Profile the network first, always

```bash
python3 scripts/match.py <path-to-Connections.csv> --profile
```

Read the output before doing anything else, and tell the user what it
means for them. Two numbers decide how much the rest is worth:

- **`with_email`**: usually near zero. LinkedIn only exports an email
  when that person opted in. If it is low, say so, because it removes
  the strongest available relationship signal.
- **`connections_by_year`**: if the last 12 months dominate the file,
  most of the network is inbound from content, not relationships. Warn
  the user plainly rather than scoring inbound follows as warm ties.

`likely_own_employers` is inferred from dense, long-lived clusters. Read
it back to the user for confirmation, since it is a guess and it drives
exclusions in reverse mode.

### 2. Run the mode that matches the question

**Target mode** when they named an account:

```bash
python3 scripts/match.py <csv> --target "Acme"
```

**Reverse mode** when they want to know where to spend the week:

```bash
python3 scripts/match.py <csv> --reverse --min-score 55 --limit 40
```

The two modes score differently on purpose. See `references/scoring.md`.

### 3. Apply the judgment pass

The script is deterministic and stops where data stops. Only after it
returns, reason over the shortlist. This is the part that cannot be
scripted:

- **Would this person actually know the buyer?** A BDR at a
  4,000-person company does not know the CRO. A Chief of Staff at a
  40-person company knows everyone. Weigh seniority against company
  size, which the script cannot see.
- **Does the account fit the ICP?** Reverse mode ranks by tie quality
  alone. Deep ties often sit in the user's previous life, in an
  industry they no longer sell to. Filter for fit and say when a
  well-connected account is simply the wrong account.
- **Is any path good enough?** If not, say so and hand the account back
  to cold outbound. Never manufacture a tenuous connection. A skill
  that refuses a bad intro is worth more than one that always finds
  something, because a bad intro-ask spends relationship capital that
  does not come back.

### 4. Draft the ask

Produce all three artifacts, never just the first. See
`references/templates.md` for the patterns and the reasoning behind
them.

1. **The ask to the connector**, with an explicit easy out.
2. **The forwardable blurb**, a separate short paragraph the connector
   can paste without editing a word. This is what makes double opt-in
   intros work and it is the piece everyone skips.
3. **The fallback**, in case the connector says no or goes quiet.

## Output format

Lead with the recommendation, not the data dump. For each recommended
path: who, why them specifically, what to say, and what the risk is.
Cap it at the top 3 paths per account. A ranked list of 15 names is a
research artifact, not a decision.

Always state the two scores separately and never average them.
Tie strength answers "will they say yes". Path relevance answers "is the
intro useful". A strong tie into a useless contact and a weak tie into
the right VP need opposite messages, and one blended number hides that.

## Known limits, state them rather than working around them

- A LinkedIn export holds **current** employer only. Alumni paths and
  second-degree bridges are not derivable from this file. If the user
  has an older export, diffing the two recovers job history, which is
  the single highest-leverage upgrade to this skill.
- No mutual-connection data, no message history, no interaction data.
- Company names are self-reported free text. Normalization handles legal
  suffixes, parentheticals and emoji, but not everything.
