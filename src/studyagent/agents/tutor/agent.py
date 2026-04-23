from __future__ import annotations

from collections.abc import AsyncGenerator

from studyagent.agents.tutor.prompts import ADAPTIVE_PROMPT_TEMPLATE, CANONICAL_TUTOR_PROMPT
from studyagent.core.llm import LLMProvider


class TutorAgent:
    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm or LLMProvider()

    def build_system_prompt(
        self,
        session_type: str = "teaching",
        topics: str = "none yet",
    ) -> str:
        adaptive = ADAPTIVE_PROMPT_TEMPLATE.format(
            session_type=session_type,
            topics=topics,
        )
        return CANONICAL_TUTOR_PROMPT + adaptive

    async def respond(
        self,
        messages: list[dict[str, str]],
        session_type: str = "teaching",
        topics: str = "none yet",
    ) -> str:
        system = self.build_system_prompt(session_type, topics)
        return await self.llm.generate(messages=messages, system=system)

    async def stream(
        self,
        messages: list[dict[str, str]],
        session_type: str = "teaching",
        topics: str = "none yet",
    ) -> AsyncGenerator[str, None]:
        system = self.build_system_prompt(session_type, topics)
        async for token in self.llm.stream(messages=messages, system=system):
            yield token
