"""
Basic test cases for User module endpoints.

This module contains simple test cases for:
- Health check endpoint
- User route endpoints
- User log route endpoints
"""

from fastapi import status

BASE_URL = "/api/v1"


def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Health": "Server is Running"}


def test_get_user_endpoint(test_client):
    """Test GET /api/v1/user/user endpoint."""
    response = test_client.get(f"{BASE_URL}/user/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Message": "user routes"}


def test_post_user_log_endpoint(test_client):
    """Test POST /api/v1/user/user-log endpoint."""
    response = test_client.post(f"{BASE_URL}/user/user-log")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Message": "user log routes"}