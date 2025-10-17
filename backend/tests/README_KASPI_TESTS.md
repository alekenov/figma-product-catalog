# Kaspi Pay Integration Tests

Comprehensive automated test suite for Kaspi payment integration.

## Overview

Kaspi payment tests simulate the complete payment workflow without requiring actual Kaspi Pay credentials during testing. The test suite includes:

- **Payment Creation** - Creating new payment requests
- **Status Tracking** - Polling payment status
- **Webhook Handling** - Simulating incoming webhooks from Kaspi
- **Refunds** - Full and partial payment refunds
- **Error Scenarios** - Handling payment failures and edge cases
- **Concurrency** - Testing multiple concurrent orders

## Structure

```
backend/tests/
├── mocks/
│   ├── __init__.py
│   └── kaspi_api.py          # Mock Kaspi API server
├── conftest_kaspi.py          # Pytest fixtures for Kaspi tests
├── test_kaspi_integration.py  # Main test suite
└── README_KASPI_TESTS.md      # This file
```

## Mock Kaspi API

The `MockKaspiAPI` class simulates Kaspi Pay behavior:

- **create_payment()** - Creates a new payment
- **get_payment_status()** - Retrieves payment status
- **process_payment()** - Simulates payment processing
- **fail_payment()** - Simulates payment failure
- **refund_payment()** - Performs refunds
- **simulate_webhook()** - Simulates incoming webhooks

## Running Tests

### Run All Kaspi Tests
```bash
pytest backend/tests/test_kaspi_integration.py -v
```

### Run Specific Test Class
```bash
pytest backend/tests/test_kaspi_integration.py::TestKaspiPaymentCreation -v
```

### Run Specific Test Method
```bash
pytest backend/tests/test_kaspi_integration.py::TestKaspiPaymentCreation::test_create_payment_success -v
```

### Run with Coverage
```bash
pytest backend/tests/test_kaspi_integration.py --cov=api.payments --cov-report=html
```

### Run Only Kaspi Tests (CI)
```bash
pytest backend/tests/test_kaspi_integration.py -v --tb=short
```

## Test Classes

### TestKaspiPaymentCreation
Tests for payment creation:
- `test_create_payment_success` - Valid payment creation
- `test_create_payment_duplicate_id` - Duplicate payment ID rejection
- `test_create_payment_invalid_amount` - Invalid amount validation
- `test_create_multiple_payments` - Multiple payments for same customer

### TestKaspiPaymentStatus
Tests for payment status tracking:
- `test_get_payment_status_created` - Get newly created payment status
- `test_get_payment_status_not_found` - Handle non-existent payments
- `test_payment_status_progression` - Track status changes

### TestKaspiPaymentProcessing
Tests for payment processing:
- `test_process_payment_success` - Successful payment processing
- `test_process_payment_not_found` - Handle missing payments
- `test_payment_failure` - Simulate payment failures

### TestKaspiPaymentRefunds
Tests for refund functionality:
- `test_refund_full_payment` - Full payment refund
- `test_refund_partial_payment` - Partial payment refund
- `test_refund_unprocessed_payment` - Prevent refunding unprocessed payments
- `test_refund_exceeds_amount` - Prevent refunding more than paid

### TestKaspiWebhooks
Tests for webhook handling:
- `test_webhook_payment_success` - Handle success webhook
- `test_webhook_payment_error` - Handle error webhook
- `test_multiple_webhooks_same_payment` - Handle multiple webhooks

### TestKaspiEndToEnd
End-to-end workflow tests:
- `test_full_order_payment_flow` - Complete order → payment → confirmation
- `test_full_refund_flow` - Complete refund workflow

### TestKaspiConcurrency
Concurrency tests:
- `test_concurrent_orders` - Handle multiple concurrent orders

## Example Usage in Backend Tests

```python
import pytest

@pytest.mark.asyncio
async def test_create_order_with_kaspi_payment(mock_kaspi_client):
    """Example: Create order and initiate Kaspi payment"""

    # Create payment
    payment = await mock_kaspi_client.create_payment(
        external_id="ORDER_12345",
        amount=17.00,
        phone="+77015211545"
    )

    # Verify payment created
    assert payment['status'] == 'Created'

    # Simulate user confirming payment in Kaspi app
    mock_kaspi_client.process_payment("ORDER_12345")

    # Verify status changed
    status = await mock_kaspi_client.get_payment_status("ORDER_12345")
    assert status['status'] == 'Processed'
```

## CI Integration

### GitHub Actions
The test suite is integrated into CI/CD pipeline:

```yaml
- name: Test Kaspi Integration
  run: pytest backend/tests/test_kaspi_integration.py -v --tb=short
```

### Local Development
Run tests before committing:

```bash
# Install test dependencies
pip install -r backend/requirements.txt

# Run Kaspi tests
pytest backend/tests/test_kaspi_integration.py -v

# Run all backend tests
pytest backend/tests/ -v
```

## Integration with Real Kaspi API

When ready to test with actual Kaspi Pay:

1. Update your backend to accept either mock or real Kaspi client
2. Set `USE_MOCK_KASPI=false` environment variable
3. Provide real `KASPI_API_KEY` and `KASPI_MERCHANT_ID`
4. Tests will still run but against real API (use test amounts)

Example:
```python
# In backend/api/payments/kaspi.py
if os.getenv('USE_MOCK_KASPI', 'true').lower() == 'true':
    kaspi_client = MockKaspiClient()
else:
    kaspi_client = RealKaspiClient(
        api_key=os.getenv('KASPI_API_KEY'),
        merchant_id=os.getenv('KASPI_MERCHANT_ID')
    )
```

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'tests'`:
```bash
# Add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
pytest tests/test_kaspi_integration.py -v
```

### Async Test Issues
If tests hang or fail with async errors:
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Run with asyncio marker
pytest backend/tests/test_kaspi_integration.py -v -m asyncio
```

### Mock Not Used
If tests are hitting real Kaspi API:
1. Verify `mock_kaspi_client` fixture is imported
2. Check that patches are applied correctly
3. Review conftest.py for fixture scope issues

## Future Improvements

- [ ] Add performance benchmarks for payment processing
- [ ] Add stress tests (1000+ concurrent payments)
- [ ] Add integration with backend order creation flow
- [ ] Add webhook signature verification tests
- [ ] Add retry logic tests for failed webhooks
- [ ] Add database transaction rollback tests
- [ ] Add logging and audit trail verification
