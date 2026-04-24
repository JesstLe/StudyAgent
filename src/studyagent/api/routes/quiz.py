from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.agents.quiz.agent import QuizAgent
from studyagent.api.schemas.quiz import QuizAttemptResponse, QuizGenerateRequest, QuizSubmitRequest
from studyagent.db.models import Flashcard, FlashcardDeck, QuizAttempt

router = APIRouter(prefix="/api/v1")


async def get_db():
    from studyagent.db.engine import create_session_factory

    factory = create_session_factory()
    async with factory() as session:
        yield session


@router.post("/quiz/generate")
async def generate_quiz(req: QuizGenerateRequest):
    agent = QuizAgent()
    questions = await agent.generate_quiz(
        concepts=req.concepts,
        difficulty=req.difficulty,
        count=req.count,
        quiz_types=req.quiz_types,
    )
    return {"questions": questions}


@router.post("/quiz/generate-and-save")
async def generate_and_save_quiz(req: QuizGenerateRequest, db: AsyncSession = Depends(get_db)):
    agent = QuizAgent()
    questions = await agent.generate_quiz(
        concepts=req.concepts,
        difficulty=req.difficulty,
        count=req.count,
        quiz_types=req.quiz_types,
    )

    deck = FlashcardDeck(
        id=str(uuid.uuid4()),
        user_id="default",
        title=f"Quiz: {', '.join(req.concepts[:3])}",
        source_type="quiz",
        card_count=len(questions),
    )
    db.add(deck)

    for q in questions:
        card = Flashcard(
            id=str(uuid.uuid4()),
            deck_id=deck.id,
            card_type=q.get("card_type", "multiple_choice"),
            front=q["front"],
            back=q["back"],
            options_json=json.dumps(q.get("options")) if q.get("options") else None,
            difficulty=q.get("difficulty", 0.5),
        )
        db.add(card)

    await db.commit()
    return {"deck_id": deck.id, "questions": questions}


@router.post("/quiz/submit", response_model=QuizAttemptResponse)
async def submit_quiz(req: QuizSubmitRequest, db: AsyncSession = Depends(get_db)):
    correct = sum(1 for a in req.answers if a.get("correct"))
    total = len(req.answers)
    score = correct / total if total > 0 else 0.0

    attempt = QuizAttempt(
        id=str(uuid.uuid4()),
        user_id="default",
        quiz_type=req.quiz_type,
        total_questions=total,
        correct_answers=correct,
        score=score,
        answers_json=json.dumps(req.answers),
    )
    db.add(attempt)
    await db.commit()

    return QuizAttemptResponse(
        id=attempt.id,
        quiz_type=attempt.quiz_type,
        total_questions=total,
        correct_answers=correct,
        score=score,
    )
