from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

import requests

from services.config import settings


class LLMClient(Protocol):
    def generate_text(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class GeminiClient:
    api_key: str
    model: str

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        resp = requests.post(
            url,
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()

        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini returned no candidates")

        content = (candidates[0].get("content") or {}).get("parts") or []
        if not content:
            raise ValueError("Gemini returned empty content")

        text = content[0].get("text")
        if not isinstance(text, str):
            raise ValueError("Gemini response text missing")

        return text


@dataclass(frozen=True)
class OpenRouterClient:
    api_key: str
    model: str
    base_url: str

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()

        choices = data.get("choices") or []
        if not choices:
            raise ValueError("OpenRouter returned no choices")

        message = (choices[0].get("message") or {}).get("content")
        if not isinstance(message, str):
            raise ValueError("OpenRouter response message missing")

        return message


def get_llm_client() -> LLMClient:
    if settings.llm_provider == "openrouter":
        return OpenRouterClient(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            base_url=settings.openrouter_base_url,
        )

    if settings.llm_provider == "gemini":
        return GeminiClient(api_key=settings.gemini_api_key, model=settings.gemini_model)

    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")


def ensure_json(text: str) -> str:
    text = text.strip()
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM output did not contain JSON")

    candidate = text[start : end + 1].strip()
    json.loads(candidate)
    return candidate
