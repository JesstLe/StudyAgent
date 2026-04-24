from __future__ import annotations

from collections.abc import AsyncGenerator

import litellm

from studyagent.core.config import LLMConfig


class LLMProvider:
    _EXTRA_HEADERS: dict[str, str] = {
        "User-Agent": "claude-code/1.0",
    }

    def __init__(self, config: LLMConfig | None = None):
        if config is None:
            from studyagent.core.config import load_config

            config = load_config().llm
        self.config = config

    def _model_name(self) -> str:
        provider = self.config.provider
        model = self.config.model
        if provider == "ollama":
            return f"ollama/{model}"
        if provider == "anthropic":
            return model if model.startswith("claude") else f"anthropic/{model}"
        if provider == "openai" and self.config.base_url:
            return f"openai/{model}"
        return model

    def _common_kwargs(self, **overrides: object) -> dict:
        kwargs: dict = {
            "model": self._model_name(),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "api_key": self.config.api_key or None,
            "api_base": self.config.base_url or None,
            "extra_headers": self._EXTRA_HEADERS,
        }
        kwargs.update(overrides)
        return {k: v for k, v in kwargs.items() if v is not None}

    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        all_messages: list[dict[str, str]] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        overrides: dict = {"messages": all_messages, "stream": False}
        if temperature is not None:
            overrides["temperature"] = temperature
        if max_tokens is not None:
            overrides["max_tokens"] = max_tokens

        response = await litellm.acompletion(**self._common_kwargs(**overrides))
        return response.choices[0].message.content or ""

    async def stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        all_messages: list[dict[str, str]] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        overrides: dict = {"messages": all_messages, "stream": True}
        if temperature is not None:
            overrides["temperature"] = temperature
        if max_tokens is not None:
            overrides["max_tokens"] = max_tokens

        response = await litellm.acompletion(**self._common_kwargs(**overrides))

        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
