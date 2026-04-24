from __future__ import annotations

import json

from studyagent.core.llm import LLMProvider


QUIZ_GENERATION_PROMPT = """You are a CS quiz generator. Generate quiz questions for the given concepts at the specified difficulty level.

Concepts: {concepts}
Difficulty level: {difficulty} (0.0=easy, 1.0=hard)
Quiz types to generate: {quiz_types}

Generate exactly {count} questions. Return ONLY valid JSON:
[
  {{
    "card_type": "multiple_choice",
    "front": "question text",
    "back": "correct answer explanation",
    "options": [
      {{"label": "A", "text": "option text", "is_correct": false}},
      {{"label": "B", "text": "correct option", "is_correct": true}},
      {{"label": "C", "text": "option text", "is_correct": false}},
      {{"label": "D", "text": "option text", "is_correct": false}}
    ],
    "concept": "concept name",
    "difficulty": 0.5
  }}
]

Card types available:
- multiple_choice: standard MCQ with 4 options
- cloze: fill-in-the-blank (front has ___ placeholder, back has answer)
- code_output: predict what code prints (front has code, back has output)
- explain_concept: open-ended explanation prompt

Match difficulty: easy questions test basic recall, medium test understanding, hard test application/analysis.
Each question must be factually correct and unambiguous."""


class QuizAgent:
    def __init__(self, llm: LLMProvider | None = None):
        self._llm = llm or LLMProvider()

    async def generate_quiz(
        self,
        concepts: list[str],
        difficulty: float = 0.5,
        count: int = 5,
        quiz_types: list[str] | None = None,
    ) -> list[dict]:
        quiz_types = quiz_types or ["multiple_choice", "cloze", "code_output"]
        prompt = QUIZ_GENERATION_PROMPT.format(
            concepts=", ".join(concepts),
            difficulty=f"{difficulty:.1f}",
            quiz_types=", ".join(quiz_types),
            count=count,
        )
        response = await self._llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000,
        )
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                result = json.loads(response[start:end])
            else:
                result = []

        if not isinstance(result, list):
            return []

        for item in result:
            item.setdefault("card_type", "multiple_choice")
            item.setdefault("difficulty", difficulty)
        return result
