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
    page = doc.new_page()  # A4 by default
    rect = fitz.Rect(54, 54, page.rect.width - 54, page.rect.height - 54)
    # insert_textbox will wrap long lines and honour explicit newlines.
    page.insert_textbox(
        rect,
        body,
        fontsize=10.5,
        fontname="helv",
        align=0,
    )
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
