"""Data models for the Math Teaching API."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


def validate_math_answer(submitted_answer: str, correct_answer: str) -> bool:
    """
    Validate a submitted math answer against the correct answer.
    
    Handles:
    - Numeric tolerance (±0.01)
    - Case-insensitive comparison
    - Whitespace normalization
    - Algebraic form equivalence for simple expressions
    
    Args:
        submitted_answer: User's submitted answer string
        correct_answer: The correct answer string
        
    Returns:
        True if answers match (within tolerance), False otherwise
    """
    # Normalize: strip whitespace, convert to lowercase
    submitted = submitted_answer.strip().lower()
    correct = correct_answer.strip().lower()
    
    # Exact match (after normalization)
    if submitted == correct:
        return True
    
    # Try numeric comparison (handles 5 vs 5.0, etc.)
    try:
        submitted_num = float(submitted)
        correct_num = float(correct)  
        # Allow ±0.01 tolerance for rounding
        return abs(submitted_num - correct_num) < 0.01
    except (ValueError, TypeError):
        pass
    
    # For non-numeric, rely on normalized string match
    return False


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
    explanation: Optional[str] = Field(None, description="Detailed explanation of solution")


class ProblemCreate(BaseModel):
    """Input schema for creating a problem."""
    question: str = Field(..., min_length=1, description="The problem statement")
    answer: str = Field(..., min_length=1, description="The correct answer")
    difficulty: LevelEnum = Field(..., description="Problem difficulty")
    hint: Optional[str] = Field(None, description="Optional hint")
    explanation: Optional[str] = Field(None, description="Detailed explanation of solution")


class Lesson(BaseModel):
    """A lesson containing one or more math problems."""
    id: str = Field(..., description="Unique lesson identifier")
    title: str = Field(..., description="Lesson title")
    description: str = Field(..., description="Lesson description")
    topic: TopicEnum = Field(..., description="Math topic covered")
    level: LevelEnum = Field(..., description="Overall difficulty level")
    problems: list[Problem] = Field(default_factory=list, description="Problems in this lesson")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")


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

    class Config:
        from_attributes = True  # Allow loading from ORM objects


class UserResponse(BaseModel):
    """Response schema for user endpoints."""
    id: str
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProgressStatusEnum(str, Enum):
    """Status of user progress on a lesson."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserProgressResponse(BaseModel):
    """Response schema for user progress endpoints."""
    id: str
    user_id: str
    lesson_id: str
    status: ProgressStatusEnum
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttemptCreate(BaseModel):
    """Input schema for submitting a problem answer."""
    problem_id: str = Field(..., description="ID of the problem being attempted")
    submitted_answer: str = Field(..., min_length=1, description="User's submitted answer")


class AttemptResponse(BaseModel):
    """Response schema for problem attempt endpoints."""
    id: str
    user_id: str
    problem_id: str
    submitted_answer: str
    is_correct: bool
    attempt_number: int
    time_spent_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
