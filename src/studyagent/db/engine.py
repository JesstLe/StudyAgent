from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from studyagent.core.config import DatabaseConfig, load_config


def create_engine(config: DatabaseConfig | None = None):
    if config is None:
        config = load_config().database
    connect_args = {"check_same_thread": False} if "sqlite" in config.url else {}
    return create_async_engine(
        config.url,
        pool_size=config.pool_size if "sqlite" not in config.url else 0,
        max_overflow=config.max_overflow,
        connect_args=connect_args,
        echo=False,
    )


def create_session_factory(engine=None) -> async_sessionmaker[AsyncSession]:
    if engine is None:
        engine = create_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = create_session_factory()
    async with session_factory() as session:
        yield session
