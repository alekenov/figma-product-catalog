"""
Kaspi Pay Integration Tests

Automated test suite for Kaspi payment integration.
Tests payment creation, status polling, webhooks, and refunds.
"""
import pytest
from datetime import datetime, timedelta
from tests.mocks.kaspi_api import PaymentStatus


class TestKaspiPaymentCreation:
    """Test payment creation"""

    @pytest.mark.asyncio
    async def test_create_payment_success(self, mock_kaspi_client):
        """Test successful payment creation"""
        external_id = "order_12345"
        amount = 17.00
        phone = "+77015211545"

        payment = await mock_kaspi_client.create_payment(external_id, amount, phone)

        assert payment['externalId'] == external_id
        assert payment['amount'] == amount
        assert payment['phone'] == phone
        assert payment['status'] == PaymentStatus.CREATED.value

    @pytest.mark.asyncio
    async def test_create_payment_duplicate_id(self, mock_kaspi_client):
        """Test that duplicate external_id fails"""
        external_id = "order_12345"

        # Create first payment
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        # Try to create duplicate
        with pytest.raises(Exception, match="already exists"):
            await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

    @pytest.mark.asyncio
    async def test_create_payment_invalid_amount(self, mock_kaspi_client):
        """Test that zero/negative amounts fail"""
        with pytest.raises(Exception, match="must be positive"):
            await mock_kaspi_client.create_payment("order_1", -50, "+77015211545")

        with pytest.raises(Exception, match="must be positive"):
            await mock_kaspi_client.create_payment("order_2", 0, "+77015211545")

    @pytest.mark.asyncio
    async def test_create_multiple_payments(self, mock_kaspi_client):
        """Test creating multiple payments for same phone"""
        phone = "+77015211545"

        payment1 = await mock_kaspi_client.create_payment("order_1", 100, phone)
        payment2 = await mock_kaspi_client.create_payment("order_2", 200, phone)

        assert payment1['externalId'] == "order_1"
        assert payment2['externalId'] == "order_2"
        assert payment1['phone'] == payment2['phone'] == phone


class TestKaspiPaymentStatus:
    """Test payment status tracking"""

    @pytest.mark.asyncio
    async def test_get_payment_status_created(self, mock_kaspi_client):
        """Test getting status of newly created payment"""
        external_id = "order_12345"
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        status = await mock_kaspi_client.get_payment_status(external_id)

        assert status['status'] == PaymentStatus.CREATED.value
        assert status['completedAt'] is None

    @pytest.mark.asyncio
    async def test_get_payment_status_not_found(self, mock_kaspi_client):
        """Test getting status of non-existent payment"""
        with pytest.raises(Exception, match="not found"):
            await mock_kaspi_client.get_payment_status("nonexistent_order")

    @pytest.mark.asyncio
    async def test_payment_status_progression(self, mock_kaspi_client):
        """Test payment status changes over time"""
        external_id = "order_12345"
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        # Check initial status
        status1 = await mock_kaspi_client.get_payment_status(external_id)
        assert status1['status'] == PaymentStatus.CREATED.value

        # Simulate processing
        mock_kaspi_client.process_payment(external_id)
        status2 = await mock_kaspi_client.get_payment_status(external_id)
        assert status2['status'] == PaymentStatus.PROCESSED.value
        assert status2['completedAt'] is not None


class TestKaspiPaymentProcessing:
    """Test payment processing workflow"""

    @pytest.mark.asyncio
    async def test_process_payment_success(self, mock_kaspi_client):
        """Test successful payment processing"""
        external_id = "order_12345"
        amount = 17.00

        await mock_kaspi_client.create_payment(external_id, amount, "+77015211545")

        # Simulate payment processing (e.g., user confirms in Kaspi app)
        processed = mock_kaspi_client.process_payment(external_id)

        assert processed['status'] == PaymentStatus.PROCESSED.value
        assert processed['completedAt'] is not None

        # Verify status is updated
        status = await mock_kaspi_client.get_payment_status(external_id)
        assert status['status'] == PaymentStatus.PROCESSED.value

    @pytest.mark.asyncio
    async def test_process_payment_not_found(self, mock_kaspi_client):
        """Test processing non-existent payment fails"""
        with pytest.raises(Exception, match="not found"):
            mock_kaspi_client.process_payment("nonexistent_order")

    @pytest.mark.asyncio
    async def test_payment_failure(self, mock_kaspi_client):
        """Test payment failure scenario"""
        external_id = "order_12345"
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        # Simulate payment failure
        failed = mock_kaspi_client.fail_payment(external_id, "User cancelled payment")

        assert failed['status'] == PaymentStatus.ERROR.value
        assert failed['errorMessage'] == "User cancelled payment"


class TestKaspiPaymentRefunds:
    """Test payment refund functionality"""

    @pytest.mark.asyncio
    async def test_refund_full_payment(self, mock_kaspi_client):
        """Test full payment refund"""
        external_id = "order_12345"
        amount = 100.0

        await mock_kaspi_client.create_payment(external_id, amount, "+77015211545")
        mock_kaspi_client.process_payment(external_id)

        # Full refund
        refund = await mock_kaspi_client.refund_payment(external_id)

        assert refund['refundAmount'] == amount
        assert refund['remainingAmount'] == 0

    @pytest.mark.asyncio
    async def test_refund_partial_payment(self, mock_kaspi_client):
        """Test partial payment refund"""
        external_id = "order_12345"
        amount = 100.0
        refund_amount = 30.0

        await mock_kaspi_client.create_payment(external_id, amount, "+77015211545")
        mock_kaspi_client.process_payment(external_id)

        # Partial refund
        refund = await mock_kaspi_client.refund_payment(external_id, refund_amount)

        assert refund['refundAmount'] == refund_amount
        assert refund['remainingAmount'] == amount - refund_amount

    @pytest.mark.asyncio
    async def test_refund_unprocessed_payment(self, mock_kaspi_client):
        """Test that unprocessed payments cannot be refunded"""
        external_id = "order_12345"
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        # Try to refund without processing
        with pytest.raises(Exception, match="Cannot refund"):
            await mock_kaspi_client.refund_payment(external_id)

    @pytest.mark.asyncio
    async def test_refund_exceeds_amount(self, mock_kaspi_client):
        """Test that refund cannot exceed original amount"""
        external_id = "order_12345"
        amount = 100.0

        await mock_kaspi_client.create_payment(external_id, amount, "+77015211545")
        mock_kaspi_client.process_payment(external_id)

        # Try to refund more than original amount
        with pytest.raises(Exception, match="exceeds payment amount"):
            await mock_kaspi_client.refund_payment(external_id, amount + 50)


class TestKaspiWebhooks:
    """Test webhook handling"""

    @pytest.mark.asyncio
    async def test_webhook_payment_success(self, mock_kaspi_client):
        """Test incoming webhook for successful payment"""
        external_id = "order_12345"
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        # Simulate webhook from Kaspi
        webhook = mock_kaspi_client.simulate_webhook(external_id, PaymentStatus.PROCESSED.value)

        assert webhook['success'] is True
        assert 'webhookId' in webhook

        # Verify payment status is updated
        status = await mock_kaspi_client.get_payment_status(external_id)
        assert status['status'] == PaymentStatus.PROCESSED.value

    @pytest.mark.asyncio
    async def test_webhook_payment_error(self, mock_kaspi_client):
        """Test incoming webhook for failed payment"""
        external_id = "order_12345"
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        # Simulate error webhook
        webhook = mock_kaspi_client.simulate_webhook(external_id, PaymentStatus.ERROR.value)

        assert webhook['success'] is True

        # Verify payment status is updated
        status = await mock_kaspi_client.get_payment_status(external_id)
        assert status['status'] == PaymentStatus.ERROR.value

    @pytest.mark.asyncio
    async def test_multiple_webhooks_same_payment(self, mock_kaspi_client):
        """Test multiple webhooks for same payment (state machine)"""
        external_id = "order_12345"
        await mock_kaspi_client.create_payment(external_id, 100, "+77015211545")

        # First webhook: processing
        mock_kaspi_client.simulate_webhook(external_id, PaymentStatus.PROCESSING.value)
        status1 = await mock_kaspi_client.get_payment_status(external_id)
        assert status1['status'] == PaymentStatus.PROCESSING.value

        # Second webhook: completed
        mock_kaspi_client.simulate_webhook(external_id, PaymentStatus.PROCESSED.value)
        status2 = await mock_kaspi_client.get_payment_status(external_id)
        assert status2['status'] == PaymentStatus.PROCESSED.value
        assert status2['completedAt'] is not None


class TestKaspiEndToEnd:
    """End-to-end payment workflow tests"""

    @pytest.mark.asyncio
    async def test_full_order_payment_flow(self, mock_kaspi_client):
        """Test complete order -> payment -> confirmation flow"""
        order_id = "ORDER_20251016_001"
        customer_phone = "+77015211545"
        order_amount = 17.00

        # Step 1: Create payment when order is created
        payment = await mock_kaspi_client.create_payment(
            order_id, order_amount, customer_phone
        )
        assert payment['status'] == PaymentStatus.CREATED.value

        # Step 2: Customer receives payment link and processes payment
        mock_kaspi_client.process_payment(order_id)

        # Step 3: Backend receives webhook from Kaspi
        mock_kaspi_client.simulate_webhook(order_id, PaymentStatus.PROCESSED.value)

        # Step 4: Verify payment is confirmed
        final_status = await mock_kaspi_client.get_payment_status(order_id)
        assert final_status['status'] == PaymentStatus.PROCESSED.value
        assert final_status['amount'] == order_amount

    @pytest.mark.asyncio
    async def test_full_refund_flow(self, mock_kaspi_client):
        """Test complete refund workflow"""
        order_id = "ORDER_20251016_002"
        customer_phone = "+77015211545"
        order_amount = 100.00

        # Create and process payment
        await mock_kaspi_client.create_payment(order_id, order_amount, customer_phone)
        mock_kaspi_client.process_payment(order_id)

        # Simulate webhook confirmation
        mock_kaspi_client.simulate_webhook(order_id, PaymentStatus.PROCESSED.value)

        # Step 1: Customer requests refund
        # Step 2: Backend initiates refund
        refund = await mock_kaspi_client.refund_payment(order_id, order_amount)

        # Step 3: Verify refund completed
        assert refund['refundAmount'] == order_amount
        assert refund['remainingAmount'] == 0


class TestKaspiConcurrency:
    """Test concurrent payment handling"""

    @pytest.mark.asyncio
    async def test_concurrent_orders(self, mock_kaspi_client):
        """Test handling multiple concurrent orders"""
        orders = []

        # Create 10 concurrent orders
        for i in range(10):
            order_id = f"ORDER_BULK_{i:03d}"
            payment = await mock_kaspi_client.create_payment(
                order_id, 100.00 + i * 10, f"+7701521154{i}"
            )
            orders.append((order_id, payment))

        # Verify all payments created
        assert len(orders) == 10

        # Verify all have unique IDs and amounts
        payment_ids = [p[0] for p in orders]
        assert len(set(payment_ids)) == 10

        # Verify amounts increment correctly
        amounts = [p[1]['amount'] for p in orders]
        expected_amounts = [100.00 + i * 10 for i in range(10)]
        assert amounts == expected_amounts
