"""
Kaspi Pay API Integration Tests

Tests the actual FastAPI endpoints with mocked Kaspi service.
These tests verify:
- Request routing and parsing
- Response serialization
- Error handling
- Full request-response cycle
"""
import pytest
from fastapi.testclient import TestClient
from typing import Generator


@pytest.fixture
def client(mock_kaspi_service_patch) -> Generator:
    """FastAPI test client with mocked Kaspi service"""
    # Import AFTER mock is patched
    from main import app
    yield TestClient(app)


class TestKaspiCreatePaymentEndpoint:
    """Test /api/v1/kaspi/create endpoint"""

    def test_create_payment_success(self, client):
        """Test successful payment creation"""
        response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 100,
            "message": "Test order"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "external_id" in data
        assert data["external_id"] is not None

    def test_create_payment_invalid_phone(self, client):
        """Test missing phone"""
        response = client.post("/api/v1/kaspi/create", json={
            "amount": 100,
            "message": "Test order"
        })

        assert response.status_code == 422  # Validation error

    def test_create_payment_invalid_amount(self, client):
        """Test invalid amount"""
        response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": -50,  # Negative amount
            "message": "Test order"
        })

        assert response.status_code == 422

    def test_create_payment_response_format(self, client):
        """Test response has correct format"""
        response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 500,
            "message": "Order #123"
        })

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "success" in data
        assert "external_id" in data
        assert "status" in data

        # Verify types
        assert isinstance(data["success"], bool)
        assert isinstance(data["external_id"], str)
        assert isinstance(data["status"], str)


class TestKaspiCheckStatusEndpoint:
    """Test /api/v1/kaspi/status/{external_id} endpoint"""

    def test_check_status_success(self, client, mock_kaspi_api):
        """Test successful status check"""
        # Create payment first
        create_response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 100,
            "message": "Test order"
        })
        external_id = create_response.json()["external_id"]

        # Check status
        response = client.get(f"/api/v1/kaspi/status/{external_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["external_id"] == external_id
        assert "status" in data

    def test_check_status_nonexistent(self, client):
        """Test checking status of non-existent payment"""
        response = client.get("/api/v1/kaspi/status/nonexistent_id")

        # Should fail because payment doesn't exist
        assert response.status_code == 500

    def test_check_status_response_format(self, client):
        """Test response has correct format"""
        # Create payment
        create_response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 100,
            "message": "Test"
        })
        external_id = create_response.json()["external_id"]

        # Check status
        response = client.get(f"/api/v1/kaspi/status/{external_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "success" in data
        assert "external_id" in data
        assert "status" in data
        assert isinstance(data["success"], bool)
        assert isinstance(data["status"], str)


class TestKaspiRefundEndpoint:
    """Test /api/v1/kaspi/refund endpoint"""

    def test_refund_success(self, client, mock_kaspi_api):
        """Test successful refund"""
        # Create payment
        create_response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 100,
            "message": "Test order"
        })
        external_id = create_response.json()["external_id"]

        # Process payment (mock)
        mock_kaspi_api.process_payment(external_id)

        # Refund
        response = client.post("/api/v1/kaspi/refund", json={
            "external_id": external_id,
            "amount": 50
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["external_id"] == external_id

    def test_refund_full_payment(self, client, mock_kaspi_api):
        """Test full payment refund"""
        # Create and process payment
        create_response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 200,
            "message": "Order"
        })
        external_id = create_response.json()["external_id"]
        mock_kaspi_api.process_payment(external_id)

        # Full refund
        response = client.post("/api/v1/kaspi/refund", json={
            "external_id": external_id,
            "amount": 200  # Full amount
        })

        assert response.status_code == 200

    def test_refund_unprocessed_payment(self, client):
        """Test refunding unprocessed payment fails"""
        # Create payment but don't process
        create_response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 100,
            "message": "Test"
        })
        external_id = create_response.json()["external_id"]

        # Try to refund (should fail)
        response = client.post("/api/v1/kaspi/refund", json={
            "external_id": external_id,
            "amount": 50
        })

        # Expected to fail
        assert response.status_code == 500

    def test_refund_response_format(self, client, mock_kaspi_api):
        """Test refund response format"""
        # Create and process payment
        create_response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 100,
            "message": "Test"
        })
        external_id = create_response.json()["external_id"]
        mock_kaspi_api.process_payment(external_id)

        # Refund
        response = client.post("/api/v1/kaspi/refund", json={
            "external_id": external_id,
            "amount": 50
        })

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "success" in data
        assert "external_id" in data
        assert "refunded_amount" in data
        assert data["external_id"] == external_id
        assert data["refunded_amount"] == 50


class TestKaspiFullEndToEnd:
    """End-to-end tests for complete payment flow"""

    def test_full_payment_cycle_via_api(self, client, mock_kaspi_api):
        """Test complete payment flow through API"""
        # Step 1: Create payment
        create_response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545",
            "amount": 1000,
            "message": "Order #123"
        })

        assert create_response.status_code == 200
        payment = create_response.json()
        external_id = payment["external_id"]
        assert payment["status"] == "Wait"

        # Step 2: Check initial status
        status_response = client.get(f"/api/v1/kaspi/status/{external_id}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "Wait"

        # Step 3: Simulate customer paying (mark as processed in mock)
        mock_kaspi_api.process_payment(external_id)

        # Step 4: Check updated status
        status_response = client.get(f"/api/v1/kaspi/status/{external_id}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "Processed"

        # Step 5: Refund part of payment
        refund_response = client.post("/api/v1/kaspi/refund", json={
            "external_id": external_id,
            "amount": 200
        })

        assert refund_response.status_code == 200
        refund_data = refund_response.json()
        assert refund_data["success"] is True
        assert refund_data["refunded_amount"] == 200

    def test_multiple_payments_concurrent(self, client):
        """Test handling multiple concurrent payments"""
        payments = []

        # Create 5 concurrent payments
        for i in range(5):
            response = client.post("/api/v1/kaspi/create", json={
                "phone": f"7701521154{i}",  # Different phones
                "amount": 100 * (i + 1),
                "message": f"Order #{i+1}"
            })

            assert response.status_code == 200
            payments.append(response.json())

        # Verify all created
        assert len(payments) == 5

        # Verify all have unique external_ids
        external_ids = [p["external_id"] for p in payments]
        assert len(set(external_ids)) == 5  # All unique

        # Check status of each
        for payment in payments:
            response = client.get(f"/api/v1/kaspi/status/{payment['external_id']}")
            assert response.status_code == 200

    def test_error_handling_invalid_json(self, client):
        """Test error handling for invalid JSON"""
        response = client.post(
            "/api/v1/kaspi/create",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Should reject invalid JSON
        assert response.status_code >= 400

    def test_error_handling_missing_fields(self, client):
        """Test validation of required fields"""
        response = client.post("/api/v1/kaspi/create", json={
            "phone": "77015211545"
            # Missing amount and message
        })

        assert response.status_code == 422  # Validation error
