"""
Test script for Kaspi Pay Multi-BIN support

This test verifies that the FastAPI backend correctly handles:
1. Payment creation with default BIN (891027350515)
2. Payment creation with alternative BIN (210440028324)
3. Refunds with specified BIN
4. Proper parameter passing to production API

Run with: pytest backend/tests/test_kaspi_multi_bin.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock
from backend.services.kaspi_pay_service import KaspiPayService, KaspiPayServiceError
from backend.api.kaspi_pay import CreatePaymentRequest, RefundRequest


class TestKaspiMultiBIN:
    """Test multi-BIN support in Kaspi Pay service"""

    @pytest.fixture
    async def service(self):
        """Create service instance for testing"""
        return KaspiPayService(timeout=30)

    @pytest.mark.asyncio
    async def test_create_payment_with_default_bin(self, service):
        """Test payment creation with default BIN (no organization_bin parameter)"""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "status": True,
                "data": {
                    "externalId": "12737065473",
                    "status": "Wait"
                }
            }

            response = await service.create_payment(
                phone="77015211545",
                amount=100,
                message="Test payment"
            )

            # Verify request was made without organizationBin
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            params = call_args[1]['params']

            assert "phone" in params
            assert params["phone"] == "77015211545"
            assert "amount" in params
            assert params["amount"] == "100"
            assert "organizationBin" not in params  # Should NOT include if not provided

            assert response["status"] is True
            assert response["data"]["externalId"] == "12737065473"

    @pytest.mark.asyncio
    async def test_create_payment_with_alternative_bin(self, service):
        """Test payment creation with alternative BIN (210440028324)"""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "status": True,
                "data": {
                    "externalId": "12737338514",
                    "status": "Wait"
                }
            }

            response = await service.create_payment(
                phone="77015211545",
                amount=10,
                message="Test Alt BIN 210440028324",
                organization_bin="210440028324"
            )

            # Verify request includes organizationBin
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            params = call_args[1]['params']

            assert params["phone"] == "77015211545"
            assert params["amount"] == "10"
            assert params["message"] == "Test Alt BIN 210440028324"
            assert params["organizationBin"] == "210440028324"  # Should be included

            assert response["status"] is True
            assert response["data"]["externalId"] == "12737338514"

    @pytest.mark.asyncio
    async def test_refund_with_alternative_bin(self, service):
        """Test refund with alternative BIN matching payment's BIN"""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "status": True,
                "data": {
                    "status": "success"
                }
            }

            response = await service.refund(
                external_id="12737338514",
                amount=5,
                organization_bin="210440028324"
            )

            # Verify request includes organizationBin for refund
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            params = call_args[1]['params']

            assert params["externalId"] == "12737338514"
            assert params["amount"] == "5"
            assert params["organizationBin"] == "210440028324"  # Should be included

            assert response["status"] is True

    @pytest.mark.asyncio
    async def test_refund_without_bin_uses_default(self, service):
        """Test refund without BIN parameter (uses default)"""
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "status": True,
                "data": {"status": "success"}
            }

            response = await service.refund(
                external_id="12737065473",
                amount=50
            )

            # Verify request was made without organizationBin
            call_args = mock_request.call_args
            params = call_args[1]['params']

            assert "externalId" in params
            assert "amount" in params
            assert "organizationBin" not in params  # Should NOT include if not provided

            assert response["status"] is True

    def test_create_payment_request_model_with_bin(self):
        """Test CreatePaymentRequest model with organization_bin"""
        request = CreatePaymentRequest(
            phone="77015211545",
            amount=100,
            message="Test",
            organization_bin="210440028324"
        )

        assert request.phone == "77015211545"
        assert request.amount == 100
        assert request.message == "Test"
        assert request.organization_bin == "210440028324"

    def test_create_payment_request_model_without_bin(self):
        """Test CreatePaymentRequest model without organization_bin (optional)"""
        request = CreatePaymentRequest(
            phone="77015211545",
            amount=100,
            message="Test"
        )

        assert request.phone == "77015211545"
        assert request.amount == 100
        assert request.message == "Test"
        assert request.organization_bin is None

    def test_refund_request_model_with_bin(self):
        """Test RefundRequest model with organization_bin"""
        request = RefundRequest(
            external_id="12737338514",
            amount=50,
            organization_bin="210440028324"
        )

        assert request.external_id == "12737338514"
        assert request.amount == 50
        assert request.organization_bin == "210440028324"

    def test_refund_request_model_without_bin(self):
        """Test RefundRequest model without organization_bin (optional)"""
        request = RefundRequest(
            external_id="12737338514",
            amount=50
        )

        assert request.external_id == "12737338514"
        assert request.amount == 50
        assert request.organization_bin is None


class TestMultiBINIntegration:
    """Integration tests for multi-BIN payment flow"""

    @pytest.mark.asyncio
    async def test_complete_alt_bin_payment_flow(self):
        """Test complete payment flow with alternative BIN:
        1. Create payment with alt BIN
        2. Check status (no BIN needed)
        3. Refund with alt BIN
        """
        service = KaspiPayService()

        # Mock all requests
        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock:
            # Create payment response
            create_response = {
                "status": True,
                "data": {"externalId": "12737338514", "status": "Wait"}
            }

            # Status response
            status_response = {
                "status": True,
                "data": {"status": "Processed"}
            }

            # Refund response
            refund_response = {
                "status": True,
                "data": {"status": "success"}
            }

            mock.side_effect = [create_response, status_response, refund_response]

            # Step 1: Create payment with alt BIN
            create_result = await service.create_payment(
                phone="77015211545",
                amount=10,
                message="Test",
                organization_bin="210440028324"
            )
            assert create_result["data"]["externalId"] == "12737338514"

            # Verify BIN was passed
            create_call = mock.call_args_list[0]
            create_params = create_call[1]['params']
            assert create_params.get("organizationBin") == "210440028324"

            # Step 2: Check status (BIN not needed)
            status_result = await service.check_status("12737338514")
            assert status_result["data"]["status"] == "Processed"

            # Verify no BIN was passed for status check
            status_call = mock.call_args_list[1]
            status_params = status_call[1]['params']
            assert "organizationBin" not in status_params

            # Step 3: Refund with matching BIN
            refund_result = await service.refund(
                external_id="12737338514",
                amount=5,
                organization_bin="210440028324"
            )
            assert refund_result["status"] is True

            # Verify BIN was passed for refund
            refund_call = mock.call_args_list[2]
            refund_params = refund_call[1]['params']
            assert refund_params.get("organizationBin") == "210440028324"

        await service.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
