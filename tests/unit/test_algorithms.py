from studyagent.core.knowledge_tracing.bkt import BKTParams, BKTState, BayesianKnowledgeTracing


def test_bkt_correct_increases_mastery():
    bkt = BayesianKnowledgeTracing()
    state = BKTState(p_learned=0.1)
    new_state = bkt.update(state, correct=True)
    assert new_state.p_learned > state.p_learned


def test_bkt_incorrect_decreases_or_slight_change():
    bkt = BayesianKnowledgeTracing()
    state = BKTState(p_learned=0.5)
    new_state = bkt.update(state, correct=False)
    assert new_state.p_learned < state.p_learned


def test_bkt_bounded():
    bkt = BayesianKnowledgeTracing()
    state = BKTState(p_learned=0.1)
    for _ in range(100):
        state = bkt.update(state, correct=True)
    assert state.p_learned <= 1.0
    assert state.p_learned >= 0.0


def test_bkt_mastered_threshold():
    bkt = BayesianKnowledgeTracing()
    state = BKTState(p_learned=0.1)
    for _ in range(20):
        state = bkt.update(state, correct=True)
    assert state.mastered


def test_bkt_predict():
    bkt = BayesianKnowledgeTracing()
    state = BKTState(p_learned=0.5)
    p_correct = bkt.predict(state)
    assert 0.0 <= p_correct <= 1.0
    assert p_correct > 0.5  # With p_L=0.5, P(correct) should be > 0.5


def test_bkt_initial_state():
    bkt = BayesianKnowledgeTracing(BKTParams(p_l0=0.2))
    state = bkt.initial_state()
    assert state.p_learned == 0.2


def test_bkt_custom_params():
    params = BKTParams(p_l0=0.2, p_transfer=0.15, p_guess=0.1, p_slip=0.05)
    bkt = BayesianKnowledgeTracing(params)
    state = bkt.initial_state()
    assert state.p_learned == 0.2
    updated = bkt.update(state, correct=True)
    assert updated.p_learned > 0.2


def test_bkt_immutability():
    bkt = BayesianKnowledgeTracing()
    state = BKTState(p_learned=0.3)
    new_state = bkt.update(state, correct=True)
    assert state.p_learned == 0.3
    assert new_state.p_learned != 0.3
