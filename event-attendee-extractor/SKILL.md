---
name: event-attendee-extractor
title: Event attendee extractor
kind: Skill
summary: Turns an event link (Luma, Partiful, Eventbrite, Meetup) into a CSV of attendees with title, company and LinkedIn, and a confidence score per row.
description: Turns an event page link (Partiful, Luma, Eventbrite, Meetup, Lu.ma calendars, conference pages, Tech Week listings) into a clean CSV of attendees with name, job title, company, LinkedIn and other social links. Use this skill whenever the user shares an event URL and wants to know who is going, who the guests are, who is on the list, or wants attendees / participants / RSVPs / guest list exported, enriched, or turned into a prospect list. Trigger even if they just paste an event link and say "get me the attendees", "who's attending this", "scrape the guest list", "find the people going to this", "enrich these guests", or paste a wall of guest names copied from an event page. Always produces a CSV plus a confidence score per attendee. Do not use for scraping product pages, pricing, or job listings (use website-scraper) or for general company research.
meta: Lead Sourcing Masterclass
author: GTM Club
source: Member
updated: 2026-09-18
---
# Event Attendee Extractor

Take an event link, get the guest list, enrich every guest with occupation, company and social
links, and hand back a CSV the user can push into lemlist or a CRM.

Respond in the user's language. Write the CSV in English column names so it imports cleanly.

## The one thing to understand first

Event platforms show very little. Partiful shows display names and cartoon avatars, and hides the
list behind "Must be on the list to view". Luma shows names and sometimes a one-line bio. Eventbrite
and Meetup show first name plus initial at best. None of them show job title, company or LinkedIn
in a reliable way.

So this is always a two-stage job:

1. **Capture**: get the raw names off the page the way the user sees it (logged in).
2. **Enrich**: resolve each name to a real professional profile using the event context as the
   disambiguation key, then pull title, company and socials.

Never skip stage 2 by guessing titles from names. An unenriched row is fine; an invented row is not.

## Stage 0: Read the event page (always, before anything else)

`web_fetch` the URL first, even if the guest list is gated. You need the **event context** for the
enrichment stage, and this is free:

- Event name, date, city
- Host name and host company
- Audience described in the blurb ("B2B founders and marketing leaders", "designers", "VCs")
- Any hashtag or umbrella event (#SFTechWeek, Web Summit, VivaTech)
- Whether the guest list is public, partially visible, or gated

Tell the user in one line what you found and which capture route you are taking. If the page
is public and the guests are all there, go straight to parsing. Otherwise pick a capture route.

Platform-specific quirks (where the list lives, how "View all" works, what fields exist) are in
`references/platforms.md`. Read the section for the platform you are on.

## Stage 1: Capture the guest list

Pick the first route that is available, in this order.

### Route A: the user's logged-in browser (preferred)

If the Claude in Chrome connector is available, use it. The guest list is only visible to someone
who RSVP'd or is signed in, so the user's own browser is the only honest way to see it.

Steps:
1. Ask the user to confirm they are logged in and can see the guest list themselves. If they cannot
   see it, neither can you; stop and say so.
2. Navigate to the event URL in a new MCP tab.
3. Find and click the guest list expander ("View all", "See all guests", "Going (42)").
4. Scroll to the bottom repeatedly until the count stops growing (these lists lazy-load).
5. `get_page_text` on the expanded list. If names come back mixed with other page text, `read_page`
   and take the list container only.
6. Save the raw text to `/home/claude/raw_guests.txt`.

Never log the user in, never click RSVP, never accept anything on their behalf. Read only.

### Route B: pasted text or screenshots

If there is no browser connector, ask the user to open the full guest list and either:
- select all the names and paste them, or
- send screenshots of the list (scroll and screenshot until the end).

Transcribe screenshots yourself into `/home/claude/raw_guests.txt`, one name per line. Keep whatever
extra the platform shows next to the name (a bio line, a company, an emoji status) on the same line
separated by ` | `.

### Route C: public page only

If the list is visible without login (some Luma events, most conference speaker pages), the
`web_fetch` from Stage 0 already has the names. Save them to `/home/claude/raw_guests.txt`.

### Parse the raw list

Run:

```bash
python3 scripts/parse_guest_list.py /home/claude/raw_guests.txt --platform partiful \
  --event "The Revenue Table" --out /home/claude/guests_parsed.csv
```

It strips platform noise (emoji reactions, "+3 friends", "Host", "Maybe"), splits first/last name,
flags partial names (`First L.`), dedupes, and writes one row per guest with an `rsvp_status`
column when the platform exposes it. Read the output count back to the user before enriching:
"38 guests captured, 9 have only a first name and last initial."

## Stage 2: Enrich each guest

The goal is title, company, LinkedIn URL, plus X/Twitter or website when they surface naturally.
The event context is your disambiguation tool: a "Sarah K." at a B2B marketing dinner in SF is not
the first Sarah K on Google, it is the one whose profile says B2B marketing and Bay Area.

### 2a. Find the LinkedIn profile (web search)

For each guest, run one `web_search_fast` query built from name plus the strongest context terms:

```
"<full name>" <host company OR umbrella event OR audience keyword> linkedin
```

Examples:
- `"Sarah Kim" SF Tech Week linkedin`
- `"Marc Dupont" B2B marketing San Francisco linkedin`
- If the host is a known company and the guest is likely staff: `"Sarah Kim" 3rd + Taylor`

Accept a match only when the snippet gives at least one corroborating signal from the event context
(location, industry, the host company, the umbrella event, a mutual connection the user named).
Record that signal in `match_evidence`.

Assign confidence:
- **high**: full name + two corroborating signals, or the platform itself linked the profile
- **medium**: full name + one signal
- **low**: partial name (`First L.`) with a plausible single match, or a common full name with a
  weak signal
- **none**: nothing found, or several equally plausible people. Leave title/company blank.

Batch the searches: do 5 to 8 guests, then give the user a one-line progress update. For lists
above 40 guests, ask the user whether to enrich everyone or only the ones matching a persona
(founders, VPs, a target company list). Enrichment is where the time goes.

### 2b. Pull title and company (choose one)

**Option 1: from the search snippet.** LinkedIn snippets usually read
"Name - Title - Company | LinkedIn". Parse that. Good enough for most lists and costs nothing.

**Option 2: lemlist enrichment (when the connector is available).** Once you have LinkedIn URLs,
`bulk_enrich_data` with `linkedin_enrichment` returns a structured title, company and company
domain, one credit per profile found. Before calling it, quote the maximum cost (1 credit x number
of profiles) and get an explicit yes. Then poll `bulk_get_enrichment_results` and read each
`summary` before reporting anything as found. Only submit rows that have a LinkedIn URL; enriching
from a bare partial name burns credits on wrong people.

If the user later wants emails to actually run outreach, that is a separate `find_email` step
(5 credits per email found). Offer it, do not do it by default.

### 2c. Other socials

Do not run extra searches for X, Instagram or personal sites. Capture them only when they show up
in the same result set or on the event page itself (Luma bios often contain them). Put whatever
you find in `other_social_url`; leave it blank otherwise.

## Stage 3: Build the CSV

Run the merge script, which takes the parsed guests and a JSON of enrichment results:

```bash
python3 scripts/build_attendee_csv.py /home/claude/guests_parsed.csv \
  /home/claude/enrichment.json --out /mnt/user-data/outputs/<event-slug>-attendees.csv
```

Write `enrichment.json` yourself as you go, one object per guest keyed by the `guest_id` from the
parsed CSV:

```json
{
  "g_003": {
    "job_title": "VP Marketing",
    "company": "Acme",
    "linkedin_url": "https://www.linkedin.com/in/...",
    "other_social_url": "",
    "confidence": "high",
    "match_evidence": "LinkedIn snippet: VP Marketing at Acme, San Francisco; event blurb targets marketing leaders"
  }
}
```

Final columns, always in this order:

```
guest_id, full_name, first_name, last_name, partial_name, rsvp_status, job_title, company,
linkedin_url, other_social_url, confidence, match_evidence, event_name, event_date, event_url,
source_platform, notes
```

Present the file with `present_files`, then give the user a five-line summary: guests captured,
enriched at high/medium/low confidence, not found, and which rows they should eyeball before
importing (all `low` rows, plus anything with a common name).

## Scope and honesty rules

- Work only from guest lists the user can legitimately see. If a page says the list is restricted
  and the user is not on it, say so and stop. Do not try to bypass it.
- Professional data only: name, title, company, public professional profiles. Never collect phone
  numbers, home addresses, personal email, or anything from a private social account.
- Blank beats wrong. A CSV with 30% empty titles that are all correct is worth more than one with
  100% filled titles where a third are the wrong person. Confidence and match_evidence exist so the
  user can trust the file.
- Never present a `low` match as a fact in prose. Say "possibly" or leave it in the CSV only.
- If the user asks to push the list into a lemlist campaign, that is a separate, explicit step
  with its own confirmation.

## Worked example

User pastes `https://partiful.com/e/...` and asks for attendees with occupation and socials.

1. `web_fetch`: "The Revenue Table, Oct 6, SF, hosted by 3rd + Taylor, audience B2B founders/CEOs/
   marketing leaders, part of #SFTechWeek. Guest list gated."
2. Reply: "The list is only visible to people on it. I can read it from your Chrome if you're logged
   in and RSVP'd, or you can paste the names. Which one?"
3. User picks Chrome. Navigate, click View all, scroll, `get_page_text`, save raw text.
4. Parse: 18 guests, 4 partial names.
5. Search each: `"Jane Doe" SF Tech Week linkedin`, `"Jane Doe" B2B marketing San Francisco linkedin`.
6. Optional lemlist enrichment on the 14 with a LinkedIn URL, after quoting 14 credits.
7. Build CSV, present it, summarise: 14 enriched (9 high, 5 medium), 4 partial names unresolved.
