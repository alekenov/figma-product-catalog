"""
Chat Storage Service - Saves conversation history to PostgreSQL.

Stores complete chat sessions and messages for manager monitoring and analytics.
Works alongside ConversationService (which keeps last 20 messages for AI context).
"""

import logging
import os
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

logger = logging.getLogger(__name__)


class ChatStorageService:
    """Service for saving chat sessions and messages to PostgreSQL."""

    def __init__(self, database_url: str, shop_id: int):
        """
        Initialize chat storage service.

        Args:
            database_url: PostgreSQL connection string
            shop_id: Default shop ID for sessions
        """
        self.shop_id = shop_id

        # Convert psycopg2 URL to asyncpg format
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info(f"💾 Chat storage initialized for shop_id={shop_id}")

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()
        logger.info("🔌 Chat storage connection closed")

    async def create_or_get_session(
        self,
        user_id: str,
        channel: str,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None
    ) -> Optional[int]:
        """
        Create new chat session or get existing active session.

        Args:
            user_id: User identifier (telegram_user_id or phone)
            channel: Channel name (telegram, whatsapp, web)
            customer_name: Customer name if known
            customer_phone: Customer phone if known

        Returns:
            Session ID or None if creation failed
        """
        try:
            async with self.async_session() as session:
                # Check for existing active session (last message within 1 hour)
                one_hour_ago = datetime.utcnow() - timedelta(hours=1)

                query = text("""
                    SELECT id FROM chat_session
                    WHERE shop_id = :shop_id
                      AND user_id = :user_id
                      AND channel = :channel
                      AND last_message_at >= :one_hour_ago
                    ORDER BY last_message_at DESC
                    LIMIT 1
                """)

                result = await session.execute(
                    query,
                    {
                        "shop_id": self.shop_id,
                        "user_id": user_id,
                        "channel": channel,
                        "one_hour_ago": one_hour_ago
                    }
                )
                existing_row = result.fetchone()

                if existing_row:
                    session_id = existing_row[0]
                    logger.info(f"📝 Found existing session {session_id} for user {user_id}")
                    return session_id

                # Create new session
                insert_query = text("""
                    INSERT INTO chat_session (
                        shop_id, user_id, channel, customer_name, customer_phone,
                        message_count, total_cost_usd, created_order
                    ) VALUES (
                        :shop_id, :user_id, :channel, :customer_name, :customer_phone,
                        0, 0.0, 0
                    ) RETURNING id
                """)

                result = await session.execute(
                    insert_query,
                    {
                        "shop_id": self.shop_id,
                        "user_id": user_id,
                        "channel": channel,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone
                    }
                )
                await session.commit()

                new_session_id = result.fetchone()[0]
                logger.info(f"✅ Created new session {new_session_id} for user {user_id} in {channel}")
                return new_session_id

        except Exception as e:
            logger.error(f"❌ Failed to create chat session: {e}")
            return None

    async def save_message(
        self,
        session_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        cost_usd: Decimal = Decimal("0.0")
    ) -> bool:
        """
        Save message to chat session.

        Args:
            session_id: Chat session ID
            role: Message role (user or assistant)
            content: Message text content
            metadata: Optional metadata (tools used, tokens, etc.)
            cost_usd: API cost for this message

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            import json

            async with self.async_session() as session:
                # Convert metadata to JSON string for storage
                metadata_json = json.dumps(metadata) if metadata else None

                insert_query = text("""
                    INSERT INTO chat_message (
                        session_id, role, content, message_metadata, cost_usd
                    ) VALUES (
                        :session_id, :role, :content, :metadata, :cost_usd
                    )
                """)

                await session.execute(
                    insert_query,
                    {
                        "session_id": session_id,
                        "role": role,
                        "content": content,
                        "metadata": metadata_json,
                        "cost_usd": float(cost_usd)
                    }
                )
                await session.commit()

                logger.info(f"💬 Saved {role} message to session {session_id} (cost: ${cost_usd})")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to save message: {e}")
            return False

    async def update_session_stats(
        self,
        session_id: int,
        increment_messages: int = 1,
        add_cost_usd: Decimal = Decimal("0.0"),
        created_order: bool = False,
        order_id: Optional[int] = None
    ) -> bool:
        """
        Update session statistics.

        Args:
            session_id: Chat session ID
            increment_messages: Number of messages to add
            add_cost_usd: Cost to add to total
            created_order: Whether an order was created
            order_id: Order ID if order was created

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            async with self.async_session() as session:
                # Build dynamic UPDATE query based on what's provided
                if order_id is not None:
                    update_query = text("""
                        UPDATE chat_session
                        SET message_count = message_count + :increment,
                            total_cost_usd = total_cost_usd + :cost,
                            created_order = :created_order,
                            order_id = :order_id,
                            last_message_at = CURRENT_TIMESTAMP
                        WHERE id = :session_id
                    """)
                    params = {
                        "session_id": session_id,
                        "increment": increment_messages,
                        "cost": float(add_cost_usd),
                        "created_order": 1 if created_order else 0,
                        "order_id": order_id
                    }
                elif created_order:
                    update_query = text("""
                        UPDATE chat_session
                        SET message_count = message_count + :increment,
                            total_cost_usd = total_cost_usd + :cost,
                            created_order = 1,
                            last_message_at = CURRENT_TIMESTAMP
                        WHERE id = :session_id
                    """)
                    params = {
                        "session_id": session_id,
                        "increment": increment_messages,
                        "cost": float(add_cost_usd)
                    }
                else:
                    update_query = text("""
                        UPDATE chat_session
                        SET message_count = message_count + :increment,
                            total_cost_usd = total_cost_usd + :cost,
                            last_message_at = CURRENT_TIMESTAMP
                        WHERE id = :session_id
                    """)
                    params = {
                        "session_id": session_id,
                        "increment": increment_messages,
                        "cost": float(add_cost_usd)
                    }

                await session.execute(update_query, params)
                await session.commit()

                logger.info(f"📊 Updated session {session_id} stats (+{increment_messages} msgs, +${add_cost_usd} cost)")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to update session stats: {e}")
            return False
