"""In-memory repository for lessons."""

import uuid
from datetime import datetime

from math_app.models import Lesson, LessonCreate, LessonUpdate, Problem, ProblemCreate


class LessonRepository:
    """In-memory repository for managing lessons."""

    def __init__(self):
        """Initialize the repository with an empty lessons store."""
        self._lessons: dict[str, Lesson] = {}

    def create(self, lesson_create: LessonCreate) -> Lesson:
        """
        Create a new lesson.

        Args:
            lesson_create: The lesson data to create

        Returns:
            The created lesson with a generated ID
        """
        lesson_id = str(uuid.uuid4())
        problems = [
            Problem(
                id=str(uuid.uuid4()),
                question=p.question,
                answer=p.answer,
                difficulty=p.difficulty,
                hint=p.hint,
            )
            for p in lesson_create.problems
        ]

        lesson = Lesson(
            id=lesson_id,
            title=lesson_create.title,
            description=lesson_create.description,
            topic=lesson_create.topic,
            level=lesson_create.level,
            problems=problems,
            created_at=datetime.utcnow(),
        )

        self._lessons[lesson_id] = lesson
        return lesson

    def read(self, lesson_id: str) -> Lesson | None:
        """
        Retrieve a lesson by ID.

        Args:
            lesson_id: The ID of the lesson to retrieve

        Returns:
            The lesson if found, None otherwise
        """
        return self._lessons.get(lesson_id)

    def list(
        self, topic: str | None = None, level: str | None = None
    ) -> list[Lesson]:
        """
        List all lessons, optionally filtered by topic and level.

        Args:
            topic: Optional topic filter (case-insensitive)
            level: Optional level filter (case-insensitive)

        Returns:
            List of lessons matching the filters
        """
        lessons = list(self._lessons.values())

        if topic:
            lessons = [
                l for l in lessons if l.topic.value.lower() == topic.lower()
            ]

        if level:
            lessons = [
                l for l in lessons if l.level.value.lower() == level.lower()
            ]

        return sorted(lessons, key=lambda l: l.created_at, reverse=True)

    def update(self, lesson_id: str, lesson_update: LessonUpdate) -> Lesson | None:
        """
        Update a lesson.

        Args:
            lesson_id: The ID of the lesson to update
            lesson_update: The updated lesson data

        Returns:
            The updated lesson if found, None otherwise
        """
        lesson = self._lessons.get(lesson_id)
        if not lesson:
            return None

        # Update fields if provided
        if lesson_update.title is not None:
            lesson.title = lesson_update.title
        if lesson_update.description is not None:
            lesson.description = lesson_update.description
        if lesson_update.topic is not None:
            lesson.topic = lesson_update.topic
        if lesson_update.level is not None:
            lesson.level = lesson_update.level

        # Update problems if provided
        if lesson_update.problems is not None:
            lesson.problems = [
                Problem(
                    id=str(uuid.uuid4()),
                    question=p.question,
                    answer=p.answer,
                    difficulty=p.difficulty,
                    hint=p.hint,
                )
                for p in lesson_update.problems
            ]

        return lesson

    def delete(self, lesson_id: str) -> bool:
        """
        Delete a lesson.

        Args:
            lesson_id: The ID of the lesson to delete

        Returns:
            True if the lesson was deleted, False if not found
        """
        if lesson_id in self._lessons:
            del self._lessons[lesson_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all lessons from the repository."""
        self._lessons.clear()


# Global repository instance
_repository = LessonRepository()


def get_repository() -> LessonRepository:
    """Get the global repository instance."""
    return _repository
