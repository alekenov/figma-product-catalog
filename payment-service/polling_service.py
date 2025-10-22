"""
Payment Status Polling Service

Two-phase polling strategy for Kaspi payment status checking:
- Phase 1 (0-10 min): Check every 15 seconds (fast response for immediate payments)
- Phase 2 (10 min - 24 hours): Check every 3 minutes (catch delayed payments)
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlmodel import Session, select, and_, or_
from sqlalchemy import text

from database import engine, get_session
from models import PaymentLog, PaymentConfig
from kaspi_client import get_kaspi_client, KaspiClientError


class PaymentPollingService:
    """Service for periodic payment status checking"""

    # Phase 1: Recent payments (0-10 minutes) - fast polling
    RECENT_MIN_AGE_SECONDS = 15  # Wait 15 seconds before first check
    RECENT_MAX_AGE_MINUTES = 10  # Check intensively for first 10 minutes
    RECENT_LIMIT = 50  # Max payments per poll

    # Phase 2: Older payments (10 minutes - 24 hours) - slow polling
    OLDER_MIN_AGE_MINUTES = 10  # Start after 10 minutes
    OLDER_MAX_AGE_HOURS = 24  # Stop after 24 hours
    OLDER_LIMIT = 100  # Max payments per poll

    @staticmethod
    def get_pending_payments(
        session: Session,
        min_age: timedelta,
        max_age: timedelta,
        limit: int
    ) -> List[Dict]:
        """
        Get pending payments within time window

        Returns list of unique payments with their latest status:
        [{"external_id": "12800123", "shop_id": 8, "organization_bin": "210440028324", ...}, ...]

        Args:
            session: Database session
            min_age: Minimum payment age (e.g., 15 seconds)
            max_age: Maximum payment age (e.g., 10 minutes)
            limit: Maximum number of payments to return
        """
        now = datetime.now()
        min_created_at = now - max_age
        max_created_at = now - min_age

        # Find all create operations in time window
        # Then exclude those that already have Processed/Error status
        query = text("""
            WITH latest_statuses AS (
                SELECT DISTINCT ON (external_id)
                    external_id,
                    status,
                    created_at as last_check_at
                FROM paymentlog
                WHERE operation_type = 'status'
                ORDER BY external_id, created_at DESC
            ),
            pending_creates AS (
                SELECT DISTINCT ON (external_id)
                    external_id,
                    shop_id,
                    organization_bin,
                    amount,
                    created_at as payment_created_at
                FROM paymentlog
                WHERE operation_type = 'create'
                  AND external_id IS NOT NULL
                  AND created_at >= :min_created_at
                  AND created_at <= :max_created_at
                ORDER BY external_id, created_at DESC
            )
            SELECT
                p.external_id,
                p.shop_id,
                p.organization_bin,
                p.amount,
                p.payment_created_at,
                COALESCE(s.status, 'Wait') as current_status,
                s.last_check_at
            FROM pending_creates p
            LEFT JOIN latest_statuses s ON p.external_id = s.external_id
            WHERE COALESCE(s.status, 'Wait') NOT IN ('Processed', 'Error')
            ORDER BY p.payment_created_at ASC
            LIMIT :limit
        """)

        result = session.exec(
            query,
            {
                "min_created_at": min_created_at,
                "max_created_at": max_created_at,
                "limit": limit
            }
        )

        payments = []
        for row in result:
            payments.append({
                "external_id": row.external_id,
                "shop_id": row.shop_id,
                "organization_bin": row.organization_bin,
                "amount": row.amount,
                "payment_created_at": row.payment_created_at,
                "current_status": row.current_status,
                "last_check_at": row.last_check_at
            })

        return payments

    @staticmethod
    async def check_and_log_payment_status_async(
        session: Session,
        payment: Dict
    ) -> Optional[str]:
        """
        Check payment status via Kaspi API and log result (async wrapper)

        Args:
            session: Database session
            payment: Payment dict from get_pending_payments()

        Returns:
            New status if changed, None if unchanged or error
        """
        kaspi_client = get_kaspi_client()
        external_id = payment["external_id"]
        old_status = payment.get("current_status", "Wait")

        try:
            # Call Kaspi API (async)
            response = await kaspi_client.check_status(external_id)
            new_status = response.get("data", {}).get("status")

            if not new_status:
                print(f"⚠️  No status in response for {external_id}")
                return None

            # Log status check result
            log = PaymentLog(
                shop_id=payment["shop_id"],
                organization_bin=payment["organization_bin"],
                operation_type="status",
                external_id=external_id,
                amount=payment.get("amount"),
                status=new_status,
                error_message=None
            )
            session.add(log)
            session.commit()

            # Report if status changed
            if new_status != old_status:
                print(f"✅ Payment {external_id}: {old_status} → {new_status}")
                return new_status
            else:
                print(f"   Payment {external_id}: still {new_status}")
                return None

        except KaspiClientError as e:
            # Log error
            log = PaymentLog(
                shop_id=payment["shop_id"],
                organization_bin=payment["organization_bin"],
                operation_type="status",
                external_id=external_id,
                amount=payment.get("amount"),
                status="Error",
                error_message=str(e)
            )
            session.add(log)
            session.commit()

            print(f"❌ Payment {external_id} check failed: {e}")
            return None

        except Exception as e:
            print(f"❌ Unexpected error checking {external_id}: {e}")
            session.rollback()
            return None

    @staticmethod
    def poll_recent_payments():
        """
        Phase 1: Poll recent payments (0-10 minutes)

        Checks payments created in last 10 minutes (excluding first 15 seconds).
        This catches immediate payments when customer pays right away.

        Called every 15 seconds by APScheduler.
        """
        print(f"\n🔄 [Phase 1] Polling recent payments (0-10 min)...")

        with Session(engine) as session:
            payments = PaymentPollingService.get_pending_payments(
                session,
                min_age=timedelta(seconds=PaymentPollingService.RECENT_MIN_AGE_SECONDS),
                max_age=timedelta(minutes=PaymentPollingService.RECENT_MAX_AGE_MINUTES),
                limit=PaymentPollingService.RECENT_LIMIT
            )

            if not payments:
                print("   No recent pending payments")
                return

            print(f"   Found {len(payments)} recent pending payment(s)")

            checked = 0
            changed = 0
            for payment in payments:
                # Run async check_status in sync context
                new_status = asyncio.run(
                    PaymentPollingService.check_and_log_payment_status_async(
                        session,
                        payment
                    )
                )
                checked += 1
                if new_status:
                    changed += 1

            print(f"   ✓ Checked {checked}, changed {changed}")

    @staticmethod
    def poll_older_payments():
        """
        Phase 2: Poll older payments (10 minutes - 24 hours)

        Checks payments created between 10 minutes and 24 hours ago.
        This catches delayed payments when customer pays hours later.

        Called every 3 minutes by APScheduler.
        """
        print(f"\n🔄 [Phase 2] Polling older payments (10 min - 24 hours)...")

        with Session(engine) as session:
            payments = PaymentPollingService.get_pending_payments(
                session,
                min_age=timedelta(minutes=PaymentPollingService.OLDER_MIN_AGE_MINUTES),
                max_age=timedelta(hours=PaymentPollingService.OLDER_MAX_AGE_HOURS),
                limit=PaymentPollingService.OLDER_LIMIT
            )

            if not payments:
                print("   No older pending payments")
                return

            print(f"   Found {len(payments)} older pending payment(s)")

            checked = 0
            changed = 0
            for payment in payments:
                # Run async check_status in sync context
                new_status = asyncio.run(
                    PaymentPollingService.check_and_log_payment_status_async(
                        session,
                        payment
                    )
                )
                checked += 1
                if new_status:
                    changed += 1

            print(f"   ✓ Checked {checked}, changed {changed}")


# Singleton instance
_polling_service: Optional[PaymentPollingService] = None


def get_polling_service() -> PaymentPollingService:
    """Get or create global polling service instance"""
    global _polling_service
    if _polling_service is None:
        _polling_service = PaymentPollingService()
    return _polling_service
