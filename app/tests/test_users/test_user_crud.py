"""
Comprehensive test cases for User module.

This module contains test cases for:
- User CRUD operations
- User log operations
- User validation and edge cases
"""

import pytest
from fastapi import status
from datetime import datetime
from app.api.v1.user.models import User, User_log
from app.auth.utils import encrypt_password


BASE_URL = "/api/v1"


class TestUserRoutes:
    """Test cases for user routes endpoints."""

    def test_get_user_route(self, test_client):
        """Test the GET /user/user endpoint."""
        response = test_client.get(f"{BASE_URL}/user/user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"Message": "user routes"}

    def test_post_user_log_route(self, test_client):
        """Test the POST /user/user-log endpoint."""
        response = test_client.post(f"{BASE_URL}/user/user-log")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"Message": "user log routes"}


class TestUserModel:
    """Test cases for User model operations."""

    def test_create_user(self, test_db_session):
        """Test creating a new user in the database."""
        user = User(
            username="testuser",
            email="test@example.com",
            password=encrypt_password("password123"),
            gender="Male",
            mobile="1234567890",
            country_code="+1",
            region="US",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.user_id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_verified is True
        assert user.is_active is True
        assert user.created_at is not None

    def test_create_user_with_minimal_fields(self, test_db_session):
        """Test creating a user with only required fields."""
        user = User(
            email="minimal@example.com",
            is_verified=False,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.user_id is not None
        assert user.email == "minimal@example.com"
        assert user.is_verified is False
        assert user.is_active is True

    def test_user_email_uniqueness(self, test_db_session):
        """Test that email must be unique."""
        user1 = User(
            email="unique@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user1)
        test_db_session.commit()

        user2 = User(
            email="unique@example.com",  # Duplicate email
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_db_session.commit()

    def test_update_user(self, test_db_session):
        """Test updating user information."""
        user = User(
            username="oldname",
            email="update@example.com",
            gender="Male",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Update user
        user.username = "newname"
        user.gender = "Female"
        user.region = "UK"
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.username == "newname"
        assert user.gender == "Female"
        assert user.region == "UK"
        assert user.updated_at is not None

    def test_delete_user(self, test_db_session):
        """Test deleting a user."""
        user = User(
            email="delete@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        user_id = user.user_id

        # Delete user
        test_db_session.delete(user)
        test_db_session.commit()

        # Verify user is deleted
        deleted_user = test_db_session.query(User).filter(User.user_id == user_id).first()
        assert deleted_user is None

    def test_user_soft_delete(self, test_db_session):
        """Test soft deleting a user by setting is_active to False."""
        user = User(
            email="softdelete@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Soft delete
        user.is_active = False
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.is_active is False

    def test_user_query_by_email(self, test_db_session):
        """Test querying user by email."""
        user = User(
            email="query@example.com",
            username="queryuser",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        found_user = test_db_session.query(User).filter(User.email == "query@example.com").first()
        assert found_user is not None
        assert found_user.email == "query@example.com"
        assert found_user.username == "queryuser"

    def test_user_query_by_mobile(self, test_db_session):
        """Test querying user by mobile number."""
        user = User(
            email="mobile@example.com",
            mobile="9876543210",
            country_code="+1",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        found_user = test_db_session.query(User).filter(
            User.mobile == "9876543210"
        ).first()
        assert found_user is not None
        assert found_user.mobile == "9876543210"

    def test_user_with_profile_pic(self, test_db_session):
        """Test creating user with profile picture URL."""
        user = User(
            email="profile@example.com",
            username="profileuser",
            profile_pic_url="https://example.com/pic.jpg",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.profile_pic_url == "https://example.com/pic.jpg"


class TestUserLogModel:
    """Test cases for User_log model operations."""

    def test_create_user_log(self, test_db_session):
        """Test creating a user log entry."""
        # First create a user
        user = User(
            email="loguser@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Create user log
        user_log = User_log(
            user_id=user.user_id,
            date_of_birth=datetime(1990, 1, 1),
            height_cm=175.5,
            weight_kg=70.0,
            chest_cm=100.0,
            neck_cm=38.0,
            biceps_cm=35.0,
            hip_cm=95.0,
            waist_cm=80.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()
        test_db_session.refresh(user_log)

        assert user_log.user_log_id is not None
        assert user_log.user_id == user.user_id
        assert user_log.height_cm == 175.5
        assert user_log.weight_kg == 70.0
        assert user_log.created_at is not None

    def test_create_user_log_with_minimal_fields(self, test_db_session):
        """Test creating user log with minimal required fields."""
        user = User(
            email="minlog@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        user_log = User_log(
            user_id=user.user_id,
            weight_kg=65.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()
        test_db_session.refresh(user_log)

        assert user_log.user_log_id is not None
        assert user_log.user_id == user.user_id
        assert user_log.weight_kg == 65.0

    def test_user_log_relationship(self, test_db_session):
        """Test the relationship between User and User_log."""
        user = User(
            email="relation@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Create multiple logs
        log1 = User_log(user_id=user.user_id, weight_kg=70.0, height_cm=175.0)
        log2 = User_log(user_id=user.user_id, weight_kg=72.0, height_cm=175.5)
        test_db_session.add_all([log1, log2])
        test_db_session.commit()

        # Refresh user to load relationship
        test_db_session.refresh(user)

        assert len(user.user_logs) == 2
        assert log1 in user.user_logs
        assert log2 in user.user_logs

    def test_user_log_cascade_delete(self, test_db_session):
        """Test that user logs are deleted when user is deleted."""
        user = User(
            email="cascade@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        log1 = User_log(user_id=user.user_id, weight_kg=70.0)
        log2 = User_log(user_id=user.user_id, weight_kg=72.0)
        test_db_session.add_all([log1, log2])
        test_db_session.commit()

        log_ids = [log1.user_log_id, log2.user_log_id]

        # Delete user
        test_db_session.delete(user)
        test_db_session.commit()

        # Verify logs are also deleted
        for log_id in log_ids:
            deleted_log = test_db_session.query(User_log).filter(
                User_log.user_log_id == log_id
            ).first()
            assert deleted_log is None

    def test_update_user_log(self, test_db_session):
        """Test updating user log measurements."""
        user = User(
            email="updatelog@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        user_log = User_log(
            user_id=user.user_id,
            weight_kg=70.0,
            height_cm=175.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()

        # Update log
        user_log.weight_kg = 75.0
        user_log.chest_cm = 105.0
        test_db_session.commit()
        test_db_session.refresh(user_log)

        assert user_log.weight_kg == 75.0
        assert user_log.chest_cm == 105.0

    def test_user_log_with_all_measurements(self, test_db_session):
        """Test creating user log with all body measurements."""
        user = User(
            email="allmeasure@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        user_log = User_log(
            user_id=user.user_id,
            date_of_birth=datetime(1995, 5, 15),
            height_cm=180.0,
            weight_kg=75.5,
            chest_cm=105.0,
            neck_cm=40.0,
            biceps_cm=38.0,
            hip_cm=100.0,
            waist_cm=85.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()
        test_db_session.refresh(user_log)

        assert user_log.height_cm == 180.0
        assert user_log.weight_kg == 75.5
        assert user_log.chest_cm == 105.0
        assert user_log.neck_cm == 40.0
        assert user_log.biceps_cm == 38.0
        assert user_log.hip_cm == 100.0
        assert user_log.waist_cm == 85.0


class TestUserValidation:
    """Test cases for user validation and edge cases."""

    def test_user_with_long_email(self, test_db_session):
        """Test user creation with a long email address."""
        long_email = "a" * 100 + "@example.com"
        user = User(
            email=long_email,
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.email == long_email

    def test_user_with_special_characters_in_username(self, test_db_session):
        """Test user creation with special characters in username."""
        user = User(
            email="special@example.com",
            username="user_name-123",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.username == "user_name-123"

    def test_user_log_with_negative_values(self, test_db_session):
        """Test user log with negative measurement values (should be allowed by DB)."""
        user = User(
            email="negative@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        user_log = User_log(
            user_id=user.user_id,
            weight_kg=-10.0,  # Negative value
            height_cm=-5.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()
        test_db_session.refresh(user_log)

        # Database allows negative values, but application logic should validate
        assert user_log.weight_kg == -10.0

    def test_user_log_with_zero_values(self, test_db_session):
        """Test user log with zero measurement values."""
        user = User(
            email="zero@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        user_log = User_log(
            user_id=user.user_id,
            weight_kg=0.0,
            height_cm=0.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()
        test_db_session.refresh(user_log)

        assert user_log.weight_kg == 0.0
        assert user_log.height_cm == 0.0

    def test_user_log_with_very_large_values(self, test_db_session):
        """Test user log with very large measurement values."""
        user = User(
            email="large@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        user_log = User_log(
            user_id=user.user_id,
            weight_kg=999.99,
            height_cm=300.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()
        test_db_session.refresh(user_log)

        assert user_log.weight_kg == 999.99
        assert user_log.height_cm == 300.0

    def test_multiple_users_same_region(self, test_db_session):
        """Test creating multiple users in the same region."""
        users = [
            User(email=f"region{i}@example.com", region="US", is_verified=True, is_active=True)
            for i in range(5)
        ]
        test_db_session.add_all(users)
        test_db_session.commit()

        region_users = test_db_session.query(User).filter(User.region == "US").all()
        assert len(region_users) == 5

    def test_user_verification_status(self, test_db_session):
        """Test user verification status changes."""
        user = User(
            email="verify@example.com",
            is_verified=False,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Verify user
        user.is_verified = True
        test_db_session.commit()
        test_db_session.refresh(user)

        assert user.is_verified is True

