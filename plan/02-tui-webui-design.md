# StudyAgent TUI and Web UI Design

> Version: 1.0 | Date: 2026-04-23 | Status: Draft

## 1. Dual Interface Strategy

StudyAgent provides two user interfaces sharing a common backend API:

| Aspect | TUI (Terminal) | Web UI |
|--------|---------------|--------|
| **Framework** | Textual v4+ (Python) | Next.js 16 + Vercel AI SDK |
| **Primary Use** | Daily study sessions, quick Q&A | Analytics dashboard, document upload, knowledge graph |
| **Streaming** | SSE via async HTTP | SSE via Vercel AI SDK Route Handlers |
| **Offline** | Full offline with SQLite | Requires server |
| **Audience** | Developer/terminal user | Any browser user |

## 2. TUI Design (Textual)

### 2.1 Main Layout

```
+----------------------------------------------------------+
| StudyAgent v1.0          [Teaching] [Quiz] [Review] [Help]|  <- Header with mode tabs
+----------------------------------------------------------+
|                                                          |
|  You: What is a B-tree? Why not just use a hash table?  |
|                                                          |
|  Tutor: Let me take you back to 1970...                  |
|                                                          |
|  ## [The Prehistoric Era]                                |
|  Databases were stored on spinning disks. Seeking to     |
|  a specific position was INSANELY slow -- think of       |
|  finding a specific frame on a VHS tape...               |
|                                                          |
|  ## [The Naive Approach]                                 |
|  Use a sorted array! Binary search is O(log n).          |
|  But insertion requires shifting ALL elements after       |
|  the insertion point. For a 1GB database, that's         |
|  catastrophic...                                         |
|                                                          |
|  ## [The B-Tree: Disk's Best Friend]                     |
|  B-trees solve this by keeping nodes fat (many keys      |
|  per node) and shallow (few levels).                      |
|                                                          |
|  Trade-off: Wastes some memory (nodes aren't full)       |
|  to guarantee every disk read counts.                     |
|                                                          |
+----------------------------------------------------------+
| > Ask a question...                          [Send] [Tab]|  <- Input bar
+----------------------------------------------------------+
| Knowledge: ████████░░ 80% | Reviews Due: 5 | Streak: 12|  <- Status bar
+----------------------------------------------------------+
```

### 2.2 TUI Screens

#### Chat Screen (Default)
- Main teaching/learning conversation with streaming markdown
- Mode tabs to switch between Teaching, Quiz, Review, Exploration
- Status bar showing knowledge level, due reviews, streak

#### Review Screen
```
+----------------------------------------------------------+
|  Spaced Repetition Review                    [3 of 15]   |
+----------------------------------------------------------+
|                                                          |
|  Q: What is the amortized time complexity of             |
|     a vector's push_back operation?                      |
|                                                          |
|  [Show Answer]                                           |
|                                                          |
|  --- After revealing answer ---                          |
|                                                          |
|  A: O(1) amortized. While individual operations may      |
|  trigger a full reallocation (O(n)), the geometric       |
|  growth strategy (doubling capacity) ensures that         |
|  expensive operations are rare enough to average O(1).   |
|                                                          |
|  Rate your recall:                                       |
|  [1:Again] [2:Hard] [3:Good] [4:Easy]                   |
+----------------------------------------------------------+
```

#### Progress Dashboard
```
+----------------------------------------------------------+
|  Learning Progress                      Last 30 days     |
+----------------------------------------------------------+
|                                                          |
|  Data Structures:  ████████████████░░░░ 78%              |
|    - Arrays/Linked Lists:  ████████████████████ 95%      |
|    - Trees (BST/AVL):      ██████████████░░░░░ 70%      |
|    - Graphs:               ████████░░░░░░░░░░ 40%       |
|    - Hash Tables:          ████████████████████ 90%       |
|                                                          |
|  Algorithms:       ██████████░░░░░░░░░░░░ 50%            |
|    - Sorting:               ██████████████████░ 85%      |
|    - Dynamic Programming:   ████░░░░░░░░░░░░░░ 20%       |
|                                                          |
|  Weekly Study: 3.2 hrs avg | Streak: 12 days            |
|  Next Review: B-tree operations (in 2 hours)             |
+----------------------------------------------------------+
```

### 2.3 TUI Implementation Pattern

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, TabbedContent, TabPane
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import MarkdownViewer, Button, ProgressBar

class StudyAgentApp(App):
    """StudyAgent TUI Application."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #chat-area {
        height: 1fr;
        padding: 1;
    }
    #input-area {
        dock: bottom;
        height: auto;
        padding: 0 1;
    }
    #status-bar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "toggle_review", "Review"),
        ("ctrl+d", "show_dashboard", "Dashboard"),
        ("ctrl+n", "new_conversation", "New Chat"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Teach", id="teach-tab"):
                yield VerticalScroll(id="chat-area")
                yield Input(
                    placeholder="Ask a question about CS...",
                    id="chat-input"
                )
            with TabPane("Review", id="review-tab"):
                yield ReviewWidget()
            with TabPane("Progress", id="progress-tab"):
                yield ProgressDashboard()
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_msg = event.value
        event.input.value = ""
        chat_area = self.query_one("#chat-area")

        # Display user message
        user_widget = Static(f"You: {user_msg}")
        chat_area.mount(user_widget)

        # Stream AI response
        response_widget = MarkdownViewer()
        chat_area.mount(response_widget)

        async for chunk in stream_tutor_response(user_msg):
            response_widget.append(chunk)

        chat_area.scroll_end(animate=False)
```

## 3. Web UI Design (Next.js 16)

### 3.1 Page Structure

```
/                          -> Landing / Login
/dashboard                 -> Learning analytics dashboard
/chat                      -> Main teaching conversation
/chat/[conversation_id]    -> Specific conversation
/review                    -> Spaced repetition review session
/knowledge-graph           -> Interactive concept graph visualization
/knowledge-graph/[concept] -> Concept detail page
/documents                 -> Upload and manage study materials
/settings                  -> Preferences and configuration
```

### 3.2 Dashboard Page

```
+------------------------------------------------------------------+
| StudyAgent    [Dashboard] [Chat] [Review] [Graph] [Docs] [Settings]|
+------------------------------------------------------------------+
|                                                                  |
|  +---------------------+  +---------------------+               |
|  | Today's Progress     |  | Reviews Due          |               |
|  | Studied: 1.5 hrs     |  | 12 cards due today   |               |
|  | Concepts: 3 new      |  | Next: B-tree insert  |               |
|  | Streak: 12 days      |  | [Start Review]       |               |
|  +---------------------+  +---------------------+               |
|                                                                  |
|  +--------------------------------------------------------------+|
|  | Knowledge Map (Interactive)                                  ||
|  |                                                              ||
|  |   [Arrays]--->[Linked Lists]--->[Stacks/Queues]             ||
|  |       |                                    |                 ||
|  |       v                                    v                 ||
|  |   [Hash Tables]              [Trees: BST/AVL/Red-Black]     ||
|  |       |                              |          |            ||
|  |       v                              v          v            ||
|  |   [Bloom Filters]            [B-Trees]   [Heaps]            ||
|  |                                                              ||
|  |   Green=mastered  Yellow=learning  Red=weak  Gray=unstarted  ||
|  +--------------------------------------------------------------+|
|                                                                  |
|  +---------------------+  +---------------------+               |
|  | Weak Areas           |  | Study Trend          |               |
|  | 1. Dynamic Prog. 20%|  | [Line chart: hours    |               |
|  | 2. Graphs 40%       |  |  per day, last 30d]   |               |
|  | 3. NP-Complete 25%  |  |                       |               |
|  +---------------------+  +---------------------+               |
+------------------------------------------------------------------+
```

### 3.3 Chat Page

```
+------------------------------------------------------------------+
| [Sidebar]     |  Teaching: Data Structures                        |
| Conversations |                                                   |
| > B-tree      |  You: Why do we need B-trees when we have         |
|   Hash Tables |      hash tables that are O(1)?                    |
|   AVL Trees   |                                                   |
|   Big O       |  Tutor: Great question! Let's rewind to the       |
|               |  1970s...                                         |
| [New Chat]    |                                                   |
|               |  ## The Prehistoric Era                            |
| Knowledge     |  Disk drives were (and still are) painfully slow.  |
| Level:        |  A single disk seek takes ~10ms. In that time,     |
| DS: 78%       |  a CPU can execute ~30 million instructions.       |
| Algo: 50%     |                                                   |
| OS: 30%       |  ## The Naive Approach                             |
|               |  "Just use binary search on sorted data!"          |
| Reviews: 12   |  Works great for reads: O(log n).                  |
|               |  But insert a record in the middle? You need to    |
|               |  shift EVERYTHING after it. On disk, this means    |
|               |  rewriting megabytes of data. Unacceptable.       |
|               |                                                   |
|               |  ## The B-Tree Solution                            |
|               |  Make each node HUGE -- store hundreds of keys     |
|               |  per node. This way:                               |
|               |  - Shallow tree (3-4 levels for billions of keys)  |
|               |  - Each level = one disk read                      |
|               |  - Total: 3-4 disk reads vs thousands              |
|               |                                                   |
|               |  **Trade-off**: Wastes some space (nodes rarely     |
|               |  100% full) to minimize disk I/O.                  |
|               |                                                   |
|               +---------------------------------------------------+
|               | [Attach file]  Ask a question...        [Send]    |
+------------------------------------------------------------------+
```

### 3.4 Web UI Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Next.js 16 | SSR, RSC, Route Handlers |
| AI Integration | Vercel AI SDK v4/v6 | `useChat`, `streamText`, `streamUI` |
| UI Components | shadcn/ui + AI Elements | Chat, forms, dashboards |
| Styling | Tailwind CSS + CSS Variables | Theming (dark/light) |
| Markdown | react-markdown + remark-gfm + rehype-highlight | AI response rendering |
| Graph Visualization | D3.js or react-force-graph | Knowledge graph rendering |
| Charts | Recharts or Tremor | Learning analytics |
| State | Zustand or Jotai | Client state management |
| Streaming Transport | SSE | AI response streaming |

### 3.5 Streaming Chat Implementation

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai';
import { createStudyAgent } from '@/lib/agent';

export async function POST(req: Request) {
  const { messages, sessionId } = await req.json();

  const agent = await createStudyAgent(sessionId);

  const result = streamText({
    model: agent.model,
    system: agent.systemPrompt,
    messages,
    tools: agent.tools,
    maxSteps: 10,
  });

  return result.toDataStreamResponse();
}

// components/chat.tsx
'use client';
import { useChat } from '@ai-sdk/react';
import { Markdown } from '@/components/markdown';

export function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: { sessionId: getCurrentSessionId() },
  });

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            {m.role === 'assistant' ? (
              <Markdown content={m.content} />
            ) : (
              <p>{m.content}</p>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="border-t p-4">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Ask about CS concepts..."
          className="w-full p-2 border rounded"
        />
      </form>
    </div>
  );
}
```

## 4. Streaming Architecture

### 4.1 SSE Flow

```
Client (TUI/Web)                Server (FastAPI)
     |                                |
     |  POST /api/chat/stream         |
     |  { messages: [...] }           |
     |------------------------------->|
     |                                |  1. Route to Agent Orchestrator
     |                                |  2. Load learner state
     |                                |  3. Select agent
     |                                |  4. Call LLM with tools
     |                                |
     |  SSE: event: token             |
     |  data: {"content": "Let"}      |
     |<-------------------------------|
     |  SSE: event: token             |
     |  data: {"content": " me"}      |
     |<-------------------------------|
     |  ... (streaming tokens)        |
     |                                |
     |  SSE: event: tool_use          |
     |  data: {"tool": "generate_quiz"}|
     |<-------------------------------|
     |                                |  (agent calls tool)
     |  SSE: event: tool_result       |
     |  data: {"result": [...]}       |
     |<-------------------------------|
     |  ... (more streaming)          |
     |                                |
     |  SSE: event: done              |
     |  data: [DONE]                  |
     |<-------------------------------|
```

### 4.2 FastAPI SSE Implementation

```python
from fastapi import FastAPI, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list[dict]
    session_id: str

@app.post("/api/chat/stream", response_class=EventSourceResponse)
async def stream_chat(
    request: ChatRequest,
    user=Depends(get_current_user),
) -> EventSourceResponse:
    async def event_generator():
        agent = await create_study_agent(request.session_id, user.id)

        async for event in agent.stream(request.messages):
            if event.type == "token":
                yield ServerSentEvent(
                    data=json.dumps({"content": event.content}),
                    event="token"
                )
            elif event.type == "tool_use":
                yield ServerSentEvent(
                    data=json.dumps({"tool": event.tool_name, "args": event.args}),
                    event="tool_use"
                )
            elif event.type == "tool_result":
                yield ServerSentEvent(
                    data=json.dumps({"result": event.result}),
                    event="tool_result"
                )
            elif event.type == "knowledge_update":
                yield ServerSentEvent(
                    data=json.dumps({"concept": event.concept, "mastery": event.mastery}),
                    event="knowledge_update"
                )

        yield ServerSentEvent(data="[DONE]", event="done")

    return EventSourceResponse(event_generator())
```

## 5. API Design

### 5.1 RESTful Endpoints

```
# Chat & Teaching
POST   /api/v1/chat/stream              SSE streaming chat
POST   /api/v1/chat/complete            Non-streaming (testing)

# Conversations
GET    /api/v1/conversations             List conversations
POST   /api/v1/conversations             Create new conversation
GET    /api/v1/conversations/:id         Get conversation with messages
DELETE /api/v1/conversations/:id         Delete conversation

# Spaced Repetition
GET    /api/v1/reviews/due               Get due review cards
POST   /api/v1/reviews/submit            Submit review result (FSRS rating)
GET    /api/v1/reviews/schedule          Get upcoming schedule

# Knowledge Graph
GET    /api/v1/knowledge/graph           Get full concept graph
GET    /api/v1/knowledge/graph/:domain   Get domain subgraph
GET    /api/v1/knowledge/state           Get learner's knowledge state
POST   /api/v1/knowledge/concepts        Add new concept
GET    /api/v1/knowledge/path/:domain    Get recommended learning path
GET    /api/v1/knowledge/search          Semantic search concepts

# Quizzes & Flashcards
POST   /api/v1/quizzes/generate          Generate quiz for concept(s)
POST   /api/v1/flashcards/generate       Generate flashcards from content
GET    /api/v1/flashcards/decks          List flashcard decks
GET    /api/v1/flashcards/decks/:id      Get deck with cards

# Documents
POST   /api/v1/documents/upload          Upload PDF/document
POST   /api/v1/documents/url             Submit URL for processing
GET    /api/v1/documents                 List processed documents
GET    /api/v1/documents/:id             Get document details

# Analytics
GET    /api/v1/analytics/progress        Get progress overview
GET    /api/v1/analytics/weak-areas      Get weak areas
GET    /api/v1/analytics/study-time      Get study time data
GET    /api/v1/analytics/streak          Get streak info

# User
GET    /api/v1/user/profile              Get user profile
PUT    /api/v1/user/preferences          Update learning preferences
```

### 5.2 WebSocket Endpoint

```
WS  /ws/agent/:session_id               Real-time agent updates
  - Used for: live knowledge state updates, agent status, notifications
  - Not used for: chat streaming (SSE preferred)
```

---

## Sources

- [Textual v4.0 Streaming Release](https://simonwillison.net/2025/Jul/22/textual-v4/)
- [Textual Official Documentation](https://textual.textualize.io/)
- [Next.js 16 AI Integration Patterns](https://www.digitalapplied.com/blog/nextjs-16-ai-integration-patterns-guide)
- [Vercel AI SDK Documentation](https://ai-sdk.dev/v4/docs/ai-sdk-rsc/streaming-react-components)
- [shadcn/ui AI Chatbot](https://www.shadcn.io/ai/chatbot)
- [FastAPI SSE Documentation](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [Rich Library Documentation](https://rich.readthedocs.io/)
