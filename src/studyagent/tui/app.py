from __future__ import annotations

import asyncio
import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Static, TabbedContent, TabPane

from studyagent.tui.screens.chat import ChatScreen


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
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ChatScreen(id="chat-screen")
        yield Footer()

    def action_new_chat(self) -> None:
        chat = self.query_one("#chat-screen", ChatScreen)
        chat.new_conversation()


def main():
    app = StudyAgentApp()
    app.run()


if __name__ == "__main__":
    main()
