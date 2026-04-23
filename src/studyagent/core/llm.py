from __future__ import annotations

from collections.abc import AsyncGenerator

import litellm

from studyagent.core.config import LLMConfig


class LLMProvider:
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
        return model

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

        response = await litellm.acompletion(
            model=self._model_name(),
            messages=all_messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            api_key=self.config.api_key or None,
            api_base=self.config.base_url or None,
            stream=False,
        )
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

        response = await litellm.acompletion(
            model=self._model_name(),
            messages=all_messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            api_key=self.config.api_key or None,
            api_base=self.config.base_url or None,
            stream=True,
        )

        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
