from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.agents.scheduler.agent import SchedulerAgent
from studyagent.api.schemas.review import (
    CardResponse,
    DeckCreate,
    DeckResponse,
    ReviewResultResponse,
    ReviewSubmit,
)
from studyagent.db.repositories import FlashcardRepo, KnowledgeRepo

router = APIRouter(prefix="/api/v1")


async def get_db():
    from studyagent.db.engine import create_session_factory

    factory = create_session_factory()
    async with factory() as session:
        yield session


@router.post("/decks", response_model=DeckResponse)
async def create_deck(req: DeckCreate, db: AsyncSession = Depends(get_db)):
    repo = FlashcardRepo(db)
    deck = await repo.create_deck(
        user_id="default",
        title=req.title,
        description=req.description,
        conversation_id=req.conversation_id,
    )
    await db.commit()
    return DeckResponse(
        id=deck.id, title=deck.title, description=deck.description,
        card_count=deck.card_count, created_at=deck.created_at.isoformat(),
    )


@router.get("/decks", response_model=list[DeckResponse])
async def list_decks(db: AsyncSession = Depends(get_db)):
    repo = FlashcardRepo(db)
    decks = await repo.list_decks("default")
    return [
        DeckResponse(
            id=d.id, title=d.title, description=d.description,
            card_count=d.card_count, created_at=d.created_at.isoformat(),
        )
        for d in decks
    ]


@router.get("/decks/{deck_id}/cards", response_model=list[CardResponse])
async def get_deck_cards(deck_id: str, db: AsyncSession = Depends(get_db)):
    repo = FlashcardRepo(db)
    cards = await repo.get_deck_cards(deck_id)
    return [
        CardResponse(
            id=c.id, card_type=c.card_type, front=c.front, back=c.back,
            extra=c.extra, options=json.loads(c.options_json) if c.options_json else None,
            concept_id=c.concept_id, difficulty=c.difficulty, fsrs_state=c.fsrs_state,
        )
        for c in cards
    ]


@router.get("/decks/{deck_id}/due", response_model=list[CardResponse])
async def get_due_cards(deck_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    f_repo = FlashcardRepo(db)
    cards = await f_repo.get_due_cards(deck_id, limit)
    return [
        CardResponse(
            id=c.id, card_type=c.card_type, front=c.front, back=None,
            extra=c.extra, options=json.loads(c.options_json) if c.options_json else None,
            concept_id=c.concept_id, difficulty=c.difficulty, fsrs_state=c.fsrs_state,
        )
        for c in cards
    ]


@router.get("/reviews/due", response_model=list[CardResponse])
async def get_due_reviews(limit: int = 20, db: AsyncSession = Depends(get_db)):
    k_repo = KnowledgeRepo(db)
    scheduler = SchedulerAgent()
    states = await scheduler.get_due_reviews(k_repo, "default", limit)
    results = []
    for s in states:
        from studyagent.db.repositories import ConceptRepo
        c_repo = ConceptRepo(db)
        concept = await c_repo.get_by_id(s.concept_id)
        results.append(CardResponse(
            id=s.id, card_type="review", front=concept.name if concept else "Review",
            back=concept.description if concept else None,
            concept_id=s.concept_id, difficulty=0.5, fsrs_state=s.fsrs_state,
        ))
    return results


@router.post("/reviews/submit", response_model=ReviewResultResponse)
async def submit_review(req: ReviewSubmit, db: AsyncSession = Depends(get_db)):
    k_repo = KnowledgeRepo(db)
    f_repo = FlashcardRepo(db)
    scheduler = SchedulerAgent()
    result = await scheduler.submit_review(
        k_repo, f_repo,
        user_id="default",
        concept_id=req.concept_id,
        card_id=req.card_id,
        grade=req.grade,
    )
    await db.commit()
    return ReviewResultResponse(**result)
