"""Generate sample PDFs for exercising each workflow mode."""
import os

import fitz  # PyMuPDF

OUT_DIR = os.path.join(os.path.dirname(__file__), "test_pdfs")


DOCS = {
    # ── SUMMARY mode ─────────────────────────────────────────────────────────
    "test_summary.pdf": """The Rise of Small Language Models

For most of the past three years the story of artificial intelligence has been
told in terms of scale. Larger parameter counts, larger training corpora,
larger compute budgets — each new frontier model announcement seemed to assume
that "bigger is better" was a settled question. That assumption is now being
challenged from multiple directions at once.

Research teams at Anthropic, Google DeepMind, and Meta have each published
results in the last year showing that carefully curated training data, better
post-training techniques, and architectural refinements can produce models
with fewer than ten billion parameters that rival the performance of models an
order of magnitude larger on a wide range of benchmarks. In several narrow
domains — code completion, structured data extraction, and mathematical
reasoning — the gap has closed entirely.

There are three forces driving this shift. First, the economics of inference
have become impossible to ignore: running a frontier model at scale costs more
per query than most commercial applications can justify. Second, on-device
deployment, particularly on phones and laptops, has opened a large market for
models that fit in four to eight gigabytes of memory. Third, regulatory
pressure in Europe and parts of Asia has begun to favour models whose
behaviour can be fully audited, something easier to achieve with smaller
systems.

None of this means that frontier-scale models are going away. They remain the
research vehicle where new capabilities first emerge. But the centre of
gravity of deployed AI is quietly moving downward, toward systems that are
cheaper, faster, and more predictable — and much closer to the user.
""",

    # ── TASKS mode (positive) ────────────────────────────────────────────────
    "test_tasks.pdf": """From: manager@company.com
To: you@company.com
Subject: Action items from our 1:1

Hi,

Thanks for the call today. Here is what we agreed you would follow up on.

1. Please submit the quarterly budget draft to Finance by Friday October 24th.
   Mark it high priority — they're blocked until we deliver it.

2. Schedule a 30-minute onboarding call with Priya next Tuesday. She starts
   on Monday and I'd like you to cover the team wiki and the deploy process.

3. Review the three candidate resumes I forwarded earlier this week and send
   me your ranking by end of day Wednesday.

4. Don't forget to renew your AWS certification — the deadline is November
   15th and HR will need the receipt for reimbursement.

Lower priority, but would be great if you could also take a look at the
performance review template I attached and suggest edits whenever you have
time. No rush on that one.

Thanks,
Alex
""",

    # ── TASKS mode (negative — should return source_type=non_actionable) ────
    "test_tasks_negative.pdf": """r/technology — top post this week

Title: Apparently the new ACME XR-9 laptop throttles under sustained load

OP: So I picked up the XR-9 last month and have been putting it through its
paces. Out of the box the performance is genuinely impressive — single-core
scores are up roughly 18 percent over the previous generation. But after
about twelve minutes of sustained compilation workloads the CPU clocks drop
by almost 40 percent and stay there until the machine cools down.

Top reply: Saw the same thing in the Linus Tech Tips review. They speculate
it's a firmware issue rather than thermals, because the fan curve never
ramps past 60 percent even when the package temperature hits 95C.

Another reply: ACME has shipped three laptops in a row with this exact
problem. At some point it stops being a bug and starts being a design
choice.

Another reply: The Dell equivalent doesn't throttle but it's 400g heavier
and the battery is worse. Everything is a trade-off.

OP edit: Worth noting that external cooling pads help a lot. Mine went from
throttling at 12 minutes to throttling at around 35 minutes with a $25
laptop cooler underneath.
""",

    # ── INSIGHTS mode ────────────────────────────────────────────────────────
    "test_insights.pdf": """Q3 2026 Customer Churn Report — Internal

Headline numbers:
  - Monthly churn rose from 3.1% in July to 4.7% in September.
  - 63% of churned accounts were on the Starter plan.
  - Customers who contacted support within 30 days of signup churned at
    roughly half the rate of those who never contacted support.
  - Enterprise churn was essentially flat at 0.8% per month.
  - Churn among customers using the mobile app was 2.1%, versus 5.9% for
    web-only users.

Cohort observations:
  - The September cohort of Starter signups came predominantly from a paid
    search campaign targeting the keyword "free invoice generator." Their
    usage patterns look very different from organic signups.
  - Customers who completed the onboarding checklist in their first week
    churned at 1.9% versus 6.4% for those who did not.
  - Roughly 40% of churned users cited price as the primary reason in the
    exit survey; 28% cited "didn't end up needing it"; 19% cited missing
    features; 13% other.

Retention experiments in flight:
  - Onboarding redesign (A/B): preliminary results show a 22% lift in
    checklist completion but no measurable effect on 30-day retention yet.
  - Annual plan discount pop-up: showing to mid-funnel users increased
    annual conversions by 8% but overall revenue was flat due to
    cannibalisation of monthly subscriptions.
""",

    # ── COMPARE mode (doc A) ─────────────────────────────────────────────────
    "test_compare_a.pdf": """Proposal A — In-House Observability Stack

We propose building our observability stack in-house, based on Prometheus
for metrics, Loki for logs, and Tempo for traces, all deployed on our
existing Kubernetes cluster.

Pros:
  - No per-seat or per-GB licensing costs.
  - Complete control over retention, sampling, and data residency.
  - Open-source, so we avoid vendor lock-in.
  - Can integrate directly with our existing deploy tooling.

Cons:
  - Initial setup and tuning will take an estimated six to eight engineering
    weeks.
  - Ongoing maintenance burden — someone needs to own the stack.
  - On-call load increases: we own the observability of our observability.
  - No out-of-the-box features for anomaly detection or ML-based alerting.

Estimated annual cost: ~$40k in infrastructure plus 0.25 FTE of engineering
time.
""",

    # ── TASKS mode (narrative — should classify as narrative, no action items) ─
    "test_tasks_narrative.pdf": """Acme Robotics unveils household assistant at annual showcase

SAN FRANCISCO — Acme Robotics took the stage at its annual developer
showcase on Wednesday morning to unveil Helio, a wheeled household
assistant the company says can fold laundry, load a dishwasher, and
recognise more than two thousand household objects out of the box.

Chief executive Marisol Tan demonstrated the robot live, asking it to
clear a small dining table and identify three unlabelled spice jars by
smell. The crowd applauded when Helio correctly named cumin, paprika, and
star anise. Tan said the unit will retail for $4,900 in the United States
beginning in March, with a leasing option priced at $129 per month.

Industry analysts greeted the announcement with cautious optimism. "The
demos look good, but household robots have a long history of looking good
on stage and struggling in real homes," said Priya Venkatesh of Forrester
Research. Acme has not yet released independent reliability data.

The company also announced a new partnership with a national elder-care
provider that will deploy 200 Helio units to assisted-living facilities
across Texas and Arizona over the next twelve months.
""",

    # ── TASKS mode (informational — reference doc, should classify informational)
    "test_tasks_informational.pdf": """HTTP Status Codes — Reference

Status codes in the HTTP protocol are three-digit numbers grouped into
five classes by their first digit.

1xx Informational
  These indicate that the request was received and the process is
  continuing. They are rarely seen in everyday application code. The most
  common is 100 Continue, used during request body negotiation.

2xx Success
  The request was successfully received, understood, and accepted. 200 OK
  is the canonical success response. 201 Created is used after a resource
  has been created, typically returned by POST endpoints. 204 No Content
  signals success but with no response body — common for DELETE endpoints.

3xx Redirection
  Further action is required to complete the request. 301 Moved
  Permanently is cacheable and should update bookmarks and indexes; 302
  Found is a temporary redirect; 304 Not Modified is returned when the
  client's cached copy is still valid.

4xx Client Error
  The request contains bad syntax or cannot be fulfilled. 400 Bad Request
  is the generic client-error response. 401 Unauthorized indicates missing
  or invalid authentication; 403 Forbidden indicates valid credentials
  without sufficient permissions. 404 Not Found is used when the resource
  does not exist. 429 Too Many Requests is used for rate limiting.

5xx Server Error
  The server failed to fulfill an apparently valid request. 500 Internal
  Server Error is generic; 502 Bad Gateway and 503 Service Unavailable
  point to upstream or capacity issues; 504 Gateway Timeout indicates a
  slow upstream service.

Choosing the right status code matters for caching, retries, and client
behaviour. Many client libraries automatically retry on 5xx but not 4xx,
and CDNs cache 301 responses indefinitely by default.
""",

    # ── CHUNKING test (long multi-page document, exercises chunker + merge) ──
    "test_long_document.pdf": (
        "A Brief History of Programming Languages\n\n"
        + (
            "The first electronic computers in the 1940s were programmed by "
            "physically rewiring patch panels. Within a decade, assembly "
            "languages let programmers write mnemonics like ADD and JMP "
            "instead of binary opcodes, and assemblers translated those "
            "mnemonics into machine code. This was a productivity leap, but "
            "every machine still had its own dialect.\n\n"
            "FORTRAN, released by IBM in 1957, was the first widely adopted "
            "high-level language. It introduced loops, conditionals, and "
            "subroutines in a form recognisable today, and proved that "
            "compiled high-level code could be nearly as fast as hand-written "
            "assembly. COBOL followed in 1959, aimed at business data "
            "processing, and remained the backbone of banking and government "
            "systems for the next half century.\n\n"
            "The 1970s introduced two languages whose influence still "
            "dominates: C and Smalltalk. C, designed at Bell Labs, gave "
            "programmers low-level control with a portable syntax — Unix was "
            "rewritten in C, and almost every operating system kernel since "
            "has followed that pattern. Smalltalk, designed at Xerox PARC, "
            "introduced object-oriented programming as a complete philosophy: "
            "everything is an object, communication happens by message "
            "passing, and the development environment is itself a live "
            "program you can edit.\n\n"
            "The 1990s saw the rise of dynamic languages on the web. Perl, "
            "Python, Ruby, and PHP each became dominant in particular "
            "ecosystems. JavaScript, designed in ten days by Brendan Eich at "
            "Netscape, would over the next twenty years become the only "
            "language that runs natively in every web browser, and through "
            "Node.js eventually on servers as well.\n\n"
            "Java, also from the mid-1990s, took a different bet: a virtual "
            "machine that could run the same bytecode on any platform. The "
            "JVM became its own ecosystem, eventually hosting languages such "
            "as Scala, Clojure, and Kotlin that share Java's runtime but "
            "explore very different design philosophies.\n\n"
            "The 2010s brought a new wave focused on safety and concurrency. "
            "Rust offered memory safety without garbage collection by "
            "tracking ownership in the type system. Go, from Google, took the "
            "opposite approach — a small language with garbage collection and "
            "first-class lightweight threads, deliberately easy to learn. "
            "Swift replaced Objective-C as the language of Apple platforms, "
            "and TypeScript brought static types to the JavaScript world.\n\n"
            "Throughout this history, three forces have repeatedly reshaped "
            "the field: hardware changes (multi-core, GPUs, and now "
            "specialised AI accelerators), shifts in deployment (mainframes "
            "to PCs to web to mobile to cloud), and changing expectations "
            "around safety and developer ergonomics. Each new generation of "
            "languages tends to absorb the lessons of the previous one while "
            "rejecting some of its constraints.\n\n"
        ) * 4
    ),

    # ── COMPARE mode (doc B) ─────────────────────────────────────────────────
    "test_compare_b.pdf": """Proposal B — Managed Observability via Datadog

We propose adopting Datadog as our primary observability platform, covering
metrics, logs, APM, and real-user monitoring.

Pros:
  - Fast to roll out — most teams can onboard in under two weeks.
  - Mature anomaly detection and ML-based alerting out of the box.
  - Unified UI across metrics, logs, traces, and RUM.
  - 24/7 vendor support included.

Cons:
  - Significant cost, especially at scale — billing is per host, per GB
    ingested, and per monitored user.
  - Limited control over retention policies without enterprise tier.
  - Vendor lock-in: query languages and alert definitions are not portable.
  - Data residency is constrained to Datadog's supported regions.

Estimated annual cost: ~$180k at current traffic projections, scaling
roughly linearly with growth.
""",
}


def write_pdf(path: str, body: str):
    doc = fitz.open()
    remaining = body
    while remaining:
        page = doc.new_page()  # A4 by default
        rect = fitz.Rect(54, 54, page.rect.width - 54, page.rect.height - 54)
        # insert_textbox returns the number of chars that did NOT fit (as a
        # negative count when overflowed). When it overflows, we don't get the
        # exact split point back, so we shrink-and-retry until it fits, then
        # recurse on the leftover.
        rc = page.insert_textbox(
            rect, remaining, fontsize=10.5, fontname="helv", align=0,
        )
        if rc >= 0:
            break
        # Binary-search the largest prefix that fits on this page.
        lo, hi = 0, len(remaining)
        best_fit = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            test_page = doc.new_page()
            test_rect = fitz.Rect(54, 54, test_page.rect.width - 54, test_page.rect.height - 54)
            r = test_page.insert_textbox(
                test_rect, remaining[:mid], fontsize=10.5, fontname="helv", align=0,
            )
            doc.delete_page(len(doc) - 1)
            if r >= 0:
                best_fit = mid
                lo = mid + 1
            else:
                hi = mid - 1
        # Replace the overflowed page with one that fits.
        doc.delete_page(len(doc) - 1)
        page = doc.new_page()
        rect = fitz.Rect(54, 54, page.rect.width - 54, page.rect.height - 54)
        page.insert_textbox(
            rect, remaining[:best_fit], fontsize=10.5, fontname="helv", align=0,
        )
        remaining = remaining[best_fit:]
    doc.save(path)
    doc.close()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, body in DOCS.items():
        path = os.path.join(OUT_DIR, name)
        write_pdf(path, body)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
