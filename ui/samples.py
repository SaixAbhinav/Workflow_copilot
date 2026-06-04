"""Demo sample documents for one-click loading from the UI."""

_MEETING_NOTES = """\
Weekly Product Sync — Notes

Attendees: Priya (PM), Marcus (Eng Lead), Sara (Design), Devon (QA), Jamie (Marketing).

Priya kicked off by reviewing last week's commitments. The onboarding revamp shipped to 10% of new users on Monday and conversion is up 4.2 points week over week. Marcus warned that the sample size is still small and asked the team not to celebrate until we have two more weeks of data. Sara agreed and noted that the friction we removed on step three may have been disproportionately responsible for the lift.

Devon raised a regression in the password reset flow that surfaced in QA yesterday. Users on Safari 17 receive the reset email but the deep link opens to a blank screen. Marcus asked Devon to file a P1 bug and assigned Raj to investigate. We want a fix in staging by Thursday at the latest, with a hotfix to production by Friday if the root cause is contained.

Jamie presented the draft launch plan for the integrations marketplace. The current target is May 28. Marketing needs final copy for the landing page by next Wednesday and three customer quotes by the following Monday. Priya offered to reach out to the three pilot customers personally. Sara flagged that the marketplace tile designs are still blocked on the iconography review and asked Jamie to expedite feedback from brand.

For the upcoming planning cycle, Marcus proposed cutting the experimental search redesign from the next sprint to focus engineering on stability work. There was broad agreement. Priya asked Marcus to write up a one-pager explaining the deferral so it does not look like the search team's work is being deprioritized indefinitely. Marcus committed to circulating the doc by end of day Friday.

Devon raised concerns about test environment reliability. The staging database has been wiped twice in the past month, which destroyed in-flight test data and forced QA to redo work. Marcus said this was unacceptable and asked the platform team to investigate. He committed to driving this to resolution and reporting back next week.

Finally, the team discussed the upcoming all-hands. Priya needs everyone to submit their team highlights slide by Tuesday evening. The deck will be reviewed Wednesday morning before being shared with the wider org. Sara volunteered to put together the design section. Marcus will cover engineering. Jamie will handle the marketing recap.

Closing items: Priya asked everyone to update their OKRs in the tracking sheet before EOD Friday. The next sync is moved to Tuesday at 10am to avoid conflict with the all-hands prep.
"""

_PRODUCT_BRIEF = """\
Product Brief: Smart Inbox Triage

Problem
Users tell us their inboxes are full of low-value notifications, status updates, and automated reports that drown out the messages that actually need attention. The average power user in our research cohort received 312 emails per week and reported that fewer than 30 were genuinely important. The remainder were either acted on slowly or ignored entirely, leading to missed deadlines and frayed working relationships.

Proposal
Introduce a Smart Inbox Triage feature that automatically classifies incoming messages into three lanes: Action Required, For Your Information, and Background. The classifier runs locally on the user's machine using a compact language model so that no email content leaves the device. Users can override any classification with a single click and the system learns from those overrides over time.

Success Metrics
We will judge success by three measures. First, the time spent in the primary inbox per day, which we expect to fall by at least 25%. Second, the rate at which Action Required messages are responded to within four hours, which we want to lift above 80%. Third, qualitative satisfaction scores from a follow-up survey, where we want a net promoter score above 40.

Risks
Misclassification of an urgent message is the most serious risk. A single missed contract negotiation or family emergency would erode trust in the feature for that user, possibly permanently. We will mitigate this by being aggressive about surfacing borderline cases to the user rather than auto-archiving them, and by always preserving full search across all lanes.

Open Questions
We have not yet decided how to handle calendar invites, shared documents, or messages from internal mailing lists. There is also an open debate about whether the For Your Information lane should be collapsed by default or shown as a secondary list.
"""

_EMAIL_THREAD = """\
From: Lin Hayes <lin@acmesupplies.com>
Subject: Re: Q2 contract renewal — a few requests

Hi team,

Thanks for the quick turnaround on the draft. Most of it looks good. A few things before we sign:

1. Could you clarify the data retention clause in section 4.2? Our legal team wants confirmation that backups are also deleted within 30 days, not just the primary store.
2. We'd like to add a service credit provision if uptime drops below 99.5% in any month. Standard 10% credit is fine.
3. Can we lock in the current pricing for 24 months instead of 12? We're planning some headcount changes and would like predictability.

We need to wrap this by April 30 to align with our budgeting cycle. If pricing can be confirmed by next Tuesday that would be ideal — otherwise we may need to bump the start date to May.

Thanks,
Lin

---

From: Dev Patel <dev@yourcompany.com>
Subject: Re: Re: Q2 contract renewal — a few requests

Lin,

On (1) yes, we delete backups within 30 days too — happy to make that explicit. I'll have the revised clause back to you by Friday.

On (2) the 10% service credit is fine but we'd want to cap total credits per quarter. Let me check with finance.

On (3) 24 months at current pricing is a stretch but I'll see what we can do. Worst case we can offer 18 months.

I'll send a revised draft early next week. Calling out: I'm on PTO from April 22–25, so if you need anything during that window, please loop in Sara.

Best,
Dev
"""

_COMPARE_DOC_A = """\
Strategy Option A: Build a Native Mobile App

We propose investing in a dedicated iOS and Android application built with native technologies. This approach gives us the best possible performance, the deepest integration with platform-specific features like push notifications and biometric authentication, and the cleanest user experience on each operating system. Users who live in their phones will get a tool that feels at home there.

The cost is higher. We would need to hire or contract at least two mobile engineers, one for each platform, and budget for ongoing maintenance of two codebases that diverge over time. Time to first release is estimated at four to five months. We also lose code reuse with our existing web frontend, which means duplicated business logic and a higher risk of inconsistencies between platforms.

The strategic upside is meaningful. Mobile-first competitors are eating into the bottom of our funnel and we have anecdotal evidence that prospects choose us less often when they discover we have no mobile presence.
"""

_COMPARE_DOC_B = """\
Strategy Option B: Ship a Progressive Web App

Instead of building native, we propose a Progressive Web App that wraps our existing web application with offline support, installability, and limited push notifications via the web push API. The work would be done by the existing web team, sharing the current codebase and component library, with no new hires required.

The user experience would be slightly inferior on iOS, where Apple constrains PWA capabilities, but it would be excellent on Android and indistinguishable from native for most workflows. Time to first release is estimated at six to eight weeks. Ongoing maintenance is bundled into the work the web team already does.

The strategic risk is that prospects evaluating us against mobile-native competitors may still perceive us as a web product. We would need to invest in marketing copy and screenshots that emphasize the installable, app-like experience. If the gap between PWAs and native apps closes further on iOS in the next year, this risk fades; if it widens, we may regret not going native.
"""


SAMPLES: dict[str, dict] = {
    "Meeting notes (tasks)": {
        "text": _MEETING_NOTES,
        "workflow": "tasks",
        "hint": "Long enough to trigger chunking — good for showing the progress counter.",
    },
    "Product brief (summary)": {
        "text": _PRODUCT_BRIEF,
        "workflow": "summary",
        "hint": "Structured product doc — good for summary and insights.",
    },
    "Email thread (tasks)": {
        "text": _EMAIL_THREAD,
        "workflow": "tasks",
        "hint": "Back-and-forth email with implicit asks and deadlines.",
    },
    "Two strategy docs (compare)": {
        "text": _COMPARE_DOC_A + "\n\n--- DOCUMENT BREAK ---\n\n" + _COMPARE_DOC_B,
        "workflow": "compare",
        "hint": "Two strategy proposals separated by a document break — runs the compare workflow.",
    },
}
