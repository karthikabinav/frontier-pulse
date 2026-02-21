from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass
class InferenceRequest:
    prompt: str
    model: str
    temperature: float = 0.35


@dataclass
class InferenceResult:
    text: str
    provider: str
    model: str


class InferenceClient(Protocol):
    def generate(self, payload: InferenceRequest) -> InferenceResult:
        ...


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def generate(self, payload: InferenceRequest) -> InferenceResult:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": payload.model,
                "prompt": payload.prompt,
                "stream": False,
                "options": {"temperature": payload.temperature},
            },
            timeout=120,
        )
        response.raise_for_status()
        body = response.json()
        return InferenceResult(
            text=body.get("response", ""),
            provider="ollama",
            model=payload.model,
        )


class OpenRouterClient:
    def __init__(self, api_key: str, model: str, base_url: str = "https://openrouter.ai/api/v1") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, payload: InferenceRequest) -> InferenceResult:
        if not self.api_key:
            raise ValueError("OpenRouter API key is required when cloud fallback is enabled")

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": payload.prompt}],
                "temperature": payload.temperature,
            },
            timeout=120,
        )
        response.raise_for_status()
        body = response.json()
        text = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        return InferenceResult(text=text, provider="openrouter", model=self.model)


class FailoverInferenceClient:
    """Local-first inference with optional cloud fallback."""

    def __init__(
        self,
        primary_client: InferenceClient,
        fallback_client: InferenceClient | None = None,
    ) -> None:
        self.primary_client = primary_client
        self.fallback_client = fallback_client

    def generate(self, payload: InferenceRequest) -> InferenceResult:
        try:
            return self.primary_client.generate(payload)
        except Exception:
            if not self.fallback_client:
                raise
            return self.fallback_client.generate(payload)
