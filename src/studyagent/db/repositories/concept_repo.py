from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.db.models import Concept, ConceptRelation


class ConceptRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, concept_id: str) -> Concept | None:
        return await self._session.get(Concept, concept_id)

    async def get_by_name(self, name: str, domain: str) -> Concept | None:
        stmt = select(Concept).where(Concept.name == name, Concept.domain == domain)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_domain(self, domain: str) -> Sequence[Concept]:
        stmt = select(Concept).where(Concept.domain == domain).order_by(Concept.name)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_all(self) -> Sequence[Concept]:
        stmt = select(Concept).order_by(Concept.domain, Concept.name)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, name: str, domain: str, **kwargs: object) -> Concept:
        concept = Concept(name=name, domain=domain, **kwargs)
        self._session.add(concept)
        await self._session.flush()
        return concept

    async def get_or_create(self, name: str, domain: str, **kwargs: object) -> Concept:
        existing = await self.get_by_name(name, domain)
        if existing:
            return existing
        return await self.create(name, domain, **kwargs)

    async def get_prerequisites(self, concept_id: str) -> Sequence[Concept]:
        stmt = (
            select(Concept)
            .join(ConceptRelation, ConceptRelation.source_id == Concept.id)
            .where(
                ConceptRelation.target_id == concept_id,
                ConceptRelation.relation_type == "prerequisite",
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        strength: float = 1.0,
    ) -> ConceptRelation:
        rel = ConceptRelation(
            source_id=source_id, target_id=target_id,
            relation_type=relation_type, strength=strength,
        )
        self._session.add(rel)
        await self._session.flush()
        return rel
