import requests
from config import settings

def call_ollama(prompt: str, model: str = None) -> str:
    model = model or settings.OLLAMA_MODEL
    try:
        response = requests.post(
            settings.OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.9},
                "format": "json",
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Could not connect to Ollama at {settings.OLLAMA_URL}. "
            "Make sure Ollama is running (ollama serve)."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out after 60 seconds.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Ollama returned an error: {e}")
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Unexpected response from Ollama: {e}")
