from __future__ import annotations

import asyncio
import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Static, TabbedContent, TabPane

from studyagent.tui.screens.chat import ChatScreen
from studyagent.tui.screens.dashboard import DashboardScreen
from studyagent.tui.screens.quiz import QuizScreen
from studyagent.tui.screens.review import ReviewScreen


class StudyAgentApp(App):
    TITLE = "StudyAgent"
    CSS = """
    Screen {
        layout: vertical;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+n", "new_chat", "New Chat", show=True),
        Binding("ctrl+d", "dashboard", "Dashboard", show=True),
        Binding("ctrl+r", "review", "Review", show=True),
        Binding("ctrl+1", "chat_tab", "Chat", show=True),
        Binding("ctrl+2", "review_tab", "Review", show=True),
        Binding("ctrl+3", "dashboard_tab", "Dashboard", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Chat", id="chat-tab"):
                yield ChatScreen(id="chat-screen")
            with TabPane("Review", id="review-tab"):
                yield ReviewScreen(id="review-screen")
            with TabPane("Dashboard", id="dashboard-tab"):
                yield DashboardScreen(id="dashboard-screen")
        yield Footer()

    def action_new_chat(self) -> None:
        chat = self.query_one("#chat-screen", ChatScreen)
        chat.new_conversation()

    def action_dashboard(self) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = "dashboard-tab"

    def action_review(self) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = "review-tab"

    def action_chat_tab(self) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = "chat-tab"

    def action_review_tab(self) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = "review-tab"

    def action_dashboard_tab(self) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = "dashboard-tab"


def main():
    app = StudyAgentApp()
    app.run()


if __name__ == "__main__":
    main()
