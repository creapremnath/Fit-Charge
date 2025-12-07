
from sqlalchemy.orm.session import Session
from app.core.config import settings
from app.core.fc_logger import get_logger
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Import Base from one of your models (example: user model)
from app.api.v1.user.models import Base
from app.api.v1.workout.models import Base

logger = get_logger("fitcharge.database")

DATABASE_URL = f"postgresql+psycopg2://{settings.database_user}:{settings.database_password}@{settings.database_host}/{settings.database_name}"

TEST_DATABASE_URL = settings.test_database

# Use SQLAlchemy's connection pooling (the default is QueuePool)
# You can tune pool_size, max_overflow, and other pool options as needed
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

