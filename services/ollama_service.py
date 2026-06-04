import requests

from config import settings

_DEFAULT_OPTIONS = {"temperature": 0.2, "top_p": 0.9}


def call_ollama(prompt: str, model: str = None, options: dict | None = None) -> str:
    model = model or settings.OLLAMA_MODEL
    merged_options = {**_DEFAULT_OPTIONS, **(options or {})}
    try:
        response = requests.post(
            settings.OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": merged_options,
                "format": "json",
                "keep_alive": "30m",
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Could not connect to Ollama at {settings.OLLAMA_URL}. "
            "Make sure Ollama is running (ollama serve)."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out after 300 seconds.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Ollama returned an error: {e}")
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Unexpected response from Ollama: {e}")
