import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_session
from app.main import app
from app.api.v1.user.models import Base

# Use SQLite in-memory database for testing (no external DB required)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a new SQLAlchemy engine and session for the test database
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,  # Set to False to reduce test output noise
    connect_args={"check_same_thread": False},  # Required for SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override the dependency in FastAPI to use test session
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables before tests run, drop after all tests complete."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop tables after tests are done
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def test_db_session():
    """Yields a new db session to the test DB, for db-dependent test code.
    Each test gets a fresh session with automatic rollback for isolation.
    """
    # Create a connection and begin a transaction
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        # Rollback transaction and close session/connection
        session.close()
        try:
            transaction.rollback()
        except Exception:
            pass  # Transaction may already be rolled back
        connection.close()

@pytest.fixture
def test_client(test_db_session):
    # Dependency override for SQLAlchemy session (used by FastAPI's Depends)
    def override_get_session():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()