import json
import os

from dotenv import load_dotenv

load_dotenv()

# User-overridable preferences (persisted to config/user_prefs.json)
_PREFS_PATH = os.path.join(os.path.dirname(__file__), "user_prefs.json")


def _load_prefs() -> dict:
    if os.path.exists(_PREFS_PATH):
        try:
            with open(_PREFS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_prefs(prefs: dict):
    with open(_PREFS_PATH, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)
    _apply_prefs(prefs)


def _apply_prefs(prefs: dict):
    global OLLAMA_MODEL, CHUNK_SIZE
    OLLAMA_MODEL = prefs.get("ollama_model", OLLAMA_MODEL)
    CHUNK_SIZE = int(prefs.get("chunk_size", CHUNK_SIZE))


# Infrastructure / credentials from .env
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "client_secret.json")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Tunables with defaults — overridden by user_prefs.json if present
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))

_apply_prefs(_load_prefs())
