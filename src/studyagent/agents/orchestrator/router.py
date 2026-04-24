from __future__ import annotations

from studyagent.core.llm import LLMProvider

ROUTING_PROMPT = """Classify the user's intent into exactly one category:

- "teach" — User wants to learn, understand, or review a CS concept (asking "what is", "explain", "how does", "why")
- "quiz" — User wants to test themselves (asking for quiz, test, practice problems, "test me")
- "review" — User wants to review flashcards (asking for review, flashcards, spaced repetition)
- "analyze" — User wants to see their progress/analytics (asking about mastery, progress, weak areas, statistics)
- "explore" — User wants to explore the knowledge graph (asking about prerequisites, learning path, concept relationships)

Reply with ONLY the category name, nothing else."""

INTENT_KEYWORDS: dict[str, list[str]] = {
    "quiz": ["quiz", "test me", "practice", "exam", "question", "测验", "测试", "考试"],
    "review": ["review", "flashcard", "复习", "闪卡", "间隔"],
    "analyze": ["progress", "mastery", "statistics", "analytics", "weak", "进度", "掌握", "统计"],
    "explore": ["prerequisite", "learning path", "knowledge graph", "先修", "学习路径", "知识图谱"],
}


class IntentRouter:
    def __init__(self, llm: LLMProvider | None = None):
        self._llm = llm

    def classify_by_keywords(self, message: str) -> str | None:
        lower = message.lower()
        for intent, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    return intent
        return None

    async def classify(self, message: str) -> str:
        keyword_result = self.classify_by_keywords(message)
        if keyword_result:
            return keyword_result

        if self._llm:
            response = await self._llm.generate(
                messages=[{"role": "user", "content": message}],
                system=ROUTING_PROMPT,
                temperature=0.0,
                max_tokens=10,
            )
            intent = response.strip().lower()
            valid = {"teach", "quiz", "review", "analyze", "explore"}
            return intent if intent in valid else "teach"

        return "teach"
