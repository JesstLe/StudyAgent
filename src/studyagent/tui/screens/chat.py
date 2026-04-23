from __future__ import annotations

import json

import httpx
from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Input, Static


API_BASE = "http://localhost:8000/api/v1"


class ChatScreen(Screen):
    CSS = """
    ChatScreen {
        layout: vertical;
    }
    #messages {
        height: 1fr;
        padding: 0 1;
        scrollbar-size: 1 1;
    }
    #input-area {
        dock: bottom;
        height: auto;
        max-height: 5;
        padding: 0 1;
    }
    #status {
        dock: bottom;
        height: 1;
        background: $primary-background-darken-1;
        color: $text-muted;
        padding: 0 1;
    }
    .user-msg {
        color: $text;
        margin: 1 0;
    }
    .assistant-msg {
        color: $success;
        margin: 1 0;
    }
    .system-msg {
        color: $text-muted;
        margin: 1 0;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_id: str | None = None
        self.messages: list[dict[str, str]] = []
        self.streaming = False

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="messages")
        yield Input(
            placeholder="Ask about CS concepts... (e.g. 'What is a B-tree?')",
            id="input-area",
        )
        yield Static("StudyAgent v0.1 | Mode: Teaching", id="status")

    def on_mount(self) -> None:
        self.query_one("#input-area", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.streaming:
            return
        user_text = event.value.strip()
        if not user_text:
            return

        input_widget = self.query_one("#input-area", Input)
        input_widget.value = ""
        input_widget.disabled = True

        self._append_message("user", user_text)
        self.messages.append({"role": "user", "content": user_text})

        self.streaming = True
        self._update_status("Thinking...")

        assistant_widget = self._create_assistant_widget()

        try:
            full_response = await self._stream_response(assistant_widget)
            self.messages.append({"role": "assistant", "content": full_response})
            self._update_status(f"StudyAgent v0.1 | Mode: Teaching | Conv: {self.conversation_id[:8] if self.conversation_id else 'new'}")
        except Exception as e:
            self._append_message("system", f"[Error] {e}")
            self._update_status("StudyAgent v0.1 | Error")
        finally:
            self.streaming = False
            input_widget.disabled = False
            input_widget.focus()

    def _append_message(self, role: str, content: str) -> None:
        messages = self.query_one("#messages", VerticalScroll)
        css_class = {"user": "user-msg", "assistant": "assistant-msg", "system": "system-msg"}.get(role, "system-msg")
        widget = Static(content, classes=css_class)
        messages.mount(widget)
        messages.scroll_end(animate=False)

    def _create_assistant_widget(self) -> Static:
        messages = self.query_one("#messages", VerticalScroll)
        widget = Static("", classes="assistant-msg", id="streaming-response")
        messages.mount(widget)
        messages.scroll_end(animate=False)
        return widget

    async def _stream_response(self, widget: Static) -> str:
        full_text = ""
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{API_BASE}/chat/stream",
                json={
                    "messages": self.messages,
                    "conversation_id": self.conversation_id,
                    "session_type": "teaching",
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if not data_str:
                        continue
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if data.get("type") == "token":
                        full_text += data["content"]
                        widget.update(Markdown(full_text))
                        self.query_one("#messages", VerticalScroll).scroll_end(animate=False)
                    elif data.get("type") == "done":
                        self.conversation_id = data.get("conversation_id", self.conversation_id)

        return full_text

    def _update_status(self, text: str) -> None:
        status = self.query_one("#status", Static)
        status.update(text)

    def new_conversation(self) -> None:
        self.conversation_id = None
        self.messages = []
        messages = self.query_one("#messages", VerticalScroll)
        for child in list(messages.children):
            child.remove()
        self._update_status("StudyAgent v0.1 | Mode: Teaching | New Session")
        self.query_one("#input-area", Input).focus()
