import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from studyagent.db.init import init_db
from studyagent.db.models import Base, Concept, ConceptRelation, KnowledgeState, Flashcard, FlashcardDeck
from studyagent.db.repositories import ConceptRepo, KnowledgeRepo, FlashcardRepo


@pytest.fixture
async def db_session(tmp_path):
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'test_phase2.db'}"
    await init_db(db_url)
    engine = create_async_engine(db_url, connect_args={"check_same_thread": False})
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_concept_crud(db_session: AsyncSession):
    repo = ConceptRepo(db_session)
    concept = await repo.create(name="B-tree", domain="data_structures", difficulty=0.6)
    await db_session.commit()

    fetched = await repo.get_by_id(concept.id)
    assert fetched is not None
    assert fetched.name == "B-tree"
    assert fetched.domain == "data_structures"


@pytest.mark.asyncio
async def test_concept_get_or_create(db_session: AsyncSession):
    repo = ConceptRepo(db_session)
    c1 = await repo.get_or_create(name="HashMap", domain="data_structures")
    await db_session.commit()
    c2 = await repo.get_or_create(name="HashMap", domain="data_structures")
    assert c1.id == c2.id


@pytest.mark.asyncio
async def test_concept_relations(db_session: AsyncSession):
    repo = ConceptRepo(db_session)
    c1 = await repo.create(name="BST", domain="data_structures")
    c2 = await repo.create(name="B-tree", domain="data_structures")
    await repo.add_relation(c1.id, c2.id, "prerequisite")
    await db_session.commit()

    prereqs = await repo.get_prerequisites(c2.id)
    assert len(prereqs) == 1
    assert prereqs[0].name == "BST"


@pytest.mark.asyncio
async def test_knowledge_state(db_session: AsyncSession):
    c_repo = ConceptRepo(db_session)
    concept = await c_repo.create(name="Sorting", domain="algorithms")
    await db_session.commit()

    k_repo = KnowledgeRepo(db_session)
    state = await k_repo.get_or_create(user_id="user1", concept_id=concept.id)
    await db_session.commit()
    assert state.mastery_level == 0.0

    updated = await k_repo.update_bkt("user1", concept.id, p_learned=0.6)
    await db_session.commit()
    assert updated.mastery_level == 0.6
    assert updated.total_assessments == 1


@pytest.mark.asyncio
async def test_knowledge_fsrs_update(db_session: AsyncSession):
    c_repo = ConceptRepo(db_session)
    concept = await c_repo.create(name="Graph", domain="data_structures")
    await db_session.commit()

    k_repo = KnowledgeRepo(db_session)
    from datetime import datetime, timezone, timedelta
    next_review = datetime.now(timezone.utc) + timedelta(days=3)

    state = await k_repo.update_fsrs(
        "user1", concept.id,
        stability=3.5, difficulty=4.2, fsrs_state="Review",
        reps=3, lapses=0, scheduled_days=3,
        next_review_at=next_review,
    )
    await db_session.commit()
    assert state.fsrs_stability == 3.5
    assert state.fsrs_state == "Review"


@pytest.mark.asyncio
async def test_flashcard_deck_and_cards(db_session: AsyncSession):
    f_repo = FlashcardRepo(db_session)
    deck = await f_repo.create_deck(user_id="user1", title="DS Quiz")
    await db_session.commit()

    card = await f_repo.create_card(
        deck_id=deck.id,
        card_type="multiple_choice",
        front="What is the time complexity of B-tree search?",
        back="O(log n)",
        difficulty=0.4,
    )
    await db_session.commit()

    assert card.deck_id == deck.id
    assert card.card_type == "multiple_choice"

    deck = await f_repo.get_deck(deck.id)
    assert deck.card_count == 1

    cards = await f_repo.get_deck_cards(deck.id)
    assert len(cards) == 1


@pytest.mark.asyncio
async def test_list_concepts_by_domain(db_session: AsyncSession):
    repo = ConceptRepo(db_session)
    await repo.create(name="B-tree", domain="data_structures")
    await repo.create(name="HashMap", domain="data_structures")
    await repo.create(name="QuickSort", domain="algorithms")
    await db_session.commit()

    ds = await repo.list_by_domain("data_structures")
    assert len(ds) == 2
    alg = await repo.list_by_domain("algorithms")
    assert len(alg) == 1
