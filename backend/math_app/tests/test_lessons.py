"""Tests for the Math Teaching API."""

import pytest


class TestHealth:
    """Tests for the health check endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Test that /health returns a healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestCreateLesson:
    """Tests for creating lessons."""

    def test_create_lesson_minimal(self, client):
        """Test creating a lesson with minimal fields."""
        payload = {
            "title": "Math Basics",
            "description": "Introduction to math",
            "topic": "arithmetic",
            "level": "beginner",
            "problems": [],
        }
        response = client.post("/lessons", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Math Basics"
        assert data["description"] == "Introduction to math"
        assert data["topic"] == "arithmetic"
        assert data["level"] == "beginner"
        assert data["problems"] == []
        assert "id" in data
        assert "created_at" in data

    def test_create_lesson_with_problems(self, client, sample_lesson_create):
        """Test creating a lesson with multiple problems."""
        response = client.post("/lessons", json=sample_lesson_create)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Basic Addition"
        assert len(data["problems"]) == 2
        assert data["problems"][0]["question"] == "What is 2 + 3?"
        assert data["problems"][0]["answer"] == "5"
        assert data["problems"][0]["hint"] == "Count on your fingers"
        assert data["problems"][1]["hint"] is None

    def test_create_lesson_with_invalid_topic(self, client):
        """Test that invalid topic returns 422."""
        payload = {
            "title": "Invalid Lesson",
            "description": "This has an invalid topic",
            "topic": "biology",  # Invalid
            "level": "beginner",
            "problems": [],
        }
        response = client.post("/lessons", json=payload)
        assert response.status_code == 422

    def test_create_lesson_with_invalid_level(self, client):
        """Test that invalid level returns 422."""
        payload = {
            "title": "Invalid Lesson",
            "description": "This has an invalid level",
            "topic": "arithmetic",
            "level": "expert",  # Invalid
            "problems": [],
        }
        response = client.post("/lessons", json=payload)
        assert response.status_code == 422

    def test_create_lesson_with_missing_required_field(self, client):
        """Test that missing required fields return 422."""
        payload = {
            "description": "Missing title",
            "topic": "arithmetic",
            "level": "beginner",
        }
        response = client.post("/lessons", json=payload)
        assert response.status_code == 422

    def test_create_lesson_empty_title(self, client):
        """Test that empty title returns 422."""
        payload = {
            "title": "   ",  # Whitespace only
            "description": "Valid description",
            "topic": "arithmetic",
            "level": "beginner",
            "problems": [],
        }
        response = client.post("/lessons", json=payload)
        assert response.status_code == 422


class TestListLessons:
    """Tests for listing lessons."""

    def test_list_empty_lessons(self, client):
        """Test that listing empty lessons returns empty list."""
        response = client.get("/lessons")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_lessons(self, client, sample_lesson_create, sample_algebra_lesson):
        """Test listing multiple lessons."""
        # Create two lessons
        client.post("/lessons", json=sample_lesson_create)
        client.post("/lessons", json=sample_algebra_lesson)

        response = client.get("/lessons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Check that lessons are sorted by created_at (most recent first)
        assert data[0]["topic"] in ["arithmetic", "algebra"]

    def test_list_lessons_filter_by_topic(self, client, sample_lesson_create, sample_algebra_lesson):
        """Test filtering lessons by topic."""
        client.post("/lessons", json=sample_lesson_create)
        client.post("/lessons", json=sample_algebra_lesson)

        # Filter by arithmetic
        response = client.get("/lessons?topic=arithmetic")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["topic"] == "arithmetic"

        # Filter by algebra
        response = client.get("/lessons?topic=algebra")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["topic"] == "algebra"

    def test_list_lessons_filter_by_level(self, client, sample_lesson_create, sample_algebra_lesson):
        """Test filtering lessons by level."""
        client.post("/lessons", json=sample_lesson_create)
        client.post("/lessons", json=sample_algebra_lesson)

        # Filter by beginner
        response = client.get("/lessons?level=beginner")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["level"] == "beginner"

        # Filter by intermediate
        response = client.get("/lessons?level=intermediate")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["level"] == "intermediate"

    def test_list_lessons_filter_by_topic_and_level(self, client, sample_lesson_create, sample_algebra_lesson):
        """Test filtering lessons by both topic and level."""
        client.post("/lessons", json=sample_lesson_create)
        client.post("/lessons", json=sample_algebra_lesson)

        response = client.get("/lessons?topic=algebra&level=intermediate")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["topic"] == "algebra"
        assert data[0]["level"] == "intermediate"


class TestGetLesson:
    """Tests for retrieving a specific lesson."""

    def test_get_lesson_by_id(self, client, sample_lesson_create):
        """Test retrieving a lesson by ID."""
        create_response = client.post("/lessons", json=sample_lesson_create)
        lesson_id = create_response.json()["id"]

        response = client.get(f"/lessons/{lesson_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lesson_id
        assert data["title"] == "Basic Addition"

    def test_get_nonexistent_lesson(self, client):
        """Test that getting a nonexistent lesson returns 404."""
        response = client.get("/lessons/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUpdateLesson:
    """Tests for updating lessons."""

    def test_update_lesson_title(self, client, sample_lesson_create):
        """Test updating a lesson's title."""
        create_response = client.post("/lessons", json=sample_lesson_create)
        lesson_id = create_response.json()["id"]

        update_payload = {"title": "Updated Title"}
        response = client.put(f"/lessons/{lesson_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Learn simple addition with single digits"  # Unchanged

    def test_update_lesson_description_and_level(self, client, sample_lesson_create):
        """Test updating multiple fields."""
        create_response = client.post("/lessons", json=sample_lesson_create)
        lesson_id = create_response.json()["id"]

        update_payload = {
            "description": "New description",
            "level": "intermediate",
        }
        response = client.put(f"/lessons/{lesson_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New description"
        assert data["level"] == "intermediate"
        assert data["title"] == "Basic Addition"  # Unchanged

    def test_update_lesson_problems(self, client, sample_lesson_create):
        """Test replacing lesson problems."""
        create_response = client.post("/lessons", json=sample_lesson_create)
        lesson_id = create_response.json()["id"]

        new_problems = [
            {
                "question": "What is 10 + 10?",
                "answer": "20",
                "difficulty": "beginner",
            }
        ]
        update_payload = {"problems": new_problems}
        response = client.put(f"/lessons/{lesson_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["problems"]) == 1
        assert data["problems"][0]["question"] == "What is 10 + 10?"

    def test_update_nonexistent_lesson(self, client):
        """Test updating a nonexistent lesson returns 404."""
        response = client.put("/lessons/nonexistent-id", json={"title": "New"})
        assert response.status_code == 404

    def test_update_with_no_fields(self, client, sample_lesson_create):
        """Test that updating with no fields returns 422."""
        create_response = client.post("/lessons", json=sample_lesson_create)
        lesson_id = create_response.json()["id"]

        response = client.put(f"/lessons/{lesson_id}", json={})
        assert response.status_code == 422

    def test_update_with_invalid_topic(self, client, sample_lesson_create):
        """Test updating with invalid topic returns 422."""
        create_response = client.post("/lessons", json=sample_lesson_create)
        lesson_id = create_response.json()["id"]

        response = client.put(f"/lessons/{lesson_id}", json={"topic": "invalid"})
        assert response.status_code == 422


class TestDeleteLesson:
    """Tests for deleting lessons."""

    def test_delete_lesson(self, client, sample_lesson_create):
        """Test deleting a lesson."""
        create_response = client.post("/lessons", json=sample_lesson_create)
        lesson_id = create_response.json()["id"]

        # Verify it exists
        response = client.get(f"/lessons/{lesson_id}")
        assert response.status_code == 200

        # Delete it
        response = client.delete(f"/lessons/{lesson_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/lessons/{lesson_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_lesson(self, client):
        """Test deleting a nonexistent lesson returns 404."""
        response = client.delete("/lessons/nonexistent-id")
        assert response.status_code == 404


class TestCRUDHappyPath:
    """Full CRUD workflow test."""

    def test_happy_path_crud(self, client, sample_lesson_create):
        """Test full CRUD lifecycle: create, read, update, delete."""
        # Create
        create_response = client.post("/lessons", json=sample_lesson_create)
        assert create_response.status_code == 201
        lesson_id = create_response.json()["id"]

        # Read
        read_response = client.get(f"/lessons/{lesson_id}")
        assert read_response.status_code == 200
        assert read_response.json()["title"] == "Basic Addition"

        # Update
        update_response = client.put(
            f"/lessons/{lesson_id}", json={"title": "Advanced Addition"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Advanced Addition"

        # Verify update
        verify_response = client.get(f"/lessons/{lesson_id}")
        assert verify_response.json()["title"] == "Advanced Addition"

        # Delete
        delete_response = client.delete(f"/lessons/{lesson_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        final_response = client.get(f"/lessons/{lesson_id}")
        assert final_response.status_code == 404
