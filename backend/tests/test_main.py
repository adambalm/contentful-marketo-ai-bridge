import os

import pytest
from fastapi.testclient import TestClient

# Set environment before importing app
os.environ["AI_PROVIDER"] = "local"

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
