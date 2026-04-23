import asyncio
import uuid

import pytest

from studyagent.db.engine import create_engine, create_session_factory
from studyagent.db.init import init_db
from studyagent.db.models import Conversation, Message, User


@pytest.fixture
async def db_session(tmp_path):
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    await init_db(db_url)

    engine = create_engine_from_url(db_url)
    factory = create_session_factory(engine)
    async with factory() as session:
        yield session
    await engine.dispose()


def create_engine_from_url(url: str):
    from sqlalchemy.ext.asyncio import create_async_engine
    return create_async_engine(url, connect_args={"check_same_thread": False})


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(id=str(uuid.uuid4()), username="learner", display_name="Learner")
    db_session.add(user)
    await db_session.commit()

    from sqlalchemy import select
    stmt = select(User).where(User.username == "learner")
    result = await db_session.execute(stmt)
    found = result.scalar_one()
    assert found.username == "learner"
    assert found.display_name == "Learner"


@pytest.mark.asyncio
async def test_create_conversation_with_messages(db_session):
    user = User(id=str(uuid.uuid4()), username="conv_test_user")
    db_session.add(user)
    await db_session.commit()

    conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=user.id,
        title="B-tree Discussion",
        session_type="teaching",
    )
    db_session.add(conv)
    await db_session.commit()

    msg1 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="user",
        content="What is a B-tree?",
    )
    msg2 = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="assistant",
        content="Let me take you back to 1970...",
    )
    db_session.add_all([msg1, msg2])
    await db_session.commit()

    from sqlalchemy import select
    stmt = select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at)
    result = await db_session.execute(stmt)
    messages = result.scalars().all()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
