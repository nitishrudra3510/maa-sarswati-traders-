from __future__ import annotations

from collections import defaultdict
from typing import Sequence

import math

from sqlalchemy.ext.asyncio import AsyncSession

from .crud import get_user_by_username, get_posts, get_user_engagements
from .models import EngagementType, Post


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in set(a) | set(b))
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _vectorize_post(post: Post) -> dict[str, float]:
    vector: dict[str, float] = defaultdict(float)
    if post.category:
        vector[f"cat:{post.category.lower()}"] = 1.0
    if isinstance(post.metadata, dict):
        for k, v in post.metadata.items():
            key = f"m:{k}:{str(v).lower()}"
            vector[key] += 1.0
    return dict(vector)


async def get_cold_start_recommendations(db: AsyncSession, username: str, limit: int = 20, offset: int = 0) -> list[dict]:
    posts = await get_posts(db, limit=limit, offset=offset)
    return [
        {
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "metadata": p.metadata,
            "reason": "cold_start",
        }
        for p in posts
    ]


async def get_personalized_recommendations(db: AsyncSession, username: str, limit: int = 20, offset: int = 0) -> list[dict]:
    user = await get_user_by_username(db, username)
    if not user:
        return await get_cold_start_recommendations(db, username, limit=limit, offset=offset)

    engagements = await get_user_engagements(db, user.id)
    all_posts = await get_posts(db, limit=1000, offset=0)

    if not engagements:
        return await get_cold_start_recommendations(db, username, limit=limit, offset=offset)

    # Build user preference vector
    user_vec: dict[str, float] = defaultdict(float)
    engaged_post_ids = {e.post_id for e in engagements}
    for e in engagements:
        weight = 0.5
        if e.type == EngagementType.view:
            weight = 0.5
        elif e.type == EngagementType.like:
            weight = 1.0
        elif e.type == EngagementType.inspire:
            weight = 1.2
        elif e.type == EngagementType.rating:
            weight = 0.8 + 0.4 * ((e.rating_score or 3) / 5.0)
        # Accumulate vector
        post = next((p for p in all_posts if p.id == e.post_id), None)
        if not post:
            continue
        vec = _vectorize_post(post)
        for k, v in vec.items():
            user_vec[k] += weight * v

    # Score all posts not yet engaged
    scored: list[tuple[Post, float]] = []
    for p in all_posts:
        if p.id in engaged_post_ids:
            continue
        vec = _vectorize_post(p)
        score = _cosine_similarity(user_vec, vec)
        scored.append((p, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    sliced = scored[offset : offset + limit]
    return [
        {
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "metadata": p.metadata,
            "reason": "personalized",
            "score": round(score, 4),
        }
        for p, score in sliced
    ]


async def get_category_recommendations(db: AsyncSession, username: str, project_code: str, limit: int = 20, offset: int = 0) -> list[dict]:
    posts = await get_posts(db, category=project_code, limit=1000, offset=0)
    result = [
        {
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "metadata": p.metadata,
            "reason": "category",
        }
        for p in posts
    ]
    return result[offset : offset + limit]


