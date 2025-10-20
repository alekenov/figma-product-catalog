"""Shared enumerations for order statuses, product types, etc."""

from enum import Enum


class OrderStatus(str, Enum):
    """Order status values from Production API."""
    NEW = "new"
    PAID = "paid"
    ACCEPTED = "accepted"
    ASSEMBLED = "assembled"
    IN_TRANSIT = "in-transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @classmethod
    def get_valid_transitions(cls, current_status: str) -> list[str]:
        """
        Get valid status transitions for order state machine.

        Args:
            current_status: Current order status

        Returns:
            List of valid next statuses

        Example:
            OrderStatus.get_valid_transitions("assembled")
            # Returns: ["in-transit", "cancelled"]
        """
        transitions = {
            cls.NEW.value: [cls.PAID.value, cls.CANCELLED.value],
            cls.PAID.value: [cls.ACCEPTED.value, cls.CANCELLED.value],
            cls.ACCEPTED.value: [cls.ASSEMBLED.value, cls.CANCELLED.value],
            cls.ASSEMBLED.value: [cls.IN_TRANSIT.value, cls.CANCELLED.value],
            cls.IN_TRANSIT.value: [cls.DELIVERED.value, cls.CANCELLED.value],
            cls.DELIVERED.value: [],  # Terminal state
            cls.CANCELLED.value: [],  # Terminal state
        }
        return transitions.get(current_status, [])


class ProductType(str, Enum):
    """Product type values."""
    VITRINA = "vitrina"  # Ready-made bouquets (displayed in shop window)
    CATALOG = "catalog"  # Catalog items (made to order)


class DeliveryType(str, Enum):
    """Delivery type values."""
    DELIVERY = "delivery"  # Home/office delivery
    PICKUP = "pickup"      # Customer picks up from shop


class UserRole(str, Enum):
    """User role values."""
    DIRECTOR = "director"
    SELLER = "seller"
    COURIER = "courier"
    FLORIST = "florist"


class City(str, Enum):
    """Kazakhstan cities with IDs."""
    ASTANA = "2"
    ALMATY = "1"
    SHYMKENT = "3"
    KARAGANDA = "4"
    AKTOBE = "5"

    @classmethod
    def get_name(cls, city_id: str) -> str:
        """Get city name by ID."""
        names = {
            "1": "Алматы",
            "2": "Астана",
            "3": "Шымкент",
            "4": "Караганда",
            "5": "Актобе",
        }
        return names.get(city_id, "Unknown")


class PaymentStatus(str, Enum):
    """Payment status values."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
