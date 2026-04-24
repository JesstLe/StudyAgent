from pydantic import BaseModel


class ConceptCreate(BaseModel):
    name: str
    domain: str
    description: str | None = None
    difficulty: float = 0.5
    importance: float = 0.5
    tags: list[str] | None = None


class ConceptResponse(BaseModel):
    id: str
    name: str
    domain: str
    description: str | None
    difficulty: float
    importance: float
    mastery_level: float | None = None


class RelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    strength: float = 1.0


class KnowledgeStateResponse(BaseModel):
    concept_id: str
    concept_name: str
    mastery_level: float
    confidence: float
    fsrs_state: str
    next_review_at: str | None


class ExtractionRequest(BaseModel):
    messages: list[dict[str, str]]


class ExtractionResponse(BaseModel):
    concepts: list[dict]
    relations: list[dict]


class LearningPathRequest(BaseModel):
    goal: str


class LearningPathResponse(BaseModel):
    path: list[str]
