# lemlist signal catalog (fallback)

Snapshot of `list_watch_list_library` on 2026-11-02. Prefer the live call; this file is for when the lemlist MCP is unavailable. "Baseline effort" is a starting point, adjust for the team.

| type | name | what it catches | baseline effort | notes |
|---|---|---|---|---|
| companyIsHiring | Company is hiring | Job posts at target companies | 1 | Best when the role IS the work the product does. Filter titles + description keywords. Can appear twice with different title sets. |
| recruitmentCampaign | Hiring campaign | Many listings in a short window | 1 | Growth proxy; weaker than a specific role. |
| republishedJobOffers | Republished job offers | Same job reposted | 1 | Turnover pain. Often best as a stacking condition, not alone. |
| jobChange | Champion job change | Tracked contact moves company | 2 | Needs a contact list (customers, users, webinar registrants). 100 credits per detected move: cap daily. |
| newHire | New hire | New decision-maker, first 90 days | 1 | Titles only. |
| promotion | Promotion | Contact promoted | 1 | Pair with newHire on the same titles. |
| companyEmployeeVisitedMyWebsite | Website visitors | Companies on your site | 2 | Needs the lemlist script. Prioritize pricing, comparison, customer pages. Never mention the visit in copy. |
| competitorConnections | Competitor connections | Prospects connecting with competitor staff | 1 | Keep business titles. Never mention the connection in copy. |
| competitorReactions | Competitor reactions | Likes or comments on competitor posts | 2 | High volume, low intent. Usually skip or light nurture. |
| technologyChange | Technology change | Adopt, drop or switch a technology | 2 | Check each technology resolves in the filter. |
| customSignals | AI Signals | Custom web-monitored prompts | 3 | Most precise; needs a company list and 2 to 3 rounds of prompt tuning. |
| linkedinKeywords | LinkedIn keywords | Posts mentioning keywords | 3 | Vendors post the same words: needs exclusions. |
| linkedinPeopleProfile | Influencer engagement | People engaging with chosen influencers | 2 | Only if the buyer follows a clear set of operators. |
| linkedinCompanyProfile | Company page engagement | Engagers on chosen company pages | 2 | Test on the client's own page once basics run. |
| mergersAcquisitions | Mergers and acquisitions | M&A activity | 2 | Stack re-evaluation; often a later AI Signals prompt. |
| companyRaisedFunds | Fundraising | Funding rounds | 1 | Every vendor emails that week. Usually a priority bump only. |
| buyingIntent | Bombora buying intent | Topic research surges | 2 | Noisy when topics are broad. |
| newProductLaunch | New product launch | Product announcements | 1 | Weak unless the launch creates the pain. |
| companyAward | Awards and recognition | Awards | 1 | Opener, not intent. |
| newPartnership | New partnership | Partnerships | 1 | Ecosystem fit only. |
| newOffice | New office opening | Geographic expansion | 2 | Needs a human check on what kind of office. |
| closingOffice | Office closing | Restructuring | 1 | Usually skip. |
| costCutting | Cost cutting | Cost reduction news | 1 | Fires on layoffs: bad week for a vendor email. |
| outagesAndSecurityBreaches | Security incidents | Outages, breaches | 1 | Only for security, reliability or compliance products. |
| lawsuitsAndLegalIssues | Legal issues | Lawsuits | 1 | Priority boost only; never mention in copy. |
| githubStargazer | GitHub activity | Engagement with public repos | 1 | Developer audiences only. |
| externalSignalContact | Contact external signals | Pushed contact events (forms, usage, webinars) | 4 | Needs an API or webhook integration. |
| externalSignalCompany | Company external signals | Pushed company events (product analytics, CRM) | 4 | Same. Strong for product-led motions. |
