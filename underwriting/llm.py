"""Local Ollama client and the timeout injector used by the failure path."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:8b"


class LLMError(Exception):
    """The model call failed after a JSON repair attempt.

    Token counts cover the original call and the repair call so a span that
    records this error does not drop the failed generation.
    """

    def __init__(self, message: str, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        super().__init__(message)
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


@dataclass
class LLMResponse:
    content: Dict[str, Any]
    prompt_tokens: int
    completion_tokens: int
    duration_ms: int


Transport = Callable[[Dict[str, Any]], Dict[str, Any]]


class OllamaClient:
    """Chat client. One complete() call may perform a single JSON repair."""

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        transport: Optional[Transport] = None,
        http_timeout: float = 180,
    ) -> None:
        self.model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
        self.host = (host or os.environ.get("OLLAMA_HOST", DEFAULT_HOST)).rstrip("/")
        self.transport = transport
        self.http_timeout = http_timeout

    def complete(self, *, agent: str, system: str, user: str) -> LLMResponse:
        del agent  # wrappers such as TimeoutInjectingClient read this name
        started = time.perf_counter()
        raw, prompt_tokens, completion_tokens = self._chat(system, user)
        parsed = _parse_object(raw)
        if parsed is None:
            repair_user = (
                "Your previous response was not a JSON object. "
                "Return only one JSON object and nothing else. Previous response:\n"
                + raw
            )
            raw, repair_prompt, repair_completion = self._chat(system, repair_user)
            prompt_tokens += repair_prompt
            completion_tokens += repair_completion
            parsed = _parse_object(raw)
            if parsed is None:
                raise LLMError(
                    "model returned invalid JSON after repair",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )
        duration_ms = int(round((time.perf_counter() - started) * 1000))
        return LLMResponse(
            content=parsed,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_ms=duration_ms,
        )

    def _chat(self, system: str, user: str) -> tuple:
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0},
        }
        if self.transport is not None:
            body = self.transport(payload)
        else:
            body = _post_json(self.host + "/api/chat", payload, self.http_timeout)
        message = body.get("message") or {}
        content = message.get("content") or ""
        prompt_tokens = int(body.get("prompt_eval_count") or 0)
        completion_tokens = int(body.get("eval_count") or 0)
        return content, prompt_tokens, completion_tokens


class TimeoutInjectingClient:
    """Raises TimeoutError on one agent's underlying complete() call."""

    def __init__(self, inner: Any, fail_agent: str = "risk_scoring") -> None:
        self.inner = inner
        self.fail_agent = fail_agent

    def complete(self, *, agent: str, system: str, user: str) -> LLMResponse:
        if agent == self.fail_agent:
            raise TimeoutError("simulated upstream timeout")
        return self.inner.complete(agent=agent, system=system, user=user)


def ollama_ready(host: Optional[str] = None, model: Optional[str] = None) -> bool:
    host = (host or os.environ.get("OLLAMA_HOST", DEFAULT_HOST)).rstrip("/")
    model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    try:
        body = _post_json(host + "/api/tags", None, 3, method="GET")
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, LLMError):
        return False
    names = [item.get("name") for item in body.get("models") or []]
    return model in names


def _parse_object(raw: str) -> Optional[Dict[str, Any]]:
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _post_json(
    url: str,
    payload: Optional[dict],
    timeout: float,
    method: str = "POST",
) -> Dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError("ollama HTTP {0}: {1}".format(exc.code, detail)) from exc
