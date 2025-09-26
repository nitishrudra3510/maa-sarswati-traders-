from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=100)


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: Optional[str] = Field(default=None, max_length=100)
    metadata: Optional[dict] = None


class PostOut(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EngagementBase(BaseModel):
    user_id: int
    post_id: int
    type: Literal["view", "like", "inspire", "rating"]
    rating_score: Optional[int] = Field(default=None, ge=1, le=5)

    @validator("rating_score")
    def rating_required_when_type_rating(cls, v, values):
        if values.get("type") == "rating" and v is None:
            raise ValueError("rating_score is required when type is 'rating'")
        return v


class EngagementOut(EngagementBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


