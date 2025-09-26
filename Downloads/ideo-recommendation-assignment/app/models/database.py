"""
Database models for Video Recommendation Engine.
Uses PostgreSQL with UUID primary keys as specified in requirements.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, String, Text, ForeignKey, Integer, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model with UUID primary key."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    engagements = relationship("UserEngagement", back_populates="user", cascade="all, delete-orphan")


class Video(Base):
    """Video model with UUID primary key."""
    
    __tablename__ = "videos"
    
    video_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    posted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional fields for enhanced functionality
    description = Column(Text, nullable=True)
    video_metadata = Column(JSON, nullable=True)
    
    # Relationships
    engagements = relationship("UserEngagement", back_populates="video", cascade="all, delete-orphan")


class EngagementType(str, Enum):
    """Types of user engagement with videos."""
    VIEW = "view"
    LIKE = "like"
    INSPIRE = "inspire"
    RATING = "rating"


class UserEngagement(Base):
    """User engagement tracking model."""
    
    __tablename__ = "user_engagements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False)
    engagement_type = Column(Enum("view", "like", "inspire", "rating", name="engagement_type"), nullable=False, index=True)
    rating_score = Column(Integer, nullable=True)  # 1-5 scale for ratings
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="engagements")
    video = relationship("Video", back_populates="engagements")
