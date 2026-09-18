# Platform notes

Read only the section for the platform in the URL.

## Partiful (partiful.com/e/...)

- **What is public**: title, date, host display names, blurb, guest count, a few avatars. The
  "Guest List" block shows "N on the list" and a "View all" link but the list itself is gated
  ("Restricted Access: Must be on the list to view event activity & see list details").
- **What a logged-in guest sees**: display names (whatever the guest typed: full name, first name
  only, nickname, sometimes emoji) grouped by status: Going, Maybe, Can't Go, and sometimes
  "Interested". Hosts are tagged "Host". No bios, no companies, no links.
- **Capture with Chrome**: open the event, click "View all" under Guest List, a modal opens with
  tabs per status. Read each tab. The modal scrolls independently; scroll inside it.
- **Raw text shape**: names appear one per line, often followed by `+2` (guests they bring) or a
  status word. Some have a "Host" badge on the line above or below.
- **Parsing hints**: pass `--platform partiful`. Treat `+N` as `plus_ones`, not a name.
- **Enrichment key**: rely heavily on event context. Partiful is used for dinners and side events at
  Tech Weeks, so the umbrella event + city + host company are your best search terms.

## Luma (lu.ma/... or luma.com/...)

- **What is public**: depends on host settings. Often shows hosts with LinkedIn/X links, and a
  "Guests" row with avatars and "N going". Some events expose the full guest list with a one-line
  bio per person (the bio field from the Luma profile), which often includes title and company.
- **Capture**: click the guests row, a modal lists them. Each entry may carry a bio line. Keep it on
  the same line as the name separated by ` | ` in the raw file; the parser puts it in `raw_bio`.
- **Raw text shape**: `Name` then `Bio` on the next line. Pass `--platform luma` and the parser pairs
  them when a bio line does not look like a name.
- **Enrichment key**: the bio line is usually enough to confirm a LinkedIn match on its own.

## Eventbrite

- **What is public**: almost nothing about attendees. Some events show "N people are going" with
  first name + last initial and no more.
- **Capture**: only via a logged-in organiser view (attendee report) or the user's own "Who's
  going" panel, which shows first name and initial.
- **Reality check**: expect mostly partial names, so confidence will be low across the board.
  Tell the user this up front and suggest focusing on the speaker/host list, which is public and
  usually has full names and companies.

## Meetup

- **What is public**: attendee list is often public with display names and avatars. Some members
  use handles rather than names.
- **Capture**: `web_fetch` may return the RSVP list directly; otherwise the "Attendees" page
  (`/events/<id>/attendees/`) lists them. Check for pagination.
- **Raw text shape**: name, then sometimes "Organizer" or "Event Host", then "N events attended".
  The parser drops the stats lines.

## Conference / Tech Week listings (tech-week.com, websummit.com, etc.)

- These pages rarely list attendees but do list **speakers, hosts and partner companies** with full
  names and titles. That is a legitimate and much higher quality list.
- Treat speaker cards as guests with `rsvp_status = speaker`. Titles and companies are usually right
  there, so mark them `high` confidence with `match_evidence = "listed on event page"`.

## Anything else

Fetch the page, look for a repeating block of person-shaped entries (name, optional title, optional
avatar). If there is none, say so and offer the speaker/host list or ask the user to paste what
they can see.
