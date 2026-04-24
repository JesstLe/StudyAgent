from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from studyagent.agents.tutor.agent import TutorAgent
from studyagent.core.llm import LLMProvider


EXTRACTION_PROMPT = """You are a CS concept extractor. Given a conversation between a tutor and student, extract:

1. **Concepts** discussed — each with a name, domain, difficulty (0-1), and one-line description.
2. **Relations** between concepts — with type (prerequisite, builds_on, related, part_of, contrasts_with).

Domains: data_structures, algorithms, os, networks, programming_languages, compilers, databases, distributed_systems, math, architecture

Return ONLY valid JSON in this exact format:
{
  "concepts": [
    {"name": "B-tree", "domain": "data_structures", "difficulty": 0.6, "description": "Balanced tree optimized for disk I/O"}
  ],
  "relations": [
    {"source": "B-tree", "target": "Binary Search Tree", "type": "builds_on"}
  ]
}

Be precise with concept names. Only include real, well-defined CS concepts. If nothing meaningful was discussed, return empty arrays."""

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
        conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        response = await self._llm.generate(
            messages=[{"role": "user", "content": conversation_text}],
            system=EXTRACTION_PROMPT,
            temperature=0.1,
            max_tokens=2000,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
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
