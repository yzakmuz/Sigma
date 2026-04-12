"""FastAPI application for the Math Teaching System."""

import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from math_app.core.models import (
    LessonCreate,
    LessonResponse,
    LessonUpdate,
    TopicEnum,
    LevelEnum,
    Problem,
)
from math_app.core.database import get_session
from math_app.core.models_orm import LessonORM
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


@app.get("/", tags=["root"])
async def root():
    """Welcome endpoint with available endpoints."""
    return {
        "message": "Welcome to the Math Teaching API",
        "endpoints": {
            "documentation": "/docs",
            "openapi_schema": "/openapi.json",
            "health_check": "/health",
            "lessons": {
                "list_all": "GET /lessons",
                "list_filtered": "GET /lessons?topic=arithmetic&level=beginner",
                "create": "POST /lessons",
                "get_by_id": "GET /lessons/{lesson_id}",
                "update": "PUT /lessons/{lesson_id}",
                "delete": "DELETE /lessons/{lesson_id}",
            },
        },
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Check if the API is running."""
    return JSONResponse({"status": "healthy"})


@app.get("/lessons", response_model=list[LessonResponse], tags=["lessons"])
async def list_lessons(
    topic: TopicEnum | None = Query(None, description="Filter by topic"),
    level: LevelEnum | None = Query(None, description="Filter by difficulty level"),
    session: Session = Depends(get_session),
):
    """
    List all lessons with optional filtering.

    Query Parameters:
    - topic: Filter by topic (arithmetic, algebra, geometry)
    - level: Filter by level (beginner, intermediate, advanced)
    """
    query = session.query(LessonORM)
    
    if topic:
        query = query.filter(LessonORM.topic == topic)
    if level:
        query = query.filter(LessonORM.level == level)
    
    lessons = query.all()
    
    # Convert ORM objects to response with problems parsed from JSON
    result = []
    for lesson_orm in lessons:
        problems_data = json.loads(lesson_orm.problems_json)
        problems = [Problem(**p) for p in problems_data]
        result.append(LessonResponse(
            id=lesson_orm.id,
            title=lesson_orm.title,
            description=lesson_orm.description,
            topic=lesson_orm.topic,
            level=lesson_orm.level,
            problems=problems,
            created_at=lesson_orm.created_at,
        ))
    
    return result


@app.post("/lessons", response_model=LessonResponse, status_code=201, tags=["lessons"])
async def create_lesson(
    lesson_create: LessonCreate,
    session: Session = Depends(get_session),
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

    # Convert problems to JSON
    problems_list = [p.model_dump() for p in lesson_create.problems] if lesson_create.problems else []
    
    lesson_orm = LessonORM(
        id=str(uuid4()),
        title=lesson_create.title,
        description=lesson_create.description,
        topic=lesson_create.topic,
        level=lesson_create.level,
        problems_json=json.dumps(problems_list),
        created_at=datetime.now(timezone.utc),
    )
    
    session.add(lesson_orm)
    session.commit()
    session.refresh(lesson_orm)
    
    # Convert back to response model
    problems = [Problem(**p) for p in problems_list]
    return LessonResponse(
        id=lesson_orm.id,
        title=lesson_orm.title,
        description=lesson_orm.description,
        topic=lesson_orm.topic,
        level=lesson_orm.level,
        problems=problems,
        created_at=lesson_orm.created_at,
    )


@app.get("/lessons/{lesson_id}", response_model=LessonResponse, tags=["lessons"])
async def get_lesson(
    lesson_id: str,
    session: Session = Depends(get_session),
):
    """Retrieve a specific lesson by ID."""
    lesson_orm = session.query(LessonORM).filter(LessonORM.id == lesson_id).first()
    if not lesson_orm:
        raise LessonNotFound(lesson_id)
    
    problems_data = json.loads(lesson_orm.problems_json)
    problems = [Problem(**p) for p in problems_data]
    
    return LessonResponse(
        id=lesson_orm.id,
        title=lesson_orm.title,
        description=lesson_orm.description,
        topic=lesson_orm.topic,
        level=lesson_orm.level,
        problems=problems,
        created_at=lesson_orm.created_at,
    )


@app.put("/lessons/{lesson_id}", response_model=LessonResponse, tags=["lessons"])
async def update_lesson(
    lesson_id: str,
    lesson_update: LessonUpdate,
    session: Session = Depends(get_session),
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
    lesson_orm = session.query(LessonORM).filter(LessonORM.id == lesson_id).first()
    if not lesson_orm:
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

    # Update fields
    if lesson_update.title is not None:
        lesson_orm.title = lesson_update.title
    if lesson_update.description is not None:
        lesson_orm.description = lesson_update.description
    if lesson_update.topic is not None:
        lesson_orm.topic = lesson_update.topic
    if lesson_update.level is not None:
        lesson_orm.level = lesson_update.level
    if lesson_update.problems is not None:
        problems_list = [p.model_dump() for p in lesson_update.problems]
        lesson_orm.problems_json = json.dumps(problems_list)

    session.commit()
    session.refresh(lesson_orm)

    # Convert back to response model
    problems_data = json.loads(lesson_orm.problems_json)
    problems = [Problem(**p) for p in problems_data]
    
    return LessonResponse(
        id=lesson_orm.id,
        title=lesson_orm.title,
        description=lesson_orm.description,
        topic=lesson_orm.topic,
        level=lesson_orm.level,
        problems=problems,
        created_at=lesson_orm.created_at,
    )


@app.delete("/lessons/{lesson_id}", status_code=204, tags=["lessons"])
async def delete_lesson(
    lesson_id: str,
    session: Session = Depends(get_session),
):
    """
    Delete a lesson.

    Returns a 204 No Content response on success.
    """
    lesson_orm = session.query(LessonORM).filter(LessonORM.id == lesson_id).first()
    if not lesson_orm:
        raise LessonNotFound(lesson_id)
    
    session.delete(lesson_orm)
    session.commit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
