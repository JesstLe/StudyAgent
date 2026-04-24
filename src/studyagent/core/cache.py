from __future__ import annotations

import json
from datetime import datetime, timezone

try:
    import redis.asyncio as aioredis

    _HAS_REDIS = True
except ImportError:
    _HAS_REDIS = False


class CacheBackend:
    def __init__(self, url: str | None = None):
        self._client: aioredis.Redis | None = None
        self._url = url
        self._local: dict[str, tuple[str, float]] = {}

    async def connect(self) -> None:
        if not self._url or not _HAS_REDIS:
            return
        self._client = aioredis.from_url(self._url, decode_responses=True)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def get(self, key: str) -> str | None:
        if self._client:
            return await self._client.get(key)
        entry = self._local.get(key)
        if entry is None:
            return None
        value, expires = entry
        if datetime.now(timezone.utc).timestamp() > expires:
            del self._local[key]
            return None
        return value

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        if self._client:
            await self._client.set(key, value, ex=ttl)
        else:
            expires = datetime.now(timezone.utc).timestamp() + ttl
            self._local[key] = (value, expires)

    async def delete(self, key: str) -> None:
        if self._client:
            await self._client.delete(key)
        else:
            self._local.pop(key, None)

    async def incr(self, key: str) -> int:
        if self._client:
            return await self._client.incr(key)
        val = int(self._local.get(key, ("0", float("inf")))[0]) + 1
        self._local[key] = (str(val), float("inf"))
        return val

    async def expire(self, key: str, ttl: int) -> None:
        if self._client:
            await self._client.expire(key, ttl)

    async def get_json(self, key: str) -> dict | list | None:
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def set_json(self, key: str, value: dict | list, ttl: int = 3600) -> None:
        await self.set(key, json.dumps(value, ensure_ascii=False), ttl)


_cache: CacheBackend | None = None


def get_cache() -> CacheBackend:
    global _cache
    if _cache is None:
        from studyagent.core.config import load_config
        config = load_config()
        url = getattr(config, "redis_url", None) or os.environ.get("REDIS_URL")
        _cache = CacheBackend(url)
    return _cache


import os
