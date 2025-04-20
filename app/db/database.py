# database.py
from config import settings
from fc_logger import get_logger
import time
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import (OperationalError, SQLAlchemyError)
from sqlalchemy import text
from models.users import User

logger=get_logger("fitcharge.database")

# Replace with your actual credentials
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.database_user}:{settings.database_password}@db/{settings.database_name}"
)
logger.info(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)


def init_db():       # etc...
    logger.info("Creating database tables if they don't exist...")
    SQLModel.metadata.create_all(engine)


def wait_for_db():
    logger.info("Waiting for database...")
    db_up = False
    while not db_up:
        try:
            with Session(engine) as session:
                session.execute(text("SELECT 1"))
            db_up = True
        except OperationalError as e:
            print(f"Database unavailable, waiting 1 second... ({e})")
            time.sleep(1)
    logger.info("Database available!")

# Make sure this imports your actual engine
def get_session():
    with Session(engine) as session:
        yield session