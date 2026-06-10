from __future__ import annotations

from collections.abc import AsyncGenerator

from studyagent.agents.tutor.prompts import ADAPTIVE_PROMPT_TEMPLATE, CANONICAL_TUTOR_PROMPT
from studyagent.core.llm import LLMProvider
from studyagent.core.token_count import estimate_messages_tokens

MAX_CONTEXT_TOKENS = 250_000
KEEP_RECENT_TURNS = 4
MIN_MESSAGES_TO_SUMMARIZE = KEEP_RECENT_TURNS * 2 + 2

SUMMARY_PROMPT = """\
Summarize the following conversation between a student and a CS tutor.
Extract:
1. Topics discussed and key concepts taught
2. The student's questions and level of understanding
3. Key insights or analogies used by the tutor

Keep the summary concise (under 500 tokens) but preserve enough detail for continuity.

Conversation:
{conversation}
"""


class TutorAgent:
    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm or LLMProvider()
        self._summary_cache: dict[str, str] = {}

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
        conversation_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        system = self.build_system_prompt(session_type, topics)
        compacted = await self._maybe_compact(messages, conversation_id)
        async for token in self.llm.stream(messages=compacted, system=system):
            yield token

    async def _maybe_compact(
        self,
        messages: list[dict[str, str]],
        conversation_id: str | None,
    ) -> list[dict[str, str]]:
        total = estimate_messages_tokens(messages)
        if total < MAX_CONTEXT_TOKENS:
            return messages
        if len(messages) < MIN_MESSAGES_TO_SUMMARIZE:
            return messages

        old_count = len(messages) - KEEP_RECENT_TURNS * 2
        old_messages = messages[:old_count]
        recent_messages = messages[old_count:]

        conv_key = conversation_id or str(id(messages))
        if conv_key not in self._summary_cache:
            conversation_text = "\n".join(
                f"[{m['role']}]: {m['content']}" for m in old_messages
            )
            prompt = SUMMARY_PROMPT.format(conversation=conversation_text)
            summary = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800,
            )
            self._summary_cache[conv_key] = summary.strip()

        summary_text = self._summary_cache[conv_key]
        return [
            {
                "role": "system",
                "content": f"[Previous conversation summary]\n{summary_text}",
            },
            *recent_messages,
        ]
