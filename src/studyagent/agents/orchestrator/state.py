from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LearningState:
    user_id: str = "default"
    conversation_id: str | None = None
    messages: list[dict[str, str]] = field(default_factory=list)
    intent: str = "teach"
    session_type: str = "teaching"
    topics: str = ""
    response: str = ""
    extracted_concepts: list[dict] = field(default_factory=list)
    extracted_relations: list[dict] = field(default_factory=list)
    quiz_questions: list[dict] = field(default_factory=list)
    review_result: dict = field(default_factory=dict)
    analytics: dict = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
