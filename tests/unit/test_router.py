import pytest

from studyagent.agents.orchestrator.router import IntentRouter


def test_keyword_quiz():
    router = IntentRouter()
    assert router.classify_by_keywords("给我出个quiz") == "quiz"
    assert router.classify_by_keywords("test me on sorting") == "quiz"


def test_keyword_review():
    router = IntentRouter()
    assert router.classify_by_keywords("我要复习") == "review"
    assert router.classify_by_keywords("show me flashcards") == "review"


def test_keyword_analyze():
    router = IntentRouter()
    assert router.classify_by_keywords("show my progress") == "analyze"
    assert router.classify_by_keywords("我的进度怎么样") == "analyze"


def test_keyword_explore():
    router = IntentRouter()
    assert router.classify_by_keywords("show the knowledge graph") == "explore"
    assert router.classify_by_keywords("what's the learning path") == "explore"


def test_keyword_teach_default():
    router = IntentRouter()
    assert router.classify_by_keywords("what is a B-tree?") is None
    assert router.classify_by_keywords("explain binary search") is None


@pytest.mark.asyncio
async def test_classify_no_llm():
    router = IntentRouter()
    result = await router.classify("explain quicksort")
    assert result == "teach"


@pytest.mark.asyncio
async def test_classify_with_keyword_match():
    router = IntentRouter()
    result = await router.classify("quiz me on graphs")
    assert result == "quiz"
    result2 = await router.classify("let me review")
    assert result2 == "review"
