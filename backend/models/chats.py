"""
Chat session and message models for AI agent conversation tracking.

Stores complete conversation history for manager monitoring and analytics.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import DateTime, func, JSON


class ChatSessionBase(SQLModel):
    """Base model for chat session."""
    shop_id: int = Field(foreign_key="shop.id", index=True)
    user_id: str = Field(max_length=255, index=True, description="Telegram user ID or phone number")
    channel: str = Field(max_length=50, description="telegram, whatsapp, web")
    customer_name: Optional[str] = Field(default=None, max_length=255)
    customer_phone: Optional[str] = Field(default=None, max_length=50)
    message_count: int = Field(default=0, description="Total messages in session")
    total_cost_usd: Decimal = Field(default=0.0, decimal_places=6, description="Total API cost")
    created_order: bool = Field(default=False, description="Whether order was created")
    order_id: Optional[int] = Field(default=None, foreign_key="order.id", description="Created order ID")


class ChatSession(ChatSessionBase, table=True):
    """Chat session table - represents one conversation with a customer."""

    __tablename__ = "chat_session"

    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )
    last_message_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    messages: list["ChatMessage"] = Relationship(back_populates="session")


class ChatSessionRead(ChatSessionBase):
    """Chat session response model."""
    id: int
    started_at: datetime
    last_message_at: datetime


class ChatSessionCreate(ChatSessionBase):
    """Chat session creation model."""
    pass


class ChatMessageBase(SQLModel):
    """Base model for chat message."""
    session_id: int = Field(foreign_key="chat_session.id", index=True)
    role: str = Field(max_length=20, description="user or assistant")
    content: str = Field(description="Message text content")
    cost_usd: Decimal = Field(default=0.0, decimal_places=6, description="API cost for this message")


class ChatMessage(ChatMessageBase, table=True):
    """Chat message table - stores individual messages in a session."""

    __tablename__ = "chat_message"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="Tools used, tokens, etc")
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )

    # Relationships
    session: Optional["ChatSession"] = Relationship(back_populates="messages")


class ChatMessageRead(ChatMessageBase):
    """Chat message response model."""
    id: int
    message_metadata: Optional[dict] = None
    created_at: datetime


class ChatMessageCreate(ChatMessageBase):
    """Chat message creation model."""
    pass


class ChatSessionWithMessages(ChatSessionRead):
    """Chat session with all messages."""
    messages: list[ChatMessageRead] = []


# Response schemas for admin endpoints
class ChatStatsRead(SQLModel):
    """Chat statistics response."""
    total_chats_today: int = Field(description="Total chats started today")
    total_messages_today: int = Field(description="Total messages today")
    conversion_rate: float = Field(description="Percentage of chats that created orders")
    avg_cost_usd: Decimal = Field(decimal_places=6, description="Average cost per chat")
    avg_messages_per_chat: float = Field(description="Average messages per chat")
