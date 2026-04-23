# StudyAgent Development Specification

> Version: 1.0 | Date: 2026-04-23 | Status: Draft

## 1. Technology Stack Summary

### Backend (Python)

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.12+ |
| Web Framework | FastAPI | 0.135+ (built-in SSE) |
| Agent Framework | LangGraph | 0.3+ |
| LLM Provider | LiteLLM (multi-provider) | Latest |
| ORM | SQLAlchemy 2.0 + Alembic | Latest |
| Vector Search | pgvector | 0.7+ |
| Cache | Redis | 7+ |
| Spaced Repetition | py-fsrs (FSRS-5) | Latest |
| Task Queue | Celery or arq | Latest |
| Testing | pytest + httpx | Latest |

### Frontend (TypeScript)

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js | 16 |
| AI SDK | Vercel AI SDK | v4/v6 |
| UI Components | shadcn/ui + AI Elements | Latest |
| Styling | Tailwind CSS | 4 |
| State | Zustand | Latest |
| Charts | Tremor | Latest |
| Graph Viz | react-force-graph | Latest |

### TUI (Python)

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Textual | 4.0+ |
| Formatting | Rich | 13+ |

### Infrastructure

| Component | Technology |
|-----------|-----------|
| Database | PostgreSQL 16+ with pgvector |
| Cache | Redis 7+ |
| Local Mode | SQLite + sqlite-vec |
| Containerization | Docker + docker-compose |
| CI/CD | GitHub Actions |

## 2. Project Structure

```
studyagent/
  pyproject.toml                    # Project config (uv/hatch)
  README.md

  src/
    studyagent/
      __init__.py

      # --- API Layer ---
      api/
        __init__.py
        main.py                     # FastAPI app factory
        dependencies.py             # Auth, DB, rate limiting
        middleware.py                # CORS, logging, error handling

        routes/
          __init__.py
          chat.py                   # POST /chat/stream, /chat/complete
          conversations.py          # CRUD for conversations
          reviews.py                # Spaced repetition endpoints
          knowledge.py              # Knowledge graph and state
          quizzes.py                # Quiz and flashcard endpoints
          documents.py              # Document upload and processing
          analytics.py              # Learning analytics
          auth.py                   # Login, register, OAuth

        schemas/                    # Pydantic request/response models
          __init__.py
          chat.py
          knowledge.py
          reviews.py
          analytics.py

      # --- Agent Layer ---
      agents/
        __init__.py
        orchestrator.py             # LangGraph state graph definition
        router.py                   # Intent classification and routing

        tutor/
          __init__.py
          agent.py                  # Tutor agent (Pain-Point Framework)
          prompts.py                # System prompts and templates
          tools.py                  # MCP tools for teaching

        quiz/
          __init__.py
          agent.py                  # Quiz generator agent
          tools.py                  # Quiz generation tools
          evaluator.py              # Answer evaluation logic

        scheduler/
          __init__.py
          agent.py                  # Review scheduler agent
          fsrs.py                   # FSRS-5 algorithm wrapper
          scheduler.py              # Review scheduling logic

        knowledge_graph/
          __init__.py
          agent.py                  # Knowledge graph builder agent
          tools.py                  # Concept extraction tools
          path_finder.py            # Learning path optimization

        analyzer/
          __init__.py
          agent.py                  # Analytics agent
          reporter.py               # Progress report generation

        document_processor/
          __init__.py
          agent.py                  # Document processing agent
          pdf_parser.py             # PDF extraction
          concept_extractor.py      # NLP concept extraction

      # --- Core Layer ---
      core/
        __init__.py
        config.py                   # Settings (pydantic-settings)
        llm.py                      # LLM provider abstraction (LiteLLM)
        memory/
          __init__.py
          short_term.py             # Redis-backed session memory
          long_term.py              # PostgreSQL-backed knowledge state
          episodic.py               # Learning event storage
        knowledge_tracing/
          __init__.py
          bkt.py                    # Bayesian Knowledge Tracing
          dkt.py                    # Deep Knowledge Tracing (future)
          zpd.py                    # Zone of Proximal Development estimator
        embeddings.py               # Embedding generation utilities
        mcp_server.py               # MCP tool server definition

      # --- Database Layer ---
      db/
        __init__.py
        engine.py                   # SQLAlchemy engine + session
        models/                     # SQLAlchemy ORM models
          __init__.py
          user.py
          conversation.py
          message.py
          concept.py
          knowledge_state.py
          flashcard.py
          document.py
          analytics.py
        repositories/               # Data access layer (Repository Pattern)
          __init__.py
          user_repo.py
          conversation_repo.py
          concept_repo.py
          knowledge_repo.py
          flashcard_repo.py
          analytics_repo.py

      # --- TUI Layer ---
      tui/
        __init__.py
        app.py                      # Textual App class
        screens/
          __init__.py
          chat.py                   # Teaching chat screen
          review.py                 # Spaced repetition screen
          dashboard.py              # Progress dashboard screen
        widgets/
          __init__.py
          message.py                # Chat message widget
          review_card.py            # Flashcard review widget
          progress_bar.py           # Knowledge progress widget
          knowledge_map.py          # ASCII concept graph widget

  # --- Web Frontend ---
  web/
    package.json
    next.config.ts
    tailwind.config.ts

    app/
      layout.tsx                    # Root layout with sidebar
      page.tsx                      # Dashboard
      chat/
        page.tsx                    # New chat
        [id]/
          page.tsx                  # Conversation
      review/
        page.tsx                    # Review session
      knowledge-graph/
        page.tsx                    # Interactive graph
        [concept]/
          page.tsx                  # Concept detail
      documents/
        page.tsx                    # Document management
      settings/
        page.tsx                    # User settings

    api/
      chat/
        route.ts                    # SSE streaming chat endpoint
      reviews/
        due/
          route.ts
        submit/
          route.ts

    components/
      chat/
        message-list.tsx
        message.tsx
        chat-input.tsx
        tool-call-display.tsx
      review/
        review-card.tsx
        rating-buttons.tsx
      graph/
        knowledge-graph.tsx
        concept-node.tsx
      dashboard/
        progress-chart.tsx
        weak-areas.tsx
        study-timeline.tsx
      ui/                           # shadcn/ui components
        button.tsx
        input.tsx
        card.tsx
        tabs.tsx
        ...

    lib/
      api-client.ts                 # API request helpers
      auth.ts                       # Authentication utilities
      store.ts                      # Zustand store
      types.ts                      # TypeScript type definitions

  # --- Testing ---
  tests/
    unit/
      agents/
        test_tutor.py
        test_scheduler.py
        test_knowledge_tracing.py
      core/
        test_memory.py
        test_fsrs.py
        test_bkt.py
    integration/
      test_chat_api.py
      test_review_api.py
      test_knowledge_api.py
    e2e/
      test_learning_flow.py

  # --- Infrastructure ---
  docker-compose.yml
  Dockerfile
  alembic/
    alembic.ini
    env.py
    versions/
  .github/
    workflows/
      ci.yml
      test.yml
```

## 3. Phase Plan

### Phase 1: Foundation (Week 1-2)

**Goal**: Basic chat with tutor persona, database setup

- [ ] Project scaffolding (pyproject.toml, Docker, CI)
- [ ] PostgreSQL schema + Alembic migrations
- [ ] FastAPI app with auth (JWT)
- [ ] Basic LangGraph agent with tutor persona
- [ ] SSE streaming endpoint
- [ ] Simple TUI with Textual (chat screen only)
- [ ] Unit tests for core components

### Phase 2: Knowledge System (Week 3-4)

**Goal**: Knowledge graph, concept tracking, spaced repetition

- [ ] Concept and concept_relation models
- [ ] Knowledge state tracking (BKT)
- [ ] FSRS-5 integration for spaced repetition
- [ ] Knowledge graph agent (concept extraction, prerequisite detection)
- [ ] Review screen in TUI
- [ ] Flashcard generation from conversations
- [ ] Tests for knowledge tracing and scheduling

### Phase 3: Multi-Agent Orchestration (Week 5-6)

**Goal**: Full agent orchestration, quiz generation, document processing

- [ ] LangGraph state graph with routing
- [ ] Quiz generator agent
- [ ] Document processor agent (PDF, URL)
- [ ] Analyzer agent (basic analytics)
- [ ] MCP tool server
- [ ] Progress dashboard in TUI
- [ ] Integration tests for multi-agent flows

### Phase 4: Web UI (Week 7-8)

**Goal**: Next.js web interface with all features

- [ ] Next.js 16 project setup with shadcn/ui
- [ ] Chat page with streaming
- [ ] Dashboard page with analytics charts
- [ ] Review page
- [ ] Knowledge graph visualization
- [ ] Document upload interface
- [ ] Settings page

### Phase 5: Polish and Deploy (Week 9-10)

**Goal**: Production readiness, observability, optimization

- [ ] Redis integration for caching and sessions
- [ ] Langfuse/LangSmith tracing
- [ ] Rate limiting and security hardening
- [ ] Performance optimization
- [ ] E2E test suite
- [ ] Docker Compose for production deployment
- [ ] Documentation

## 4. Key Implementation Details

### 4.1 Tutor System Prompt (The Pain-Point Framework)

完整的导师角色系统提示词定义在 [06-tutor-persona-spec.md](06-tutor-persona-spec.md) 中。

系统提示词由两层组成：

1. **Canonical Layer (原始提示词)** — 用户提供的中文系统提示词，原样注入，不可修改
2. **Adaptive Layer (自适应增强层)** — 系统自动注入学习者状态（知识图谱、ZPD、待复习概念等）

```python
from studyagent.agents.tutor.prompts import CANONICAL_TUTOR_PROMPT

def build_tutor_system_prompt(user_context: UserContext) -> str:
    """Assemble complete tutor system prompt with learner context."""
    # Layer 1: Canonical prompt (exact user-provided Chinese text)
    # Layer 2: Auto-injected learner state + adaptation rules
    # Full implementation: see 06-tutor-persona-spec.md Section 5.1
    return CANONICAL_TUTOR_PROMPT + build_adaptive_layer(user_context)
```

### 4.2 FSRS-5 Integration

```python
from fsrs import FSRS, Rating, Card, ReviewLog
from datetime import datetime, timedelta

class SpacedRepetitionScheduler:
    def __init__(self, parameters: dict | None = None):
        self.fsrs = FSRS(parameters) if parameters else FSRS()

    def get_due_reviews(
        self,
        user_id: str,
        limit: int = 20,
        concept_filter: str | None = None
    ) -> list[dict]:
        """Get cards due for review."""
        now = datetime.now()
        due_cards = self.repo.get_cards_due_before(
            user_id=user_id,
            due_before=now,
            limit=limit,
            concept_filter=concept_filter
        )
        return due_cards

    def submit_review(
        self,
        card_id: str,
        rating: int  # 1=Again, 2=Hard, 3=Good, 4=Easy
    ) -> dict:
        """Submit a review and get next schedule."""
        card = self.repo.get_card(card_id)
        fsrs_rating = Rating(rating)

        # FSRS-5 scheduling
        scheduling_cards = self.fsrs.repeat(card, datetime.now())
        updated_card = scheduling_cards[fsrs_rating].card

        # Update database
        self.repo.update_card(card_id, {
            "fsrs_state": {
                "stability": updated_card.stability,
                "difficulty": updated_card.difficulty,
                "elapsed_days": updated_card.elapsed_days,
                "scheduled_days": updated_card.scheduled_days,
                "reps": updated_card.reps,
                "lapses": updated_card.lapses,
                "state": updated_card.state.name,
                "last_review": datetime.now().isoformat(),
            },
            "next_review_at": datetime.now() + timedelta(
                days=updated_card.scheduled_days
            ),
        })

        return {
            "card_id": card_id,
            "next_review": updated_card.scheduled_days,
            "stability": updated_card.stability,
        }
```

### 4.3 Knowledge Tracing (BKT)

```python
class BayesianKnowledgeTracing:
    """BKT model for estimating concept mastery."""

    def __init__(
        self,
        p_L0: float = 0.1,   # P(initial mastery)
        p_T: float = 0.1,     # P(transition to mastered)
        p_G: float = 0.2,     # P(guess correctly | not mastered)
        p_S: float = 0.1,     # P(slip | mastered)
    ):
        self.p_L0 = p_L0
        self.p_T = p_T
        self.p_G = p_G
        self.p_S = p_S

    def update(self, p_L_prev: float, correct: bool) -> float:
        """Update P(mastery) given an observation."""
        if correct:
            # P(L|correct) = P(correct|L) * P(L) / P(correct)
            p_correct_given_L = 1 - self.p_S
            p_correct_given_not_L = self.p_G
        else:
            p_correct_given_L = self.p_S
            p_correct_given_not_L = 1 - self.p_G

        # Bayesian update
        p_L_after_evidence = (
            p_correct_given_L * p_L_prev
            / (p_correct_given_L * p_L_prev
               + p_correct_given_not_L * (1 - p_L_prev))
        )

        # Apply transition
        p_L_new = p_L_after_evidence + (1 - p_L_after_evidence) * self.p_T

        return min(p_L_new, 1.0)
```

### 4.4 ZPD Estimator

```python
class ZPDEstimator:
    """Estimate Zone of Proximal Development for adaptive difficulty."""

    def estimate(
        self,
        learner_mastery: float,
        prerequisite_mastery: float,
        concept_difficulty: float,
    ) -> dict:
        zpd_lower = learner_mastery * 0.8  # Can do with scaffolding
        zpd_upper = min(
            prerequisite_mastery + 0.3 * concept_difficulty,
            1.0
        )

        return {
            "lower": zpd_lower,
            "upper": zpd_upper,
            "optimal_difficulty": (zpd_lower + zpd_upper) / 2,
            "is_in_zpd": zpd_lower < learner_mastery < zpd_upper,
            "recommendation": self._get_recommendation(
                learner_mastery, zpd_lower, zpd_upper
            ),
        }

    def _get_recommendation(
        self, mastery: float, lower: float, upper: float
    ) -> str:
        if mastery < lower:
            return "prerequisite_gap"  # Need to learn prerequisites
        elif mastery > upper:
            return "too_easy"          # Move to harder concepts
        else:
            return "optimal"           # Right difficulty level
```

## 5. Configuration

```yaml
# config.yaml
app:
  name: StudyAgent
  version: "1.0.0"
  debug: false

server:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["http://localhost:3000"]

database:
  url: "postgresql+asyncpg://studyagent:password@localhost:5432/studyagent"
  pool_size: 20
  max_overflow: 10

redis:
  url: "redis://localhost:6379/0"
  session_ttl: 86400  # 24 hours

llm:
  default_provider: "openai"
  default_model: "gpt-4o"
  fallback_model: "gpt-4o-mini"

  providers:
    openai:
      api_key: "${OPENAI_API_KEY}"
      models:
        tutor: "gpt-4o"
        quiz: "gpt-4o-mini"
        embedding: "text-embedding-3-small"
    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      models:
        tutor: "claude-sonnet-4-20250514"
    local:
      base_url: "http://localhost:11434"
      models:
        tutor: "qwen2.5:14b"
        embedding: "nomic-embed-text"

agent:
  max_steps: 10
  max_tokens_per_response: 4096
  streaming: true

fsrs:
  request_retention: 0.9
  maximum_interval: 365
  default_parameters: [
    0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01,
    1.49, 0.14, 0.94, 2.22, 0.99, 0.06, 0.36
  ]

knowledge_tracing:
  method: "bkt"  # "bkt" or "dkt"
  bkt_defaults:
    p_L0: 0.1
    p_T: 0.1
    p_G: 0.2
    p_S: 0.1
```

## 6. Testing Strategy

### 6.1 Coverage Requirements
- Minimum 80% code coverage
- All agent tools must have unit tests
- All API endpoints must have integration tests
- Critical learning flows must have E2E tests

### 6.2 Test Categories

| Category | Tool | Scope |
|----------|------|-------|
| Unit Tests | pytest | Individual functions, agents, algorithms |
| Integration Tests | pytest + httpx | API endpoints, database operations |
| E2E Tests | pytest + Playwright | Full learning flows |
| Agent Tests | pytest | Agent trajectory validation |

### 6.3 Key Test Cases

```python
# tests/unit/test_fsrs.py
def test_fsrs_first_review_good():
    """First review with 'Good' rating should schedule 1-3 days out."""
    scheduler = SpacedRepetitionScheduler()
    result = scheduler.submit_review(card_id="test", rating=3)
    assert 1 <= result["next_review"] <= 3

# tests/unit/test_bkt.py
def test_bkt_correct_answer_increases_mastery():
    """Correct answer should increase P(mastery)."""
    bkt = BayesianKnowledgeTracing()
    p_L = 0.1
    new_p_L = bkt.update(p_L, correct=True)
    assert new_p_L > p_L

# tests/integration/test_chat_api.py
async def test_chat_stream_returns_sse():
    """POST /chat/stream should return SSE events."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json={"messages": [{"role": "user", "content": "What is a B-tree?"}]},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
```

## 7. Security Checklist

- [ ] No hardcoded secrets (use environment variables)
- [ ] All user inputs validated (Pydantic schemas)
- [ ] SQL injection prevention (SQLAlchemy parameterized queries)
- [ ] XSS prevention (sanitized HTML output)
- [ ] JWT authentication on all endpoints
- [ ] Rate limiting (Redis sliding window)
- [ ] CORS properly configured
- [ ] LLM API keys never exposed to client
- [ ] File upload validation (type, size limits)
- [ ] Audit logging for sensitive operations

---

## Sources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Vercel AI SDK](https://ai-sdk.dev/)
- [FSRS Python Package (PyPI)](https://pypi.org/project/fsrs/)
- [FastAPI SSE Documentation](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [Textual Documentation](https://textual.textualize.io/)
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [pgvector](https://github.com/pgvector/pgvector)
