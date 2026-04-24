from pydantic import BaseModel


class QuizGenerateRequest(BaseModel):
    concepts: list[str]
    difficulty: float = 0.5
    count: int = 5
    quiz_types: list[str] | None = None


class QuizSubmitRequest(BaseModel):
    answers: list[dict]  # [{card_id, answer, correct}]
    quiz_type: str = "adaptive"


class QuizAttemptResponse(BaseModel):
    id: str
    quiz_type: str
    total_questions: int
    correct_answers: int
    score: float | None
