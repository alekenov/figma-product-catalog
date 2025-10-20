"""Pytest configuration and fixtures for AI Agent Service tests."""

import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add parent directory to path to import main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="module")
def client():
    """Create FastAPI test client."""
    from main import app
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user_id():
    """Return a unique test user ID for each test."""
    import uuid
    return f"test_user_{uuid.uuid4().hex[:8]}"
