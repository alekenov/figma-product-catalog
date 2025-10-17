"""
Pytest fixtures for Kaspi payment integration tests

IMPORTANT: These fixtures are for testing the mock Kaspi API itself.
For integration tests with backend, use mock_kaspi_service fixture.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from tests.mocks.kaspi_api import MockKaspiAPI


@pytest.fixture
def mock_kaspi_api():
    """Provide mock Kaspi API instance"""
    api = MockKaspiAPI()
    yield api
    api.reset()


@pytest.fixture
def mock_kaspi_client(mock_kaspi_api):
    """Mock Kaspi client that uses mock API"""
    class MockKaspiClient:
        def __init__(self, api):
            self.api = api

        async def create_payment(self, external_id: str, amount: float, phone: str):
            result = self.api.create_payment(external_id, amount, phone)
            if 'error' in result:
                raise Exception(result['error'])
            return result['data']

        async def get_payment_status(self, external_id: str):
            result = self.api.get_payment_status(external_id)
            if 'error' in result:
                raise Exception(result['error'])
            return result['data']

        async def refund_payment(self, external_id: str, amount: float = None):
            result = self.api.refund_payment(external_id, amount)
            if 'error' in result:
                raise Exception(result['error'])
            return result['data']

        def process_payment(self, external_id: str):
            """Simulate payment processing"""
            result = self.api.process_payment(external_id)
            if 'error' in result:
                raise Exception(result['error'])
            return result['data']

        def fail_payment(self, external_id: str, error: str = "Payment failed"):
            """Simulate payment failure"""
            result = self.api.fail_payment(external_id, error)
            if 'error' in result:
                raise Exception(result['error'])
            return result['data']

        def simulate_webhook(self, external_id: str, status: str):
            """Simulate webhook from Kaspi"""
            result = self.api.simulate_webhook(external_id, status)
            if 'error' in result:
                raise Exception(result['error'])
            return result

    return MockKaspiClient(mock_kaspi_api)


@pytest.fixture
def mock_kaspi_service(mock_kaspi_api):
    """Mock KaspiPayService for backend integration tests"""
    class MockKaspiPayService:
        def __init__(self, api):
            self.api = api

        async def create_payment(self, phone: str, amount: float, message: str):
            """Create payment - matches backend interface"""
            external_id = f"order_{phone}_{int(amount)}"
            result = self.api.create_payment(external_id, amount, phone)
            if 'error' in result:
                raise Exception(result['error'])
            # Convert mock response to backend format
            return {
                'success': True,
                'data': result['data'],
                'status': True
            }

        async def check_status(self, external_id: str):
            """Check payment status - matches backend interface"""
            result = self.api.get_payment_status(external_id)
            if 'error' in result:
                raise Exception(result['error'])
            return {
                'success': True,
                'data': result['data'],
                'status': True
            }

        async def refund(self, external_id: str, amount: float):
            """Refund payment - matches backend interface"""
            result = self.api.refund_payment(external_id, amount)
            if 'error' in result:
                raise Exception(result['error'])
            return {
                'success': True,
                'data': result['data'],
                'status': True
            }

        async def close(self):
            """Cleanup"""
            pass

    return MockKaspiPayService(mock_kaspi_api)


@pytest.fixture
def mock_kaspi_service_patch(mock_kaspi_service):
    """Patch the KaspiPayService in backend code for integration tests"""
    with patch('services.kaspi_pay_service.KaspiPayService', return_value=mock_kaspi_service):
        # Also patch get_kaspi_service function
        with patch('services.kaspi_pay_service.get_kaspi_service', return_value=mock_kaspi_service):
            # Patch imports in api.kaspi_pay module
            with patch('api.kaspi_pay.get_kaspi_service', return_value=mock_kaspi_service):
                yield mock_kaspi_service
