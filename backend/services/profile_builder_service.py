"""
Profile Builder Service for automatic client profile updates.

Automatically calculates and updates client preferences based on order history:
- Budget preferences (avg/min/max order total)
- Frequent recipients (top-3 by delivery count)
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, func

from models import Order, Client, ClientProfile, OrderStatus


class ProfileBuilderService:
    """Service for building and updating client profiles from order data."""

    async def update_client_profile_after_order(
        self,
        session: AsyncSession,
        order: Order
    ) -> Optional[ClientProfile]:
        """
        Update client profile after order is created or delivered.

        Recalculates:
        1. Budget stats (avg/min/max order total)
        2. Frequent recipients (top-3)

        Args:
            session: Database session
            order: Order that was just created/updated

        Returns:
            Updated ClientProfile or None if client not found
        """
        # Get client from order's phone number
        client_query = select(Client).where(
            Client.phone == order.phone,
            Client.shop_id == order.shop_id
        )
        result = await session.execute(client_query)
        client = result.scalar_one_or_none()

        if not client:
            # Client should exist (created during order), but handle edge case
            return None

        # Get or create profile
        profile = await self.get_or_create_profile(session, client.id, order.shop_id)

        # Only count DELIVERED orders for statistics (exclude pending/cancelled)
        if order.status == OrderStatus.DELIVERED:
            # Recalculate budget statistics
            budget_stats = await self._calculate_budget_stats(session, client.id, order.shop_id)
            profile.avg_order_total = budget_stats.get("avg")
            profile.min_order_total = budget_stats.get("min")
            profile.max_order_total = budget_stats.get("max")
            profile.total_orders_count = budget_stats.get("count", 0)

            # Recalculate frequent recipients
            recipients_json = await self._calculate_top_recipients(session, client.id, order.shop_id)
            profile.frequent_recipients = recipients_json

            # Update last order timestamp
            profile.last_order_at = order.created_at or datetime.utcnow()

        # Save profile
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        return profile

    async def get_or_create_profile(
        self,
        session: AsyncSession,
        client_id: int,
        shop_id: int
    ) -> ClientProfile:
        """
        Get existing profile or create new one.

        Args:
            session: Database session
            client_id: Client ID
            shop_id: Shop ID

        Returns:
            ClientProfile instance
        """
        # Try to get existing profile
        query = select(ClientProfile).where(
            ClientProfile.client_id == client_id,
            ClientProfile.shop_id == shop_id
        )
        result = await session.execute(query)
        profile = result.scalar_one_or_none()

        if profile:
            return profile

        # Create new profile
        try:
            new_profile = ClientProfile(
                client_id=client_id,
                shop_id=shop_id,
                allow_personalization=True  # Default: enabled
            )
            session.add(new_profile)
            await session.commit()
            await session.refresh(new_profile)
            return new_profile

        except IntegrityError:
            # Handle race condition: another process created profile
            await session.rollback()
            result = await session.execute(query)
            profile = result.scalar_one_or_none()
            if profile:
                return profile
            else:
                raise RuntimeError(f"Failed to create profile for client {client_id}")

    async def _calculate_budget_stats(
        self,
        session: AsyncSession,
        client_id: int,
        shop_id: int
    ) -> Dict[str, Optional[int]]:
        """
        Calculate budget statistics from delivered orders.

        Args:
            session: Database session
            client_id: Client ID
            shop_id: Shop ID

        Returns:
            Dict with avg, min, max, count
        """
        # Get client phone
        client_query = select(Client).where(Client.id == client_id)
        result = await session.execute(client_query)
        client = result.scalar_one_or_none()

        if not client:
            return {"avg": None, "min": None, "max": None, "count": 0}

        # Calculate stats from DELIVERED orders only
        stats_query = select(
            func.avg(Order.total).label("avg"),
            func.min(Order.total).label("min"),
            func.max(Order.total).label("max"),
            func.count(Order.id).label("count")
        ).where(
            Order.phone == client.phone,
            Order.shop_id == shop_id,
            Order.status == OrderStatus.DELIVERED
        )

        result = await session.execute(stats_query)
        row = result.one()

        return {
            "avg": int(row.avg) if row.avg is not None else None,
            "min": int(row.min) if row.min is not None else None,
            "max": int(row.max) if row.max is not None else None,
            "count": int(row.count) if row.count is not None else 0
        }

    async def _calculate_top_recipients(
        self,
        session: AsyncSession,
        client_id: int,
        shop_id: int,
        limit: int = 3
    ) -> Optional[str]:
        """
        Calculate top recipients by delivery count.

        Returns JSON string with top-3 recipients:
        [
            {"name": "Maria", "phone": "+7...", "address": "...", "count": 8},
            {"name": "Anna", "phone": "+7...", "address": "...", "count": 3}
        ]

        Args:
            session: Database session
            client_id: Client ID
            shop_id: Shop ID
            limit: Max recipients to return (default 3)

        Returns:
            JSON string or None if no recipients
        """
        # Get client phone
        client_query = select(Client).where(Client.id == client_id)
        result = await session.execute(client_query)
        client = result.scalar_one_or_none()

        if not client:
            return None

        # Get top recipients from DELIVERED orders with recipient data
        recipients_query = select(
            Order.recipient_name,
            Order.recipient_phone,
            Order.delivery_address,
            func.count(Order.id).label("count")
        ).where(
            Order.phone == client.phone,
            Order.shop_id == shop_id,
            Order.status == OrderStatus.DELIVERED,
            Order.recipient_name.isnot(None),
            Order.recipient_name != ""
        ).group_by(
            Order.recipient_name,
            Order.recipient_phone,
            Order.delivery_address
        ).order_by(
            func.count(Order.id).desc()
        ).limit(limit)

        result = await session.execute(recipients_query)
        rows = result.all()

        if not rows:
            return None

        # Build JSON array
        recipients = []
        for row in rows:
            recipients.append({
                "name": row.recipient_name,
                "phone": row.recipient_phone,
                "address": row.delivery_address,
                "count": row.count
            })

        return json.dumps(recipients, ensure_ascii=False)

    async def update_profile_privacy(
        self,
        session: AsyncSession,
        client_id: int,
        shop_id: int,
        action: str
    ) -> Dict[str, Any]:
        """
        Update profile privacy settings.

        Actions:
        - "disable_personalization": Set allow_personalization=False
        - "enable_personalization": Set allow_personalization=True
        - "delete_profile_data": Clear all profile data (budget, recipients)

        Args:
            session: Database session
            client_id: Client ID
            shop_id: Shop ID
            action: Privacy action to perform

        Returns:
            Dict with status message
        """
        profile = await self.get_or_create_profile(session, client_id, shop_id)

        if action == "disable_personalization":
            profile.allow_personalization = False
            message = "Персонализация отключена"

        elif action == "enable_personalization":
            profile.allow_personalization = True
            message = "Персонализация включена"

        elif action == "delete_profile_data":
            # Clear all profile data but keep the record
            profile.avg_order_total = None
            profile.min_order_total = None
            profile.max_order_total = None
            profile.total_orders_count = 0
            profile.frequent_recipients = None
            profile.allow_personalization = False
            message = "Данные профиля удалены"

        else:
            return {"success": False, "message": f"Unknown action: {action}"}

        session.add(profile)
        await session.commit()

        return {"success": True, "message": message}


# Global service instance
profile_builder_service = ProfileBuilderService()
