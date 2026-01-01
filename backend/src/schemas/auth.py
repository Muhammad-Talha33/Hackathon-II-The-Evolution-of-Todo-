"""Authentication request/response schemas."""
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class SignupRequest(BaseModel):
    """Request schema for user signup."""

    email: EmailStr
    password: str = Field(min_length=8, description="Password (minimum 8 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepass123",
            }
        }


class SigninRequest(BaseModel):
    """Request schema for user signin."""

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepass123",
            }
        }


class RefreshRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
