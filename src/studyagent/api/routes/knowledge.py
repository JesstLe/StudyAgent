from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.agents.knowledge_graph.agent import KnowledgeGraphAgent
from studyagent.api.schemas.knowledge import (
    ConceptCreate,
    ConceptResponse,
    ExtractionRequest,
    ExtractionResponse,
    KnowledgeStateResponse,
    LearningPathRequest,
    LearningPathResponse,
    RelationCreate,
)
from studyagent.db.models import Concept
from studyagent.db.repositories import ConceptRepo, KnowledgeRepo

router = APIRouter(prefix="/api/v1")


async def get_db():
    from studyagent.db.engine import create_session_factory

    factory = create_session_factory()
    async with factory() as session:
        yield session


@router.post("/concepts", response_model=ConceptResponse)
async def create_concept(req: ConceptCreate, db: AsyncSession = Depends(get_db)):
    repo = ConceptRepo(db)
    concept = await repo.create(
        name=req.name,
        domain=req.domain,
        description=req.description,
        difficulty=req.difficulty,
        importance=req.importance,
    )
    await db.commit()
    return ConceptResponse(
        id=concept.id,
        name=concept.name,
        domain=concept.domain,
        description=concept.description,
        difficulty=concept.difficulty,
        importance=concept.importance,
    )


@router.get("/concepts", response_model=list[ConceptResponse])
async def list_concepts(domain: str | None = None, db: AsyncSession = Depends(get_db)):
    repo = ConceptRepo(db)
    if domain:
        concepts = await repo.list_by_domain(domain)
    else:
        concepts = await repo.list_all()
    return [
        ConceptResponse(
            id=c.id, name=c.name, domain=c.domain,
            description=c.description, difficulty=c.difficulty, importance=c.importance,
        )
        for c in concepts
    ]


@router.get("/concepts/{concept_id}", response_model=ConceptResponse)
async def get_concept(concept_id: str, db: AsyncSession = Depends(get_db)):
    repo = ConceptRepo(db)
    concept = await repo.get_by_id(concept_id)
    if not concept:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Concept not found")
    return ConceptResponse(
        id=concept.id, name=concept.name, domain=concept.domain,
        description=concept.description, difficulty=concept.difficulty, importance=concept.importance,
    )


@router.post("/concepts/relations")
async def create_relation(req: RelationCreate, db: AsyncSession = Depends(get_db)):
    repo = ConceptRepo(db)
    relation = await repo.add_relation(
        source_id=req.source_id, target_id=req.target_id,
        relation_type=req.relation_type, strength=req.strength,
    )
    await db.commit()
    return {"id": relation.id, "source_id": req.source_id, "target_id": req.target_id, "type": req.relation_type}


@router.post("/concepts/extract", response_model=ExtractionResponse)
async def extract_concepts(req: ExtractionRequest):
    agent = KnowledgeGraphAgent()
    result = await agent.extract_concepts(req.messages)
    return ExtractionResponse(**result)


@router.get("/knowledge/{user_id}", response_model=list[KnowledgeStateResponse])
async def get_knowledge_state(user_id: str, db: AsyncSession = Depends(get_db)):
    k_repo = KnowledgeRepo(db)
    c_repo = ConceptRepo(db)
    states = await k_repo.get_all_for_user(user_id)
    result = []
    for s in states:
        concept = await c_repo.get_by_id(s.concept_id)
        result.append(KnowledgeStateResponse(
            concept_id=s.concept_id,
            concept_name=concept.name if concept else "unknown",
            mastery_level=s.mastery_level,
            confidence=s.confidence,
            fsrs_state=s.fsrs_state,
            next_review_at=s.next_review_at.isoformat() if s.next_review_at else None,
        ))
    return result


@router.post("/learning-path", response_model=LearningPathResponse)
async def suggest_learning_path(req: LearningPathRequest, db: AsyncSession = Depends(get_db)):
    c_repo = ConceptRepo(db)
    k_repo = KnowledgeRepo(db)
    agent = KnowledgeGraphAgent()

    concepts = await c_repo.list_all()
    states = await k_repo.get_all_for_user("default")
    knowledge_map = {}
    for s in states:
        concept = await c_repo.get_by_id(s.concept_id)
        if concept:
            knowledge_map[concept.name] = s.mastery_level

    concepts_data = [{"name": c.name, "domain": c.domain, "difficulty": c.difficulty} for c in concepts]
    relations_data = []

    path = await agent.suggest_learning_path(concepts_data, relations_data, knowledge_map, req.goal)
    return LearningPathResponse(path=path)
