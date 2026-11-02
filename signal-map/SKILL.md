---
title: Signal map
kind: Skill
description: Builds a lemlist signal map for one company. Researches their site, interviews you on pains and team, scores every lemlist signal on effectiveness vs effort, and outputs a ranked HTML playbook with setup, plays and example emails.
author: GTM Club
source: Member
meta: Uses the lemlist MCP
updated: 2026-11-02
---


# Signal map

The output is one page that answers: **for this company, which lemlist signals should they switch on this week, which next, which never, and exactly how to set each one up.** Quality bar: `examples/voice-ai-example.json`, a real map built for an AI voice agent company, anonymized as Acme Voice. Read it before writing anything. Every sentence in it is specific to that company: their pains, their customers' numbers, their competitors, their job titles. A map that could be pasted onto another company has failed.

## Workflow

1. Get the company name and website (ask in chat if not given).
2. Research first, then ask. Don't make the user type what the site already says.
3. Interview (AskUserQuestion, 3 rounds max, propose answers from research).
4. Score and rank the full signal catalog.
5. Write the data JSON, build, publish.

### 1. Research (before any question)

Fetch the site with WebFetch (home, pricing, customers or case studies, every comparison or "alternatives" page, enterprise or trust page, blog index). Record with URLs:

- What they sell, to whom, in one sentence. Sales-led, self-serve, or both.
- Every customer story with its hard numbers, verbatim (these become `proof`).
- Competitors they name themselves (comparison pages are gold).
- Industries, company sizes, buyer titles they target or show in logos.
- Public offers to close on: free plan, live demo, calculator, webinar, report.

Then load the live catalog with `mcp__lemlist__list_watch_list_library` (fall back to `references/signals.md` if the lemlist MCP is unavailable). If the user's lemlist workspace is the client's, `mcp__lemlist__list_watch_lists` shows what already runs.

### 2. Interview

Use AskUserQuestion. Each option is a concrete draft from research, marked "(from site)" where true, so the user mostly clicks. Users can always type "Other". Never ask what research answered with certainty.

**Round 1: who they sell to** (up to 4 questions)
- Offer, always first: which product or offer this map sells (multiSelect, drafted from the pricing, sales and product pages). Many companies sell several offers to different buyers (programs, space, events, seats); one map sells one primary offer to one primary buyer. If the user picks several, ask which is primary and treat the rest as secondary, with at most one or two signals each.
- ICP: industries, size, geography (offer 2 to 3 drafted cuts) for the chosen offer.
- Buyer: which titles sign and which champion (multiSelect).
- Motion this map targets: sales-led, self-serve, or both.
- Competitors: confirm the list, flag additions that aren't on their site.

**Round 2: the pains** (the core of the map)
- Present 3 to 5 drafted pains, each as "short TAG: the moment it hurts", with a proof number from the site. Ask which are real and which is #1 (multiSelect plus a top pick). Pains drive every effectiveness score, so get these right.
- Proof check: if research found fewer than 3 customer outcome numbers for the chosen offer (case studies, results, before and after), ask for them now in the same round: "Which 2 or 3 customer results can we name? (customer, number, timeframe)". Offer "We have none we can share" and "I'll get them from the client" as options. Proof is what turns a pain into a reply, so push here rather than leaving placeholders. Only if the user can't supply any, fall back to `[BRACKETED PLACEHOLDER]` and flag it first in `notes`.
- Ask what the market is changing for them (regulation, platform shift, new competitor type) only if research hinted at one.

**Round 3: what they can run** (drives effort scores)
- Signals running today: none, a few (which), many.
- Can they install the lemlist website script? Do they have a CRM export of customers or users for a champion list?
- Who works the signals: number of AEs or SDRs, tasks per day they can absorb.
- Output: include example emails? Audience (client workshop, internal prep, prospect)? "Prepared by" line?

Stop after round 3. If something is still unknown, assume, and list the assumption in `notes`.

### 3. Score

Score every catalog signal, keep 10 to 12 for the ranked list, name the rest in `leftOut` with a reason each.

**Effectiveness (1 to 5): how directly and how early the signal exposes one of the confirmed pains.**
- 5: fires at the moment the pain costs money, intent is explicit (a job post for the exact work they automate, a champion moving, a visit to a comparison page).
- 4: strong proxy for a pain, some noise or a lag.
- 3: real but diluted; needs a human check or exclusions.
- 2: generic timing (funding, awards); every vendor sees it.
- 1: no line to any pain.

**Effort (1 to 5): work before the first good lead lands, for THIS team.**
- 1: titles or a competitor list and go.
- 2: needs one prerequisite (a contact list from the CRM, the website script, a credit cap).
- 3: prompt tuning (AI Signals), ongoing exclusions, or a company list to build first.
- 4 to 5: integration work (external signals via API), heavy manual review.

**Tiers** (signals are listed in this order):
- `now`: 3 to 5 signals, effectiveness 4+ and effort 1 to 2. Launch this week.
- `next`: effectiveness 4+ with more effort, or a sharper variant of a `now` signal.
- `opp`: effectiveness 3, run once the first ones work.
- `skip`: shown on purpose, with the reason it looks good but isn't (keep 1 to 2 so the client sees you considered them).

A signal type can appear twice with different setups (e.g. `companyIsHiring` for frontline roles and for builders). Sort within a tier by effectiveness, then lower effort.

### 4. Write the page content

Fill a JSON file following the schema in `examples/voice-ai-example.json`. Rules that make it good:

- **specs**: start with an `Offer` line naming what the map sells (with a reference customer if there is one), then ICP, Buyer, Competitors.
- **lede**: how many to switch on, how many ranked behind, current state ("runs no signals today, so this is a from-scratch setup"), and the pains named in plain words.
- **pains**: 3 to 5, each with a site-sourced `proof` line and `sigs` naming which signals expose it.
- **market**: 2 to 4 bullets on what's changing that shapes the ranking. Bold the claim, then why.
- **signals.why**: why this fires on their pain, concretely. Justify the effort score in one clause when it isn't obvious.
- **signals.setup**: exact values the user types in lemlist: job titles, keywords, technologies, competitor names, AI Signals prompts, all in `<code>`. Plus routing and exclusions. Verify technologies resolve with `mcp__lemlist__get_watch_list_filter_value` when available; note the ones that don't.
- **signals.res**: which customer story or page to send with it.
- **plays**: 3 to 4 combos of 2 signals with an output ("AE call today", "Priority tier") and the proof to lead with.
- **run**: 3 steps: lists to build first, the rollout waves with credit caps, the 30-day review that replaces judgment scores with their reply data.
- **copy** (if asked): one fictional example account shaped like their best customers, 3 to 4 fictional contacts, and 4 to 6 first-touch emails for the top signals, all to that same account. Each email: names the trigger (except website visits and competitor connections: never mention those), stays in the prospect's world, cites one real proof number, ends on a resource or a live demo, never a meeting ask. 60 to 110 words. Lowercase short subjects.
- **resources**: every public asset with a real URL you fetched, grouped (Customer stories, Comparison and proof, Content, Offers to close on), each tagged with the signal or play it pairs with.
- **notes**: honest caveats: scores are judgment until step 3, assumptions you made, competitors you added, anything to confirm before naming customers in cold outreach.
- **footer**: preparer line, date the catalog and site were read, which names are fictional.

Writing rules: no em dashes anywhere (the build fails on them). No invented numbers or quotes; a missing fact becomes `[BRACKETED PLACEHOLDER]` and goes in notes. Plain, short sentences. English unless the user asks otherwise.

### 5. Build and publish

```bash
python3 <this skill's folder>/scripts/build.py <company>-signal-map.json <company>-signal-map.html
```

Fix every error it prints. If the Artifact tool is available, publish the HTML with it (title "<Company> Signal Map", icon "map"); the template already meets the page contract, so no extra design pass is needed. Otherwise save the HTML next to the JSON and give the user its path to open in a browser. Reply with the link, the 3 to 5 launch-now signals in one line each, and the assumptions the user should confirm.

To revise a map later, edit the JSON, rebuild, and republish to the same file path.
