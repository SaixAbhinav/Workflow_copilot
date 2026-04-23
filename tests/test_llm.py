import pytest
from unittest.mock import patch, MagicMock
from core.llm_router import route_llm, set_provider, get_provider


def test_default_provider_is_ollama():
    set_provider("ollama")
    assert get_provider() == "ollama"


def test_set_provider_invalid_raises():
    with pytest.raises(ValueError):
        set_provider("groq")


@patch("core.llm_router.call_ollama")
def test_route_llm_calls_ollama(mock_ollama):
    mock_ollama.return_value = '{"summary": "test"}'
    set_provider("ollama")
    result = route_llm("test prompt")
    mock_ollama.assert_called_once_with("test prompt")
    assert result == '{"summary": "test"}'


@patch("services.ollama_service.requests.post")
def test_ollama_service_returns_response(mock_post):
    from services.ollama_service import call_ollama
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": '{"summary": "ok"}'}
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    result = call_ollama("hello")
    assert result == '{"summary": "ok"}'


@patch("services.ollama_service.requests.post")
def test_ollama_service_raises_on_connection_error(mock_post):
    import requests
    from services.ollama_service import call_ollama
    mock_post.side_effect = requests.exceptions.ConnectionError()
    with pytest.raises(RuntimeError, match="Could not connect"):
        call_ollama("hello")
