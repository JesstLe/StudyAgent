from studyagent.core.knowledge_tracing.zpd import ZPDResult, adapt_difficulty, estimate_zpd


def test_zpd_optimal_range():
    result = estimate_zpd(learner_mastery=0.5, prerequisite_mastery=0.7, concept_difficulty=0.3)
    assert result.lower < result.upper
    assert result.optimal > 0.0
    assert 0.0 <= result.lower <= 1.0
    assert 0.0 <= result.upper <= 1.0


def test_zpd_in_zone():
    # Learner at 0.5, prerequisites at 0.8 => lower=0.56, upper=0.94 => 0.5 < 0.56, so NOT in zone
    # Use mastery within ZPD range instead
    result = estimate_zpd(learner_mastery=0.7, prerequisite_mastery=0.8, concept_difficulty=0.3)
    assert result.is_in_zpd is True
    assert result.recommendation == "optimal"


def test_zpd_too_easy():
    result = estimate_zpd(learner_mastery=0.99, prerequisite_mastery=0.9, concept_difficulty=0.1)
    assert result.recommendation == "too_easy"


def test_zpd_prerequisite_gap():
    # mastery=0.05, prereq=0.1 => lower=0.07 => 0.05 < 0.07 => prerequisite_gap
    result = estimate_zpd(learner_mastery=0.05, prerequisite_mastery=0.1, concept_difficulty=0.7)
    assert result.recommendation == "prerequisite_gap"


def test_adapt_difficulty_too_easy():
    zpd = ZPDResult(lower=0.3, upper=0.7, optimal=0.5, is_in_zpd=True, recommendation="optimal")
    result = adapt_difficulty(zpd, recent_accuracy=0.9)
    assert result > zpd.optimal


def test_adapt_difficulty_too_hard():
    zpd = ZPDResult(lower=0.3, upper=0.7, optimal=0.5, is_in_zpd=True, recommendation="optimal")
    result = adapt_difficulty(zpd, recent_accuracy=0.4)
    assert result < zpd.optimal


def test_adapt_difficulty_just_right():
    zpd = ZPDResult(lower=0.3, upper=0.7, optimal=0.5, is_in_zpd=True, recommendation="optimal")
    result = adapt_difficulty(zpd, recent_accuracy=0.7)
    assert result == zpd.optimal


def test_zpd_upper_bounded():
    result = estimate_zpd(learner_mastery=0.9, prerequisite_mastery=0.95, concept_difficulty=0.1)
    assert result.upper <= 1.0
