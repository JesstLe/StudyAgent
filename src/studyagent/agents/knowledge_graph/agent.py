from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from studyagent.agents.tutor.agent import TutorAgent
from studyagent.core.llm import LLMProvider


EXTRACTION_INSTRUCTION = """Extract CS concepts from this tutoring session. Return JSON:
{"concepts":[{"name":"...","domain":"os|data_structures|algorithms|networks|compilers|databases|distributed_systems|math|architecture","difficulty":0.5,"description":"..."}],"relations":[{"source":"...","target":"...","type":"prerequisite|builds_on|related|part_of|contrasts_with"}]}

Session:"""

MAX_EXTRACTION_CHARS = 600

LEARNING_PATH_PROMPT = """Given a set of CS concepts with prerequisite relations and a learner's current mastery levels, suggest an optimal learning path.

The learner wants to learn: {goal}

Current knowledge state:
{knowledge_state}

Available concepts and relations:
{concepts_data}

Return a JSON array of concept names in recommended learning order:
["concept1", "concept2", ...]

Only include concepts the learner hasn't mastered yet (mastery < 0.8). Place prerequisites before dependent concepts."""


class KnowledgeGraphAgent:
    def __init__(self, llm: LLMProvider | None = None):
        self._llm = llm or LLMProvider()

    async def extract_concepts(self, messages: list[dict[str, str]]) -> dict:
        conversation_text = "\n".join(
            f"{m['role']}: {m['content'][:300]}" for m in messages
        )
        if len(conversation_text) > MAX_EXTRACTION_CHARS:
            conversation_text = conversation_text[:MAX_EXTRACTION_CHARS]
        prompt = EXTRACTION_INSTRUCTION + "\n" + conversation_text
        response = ""
        for attempt in range(3):
            tokens: list[str] = []
            async for token in self._llm.stream(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000,
            ):
                tokens.append(token)
            response = "".join(tokens)
            if response.strip():
                break
            await asyncio.sleep(2)
        if not response.strip():
            return {"concepts": [], "relations": []}
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(response[start:end])
                except json.JSONDecodeError:
                    pass
            return {"concepts": [], "relations": []}

    async def suggest_learning_path(
        self,
        concepts: list[dict],
        relations: list[dict],
        knowledge_state: dict[str, float],
        goal: str,
    ) -> list[str]:
        concepts_data = json.dumps(
            {"concepts": concepts, "relations": relations}, ensure_ascii=False, indent=2
        )
        knowledge_text = "\n".join(
            f"  {name}: {mastery:.0%}" for name, mastery in knowledge_state.items()
        )
        prompt = LEARNING_PATH_PROMPT.format(
            goal=goal,
            knowledge_state=knowledge_text or "  (no prior knowledge)",
            concepts_data=concepts_data,
        )
        response = await self._llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
        )
        try:
            path = json.loads(response)
            if isinstance(path, list):
                return path
        except json.JSONDecodeError:
            pass
        start = response.find("[")
        end = response.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return []
