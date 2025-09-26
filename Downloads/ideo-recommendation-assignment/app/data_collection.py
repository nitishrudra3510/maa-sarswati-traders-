from __future__ import annotations

from typing import Any, Optional

import httpx

from .config import get_settings
from .crud import save_post, save_engagement, get_or_create_user, get_user_by_username
from .models import EngagementType
from .dependencies import AsyncSession


settings = get_settings()


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if settings.FLIC_TOKEN:
        headers["Flic-Token"] = settings.FLIC_TOKEN
    return headers


async def _get(endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
    url = settings.API_BASE_URL.rstrip("/") + "/" + endpoint.lstrip("/")
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, headers=_headers(), params=params)
        resp.raise_for_status()
        return resp.json()


async def fetch_viewed_posts(username: str | None = None) -> Any:
    if username:
        return await _get(f"users/{username}/viewed")
    return await _get("posts/view", params={"page": 1, "page_size": 1000, "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"})


async def fetch_liked_posts(username: str | None = None) -> Any:
    if username:
        return await _get(f"users/{username}/liked")
    return await _get("posts/like", params={"page": 1, "page_size": 1000, "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"})


async def fetch_inspired_posts(username: str | None = None) -> Any:
    if username:
        return await _get(f"users/{username}/inspired")
    return await _get("posts/inspire", params={"page": 1, "page_size": 1000, "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"})


async def fetch_rated_posts(username: str | None = None) -> Any:
    if username:
        return await _get(f"users/{username}/rated")
    return await _get("posts/rating", params={"page": 1, "page_size": 1000, "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"})


async def fetch_all_posts() -> Any:
    return await _get("posts/summary/get", params={"page": 1, "page_size": 1000})


async def fetch_all_users() -> Any:
    return await _get("users/get_all", params={"page": 1, "page_size": 1000})


async def sync_to_db(db: AsyncSession) -> None:
    users = await fetch_all_users()
    for user in users or []:
        username = user.get("username")
        if not username:
            continue
        await get_or_create_user(db, username)

    posts = await fetch_all_posts()
    for p in posts or []:
        title = p.get("title") or "Untitled"
        category = p.get("category")
        metadata = p.get("metadata") or {}
        await save_post(db, title=title, category=category, metadata=metadata)

    # Optionally sync engagements for each user
    for user in users or []:
        username = user.get("username")
        if not username:
            continue
        viewed = await fetch_viewed_posts(username)
        for item in viewed or []:
            await _save_eng_from_item(db, username, item, EngagementType.view)
        liked = await fetch_liked_posts(username)
        for item in liked or []:
            await _save_eng_from_item(db, username, item, EngagementType.like)
        inspired = await fetch_inspired_posts(username)
        for item in inspired or []:
            await _save_eng_from_item(db, username, item, EngagementType.inspire)
        rated = await fetch_rated_posts(username)
        for item in rated or []:
            await _save_eng_from_item(db, username, item, EngagementType.rating)


async def _save_eng_from_item(db: AsyncSession, username: str, item: dict, etype: EngagementType) -> None:
    user = await get_or_create_user(db, username)
    title = item.get("title") or item.get("post_title") or "Untitled"
    category = item.get("category")
    metadata = item.get("metadata") or {}
    post = await save_post(db, title=title, category=category, metadata=metadata)
    rating_score = item.get("rating") if etype == EngagementType.rating else None
    await save_engagement(db, user_id=user.id, post_id=post.id, type=etype, rating_score=rating_score)


