# StudyAgent Development Roadmap

> Version: 1.0 | Date: 2026-04-23 | Status: Draft

## 1. Overview

This document provides the implementation roadmap for StudyAgent, broken into phases from MVP to full production. Each phase has clear deliverables, acceptance criteria, and dependencies.

## 2. Phase 1: Foundation (Weeks 1-3)

**Goal**: Working TUI chat with single agent, local SQLite, basic teaching.

### Deliverables

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 1.1 | Project scaffold (Python package, config, dev tooling) | P0 | 2h |
| 1.2 | Database models (SQLAlchemy 2.0 async) + Alembic migrations | P0 | 4h |
| 1.3 | SQLite local mode with sqlite-vec | P0 | 2h |
| 1.4 | LLM provider abstraction (LiteLLM) with Ollama support | P0 | 3h |
| 1.5 | Tutor agent with Pain-Point Framework system prompt | P0 | 4h |
| 1.6 | Basic TUI (Textual) with streaming chat | P0 | 4h |
| 1.7 | Conversation persistence (save/resume) | P1 | 2h |
| 1.8 | Knowledge state tracking (basic BKT) | P1 | 3h |

### Acceptance Criteria

- User can start TUI, chat with tutor about any CS concept
- Tutor follows Pain-Point Framework in explanations
- Conversations persist across sessions in SQLite
- Basic knowledge state tracking works (concept mastery updates)

### Technology

```
Python 3.12+ | FastAPI | SQLAlchemy 2.0 (async) | SQLite + sqlite-vec
Textual 4.0+ | Rich 13.9+ | LiteLLM | Ollama (local LLM)
```

## 3. Phase 2: Core Learning Engine (Weeks 4-6)

**Goal**: Spaced repetition, knowledge graph, quiz generation.

### Deliverables

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 2.1 | FSRS-5 scheduler integration (fsrs Python package) | P0 | 3h |
| 2.2 | Flashcard CRUD (create from AI, create from user) | P0 | 3h |
| 2.3 | Review mode in TUI (flashcard interface with FSRS rating) | P0 | 4h |
| 2.4 | Quiz generator agent (MCQ, fill-blank, open-ended) | P0 | 4h |
| 2.5 | Quiz mode in TUI (answer, evaluate, show results) | P1 | 3h |
| 2.6 | Knowledge graph schema + concept extraction | P0 | 4h |
| 2.7 | Knowledge graph visualization in TUI (tree view) | P1 | 3h |
| 2.8 | LangGraph orchestration (router + specialized agents) | P0 | 4h |
| 2.9 | Feynman technique integration | P2 | 2h |

### Acceptance Criteria

- User can create flashcards from conversations, review them with FSRS scheduling
- Quiz generator produces calibrated questions based on ZPD
- Knowledge graph shows concept relationships and prerequisite chains
- Router dispatches to correct agent based on user intent

## 4. Phase 3: Web UI (Weeks 7-10)

**Goal**: Full-featured Next.js web interface with visualizations.

### Deliverables

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 3.1 | Next.js 16 project scaffold with shadcn/ui | P0 | 2h |
| 3.2 | FastAPI backend SSE streaming endpoint | P0 | 3h |
| 3.3 | Chat interface with streaming (Vercel AI SDK) | P0 | 4h |
| 3.4 | Sidebar navigation + conversation management | P0 | 3h |
| 3.5 | Review mode web UI (flashcard flip animation) | P0 | 4h |
| 3.6 | Quiz mode web UI | P1 | 3h |
| 3.7 | Knowledge graph visualization (D3.js force graph) | P1 | 4h |
| 3.8 | Progress dashboard with charts (Recharts) | P1 | 4h |
| 3.9 | Document import UI (drag-and-drop) | P1 | 3h |
| 3.10 | Dark/light theme, mobile responsive | P1 | 3h |
| 3.11 | User authentication (JWT) | P0 | 4h |

### Acceptance Criteria

- Web UI has feature parity with TUI for core flows
- Streaming responses render correctly in real-time
- Knowledge graph is interactive (click, zoom, filter)
- Progress dashboard shows meaningful analytics
- Mobile-responsive layout works on phone screens

## 5. Phase 4: Multi-Agent Intelligence (Weeks 11-14)

**Goal**: Advanced agent capabilities, document processing, analytics.

### Deliverables

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 4.1 | Document processor agent (PDF, URL, code) | P0 | 5h |
| 4.2 | Knowledge graph auto-building from documents | P0 | 4h |
| 4.3 | Learning path optimization algorithm | P1 | 4h |
| 4.4 | Knowledge gap detection and reporting | P1 | 3h |
| 4.5 | Deep Knowledge Tracing (DKT) model | P2 | 5h |
| 4.6 | FSRS parameter personalization | P2 | 3h |
| 4.7 | Cornell Notes AI enhancement | P2 | 3h |
| 4.8 | Learning analytics dashboard (full) | P1 | 4h |
| 4.9 | LLM-as-Judge quality evaluation | P2 | 3h |
| 4.10 | Agent observability (Langfuse integration) | P1 | 3h |

### Acceptance Criteria

- Users can import PDFs and have concepts automatically extracted
- Learning path is personalized based on knowledge state and goals
- Analytics dashboard shows actionable insights
- Agent behavior is observable and debuggable

## 6. Phase 5: Production (Weeks 15-18)

**Goal**: Production deployment, multi-user, polish.

### Deliverables

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 5.1 | PostgreSQL + pgvector production setup | P0 | 3h |
| 5.2 | Redis session management | P0 | 2h |
| 5.3 | Docker Compose for full stack | P0 | 3h |
| 5.4 | API rate limiting and security hardening | P0 | 3h |
| 5.5 | Multi-user support and data isolation | P0 | 4h |
| 5.6 | Background task queue (Celery) for document processing | P1 | 3h |
| 5.7 | Data export (GDPR compliance) | P1 | 2h |
| 5.8 | MCP server for external tool integration | P2 | 4h |
| 5.9 | Performance optimization and caching | P1 | 4h |
| 5.10 | End-to-end testing suite | P0 | 5h |

### Acceptance Criteria

- System handles multiple concurrent users
- Document processing runs in background without blocking
- All API endpoints have rate limiting
- Data export produces complete user data archive
- E2E tests cover critical user flows

## 7. Project Structure

```
StudyAgent/
├── plan/                           # Design documents (this directory)
├── src/
│   └── studyagent/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app entry point
│       ├── config.py               # Configuration management
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── router.py           # Intent routing agent
│       │   ├── tutor.py            # Core teaching agent
│       │   ├── quiz_generator.py   # Quiz generation agent
│       │   ├── scheduler.py        # FSRS-5 review scheduler
│       │   ├── knowledge_graph.py  # Knowledge graph builder
│       │   ├── analyzer.py         # Learning analytics agent
│       │   └── document_processor.py # Document ingestion agent
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── state.py            # LearningState definition
│       │   └── orchestrator.py     # LangGraph orchestration
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── conversation.py
│       │   ├── concept.py
│       │   ├── knowledge_state.py
│       │   ├── flashcard.py
│       │   ├── quiz.py
│       │   └── document.py
│       ├── algorithms/
│       │   ├── __init__.py
│       │   ├── fsrs.py             # FSRS-5 wrapper
│       │   ├── bkt.py              # Bayesian Knowledge Tracing
│       │   ├── dkt.py              # Deep Knowledge Tracing
│       │   ├── zpd.py              # ZPD estimation
│       │   └── path_optimizer.py   # Learning path optimization
│       ├── api/
│       │   ├── __init__.py
│       │   ├── chat.py             # Chat/streaming endpoints
│       │   ├── quiz.py             # Quiz endpoints
│       │   ├── review.py           # Review endpoints
│       │   ├── knowledge.py        # Knowledge graph endpoints
│       │   ├── analytics.py        # Progress/analytics endpoints
│       │   └── documents.py        # Document import endpoints
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── short_term.py       # Redis-backed STM
│       │   ├── long_term.py        # PostgreSQL-backed LTM
│       │   └── episodic.py         # Learning event logging
│       ├── tui/
│       │   ├── __init__.py
│       │   ├── app.py              # Main Textual app
│       │   ├── screens/
│       │   │   ├── chat.py         # Chat screen
│       │   │   ├── quiz.py         # Quiz screen
│       │   │   ├── review.py       # Review screen
│       │   │   └── dashboard.py    # Progress dashboard
│       │   └── widgets/
│       │       ├── knowledge_tree.py
│       │       ├── markdown_stream.py
│       │       └── review_panel.py
│       └── utils/
│           ├── __init__.py
│           ├── llm.py              # LLM provider abstraction
│           └── embeddings.py       # Embedding generation
├── web/                            # Next.js 16 frontend
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Dashboard
│   │   ├── learn/
│   │   │   └── page.tsx            # Learning chat
│   │   ├── review/
│   │   │   └── page.tsx            # Review mode
│   │   ├── progress/
│   │   │   └── page.tsx            # Analytics
│   │   └── knowledge-graph/
│   │       └── page.tsx            # Graph visualization
│   ├── components/
│   │   ├── chat/
│   │   ├── review/
│   │   ├── knowledge-graph/
│   │   └── analytics/
│   ├── lib/
│   │   └── api.ts                  # API client
│   └── package.json
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── alembic/                        # Database migrations
│   └── versions/
├── docker-compose.yaml
├── pyproject.toml
├── Makefile
└── README.md
```

## 8. Key Dependencies

```toml
# pyproject.toml [project.dependencies]
python = ">=3.12"
fastapi = ">=0.115"
uvicorn = {version = ">=0.30", extras = ["standard"]}
sqlalchemy = {version = ">=2.0", extras = ["asyncio"]}
aiosqlite = ">=0.20"
asyncpg = ">=0.30"
alembic = ">=1.13"
langgraph = ">=0.3"
langchain-core = ">=0.3"
litellm = ">=1.50"
fsrs = ">=4.0"
redis = {version = ">=5.0", extras = ["hiredis"]}
textual = ">=4.0"
rich = ">=13.9"
pydantic = ">=2.0"
structlog = ">=24.0"
celery = ">=5.4"
httpx = ">=0.27"
```

## 9. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM hallucination in teaching | High | Fact-check layer + domain validation + LLM-as-Judge |
| FSRS cold start (no data) | Medium | Default parameters from Anki community data |
| Knowledge graph quality | Medium | Human-in-the-loop confirmation for extracted concepts |
| TUI performance with long conversations | Low | Pagination + context window management |
| Local LLM quality insufficient | Medium | Cloud LLM fallback architecture |
| SQLite concurrency limits | Low | WAL mode + connection pooling; PostgreSQL for production |

## 10. Success Metrics

| Metric | Target (Phase 1) | Target (Phase 5) |
|--------|-------------------|-------------------|
| Concept explanation quality | 80% user satisfaction | 90% user satisfaction |
| Quiz difficulty calibration | +-0.15 of ZPD optimal | +-0.05 of ZPD optimal |
| FSRS prediction accuracy | 80% (default params) | 90% (personalized) |
| Learning velocity improvement | Baseline established | 30% vs unassisted study |
| User retention (30-day) | N/A | 60% |
| System response latency | <3s first token | <1s first token |
