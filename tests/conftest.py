"""Shared fixtures."""

import pytest

from underwriting.llm import OllamaClient, ollama_ready


@pytest.fixture
def live_llm():
    if not ollama_ready():
        pytest.skip("local Ollama model qwen3:8b is not available")
    return OllamaClient()
