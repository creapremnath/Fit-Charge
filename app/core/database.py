
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.exc import OperationalError
from app.core.config import settings
from app.core.fc_logger import get_logger

logger = get_logger("fitcharge.database")


class Base(DeclarativeBase):
    """Canonical SQLAlchemy DeclarativeBase for all Fit-Charge models."""
    pass


DATABASE_URL = f"postgresql+psycopg2://{settings.database_user}:{settings.database_password}@{settings.database_host}/{settings.database_name}"
TEST_DATABASE_URL = settings.test_database

# Use SQLAlchemy's connection pooling (the default is QueuePool)
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,              # Number of connections to keep in pool (default 5)
    max_overflow=20,           # Maximum overflow connections above pool_size (default 10)
    pool_pre_ping=True,        # Test connections before use
    pool_timeout=30            # Seconds to wait before giving up on getting a connection
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db_initialized = False

def init_db():
    global _db_initialized
    if not _db_initialized:
        # Import models so all tables are registered onto Base.metadata
        from app.api.v1.user import models as _user_models  # noqa: F401
        from app.api.v1.workout import models as _workout_models  # noqa: F401
        from app.api.v1.food import models as _food_models  # noqa: F401

        logger.info("init_db: Creating tables using SQLAlchemy Base.metadata.create_all.")
        Base.metadata.create_all(bind=engine)
        _db_initialized = True
    else:
        logger.info("init_db: Database already initialized.")

def wait_for_db():
    logger.info("Waiting for database with connection pool...")
    db_up = False
    while not db_up:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            db_up = True
        except OperationalError as e:
            print(f"Database unavailable, waiting 1 second... ({e})")
            time.sleep(1)
    logger.info("Database available!")

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


