from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from langgraph.graph import END, START, StateGraph

from studyagent.agents.knowledge_graph.agent import KnowledgeGraphAgent
from studyagent.agents.orchestrator.router import IntentRouter
from studyagent.agents.orchestrator.state import LearningState
from studyagent.agents.quiz.agent import QuizAgent
from studyagent.agents.scheduler.agent import SchedulerAgent
from studyagent.agents.tutor.agent import TutorAgent
from studyagent.core.llm import LLMProvider


def _route_intent(state: dict) -> str:
    intent = state.get("intent", "teach")
    mapping = {
        "teach": "tutor",
        "quiz": "quiz",
        "review": "review",
        "analyze": "analyze",
        "explore": "explore",
    }
    return mapping.get(intent, "tutor")


async def _classify_node(state: dict) -> dict:
    router = IntentRouter()
    messages = state.get("messages", [])
    last_msg = messages[-1]["content"] if messages else ""
    intent = await router.classify(last_msg)
    state["intent"] = intent
    return state


async def _tutor_node(state: dict) -> dict:
    tutor = TutorAgent()
    messages = state.get("messages", [])
    session_type = state.get("session_type", "teaching")
    topics = state.get("topics", "")

    response = await tutor.respond(messages=messages, session_type=session_type, topics=topics)
    state["response"] = response

    # Auto-extract concepts
    kg_agent = KnowledgeGraphAgent()
    extraction = await kg_agent.extract_concepts(messages + [{"role": "assistant", "content": response}])
    state["extracted_concepts"] = extraction.get("concepts", [])
    state["extracted_relations"] = extraction.get("relations", [])

    return state


async def _quiz_node(state: dict) -> dict:
    quiz_agent = QuizAgent()
    topics = state.get("topics", "")
    concepts = [c.strip() for c in topics.split(",") if c.strip()] if topics else []

    if not concepts:
        messages = state.get("messages", [])
        last_msg = messages[-1]["content"] if messages else ""
        concepts = [last_msg[:30]]

    questions = await quiz_agent.generate_quiz(concepts=concepts, difficulty=0.5, count=5)
    state["quiz_questions"] = questions

    from studyagent.agents.tutor.agent import TutorAgent
    tutor = TutorAgent()
    quiz_intro = f"好，来测验一下！我准备了 {len(questions)} 道题。\n\n"
    for i, q in enumerate(questions):
        quiz_intro += f"**Q{i+1}.** {q['front']}\n"
        if q.get("options"):
            for opt in q["options"]:
                marker = "✓" if opt.get("is_correct") else " "
                quiz_intro += f"  [{marker}] {opt['label']}. {opt['text']}\n"
        quiz_intro += "\n"
    state["response"] = quiz_intro

    return state


async def _review_node(state: dict) -> dict:
    scheduler = SchedulerAgent()
    state["response"] = "启动复习模式。正在加载待复习的卡片..."
    return state


async def _analyze_node(state: dict) -> dict:
    state["response"] = "学习分析功能正在开发中。"
    return state


async def _explore_node(state: dict) -> dict:
    state["response"] = "知识图谱探索功能正在开发中。"
    return state


def build_graph() -> StateGraph:
    graph = StateGraph(dict)

    graph.add_node("classify", _classify_node)
    graph.add_node("tutor", _tutor_node)
    graph.add_node("quiz", _quiz_node)
    graph.add_node("review", _review_node)
    graph.add_node("analyze", _analyze_node)
    graph.add_node("explore", _explore_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", _route_intent, {
        "tutor": "tutor",
        "quiz": "quiz",
        "review": "review",
        "analyze": "analyze",
        "explore": "explore",
    })
    graph.add_edge("tutor", END)
    graph.add_edge("quiz", END)
    graph.add_edge("review", END)
    graph.add_edge("analyze", END)
    graph.add_edge("explore", END)

    return graph


class Orchestrator:
    def __init__(self, llm: LLMProvider | None = None):
        self._llm = llm
        graph = build_graph()
        self._compiled = graph.compile()

    async def run(
        self,
        messages: list[dict[str, str]],
        *,
        session_type: str = "teaching",
        topics: str = "",
        user_id: str = "default",
        conversation_id: str | None = None,
    ) -> LearningState:
        initial = LearningState(
            user_id=user_id,
            conversation_id=conversation_id,
            messages=messages,
            session_type=session_type,
            topics=topics,
        )
        result = await self._compiled.ainvoke(initial.__dict__)
        return LearningState(**{k: v for k, v in result.items() if k in LearningState.__dataclass_fields__})

    async def run_teach(
        self,
        messages: list[dict[str, str]],
        session_type: str = "teaching",
        topics: str = "",
    ) -> str:
        state = await self.run(messages, session_type=session_type, topics=topics, intent="teach")
        return state.response

    async def run_quiz(self, topics: str = "") -> list[dict]:
        state = await self.run(
            messages=[{"role": "user", "content": f"Quiz me on: {topics}"}],
            topics=topics,
        )
        return state.quiz_questions
