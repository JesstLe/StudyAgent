from datetime import datetime, timezone

from studyagent.core.algorithms.scheduler import CardState, SpacedRepetitionScheduler


def test_new_card():
    s = SpacedRepetitionScheduler()
    card = s.new_card()
    assert card.state == "New"
    assert card.stability == 0.0
    assert card.reps == 0


def test_first_review_good():
    s = SpacedRepetitionScheduler()
    card = s.new_card()
    result = s.review(card, 3)  # Good
    assert result.card.state == "Learning"
    assert result.card.reps == 1
    assert result.scheduled_days >= 0


def test_first_review_easy():
    s = SpacedRepetitionScheduler()
    card = s.new_card()
    result = s.review(card, 4)  # Easy
    assert result.card.state == "Review"
    assert result.card.reps == 1


def test_review_again_counts_lapse():
    s = SpacedRepetitionScheduler()
    card = s.new_card()
    # First review with Good to graduate from learning
    r1 = s.review(card, 3)
    # Then review with Again (lapse)
    r2 = s.review(r1.card, 1)
    assert r2.card.lapses == 1


def test_multi_review_increases_interval():
    s = SpacedRepetitionScheduler()
    card = s.new_card()
    r1 = s.review(card, 3)  # Good -> Learning
    now = datetime.now(timezone.utc)
    r2 = s.review(r1.card, 3, now)  # Good -> should graduate to Review
    r3 = s.review(r2.card, 3, r2.next_due)  # Good again
    assert r3.scheduled_days >= r2.scheduled_days


def test_retrievability():
    s = SpacedRepetitionScheduler()
    card = s.new_card()
    result = s.review(card, 3)
    assert 0.0 <= result.retrievability <= 1.0


def test_state_persistence():
    s = SpacedRepetitionScheduler()
    card = s.new_card()
    r1 = s.review(card, 3)
    state = r1.card
    assert state.stability > 0.0
    assert state.last_review is not None
    # Verify state can be reconstructed
    assert state.state == "Learning"
