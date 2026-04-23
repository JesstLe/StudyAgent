# StudyAgent Research Findings

> Version: 1.0 | Date: 2026-04-23 | Status: Reference

This document compiles all research findings that informed the StudyAgent design.

## 1. Agent Frameworks (2026 Landscape)

### Tier 1: Production-Ready

| Framework | Key Feature | Best For |
|-----------|-----------|----------|
| **LangGraph** | Graph-based orchestration, typed state, conditional edges, checkpointing | Complex multi-agent workflows (our choice) |
| **OpenAI Agents SDK** | 3 primitives (Agents, Handoffs, Tracing), 100+ models | Simple, reliable agent loops |
| **Claude Agent SDK** | Agentic loop pattern, same tools as Claude Code | Claude-native applications |
| **CrewAI** | Role-based multi-agent, easy Python API | Team-like agent collaboration |

### Tier 2: Specialized

| Framework | Key Feature |
|-----------|-----------|
| **Google ADK** | A2A protocol, Vertex AI integration |
| **AutoGen/AG2** | Microsoft-backed, multi-agent conversations |
| **Semantic Kernel** | Enterprise-grade, Python/C#/Java |
| **Pydantic AI** | Type-safe, validation-heavy |
| **Smolagents** | Lightweight minimal agents |

### Tier 3: Protocols

- **MCP (Model Context Protocol)**: "USB-C for AI" -- universal connector between LLMs and tools/data
- **A2A (Agent-to-Agent)**: Google's protocol for cross-framework agent communication

## 2. Agentic Design Patterns

### Anthropic's 6 Workflow Patterns

1. **Prompt Chaining**: Sequential steps with programmatic gates between LLM calls
2. **Routing**: Classify input, direct to specialized handler
3. **Parallelization**: Independent subtasks (sectioning) or multi-perspective voting
4. **Orchestrator-Workers**: Central LLM dynamically delegates to workers
5. **Evaluator-Optimizer**: Generate/critique loop with structured scoring
6. **Autonomous Agents**: LLM + tools + environmental feedback loop

### SitePoint's 6 Agentic Design Patterns (2026)

1. **Reflection (Self-Critique Loops)**: Generate -> Critique -> Refine cycle with score extraction and iteration caps
2. **Tool Use (Grounding Agents)**: Structured tool calling with schema validation (Zod), SQL injection prevention
3. **Planning (Decompose, Then Execute)**: Plan-and-Execute vs ReAct patterns; Planner/Executor/Replanner/Aggregator nodes
4. **Multi-Agent Collaboration**: Peer-to-Peer, Hierarchical, Debate topologies with message accumulation
5. **Orchestrator-Worker**: Dynamic fan-out with `Send` API for parallel worker execution
6. **Evaluator-Optimizer**: LLM-as-judge scoring with quality threshold routing

## 3. Memory Systems

### Three-Layer Architecture

| Layer | Storage | Content | TTL |
|-------|---------|---------|-----|
| **Short-term** | Redis | Conversation context, working memory | Session (24h) |
| **Long-term** | PostgreSQL + pgvector | Knowledge state, concept mastery, preferences | Persistent with invalidation triggers |
| **Episodic** | PostgreSQL (structured logs) | Learning events, breakthroughs, struggle patterns | 1 year (summarized) |

### Best Practice
"Every long-term write needs source + TTL + an invalidation trigger."

## 4. Spaced Repetition Algorithms

### SM-2 (Legacy, 1987)
- **E-Factor Formula**: `EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))`
- Initial EF = 2.5, minimum EF = 1.3
- Intervals: I(1)=1, I(2)=6, I(n)=I(n-1)*EF for n>2
- Quality scale: 0-5 (used by original Anki)

### FSRS-5 (Current Best, 2024-2026)
- Based on three-component memory model (Piotr Wozniak) + stochastic shortest path optimization
- 2 more parameters than FSRS-4.5; models same-day reviews
- Adapts to individual memory patterns
- Becoming default in Anki (late 2025/early 2026)
- Open-source: `py-fsrs` on PyPI, `open-spaced-repetition` on GitHub
- Rating scale: 1-4 (Again, Hard, Good, Easy)
- Tracks: stability, difficulty, elapsed_days, scheduled_days, reps, lapses, state

### Why FSRS-5 over SM-2
- More accurate forgetting curve modeling
- Individual parameter optimization from review history
- Stochastic shortest path optimality guarantee
- Active research community and regular improvements

## 5. Knowledge Tracing

### Bayesian Knowledge Tracing (BKT)
- Hidden Markov Model approach
- 4 parameters: P(L0), P(T), P(G), P(S)
- Binary mastery state (mastered / not mastered)
- Interpretable parameters
- Less data required

### Deep Knowledge Tracing (DKT)
- RNN/LSTM-based
- Continuous distributed representation
- Often outperforms BKT in prediction accuracy
- Requires more training data
- Less interpretable (black box)

### Recommendation for StudyAgent
- Use BKT initially (interpretable, less data needed)
- Add DKT later as data accumulates
- Hybrid: BKT for cold-start, DKT for established learners

## 6. Knowledge Graph for Education

### Key Concepts
- **Educational Knowledge Graphs (EduKGs)**: Specialized KGs with learning entity relationships
- **Prerequisite Relation Extraction**: Automated identification of concept ordering (LCPRE method)
- **Learning Path Optimization**: Graph-based shortest path / topological sort through concept dependencies
- **Skill Trees**: Game-like visualization of concept mastery (like tech trees in strategy games)

### Relevant Research
- **GraphMASAL**: Graph-based Multi-Agent System for Adaptive Learning (arXiv)
- **ACE**: AI-Assisted Construction of Educational Knowledge Graphs (JEDM)
- **KG-RAG**: Knowledge Graph-enhanced RAG for adaptive tutoring
- **OpenTutor**: Self-hosted AI learning platform with knowledge graph

## 7. Zone of Proximal Development (ZPD)

### Theory (Vygotsky)
- The gap between what a learner can do independently and with guidance
- Optimal learning occurs in this zone -- not too easy, not too hard

### Implementation in ITS
- Adaptive difficulty adjustment algorithms
- Dynamic difficulty calibration based on performance data
- Three-model architecture: Domain Model + Learner Model + Pedagogical Model

### 2026 Research
- **IncluLearn AI** (Frontiers in Education, 2026): User-centered adaptive tutoring with ZPD
- **ITS2026 Conference**: Dedicated to agentic AI in intelligent tutoring

## 8. AI-Enhanced Study Techniques

| Technique | Traditional Approach | AI Enhancement |
|-----------|---------------------|---------------|
| **Active Recall** | Self-testing, practice problems | AI-generated quizzes, adaptive questioning |
| **Feynman Technique** | Explain to a peer | AI as conversational tutor testing explanations |
| **Spaced Repetition** | Anki, physical flashcards | AI-generated cards, FSRS scheduling |
| **Pomodoro** | Timer-based sessions | AI-adaptive session length based on engagement |
| **Cornell Notes** | Manual note organization | AI-structured note extraction |
| **Elaborative Interrogation** | Self-questioning "why?" | AI-guided "why" chains probing understanding |
| **Mind Mapping** | Manual diagrams | AI-generated concept maps from study material |

## 9. Multi-Agent Intelligent Tutoring Systems (2025-2026 Research)

### Key Papers

1. **LLM-powered Multi-agent Framework for Goal-oriented ITS** (arXiv 2501.15749, Jan 2025)
   - Multi-agent framework for personalized goal-oriented learning
   - Career-specific goals, skill acquisition tracking
   - Framework: GenMentor

2. **Multi-Agentic LLMs for Personalizing STEM Texts** (MDPI, 2025)
   - Two agents: Profiler Agent + Rewrite Agent
   - Formal message-passing protocol between agents

3. **Agentic AI-Driven Tutoring** (ResearchGate, 2025)
   - Multi-agent cognitive architecture for personalized adaptive learning
   - Integration of ITS, multi-agent architecture, cognitive computing

### Agent Specialization Patterns
- **Profiler Agent**: Analyzes learner skills and knowledge gaps
- **Content Generator Agent**: Creates personalized learning materials
- **Assessment Agent**: Evaluates understanding through quizzes
- **Scheduler Agent**: Manages spaced repetition timing
- **Analytics Agent**: Tracks progress and identifies weak areas

## 10. Learning Analytics

### Dashboard Components
- **Progress Tracking**: Real-time visualization of concept mastery
- **Weakness Identification**: AI-powered pinpointing of struggle areas
- **Study Pattern Analysis**: Time-of-day, session frequency, duration trends
- **Motivation Metrics**: Streak tracking, achievement badges, engagement scores
- **Outcome Prediction**: ML models predicting learning trajectory

### Key Metrics
- Study time per domain/week
- Concepts mastered per unit time (learning velocity)
- Review accuracy (predicted vs actual recall)
- Quiz scores trend
- Knowledge decay rate
- Session completion rate

## 11. Multi-Modal Learning

### Capabilities
- **Text**: LLM-based understanding, concept extraction, summarization
- **PDF/Documents**: PyMuPDF/pdfplumber for text extraction, vision models for scanned content
- **Code**: AST parsing, semantic understanding, error analysis
- **Images/Diagrams**: Vision model understanding (GPT-4o, Claude)
- **Web Pages**: Content extraction, concept identification
- **Video** (future): Transcript analysis, key frame extraction

### Processing Pipeline
```
Document Input -> Content Extraction -> Concept Identification ->
  -> Knowledge Graph Update -> Flashcard Generation -> Learning Path Update
```

## 12. Agent Evaluation and Observability

### Tools (2026)
| Tool | Purpose |
|------|---------|
| **LangSmith** | Agent trajectory tracing, evaluation |
| **Langfuse** | Open-source alternative, tracing + evaluation |
| **Arize Phoenix** | ML observability for agents |
| **LLM-as-Judge** | Automated quality evaluation using a judge model |

### Metrics
- **Trajectory accuracy**: Did the agent follow the optimal path?
- **Tool usage efficiency**: Were tool calls necessary and correct?
- **Response quality**: Accuracy, clarity, adherence to teaching framework
- **Latency**: Time to first token, total response time
- **Cost**: Token usage per interaction

## 13. TUI and Web UI Research

### TUI (Textual v4+)
- `MarkdownStream` class for efficient streaming LLM output
- Async-first architecture (Python asyncio)
- CSS-like styling, responsive design
- Runs in terminal AND web browser
- Widget toolkit: tables, inputs, buttons, scrollable containers

### Web UI (Next.js 16 + Vercel AI SDK)
- `useChat` hook for streaming chat
- `streamText` / `streamUI` for server-side AI streaming
- Route Handlers (not Server Actions) for SSE streaming
- shadcn/ui + AI Elements for production-ready chat components
- SSE preferred over WebSocket for AI streaming (simpler, auto-reconnect)

### Backend (FastAPI 0.135+)
- Built-in SSE support via `EventSourceResponse`
- `ServerSentEvent` objects with event/id/retry control
- POST-based SSE for chat endpoints
- Auto keep-alive pings, Cache-Control headers

---

## Sources

### Agent Frameworks
- [Anthropic: Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)
- [SitePoint: Definitive Guide to Agentic Design Patterns 2026](https://www.sitepoint.com/the-definitive-guide-to-agentic-design-patterns-in-2026/)
- [Complete Guide to AI Agent Architectures 2026](https://agnt.gg/articles/the-complete-guide-to-ai-agent-architectures-2026)
- [Every AI Agent Architecture in One Place](https://pub.towardsai.net/every-ai-agent-architecture-in-one-place-595ba68d49cd)
- [AI Agent Systems Survey (arXiv)](https://arxiv.org/html/2601.01743v1)

### Spaced Repetition
- [FSRS Algorithm Wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- [FSRS PyPI](https://pypi.org/project/fsrs/)
- [FSRS GitHub](https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler)
- [SM-2 Algorithm (SuperMemo)](https://www-beta.supermemo.com/archives1990-2015/english/ol/sm2)
- [History of FSRS (LessWrong)](https://www.lesswrong.com/posts/G7fpGCi8r7nCKXsQk/the-history-of-fsrs-for-anki)

### Knowledge Tracing
- [Deep Knowledge Tracing (Stanford)](https://stanford.edu/~cpiech/bio/papers/deepKnowledgeTracing.pdf)
- [Knowledge Tracing Survey (arXiv)](https://arxiv.org/html/2105.15106v4)
- [BKT Overview (Emergent Mind)](https://www.emergentmind.com/topics/bayesian-knowledge-tracing)

### Intelligent Tutoring
- [LLM Multi-agent ITS (arXiv)](https://arxiv.org/abs/2501.15749)
- [Agentic AI-Driven Tutoring (ResearchGate)](https://www.researchgate.net/publication/400991247)
- [ITS2026 Conference](https://iis-international.org/its2026/)
- [IncluLearn AI (Frontiers 2026)](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2026.1783693/full)

### Knowledge Graphs for Education
- [LCPRE (ACM)](https://dl.acm.org/doi/10.1145/3627673.3679597)
- [Educational KGs (arXiv)](https://arxiv.org/abs/2509.05393)
- [ACE: AI-Assisted EduKG (JEDM)](https://jedm.educationaldatamining.org/index.php/JEDM/article/view/737)
- [Knowledge Graph for Learning Science (Chan Zuckerberg)](https://chanzuckerberg.com/blog/knowledge-graph-ai-education/)

### TUI and Web UI
- [Textual v4.0 Streaming Release](https://simonwillison.net/2025/Jul/22/textual-v4/)
- [Textual Documentation](https://textual.textualize.io/)
- [Next.js 16 AI Patterns](https://www.digitalapplied.com/blog/nextjs-16-ai-integration-patterns-guide)
- [Vercel AI SDK](https://ai-sdk.dev/v4/docs/ai-sdk-rsc/streaming-react-components)
- [shadcn/ui AI Chatbot](https://www.shadcn.io/ai/chatbot)
- [FastAPI SSE](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [Redis AI Agent Architecture](https://redis.io/blog/ai-agent-architecture/)
