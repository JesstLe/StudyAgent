# StudyAgent Learning Algorithms Specification

> Version: 1.0 | Date: 2026-04-23 | Status: Draft

## 1. Overview

This document provides the detailed mathematical specification for all learning algorithms used in StudyAgent. Each algorithm is defined with complete formulas, parameter values, and Python implementation guidance.

## 2. Spaced Repetition: FSRS-5

### 2.1 Algorithm Overview

FSRS-5 (Free Spaced Repetition Scheduler, version 5) is the core spaced repetition algorithm. It uses 19 trainable parameters based on the DSR (Difficulty-Stability-Retrievability) three-component memory model.

### 2.2 Core Formulas

#### Retrievability (Forgetting Curve)

The probability that a learner can recall an item at time t after last review:

```
R(t, S) = (1 + FACTOR * t / (9 * S))^(-DECAY)

Where:
  DECAY  = -0.5   (FSRS-5 default)
  FACTOR = 19/81  (FSRS-5 default, approximately 0.2346)
  t      = elapsed time since last review (days)
  S      = current stability (days)
```

This produces a power-law forgetting curve where retrievability decreases over time.

#### Initial Stability (First Review)

Four parameters define starting stability for each grade:
```
S0(Again) = w0 = 0.4072   (stability in days)
S0(Hard)  = w1 = 1.1829
S0(Good)  = w2 = 3.1262
S0(Easy)  = w3 = 15.4722
```

#### Initial Difficulty (First Review)

```
D0(G) = w4 - exp(w5 * (G - 1))    then clamp to [1, 10]

Where:
  w4 = 7.2102  (difficulty offset)
  w5 = 0.5316  (difficulty slope)
  G  = grade (1=Again, 2=Hard, 3=Good, 4=Easy)
```

#### Difficulty Update (Subsequent Reviews)

```
D'(D, G) = w6 * D0(G) + (1 - w6) * (D + w7) / 2    then clamp to [1, 10]

Where:
  w6 = 0.6631  (weight: new vs old difficulty)
  w7 = 0.0046  (linear damping, prevents extreme values)
```

#### Stability Update After Successful Recall

For grades 2 (Hard), 3 (Good), 4 (Easy):

```
S'_recall(D, S, R, G) = S * (
    e^(w8) * (11 - D) * S^(-w9) * (e^(w10 * (1 - R)) - 1) * w15
    + w16 * w17 * (e^(w10 * (1 - R)) - 1)
    + 1
)

Where:
  w8  = 1.5458   (stability increase base multiplier)
  w9  = 0.1962   (difficulty penalty on stability growth)
  w10 = 1.4025   (retrievability impact factor)
  w15 = 0.0035   (hard penalty coefficient)
  w16 = 0.5228   (easy bonus weight)
  w17 = 0.5937   (same-day review exponential factor)
```

#### Stability Update After Forgetting (Grade = Again)

```
S'_forget(D, S, R) = w11 * D^(-w12) * ((S + 1)^w13 - 1) * e^(w14 * (1 - R))

Where:
  w11 = 0.0234   (post-lapse base stability)
  w12 = 0.1020   (difficulty impact on post-lapse)
  w13 = 0.6089   (previous stability impact)
  w14 = 0.5302   (retrievability impact on post-lapse)
```

#### Same-Day Review (FSRS-5 Feature)

When reviewing a card again on the same day:
```
S'_sameday(S, G) = S * e^(w17 * (G - 3 + w18))

Where:
  w17 = 0.5937   (same-day exponential factor)
  w18 = 0.1382   (same-day offset)
```

### 2.3 Complete Default Parameters (19 values)

```
Index  Value    Description
w0     0.4072   Initial stability: Again
w1     1.1829   Initial stability: Hard
w2     3.1262   Initial stability: Good
w3    15.4722   Initial stability: Easy
w4     7.2102   Initial difficulty offset
w5     0.5316   Initial difficulty slope
w6     0.6631   Difficulty update weight
w7     0.0046   Difficulty linear damping
w8     1.5458   Stability increase multiplier
w9     0.1962   Difficulty penalty on stability
w10    1.4025   Retrievability impact
w11    0.0234   Post-lapse stability base
w12    0.1020   Post-lapse difficulty impact
w13    0.6089   Post-lapse previous stability impact
w14    0.5302   Post-lapse retrievability impact
w15    0.0035   Hard penalty
w16    0.5228   Easy bonus weight
w17    0.5937   Same-day review factor
w18    0.1382   Same-day review offset
```

### 2.4 Implementation

```python
from fsrs import FSRS, Rating, Card, ReviewLog
from datetime import datetime, timezone

fsrs = FSRS()  # Default parameters

def review_flashcard(card: Card, grade: int) -> Card:
    """Review a flashcard. grade: 1=Again, 2=Hard, 3=Good, 4=Easy."""
    rating = Rating(grade)
    now = datetime.now(timezone.utc)
    scheduling = fsrs.repeat(card, now)
    return scheduling[rating].card

def get_due_cards(user_id: str, limit: int = 20) -> list[Card]:
    """Get cards due for review."""
    # Query knowledge_state where next_review_at <= NOW()
    # Sort by next_review_at ASC (most overdue first)
    pass
```

## 3. Bayesian Knowledge Tracing (BKT)

### 3.1 Model

BKT uses a Hidden Markov Model with binary latent state (learned/not-learned).

#### Parameters

| Parameter | Name | Typical Range |
|-----------|------|---------------|
| P(L0) | Prior (initial knowledge) | 0.0 - 0.3 |
| P(T) | Transition (learning rate) | 0.05 - 0.3 |
| P(G) | Guess (correct without knowing) | 0.1 - 0.3 |
| P(S) | Slip (wrong despite knowing) | 0.01 - 0.1 |

#### Update Equations

After observing evidence E (correct=1, incorrect=0):

```
P(L|correct) = P(L) * (1 - P(S)) / [P(L) * (1 - P(S)) + (1 - P(L)) * P(G)]

P(L|incorrect) = P(L) * P(S) / [P(L) * P(S) + (1 - P(L)) * (1 - P(G))]

P(L)_next = P(L|E) + (1 - P(L|E)) * P(T)    [clamp to [0, 1]]
```

#### Prediction

```
P(correct) = P(L) * (1 - P(S)) + (1 - P(L)) * P(G)
```

### 3.2 Implementation

```python
@dataclass
class BKTModel:
    p_l0: float = 0.1
    p_transfer: float = 0.1
    p_guess: float = 0.2
    p_slip: float = 0.1

    def update(self, p_learned: float, correct: bool) -> float:
        if correct:
            p_evidence = p_learned * (1 - self.p_slip) + \
                         (1 - p_learned) * self.p_guess
            p_l_given_e = p_learned * (1 - self.p_slip) / p_evidence
        else:
            p_evidence = p_learned * self.p_slip + \
                         (1 - p_learned) * (1 - self.p_guess)
            p_l_given_e = p_learned * self.p_slip / p_evidence

        return min(1.0, p_l_given_e + (1 - p_l_given_e) * self.p_transfer)
```

## 4. Zone of Proximal Development (ZPD)

### 4.1 Estimation

```python
def estimate_zpd(
    learner_mastery: float,       # Current mastery of target concept (0.0-1.0)
    prerequisite_mastery: float,   # Min mastery across prerequisites (0.0-1.0)
    concept_difficulty: float,     # Intrinsic difficulty (0.0-1.0)
) -> dict:
    lower = learner_mastery
    upper = min(prerequisite_mastery + 0.3, 1.0 - concept_difficulty * 0.2)
    upper = max(upper, lower + 0.1)  # Ensure meaningful ZPD range

    return {
        "lower": lower,
        "upper": upper,
        "optimal": (lower + upper) / 2,
        "is_in_zpd": 0.3 <= learner_mastery <= 0.7,
    }
```

### 4.2 Difficulty Adaptation

```python
def adapt_difficulty(zpd: dict, recent_accuracy: float) -> float:
    if recent_accuracy > 0.85:
        return min(zpd["upper"], zpd["optimal"] + 0.1)   # Too easy
    elif recent_accuracy < 0.50:
        return max(zpd["lower"], zpd["optimal"] - 0.1)   # Too hard
    else:
        return zpd["optimal"]                              # Just right
```

## 5. Hybrid Knowledge Tracing Strategy

| Phase | Interactions | Algorithm | Rationale |
|-------|-------------|-----------|-----------|
| Cold Start | < 50 per concept | BKT | Works with minimal data, interpretable |
| Warm | 50 - 500 | BKT + FSRS | BKT feeds mastery into FSRS scheduling |
| Hot | > 500 | DKT (RNN) | Better accuracy, personalized patterns |

## 6. Learning Path Optimization

### Algorithm: Priority-based Topological Sort

```python
def optimize_learning_path(
    concepts: list[dict],
    relations: list[dict],
    learner_state: dict[str, float],
    goal: str | None = None,
) -> list[str]:
    prereqs = build_prerequisite_map(relations)
    in_degree = count_in_degrees(concepts, prereqs)

    def priority(concept_name: str) -> float:
        mastery = learner_state.get(concept_name, 0.0)
        score = 0.0
        zpd = estimate_zpd(mastery, get_min_prereq(concept_name, learner_state), 0.5)
        if zpd["is_in_zpd"]:
            score += 2.0
        score += get_min_prereq(concept_name, learner_state)
        if goal and goal.lower() in concept_name.lower():
            score += 1.0
        return score

    # Kahn's algorithm with priority queue
    available = []
    for name in concepts:
        if all_prereqs_met(name, learner_state, prereqs):
            heapq.heappush(available, (-priority(name), name))

    path = []
    while available:
        _, name = heapq.heappop(available)
        path.append(name)
        for dependent in get_dependents(name, relations):
            if all_prereqs_met(dependent, learner_state, prereqs) and dependent not in path:
                heapq.heappush(available, (-priority(dependent), dependent))

    return path
```

---

## Sources

- [FSRS Algorithm Wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- [FSRS-5 Parameters](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm#fsrs-5)
- [FSRS PyPI Package](https://pypi.org/project/fsrs/)
- [Deep Knowledge Tracing (Stanford)](https://stanford.edu/~cpiech/bio/papers/deepKnowledgeTracing.pdf)
- [Knowledge Tracing Survey (arXiv)](https://arxiv.org/html/2105.15106v4)
- [IncluLearn AI (Frontiers 2026)](https://www.frontiersin.org/articles/10.3389/frai.2026.1510424)
