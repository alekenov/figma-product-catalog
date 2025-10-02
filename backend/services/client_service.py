"""
Client Service Module

Provides centralized client management functionality including:
- Auto-creation of Client records when new phone numbers appear in orders
- Caching for frequently accessed client data
- Atomic client lookup and creation to prevent duplicates
- Phone number normalization before storage
"""

import re
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, func
from models import Client, ClientCreate


class ClientCache:
    """Simple in-memory cache for client data"""

    def __init__(self, cache_duration_minutes: int = 30):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)

    def get(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get client data from cache if not expired"""
        if phone not in self._cache:
            return None

        # Check if cache entry is expired
        if datetime.now() - self._cache_timestamps[phone] > self.cache_duration:
            self.invalidate(phone)
            return None

        return self._cache[phone]

    def set(self, phone: str, client_data: Dict[str, Any]) -> None:
        """Store client data in cache"""
        self._cache[phone] = client_data
        self._cache_timestamps[phone] = datetime.now()

    def invalidate(self, phone: str) -> None:
        """Remove client data from cache"""
        self._cache.pop(phone, None)
        self._cache_timestamps.pop(phone, None)

    def clear(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()


class ClientService:
    """Service for centralized client management"""

    def __init__(self):
        self._cache = ClientCache()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalize phone number for consistent storage

        Args:
            phone: Raw phone number input

        Returns:
            Normalized phone number
        """
        if not phone:
            return phone

        # Remove all non-digit characters
        digits_only = re.sub(r'[^\d]', '', phone)

        # Handle Kazakhstan phone numbers
        if digits_only.startswith('8') and len(digits_only) == 11:
            # Convert 8XXXXXXXXXX to +7XXXXXXXXXX
            digits_only = '7' + digits_only[1:]
        elif digits_only.startswith('7') and len(digits_only) == 11:
            # Already in correct format
            pass
        elif len(digits_only) == 10:
            # Add country code for 10-digit numbers
            digits_only = '7' + digits_only

        # Add + prefix for international format
        if not digits_only.startswith('+'):
            digits_only = '+' + digits_only

        return digits_only

    async def get_or_create_client(
        self,
        session: AsyncSession,
        phone: str,
        shop_id: int,
        customer_name: Optional[str] = None,
        notes: Optional[str] = None,
        use_cache: bool = True
    ) -> Tuple[Client, bool]:
        """
        Get existing client or create new one atomically

        Args:
            session: Database session
            phone: Client phone number (will be normalized)
            shop_id: Shop ID for multi-tenancy (clients are unique per shop)
            customer_name: Optional customer name for new clients
            notes: Optional notes for new clients
            use_cache: Whether to use cache for lookups

        Returns:
            Tuple of (Client instance, was_created boolean)
        """
        normalized_phone = self.normalize_phone(phone)
        cache_key = f"{shop_id}:{normalized_phone}"

        # Try cache first if enabled
        if use_cache:
            cached_client = self._cache.get(cache_key)
            if cached_client:
                # Convert cached data back to Client instance
                client = Client(**cached_client)
                return client, False

        # Try to get existing client for this shop
        existing_client = await self._get_client_by_phone(session, normalized_phone, shop_id)
        if existing_client:
            # Update cache
            if use_cache:
                self._cache.set(cache_key, {
                    "id": existing_client.id,
                    "shop_id": existing_client.shop_id,
                    "phone": existing_client.phone,
                    "customerName": existing_client.customerName,
                    "notes": existing_client.notes,
                    "created_at": existing_client.created_at,
                    "updated_at": existing_client.updated_at
                })
            return existing_client, False

        # Create new client for this shop
        try:
            new_client = await self._create_client(
                session,
                normalized_phone,
                shop_id,
                customer_name or f"Клиент {normalized_phone}",
                notes or ""
            )

            # Update cache
            if use_cache:
                self._cache.set(cache_key, {
                    "id": new_client.id,
                    "shop_id": new_client.shop_id,
                    "phone": new_client.phone,
                    "customerName": new_client.customerName,
                    "notes": new_client.notes,
                    "created_at": new_client.created_at,
                    "updated_at": new_client.updated_at
                })

            return new_client, True

        except IntegrityError:
            # Handle race condition where another process created the client
            await session.rollback()
            existing_client = await self._get_client_by_phone(session, normalized_phone, shop_id)
            if existing_client:
                return existing_client, False
            else:
                # This should not happen, but just in case
                raise RuntimeError(f"Failed to create or retrieve client for phone {normalized_phone} in shop {shop_id}")

    async def get_client_by_phone(
        self,
        session: AsyncSession,
        phone: str,
        use_cache: bool = True
    ) -> Optional[Client]:
        """
        Get client by phone number

        Args:
            session: Database session
            phone: Client phone number (will be normalized)
            use_cache: Whether to use cache for lookups

        Returns:
            Client instance or None if not found
        """
        normalized_phone = self.normalize_phone(phone)

        # Try cache first if enabled
        if use_cache:
            cached_client = self._cache.get(normalized_phone)
            if cached_client:
                return Client(**cached_client)

        # Get from database
        client = await self._get_client_by_phone(session, normalized_phone)

        # Update cache
        if client and use_cache:
            self._cache.set(normalized_phone, {
                "id": client.id,
                "phone": client.phone,
                "customerName": client.customerName,
                "notes": client.notes,
                "created_at": client.created_at,
                "updated_at": client.updated_at
            })

        return client

    async def update_client_name(
        self,
        session: AsyncSession,
        phone: str,
        customer_name: str
    ) -> Optional[Client]:
        """
        Update client name if phone exists and name is currently empty

        Args:
            session: Database session
            phone: Client phone number
            customer_name: New customer name

        Returns:
            Updated client or None if not found
        """
        normalized_phone = self.normalize_phone(phone)
        client = await self._get_client_by_phone(session, normalized_phone)

        if client and not client.customerName:
            client.customerName = customer_name
            client.updated_at = datetime.now()
            await session.commit()
            await session.refresh(client)

            # Invalidate cache
            self._cache.invalidate(normalized_phone)

            return client

        return client

    async def invalidate_cache(self, phone: str) -> None:
        """Invalidate cache for specific phone number"""
        normalized_phone = self.normalize_phone(phone)
        self._cache.invalidate(normalized_phone)

    async def clear_cache(self) -> None:
        """Clear all cached client data"""
        self._cache.clear()

    async def batch_sync_clients_from_orders(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Sync all clients from orders table - creates Client records for missing phone numbers

        Args:
            session: Database session

        Returns:
            Dictionary with sync results
        """
        # Get all unique phones from orders that don't have client records
        from models import Order  # Import here to avoid circular imports

        missing_clients_query = (
            select(Order.phone, func.max(Order.customerName).label("customerName"))
            .distinct(Order.phone)
            .outerjoin(Client, Client.phone == Order.phone)
            .where(Client.id == None)
            .group_by(Order.phone)
        )

        result = await session.execute(missing_clients_query)
        missing_data = result.all()

        if not missing_data:
            return {
                "message": "All clients are already synchronized",
                "created_count": 0,
                "phones": []
            }

        # Batch create all missing client records
        created_clients = []
        for row in missing_data:
            phone = row.phone
            customer_name = row.customerName

            normalized_phone = self.normalize_phone(phone)
            new_client = Client(
                phone=normalized_phone,
                customerName=customer_name or f"Клиент {normalized_phone}",
                notes=""
            )
            created_clients.append(new_client)

        try:
            session.add_all(created_clients)
            await session.commit()

            # Clear cache since we have new data
            self._cache.clear()

            return {
                "message": f"Created {len(created_clients)} new client records",
                "created_count": len(created_clients),
                "phones": [client.phone for client in created_clients]
            }

        except IntegrityError as e:
            await session.rollback()
            # Handle potential duplicates that might have been created during batch operation
            return {
                "message": f"Partial sync completed with conflicts",
                "created_count": 0,
                "error": str(e)
            }

    async def _get_client_by_phone(
        self,
        session: AsyncSession,
        phone: str,
        shop_id: Optional[int] = None
    ) -> Optional[Client]:
        """Internal method to get client by phone from database"""
        query = select(Client).where(Client.phone == phone)

        # Filter by shop_id for multi-tenancy
        if shop_id is not None:
            query = query.where(Client.shop_id == shop_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _create_client(
        self,
        session: AsyncSession,
        phone: str,
        shop_id: int,
        customer_name: str,
        notes: str
    ) -> Client:
        """Internal method to create new client"""
        new_client = Client(
            shop_id=shop_id,
            phone=phone,
            customerName=customer_name,
            notes=notes
        )

        session.add(new_client)
        await session.commit()
        await session.refresh(new_client)

        return new_client


# Global service instance
client_service = ClientService()