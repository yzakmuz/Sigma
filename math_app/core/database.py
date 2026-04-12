"""
Database configuration and session management for SQLAlchemy ORM.
"""
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load database URL from environment
DATABASE_URL = getenv(
    "DATABASE_URL", "mysql+pymysql://root:rootpassword@localhost:3306/math_app"
)
DATABASE_ECHO = getenv("DATABASE_ECHO", "false").lower() == "true"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    pool_pre_ping=True,  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_session():
    """
    Dependency injection for FastAPI to provide database sessions.
    Usage: def endpoint(session: Session = Depends(get_session)):
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
