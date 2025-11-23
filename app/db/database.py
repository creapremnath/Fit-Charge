
from config import settings
from fc_logger import get_logger
import time
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError,ProgrammingError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import psycopg2


logger = get_logger("fitcharge.database")

from config import settings
# Replace with your actual credentials
DATABASE_URL = f"postgresql+psycopg2://{settings.database_user}:{settings.database_password}@{settings.database_host}/{settings.database_name}"
# logger.info(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)


def init_db():  # etc...
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


def create_database_if_not_exists():
    # Connect to the default 'postgres' DB
    url = URL.create(
        "postgresql+psycopg2",
        username=settings.database_user,
        password=settings.database_password,
        host=settings.database_host,
        database="postgres"
    )

    engine = create_engine(url, isolation_level="AUTOCOMMIT")

    db_name = settings.database_name

    with engine.connect() as connection:
        result = connection.execute(text(f"""
            SELECT 1 FROM pg_database WHERE datname = '{db_name}'
        """))
        exists = result.scalar()

        if not exists:
            logger.info(f"Database '{db_name}' not found. Creating...")
            connection.execute(text(f'CREATE DATABASE "{db_name}"'))
        else:
            logger.info(f"Database '{db_name}' already exists.")