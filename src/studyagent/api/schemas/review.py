from pydantic import BaseModel


class DeckCreate(BaseModel):
    title: str
    description: str | None = None
    conversation_id: str | None = None


class DeckResponse(BaseModel):
    id: str
    title: str
    description: str | None
    card_count: int
    created_at: str


class CardResponse(BaseModel):
    id: str
    card_type: str
    front: str
    back: str | None = None
    extra: str | None = None
    options: list[dict] | None = None
    concept_id: str | None = None
    difficulty: float
    fsrs_state: str


class ReviewSubmit(BaseModel):
    grade: int  # 1=Again, 2=Hard, 3=Good, 4=Easy
    concept_id: str
    card_id: str | None = None


class ReviewResultResponse(BaseModel):
    concept_id: str
    grade: int
    scheduled_days: int
    next_review: str
    retrievability: float
