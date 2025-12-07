"""
Integration test cases for User module.

This module contains integration tests that test the interaction
between User and User_log models, and more complex scenarios.
"""

import pytest
from datetime import datetime
from app.api.v1.user.models import User, User_log
from app.auth.utils import encrypt_password


class TestUserIntegration:
    """Integration tests for User module."""

    def test_user_lifecycle_with_logs(self, test_db_session):
        """Test complete user lifecycle: create, add logs, update, delete."""
        # Create user
        user = User(
            email="lifecycle@example.com",
            username="lifecycleuser",
            password=encrypt_password("password123"),
            gender="Male",
            mobile="1111111111",
            country_code="+1",
            region="US",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        user_id = user.user_id

        # Add initial log
        initial_log = User_log(
            user_id=user_id,
            date_of_birth=datetime(1990, 1, 1),
            height_cm=170.0,
            weight_kg=70.0,
            chest_cm=95.0,
            waist_cm=80.0
        )
        test_db_session.add(initial_log)
        test_db_session.commit()

        # Add progress log after 3 months
        progress_log = User_log(
            user_id=user_id,
            height_cm=170.0,
            weight_kg=68.0,  # Lost weight
            chest_cm=98.0,   # Gained muscle
            waist_cm=78.0    # Lost inches
        )
        test_db_session.add(progress_log)
        test_db_session.commit()

        # Verify user has 2 logs
        test_db_session.refresh(user)
        assert len(user.user_logs) == 2

        # Update user profile
        user.username = "updatedlifecycle"
        user.region = "CA"
        test_db_session.commit()

        # Verify updates
        test_db_session.refresh(user)
        assert user.username == "updatedlifecycle"
        assert user.region == "CA"

        # Delete user (should cascade delete logs)
        test_db_session.delete(user)
        test_db_session.commit()

        # Verify user and logs are deleted
        deleted_user = test_db_session.query(User).filter(User.user_id == user_id).first()
        assert deleted_user is None

        deleted_logs = test_db_session.query(User_log).filter(
            User_log.user_id == user_id
        ).all()
        assert len(deleted_logs) == 0

    def test_multiple_users_with_logs(self, test_db_session):
        """Test creating multiple users, each with their own logs."""
        users_data = [
            {
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "gender": "Male" if i % 2 == 0 else "Female",
                "logs": [
                    {"weight_kg": 70.0 + i, "height_cm": 170.0 + i},
                    {"weight_kg": 72.0 + i, "height_cm": 170.0 + i}
                ]
            }
            for i in range(3)
        ]

        created_users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                gender=user_data["gender"],
                is_verified=True,
                is_active=True
            )
            test_db_session.add(user)
            test_db_session.flush()  # Get user_id without committing

            # Add logs for this user
            for log_data in user_data["logs"]:
                log = User_log(user_id=user.user_id, **log_data)
                test_db_session.add(log)

            created_users.append(user)

        test_db_session.commit()

        # Verify all users and their logs
        for user in created_users:
            test_db_session.refresh(user)
            assert len(user.user_logs) == 2

    def test_user_query_with_active_filter(self, test_db_session):
        """Test querying only active users."""
        # Create active users
        active_users = [
            User(email=f"active{i}@example.com", is_verified=True, is_active=True)
            for i in range(3)
        ]

        # Create inactive users
        inactive_users = [
            User(email=f"inactive{i}@example.com", is_verified=True, is_active=False)
            for i in range(2)
        ]

        test_db_session.add_all(active_users + inactive_users)
        test_db_session.commit()

        # Query only active users
        active_only = test_db_session.query(User).filter(User.is_active == True).all()
        assert len(active_only) == 3

        # Query only inactive users
        inactive_only = test_db_session.query(User).filter(User.is_active == False).all()
        assert len(inactive_only) == 2

    def test_user_query_with_verification_filter(self, test_db_session):
        """Test querying users by verification status."""
        verified_users = [
            User(email=f"verified{i}@example.com", is_verified=True, is_active=True)
            for i in range(4)
        ]

        unverified_users = [
            User(email=f"unverified{i}@example.com", is_verified=False, is_active=True)
            for i in range(3)
        ]

        test_db_session.add_all(verified_users + unverified_users)
        test_db_session.commit()

        # Query verified users
        verified_only = test_db_session.query(User).filter(
            User.is_verified == True
        ).all()
        assert len(verified_only) == 4

        # Query unverified users
        unverified_only = test_db_session.query(User).filter(
            User.is_verified == False
        ).all()
        assert len(unverified_only) == 3

    def test_user_log_tracking_progress(self, test_db_session):
        """Test tracking user progress over time with multiple logs."""
        user = User(
            email="progress@example.com",
            username="progressuser",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Create logs over time (simulating monthly check-ins)
        logs_data = [
            {"weight_kg": 80.0, "waist_cm": 90.0, "chest_cm": 95.0},  # Month 1
            {"weight_kg": 78.0, "waist_cm": 88.0, "chest_cm": 96.0},  # Month 2
            {"weight_kg": 75.0, "waist_cm": 85.0, "chest_cm": 98.0},  # Month 3
            {"weight_kg": 73.0, "waist_cm": 83.0, "chest_cm": 100.0}, # Month 4
        ]

        for log_data in logs_data:
            log = User_log(user_id=user.user_id, **log_data)
            test_db_session.add(log)

        test_db_session.commit()

        # Verify all logs are created
        test_db_session.refresh(user)
        assert len(user.user_logs) == 4

        # Verify progress (weight should be decreasing)
        logs = sorted(user.user_logs, key=lambda x: x.created_at)
        assert logs[0].weight_kg == 80.0
        assert logs[-1].weight_kg == 73.0

    def test_user_with_complete_profile(self, test_db_session):
        """Test creating a user with complete profile and initial log."""
        user = User(
            username="completeuser",
            email="complete@example.com",
            password=encrypt_password("securepassword123"),
            gender="Female",
            profile_pic_url="https://example.com/profile.jpg",
            country_code="+44",
            mobile="9876543210",
            region="UK",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Add comprehensive initial log
        user_log = User_log(
            user_id=user.user_id,
            date_of_birth=datetime(1992, 6, 15),
            height_cm=165.0,
            weight_kg=60.0,
            chest_cm=88.0,
            neck_cm=32.0,
            biceps_cm=28.0,
            hip_cm=92.0,
            waist_cm=70.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()

        # Verify complete user profile
        test_db_session.refresh(user)
        assert user.username == "completeuser"
        assert user.email == "complete@example.com"
        assert user.gender == "Female"
        assert user.profile_pic_url == "https://example.com/profile.jpg"
        assert user.country_code == "+44"
        assert user.mobile == "9876543210"
        assert user.region == "UK"
        assert user.is_verified is True
        assert user.is_active is True

        # Verify log
        assert len(user.user_logs) == 1
        log = user.user_logs[0]
        assert log.height_cm == 165.0
        assert log.weight_kg == 60.0
        assert log.chest_cm == 88.0

    def test_user_reactivation(self, test_db_session):
        """Test deactivating and reactivating a user."""
        user = User(
            email="reactivate@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Deactivate
        user.is_active = False
        test_db_session.commit()

        # Verify deactivated
        test_db_session.refresh(user)
        assert user.is_active is False

        # Reactivate
        user.is_active = True
        test_db_session.commit()

        # Verify reactivated
        test_db_session.refresh(user)
        assert user.is_active is True

    def test_user_log_with_future_date(self, test_db_session):
        """Test creating user log with future date of birth (edge case)."""
        user = User(
            email="futuredate@example.com",
            is_verified=True,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Future date (should be allowed by DB, but app logic should validate)
        future_date = datetime(2100, 1, 1)
        user_log = User_log(
            user_id=user.user_id,
            date_of_birth=future_date,
            weight_kg=70.0
        )
        test_db_session.add(user_log)
        test_db_session.commit()
        test_db_session.refresh(user_log)

        assert user_log.date_of_birth == future_date

