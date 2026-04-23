def build_prompt(text: str, workflow: str) -> str:

    if workflow == "summary":
        return f"""You are a summarization system.

Return ONLY JSON:
{{
  "summary": "...",
  "key_insights": []
}}

Focus:
- Short, clear summary
- No tasks
- No action items

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
