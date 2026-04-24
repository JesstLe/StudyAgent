from __future__ import annotations

from datetime import datetime, timezone

from studyagent.core.algorithms.scheduler import CardState, SpacedRepetitionScheduler
from studyagent.db.repositories.flashcard_repo import FlashcardRepo
from studyagent.db.repositories.knowledge_repo import KnowledgeRepo


class SchedulerAgent:
    def __init__(self, desired_retention: float = 0.9):
        self._fsrs = SpacedRepetitionScheduler(desired_retention=desired_retention)

    async def get_due_reviews(self, knowledge_repo: KnowledgeRepo, user_id: str, limit: int = 20):
        return await knowledge_repo.get_due_reviews(user_id, limit)

    async def get_due_flashcards(self, flashcard_repo: FlashcardRepo, deck_id: str, limit: int = 20):
        return await flashcard_repo.get_due_cards(deck_id, limit)

    async def submit_review(
        self,
        knowledge_repo: KnowledgeRepo,
        flashcard_repo: FlashcardRepo | None,
        *,
        user_id: str,
        concept_id: str,
        card_id: str | None,
        grade: int,
    ) -> dict:
        now = datetime.now(timezone.utc)

        knowledge = await knowledge_repo.get_or_create(user_id, concept_id)
        card_state = CardState(
            stability=knowledge.fsrs_stability,
            difficulty=knowledge.fsrs_difficulty,
            state=knowledge.fsrs_state,
            reps=knowledge.fsrs_reps,
            lapses=knowledge.fsrs_lapses,
            last_review=knowledge.last_review_at,
        )

        if knowledge.last_review_at is None:
            card_state = self._fsrs.new_card()

        result = self._fsrs.review(card_state, grade, now)

        await knowledge_repo.update_fsrs(
            user_id,
            concept_id,
            stability=result.card.stability,
            difficulty=result.card.difficulty,
            fsrs_state=result.card.state,
            reps=result.card.reps,
            lapses=result.card.lapses,
            scheduled_days=result.scheduled_days,
            next_review_at=result.next_due,
        )

        if card_id and flashcard_repo:
            await flashcard_repo.update_card_fsrs(
                card_id,
                fsrs_state=result.card.state,
                stability=result.card.stability,
                difficulty=result.card.difficulty,
                reps=result.card.reps,
                lapses=result.card.lapses,
                scheduled_days=result.scheduled_days,
                next_review_at=result.next_due,
            )

        return {
            "concept_id": concept_id,
            "grade": grade,
            "scheduled_days": result.scheduled_days,
            "next_review": result.next_due.isoformat(),
            "retrievability": result.retrievability,
        }
