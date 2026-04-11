"""Data models for the Math Teaching API."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TopicEnum(str, Enum):
    """Math topics supported by the system."""
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"


class LevelEnum(str, Enum):
    """Difficulty levels for lessons."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Problem(BaseModel):
    """A single math problem."""
    id: str = Field(..., description="Unique problem identifier")
    question: str = Field(..., description="The problem statement")
    answer: str = Field(..., description="The correct answer")
    difficulty: LevelEnum = Field(..., description="Problem difficulty")
    hint: Optional[str] = Field(None, description="Optional hint for solving")


class ProblemCreate(BaseModel):
    """Input schema for creating a problem."""
    question: str = Field(..., min_length=1, description="The problem statement")
    answer: str = Field(..., min_length=1, description="The correct answer")
    difficulty: LevelEnum = Field(..., description="Problem difficulty")
    hint: Optional[str] = Field(None, description="Optional hint")


class Lesson(BaseModel):
    """A lesson containing one or more math problems."""
    id: str = Field(..., description="Unique lesson identifier")
    title: str = Field(..., description="Lesson title")
    description: str = Field(..., description="Lesson description")
    topic: TopicEnum = Field(..., description="Math topic covered")
    level: LevelEnum = Field(..., description="Overall difficulty level")
    problems: list[Problem] = Field(default_factory=list, description="Problems in this lesson")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class LessonCreate(BaseModel):
    """Input schema for creating a lesson."""
    title: str = Field(..., min_length=1, max_length=200, description="Lesson title")
    description: str = Field(..., min_length=1, description="Lesson description")
    topic: TopicEnum = Field(..., description="Math topic")
    level: LevelEnum = Field(..., description="Overall difficulty level")
    problems: list[ProblemCreate] = Field(default_factory=list, description="Initial problems for the lesson")


class LessonUpdate(BaseModel):
    """Input schema for updating a lesson."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    topic: Optional[TopicEnum] = None
    level: Optional[LevelEnum] = None
    problems: Optional[list[ProblemCreate]] = None


class LessonResponse(BaseModel):
    """Response schema for lesson endpoints."""
    id: str
    title: str
    description: str
    topic: TopicEnum
    level: LevelEnum
    problems: list[Problem]
    created_at: datetime
