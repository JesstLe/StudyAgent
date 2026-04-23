# StudyAgent Architecture Design

> Version: 1.0 | Date: 2026-04-23 | Status: Draft

## 1. Executive Summary

StudyAgent is an AI-powered learning assistant designed for a high-cognitive adult learner self-studying CS courses. It combines a CS tutor persona (with "Genetic Epistemology" teaching philosophy) with modern agentic AI architecture -- including multi-agent orchestration, memory-augmented reasoning, knowledge graph construction, spaced repetition, and adaptive learning paths.

The system provides both a TUI (terminal) and a Web UI, backed by a Python FastAPI server with PostgreSQL + pgvector for knowledge storage and Redis for session management.

## 2. Core Design Principles

1. **Knowledge is invented, not discovered** -- Follow the "Pain-Point Framework" (Prehistoric -> Naive Approach -> Solution) for all teaching.
2. **Multi-agent specialization** -- Different agents handle different cognitive tasks (teaching, quiz generation, knowledge tracing, scheduling).
3. **Memory-augmented cognition** -- Short-term (conversation), long-term (knowledge state), and episodic (learning history) memory systems.
4. **Adaptive difficulty via ZPD** -- Keep learners in their Zone of Proximal Development using knowledge tracing.
5. **Spaced repetition integration** -- FSRS-5 algorithm for optimal review scheduling.
6. **Local-first with cloud option** -- SQLite for local mode, PostgreSQL for production.

## 3. System Architecture Overview

```
+--------------------------------------------------+
|                   Client Layer                     |
|  +----------------+    +----------------------+   |
|  |  TUI (Textual)  |    |  Web UI (Next.js 16) |   |
|  +-------+--------+    +----------+-----------+   |
+----------|-------------------------|---------------+
           |  SSE / WebSocket        |
+----------v-------------------------v---------------+
|                API Gateway (FastAPI)                |
|  +----------------------------------------------+  |
|  |  Auth (JWT)  |  Rate Limit  |  Session Mgmt  |  |
|  +----------------------------------------------+  |
+----------|-----------------------------------------+
           |
+----------v-----------------------------------------+
|            Agent Orchestrator (LangGraph)           |
|                                                    |
|  +------------+  +-------------+  +--------------+ |
|  | Tutor      |  | Quiz        |  | Knowledge   | |
|  | Agent      |  | Generator   |  | Graph       | |
|  |            |  | Agent       |  | Agent       | |
|  +------------+  +-------------+  +--------------+ |
|                                                    |
|  +------------+  +-------------+  +--------------+ |
|  | Scheduler  |  | Analyzer    |  | Document    | |
|  | Agent      |  | Agent       |  | Processor   | |
|  | (FSRS-5)  |  |             |  | Agent       | |
|  +------------+  +-------------+  +--------------+ |
+----------|-----------------------------------------+
           |
+----------v-----------------------------------------+
|              Infrastructure Layer                   |
|  +----------+  +---------+  +------------------+   |
|  | PostgreSQL|  | Redis   |  | LLM Providers   |   |
|  | +pgvector |  | (cache/ |  | (OpenAI/Claude/ |   |
|  |           |  |  session)|  |  local Ollama)  |   |
|  +----------+  +---------+  +------------------+   |
+--------------------------------------------------+
```

## 4. Agent Architecture (LangGraph)

### 4.1 Why LangGraph

LangGraph is the #1 ranked agent framework in 2026:
- Graph-based orchestration with typed state
- Conditional edges for dynamic routing
- Built-in checkpointing for conversation persistence
- Human-in-the-loop support via interrupt/resume
- Python-native, excellent async support
- MCP integration for tool use

### 4.2 State Graph Design

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator

class LearningState(TypedDict):
    messages: Annotated[list, operator.add]
    current_topic: str | None
    knowledge_level: dict  # {concept: float} 0.0-1.0
    learning_objectives: list[str]
    pending_reviews: list[dict]
    active_session_type: Literal["teaching", "quiz", "review", "exploration"]
    zpd_zone: dict  # {lower: float, upper: float}
    concept_graph_diff: list[dict]  # Knowledge graph modifications

# Node definitions
graph = StateGraph(LearningState)

# Add nodes
graph.add_node("router", route_request)
graph.add_node("tutor", tutor_agent)
graph.add_node("quiz_generator", quiz_agent)
graph.add_node("review_scheduler", scheduler_agent)
graph.add_node("knowledge_tracer", knowledge_tracing_agent)
graph.add_node("analyzer", analyzer_agent)

# Edges
graph.set_entry_point("router")
graph.add_conditional_edges("router", route_by_intent, {
    "teach": "tutor",
    "quiz": "quiz_generator",
    "review": "review_scheduler",
    "analyze": "analyzer",
})
graph.add_edge("tutor", "knowledge_tracer")
graph.add_edge("quiz_generator", "knowledge_tracer")
graph.add_edge("review_scheduler", END)
graph.add_edge("knowledge_tracer", END)
graph.add_edge("analyzer", END)
```

### 4.3 Agent Specializations

#### Tutor Agent (Core Teaching Agent)
- **Persona**: CS tutor with Genetic Epistemology philosophy
- **System Prompt**: The "Pain-Point Framework" three-step protocol
- **Capabilities**:
  - Explain concepts using Prehistoric -> Naive -> Solution pattern
  - Generate engineering analogies (ADT vs physical implementation)
  - Cross-domain connections (CS <-> investing analogies)
  - Code demonstrations in C++ (Deng Junhui style)
- **Tools**: `explain_concept`, `generate_code_example`, `create_analogy`, `fetch_reference`
- **Memory**: Reads learner's knowledge state, adapts explanations to ZPD

#### Quiz Generator Agent
- **Purpose**: Create active recall questions, flashcards, and assessments
- **Capabilities**:
  - Generate multiple-choice, fill-in-blank, open-ended questions
  - Auto-generate flashcard decks from study material
  - Feynman technique prompts ("explain this to a 5-year-old")
  - Difficulty calibrated to learner's ZPD
- **Tools**: `generate_flashcards`, `create_quiz`, `evaluate_answer`
- **Output Format**: JSON flashcards compatible with FSRS scheduler

#### Knowledge Graph Agent
- **Purpose**: Build and maintain prerequisite/dependency graphs
- **Capabilities**:
  - Extract concept relationships from study material
  - Build prerequisite chains (what must be learned before what)
  - Identify knowledge gaps
  - Recommend optimal learning paths
  - Generate "skill tree" visualizations
- **Tools**: `add_concept`, `add_prerequisite`, `find_gaps`, `recommend_path`
- **Storage**: Neo4j or PostgreSQL adjacency list + pgvector embeddings

#### Scheduler Agent (FSRS-5)
- **Purpose**: Manage spaced repetition scheduling
- **Algorithm**: FSRS-5 (Free Spaced Repetition Scheduler)
  - Based on three-component memory model (Piotr Wozniak)
  - Stochastic shortest path optimization
  - Models same-day reviews (FSRS-5 improvement over FSRS-4.5)
  - Adapts to individual memory patterns
- **Tools**: `schedule_review`, `get_due_reviews`, `update_memory_state`

#### Analyzer Agent
- **Purpose**: Learning analytics and progress tracking
- **Capabilities**:
  - Track study time, session frequency
  - Identify weak areas (low knowledge_level concepts)
  - Predict learning outcomes
  - Generate progress reports
  - Motivation/engagement metrics
- **Tools**: `get_progress`, `get_weak_areas`, `predict_outcomes`

#### Document Processor Agent
- **Purpose**: Multi-modal content ingestion
- **Capabilities**:
  - PDF parsing and concept extraction
  - Web page content analysis
  - Code repository analysis
  - Image/diagram understanding (via vision model)
- **Tools**: `process_pdf`, `process_url`, `process_code`, `extract_concepts`

### 4.4 Agentic Design Patterns Used

| Pattern | Application |
|---------|-------------|
| **Prompt Chaining** | Document -> Extract Concepts -> Build Knowledge Graph -> Generate Learning Path |
| **Routing** | User intent classification -> specialized agent dispatch |
| **Parallelization** | Simultaneous quiz generation + knowledge tracing + scheduling |
| **Orchestrator-Worker** | Tutor agent delegates sub-tasks (code example, analogy, quiz) |
| **Evaluator-Optimizer** | Quiz answer evaluation -> knowledge state update -> difficulty adjustment |
| **Reflection** | Tutor reviews its own explanation quality, refines approach |
| **Memory-Augmented** | Knowledge state persists across sessions, adapts teaching |

## 5. Memory System Architecture

### 5.1 Three-Layer Memory Model

```
+---------------------------+
|   Short-Term Memory       |  Redis (TTL: session duration)
|   - Current conversation   |  - Active messages
|   - Working context        |  - Current ZPD state
|   - Session state          |  - Temporary calculations
+---------------------------+
            |
            v  (consolidate every N turns)
+---------------------------+
|   Long-Term Memory        |  PostgreSQL + pgvector
|   - Knowledge state        |  - Concept mastery levels
|   - Concept embeddings     |  - Prerequisite relationships
|   - Learning preferences   |  - Review history
|   - Weak areas             |  - Semantic search index
+---------------------------+
            |
            v  (summarize periodically)
+---------------------------+
|   Episodic Memory         |  PostgreSQL (structured logs)
|   - Session summaries      |  - Learning events
|   - Breakthrough moments   |  - Struggle patterns
|   - Study patterns         |  - Time-series analytics
+---------------------------+
```

### 5.2 Memory Operations

**Write Rule**: Every long-term memory write requires:
- Source tracking (which interaction produced this knowledge)
- TTL or invalidation trigger (when might this become stale)
- Confidence score (how certain is this assessment)

**Read Pattern**: On each interaction:
1. Load learner profile from long-term memory
2. Load active session context from short-term memory
3. Retrieve relevant episodic memories (recent struggles, recent breakthroughs)
4. Construct rich context for the agent

## 6. Knowledge Graph Design

### 6.1 Graph Schema

```sql
-- Concepts (nodes)
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,  -- 'data_structures', 'algorithms', 'os', etc.
    description TEXT,
    difficulty FLOAT DEFAULT 0.5,  -- 0.0 (easy) to 1.0 (hard)
    embedding VECTOR(1536),  -- pgvector for semantic search
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Relationships (edges)
CREATE TABLE concept_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_concept_id UUID REFERENCES concepts(id),
    target_concept_id UUID REFERENCES concepts(id),
    relation_type TEXT NOT NULL,  -- 'prerequisite', 'related', 'part_of', 'builds_on'
    strength FLOAT DEFAULT 1.0,  -- 0.0 to 1.0
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Learner knowledge state
CREATE TABLE knowledge_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    concept_id UUID NOT NULL REFERENCES concepts(id),
    mastery_level FLOAT NOT NULL DEFAULT 0.0,  -- 0.0 to 1.0 (DKT-style continuous)
    confidence FLOAT NOT NULL DEFAULT 0.0,
    last_assessed_at TIMESTAMPTZ,
    review_count INT DEFAULT 0,
    next_review_at TIMESTAMPTZ,
    fsrs_state JSONB,  -- FSRS-5 algorithm state (stability, difficulty, etc.)
    UNIQUE(user_id, concept_id)
);
```

### 6.2 Knowledge Tracing

Implement a hybrid approach:

1. **Bayesian Knowledge Tracing (BKT)** for initial modeling
   - Probabilistic: P(L) = P(L|correct) or P(L|incorrect)
   - Four parameters: P(L0), P(T), P(G), P(S)
   - Interpretable parameters with clear meaning

2. **Deep Knowledge Tracing (DKT)** for production refinement
   - RNN/LSTM-based continuous mastery estimation
   - Continuous representation (not binary mastered/not-mastered)
   - Better prediction accuracy with sufficient data

3. **FSRS-5 Integration** for review scheduling
   - Uses knowledge state to determine optimal review intervals
   - Adapts to individual forgetting curves

### 6.3 ZPD Estimation

```python
def estimate_zpd(learner_state: dict, concept: Concept) -> dict:
    """Estimate Zone of Proximal Development for a concept."""
    current_mastery = learner_state.get("mastery_level", 0.0)
    prerequisites = get_prerequisites(concept)

    # ZPD lower bound: learner can do with scaffolding
    zpd_lower = current_mastery

    # ZPD upper bound: next challengeable level
    prereq_mastery = min(
        learner_state.get(p.name, 0.0) for p in prerequisites
    ) if prerequisites else current_mastery
    zpd_upper = min(prereq_mastery + 0.3, 1.0)

    return {
        "lower": zpd_lower,
        "upper": zpd_upper,
        "optimal_difficulty": (zpd_lower + zpd_upper) / 2,
        "is_in_zpd": zpd_lower < 0.7 < zpd_upper
    }
```

## 7. MCP (Model Context Protocol) Integration

### 7.1 MCP Tools for StudyAgent

```yaml
# MCP server configuration
tools:
  - name: explain_concept
    description: "Explain a CS concept using the Pain-Point Framework"
    parameters:
      concept: { type: string, required: true }
      depth: { type: string, enum: [overview, detailed, deep_dive] }

  - name: generate_quiz
    description: "Generate quiz questions for a concept"
    parameters:
      concept: { type: string, required: true }
      format: { type: string, enum: [multiple_choice, fill_blank, open_ended] }
      difficulty: { type: float, min: 0.0, max: 1.0 }
      count: { type: integer, default: 5 }

  - name: get_review_schedule
    description: "Get due spaced repetition reviews"
    parameters:
      limit: { type: integer, default: 20 }
      concept_filter: { type: string }

  - name: submit_review_result
    description: "Submit a review result to update FSRS state"
    parameters:
      card_id: { type: string, required: true }
      rating: { type: integer, min: 1, max: 4 }  # FSRS rating scale

  - name: get_learning_path
    description: "Get recommended learning path for a domain"
    parameters:
      domain: { type: string, required: true }
      goal: { type: string }

  - name: get_progress_report
    description: "Get learning analytics and progress"
    parameters:
      time_range: { type: string, enum: [week, month, quarter] }
      domain: { type: string }

  - name: process_document
    description: "Ingest and process a learning document"
    parameters:
      source_type: { type: string, enum: [pdf, url, code, text] }
      source: { type: string, required: true }
```

## 8. Protocol Integration

### 8.1 MCP (Model Context Protocol)
- "USB-C for AI" -- universal connector between LLM and tools/data
- Used for all tool invocations within StudyAgent
- Enables future extensibility (add new tools without changing agent logic)

### 8.2 A2A (Agent-to-Agent Protocol)
- Google's open protocol for cross-framework agent communication
- Future use: allow StudyAgent to collaborate with other agents
- Enables specialized external agents (e.g., code execution agent)

## 9. Observability and Evaluation

### 9.1 Tracing
- **LangSmith** / **Langfuse** for agent trajectory tracing
- Track: LLM calls, tool usage, handoffs, guardrails, latency
- Visualize agent decision paths for debugging

### 9.2 Evaluation Metrics
- Teaching quality: learner comprehension scores before/after sessions
- Quiz effectiveness: item discrimination, difficulty calibration
- Review accuracy: FSRS predicted vs actual recall rates
- Engagement: session frequency, duration, completion rates
- Learning velocity: concepts mastered per unit time

### 9.3 LLM-as-Judge
- Periodic evaluation of tutor explanations using a judge model
- Scoring rubric: accuracy, clarity, adherence to Pain-Point Framework
- Automated quality checks on generated quiz questions

---

## Sources

- [Anthropic: Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)
- [SitePoint: Definitive Guide to Agentic Design Patterns 2026](https://www.sitepoint.com/the-definitive-guide-to-agentic-design-patterns-in-2026/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FSRS Algorithm Wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- [FSRS PyPI Package](https://pypi.org/project/fsrs/)
- [Deep Knowledge Tracing (Stanford)](https://stanford.edu/~cpiech/bio/papers/deepKnowledgeTracing.pdf)
- [Knowledge Tracing Survey (arXiv)](https://arxiv.org/html/2105.15106v4)
- [LLM-powered Multi-agent Framework for ITS](https://arxiv.org/abs/2501.15749)
- [Agentic AI-Driven Tutoring (ResearchGate)](https://www.researchgate.net/publication/400991247)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Google A2A Protocol](https://github.com/google/A2A)
- [Redis AI Agent Architecture](https://redis.io/blog/ai-agent-architecture/)
