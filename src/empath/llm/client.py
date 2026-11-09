"""Pembungkus tipis google-genai. Satu client per proses."""
from __future__ import annotations

import logging
from collections.abc import Iterator

from google import genai
from google.genai import types

from empath.config import settings

log = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str | None = None) -> None:
        self._client = genai.Client(api_key=api_key or settings.gemini_api_key)

    def stream(
        self,
        contents: list[dict],
        system_instruction: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        stream = self._client.models.generate_content_stream(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature if temperature is not None else settings.temperature,
                max_output_tokens=max_tokens or settings.max_output_tokens,
            ),
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text

    def complete(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 220) -> str:
        response = self._client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return (response.text or "").strip()