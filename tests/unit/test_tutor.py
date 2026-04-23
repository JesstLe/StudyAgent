from studyagent.agents.tutor.agent import TutorAgent
from studyagent.agents.tutor.prompts import CANONICAL_TUTOR_PROMPT


def test_canonical_prompt_loaded():
    assert "发生认识论" in CANONICAL_TUTOR_PROMPT
    assert "史前时代" in CANONICAL_TUTOR_PROMPT
    assert "笨办法" in CANONICAL_TUTOR_PROMPT
    assert "救世主登场" in CANONICAL_TUTOR_PROMPT
    assert "邓俊辉" in CANONICAL_TUTOR_PROMPT
    assert "Trade-off" in CANONICAL_TUTOR_PROMPT


def test_system_prompt_builds():
    agent = TutorAgent()
    prompt = agent.build_system_prompt(session_type="teaching", topics="B-tree")
    assert "发生认识论" in prompt
    assert "teaching" in prompt
    assert "B-tree" in prompt


def test_adaptive_layer_appended():
    agent = TutorAgent()
    prompt = agent.build_system_prompt(session_type="quiz", topics="sorting")
    assert "System Extensions" in prompt
    assert "quiz" in prompt
