# Math Teaching API 🧮

A modern FastAPI backend for progressive mathematics learning. Designed with clean architecture, containerization, and automated testing in mind.

---

## 🚀 Quick Start

### Option 1: Full Stack with Docker (Recommended)

The fastest way to get everything running — Backend, Database, and Frontend — with a single command:

```bash
# 1. Clone the repo
git clone https://github.com/yzakmuz/Sigma.git
cd Sigma

# 2. Build and start all services
docker compose up --build -d
```

This starts 3 containers:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | [http://localhost:5173](http://localhost:5173) | React app served via Nginx |
| API | [http://localhost:8000](http://localhost:8000) | FastAPI backend |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI |
| Database | `localhost:3306` | MySQL 8.0 |

```bash
# Stop all services
docker compose down

# Stop and delete database data
docker compose down -v

# View logs
docker compose logs -f
```

### Option 2: Docker Backend + Local Frontend

Run the backend and database in Docker, but the frontend locally (useful for frontend development with hot-reload):

```bash
# 1. Start backend + database
cd Sigma
docker compose up --build -d mysql api

# 2. Start frontend locally (in a separate terminal)
cd Sigma/frontend
npm install
npm run dev
```

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

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
- **Frontend**: Vite, React 19, TypeScript, Tailwind CSS 4, served via Nginx in production.

---

## 📂 Project Structure

```text
.
├── backend/              # FastAPI Service
│   ├── alembic/          # DB Migrations
│   ├── math_app/         # Source Code (Core logic & API)
│   ├── tests/            # Pytest Suite
│   └── Dockerfile        # Backend container image
├── frontend/             # Vite + React Frontend
│   ├── src/              # React source code
│   ├── Dockerfile        # Frontend container image (multi-stage: Node build + Nginx)
│   └── nginx.conf        # Nginx config for serving the SPA
├── db/                   # Seed Data (sample_db.json)
└── docker-compose.yml    # Service Orchestration (3 services: MySQL, API, Frontend)
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
