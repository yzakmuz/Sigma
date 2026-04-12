"""
SQLAlchemy ORM models for the Math Teaching API.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from math_app.core.database import Base
from math_app.core.models import LevelEnum, TopicEnum


class ProgressStatusEnum(str, Enum):
    """Status of user progress on a lesson."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LessonORM(Base):
    """ORM model for lessons."""
    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    topic = Column(SQLEnum(TopicEnum), nullable=False, index=True)
    level = Column(SQLEnum(LevelEnum), nullable=False, index=True)
    problems_json = Column(Text, nullable=False, default="[]")  # Stored as JSON string
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    user_progress = relationship("UserProgressORM", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LessonORM(id={self.id}, title={self.title})>"


class UserORM(Base):
    """ORM model for users (prepared for future authentication)."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    progress = relationship("UserProgressORM", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserORM(id={self.id}, username={self.username})>"


class UserProgressORM(Base):
    """ORM model for tracking user progress on lessons."""
    __tablename__ = "user_progress"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        SQLEnum(ProgressStatusEnum),
        nullable=False,
        default=ProgressStatusEnum.NOT_STARTED,
        index=True
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("UserORM", back_populates="progress")
    lesson = relationship("LessonORM", back_populates="user_progress")

    def __repr__(self):
        return f"<UserProgressORM(user_id={self.user_id}, lesson_id={self.lesson_id}, status={self.status})>"
