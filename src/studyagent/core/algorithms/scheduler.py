from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone

from fsrs import Card, Rating, Scheduler, State


@dataclass(frozen=True)
class CardState:
    stability: float = 0.0
    difficulty: float = 0.0
    state: str = "New"
    step: int = 0
    reps: int = 0
    lapses: int = 0
    elapsed_days: int = 0
    scheduled_days: int = 0
    last_review: datetime | None = None
    due: datetime | None = None


@dataclass(frozen=True)
class ReviewResult:
    card: CardState
    next_due: datetime
    scheduled_days: int
    retrievability: float


class SpacedRepetitionScheduler:
    def __init__(self, desired_retention: float = 0.9):
        self._scheduler = Scheduler(desired_retention=desired_retention)

    def review(self, card_state: CardState, grade: int, now: datetime | None = None) -> ReviewResult:
        now = now or datetime.now(timezone.utc)
        fsrs_card = self._to_fsrs_card(card_state)
        rating = Rating(grade)

        updated_card, _review_log = self._scheduler.review_card(fsrs_card, rating, now)

        retrievability = self._scheduler.get_card_retrievability(updated_card)

        new_state = self._from_fsrs_card(updated_card, card_state.reps + 1, card_state.lapses + (1 if grade == 1 else 0))

        return ReviewResult(
            card=new_state,
            next_due=updated_card.due,
            scheduled_days=self._calc_scheduled_days(updated_card, now),
            retrievability=retrievability,
        )

    def new_card(self) -> CardState:
        return CardState()

    def _to_fsrs_card(self, state: CardState) -> Card:
        card = Card()
        if state.state != "New" and state.last_review is not None:
            card.stability = state.stability
            card.difficulty = state.difficulty
            card.due = state.due or datetime.now(timezone.utc)
            card.last_review = state.last_review
            state_map = {"Learning": State.Learning, "Review": State.Review, "Relearning": State.Relearning}
            card.state = state_map.get(state.state, State.Learning)
            card.step = state.step
        return card

    def _from_fsrs_card(self, card: Card, reps: int, lapses: int) -> CardState:
        state_names = {State.Learning: "Learning", State.Review: "Review", State.Relearning: "Relearning"}
        return CardState(
            stability=card.stability or 0.0,
            difficulty=card.difficulty or 0.0,
            state=state_names.get(card.state, "New"),
            step=card.step,
            reps=reps,
            lapses=lapses,
            last_review=card.last_review,
            due=card.due,
        )

    def _calc_scheduled_days(self, card: Card, now: datetime) -> int:
        if card.last_review and card.due:
            delta = card.due - card.last_review
            return max(0, int(delta.total_seconds() / 86400))
        return 0
