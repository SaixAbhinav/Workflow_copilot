import json
import re


def extract_json(text: str) -> str | None:
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?\s*", "", text).strip()

    # Find the outermost balanced JSON object
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None

def parse_output(raw_output: str) -> dict:
    try:
        cleaned = extract_json(raw_output)
        if not cleaned:
            raise ValueError("No JSON found in LLM output")
        return json.loads(cleaned)
    except Exception:
        return {"error": "Failed to parse output", "raw": raw_output}
