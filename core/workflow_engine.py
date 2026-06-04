from typing import Callable, Optional

from config import settings
from core.llm_router import route_llm
from core.output_parser import parse_output
from core.prompt_manager import build_prompt
from input_processing.chunker import chunk_text
from utils.logger import get_logger

logger = get_logger(__name__)

ProgressCallback = Callable[[int, int], None]


def run_workflow(
    text: str,
    workflow: str = "summary",
    progress_callback: Optional[ProgressCallback] = None,
) -> dict:
    if not text or not text.strip():
        return {"error": "No input text provided"}

    # Compare workflow needs whole-document view — don't chunk
    if workflow == "compare":
        chunks = [text]
    else:
        chunks = chunk_text(text, max_words=settings.CHUNK_SIZE)

    total = len(chunks)
    if progress_callback:
        progress_callback(0, total)

    all_results = []
    for i, chunk in enumerate(chunks):
        try:
            prompt = build_prompt(chunk, workflow)
            raw_output = route_llm(prompt)
            parsed = parse_output(raw_output)
            if "error" not in parsed:
                all_results.append(parsed)
            else:
                logger.warning(f"Chunk {i} failed to parse: {parsed.get('raw', '')[:100]}")
        except Exception as e:
            logger.error(f"Chunk {i} raised an exception: {e}")
        if progress_callback:
            progress_callback(i + 1, total)

    if not all_results:
        return {"error": "All chunks failed to process. Check the provider is reachable."}

    return merge_results(all_results, workflow)


def merge_results(results: list[dict], workflow: str) -> dict:
    if workflow == "tasks":
        final: dict = {"action_items": [], "source_type": None}
    elif workflow == "insights":
        final = {"key_insights": []}
    elif workflow == "compare":
        final = {"summary": "", "common_themes": [], "differences": [], "key_insights": []}
    else:
        final = {"summary": []}

    for res in results:
        if workflow == "tasks":
            final["action_items"].extend(res.get("action_items", []))
            st = res.get("source_type")
            # Any non-actionable verdict from any chunk downgrades the whole doc.
            if st and final["source_type"] != "non_actionable":
                if st == "actionable":
                    final["source_type"] = final["source_type"] or "actionable"
                else:
                    final["source_type"] = "non_actionable"
        elif workflow == "insights":
            final["key_insights"].extend(res.get("key_insights", []))
        elif workflow == "compare":
            s = res.get("summary", "")
            # Compare uses prose; keep string concat.
            if isinstance(s, str) and s.strip():
                final["summary"] = (final["summary"] + " " + s).strip()
            elif isinstance(s, list):
                # Tolerate the model returning a list here too.
                final["summary"] = (final["summary"] + " " + " ".join(p for p in s if isinstance(p, str))).strip()
            final["common_themes"].extend(res.get("common_themes", []))
            final["differences"].extend(res.get("differences", []))
            final["key_insights"].extend(res.get("key_insights", []))
        else:
            s = res.get("summary")
            if isinstance(s, list):
                final["summary"].extend(p.strip() for p in s if isinstance(p, str) and p.strip())
            elif isinstance(s, str) and s.strip():
                # Backwards-compat: if a chunk returns prose, keep it as one bullet.
                final["summary"].append(s.strip())

    return final
