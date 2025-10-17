"""
Mock Kaspi Pay API for testing payment integration
"""
from datetime import datetime
from typing import Optional
from enum import Enum
import json


class PaymentStatus(Enum):
    """Kaspi payment status"""
    CREATED = "Created"
    PROCESSING = "Processing"
    PROCESSED = "Processed"
    ERROR = "Error"


class MockKaspiPaymentRecord:
    """Mock Kaspi payment record"""

    def __init__(self, external_id: str, amount: float, phone: str):
        self.external_id = external_id
        self.amount = amount
        self.phone = phone
        self.status = PaymentStatus.CREATED.value
        self.created_at = datetime.utcnow().isoformat()
        self.completed_at: Optional[str] = None
        self.error_message: Optional[str] = None

    def to_dict(self):
        return {
            'externalId': self.external_id,
            'amount': self.amount,
            'phone': self.phone,
            'status': self.status,
            'createdAt': self.created_at,
            'completedAt': self.completed_at,
            'errorMessage': self.error_message
        }


class MockKaspiAPI:
    """Mock Kaspi Pay API server for testing"""

    def __init__(self):
        self.payments: dict[str, MockKaspiPaymentRecord] = {}
        self.webhooks_received: list[dict] = []

    def create_payment(self, external_id: str, amount: float, phone: str) -> dict:
        """Create a payment"""
        if external_id in self.payments:
            return {
                'error': 'Payment with this external_id already exists',
                'status': 400
            }

        if amount <= 0:
            return {
                'error': 'Amount must be positive',
                'status': 400
            }

        payment = MockKaspiPaymentRecord(external_id, amount, phone)
        self.payments[external_id] = payment

        return {
            'success': True,
            'data': payment.to_dict(),
            'status': 201
        }

    def get_payment_status(self, external_id: str) -> dict:
        """Get payment status"""
        if external_id not in self.payments:
            return {
                'error': 'Payment not found',
                'status': 404
            }

        payment = self.payments[external_id]
        return {
            'success': True,
            'data': payment.to_dict(),
            'status': 200
        }

    def process_payment(self, external_id: str) -> dict:
        """Simulate payment processing (for testing)"""
        if external_id not in self.payments:
            return {
                'error': 'Payment not found',
                'status': 404
            }

        payment = self.payments[external_id]
        payment.status = PaymentStatus.PROCESSED.value
        payment.completed_at = datetime.utcnow().isoformat()

        return {
            'success': True,
            'data': payment.to_dict(),
            'status': 200
        }

    def fail_payment(self, external_id: str, error_message: str = "Payment failed") -> dict:
        """Simulate payment failure (for testing)"""
        if external_id not in self.payments:
            return {
                'error': 'Payment not found',
                'status': 404
            }

        payment = self.payments[external_id]
        payment.status = PaymentStatus.ERROR.value
        payment.error_message = error_message

        return {
            'success': True,
            'data': payment.to_dict(),
            'status': 200
        }

    def refund_payment(self, external_id: str, amount: Optional[float] = None) -> dict:
        """Refund a payment (full or partial)"""
        if external_id not in self.payments:
            return {
                'error': 'Payment not found',
                'status': 404
            }

        payment = self.payments[external_id]

        if payment.status != PaymentStatus.PROCESSED.value:
            return {
                'error': f'Cannot refund payment with status: {payment.status}',
                'status': 400
            }

        refund_amount = amount or payment.amount

        if refund_amount > payment.amount:
            return {
                'error': f'Refund amount ({refund_amount}) exceeds payment amount ({payment.amount})',
                'status': 400
            }

        return {
            'success': True,
            'data': {
                'refundAmount': refund_amount,
                'remainingAmount': payment.amount - refund_amount,
                'externalId': external_id
            },
            'status': 200
        }

    def simulate_webhook(self, external_id: str, status: str) -> dict:
        """Simulate incoming webhook from Kaspi"""
        if external_id not in self.payments:
            return {
                'error': 'Payment not found',
                'status': 404
            }

        payment = self.payments[external_id]
        webhook_data = {
            'externalId': external_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.webhooks_received.append(webhook_data)

        # Update payment status
        payment.status = status
        if status == PaymentStatus.PROCESSED.value:
            payment.completed_at = datetime.utcnow().isoformat()

        return {
            'success': True,
            'webhookId': f'wh_{len(self.webhooks_received)}',
            'status': 200
        }

    def reset(self):
        """Reset mock state (for testing)"""
        self.payments.clear()
        self.webhooks_received.clear()
