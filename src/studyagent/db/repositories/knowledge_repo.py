from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.db.models import KnowledgeState


class KnowledgeRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: str, concept_id: str) -> KnowledgeState | None:
        stmt = select(KnowledgeState).where(
            KnowledgeState.user_id == user_id,
            KnowledgeState.concept_id == concept_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: str, concept_id: str) -> KnowledgeState:
        existing = await self.get(user_id, concept_id)
        if existing:
            return existing
        state = KnowledgeState(user_id=user_id, concept_id=concept_id)
        self._session.add(state)
        await self._session.flush()
        return state

    async def get_due_reviews(self, user_id: str, limit: int = 20) -> Sequence[KnowledgeState]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(KnowledgeState)
            .where(
                KnowledgeState.user_id == user_id,
                KnowledgeState.next_review_at <= now,
            )
            .order_by(KnowledgeState.next_review_at)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all_for_user(self, user_id: str) -> Sequence[KnowledgeState]:
        stmt = (
            select(KnowledgeState)
            .where(KnowledgeState.user_id == user_id)
            .order_by(KnowledgeState.mastery_level)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_bkt(self, user_id: str, concept_id: str, p_learned: float) -> KnowledgeState:
        state = await self.get_or_create(user_id, concept_id)
        now = datetime.now(timezone.utc)
        state.mastery_level = p_learned
        state.bkt_p_learned = p_learned
        state.total_assessments += 1
        state.last_assessed_at = now
        state.updated_at = now
        await self._session.flush()
        return state

    async def update_fsrs(
        self,
        user_id: str,
        concept_id: str,
        *,
        stability: float,
        difficulty: float,
        fsrs_state: str,
        reps: int,
        lapses: int,
        scheduled_days: int,
        next_review_at: datetime | None,
    ) -> KnowledgeState:
        state = await self.get_or_create(user_id, concept_id)
        now = datetime.now(timezone.utc)
        state.fsrs_stability = stability
        state.fsrs_difficulty = difficulty
        state.fsrs_state = fsrs_state
        state.fsrs_reps = reps
        state.fsrs_lapses = lapses
        state.fsrs_scheduled_days = scheduled_days
        state.last_review_at = now
        state.next_review_at = next_review_at
        state.updated_at = now
        await self._session.flush()
        return state
