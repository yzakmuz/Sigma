"""
SQLAlchemy ORM models for the Math Teaching API.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic: Mapped[TopicEnum] = mapped_column(SQLEnum(TopicEnum), nullable=False, index=True)
    level: Mapped[LevelEnum] = mapped_column(SQLEnum(LevelEnum), nullable=False, index=True)
    problems_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # Stored as JSON string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    user_progress: Mapped[List["UserProgressORM"]] = relationship("UserProgressORM", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LessonORM(id={self.id}, title={self.title})>"


class UserORM(Base):
    """ORM model for users (prepared for future authentication)."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    progress: Mapped[List["UserProgressORM"]] = relationship("UserProgressORM", back_populates="user", cascade="all, delete-orphan")
    attempts: Mapped[List["UserAttemptORM"]] = relationship("UserAttemptORM", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserORM(id={self.id}, username={self.username})>"


class UserProgressORM(Base):
    """ORM model for tracking user progress on lessons."""
    __tablename__ = "user_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id: Mapped[str] = mapped_column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[ProgressStatusEnum] = mapped_column(
        SQLEnum(ProgressStatusEnum),
        nullable=False,
        default=ProgressStatusEnum.NOT_STARTED,
        index=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="progress")
    lesson: Mapped["LessonORM"] = relationship("LessonORM", back_populates="user_progress")

    def __repr__(self):
        return f"<UserProgressORM(user_id={self.user_id}, lesson_id={self.lesson_id}, status={self.status})>"


class UserAttemptORM(Base):
    """ORM model for tracking user problem submission attempts."""
    __tablename__ = "user_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    submitted_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0=False, 1=True
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="attempts")

    def __repr__(self):
        return f"<UserAttemptORM(user_id={self.user_id}, problem_id={self.problem_id}, is_correct={self.is_correct})>"
