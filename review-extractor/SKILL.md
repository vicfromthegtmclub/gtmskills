---
name: review-extractor
title: Review extractor
kind: Skill
summary: Turns a G2, Capterra or Trustpilot review page into a CSV of prospects, with the sentence that says why each one would switch.
description: Extract prospects from software review sites (G2, Capterra, TrustRadius, Trustpilot, App Store, Google Play) into a clean CSV with the review text preserved as the outreach reason. Use this whenever someone wants to find leads from competitor reviews, mine reviews for prospects, build a list from G2 or Capterra, find people unhappy with a competitor, or turn review pages into a prospect list — including when they just paste a review page URL or a wall of copied review text and ask what to do with it. Defaults to mid-range ratings (3-star) because those reviewers are still paying and still unhappy, which one-star reviewers are not.
meta: Lead Sourcing Masterclass
author: GTM Club
source: Member
updated: 2026-09-18
---
# Review extractor

Turns a review page into a table of people worth contacting, with the reason attached to each row.

## Why the review text is the whole point

Generic scrapers collect contacts. This collects **reasons**. A name and a job title tells you who to email; a review tells you what to say. If the review text does not survive into the output, this skill has failed regardless of how many rows it produced.

## Which reviews to take

Default to **3-star reviews**, and 2- and 4-star if volume is thin.

A 1-star reviewer has usually already churned — they are the competitor's post-mortem, not your prospect. A 5-star reviewer is happy and not going anywhere. A 3-star reviewer is still paying, still using it, quietly frustrated, and sitting in a contract that renews. They have written down, in public, the exact thing that would make them switch.

Take 1-star reviews only if the user explicitly asks, and say why you are flagging it.

Sort by **most recent** and prefer the last 90 days. A complaint from two years ago has usually been fixed or the person has left.

## Getting the input

Two paths, both fine:

**A URL** — fetch it if a fetch tool is available. If fetching fails or returns a JS shell with no review content, do not retry repeatedly. Say so plainly and ask the user to open the page, select all, and paste. That is a 10-second fix and much faster than fighting a renderer.

**Pasted text** — this is the common case and works better than people expect. Ask for select-all rather than careful selection: careful selection loses rows and takes ten times longer.

Ask which competitor and which rating band before starting, unless the user has already said.

## Extraction rules

Extract every **reviewer** into a row. Ignore vendor responses, "helpful" counts, related-product widgets, ads, and navigation.

**Never invent a field.** Review sites show wildly inconsistent reviewer detail — some show full name, role, company and headcount, others show "Verified User in Marketing" and nothing else. Both are normal. When a field is not present in the source, leave it blank rather than inferring it from context. An inferred job title looks identical to a real one in a spreadsheet and you will not catch it later.

If you are unsure whether a value appeared verbatim, write `UNVERIFIED` in that cell.

Anonymous reviewers still belong in the output when their review text is strong. The row is a lead on a *company*, and the named person can be found later. Note them as `ANONYMOUS` in the name column rather than dropping the row.

## Output

Write a CSV. Columns, in this order:

| Column | Notes |
|---|---|
| `name` | `ANONYMOUS` if the site withholds it |
| `job_title` | Blank if absent. Never inferred. |
| `company` | Blank if absent |
| `company_size` | Whatever band the site gives |
| `rating` | Numeric |
| `review_date` | ISO format where possible |
| `review_quote` | The specific sentence describing the problem, not the whole review |
| `why_them` | One line: what this review tells you about their situation |
| `source` | e.g. `g2:competitor-name` |
| `profile_url` | If present |

`review_quote` should be the sharpest 1-2 sentences, not a paragraph. The user is going to read 30 of these; give them the part that matters.

`why_them` is your judgement, written for someone deciding whether to email this person. "Onboarding breaks above ~50 users, they have 200+" beats "unhappy with onboarding."

## Verify before handing it over

Pick **three rows at random** and confirm each field against the source text. Report what you checked and anything you corrected.

This matters more than it sounds. The output looks equally confident whether or not it is accurate, and the user's whole reason for using this is that they did not read the source themselves.

State the real numbers: how many reviews were in the source, how many rows you produced, how many fields came back blank or unverified. Do not smooth this over — a run that produces 9 usable rows out of 30 reviews is a good run, and saying so builds more trust than a suspiciously complete table.

## Then stop

Do not write outreach copy, suggest subject lines, or draft emails unless asked. This skill produces the list. What to say to it is a separate problem and a much harder one.

## Common failure modes

**Everything comes back complete and tidy.** Review sites are not tidy. If every row has a full name, title, company and headcount, you have almost certainly inferred some of it. Re-check against the source.

**Vendor responses parsed as reviewers.** The vendor replies underneath reviews and those replies contain names and titles. They are not prospects.

**One review split into several rows.** Long reviews with pros/cons/switching-from sections can look like multiple entries. One reviewer, one row.

**The same person across several products.** Reviewers often review a whole category. Deduplicate on name plus company, and keep the review most relevant to what the user sells.
