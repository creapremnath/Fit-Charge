from logging.config import fileConfig
from app.core.config import settings

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import central Base and all model modules to register tables
from app.core.database import Base
import app.api.v1.user.models  # noqa: F401
import app.api.v1.workout.models  # noqa: F401
import app.api.v1.food.models  # noqa: F401

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

# Set target_metadata to central Base metadata for autogenerate
target_metadata = Base.metadata


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
