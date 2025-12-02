
from sqlalchemy.orm.session import Session
from core.config import settings
from core.fc_logger import get_logger
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError, ProgrammingError

# Import Base from one of your models (example: user model)
from api.v1.user.models import Base

logger = get_logger("fitcharge.database")

DATABASE_URL = f"postgresql+psycopg2://{settings.database_user}:{settings.database_password}@{settings.database_host}/{settings.database_name}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine) # type: ignore

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
    logger.info("Waiting for database...")
    db_up = False
    while not db_up:
        try:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
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
