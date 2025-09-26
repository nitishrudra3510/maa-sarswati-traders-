from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..cache import get_cached_feed, cache_user_feed, paginate
from ..recommendation import (
    get_cold_start_recommendations,
    get_personalized_recommendations,
    get_category_recommendations,
)


router = APIRouter(tags=["feed"])


@router.get("/feed")
async def get_feed(
    username: str = Query(..., min_length=3),
    project_code: str | None = Query(None, min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    try:
        cached = await get_cached_feed(username)
        if cached is not None and not project_code:
            return paginate(cached, limit, offset)

        if project_code:
            feed = await get_category_recommendations(db, username, project_code, limit=limit, offset=offset)
            return feed

        # try personalized, fallback to cold start
        feed = await get_personalized_recommendations(db, username, limit=limit, offset=offset)
        if not feed:
            feed = await get_cold_start_recommendations(db, username, limit=limit, offset=offset)

        await cache_user_feed(username, feed)
        return feed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


