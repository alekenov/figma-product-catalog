"""
User models including authentication, clients, and team invitations.

Includes User, Client, and TeamInvitation models with their schemas.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Index
from sqlalchemy import DateTime, func, Column
from pydantic import field_validator

from .enums import UserRole, InvitationStatus
from utils import normalize_phone_number


# ===============================
# Client Models
# ===============================

class ClientBase(SQLModel):
    """Shared client fields"""
    phone: str = Field(
        max_length=20,
        description="Client phone number (normalized format +7XXXXXXXXXX)",
        index=True  # Add explicit index for fast lookups
    )
    customerName: Optional[str] = Field(default=None, max_length=200, description="Client name")
    notes: Optional[str] = Field(default=None, max_length=2000, description="Notes about the client")
    shop_id: int = Field(foreign_key="shop.id", description="Shop that owns this client")

    # Telegram integration fields
    telegram_user_id: Optional[str] = Field(default=None, max_length=50, description="Telegram user ID for bot integration", index=True)
    telegram_username: Optional[str] = Field(default=None, max_length=100, description="Telegram @username")
    telegram_first_name: Optional[str] = Field(default=None, max_length=100, description="Telegram first name")

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v)


class Client(ClientBase, table=True):
    """Client table model for storing client-specific data like notes"""
    __tablename__ = "client"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    shop: Optional["Shop"] = Relationship()

    # Add composite index for common query patterns (phone + shop_id for uniqueness within shop)
    __table_args__ = (
        Index('idx_client_phone_shop', 'phone', 'shop_id', unique=True),
        Index('idx_client_phone_name', 'phone', 'customerName'),
        Index('idx_client_created_at', 'created_at'),
        Index('idx_client_telegram_user_shop', 'telegram_user_id', 'shop_id'),  # For Telegram bot lookups
    )


class ClientCreate(SQLModel):
    """Schema for creating a new client"""
    phone: str = Field(max_length=20, description="Client phone number")
    customerName: str = Field(min_length=1, max_length=200, description="Client name")
    notes: Optional[str] = Field(default="", max_length=2000, description="Notes about the client")


class ClientUpdate(SQLModel):
    """Schema for updating client information"""
    customerName: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Client name")
    phone: Optional[str] = Field(default=None, max_length=20, description="Client phone number")
    notes: Optional[str] = Field(default=None, max_length=2000, description="Notes about the client")


class ClientRead(ClientBase):
    """Schema for reading client information"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===============================
# User Authentication Models
# ===============================

class UserBase(SQLModel):
    """Shared user fields"""
    name: str = Field(max_length=100)
    phone: str = Field(unique=True, max_length=20, description="Phone number in Kazakhstan format")
    role: UserRole = Field(default=UserRole.FLORIST)
    is_active: bool = Field(default=True)
    is_superadmin: bool = Field(default=False, description="Superadmin with access to all shops")
    invited_by: Optional[int] = Field(default=None, foreign_key="user.id")
    shop_id: Optional[int] = Field(default=None, foreign_key="shop.id", description="Shop where user works")

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v)


class User(UserBase, table=True):
    """User table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    inviter: Optional["User"] = Relationship(back_populates="invited_users", sa_relationship_kwargs={"remote_side": "User.id", "foreign_keys": "[User.invited_by]"})
    invited_users: List["User"] = Relationship(back_populates="inviter", sa_relationship_kwargs={"foreign_keys": "[User.invited_by]"})
    invitations_sent: List["TeamInvitation"] = Relationship(back_populates="invited_by_user")
    shop: Optional["Shop"] = Relationship(back_populates="users", sa_relationship_kwargs={"foreign_keys": "[User.shop_id]"})
    owned_shop: Optional["Shop"] = Relationship(back_populates="owner", sa_relationship_kwargs={"foreign_keys": "[Shop.owner_id]"})


class UserCreate(SQLModel):
    """Schema for creating users"""
    name: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    role: UserRole = Field(default=UserRole.FLORIST)
    password: str = Field(min_length=6, description="Plain text password to be hashed")
    invited_by: Optional[int] = None

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v)


class UserUpdate(SQLModel):
    """Schema for updating users"""
    name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6, description="New password to be hashed")

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v) if v else None


class UserRead(UserBase):
    """Schema for reading users"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserResponse(SQLModel):
    """Schema for API responses with uppercase role"""
    id: int
    name: str
    phone: str
    role: str  # Will be uppercase enum name
    is_active: bool
    is_superadmin: bool
    invited_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_user(cls, user):
        """Create UserResponse from User object with uppercase role"""
        return cls(
            id=user.id,
            name=user.name,
            phone=user.phone,
            role=user.role.name,  # Convert to uppercase enum name
            is_active=user.is_active,
            is_superadmin=user.is_superadmin,
            invited_by=user.invited_by,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


# ===============================
# Team Invitation Models
# ===============================

class TeamInvitationBase(SQLModel):
    """Shared team invitation fields"""
    phone: str = Field(max_length=20, description="Phone number to invite")
    name: str = Field(max_length=100, description="Name of person being invited")
    role: UserRole = Field(description="Role to assign to invited user")
    invited_by: int = Field(foreign_key="user.id", description="User ID who sent invitation")
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    invitation_code: str = Field(max_length=6, description="6-digit invitation code")
    expires_at: datetime = Field(description="When invitation expires")

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v)


class TeamInvitation(TeamInvitationBase, table=True):
    """Team invitation table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    invited_by_user: Optional["User"] = Relationship(back_populates="invitations_sent")


class TeamInvitationCreate(SQLModel):
    """Schema for creating team invitations"""
    phone: str = Field(max_length=20)
    name: str = Field(max_length=100)
    role: UserRole

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone number to +7XXXXXXXXXX format"""
        return normalize_phone_number(v)


class TeamInvitationRead(TeamInvitationBase):
    """Schema for reading team invitations"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    invited_by_user: Optional[UserRead] = None


# ===============================
# Authentication Models
# ===============================

class LoginRequest(SQLModel):
    """Schema for login request"""
    phone: str = Field(max_length=20, description="Phone number")
    password: str = Field(description="User password")


class LoginResponse(SQLModel):
    """Schema for login response"""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer")
    user: UserResponse = Field(description="User information")


class TokenData(SQLModel):
    """Schema for JWT token data"""
    user_id: int = Field(description="User ID")
    phone: Optional[str] = Field(default=None, description="User phone")
    role: Optional[str] = Field(default=None, description="User role")
    shop_id: Optional[int] = Field(default=None, description="Shop ID for multi-tenancy filtering")
