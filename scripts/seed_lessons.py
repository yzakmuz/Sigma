"""Seed script to populate sample math lessons."""

import json
from math_app.models import LessonCreate, TopicEnum, LevelEnum
from math_app.repository import get_repository


def seed_lessons():
    """Populate the repository with sample lessons across topics and levels."""
    repository = get_repository()

    # Sample lessons to seed
    lessons = [
        {
            "title": "Basic Addition",
            "description": "Learn simple addition with single-digit numbers",
            "topic": TopicEnum.ARITHMETIC,
            "level": LevelEnum.BEGINNER,
            "problems": [
                {
                    "question": "What is 2 + 3?",
                    "answer": "5",
                    "difficulty": LevelEnum.BEGINNER,
                    "hint": "Count on your fingers",
                },
                {
                    "question": "What is 5 + 4?",
                    "answer": "9",
                    "difficulty": LevelEnum.BEGINNER,
                    "hint": "Start with 5 and count 4 more",
                },
                {
                    "question": "What is 6 + 3?",
                    "answer": "9",
                    "difficulty": LevelEnum.BEGINNER,
                    "hint": None,
                },
            ],
        },
        {
            "title": "Subtraction Basics",
            "description": "Introduction to subtraction with small numbers",
            "topic": TopicEnum.ARITHMETIC,
            "level": LevelEnum.BEGINNER,
            "problems": [
                {
                    "question": "What is 7 - 2?",
                    "answer": "5",
                    "difficulty": LevelEnum.BEGINNER,
                    "hint": "Remove 2 from 7",
                },
                {
                    "question": "What is 10 - 3?",
                    "answer": "7",
                    "difficulty": LevelEnum.BEGINNER,
                    "hint": None,
                },
            ],
        },
        {
            "title": "Multiplication Fundamentals",
            "description": "Learn multiplication as repeated addition",
            "topic": TopicEnum.ARITHMETIC,
            "level": LevelEnum.INTERMEDIATE,
            "problems": [
                {
                    "question": "What is 3 × 4?",
                    "answer": "12",
                    "difficulty": LevelEnum.INTERMEDIATE,
                    "hint": "Think of 4 groups of 3",
                },
                {
                    "question": "What is 5 × 6?",
                    "answer": "30",
                    "difficulty": LevelEnum.INTERMEDIATE,
                    "hint": None,
                },
                {
                    "question": "What is 7 × 8?",
                    "answer": "56",
                    "difficulty": LevelEnum.INTERMEDIATE,
                    "hint": None,
                },
            ],
        },
        {
            "title": "Linear Equations",
            "description": "Solve equations of the form ax + b = c",
            "topic": TopicEnum.ALGEBRA,
            "level": LevelEnum.INTERMEDIATE,
            "problems": [
                {
                    "question": "Solve: 2x + 3 = 7",
                    "answer": "2",
                    "difficulty": LevelEnum.INTERMEDIATE,
                    "hint": "Subtract 3 from both sides, then divide by 2",
                },
                {
                    "question": "Solve: 3x - 5 = 10",
                    "answer": "5",
                    "difficulty": LevelEnum.INTERMEDIATE,
                    "hint": "Add 5 to both sides first",
                },
            ],
        },
        {
            "title": "Quadratic Equations",
            "description": "Solve equations of the form ax² + bx + c = 0",
            "topic": TopicEnum.ALGEBRA,
            "level": LevelEnum.ADVANCED,
            "problems": [
                {
                    "question": "Solve: x² - 5x + 6 = 0",
                    "answer": "x = 2 or x = 3",
                    "difficulty": LevelEnum.ADVANCED,
                    "hint": "Use the quadratic formula or factor the equation",
                },
                {
                    "question": "Solve: 2x² + 3x - 2 = 0",
                    "answer": "x = 0.5 or x = -2",
                    "difficulty": LevelEnum.ADVANCED,
                    "hint": "Factor or use the quadratic formula",
                },
            ],
        },
        {
            "title": "Basic Geometry",
            "description": "Calculate area and perimeter of simple shapes",
            "topic": TopicEnum.GEOMETRY,
            "level": LevelEnum.BEGINNER,
            "problems": [
                {
                    "question": "What is the area of a square with side 5?",
                    "answer": "25",
                    "difficulty": LevelEnum.BEGINNER,
                    "hint": "Area = side × side",
                },
                {
                    "question": "What is the perimeter of a rectangle with length 4 and width 3?",
                    "answer": "14",
                    "difficulty": LevelEnum.BEGINNER,
                    "hint": "Perimeter = 2(length + width)",
                },
            ],
        },
        {
            "title": "Triangle Properties",
            "description": "Learn about triangle angles and sides",
            "topic": TopicEnum.GEOMETRY,
            "level": LevelEnum.INTERMEDIATE,
            "problems": [
                {
                    "question": "What is the sum of angles in a triangle?",
                    "answer": "180 degrees",
                    "difficulty": LevelEnum.INTERMEDIATE,
                    "hint": "The sum is always constant",
                },
                {
                    "question": "In a right triangle with legs 3 and 4, what is the hypotenuse?",
                    "answer": "5",
                    "difficulty": LevelEnum.INTERMEDIATE,
                    "hint": "Use the Pythagorean theorem: a² + b² = c²",
                },
            ],
        },
    ]

    # Create and insert lessons
    created_count = 0
    for lesson_data in lessons:
        try:
            lesson_create = LessonCreate(
                title=lesson_data["title"],
                description=lesson_data["description"],
                topic=lesson_data["topic"],
                level=lesson_data["level"],
                problems=lesson_data["problems"],
            )
            lesson = repository.create(lesson_create)
            created_count += 1
            print(f"✓ Created: {lesson.title} ({lesson.topic.value}/{lesson.level.value})")
        except Exception as e:
            print(f"✗ Failed to create lesson '{lesson_data['title']}': {e}")

    print(f"\n📚 Seeding complete! {created_count}/{len(lessons)} lessons created.")
    print("\nTo view the lessons, run the API and visit:")
    print("  - http://localhost:8000/docs (Swagger UI)")
    print("  - http://localhost:8000/lessons (JSON list)")
    print("\nTo filter by topic:")
    print("  - http://localhost:8000/lessons?topic=arithmetic")
    print("  - http://localhost:8000/lessons?topic=algebra")
    print("  - http://localhost:8000/lessons?topic=geometry")


if __name__ == "__main__":
    seed_lessons()
