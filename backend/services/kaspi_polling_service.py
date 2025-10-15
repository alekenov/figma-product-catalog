"""
Kaspi Pay Polling Service - Automated payment status checker

This service polls Kaspi Pay API for payment status updates and automatically
updates order statuses when payments are confirmed. Matches the implementation
pattern used by onelab.kaspipay module on production.

Polling Strategy:
- Runs every 2-3 minutes via APScheduler
- Checks orders with kaspi_payment_status IN ('Wait', 'QrTokenCreated', 'RemotePaymentCreated', 'Error')
- Filters payments created between 2 and 600 minutes ago (to avoid spamming API)
- Processes up to 200 orders per run (rate limiting)
- Updates order status to 'PAID' when payment is 'Processed'
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from services.kaspi_pay_service import get_kaspi_service, KaspiPayServiceError
from models.orders import Order
from database import get_session

# Import settings based on environment
if os.getenv("DATABASE_URL"):
    from config_render import settings
else:
    from config_sqlite import settings

logger = get_logger(__name__)


class KaspiPollingService:
    """Service for polling Kaspi Pay payment status"""

    # Polling configuration (matching onelab implementation)
    MIN_AGE_MINUTES = 2      # Minimum payment age before first check
    MAX_AGE_MINUTES = 600    # Maximum payment age (10 hours, then stop checking)
    MAX_ORDERS_PER_RUN = 200  # Rate limit to avoid API overload

    @staticmethod
    async def get_pending_payments(session: AsyncSession) -> List[Order]:
        """
        Query orders with pending Kaspi payments

        Returns orders where:
        - payment_method = 'kaspi'
        - kaspi_payment_id is not null
        - kaspi_payment_status IN ('Wait', 'QrTokenCreated', 'RemotePaymentCreated', 'Error')
        - kaspi_payment_created_at between 2 and 600 minutes ago
        - Limit to 200 orders per run

        Args:
            session: Database session

        Returns:
            List of Order objects with pending payments
        """
        now = datetime.now()
        min_created_at = now - timedelta(minutes=KaspiPollingService.MAX_AGE_MINUTES)
        max_created_at = now - timedelta(minutes=KaspiPollingService.MIN_AGE_MINUTES)

        query = (
            select(Order)
            .where(
                Order.payment_method == "kaspi",
                Order.kaspi_payment_id.isnot(None),
                Order.kaspi_payment_status.in_(["Wait", "QrTokenCreated", "RemotePaymentCreated", "Error"]),
                Order.kaspi_payment_created_at >= min_created_at,
                Order.kaspi_payment_created_at <= max_created_at
            )
            .order_by(Order.kaspi_payment_created_at.asc())
            .limit(KaspiPollingService.MAX_ORDERS_PER_RUN)
        )

        result = await session.execute(query)
        orders = result.scalars().all()

        logger.info(
            "kaspi_polling_query",
            found_orders=len(orders),
            min_age_minutes=KaspiPollingService.MIN_AGE_MINUTES,
            max_age_minutes=KaspiPollingService.MAX_AGE_MINUTES,
            max_orders=KaspiPollingService.MAX_ORDERS_PER_RUN
        )

        return list(orders)

    @staticmethod
    async def check_and_update_payment_status(
        session: AsyncSession,
        order: Order
    ) -> Optional[str]:
        """
        Check payment status via Kaspi API and update order

        Args:
            session: Database session
            order: Order to check

        Returns:
            New payment status if changed, None if unchanged or error

        Side effects:
            - Updates order.kaspi_payment_status
            - Updates order.kaspi_payment_completed_at (if Processed)
            - Updates order.status to 'confirmed' (if Processed)
            - Commits changes to database
        """
        kaspi_service = get_kaspi_service()

        try:
            # Call Kaspi API to check status
            response = await kaspi_service.check_status(order.kaspi_payment_id)

            # Extract new status from response
            new_status = response.get("data", {}).get("status")
            old_status = order.kaspi_payment_status

            if not new_status:
                logger.warning(
                    "kaspi_polling_no_status",
                    order_id=order.id,
                    order_number=order.orderNumber,
                    external_id=order.kaspi_payment_id
                )
                return None

            # Status unchanged - skip update
            if new_status == old_status:
                logger.debug(
                    "kaspi_polling_unchanged",
                    order_id=order.id,
                    order_number=order.orderNumber,
                    status=new_status
                )
                return None

            # Status changed - update order
            logger.info(
                "kaspi_polling_status_changed",
                order_id=order.id,
                order_number=order.orderNumber,
                old_status=old_status,
                new_status=new_status,
                external_id=order.kaspi_payment_id
            )

            # Update payment status
            order.kaspi_payment_status = new_status

            # If payment is successful, mark order as paid
            if new_status == "Processed":
                order.kaspi_payment_completed_at = datetime.now()

                # Update order status to PAID (equivalent to onelab's 'PD' status)
                from models.enums import OrderStatus
                if order.status != OrderStatus.PAID:
                    old_order_status = order.status
                    order.status = OrderStatus.PAID

                    logger.info(
                        "kaspi_polling_order_paid",
                        order_id=order.id,
                        order_number=order.orderNumber,
                        old_order_status=old_order_status.value if hasattr(old_order_status, 'value') else old_order_status,
                        new_order_status=OrderStatus.PAID.value
                    )

            # Commit changes
            await session.commit()

            return new_status

        except KaspiPayServiceError as e:
            logger.error(
                "kaspi_polling_api_error",
                order_id=order.id,
                order_number=order.orderNumber,
                external_id=order.kaspi_payment_id,
                error=str(e)
            )
            return None

        except Exception as e:
            logger.error(
                "kaspi_polling_unexpected_error",
                order_id=order.id,
                order_number=order.orderNumber,
                external_id=order.kaspi_payment_id,
                error=str(e),
                error_type=type(e).__name__
            )
            await session.rollback()
            return None

    @staticmethod
    async def poll_payment_statuses():
        """
        Main polling function - checks all pending payments and updates statuses

        This function is called by APScheduler every 2-3 minutes.
        It queries pending payments and checks their status via Kaspi API.

        Returns:
            None

        Side effects:
            - Updates order records in database
            - Logs status changes
        """
        logger.info("kaspi_polling_started")

        try:
            # Get database session
            async for session in get_session():
                # Query pending payments
                pending_orders = await KaspiPollingService.get_pending_payments(session)

                if not pending_orders:
                    logger.info("kaspi_polling_no_pending_orders")
                    return

                # Check status for each order
                checked_count = 0
                changed_count = 0
                error_count = 0

                for order in pending_orders:
                    try:
                        new_status = await KaspiPollingService.check_and_update_payment_status(
                            session,
                            order
                        )

                        checked_count += 1

                        if new_status:
                            changed_count += 1

                    except Exception as e:
                        error_count += 1
                        logger.error(
                            "kaspi_polling_order_failed",
                            order_id=order.id,
                            error=str(e)
                        )

                # Log summary
                logger.info(
                    "kaspi_polling_completed",
                    total_orders=len(pending_orders),
                    checked=checked_count,
                    changed=changed_count,
                    errors=error_count
                )

        except Exception as e:
            logger.error(
                "kaspi_polling_critical_error",
                error=str(e),
                error_type=type(e).__name__
            )


# Singleton instance for scheduler
_polling_service: Optional[KaspiPollingService] = None


def get_polling_service() -> KaspiPollingService:
    """Get or create global polling service instance"""
    global _polling_service
    if _polling_service is None:
        _polling_service = KaspiPollingService()
    return _polling_service
