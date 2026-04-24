import pytest
from httpx import ASGITransport, AsyncClient

from studyagent.api.main import create_app
from studyagent.db.init import init_db
import studyagent.api.routes.chat as chat_module
import studyagent.api.routes.knowledge as knowledge_module
import studyagent.api.routes.review as review_module
import studyagent.api.routes.quiz as quiz_module


@pytest.fixture
async def client(tmp_path):
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'test_api2.db'}"
    await init_db(db_url)

    from sqlalchemy.ext.asyncio import create_async_engine
    engine = create_async_engine(db_url, connect_args={"check_same_thread": False})

    from studyagent.db.engine import create_session_factory
    factory = create_session_factory(engine)

    async def override_get_db():
        async with factory() as session:
            yield session

    app = create_app()
    for module in [chat_module, knowledge_module, review_module, quiz_module]:
        app.dependency_overrides[module.get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_concept(client: AsyncClient):
    resp = await client.post(
        "/api/v1/concepts",
        json={"name": "B-tree", "domain": "data_structures", "difficulty": 0.6},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "B-tree"
    assert data["domain"] == "data_structures"


@pytest.mark.asyncio
async def test_list_concepts(client: AsyncClient):
    await client.post("/api/v1/concepts", json={"name": "HashMap", "domain": "data_structures"})
    resp = await client.get("/api/v1/concepts")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_concept_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/concepts/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient):
    resp = await client.post(
        "/api/v1/decks",
        json={"title": "Data Structures Review"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Data Structures Review"
    assert data["card_count"] == 0


@pytest.mark.asyncio
async def test_list_decks(client: AsyncClient):
    resp = await client.get("/api/v1/decks")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_knowledge_state(client: AsyncClient):
    resp = await client.get("/api/v1/knowledge/default")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_due_reviews(client: AsyncClient):
    resp = await client.get("/api/v1/reviews/due")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_submit_review(client: AsyncClient):
    concept_resp = await client.post(
        "/api/v1/concepts",
        json={"name": "TestConcept", "domain": "algorithms"},
    )
    concept_id = concept_resp.json()["id"]

    resp = await client.post(
        "/api/v1/reviews/submit",
        json={"grade": 3, "concept_id": concept_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["grade"] == 3
    assert data["scheduled_days"] >= 0
