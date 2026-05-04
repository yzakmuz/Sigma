"""
Authentication request/response schemas.
"""
from pydantic import BaseModel, EmailStr, Field

class UserLoginRequest(BaseModel):
    """Request schema for user login (signin)."""
    username: str = Field(..., description="Username or email", strip_whitespace=True)
    password: str = Field(..., description="Password")

class UserRegisterRequest(BaseModel):
    """Request schema for user registration (signup)."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username", strip_whitespace=True)
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class TokenResponse(BaseModel):
    """Response schema for auth token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")


class UserResponse(BaseModel):
    """Response schema for user profile."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    created_at: str = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
