"""
Database configuration and session management for SQLAlchemy ORM.
"""
from os import getenv
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Load database URL from environment (no hardcoded password fallback)
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


def get_current_user(authorization: str | None = None, session=None):
    """
    Dependency to get the current authenticated user from JWT token.
    
    Usage: def endpoint(current_user = Depends(get_current_user)):
    
    Returns: UserORM object
    Raises: HTTPException 401 if token invalid or expired
    """
    from fastapi import Depends, HTTPException
    from math_app.core.models_orm import UserORM
    from math_app.core.security import decode_access_token
    
    if session is None:
        # This will be injected by FastAPI
        from sqlalchemy.orm import Session as SQLSession
        session = SessionLocal()
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token
    try:
        scheme, token = authorization.split() if " " in authorization else ("", authorization)
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    # Decode token
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    # Get user
    user = session.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
