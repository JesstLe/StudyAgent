import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(500))
    session_type: Mapped[str] = mapped_column(String(50), default="teaching")
    message_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (Index("idx_conversations_user", "user_id", "updated_at"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(100))
    token_count: Mapped[int | None] = mapped_column()
    latency_ms: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (Index("idx_messages_conversation", "conversation_id", "created_at"),)


# --- Phase 2: Knowledge System Models ---


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    tags: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("name", "domain", name="uq_concept_name_domain"),
        Index("idx_concepts_domain", "domain"),
    )


class ConceptRelation(Base):
    __tablename__ = "concept_relations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    target_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    strength: Mapped[float] = mapped_column(Float, default=1.0)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )

    source = relationship("Concept", foreign_keys=[source_id])
    target = relationship("Concept", foreign_keys=[target_id])

    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "relation_type", name="uq_concept_relation"),
        Index("idx_relations_source", "source_id"),
        Index("idx_relations_target", "target_id"),
        CheckConstraint("strength BETWEEN 0.0 AND 1.0", name="ck_relation_strength"),
    )


class KnowledgeState(Base):
    __tablename__ = "knowledge_state"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    mastery_level: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    bkt_p_learned: Mapped[float] = mapped_column(Float, default=0.1)
    fsrs_stability: Mapped[float] = mapped_column(Float, default=0.0)
    fsrs_difficulty: Mapped[float] = mapped_column(Float, default=0.0)
    fsrs_state: Mapped[str] = mapped_column(String(20), default="New")
    fsrs_reps: Mapped[int] = mapped_column(Integer, default=0)
    fsrs_lapses: Mapped[int] = mapped_column(Integer, default=0)
    fsrs_scheduled_days: Mapped[int] = mapped_column(Integer, default=0)
    fsrs_elapsed_days: Mapped[int] = mapped_column(Integer, default=0)
    total_assessments: Mapped[int] = mapped_column(Integer, default=0)
    correct_assessments: Mapped[int] = mapped_column(Integer, default=0)
    last_assessed_at: Mapped[datetime | None] = mapped_column()
    last_review_at: Mapped[datetime | None] = mapped_column()
    next_review_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_knowledge_user_concept"),
        Index("idx_knowledge_user", "user_id"),
        Index("idx_knowledge_review", "user_id", "next_review_at"),
        CheckConstraint("mastery_level BETWEEN 0.0 AND 1.0", name="ck_mastery"),
        CheckConstraint("confidence BETWEEN 0.0 AND 1.0", name="ck_confidence"),
    )


class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(50), default="ai_generated")
    card_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (Index("idx_decks_user", "user_id"),)


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    deck_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("flashcard_decks.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("concepts.id", ondelete="SET NULL")
    )
    card_type: Mapped[str] = mapped_column(String(50), nullable=False)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    extra: Mapped[str | None] = mapped_column(Text)
    options_json: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    fsrs_state: Mapped[str] = mapped_column(String(20), default="New")
    fsrs_stability: Mapped[float] = mapped_column(Float, default=0.0)
    fsrs_difficulty: Mapped[float] = mapped_column(Float, default=0.0)
    fsrs_reps: Mapped[int] = mapped_column(Integer, default=0)
    fsrs_lapses: Mapped[int] = mapped_column(Integer, default=0)
    fsrs_scheduled_days: Mapped[int] = mapped_column(Integer, default=0)
    next_review_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_flashcards_deck", "deck_id"),
        Index("idx_flashcards_review", "deck_id", "next_review_at"),
        CheckConstraint("difficulty BETWEEN 0.0 AND 1.0", name="ck_card_difficulty"),
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="SET NULL")
    )
    quiz_type: Mapped[str] = mapped_column(String(50), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float | None] = mapped_column(Float)
    time_spent_seconds: Mapped[int | None] = mapped_column()
    answers_json: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column()

    __table_args__ = (Index("idx_quiz_user", "user_id"),)


# --- Payment System Models ---


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="CNY")
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending | paid | cancelled | refunded | expired
    payment_channel: Mapped[str | None] = mapped_column(String(50))
    paid_at: Mapped[datetime | None] = mapped_column()
    expired_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="order", order_by="Payment.created_at.desc()"
    )

    __table_args__ = (
        Index("idx_orders_user", "user_id", "created_at"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_no", "order_no"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    trade_no: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)  # alipay | wxpay | qqpay
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fee_rate: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)
    fee_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    status: Mapped[str] = mapped_column(
        String(20), default="created"
    )  # created | pending | success | failed
    payment_url: Mapped[str | None] = mapped_column(Text)
    epay_trade_no: Mapped[str | None] = mapped_column(String(128))
    paid_at: Mapped[datetime | None] = mapped_column()
    callback_raw: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    order: Mapped["Order"] = relationship("Order", back_populates="payments")

    __table_args__ = (
        Index("idx_payments_order", "order_id"),
        Index("idx_payments_trade_no", "trade_no"),
        Index("idx_payments_status", "status"),
    )
