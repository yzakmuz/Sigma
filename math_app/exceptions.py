"""Custom exceptions for the Math Teaching API."""


class MathAPIException(Exception):
    """Base exception for the Math Teaching API."""

    def __init__(self, message: str, status_code: int):
        """Initialize the exception."""
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LessonNotFound(MathAPIException):
    """Raised when a lesson is not found."""

    def __init__(self, lesson_id: str):
        """Initialize the exception."""
        super().__init__(
            f"Lesson with ID '{lesson_id}' not found", status_code=404
        )


class InvalidLesson(MathAPIException):
    """Raised when lesson data is invalid."""

    def __init__(self, message: str):
        """Initialize the exception."""
        super().__init__(message, status_code=422)


class InvalidTopic(MathAPIException):
    """Raised when a topic is invalid."""

    def __init__(self, topic: str):
        """Initialize the exception."""
        valid_topics = ["arithmetic", "algebra", "geometry"]
        super().__init__(
            f"Invalid topic '{topic}'. Must be one of: {', '.join(valid_topics)}",
            status_code=422,
        )


class InvalidLevel(MathAPIException):
    """Raised when a level is invalid."""

    def __init__(self, level: str):
        """Initialize the exception."""
        valid_levels = ["beginner", "intermediate", "advanced"]
        super().__init__(
            f"Invalid level '{level}'. Must be one of: {', '.join(valid_levels)}",
            status_code=422,
        )
