"""
Test configuration file for Fit-Charge application.

This module sets up the test environment with:
- SQLite in-memory database for testing
- All database models imported and tables created
- Pytest fixtures for database session and FastAPI test client
- Proper dependency overrides for testing
"""

from fastapi import status

BASE_URL = ""


def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"Health": "Server is Running"}