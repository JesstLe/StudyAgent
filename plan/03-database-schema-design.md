# StudyAgent Database Schema Design

> Version: 1.0 | Date: 2026-04-23 | Status: Draft

## 1. Database Strategy

StudyAgent uses a dual-database approach:

| Database | Role | Technology |
|----------|------|-----------|
| Primary Store | Relational data, knowledge graph, analytics | PostgreSQL 16+ with pgvector |
| Cache / Sessions | Hot data, session state, rate limiting | Redis 7+ |
| Local Mode | Offline/desktop development | SQLite + sqlite-vec |

## 2. PostgreSQL Schema

### 2.1 Users and Authentication

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT,  -- NULL for OAuth users
    display_name TEXT,
    avatar_url TEXT,

    -- Learning preferences
    preferred_language TEXT DEFAULT 'zh-CN',
    default_programming_lang TEXT DEFAULT 'cpp',
    learning_style TEXT DEFAULT 'socratic',  -- 'socratic', 'direct', 'discovery'

    -- FSRS parameters (personalized)
    fsrs_parameters JSONB DEFAULT '{
        "w": [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.22, 0.99, 0.06, 0.36],
        "request_retention": 0.9,
        "maximum_interval": 365
    }',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- OAuth connections
CREATE TABLE oauth_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,  -- 'google', 'github'
    provider_id TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    UNIQUE(provider, provider_id)
);

-- Sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 Conversations and Messages

```sql
-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    session_type TEXT DEFAULT 'teaching',  -- 'teaching', 'quiz', 'review', 'exploration'

    -- Context
    active_domain TEXT,  -- 'data_structures', 'algorithms', 'os', etc.
    active_concepts TEXT[],  -- concepts discussed in this conversation

    -- Metadata
    message_count INT DEFAULT 0,
    tokens_used INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id, updated_at DESC);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),

    -- Content
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'markdown',  -- 'markdown', 'code', 'quiz', 'flashcard'

    -- Metadata
    model TEXT,  -- which LLM model generated this
    tokens_in INT,
    tokens_out INT,
    latency_ms INT,

    -- Tool usage tracking
    tool_calls JSONB DEFAULT '[]',  -- [{name, args, result}]
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_role ON messages(role);
```

### 2.3 Knowledge Graph

```sql
-- CS Concepts
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    domain TEXT NOT NULL,  -- 'data_structures', 'algorithms', 'os', 'networks', 'math', 'cpp'

    -- Content
    description TEXT,
    key_ideas TEXT[],  -- bullet points of core ideas
    common_misconceptions TEXT[],
    related_analogies TEXT[],

    -- Classification
    difficulty FLOAT DEFAULT 0.5 CHECK (difficulty BETWEEN 0.0 AND 1.0),
    importance FLOAT DEFAULT 0.5 CHECK (importance BETWEEN 0.0 AND 1.0),

    -- Reference material
    textbook_references JSONB DEFAULT '[]',  -- [{book, chapter, section}]
    code_examples JSONB DEFAULT '[]',  -- [{title, language, code}]

    -- Semantic embedding for search
    embedding vector(1536),

    -- Metadata
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(name, domain)
);

CREATE INDEX idx_concepts_domain ON concepts(domain);
CREATE INDEX idx_concepts_embedding ON concepts USING ivfflat (embedding vector_cosine_ops);

-- Concept relationships (directed graph)
CREATE TABLE concept_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL CHECK (relation_type IN (
        'prerequisite',     -- A must be learned before B
        'builds_on',        -- B extends A
        'related',          -- A and B are related concepts
        'part_of',          -- A is a subtopic of B
        'contrasts_with',   -- A and B are alternatives to compare
        'depends_on'        -- A depends on B (runtime/implementation dependency)
    )),
    strength FLOAT DEFAULT 1.0 CHECK (strength BETWEEN 0.0 AND 1.0),
    description TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(source_id, target_id, relation_type)
);

CREATE INDEX idx_relations_source ON concept_relations(source_id);
CREATE INDEX idx_relations_target ON concept_relations(target_id);
CREATE INDEX idx_relations_type ON concept_relations(relation_type);
```

### 2.4 Knowledge State and Spaced Repetition

```sql
-- Learner's knowledge state per concept
CREATE TABLE knowledge_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,

    -- Mastery tracking (DKT-style continuous)
    mastery_level FLOAT NOT NULL DEFAULT 0.0 CHECK (mastery_level BETWEEN 0.0 AND 1.0),
    confidence FLOAT NOT NULL DEFAULT 0.0 CHECK (confidence BETWEEN 0.0 AND 1.0),

    -- BKT parameters
    bkt_state JSONB DEFAULT '{
        "p_L0": 0.1,
        "p_T": 0.1,
        "p_G": 0.2,
        "p_S": 0.1,
        "p_L_current": 0.1
    }',

    -- FSRS-5 state
    fsrs_state JSONB DEFAULT '{
        "stability": 0.0,
        "difficulty": 0.0,
        "elapsed_days": 0,
        "scheduled_days": 0,
        "reps": 0,
        "lapses": 0,
        "state": "New",  -- New, Learning, Review, Relearning
        "last_review": null
    }',

    -- Assessment history
    total_assessments INT DEFAULT 0,
    correct_assessments INT DEFAULT 0,
    last_assessed_at TIMESTAMPTZ,
    next_review_at TIMESTAMPTZ,

    -- ZPD
    zpd_zone JSONB DEFAULT '{"lower": 0.0, "upper": 0.3}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, concept_id)
);

CREATE INDEX idx_knowledge_user ON knowledge_state(user_id);
CREATE INDEX idx_knowledge_concept ON knowledge_state(concept_id);
CREATE INDEX idx_knowledge_review ON knowledge_state(user_id, next_review_at)
    WHERE next_review_at IS NOT NULL;
```

### 2.5 Flashcards and Quizzes

```sql
-- Flashcard decks
CREATE TABLE flashcard_decks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    description TEXT,
    concept_ids UUID[],  -- concepts covered by this deck
    source_type TEXT DEFAULT 'ai_generated',  -- 'ai_generated', 'manual', 'document_extract'
    source_document_id UUID,

    card_count INT DEFAULT 0,
    tags TEXT[],

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Flashcards
CREATE TABLE flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deck_id UUID NOT NULL REFERENCES flashcard_decks(id) ON DELETE CASCADE,

    -- Card content
    card_type TEXT NOT NULL CHECK (card_type IN (
        'basic',           -- front/back
        'cloze',           -- fill in the blank
        'multiple_choice', -- question + options + correct answer
        'code_output',     -- predict output of code
        'explain_concept'  -- open-ended explanation prompt
    )),

    front TEXT NOT NULL,      -- question / prompt
    back TEXT NOT NULL,       -- answer / explanation
    extra TEXT,               -- additional context or hints

    -- For multiple choice
    options JSONB,            -- [{label, text, is_correct}]

    -- Concept linkage
    concept_id UUID REFERENCES concepts(id),

    -- Difficulty
    difficulty FLOAT DEFAULT 0.5 CHECK (difficulty BETWEEN 0.0 AND 1.0),

    -- FSRS scheduling state (per-card)
    fsrs_state JSONB DEFAULT '{
        "stability": 0.0,
        "difficulty": 0.0,
        "elapsed_days": 0,
        "scheduled_days": 0,
        "reps": 0,
        "lapses": 0,
        "state": "New",
        "last_review": null
    }',
    next_review_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_flashcards_deck ON flashcards(deck_id);
CREATE INDEX idx_flashcards_review ON flashcards(deck_id, next_review_at)
    WHERE next_review_at IS NOT NULL;

-- Quiz attempts
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),

    quiz_type TEXT NOT NULL,  -- 'adaptive', 'comprehensive', 'targeted'
    concept_ids UUID[],
    total_questions INT NOT NULL,
    correct_answers INT NOT NULL DEFAULT 0,

    -- Results
    score FLOAT,  -- 0.0 to 1.0
    time_spent_seconds INT,

    -- Detailed results
    answers JSONB DEFAULT '[]',  -- [{card_id, answer, correct, time_ms}]

    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

### 2.6 Documents and Content

```sql
-- Uploaded documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    title TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('pdf', 'url', 'text', 'code')),
    source_url TEXT,        -- for URLs
    file_path TEXT,         -- for uploaded files
    file_size INT,

    -- Processing status
    processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN (
        'pending', 'processing', 'completed', 'failed'
    )),
    processed_at TIMESTAMPTZ,

    -- Extracted content
    raw_text TEXT,
    summary TEXT,
    extracted_concepts UUID[],  -- references to concepts table

    -- Embedding for document-level search
    embedding vector(1536),

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);
```

### 2.7 Analytics

```sql
-- Study sessions (time tracking)
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),

    session_type TEXT NOT NULL,  -- 'teaching', 'quiz', 'review', 'reading'
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    -- Metrics
    duration_seconds INT,
    messages_exchanged INT DEFAULT 0,
    concepts_covered UUID[],
    tokens_used INT DEFAULT 0,

    -- Engagement
    focus_score FLOAT,  -- 0.0-1.0, derived from interaction patterns
    satisfaction_rating INT CHECK (satisfaction_rating BETWEEN 1 AND 5)
);

CREATE INDEX idx_sessions_user_time ON study_sessions(user_id, started_at DESC);

-- Learning events (for episodic memory and analytics)
CREATE TABLE learning_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES study_sessions(id),

    event_type TEXT NOT NULL,  -- 'concept_learned', 'quiz_answered', 'review_completed',
                               -- 'breakthrough', 'struggle', ' misconception_corrected'
    concept_id UUID REFERENCES concepts(id),

    -- Event data
    data JSONB NOT NULL DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_user_time ON learning_events(user_id, created_at DESC);
CREATE INDEX idx_events_type ON learning_events(user_id, event_type);
```

## 3. Redis Schema

### 3.1 Key Structure

```
# Session state
session:{session_id}:context       -> JSON (active conversation context, TTL: 24h)
session:{session_id}:agent_state   -> JSON (current agent state, TTL: 24h)

# Active conversation buffer
conversation:{conv_id}:messages    -> LIST (recent messages, TTL: 1h)
conversation:{conv_id}:working_mem -> JSON (extracted context, TTL: 1h)

# Rate limiting
ratelimit:{user_id}:global         -> counter (sliding window)
ratelimit:{user_id}:chat           -> counter (per-endpoint)

# Semantic cache
cache:query:{hash}                 -> JSON (cached LLM response, TTL: 1h)

# Real-time state
user:{user_id}:online              -> SET (active WebSocket connections)
user:{user_id}:streak              -> STRING (current streak count)
```

## 4. Entity Relationship Summary

```
users 1--* conversations 1--* messages
users 1--* knowledge_state *--1 concepts
users 1--* flashcard_decks 1--* flashcards
users 1--* study_sessions 1--* learning_events
users 1--* documents
users 1--* quiz_attempts

concepts 1--* concept_relations *--1 concepts  (self-referential graph)
concepts 1--* knowledge_state
concepts 1--* flashcards

flashcard_decks *--* concepts (via flashcards.concept_id)
documents *--* concepts (via extracted_concepts array)
```

## 5. Migration Strategy

Use Alembic for database migrations:

```
alembic/
  versions/
    001_initial_schema.py        -- users, conversations, messages
    002_knowledge_graph.py       -- concepts, concept_relations
    003_knowledge_state.py       -- knowledge_state with FSRS
    004_flashcards.py            -- flashcard_decks, flashcards
    005_documents.py             -- documents with embeddings
    006_analytics.py             -- study_sessions, learning_events
    007_pgvector_setup.py        -- enable pgvector, create IVFFlat indexes
```

---

## Sources

- [PostgreSQL pgvector Documentation](https://github.com/pgvector/pgvector)
- [FSRS Algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- [Deep Knowledge Tracing](https://stanford.edu/~cpiech/bio/papers/deepKnowledgeTracing.pdf)
- [Redis AI Agent Patterns](https://redis.io/blog/ai-agent-architecture-patterns/)
- [FastAPI + SQLAlchemy Best Practices](https://fastapi.tiangolo.com/tutorial/sql-databases/)
