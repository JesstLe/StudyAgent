from __future__ import annotations

import re


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~1.5 per CJK char, ~0.75 per English word, ~1 per other."""
    cjk = len(re.findall(r"[一-鿿　-〿＀-￯]", text))
    remaining = text[cjk:] if cjk == 0 else re.sub(r"[一-鿿　-〿＀-￯]", "", text)
    words = len(remaining.split())
    others = max(0, len(remaining) - words)
    return int(cjk * 1.5 + words * 1.3 + others * 0.5) + 1


def estimate_messages_tokens(messages: list[dict[str, str]]) -> int:
    return sum(estimate_tokens(m.get("content", "")) for m in messages)
