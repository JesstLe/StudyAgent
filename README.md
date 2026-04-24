# StudyAgent

AI-powered CS learning agent with the **Pain-Point Framework** teaching philosophy — knowledge is explained through the lens of the specific historical pain point that motivated its invention.

## Architecture

```
Client Layer:   TUI (Textual)  |  Web UI (Next.js 16)
                        ↓ SSE / REST
API Layer:       FastAPI + Rate Limiting
                        ↓
Agent Layer:     LangGraph Orchestrator
                 ├── Tutor Agent (Pain-Point Framework)
                 ├── Quiz Agent (ZPD-adaptive)
                 ├── Scheduler Agent (FSRS-5)
                 ├── Knowledge Graph Agent
                 └── Analyzer Agent (BKT)
                        ↓
Infrastructure:  SQLite / PostgreSQL  |  Redis (cache)
                 Kimi Code API / OpenAI / Ollama
```

## Quick Start

### Backend

```bash
# Install dependencies
uv sync

# Seed knowledge graph (39 CS concepts)
uv run python -m studyagent.db.seed

# Start API server
uv run studyagent-server

# Or start TUI
uv run studyagent
```

### Web UI

```bash
cd web
npm install
npm run dev
# Open http://localhost:3000
```

### Docker (Production)

```bash
docker-compose up -d
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | `openai`, `anthropic`, or `ollama` |
| `LLM_MODEL` | `kimi-for-coding` | Model ID |
| `LLM_API_KEY` | — | API key |
| `LLM_BASE_URL` | — | Base URL for OpenAI-compatible APIs |
| `DATABASE_URL` | SQLite local | PostgreSQL for production |
| `REDIS_URL` | — | Redis for caching/rate limiting |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat/stream` | SSE streaming chat |
| POST | `/api/v1/conversations` | Create conversation |
| GET | `/api/v1/conversations` | List conversations |
| GET | `/api/v1/concepts` | List CS concepts |
| POST | `/api/v1/concepts/extract` | Extract concepts from text |
| POST | `/api/v1/decks` | Create flashcard deck |
| GET | `/api/v1/decks/{id}/due` | Get due flashcards |
| GET | `/api/v1/reviews/due` | Get due reviews |
| POST | `/api/v1/reviews/submit` | Submit review with FSRS grade |
| POST | `/api/v1/quiz/generate` | Generate quiz questions |
| POST | `/api/v1/quiz/submit` | Submit quiz answers |
| GET | `/api/v1/analytics/{uid}/overview` | Learning overview |
| GET | `/api/v1/analytics/{uid}/weak-areas` | Weak areas |
| GET | `/api/v1/analytics/{uid}/recommendations` | Recommended topics |
| GET | `/health` | Health check |

## Algorithms

- **BKT** (Bayesian Knowledge Tracing): Tracks concept mastery probability
- **FSRS-5** (Free Spaced Repetition Scheduler): Optimizes review intervals
- **ZPD** (Zone of Proximal Development): Adaptive difficulty estimation
- **Pain-Point Framework**: Three-step teaching protocol (史前时代 → 笨办法 → 救世主登场)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+ / FastAPI / LangGraph / LiteLLM / SQLAlchemy 2.0 |
| Frontend | Next.js 16 / TypeScript / Tailwind CSS 4 / Zustand |
| TUI | Textual 4+ / Rich |
| Database | SQLite (dev) / PostgreSQL + pgvector (prod) |
| Cache | Redis 7 |
| CI/CD | GitHub Actions |

## Testing

```bash
uv run pytest tests/ -v
# 58 tests covering algorithms, agents, API endpoints, and DB operations
```

## License

MIT
