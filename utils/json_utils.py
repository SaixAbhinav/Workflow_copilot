import json

def safe_loads(text: str) -> dict | None:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

def pretty(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
