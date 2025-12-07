from logging.config import fileConfig
from app.core.config import settings

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all your models' Base objects explicitly
from app.api.v1.user.models import Base as UserBase
from api.v1.workout.models import Base as WorkoutBase
# from api.v1.food.models import Base as FoodBase

# Compose a proper SQLAlchemy URL with settings, for Alembic to use
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.database_user}:{settings.database_password}@"
    f"{settings.database_host}/{settings.database_name}"
)

# Alembic Config object for .ini (migration env) file settings
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Set up logging using alembic.ini (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Aggregate all relevant model metadatas as target_metadata for autogenerate
# WARNING: Alembic expects a MetaData instance, not a set
metadatas = [
    UserBase.metadata,
    WorkoutBase.metadata,
    # FoodBase.metadata,
]
# If all use the same declarative base, this is a single instance. If not, create a MetaData union.
# We'll combine all those tables in a dynamic MetaData (useful for autogenerate with multiple bases)
from sqlalchemy import MetaData
target_metadata = MetaData()
for meta in metadatas:
    for table in meta.tables.values():
        if table.name not in target_metadata.tables:
            table.tometadata(target_metadata)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
