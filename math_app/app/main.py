"""FastAPI application for the Math Teaching System."""

import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.requests import Request

from math_app.core.models import (
    LessonCreate,
    LessonResponse,
    LessonUpdate,
    TopicEnum,
    LevelEnum,
    Problem,
    AttemptCreate,
    AttemptResponse,
    validate_math_answer,
)
from math_app.core.database import get_session
from math_app.core.models_orm import LessonORM, UserAttemptORM, UserORM
from math_app.core.exceptions import MathAPIException, LessonNotFound
from math_app.app import auth

app = FastAPI(
    title="Math Teaching API",
    description="A simplified backend for teaching math progressively",
    version="0.1.0",
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include auth router
app.include_router(auth.router)


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

    # Convert problems to JSON with generated IDs
    problems_list = [
        {**p.model_dump(), "id": str(uuid4())} 
        for p in lesson_create.problems
    ] if lesson_create.problems else []
    
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
        problems_list = [
            {**p.model_dump(), "id": str(uuid4())} 
            for p in lesson_update.problems
        ]
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


@app.post("/problems/{problem_id}/submit", response_model=dict, status_code=200, tags=["problems"])
async def submit_problem_answer(
    problem_id: str,
    attempt: AttemptCreate,
    session: Session = Depends(get_session),
    current_user = Depends(auth.get_current_user),
):
    """
    Submit an answer to a problem.
    
    Returns:
    - is_correct: Whether the submitted answer is correct
    - attempt_number: Current attempt number for this problem by this user
    - feedback: Feedback message about correctness
    """
    if attempt.problem_id != problem_id:
        raise HTTPException(status_code=400, detail="Problem ID mismatch")
    
    # Find the correct answer for this problem by searching all lessons
    all_lessons = session.query(LessonORM).all()
    correct_answer = None
    explanation = None
    
    for lesson_orm in all_lessons:
        problems_data = json.loads(lesson_orm.problems_json)
        for problem_data in problems_data:
            if problem_data["id"] == problem_id:
                correct_answer = problem_data["answer"]
                explanation = problem_data.get("explanation")
                break
        if correct_answer:
            break
    
    if not correct_answer:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Validate the answer
    is_correct = validate_math_answer(attempt.submitted_answer, correct_answer)
    
    # Get current attempt number
    attempt_count = session.query(UserAttemptORM).filter(
        UserAttemptORM.user_id == current_user.id,
        UserAttemptORM.problem_id == problem_id,
    ).count()
    attempt_number = attempt_count + 1
    
    # Save the attempt
    attempt_orm = UserAttemptORM(
        id=str(uuid4()),
        user_id=current_user.id,
        problem_id=problem_id,
        submitted_answer=attempt.submitted_answer,
        is_correct=1 if is_correct else 0,
        attempt_number=attempt_number,
        created_at=datetime.now(timezone.utc),
    )
    session.add(attempt_orm)
    session.commit()
    
    # Prepare response
    feedback = "Correct!" if is_correct else "Incorrect. Try again."
    response = {
        "is_correct": is_correct,
        "attempt_number": attempt_number,
        "feedback": feedback,
    }
    
    if explanation:
        response["explanation"] = explanation
    
    return response


@app.get("/users/{user_id}/attempts", response_model=list[AttemptResponse], tags=["attempts"])
async def get_user_attempts(
    user_id: str,
    problem_id: str | None = Query(None, description="Filter by problem ID"),
    limit: int = Query(100, description="Maximum number of attempts to return"),
    session: Session = Depends(get_session),
    current_user = Depends(auth.get_current_user),
):
    """
    Get attempts for a user.
    
    Requires authentication. Users can only view their own attempts.
    
    Query Parameters:
    - problem_id: Filter attempts to a specific problem (optional)
    - limit: Maximum number of attempts to return (default: 100)
    """
    # Users can only view their own attempts
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own attempts")
    
    query = session.query(UserAttemptORM).filter(UserAttemptORM.user_id == user_id)
    
    if problem_id:
        query = query.filter(UserAttemptORM.problem_id == problem_id)
    
    attempts = query.order_by(UserAttemptORM.created_at.desc()).limit(limit).all()
    
    return [
        AttemptResponse(
            id=attempt.id,
            user_id=attempt.user_id,
            problem_id=attempt.problem_id,
            submitted_answer=attempt.submitted_answer,
            is_correct=bool(attempt.is_correct),
            attempt_number=attempt.attempt_number,
            time_spent_seconds=attempt.time_spent_seconds,
            created_at=attempt.created_at,
        )
        for attempt in attempts
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
