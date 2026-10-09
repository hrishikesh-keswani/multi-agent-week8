"""Shared fixtures."""

import os

import pytest

from underwriting.llm import OllamaClient, ollama_ready


@pytest.fixture
def live_llm():
    if not ollama_ready():
        message = "local Ollama model is not available"
        if os.environ.get("REQUIRE_OLLAMA") == "1":
            pytest.fail(message)
        pytest.skip(message)
    return OllamaClient()
