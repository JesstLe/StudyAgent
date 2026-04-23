from studyagent.db.engine import create_engine
from studyagent.db.models import Base


async def init_db(database_url: str | None = None) -> None:
    from studyagent.core.config import DatabaseConfig

    config = DatabaseConfig(url=database_url) if database_url else None
    engine = create_engine(config)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
