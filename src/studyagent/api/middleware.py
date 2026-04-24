from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable, Awaitable

from starlette.types import ASGIApp, Receive, Scope, Send, Message


class RateLimitMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst: int = 10,
    ):
        self.app = app
        self.rpm = requests_per_minute
        self.burst = burst
        self._windows: dict[str, list[float]] = defaultdict(list)

    def _key(self, scope: Scope) -> str:
        headers: dict[bytes, bytes] = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for")
        if forwarded:
            return forwarded.decode().split(",")[0].strip()
        client = scope.get("client")
        return client[0] if client else "unknown"

    def _check(self, key: str) -> bool:
        now = time.time()
        window = self._windows[key]
        self._windows[key] = [t for t in window if now - t < 60]
        window = self._windows[key]

        if len(window) >= self.rpm:
            return False
        self._windows[key].append(now)
        return True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in ("/docs", "/redoc", "/openapi.json", "/health"):
            await self.app(scope, receive, send)
            return

        key = self._key(scope)
        if not self._check(key):
            body = b'{"detail":"Rate limit exceeded"}'
            await send({"type": "http.response.start", "status": 429, "headers": [
                [b"content-type", b"application/json"],
                [b"retry-after", b"60"],
                [b"content-length", str(len(body)).encode()],
            ]})
            await send({"type": "http.response.body", "body": body})
            return

        await self.app(scope, receive, send)
