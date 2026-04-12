"""Pytest configuration and fixtures for the Math Teaching API."""

import pytest
from fastapi.testclient import TestClient

from math_app.app.main import app
from math_app.core.repository import get_repository, LessonRepository


@pytest.fixture
def test_repository():
    """Provide a fresh, empty test repository for each test."""
    repo = LessonRepository()
    repo.clear()
    yield repo
    repo.clear()


@pytest.fixture
def client(test_repository):
    """Provide a TestClient with dependency injection for the test repository."""

    def get_test_repository():
        return test_repository

    app.dependency_overrides[get_repository] = get_test_repository
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
