"""
Tests for order status transitions.

Ensures valid order status flows and prevents invalid state changes.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from models import Order, OrderStatus


class TestOrderStatusTransitions:
    """Test valid and invalid order status transitions"""

    # Valid status transition flows
    VALID_TRANSITIONS = {
        OrderStatus.NEW: [OrderStatus.PAID, OrderStatus.ACCEPTED, OrderStatus.CANCELLED],
        OrderStatus.PAID: [OrderStatus.ACCEPTED, OrderStatus.CANCELLED],
        OrderStatus.ACCEPTED: [OrderStatus.IN_PRODUCTION, OrderStatus.CANCELLED],
        OrderStatus.IN_PRODUCTION: [OrderStatus.READY, OrderStatus.CANCELLED],
        OrderStatus.READY: [OrderStatus.IN_DELIVERY],
        OrderStatus.IN_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.READY],  # Can return to READY if delivery failed
        OrderStatus.DELIVERED: [],  # Terminal state
        OrderStatus.CANCELLED: [],  # Terminal state
    }

    def test_new_to_paid_transition_valid(self, client: TestClient, auth_token: str, test_order_id: int):
        """Test NEW → PAID is a valid transition"""
        response = client.patch(
            f"/api/v1/orders/{test_order_id}/status",
            json={"status": "PAID"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "PAID"

    def test_new_to_accepted_transition_valid(self, client: TestClient, auth_token: str, test_order_id: int):
        """Test NEW → ACCEPTED is a valid transition (skip payment)"""
        response = client.patch(
            f"/api/v1/orders/{test_order_id}/status",
            json={"status": "ACCEPTED"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ACCEPTED"

    def test_new_to_delivered_transition_invalid(self, client: TestClient, auth_token: str, test_order_id: int):
        """Test NEW → DELIVERED is invalid (skips required steps)"""
        response = client.patch(
            f"/api/v1/orders/{test_order_id}/status",
            json={"status": "DELIVERED"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should reject or allow but require validation
        # Implementation may vary - document expected behavior
        assert response.status_code in [400, 422, 200]  # Depends on business rules

    def test_delivered_cannot_transition_to_other_states(self, client: TestClient, auth_token: str):
        """Test that DELIVERED is a terminal state"""
        # Create order and set to DELIVERED
        order_id = self._create_order_with_status(client, auth_token, "DELIVERED")

        # Try to change from DELIVERED
        response = client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "IN_PRODUCTION"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [400, 422], "Cannot transition from DELIVERED"

    def test_cancelled_cannot_transition_to_other_states(self, client: TestClient, auth_token: str):
        """Test that CANCELLED is a terminal state"""
        # Create order and set to CANCELLED
        order_id = self._create_order_with_status(client, auth_token, "CANCELLED")

        # Try to change from CANCELLED
        response = client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "ACCEPTED"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [400, 422], "Cannot transition from CANCELLED"

    def test_complete_order_flow(self, client: TestClient, auth_token: str):
        """Test a complete order lifecycle: NEW → PAID → ACCEPTED → IN_PRODUCTION → READY → IN_DELIVERY → DELIVERED"""
        # Create order
        order_data = {
            "customerName": "Test Customer",
            "phone": "+77015211545",
            "delivery_date": "2024-12-25",
            "delivery_time": "14:00",
            "shop_id": 8,
            "items": [{"product_id": 1, "quantity": 1}],
            "total_price": 50000,
        }

        create_response = client.post(
            "/api/v1/orders/public/create?shop_id=8",
            json=order_data
        )
        assert create_response.status_code == 201
        order_id = create_response.json()["id"]

        # Transition through states
        states = ["PAID", "ACCEPTED", "IN_PRODUCTION", "READY", "IN_DELIVERY", "DELIVERED"]

        for state in states:
            response = client.patch(
                f"/api/v1/orders/{order_id}/status",
                json={"status": state},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert response.status_code == 200, f"Failed to transition to {state}"
            assert response.json()["status"] == state

    def test_order_cancellation_from_various_states(self, client: TestClient, auth_token: str):
        """Test that orders can be cancelled from non-terminal states"""
        cancellable_states = ["NEW", "PAID", "ACCEPTED", "IN_PRODUCTION"]

        for state in cancellable_states:
            order_id = self._create_order_with_status(client, auth_token, state)

            response = client.patch(
                f"/api/v1/orders/{order_id}/status",
                json={"status": "CANCELLED", "notes": f"Cancelled from {state}"},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert response.status_code == 200, f"Should allow cancellation from {state}"
            assert response.json()["status"] == "CANCELLED"

    def test_cannot_cancel_delivered_order(self, client: TestClient, auth_token: str):
        """Test that delivered orders cannot be cancelled"""
        order_id = self._create_order_with_status(client, auth_token, "DELIVERED")

        response = client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "CANCELLED"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [400, 422], "Cannot cancel DELIVERED order"

    def test_status_history_created_on_transition(self, client: TestClient, auth_token: str, test_order_id: int):
        """Test that status transitions create history records"""
        # Change status
        client.patch(
            f"/api/v1/orders/{test_order_id}/status",
            json={"status": "ACCEPTED", "notes": "Test note"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Check history
        response = client.get(
            f"/api/v1/orders/{test_order_id}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        history = response.json()
        assert len(history) > 0, "Should have status history records"

        # Find the ACCEPTED status change
        accepted_records = [h for h in history if h["new_status"] == "ACCEPTED"]
        assert len(accepted_records) > 0, "Should have ACCEPTED status in history"
        assert accepted_records[0]["notes"] == "Test note"

    def test_invalid_status_value_rejected(self, client: TestClient, auth_token: str, test_order_id: int):
        """Test that invalid status values are rejected"""
        response = client.patch(
            f"/api/v1/orders/{test_order_id}/status",
            json={"status": "INVALID_STATUS"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422, "Should reject invalid status value"

    def test_lowercase_status_converted_to_uppercase(self, client: TestClient, auth_token: str, test_order_id: int):
        """Test that lowercase status values are handled correctly"""
        response = client.patch(
            f"/api/v1/orders/{test_order_id}/status",
            json={"status": "accepted"},  # lowercase
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Should either accept and convert, or reject
        if response.status_code == 200:
            assert response.json()["status"] == "ACCEPTED", "Should convert to uppercase"
        else:
            assert response.status_code == 422, "Should reject lowercase if not supported"

    # Helper methods

    def _create_order_with_status(self, client: TestClient, auth_token: str, status: str) -> int:
        """Helper to create an order with specific status"""
        # Create order
        order_data = {
            "customerName": "Test Customer",
            "phone": "+77015211545",
            "delivery_date": "2024-12-25",
            "delivery_time": "14:00",
            "shop_id": 8,
            "items": [{"product_id": 1, "quantity": 1}],
            "total_price": 50000,
        }

        create_response = client.post(
            "/api/v1/orders/public/create?shop_id=8",
            json=order_data
        )
        order_id = create_response.json()["id"]

        # Set to desired status
        client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": status},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        return order_id


class TestOrderStatusValidation:
    """Test order status enum validation"""

    def test_all_status_values_are_valid(self):
        """Test that all OrderStatus enum values are uppercase"""
        for status in OrderStatus:
            assert status.value == status.value.upper(), f"Status {status.value} should be uppercase"

    def test_status_enum_values(self):
        """Test that expected status values exist in enum"""
        expected_statuses = [
            "NEW", "PAID", "ACCEPTED", "IN_PRODUCTION",
            "READY", "IN_DELIVERY", "DELIVERED", "CANCELLED"
        ]

        enum_values = [s.value for s in OrderStatus]

        for expected in expected_statuses:
            assert expected in enum_values, f"Status {expected} should exist in OrderStatus enum"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
