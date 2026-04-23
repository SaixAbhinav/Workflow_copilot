from services.ollama_service import call_ollama

_PROVIDER = "ollama"


def set_provider(provider: str):
    global _PROVIDER
    if provider != "ollama":
        raise ValueError(f"Unknown provider: {provider}")
    _PROVIDER = provider


def get_provider() -> str:
    return _PROVIDER


def route_llm(prompt: str) -> str:
    return call_ollama(prompt)
