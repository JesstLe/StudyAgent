from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ZPDResult:
    lower: float
    upper: float
    optimal: float
    is_in_zpd: bool
    recommendation: str


def estimate_zpd(
    learner_mastery: float,
    prerequisite_mastery: float,
    concept_difficulty: float,
) -> ZPDResult:
    lower = prerequisite_mastery * 0.7
    upper = min(prerequisite_mastery + 0.3, 1.0 - concept_difficulty * 0.2)
    upper = max(upper, lower + 0.1)
    upper = min(upper, 1.0)
    optimal = (lower + upper) / 2
    is_in_zpd = lower <= learner_mastery <= upper

    if learner_mastery < lower:
        recommendation = "prerequisite_gap"
    elif learner_mastery > upper:
        recommendation = "too_easy"
    else:
        recommendation = "optimal"

    return ZPDResult(
        lower=lower,
        upper=upper,
        optimal=optimal,
        is_in_zpd=is_in_zpd,
        recommendation=recommendation,
    )


def adapt_difficulty(zpd: ZPDResult, recent_accuracy: float) -> float:
    if recent_accuracy > 0.85:
        return min(zpd.upper, zpd.optimal + 0.1)
    elif recent_accuracy < 0.50:
        return max(zpd.lower, zpd.optimal - 0.1)
    return zpd.optimal
