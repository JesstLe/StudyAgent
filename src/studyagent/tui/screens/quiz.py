from __future__ import annotations

import json

import httpx
from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static

from studyagent.tui.screens.chat import API_BASE


class QuizScreen(Screen):
    CSS = """
    QuizScreen {
        layout: vertical;
    }
    #quiz-area {
        height: 1fr;
        padding: 1 2;
        scrollbar-size: 1 1;
    }
    #quiz-status {
        dock: bottom;
        height: 1;
        background: $primary-background-darken-1;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, concepts: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.concepts = concepts or []
        self.questions: list[dict] = []
        self.current_index = 0
        self.answers: list[dict] = []
        self.quiz_finished = False

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="quiz-area")
        yield Static("Loading quiz...", id="quiz-status")

    async def on_mount(self) -> None:
        if self.concepts:
            await self._generate_quiz()
        else:
            area = self.query_one("#quiz-area", VerticalScroll)
            area.mount(Static(Markdown("## No concepts specified for quiz.")))

    async def _generate_quiz(self) -> None:
        status = self.query_one("#quiz-status", Static)
        status.update("Generating quiz questions...")

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{API_BASE}/quiz/generate",
                json={"concepts": self.concepts, "difficulty": 0.5, "count": 5},
            )
            if resp.status_code == 200:
                data = resp.json()
                self.questions = data.get("questions", [])
            else:
                self.questions = []

        self.current_index = 0
        self.answers = []
        self.quiz_finished = False
        self._render_question()

    def _render_question(self) -> None:
        area = self.query_one("#quiz-area", VerticalScroll)
        for child in list(area.children):
            child.remove()

        status = self.query_one("#quiz-status", Static)

        if self.quiz_finished:
            self._render_results(area, status)
            return

        if not self.questions or self.current_index >= len(self.questions):
            status.update("No questions available.")
            return

        q = self.questions[self.current_index]
        status.update(f"Question {self.current_index + 1}/{len(self.questions)}")

        area.mount(Static(Markdown(f"## {q['front']}")))

        if q.get("card_type") == "multiple_choice" and q.get("options"):
            from textual.containers import Horizontal

            for opt in q["options"]:
                label = opt.get("label", "?")
                text = opt.get("text", "")
                btn = Button(
                    f"{label}. {text}",
                    id=f"opt-{label}",
                    variant="default",
                )
                area.mount(btn)
        else:
            area.mount(Static(Markdown(f"*Type your answer below*\n\n**Answer:** {q.get('back', 'N/A')}")))

    def _render_results(self, area: VerticalScroll, status: Static) -> None:
        correct = sum(1 for a in self.answers if a.get("correct"))
        total = len(self.answers)
        pct = (correct / total * 100) if total > 0 else 0

        area.mount(Static(Markdown(f"## Quiz Results\n\n**Score:** {correct}/{total} ({pct:.0f}%)\n")))

        for i, (q, a) in enumerate(zip(self.questions, self.answers)):
            icon = "+" if a.get("correct") else "-"
            area.mount(Static(Markdown(f"{'+' if a.get('correct') else '-'} **Q{i+1}:** {q.get('front', '')[:60]}")))

        status.update(f"Quiz complete! {correct}/{total} correct")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if not btn_id or not btn_id.startswith("opt-"):
            return

        selected_label = btn_id[4:]
        q = self.questions[self.current_index]

        correct = False
        for opt in q.get("options", []):
            if opt.get("label") == selected_label and opt.get("is_correct"):
                correct = True
                break

        self.answers.append({"card_id": q.get("id", ""), "answer": selected_label, "correct": correct})
        self.current_index += 1

        if self.current_index >= len(self.questions):
            self.quiz_finished = True

        self._render_question()
