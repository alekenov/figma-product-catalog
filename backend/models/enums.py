"""
Enum definitions for the application.

All enum types used across models.
"""
from enum import Enum


class ProductType(str, Enum):
    """Product type categories"""
    FLOWERS = "flowers"
    SWEETS = "sweets"
    FRUITS = "fruits"
    GIFTS = "gifts"
    VITRINA = "vitrina"  # Ready-made bouquets (production Bitrix API)
    CATALOG = "catalog"  # Catalog products (production Bitrix API)


class OrderStatus(str, Enum):
    """Order status workflow"""
    NEW = "new"
    PAID = "paid"
    ACCEPTED = "accepted"
    ASSEMBLED = "assembled"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    """User roles for authorization"""
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    DIRECTOR = "DIRECTOR"
    MANAGER = "MANAGER"
    FLORIST = "FLORIST"
    COURIER = "COURIER"


class WarehouseOperationType(str, Enum):
    """Types of warehouse operations"""
    DELIVERY = "delivery"
    SALE = "sale"
    WRITEOFF = "writeoff"
    PRICE_CHANGE = "price_change"
    INVENTORY = "inventory"


class City(str, Enum):
    """Cities where shops operate"""
    ALMATY = "Almaty"
    ASTANA = "Astana"


class InvitationStatus(str, Enum):
    """Status of team invitations"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
