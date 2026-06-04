"""Generate a comprehensive PDF reference for AI Workflow Copilot.

Run:  venv/Scripts/python.exe tools/generate_doc.py
Output: docs/AI_Workflow_Copilot_Guide.pdf
"""
from __future__ import annotations

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Output ────────────────────────────────────────────────────────────────

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "docs", "AI_Workflow_Copilot_Guide.pdf")


# ── Style palette ─────────────────────────────────────────────────────────

ACCENT = colors.HexColor("#0a84ff")
ACCENT_DARK = colors.HexColor("#0060df")
TEXT = colors.HexColor("#1d1d1f")
MUTED = colors.HexColor("#636366")
CODE_BG = colors.HexColor("#f2f2f7")
RULE = colors.HexColor("#d1d1d6")


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "TitleBig": ParagraphStyle(
            "TitleBig", parent=base["Title"],
            fontName="Helvetica-Bold", fontSize=32, leading=38,
            textColor=ACCENT, alignment=TA_LEFT, spaceAfter=8,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"],
            fontName="Helvetica", fontSize=14, leading=18,
            textColor=MUTED, alignment=TA_LEFT, spaceAfter=24,
        ),
        "H1": ParagraphStyle(
            "H1", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=20, leading=24,
            textColor=ACCENT, spaceBefore=20, spaceAfter=8,
        ),
        "H2": ParagraphStyle(
            "H2", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=14, leading=18,
            textColor=TEXT, spaceBefore=14, spaceAfter=4,
        ),
        "H3": ParagraphStyle(
            "H3", parent=base["Heading3"],
            fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=ACCENT_DARK, spaceBefore=10, spaceAfter=2,
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["BodyText"],
            fontName="Helvetica", fontSize=10.5, leading=15,
            textColor=TEXT, alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "Bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"],
            fontName="Helvetica", fontSize=10.5, leading=15,
            textColor=TEXT, alignment=TA_JUSTIFY,
            leftIndent=14, bulletIndent=4, spaceAfter=4,
        ),
        "Code": ParagraphStyle(
            "Code", parent=base["Code"],
            fontName="Courier", fontSize=9, leading=12,
            textColor=TEXT, backColor=CODE_BG,
            leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10,
            borderPadding=6, borderColor=RULE, borderWidth=0,
        ),
        "Caption": ParagraphStyle(
            "Caption", parent=base["Italic"],
            fontName="Helvetica-Oblique", fontSize=9, leading=12,
            textColor=MUTED, alignment=TA_LEFT, spaceAfter=12,
        ),
        "Footer": ParagraphStyle(
            "Footer", parent=base["Normal"],
            fontName="Helvetica", fontSize=8, leading=10,
            textColor=MUTED, alignment=TA_CENTER,
        ),
    }


# ── Builders ──────────────────────────────────────────────────────────────

def _bullets(S, items: list[str]) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(t, S["Bullet"]), leftIndent=18, bulletColor=ACCENT) for t in items],
        bulletType="bullet", start="•", leftIndent=14,
    )


def _code(S, text: str) -> Preformatted:
    return Preformatted(text, S["Code"])


def _hr() -> Table:
    t = Table([[""]], colWidths=[6.5 * inch], rowHeights=[1])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.8, RULE)]))
    return t


def _on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.45 * inch, "AI Workflow Copilot — Project Guide")
    canvas.drawRightString(
        LETTER[0] - 0.75 * inch, 0.45 * inch, f"Page {doc.page}"
    )
    canvas.restoreState()


# ── Content sections ──────────────────────────────────────────────────────

def cover(S) -> list:
    return [
        Spacer(1, 1.2 * inch),
        Paragraph("AI Workflow Copilot", S["TitleBig"]),
        Paragraph(
            "A local-first desktop assistant for documents, email, and tasks — "
            "built on PyQt5 and Ollama.",
            S["Subtitle"],
        ),
        _hr(),
        Spacer(1, 0.4 * inch),
        Paragraph("What this guide covers", S["H2"]),
        Paragraph(
            "This document is a self-contained reference for the AI Workflow Copilot "
            "project. It explains what the app does, how it is put together, why each "
            "design choice was made, and how to talk about the project to someone who "
            "has never seen it before.",
            S["Body"],
        ),
        Paragraph(
            "Read it end-to-end the first time. Each section opens with the high-level "
            "idea and then drills into the implementation, so you can stop reading any "
            "section once you have what you need.",
            S["Body"],
        ),
        Spacer(1, 0.2 * inch),
        Paragraph("In one sentence", S["H3"]),
        Paragraph(
            "AI Workflow Copilot turns documents and Gmail messages into "
            "summaries, action items, insights, and comparisons — all without sending a "
            "single byte of content to a cloud LLM.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_overview(S) -> list:
    return [
        Paragraph("1. Project overview", S["H1"]),
        Paragraph(
            "AI Workflow Copilot is a Windows desktop application that helps a "
            "knowledge worker process long-form text — pasted notes, .txt or .pdf "
            "documents, or Gmail messages — and extract one of four structured "
            "outputs: a summary, a list of action items, key insights, or a comparison "
            "between two or more documents.",
            S["Body"],
        ),
        Paragraph(
            "The entire pipeline runs locally. The large language model is served by "
            "Ollama on the user's own machine. Only the original documents, the "
            "model weights, and the user's Google credentials ever touch disk. "
            "Nothing about the content of an email or a document leaves the device.",
            S["Body"],
        ),
        Paragraph("Who is it for?", S["H2"]),
        _bullets(S, [
            "<b>Knowledge workers</b> who deal with long emails, meeting notes, and PDFs "
            "and want a faster way to find the action items.",
            "<b>Privacy-sensitive teams</b> who cannot send work content to a cloud AI "
            "vendor because of legal, compliance, or trust constraints.",
            "<b>Tinkerers and students</b> who want to see how a complete local-first "
            "LLM application is wired together end-to-end.",
        ]),
        Paragraph("Core value propositions", S["H2"]),
        _bullets(S, [
            "<b>Local-first by construction.</b> The LLM never talks to the internet.",
            "<b>One window, four workflows.</b> Summary, Tasks, Insights, and Compare "
            "share a single pipeline and UI surface.",
            "<b>Auto mode triage.</b> One click scans recent emails and tells you which "
            "ones need your attention right now.",
            "<b>Calendar integration.</b> Extracted tasks become real Google Calendar "
            "events with priority-aware reminders.",
            "<b>Replayable history.</b> Every run is stored in SQLite and can be reopened.",
        ]),
        Paragraph("Concretely, what does a session look like?", S["H2"]),
        Paragraph(
            "The user opens the app, pastes a 600-word meeting note into the input "
            "area, picks the Tasks workflow, and clicks Process. About ten seconds "
            "later, a list of action items appears — each with a deadline and "
            "priority. The user clicks <i>Push Tasks to Google Calendar</i>, edits a "
            "few rows in the review dialog, and watches the events land on their "
            "calendar. They never had to type the events themselves, and the meeting "
            "note never left the laptop.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_use_cases(S) -> list:
    return [
        Paragraph("2. Use cases", S["H1"]),
        Paragraph(
            "AI Workflow Copilot is built for situations where a knowledge worker "
            "needs to extract structure from long-form text quickly, but cannot or "
            "does not want to send that text to a cloud service. The scenarios "
            "below describe the people we had in mind and the moments in their day "
            "where the app earns its place.",
            S["Body"],
        ),

        Paragraph("Scenario 1 — The Monday-morning inbox", S["H2"]),
        Paragraph(
            "<b>Persona:</b> Priya, a product manager. Over the weekend she has "
            "accumulated 80 emails. Many are CC noise; a handful demand action by "
            "Tuesday.",
            S["Body"],
        ),
        Paragraph(
            "<b>Flow:</b> She opens the app, flips to Auto mode, picks the 48-hour "
            "window, and clicks Scan. Within a minute she has a ranked digest: two "
            "<i>high</i>-tier emails (a contract clause to review by EOD, an "
            "escalation from a key customer) plus several <i>medium</i>-tier items "
            "with later deadlines. She clicks Push to Calendar, edits the "
            "auto-extracted deadlines in the review dialog, and starts her actual "
            "workday from a clean list — not from page 1 of an inbox.",
            S["Body"],
        ),
        Paragraph(
            "<b>Why this app:</b> An assistant that reads her real Gmail without "
            "the email content ever leaving the laptop.",
            S["Body"],
        ),

        Paragraph("Scenario 2 — Post-meeting task capture", S["H2"]),
        Paragraph(
            "<b>Persona:</b> Marcus, an engineering lead, takes raw notes during a "
            "sync. The notes are full of <i>“Raj will fix X by Friday, Sara owns "
            "the Q3 design review”</i> phrasing.",
            S["Body"],
        ),
        Paragraph(
            "<b>Flow:</b> Marcus pastes the meeting notes into the input area "
            "(Manual mode, Tasks workflow) and clicks Process. The Tasks workflow "
            "extracts each obligation with its owner-inferred priority and deadline. "
            "Marcus pushes them to Calendar with a single button. Total time: under "
            "thirty seconds from <i>“meeting just ended”</i> to <i>“all action "
            "items on the calendar.”</i>",
            S["Body"],
        ),
        Paragraph(
            "<b>Why this app:</b> Cloud LLMs can do this, but Marcus's meeting "
            "notes contain internal team names and unannounced project codenames. "
            "Local processing avoids the discomfort.",
            S["Body"],
        ),

        Paragraph("Scenario 3 — Comparing two proposals", S["H2"]),
        Paragraph(
            "<b>Persona:</b> Lin, a CFO, has two vendor proposals for the same "
            "system. The proposals are 12-page PDFs.",
            S["Body"],
        ),
        Paragraph(
            "<b>Flow:</b> Lin drops both PDFs into the input area — the app reads "
            "them and inserts a "
            "<font face=\"Courier\">--- DOCUMENT BREAK ---</font> separator. She "
            "picks the Compare workflow and clicks Process. The result lists "
            "common themes, differences side-by-side (option A vs option B per "
            "topic), and a few cross-document insights. She can scan it in two "
            "minutes instead of cross-referencing two PDFs with a highlighter.",
            S["Body"],
        ),
        Paragraph(
            "<b>Why this app:</b> The proposals are competitively sensitive; she "
            "is not willing to upload them to a third-party chat product.",
            S["Body"],
        ),

        Paragraph("Scenario 4 — Reading a regulatory document offline", S["H2"]),
        Paragraph(
            "<b>Persona:</b> Devon, a compliance analyst, opens a 30-page PDF "
            "while travelling without internet access.",
            S["Body"],
        ),
        Paragraph(
            "<b>Flow:</b> Devon opens the app, loads the PDF, picks Summary, and "
            "waits for the model to chunk through the document. The result is a "
            "bulleted overview that lets her decide which sections need a careful "
            "read. None of this requires connectivity — Ollama runs entirely "
            "offline once the model is pulled.",
            S["Body"],
        ),
        Paragraph(
            "<b>Why this app:</b> Offline-capable AI is rare. Most assistants "
            "stop working the moment the plane door closes.",
            S["Body"],
        ),

        Paragraph("Common thread", S["H2"]),
        Paragraph(
            "All four scenarios share two pressures: <b>sensitive content</b> that "
            "should not leave the machine, and <b>repetitive structure-extraction</b> "
            "that a model is unusually good at. Where those two pressures meet, "
            "this app is the right tool.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_comparison(S) -> list:
    rows = [
        ["Product", "Runs locally", "Email integration", "Calendar push",
         "Workflow templates", "Cost"],
        ["AI Workflow Copilot", "✓", "✓", "✓", "✓ (4 built-in)", "Free"],
        ["ChatGPT (web)", "✗", "✗", "✗", "✗ (chat only)", "Free / Plus"],
        ["Claude.ai", "✗", "✗", "✗", "Manual prompts", "Free / Pro"],
        ["Microsoft 365 Copilot", "✗", "✓ (Outlook)", "✓ (Outlook)", "Office-specific", "Paid sub"],
        ["Superhuman AI", "✗", "✓ (own client)", "✗", "Email-focused", "Paid sub"],
        ["Gemini in Workspace", "✗", "✓ (Gmail)", "✓ (Calendar)", "Workspace-specific", "Paid tier"],
        ["LM Studio / Jan.ai", "✓", "✗", "✗", "✗ (chat only)", "Free"],
        ["Open-WebUI", "✓", "✗", "✗", "✗ (chat / RAG)", "Free"],
        ["AnythingLLM", "✓", "✗", "✗", "RAG-focused", "Free / Paid"],
    ]
    table = Table(rows, colWidths=[1.6 * inch, 0.75 * inch, 0.95 * inch, 0.85 * inch, 1.25 * inch, 0.8 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#e6f4ff")),  # highlight our row
        ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, CODE_BG]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT_DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [
        Paragraph("3. How it compares to other products", S["H1"]),
        Paragraph(
            "Plenty of AI products help you process documents and email. Almost "
            "none of them combine the three features that matter most here: "
            "<b>local execution</b>, <b>email/calendar integration</b>, and "
            "<b>specialised workflow templates</b> (rather than free-form chat).",
            S["Body"],
        ),
        table,
        Paragraph(
            "<i>Comparison is approximate and based on publicly documented "
            "behaviour as of late 2025 / early 2026. Product features change "
            "frequently.</i>",
            S["Caption"],
        ),

        Paragraph("What makes this app different", S["H2"]),
        _bullets(S, [
            "<b>Strictly local LLM.</b> Cloud assistants (ChatGPT, Claude, Microsoft "
            "Copilot, Gemini in Workspace, Superhuman AI) all send your content to "
            "a third-party server. This app sends nothing.",
            "<b>Real Google integration in a local app.</b> Local LLM frontends "
            "(LM Studio, Jan.ai, Open-WebUI, AnythingLLM) treat the LLM as a "
            "general chatbox. They do not know how to fetch your inbox or push "
            "events to your calendar.",
            "<b>Workflow templates over free-form chat.</b> Summary, Tasks, "
            "Insights, and Compare are four pre-engineered prompts. The user "
            "picks an intent; the prompt enforces output structure. There is no "
            "<i>“how should I phrase this?”</i> step.",
            "<b>Action items become calendar events.</b> Most assistants stop at "
            "<i>showing</i> tasks. This one ships them — one click, real Google "
            "Calendar events with priority-aware reminders.",
            "<b>Open and inspectable.</b> Every prompt, every score, every line "
            "of UI is in this codebase. No black box, no vendor lock-in.",
        ]),

        Paragraph("Where the other products win", S["H2"]),
        Paragraph(
            "It would be dishonest not to name the trade-offs. Cloud assistants "
            "have larger models — a frontier API can write better summaries than "
            "a 1B local model. Microsoft 365 Copilot and Gemini in Workspace are "
            "deeply embedded in the Office and Workspace UIs respectively, so "
            "they meet users where they already work. Superhuman AI's triage "
            "is integrated into a fully-redesigned email client. AnythingLLM has "
            "real document-search via embeddings.",
            S["Body"],
        ),
        Paragraph(
            "Each of those wins matters when the user's content is shareable. "
            "When it is not — when privacy, compliance, cost, or offline are "
            "binding constraints — those wins do not apply, and this app is the "
            "remaining option.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_modes(S) -> list:
    return [
        Paragraph("4. Two operating modes", S["H1"]),
        Paragraph(
            "The app has a hard split between <b>Manual</b> and <b>Auto</b> mode, "
            "selected by a dropdown in the header. The two modes share almost no UI "
            "and exist for very different jobs.",
            S["Body"],
        ),
        Paragraph("Manual mode", S["H2"]),
        Paragraph(
            "The default. The user picks one piece of content (paste, drop a file, "
            "fetch an email, or load a built-in sample), chooses a workflow from a "
            "dropdown, and clicks Process. One workflow runs on one input. The "
            "output appears in the right-hand panel.",
            S["Body"],
        ),
        Paragraph(
            "Manual mode is the right choice when the user already knows what they "
            "want to do with a specific document. It is precise, deterministic, and "
            "predictable.",
            S["Body"],
        ),
        Paragraph("Auto mode", S["H2"]),
        Paragraph(
            "A different idiom. The user clicks <i>Scan recent emails</i> and the app "
            "fetches messages from the last N hours (default 12), runs a lean triage "
            "prompt against each, scores them, and presents a ranked digest with "
            "color-coded urgency tiers. Auto mode is for the morning inbox catch-up: "
            "<i>What needs my attention from overnight?</i>",
            S["Body"],
        ),
        Paragraph(
            "Auto mode hides the input area and workflow picker entirely. They would "
            "not make sense — Auto picks its own inputs and runs its own (single) "
            "workflow. The result is shown on a dedicated <i>Auto</i> tab.",
            S["Body"],
        ),
        Paragraph("Why two modes instead of one?", S["H3"]),
        Paragraph(
            "Bulk processing and precise single-document work have different "
            "constraints. Manual mode optimises for output quality (full prompts, "
            "full chunking, no shortcuts). Auto mode optimises for throughput (lean "
            "prompt, hard caps on input and output tokens, parallel execution). "
            "Trying to serve both from one code path would compromise both.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_workflows(S) -> list:
    return [
        Paragraph("5. The four manual workflows", S["H1"]),
        Paragraph(
            "Each workflow is one prompt and one expected JSON shape. The prompts "
            "live in <font face=\"Courier\">core/prompt_manager.py</font>; the parsers "
            "share <font face=\"Courier\">core/output_parser.py</font>.",
            S["Body"],
        ),
        Paragraph("Summary", S["H2"]),
        Paragraph(
            "Produces a scannable bulleted overview of the input. The prompt enforces "
            "4–7 complete sentences, opening with topic + setting and closing with "
            "the implication. A few-shot example is included to keep small models "
            "(like <font face=\"Courier\">llama3.2:1b</font>) from collapsing the output "
            "into short noun phrases.",
            S["Body"],
        ),
        Paragraph(
            "Output schema:",
            S["Body"],
        ),
        _code(S, '{ "summary": ["sentence 1.", "sentence 2.", "..."] }'),
        Paragraph("Tasks", S["H2"]),
        Paragraph(
            "Extracts obligations directed at the reader. The prompt is deliberate "
            "about distinguishing actionable content (memos, emails) from narrative "
            "content (news articles, discussions) — the latter returns an empty "
            "<font face=\"Courier\">action_items</font> list to avoid fabricating "
            "tasks out of stories.",
            S["Body"],
        ),
        _code(S, (
            '{\n'
            '  "source_type": "actionable" | "narrative" | "discussion" | "informational",\n'
            '  "action_items": [\n'
            '    {"task": "...", "deadline": "...", "priority": "high|medium|low"}\n'
            '  ]\n'
            '}'
        )),
        Paragraph("Insights", S["H2"]),
        Paragraph(
            "Surfaces observations, patterns, and implications — not action items, "
            "not a summary. Used when the user wants the <i>so what</i> rather than "
            "the <i>what happened</i>.",
            S["Body"],
        ),
        _code(S, '{ "key_insights": ["...", "...", "..."] }'),
        Paragraph("Compare", S["H2"]),
        Paragraph(
            "Operates on two or more documents separated by an explicit "
            "<font face=\"Courier\">--- DOCUMENT BREAK ---</font> marker. Unlike the "
            "other workflows, Compare bypasses the chunker entirely — comparing "
            "documents needs the whole-document view in a single prompt or the "
            "comparison loses cross-document context.",
            S["Body"],
        ),
        _code(S, (
            '{\n'
            '  "summary": "one-paragraph overview",\n'
            '  "common_themes": ["..."],\n'
            '  "differences": ["..."],\n'
            '  "key_insights": ["..."]\n'
            '}'
        )),
        Paragraph(
            "The renderer in <font face=\"Courier\">ui/main_window.py::_format_bullet</font> "
            "is tolerant of both plain-string and structured-dict outputs in the "
            "differences and insights arrays. Some models return rich "
            "<font face=\"Courier\">{text, option_a, option_b}</font> objects; the UI "
            "formats those as nested A/B sections under a header.",
            S["Body"],
        ),

        Paragraph("Parsing the model's JSON", S["H2"]),
        Paragraph(
            "All four workflows share one parser. Real LLM output often arrives "
            "wrapped in code fences or with leading prose, so we strip fences and "
            "walk the brace structure to find the outermost balanced object.",
            S["Body"],
        ),
        _code(S, (
            "# core/output_parser.py\n"
            "def extract_json(text: str) -> str | None:\n"
            "    text = re.sub(r'```(?:json)?\\s*', '', text).strip()\n"
            "    start = text.find('{')\n"
            "    if start == -1:\n"
            "        return None\n"
            "    depth = 0\n"
            "    for i, ch in enumerate(text[start:], start):\n"
            "        if ch == '{':\n"
            "            depth += 1\n"
            "        elif ch == '}':\n"
            "            depth -= 1\n"
            "            if depth == 0:\n"
            "                return text[start:i + 1]\n"
            "    return None"
        )),
        Paragraph(
            "If parsing still fails the chunk is logged and dropped, and the "
            "remaining chunks proceed — partial output is better than a full "
            "failure.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_auto_mode(S) -> list:
    return [
        Paragraph("6. Auto mode in depth", S["H1"]),
        Paragraph(
            "Auto mode is the most engineered feature in the app. This section walks "
            "through every design decision so you can defend it under questioning.",
            S["Body"],
        ),
        Paragraph("The pipeline", S["H2"]),
        _code(S, (
            "Gmail (newer_than:Nh)\n"
            "      ↓ (cap to 8 emails)\n"
            "_truncate_body(150 words)\n"
            "      ↓\n"
            "_triage_prompt  ── 3 worker threads ──→  Ollama (num_predict=150,\n"
            "      ↓                                          num_ctx=1024,\n"
            "_parse_triage_response                            format=json)\n"
            "      ↓\n"
            "score_email  → (score, tier)\n"
            "      ↓\n"
            "sort by score desc → digest rendering → calendar push (optional)"
        )),
        Paragraph("The triage prompt", S["H2"]),
        Paragraph(
            "Defined in <font face=\"Courier\">core/auto_scan.py::_triage_prompt</font>. "
            "Asks the LLM for three things in a single JSON response: an urgency "
            "tier, a one-sentence reason, and up to three extracted tasks. Short "
            "input plus short output equals fast generation, which matters because "
            "we run this once per email.",
            S["Body"],
        ),
        _code(S, (
            'You are an inbox triage assistant. Read the email and rate\n'
            'how urgently the reader must act.\n'
            '\n'
            'Return ONLY JSON in this exact shape:\n'
            '{\n'
            '  "urgency": "high" | "medium" | "low" | "none",\n'
            '  "reason": "one short sentence explaining the rating",\n'
            '  "tasks": [\n'
            '    {"task": "...", "priority": "high|medium|low",\n'
            '     "deadline": "deadline or \\\'not specified\\\'"}\n'
            '  ]\n'
            '}\n'
            '\n'
            'Rules:\n'
            '- "high"  — deadline today/tomorrow or escalated/urgent.\n'
            '- "medium"— request with a non-urgent deadline.\n'
            '- "low"   — soft ask, FYI with follow-up.\n'
            '- "none"  — newsletter, no action required.'
        )),

        Paragraph("Scoring heuristic", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">score_email()</font> uses the LLM's "
            "<font face=\"Courier\">urgency</font> field as the primary tier signal, "
            "with a fallback heuristic over extracted tasks for cases where the model "
            "omits the field. The numeric score is computed deterministically from "
            "task priority and deadline urgency words, and serves as the "
            "within-tier tie-breaker for sorting.",
            S["Body"],
        ),
        _bullets(S, [
            "<b>Per task</b>: priority weight (high=3, medium=2, low=1).",
            "<b>Per deadline</b>: urgent words like <i>today, asap, urgent, eod</i> add +2; "
            "soft urgency like <i>tomorrow, this week,</i> or a day-of-week name adds +1.",
            "<b>Tier from score</b>: ≥6 → high, ≥3 → medium, ≥1 → low, else none.",
        ]),
        _code(S, (
            "# core/auto_scan.py — heart of the scoring function\n"
            "def score_email(parsed: dict) -> tuple[int, str]:\n"
            "    tasks = parsed.get('action_items') or []\n"
            "    score = 0\n"
            "    for task in tasks:\n"
            "        prio = (task.get('priority') or '').lower()\n"
            "        score += _PRIORITY_SCORES.get(prio, 1)\n"
            "        score += _deadline_urgency(task.get('deadline') or '')\n"
            "    llm_tier = (parsed.get('urgency') or '').lower()\n"
            "    if llm_tier in _VALID_TIERS:\n"
            "        return score, llm_tier        # trust the LLM\n"
            "    if not tasks:\n"
            "        return 0, 'none'\n"
            "    return score, _tier_for(score)    # fall back to heuristic"
        )),

        Paragraph("Parallelism and performance", S["H2"]),
        Paragraph(
            "The scan uses a "
            "<font face=\"Courier\">ThreadPoolExecutor</font> with three workers and "
            "<font face=\"Courier\">as_completed()</font> for monotonic progress. "
            "Cancellation is non-blocking via "
            "<font face=\"Courier\">shutdown(wait=False, cancel_futures=True)</font> — "
            "in-flight LLM requests are dropped rather than waited on.",
            S["Body"],
        ),
        _code(S, (
            "# core/auto_scan.py — parallel scan loop\n"
            "executor = ThreadPoolExecutor(max_workers=max_workers)\n"
            "try:\n"
            "    future_map = {executor.submit(_analyse_email, e): e\n"
            "                  for e in emails}\n"
            "    for fut in as_completed(future_map):\n"
            "        if cancel_check and cancel_check():\n"
            "            break\n"
            "        results.append(fut.result())\n"
            "        completed += 1\n"
            "        progress_callback(completed, total,\n"
            "                          future_map[fut].get('subject'))\n"
            "finally:\n"
            "    executor.shutdown(wait=False, cancel_futures=True)\n"
            "results.sort(key=lambda r: r['score'], reverse=True)"
        )),
        Paragraph(
            "The biggest single performance lever was capping "
            "<font face=\"Courier\">num_predict</font> on the Ollama call. Without "
            "this cap, small models often keep generating after the JSON closes — "
            "trailing whitespace, repeated keys, hallucinated continuations. We "
            "also reduced <font face=\"Courier\">num_ctx</font> to 1024 to speed up "
            "prefill on CPU-only runs.",
            S["Body"],
        ),
        Paragraph("The visible knobs", S["H2"]),
        _bullets(S, [
            "<b>Window</b>: 4 / 12 / 24 / 48 hours — Gmail's "
            "<font face=\"Courier\">newer_than:</font> search operator.",
            "<b>MAX_EMAILS</b>: hard cap at 8 per scan (UI constant in "
            "<font face=\"Courier\">main_window.py</font>).",
            "<b>MAX_EMAIL_WORDS</b>: 150 (<font face=\"Courier\">auto_scan.py</font>).",
            "<b>MAX_WORKERS</b>: 3. Bumping this only helps if Ollama's "
            "<font face=\"Courier\">OLLAMA_NUM_PARALLEL</font> is set ≥3 too.",
        ]),
        PageBreak(),
    ]


def section_architecture(S) -> list:
    return [
        Paragraph("7. Architecture and data flow", S["H1"]),
        Paragraph(
            "The codebase is structured as a thin UI on top of a clean processing "
            "core. Side effects (Ollama, Gmail, Calendar, SQLite, file I/O) live in "
            "leaf modules that the core orchestrates.",
            S["Body"],
        ),
        Paragraph("Manual-mode pipeline", S["H2"]),
        _code(S, (
            "input source (paste / .txt / .pdf / Gmail / sample)\n"
            "    │\n"
            "    ▼\n"
            "input_processing/cleaner.py   collapse whitespace\n"
            "    │\n"
            "    ▼\n"
            "input_processing/chunker.py   split by sentence ≤ CHUNK_SIZE words\n"
            "    │\n"
            "    ▼  for each chunk:\n"
            "core/prompt_manager.py        build the workflow-specific prompt\n"
            "    │\n"
            "    ▼\n"
            "core/llm_router.py            (currently always 'ollama')\n"
            "    │\n"
            "    ▼\n"
            "services/ollama_service.py    HTTP POST → http://localhost:11434/api/generate\n"
            "    │\n"
            "    ▼\n"
            "core/output_parser.py         strip code fences, find balanced JSON\n"
            "    │\n"
            "    ▼\n"
            "core/workflow_engine.py       merge_results across chunks\n"
            "    │\n"
            "    ▼\n"
            "ui/main_window.py::_format_result   render bullets + sections\n"
            "    │\n"
            "    ▼\n"
            "storage/history_manager.py    record run to SQLite"
        )),
        Paragraph("Why the chunker exists", S["H2"]),
        Paragraph(
            "Local models have small context windows. A 30-page PDF will not fit in a "
            "single prompt for most local models, and even when it does, generation "
            "quality often drops on very long inputs. The chunker splits text on "
            "sentence boundaries to a configurable word limit (default 300), runs the "
            "prompt independently on each chunk, and then "
            "<font face=\"Courier\">merge_results()</font> reduces the per-chunk "
            "outputs into a single result.",
            S["Body"],
        ),
        _code(S, (
            "# input_processing/chunker.py\n"
            "def chunk_text(text: str, max_words: int = 300) -> list[str]:\n"
            "    sentences = re.split(r'(?<=[.!?])\\s+', text.strip())\n"
            "    chunks, current, count = [], [], 0\n"
            "    for sentence in sentences:\n"
            "        wc = len(sentence.split())\n"
            "        if count + wc > max_words and current:\n"
            "            chunks.append(' '.join(current))\n"
            "            current, count = [], 0\n"
            "        current.append(sentence); count += wc\n"
            "    if current:\n"
            "        chunks.append(' '.join(current))\n"
            "    return chunks if chunks else [text]"
        )),
        Paragraph("Why Compare bypasses the chunker", S["H2"]),
        Paragraph(
            "Comparison is inherently cross-document. Running the Compare prompt on a "
            "single chunk of Document A would not see Document B — there would be "
            "nothing to compare against. So Compare passes the whole concatenated "
            "input to the model as one prompt and accepts the trade-off that very "
            "long compare inputs may exceed context.",
            S["Body"],
        ),
        Paragraph("Why Auto bypasses both", S["H2"]),
        Paragraph(
            "Auto mode hits the LLM once per email with a tight, lean prompt — no "
            "chunker, no workflow engine, no merge. The path is short and fast.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_tech_stack(S) -> list:
    return [
        Paragraph("8. Tech stack and rationale", S["H1"]),
        Paragraph("PyQt5 — desktop UI", S["H2"]),
        Paragraph(
            "Mature, native-feeling, and works on Windows without bundling a web "
            "engine. The window draws like a real app, not a browser. Importantly, "
            "PyQt5 lets us run real OS-thread workers (<font face=\"Courier\">QThread</font>) "
            "for long LLM calls without freezing the UI — the central reliability "
            "story for any local-AI desktop product.",
            S["Body"],
        ),
        Paragraph("Ollama — local LLM serving", S["H2"]),
        Paragraph(
            "Ollama provides a simple HTTP API (<font face=\"Courier\">/api/generate</font>) "
            "with a model registry that handles GGUF downloads transparently. It "
            "supports <font face=\"Courier\">keep_alive</font> so the model stays "
            "warm between requests, and a <font face=\"Courier\">format: \"json\"</font> "
            "flag for constrained JSON decoding. Switching models means changing one "
            "line in <font face=\"Courier\">.env</font>.",
            S["Body"],
        ),
        _code(S, (
            "# services/ollama_service.py\n"
            "def call_ollama(prompt, model=None, options=None):\n"
            "    merged = {**_DEFAULT_OPTIONS, **(options or {})}\n"
            "    response = requests.post(\n"
            "        settings.OLLAMA_URL,\n"
            "        json={\n"
            "            'model': model or settings.OLLAMA_MODEL,\n"
            "            'prompt': prompt,\n"
            "            'stream': False,\n"
            "            'options': merged,       # temp, num_predict, num_ctx…\n"
            "            'format': 'json',        # constrained JSON decoding\n"
            "            'keep_alive': '30m',     # keep model warm in RAM\n"
            "        },\n"
            "        timeout=300,\n"
            "    )\n"
            "    return response.json()['response']"
        )),
        Paragraph("PyMuPDF — PDF reading", S["H2"]),
        Paragraph(
            "Used purely for "
            "<font face=\"Courier\">page.get_text()</font> in "
            "<font face=\"Courier\">pdf_handler.py</font>. Lighter than alternatives "
            "and Windows-friendly.",
            S["Body"],
        ),
        Paragraph("google-api-python-client + google-auth-oauthlib", S["H2"]),
        Paragraph(
            "Gmail and Google Calendar integration with a desktop OAuth flow. The "
            "first time the user clicks <i>Add account</i>, "
            "<font face=\"Courier\">InstalledAppFlow.run_local_server()</font> opens "
            "a browser, the user grants scopes, and the resulting credentials are "
            "pickled to <font face=\"Courier\">tokens/&lt;email&gt;.pkl</font>.",
            S["Body"],
        ),
        Paragraph("SQLite — run history", S["H2"]),
        Paragraph(
            "The standard library's <font face=\"Courier\">sqlite3</font> module "
            "backs <font face=\"Courier\">history.db</font> at the project root. One "
            "table, four columns, JSON-blob result column. Zero external dependency.",
            S["Body"],
        ),
        Paragraph("python-dotenv — config", S["H2"]),
        Paragraph(
            "Reads <font face=\"Courier\">.env</font> at startup. Three keys: "
            "<font face=\"Courier\">GMAIL_CLIENT_SECRET</font>, "
            "<font face=\"Courier\">OLLAMA_URL</font>, "
            "<font face=\"Courier\">OLLAMA_MODEL</font>. User preferences "
            "(model and chunk size) are layered on top via "
            "<font face=\"Courier\">config/user_prefs.json</font>.",
            S["Body"],
        ),
        Paragraph("requests — HTTP", S["H2"]),
        Paragraph(
            "Used only by <font face=\"Courier\">ollama_service.py</font>. The "
            "Gmail/Calendar clients use Google's own HTTP layer.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_module_reference_header() -> str:
    return "9. Module reference"


def section_module_reference(S) -> list:
    rows = [
        ["File", "Role"],
        ["main.py", "Entry point — calls run_app(). Also exposes process_file() for CLI use."],
        ["config/settings.py", "Loads .env, layers user_prefs.json on top, exposes module-level vars."],
        ["core/prompt_manager.py", "Builds the workflow-specific prompt string for each chunk."],
        ["core/llm_router.py", "Single-function indirection over Ollama. Easy place to add other providers."],
        ["core/output_parser.py", "Strips code fences and extracts the outermost balanced JSON object."],
        ["core/workflow_engine.py", "run_workflow(text, workflow, progress_callback) — chunks, calls, merges."],
        ["core/auto_scan.py", "Auto mode: fetches recent emails, runs triage prompt in parallel, scores, sorts."],
        ["services/ollama_service.py", "HTTP client. Merges per-call options over defaults."],
        ["services/calendar_service.py", "push_tasks_to_calendar — deadline parsing, priority-aware reminders."],
        ["input_processing/cleaner.py", "Collapse whitespace."],
        ["input_processing/chunker.py", "Sentence-boundary split to ≤ max_words per chunk."],
        ["input_processing/text_handler.py", "Read .txt file."],
        ["input_processing/pdf_handler.py", "Read .pdf via PyMuPDF page.get_text()."],
        ["input_processing/email_handler.py", "Gmail messages list+get; extracts plain-text body."],
        ["input_processing/google_auth.py", "Multi-account OAuth: tokens/<email>.pkl, active.txt pointer."],
        ["storage/database.py", "SQLite history table — init/save/get/clear."],
        ["storage/history_manager.py", "Thin wrapper over database.py — record/fetch/purge."],
        ["exports/exporter.py", "Render a result dict to .txt or .csv."],
        ["utils/logger.py", "get_logger() — standard logging setup."],
        ["utils/date_extractor.py", "Cheap regex deadline detector (legacy helper)."],
        ["ui/main_window.py", "The whole window — header, mode switching, splitters, all workers."],
        ["ui/samples.py", "Four built-in demo documents loaded via the Sample menu."],
        ["ui/settings_dialog.py", "Settings dialog for Ollama model and chunk size."],
        ["ui/task_review_dialog.py", "Editable table of tasks before pushing to Calendar."],
    ]
    table = Table(rows, colWidths=[2.0 * inch, 4.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Courier-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CODE_BG]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT_DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [
        Paragraph("9. Module reference", S["H1"]),
        Paragraph(
            "A one-line description of every meaningful Python file in the project. "
            "If you forget where something lives, this is the index.",
            S["Body"],
        ),
        table,
        PageBreak(),
    ]


def section_google(S) -> list:
    return [
        Paragraph("10. Google integration", S["H1"]),
        Paragraph(
            "Two Google APIs are used: Gmail (read-only) and Calendar (event creation). "
            "Both go through one authentication system that supports multiple accounts.",
            S["Body"],
        ),
        Paragraph("Scopes requested", S["H2"]),
        _bullets(S, [
            "<font face=\"Courier\">gmail.readonly</font> — fetch message list and bodies. "
            "Read-only by design; the app never sends, deletes, or modifies email.",
            "<font face=\"Courier\">calendar.events</font> — create events on the user's "
            "primary calendar (no read of existing events, no other calendars).",
            "<font face=\"Courier\">userinfo.email</font> + <font face=\"Courier\">openid</font> "
            "— identify which account just signed in, so multiple Google accounts can "
            "co-exist and the user can switch between them.",
        ]),
        Paragraph("Multi-account flow", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">input_processing/google_auth.py</font> manages a "
            "<font face=\"Courier\">tokens/</font> directory with one "
            "<font face=\"Courier\">&lt;email&gt;.pkl</font> file per signed-in account, "
            "plus an <font face=\"Courier\">active.txt</font> pointer to whichever account "
            "the user has currently selected. The header dropdown shows the list, "
            "with virtual entries to add or remove accounts.",
            S["Body"],
        ),
        Paragraph(
            "Tokens auto-refresh on every API call using "
            "<font face=\"Courier\">google.auth.transport.requests.Request</font>. If "
            "refresh fails, the auth flow restarts and the user is prompted to "
            "re-grant.",
            S["Body"],
        ),
        Paragraph("Calendar event shape", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">services/calendar_service.py::push_tasks_to_calendar</font> "
            "creates one event per task. Deadline parsing uses "
            "<font face=\"Courier\">dateutil.parser</font> with a +7-day fallback for "
            "freeform strings. Reminder lead-time follows task priority: high → 30 min, "
            "medium → 2 hours, low → 24 hours. Events default to a 9am, 30-minute slot "
            "if no time component is parsed.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_storage(S) -> list:
    return [
        Paragraph("11. Storage and export", S["H1"]),
        Paragraph("Run history", S["H2"]),
        Paragraph(
            "Every successful manual-mode run is recorded to "
            "<font face=\"Courier\">history.db</font> at the project root. The schema "
            "is intentionally minimal:",
            S["Body"],
        ),
        _code(S, (
            "CREATE TABLE history (\n"
            "    id            INTEGER PRIMARY KEY AUTOINCREMENT,\n"
            "    timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,\n"
            "    workflow      TEXT NOT NULL,\n"
            "    input_preview TEXT,           -- first 120 chars of input\n"
            "    result        TEXT NOT NULL   -- json.dumps(result)\n"
            ");"
        )),
        Paragraph(
            "The History tab on the right panel reads the most recent 50 rows, lets "
            "the user search by workflow or preview text, and re-loads the full "
            "result into the Output panel on click. The renderer tolerates both old "
            "(string summary) and new (list summary) shapes so historical entries "
            "still render correctly.",
            S["Body"],
        ),
        Paragraph("TXT and CSV export", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">exports/exporter.py</font> writes either a human-"
            "readable TXT or a CSV (different shape per workflow) into a folder of "
            "the user's choice. Filename pattern: "
            "<font face=\"Courier\">result_&lt;workflow&gt;_&lt;timestamp&gt;.&lt;ext&gt;</font>.",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_ui(S) -> list:
    return [
        Paragraph("12. UI tour", S["H1"]),
        Paragraph(
            "The whole window is built in <font face=\"Courier\">ui/main_window.py</font>. "
            "Major pieces:",
            S["Body"],
        ),
        Paragraph("Header", S["H2"]),
        Paragraph(
            "Title block on the left; Mode, Provider, Account combos and a settings "
            "gear on the right. Switching Mode rebinds the left panel and the right "
            "tab focus instantly.",
            S["Body"],
        ),
        Paragraph("Splitters", S["H2"]),
        Paragraph(
            "A horizontal QSplitter divides the body into left (input + controls) "
            "and right (output tabs). A vertical QSplitter inside the Output tab "
            "divides emails (top) from the workflow output (bottom). Handles are "
            "6px wide, dark gray, and turn blue on hover. All splitters are "
            "<font face=\"Courier\">setChildrenCollapsible(False)</font> to prevent "
            "accidental hiding of panes.",
            S["Body"],
        ),
        Paragraph("Workers", S["H2"]),
        Paragraph(
            "Every long-running operation runs in its own QThread to keep the UI "
            "responsive: <font face=\"Courier\">Worker</font> for manual workflow runs, "
            "<font face=\"Courier\">AutoScanWorker</font> for the auto-mode scan, "
            "<font face=\"Courier\">CalendarWorker</font> for batched event creation, "
            "<font face=\"Courier\">AddAccountWorker</font> for the OAuth flow. Each emits "
            "<font face=\"Courier\">finished</font>, <font face=\"Courier\">error</font>, "
            "and (for cancellable workers) <font face=\"Courier\">cancelled</font> "
            "signals. Progress signals route through "
            "<font face=\"Courier\">_on_progress</font> / "
            "<font face=\"Courier\">_on_auto_progress</font> for the chunk counter and "
            "email-scan ticker.",
            S["Body"],
        ),
        Paragraph("Sample documents", S["H2"]),
        Paragraph(
            "Four built-in demo documents in <font face=\"Courier\">ui/samples.py</font> "
            "are loaded from a popup menu under the <i>Sample</i> button. Choosing one "
            "fills the input text and auto-selects the matching workflow. Meeting "
            "notes are deliberately long enough to chunk into multiple pieces so the "
            "progress counter is meaningful on stage.",
            S["Body"],
        ),
        Paragraph("Justified output", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">output_text</font> applies "
            "<font face=\"Courier\">Qt.AlignJustify</font> as the document's default "
            "text option, so all rendered prose has flush left and right margins.",
            S["Body"],
        ),

        Paragraph("Mode-switching code", S["H2"]),
        Paragraph(
            "The single function that swaps the entire left panel and the active "
            "right tab when the user changes Mode in the header dropdown:",
            S["Body"],
        ),
        _code(S, (
            "# ui/main_window.py — toggles every manual-only widget\n"
            "def _apply_mode(self):\n"
            "    is_auto = self._mode == 'auto'\n"
            "    self._input_label.setVisible(not is_auto)\n"
            "    self.input_text.setVisible(not is_auto)\n"
            "    for btn in self._input_buttons:\n"
            "        btn.setVisible(not is_auto)\n"
            "    self._workflow_label.setVisible(not is_auto)\n"
            "    self.workflow_selector.setVisible(not is_auto)\n"
            "    self._auto_hint.setVisible(is_auto)\n"
            "    for w in self._auto_window_row_widgets:\n"
            "        w.setVisible(is_auto)\n"
            "    if is_auto:\n"
            "        self.process_button.setText('🔍  Scan recent emails')\n"
            "        self.tabs.setCurrentIndex(self._auto_tab_index)\n"
            "    else:\n"
            "        self.process_button.setText('▶  Process   (Ctrl+Enter)')\n"
            "        self.tabs.setCurrentIndex(0)"
        )),
        PageBreak(),
    ]


def section_perf(S) -> list:
    return [
        Paragraph("13. Performance engineering", S["H1"]),
        Paragraph(
            "Auto mode is where most of the performance work went. The journey is "
            "worth knowing because the audience may ask <i>why is local AI viable on a "
            "laptop?</i>",
            S["Body"],
        ),
        Paragraph("Where the time goes", S["H2"]),
        Paragraph(
            "Total scan time is dominated by Ollama generation. Each LLM call has "
            "two phases: <b>prefill</b> (processing the prompt tokens) and "
            "<b>decoding</b> (generating output tokens). On CPU with a 1B model, "
            "decoding is roughly 30 tokens/second. Prefill scales linearly with "
            "<font face=\"Courier\">num_ctx</font>.",
            S["Body"],
        ),
        Paragraph("The four levers we pulled", S["H2"]),
        _bullets(S, [
            "<b>Per-email body truncation</b> — capped at 150 words. Most actionable "
            "content sits in the first paragraph; truncating to a tight window also "
            "guarantees a single LLM call per email (no chunker fan-out).",
            "<b>num_predict cap (150 tokens)</b> — without this, small models often "
            "continue generating after the JSON object closes. This was the single "
            "biggest win.",
            "<b>num_ctx = 1024</b> — shrinks the context window from the 2048/4096 "
            "default. Triage prompts are short, so this is enough headroom and it "
            "halves prefill time on CPU.",
            "<b>ThreadPoolExecutor (3 workers)</b> — pipelines requests through Ollama. "
            "Actually parallel only if Ollama's <font face=\"Courier\">OLLAMA_NUM_PARALLEL</font> "
            "env var is also set to 3+.",
        ]),
        Paragraph("Observed timing on a 1B model, CPU-only", S["H2"]),
        Paragraph(
            "Before any optimization: 5 emails in ~5 minutes (60 seconds per email, "
            "compounded by 2+ chunks per email because of long bodies).",
            S["Body"],
        ),
        Paragraph(
            "After body truncation + lean triage prompt + parallelism: 5 emails in "
            "~90 seconds (18 seconds per email).",
            S["Body"],
        ),
        Paragraph(
            "After tighter caps (num_predict 150, MAX_EMAIL_WORDS 150): expected to "
            "land around 50–60 seconds for 5 emails on the same hardware.",
            S["Body"],
        ),
        Paragraph("What we did not do (on purpose)", S["H2"]),
        _bullets(S, [
            "<b>Did not</b> swap to a smaller model — already on llama3.2:1b.",
            "<b>Did not</b> force GPU offload — installation pain is high; depends on "
            "the user's machine.",
            "<b>Did not</b> drop <font face=\"Courier\">format: \"json\"</font> — reliability "
            "of structured output matters more than the extra ~10% it costs.",
            "<b>Did not</b> add a noise pre-filter (auto-reply/no-reply skip). The "
            "false-positive risk on important emails outweighs the speedup.",
        ]),
        PageBreak(),
    ]


def section_demo_script(S) -> list:
    return [
        Paragraph("14. Demo presentation script", S["H1"]),
        Paragraph(
            "A 5–7 minute live demo flow, in suggested order. Memorise the beats; "
            "adapt the words.",
            S["Body"],
        ),
        Paragraph("Opener (30 seconds)", S["H2"]),
        Paragraph(
            "<i>“Knowledge workers spend a huge fraction of their day on documents "
            "and email. AI assistants help, but most of them send your content to a "
            "third party. I built a local-first version: same superpowers, nothing "
            "leaves the laptop.”</i>",
            S["Body"],
        ),
        Paragraph("Manual mode + sample doc (90 seconds)", S["H2"]),
        _bullets(S, [
            "Click Sample → Meeting notes. Show the placeholder swap to a real document.",
            "Pick Tasks workflow. Click Process. <b>Narrate</b> while the chunk counter "
            "ticks (\"Processing chunk 2 of 3…\") — this is where the audience sees "
            "the local model working.",
            "When the result lands, scroll through the action items. Point out the "
            "deadlines and priorities <i>that the model extracted itself</i>.",
        ]),
        Paragraph("Calendar push (60 seconds)", S["H2"]),
        _bullets(S, [
            "Click Push Tasks to Google Calendar. Show the review dialog — edit one "
            "deadline live to demonstrate the human-in-the-loop step.",
            "Click Push. Show the events landing on your real calendar.",
        ]),
        Paragraph("Summary, Insights, Compare (90 seconds)", S["H2"]),
        _bullets(S, [
            "Load the Product brief sample, run Summary — the bullets read crisply.",
            "Run Insights on the same doc to show the difference in framing.",
            "Load the Compare sample (two strategy docs), run Compare. The "
            "<i>differences</i> section shows side-by-side A/B answers.",
        ]),
        Paragraph("Auto mode finale (90 seconds)", S["H2"]),
        _bullets(S, [
            "Flip Mode to Auto. The left panel transforms. Narrate the transition.",
            "Pick 4 hours. Click Scan. Narrate over the email-by-email progress.",
            "When results land, point at the colored tiers and the LLM's one-line "
            "reasons.",
            "Click Push high/medium tasks to Calendar to close the loop.",
        ]),
        Paragraph("Close (30 seconds)", S["H2"]),
        Paragraph(
            "<i>“Everything you just saw — the summarisation, the task extraction, "
            "the inbox triage — ran on this laptop. No cloud LLM was called. The "
            "model weights are 1.3 gigabytes. The audience for this is anyone with "
            "a privacy constraint or an offline use case.”</i>",
            S["Body"],
        ),
        PageBreak(),
    ]


def section_qa(S) -> list:
    return [
        Paragraph("15. Likely audience questions", S["H1"]),
        Paragraph(
            "Prepared answers for the questions that tend to come up.",
            S["Body"],
        ),

        Paragraph("Q: How does this scale to a larger document?", S["H2"]),
        Paragraph(
            "The chunker splits on sentence boundaries to a configurable word "
            "count (default 300). Each chunk runs independently and "
            "<font face=\"Courier\">merge_results()</font> reduces. A 30-page PDF "
            "becomes 30–60 LLM calls, which take a couple of minutes on local "
            "hardware. Compare is the exception — it needs whole-document context "
            "and therefore caps out at the model's context window.",
            S["Body"],
        ),

        Paragraph("Q: What stops the LLM from inventing tasks?", S["H2"]),
        Paragraph(
            "The Tasks prompt explicitly distinguishes <i>actionable</i> sources "
            "(emails, memos addressed to the reader) from <i>narrative</i> or "
            "<i>discussion</i> sources (news articles, forum threads). If the model "
            "classifies the input as narrative, it must return an empty action "
            "items list. The prompt also lists positive and negative examples.",
            S["Body"],
        ),

        Paragraph("Q: What if the LLM returns invalid JSON?", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">core/output_parser.py</font> strips code fences "
            "and extracts the outermost balanced JSON object before parsing. Ollama "
            "is also called with <font face=\"Courier\">format: \"json\"</font>, "
            "which enforces a JSON-shaped output. If parsing still fails, the "
            "chunk is logged and dropped; other chunks proceed normally.",
            S["Body"],
        ),

        Paragraph("Q: Why local, not cloud?", S["H2"]),
        Paragraph(
            "Three reasons. <b>Privacy</b>: legal and compliance constraints often "
            "rule out sending content to a third-party API. <b>Cost</b>: a frontier "
            "API call costs more than a local laptop second. <b>Offline</b>: the "
            "app works on a plane, in a SCIF, or behind a corporate firewall.",
            S["Body"],
        ),

        Paragraph("Q: Why Ollama specifically?", S["H2"]),
        Paragraph(
            "Three reasons. <b>Simplicity</b>: a single HTTP endpoint. "
            "<b>Model library</b>: pull a model by name, no GGUF hunting. "
            "<b>keep_alive</b>: the model stays warm in RAM between requests, which "
            "makes back-to-back calls fast.",
            S["Body"],
        ),

        Paragraph("Q: What happens if Ollama is not running?", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">services/ollama_service.py</font> catches the "
            "connection error and raises a user-facing RuntimeError with the URL "
            "it tried and a suggestion to run <font face=\"Courier\">ollama serve</font>. "
            "The Worker thread reports this to the UI, which surfaces it in the "
            "Output panel — no silent failure.",
            S["Body"],
        ),

        Paragraph("Q: How is multi-account Gmail handled?", S["H2"]),
        Paragraph(
            "<font face=\"Courier\">tokens/&lt;email&gt;.pkl</font> per account, "
            "<font face=\"Courier\">active.txt</font> as a pointer. The header dropdown "
            "switches accounts by rewriting that pointer. New accounts go through "
            "the OAuth flow in <font face=\"Courier\">add_account()</font>. Tokens "
            "auto-refresh on every API call.",
            S["Body"],
        ),

        Paragraph("Q: Could you swap Ollama for another provider?", S["H2"]),
        Paragraph(
            "Yes. <font face=\"Courier\">core/llm_router.py</font> is the abstraction "
            "point. It currently delegates to <font face=\"Courier\">ollama_service.py</font>, "
            "but adding (say) an Anthropic or OpenAI provider would mean a new "
            "<font face=\"Courier\">services/&lt;name&gt;_service.py</font> with the "
            "same <font face=\"Courier\">call_x(prompt, options)</font> shape and a "
            "branch in <font face=\"Courier\">set_provider()</font>. The rest of the "
            "code is provider-agnostic.",
            S["Body"],
        ),

        Paragraph("Q: How accurate is the triage scoring?", S["H2"]),
        Paragraph(
            "It is a heuristic. The LLM-supplied urgency tier is the primary signal; "
            "the numeric score is deterministic from extracted task priorities and "
            "deadline urgency words. We deliberately did not use an LLM-rated "
            "numeric score because that adds an extra call per email without "
            "obvious quality improvement, and reproducibility matters for demos.",
            S["Body"],
        ),

        PageBreak(),
    ]


def section_recent(S) -> list:
    return [
        Paragraph("16. Recent improvements", S["H1"]),
        Paragraph(
            "Features added in the final iteration round, in the order they were "
            "built. Mentioning these helps tell the story of <i>why</i> the app "
            "looks the way it does today.",
            S["Body"],
        ),
        _bullets(S, [
            "<b>Sample document menu</b> — four built-in demo docs so the live demo "
            "never depends on Gmail or a freshly typed input.",
            "<b>Chunk progress counter</b> — the workflow engine now reports chunk "
            "completion to the UI, so the user sees \"Processing chunk 2 / 5…\" "
            "during long runs.",
            "<b>Auto mode</b> — the headline feature added late: inbox triage with a "
            "lean prompt, deterministic scoring, parallel execution, calendar push.",
            "<b>Performance tuning of auto mode</b> — body truncation, num_predict "
            "cap, num_ctx cap, ThreadPoolExecutor. Reduced 5 minutes to under a "
            "minute for 5 emails on a 1B CPU model.",
            "<b>Bullet-style summary output</b> — the summary workflow returns an "
            "array of complete sentences instead of a single prose blob, with "
            "extra blank lines between bullets for readability.",
            "<b>Justified output panel</b> — long lines wrap with flush left and "
            "right margins for a printed-page feel.",
            "<b>Compare dict rendering</b> — the renderer detects when the LLM "
            "returns structured <font face=\"Courier\">{text, option_a, option_b}</font> "
            "objects and formats them as nested A/B sections.",
            "<b>Resizable panes</b> — horizontal splitter between left and right, "
            "vertical splitter between email list and output. The input box "
            "expands to fill available space.",
        ]),
        PageBreak(),
    ]


def section_setup(S) -> list:
    return [
        Paragraph("17. Setup and configuration reference", S["H1"]),
        Paragraph("Required services", S["H2"]),
        _bullets(S, [
            "<b>Ollama</b> running locally with at least one model pulled. "
            "Default model name is <font face=\"Courier\">mistral</font> but the "
            "<font face=\"Courier\">.env</font> file can override.",
            "<b>Google Cloud project</b> with OAuth client credentials (Desktop "
            "type) downloaded as a JSON file, plus Gmail API and Calendar API "
            "enabled for that project.",
        ]),
        Paragraph(".env keys", S["H2"]),
        _code(S, (
            "GMAIL_CLIENT_SECRET=path/to/client_secret.json\n"
            "OLLAMA_URL=http://localhost:11434/api/generate\n"
            "OLLAMA_MODEL=llama3.2:1b"
        )),
        Paragraph("User preferences", S["H2"]),
        Paragraph(
            "Stored in <font face=\"Courier\">config/user_prefs.json</font> and edited "
            "via the Settings dialog (Ctrl+,). Currently exposes Ollama model and "
            "chunk size. Saved values override the corresponding "
            "<font face=\"Courier\">.env</font> values.",
            S["Body"],
        ),
        Paragraph("Keyboard shortcuts", S["H2"]),
        _bullets(S, [
            "<font face=\"Courier\">Ctrl+Enter</font> — Process / Scan",
            "<font face=\"Courier\">Ctrl+S</font> — Export TXT",
            "<font face=\"Courier\">Ctrl+Shift+S</font> — Export CSV",
            "<font face=\"Courier\">Ctrl+O</font> — Open file",
            "<font face=\"Courier\">Ctrl+E</font> — Fetch emails",
            "<font face=\"Courier\">Ctrl+,</font> — Settings",
            "<font face=\"Courier\">Ctrl+L</font> — Clear input",
        ]),
        Paragraph("Run", S["H2"]),
        _code(S, (
            "venv/Scripts/python.exe main.py\n"
            "\n"
            "# Re-generate this PDF:\n"
            "venv/Scripts/python.exe tools/generate_doc.py"
        )),
    ]


# ── Main ──────────────────────────────────────────────────────────────────

def build():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="AI Workflow Copilot — Project Guide",
        author="AI Workflow Copilot",
    )
    S = _styles()
    story = []
    story += cover(S)
    story += section_overview(S)
    story += section_use_cases(S)
    story += section_comparison(S)
    story += section_modes(S)
    story += section_workflows(S)
    story += section_auto_mode(S)
    story += section_architecture(S)
    story += section_tech_stack(S)
    story += section_module_reference(S)
    story += section_google(S)
    story += section_storage(S)
    story += section_ui(S)
    story += section_perf(S)
    story += section_demo_script(S)
    story += section_qa(S)
    story += section_recent(S)
    story += section_setup(S)
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return OUT_PATH


if __name__ == "__main__":
    out = build()
    print(f"Wrote {out}")
