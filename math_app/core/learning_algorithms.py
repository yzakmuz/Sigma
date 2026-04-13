"""Business logic for spaced repetition and adaptive learning."""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from math_app.core.models_orm import UserAttemptORM, LessonORM
import json
from typing import Optional


def get_next_problems_by_spaced_repetition(
    session: Session,
    user_id: str,
    lesson_id: str,
) -> list[dict]:
    """
    Get problems ordered by spaced repetition algorithm.
    
    Strategy:
    - Problems with 3+ correct attempts: retire (don't show)
    - Problems with 1 correct attempt shown 3+ days ago: show now
    - Problems with incorrect attempt: show immediately (prioritize)
    - New problems: show after incorrect/due for review
    
    Returns list of problem dicts ordered by priority.
    """
    lesson_orm = session.query(LessonORM).filter(LessonORM.id == lesson_id).first()
    if not lesson_orm:
        return []
    
    problems_data = json.loads(lesson_orm.problems_json)
    now = datetime.now(timezone.utc)
    
    # Categorize problems
    priority_problems = []  # Wrong answers - show immediately
    due_for_review = []    # Correct but 3+ days old
    new_problems = []       # No attempts
    retired_problems = set()  # 3+ correct attempts
    
    for problem in problems_data:
        problem_id = problem["id"]
        
        # Get all attempts for this problem by this user
        attempts = session.query(UserAttemptORM).filter(
            UserAttemptORM.user_id == user_id,
            UserAttemptORM.problem_id == problem_id,
        ).order_by(UserAttemptORM.created_at.desc()).all()
        
        if not attempts:
            # No attempts - it's a new problem
            new_problems.append(problem)
        else:
            # Check correctness stats
            correct_count = sum(1 for a in attempts if a.is_correct == 1)
            
            if correct_count >= 3:
                # Retire this problem
                retired_problems.add(problem_id)
            elif correct_count == 0:
                # All attempts wrong - prioritize
                priority_problems.append(problem)
            elif correct_count >= 1:
                # Has correct attempts - check if due for review
                last_correct_attempt = next(a for a in attempts if a.is_correct == 1)
                days_since_correct = (now - last_correct_attempt.created_at).days
                
                if days_since_correct >= 3:
                    due_for_review.append(problem)
    
    # Order: priority > due_for_review > new
    result = priority_problems + due_for_review + new_problems
    return [p for p in result if p["id"] not in retired_problems]


def recommend_difficulty_level(
    session: Session,
    user_id: str,
    topic: str,
) -> str:
    """
    Recommend difficulty level for a user on a topic.
    
    Based on accuracy of last 10 attempts on the topic:
    - > 80% accuracy: recommend next level
    - 50-80% accuracy: stay at current level
    - < 50% accuracy: recommend previous/same level
    
    Returns: 'beginner', 'intermediate', or 'advanced'
    """
    # Get last 10 attempts from lessons with this topic
    attempts = session.query(UserAttemptORM).join(
        LessonORM,
        lambda: True  # We'll filter manually
    ).filter(
        UserAttemptORM.user_id == user_id
    ).order_by(UserAttemptORM.created_at.desc()).limit(10).all()
    
    if not attempts:
        return "beginner"
    
    # Find out which of these attempts are on lessons with this topic
    lesson_ids_by_topic = set()
    all_lessons = session.query(LessonORM).filter(LessonORM.topic == topic).all()
    for lesson in all_lessons:
        problems_data = json.loads(lesson.problems_json)
        for problem in problems_data:
            lesson_ids_by_topic.add((lesson.id, problem["id"]))
    
    # Filter attempts to only those on this topic
    topic_attempts = []
    for attempt in attempts:
        # Check if this attempt's problem is in a lesson with this topic
        for lesson_id, problem_id in lesson_ids_by_topic:
            if attempt.problem_id == problem_id:
                topic_attempts.append(attempt)
                break
    
    if not topic_attempts:
        return "beginner"
    
    # Calculate accuracy
    correct_count = sum(1 for a in topic_attempts if a.is_correct == 1)
    accuracy = correct_count / len(topic_attempts)
    
    if accuracy > 0.80:
        return "advanced"  # Recommend stepping up (simplified - would need current level)
    elif accuracy < 0.50:
        return "beginner"  # Recommend stepping down or staying
    else:
        return "intermediate"  # Stay at current level


def get_user_attempt_stats(
    session: Session,
    user_id: str,
    limit_problems: int = 50,
) -> dict:
    """
    Get user's performance statistics.
    
    Returns:
    - total_problems_solved: Number of unique problems attempted
    - total_attempts: Total submission count
    - accuracy: Percentage of correct submissions
    - streak: Current correct answer streak
    """
    attempts = session.query(UserAttemptORM).filter(
        UserAttemptORM.user_id == user_id
    ).order_by(UserAttemptORM.created_at.desc()).all()
    
    if not attempts:
        return {
            "total_problems_solved": 0,
            "total_attempts": 0,
            "accuracy": 0.0,
            "streak": 0,
        }
    
    unique_problems = len(set(a.problem_id for a in attempts))
    total_correct = sum(1 for a in attempts if a.is_correct == 1)
    accuracy = (total_correct / len(attempts) * 100) if attempts else 0
    
    # Calculate streak (consecutive correct from most recent)
    streak = 0
    for attempt in attempts:
        if attempt.is_correct == 1:
            streak += 1
        else:
            break
    
    return {
        "total_problems_solved": unique_problems,
        "total_attempts": len(attempts),
        "accuracy": round(accuracy, 1),
        "streak": streak,
    }
