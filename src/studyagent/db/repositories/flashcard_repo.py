from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.db.models import Flashcard, FlashcardDeck


class FlashcardRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_deck(
        self,
        user_id: str,
        title: str,
        *,
        description: str | None = None,
        conversation_id: str | None = None,
        source_type: str = "ai_generated",
    ) -> FlashcardDeck:
        deck = FlashcardDeck(
            user_id=user_id,
            title=title,
            description=description,
            conversation_id=conversation_id,
            source_type=source_type,
        )
        self._session.add(deck)
        await self._session.flush()
        return deck

    async def get_deck(self, deck_id: str) -> FlashcardDeck | None:
        return await self._session.get(FlashcardDeck, deck_id)

    async def list_decks(self, user_id: str) -> Sequence[FlashcardDeck]:
        stmt = (
            select(FlashcardDeck)
            .where(FlashcardDeck.user_id == user_id)
            .order_by(FlashcardDeck.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_card(
        self,
        deck_id: str,
        card_type: str,
        front: str,
        back: str,
        *,
        concept_id: str | None = None,
        extra: str | None = None,
        options_json: str | None = None,
        difficulty: float = 0.5,
    ) -> Flashcard:
        card = Flashcard(
            deck_id=deck_id,
            card_type=card_type,
            front=front,
            back=back,
            concept_id=concept_id,
            extra=extra,
            options_json=options_json,
            difficulty=difficulty,
        )
        self._session.add(card)
        await self._session.flush()

        deck = await self._session.get(FlashcardDeck, deck_id)
        if deck:
            deck.card_count += 1
        await self._session.flush()
        return card

    async def get_card(self, card_id: str) -> Flashcard | None:
        return await self._session.get(Flashcard, card_id)

    async def get_due_cards(self, deck_id: str, limit: int = 20) -> Sequence[Flashcard]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Flashcard)
            .where(
                Flashcard.deck_id == deck_id,
                (Flashcard.next_review_at <= now) | (Flashcard.next_review_at.is_(None)),
            )
            .order_by(Flashcard.next_review_at)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_card_fsrs(
        self,
        card_id: str,
        *,
        fsrs_state: str,
        stability: float,
        difficulty: float,
        reps: int,
        lapses: int,
        scheduled_days: int,
        next_review_at: datetime | None,
    ) -> Flashcard | None:
        card = await self.get_card(card_id)
        if not card:
            return None
        now = datetime.now(timezone.utc)
        card.fsrs_state = fsrs_state
        card.fsrs_stability = stability
        card.fsrs_difficulty = difficulty
        card.fsrs_reps = reps
        card.fsrs_lapses = lapses
        card.fsrs_scheduled_days = scheduled_days
        card.next_review_at = next_review_at
        card.updated_at = now
        await self._session.flush()
        return card

    async def get_deck_cards(self, deck_id: str) -> Sequence[Flashcard]:
        stmt = (
            select(Flashcard)
            .where(Flashcard.deck_id == deck_id)
            .order_by(Flashcard.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
