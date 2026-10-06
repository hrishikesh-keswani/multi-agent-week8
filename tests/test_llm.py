"""JSON repair accounting for the Ollama client."""

import time

import pytest

from underwriting.llm import LLMError, OllamaClient


def test_repair_time_and_tokens_stay_on_one_response():
    calls = {"n": 0}

    def transport(payload):
        calls["n"] += 1
        time.sleep(0.01)
        assert payload["think"] is False
        assert payload["format"] == "json"
        if calls["n"] == 1:
            return {
                "message": {"content": "not json"},
                "prompt_eval_count": 10,
                "eval_count": 3,
            }
        return {
            "message": {"content": '{"ok": true}'},
            "prompt_eval_count": 4,
            "eval_count": 2,
        }

    client = OllamaClient(transport=transport)
    started = time.perf_counter()
    result = client.complete(agent="intake", system="Return JSON.", user="hello")
    elapsed_ms = (time.perf_counter() - started) * 1000

    assert calls["n"] == 2
    assert result.content == {"ok": True}
    assert result.prompt_tokens == 14
    assert result.completion_tokens == 5
    assert result.duration_ms >= 20
    assert result.duration_ms <= elapsed_ms + 50


def test_valid_json_does_not_repair():
    calls = {"n": 0}

    def transport(payload):
        del payload
        calls["n"] += 1
        return {
            "message": {"content": '{"score": 12}'},
            "prompt_eval_count": 6,
            "eval_count": 1,
        }

    result = OllamaClient(transport=transport).complete(agent="risk_scoring", system="s", user="u")
    assert calls["n"] == 1
    assert result.prompt_tokens == 6
    assert result.completion_tokens == 1
    assert result.content == {"score": 12}


def test_second_invalid_body_raises_with_both_token_counts():
    def transport(payload):
        del payload
        return {
            "message": {"content": "still not json"},
            "prompt_eval_count": 8,
            "eval_count": 2,
        }

    with pytest.raises(LLMError) as caught:
        OllamaClient(transport=transport).complete(agent="intake", system="s", user="u")
    assert caught.value.prompt_tokens == 16
    assert caught.value.completion_tokens == 4
