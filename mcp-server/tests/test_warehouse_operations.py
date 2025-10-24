"""
Pytest tests for warehouse operations MCP tools.

Tests verify that warehouse operations tools correctly interact with backend API
and handle various scenarios including success cases, validation, and error handling.
"""
import pytest
from unittest.mock import AsyncMock, patch
from domains.inventory import tools


# ===== Fixtures =====

@pytest.fixture
def admin_token():
    """Admin JWT token for testing."""
    return "test_admin_token_12345"


@pytest.fixture
def mock_api_client():
    """Mock API client for testing without hitting real backend."""
    with patch('domains.inventory.tools.api_client') as mock_client:
        yield mock_client


# ===== record_warehouse_operation tests =====

@pytest.mark.asyncio
async def test_record_warehouse_operation_delivery(mock_api_client, admin_token):
    """Test recording IN operation (stock arrival/delivery)."""
    # Arrange
    expected_response = {
        "id": 123,
        "warehouse_item_id": 5,
        "quantity_change": 50,
        "operation_type": "DELIVERY",
        "description": "Delivery from supplier",
        "created_at": "2025-01-23T10:30:00"
    }
    mock_api_client.post = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.record_warehouse_operation(
        token=admin_token,
        warehouse_item_id=5,
        quantity=50,
        operation_type="IN",
        notes="Delivery from supplier"
    )

    # Assert
    assert result == expected_response
    mock_api_client.post.assert_called_once_with(
        "/warehouse/5/delivery",
        json_data={
            "quantity_change": 50,
            "description": "Delivery from supplier"
        },
        token=admin_token
    )


@pytest.mark.asyncio
async def test_record_warehouse_operation_sale(mock_api_client, admin_token):
    """Test recording OUT operation (stock usage/sale)."""
    # Arrange
    expected_response = {
        "id": 124,
        "warehouse_item_id": 5,
        "quantity_change": -10,
        "operation_type": "SALE",
        "description": "Sold in order #123",
        "created_at": "2025-01-23T11:00:00"
    }
    mock_api_client.post = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.record_warehouse_operation(
        token=admin_token,
        warehouse_item_id=5,
        quantity=-10,
        operation_type="OUT",
        notes="Sold in order #123"
    )

    # Assert
    assert result == expected_response
    assert result["quantity_change"] == -10
    assert result["operation_type"] == "SALE"
    mock_api_client.post.assert_called_once_with(
        "/warehouse/5/sale",
        json_data={
            "quantity_change": -10,
            "description": "Sold in order #123"
        },
        token=admin_token
    )


@pytest.mark.asyncio
async def test_record_warehouse_operation_writeoff(mock_api_client, admin_token):
    """Test recording WRITE_OFF operation (damaged goods)."""
    # Arrange
    expected_response = {
        "id": 125,
        "warehouse_item_id": 8,
        "quantity_change": -3,
        "operation_type": "WRITEOFF",
        "description": "Damaged tulips",
        "created_at": "2025-01-23T12:00:00"
    }
    mock_api_client.post = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.record_warehouse_operation(
        token=admin_token,
        warehouse_item_id=8,
        quantity=-3,
        operation_type="WRITE_OFF",
        notes="Damaged tulips"
    )

    # Assert
    assert result["operation_type"] == "WRITEOFF"
    assert result["quantity_change"] < 0
    # Verify reason field is added for writeoff
    mock_api_client.post.assert_called_once_with(
        "/warehouse/8/writeoff",
        json_data={
            "quantity_change": -3,
            "description": "Damaged tulips",
            "reason": "Damaged tulips"
        },
        token=admin_token
    )


@pytest.mark.asyncio
async def test_record_warehouse_operation_invalid_type(admin_token):
    """Test error handling for unsupported operation_type."""
    with pytest.raises(ValueError) as exc_info:
        await tools.record_warehouse_operation(
            token=admin_token,
            warehouse_item_id=5,
            quantity=10,
            operation_type="CORRECTION",  # Not supported
            notes="Test"
        )

    assert "Unsupported operation_type" in str(exc_info.value)
    assert "CORRECTION" in str(exc_info.value)


# ===== get_warehouse_history tests =====

@pytest.mark.asyncio
async def test_get_warehouse_history_all(mock_api_client, admin_token):
    """Test getting all warehouse history for an item."""
    # Arrange
    expected_response = [
        {"id": 123, "operation_type": "DELIVERY", "quantity_change": 50},
        {"id": 124, "operation_type": "SALE", "quantity_change": -10},
    ]
    mock_api_client.get = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.get_warehouse_history(
        token=admin_token,
        warehouse_item_id=5
    )

    # Assert
    assert result == expected_response
    mock_api_client.get.assert_called_once_with(
        "/warehouse/5/operations",
        token=admin_token,
        params={"skip": 0, "limit": 50}
    )


@pytest.mark.asyncio
async def test_get_warehouse_history_filtered(mock_api_client, admin_token):
    """Test filtering warehouse history by operation type."""
    # Arrange
    expected_response = [
        {
            "id": 124,
            "warehouse_item_id": 5,
            "operation_type": "SALE",
            "quantity_change": -10,
            "created_at": "2025-01-20T10:00:00"
        }
    ]
    mock_api_client.get = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.get_warehouse_history(
        token=admin_token,
        warehouse_item_id=5,
        operation_type="SALE",
        skip=0,
        limit=20
    )

    # Assert
    assert len(result) == 1
    assert result[0]["operation_type"] == "SALE"
    # Verify params were passed correctly
    call_args = mock_api_client.get.call_args
    params = call_args[1]["params"]
    assert params["operation_type"] == "SALE"
    assert params["skip"] == 0
    assert params["limit"] == 20


# ===== create_inventory_check tests =====

@pytest.mark.asyncio
async def test_create_inventory_check_with_items(mock_api_client, admin_token):
    """Test creating inventory check with items."""
    # Arrange
    expected_response = {
        "id": 10,
        "conducted_by": "Ivan Petrov",
        "comment": "Monthly inventory - January 2025",
        "status": "pending",
        "created_at": "2025-01-23T09:00:00",
        "items": [
            {"warehouse_item_id": 5, "actual_quantity": 48, "difference": -2},
            {"warehouse_item_id": 8, "actual_quantity": 30, "difference": 0}
        ]
    }
    mock_api_client.post = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.create_inventory_check(
        token=admin_token,
        conducted_by="Ivan Petrov",
        items=[
            {"warehouse_item_id": 5, "actual_quantity": 48},
            {"warehouse_item_id": 8, "actual_quantity": 30}
        ],
        comment="Monthly inventory - January 2025"
    )

    # Assert
    assert result["id"] == 10
    assert result["status"] == "pending"
    assert len(result["items"]) == 2
    mock_api_client.post.assert_called_once_with(
        "/inventory/",
        json_data={
            "conducted_by": "Ivan Petrov",
            "items": [
                {"warehouse_item_id": 5, "actual_quantity": 48},
                {"warehouse_item_id": 8, "actual_quantity": 30}
            ],
            "comment": "Monthly inventory - January 2025"
        },
        token=admin_token
    )


@pytest.mark.asyncio
async def test_create_inventory_check_no_comment(mock_api_client, admin_token):
    """Test creating inventory check without comment."""
    # Arrange
    expected_response = {
        "id": 11,
        "conducted_by": "Maria Sidorova",
        "comment": None,
        "status": "pending",
        "created_at": "2025-01-23T10:00:00",
        "items": [
            {"warehouse_item_id": 5, "actual_quantity": 50, "difference": 0}
        ]
    }
    mock_api_client.post = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.create_inventory_check(
        token=admin_token,
        conducted_by="Maria Sidorova",
        items=[{"warehouse_item_id": 5, "actual_quantity": 50}]
    )

    # Assert
    assert result["id"] == 11
    # Verify comment was not in request data
    call_args = mock_api_client.post.call_args
    assert "comment" not in call_args[1]["json_data"]


# ===== list_inventory_checks tests =====

@pytest.mark.asyncio
async def test_list_inventory_checks(mock_api_client, admin_token):
    """Test listing inventory checks."""
    # Arrange
    expected_response = [
        {
            "id": 10,
            "conducted_by": "Ivan",
            "comment": "Monthly inventory",
            "status": "applied",
            "items_count": 25,
            "created_at": "2025-01-15T09:00:00"
        },
        {
            "id": 11,
            "conducted_by": "Maria",
            "comment": "Weekly check",
            "status": "pending",
            "items_count": 10,
            "created_at": "2025-01-22T10:00:00"
        }
    ]
    mock_api_client.get = AsyncMock(return_value=expected_response)

    # Act
    result = await tools.list_inventory_checks(token=admin_token, limit=10)

    # Assert
    assert len(result) == 2
    assert result[0]["status"] == "applied"
    assert result[1]["status"] == "pending"
    # Verify endpoint and pagination params
    mock_api_client.get.assert_called_once_with(
        "/inventory/",
        token=admin_token,
        params={"skip": 0, "limit": 10}
    )
