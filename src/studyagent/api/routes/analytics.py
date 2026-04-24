from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.agents.analyzer.agent import AnalyzerAgent

router = APIRouter(prefix="/api/v1")


async def get_db():
    from studyagent.db.engine import create_session_factory

    factory = create_session_factory()
    async with factory() as session:
        yield session


@router.get("/analytics/{user_id}/overview")
async def get_analytics_overview(user_id: str, db: AsyncSession = Depends(get_db)):
    agent = AnalyzerAgent(db)
    return await agent.get_overview(user_id)


@router.get("/analytics/{user_id}/weak-areas")
async def get_weak_areas(user_id: str, limit: int = 10, db: AsyncSession = Depends(get_db)):
    agent = AnalyzerAgent(db)
    return await agent.get_weak_areas(user_id, limit)


@router.get("/analytics/{user_id}/recommendations")
async def get_recommendations(user_id: str, limit: int = 5, db: AsyncSession = Depends(get_db)):
    agent = AnalyzerAgent(db)
    return await agent.get_recommended_topics(user_id, limit)


@router.get("/analytics/{user_id}/domains")
async def get_domain_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    agent = AnalyzerAgent(db)
    return await agent.get_domain_summary(user_id)
