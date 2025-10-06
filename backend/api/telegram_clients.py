"""
Telegram Client API endpoints for bot authorization.
Handles registration and lookup of clients via Telegram contact sharing.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional

from models.users import Client, ClientRead
from database import get_session

router = APIRouter(prefix="/telegram", tags=["Telegram"])


# ===============================
# Request/Response Schemas
# ===============================

from pydantic import BaseModel, Field


class TelegramClientRegister(BaseModel):
    """Schema for registering a Telegram user with their contact info."""
    telegram_user_id: str = Field(description="Telegram user ID")
    phone: str = Field(description="Phone number from Telegram contact")
    customer_name: str = Field(description="Customer name from Telegram")
    shop_id: int = Field(description="Shop ID for multi-tenancy")
    telegram_username: Optional[str] = Field(default=None, description="Telegram @username")
    telegram_first_name: Optional[str] = Field(default=None, description="Telegram first name")


class TelegramClientResponse(BaseModel):
    """Response schema for Telegram client operations."""
    id: int
    phone: str
    customerName: Optional[str]
    telegram_user_id: Optional[str]
    telegram_username: Optional[str]
    telegram_first_name: Optional[str]
    shop_id: int


# ===============================
# Endpoints
# ===============================

@router.get("/client", response_model=Optional[TelegramClientResponse])
async def get_telegram_client(
    telegram_user_id: str = Query(..., description="Telegram user ID"),
    shop_id: int = Query(..., description="Shop ID"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get client by Telegram user ID and shop ID.
    Used to check if user is already authorized in the bot.

    Returns:
        Client data if found, None if not found
    """
    # Query for client with matching telegram_user_id and shop_id
    statement = select(Client).where(
        Client.telegram_user_id == telegram_user_id,
        Client.shop_id == shop_id
    )
    result = await session.execute(statement)
    client = result.scalars().first()

    if not client:
        return None

    return TelegramClientResponse(
        id=client.id,
        phone=client.phone,
        customerName=client.customerName,
        telegram_user_id=client.telegram_user_id,
        telegram_username=client.telegram_username,
        telegram_first_name=client.telegram_first_name,
        shop_id=client.shop_id
    )


@router.post("/client/register", response_model=TelegramClientResponse)
async def register_telegram_client(
    data: TelegramClientRegister,
    session: AsyncSession = Depends(get_session)
):
    """
    Register or update a client with Telegram contact information.

    Logic:
    1. Check if client exists by telegram_user_id + shop_id
    2. If exists, update telegram fields if needed
    3. If not exists, check by phone + shop_id (unique constraint)
    4. If phone exists, link telegram_user_id to existing client
    5. If neither exists, create new client

    Returns:
        Created or updated client data
    """
    # First, check if client with this telegram_user_id already exists
    statement = select(Client).where(
        Client.telegram_user_id == data.telegram_user_id,
        Client.shop_id == data.shop_id
    )
    result = await session.execute(statement)
    existing_telegram_client = result.scalars().first()

    if existing_telegram_client:
        # Update telegram metadata if changed
        updated = False
        if data.telegram_username and existing_telegram_client.telegram_username != data.telegram_username:
            existing_telegram_client.telegram_username = data.telegram_username
            updated = True
        if data.telegram_first_name and existing_telegram_client.telegram_first_name != data.telegram_first_name:
            existing_telegram_client.telegram_first_name = data.telegram_first_name
            updated = True

        if updated:
            session.add(existing_telegram_client)
            await session.commit()
            await session.refresh(existing_telegram_client)

        return TelegramClientResponse(
            id=existing_telegram_client.id,
            phone=existing_telegram_client.phone,
            customerName=existing_telegram_client.customerName,
            telegram_user_id=existing_telegram_client.telegram_user_id,
            telegram_username=existing_telegram_client.telegram_username,
            telegram_first_name=existing_telegram_client.telegram_first_name,
            shop_id=existing_telegram_client.shop_id
        )

    # Check if client exists by phone + shop_id
    statement = select(Client).where(
        Client.phone == data.phone,
        Client.shop_id == data.shop_id
    )
    result = await session.execute(statement)
    existing_phone_client = result.scalars().first()

    if existing_phone_client:
        # Link telegram_user_id to existing client
        existing_phone_client.telegram_user_id = data.telegram_user_id
        existing_phone_client.telegram_username = data.telegram_username
        existing_phone_client.telegram_first_name = data.telegram_first_name

        # Update customerName if provided and different
        if data.customer_name and existing_phone_client.customerName != data.customer_name:
            existing_phone_client.customerName = data.customer_name

        session.add(existing_phone_client)
        await session.commit()
        await session.refresh(existing_phone_client)

        return TelegramClientResponse(
            id=existing_phone_client.id,
            phone=existing_phone_client.phone,
            customerName=existing_phone_client.customerName,
            telegram_user_id=existing_phone_client.telegram_user_id,
            telegram_username=existing_phone_client.telegram_username,
            telegram_first_name=existing_phone_client.telegram_first_name,
            shop_id=existing_phone_client.shop_id
        )

    # Create new client
    new_client = Client(
        phone=data.phone,
        customerName=data.customer_name,
        shop_id=data.shop_id,
        telegram_user_id=data.telegram_user_id,
        telegram_username=data.telegram_username,
        telegram_first_name=data.telegram_first_name,
        notes=""  # Empty notes by default
    )

    session.add(new_client)
    await session.commit()
    await session.refresh(new_client)

    return TelegramClientResponse(
        id=new_client.id,
        phone=new_client.phone,
        customerName=new_client.customerName,
        telegram_user_id=new_client.telegram_user_id,
        telegram_username=new_client.telegram_username,
        telegram_first_name=new_client.telegram_first_name,
        shop_id=new_client.shop_id
    )
