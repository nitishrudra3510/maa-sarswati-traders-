from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

try:
    import redis.asyncio as redis
except Exception:  # pragma: no cover - fallback typing only
    redis = None  # type: ignore

from .config import get_settings


settings = get_settings()
_redis_client: Optional["redis.Redis"] = None


async def get_redis() -> Optional["redis.Redis"]:
    global _redis_client
    if redis is None:
        return None
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis_client


async def cache_user_feed(username: str, feed: list[dict], ttl_seconds: int = 300) -> None:
    client = await get_redis()
    if not client:
        return
    key = f"feed:{username}"
    try:
        await client.set(key, json.dumps(feed), ex=ttl_seconds)
    except Exception:
        pass


async def get_cached_feed(username: str) -> Optional[list[dict]]:
    client = await get_redis()
    if not client:
        return None
    key = f"feed:{username}"
    try:
        data = await client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        return None
    return None


def paginate(items: list[dict], limit: int, offset: int) -> list[dict]:
    start = max(offset, 0)
    end = start + max(limit, 0)
    return items[start:end]


