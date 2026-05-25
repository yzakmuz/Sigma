"""Pytest configuration and fixtures for the Math Teaching API."""

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from math_app.app.main import app
from math_app.core.database import get_session, get_current_user
from math_app.core.models_orm import Base


# Create a test database
@pytest.fixture(scope="function")
def test_db():
    """Create a test database using SQLite."""
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create engine with file-based database
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal, engine, db_path
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def db_session(test_db):
    """Provide a database session for testing."""
    TestingSessionLocal, engine, db_path = test_db
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Provide a TestClient with database session dependency injection."""
    
    def override_get_session():
        return db_session
    
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_lesson_create():
    """Sample lesson creation payload."""
    return {
        "title": "Basic Addition",
        "description": "Learn simple addition with single digits",
        "topic": "arithmetic",
        "level": "beginner",
        "problems": [
            {
                "question": "What is 2 + 3?",
                "answer": "5",
                "difficulty": "beginner",
                "hint": "Count on your fingers",
            },
            {
                "question": "What is 5 + 4?",
                "answer": "9",
                "difficulty": "beginner",
                "hint": None,
            },
        ],
    }


@pytest.fixture
def sample_algebra_lesson():
    """Sample algebra lesson creation payload."""
    return {
        "title": "Solving Linear Equations",
        "description": "Solve equations of the form ax + b = c",
        "topic": "algebra",
        "level": "intermediate",
        "problems": [
            {
                "question": "Solve: 2x + 3 = 7",
                "answer": "2",
                "difficulty": "intermediate",
                "hint": "Subtract 3 from both sides",
            }
        ],
    }
