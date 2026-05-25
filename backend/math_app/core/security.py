"""
Security utilities for JWT tokens and password hashing.
"""
from datetime import datetime, timedelta, timezone
from os import getenv

import jwt
from bcrypt import checkpw, hashpw, gensalt

# JWT Configuration
SECRET_KEY = getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-min-32-chars-long")
ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
EXPIRATION_HOURS = int(getenv("JWT_EXPIRATION_HOURS", "20"))


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = gensalt()
    hashed = hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims (e.g., {"sub": user_id})
        expires_delta: Custom expiration time (default: JWT_EXPIRATION_HOURS)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}") from e


async def get_current_user_from_token(authorization: str | None = None) -> dict:
    """
    Extract and validate user from Authorization header.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
    
    Returns:
        Decoded token payload with user info
    
    Raises:
        HTTPException: If token is missing or invalid
    """
    from fastapi import HTTPException
    
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
        return payload
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
