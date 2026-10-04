---
name: closed-lost-reactivation
title: Closed-lost reactivation
kind: Skill
summary: Turns the call where a deal was lost into one reactivation email built on three bricks: a detail only someone on the call would know, what changed since, and an asset shaped around their reason for saying no.
description: Writes a closed-lost reactivation email (plus an optional LinkedIn and follow-up variant) from the transcript of the call where the deal was lost. Use this skill whenever the user wants to reactivate, re-engage, revive or win back a closed-lost deal, a lost opportunity, a churned prospect or a "not now" account, or pastes a sales call transcript and asks what to send now. Also use it for the weekly closed-lost review ("which closed-lost should we reopen this week"), even if the user only says "reopen this deal", "they said no in March, what do I send", or shares a Claap or Gong recording link. Never write a closed-lost email from the CRM loss reason alone when a transcript exists.
author: GTM Club
source: Member
updated: 2026-10-04
---

# Closed-lost reactivation

A closed-lost deal is the warmest cold lead you have. The prospect already knows you, already explained their problem, and told you exactly why they said no. Generic "checking back in" sequences waste all of that. This skill turns the call where the deal died into one email built on three bricks.

## The three bricks

1. **Oddly specific.** Prove you listened. Reference who said what, in which call, in their own words. One detail only a person who was on the call (or read the transcript) could know.
2. **Why now.** Name the reason they said no, then explain what changed since that makes this the right moment. This is the heart of the email and must be convincing on its own.
3. **CTA built from 1 + 2.** The ask is shaped around the loss reason and the timing. It is a dedicated asset, not "a quick call": a demo of the missing feature on their own data, a cost model with their numbers, a test harness for their calls, a security pack for their legal team.

If one brick is weak, the email is a generic follow-up with a name in it. Fix the weak brick before writing.

## Step 1: Get the material

You need, per deal:

- The transcript of the call where the deal was lost (or the last substantive call). If a call recorder is connected through MCP (Claap: `search_recording_transcripts`, `get_recording_transcript`; or any other recorder), fetch it yourself. Otherwise ask the user to paste it.
- Deal basics: company, contact name and role, close-lost date, CRM loss reason.
- What changed since (product releases, their own announcements, their fiscal calendar, a signal like hiring or funding). If the user hasn't said and you can't find it, ask in one message. Never invent a change.

Ask for everything missing in a single message, never in several rounds.

## Step 2: Mine the transcript

Extract these, with timestamps and speaker names when available:

| Field | What to look for |
|---|---|
| Real loss reason | The reason as the prospect said it, which often differs from the CRM field ("budget" in the CRM, "my CFO froze tools until planning" on the call) |
| Exact words | 1 or 2 short phrases the prospect used about the problem or the reason (under 12 words each) |
| Stated condition | Any "we'd look again if...", "come back when...", "after Q3", "once X ships". This is gold: it is their own why-now |
| Numbers | Volumes, costs, deadlines, headcount, languages, latency targets, anything quantified |
| Stakeholders | Who else was named (CFO, legal, the engineer who wanted to build it) |
| What they liked | The part of the demo or offer that landed |

## Step 3: Build the why-now

Match the real loss reason to the strongest why-now. Use the first one that is true.

| Loss reason | Strongest why-now | CTA shape |
|---|---|---|
| Product gap (missing feature, language, integration, performance) | The gap is closed: name the release and when it shipped | A demo of that exact capability on their use case, prepared before they reply |
| Budget or price | Their budget cycle reopened (fiscal year, planning week, new quarter) or the pricing changed | A cost model built with the numbers they gave on the call |
| Timing or priority | The condition they set has matured ("after the launch", "Q3") | A plan that starts where they are now, with a date |
| Lost to a competitor | Contract renewal window, or a known limit of the competitor they hit since | A side-by-side test on their own data |
| Built in-house | The in-house project hit the limit they predicted, or they are now hiring to maintain it | A test harness or a migration plan that keeps their work |
| Security, legal, compliance | The certification, region or contract term they needed now exists | The security pack, pre-filled for their legal team |
| Champion left / no decision | A new owner is in place (job change signal) | A 1-page brief the new owner can use, written from the old calls |

Rules for the why-now:

- State the original reason plainly. Pretending it never happened reads as a template.
- Show causality: "you said X, X changed, so Y is now possible".
- Use only true facts. If you don't know whether a feature shipped, write `[confirm: feature + ship date]` and tell the user.
- If nothing changed, say so to the user and recommend waiting or using their stated condition. A reactivation with no real why-now burns the account.

## Step 4: Write the email

Structure:

```
Subject: 2 to 5 words, lowercase, tied to their reason (not "following up")

Line 1, brick 1: the oddly specific callback (who, when, their words)
Line 2-3, brick 2: the reason, what changed, why it matters for them now
Line 4, brick 3: the asset, already prepared or ready in 48h, and a yes/no ask
Signature
```

Constraints:

- 60 to 120 words in the body.
- First word is never "I". Open with their name or the callback.
- One quote from the call at most, under 12 words, attributed ("as Dana put it").
- Mention the call naturally ("when we spoke in March"). Never mention recording, transcript or the tool used to find the detail.
- One CTA, phrased so a "yes" costs them nothing: "Want me to send it?", "Should I run it on your 20 calls?".
- No em dashes or en dashes as punctuation. Use commas, periods or colons.
- No "just checking in", "circling back", "hope you're well", "touch base".
- No invented numbers, customers or results. Placeholders in brackets when needed.

Optional, only if asked or useful:

- **LinkedIn version**: under 300 characters, same three bricks compressed, plain text.
- **Follow-up (day 4, same thread, empty subject)**: one sentence that hands over a smaller piece of the asset with no ask attached.

## Step 5: Output format

For each deal, return:

```
### [Company] | [contact, role] | lost [month year]

Brick map
- Oddly specific: [the detail used + where it came from in the call]
- Why now: [reason → what changed → consequence]
- CTA: [the asset and why it follows from the reason and the timing]

Generic version (what a standard sequence would send)
[2 lines]

Reactivation email
Subject: ...
[body]
```

When processing several deals (weekly review), add a short ranking first: which deals to send this week, which to hold, and why (a deal with no real why-now goes to "hold").

## Quality gate

Check every email before returning it. Fix and re-check if anything fails.

1. Could this email be sent to another closed-lost account by swapping the name? If yes, brick 1 is too weak.
2. Does the email name the original reason and a real change? If not, brick 2 is missing.
3. Is the CTA a specific asset tied to that reason? If it is "a call" or "a demo", rewrite it.
4. Any em dash, en dash, or spaced hyphen used as punctuation? Remove.
5. Any fact, release or number you can't trace to the transcript or the user? Replace with a bracketed placeholder and flag it.
6. Over 120 words? Cut.

## Weekly routine (suggest it when relevant)

Every Monday, run the skill on two lists: deals lost last week (fresh context, reopen with the condition they set), and deals lost 3, 6 and 12 months ago whose stated condition has now matured. Push the approved emails to a lemlist campaign with the email body in a custom variable, so each rep reviews and sends from one place.
