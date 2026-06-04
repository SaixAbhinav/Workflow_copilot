"""Auto-mode: fetch recent emails, run the tasks workflow on each, and rank
them by a cheap deterministic importance heuristic.

Importance score per email:
  - per task:  priority (high=3, medium=2, low=1) + deadline urgency
  - deadline urgency: "today/asap/urgent/eod" → +2, day-of-week or
    "tomorrow/this week" → +1, otherwise +0

Tier:  high (>=6), medium (>=3), low (>=1), none (0)
"""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

from core.llm_router import route_llm
from input_processing.cleaner import clean_text
from input_processing.email_handler import get_latest_emails
from utils.logger import get_logger

logger = get_logger(__name__)

# Callback signature: (completed_count, total, last_subject)
ProgressCallback = Callable[[int, int, str], None]
CancelCheck = Callable[[], bool]

# Cap body length before sending to the LLM. Auto mode hits the LLM directly
# (no chunker), so this is the hard cap on prompt size per email. Tight on
# purpose — most actionable signal is in the first paragraph of an email.
MAX_EMAIL_WORDS = 150

# How many emails to analyse in parallel against Ollama. 3 is a safe default
# for a single-GPU local model; increase if your hardware can handle it.
# Note: real parallelism also depends on Ollama's OLLAMA_NUM_PARALLEL env var
# (default 1 on older builds, 4 on newer). If Ollama serialises requests,
# raising MAX_WORKERS won't help.
MAX_WORKERS = 3

# Per-call Ollama options for the triage prompt. The big wins:
# - num_predict caps generated tokens so the model can't run away after the
#   JSON closes (the single biggest source of slow triage responses).
# - num_ctx shrinks the context window. Triage input is short, so a 1024-token
#   window is plenty and dramatically speeds up prefill on CPU.
_TRIAGE_LLM_OPTIONS = {
    "num_predict": 150,
    "num_ctx": 1024,
}

_URGENT_WORDS = ("today", "asap", "immediately", "urgent", "now", "eod", "tonight")
_SOON_WORDS = (
    "tomorrow", "this week",
    "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday",
)

_PRIORITY_SCORES = {"high": 3, "medium": 2, "med": 2, "low": 1}

_VALID_TIERS = ("high", "medium", "low", "none")


def _triage_prompt(text: str) -> str:
    """Lean per-email prompt: short input → short output → fast generation."""
    return f"""You are an inbox triage assistant. Read the email and rate how urgently the reader must act.

Return ONLY JSON in this exact shape:
{{
  "urgency": "high" | "medium" | "low" | "none",
  "reason": "one short sentence explaining the rating",
  "tasks": [
    {{"task": "what the reader must do", "priority": "high" | "medium" | "low", "deadline": "deadline or 'not specified'"}}
  ]
}}

Rules:
- "high" — explicit request to the reader with a deadline today/tomorrow, or anything escalated/urgent.
- "medium" — request to the reader with a non-urgent deadline (this week, next week).
- "low" — soft ask, FYI with a follow-up, or low-priority obligation.
- "none" — newsletter, auto-notification, marketing, no action required. Return an empty tasks list.
- Extract at most 3 tasks. Do NOT invent tasks from informational content.

Email:
{text}
"""


def _deadline_urgency(deadline: str) -> int:
    if not deadline:
        return 0
    lower = deadline.lower()
    if lower in ("not specified", "n/a", "none", "tbd", ""):
        return 0
    if any(w in lower for w in _URGENT_WORDS):
        return 2
    if any(w in lower for w in _SOON_WORDS):
        return 1
    return 0


def _tier_for(score: int) -> str:
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    if score >= 1:
        return "low"
    return "none"


def score_email(parsed: dict) -> tuple[int, str]:
    """Return (score, tier).

    Tier is taken from the LLM-supplied ``urgency`` when present, falling back
    to a heuristic over extracted tasks. Score is heuristic-only — used as a
    tie-breaker for sorting within a tier.
    """
    if not parsed or "error" in parsed:
        return 0, "none"
    tasks = parsed.get("action_items") or []
    score = 0
    for task in tasks:
        prio = (task.get("priority") or "").strip().lower()
        score += _PRIORITY_SCORES.get(prio, 1)
        score += _deadline_urgency(task.get("deadline") or "")

    llm_tier = (parsed.get("urgency") or "").strip().lower()
    if llm_tier in _VALID_TIERS:
        return score, llm_tier
    if not tasks:
        return 0, "none"
    return score, _tier_for(score)


def _truncate_body(body: str, max_words: int = MAX_EMAIL_WORDS) -> str:
    words = body.split()
    if len(words) <= max_words:
        return body
    return " ".join(words[:max_words]) + " …"


def _parse_triage_response(raw: str) -> dict:
    """Parse the LLM's JSON. Normalise to look like a tasks-workflow result
    (i.e. expose ``action_items``) so the rest of the UI keeps working.
    """
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"error": "Could not parse LLM response", "raw": raw[:200]}
    urgency = (data.get("urgency") or "none").strip().lower()
    if urgency not in _VALID_TIERS:
        urgency = "none"
    tasks_in = data.get("tasks") or []
    action_items = []
    for t in tasks_in[:5]:  # hard cap, model occasionally over-produces
        if not isinstance(t, dict):
            continue
        action_items.append({
            "task": (t.get("task") or "").strip(),
            "priority": (t.get("priority") or "medium").strip().lower(),
            "deadline": (t.get("deadline") or "not specified").strip(),
        })
    return {
        "urgency": urgency,
        "reason": (data.get("reason") or "").strip(),
        "action_items": action_items,
        "source_type": "actionable" if action_items else "non_actionable",
    }


def _analyse_email(email: dict) -> dict:
    """Triage a single email with one direct LLM call. Thread-safe."""
    subject = email.get("subject") or "(no subject)"
    body = _truncate_body(email.get("body", ""))
    text = clean_text(
        f"From: {email.get('sender', '')}\n"
        f"Subject: {subject}\n\n"
        f"{body}"
    )
    try:
        raw = route_llm(_triage_prompt(text), options=_TRIAGE_LLM_OPTIONS)
        parsed = _parse_triage_response(raw)
    except Exception as e:
        logger.warning(f"Auto-scan failed on '{subject}': {e}")
        parsed = {"error": str(e)}
    score, tier = score_email(parsed)
    return {"email": email, "result": parsed, "score": score, "tier": tier}


def run_auto_scan(
    window_hours: int = 12,
    max_emails: int = 15,
    account: Optional[str] = None,
    progress_callback: Optional[ProgressCallback] = None,
    cancel_check: Optional[CancelCheck] = None,
    max_workers: int = MAX_WORKERS,
) -> list[dict]:
    """Fetch recent emails and rank them by task urgency.

    Emails are analysed in parallel against the LLM (up to ``max_workers`` at a
    time). Progress arrives as each email completes, so the count is monotonic
    but the surfaced subject reflects the most-recently-completed email rather
    than a strict order.

    Returns a list (sorted by score desc) of:
        {"email": {...}, "result": {...}, "score": int, "tier": str}
    """
    query = f"newer_than:{window_hours}h"
    page = get_latest_emails(max_results=max_emails, account=account, query=query)
    emails = page["emails"]
    total = len(emails)

    if progress_callback:
        progress_callback(0, total, "")

    if not emails:
        return []

    results: list[dict] = []
    completed = 0
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        future_map = {executor.submit(_analyse_email, e): e for e in emails}
        for fut in as_completed(future_map):
            if cancel_check and cancel_check():
                break
            email = future_map[fut]
            try:
                results.append(fut.result())
            except Exception as e:
                subject = email.get("subject") or "(no subject)"
                logger.warning(f"Auto-scan future failed on '{subject}': {e}")
                results.append({
                    "email": email,
                    "result": {"error": str(e)},
                    "score": 0,
                    "tier": "none",
                })
            completed += 1
            if progress_callback:
                subject = email.get("subject") or "(no subject)"
                progress_callback(completed, total, subject)
    finally:
        # Don't block on in-flight LLM requests when the user cancels.
        executor.shutdown(wait=False, cancel_futures=True)

    results.sort(key=lambda r: r["score"], reverse=True)
    return results
