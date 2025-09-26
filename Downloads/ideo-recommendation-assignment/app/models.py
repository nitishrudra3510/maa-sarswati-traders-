from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column


Base = declarative_base()


class EngagementType(str, enum.Enum):
    view = "view"
    like = "like"
    inspire = "inspire"
    rating = "rating"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    engagements: Mapped[list[Engagement]] = relationship(
        "Engagement", back_populates="user", cascade="all, delete-orphan"
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    post_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    engagements: Mapped[list[Engagement]] = relationship(
        "Engagement", back_populates="post", cascade="all, delete-orphan"
    )


class Engagement(Base):
    __tablename__ = "engagements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[EngagementType] = mapped_column(Enum(EngagementType), index=True, nullable=False)
    rating_score: Mapped[int | None] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user: Mapped[User] = relationship("User", back_populates="engagements")
    post: Mapped[Post] = relationship("Post", back_populates="engagements")


