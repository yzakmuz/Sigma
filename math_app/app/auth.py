"""
Authentication endpoints: signup, signin, get current user.
"""
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from math_app.core.database import get_session
from math_app.core.models_orm import UserORM
from math_app.core.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from math_app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(request: UserRegisterRequest, session: Session = Depends(get_session)):
    """
    Register a new user account.
    
    - email: Valid email address
    - username: Unique username (3-50 chars)
    - password: Password (min 8 chars)
    
    Returns JWT token for immediate login.
    """
    # Check if email already exists
    existing_email = session.query(UserORM).filter(UserORM.email == request.email).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Check if username already exists
    existing_username = session.query(UserORM).filter(UserORM.username == request.username).first()
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already taken")
    
    # Create new user
    user_id = str(uuid4())
    new_user = UserORM(
        id=user_id,
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        created_at=datetime.now(timezone.utc),
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.id, "username": new_user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username,
    )


@router.post("/signin", response_model=TokenResponse)
async def signin(request: UserLoginRequest, session: Session = Depends(get_session)):
    """
    Login with username/email and password.
    
    Returns JWT token for authenticated requests.
    """
    # Find user by username or email
    user = session.query(UserORM).filter(
        (UserORM.username == request.username) | (UserORM.email == request.username)
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    authorization: str | None = None,
    session: Session = Depends(get_session),
):
    """
    Get current authenticated user profile.
    
    Requires: Authorization header with Bearer token
    """
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
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at.isoformat(),
    )
