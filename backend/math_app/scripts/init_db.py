"""
Database initialization script.
Runs migrations and seeds sample data into the database.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# Add parent directory to path so we can import math_app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from math_app.core.database import SessionLocal, engine
from math_app.core.models_orm import LessonORM


def init_database():
    """Initialize database: run migrations and seed sample data."""
    print("🔧 Initializing database...")

    # Create all tables
    from math_app.core.models_orm import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

    # Seed sample lessons if not already seeded
    session = SessionLocal()
    try:
        existing_lessons = session.query(LessonORM).count()
        if existing_lessons > 0:
            print(f"ℹ️  Database already has {existing_lessons} lessons, skipping seed")
            return

        # Load sample data from JSON
        sample_db_path = Path(__file__).parent.parent.parent.parent / "db" / "sample_db.json"
        if not sample_db_path.exists():
            print(f"⚠️  Sample database not found at {sample_db_path}")
            return

        with open(sample_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        lessons_data = data.get("lessons", [])
        print(f"📚 Loading {len(lessons_data)} lessons from sample_db.json...")

        for lesson_data in lessons_data:
            # Convert problems to JSON string
            problems_json = json.dumps(lesson_data.get("problems", []))

            lesson = LessonORM(
                id=lesson_data["id"],
                title=lesson_data["title"],
                description=lesson_data["description"],
                topic=lesson_data["topic"],
                level=lesson_data["level"],
                problems_json=problems_json,
                created_at=datetime.fromisoformat(lesson_data["created_at"].replace("Z", "+00:00")),
            )
            session.add(lesson)

        session.commit()
        print(f"✅ Seeded {len(lessons_data)} lessons into database")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
    print("🎉 Database initialization complete!")
