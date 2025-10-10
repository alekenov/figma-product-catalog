"""
Chats Router - Admin endpoints for monitoring AI agent conversations.

Provides endpoints for viewing chat sessions and messages across all channels.
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, desc
from sqlalchemy.orm import selectinload
from decimal import Decimal

from database import get_session
from models import (
    ChatSession,
    ChatSessionRead,
    ChatMessage,
    ChatMessageRead,
    ChatSessionWithMessages,
    ChatStatsRead,
    User
)
from auth_utils import get_current_user, get_current_user_shop_id

router = APIRouter()


@router.get("/admin", response_model=List[ChatSessionRead])
async def get_chat_sessions(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of sessions to return"),
    channel: Optional[str] = Query(None, description="Filter by channel (telegram/whatsapp/web)"),
    date_from: Optional[date] = Query(None, description="Filter sessions started from this date"),
    date_to: Optional[date] = Query(None, description="Filter sessions started until this date"),
    has_order: Optional[bool] = Query(None, description="Filter by whether order was created"),
    search: Optional[str] = Query(None, description="Search by customer name or phone"),
):
    """
    Get list of chat sessions with filtering.

    Only accessible to authenticated users. Returns sessions for current shop only.
    """

    # Build query
    query = select(ChatSession)

    # CRITICAL: Filter by shop_id for multi-tenancy
    query = query.where(ChatSession.shop_id == shop_id)

    # Apply filters
    if channel:
        query = query.where(ChatSession.channel == channel)

    if date_from:
        query = query.where(func.date(ChatSession.started_at) >= date_from)

    if date_to:
        query = query.where(func.date(ChatSession.started_at) <= date_to)

    if has_order is not None:
        query = query.where(ChatSession.created_order == has_order)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (ChatSession.customer_name.ilike(search_pattern)) |
            (ChatSession.customer_phone.ilike(search_pattern))
        )

    # Order by most recent first
    query = query.order_by(desc(ChatSession.last_message_at))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    sessions = result.scalars().all()

    # Round total_cost_usd to 6 decimal places for each session
    return [
        ChatSessionRead(
            id=s.id,
            shop_id=s.shop_id,
            user_id=s.user_id,
            channel=s.channel,
            customer_name=s.customer_name,
            customer_phone=s.customer_phone,
            message_count=s.message_count,
            total_cost_usd=round(s.total_cost_usd, 6),
            created_order=s.created_order,
            order_id=s.order_id,
            started_at=s.started_at,
            last_message_at=s.last_message_at
        )
        for s in sessions
    ]


@router.get("/admin/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session_detail(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
    session_id: int,
):
    """
    Get detailed chat session with all messages.

    Only accessible to authenticated users. Verifies session belongs to current shop.
    """

    # Get session with messages
    query = select(ChatSession).options(
        selectinload(ChatSession.messages)
    ).where(ChatSession.id == session_id)

    result = await session.execute(query)
    chat_session = result.scalar_one_or_none()

    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Verify session belongs to shop
    if chat_session.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Chat session does not belong to your shop")

    # Build response with messages (round decimals to 6 places)
    return ChatSessionWithMessages(
        id=chat_session.id,
        shop_id=chat_session.shop_id,
        user_id=chat_session.user_id,
        channel=chat_session.channel,
        customer_name=chat_session.customer_name,
        customer_phone=chat_session.customer_phone,
        message_count=chat_session.message_count,
        total_cost_usd=round(chat_session.total_cost_usd, 6),
        created_order=chat_session.created_order,
        order_id=chat_session.order_id,
        started_at=chat_session.started_at,
        last_message_at=chat_session.last_message_at,
        messages=[
            ChatMessageRead(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                metadata=msg.metadata,
                cost_usd=round(msg.cost_usd, 6),
                created_at=msg.created_at
            )
            for msg in sorted(chat_session.messages, key=lambda m: m.created_at)
        ]
    )


@router.get("/stats", response_model=ChatStatsRead)
async def get_chat_stats(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    shop_id: int = Depends(get_current_user_shop_id),
):
    """
    Get chat statistics for current shop.

    Returns:
    - Total chats started today
    - Total messages today
    - Conversion rate (chats with orders / total chats)
    - Average cost per chat
    - Average messages per chat
    """

    today = date.today()

    # Total chats started today
    chats_today_query = select(func.count(ChatSession.id)).where(
        and_(
            ChatSession.shop_id == shop_id,
            func.date(ChatSession.started_at) == today
        )
    )
    chats_today_result = await session.execute(chats_today_query)
    total_chats_today = chats_today_result.scalar() or 0

    # Total messages today
    messages_today_query = select(func.count(ChatMessage.id)).join(
        ChatSession
    ).where(
        and_(
            ChatSession.shop_id == shop_id,
            func.date(ChatMessage.created_at) == today
        )
    )
    messages_today_result = await session.execute(messages_today_query)
    total_messages_today = messages_today_result.scalar() or 0

    # Conversion rate (all time for this shop)
    total_sessions_query = select(func.count(ChatSession.id)).where(
        ChatSession.shop_id == shop_id
    )
    total_sessions_result = await session.execute(total_sessions_query)
    total_sessions = total_sessions_result.scalar() or 0

    sessions_with_orders_query = select(func.count(ChatSession.id)).where(
        and_(
            ChatSession.shop_id == shop_id,
            ChatSession.created_order == True
        )
    )
    sessions_with_orders_result = await session.execute(sessions_with_orders_query)
    sessions_with_orders = sessions_with_orders_result.scalar() or 0

    conversion_rate = (sessions_with_orders / total_sessions * 100) if total_sessions > 0 else 0.0

    # Average cost per chat (all time)
    avg_cost_query = select(func.avg(ChatSession.total_cost_usd)).where(
        ChatSession.shop_id == shop_id
    )
    avg_cost_result = await session.execute(avg_cost_query)
    avg_cost_raw = avg_cost_result.scalar() or Decimal("0.0")
    # Round to 6 decimal places to match Pydantic validation
    avg_cost_usd = round(avg_cost_raw, 6)

    # Average messages per chat (all time)
    avg_messages_query = select(func.avg(ChatSession.message_count)).where(
        ChatSession.shop_id == shop_id
    )
    avg_messages_result = await session.execute(avg_messages_query)
    avg_messages_per_chat = avg_messages_result.scalar() or 0.0

    return ChatStatsRead(
        total_chats_today=total_chats_today,
        total_messages_today=total_messages_today,
        conversion_rate=round(conversion_rate, 2),
        avg_cost_usd=avg_cost_usd,
        avg_messages_per_chat=round(avg_messages_per_chat, 1)
    )
