from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst: int = 10,
    ):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.burst = burst
        self._windows: dict[str, list[float]] = defaultdict(list)

    def _key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = request.client
        return client.host if client else "unknown"

    def _check(self, key: str) -> bool:
        now = time.time()
        window = self._windows[key]
        # Remove entries older than 60s
        self._windows[key] = [t for t in window if now - t < 60]
        window = self._windows[key]

        if len(window) >= self.rpm:
            return False
        self._windows[key].append(now)
        return True

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for docs and health
        path = request.url.path
        if path in ("/docs", "/redoc", "/openapi.json", "/health"):
            return await call_next(request)

        key = self._key(request)
        if not self._check(key):
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        return await call_next(request)
