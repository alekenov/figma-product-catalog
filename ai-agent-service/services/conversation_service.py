"""Conversation history management with SQLite."""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, delete
from models.conversation import Base, Conversation

logger = logging.getLogger(__name__)


class ConversationService:
    """Manages conversation history in SQLite."""

    MAX_MESSAGES = 20  # Keep last 20 messages per user

    def __init__(self, database_url: str):
        """
        Initialize conversation service.

        Args:
            database_url: SQLAlchemy database URL (e.g. sqlite+aiosqlite:///./data/conversations.db)
        """
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def init_db(self):
        """Create tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database initialized")

    async def get_conversation(self, user_id: str, channel: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for user.

        Args:
            user_id: User identifier
            channel: Channel name

        Returns:
            List of message dicts (role, content)
        """
        async with self.async_session() as session:
            stmt = select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.channel == channel
            )
            result = await session.execute(stmt)
            conv = result.scalar_one_or_none()

            if conv:
                return conv.messages
            return []

    async def save_conversation(self, user_id: str, channel: str, messages: List[Dict[str, Any]]):
        """
        Save conversation history for user.

        Args:
            user_id: User identifier
            channel: Channel name
            messages: List of message dicts
        """
        # Limit history to last MAX_MESSAGES
        if len(messages) > self.MAX_MESSAGES:
            messages = messages[-self.MAX_MESSAGES:]

        async with self.async_session() as session:
            stmt = select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.channel == channel
            )
            result = await session.execute(stmt)
            conv = result.scalar_one_or_none()

            if conv:
                conv.messages = messages
            else:
                conv = Conversation(
                    user_id=user_id,
                    channel=channel,
                    messages=messages
                )
                session.add(conv)

            await session.commit()

    async def clear_conversation(self, user_id: str, channel: Optional[str] = None):
        """
        Clear conversation history for user.

        Args:
            user_id: User identifier
            channel: Optional channel name (if None, clear all channels)
        """
        async with self.async_session() as session:
            if channel:
                stmt = delete(Conversation).where(
                    Conversation.user_id == user_id,
                    Conversation.channel == channel
                )
            else:
                stmt = delete(Conversation).where(
                    Conversation.user_id == user_id
                )

            await session.execute(stmt)
            await session.commit()
            logger.info(f"🗑️  Cleared conversation for user {user_id}")

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()
