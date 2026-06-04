def build_prompt(text: str, workflow: str) -> str:

    if workflow == "summary":
        return f"""You are a professional summarization assistant. Produce a clear, scannable summary a busy reader can use INSTEAD OF reading the original.

Return ONLY JSON in this exact shape:
{{
  "summary": ["full sentence one.", "full sentence two.", "full sentence three.", "full sentence four."]
}}

STRICT RULES for every element of the "summary" array:
1. Each element MUST be a COMPLETE SENTENCE of at least 12 words.
2. Each element MUST contain a verb and state a fact, claim, or event from the source.
3. NEVER return single words, names, or noun phrases. "Anthropic" is WRONG. "Anthropic released Claude Opus 4.7 in early 2026" is RIGHT.
4. Return between 4 and 7 elements total.
5. Element 1 names the topic, source, and setting.
6. Middle elements cover the main claims, decisions, findings, or events in source order, with concrete specifics (names, numbers, dates, outcomes) where present.
7. The final element states the implication, conclusion, or "so what".
8. Do NOT include tasks, action items, or advice to the reader.
9. Do NOT prefix elements with dashes, bullets, or numbers — the array IS the structure.

EXAMPLE OF GOOD OUTPUT (for an article about small language models):
{{
  "summary": [
    "A TechCrunch piece reviews the 2026 shift among major AI labs toward smaller, locally runnable language models.",
    "Anthropic, Google DeepMind, and Meta have each released sub-3-billion-parameter models tuned for on-device use this year.",
    "The article argues the move is driven by privacy demands from enterprise customers and rising cloud inference costs.",
    "Benchmarks cited show the new small models reach 80 to 90 percent of last year's flagship performance on common tasks.",
    "The author concludes that the next 12 months will favour developers who ship local-first AI features over cloud-only ones."
  ]
}}

EXAMPLE OF BAD OUTPUT (do NOT do this):
{{
  "summary": ["Small Language Models", "Anthropic", "Google DeepMind", "Meta"]
}}

Input:
{text}
"""

    elif workflow == "tasks":
        return f"""You are a task extraction system.

Return ONLY JSON:
{{
  "source_type": "actionable" | "narrative" | "discussion" | "informational",
  "action_items": [
    {{"task": "...", "deadline": "...", "priority": "high/medium/low"}}
  ]
}}

A "task" means something the READER must DO. It is an obligation, request,
commitment, or instruction directed at the reader.

COUNT as a task:
- "Please submit the report by Friday"
- "Don't forget to renew your license"
- "You need to email HR"
- Meeting invites requiring the reader's attendance
- Deadlines or deliverables assigned to the reader

DO NOT count as a task:
- Events being described ("X happened", "Y released a product")
- Opinions, reactions, commentary, or discussion
- News reports, reddit threads, articles, blog posts, narratives
- Things OTHER people did or will do
- Suggestions or hypotheticals with no commitment from the reader

First decide source_type:
- "actionable"   — email/memo/instructions addressed to the reader
- "narrative"    — news, stories, descriptions of events
- "discussion"   — forum/reddit/comments/opinion
- "informational"— reference material, articles, documentation

If source_type is anything other than "actionable", return an EMPTY
action_items list. Do NOT invent tasks from narrative or discussion content.

Input:
{text}
"""

    elif workflow == "insights":
        return f"""You are a business analyst.

Return ONLY JSON:
{{
  "key_insights": ["...", "..."]
}}

Focus:
- Observations
- Patterns
- Implications
- NO tasks
- NO summary

Input:
{text}
"""

    elif workflow == "compare":
        return f"""You are a document comparison system.

The input contains TWO OR MORE documents (typically separated by blank lines or headers).

Return ONLY JSON:
{{
  "summary": "one-paragraph overview of what's being compared",
  "common_themes": ["...", "..."],
  "differences": ["...", "..."],
  "key_insights": ["...", "..."]
}}

Focus:
- What's shared across the documents (common_themes)
- What's unique or contradictory between them (differences)
- Higher-level observations (key_insights)

Input:
{text}
"""

    else:
        return f"Return structured JSON.\n\nInput:\n{text}"
