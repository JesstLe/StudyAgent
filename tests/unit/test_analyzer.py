import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from studyagent.agents.analyzer.agent import AnalyzerAgent
from studyagent.agents.orchestrator.state import LearningState
from studyagent.db.init import init_db
from studyagent.db.repositories import ConceptRepo, KnowledgeRepo


@pytest.fixture
async def db_with_data(tmp_path):
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'test_analyzer.db'}"
    await init_db(db_url)
    engine = create_async_engine(db_url, connect_args={"check_same_thread": False})
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        c_repo = ConceptRepo(session)
        k_repo = KnowledgeRepo(session)

        c1 = await c_repo.create(name="Sorting", domain="algorithms", difficulty=0.3)
        c2 = await c_repo.create(name="B-tree", domain="data_structures", difficulty=0.55)
        c3 = await c_repo.create(name="Deadlock", domain="os", difficulty=0.5)
        c4 = await c_repo.create(name="TCP", domain="networks", difficulty=0.4)
        await session.commit()

        s1 = await k_repo.get_or_create("user1", c1.id)
        s1.mastery_level = 0.9
        s1.total_assessments = 10

        s2 = await k_repo.get_or_create("user1", c2.id)
        s2.mastery_level = 0.3
        s2.total_assessments = 3

        s3 = await k_repo.get_or_create("user1", c3.id)
        s3.mastery_level = 0.1
        s3.total_assessments = 1

        await session.commit()
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_analyzer_overview(db_with_data: AsyncSession):
    agent = AnalyzerAgent(db_with_data)
    overview = await agent.get_overview("user1")
    assert overview["total_concepts"] == 3
    assert overview["mastered"] == 1
    assert overview["learning"] == 1
    assert overview["new"] == 1
    assert 0.0 <= overview["avg_mastery"] <= 1.0


@pytest.mark.asyncio
async def test_analyzer_weak_areas(db_with_data: AsyncSession):
    agent = AnalyzerAgent(db_with_data)
    weak = await agent.get_weak_areas("user1")
    assert len(weak) > 0
    assert all(w["mastery"] < 0.6 for w in weak)
    # Deadlock (0.1) should be weakest
    assert weak[0]["concept_name"] == "Deadlock"


@pytest.mark.asyncio
async def test_analyzer_recommendations(db_with_data: AsyncSession):
    agent = AnalyzerAgent(db_with_data)
    recs = await agent.get_recommended_topics("user1")
    assert len(recs) > 0
    # TCP has no knowledge state (mastery 0), should be recommended
    names = [r["name"] for r in recs]
    assert "TCP" in names


@pytest.mark.asyncio
async def test_analyzer_domain_summary(db_with_data: AsyncSession):
    agent = AnalyzerAgent(db_with_data)
    domains = await agent.get_domain_summary("user1")
    assert len(domains) > 0
    domain_names = [d["domain"] for d in domains]
    assert "algorithms" in domain_names
    assert "data_structures" in domain_names


@pytest.mark.asyncio
async def test_analyzer_empty_user(db_with_data: AsyncSession):
    agent = AnalyzerAgent(db_with_data)
    overview = await agent.get_overview("nonexistent_user")
    assert overview["total_concepts"] == 0
    assert overview["avg_mastery"] == 0.0


def test_learning_state():
    state = LearningState(user_id="test", intent="teach")
    assert state.user_id == "test"
    assert state.intent == "teach"
    assert state.messages == []
    assert state.extracted_concepts == []
