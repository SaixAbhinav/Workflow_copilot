from core.prompt_manager import build_prompt
from core.llm_router import route_llm
from core.output_parser import parse_output
from input_processing.chunker import chunk_text
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def run_workflow(text: str, workflow: str = "summary") -> dict:
    if not text or not text.strip():
        return {"error": "No input text provided"}

    # Compare workflow needs whole-document view — don't chunk
    if workflow == "compare":
        chunks = [text]
    else:
        chunks = chunk_text(text, max_words=settings.CHUNK_SIZE)

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
        final = {"summary": ""}

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
            s = res.get("summary", "").strip()
            if s:
                final["summary"] = (final["summary"] + " " + s).strip()
            final["common_themes"].extend(res.get("common_themes", []))
            final["differences"].extend(res.get("differences", []))
            final["key_insights"].extend(res.get("key_insights", []))
        else:
            s = res.get("summary", "").strip()
            if s:
                final["summary"] = (final["summary"] + " " + s).strip()

    return final
