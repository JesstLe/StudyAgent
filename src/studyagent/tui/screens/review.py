from __future__ import annotations

import json

import httpx
from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Header, Static

from studyagent.tui.screens.chat import API_BASE


GRADE_LABELS = {
    1: "Again",
    2: "Hard",
    3: "Good",
    4: "Easy",
}


class ReviewScreen(Screen):
    CSS = """
    ReviewScreen {
        layout: vertical;
    }
    #card-area {
        height: 1fr;
        padding: 1 2;
        scrollbar-size: 1 1;
    }
    #card-front {
        text-align: center;
        padding: 2;
        margin: 1 0;
        background: $surface;
        border: round $primary;
    }
    #card-back {
        text-align: center;
        padding: 2;
        margin: 1 0;
        background: $surface;
        border: round $success;
    }
    #grade-buttons {
        dock: bottom;
        height: auto;
        padding: 0 1;
    }
    #grade-buttons Horizontal {
        height: 3;
    }
    #review-status {
        dock: bottom;
        height: 1;
        background: $primary-background-darken-1;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards: list[dict] = []
        self.current_index = 0
        self.showing_answer = False
        self.deck_id: str | None = None

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="card-area")
        yield Static("No cards to review", id="review-status")

    async def on_mount(self) -> None:
        await self._load_due_cards()

    async def _load_due_cards(self) -> None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{API_BASE}/reviews/due", params={"limit": 20})
            if resp.status_code == 200:
                self.cards = resp.json()
            else:
                self.cards = []

        self.current_index = 0
        self.showing_answer = False
        self._render_card()

    def _render_card(self) -> None:
        area = self.query_one("#card-area", VerticalScroll)
        for child in list(area.children):
            child.remove()

        status = self.query_one("#review-status", Static)

        if not self.cards or self.current_index >= len(self.cards):
            status.update(f"Review complete! Reviewed {self.current_index} cards.")
            area.mount(Static(Markdown("## All caught up!\n\nNo more cards due for review.")))
            return

        card = self.cards[self.current_index]
        status.update(f"Card {self.current_index + 1}/{len(self.cards)} | {card.get('fsrs_state', 'New')}")

        front = card.get("front", "Review")
        area.mount(Static(Markdown(f"## {front}"), id="card-front"))

        if not self.showing_answer:
            area.mount(Button("Show Answer", variant="primary", id="show-answer-btn"))
        else:
            back = card.get("back", "")
            if back:
                area.mount(Static(Markdown(back), id="card-back"))

            from textual.containers import Horizontal
            btns = Horizontal()
            for grade in [1, 2, 3, 4]:
                btns.mount(Button(GRADE_LABELS[grade], id=f"grade-{grade}", variant=self._grade_variant(grade)))
            area.mount(btns)

    def _grade_variant(self, grade: int) -> str:
        return {1: "error", 2: "warning", 3: "success", 4: "primary"}.get(grade, "default")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "show-answer-btn":
            self.showing_answer = True
            self._render_card()
        elif btn_id and btn_id.startswith("grade-"):
            grade = int(btn_id.split("-")[1])
            await self._submit_grade(grade)

    async def _submit_grade(self, grade: int) -> None:
        card = self.cards[self.current_index]
        concept_id = card.get("concept_id", "")
        card_id = card.get("id")

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{API_BASE}/reviews/submit",
                json={"grade": grade, "concept_id": concept_id, "card_id": card_id},
            )
            if resp.status_code == 200:
                result = resp.json()
                status = self.query_one("#review-status", Static)
                status.update(f"Grade: {GRADE_LABELS[grade]} | Next review in {result['scheduled_days']} days")

        self.current_index += 1
        self.showing_answer = False
        self._render_card()
