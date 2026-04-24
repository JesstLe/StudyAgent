from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class BKTParams:
    p_l0: float = 0.1
    p_transfer: float = 0.1
    p_guess: float = 0.2
    p_slip: float = 0.1


@dataclass(frozen=True)
class BKTState:
    p_learned: float = 0.1

    @property
    def mastered(self) -> bool:
        return self.p_learned >= 0.95


class BayesianKnowledgeTracing:
    def __init__(self, params: BKTParams | None = None):
        self.params = params or BKTParams()

    def update(self, state: BKTState, correct: bool) -> BKTState:
        p = self.params
        p_L = state.p_learned

        if correct:
            p_evidence = p_L * (1 - p.p_slip) + (1 - p_L) * p.p_guess
            p_L_given_e = p_L * (1 - p.p_slip) / p_evidence
        else:
            p_evidence = p_L * p.p_slip + (1 - p_L) * (1 - p.p_guess)
            p_L_given_e = p_L * p.p_slip / p_evidence

        p_L_new = p_L_given_e + (1 - p_L_given_e) * p.p_transfer
        return replace(state, p_learned=min(1.0, p_L_new))

    def predict(self, state: BKTState) -> float:
        p = self.params
        p_L = state.p_learned
        return p_L * (1 - p.p_slip) + (1 - p_L) * p.p_guess

    def initial_state(self) -> BKTState:
        return BKTState(p_learned=self.params.p_l0)
