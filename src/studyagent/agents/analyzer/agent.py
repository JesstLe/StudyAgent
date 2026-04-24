from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.db.models import Concept, KnowledgeState
from studyagent.db.repositories import ConceptRepo, KnowledgeRepo


class AnalyzerAgent:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._c_repo = ConceptRepo(session)
        self._k_repo = KnowledgeRepo(session)

    async def get_overview(self, user_id: str) -> dict:
        states = await self._k_repo.get_all_for_user(user_id)
        total = len(states)
        if total == 0:
            return {
                "total_concepts": 0,
                "mastered": 0,
                "learning": 0,
                "new": 0,
                "avg_mastery": 0.0,
                "due_reviews": 0,
                "mastery_distribution": {"mastered": 0, "learning": 0, "new": 0},
            }

        mastered = sum(1 for s in states if s.mastery_level >= 0.8)
        learning = sum(1 for s in states if 0.2 <= s.mastery_level < 0.8)
        new = sum(1 for s in states if s.mastery_level < 0.2)
        avg_mastery = sum(s.mastery_level for s in states) / total

        now = datetime.now(timezone.utc)
        due = sum(1 for s in states if s.next_review_at and s.next_review_at <= now)

        return {
            "total_concepts": total,
            "mastered": mastered,
            "learning": learning,
            "new": new,
            "avg_mastery": round(avg_mastery, 3),
            "due_reviews": due,
            "mastery_distribution": {"mastered": mastered, "learning": learning, "new": new},
        }

    async def get_weak_areas(self, user_id: str, limit: int = 10) -> list[dict]:
        states = await self._k_repo.get_all_for_user(user_id)
        weak = sorted(states, key=lambda s: s.mastery_level)[:limit]

        result = []
        for s in weak:
            concept = await self._c_repo.get_by_id(s.concept_id)
            if concept and s.mastery_level < 0.6:
                result.append({
                    "concept_id": s.concept_id,
                    "concept_name": concept.name,
                    "domain": concept.domain,
                    "mastery": round(s.mastery_level, 3),
                    "assessments": s.total_assessments,
                })
        return result

    async def get_recommended_topics(self, user_id: str, limit: int = 5) -> list[dict]:
        stmt = (
            select(Concept)
            .outerjoin(KnowledgeState, (KnowledgeState.concept_id == Concept.id) & (KnowledgeState.user_id == user_id))
            .where((KnowledgeState.mastery_level < 0.3) | (KnowledgeState.id.is_(None)))
            .order_by(Concept.importance.desc(), Concept.difficulty.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        concepts = result.scalars().all()

        recommendations = []
        for c in concepts:
            prereqs = await self._c_repo.get_prerequisites(c.id)
            prereq_names = [p.name for p in prereqs]
            recommendations.append({
                "concept_id": c.id,
                "name": c.name,
                "domain": c.domain,
                "difficulty": c.difficulty,
                "prerequisites": prereq_names,
            })
        return recommendations

    async def get_domain_summary(self, user_id: str) -> list[dict]:
        concepts = await self._c_repo.list_all()
        domain_map: dict[str, list[float]] = {}

        for c in concepts:
            state = await self._k_repo.get(user_id, c.id)
            mastery = state.mastery_level if state else 0.0
            domain_map.setdefault(c.domain, []).append(mastery)

        return [
            {
                "domain": domain,
                "concepts": len(masteries),
                "avg_mastery": round(sum(masteries) / len(masteries), 3) if masteries else 0.0,
            }
            for domain, masteries in sorted(domain_map.items())
        ]
