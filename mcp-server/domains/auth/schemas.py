"""
Authentication schemas with Pydantic validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Login request payload."""

    phone: str = Field(
        ...,
        description="User phone number (e.g., '77015211545')",
        min_length=11,
        max_length=15,
        examples=["77015211545"]
    )
    password: str = Field(
        ...,
        description="User password",
        min_length=4,
        max_length=100
    )


class UserInfo(BaseModel):
    """User information from JWT token."""

    id: int
    phone: str
    role: str  # "admin", "manager", "florist"
    shop_id: Optional[int] = None


class LoginResponse(BaseModel):
    """Login response with access token."""

    access_token: str
    token_type: str = "bearer"
    user: UserInfo
