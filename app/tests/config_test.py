"""
Test configuration file for Fit-Charge application.

This module sets up the test environment with:
- SQLite in-memory database for testing
- All database models imported and tables created
- Pytest fixtures for database session and FastAPI test client
- Proper dependency overrides for testing
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import Base and all models
from app.api.v1.user.models import Base, User
# Import future models here when they are created
# from api.v1.food.models import Food
# from api.v1.workout.models import Workout

# Import database dependency and app
from app.core.database import get_session
from main import app

# Use SQLite in-memory database for testing
# This ensures tests are isolated and fast
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with StaticPool for in-memory SQLite
# connect_args={"check_same_thread": False} is required for SQLite
# poolclass=StaticPool ensures connections are shared properly
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL query debugging
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    This fixture ensures database is clean for each test.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a new session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after each test for clean state
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """
    Override the get_session dependency to use test database.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session cleanup handled by db_session fixture
    
    return _override_get_db


@pytest.fixture(scope="function")
def client(override_get_db):
    """
    Create a test client with database dependency overridden.
    """
    app.dependency_overrides[get_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Create a test user for testing purposes.
    """
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password_here",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
