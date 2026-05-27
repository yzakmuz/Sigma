# Math Teaching API 🧮

A modern FastAPI backend for progressive mathematics learning. Designed with clean architecture, containerization, and automated testing in mind.

---

## 🚀 Quick Start

The fastest way to get the full stack (Backend + Database) running is with Docker.

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd ex1_math

# 2. Start the services
docker-compose up -d
```

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger)
- **Base URL**: `http://localhost:8000`

---

## ✨ Key Features

- **Auth**: JWT-based registration, login, and profile management.
- **Content**: Full CRUD for math Lessons and Problems.
- **Organization**: Topic-based (Arithmetic, Algebra, Geometry) with Difficulty Levels.
- **Quality**: Pydantic validation, custom error handling, and 10+ test cases.
- **Infrastructure**: MySQL with SQLAlchemy ORM and Alembic migrations.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic, SQLAlchemy.
- **Database**: MySQL 8.0, Alembic (Migrations).
- **Tooling**: `uv` (Fast dependency management), Docker & Docker Compose.
- **Frontend**: Vite, React, TypeScript (Modern frontend boilerplate).

---

## 📂 Project Structure

```text
.
├── backend/           # FastAPI Service
│   ├── alembic/       # DB Migrations
│   ├── math_app/      # Source Code (Core logic & API)
│   └── tests/         # Pytest Suite
├── frontend/          # Vite + React Frontend
├── db/                # Seed Data (sample_db.json)
└── docker-compose.yml # Service Orchestration
```

---

## 🧪 Development & Testing

### Local Setup (Manual)
If you prefer not to use Docker:

```bash
cd backend
python -m venv .venv
# Activate venv...
pip install -e .
python math_app/scripts/init_db.py  # Seed DB
uvicorn math_app.app.main:app --reload
```

### Running Tests
```bash
pytest
```

---

## 📖 Further Reading

For a deep dive into the architecture, full API endpoint references, and troubleshooting guides, please see the [Detailed README](./README_DETAILED.md).

---

**Version**: 0.1.0 | **Author**: Student | **Course**: EASS-HIT
