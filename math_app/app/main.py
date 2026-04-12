"""FastAPI application for the Math Teaching System."""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from starlette.requests import Request

from math_app.core.models import (
    LessonCreate,
    LessonResponse,
    LessonUpdate,
    TopicEnum,
    LevelEnum,
)
from math_app.core.repository import LessonRepository, get_repository
from math_app.core.exceptions import MathAPIException, LessonNotFound

app = FastAPI(
    title="Math Teaching API",
    description="A simplified backend for teaching math progressively",
    version="0.1.0",
)


@app.exception_handler(MathAPIException)
async def math_api_exception_handler(request: Request, exc: MathAPIException):
    """Handle custom MathAPIException errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/health", tags=["health"])
async def health_check():
    """Check if the API is running."""
    return JSONResponse({"status": "healthy"})


@app.get("/lessons", response_model=list[LessonResponse], tags=["lessons"])
async def list_lessons(
    topic: TopicEnum | None = Query(None, description="Filter by topic"),
    level: LevelEnum | None = Query(None, description="Filter by difficulty level"),
    repository: LessonRepository = Depends(get_repository),
):
    """
    List all lessons with optional filtering.

    Query Parameters:
    - topic: Filter by topic (arithmetic, algebra, geometry)
    - level: Filter by level (beginner, intermediate, advanced)
    """
    return repository.list(
        topic=topic.value if topic else None,
        level=level.value if level else None,
    )


@app.post("/lessons", response_model=LessonResponse, status_code=201, tags=["lessons"])
async def create_lesson(
    lesson_create: LessonCreate,
    repository: LessonRepository = Depends(get_repository),
):
    """
    Create a new lesson with problems.

    Request body must include:
    - title: Lesson title
    - description: Lesson description
    - topic: Math topic (arithmetic, algebra, geometry)
    - level: Difficulty level (beginner, intermediate, advanced)
    - problems: List of problems with question, answer, difficulty, and optional hint
    """
    if not lesson_create.title or not lesson_create.title.strip():
        raise HTTPException(status_code=422, detail="Title cannot be empty")

    lesson = repository.create(lesson_create)
    return lesson


@app.get("/lessons/{lesson_id}", response_model=LessonResponse, tags=["lessons"])
async def get_lesson(
    lesson_id: str,
    repository: LessonRepository = Depends(get_repository),
):
    """Retrieve a specific lesson by ID."""
    lesson = repository.read(lesson_id)
    if not lesson:
        raise LessonNotFound(lesson_id)
    return lesson


@app.put("/lessons/{lesson_id}", response_model=LessonResponse, tags=["lessons"])
async def update_lesson(
    lesson_id: str,
    lesson_update: LessonUpdate,
    repository: LessonRepository = Depends(get_repository),
):
    """
    Update a lesson.

    Provide any of the following fields to update:
    - title
    - description
    - topic
    - level
    - problems (replaces entire problem list)
    """
    lesson = repository.read(lesson_id)
    if not lesson:
        raise LessonNotFound(lesson_id)

    # Validate that at least one field is provided
    if not any(
        [
            lesson_update.title,
            lesson_update.description,
            lesson_update.topic,
            lesson_update.level,
            lesson_update.problems,
        ]
    ):
        raise HTTPException(status_code=422, detail="No fields to update provided")

    updated_lesson = repository.update(lesson_id, lesson_update)
    return updated_lesson


@app.delete("/lessons/{lesson_id}", status_code=204, tags=["lessons"])
async def delete_lesson(
    lesson_id: str,
    repository: LessonRepository = Depends(get_repository),
):
    """
    Delete a lesson.

    Returns a 204 No Content response on success.
    """
    if not repository.delete(lesson_id):
        raise LessonNotFound(lesson_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
