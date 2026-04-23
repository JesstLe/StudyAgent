import pytest
from httpx import ASGITransport, AsyncClient

from studyagent.api.main import create_app
from studyagent.db.init import init_db


@pytest.fixture
async def client(tmp_path):
    import studyagent.api.routes.chat as chat_module

    db_url = f"sqlite+aiosqlite:///{tmp_path / 'test_api.db'}"
    await init_db(db_url)

    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(db_url, connect_args={"check_same_thread": False})

    from studyagent.db.engine import create_session_factory

    factory = create_session_factory(engine)

    async def override_get_db():
        async with factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[chat_module.get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient):
    resp = await client.post(
        "/api/v1/conversations",
        json={"title": "Test Conv", "session_type": "teaching"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Conv"
    assert data["session_type"] == "teaching"


@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient):
    resp = await client.get("/api/v1/conversations")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
