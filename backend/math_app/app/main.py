"""FastAPI application for the Math Teaching System."""

import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.responses import JSONResponse, FileResponse
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
from math_app.core.learning_algorithms import (
    get_next_problems_by_spaced_repetition,
    recommend_difficulty_level,
    get_user_attempt_stats,
)
from math_app.core.security import get_current_user_from_token
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


# Dependency: Extract current user from Authorization header
async def get_current_user(
    authorization: str | None = Header(None),
    session: Session = Depends(get_session),
):
    """Extract and validate user from Authorization header with Bearer token."""
    # Validate token
    await get_current_user_from_token(authorization)
    
    # Get payload from token
    payload = await get_current_user_from_token(authorization)
    user_id = payload.get("sub")
    
    # Get user object from database
    user = session.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@app.exception_handler(MathAPIException)
async def math_api_exception_handler(request: Request, exc: MathAPIException):
    """Handle custom MathAPIException errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/api/help", tags=["root"])
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


@app.get("/lessons/{lesson_id}/recommended-problems", response_model=list[Problem], tags=["lessons"])
async def get_recommended_problems(
    lesson_id: str,
    strategy: str = Query("spaced_repetition", description="Strategy: spaced_repetition or newest"),
    session: Session = Depends(get_session),
    current_user = Depends(auth.get_current_user),
):
    """
    Get problems recommended for a user based on their performance.
    
    Query Parameters:
    - strategy: 'spaced_repetition' (default) or 'newest'
    
    Spaced repetition strategy:
    - Prioritizes problems with recent wrong attempts
    - Shows problems due for review (3+ days after last correct attempt)
    - Retires problems solved correctly 3+ times
    - Shows new problems last
    """
    lesson_orm = session.query(LessonORM).filter(LessonORM.id == lesson_id).first()
    if not lesson_orm:
        raise LessonNotFound(lesson_id)
    
    if strategy == "spaced_repetition":
        problems_data = get_next_problems_by_spaced_repetition(
            session, current_user.id, lesson_id
        )
    else:
        # Default to newest (all problems)
        problems_data = json.loads(lesson_orm.problems_json)
    
    # Convert to Problem response models
    return [Problem(**p) for p in problems_data]


@app.get("/users/{user_id}/dashboard", response_model=dict, tags=["users"])
async def get_user_dashboard(
    user_id: str,
    session: Session = Depends(get_session),
    current_user = Depends(auth.get_current_user),
):
    """
    Get user's learning dashboard with statistics and progress.
    
    Returns:
    - total_problems_solved: Number of unique problems attempted
    - total_attempts: Total submission count
    - accuracy: Percentage of correct submissions
    - streak: Current correct answer streak
    - next_review_due: Estimated date of next problem due for review
    """
    # Users can only view their own dashboard
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own dashboard")
    
    stats = get_user_attempt_stats(session, user_id)
    
    # Find next problem due for review
    all_attempts = session.query(UserAttemptORM).filter(
        UserAttemptORM.user_id == user_id
    ).all()
    
    next_review_due = None
    if all_attempts:
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        
        # Find oldest correct attempt that's less than 3 days old
        for attempt in sorted(all_attempts, key=lambda a: a.created_at):
            if attempt.is_correct == 1:
                days_since = (now - attempt.created_at).days
                if days_since < 3:
                    days_until_due = 3 - days_since
                    next_review_due = (now + timedelta(days=days_until_due)).isoformat()
                    break
    
    return {
        **stats,
        "next_review_due": next_review_due,
    }


@app.get("/problems/{problem_id}/hint", response_model=dict, tags=["problems"])
async def get_progressive_hint(
    problem_id: str,
    attempt_number: int = Query(1, description="User's current attempt number"),
    session: Session = Depends(get_session),
    current_user = Depends(auth.get_current_user),
):
    """
    Get a progressive hint for a problem based on attempt count.
    
    Strategy:
    - Attempt 1: No hint (user should try first)
    - Attempt 2-3: Show hint if available
    - Attempt 4+: Show explanation if available
    
    Query Parameters:
    - attempt_number: Current attempt count (default: 1)
    """
    # Find the problem
    all_lessons = session.query(LessonORM).all()
    problem_data = None
    
    for lesson_orm in all_lessons:
        problems_data = json.loads(lesson_orm.problems_json)
        for problem in problems_data:
            if problem["id"] == problem_id:
                problem_data = problem
                break
        if problem_data:
            break
    
    if not problem_data:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    response = {}
    
    if attempt_number >= 4 and problem_data.get("explanation"):
        response["hint_type"] = "explanation"
        response["hint"] = problem_data["explanation"]
    elif attempt_number >= 2 and problem_data.get("hint"):
        response["hint_type"] = "hint"
        response["hint"] = problem_data["hint"]
    else:
        response["hint_type"] = "none"
        response["hint"] = "Try again! You can do it."
    
    return response


@app.post("/users/{user_id}/difficulty-recommendation", response_model=dict, tags=["users"])
async def get_difficulty_recommendation(
    user_id: str,
    topic: TopicEnum,
    session: Session = Depends(get_session),
    current_user = Depends(auth.get_current_user),
):
    """
    Get difficulty level recommendation for a user on a specific topic.
    
    Returns:
    - recommended_level: 'beginner', 'intermediate', or 'advanced'
    - reason: Explanation based on recent performance
    - accuracy: Current accuracy on this topic (last 10 attempts)
    """
    # Users can only get their own recommendations
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own recommendations")
    
    recommended_level = recommend_difficulty_level(session, user_id, topic.value)
    
    # Calculate accuracy on this topic for context
    all_lessons = session.query(LessonORM).filter(LessonORM.topic == topic).all()
    problem_ids_for_topic = set()
    for lesson in all_lessons:
        problems_data = json.loads(lesson.problems_json)
        for problem in problems_data:
            problem_ids_for_topic.add(problem["id"])
    
    attempts = session.query(UserAttemptORM).filter(
        UserAttemptORM.user_id == user_id,
        UserAttemptORM.problem_id.in_(list(problem_ids_for_topic)) if problem_ids_for_topic else False
    ).order_by(UserAttemptORM.created_at.desc()).limit(10).all()
    
    if attempts:
        correct_count = sum(1 for a in attempts if a.is_correct == 1)
        accuracy = (correct_count / len(attempts) * 100)
    else:
        accuracy = 0
    
    # Generate reason
    if accuracy > 80:
        reason = "Great job! You're ready for more challenging problems."
    elif accuracy < 50:
        reason = "Keep practicing! This level will help build your foundation."
    else:
        reason = "You're doing well. Continue at this level or challenge yourself."
    
    return {
        "recommended_level": recommended_level,
        "reason": reason,
        "accuracy": round(accuracy, 1),
        "topic": topic.value,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

import os

@app.get("/")
def serve_frontend():
    # Use path relative to the root of the repo rather than the hardcoded '/app'
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "frontend.html")
    return FileResponse(file_path)
