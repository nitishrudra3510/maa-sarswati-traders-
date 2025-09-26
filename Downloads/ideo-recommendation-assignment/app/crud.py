from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Post, Engagement, EngagementType


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, username: str) -> User:
    user = User(username=username)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user(db: AsyncSession, username: str) -> User:
    user = await get_user_by_username(db, username)
    if user:
        return user
    return await create_user(db, username)


async def get_posts(db: AsyncSession, *, category: str | None = None, limit: int = 20, offset: int = 0) -> Sequence[Post]:
    stmt = select(Post).order_by(Post.created_at.desc())
    if category:
        stmt = stmt.where(Post.category == category)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_post_by_title(db: AsyncSession, title: str) -> Post | None:
    result = await db.execute(select(Post).where(Post.title == title))
    return result.scalars().first()


async def get_user_engagements(db: AsyncSession, user_id: int) -> Sequence[Engagement]:
    result = await db.execute(select(Engagement).where(Engagement.user_id == user_id))
    return list(result.scalars().all())


async def save_post(db: AsyncSession, *, title: str, category: str | None, metadata: dict | None) -> Post:
    existing = await get_post_by_title(db, title)
    if existing:
        # update basic fields if changed
        updated = False
        if existing.category != category:
            existing.category = category
            updated = True
        if metadata is not None and existing.metadata != metadata:
            existing.metadata = metadata
            updated = True
        if updated:
            await db.commit()
            await db.refresh(existing)
        return existing
    post = Post(title=title, category=category, metadata=metadata)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def save_engagement(
    db: AsyncSession,
    *,
    user_id: int,
    post_id: int,
    type: EngagementType,
    rating_score: int | None = None,
) -> Engagement:
    engagement = Engagement(user_id=user_id, post_id=post_id, type=type, rating_score=rating_score)
    db.add(engagement)
    await db.commit()
    await db.refresh(engagement)
    return engagement


